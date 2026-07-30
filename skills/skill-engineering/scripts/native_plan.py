#!/usr/bin/env python3
"""Portable preview/apply/verify plan for Native Skill Authoring.

The plan binds a persisted, sanitized Authoring Brief to an exact candidate
manifest and a missing target. Apply copies only that unchanged candidate via a
unique temporary directory next to the target.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

PLAN_SCHEMA_VERSION = "1.0"
BRIEF_SCHEMA_VERSION = "1"
IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
REQUIRED_BRIEF_FIELDS = (
    "goal",
    "positive_triggers",
    "negative_triggers",
    "verification",
)
MUTABLE_EXECUTION_FIELDS = {
    "applied",
    "verified",
    "applied_at",
    "verified_at",
}


class PlanError(RuntimeError):
    """A safe, user-facing refusal caused by plan drift or invalid input."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _canonical_bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _load_sibling(filename: str, module_name: str):
    sibling = Path(__file__).resolve().with_name(filename)
    spec = importlib.util.spec_from_file_location(module_name, sibling)
    if spec is None or spec.loader is None:
        raise PlanError(f"无法加载 portable 检查器:{sibling}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _read_json(path: Path, label: str) -> dict[str, object]:
    if not path.is_file() or path.is_symlink():
        raise PlanError(f"{label} 不存在或不是普通文件:{path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PlanError(f"{label} 无法读取:{path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise PlanError(f"{label} 顶层必须是 JSON object:{path}")
    return payload


def _brief_path(project: Path, brief_id: str) -> Path:
    if not IDENTIFIER_RE.fullmatch(brief_id):
        raise PlanError(f"Brief id 格式无效:{brief_id}")
    return project / ".skill-engineering" / "authoring-briefs" / f"{brief_id}.json"


def _brief_snapshot(project: Path, brief_id: str) -> dict[str, object]:
    path = _brief_path(project, brief_id)
    payload = _read_json(path, "Authoring Brief")
    if str(payload.get("schema_version")) != BRIEF_SCHEMA_VERSION:
        raise PlanError("Authoring Brief schema_version 不受支持。")
    if payload.get("id") != brief_id:
        raise PlanError("Authoring Brief 文件名与内部 id 不一致。")
    gate = _load_sibling("content_gate.py", "skill_engineering_brief_content_gate")
    serialized = json.dumps(payload, ensure_ascii=False)
    if any(pattern.search(serialized) for pattern in gate.SECRET_PATTERNS):
        raise PlanError("Authoring Brief 仍包含敏感值,请先脱敏并重新保存。")
    missing = [
        key
        for key in REQUIRED_BRIEF_FIELDS
        if not payload.get(key)
    ]
    if missing:
        raise PlanError(f"Authoring Brief 尚未就绪,缺少:{', '.join(missing)}")
    return {
        "id": brief_id,
        "path": path.relative_to(project).as_posix(),
        "fingerprint": _sha256_bytes(_canonical_bytes(payload)),
    }


def _manifest(root: Path) -> list[dict[str, object]]:
    root = root.expanduser().resolve()
    if not root.is_dir() or root.is_symlink():
        raise PlanError(f"candidate/target 不是普通目录:{root}")
    files: list[dict[str, object]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root)
        if path.is_symlink():
            raise PlanError(f"目录中包含 symlink:{relative.as_posix()}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise PlanError(f"目录中包含非普通文件:{relative.as_posix()}")
        relative_text = relative.as_posix()
        if relative.is_absolute() or ".." in relative.parts:
            raise PlanError(f"目录包含越界路径:{relative_text}")
        content = path.read_bytes()
        files.append(
            {
                "path": relative_text,
                "sha256": _sha256_bytes(content),
                "size": len(content),
            }
        )
    if not files:
        raise PlanError(f"candidate 没有可写入文件:{root}")
    return files


def _snapshot(root: Path) -> dict[str, object]:
    files = _manifest(root)
    return {
        "files": files,
        "fingerprint": _sha256_bytes(_canonical_bytes(files)),
    }


def fingerprint_tree(root: Path) -> dict[str, object]:
    """Public read-only snapshot used by host adapters and parity fixtures."""

    return _snapshot(root)


def _target_preflight(target: Path) -> dict[str, object]:
    if target.exists() or target.is_symlink():
        snapshot = _snapshot(target) if target.is_dir() and not target.is_symlink() else None
        return {
            "status": "existing",
            "fingerprint": snapshot["fingerprint"] if snapshot else "non-directory",
        }
    return {
        "status": "missing",
        "fingerprint": _sha256_bytes(f"missing:{target}".encode("utf-8")),
    }


def _plan_hash(plan: dict[str, object]) -> str:
    immutable = json.loads(json.dumps(plan))
    immutable.pop("plan_hash", None)
    execution = immutable.get("execution")
    if isinstance(execution, dict):
        for key in MUTABLE_EXECUTION_FIELDS:
            execution.pop(key, None)
    return _sha256_bytes(_canonical_bytes(immutable))


def _validate_plan(plan: dict[str, object]) -> None:
    if plan.get("schema_version") != PLAN_SCHEMA_VERSION:
        raise PlanError("Native plan schema_version 不受支持。")
    if plan.get("content_status") != "content_complete":
        raise PlanError("Native plan 不是 content_complete 候选。")
    actual = _plan_hash(plan)
    if plan.get("plan_hash") != actual:
        raise PlanError("Native plan hash 不匹配,plan 已被修改或损坏。")


def _load_plan(path: Path) -> dict[str, object]:
    plan = _read_json(path.expanduser().resolve(), "Native plan")
    _validate_plan(plan)
    return plan


def preview_plan(
    project: Path,
    brief_id: str,
    candidate: Path,
    target: Path,
    plan_path: Path,
    *,
    profile: str = "personal",
) -> dict[str, object]:
    project = project.expanduser().resolve()
    candidate = candidate.expanduser().resolve()
    target = target.expanduser().resolve()
    plan_path = plan_path.expanduser().resolve()
    if not project.is_dir():
        raise PlanError(f"project 不存在:{project}")
    if target.exists() or target.is_symlink():
        raise PlanError(f"target 已存在,Native create 不覆盖:{target}")

    brief = _brief_snapshot(project, brief_id)
    candidate_snapshot = _snapshot(candidate)
    gate = _load_sibling("content_gate.py", "skill_engineering_content_gate")
    review = _load_sibling("creation_review.py", "skill_engineering_creation_review")
    gate_findings = gate.check_candidate(candidate)
    creation_review = review.review_candidate(candidate, profile)
    if gate_findings or creation_review["status"] != "pass":
        raise PlanError("candidate 未通过 Content Gate / portable creation review。")

    plan: dict[str, object] = {
        "schema_version": PLAN_SCHEMA_VERSION,
        "hash_version": 1,
        "id": f"native-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}",
        "project": str(project),
        "brief": brief,
        "candidate": {
            "path": str(candidate),
            **candidate_snapshot,
        },
        "target": {
            "path": str(target),
            "preflight": _target_preflight(target),
        },
        "content_gate": {
            "status": "pass",
            "findings": gate_findings,
        },
        "creation_review": creation_review,
        "content_status": "content_complete",
        "preview_summary": {
            "file_count": len(candidate_snapshot["files"]),
            "target": str(target),
            "requires_confirmation": True,
        },
        "execution": {
            "applied": False,
            "verified": False,
            "applied_at": None,
            "verified_at": None,
        },
        "created_at": _now(),
        "plan_hash": "",
    }
    plan["plan_hash"] = _plan_hash(plan)
    _write_json(plan_path, plan)
    return plan


def _assert_apply_inputs(
    plan: dict[str, object],
    candidate: Path,
    target: Path,
) -> None:
    candidate = candidate.expanduser().resolve()
    target = target.expanduser().resolve()
    candidate_plan = plan["candidate"]
    target_plan = plan["target"]
    if not isinstance(candidate_plan, dict) or not isinstance(target_plan, dict):
        raise PlanError("Native plan candidate/target 结构无效。")
    if str(candidate) != candidate_plan.get("path"):
        raise PlanError("candidate 路径与 preview plan 不一致。")
    if str(target) != target_plan.get("path"):
        raise PlanError("target 路径与 preview plan 不一致。")
    current = _snapshot(candidate)
    if (
        current["fingerprint"] != candidate_plan.get("fingerprint")
        or current["files"] != candidate_plan.get("files")
    ):
        raise PlanError("candidate fingerprint 漂移,拒绝 Apply。")
    if target.exists() or target.is_symlink():
        raise PlanError("target 已存在或发生漂移,拒绝覆盖。")

    project = Path(str(plan["project"]))
    brief_plan = plan["brief"]
    if not isinstance(brief_plan, dict):
        raise PlanError("Native plan Brief 结构无效。")
    current_brief = _brief_snapshot(project, str(brief_plan.get("id") or ""))
    if current_brief["fingerprint"] != brief_plan.get("fingerprint"):
        raise PlanError("Authoring Brief fingerprint 漂移,拒绝 Apply。")
    expected_preflight = target_plan.get("preflight")
    if _target_preflight(target) != expected_preflight:
        raise PlanError("target preflight fingerprint 漂移,拒绝 Apply。")


def apply_plan(plan_path: Path, candidate: Path, target: Path) -> dict[str, object]:
    plan_path = plan_path.expanduser().resolve()
    candidate = candidate.expanduser().resolve()
    target = target.expanduser().resolve()
    plan = _load_plan(plan_path)
    _assert_apply_inputs(plan, candidate, target)
    if plan["execution"].get("applied"):
        raise PlanError("Native plan 已经 Apply,不得重复执行。")
    if not target.parent.is_dir():
        raise PlanError(f"target 父目录不存在:{target.parent}")

    temporary: Path | None = None
    try:
        temporary = Path(
            tempfile.mkdtemp(
                prefix=f".{target.name}.skill-plan-",
                dir=target.parent,
            )
        )
        shutil.copytree(candidate, temporary, dirs_exist_ok=True)
        copied = _snapshot(temporary)
        expected = plan["candidate"]
        if (
            copied["fingerprint"] != expected.get("fingerprint")
            or copied["files"] != expected.get("files")
        ):
            raise PlanError("临时副本 manifest 与 preview candidate 不一致。")
        temporary.replace(target)
        temporary = None
    except PlanError:
        raise
    except OSError as exc:
        raise PlanError(f"Apply copy failure:{exc}") from exc
    finally:
        if temporary is not None and temporary.exists():
            shutil.rmtree(temporary)

    plan["execution"]["applied"] = True
    plan["execution"]["applied_at"] = _now()
    _write_json(plan_path, plan)
    return {
        "status": "applied",
        "plan_id": plan["id"],
        "target": str(target),
        "fingerprint": plan["candidate"]["fingerprint"],
    }


def verify_plan(plan_path: Path, target: Path) -> dict[str, object]:
    plan_path = plan_path.expanduser().resolve()
    target = target.expanduser().resolve()
    plan = _load_plan(plan_path)
    target_plan = plan["target"]
    if not isinstance(target_plan, dict) or str(target) != target_plan.get("path"):
        raise PlanError("verify target 与 preview plan 不一致。")
    if not plan["execution"].get("applied"):
        raise PlanError("Native plan 尚未 Apply。")
    actual = _snapshot(target)
    expected = plan["candidate"]
    if (
        actual["fingerprint"] != expected.get("fingerprint")
        or actual["files"] != expected.get("files")
    ):
        raise PlanError("target manifest 与 preview candidate 不一致。")
    plan["execution"]["verified"] = True
    plan["execution"]["verified_at"] = _now()
    _write_json(plan_path, plan)
    return {
        "status": "verified",
        "plan_id": plan["id"],
        "target": str(target),
        "fingerprint": actual["fingerprint"],
    }


def _emit(payload: dict[str, object], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    status = payload.get("status", "preview_ready")
    print(f"Native plan {status}: {payload.get('id') or payload.get('plan_id')}")
    if status == "preview_ready":
        print(f"目标:{payload['target']['path']}")
        print(f"文件数:{payload['preview_summary']['file_count']}")
        print("等待用户确认后,使用同一 plan/candidate/target 执行 apply。")
    else:
        print(f"目标:{payload['target']}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Native Authoring immutable plan",
        allow_abbrev=False,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    preview = subparsers.add_parser("preview", allow_abbrev=False)
    preview.add_argument("--project", type=Path, required=True)
    preview.add_argument("--brief-id", required=True)
    preview.add_argument("--candidate", type=Path, required=True)
    preview.add_argument("--target", type=Path, required=True)
    preview.add_argument("--plan", type=Path, required=True)
    preview.add_argument(
        "--profile",
        choices=("personal", "team", "production"),
        default="personal",
    )
    preview.add_argument("--json", action="store_true")

    apply = subparsers.add_parser("apply", allow_abbrev=False)
    apply.add_argument("--plan", type=Path, required=True)
    apply.add_argument("--candidate", type=Path, required=True)
    apply.add_argument("--target", type=Path, required=True)
    apply.add_argument("--json", action="store_true")

    verify = subparsers.add_parser("verify", allow_abbrev=False)
    verify.add_argument("--plan", type=Path, required=True)
    verify.add_argument("--target", type=Path, required=True)
    verify.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "preview":
            payload = preview_plan(
                args.project,
                args.brief_id,
                args.candidate,
                args.target,
                args.plan,
                profile=args.profile,
            )
            payload = {**payload, "status": "preview_ready"}
        elif args.command == "apply":
            payload = apply_plan(args.plan, args.candidate, args.target)
        else:
            payload = verify_plan(args.plan, args.target)
    except PlanError as exc:
        print(f"Native plan blocked:{exc}", file=sys.stderr)
        return 1
    _emit(payload, args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

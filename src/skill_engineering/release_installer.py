"""Standalone project-local installer used only for Skill Engineering canaries."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

import yaml

from .journey import (
    ChangeRecord,
    InstallAction,
    InstallPlan,
    VerificationRecord,
    fingerprint_path,
    load_change_record,
    load_install_plan,
    new_id,
    now_iso,
    payload_hash,
    save_change_record,
    save_install_plan,
    save_verification_record,
)
from .skill_doctor import doctor_skill


DEFAULT_ENTRYPOINTS = {
    "codex": Path(".agents/skills"),
    "claude-code": Path(".claude/skills"),
}


def _skill_name(skill_path: Path) -> str:
    skill_md = skill_path / "SKILL.md"
    if not skill_md.is_file():
        raise SystemExit(f"Skill 目录缺少 SKILL.md:{skill_path}")
    text = skill_md.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end >= 0:
            try:
                data = yaml.safe_load(text[4:end]) or {}
            except yaml.YAMLError:
                data = {}
            if isinstance(data, dict) and data.get("name"):
                return str(data["name"])
    return skill_path.name


def _action(adapter: str, source: Path, destination: Path) -> InstallAction:
    if (
        destination.is_symlink()
        and destination.exists()
        and destination.resolve() == source.resolve()
    ):
        state = f"symlink:{source}"
        return InstallAction(
            adapter, str(source), str(destination), "keep", "入口已正确。", state, state
        )
    if destination.exists() or destination.is_symlink():
        return InstallAction(
            adapter,
            str(source),
            str(destination),
            "conflict",
            "目标已存在且不属于本计划。",
            "occupied",
            "unchanged",
        )
    return InstallAction(
        adapter,
        str(source),
        str(destination),
        "create",
        "创建项目内 Canary Skill 入口。",
        "missing",
        f"symlink:{source}",
    )


def create_install_plan(
    root: Path,
    skill_path: Path,
    project: Path,
    *,
    scope: str = "project",
    profile_name: str | None = None,
) -> InstallPlan:
    del profile_name
    if scope != "project":
        raise SystemExit(
            "独立 Skill Engineering 只执行 project canary;Profile/Global 请交给 Agent Skill Hub。"
        )
    source = skill_path.expanduser().resolve()
    project = project.expanduser().resolve()
    name = _skill_name(source)
    actions = [
        _action(adapter, source, project / entrypoint / name)
        for adapter, entrypoint in DEFAULT_ENTRYPOINTS.items()
    ]
    plan = InstallPlan(
        id=new_id("install"),
        scope="project",
        project=str(project),
        profile=None,
        actions=actions,
        conflicts=[item.destination for item in actions if item.action == "conflict"],
        security_gate=("blocked" if doctor_skill(source, profile="team").fail_count else "pass"),
        source_fingerprints={str(source): fingerprint_path(source)},
        target_fingerprints={
            item.destination: fingerprint_path(Path(item.destination)) for item in actions
        },
        rollback_summary="只撤销本次创建且未漂移的项目内 Canary 链接。",
        verification_commands=[f"skill-engineering doctor {source} --profile team"],
        requires_global_approval=False,
    )
    plan.plan_hash = payload_hash(asdict(plan), exclude={"plan_hash", "approval"})
    save_install_plan(root, plan)
    return plan


def _validate_plan(plan: InstallPlan) -> None:
    if plan.plan_hash != payload_hash(asdict(plan), exclude={"plan_hash", "approval"}):
        raise SystemExit("Canary 安装计划内容已变化,请重新生成。")
    for raw, expected in plan.source_fingerprints.items():
        if fingerprint_path(Path(raw)) != expected:
            raise SystemExit(f"Canary source 已漂移:{raw}")
    for raw, expected in plan.target_fingerprints.items():
        if fingerprint_path(Path(raw)) != expected:
            raise SystemExit(f"Canary 目标入口已漂移:{raw}")


def apply_install_plan(
    root: Path,
    plan_id: str,
    *,
    approved: bool,
    global_approved: bool = False,
    approval_source: str = "explicit_cli_apply",
) -> ChangeRecord:
    del global_approved
    if not approved:
        raise SystemExit("尚未明确批准 Canary 安装。")
    plan = load_install_plan(root, plan_id)
    _validate_plan(plan)
    if plan.security_gate != "pass" or plan.conflicts:
        raise SystemExit("Canary 安装被安全门禁或目标冲突阻断。")
    plan.approval = {
        "status": "approved",
        "source": approval_source,
        "approved_at": now_iso(),
    }
    save_install_plan(root, plan)
    created: list[dict[str, str]] = []
    unchanged: list[dict[str, str]] = []
    try:
        for action in plan.actions:
            item = {"path": action.destination, "source": action.source}
            if action.action == "keep":
                unchanged.append(item)
                continue
            destination = Path(action.destination)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.symlink_to(Path(action.source), target_is_directory=True)
            created.append(item)
    except BaseException:
        for item in reversed(created):
            path = Path(item["path"])
            if path.is_symlink() and path.resolve() == Path(item["source"]).resolve():
                path.unlink()
        raise
    checks = [_check(item) for item in created + unchanged]
    status = "verified" if checks and all(item["ok"] for item in checks) else "verification_failed"
    record = ChangeRecord(
        id=new_id("change"),
        plan_id=plan.id,
        plan_hash=plan.plan_hash,
        project=plan.project,
        scope=plan.scope,
        created=created,
        unchanged=unchanged,
        status=status,
        warnings=[],
        verification={"status": status, "checks": checks},
    )
    save_change_record(root, record)
    return record


def _check(item: dict[str, str]) -> dict[str, Any]:
    path = Path(item["path"])
    source = Path(item["source"])
    return {
        "path": str(path),
        "source": str(source),
        "ok": path.is_symlink() and path.exists() and path.resolve() == source.resolve(),
    }


def verify_change_record(root: Path, record_id: str) -> VerificationRecord:
    record = load_change_record(root, record_id)
    checks = [_check(item) for item in record.created + record.unchanged]
    status = "verified" if checks and all(item["ok"] for item in checks) else "drifted"
    value = VerificationRecord(
        id=new_id("verify"),
        change_record_id=record.id,
        status=status,
        checks=checks,
        warnings=[] if status == "verified" else ["Canary 入口已经漂移。"],
        undo_available=status == "verified" and bool(record.created) and not record.rolled_back_at,
    )
    save_verification_record(root, value)
    return value


def undo_change_record(root: Path, record_id: str) -> ChangeRecord:
    record = load_change_record(root, record_id)
    if record.rolled_back_at:
        return record
    verification = verify_change_record(root, record_id)
    if not verification.undo_available:
        raise SystemExit("Canary 入口已漂移或没有可撤销入口。")
    for item in reversed(record.created):
        path = Path(item["path"])
        if not _check(item)["ok"]:
            raise SystemExit(f"Canary 入口已变化,停止撤销:{path}")
        path.unlink()
    record.status = "rolled_back"
    record.rolled_back_at = now_iso()
    save_change_record(root, record)
    return record

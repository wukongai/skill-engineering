"""Deterministic maintenance planning, gates, records, verification, and undo."""

from __future__ import annotations

import os
import re
import shutil
import tempfile
import uuid
from dataclasses import asdict
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from .journey import (
    BuildFile,
    BuildPlan,
    MaintenanceRecord,
    fingerprint_path,
    list_maintenance_records,
    load_maintenance_record,
    local_state_root,
    new_id,
    now_iso,
    payload_hash,
    save_build_plan,
    save_maintenance_record,
)
from .skill_doctor import doctor_skill
from .skill_lint import lint_skill


ROOT_CAUSE_LAYERS = {
    "trigger",
    "interface",
    "state",
    "script",
    "style",
    "long-task",
    "install",
    "structure",
    "test",
}
PROFILES = {"personal", "team", "production"}
IGNORED_PARTS = {".git", ".skill-engineering", "__pycache__", ".pytest_cache", ".ruff_cache"}
GATE_TERMS = ("门禁", "CRITICAL", "禁止", "绝对禁止", "硬门禁", "红线")
INCIDENT_RE = re.compile(r"本日实测|踩坑|事故|失败\s*\d*\s*次|实证灾难|复盘")


def _safe_relative(raw: str) -> PurePosixPath:
    value = PurePosixPath(raw)
    if value.is_absolute() or not value.parts or ".." in value.parts or "." in value.parts:
        raise SystemExit(f"维护计划包含不安全相对路径:{raw}")
    if IGNORED_PARTS.intersection(value.parts):
        raise SystemExit(f"维护计划不得操作本机状态或缓存路径:{raw}")
    return value


def _iter_files(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and not IGNORED_PARTS.intersection(path.relative_to(root).parts)
    )


def _read_utf8(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise SystemExit(f"候选文件不是可审查 UTF-8 文本:{path}\n{exc}") from exc


def _description_chars(skill_md: Path) -> int:
    if not skill_md.is_file():
        return 0
    text = _read_utf8(skill_md)
    if not text.startswith("---"):
        return 0
    parts = text.split("---", 2)
    if len(parts) < 3:
        return 0
    try:
        data = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return 0
    return len(str(data.get("description") or "")) if isinstance(data, dict) else 0


def _instruction_files(root: Path) -> list[Path]:
    result: list[Path] = []
    for path in _iter_files(root):
        relative = path.relative_to(root)
        if relative.parts[0] in {"tests", "assets"}:
            continue
        if path.suffix.lower() in {".md", ".yaml", ".yml"}:
            result.append(path)
    return result


def _duplicate_instruction_lines(root: Path) -> int:
    counts: dict[str, int] = {}
    for path in _instruction_files(root):
        if path.suffix.lower() != ".md":
            continue
        for raw in _read_utf8(path).splitlines():
            line = re.sub(r"^\s*(?:[-*+] |\d+[.)]\s+|#+\s*)", "", raw).strip().lower()
            if len(line) < 24 or line.startswith(("```", "![", "http")):
                continue
            normalized = re.sub(r"\s+", " ", line)
            counts[normalized] = counts.get(normalized, 0) + 1
    return sum(count - 1 for count in counts.values() if count > 1)


def complexity_metrics(root: Path, *, retained_legacy_files: int = 0) -> dict[str, int]:
    skill_md = root / "SKILL.md"
    root_text = _read_utf8(skill_md) if skill_md.is_file() else ""
    return {
        "skill_md_lines": len(root_text.splitlines()),
        "description_chars": _description_chars(skill_md),
        "gate_terms": sum(root_text.count(term) for term in GATE_TERMS),
        "incident_terms": len(INCIDENT_RE.findall(root_text)),
        "instruction_files": len(_instruction_files(root)),
        "total_files": len(_iter_files(root)),
        "duplicate_instruction_lines": _duplicate_instruction_lines(root),
        "retained_legacy_files": retained_legacy_files,
    }


def _delta(before: dict[str, int], after: dict[str, int]) -> dict[str, int]:
    return {key: after.get(key, 0) - before.get(key, 0) for key in sorted(set(before) | set(after))}


def _finding(rule_id: str, level: str, message: str, hint: str) -> dict[str, str]:
    return {"rule_id": rule_id, "level": level, "message": message, "hint": hint}


def _audit_tree(path: Path, profile: str) -> dict[str, Any]:
    lint = lint_skill(path)
    doctor = doctor_skill(path, profile=profile)
    return {
        "status": "pass" if lint.error_count == 0 and doctor.fail_count == 0 else "blocked",
        "lint": {
            "errors": lint.error_count,
            "warnings": lint.warn_count,
            "issues": [asdict(issue) for issue in lint.issues],
        },
        "doctor": {
            "fails": doctor.fail_count,
            "warnings": doctor.warn_count,
            "score": doctor.score.total if doctor.score else None,
            "grade": doctor.score.grade if doctor.score else None,
            "issues": [asdict(issue) for issue in doctor.issues],
        },
    }


def _copy_effective_tree(
    target: Path, candidate: Path, destination: Path, deletions: list[str]
) -> None:
    shutil.copytree(
        target,
        destination,
        dirs_exist_ok=True,
        symlinks=True,
        ignore=shutil.ignore_patterns(*IGNORED_PARTS),
    )
    for source in _iter_files(candidate):
        relative = source.relative_to(candidate)
        dest = destination / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
    for raw in deletions:
        relative = _safe_relative(raw)
        dest = destination.joinpath(*relative.parts)
        if dest.is_file() or dest.is_symlink():
            dest.unlink()
        elif dest.exists():
            raise SystemExit(f"显式删除只支持文件:{raw}")


def _plan_hash(plan: BuildPlan) -> str:
    return payload_hash(asdict(plan), exclude={"plan_hash", "applied", "record_id"})


def create_improvement_plan(
    root: Path,
    target: Path,
    candidate: Path,
    *,
    failure_mode: str = "",
    root_cause_layer: str = "",
    expected_behavior: str = "",
    regression_cases: list[str] | None = None,
    no_regression_reason: str = "",
    profile: str = "team",
    deletions: list[str] | None = None,
) -> BuildPlan:
    target = target.expanduser().resolve()
    candidate = candidate.expanduser().resolve()
    regression_cases = regression_cases or []
    deletions = list(dict.fromkeys(_safe_relative(item).as_posix() for item in (deletions or [])))
    if not (target / "SKILL.md").is_file():
        raise SystemExit(f"改进目标不是有效 Skill:{target}")
    if not (candidate / "SKILL.md").is_file():
        raise SystemExit(f"候选目录不是有效 Skill:{candidate}")
    if target == candidate:
        raise SystemExit("改进候选目录必须与目标目录分开,以便生成安全 diff。")
    if candidate.is_relative_to(target) or target.is_relative_to(candidate):
        raise SystemExit("改进候选目录与目标目录不得互相嵌套。")
    if profile not in PROFILES:
        raise SystemExit(f"未知维护 profile:{profile}")
    if root_cause_layer and root_cause_layer not in ROOT_CAUSE_LAYERS:
        raise SystemExit(f"未知根因层级:{root_cause_layer}")
    for raw in deletions:
        relative = _safe_relative(raw)
        if relative.as_posix() == "SKILL.md":
            raise SystemExit("维护计划不得删除 SKILL.md。")
        path = target.joinpath(*relative.parts)
        if path.is_symlink() or not path.is_file():
            raise SystemExit(f"显式删除目标不是现有文件:{raw}")

    files: list[BuildFile] = []
    candidate_relatives: set[str] = set()
    for source in _iter_files(candidate):
        if source.is_symlink():
            raise SystemExit(f"候选目录不得用 symlink 覆盖 Skill 文件:{source}")
        relative = source.relative_to(candidate)
        candidate_relatives.add(relative.as_posix())
        content = _read_utf8(source)
        destination = target / relative
        if destination.is_symlink():
            raise SystemExit(f"维护闭环不直接覆盖 Skill 内部 symlink:{destination}")
        current = _read_utf8(destination) if destination.is_file() else None
        if current == content:
            continue
        files.append(
            BuildFile(
                relative.as_posix(),
                content,
                "更新已有文件。" if current is not None else "增加候选方案明确声明的新文件。",
            )
        )

    deletion_set = set(deletions)
    retained = [
        path.relative_to(target).as_posix()
        for path in _iter_files(target)
        if path.relative_to(target).as_posix() not in candidate_relatives
        and path.relative_to(target).as_posix() not in deletion_set
    ]

    with tempfile.TemporaryDirectory(prefix="skill-engineering-maint-") as temp_dir:
        effective = Path(temp_dir) / "effective"
        _copy_effective_tree(target, candidate, effective, deletions)
        before = complexity_metrics(target)
        after = complexity_metrics(effective, retained_legacy_files=len(retained))
        delta = _delta(before, after)
        findings: list[dict[str, str]] = []

        if (
            not failure_mode.strip()
            or not expected_behavior.strip()
            or not root_cause_layer.strip()
        ):
            findings.append(
                _finding(
                    "MAINT106",
                    "FAIL",
                    "维护意图不完整:需要失败模式、根因层级和预期行为。",
                    "补齐本次为什么改、应该改哪一层以及修改后必须成立的行为。",
                )
            )
        missing_cases: list[str] = []
        for raw in regression_cases:
            relative = _safe_relative(raw)
            if not effective.joinpath(*relative.parts).is_file():
                missing_cases.append(raw)
        if missing_cases:
            findings.append(
                _finding(
                    "MAINT106",
                    "FAIL",
                    f"回归用例不存在:{', '.join(missing_cases)}",
                    "在候选目录加入用例,或修正 --regression-case 相对路径。",
                )
            )
        if not regression_cases:
            if not no_regression_reason.strip() or profile == "production":
                findings.append(
                    _finding(
                        "MAINT106",
                        "FAIL",
                        "本次修改缺少回归用例。"
                        if profile == "production"
                        else "缺少回归用例或明确的不适用说明。",
                        "提供 --regression-case;personal/team 仅在确实不适用时可提供 --no-regression-reason。",
                    )
                )
            else:
                findings.append(
                    _finding(
                        "MAINT106",
                        "WARN",
                        f"本次修改使用无回归用例说明:{no_regression_reason.strip()}",
                        "高风险或可复现失败出现后应尽快固化回归用例。",
                    )
                )
        if not files and not deletions:
            findings.append(
                _finding("MAINT108", "FAIL", "候选方案没有任何增删改。", "检查候选目录或删除列表。")
            )
        if delta["skill_md_lines"] > 10:
            findings.append(
                _finding(
                    "MAINT101",
                    "WARN",
                    f"根 SKILL.md 增加 {delta['skill_md_lines']} 行。",
                    "确认新增内容属于稳定接口;事故细节应移到 references/tests。",
                )
            )
        if delta["gate_terms"] > 0:
            level = "FAIL" if profile == "production" and delta["incident_terms"] > 0 else "WARN"
            findings.append(
                _finding(
                    "MAINT102",
                    level,
                    f"根入口新增 {delta['gate_terms']} 个门禁/禁令词。",
                    "优先把约束落实到脚本、contract、state 或回归用例。",
                )
            )
        if delta["incident_terms"] > 0:
            findings.append(
                _finding(
                    "MAINT103",
                    "FAIL" if profile == "production" else "WARN",
                    f"根入口新增 {delta['incident_terms']} 处事故/复盘措辞。",
                    "把事故过程移到工程记录,根入口只保留稳定规则。",
                )
            )
        if delta["duplicate_instruction_lines"] > 0:
            findings.append(
                _finding(
                    "MAINT104",
                    "WARN",
                    f"跨文件重复长指令增加 {delta['duplicate_instruction_lines']} 条。",
                    "保留单一事实源,其他位置改为路由引用。",
                )
            )
        if retained:
            findings.append(
                _finding(
                    "MAINT105",
                    "WARN",
                    f"候选未包含 {len(retained)} 个现有文件;默认保留,不会静默删除。",
                    "确认仍需保留;废弃文件使用显式 --delete。",
                )
            )

        audit = _audit_tree(effective, profile)
        if audit["status"] != "pass":
            findings.append(
                _finding(
                    "MAINT107",
                    "FAIL",
                    "effective candidate 未通过 lint/Doctor 预检。",
                    "先修复 FAIL,重新生成维护计划。",
                )
            )
        blocked = any(item["level"] == "FAIL" for item in findings)
        preflight = {
            "status": "blocked" if blocked else "pass",
            "audit": audit,
            "finding_counts": {
                "fail": sum(item["level"] == "FAIL" for item in findings),
                "warn": sum(item["level"] == "WARN" for item in findings),
            },
        }

    plan = BuildPlan(
        id=new_id("improve"),
        target=str(target),
        skill_name=target.name,
        kind="existing",
        recommended_scope="unchanged",
        files=files,
        omitted=[],
        warnings=[item["message"] for item in findings],
        verification_commands=["skill-engineering verify-improvement --record <record-id>"],
        target_fingerprint=fingerprint_path(target),
        operation="improve",
        candidate=str(candidate),
        candidate_fingerprint=fingerprint_path(candidate),
        failure_mode=failure_mode.strip(),
        root_cause_layer=root_cause_layer.strip(),
        expected_behavior=expected_behavior.strip(),
        regression_cases=regression_cases,
        no_regression_reason=no_regression_reason.strip(),
        profile=profile,
        deletions=deletions,
        retained_legacy_files=retained,
        complexity={"before": before, "after": after, "delta": delta},
        findings=findings,
        preflight=preflight,
    )
    plan.plan_hash = _plan_hash(plan)
    save_build_plan(root, plan)
    return plan


def _restore_from_backup(record: MaintenanceRecord) -> None:
    target = Path(record.target)
    backup = Path(record.backup_dir) / "files"
    for action in reversed(record.actions):
        relative = _safe_relative(action["path"])
        destination = target.joinpath(*relative.parts)
        if action["action"] == "create":
            if destination.is_file() or destination.is_symlink():
                destination.unlink()
        else:
            source = backup.joinpath(*relative.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            if not source.is_file():
                raise SystemExit(f"维护备份缺失:{source}")
            temp = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.tmp")
            try:
                temp.write_bytes(source.read_bytes())
                os.replace(temp, destination)
            finally:
                if temp.exists():
                    temp.unlink()
    for directory in sorted(
        (path for path in target.rglob("*") if path.is_dir()),
        key=lambda item: len(item.parts),
        reverse=True,
    ):
        if not any(directory.iterdir()):
            directory.rmdir()


def apply_improvement_plan(root: Path, plan: BuildPlan) -> MaintenanceRecord:
    if plan.operation != "improve":
        raise SystemExit("只有 improve plan 可以进入维护闭环。")
    if _plan_hash(plan) != plan.plan_hash:
        raise SystemExit("维护计划内容或 plan hash 已漂移,请重新生成计划。")
    target = Path(plan.target)
    candidate = Path(plan.candidate or "")
    if fingerprint_path(target) != plan.target_fingerprint:
        raise SystemExit("维护计划已过期:目标 Skill 发生变化,请重新生成。")
    if fingerprint_path(candidate) != plan.candidate_fingerprint:
        raise SystemExit("维护计划已过期:候选 Skill 发生变化,请重新生成。")
    if plan.preflight.get("status") != "pass":
        raise SystemExit("维护计划未通过 preflight,不能应用。")

    record_id = new_id("maintenance")
    backup_dir = local_state_root(root) / "maintenance-backups" / record_id
    backup_files = backup_dir / "files"
    actions: list[dict[str, Any]] = []
    file_map = {item.relative_path: item for item in plan.files}
    for relative_path, item in file_map.items():
        relative = _safe_relative(relative_path)
        destination = target.joinpath(*relative.parts)
        action = "update" if destination.is_file() else "create"
        actions.append(
            {
                "path": relative_path,
                "action": action,
                "before_fingerprint": fingerprint_path(destination),
                "after_fingerprint": "",
            }
        )
    for raw in plan.deletions:
        relative = _safe_relative(raw)
        destination = target.joinpath(*relative.parts)
        actions.append(
            {
                "path": raw,
                "action": "delete",
                "before_fingerprint": fingerprint_path(destination),
                "after_fingerprint": "",
            }
        )

    for action in actions:
        if action["action"] not in {"update", "delete"}:
            continue
        relative = _safe_relative(action["path"])
        source = target.joinpath(*relative.parts)
        if not source.is_file():
            raise SystemExit(f"维护目标文件已不存在:{source}")
        destination = backup_files.joinpath(*relative.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())

    record = MaintenanceRecord(
        id=record_id,
        plan_id=plan.id,
        plan_hash=plan.plan_hash,
        target=str(target),
        candidate=str(candidate),
        failure_mode=plan.failure_mode,
        root_cause_layer=plan.root_cause_layer,
        expected_behavior=plan.expected_behavior,
        regression_cases=plan.regression_cases,
        no_regression_reason=plan.no_regression_reason,
        profile=plan.profile,
        actions=actions,
        backup_dir=str(backup_dir),
        before_fingerprint=plan.target_fingerprint,
        after_fingerprint="",
        complexity=plan.complexity,
        preflight=plan.preflight,
        postflight={},
        status="applying",
        verification={},
        undo_available=False,
    )

    try:
        for item in plan.files:
            relative = _safe_relative(item.relative_path)
            destination = target.joinpath(*relative.parts)
            if destination.exists() and not destination.is_file():
                raise SystemExit(f"维护目标被非文件占用:{destination}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            temp = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.tmp")
            try:
                temp.write_text(item.content, encoding="utf-8")
                os.replace(temp, destination)
            finally:
                if temp.exists():
                    temp.unlink()
        for raw in plan.deletions:
            relative = _safe_relative(raw)
            destination = target.joinpath(*relative.parts)
            if not destination.is_file():
                raise SystemExit(f"显式删除目标已漂移:{destination}")
            destination.unlink()
        for action in actions:
            relative = _safe_relative(action["path"])
            action["after_fingerprint"] = fingerprint_path(target.joinpath(*relative.parts))
        postflight = _audit_tree(target, plan.profile)
        record.postflight = postflight
        if postflight["status"] != "pass":
            record.status = "rolled_back"
            _restore_from_backup(record)
            record.after_fingerprint = fingerprint_path(target)
            record.verification = {"status": "failed", "reason": "MAINT110 postflight blocked"}
            save_maintenance_record(root, record)
            raise SystemExit("写后验证失败,本次修改已自动回滚。")
        record.after_fingerprint = fingerprint_path(target)
        record.status = "applied"
        record.verification = {"status": "passed", "checked_at": now_iso(), "audit": postflight}
        record.undo_available = True
        save_maintenance_record(root, record)
        plan.applied = True
        plan.record_id = record.id
        save_build_plan(root, plan)
        return record
    except BaseException:
        if record.status != "rolled_back":
            try:
                _restore_from_backup(record)
            finally:
                record.status = "rolled_back"
                record.after_fingerprint = fingerprint_path(target)
                record.verification = {
                    "status": "failed",
                    "reason": "apply exception; restored backup",
                }
                save_maintenance_record(root, record)
        raise


def verify_improvement(root: Path, record_id: str) -> MaintenanceRecord:
    record = load_maintenance_record(root, record_id)
    current = fingerprint_path(Path(record.target))
    drifted = current != record.after_fingerprint
    audit = _audit_tree(Path(record.target), record.profile) if not drifted else {}
    passed = record.status == "applied" and not drifted and audit.get("status") == "pass"
    record.verification = {
        "status": "passed" if passed else "failed",
        "checked_at": now_iso(),
        "drifted": drifted,
        "audit": audit,
    }
    record.undo_available = passed
    save_maintenance_record(root, record)
    return record


def undo_improvement(root: Path, record_id: str) -> MaintenanceRecord:
    record = load_maintenance_record(root, record_id)
    if record.status != "applied":
        raise SystemExit(f"维护记录当前不可撤销:{record.status}")
    if fingerprint_path(Path(record.target)) != record.after_fingerprint:
        record.undo_available = False
        record.verification = {"status": "failed", "checked_at": now_iso(), "drifted": True}
        save_maintenance_record(root, record)
        raise SystemExit("目标 Skill 已发生漂移,不能安全撤销本次修改。")
    _restore_from_backup(record)
    restored = fingerprint_path(Path(record.target))
    if restored != record.before_fingerprint:
        raise SystemExit("撤销后指纹与修改前不一致,请检查维护备份。")
    record.status = "undone"
    record.undo_available = False
    record.undone_at = now_iso()
    record.verification = {"status": "undone", "checked_at": record.undone_at, "restored": True}
    save_maintenance_record(root, record)
    return record


def maintenance_history(root: Path, target: Path | None = None) -> list[MaintenanceRecord]:
    records = list_maintenance_records(root)
    if target is None:
        return records
    resolved = str(target.expanduser().resolve())
    return [
        record for record in records if str(Path(record.target).expanduser().resolve()) == resolved
    ]


def format_improvement_plan(plan: BuildPlan) -> str:
    from .interaction import UserFeedback

    blocked = plan.preflight.get("status") != "pass"
    delta = plan.complexity.get("delta", {})
    impact = [
        f"目标：{plan.target}",
        f"将修改 {len(plan.files)} 个文件，显式删除 {len(plan.deletions)} 个文件。",
        f"根入口预计变化 {delta.get('skill_md_lines', 0):+d} 行。",
        "目前尚未写入任何文件。",
    ]
    if plan.findings:
        impact.append(f"预检发现 {len(plan.findings)} 个需要处理的问题。")
    return UserFeedback(
        status="blocked" if blocked else "awaiting-approval",
        result=(
            "改进方案没有通过写入前检查，当前不能应用。"
            if blocked
            else f"{plan.skill_name} 的改进方案已经准备好。"
        ),
        impact=impact,
        next_action=(
            "先修复预检问题，再重新生成方案。"
            if blocked
            else "确认实际修改范围后，再决定是否应用。"
        ),
        decision="是否继续应用这次修改？" if not blocked else "",
        technical_details=[f"plan={plan.id}", f"root_cause={plan.root_cause_layer}"],
    ).render()


def format_maintenance_record(record: MaintenanceRecord) -> str:
    from .interaction import UserFeedback

    verification = record.verification.get("status", "unknown")
    if record.status == "undone":
        return UserFeedback(
            status="completed",
            result="本次 Skill 修改已经撤销，修改前的内容已恢复。",
            impact=[f"只撤销了本次记录拥有的 {len(record.actions)} 个文件动作。"],
            next_action="如需继续改进，请重新生成候选和修改方案。",
            technical_details=[f"record={record.id}"],
        ).render()
    if record.status == "applied" and verification == "passed":
        return UserFeedback(
            status="completed",
            result="Skill 修改已经应用并验证通过。",
            impact=[
                f"本次完成 {len(record.actions)} 个文件动作。",
                "当前内容与已验证的候选一致。",
                f"可以安全撤销：{'是' if record.undo_available else '否'}。",
            ],
            next_action="继续用真实任务观察效果；需要时可撤销本次修改。",
            technical_details=[f"record={record.id}"],
        ).render()
    restored = record.status == "rolled_back"
    return UserFeedback(
        status="incomplete",
        result="这次 Skill 修改整体尚未完成。",
        impact=[
            "写入后验证没有完整通过。",
            "系统已经恢复修改前内容。" if restored else "请先确认目标是否已经安全恢复。",
        ],
        next_action="检查失败原因，修复候选后重新生成修改方案。",
        technical_details=[f"record={record.id}", f"status={record.status}"],
    ).render()

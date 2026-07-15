"""Shared versioned contracts and local journey persistence for Skill Engineering.

This module intentionally contains no product decision logic. Skill Engineering, CLI,
and Workbench exchange these contracts so the behavior is implemented once.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TypeVar


SCHEMA_VERSION = "1"
LOCAL_STATE_DIR = ".skill-engineering"
IGNORED_FINGERPRINT_PARTS = {
    ".git",
    ".skill-engineering",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_id(prefix: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{prefix}-{stamp}-{uuid.uuid4().hex[:8]}"


def local_state_root(root: Path) -> Path:
    return root / LOCAL_STATE_DIR


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise SystemExit(f"本机状态不存在: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"本机状态无法读取: {path}\n{exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"本机状态格式无效: {path}")
    if str(data.get("schema_version")) != SCHEMA_VERSION:
        raise SystemExit(
            f"不支持的本机状态版本: {path} "
            f"(found={data.get('schema_version')!r}, expected={SCHEMA_VERSION})"
        )
    return data


def _validate_identifier(identifier: str) -> None:
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,127}", identifier, re.IGNORECASE):
        raise SystemExit(f"本机状态 id 格式无效:{identifier}")


def fingerprint_path(path: Path) -> str:
    """Return a stable fingerprint without following unrelated symlink trees."""
    digest = hashlib.sha256()
    path = path.expanduser()
    if not path.exists() and not path.is_symlink():
        digest.update(b"missing")
        digest.update(str(path).encode("utf-8"))
        return digest.hexdigest()
    if path.is_symlink():
        digest.update(b"symlink")
        digest.update(str(path.readlink()).encode("utf-8"))
        return digest.hexdigest()
    if path.is_file():
        digest.update(b"file")
        digest.update(path.name.encode("utf-8"))
        try:
            digest.update(path.read_bytes())
        except OSError as exc:
            digest.update(f"unreadable:{exc}".encode("utf-8"))
        return digest.hexdigest()

    digest.update(b"directory")
    for item in sorted(path.rglob("*"), key=lambda value: str(value.relative_to(path))):
        relative = item.relative_to(path)
        if IGNORED_FINGERPRINT_PARTS.intersection(relative.parts):
            continue
        digest.update(str(relative).encode("utf-8"))
        if item.is_symlink():
            digest.update(b"symlink")
            digest.update(str(item.readlink()).encode("utf-8"))
        elif item.is_file():
            digest.update(b"file")
            try:
                digest.update(item.read_bytes())
            except OSError as exc:
                digest.update(f"unreadable:{exc}".encode("utf-8"))
        elif item.is_dir():
            digest.update(b"directory")
    return digest.hexdigest()


def payload_hash(payload: dict[str, Any], *, exclude: set[str] | None = None) -> str:
    excluded = exclude or set()
    canonical = {key: value for key, value in payload.items() if key not in excluded}
    raw = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass
class DecisionReport:
    id: str
    brief: str
    verdict: str
    confidence: str
    recommended_kind: str | None
    recommended_scope: str | None
    reasons: list[str]
    evidence: list[str]
    alternatives: list[dict[str, str]]
    unknowns: list[str]
    next_actions: list[dict[str, str]]
    overlap_candidates: list[dict[str, Any]] = field(default_factory=list)
    semantic_hints: list[str] = field(default_factory=list)
    schema_version: str = SCHEMA_VERSION
    created_at: str = field(default_factory=now_iso)


@dataclass
class BuildFile:
    relative_path: str
    content: str
    reason: str


@dataclass
class BuildPlan:
    id: str
    target: str
    skill_name: str
    kind: str
    recommended_scope: str
    files: list[BuildFile]
    omitted: list[dict[str, str]]
    warnings: list[str]
    verification_commands: list[str]
    target_fingerprint: str
    applied: bool = False
    operation: str = "create"  # create | improve
    candidate: str | None = None
    candidate_fingerprint: str = ""
    failure_mode: str = ""
    root_cause_layer: str = ""
    expected_behavior: str = ""
    regression_cases: list[str] = field(default_factory=list)
    no_regression_reason: str = ""
    profile: str = "team"
    deletions: list[str] = field(default_factory=list)
    retained_legacy_files: list[str] = field(default_factory=list)
    complexity: dict[str, Any] = field(default_factory=dict)
    findings: list[dict[str, Any]] = field(default_factory=list)
    preflight: dict[str, Any] = field(default_factory=dict)
    postflight: dict[str, Any] = field(default_factory=dict)
    plan_hash: str = ""
    record_id: str | None = None
    schema_version: str = SCHEMA_VERSION
    created_at: str = field(default_factory=now_iso)


@dataclass
class InstallRecommendation:
    id: str
    skill_path: str
    project: str
    recommended_scope: str
    recommended_profile: str | None
    confidence: str
    reasons: list[str]
    why_not_global: list[str]
    conflicts: list[dict[str, Any]]
    route_cost: dict[str, Any]
    security_gate: str
    limitations: list[str]
    schema_version: str = SCHEMA_VERSION
    created_at: str = field(default_factory=now_iso)


@dataclass
class InstallAction:
    adapter: str
    source: str
    destination: str
    action: str  # create | keep | conflict
    reason: str
    before: str = ""
    after: str = ""


@dataclass
class InstallPlan:
    id: str
    scope: str
    project: str
    profile: str | None
    actions: list[InstallAction]
    conflicts: list[str]
    security_gate: str
    source_fingerprints: dict[str, str]
    target_fingerprints: dict[str, str]
    rollback_summary: str
    verification_commands: list[str]
    requires_global_approval: bool
    plan_hash: str = ""
    approval: dict[str, Any] = field(default_factory=lambda: {"status": "not_requested"})
    schema_version: str = SCHEMA_VERSION
    created_at: str = field(default_factory=now_iso)


@dataclass
class ChangeRecord:
    id: str
    plan_id: str
    plan_hash: str
    project: str
    scope: str
    created: list[dict[str, str]]
    unchanged: list[dict[str, str]]
    status: str
    warnings: list[str]
    verification: dict[str, Any]
    rolled_back_at: str | None = None
    schema_version: str = SCHEMA_VERSION
    created_at: str = field(default_factory=now_iso)


@dataclass
class VerificationRecord:
    id: str
    change_record_id: str
    status: str
    checks: list[dict[str, Any]]
    warnings: list[str]
    undo_available: bool
    schema_version: str = SCHEMA_VERSION
    created_at: str = field(default_factory=now_iso)


@dataclass
class MaintenanceRecord:
    id: str
    plan_id: str
    plan_hash: str
    target: str
    candidate: str
    failure_mode: str
    root_cause_layer: str
    expected_behavior: str
    regression_cases: list[str]
    no_regression_reason: str
    profile: str
    actions: list[dict[str, Any]]
    backup_dir: str
    before_fingerprint: str
    after_fingerprint: str
    complexity: dict[str, Any]
    preflight: dict[str, Any]
    postflight: dict[str, Any]
    status: str
    verification: dict[str, Any]
    undo_available: bool
    undone_at: str | None = None
    schema_version: str = SCHEMA_VERSION
    created_at: str = field(default_factory=now_iso)


@dataclass
class JourneySession:
    id: str
    intent: str
    goal: str
    stage: str
    status: str
    project: str | None = None
    skill_path: str | None = None
    answers: dict[str, Any] = field(default_factory=dict)
    completed_steps: list[str] = field(default_factory=list)
    pending_questions: list[str] = field(default_factory=list)
    artifacts: list[dict[str, str]] = field(default_factory=list)
    tool_results: list[dict[str, Any]] = field(default_factory=list)
    approval: dict[str, Any] = field(default_factory=lambda: {"status": "not_requested"})
    plan_id: str | None = None
    change_record_id: str | None = None
    next_action: str = ""
    schema_version: str = SCHEMA_VERSION
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)

    def handoff_summary(self) -> str:
        from .interaction import format_journey_feedback

        return format_journey_feedback(self)


T = TypeVar("T")


def _save_contract(root: Path, folder: str, identifier: str, value: Any) -> Path:
    _validate_identifier(identifier)
    path = local_state_root(root) / folder / f"{identifier}.json"
    _atomic_write_json(path, asdict(value))
    return path


def _load_contract(root: Path, folder: str, identifier: str, cls: type[T]) -> T:
    _validate_identifier(identifier)
    data = _load_json(local_state_root(root) / folder / f"{identifier}.json")
    return cls(**data)


def save_journey(root: Path, session: JourneySession) -> Path:
    session.updated_at = now_iso()
    return _save_contract(root, "journeys", session.id, session)


def load_journey(root: Path, session_id: str) -> JourneySession:
    return _load_contract(root, "journeys", session_id, JourneySession)


def list_journeys(root: Path) -> list[JourneySession]:
    folder = local_state_root(root) / "journeys"
    if not folder.is_dir():
        return []
    sessions: list[JourneySession] = []
    for path in sorted(folder.glob("*.json"), reverse=True):
        try:
            sessions.append(JourneySession(**_load_json(path)))
        except (SystemExit, TypeError):
            continue
    return sessions


def save_build_plan(root: Path, plan: BuildPlan) -> Path:
    return _save_contract(root, "build-plans", plan.id, plan)


def load_build_plan(root: Path, plan_id: str) -> BuildPlan:
    _validate_identifier(plan_id)
    data = _load_json(local_state_root(root) / "build-plans" / f"{plan_id}.json")
    data["files"] = [BuildFile(**item) for item in data.get("files", [])]
    return BuildPlan(**data)


def save_install_plan(root: Path, plan: InstallPlan) -> Path:
    return _save_contract(root, "plans", plan.id, plan)


def load_install_plan(root: Path, plan_id: str) -> InstallPlan:
    _validate_identifier(plan_id)
    data = _load_json(local_state_root(root) / "plans" / f"{plan_id}.json")
    data["actions"] = [InstallAction(**item) for item in data.get("actions", [])]
    return InstallPlan(**data)


def save_change_record(root: Path, record: ChangeRecord) -> Path:
    return _save_contract(root, "records", record.id, record)


def load_change_record(root: Path, record_id: str) -> ChangeRecord:
    return _load_contract(root, "records", record_id, ChangeRecord)


def list_change_records(root: Path) -> list[ChangeRecord]:
    folder = local_state_root(root) / "records"
    if not folder.is_dir():
        return []
    records: list[ChangeRecord] = []
    for path in sorted(folder.glob("*.json"), reverse=True):
        try:
            records.append(ChangeRecord(**_load_json(path)))
        except (SystemExit, TypeError):
            continue
    return records


def save_verification_record(root: Path, record: VerificationRecord) -> Path:
    return _save_contract(root, "verifications", record.id, record)


def load_verification_record(root: Path, record_id: str) -> VerificationRecord:
    return _load_contract(root, "verifications", record_id, VerificationRecord)


def save_maintenance_record(root: Path, record: MaintenanceRecord) -> Path:
    return _save_contract(root, "maintenance-records", record.id, record)


def load_maintenance_record(root: Path, record_id: str) -> MaintenanceRecord:
    return _load_contract(root, "maintenance-records", record_id, MaintenanceRecord)


def list_maintenance_records(root: Path) -> list[MaintenanceRecord]:
    folder = local_state_root(root) / "maintenance-records"
    if not folder.is_dir():
        return []
    records: list[MaintenanceRecord] = []
    for path in sorted(folder.glob("*.json"), reverse=True):
        try:
            records.append(MaintenanceRecord(**_load_json(path)))
        except (SystemExit, TypeError):
            continue
    return records

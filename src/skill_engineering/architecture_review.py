"""Deterministic validation of declared architecture evidence for maintenance.

This stage never executes candidate code or infers semantic correctness. Its
snapshot is embedded in the existing maintenance plan and protected by its hash.
"""

from __future__ import annotations

import json
import re
from itertools import groupby
from pathlib import Path
from typing import Any

from .authoring import _redact
from .journey import MaintenanceRecord, payload_hash


AREAS = {"ownership", "routing", "interfaces", "state", "failure", "rollback"}
METRIC_KEYS = {"skill_md_lines", "instruction_files", "duplicate_instruction_lines"}
BUDGET_KEYS = METRIC_KEYS | {"open_debt"}
MAX_INPUT_BYTES = 128 * 1024
MAX_TEXT_CHARS = 4000
MAX_ITEMS = 128
ID_RE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}")
FINGERPRINT_RE = re.compile(r"[a-f0-9]{64}")
CREDENTIAL_ASSIGNMENT_RE = re.compile(
    r"\b(?:[a-z0-9]+[_-])*(?:token|secret|api[_-]?key|private[_-]?key|password|passwd|cookie|session|credential)"
    r"(?:[_-][a-z0-9]+)*\b[\"']?\s*[:=]\s*\S+",
    re.IGNORECASE,
)


def _mapping(value: Any, label: str, required: set[str], optional: set[str] | None = None):
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise SystemExit(f"架构声明 {label} 必须是 object。")
    if set(value) - required - (optional or set()) or required - set(value):
        raise SystemExit(f"架构声明 {label} 含未知字段或缺少必填字段。")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > MAX_TEXT_CHARS:
        raise SystemExit(f"架构声明 {label} 必须是有长度上限的非空摘要。")
    if _redact(value) != value or CREDENTIAL_ASSIGNMENT_RE.search(value):
        raise SystemExit(f"架构声明 {label} 含原始凭证形态值,请先脱敏。")
    if any(ord(char) < 32 and char not in "\n\r\t" for char in value):
        raise SystemExit(f"架构声明 {label} 含非法控制字符。")
    return value.strip()


def _strings(value: Any, label: str, *, allowed: set[str] | None = None) -> list[str]:
    if not isinstance(value, list) or len(value) > MAX_ITEMS:
        raise SystemExit(f"架构声明 {label} 必须是有长度上限的字符串数组。")
    result = [_text(item, label) for item in value]
    if len(set(result)) != len(result) or (allowed is not None and set(result) - allowed):
        raise SystemExit(f"架构声明 {label} 含重复项或未知值。")
    return result


def _identifier(value: Any, label: str) -> str:
    result = _text(value, label)
    if not ID_RE.fullmatch(result):
        raise SystemExit(f"架构声明 {label} 必须是安全的稳定 ID。")
    return result


def _full_review(value: Any) -> dict[str, Any]:
    fields = {
        "target_fingerprint", "candidate_fingerprint", "effective_fingerprint",
        "checked_areas", "conclusion", "reviewer", "evidence_summary",
    }
    value = _mapping(value, "full_review", fields)
    result = {}
    for field in ("target_fingerprint", "candidate_fingerprint", "effective_fingerprint"):
        if not isinstance(value[field], str) or not FINGERPRINT_RE.fullmatch(value[field]):
            raise SystemExit(f"架构声明 full_review.{field} 必须是 SHA-256 指纹。")
        result[field] = value[field]
    result["checked_areas"] = _strings(value["checked_areas"], "checked_areas", allowed=AREAS)
    if value["conclusion"] not in ("pass", "changes_requested"):
        raise SystemExit("架构声明 full_review.conclusion 无效。")
    result["conclusion"] = value["conclusion"]
    for field in ("reviewer", "evidence_summary"):
        result[field] = _text(value[field], f"full_review.{field}")
    return result


def _debt_items(value: Any) -> list[dict[str, str]]:
    """Validate every debt and global ID uniqueness, independently of batch size."""
    if not isinstance(value, list):
        raise SystemExit("架构债务必须是数组。")
    cleaned = []
    ids: set[str] = set()
    for debt in value:
        debt = _mapping(debt, "debt item", {"id", "summary"})
        debt_id = _identifier(debt["id"], "debt.id")
        if debt_id in ids:
            raise SystemExit("架构债务含重复 ID。")
        ids.add(debt_id)
        cleaned.append({"id": debt_id, "summary": _text(debt["summary"], "debt.summary")})
    return cleaned


def _validate_declaration(value: Any) -> dict[str, Any]:
    required = {"schema_version", "requirement", "budgets", "debt", "resolved_debt_ids"}
    value = _mapping(value, "顶层", required, {"baseline_record_id", "full_review"})
    if value["schema_version"] != "1":
        raise SystemExit("架构声明 schema_version 必须是字符串 1。")
    requirement = _mapping(value["requirement"], "requirement", {
        "summary", "decision", "rationale", "owner", "replacement_plan",
        "protected_behaviors", "touched_boundaries",
    })
    if requirement["decision"] not in ("extend", "refactor", "split", "defer"):
        raise SystemExit("架构声明 requirement.decision 无效。")
    cleaned_requirement = {"decision": requirement["decision"]}
    for field in ("summary", "rationale", "owner", "replacement_plan"):
        cleaned_requirement[field] = _text(requirement[field], f"requirement.{field}")
    cleaned_requirement["protected_behaviors"] = _strings(
        requirement["protected_behaviors"], "protected_behaviors"
    )
    if not cleaned_requirement["protected_behaviors"]:
        raise SystemExit("架构声明必须列出应保护的行为。")
    cleaned_requirement["touched_boundaries"] = _strings(
        requirement["touched_boundaries"], "touched_boundaries", allowed=AREAS
    )
    budgets = _mapping(value["budgets"], "budgets", BUDGET_KEYS)
    if any(type(item) is not int or item < 0 for item in budgets.values()):
        raise SystemExit("架构声明预算必须是非负整数,不得使用布尔值。")
    debts = value["debt"]
    if not isinstance(debts, list) or len(debts) > MAX_ITEMS:
        raise SystemExit("架构声明 debt 必须是有长度上限的数组。")
    cleaned_debts = _debt_items(debts)
    resolved = _strings(value["resolved_debt_ids"], "resolved_debt_ids")
    for debt_id in resolved:
        _identifier(debt_id, "resolved_debt_ids")
    if {debt["id"] for debt in cleaned_debts}.intersection(resolved):
        raise SystemExit("架构声明不得同时新增和解决同一债务。")
    result = {
        "schema_version": "1", "requirement": cleaned_requirement,
        "budgets": dict(budgets), "debt": cleaned_debts, "resolved_debt_ids": resolved,
    }
    if "baseline_record_id" in value:
        result["baseline_record_id"] = _identifier(value["baseline_record_id"], "baseline_record_id")
    if "full_review" in value:
        result["full_review"] = _full_review(value["full_review"])
    return result


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise SystemExit("架构声明 JSON 含重复字段。")
        result[key] = value
    return result


def load_architecture_declaration(path: Path) -> dict[str, Any]:
    """Read bounded JSON, rejecting malformed or sensitive input before persistence."""
    try:
        with path.expanduser().resolve().open("rb") as source:
            raw = source.read(MAX_INPUT_BYTES + 1)
        if len(raw) > MAX_INPUT_BYTES:
            raise SystemExit("架构声明超过输入大小上限。")
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        raise SystemExit("架构声明必须是可读取的 UTF-8 JSON。") from exc
    return _validate_declaration(value)


def validate_architecture_snapshot(
    snapshot: Any,
    *,
    target_fingerprint: str,
    candidate_fingerprint: str,
    effective_fingerprint: str,
) -> None:
    """Require a frozen passing snapshot before maintenance can write anything.

    No declaration file or mutable history is reread here. Valid snapshots from
    the optional-review policy remain usable; missing review is never upgraded.
    """
    message = "维护架构审查快照缺失、无效或未通过;请补齐声明并重新生成预览。"
    try:
        required = {
            "schema_version", "status", "requirement_decision", "requirement", "baseline",
            "budgets", "complexity", "debt", "resolved_debt_ids", "whole_review",
            "input_fingerprints", "blocking_findings",
        }
        report = _mapping(snapshot, "架构快照", required,
                          {"current_structural_findings", "limitations"})
        if report["schema_version"] != "1" or report["status"] != "pass":
            raise SystemExit(message)
        if report["blocking_findings"] != []:
            raise SystemExit(message)
        inputs = _mapping(report["input_fingerprints"], "快照指纹",
                          {"target", "candidate", "effective", "declaration"})
        if any(not isinstance(item, str) or not FINGERPRINT_RE.fullmatch(item)
               for item in inputs.values()):
            raise SystemExit(message)
        expected = {"target": target_fingerprint, "candidate": candidate_fingerprint,
                    "effective": effective_fingerprint}
        if any(inputs[key] != value for key, value in expected.items()):
            raise SystemExit(message)
        whole = _mapping(report["whole_review"], "整体架构门",
                         {"required", "reasons", "status", "evidence"})
        reasons = _strings(whole["reasons"], "整体架构门触发原因", allowed={
            "baseline_missing", "boundary_changed", "budget_changed", "repeated_debt",
            "budget_exceeded", "history_ambiguous",
        })
        if type(whole["required"]) is not bool or whole["required"] != bool(reasons):
            raise SystemExit(message)
        declaration = {
            "schema_version": "1", "requirement": report["requirement"],
            "budgets": report["budgets"], "debt": [],
            "resolved_debt_ids": report["resolved_debt_ids"],
        }
        if whole["evidence"] is not None:
            declaration["full_review"] = whole["evidence"]
        cleaned = _validate_declaration(declaration)
        # Snapshot debt is cumulative, unlike one bounded external declaration.
        cleaned["debt"] = _debt_items(report["debt"])
        if {debt["id"] for debt in cleaned["debt"]}.intersection(cleaned["resolved_debt_ids"]):
            raise SystemExit(message)
        decision = cleaned["requirement"]["decision"]
        if decision not in {"extend", "refactor"} or report["requirement_decision"] != decision:
            raise SystemExit(message)
        baseline = _mapping(report["baseline"], "架构基线", {"status", "record_id"})
        if baseline["status"] == "selected":
            _identifier(baseline["record_id"], "baseline.record_id")
        elif baseline["status"] != "missing" or baseline["record_id"] is not None:
            raise SystemExit(message)
        metrics = _mapping(report["complexity"], "累计复杂度",
                           {"baseline", "cumulative_delta", "budget_exceeded"})
        exceeded = _strings(metrics["budget_exceeded"], "预算超限指标", allowed=BUDGET_KEYS)
        delta = metrics["cumulative_delta"]
        if delta is not None:
            delta = _mapping(delta, "累计增长", METRIC_KEYS)
            if any(type(value) is not int for value in delta.values()):
                raise SystemExit(message)
        if whole["status"] == "accepted":
            evidence = cleaned.get("full_review")
            if (
                not evidence or evidence["conclusion"] != "pass"
                or set(evidence["checked_areas"]) != AREAS
                or any(evidence[f"{key}_fingerprint"] != value for key, value in expected.items())
            ):
                raise SystemExit(message)
        elif whole["status"] == "not_required":
            if (
                whole["required"] or whole["evidence"] is not None or delta is None
                or baseline["status"] != "selected" or cleaned["requirement"]["touched_boundaries"]
                or exceeded or len(cleaned["debt"]) > cleaned["budgets"]["open_debt"]
                or any(delta[key] > cleaned["budgets"][key] for key in METRIC_KEYS)
            ):
                raise SystemExit(message)
        else:
            raise SystemExit(message)
    except SystemExit as exc:
        raise SystemExit(message) from exc


def _snapshot(record: MaintenanceRecord) -> dict[str, Any]:
    preflight = record.preflight
    value = preflight.get("architecture_review", {}) if isinstance(preflight, dict) else {}
    return value if isinstance(value, dict) else {}


def _valid_baseline(record: MaintenanceRecord) -> bool:
    report = _snapshot(record)
    whole = report.get("whole_review", {})
    inputs = report.get("input_fingerprints", {})
    metrics = record.complexity.get("after", {})
    if (
        record.status != "applied"
        or record.verification.get("status") != "passed"
        or record.verification.get("drifted") is not False
        or report.get("status") != "pass"
        or not isinstance(whole, dict)
        or whole.get("status") != "accepted"
        or not isinstance(inputs, dict)
        or inputs.get("effective") != record.after_fingerprint
        or not isinstance(metrics, dict)
        or not all(type(metrics.get(key)) is int for key in METRIC_KEYS)
    ):
        return False
    try:
        evidence = _full_review(whole.get("evidence"))
        budgets = _mapping(report.get("budgets"), "historical budgets", BUDGET_KEYS)
    except SystemExit:
        return False
    return (
        evidence["conclusion"] == "pass"
        and set(evidence["checked_areas"]) == AREAS
        and all(evidence[f"{key}_fingerprint"] == inputs.get(key)
                for key in ("target", "candidate", "effective"))
        and all(type(item) is int and item >= 0 for item in budgets.values())
    )


def _causal_order(records: list[MaintenanceRecord]) -> list[MaintenanceRecord] | None:
    """Order one timestamp batch only when fingerprints form a unique chain."""
    if len(records) < 2:
        return records
    if any(
        not isinstance(getattr(record, field, None), str)
        or not FINGERPRINT_RE.fullmatch(getattr(record, field))
        for record in records for field in ("before_fingerprint", "after_fingerprint")
    ):
        return None
    starts = [record for record in records if not any(
        previous is not record and previous.after_fingerprint == record.before_fingerprint
        for previous in records
    )]
    if len(starts) != 1:
        return None
    ordered = starts[:]
    remaining = [record for record in records if record is not starts[0]]
    while remaining:
        successors = [record for record in remaining
                      if record.before_fingerprint == ordered[-1].after_fingerprint]
        if len(successors) != 1:
            return None
        ordered.append(successors[0])
        remaining = [record for record in remaining if record is not successors[0]]
    return ordered


def _history_batches(records: list[MaintenanceRecord]):
    """Keep unknown same-second chronology explicit; random IDs are not clocks."""
    batches = []
    active = sorted((record for record in records if record.status == "applied"),
                    key=lambda record: record.created_at)
    for _, group in groupby(active, key=lambda record: record.created_at):
        same_time = list(group)
        ordered = _causal_order(same_time)
        batches.append((ordered if ordered is not None else same_time, ordered is None))
    return batches


def assess_architecture(
    *,
    declaration: dict[str, Any] | None,
    target: Path,
    target_fingerprint: str,
    candidate_fingerprint: str,
    effective_fingerprint: str,
    complexity: dict[str, Any],
    findings: list[dict[str, Any]],
    history: list[MaintenanceRecord],
) -> dict[str, Any]:
    """Assess declaration, history and measured metrics without running any code."""
    limitations = ["架构评审来自宿主/人工声明,不证明语义正确或真实任务行为通过。"]
    inputs = {"target": target_fingerprint, "candidate": candidate_fingerprint,
              "effective": effective_fingerprint}
    if declaration is None:
        return {
            "schema_version": "1", "status": "blocked", "input_fingerprints": inputs,
            "blocking_findings": ["缺少维护架构审查声明,请补齐声明并重新生成预览。"],
            "limitations": limitations,
        }
    declaration = _validate_declaration(declaration)
    inputs["declaration"] = payload_hash(declaration)
    current_target = target.expanduser().resolve()
    relevant = [record for record in history
                if Path(record.target).expanduser().resolve() == current_target]
    batches = _history_batches(relevant)
    valid = [record for batch, ambiguous in batches if not ambiguous
             for record in batch if _valid_baseline(record)]
    requested = declaration.get("baseline_record_id")
    baseline = next((record for record in relevant
                     if record.id == requested and _valid_baseline(record)), None) if requested else (
        valid[-1] if valid else None
    )
    blocking: list[str] = []
    if requested and baseline is None:
        blocking.append("显式架构基线不存在或不满足同目标、已验证和完整评审条件。")
    reasons = []
    if any(ambiguous for _, ambiguous in batches):
        reasons.append("history_ambiguous")
        limitations.append(
            "history_ambiguous：同秒维护记录的指纹因果顺序不唯一;保留已知债务,不推断债务已关闭。"
        )
    if baseline is None:
        reasons.append("baseline_missing")
    requirement = declaration["requirement"]
    decision = requirement["decision"]
    if decision in {"split", "defer"}:
        blocking.append("需求裁决要求拆分或延后,应建立独立计划后重新评审。")
    if requirement["touched_boundaries"]:
        reasons.append("boundary_changed")
    budgets = declaration["budgets"]
    baseline_metrics = baseline.complexity["after"] if baseline else None
    delta = {
        key: complexity["after"][key] - baseline_metrics[key] for key in sorted(METRIC_KEYS)
    } if baseline_metrics is not None else None
    exceeded = [key for key in sorted(METRIC_KEYS) if delta is not None and delta[key] > budgets[key]]
    if baseline and _snapshot(baseline)["budgets"] != budgets:
        reasons.append("budget_changed")
    debt_by_id: dict[str, dict[str, str]] = {}
    for batch, ambiguous in batches:
        for previous in batch:
            snapshot = _snapshot(previous)
            if snapshot.get("status") != "pass" or not isinstance(snapshot.get("debt"), list):
                if "历史记录缺少结构化债务,历史覆盖有限;不能推断债务已清零。" not in limitations:
                    limitations.append("历史记录缺少结构化债务,历史覆盖有限;不能推断债务已清零。")
                continue
            for debt in snapshot["debt"]:
                if isinstance(debt, dict) and isinstance(debt.get("id"), str):
                    debt_by_id[debt["id"]] = {
                        "id": _identifier(debt["id"], "historical debt.id"),
                        "summary": _text(debt.get("summary"), "historical debt.summary"),
                    }
            if not ambiguous:
                for debt_id in snapshot.get("resolved_debt_ids", []):
                    debt_by_id.pop(debt_id, None)
    if any(debt["id"] in debt_by_id for debt in declaration["debt"]):
        reasons.append("repeated_debt")
    for debt_id in declaration["resolved_debt_ids"]:
        if debt_id not in debt_by_id:
            blocking.append("显式解决的债务 ID 不存在于可用历史。")
        debt_by_id.pop(debt_id, None)
    for debt in declaration["debt"]:
        debt_by_id[debt["id"]] = debt
    if len(debt_by_id) > budgets["open_debt"]:
        exceeded.append("open_debt")
    if exceeded:
        reasons.append("budget_exceeded")
    evidence = declaration.get("full_review")
    whole_status = "missing" if reasons else "not_required"
    if evidence:
        matches = all(evidence[f"{key}_fingerprint"] == inputs[key]
                      for key in ("target", "candidate", "effective"))
        if not matches or set(evidence["checked_areas"]) != AREAS:
            whole_status = "invalid"
            blocking.append("整体架构评审指纹或六项检查范围与本次完整候选不一致。")
        elif evidence["conclusion"] != "pass":
            whole_status = "rejected"
            blocking.append("整体架构评审要求修改,当前候选不能应用。")
        else:
            whole_status = "accepted"
    elif reasons:
        blocking.append("需要绑定本次完整候选的整体架构评审证据。")
    return {
        "schema_version": "1", "status": "blocked" if blocking else "pass",
        "requirement_decision": decision, "requirement": requirement,
        "baseline": {"status": "selected" if baseline else "missing",
                     "record_id": baseline.id if baseline else None},
        "budgets": budgets,
        "complexity": {"baseline": baseline_metrics, "cumulative_delta": delta,
                       "budget_exceeded": exceeded},
        "debt": [debt_by_id[key] for key in sorted(debt_by_id)],
        "resolved_debt_ids": declaration["resolved_debt_ids"],
        "whole_review": {"required": bool(reasons), "reasons": reasons,
                         "status": whole_status, "evidence": evidence},
        "input_fingerprints": inputs, "blocking_findings": blocking,
        "current_structural_findings": sorted({str(item.get("rule_id")) for item in findings}),
        "limitations": limitations,
    }

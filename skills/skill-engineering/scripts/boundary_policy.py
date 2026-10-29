"""Portable, deterministic boundary and candidate-text evidence rules.

This file is the canonical stdlib-only source. Its byte-identical portable copy
is generated for Skill-only installations. A confirmation records a host claim;
neither a source label nor a fingerprint authenticates a human or a message.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any


class BoundaryError(ValueError):
    """Invalid or unsafe boundary evidence, without sensitive input excerpts."""


POLICY_VERSION = "1"
MAX_TEXT_CHARS = 4000
MAX_ITEMS = 128
MAX_CANDIDATE_CHARS = 8 * 1024 * 1024
TEXT_FIELDS = ("goal", "mission")
LIST_FIELDS = (
    "owned_capabilities", "excluded_capabilities", "allowed_context",
    "positive_triggers", "negative_triggers", "inputs", "outputs",
    "drift_signals", "redirect_strategy", "stop_conditions", "side_effects", "approvals",
)
BRIEF_METADATA = {
    "id", "target_users", "workflow", "failure_modes", "resources", "examples",
    "verification", "host_requirements", "acceptance_cases", "behavior_cases",
    "status", "schema_version", "created_at", "updated_at",
}
CATEGORIES = {"success", "insufficient", "negative", "drift", "failure", "approval"}
CONFIRMATION_STATUSES = {"confirmed", "pending", "rejected", "stale", "legacy_unknown"}
ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")
FINGERPRINT_RE = re.compile(r"[a-f0-9]{64}")
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]+"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}"),
    re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{12,}|github_pat_[A-Za-z0-9_]{12,})"),
    re.compile(
        r"(?i)\b(?:[a-z0-9]+[_-])*(?:token|secret|api[_-]?key|private[_-]?key|"
        r"password|passwd|cookie|session|credential)(?:[_-][a-z0-9]+)*"
        r"\b[\"']?\s*[:=]\s*\S+"
    ),
)
LIMITATIONS = [
    "仅检查宿主声明与候选文本，不验证人类身份或消息真实性。",
    "候选文本断言不证明真实工具、多轮纠偏、停止行为或下游任务效用。",
]


def _mapping(value: Any, label: str, required: set[str], optional: set[str] | None = None):
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise BoundaryError(f"{label}必须是对象。")
    if required - set(value) or set(value) - required - (optional or set()):
        raise BoundaryError(f"{label}含未知字段或缺少必填字段。")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > MAX_TEXT_CHARS:
        raise BoundaryError(f"{label}必须是有长度上限的非空文本。")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        raise BoundaryError(f"{label}必须是有效UTF-8文本。") from None
    if any(pattern.search(value) for pattern in SECRET_PATTERNS):
        raise BoundaryError(f"{label}含凭证形态值，请先脱敏。")
    if any(ord(char) < 32 and char not in "\n\r\t" for char in value):
        raise BoundaryError(f"{label}含非法控制字符。")
    return value.strip()


def _strings(value: Any, label: str, *, preserve_whitespace: bool = False) -> list[str]:
    if not isinstance(value, list) or len(value) > MAX_ITEMS:
        raise BoundaryError(f"{label}必须是有数量上限的文本数组。")
    result = [_text(item, label) for item in value]
    if preserve_whitespace:
        result = list(value)
    if len(result) != len(set(result)):
        raise BoundaryError(f"{label}不得含重复项。")
    return result


def _identifier(value: Any, label: str) -> str:
    value = _text(value, label)
    if not ID_RE.fullmatch(value):
        raise BoundaryError(f"{label}必须是非空稳定 ID。")
    return value


def _fingerprint(value: Any) -> str:
    if not isinstance(value, str) or not FINGERPRINT_RE.fullmatch(value):
        raise BoundaryError("输入指纹必须是 SHA-256。")
    return value


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)


def boundary_projection(value: dict) -> dict:
    """Return the normalized business projection, excluding known Brief metadata."""
    value = _mapping(value, "业务边界", set(TEXT_FIELDS), set(LIST_FIELDS) | BRIEF_METADATA)
    result = {key: _text(value[key], f"业务边界.{key}") for key in TEXT_FIELDS}
    result.update({key: _strings(value.get(key, []), f"业务边界.{key}") for key in LIST_FIELDS})
    for key in ("owned_capabilities", "positive_triggers", "drift_signals",
                "redirect_strategy", "stop_conditions"):
        if not result[key]:
            raise BoundaryError(f"业务边界.{key}不得为空。")
    return result


def boundary_fingerprint(value: dict) -> str:
    """Bind confirmation to business fields, never to time or workflow status."""
    return hashlib.sha256(_canonical(boundary_projection(value)).encode("utf-8")).hexdigest()


def validate_behavior_policy(policy: dict, boundary: dict) -> dict:
    """Validate declared capabilities; the host must verify their actual semantics."""
    value = _mapping(policy, "行为策略", {
        "interaction", "uses_tools", "has_side_effects", "rationale",
    })
    if value["interaction"] not in ("single_turn", "multi_turn"):
        raise BoundaryError("行为策略.interaction无效。")
    if any(type(value[key]) is not bool for key in ("uses_tools", "has_side_effects")):
        raise BoundaryError("行为策略的能力标记必须是布尔值。")
    projected = boundary_projection(boundary)
    if projected["side_effects"] and not value["has_side_effects"]:
        raise BoundaryError("已声明副作用，不能将行为策略标记为无副作用。")
    return {
        "interaction": value["interaction"], "uses_tools": value["uses_tools"],
        "has_side_effects": value["has_side_effects"],
        "rationale": _text(value["rationale"], "行为策略.rationale"),
    }


def validate_confirmation(boundary: dict, confirmation: dict, *,
                          subject_id: str | None = None) -> dict:
    """Validate an explicit confirmation claim without claiming human authentication."""
    fields = {
        "schema_version", "subject_id", "boundary_fingerprint", "status", "source",
        "summary", "excluded_decision", "behavior_policy",
    }
    value = _mapping(confirmation, "边界确认", fields, {"message_ref"})
    if value["schema_version"] != "1":
        raise BoundaryError("边界确认.schema_version必须是字符串1。")
    confirmed_id = _identifier(value["subject_id"], "边界确认.subject_id")
    if subject_id is not None and confirmed_id != _identifier(subject_id, "目标subject_id"):
        raise BoundaryError("边界确认与目标subject_id不一致。")
    if (not isinstance(value["status"], str) or value["status"] not in CONFIRMATION_STATUSES
            or value["status"] != "confirmed"):
        raise BoundaryError("边界确认尚未confirmed，请重新确认。")
    if value["source"] not in ("explicit_user_message", "explicit_cli_argument"):
        raise BoundaryError("边界确认必须来自宿主记录的明确用户表达或CLI参数。")
    projected = boundary_projection(boundary)
    fingerprint = _fingerprint(value["boundary_fingerprint"])
    if fingerprint != boundary_fingerprint(projected):
        raise BoundaryError("业务边界已变化，边界确认指纹失效。")
    expected = "listed" if projected["excluded_capabilities"] else "none"
    if value["excluded_decision"] != expected:
        raise BoundaryError("排除项确认与实际清单不一致。")
    result = {
        "schema_version": "1", "subject_id": confirmed_id,
        "boundary_fingerprint": fingerprint, "status": "confirmed", "source": value["source"],
        "summary": _text(value["summary"], "边界确认.summary"),
        "excluded_decision": expected,
        "behavior_policy": validate_behavior_policy(value["behavior_policy"], projected),
    }
    if "message_ref" in value:
        result["message_ref"] = _text(value["message_ref"], "边界确认.message_ref")
    return result


def _required_categories(policy: dict | None, boundary: dict | None) -> set[str]:
    if policy is None:
        return set()
    policy = validate_behavior_policy(policy, boundary)
    projected = boundary_projection(boundary)
    result = {"success", "insufficient"}
    if projected["excluded_capabilities"] or projected["negative_triggers"]:
        result.add("negative")
    if policy["interaction"] == "multi_turn":
        result.add("drift")
    if policy["uses_tools"] or policy["has_side_effects"]:
        result.add("failure")
    if policy["has_side_effects"]:
        result.add("approval")
    return result


def _case(value: Any, index: int, ids: set[str], required: set[str], *,
          typed: bool) -> tuple[dict, dict | None]:
    fallback = f"case-{index + 1}"
    if isinstance(value, str):
        return {"id": _text(value, "旧案例标签"), "status": "uncovered"}, None
    if not isinstance(value, dict):
        raise BoundaryError("行为案例必须是对象或旧文本标签。")
    if not value:
        return {"id": fallback, "status": "uncovered"}, None
    case_id = _identifier(value.get("id"), "行为案例.id")
    if case_id in ids:
        raise BoundaryError("行为案例ID重复。")
    ids.add(case_id)
    category = value.get("category")
    if category is not None and (not isinstance(category, str) or category not in CATEGORIES):
        raise BoundaryError("行为案例.category无效。")
    if typed and category is None:
        raise BoundaryError("按类型验收需要行为案例.category。")
    if value.get("status") == "not_applicable":
        value = _mapping(value, "非适用案例", {"id", "category", "status", "reason"})
        reason = _text(value["reason"], "非适用理由")
        if category in required or category == "success":
            raise BoundaryError("必需行为类别不得标记为not_applicable。")
        return {"id": case_id, "category": category, "status": "not_applicable",
                "reason": reason}, dict(value, id=case_id, reason=reason)
    value = _mapping(value, "行为案例", {"id"}, {
        "category", "given", "expect", "must_not", "assertions",
    })
    cleaned = {"id": case_id}
    if category is not None:
        cleaned["category"] = category
    incomplete = False
    for key in ("given", "expect"):
        if key not in value or value[key] is None or value[key] == "":
            incomplete = True
        else:
            cleaned[key] = _text(value[key], f"行为案例.{key}")
    if "must_not" not in value or value["must_not"] is None:
        incomplete = True
    else:
        cleaned["must_not"] = (
            _text(value["must_not"], "行为案例.must_not") if isinstance(value["must_not"], str)
            else _strings(value["must_not"], "行为案例.must_not")
        )
    assertions = value.get("assertions")
    if assertions is None:
        incomplete = True
    else:
        assertions = _mapping(assertions, "行为断言", set(), {"must_include", "must_not_include"})
        assertions = {key: _strings(item, f"行为断言.{key}", preserve_whitespace=True)
                      for key, item in assertions.items()}
        cleaned["assertions"] = assertions
        if not any(assertions.values()):
            incomplete = True
    status = "uncovered" if incomplete else "executable"
    return dict(cleaned, status=status), cleaned


def run_text_cases(text: str, cases: list, *, policy: dict | None = None,
                   boundary: dict | None = None) -> dict:
    """Run actual declarative text assertions, with optional capability coverage."""
    if not isinstance(text, str) or len(text) > MAX_CANDIDATE_CHARS:
        raise BoundaryError("候选文本必须是有长度上限的字符串。")
    required = _required_categories(policy, boundary)
    reports = []
    ids: set[str] = set()
    if not isinstance(cases, list) or len(cases) > MAX_ITEMS:
        reports.append({"id": "suite", "status": "failed", "reason": "案例必须是有数量上限的数组。"})
        cases = []
    for index, value in enumerate(cases):
        try:
            report, _ = _case(value, index, ids, required, typed=policy is not None)
            if report["status"] == "executable":
                assertions = report.pop("assertions")
                # Keep only short assertion evidence, never candidate text or conversations.
                report = {key: item for key, item in report.items()
                          if key in ("id", "category")}
                missing = [item for item in assertions.get("must_include", []) if item not in text]
                forbidden = [item for item in assertions.get("must_not_include", []) if item in text]
                report.update(status="failed" if missing or forbidden else "passed",
                              missing=missing, forbidden=forbidden)
        except BoundaryError as exc:
            report = {"id": f"case-{index + 1}", "status": "failed", "reason": str(exc)}
        reports.append(report)
    counts = {name: sum(item["status"] == name for item in reports)
              for name in ("passed", "failed", "uncovered", "not_applicable")}
    covered = {item.get("category") for item in reports if item["status"] == "passed"}
    missing_categories = sorted(required - covered)
    status = "failed" if counts["failed"] else (
        "uncovered" if counts["uncovered"] or missing_categories or not counts["passed"]
        else "passed"
    )
    return {
        "status": status, "total": len(reports), **counts, "cases": reports,
        "required_categories": sorted(required), "missing_categories": missing_categories,
        "evidence_kind": "candidate_text", "utility_claim": False,
    }


def _declaration(value: dict) -> dict:
    value = _mapping(value, "边界声明", {"schema_version", "change"}, {
        "reason", "boundary", "confirmation", "cases",
    })
    if value["schema_version"] != "1":
        raise BoundaryError("边界声明.schema_version必须是字符串1。")
    if value["change"] == "unchanged":
        value = _mapping(value, "未变边界声明", {"schema_version", "change", "reason"}, {"boundary"})
        cleaned = {"schema_version": "1", "change": "unchanged",
                   "reason": _text(value["reason"], "未变边界理由")}
        if "boundary" in value:
            cleaned["boundary"] = boundary_projection(value["boundary"])
        return cleaned
    if value["change"] != "changed":
        raise BoundaryError("边界声明.change无效。")
    value = _mapping(value, "变更边界声明", {
        "schema_version", "change", "boundary", "confirmation", "cases",
    })
    projected = boundary_projection(value["boundary"])
    confirmed = validate_confirmation(projected, value["confirmation"])
    cases = value["cases"]
    if not isinstance(cases, list) or len(cases) > MAX_ITEMS:
        raise BoundaryError("边界声明.cases必须是有数量上限的数组。")
    cleaned_cases = []
    ids: set[str] = set()
    required = _required_categories(confirmed["behavior_policy"], projected)
    for index, case in enumerate(cases):
        _, cleaned_case = _case(case, index, ids, required, typed=True)
        if cleaned_case is None:
            raise BoundaryError("新边界声明不得使用旧标签或空案例。")
        cleaned_cases.append(cleaned_case)
    return {"schema_version": "1", "change": "changed", "boundary": projected,
            "confirmation": confirmed, "cases": cleaned_cases}


def assess_boundary(declaration: dict | None, *, target_fingerprint: str,
                    candidate_fingerprint: str, effective_fingerprint: str,
                    architecture_boundary_changed: bool = False, candidate_text: str = "") -> dict:
    """Freeze deterministic evidence alongside the existing architecture review."""
    if type(architecture_boundary_changed) is not bool:
        raise BoundaryError("架构边界变更标记必须是布尔值。")
    report = {
        "schema_version": "1", "policy_version": POLICY_VERSION, "status": "unreviewed",
        "change": None, "confirmation_status": "legacy_unknown", "declaration": None,
        "input_fingerprints": {
            "target": _fingerprint(target_fingerprint),
            "candidate": _fingerprint(candidate_fingerprint),
            "effective": _fingerprint(effective_fingerprint),
        },
        "architecture_boundary_changed": architecture_boundary_changed,
        "behavior_policy": None, "behavior_tests": None, "blocking_findings": [],
        "evidence_kind": "candidate_text", "utility_claim": False,
        "limitations": list(LIMITATIONS),
    }
    if declaration is None:
        report["blocking_findings"].append("缺少边界声明，请确认业务边界或说明未变理由。")
        return report
    report["status"] = "blocked"
    try:
        cleaned = _declaration(declaration)
        report["declaration"] = cleaned
        report["change"] = cleaned["change"]
        if cleaned["change"] == "unchanged":
            if architecture_boundary_changed:
                raise BoundaryError("架构审查已声明边界变化，与unchanged边界声明冲突。")
        else:
            confirmation = cleaned["confirmation"]
            report["confirmation_status"] = confirmation["status"]
            report["behavior_policy"] = confirmation["behavior_policy"]
            behavior = run_text_cases(candidate_text, cleaned["cases"],
                                      policy=confirmation["behavior_policy"], boundary=cleaned["boundary"])
            report["behavior_tests"] = behavior
            if behavior["status"] != "passed":
                raise BoundaryError("边界行为文本案例未全部通过或缺少必需类别。")
        report["status"] = "pass"
    except BoundaryError as exc:
        report["blocking_findings"].append(str(exc))
    return report


def validate_boundary_snapshot(report: dict, *, target_fingerprint: str,
                               candidate_fingerprint: str, effective_fingerprint: str,
                               candidate_text: str = "") -> None:
    """Recompute the complete frozen report and reject drift or tampering."""
    message = "边界确认快照缺失、漂移、被篡改或未通过；请重新预览。"
    if not isinstance(report, dict) or report.get("status") != "pass":
        raise BoundaryError(message)
    try:
        expected = assess_boundary(
            report.get("declaration"), target_fingerprint=target_fingerprint,
            candidate_fingerprint=candidate_fingerprint, effective_fingerprint=effective_fingerprint,
            architecture_boundary_changed=report.get("architecture_boundary_changed"),
            candidate_text=candidate_text,
        )
        if expected["status"] != "pass" or _canonical(report) != _canonical(expected):
            raise BoundaryError(message)
    except (BoundaryError, TypeError, ValueError, RecursionError) as exc:
        raise BoundaryError(message) from exc

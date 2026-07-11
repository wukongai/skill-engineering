"""Deterministic behavior-evidence evaluator for Skill Guide.

This module never executes commands from a suite. It validates already produced
baseline/candidate run artifacts, applies deterministic assertions, and emits a
traceable comparison report.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .journey import SCHEMA_VERSION, local_state_root, new_id, now_iso


MAX_INPUT_BYTES = 5 * 1024 * 1024
MAX_OUTPUT_CHARS = 1_000_000
VALID_SPLITS = {"development", "holdout"}
VALID_CATEGORIES = {"success", "failure", "high_risk"}
ID_RE = re.compile(r"[a-z0-9][a-z0-9._-]{0,127}", re.IGNORECASE)
ALLOWED_EXPECTED_KEYS = {"status", "contains", "not_contains", "regex", "json_equals"}


@dataclass(frozen=True)
class EvaluationCase:
    id: str
    split: str
    category: str
    expected: dict[str, Any]


@dataclass(frozen=True)
class EvaluationSuite:
    id: str
    description: str
    cases: list[EvaluationCase]
    gates: dict[str, float | int]
    schema_version: str = SCHEMA_VERSION


@dataclass(frozen=True)
class BehaviorRun:
    status: str
    output: str
    output_json: Any = None
    duration_ms: float | None = None
    artifact: str | None = None


@dataclass(frozen=True)
class BehaviorResults:
    suite_id: str
    subject: str
    subject_fingerprint: str
    runs: dict[str, BehaviorRun]
    schema_version: str = SCHEMA_VERSION


@dataclass(frozen=True)
class CaseEvaluation:
    case_id: str
    split: str
    category: str
    status: str  # pass | fail | not_evaluated
    assertions: list[dict[str, Any]]


@dataclass
class BehaviorEvaluationReport:
    id: str
    suite_id: str
    baseline_subject: str
    baseline_fingerprint: str
    candidate_subject: str
    candidate_fingerprint: str
    input_artifacts: dict[str, dict[str, str]]
    baseline_cases: list[CaseEvaluation]
    candidate_cases: list[CaseEvaluation]
    metrics: dict[str, Any]
    negative_transfer: list[str]
    gate_outcomes: dict[str, dict[str, Any]]
    coverage: dict[str, Any]
    decision: str
    utility_claim: str
    limitations: list[str]
    schema_version: str = SCHEMA_VERSION
    created_at: str = field(default_factory=now_iso)


def _read_bounded(path: Path) -> bytes:
    path = path.expanduser().resolve()
    if not path.is_file():
        raise SystemExit(f"评测输入不存在:{path}")
    size = path.stat().st_size
    if size > MAX_INPUT_BYTES:
        raise SystemExit(f"评测输入过大:{path} ({size} bytes, max={MAX_INPUT_BYTES})")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise SystemExit(f"无法读取评测输入:{path}\n{exc}") from exc


def _load_mapping(path: Path, *, yaml_allowed: bool) -> tuple[dict[str, Any], bytes]:
    raw = _read_bounded(path)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SystemExit(f"评测输入必须是 UTF-8:{path}") from exc
    try:
        value = yaml.safe_load(text) if yaml_allowed else json.loads(text)
    except (yaml.YAMLError, json.JSONDecodeError) as exc:
        kind = "YAML/JSON" if yaml_allowed else "JSON"
        raise SystemExit(f"评测输入不是合法 {kind}:{path}\n{exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"评测输入顶层必须是 object:{path}")
    return value, raw


def _require_version(data: dict[str, Any], path: Path) -> None:
    if str(data.get("schema_version")) != SCHEMA_VERSION:
        raise SystemExit(
            f"不支持的评测 schema:{path} "
            f"(found={data.get('schema_version')!r}, expected={SCHEMA_VERSION})"
        )


def _require_id(value: Any, label: str) -> str:
    text = str(value or "")
    if not ID_RE.fullmatch(text):
        raise SystemExit(f"{label} 必须是安全的稳定 id:{text!r}")
    return text


def _string_list(value: Any, label: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise SystemExit(f"{label} 必须是字符串数组。")
    return value


def _number(value: Any, label: str, *, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SystemExit(f"{label} 必须是数字。")
    result = float(value)
    if not minimum <= result <= maximum:
        raise SystemExit(f"{label} 必须在 {minimum}..{maximum} 之间。")
    return result


def load_evaluation_suite(path: Path, *, production: bool = False) -> tuple[EvaluationSuite, str]:
    data, raw = _load_mapping(path, yaml_allowed=True)
    _require_version(data, path)
    suite_id = _require_id(data.get("id"), "suite.id")
    raw_cases = data.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise SystemExit("suite.cases 必须是非空数组。")

    cases: list[EvaluationCase] = []
    seen: set[str] = set()
    for index, item in enumerate(raw_cases):
        if not isinstance(item, dict):
            raise SystemExit(f"suite.cases[{index}] 必须是 object。")
        case_id = _require_id(item.get("id"), f"suite.cases[{index}].id")
        if case_id in seen:
            raise SystemExit(f"suite case id 重复:{case_id}")
        seen.add(case_id)
        split = str(item.get("split") or "")
        category = str(item.get("category") or "")
        if split not in VALID_SPLITS:
            raise SystemExit(f"case {case_id} split 无效:{split}")
        if category not in VALID_CATEGORIES:
            raise SystemExit(f"case {case_id} category 无效:{category}")
        expected = item.get("expected")
        if not isinstance(expected, dict) or not expected:
            raise SystemExit(f"case {case_id} expected 必须是非空 object。")
        unknown = sorted(set(expected) - ALLOWED_EXPECTED_KEYS)
        if unknown:
            raise SystemExit(f"case {case_id} 包含不支持的断言:{', '.join(unknown)}")
        if "status" in expected and not isinstance(expected["status"], str):
            raise SystemExit(f"case {case_id} expected.status 必须是字符串。")
        for key in ("contains", "not_contains", "regex"):
            values = _string_list(expected.get(key), f"case {case_id} expected.{key}")
            if key == "regex":
                for pattern in values:
                    try:
                        re.compile(pattern)
                    except re.error as exc:
                        raise SystemExit(f"case {case_id} regex 无效:{pattern}\n{exc}") from exc
        json_equals = expected.get("json_equals") or []
        if not isinstance(json_equals, list):
            raise SystemExit(f"case {case_id} expected.json_equals 必须是数组。")
        for assertion in json_equals:
            if (
                not isinstance(assertion, dict)
                or not isinstance(assertion.get("path"), str)
                or "value" not in assertion
            ):
                raise SystemExit(f"case {case_id} json_equals 每项必须包含 path 和 value。")
        cases.append(EvaluationCase(case_id, split, category, expected))

    gates_raw = data.get("gates") or {}
    if not isinstance(gates_raw, dict):
        raise SystemExit("suite.gates 必须是 object。")
    allowed_gates = {
        "min_candidate_pass_rate",
        "min_holdout_pass_rate",
        "min_high_risk_pass_rate",
        "max_negative_transfer",
        "min_delta",
    }
    unknown_gates = sorted(set(gates_raw) - allowed_gates)
    if unknown_gates:
        raise SystemExit(f"suite.gates 包含未知字段:{', '.join(unknown_gates)}")
    gates: dict[str, float | int] = {
        "min_candidate_pass_rate": _number(
            gates_raw.get("min_candidate_pass_rate", 1.0),
            "min_candidate_pass_rate",
            minimum=0,
            maximum=1,
        ),
        "min_holdout_pass_rate": _number(
            gates_raw.get("min_holdout_pass_rate", 1.0),
            "min_holdout_pass_rate",
            minimum=0,
            maximum=1,
        ),
        "min_high_risk_pass_rate": _number(
            gates_raw.get("min_high_risk_pass_rate", 1.0),
            "min_high_risk_pass_rate",
            minimum=0,
            maximum=1,
        ),
        "min_delta": _number(gates_raw.get("min_delta", 0.0), "min_delta", minimum=-1, maximum=1),
    }
    max_negative = gates_raw.get("max_negative_transfer", 0)
    if isinstance(max_negative, bool) or not isinstance(max_negative, int) or max_negative < 0:
        raise SystemExit("max_negative_transfer 必须是非负整数。")
    gates["max_negative_transfer"] = max_negative

    if production:
        categories = {case.category for case in cases}
        missing = sorted(VALID_CATEGORIES - categories)
        if missing:
            raise SystemExit(f"production suite 缺少 case category:{', '.join(missing)}")
        if not any(case.split == "holdout" for case in cases):
            raise SystemExit("production suite 至少需要一个 holdout case。")

    suite = EvaluationSuite(
        id=suite_id,
        description=str(data.get("description") or ""),
        cases=cases,
        gates=gates,
    )
    return suite, hashlib.sha256(raw).hexdigest()


def load_behavior_results(path: Path, suite: EvaluationSuite) -> tuple[BehaviorResults, str]:
    data, raw = _load_mapping(path, yaml_allowed=False)
    _require_version(data, path)
    suite_id = _require_id(data.get("suite_id"), "results.suite_id")
    if suite_id != suite.id:
        raise SystemExit(f"results suite_id 不匹配:{suite_id} != {suite.id}")
    subject = str(data.get("subject") or "").strip()
    fingerprint = str(data.get("subject_fingerprint") or "").strip()
    if not subject or not fingerprint:
        raise SystemExit("results 必须包含 subject 和 subject_fingerprint。")
    raw_runs = data.get("runs")
    if not isinstance(raw_runs, dict):
        raise SystemExit("results.runs 必须是 object。")
    known = {case.id for case in suite.cases}
    unknown = sorted(set(raw_runs) - known)
    if unknown:
        raise SystemExit(f"results 包含 suite 之外的 case:{', '.join(unknown)}")
    runs: dict[str, BehaviorRun] = {}
    for case_id, item in raw_runs.items():
        if not isinstance(item, dict):
            raise SystemExit(f"results.runs.{case_id} 必须是 object。")
        status = str(item.get("status") or "").strip()
        output = item.get("output", "")
        if not status or not isinstance(output, str):
            raise SystemExit(f"results.runs.{case_id} 必须包含字符串 status/output。")
        if len(output) > MAX_OUTPUT_CHARS:
            raise SystemExit(f"results.runs.{case_id}.output 过大。")
        duration = item.get("duration_ms")
        if duration is not None:
            duration = _number(
                duration, f"results.runs.{case_id}.duration_ms", minimum=0, maximum=86_400_000
            )
        artifact = item.get("artifact")
        if artifact is not None and not isinstance(artifact, str):
            raise SystemExit(f"results.runs.{case_id}.artifact 必须是字符串。")
        runs[case_id] = BehaviorRun(
            status=status,
            output=output,
            output_json=item.get("output_json"),
            duration_ms=duration,
            artifact=artifact,
        )
    value = BehaviorResults(suite.id, subject, fingerprint, runs)
    return value, hashlib.sha256(raw).hexdigest()


def _json_path(value: Any, path: str) -> tuple[bool, Any]:
    current = value
    if path in {"", ".", "$"}:
        return True, current
    normalized = path[2:] if path.startswith("$.") else path
    for part in normalized.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            return False, None
    return True, current


def _assertion(kind: str, expected: Any, actual: Any, passed: bool) -> dict[str, Any]:
    return {"kind": kind, "expected": expected, "actual": actual, "passed": passed}


def evaluate_case(case: EvaluationCase, run: BehaviorRun | None) -> CaseEvaluation:
    if run is None:
        return CaseEvaluation(case.id, case.split, case.category, "not_evaluated", [])
    checks: list[dict[str, Any]] = []
    expected = case.expected
    if "status" in expected:
        checks.append(
            _assertion("status", expected["status"], run.status, run.status == expected["status"])
        )
    for needle in expected.get("contains") or []:
        checks.append(_assertion("contains", needle, needle in run.output, needle in run.output))
    for needle in expected.get("not_contains") or []:
        absent = needle not in run.output
        checks.append(_assertion("not_contains", needle, absent, absent))
    for pattern in expected.get("regex") or []:
        matched = re.search(pattern, run.output) is not None
        checks.append(_assertion("regex", pattern, matched, matched))
    for item in expected.get("json_equals") or []:
        found, actual = _json_path(run.output_json, item["path"])
        checks.append(
            _assertion(
                "json_equals",
                {"path": item["path"], "value": item["value"]},
                {"found": found, "value": actual},
                found and actual == item["value"],
            )
        )
    passed = bool(checks) and all(item["passed"] for item in checks)
    return CaseEvaluation(case.id, case.split, case.category, "pass" if passed else "fail", checks)


def _metric(items: list[CaseEvaluation]) -> dict[str, Any]:
    total = len(items)
    evaluated = sum(item.status in {"pass", "fail"} for item in items)
    passed = sum(item.status == "pass" for item in items)
    return {
        "total": total,
        "evaluated": evaluated,
        "passed": passed,
        "coverage_percent": round(evaluated * 100 / total) if total else None,
        "pass_rate": round(passed / total, 6) if total and evaluated == total else None,
    }


def _metrics(items: list[CaseEvaluation]) -> dict[str, Any]:
    return {
        "overall": _metric(items),
        "development": _metric([item for item in items if item.split == "development"]),
        "holdout": _metric([item for item in items if item.split == "holdout"]),
        "high_risk": _metric([item for item in items if item.category == "high_risk"]),
    }


def _gate(actual: Any, expected: Any, operator: str) -> dict[str, Any]:
    if actual is None:
        passed = None
    elif operator == ">=":
        passed = actual >= expected
    else:
        passed = actual <= expected
    return {
        "actual": actual,
        "expected": expected,
        "operator": operator,
        "passed": passed,
        "applicable": True,
    }


def _not_applicable_gate(expected: Any, operator: str) -> dict[str, Any]:
    return {
        "actual": None,
        "expected": expected,
        "operator": operator,
        "passed": True,
        "applicable": False,
    }


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def _compare_results(
    suite: EvaluationSuite,
    baseline: BehaviorResults,
    candidate: BehaviorResults,
) -> dict[str, Any]:
    baseline_cases = [evaluate_case(case, baseline.runs.get(case.id)) for case in suite.cases]
    candidate_cases = [evaluate_case(case, candidate.runs.get(case.id)) for case in suite.cases]
    baseline_by_id = {item.case_id: item for item in baseline_cases}
    candidate_by_id = {item.case_id: item for item in candidate_cases}
    negative_transfer = [
        case.id
        for case in suite.cases
        if baseline_by_id[case.id].status == "pass" and candidate_by_id[case.id].status == "fail"
    ]
    baseline_metrics = _metrics(baseline_cases)
    candidate_metrics = _metrics(candidate_cases)
    baseline_rate = baseline_metrics["overall"]["pass_rate"]
    candidate_rate = candidate_metrics["overall"]["pass_rate"]
    delta = (
        round(candidate_rate - baseline_rate, 6)
        if baseline_rate is not None and candidate_rate is not None
        else None
    )
    gates = {
        "candidate_pass_rate": _gate(candidate_rate, suite.gates["min_candidate_pass_rate"], ">="),
        "holdout_pass_rate": _gate(
            candidate_metrics["holdout"]["pass_rate"], suite.gates["min_holdout_pass_rate"], ">="
        ),
        "high_risk_pass_rate": (
            _gate(
                candidate_metrics["high_risk"]["pass_rate"],
                suite.gates["min_high_risk_pass_rate"],
                ">=",
            )
            if candidate_metrics["high_risk"]["total"]
            else _not_applicable_gate(suite.gates["min_high_risk_pass_rate"], ">=")
        ),
        "negative_transfer": _gate(
            len(negative_transfer), suite.gates["max_negative_transfer"], "<="
        ),
        "delta": _gate(delta, suite.gates["min_delta"], ">="),
    }
    total = len(suite.cases) * 2
    evaluated = sum(item.status != "not_evaluated" for item in baseline_cases + candidate_cases)
    has_holdout = any(case.split == "holdout" for case in suite.cases)
    complete = evaluated == total
    gate_values = [item["passed"] for item in gates.values()]
    if not complete or not has_holdout or any(value is None for value in gate_values):
        decision = "inconclusive"
    elif all(gate_values):
        decision = "accept"
    else:
        decision = "reject"
    return {
        "baseline_cases": baseline_cases,
        "candidate_cases": candidate_cases,
        "metrics": {"baseline": baseline_metrics, "candidate": candidate_metrics, "delta": delta},
        "negative_transfer": negative_transfer,
        "gate_outcomes": gates,
        "coverage": {
            "total_results": total,
            "evaluated_results": evaluated,
            "coverage_percent": round(evaluated * 100 / total) if total else 0,
            "has_holdout": has_holdout,
        },
        "decision": decision,
    }


def evaluate_behavior(
    root: Path,
    suite_path: Path,
    baseline_path: Path,
    candidate_path: Path,
    *,
    production: bool = False,
) -> BehaviorEvaluationReport:
    suite_path = suite_path.expanduser().resolve()
    baseline_path = baseline_path.expanduser().resolve()
    candidate_path = candidate_path.expanduser().resolve()
    suite, suite_hash = load_evaluation_suite(suite_path, production=production)
    baseline, baseline_hash = load_behavior_results(baseline_path, suite)
    candidate, candidate_hash = load_behavior_results(candidate_path, suite)
    comparison = _compare_results(suite, baseline, candidate)
    decision = comparison["decision"]

    report = BehaviorEvaluationReport(
        id=new_id("evaluation"),
        suite_id=suite.id,
        baseline_subject=baseline.subject,
        baseline_fingerprint=baseline.subject_fingerprint,
        candidate_subject=candidate.subject,
        candidate_fingerprint=candidate.subject_fingerprint,
        input_artifacts={
            "suite": {"path": str(suite_path), "sha256": suite_hash},
            "baseline_results": {"path": str(baseline_path), "sha256": baseline_hash},
            "candidate_results": {"path": str(candidate_path), "sha256": candidate_hash},
        },
        baseline_cases=comparison["baseline_cases"],
        candidate_cases=comparison["candidate_cases"],
        metrics=comparison["metrics"],
        negative_transfer=comparison["negative_transfer"],
        gate_outcomes=comparison["gate_outcomes"],
        coverage=comparison["coverage"],
        decision=decision,
        utility_claim={
            "accept": "behavioral-evidence",
            "reject": "evidence-failed",
            "inconclusive": "not-evaluated",
        }[decision],
        limitations=[
            "本报告只证明候选在这份有哈希的 suite 和结果 artifact 上的行为。",
            "确定性字符串/JSON 断言不等于 LLM 语义评审。",
            "结果 artifact 的生成者与运行环境需要由外部 harness 单独记录和审计。",
        ],
    )
    _atomic_write(local_state_root(root) / "evaluations" / f"{report.id}.json", asdict(report))
    return report


def load_evaluation_report(
    path: Path, *, verify_inputs: bool = True
) -> tuple[dict[str, Any], list[str]]:
    data, _ = _load_mapping(path, yaml_allowed=False)
    _require_version(data, path)
    _require_id(data.get("id"), "report.id")
    _require_id(data.get("suite_id"), "report.suite_id")
    decision = data.get("decision")
    if decision not in {"accept", "reject", "inconclusive"}:
        raise SystemExit(f"report decision 无效:{decision}")
    artifacts = data.get("input_artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != {
        "suite",
        "baseline_results",
        "candidate_results",
    }:
        raise SystemExit("report input_artifacts 不完整。")
    warnings: list[str] = []
    resolved_inputs: dict[str, Path] = {}
    if verify_inputs:
        for label, item in artifacts.items():
            if (
                not isinstance(item, dict)
                or not isinstance(item.get("path"), str)
                or not isinstance(item.get("sha256"), str)
            ):
                raise SystemExit(f"report input_artifacts.{label} 格式无效。")
            source = Path(item["path"])
            resolved_inputs[label] = source
            if not source.is_file():
                warnings.append(f"输入 artifact 已不存在:{source}")
                continue
            actual = hashlib.sha256(_read_bounded(source)).hexdigest()
            if actual != item["sha256"]:
                warnings.append(f"输入 artifact hash 已漂移:{source}")
        if not warnings:
            try:
                suite, _ = load_evaluation_suite(resolved_inputs["suite"])
                baseline, _ = load_behavior_results(resolved_inputs["baseline_results"], suite)
                candidate, _ = load_behavior_results(resolved_inputs["candidate_results"], suite)
                expected = _compare_results(suite, baseline, candidate)
                stored_comparable = {
                    "baseline_cases": data.get("baseline_cases"),
                    "candidate_cases": data.get("candidate_cases"),
                    "metrics": data.get("metrics"),
                    "negative_transfer": data.get("negative_transfer"),
                    "gate_outcomes": data.get("gate_outcomes"),
                    "coverage": data.get("coverage"),
                    "decision": data.get("decision"),
                }
                expected_comparable = {
                    **expected,
                    "baseline_cases": [asdict(item) for item in expected["baseline_cases"]],
                    "candidate_cases": [asdict(item) for item in expected["candidate_cases"]],
                }
                if stored_comparable != expected_comparable:
                    warnings.append("report 内容与输入 artifacts 的确定性重算结果不一致。")
                if (
                    data.get("baseline_subject") != baseline.subject
                    or data.get("baseline_fingerprint") != baseline.subject_fingerprint
                ):
                    warnings.append("report baseline subject/fingerprint 与结果 artifact 不一致。")
                if (
                    data.get("candidate_subject") != candidate.subject
                    or data.get("candidate_fingerprint") != candidate.subject_fingerprint
                ):
                    warnings.append("report candidate subject/fingerprint 与结果 artifact 不一致。")
            except SystemExit as exc:
                warnings.append(f"report 输入 artifacts 无法重算:{exc}")
    return data, warnings


def format_behavior_report(report: BehaviorEvaluationReport) -> str:
    from .interaction import UserFeedback

    labels = {
        "accept": "候选通过了当前真实行为验收。",
        "reject": "候选没有通过当前真实行为验收。",
        "inconclusive": "当前证据不足，暂时不能判断候选是否更好。",
    }
    candidate = report.metrics["candidate"]
    next_actions = {
        "accept": "可以继续版本化或进入范围明确的测试接入。",
        "reject": "先修复失败和负迁移案例，再生成新候选。",
        "inconclusive": "补齐缺失的真实运行结果后重新评测。",
    }
    return UserFeedback(
        status="completed" if report.decision == "accept" else "incomplete",
        result=labels[report.decision],
        impact=[
            f"真实结果覆盖率：{report.coverage['coverage_percent']}%。",
            f"候选通过率：{candidate['overall']['pass_rate']:.0%}；高风险通过率：{candidate['high_risk']['pass_rate']:.0%}。",
            f"负迁移：{len(report.negative_transfer)} 个。",
            f"结论边界：{report.utility_claim}。",
        ],
        next_action=next_actions[report.decision],
        technical_details=[f"suite={report.suite_id}"],
    ).render()

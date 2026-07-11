from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from skill_engineering.evaluation import (
    MAX_INPUT_BYTES,
    evaluate_behavior,
    load_behavior_results,
    load_evaluation_report,
    load_evaluation_suite,
)


def write_suite(tmp_path: Path, *, mutate=None) -> Path:
    data = {
        "schema_version": "1",
        "id": "demo-suite",
        "description": "通用行为证据",
        "cases": [
            {
                "id": "normal-success",
                "split": "development",
                "category": "success",
                "expected": {
                    "status": "completed",
                    "contains": ["完成"],
                    "not_contains": ["伪造"],
                },
            },
            {
                "id": "known-failure",
                "split": "development",
                "category": "failure",
                "expected": {
                    "status": "failed",
                    "regex": ["恢复|修复"],
                    "json_equals": [{"path": "recovery.available", "value": True}],
                },
            },
            {
                "id": "unseen-risk",
                "split": "holdout",
                "category": "high_risk",
                "expected": {"status": "blocked", "regex": ["确认|批准"]},
            },
        ],
        "gates": {
            "min_candidate_pass_rate": 1.0,
            "min_holdout_pass_rate": 1.0,
            "min_high_risk_pass_rate": 1.0,
            "max_negative_transfer": 0,
            "min_delta": 0.0,
        },
    }
    if mutate:
        mutate(data)
    path = tmp_path / "suite.yaml"
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def passing_runs() -> dict:
    return {
        "normal-success": {"status": "completed", "output": "已经完成任务"},
        "known-failure": {
            "status": "failed",
            "output": "可以恢复并修复",
            "output_json": {"recovery": {"available": True}},
        },
        "unseen-risk": {"status": "blocked", "output": "需要用户确认后继续"},
    }


def write_results(
    tmp_path: Path,
    name: str,
    *,
    subject: str,
    runs: dict | None = None,
    suite_id: str = "demo-suite",
) -> Path:
    path = tmp_path / f"{name}.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "suite_id": suite_id,
                "subject": subject,
                "subject_fingerprint": f"fingerprint-{subject}",
                "runs": passing_runs() if runs is None else runs,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def test_valid_production_suite_and_results(tmp_path: Path):
    suite, _ = load_evaluation_suite(write_suite(tmp_path), production=True)
    results, _ = load_behavior_results(
        write_results(tmp_path, "candidate", subject="candidate"), suite
    )
    assert suite.id == "demo-suite"
    assert set(results.runs) == {"normal-success", "known-failure", "unseen-risk"}


def test_accept_report_has_holdout_metrics_hashes_and_persistence(tmp_path: Path):
    root = tmp_path / "hub"
    root.mkdir()
    report = evaluate_behavior(
        root,
        write_suite(tmp_path),
        write_results(tmp_path, "baseline", subject="baseline"),
        write_results(tmp_path, "candidate", subject="candidate"),
        production=True,
    )
    assert report.decision == "accept"
    assert report.utility_claim == "behavioral-evidence"
    assert report.coverage["coverage_percent"] == 100
    assert report.metrics["candidate"]["holdout"]["pass_rate"] == 1.0
    assert report.negative_transfer == []
    assert all(len(value["sha256"]) == 64 for value in report.input_artifacts.values())
    saved = root / ".skill-engineering" / "evaluations" / f"{report.id}.json"
    assert saved.is_file()
    loaded, warnings = load_evaluation_report(saved)
    assert loaded["decision"] == "accept"
    assert warnings == []


def test_negative_transfer_rejects_candidate(tmp_path: Path):
    root = tmp_path / "hub"
    root.mkdir()
    candidate_runs = passing_runs()
    candidate_runs["normal-success"] = {"status": "completed", "output": "没有目标词"}
    report = evaluate_behavior(
        root,
        write_suite(tmp_path),
        write_results(tmp_path, "baseline", subject="baseline"),
        write_results(tmp_path, "candidate", subject="candidate", runs=candidate_runs),
        production=True,
    )
    assert report.decision == "reject"
    assert report.utility_claim == "evidence-failed"
    assert report.negative_transfer == ["normal-success"]
    assert report.gate_outcomes["negative_transfer"]["passed"] is False


def test_holdout_regression_rejects_candidate(tmp_path: Path):
    root = tmp_path / "hub"
    root.mkdir()
    candidate_runs = passing_runs()
    candidate_runs["unseen-risk"] = {"status": "completed", "output": "直接执行"}
    report = evaluate_behavior(
        root,
        write_suite(tmp_path),
        write_results(tmp_path, "baseline", subject="baseline"),
        write_results(tmp_path, "candidate", subject="candidate", runs=candidate_runs),
        production=True,
    )
    assert report.decision == "reject"
    assert report.metrics["candidate"]["holdout"]["pass_rate"] == 0.0
    assert report.metrics["candidate"]["high_risk"]["pass_rate"] == 0.0


def test_missing_result_is_inconclusive_not_zero_score(tmp_path: Path):
    root = tmp_path / "hub"
    root.mkdir()
    candidate_runs = passing_runs()
    del candidate_runs["unseen-risk"]
    report = evaluate_behavior(
        root,
        write_suite(tmp_path),
        write_results(tmp_path, "baseline", subject="baseline"),
        write_results(tmp_path, "candidate", subject="candidate", runs=candidate_runs),
        production=True,
    )
    assert report.decision == "inconclusive"
    assert report.utility_claim == "not-evaluated"
    assert report.metrics["candidate"]["overall"]["pass_rate"] is None
    assert report.metrics["candidate"]["overall"]["evaluated"] == 2


def test_rejects_duplicate_case_invalid_regex_and_command(tmp_path: Path):
    duplicate = write_suite(
        tmp_path,
        mutate=lambda data: data["cases"].append(dict(data["cases"][0])),
    )
    with pytest.raises(SystemExit, match="重复"):
        load_evaluation_suite(duplicate)

    invalid_regex = write_suite(
        tmp_path,
        mutate=lambda data: data["cases"][0]["expected"].update({"regex": ["["]}),
    )
    with pytest.raises(SystemExit, match="regex 无效"):
        load_evaluation_suite(invalid_regex)

    command = write_suite(
        tmp_path,
        mutate=lambda data: data["cases"][0]["expected"].update({"command": "rm -rf /"}),
    )
    with pytest.raises(SystemExit, match="不支持的断言"):
        load_evaluation_suite(command)


def test_production_suite_requires_portfolio_and_holdout(tmp_path: Path):
    suite = write_suite(
        tmp_path,
        mutate=lambda data: data.update({"cases": [data["cases"][0]]}),
    )
    with pytest.raises(SystemExit, match="缺少 case category"):
        load_evaluation_suite(suite, production=True)

    no_holdout = write_suite(
        tmp_path,
        mutate=lambda data: [item.update({"split": "development"}) for item in data["cases"]],
    )
    with pytest.raises(SystemExit, match="holdout"):
        load_evaluation_suite(no_holdout, production=True)


def test_complete_results_without_holdout_are_inconclusive(tmp_path: Path):
    root = tmp_path / "hub"
    root.mkdir()
    suite = write_suite(
        tmp_path,
        mutate=lambda data: [item.update({"split": "development"}) for item in data["cases"]],
    )
    report = evaluate_behavior(
        root,
        suite,
        write_results(tmp_path, "baseline", subject="baseline"),
        write_results(tmp_path, "candidate", subject="candidate"),
    )
    assert report.coverage["coverage_percent"] == 100
    assert report.coverage["has_holdout"] is False
    assert report.decision == "inconclusive"


def test_results_reject_wrong_suite_and_extra_case(tmp_path: Path):
    suite, _ = load_evaluation_suite(write_suite(tmp_path))
    wrong = write_results(tmp_path, "wrong", subject="candidate", suite_id="other-suite")
    with pytest.raises(SystemExit, match="不匹配"):
        load_behavior_results(wrong, suite)

    runs = passing_runs()
    runs["outside"] = {"status": "completed", "output": "x"}
    extra = write_results(tmp_path, "extra", subject="candidate", runs=runs)
    with pytest.raises(SystemExit, match="suite 之外"):
        load_behavior_results(extra, suite)


def test_report_detects_input_hash_drift(tmp_path: Path):
    root = tmp_path / "hub"
    root.mkdir()
    suite_path = write_suite(tmp_path)
    report = evaluate_behavior(
        root,
        suite_path,
        write_results(tmp_path, "baseline", subject="baseline"),
        write_results(tmp_path, "candidate", subject="candidate"),
    )
    saved = root / ".skill-engineering" / "evaluations" / f"{report.id}.json"
    suite_path.write_text("schema_version: '1'\nid: changed\ncases: []\n", encoding="utf-8")
    _, warnings = load_evaluation_report(saved)
    assert any("hash 已漂移" in warning for warning in warnings)


def test_report_detects_tampered_decision_even_when_inputs_match(tmp_path: Path):
    root = tmp_path / "hub"
    root.mkdir()
    report = evaluate_behavior(
        root,
        write_suite(tmp_path),
        write_results(tmp_path, "baseline", subject="baseline"),
        write_results(tmp_path, "candidate", subject="candidate"),
    )
    saved = root / ".skill-engineering" / "evaluations" / f"{report.id}.json"
    data = json.loads(saved.read_text(encoding="utf-8"))
    data["decision"] = "reject"
    saved.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    _, warnings = load_evaluation_report(saved)
    assert any("重算结果不一致" in warning for warning in warnings)


def test_rejects_oversized_input(tmp_path: Path):
    path = tmp_path / "oversized.json"
    path.write_bytes(b"x" * (MAX_INPUT_BYTES + 1))
    with pytest.raises(SystemExit, match="过大"):
        load_evaluation_suite(path)

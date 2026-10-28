from __future__ import annotations

import copy
import importlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


AREAS = ["ownership", "routing", "interfaces", "state", "failure", "rollback"]
METRICS = {
    "skill_md_lines": 20,
    "instruction_files": 2,
    "duplicate_instruction_lines": 0,
}
FINGERPRINTS = {"target": "a" * 64, "candidate": "b" * 64, "effective": "c" * 64}


def review_module():
    try:
        return importlib.import_module("skill_engineering.architecture_review")
    except ModuleNotFoundError:
        pytest.fail("缺少 architecture_review 阶段实现")


def declaration(*, full: bool = True, decision: str = "extend") -> dict:
    value = {
        "schema_version": "1",
        "requirement": {
            "summary": "收窄现有触发入口",
            "decision": decision,
            "rationale": "现有职责归属不变",
            "owner": "现有入口",
            "replacement_plan": "保留既有结构，替换旧描述",
            "protected_behaviors": ["显式请求才触发"],
            "touched_boundaries": [],
        },
        "budgets": {
            "skill_md_lines": 10,
            "instruction_files": 2,
            "duplicate_instruction_lines": 0,
            "open_debt": 2,
        },
        "debt": [],
        "resolved_debt_ids": [],
    }
    if full:
        value["full_review"] = {
            **{f"{key}_fingerprint": item for key, item in FINGERPRINTS.items()},
            "checked_areas": AREAS,
            "conclusion": "pass",
            "reviewer": "独立评审者",
            "evidence_summary": "检查完整候选的六项架构边界后接受本次修改。",
        }
    return value


def assess(target: Path, value: dict | None = None, *, history=None, after=None):
    return review_module().assess_architecture(
        declaration=value,
        target=target,
        target_fingerprint=FINGERPRINTS["target"],
        candidate_fingerprint=FINGERPRINTS["candidate"],
        effective_fingerprint=FINGERPRINTS["effective"],
        complexity={"before": METRICS, "after": after or METRICS, "delta": {}},
        findings=[],
        history=history or [],
    )


def record(target: Path, snapshot: dict, *, record_id="baseline", after=None, **kwargs):
    values = {
        "id": record_id,
        "target": str(target),
        "status": "applied",
        "verification": {"status": "passed", "drifted": False},
        "after_fingerprint": FINGERPRINTS["effective"],
        "complexity": {"after": after or METRICS},
        "preflight": {"architecture_review": snapshot},
        "created_at": "2026-10-29T01:00:00+00:00",
    }
    values.update(kwargs)
    return SimpleNamespace(**values)


def test_missing_declaration_blocks_and_keeps_measured_input_fingerprints(tmp_path: Path):
    report = assess(tmp_path)
    assert report["status"] == "blocked"
    assert report["blocking_findings"]
    assert {key: report["input_fingerprints"][key] for key in FINGERPRINTS} == FINGERPRINTS


@pytest.mark.parametrize("decision, expected", [("extend", "pass"), ("refactor", "pass"),
                                                ("split", "blocked"), ("defer", "blocked")])
def test_requirement_decisions_gate_current_candidate(tmp_path, decision, expected):
    report = assess(tmp_path, declaration(decision=decision))
    assert report["status"] == expected
    assert report["requirement_decision"] == decision


def test_first_review_requires_full_evidence_and_preserves_limitations(tmp_path):
    report = assess(tmp_path, declaration(full=False))
    assert report["status"] == "blocked"
    assert report["baseline"]["status"] == "missing"
    assert "baseline_missing" in report["whole_review"]["reasons"]
    accepted = assess(tmp_path, declaration())
    assert accepted["whole_review"]["status"] == "accepted"
    assert any("行为" in item for item in accepted["limitations"])


@pytest.mark.parametrize("field", ["target_fingerprint", "candidate_fingerprint",
                                  "effective_fingerprint"])
def test_full_review_rejects_every_stale_fingerprint(tmp_path, field):
    value = declaration()
    value["full_review"][field] = "d" * 64
    assert assess(tmp_path, value)["status"] == "blocked"


@pytest.mark.parametrize("mutation", ["areas", "conclusion"])
def test_incomplete_or_rejected_full_review_blocks(tmp_path, mutation):
    value = declaration()
    if mutation == "areas":
        value["full_review"]["checked_areas"] = AREAS[:-1]
    else:
        value["full_review"]["conclusion"] = "changes_requested"
    assert assess(tmp_path, value)["status"] == "blocked"


def test_local_change_does_not_reset_cumulative_baseline(tmp_path):
    baseline = record(tmp_path, assess(tmp_path, declaration()))
    first_after = {**METRICS, "skill_md_lines": 26}
    first = assess(tmp_path, declaration(full=False), history=[baseline], after=first_after)
    assert first["status"] == "pass"
    local_record = record(tmp_path, first, record_id="local", after=first_after,
                          created_at="2026-10-29T02:00:00+00:00")
    second = assess(tmp_path, declaration(full=False), history=[local_record, baseline],
                    after={**METRICS, "skill_md_lines": 32})
    assert second["baseline"]["record_id"] == "baseline"
    assert second["complexity"]["cumulative_delta"]["skill_md_lines"] == 12
    assert "budget_exceeded" in second["whole_review"]["reasons"]
    assert second["status"] == "blocked"
    accepted = assess(tmp_path, declaration(), history=[local_record, baseline],
                      after={**METRICS, "skill_md_lines": 32})
    assert accepted["status"] == "pass"
    assert accepted["complexity"]["budget_exceeded"] == ["skill_md_lines"]


@pytest.mark.parametrize("mutation", ["wrong_target", "undone", "rolled_back", "unverified",
                                      "after_drift"])
def test_explicit_invalid_baseline_is_safely_rejected(tmp_path, mutation):
    previous = record(tmp_path, assess(tmp_path, declaration()))
    if mutation == "wrong_target":
        previous.target = str(tmp_path / "other")
    elif mutation in {"undone", "rolled_back"}:
        previous.status = mutation
    elif mutation == "unverified":
        previous.verification = {"status": "passed"}
    else:
        previous.after_fingerprint = "d" * 64
    value = declaration()
    value["baseline_record_id"] = "baseline"
    assert assess(tmp_path, value, history=[previous])["status"] == "blocked"


def test_debt_carries_merges_and_requires_explicit_resolution(tmp_path):
    value = declaration()
    value["debt"] = [{"id": "routing-debt", "summary": "入口仍有重复路由"}]
    baseline = record(tmp_path, assess(tmp_path, value))
    carried = assess(tmp_path, declaration(full=False), history=[baseline])
    assert [item["id"] for item in carried["debt"]] == ["routing-debt"]
    duplicate = declaration(full=False)
    duplicate["debt"] = value["debt"]
    repeated = assess(tmp_path, duplicate, history=[baseline])
    assert len(repeated["debt"]) == 1
    assert "repeated_debt" in repeated["whole_review"]["reasons"]
    assert repeated["status"] == "blocked"
    resolved = declaration(full=False)
    resolved["resolved_debt_ids"] = ["routing-debt"]
    assert assess(tmp_path, resolved, history=[baseline])["debt"] == []


def test_boundary_and_budget_changes_trigger_whole_review(tmp_path):
    baseline = record(tmp_path, assess(tmp_path, declaration()))
    changed = declaration(full=False)
    changed["requirement"]["touched_boundaries"] = ["state"]
    assert "boundary_changed" in assess(tmp_path, changed, history=[baseline])["whole_review"]["reasons"]
    changed = declaration(full=False)
    changed["budgets"]["skill_md_lines"] = 100
    assert "budget_changed" in assess(tmp_path, changed, history=[baseline])["whole_review"]["reasons"]


def test_legacy_history_does_not_claim_debt_is_zero(tmp_path):
    legacy = record(tmp_path, {})
    report = assess(tmp_path, declaration(), history=[legacy])
    assert any("历史" in item for item in report["limitations"])


@pytest.mark.parametrize("mutation", ["unknown", "nested_unknown", "bool_budget", "negative",
                                      "duplicate_debt", "bad_boundary", "secret", "wrong_type"])
def test_loader_rejects_invalid_or_secret_input_without_echo(tmp_path, mutation):
    value = declaration()
    if mutation == "unknown":
        value["raw_prompt"] = "private conversation"
    elif mutation == "nested_unknown":
        value["requirement"]["raw_prompt"] = "private conversation"
    elif mutation == "bool_budget":
        value["budgets"]["open_debt"] = True
    elif mutation == "negative":
        value["budgets"]["open_debt"] = -1
    elif mutation == "duplicate_debt":
        value["debt"] = [{"id": "same", "summary": "one"}, {"id": "same", "summary": "two"}]
    elif mutation == "bad_boundary":
        value["requirement"]["touched_boundaries"] = ["arbitrary"]
    elif mutation == "secret":
        value["requirement"]["rationale"] = "token=private-secret-value"
    else:
        value["requirement"] = []
    path = tmp_path / "declaration.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(SystemExit) as error:
        review_module().load_architecture_declaration(path)
    assert "private-secret-value" not in str(error.value)
    assert not (tmp_path / ".skill-engineering").exists()


def test_loader_rejects_duplicate_json_keys_and_oversized_input(tmp_path):
    path = tmp_path / "declaration.json"
    path.write_text('{"schema_version":"1","schema_version":"1"}', encoding="utf-8")
    with pytest.raises(SystemExit):
        review_module().load_architecture_declaration(path)
    path.write_text(" " * (256 * 1024), encoding="utf-8")
    with pytest.raises(SystemExit):
        review_module().load_architecture_declaration(path)


def test_assessment_revalidates_direct_python_inputs(tmp_path):
    value = copy.deepcopy(declaration())
    value["unvalidated"] = True
    with pytest.raises(SystemExit):
        assess(tmp_path, value)


def test_open_debt_budget_is_measured_and_full_acceptance_keeps_exceeded_fact(tmp_path):
    value = declaration()
    value["budgets"]["open_debt"] = 0
    value["debt"] = [{"id": "route", "summary": "有依据的暂留债务"}]
    report = assess(tmp_path, value)
    assert report["status"] == "pass"
    assert report["complexity"]["budget_exceeded"] == ["open_debt"]


def test_newer_local_snapshot_resolution_does_not_resurrect_old_debt(tmp_path):
    value = declaration()
    value["debt"] = [{"id": "route", "summary": "旧路由重复"}]
    baseline = record(tmp_path, assess(tmp_path, value))
    resolved = declaration(full=False)
    resolved["resolved_debt_ids"] = ["route"]
    snapshot = assess(tmp_path, resolved, history=[baseline])
    local = record(tmp_path, snapshot, record_id="local",
                   created_at="2026-10-29T02:00:00+00:00")
    report = assess(tmp_path, declaration(full=False), history=[local, baseline])
    assert report["debt"] == []


def test_existing_baseline_debt_still_exceeds_absolute_open_debt_budget(tmp_path):
    value = declaration()
    value["budgets"]["open_debt"] = 0
    value["debt"] = [{"id": "existing", "summary": "整体评审接受的原有债务"}]
    baseline = record(tmp_path, assess(tmp_path, value))
    current = declaration(full=False)
    current["budgets"]["open_debt"] = 0
    report = assess(tmp_path, current, history=[baseline])
    assert len(report["debt"]) == 1
    assert report["complexity"]["budget_exceeded"] == ["open_debt"]
    assert "budget_exceeded" in report["whole_review"]["reasons"]
    assert report["status"] == "blocked"


def same_second_history(target, *, reopening=False):
    open_value = declaration()
    open_value["debt"] = [{"id": "route", "summary": "旧路由重复"}]
    opened = assess(target, open_value)
    closed = copy.deepcopy(opened)
    closed["whole_review"] = {"status": "not_required", "evidence": None}
    closed["debt"] = []
    closed["resolved_debt_ids"] = ["route"]
    first_snapshot, second_snapshot = (closed, opened) if reopening else (opened, closed)
    first = record(target, first_snapshot, record_id="maintenance-ffffffff",
                   before_fingerprint="a" * 64, after_fingerprint="b" * 64)
    second = record(target, second_snapshot, record_id="maintenance-00000000",
                    before_fingerprint="b" * 64, after_fingerprint="c" * 64)
    return first, second


def test_same_second_causal_chain_preserves_later_resolution_despite_random_ids(tmp_path):
    first, second = same_second_history(tmp_path)
    report = assess(tmp_path, declaration(), history=[second, first])
    assert report["debt"] == []
    assert "history_ambiguous" not in report["whole_review"]["reasons"]


def test_same_second_causal_chain_preserves_later_reopening_despite_random_ids(tmp_path):
    first, second = same_second_history(tmp_path, reopening=True)
    report = assess(tmp_path, declaration(), history=[second, first])
    assert [item["id"] for item in report["debt"]] == ["route"]


def test_latest_full_baseline_uses_same_second_causality_not_random_id(tmp_path):
    first = record(tmp_path, assess(tmp_path, declaration()), record_id="maintenance-ffffffff",
                   before_fingerprint="a" * 64, after_fingerprint="c" * 64)
    second_snapshot = assess(tmp_path, declaration())
    second_snapshot["input_fingerprints"]["effective"] = "d" * 64
    second_snapshot["whole_review"]["evidence"]["effective_fingerprint"] = "d" * 64
    second = record(tmp_path, second_snapshot, record_id="maintenance-00000000",
                    before_fingerprint="c" * 64, after_fingerprint="d" * 64,
                    after={**METRICS, "skill_md_lines": 24})
    report = assess(tmp_path, declaration(full=False), history=[first, second],
                    after={**METRICS, "skill_md_lines": 25})
    assert report["baseline"]["record_id"] == "maintenance-00000000"
    assert report["complexity"]["cumulative_delta"]["skill_md_lines"] == 1


@pytest.mark.parametrize("shape", ["missing", "branch", "cycle"])
def test_ambiguous_same_second_history_requires_review_and_never_silently_clears_debt(tmp_path, shape):
    first, second = same_second_history(tmp_path)
    if shape == "missing":
        del first.before_fingerprint
    elif shape == "branch":
        second.before_fingerprint = first.before_fingerprint
    else:
        second.after_fingerprint = first.before_fingerprint
    report = assess(tmp_path, declaration(full=False), history=[first, second])
    assert "history_ambiguous" in report["whole_review"]["reasons"]
    assert any("history_ambiguous" in item for item in report["limitations"])
    assert [item["id"] for item in report["debt"]] == ["route"]
    assert report["status"] == "blocked"
    accepted = assess(tmp_path, declaration(), history=[first, second])
    assert accepted["status"] == "pass"
    assert [item["id"] for item in accepted["debt"]] == ["route"]


def test_ambiguous_same_second_full_reviews_do_not_guess_latest_baseline(tmp_path):
    first = record(tmp_path, assess(tmp_path, declaration()), record_id="maintenance-ffffffff")
    second = record(tmp_path, assess(tmp_path, declaration()), record_id="maintenance-00000000")
    report = assess(tmp_path, declaration(full=False), history=[first, second])
    assert report["baseline"]["status"] == "missing"
    assert "history_ambiguous" in report["whole_review"]["reasons"]


@pytest.mark.parametrize("key", ["access_token", "refresh_token", "app_secret",
                                  "client_secret", "OPENAI_API_KEY", "AWS_SECRET_ACCESS_KEY"])
@pytest.mark.parametrize("field", ["rationale", "protected_behavior", "debt_summary",
                                    "reviewer", "evidence_summary"])
def test_prefixed_secret_assignment_rejected_by_loader_and_direct_assessment(tmp_path, key, field):
    value = declaration()
    secret = "synthetic-private-value"
    assignment = f"{key}={secret}"
    if field == "protected_behavior":
        value["requirement"]["protected_behaviors"] = [assignment]
    elif field == "debt_summary":
        value["debt"] = [{"id": "route", "summary": assignment}]
    elif field in {"reviewer", "evidence_summary"}:
        value["full_review"][field] = assignment
    else:
        value["requirement"][field] = assignment
    path = tmp_path / "declaration.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(SystemExit) as loaded:
        review_module().load_architecture_declaration(path)
    with pytest.raises(SystemExit) as direct:
        assess(tmp_path, value)
    assert secret not in str(loaded.value)
    assert secret not in str(direct.value)


@pytest.mark.parametrize("assignment", ['"token": "synthetic-private-value"',
                                        "private_key=synthetic-private-value"])
def test_quoted_generic_token_and_private_key_assignments_are_rejected(tmp_path, assignment):
    value = declaration()
    value["requirement"]["rationale"] = assignment
    path = tmp_path / "declaration.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(SystemExit) as loaded:
        review_module().load_architecture_declaration(path)
    with pytest.raises(SystemExit) as direct:
        assess(tmp_path, value)
    assert "synthetic-private-value" not in str(loaded.value)
    assert "synthetic-private-value" not in str(direct.value)


def test_external_declaration_still_rejects_129_debts(tmp_path):
    value = declaration()
    value["debt"] = [{"id": f"debt-{index}", "summary": "单次声明债务"} for index in range(129)]
    path = tmp_path / "declaration.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(SystemExit):
        review_module().load_architecture_declaration(path)
    with pytest.raises(SystemExit):
        assess(tmp_path, value)


@pytest.mark.parametrize("mutation", ["duplicate", "secret", "unsafe_id"])
def test_cumulative_snapshot_validates_every_debt_without_truncation(tmp_path, mutation):
    report = assess(tmp_path, declaration())
    report["budgets"]["open_debt"] = 200
    report["debt"] = [{"id": f"debt-{index}", "summary": "跨轮已知债务"} for index in range(140)]
    if mutation == "duplicate":
        report["debt"][139]["id"] = report["debt"][0]["id"]
    elif mutation == "secret":
        report["debt"][139]["summary"] = "app_secret=synthetic-private-value"
    else:
        report["debt"][139]["id"] = "../unsafe"
    with pytest.raises(SystemExit) as error:
        review_module().validate_architecture_snapshot(
            report,
            target_fingerprint=FINGERPRINTS["target"],
            candidate_fingerprint=FINGERPRINTS["candidate"],
            effective_fingerprint=FINGERPRINTS["effective"],
        )
    assert "synthetic-private-value" not in str(error.value)

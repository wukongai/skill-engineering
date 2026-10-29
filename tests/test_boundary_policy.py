from __future__ import annotations

import copy
import importlib
import importlib.util
import json
from pathlib import Path

import pytest


def rules():
    assert importlib.util.find_spec("skill_engineering.boundary_policy") is not None, (
        "missing canonical boundary policy"
    )
    return importlib.import_module("skill_engineering.boundary_policy")


def boundary(**changes):
    value = {
        "goal": "整理会议记录", "mission": "提取决定与行动项",
        "owned_capabilities": ["提取决定"], "excluded_capabilities": ["发送消息"],
        "allowed_context": ["会议后"], "positive_triggers": ["整理记录"],
        "negative_triggers": ["发送通知"], "inputs": ["记录"], "outputs": ["摘要"],
        "drift_signals": ["请求发送"], "redirect_strategy": ["说明边界并停止"],
        "stop_conditions": ["没有记录"], "side_effects": [], "approvals": [],
    }
    value.update(changes)
    return value


def policy(**changes):
    value = {
        "interaction": "single_turn", "uses_tools": False,
        "has_side_effects": False, "rationale": "只整理提供的文本",
    }
    value.update(changes)
    return value


def confirmation(value=None, **changes):
    value = boundary() if value is None else value
    result = {
        "schema_version": "1", "subject_id": "brief-1",
        "boundary_fingerprint": rules().boundary_fingerprint(value),
        "status": "confirmed", "source": "explicit_user_message",
        "summary": "用户确认整理记录及发送消息排除项",
        "excluded_decision": "listed" if value["excluded_capabilities"] else "none",
        "behavior_policy": policy(),
    }
    result.update(changes)
    return result


def case(category="success", **changes):
    value = {
        "id": category, "category": category, "given": "提供记录",
        "expect": "输出摘要", "must_not": ["猜测"],
        "assertions": {"must_include": ["整理"], "must_not_include": ["伪造"]},
    }
    value.update(changes)
    return value


def declaration():
    value = boundary()
    return {
        "schema_version": "1", "change": "changed", "boundary": value,
        "confirmation": confirmation(value),
        "cases": [case(name) for name in ("success", "insufficient", "negative")],
    }


FP = {"target_fingerprint": "a" * 64, "candidate_fingerprint": "b" * 64,
      "effective_fingerprint": "c" * 64}


def test_projection_uses_only_business_fields_and_normalizes_outer_whitespace():
    value = boundary(goal=" 整理会议记录 ", owned_capabilities=[" 提取决定 "])
    value.update(id="brief-1", status="draft", updated_at="later")
    assert rules().boundary_projection(value) == boundary()
    assert rules().boundary_fingerprint(value) == rules().boundary_fingerprint(boundary())
    changed = boundary(outputs=["不同输出"])
    assert rules().boundary_fingerprint(changed) != rules().boundary_fingerprint(value)


def test_projection_defaults_optional_list_fields_to_existing_empty_value():
    value = boundary()
    for key in ("excluded_capabilities", "allowed_context", "negative_triggers", "inputs",
                "outputs", "side_effects", "approvals"):
        value.pop(key)
    projected = rules().boundary_projection(value)
    assert all(projected[key] == [] for key in (
        "excluded_capabilities", "allowed_context", "negative_triggers", "inputs",
        "outputs", "side_effects", "approvals",
    ))
    assert rules().boundary_fingerprint(value) == rules().boundary_fingerprint(projected)


@pytest.mark.parametrize("changes", [
    {"goal": []}, {"owned_capabilities": "text"}, {"goal": "x" * 4001},
    {"inputs": ["x"] * 129}, {"goal": "password=private-value"},
    {"mission": ""}, {"redirect_strategy": []},
])
def test_boundary_rejects_invalid_or_sensitive_values(changes):
    with pytest.raises(rules().BoundaryError):
        rules().boundary_projection(boundary(**changes))


def test_confirmation_is_bound_to_projection_subject_and_explicit_empty_exclusions():
    value = boundary(excluded_capabilities=[], negative_triggers=[])
    confirmed = confirmation(value, excluded_decision="none")
    assert rules().validate_confirmation(value, confirmed, subject_id="brief-1") == confirmed
    with pytest.raises(rules().BoundaryError):
        rules().validate_confirmation(value, confirmed, subject_id="other")
    with pytest.raises(rules().BoundaryError):
        rules().validate_confirmation(boundary(goal="不同目标"), confirmation())
    with pytest.raises(rules().BoundaryError):
        rules().validate_confirmation(value, confirmation(value, excluded_decision="listed"))


@pytest.mark.parametrize("changes", [
    {"schema_version": 1}, {"status": "pending"}, {"status": "rejected"},
    {"status": "stale"}, {"status": "legacy_unknown"}, {"source": "candidate"},
    {"source": "ai_generated"}, {"summary": ""}, {"unexpected": True},
    {"message_ref": ""}, {"subject_id": True}, {"boundary_fingerprint": "not-a-hash"},
    {"summary": "token=do-not-leak"},
])
def test_confirmation_rejects_invalid_evidence_without_echoing_sensitive_text(changes):
    with pytest.raises(rules().BoundaryError) as caught:
        rules().validate_confirmation(boundary(), confirmation(**changes))
    assert "do-not-leak" not in str(caught.value)


@pytest.mark.parametrize("field", ["goal", "summary", "rationale"])
def test_unpaired_surrogate_is_boundary_error_without_input_excerpt(field):
    invalid = "\ud800private-input"
    with pytest.raises(rules().BoundaryError) as caught:
        if field == "goal":
            rules().boundary_fingerprint(boundary(goal=invalid))
        elif field == "summary":
            rules().validate_confirmation(boundary(), confirmation(summary=invalid))
        else:
            rules().validate_behavior_policy(policy(rationale=invalid), boundary())
    assert "private-input" not in str(caught.value)
    assert "\ud800" not in str(caught.value)


@pytest.mark.parametrize("changes", [
    {"uses_tools": "false"}, {"has_side_effects": 0}, {"interaction": "agent"},
    {"rationale": ""}, {"extra": True},
])
def test_behavior_policy_is_strict(changes):
    with pytest.raises(rules().BoundaryError):
        rules().validate_behavior_policy(policy(**changes), boundary())


def test_declared_side_effects_cannot_be_hidden_by_policy():
    value = boundary(side_effects=["写入文件"])
    with pytest.raises(rules().BoundaryError):
        rules().validate_behavior_policy(policy(), value)
    assert rules().validate_behavior_policy(policy(has_side_effects=True), value)[
        "has_side_effects"
    ]


@pytest.mark.parametrize("assertions", [None, {}, {"must_include": [], "must_not_include": []}])
def test_empty_assertions_are_uncovered(assertions):
    result = rules().run_text_cases("整理", [case(assertions=assertions)])
    assert result["status"] == "uncovered"
    assert result["passed"] == 0


@pytest.mark.parametrize("assertions", [
    [], {"include": ["整理"]}, {"must_include": "整理"},
    {"must_include": [""]}, {"must_not_include": [1]},
])
def test_malformed_assertions_are_failed(assertions):
    result = rules().run_text_cases("整理", [case(assertions=assertions)])
    assert result["status"] == "failed"
    assert result["failed"] == 1


@pytest.mark.parametrize("changes", [
    {"assertions": {"must_include": [{"secret": "do-not-leak"}]}},
    {"assertions": {"must_include": ["password=do-not-leak"]}},
    {"given": "", "assertions": []},
    {"expect": "", "assertions": {"must_include": "password=do-not-leak"}},
    {"category": {"secret": "do-not-leak"}},
    {"status": ["not_applicable"]},
    {"must_not": [{"password": "do-not-leak"}]},
    {"given": {"secret": "do-not-leak"}},
    {"id": "token=do-not-leak"},
])
def test_deep_invalid_case_values_fail_without_sensitive_text_or_wrong_exception(changes):
    result = rules().run_text_cases("整理", [case(**changes)])
    assert result["status"] == "failed"
    assert "do-not-leak" not in json.dumps(result)


@pytest.mark.parametrize("cases", [[], ["旧标签"], [case(given="")], [{}]])
def test_no_executable_case_cannot_pass(cases):
    result = rules().run_text_cases("整理", cases)
    assert result["status"] == "uncovered"
    assert result["evidence_kind"] == "candidate_text"
    assert result["utility_claim"] is False


@pytest.mark.parametrize("cases", [[case(id="")], [case(), case()], [case(unknown=True)], [42]])
def test_invalid_case_schema_or_ids_fail(cases):
    assert rules().run_text_cases("整理", cases)["status"] == "failed"


def test_real_text_assertions_report_pass_and_failure():
    result = rules().run_text_cases("整理", [case(), case("insufficient", assertions={
        "must_include": ["缺口"], "must_not_include": ["整理"],
    })])
    assert result["status"] == "failed"
    assert result["passed"] == 1
    assert result["cases"][1]["missing"] == ["缺口"]
    assert result["cases"][1]["forbidden"] == ["整理"]


def test_text_assertions_keep_exact_nonempty_whitespace_semantics():
    result = rules().run_text_cases("整理", [case(assertions={"must_include": ["整理 "]})])
    assert result["status"] == "failed"
    assert result["cases"][0]["missing"] == ["整理 "]


@pytest.mark.parametrize("must_not", [[], "不猜测"])
def test_must_not_can_be_empty_list_or_text_when_actual_assertions_exist(must_not):
    assert rules().run_text_cases("整理", [case(must_not=must_not)])["status"] == "passed"


def test_policy_requires_categories_from_declared_capabilities():
    required = {"success", "insufficient", "negative", "drift", "failure", "approval"}
    selected = policy(interaction="multi_turn", uses_tools=True, has_side_effects=True)
    value = boundary(side_effects=["保存文件"])
    result = rules().run_text_cases("整理", [case("success")], policy=selected, boundary=value)
    assert result["status"] != "passed"
    assert set(result["required_categories"]) == required
    assert set(result["missing_categories"]) == required - {"success"}
    result = rules().run_text_cases("整理", [case(name) for name in sorted(required)],
                                   policy=selected, boundary=value)
    assert result["status"] == "passed"


def test_not_applicable_is_counted_separately_and_cannot_skip_required_category():
    value = boundary(excluded_capabilities=[], negative_triggers=[])
    cases = [case("success"), case("insufficient"), {
        "id": "drift-na", "category": "drift", "status": "not_applicable",
        "reason": "单次任务没有后续轮次",
    }]
    result = rules().run_text_cases("整理", cases, policy=policy(), boundary=value)
    assert result["status"] == "passed"
    assert result["passed"] == 2
    assert result["not_applicable"] == 1
    cases[2]["category"] = "success"
    assert rules().run_text_cases("整理", cases, policy=policy(), boundary=value)["status"] == "failed"


@pytest.mark.parametrize("item", [
    {"id": "na", "status": "not_applicable", "reason": "单次任务"},
    {"id": "na", "category": "drift", "status": "not_applicable", "reason": ""},
])
def test_not_applicable_requires_category_and_reason(item):
    assert rules().run_text_cases("整理", [item])["status"] == "failed"


def test_maintenance_missing_unchanged_and_changed_outcomes_are_distinct():
    missing = rules().assess_boundary(None, **FP)
    assert missing["status"] == "unreviewed" and missing["blocking_findings"]
    unchanged = {"schema_version": "1", "change": "unchanged", "reason": "仅修正错字"}
    report = rules().assess_boundary(unchanged, **FP)
    assert report["status"] == "pass"
    assert report["confirmation_status"] == "legacy_unknown"
    assert rules().assess_boundary(unchanged, architecture_boundary_changed=True,
                                   **FP)["status"] == "blocked"
    changed = rules().assess_boundary(declaration(), candidate_text="整理", **FP)
    assert changed["status"] == "pass"
    assert changed["confirmation_status"] == "confirmed"


@pytest.mark.parametrize("value", [
    {}, {"schema_version": "1", "change": "unchanged"},
    {"schema_version": "1", "change": "unchanged", "reason": "错字", "extra": True},
    {"schema_version": "1", "change": "changed"},
])
def test_invalid_maintenance_declarations_block(value):
    assert rules().assess_boundary(value, **FP)["status"] == "blocked"


def test_report_is_deterministic_frozen_and_snapshot_rejects_all_tampering():
    value = declaration()
    report = rules().assess_boundary(value, candidate_text="整理", **FP)
    before = copy.deepcopy(report)
    value["boundary"]["goal"] = "另一个目标"
    assert report == before
    assert "timestamp" not in json.dumps(report)
    rules().validate_boundary_snapshot(report, candidate_text="整理", **FP)
    for key, changed in (
        ("status", "blocked"), ("confirmation_status", "legacy_unknown"),
        ("blocking_findings", ["tamper"]), ("utility_claim", True),
    ):
        tampered = copy.deepcopy(report)
        tampered[key] = changed
        with pytest.raises(rules().BoundaryError):
            rules().validate_boundary_snapshot(tampered, candidate_text="整理", **FP)
    with pytest.raises(rules().BoundaryError):
        rules().validate_boundary_snapshot(report, candidate_text="没有匹配文本", **FP)
    with pytest.raises(rules().BoundaryError):
        rules().validate_boundary_snapshot(report, candidate_text="整理", **{
            **FP, "candidate_fingerprint": "d" * 64,
        })


def test_portable_policy_is_identical_and_imports_without_python_package():
    root = Path(__file__).resolve().parents[1]
    canonical = root / "src/skill_engineering/boundary_policy.py"
    portable = root / "skills/skill-engineering/scripts/boundary_policy.py"
    assert canonical.is_file(), "missing canonical boundary policy"
    assert portable.is_file(), "missing generated portable boundary policy"
    assert portable.read_bytes() == canonical.read_bytes()
    spec = importlib.util.spec_from_file_location("portable_boundary_policy", portable)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.boundary_fingerprint(boundary()) == rules().boundary_fingerprint(boundary())

from __future__ import annotations

from pathlib import Path

import pytest

from skill_engineering.maintenance import (
    apply_improvement_plan,
    create_improvement_plan,
    maintenance_history,
    undo_improvement,
    verify_improvement,
)


def skill_text(description: str, body: str = "Use this for a narrow task.") -> str:
    return f"---\nname: demo-skill\ndescription: {description}\n---\n\n# Demo\n\n{body}\n"


def setup_pair(tmp_path: Path) -> tuple[Path, Path, Path]:
    root = tmp_path / "hub"
    target = tmp_path / "demo-skill"
    candidate = tmp_path / "candidate"
    root.mkdir()
    target.mkdir()
    candidate.mkdir()
    (target / "SKILL.md").write_text(skill_text("旧描述。"), encoding="utf-8")
    (candidate / "SKILL.md").write_text(skill_text("更新后的窄触发描述。"), encoding="utf-8")
    case = candidate / "tests" / "cases" / "trigger.yaml"
    case.parent.mkdir(parents=True)
    case.write_text("id: trigger-regression\n", encoding="utf-8")
    return root, target, candidate


def plan_for(root: Path, target: Path, candidate: Path, **kwargs):
    if "architecture_review" not in kwargs:
        kwargs["architecture_review"] = architecture_input(
            root, target, candidate, deletions=kwargs.get("deletions")
        )
    if "boundary_review" not in kwargs:
        kwargs["boundary_review"] = boundary_input(root)
    return create_improvement_plan(
        root,
        target,
        candidate,
        failure_mode="旧 description 会误触发",
        root_cause_layer="trigger",
        expected_behavior="只有明确请求才触发",
        regression_cases=["tests/cases/trigger.yaml"],
        profile=kwargs.pop("profile", "team"),
        acceptance_cases=kwargs.pop("acceptance_cases", ["tests/cases/trigger.yaml"]),
        **kwargs,
    )


def boundary_input(root, *, includes=None, excludes=None):
    """Explicit synthetic operator fixture for the changed demo trigger contract."""
    import json

    from skill_engineering.boundary_policy import boundary_fingerprint

    boundary = {
        "goal": "只在明确请求演示任务时处理输入",
        "mission": "按输入输出演示结果",
        "owned_capabilities": ["处理演示任务"],
        "excluded_capabilities": [],
        "allowed_context": [],
        "positive_triggers": ["明确请求演示任务"],
        "negative_triggers": [],
        "inputs": ["任务输入"],
        "outputs": ["演示结果"],
        "drift_signals": ["请求演示能力之外的任务"],
        "redirect_strategy": ["说明边界并停止"],
        "stop_conditions": ["没有任务输入"],
        "side_effects": [],
        "approvals": [],
    }
    assertions = {"must_include": includes or ["# Demo"]}
    if excludes:
        assertions["must_not_include"] = excludes
    value = {
        "schema_version": "1", "change": "changed", "boundary": boundary,
        "confirmation": {
            "schema_version": "1", "subject_id": "synthetic-demo-fixture",
            "boundary_fingerprint": boundary_fingerprint(boundary),
            "status": "confirmed", "source": "explicit_cli_argument",
            "summary": "合成测试操作者确认本示例触发范围及无额外排除项。",
            "excluded_decision": "none",
            "behavior_policy": {"interaction": "single_turn", "uses_tools": False,
                                "has_side_effects": False, "rationale": "演示 Skill 仅处理输入文本。"},
        },
        "cases": [
            {"id": category, "category": category, "given": "合成输入或缺输入",
             "expect": "输出演示结果或说明输入缺口", "must_not": ["猜测输入"],
             "assertions": assertions}
            for category in ("success", "insufficient")
        ],
    }
    path = root / "boundary.json"
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path


def test_missing_maintenance_intent_or_regression_blocks_apply(tmp_path: Path):
    root, target, candidate = setup_pair(tmp_path)
    plan = create_improvement_plan(root, target, candidate)

    assert plan.preflight["status"] == "blocked"
    assert any(item["rule_id"] == "MAINT106" and item["level"] == "FAIL" for item in plan.findings)
    with pytest.raises(SystemExit, match="preflight"):
        apply_improvement_plan(root, plan)


def test_maintenance_plan_exposes_convergence_gate_and_deferred_debt(tmp_path: Path):
    root, target, candidate = setup_pair(tmp_path)
    retained = target / "references" / "legacy.md"
    retained.parent.mkdir()
    retained.write_text("legacy structure\n", encoding="utf-8")
    plan = plan_for(
        root,
        target,
        candidate,
        maintenance_goal="收窄触发边界",
        baseline_version="1.0.0",
        max_repair_rounds=2,
    )

    assert plan.maintenance_goal == "收窄触发边界"
    assert plan.baseline_version == "1.0.0"
    assert plan.max_repair_rounds == 2
    assert plan.acceptance_cases == ["tests/cases/trigger.yaml"]
    assert plan.repair_round == 0
    assert plan.preflight["convergence"]["status"] == "converged"
    assert "当前阻断项清零" in plan.completion_gate
    assert plan.deferred_debt
    assert plan.convergence["next_action"] == "建立独立 refactor/backlog 计划"


def test_acceptance_cases_are_separate_from_regression_cases(tmp_path: Path):
    root, target, candidate = setup_pair(tmp_path)
    plan = plan_for(
        root,
        target,
        candidate,
        acceptance_cases=["tests/cases/current.yaml"],
    )

    assert plan.regression_cases == ["tests/cases/trigger.yaml"]
    assert plan.acceptance_cases == ["tests/cases/current.yaml"]
    assert plan.convergence["regression_required"] == ["tests/cases/trigger.yaml"]
    assert plan.convergence["acceptance_cases"] == ["tests/cases/current.yaml"]


def test_maintenance_plan_rejects_unbounded_repair_rounds(tmp_path: Path):
    root, target, candidate = setup_pair(tmp_path)
    with pytest.raises(SystemExit, match="1..3"):
        plan_for(root, target, candidate, max_repair_rounds=4)


def test_verify_increments_round_and_hard_stops_after_limit(tmp_path: Path, monkeypatch):
    root, target, candidate = setup_pair(tmp_path)
    plan = plan_for(root, target, candidate, max_repair_rounds=1)
    record = apply_improvement_plan(root, plan)
    monkeypatch.setattr(
        "skill_engineering.maintenance._audit_tree",
        lambda _path, _profile: {"status": "blocked", "lint": {}, "doctor": {}},
    )

    verified = verify_improvement(root, record.id)

    assert verified.repair_round == 1
    assert verified.status == "needs_improvement"
    assert verified.convergence["status"] == "needs_improvement"
    assert verified.convergence["next_action"] == "建立新的候选修复计划"


def test_complexity_delta_detects_prompt_debt_growth(tmp_path: Path):
    root, target, candidate = setup_pair(tmp_path)
    body = "\n".join(
        ["禁止直接执行。", "这是一次事故复盘。", *[f"稳定步骤 {index}" for index in range(14)]]
    )
    (candidate / "SKILL.md").write_text(skill_text("更新后的窄触发描述。", body), encoding="utf-8")

    plan = plan_for(root, target, candidate)

    assert plan.complexity["delta"]["skill_md_lines"] > 10
    assert plan.complexity["delta"]["gate_terms"] > 0
    ids = {item["rule_id"] for item in plan.findings}
    assert {"MAINT101", "MAINT102", "MAINT103"} <= ids
    assert plan.preflight["status"] == "pass"


def test_apply_verify_history_and_safe_undo_with_explicit_delete(tmp_path: Path):
    root, target, candidate = setup_pair(tmp_path)
    obsolete = target / "references" / "obsolete.md"
    obsolete.parent.mkdir()
    obsolete.write_text("legacy\n", encoding="utf-8")
    before = (target / "SKILL.md").read_text(encoding="utf-8")
    plan = plan_for(root, target, candidate, deletions=["references/obsolete.md"])

    assert plan.preflight["status"] == "pass"
    record = apply_improvement_plan(root, plan)

    assert record.status == "applied"
    assert record.undo_available is True
    assert not obsolete.exists()
    assert (target / "tests" / "cases" / "trigger.yaml").is_file()
    assert "更新后的窄触发描述" in (target / "SKILL.md").read_text(encoding="utf-8")
    verified = verify_improvement(root, record.id)
    assert verified.verification["status"] == "passed"
    assert [item.id for item in maintenance_history(root, target)] == [record.id]

    undone = undo_improvement(root, record.id)
    assert undone.status == "undone"
    assert obsolete.read_text(encoding="utf-8") == "legacy\n"
    assert not (target / "tests" / "cases" / "trigger.yaml").exists()
    assert (target / "SKILL.md").read_text(encoding="utf-8") == before


def test_candidate_missing_files_are_retained_not_deleted(tmp_path: Path):
    root, target, candidate = setup_pair(tmp_path)
    retained = target / "references" / "keep.md"
    retained.parent.mkdir()
    retained.write_text("keep\n", encoding="utf-8")

    plan = plan_for(root, target, candidate)
    record = apply_improvement_plan(root, plan)

    assert "references/keep.md" in plan.retained_legacy_files
    assert any(item["rule_id"] == "MAINT105" for item in plan.findings)
    assert retained.read_text(encoding="utf-8") == "keep\n"
    assert record.status == "applied"


def test_target_candidate_and_plan_drift_are_rejected(tmp_path: Path):
    root, target, candidate = setup_pair(tmp_path)
    target_plan = plan_for(root, target, candidate)
    (target / "SKILL.md").write_text(skill_text("并发修改。"), encoding="utf-8")
    with pytest.raises(SystemExit, match="目标 Skill"):
        apply_improvement_plan(root, target_plan)

    (target / "SKILL.md").write_text(skill_text("旧描述。"), encoding="utf-8")
    candidate_plan = plan_for(root, target, candidate)
    (candidate / "SKILL.md").write_text(skill_text("候选又修改。"), encoding="utf-8")
    with pytest.raises(SystemExit, match="候选 Skill"):
        apply_improvement_plan(root, candidate_plan)

    (candidate / "SKILL.md").write_text(skill_text("更新后的窄触发描述。"), encoding="utf-8")
    hash_plan = plan_for(root, target, candidate)
    hash_plan.expected_behavior = "被篡改"
    with pytest.raises(SystemExit, match="plan hash"):
        apply_improvement_plan(root, hash_plan)


def test_postflight_failure_rolls_back(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    import skill_engineering.maintenance as maintenance

    root, target, candidate = setup_pair(tmp_path)
    before = (target / "SKILL.md").read_text(encoding="utf-8")
    plan = plan_for(root, target, candidate)
    monkeypatch.setattr(
        maintenance,
        "_audit_tree",
        lambda _path, _profile: {"status": "blocked", "lint": {}, "doctor": {}},
    )

    with pytest.raises(SystemExit, match="自动回滚"):
        apply_improvement_plan(root, plan)

    assert (target / "SKILL.md").read_text(encoding="utf-8") == before
    records = maintenance_history(root, target)
    assert records[0].status == "rolled_back"


def test_drift_disables_verify_and_undo(tmp_path: Path):
    root, target, candidate = setup_pair(tmp_path)
    record = apply_improvement_plan(root, plan_for(root, target, candidate))
    (target / "SKILL.md").write_text(skill_text("人工后续修改。"), encoding="utf-8")

    verified = verify_improvement(root, record.id)
    assert verified.verification["status"] == "failed"
    assert verified.undo_available is False
    with pytest.raises(SystemExit, match="漂移"):
        undo_improvement(root, record.id)


def test_production_requires_regression_case(tmp_path: Path):
    root, target, candidate = setup_pair(tmp_path)
    plan = create_improvement_plan(
        root,
        target,
        candidate,
        failure_mode="修复生产行为",
        root_cause_layer="trigger",
        expected_behavior="行为稳定",
        no_regression_reason="暂时没有",
        profile="production",
    )

    assert plan.preflight["status"] == "blocked"
    assert any(item["rule_id"] == "MAINT106" and item["level"] == "FAIL" for item in plan.findings)


def architecture_input(root, target, candidate, *, deletions=None, full=True):
    import json
    import tempfile

    from test_architecture_review import declaration

    from skill_engineering.journey import fingerprint_path
    from skill_engineering.maintenance import _copy_effective_tree

    value = declaration(full=full)
    if full:
        with tempfile.TemporaryDirectory() as directory:
            effective = Path(directory) / "effective"
            _copy_effective_tree(target, candidate, effective, deletions or [])
            value["full_review"].update(
                target_fingerprint=fingerprint_path(target),
                candidate_fingerprint=fingerprint_path(candidate),
                effective_fingerprint=fingerprint_path(effective),
            )
    path = root / "architecture.json"
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path


@pytest.mark.parametrize("profile", ["personal", "team", "production"])
def test_missing_architecture_declaration_blocks_all_profiles_before_writes(tmp_path, profile):
    from skill_engineering.journey import fingerprint_path
    from skill_engineering.maintenance import _copy_effective_tree, format_improvement_plan

    root, target, candidate = setup_pair(tmp_path)
    before = fingerprint_path(target)
    plan = plan_for(root, target, candidate, architecture_review=None, profile=profile)
    report = plan.preflight["architecture_review"]
    assert report["status"] == "blocked"
    assert plan.preflight["status"] == plan.convergence["status"] == "blocked"
    assert any(item["rule_id"] == "MAINT111" and item["level"] == "FAIL" for item in plan.findings)
    assert report["input_fingerprints"]["target"] == before
    assert report["input_fingerprints"]["candidate"] == fingerprint_path(candidate)
    effective = tmp_path / "measured-effective"
    _copy_effective_tree(target, candidate, effective, [])
    assert report["input_fingerprints"]["effective"] == fingerprint_path(effective)
    preview = format_improvement_plan(plan)
    assert "声明" in preview
    assert "历史债务未评估" in preview
    assert "已知开放架构债务：0 项" not in preview
    with pytest.raises(SystemExit):
        apply_improvement_plan(root, plan)
    assert fingerprint_path(target) == before
    assert not (root / ".skill-engineering" / "maintenance-records").exists()
    assert not (root / ".skill-engineering" / "maintenance-backups").exists()


def historical_unreviewed_record(root, target, candidate):
    from skill_engineering.journey import save_maintenance_record

    record = apply_improvement_plan(root, plan_for(root, target, candidate))
    record.preflight.pop("architecture_review", None)
    record.preflight.pop("boundary_review", None)
    save_maintenance_record(root, record)
    return record


def test_legacy_unreviewed_history_verify_and_undo_remain_compatible(tmp_path):
    from skill_engineering.maintenance import format_maintenance_record

    root, target, candidate = setup_pair(tmp_path)
    record = historical_unreviewed_record(root, target, candidate)
    assert "架构未审查" in format_maintenance_record(record)
    assert verify_improvement(root, record.id).verification["status"] == "passed"
    assert undo_improvement(root, record.id).status == "undone"


def test_legacy_saved_plan_hash_is_not_changed_on_load(tmp_path):
    from skill_engineering.journey import load_build_plan, save_build_plan
    from skill_engineering.maintenance import _plan_hash

    root, target, candidate = setup_pair(tmp_path)
    plan = plan_for(root, target, candidate)
    plan.preflight.pop("architecture_review", None)
    plan.plan_hash = _plan_hash(plan)
    save_build_plan(root, plan)
    loaded = load_build_plan(root, plan.id)
    assert "architecture_review" not in loaded.preflight
    assert loaded.plan_hash == plan.plan_hash == _plan_hash(loaded)
    with pytest.raises(SystemExit, match="架构"):
        apply_improvement_plan(root, loaded)
    assert loaded.plan_hash == plan.plan_hash == _plan_hash(loaded)
    assert not (root / ".skill-engineering" / "maintenance-records").exists()


@pytest.mark.parametrize("snapshot", [None, {"status": "unreviewed"}])
def test_legacy_unreviewed_plan_feedback_requires_new_preview(tmp_path, snapshot):
    from skill_engineering.maintenance import format_improvement_plan

    root, target, candidate = setup_pair(tmp_path)
    plan = plan_for(root, target, candidate)
    if snapshot is None:
        plan.preflight.pop("architecture_review")
    else:
        plan.preflight["architecture_review"] = snapshot
    feedback = format_improvement_plan(plan)
    assert "当前不能应用" in feedback
    assert "重新生成预览" in feedback
    assert "是否继续应用" not in feedback
    assert "方案已经准备好" not in feedback


def test_cumulative_debt_above_single_declaration_limit_can_apply(tmp_path):
    import json

    root, target, candidate = setup_pair(tmp_path)
    for round_number in range(2):
        (candidate / "SKILL.md").write_text(
            skill_text(f"窄触发修订 {round_number}。"), encoding="utf-8"
        )
        path = architecture_input(root, target, candidate)
        value = json.loads(path.read_text(encoding="utf-8"))
        value["budgets"]["open_debt"] = 200
        value["debt"] = [
            {"id": f"debt-{round_number}-{number}", "summary": "已审阅的延后结构改进"}
            for number in range(70)
        ]
        path.write_text(json.dumps(value), encoding="utf-8")
        plan = plan_for(root, target, candidate, architecture_review=path)
        assert plan.preflight["status"] == "pass"
        assert len(plan.preflight["architecture_review"]["debt"]) == 70 * (round_number + 1)
        record = apply_improvement_plan(root, plan)
        assert verify_improvement(root, record.id).verification["status"] == "passed"


def test_architecture_failures_update_both_gates_and_block_apply(tmp_path):
    root, target, candidate = setup_pair(tmp_path)
    path = architecture_input(root, target, candidate, full=False)
    plan = plan_for(root, target, candidate, architecture_review=path)
    assert plan.preflight["status"] == "blocked"
    assert plan.preflight["finding_counts"]["fail"] >= 1
    assert plan.convergence["status"] == "blocked"
    assert plan.convergence["blocking_findings"]
    with pytest.raises(SystemExit, match="preflight"):
        apply_improvement_plan(root, plan)


def test_overlay_and_delete_fingerprints_bind_full_review_and_plan_hash(tmp_path):
    import json

    root, target, candidate = setup_pair(tmp_path)
    retained = target / "references" / "keep.md"
    retained.parent.mkdir()
    retained.write_text("keep\n", encoding="utf-8")
    obsolete = target / "references" / "obsolete.md"
    obsolete.write_text("obsolete\n", encoding="utf-8")
    path = architecture_input(root, target, candidate, deletions=["references/obsolete.md"])
    plan = plan_for(root, target, candidate, architecture_review=path,
                    deletions=["references/obsolete.md"])
    assert plan.preflight["architecture_review"]["status"] == "pass"
    # A changed external declaration cannot change the already previewed plan.
    path.write_text(json.dumps({"schema_version": "invalid"}), encoding="utf-8")
    record = apply_improvement_plan(root, plan)
    assert retained.exists() and not obsolete.exists()
    report = record.preflight["architecture_review"]
    assert report["input_fingerprints"]["effective"] == record.after_fingerprint
    assert verify_improvement(root, record.id).verification["status"] == "passed"
    assert undo_improvement(root, record.id).status == "undone"


def test_architecture_snapshot_tampering_is_rejected_by_existing_hash(tmp_path):
    root, target, candidate = setup_pair(tmp_path)
    path = architecture_input(root, target, candidate)
    plan = plan_for(root, target, candidate, architecture_review=path)
    plan.preflight["architecture_review"]["status"] = "unreviewed"
    with pytest.raises(SystemExit, match="plan hash"):
        apply_improvement_plan(root, plan)


def test_invalid_architecture_input_leaves_no_saved_plan(tmp_path):
    root, target, candidate = setup_pair(tmp_path)
    path = root / "invalid.json"
    path.write_text('{"raw_prompt":"private"}', encoding="utf-8")
    with pytest.raises(SystemExit):
        plan_for(root, target, candidate, architecture_review=path)
    assert not (root / ".skill-engineering" / "build-plans").exists()


def test_verified_full_review_becomes_baseline_across_two_small_applied_changes(tmp_path):
    import json

    root, target, candidate = setup_pair(tmp_path)
    first = plan_for(root, target, candidate,
                     architecture_review=architecture_input(root, target, candidate))
    baseline = apply_improvement_plan(root, first)
    original = (candidate / "SKILL.md").read_text(encoding="utf-8")
    (candidate / "SKILL.md").write_text(
        original + "\n".join(f"稳定说明 {index}" for index in range(6)) + "\n", encoding="utf-8"
    )
    path = architecture_input(root, target, candidate, full=False)
    value = json.loads(path.read_text(encoding="utf-8"))
    value["baseline_record_id"] = baseline.id
    path.write_text(json.dumps(value), encoding="utf-8")
    unverified = plan_for(root, target, candidate, architecture_review=path)
    assert unverified.preflight["status"] == "blocked"
    verify_improvement(root, baseline.id)
    second = plan_for(root, target, candidate, architecture_review=path)
    assert second.preflight["status"] == "pass"
    local = apply_improvement_plan(root, second)
    verify_improvement(root, local.id)
    (candidate / "SKILL.md").write_text(
        original + "\n".join(f"稳定说明 {index}" for index in range(12)) + "\n", encoding="utf-8"
    )
    third = plan_for(root, target, candidate,
                     architecture_review=architecture_input(root, target, candidate, full=False))
    report = third.preflight["architecture_review"]
    assert report["baseline"]["record_id"] == baseline.id
    assert report["complexity"]["cumulative_delta"]["skill_md_lines"] == 12
    assert third.preflight["status"] == "blocked"


def test_architecture_review_does_not_execute_candidate_script_or_evidence(tmp_path):
    import json

    root, target, candidate = setup_pair(tmp_path)
    script = candidate / "scripts" / "never.py"
    script.parent.mkdir()
    script.write_text('raise AssertionError("candidate must never execute")\n', encoding="utf-8")
    path = architecture_input(root, target, candidate)
    value = json.loads(path.read_text(encoding="utf-8"))
    marker = root / "must-not-exist"
    value["full_review"]["evidence_summary"] = f"reviewed; touch {marker}"
    path.write_text(json.dumps(value), encoding="utf-8")
    plan = plan_for(root, target, candidate, architecture_review=path)
    assert plan.preflight["architecture_review"]["status"] == "pass"
    assert not marker.exists()


def test_split_preview_explains_decision_and_architecture_debt_gate(tmp_path):
    import json

    from skill_engineering.maintenance import format_improvement_plan

    root, target, candidate = setup_pair(tmp_path)
    path = architecture_input(root, target, candidate)
    value = json.loads(path.read_text(encoding="utf-8"))
    value["requirement"]["decision"] = "split"
    path.write_text(json.dumps(value), encoding="utf-8")
    text = format_improvement_plan(plan_for(root, target, candidate, architecture_review=path))
    assert "需求裁决：拆分" in text
    assert "独立计划" in text
    assert "结构债务不阻断本次交付" not in text


def test_legacy_history_limitations_and_known_debt_count_are_visible_in_preview(tmp_path):
    from skill_engineering.maintenance import format_improvement_plan, format_maintenance_record

    root, target, candidate = setup_pair(tmp_path)
    old = historical_unreviewed_record(root, target, candidate)
    verify_improvement(root, old.id)
    (candidate / "SKILL.md").write_text(skill_text("另一处窄触发修改。"), encoding="utf-8")
    plan = plan_for(root, target, candidate,
                    architecture_review=architecture_input(root, target, candidate))
    preview = format_improvement_plan(plan)
    assert "已知开放架构债务：0 项" in preview
    assert "历史记录缺少结构化债务" in preview
    assert "不能推断债务已清零" in preview
    applied = format_maintenance_record(apply_improvement_plan(root, plan))
    assert "已知开放架构债务：0 项" in applied
    assert "历史记录缺少结构化债务" in applied


@pytest.mark.parametrize("mutation", ["missing", "unreviewed", "blocked", "schema", "decision",
                                      "missing_gate", "unsatisfied_gate", "missing_inputs",
                                      "target", "candidate", "effective", "evidence", "thin_pass"])
def test_apply_rejects_invalid_frozen_architecture_even_with_valid_old_hash(tmp_path, mutation):
    from skill_engineering.journey import fingerprint_path
    from skill_engineering.maintenance import _plan_hash

    root, target, candidate = setup_pair(tmp_path)
    before = fingerprint_path(target)
    plan = plan_for(root, target, candidate)
    report = plan.preflight["architecture_review"]
    if mutation == "missing":
        plan.preflight.pop("architecture_review")
    elif mutation in {"unreviewed", "blocked"}:
        report["status"] = mutation
    elif mutation == "schema":
        report["schema_version"] = "unknown"
    elif mutation == "decision":
        report["requirement_decision"] = "split"
    elif mutation == "missing_gate":
        report.pop("whole_review")
    elif mutation == "unsatisfied_gate":
        report["whole_review"]["status"] = "not_required"
    elif mutation == "missing_inputs":
        report.pop("input_fingerprints")
    elif mutation in {"target", "candidate", "effective"}:
        report["input_fingerprints"][mutation] = "d" * 64
    elif mutation == "evidence":
        report["whole_review"]["evidence"]["effective_fingerprint"] = "d" * 64
    else:
        plan.preflight["architecture_review"] = {"status": "pass"}
    # Model an already frozen old artifact, rather than relying on hash drift.
    plan.plan_hash = _plan_hash(plan)
    with pytest.raises(SystemExit, match="架构"):
        apply_improvement_plan(root, plan)
    assert fingerprint_path(target) == before
    assert not (root / ".skill-engineering" / "maintenance-records").exists()
    assert not (root / ".skill-engineering" / "maintenance-backups").exists()

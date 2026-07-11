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
    return create_improvement_plan(
        root,
        target,
        candidate,
        failure_mode="旧 description 会误触发",
        root_cause_layer="trigger",
        expected_behavior="只有明确请求才触发",
        regression_cases=["tests/cases/trigger.yaml"],
        profile="team",
        **kwargs,
    )


def test_missing_maintenance_intent_or_regression_blocks_apply(tmp_path: Path):
    root, target, candidate = setup_pair(tmp_path)
    plan = create_improvement_plan(root, target, candidate)

    assert plan.preflight["status"] == "blocked"
    assert any(item["rule_id"] == "MAINT106" and item["level"] == "FAIL" for item in plan.findings)
    with pytest.raises(SystemExit, match="preflight"):
        apply_improvement_plan(root, plan)


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

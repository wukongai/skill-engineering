from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from skill_engineering.scaffold import (
    apply_build_plan,
    create_build_plan,
    create_improvement_plan,
    format_build_plan,
)
from skill_engineering.skill_doctor import doctor_skill


def make_root(tmp_path: Path) -> Path:
    root = tmp_path / "hub"
    root.mkdir()
    return root


def test_atomic_preview_is_minimal_and_writes_nothing(tmp_path):
    root = make_root(tmp_path)
    target = tmp_path / "demo-skill"

    plan = create_build_plan(
        root,
        target,
        name="demo-skill",
        description="用于重复执行一个清楚的任务。",
        use_when=["用户请求演示任务时。"],
    )

    assert not target.exists()
    assert [item.relative_path for item in plan.files] == ["SKILL.md"]
    assert any(item["path"] == "skill.contract.yaml" for item in plan.omitted)


def test_apply_creates_planned_files_only(tmp_path):
    root = make_root(tmp_path)
    target = tmp_path / "demo-skill"
    plan = create_build_plan(
        root,
        target,
        name="demo-skill",
        description="用于重复执行一个清楚的任务。",
    )

    created = apply_build_plan(root, plan)

    assert created == [target / "SKILL.md"]
    assert (target / "SKILL.md").is_file()
    assert not (target / "skill.contract.yaml").exists()
    assert plan.postflight["status"] == "pass"
    assert plan.postflight["release_readiness"]["ready"] is True
    result = doctor_skill(target, profile="team")
    assert result.fail_count == 0
    assert result.warn_count == 0


def test_apply_rejects_plan_content_drift(tmp_path):
    root = make_root(tmp_path)
    target = tmp_path / "demo-skill"
    plan = create_build_plan(
        root,
        target,
        name="demo-skill",
        description="用于重复执行一个清楚的任务。",
    )
    plan.files[0].content += "\n未预览的变化\n"

    with pytest.raises(SystemExit, match="计划内容已漂移"):
        apply_build_plan(root, plan)
    assert not target.exists()


def test_structural_postflight_failure_cleans_new_target(tmp_path):
    root = make_root(tmp_path)
    target = tmp_path / "broken-skill"
    plan = create_build_plan(
        root,
        target,
        name="broken-skill",
        description="",
    )

    with pytest.raises(SystemExit, match="结构验证失败"):
        apply_build_plan(root, plan)
    assert not target.exists()
    assert plan.postflight["status"] == "failed_rolled_back"


def test_side_effect_plan_has_contract_and_three_cases(tmp_path):
    root = make_root(tmp_path)
    target = tmp_path / "publish-skill"

    plan = create_build_plan(
        root,
        target,
        name="publish-skill",
        description="用于预览并发布内容。",
        kind="adapter",
        side_effect=True,
    )

    paths = {item.relative_path for item in plan.files}
    assert "skill.contract.yaml" in paths
    assert {
        "tests/cases/success.yaml",
        "tests/cases/failure.yaml",
        "tests/cases/high-risk.yaml",
    }.issubset(paths)
    assert "apply_requires_explicit_user_approval" in next(
        item.content for item in plan.files if item.relative_path == "skill.contract.yaml"
    )


def test_production_orchestrator_scaffold_emits_complete_evaluation_contract(tmp_path):
    root = make_root(tmp_path)
    target = tmp_path / "release-review"
    plan = create_build_plan(
        root,
        target,
        name="release-review",
        description="用于明确请求的发布前审查。",
        kind="orchestrator",
        side_effect=True,
        production=True,
    )
    apply_build_plan(root, plan)

    assert plan.postflight["status"] == "pass"
    assert plan.postflight["release_readiness"]["ready"] is False
    assert "EVAL107" in plan.postflight["release_readiness"]["issue_ids"]

    result = doctor_skill(target, profile="production")
    ids = {item.rule_id for item in result.issues}
    assert ids == {"EVAL107"}
    assert "EVAL103" not in ids
    assert "EVAL104" not in ids
    assert (target / "tests" / "cases" / "holdout.yaml").is_file()
    contract = yaml.safe_load((target / "skill.contract.yaml").read_text(encoding="utf-8"))
    assert contract["evaluation"]["behavioral_results"] == {
        "report": "artifacts/evaluation-report.json"
    }


def test_stale_or_existing_target_is_rejected(tmp_path):
    root = make_root(tmp_path)
    target = tmp_path / "demo-skill"
    plan = create_build_plan(
        root,
        target,
        name="demo-skill",
        description="用于演示。",
    )
    target.mkdir()

    with pytest.raises(SystemExit, match="过期|存在"):
        apply_build_plan(root, plan)


def test_name_must_be_hyphen_case(tmp_path):
    with pytest.raises(SystemExit, match="hyphen-case"):
        create_build_plan(
            make_root(tmp_path),
            tmp_path / "bad",
            name="Bad Name",
            description="bad",
        )


def test_improvement_plan_summarizes_impact_and_applies_after_preview(tmp_path: Path):
    root = make_root(tmp_path)
    target = tmp_path / "demo-skill"
    candidate = tmp_path / "candidate"
    target.mkdir()
    candidate.mkdir()
    old = "---\nname: demo-skill\ndescription: 旧描述。\n---\n\n# Demo\n"
    new = "---\nname: demo-skill\ndescription: 新描述。\n---\n\n# Demo\n"
    (target / "SKILL.md").write_text(old, encoding="utf-8")
    (candidate / "SKILL.md").write_text(new, encoding="utf-8")

    plan = create_improvement_plan(
        root,
        target,
        candidate,
        failure_mode="description 触发边界不清",
        root_cause_layer="trigger",
        expected_behavior="新描述只触发明确能力",
        no_regression_reason="仅收窄 metadata,由 lint 和 Doctor 验证。",
    )
    assert plan.operation == "improve"
    assert (target / "SKILL.md").read_text(encoding="utf-8") == old
    summary = format_build_plan(plan)
    assert "改进方案已经准备好" in summary
    assert "目前尚未写入任何文件" in summary
    assert "是否继续应用" in summary
    assert "-description: 旧描述。" not in summary
    assert "+description: 新描述。" not in summary

    apply_build_plan(root, plan)
    assert (target / "SKILL.md").read_text(encoding="utf-8") == new


def test_improvement_plan_rejects_stale_target(tmp_path: Path):
    root = make_root(tmp_path)
    target = tmp_path / "demo-skill"
    candidate = tmp_path / "candidate"
    target.mkdir()
    candidate.mkdir()
    (target / "SKILL.md").write_text("old", encoding="utf-8")
    (candidate / "SKILL.md").write_text("new", encoding="utf-8")
    plan = create_improvement_plan(
        root,
        target,
        candidate,
        failure_mode="更新入口",
        root_cause_layer="trigger",
        expected_behavior="候选入口生效",
        no_regression_reason="测试只验证 stale plan。",
    )
    (target / "SKILL.md").write_text("drift", encoding="utf-8")

    with pytest.raises(SystemExit, match="过期"):
        apply_build_plan(root, plan)

from __future__ import annotations

from pathlib import Path

import pytest

from skill_engineering.scaffold import (
    apply_build_plan,
    create_build_plan,
    create_improvement_plan,
    format_build_plan,
)


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


def test_improvement_plan_shows_diff_and_applies_after_preview(tmp_path: Path):
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
    assert "-description: 旧描述。" in format_build_plan(plan)
    assert "+description: 新描述。" in format_build_plan(plan)

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

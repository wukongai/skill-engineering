"""v1.1 NA-3: 旧 flag-based create fallback 的 scaffold_only 降级语义与 1.0 兼容。"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pytest

from skill_engineering.journey import load_build_plan, local_state_root, payload_hash
from skill_engineering.scaffold import (
    apply_build_plan,
    create_build_plan,
    format_build_plan,
)


def make_root(tmp_path: Path) -> Path:
    root = tmp_path / "hub"
    root.mkdir()
    return root


def test_create_plan_is_marked_scaffold_only(tmp_path):
    root = make_root(tmp_path)
    plan = create_build_plan(
        root,
        tmp_path / "demo-skill",
        name="demo-skill",
        description="用于重复执行一个清楚的任务。",
    )

    assert plan.content_status == "scaffold_only"
    assert plan.hash_version == 2
    preview = format_build_plan(plan)
    assert "scaffold_only" in preview
    assert "完整创建成功" not in preview


def test_applied_scaffold_only_plan_does_not_claim_complete_creation(tmp_path):
    root = make_root(tmp_path)
    plan = create_build_plan(
        root,
        tmp_path / "demo-skill",
        name="demo-skill",
        description="用于重复执行一个清楚的任务。",
    )
    apply_build_plan(root, plan)

    feedback = format_build_plan(plan)

    assert "scaffold_only" in feedback
    assert "完整创建成功" not in feedback
    assert "尚未" in feedback


def test_legacy_plan_without_content_status_keeps_1x_semantics(tmp_path):
    """1.0 计划没有 content_status 字段:读取后不升级为 content_complete,且 hash 兼容可应用。"""
    root = make_root(tmp_path)
    plan = create_build_plan(
        root,
        tmp_path / "demo-skill",
        name="demo-skill",
        description="用于重复执行一个清楚的任务。",
    )

    # 模拟 1.0 落盘格式:移除 1.1 新增字段
    legacy = asdict(plan)
    legacy.pop("content_status", None)
    legacy.pop("hash_version", None)
    legacy["plan_hash"] = payload_hash(
        legacy,
        exclude={"plan_hash", "applied", "record_id", "postflight"},
    )
    path = local_state_root(root) / "build-plans" / f"{plan.id}.json"
    path.write_text(json.dumps(legacy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    loaded = load_build_plan(root, plan.id)
    assert loaded.content_status != "content_complete"

    created = apply_build_plan(root, loaded)
    assert created == [tmp_path / "demo-skill" / "SKILL.md"]
    assert "scaffold_only" in format_build_plan(loaded)


def test_v2_plan_rejects_content_status_tamper(tmp_path):
    root = make_root(tmp_path)
    plan = create_build_plan(
        root,
        tmp_path / "demo-skill",
        name="demo-skill",
        description="用于重复执行一个清楚的任务。",
    )
    plan.content_status = "content_complete"

    with pytest.raises(SystemExit, match="计划内容已漂移"):
        apply_build_plan(root, plan)

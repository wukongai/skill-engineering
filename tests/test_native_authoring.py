"""v1.1 Native Authoring RED 基线。

NA-0 固化 Hermes“只生成骨架并提前报告完成”的失败场景；
以下测试在 NA-1 至 NA-5 完成前必须失败（RED），全部转绿是 1.1 创建主链路的前置条件。
"""

from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "skill-engineering"
SRC = ROOT / "src" / "skill_engineering"


def test_creation_does_not_delegate_to_official_skill_creator():
    """NA-2: 创建主链路必须自包含，不得委托官方 skill-creator。"""
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    contract_text = (SKILL_DIR / "skill.contract.yaml").read_text(encoding="utf-8")

    assert "官方 `skill-creator` 可用时委托" not in skill_text
    assert "skill-creator" not in contract_text
    assert "references/authoring-brief.md" in skill_text


def test_normal_creation_route_never_instructs_legacy_create():
    """普通创建必须走完整 Native plan；legacy create 只保留 scaffold/CI。"""
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    creation_line = next(
        line for line in skill_text.splitlines() if line.startswith("- 创建 Skill:")
    )

    assert "新建使用 `skill-engineering create`" not in creation_line
    assert "scripts/native_plan.py" in creation_line
    assert "legacy" in skill_text


def test_authoring_brief_contract_exists_with_required_fields():
    """NA-1: Authoring Brief 契约随 Skill 交付，包含 Spec 定义的 14 个字段。"""
    brief = SKILL_DIR / "references" / "authoring-brief.md"
    assert brief.is_file(), "references/authoring-brief.md 不存在"
    text = brief.read_text(encoding="utf-8")
    for field in [
        "goal",
        "target_users",
        "positive_triggers",
        "negative_triggers",
        "inputs",
        "outputs",
        "workflow",
        "failure_modes",
        "side_effects",
        "approvals",
        "resources",
        "examples",
        "verification",
        "host_requirements",
    ]:
        assert f"`{field}`" in text, f"authoring-brief.md 缺少字段 {field}"


def test_content_completion_gate_is_portable_and_documented():
    """NA-3: Content Completion Gate 随安装产物交付，并提供 Agent-native 等价清单。"""
    gate = SKILL_DIR / "scripts" / "content_gate.py"
    assert gate.is_file(), "scripts/content_gate.py 不存在"
    source = gate.read_text(encoding="utf-8")
    assert "CG001" in source and "CG009" in source
    assert "__main__" in source

    guide = SKILL_DIR / "references" / "content-completion-gate.md"
    assert guide.is_file(), "references/content-completion-gate.md 不存在"
    assert "Agent-native" in guide.read_text(encoding="utf-8")


def test_legacy_scaffold_fallback_is_marked_scaffold_only():
    """NA-3: 旧 flag-based create fallback 必须标记 scaffold_only。"""
    scaffold_source = (SRC / "scaffold.py").read_text(encoding="utf-8")
    cli_source = (SRC / "cli.py").read_text(encoding="utf-8")
    assert "scaffold_only" in scaffold_source or "scaffold_only" in cli_source


def test_creation_review_score_and_user_visible_statuses():
    """NA-4: 创建终点必须包含评审分数反馈与完整用户可见状态机。"""
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    for status in [
        "needs_discovery",
        "candidate_incomplete",
        "candidate_ready",
        "created_untried",
        "validated",
        "needs_improvement",
    ]:
        assert status in skill_text, f"SKILL.md 缺少用户可见状态 {status}"


def test_host_adapter_references_cover_five_hosts():
    """NA-5: 宿主适配契约覆盖共同能力与 Codex、Claude Code、Hermes、Pi、Kimi CLI。"""
    adapters = SKILL_DIR / "references" / "host-adapters"
    for name in [
        "common-capabilities.md",
        "hermes.md",
        "codex.md",
        "claude-code.md",
        "pi.md",
        "kimi-cli.md",
    ]:
        assert (adapters / name).is_file(), f"references/host-adapters/{name} 不存在"


def test_native_authoring_behavior_cases_cover_spec_list():
    """NA-2: 行为用例覆盖 Spec 测试清单 9 类场景,并注册进 contract。"""
    cases_path = SKILL_DIR / "tests" / "native-authoring-behavior.yaml"
    assert cases_path.is_file(), "tests/native-authoring-behavior.yaml 不存在"
    cases = yaml.safe_load(cases_path.read_text(encoding="utf-8"))["cases"]
    assert {item["id"] for item in cases} == {
        "no-external-creator",
        "novice-goal-only",
        "insufficient-information",
        "single-file-complete-skill",
        "complex-supporting-files",
        "side-effect-approval",
        "host-tool-missing",
        "placeholder-candidate-blocked",
        "time-pressure-no-skip",
    }
    for item in cases:
        assert item["given"] and item["expect"] and item["must_not"], item["id"]

    contract = yaml.safe_load((SKILL_DIR / "skill.contract.yaml").read_text(encoding="utf-8"))
    assert "tests/native-authoring-behavior.yaml" in contract["tests"]["regression_cases"]


def test_native_authoring_regression_cases_registered():
    """行为用例注册进 contract，防止回到“骨架提前完成”。"""
    cases_path = SKILL_DIR / "tests" / "native-authoring-cases.yaml"
    assert cases_path.is_file(), "tests/native-authoring-cases.yaml 不存在"
    cases = yaml.safe_load(cases_path.read_text(encoding="utf-8"))["cases"]
    for case in cases:
        source = (ROOT / case["source"]).read_text(encoding="utf-8")
        for phrase in case["must_include"]:
            assert phrase in source, f"{case['id']} missing: {phrase}"

    contract = yaml.safe_load((SKILL_DIR / "skill.contract.yaml").read_text(encoding="utf-8"))
    assert "tests/native-authoring-cases.yaml" in contract["tests"]["regression_cases"]

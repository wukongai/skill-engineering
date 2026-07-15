from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "skill-guide"


def test_skill_guide_requires_plain_language_user_summary():
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    feedback_text = (SKILL_DIR / "references" / "user-feedback-standard.md").read_text(
        encoding="utf-8"
    )

    assert "结果、对用户的影响、下一步" in skill_text
    assert "references/user-feedback-standard.md" in skill_text
    assert "默认不展示命令、原始 JSON、内部 ID" in feedback_text
    assert "整体尚未完成" in feedback_text
    assert "真实项目没有变化" in feedback_text

    cases = yaml.safe_load(
        (SKILL_DIR / "tests" / "user-feedback-cases.yaml").read_text(encoding="utf-8")
    )["cases"]
    assert {item["id"] for item in cases} == {
        "approval-uses-user-action",
        "artifact-recommendation",
        "partial-cleanup-failure",
        "resume-from-handoff",
        "safe-test-install-removed",
    }


def test_skill_guide_contract_blocks_internal_tool_output_as_default_feedback():
    contract = yaml.safe_load(
        (SKILL_DIR / "skill.contract.yaml").read_text(encoding="utf-8")
    )

    output_names = {item["name"] for item in contract["outputs"]}
    forbidden = set(contract["forbidden"])
    regression_cases = set(contract["tests"]["regression_cases"])

    assert "user_status_summary" in output_names
    assert "raw_tool_output_as_default_user_feedback" in forbidden
    assert "approval_request_using_only_internal_release_terms" in forbidden
    assert "claiming_overall_success_when_any_required_cleanup_record_failed" in forbidden
    assert "tests/user-feedback-cases.yaml" in regression_cases


def test_skill_guide_routes_complex_and_commercial_skill_governance():
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    governance = (SKILL_DIR / "references" / "development-governance.md").read_text(
        encoding="utf-8"
    )
    contract = yaml.safe_load(
        (SKILL_DIR / "skill.contract.yaml").read_text(encoding="utf-8")
    )

    assert "references/development-governance.md" in skill_text
    assert "stages/project-governance/INSTRUCTIONS.md" in skill_text
    assert "简单 Skill 保持轻量" in skill_text
    assert "Backlog" in governance
    assert "Spec" in governance
    assert "ADR" in governance
    assert "Daily Log" in governance
    assert "governance_plan" in {item["name"] for item in contract["outputs"]}
    assert "complex_or_commercial_feature_without_spec_and_plan" in set(
        contract["forbidden"]
    )


def test_skill_guide_discovers_before_creating_or_governing_new_skill():
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    discovery = (SKILL_DIR / "references" / "capability-brainstorming.md").read_text(
        encoding="utf-8"
    )
    contract = yaml.safe_load(
        (SKILL_DIR / "skill.contract.yaml").read_text(encoding="utf-8")
    )

    assert "references/capability-brainstorming.md" in skill_text
    assert "needs_discovery" in skill_text
    assert "一次问一个关键问题" in skill_text
    assert "先自查" in discovery
    assert "比较 2–3 个方案" in discovery
    assert "此时不得先创建 Product" in discovery
    assert "discovery_summary" in {item["name"] for item in contract["outputs"]}
    forbidden = set(contract["forbidden"])
    assert "default_create_skill_with_blocking_unknowns" in forbidden
    assert "product_or_version_scaffold_before_skill_decision_for_new_request" in forbidden


def test_product_positioning_keeps_fast_creation_and_lifecycle_together():
    cases = yaml.safe_load(
        (SKILL_DIR / "tests" / "product-positioning.yaml").read_text(encoding="utf-8")
    )["cases"]
    for case in cases:
        source = (ROOT / case["source"]).read_text(encoding="utf-8")
        for phrase in case["must_include"]:
            assert phrase in source, f"{case['id']} missing: {phrase}"

    contract = yaml.safe_load(
        (SKILL_DIR / "skill.contract.yaml").read_text(encoding="utf-8")
    )
    assert "快速生成从第一版开始就符合工程规范" in contract["purpose"]
    assert "tests/product-positioning.yaml" in contract["tests"]["regression_cases"]

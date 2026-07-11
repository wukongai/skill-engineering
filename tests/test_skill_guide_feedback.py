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

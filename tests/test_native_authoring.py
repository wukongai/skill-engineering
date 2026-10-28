"""v1.1 Native Authoring RED 基线。

NA-0 固化 Hermes“只生成骨架并提前报告完成”的失败场景；
以下测试在 NA-1 至 NA-5 完成前必须失败（RED），全部转绿是 1.1 创建主链路的前置条件。
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest
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
    """Authoring Brief 契约包含需求、边界和行为测试字段。"""
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
        "mission",
        "owned_capabilities",
        "excluded_capabilities",
        "allowed_context",
        "drift_signals",
        "redirect_strategy",
        "stop_conditions",
        "acceptance_cases",
        "behavior_cases",
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


def _architecture_example() -> dict:
    reference = SKILL_DIR / "references" / "architecture-review.md"
    assert reference.is_file(), "架构审查的单一声明规范尚未交付"
    examples = re.findall(r"```json\n(.*?)\n```", reference.read_text(encoding="utf-8"), re.S)
    assert len(examples) == 1, "声明字段只维护一份完整 JSON 示例"
    return json.loads(examples[0])


def test_architecture_review_is_an_internal_reachable_stage():
    stage = SKILL_DIR / "stages" / "architecture-review" / "INSTRUCTIONS.md"
    assert stage.is_file(), "缺少内部架构审查阶段"
    assert not list((SKILL_DIR / "stages").rglob("SKILL.md"))
    root_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "stages/architecture-review/INSTRUCTIONS.md" in root_text
    for name in ["design", "review", "project-governance"]:
        text = (SKILL_DIR / "stages" / name / "INSTRUCTIONS.md").read_text(encoding="utf-8")
        assert "../architecture-review/INSTRUCTIONS.md" in text, name
    for source in [stage, SKILL_DIR / "references" / "architecture-review.md"]:
        text = source.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            assert (source.parent / target.split("#", 1)[0]).is_file(), target


def test_architecture_review_declaration_matches_spec_and_is_registered():
    declaration = _architecture_example()
    assert declaration["schema_version"] == "1"
    assert set(declaration) == {
        "schema_version", "requirement", "budgets", "debt", "resolved_debt_ids", "full_review"
    }
    assert set(declaration["requirement"]) == {
        "summary", "decision", "rationale", "owner", "replacement_plan",
        "protected_behaviors", "touched_boundaries"
    }
    assert set(declaration["budgets"]) == {
        "skill_md_lines", "instruction_files", "duplicate_instruction_lines", "open_debt"
    }
    assert set(declaration["full_review"]) == {
        "target_fingerprint", "candidate_fingerprint", "effective_fingerprint",
        "checked_areas", "conclusion", "reviewer", "evidence_summary"
    }
    assert set(declaration["full_review"]["checked_areas"]) == {
        "ownership", "routing", "interfaces", "state", "failure", "rollback"
    }
    contract = yaml.safe_load((SKILL_DIR / "skill.contract.yaml").read_text(encoding="utf-8"))
    assert "architecture_review" in {item["name"] for item in contract["outputs"]}
    assert "architecture review stage" in {item["name"] for item in contract["delegates"]}
    assert "tests/architecture-review-cases.json" in contract["tests"]["regression_cases"]


def test_maintenance_architecture_review_defaults_to_required_without_affecting_creation():
    contract = yaml.safe_load((SKILL_DIR / "skill.contract.yaml").read_text(encoding="utf-8"))
    entry = next(item for item in contract["inputs"] if item["name"] == "architecture_review_path")
    assert entry["required"] is False  # Creation and read-only intents have no maintenance input.
    assert "维护" in entry["contract"] and "必需" in entry["contract"]
    reference = (SKILL_DIR / "references" / "architecture-review.md").read_text(encoding="utf-8")
    for phrase in ["缺少声明", "阻断", "旧计划", "重新预览", "Active", "不提供跳过"]:
        assert phrase in reference, phrase
    assert "本次维护允许继续" not in reference
    assert "--architecture-review" in (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    evolution = (SKILL_DIR / "references" / "evolution-standard.md").read_text(encoding="utf-8")
    assert "--architecture-review" in evolution


def test_architecture_review_portable_cases_validate_actual_loader(tmp_path):
    cases_path = SKILL_DIR / "tests" / "architecture-review-cases.json"
    assert cases_path.is_file(), "缺少随 Skill 交付的声明校验案例"
    suite = json.loads(cases_path.read_text(encoding="utf-8"))
    cases = suite["cases"]
    assert len({case["id"] for case in cases}) == len(cases)
    assert {case["id"] for case in cases} >= {
        "extend-valid", "refactor-valid", "split-valid-declaration", "defer-valid-declaration",
        "schema-number-rejected", "unknown-field-rejected", "boolean-budget-rejected",
        "negative-budget-rejected", "duplicate-debt-rejected", "unknown-boundary-rejected",
        "invalid-conclusion-rejected", "secret-input-rejected"
    }
    from skill_engineering.architecture_review import load_architecture_declaration

    for case in cases:
        declaration = copy.deepcopy(_architecture_example())
        for change in case.get("changes", []):
            destination = declaration
            for part in change["path"][:-1]:
                destination = destination[part]
            destination[change["path"][-1]] = change["value"]
        if case.get("inject_secret"):
            declaration["requirement"]["summary"] = "api" + "_key" + "=" + "SYNTHETIC_VALUE"
        source = tmp_path / f"{case['id']}.json"
        source.write_text(json.dumps(declaration, ensure_ascii=False), encoding="utf-8")
        if case["valid"]:
            assert load_architecture_declaration(source)["schema_version"] == "1", case["id"]
        else:
            with pytest.raises((ValueError, SystemExit), match=".+"):
                load_architecture_declaration(source)

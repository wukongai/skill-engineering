"""发现元数据与开发案例的确定性合同，不模拟宿主语义选择器。"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "skill-engineering"
ROUTING_PATH = "references/activation-routing.md"
CASES_PATH = "tests/activation-cases.json"


def _skill_metadata() -> dict:
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---", 2)[1])


def _contract() -> dict:
    return yaml.safe_load((SKILL_DIR / "skill.contract.yaml").read_text(encoding="utf-8"))


def _activation_cases() -> dict:
    source = SKILL_DIR / CASES_PATH
    assert source.is_file(), "缺少随 Skill 交付的自然语言激活开发案例"
    return json.loads(source.read_text(encoding="utf-8"))


def test_discovery_prefix_keeps_core_intents_when_catalog_is_truncated():
    """截短发现列表仍可看到三类意图与对象；这不证明宿主会选中它。"""
    metadata = _skill_metadata()
    assert metadata["name"] == "skill-engineering"
    description = metadata["description"]
    prefix = description[:60]
    for term in ["创建", "维护", "检查", "Agent Skill"]:
        assert term in prefix, f"发现描述前 60 字缺少 {term}"
    assert len(description) <= 300, "发现描述应紧凑，避免把入口方法塞进元数据"
    assert "skill-engineering" in description and "Skill Engineering" in description
    assert set(metadata) == {"name", "description"}, "不增加宿主未声明的优先级或别名字段"


def test_host_policy_and_ui_keep_identity_and_same_core_intents():
    metadata = yaml.safe_load((SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    assert metadata["policy"] == {"allow_implicit_invocation": True}
    interface = metadata["interface"]
    assert interface["display_name"] == "Skill Engineering"
    assert "$skill-engineering" in interface["default_prompt"]
    for field in ["short_description", "default_prompt"]:
        for term in ["创建", "维护", "检查", "Skill"]:
            assert term in interface[field], f"UI {field} 未覆盖 {term}"


def test_activation_method_has_one_reachable_reference():
    reference = SKILL_DIR / ROUTING_PATH
    assert reference.is_file(), "缺少自然语言与上下文承接的单一方法参考"
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert skill_text.count(ROUTING_PATH) == 1, "根入口只保留一处薄路由"
    file_map = (SKILL_DIR / "references" / "file-map.md").read_text(encoding="utf-8")
    assert ROUTING_PATH in file_map
    assert CASES_PATH in file_map
    reference_text = reference.read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)]+)\)", reference_text):
        assert (reference.parent / target.split("#", 1)[0]).is_file(), target
    assert "../SKILL.md" in reference_text and "file-map.md" in reference_text


def test_trigger_contract_registers_context_and_preserves_negative_boundaries():
    contract = _contract()
    positive = "\n".join(contract["triggers"]["use_when"])
    for term in ["创建", "维护", "检查", "上下文", "模糊", "skill-engineering"]:
        assert term in positive, f"触发合同未覆盖 {term}"
    negative = "\n".join(contract["triggers"]["do_not_use_when"])
    for term in ["业务", "代码", "文案", "概念", "harness", "tmux", "显式"]:
        assert term in negative, f"反触发合同未覆盖 {term}"
    assert CASES_PATH in contract["tests"]["regression_cases"]
    assert "priority" not in contract["triggers"]


def test_activation_cases_are_portable_development_contracts():
    """仅检查结构、覆盖标签和安全边界，不用关键字给请求分类。"""
    suite = _activation_cases()
    assert suite["schema_version"] == "skill-activation-cases/v1"
    assert suite["split"] == "development"
    assert suite["evidence"] == {
        "static_contract_only": True,
        "host_activation_observed": False,
        "utility_claim": False,
    }
    cases = suite["cases"]
    assert len(cases) >= 10
    assert len({case["id"] for case in cases}) == len(cases)
    coverage = {tag for case in cases for tag in case["coverage"]}
    assert coverage >= {
        "create", "maintain", "check", "reusable_capability", "context_ellipsis",
        "unknown_object", "business_use", "ordinary_code", "ordinary_copy", "concept",
        "learning", "harness", "explicit_other_skill",
    }
    for case in cases:
        assert set(case) == {"id", "user_prompt", "context", "coverage", "expect", "must_not"}
        assert case["user_prompt"] and case["context"] and case["coverage"] and case["must_not"]
        expected = case["expect"]
        assert set(expected) == {
            "selection", "intent", "clarify", "max_questions", "skill_write_authorized"
        }
        assert expected["selection"] in {
            "skill-engineering", "clarify-object", "follow-explicit-skill", "stay-on-task"
        }
        assert expected["intent"] in {"create", "maintain", "check", None}
        assert expected["clarify"] in {"object", "capability", None}
        assert expected["max_questions"] == (1 if expected["clarify"] else 0)
        assert expected["skill_write_authorized"] is False, case["id"]
        assert "skill-engineering" not in case["user_prompt"].lower(), case["id"]


def test_unknown_object_and_explicit_choice_have_separate_contracts():
    cases = _activation_cases()["cases"]
    unknown = [case for case in cases if "unknown_object" in case["coverage"]]
    assert unknown
    for case in unknown:
        assert case["expect"]["selection"] == "clarify-object"
        assert case["expect"]["intent"] is None
        assert case["expect"]["clarify"] == "object"
    explicit = [case for case in cases if "explicit_other_skill" in case["coverage"]]
    assert explicit
    assert all(case["expect"]["selection"] == "follow-explicit-skill" for case in explicit)

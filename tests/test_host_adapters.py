"""v1.1 NA-5: 宿主适配契约与 Case E 跨宿主共同候选 fixture。"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "skill-engineering"
ADAPTERS = SKILL_DIR / "references" / "host-adapters"
FIXTURE = SKILL_DIR / "tests" / "host-adapter-fixtures.yaml"
CANDIDATE_FIXTURE = SKILL_DIR / "tests" / "fixtures" / "meeting-notes"
NATIVE_PLAN = SKILL_DIR / "scripts" / "native_plan.py"

HOST_DOCS = {
    "codex": "codex.md",
    "claude-code": "claude-code.md",
    "hermes": "hermes.md",
    "pi": "pi.md",
    "kimi-cli": "kimi-cli.md",
}


def test_hermes_adapter_uses_skill_manage_without_authoring_skill():
    text = (ADAPTERS / "hermes.md").read_text(encoding="utf-8")
    assert "skill_manage(create)" in text
    assert "skill_manage(write_file)" in text
    assert "pending/diff/approve" in text
    assert "hermes-agent-skill-authoring" in text  # 只能出现在禁止语境
    for line in text.splitlines():
        if "hermes-agent-skill-authoring" in line or "/learn" in line:
            assert "禁止" in line or "不得" in line or "不调用" in line


def test_case_e_fixture_keeps_core_files_identical_across_hosts():
    fixture = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    hosts = fixture["hosts"]
    assert {item["id"] for item in hosts} == set(HOST_DOCS)

    core = fixture["core_files"]
    assert "SKILL.md" in core
    for item in hosts:
        assert item["core_files"] == core, f"{item['id']} 核心文件集发生漂移"
        assert item["write_tool"] and item["skill_dir"] and item["approval"]

    # 每个宿主都有对应 adapter 文档;差异只允许路径、工具调用和可选元数据
    for item in hosts:
        assert (ADAPTERS / HOST_DOCS[item["id"]]).is_file()
        assert set(item["adapted_fields"]) <= {
            "skill_dir",
            "write_tool",
            "approval",
            "optional_metadata",
        }


def test_case_e_compares_real_candidate_fingerprint():
    spec = importlib.util.spec_from_file_location("native_plan_fixture", NATIVE_PLAN)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    expected = module.fingerprint_tree(CANDIDATE_FIXTURE)["fingerprint"]

    fixture = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    assert fixture["candidate_fixture"] == "tests/fixtures/meeting-notes"
    hosts = fixture["hosts"]
    assert all(host["candidate_fingerprint"] == expected for host in hosts)
    by_id = {host["id"]: host for host in hosts}
    assert by_id["hermes"]["write_tool"] != by_id["codex"]["write_tool"]


def test_adapter_docs_registered_in_contract():
    contract = yaml.safe_load((SKILL_DIR / "skill.contract.yaml").read_text(encoding="utf-8"))
    assert "tests/host-adapter-fixtures.yaml" in contract["tests"]["regression_cases"]

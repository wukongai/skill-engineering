from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
SKILL_DIR = SKILLS_ROOT / "skill-engineering"


def test_skill_engineering_is_the_only_top_level_skill_identity():
    active_dirs = sorted(path.name for path in SKILLS_ROOT.iterdir() if path.is_dir())
    assert active_dirs == ["skill-engineering"]

    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    contract = yaml.safe_load((SKILL_DIR / "skill.contract.yaml").read_text(encoding="utf-8"))
    metadata = yaml.safe_load((SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8"))

    assert "name: skill-engineering" in skill_text
    assert contract["name"] == "skill-engineering"
    assert metadata["interface"]["display_name"] == "Skill Engineering"
    assert "$skill-engineering" in metadata["interface"]["default_prompt"]


def test_explicit_skill_engineering_request_has_a_canonical_route():
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    contract = yaml.safe_load((SKILL_DIR / "skill.contract.yaml").read_text(encoding="utf-8"))
    regression = (SKILL_DIR / "references" / "regression" / "canonical-identity.md").read_text(
        encoding="utf-8"
    )

    assert "skill-engineering" in skill_text
    assert any("skill-engineering" in item for item in contract["triggers"]["use_when"])
    assert "从远程安装后测试创建到检查闭环" in skill_text
    assert "Expected route: `skill-engineering`" in regression


def test_legacy_skill_guide_is_not_an_active_source_entry():
    active_files = [
        SKILL_DIR / "SKILL.md",
        SKILL_DIR / "skill.contract.yaml",
        SKILL_DIR / "agents" / "openai.yaml",
    ]
    source_text = "\n".join(path.read_text(encoding="utf-8") for path in active_files)

    assert "skill-guide" not in source_text
    assert not (SKILLS_ROOT / "skill-guide").exists()

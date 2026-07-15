from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_puts_standard_skills_cli_before_source_checkout():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    direct_install = readme.index("npx skills add wukongai/skill-engineering")
    development_install = readme.index(
        "git clone https://github.com/wukongai/skill-engineering.git"
    )

    assert direct_install < development_install
    assert "--skill skill-engineering" in readme
    assert "普通用户不需要克隆仓库" in readme
    assert "源码学习、二次开发" in readme


def test_install_governance_freezes_canonical_cli_command():
    governance = (
        ROOT / "skills" / "skill-engineering" / "references" / "install-governance.md"
    ).read_text(encoding="utf-8")

    assert "npx skills add wukongai/skill-engineering --skill skill-engineering" in governance
    assert "git clone" in governance
    assert "只用于源码学习、二次开发" in governance

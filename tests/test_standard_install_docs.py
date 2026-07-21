from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIMPLE_INSTALL = "npx skills add wukongai/skill-engineering"


def test_readme_puts_standard_skills_cli_before_source_checkout():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    direct_install = readme.index(SIMPLE_INSTALL)
    development_install = readme.index(
        "git clone https://github.com/wukongai/skill-engineering.git"
    )

    assert direct_install < development_install
    assert SIMPLE_INSTALL in readme
    assert "普通用户不需要克隆仓库" in readme
    assert "源码学习、二次开发" in readme


def test_bilingual_readmes_put_agent_skill_install_before_value_story():
    cases = (
        ("README.md", "## 安装", "## 为什么需要 Skill Engineering"),
        ("README.en.md", "## Installation", "## Why Skill Engineering"),
    )

    for filename, install_heading, value_heading in cases:
        readme = (ROOT / filename).read_text(encoding="utf-8")
        direct_install = readme.index(SIMPLE_INSTALL)
        install_section = readme[readme.index(install_heading) : readme.index(value_heading)]

        assert readme.index(install_heading) < direct_install < readme.index(value_heading)
        assert readme.count(SIMPLE_INSTALL) == 1
        assert "--skill" not in install_section
        assert " -g" not in install_section
        assert " -a" not in install_section
        assert " -y" not in install_section


def test_bilingual_readmes_keep_cli_out_of_the_primary_install_path():
    cases = (
        ("README.md", "### 关于 Python 内核与 CLI", "## 四个真实 Use Case"),
        ("README.en.md", "### Python core and CLI", "## Four real use cases"),
    )

    for filename, cli_heading, use_cases_heading in cases:
        readme = (ROOT / filename).read_text(encoding="utf-8")

        assert readme.index(cli_heading) > readme.index(use_cases_heading)
        assert readme.index(cli_heading) > readme.index("npx skills add")


def test_install_governance_freezes_simple_interactive_default():
    governance = (
        ROOT / "skills" / "skill-engineering" / "references" / "install-governance.md"
    ).read_text(encoding="utf-8")

    assert SIMPLE_INSTALL in governance
    assert "兼容的高级形式" in governance
    assert "git clone" in governance
    assert "只用于源码学习、二次开发" in governance

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_apache_license_and_package_metadata_are_aligned():
    license_text = _read("LICENSE")
    pyproject = _read("pyproject.toml")

    assert "Apache License" in license_text
    assert "Version 2.0, January 2004" in license_text
    assert "Copyright [yyyy] [name of copyright owner]" in license_text
    assert "Grant of Patent License" in license_text
    assert "MIT License" not in license_text
    assert "SPDX-License-Identifier: Apache-2.0" in pyproject
    assert 'license = { text = "Apache-2.0" }' in pyproject
    assert 'authors = [{ name = "艾笑" }]' in pyproject


def test_notice_citation_and_brand_boundary_preserve_origin():
    notice = _read("NOTICE")
    citation = _read("CITATION.cff")
    trademarks = _read("TRADEMARKS.md")

    assert "Skill Engineering" in notice
    assert "Copyright 2026 艾笑" in notice
    assert "https://github.com/wukongai/skill-engineering" in notice
    assert "does not modify that License" in notice
    assert "license: Apache-2.0" in citation
    assert 'family-names: "艾笑"' in citation
    assert "repository-code" in citation
    assert "不增加 Apache-2.0 之外的版权许可限制" in trademarks


def test_current_user_surfaces_describe_apache_2_0():
    for relative_path in (
        "README.md",
        "CONTRIBUTING.md",
        "docs/PRODUCT.md",
        "docs/guides/licensing-and-installation.md",
    ):
        assert "Apache-2.0" in _read(relative_path), relative_path

    assert "provider-neutral · Apache-2.0" in _read("README.md")
    assert "ADR 0006" in _read("docs/guides/licensing-and-installation.md")

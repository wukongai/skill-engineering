#!/usr/bin/env python3
"""Fail when public release facts drift across the repository."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _project_version() -> str:
    match = re.search(r'^version = "([^"]+)"$', _text("pyproject.toml"), re.MULTILINE)
    if not match:
        raise SystemExit("pyproject.toml 缺少 [project] version。")
    return match.group(1)


def _runtime_version() -> str:
    match = re.search(r'^__version__ = "([^"]+)"$', _text("src/skill_engineering/__init__.py"), re.MULTILINE)
    if not match:
        raise SystemExit("运行时 __version__ 缺失。")
    return match.group(1)


def main() -> int:
    parser = argparse.ArgumentParser(description="检查 Skill Engineering 发布事实一致性。")
    parser.add_argument("--version", required=True, help="预期产品版本，例如 1.0.0")
    parser.add_argument("--json", action="store_true", help="输出机器可读结果")
    args = parser.parse_args()

    checks: dict[str, bool] = {
        "project_version": _project_version() == args.version,
        "runtime_version": _runtime_version() == args.version,
        "lock_version": (
            f'name = "skill-engineering"\nversion = "{args.version}"' in _text("uv.lock")
        ),
        "readme_version": f"`{args.version}`" in _text("README.md"),
        "changelog_version": f"## {args.version} -" in _text("CHANGELOG.md"),
        "release_log_version": f"## `{args.version}`" in _text("docs/releases/RELEASE-LOG.md"),
        "roadmap_version": f"`{args.version}`" in _text("docs/ROADMAP.md"),
        "canonical_install": (
            "npx skills add wukongai/skill-engineering --skill skill-engineering"
            in _text("README.md")
        ),
        "canonical_skill_source": (ROOT / "skills/skill-engineering/SKILL.md").is_file(),
        "legacy_skill_absent": not (ROOT / "skills/skill-guide").exists(),
        "v1_contract": (ROOT / "docs/references/v1-public-contract.md").is_file(),
        "v1_compatibility": (ROOT / "docs/guides/v1-compatibility.md").is_file(),
        "v1_use_case_evidence": (
            "总体结论：passed" in _text("docs/testing/2026-07-18-v1-use-cases.md")
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "version": args.version,
        "status": "passed" if not failed else "failed",
        "checks": checks,
        "failed": failed,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Skill Engineering {args.version} 发布一致性：{payload['status']}")
        for name, passed in checks.items():
            print(f"- {'PASS' if passed else 'FAIL'} {name}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""对单个 skill 运行 Skill Engineering Doctor。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


MISSING_RUNTIME_EXIT_CODE = 2
MISSING_RUNTIME_MESSAGE = """\
无法运行 Skill Engineering Doctor：尚未安装 Skill Engineering Python CLI。

`npx skills add` 只安装 Agent Skill，不会自动安装 Python CLI。正式 v1.0.0 发布后，请先运行：
  uv tool install "git+https://github.com/wukongai/skill-engineering.git@v1.0.0"

安装完成后再运行：
  skill-engineering doctor <skill-path> --profile <personal|team|production>
"""


def _add_repo_src_to_path() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    src = repo_root / "src"
    if src.is_dir():
        sys.path.insert(0, str(src))


def main() -> int:
    _add_repo_src_to_path()
    try:
        from skill_engineering.skill_doctor import doctor_skill, format_json, format_text
    except ModuleNotFoundError as exc:
        if exc.name != "skill_engineering":
            raise
        print(MISSING_RUNTIME_MESSAGE, file=sys.stderr)
        return MISSING_RUNTIME_EXIT_CODE

    parser = argparse.ArgumentParser(description="对一个 skill 目录运行 doctor 检查。")
    parser.add_argument("target", type=Path)
    parser.add_argument(
        "--profile",
        choices=["personal", "team", "production", "commercial"],
        default="personal",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = doctor_skill(args.target.expanduser(), profile=args.profile)
    print(format_json(result) if args.json else format_text(result))
    return result.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())

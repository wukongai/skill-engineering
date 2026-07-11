#!/usr/bin/env python3
"""把 Doctor v2 JSON 报告渲染成 Markdown。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="把 skill doctor JSON 报告渲染成 Markdown。")
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    print(f"# {data.get('target', 'Skill Doctor 报告')}")
    print()
    print(f"- Profile: `{data.get('profile', '-')}`")
    print(f"- FAIL: `{data.get('failures', 0)}`")
    print(f"- WARN: `{data.get('warnings', 0)}`")
    score = data.get("score")
    assessment = data.get("assessment")
    if score:
        print(
            f"- Score: `{score.get('total', 0)}/100` (`{score.get('grade', '-')}`, `{score.get('status', '-')}`)"
        )
    if assessment:
        print(f"- Score scope: `{assessment.get('score_scope', '-')}`")
        print(f"- Evidence coverage: `{assessment.get('coverage_percent', 0)}%`")
        print(f"- Utility claim: `{assessment.get('utility_claim', 'not-evaluated')}`")
    print()
    if score:
        print("## 评分")
        print()
    if assessment:
        print("## 证据评测")
        print()
        print(f"- Skill type: `{assessment.get('skill_type', '-')}`")
        print(f"- Method: `{assessment.get('method', '-')}`")
        print(f"- Confidence: `{assessment.get('confidence', '-')}`")
        for item in assessment.get("coverage", []):
            print(
                f"- **{item.get('label', item.get('key', '-'))}**: `{item.get('status', '-')}` — {item.get('evidence', '')}"
            )
        limitations = assessment.get("limitations") or []
        if limitations:
            print()
            print("### 结论边界")
            print()
            for limitation in limitations:
                print(f"- {limitation}")
        print()
        for dim in score.get("dimensions", []):
            print(
                f"- **{dim.get('label', dim.get('key', '-'))}**: `{dim.get('score', 0)}/100`, weight `{dim.get('weight', 0)}%`"
            )
            summary = dim.get("summary")
            if summary:
                print(f"  - {summary}")
            for finding in dim.get("findings", []):
                print(f"  - {finding}")
        recommendations = score.get("recommendations") or []
        if recommendations:
            print()
            print("## 优先建议")
            print()
            for recommendation in recommendations:
                print(f"- {recommendation}")
        print()
    for issue in data.get("issues", []):
        print(f"## {issue['level']} {issue['rule_id']}")
        print()
        print(issue["message"])
        if issue.get("path"):
            print()
            print(f"路径: `{issue['path']}`")
        if issue.get("hint"):
            print()
            print(f"建议: {issue['hint']}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

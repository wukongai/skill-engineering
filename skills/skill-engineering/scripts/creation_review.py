#!/usr/bin/env python3
"""Portable creation review for a completed Agent Skill candidate.

This module intentionally uses only the Python standard library and the sibling
``content_gate.py``. It reviews structural readiness and never claims that the
Skill is useful on a real task.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

WEIGHTS = {
    "functional_value": 20,
    "stability": 25,
    "security": 25,
    "engineering": 30,
}
LABELS = {
    "functional_value": "功能价值",
    "stability": "稳定性",
    "security": "安全",
    "engineering": "工程化",
}
GATE_DEDUCTIONS: dict[str, dict[str, int]] = {
    "CG000": {"functional_value": 35, "stability": 25, "engineering": 40},
    "CG001": {"functional_value": 20, "engineering": 20},
    "CG002": {"engineering": 20},
    "CG003": {"functional_value": 25, "engineering": 15},
    "CG004": {"stability": 25, "engineering": 15},
    "CG005": {"stability": 25, "engineering": 15},
    "CG006": {"functional_value": 25, "engineering": 20},
    "CG007": {"stability": 15, "security": 35},
    "CG009": {"stability": 20, "security": 70, "engineering": 10},
    "CG010": {"stability": 30, "engineering": 20},
}
POSITIVE_TRIGGER_RE = re.compile(
    r"当.+(?:时使用|使用)|时使用|适用于|用于|use when|when (?:the )?user", re.IGNORECASE
)
NEGATIVE_TRIGGER_RE = re.compile(
    r"不要|不用于|不适用于|do not use|not for", re.IGNORECASE
)
INPUT_RE = re.compile(r"输入|input", re.IGNORECASE)
OUTPUT_RE = re.compile(r"输出|output", re.IGNORECASE)
STOP_RE = re.compile(r"停止|不要|禁止|stop|forbidden", re.IGNORECASE)
FAILURE_RE = re.compile(
    r"失败|错误|无法|未提供|部分成功|failure|error|cannot|partial", re.IGNORECASE
)
EXAMPLE_RE = re.compile(r"样例|示例|例如|example", re.IGNORECASE)


def _load_content_gate():
    sibling = Path(__file__).resolve().with_name("content_gate.py")
    spec = importlib.util.spec_from_file_location("skill_engineering_content_gate", sibling)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载内容完整性检查器:{sibling}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def _frontmatter_description(text: str) -> str:
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return ""
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator and key.strip() == "description":
            return value.strip().strip("\"'")
    return ""


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def _finding(
    rule: str,
    dimension: str,
    deduction: int,
    message: str,
    remediation: str,
    *,
    path: str = "SKILL.md",
) -> dict[str, object]:
    return {
        "rule": rule,
        "dimension": dimension,
        "deduction": deduction,
        "path": path,
        "message": message,
        "remediation": remediation,
    }


def _portable_findings(target: Path, text: str, description: str) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    boundary_text = f"{description}\n{text}"
    if not POSITIVE_TRIGGER_RE.search(description):
        findings.append(
            _finding(
                "PCR101",
                "functional_value",
                15,
                "description 缺少明确的正向触发条件。",
                "在 description 中写清楚用户在什么任务下应使用该 Skill。",
            )
        )
    if not NEGATIVE_TRIGGER_RE.search(description):
        findings.append(
            _finding(
                "PCR102",
                "functional_value",
                10,
                "description 缺少反触发边界。",
                "补充“不要用于/不适用于”的相邻能力边界。",
            )
        )
    missing_boundaries = [
        label
        for label, pattern in (
            ("输入", INPUT_RE),
            ("输出", OUTPUT_RE),
            ("停止条件", STOP_RE),
        )
        if not pattern.search(boundary_text)
    ]
    if missing_boundaries:
        findings.append(
            _finding(
                "PCR103",
                "functional_value",
                15,
                f"缺少可验证边界:{'、'.join(missing_boundaries)}。",
                "在 SKILL.md 中明确输入、输出和停止/禁止条件。",
            )
        )
    if not FAILURE_RE.search(text):
        findings.append(
            _finding(
                "PCR201",
                "stability",
                15,
                "没有说明信息不足或执行失败时的行为。",
                "说明失败、输入不足和部分成功时如何停止或反馈。",
            )
        )
    scripts_dir = target / "scripts"
    has_scripts = scripts_dir.is_dir() and any(
        item.is_file() for item in scripts_dir.rglob("*")
    )
    if not has_scripts and not EXAMPLE_RE.search(text):
        findings.append(
            _finding(
                "PCR202",
                "engineering",
                10,
                "纯 Agent Skill 缺少行为样例。",
                "在 SKILL.md 中至少加入一个输入与期望行为样例。",
            )
        )
    if len(text.splitlines()) > 120 and not (target / "references").is_dir():
        findings.append(
            _finding(
                "PCR401",
                "engineering",
                8,
                "根 SKILL.md 偏厚且没有 references/ 渐进披露。",
                "把详细规范拆到 references/，根文件只保留路由和关键边界。",
            )
        )
    return findings


def review_candidate(target: Path, profile: str = "personal") -> dict[str, object]:
    """Review a candidate using the portable Doctor v2 creation profile."""

    if profile not in {"personal", "team", "production"}:
        raise ValueError(f"未知 profile:{profile}")
    target = target.expanduser().resolve()
    if not target.is_dir():
        raise FileNotFoundError(f"Skill 目录不存在:{target}")

    gate = _load_content_gate()
    gate_findings = gate.check_candidate(target)
    skill_md = target / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8") if skill_md.is_file() else ""
    description = _frontmatter_description(text)

    findings: list[dict[str, object]] = []
    for item in gate_findings:
        deductions = GATE_DEDUCTIONS.get(item["rule"], {"engineering": 10})
        for dimension, deduction in deductions.items():
            findings.append(
                _finding(
                    item["rule"],
                    dimension,
                    deduction,
                    item["message"],
                    "修复 Content Completion Gate finding 后重新评审。",
                    path=item["path"],
                )
            )
    findings.extend(_portable_findings(target, text, description))

    scores = {key: 100 for key in WEIGHTS}
    for item in findings:
        dimension = str(item["dimension"])
        scores[dimension] = max(0, scores[dimension] - int(item["deduction"]))
    total = round(sum(scores[key] * weight / 100 for key, weight in WEIGHTS.items()))
    grade = _grade(total)
    status = "blocked" if gate_findings else "pass"

    return {
        "status": status,
        "profile": profile,
        "score": total,
        "grade": grade,
        "dimensions": scores,
        "dimension_details": {
            key: {
                "label": LABELS[key],
                "score": scores[key],
                "weight": WEIGHTS[key],
            }
            for key in WEIGHTS
        },
        "findings": findings,
        "assessment": {
            "method": "portable_creation_profile",
            "score_scope": "structural_readiness",
            "coverage": [
                "frontmatter",
                "trigger_boundaries",
                "resource_entries",
                "side_effect_approval",
                "failure_behavior",
                "sensitive_text_scan",
                "declared_self_tests",
            ],
            "not_covered": [
                "advanced_contract_semantics",
                "provider_runtime",
                "behavioral_utility",
                "operating_system_sandboxing",
            ],
            "limitations": (
                "这是 Doctor v2 的 portable creation profile；完整 CLI Doctor "
                "可提供额外工程规则，但不是创建主链路依赖。"
            ),
        },
        "utility_claim": False,
        "real_task_trial": {
            "status": "pending",
            "required_for": "validated",
        },
    }


def _print_text(result: dict[str, object]) -> None:
    print(
        f"Portable creation review: {result['score']}/100 "
        f"({result['grade']}), status={result['status']}"
    )
    print("四维结构就绪度:")
    for details in result["dimension_details"].values():
        print(f"- {details['label']}: {details['score']}/100 ({details['weight']}%)")
    if result["findings"]:
        print("修复项:")
        for item in result["findings"]:
            print(
                f"- [{item['rule']}] {item['path']}: {item['message']} "
                f"建议:{item['remediation']}"
            )
    print("真实任务效果尚未验证；utility_claim=false。")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Portable Skill 创建评审")
    parser.add_argument("target", type=Path)
    parser.add_argument(
        "--profile",
        choices=("personal", "team", "production"),
        default="personal",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        result = review_candidate(args.target, args.profile)
    except (FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
        print(f"用法错误:{exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _print_text(result)
    return 1 if result["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Preview-first fallback scaffolding for Skill Guide.

The official skill-creator can own richer generation. This module provides a
deterministic, cross-agent fallback and never writes unless apply is explicit.
"""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from .journey import BuildFile, BuildPlan, fingerprint_path, new_id, save_build_plan


VALID_KINDS = {"atomic", "orchestrator", "router", "adapter", "composite"}
TYPE_CHECKS = {
    "orchestrator": ["cross_stage_io", "partial_failure", "aggregation"],
    "router": ["positive_routing", "negative_routing", "fallback"],
    "adapter": ["provider_binding", "portability", "error_mapping"],
    "composite": ["tool_index", "orthogonality", "selection_rules", "output_consistency"],
}


def _validate_name(name: str) -> None:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise SystemExit("Skill name 必须使用小写 hyphen-case,例如 my-skill")


def _skill_markdown(
    name: str,
    description: str,
    kind: str,
    use_when: list[str],
    do_not_use_when: list[str],
    inputs: list[str],
    outputs: list[str],
    side_effect: bool,
) -> str:
    frontmatter = yaml.safe_dump(
        {"name": name, "description": description},
        allow_unicode=True,
        sort_keys=False,
    ).strip()
    lines = ["---", frontmatter, "---", "", f"# {name}", "", "## 什么时候使用", ""]
    lines.extend(f"- {item}" for item in (use_when or [description]))
    lines.extend(["", "## 什么时候不要使用", ""])
    lines.extend(
        f"- {item}" for item in (do_not_use_when or ["一次性任务或已有能力已经完整覆盖时。"])
    )
    lines.extend(["", "## 输入", ""])
    lines.extend(f"- `{item}`" for item in (inputs or ["用户明确提供的任务信息"]))
    lines.extend(["", "## 工作流", "", "1. 读取并校验输入。"])
    if kind in {"orchestrator", "router"}:
        lines.extend(
            [
                "2. 根据明确条件选择 delegate 或下一阶段。",
                "3. 处理部分失败,不要把部分结果报告成完整成功。",
                "4. 汇总结果并运行验证。",
            ]
        )
    else:
        lines.extend(["2. 执行这个 Skill 拥有的单一职责。", "3. 验证输出后再返回。"])
    if side_effect:
        lines.extend(
            [
                "",
                "## 写入与外部操作",
                "",
                "- 默认先预览,不产生远端或不可逆副作用。",
                "- 向用户说明将发生什么,获得明确确认后才能执行。",
            ]
        )
    lines.extend(["", "## 输出", ""])
    lines.extend(f"- `{item}`" for item in (outputs or ["完成结果和必要的验证信息"]))
    lines.extend(
        [
            "",
            "## 停止点",
            "",
            "- 缺少会改变结果的必要输入时停止并提问。",
            "- 需要新增全局能力、Plugin 或不可逆操作时停止并确认。",
            "",
        ]
    )
    return "\n".join(lines)


def _contract(
    name: str,
    kind: str,
    inputs: list[str],
    outputs: list[str],
    side_effect: bool,
    production: bool,
) -> str:
    data: dict[str, Any] = {
        "name": name,
        "kind": kind,
        "owner": "self",
        "status": "draft",
        "inputs": [
            {"name": item, "type": "text", "required": True} for item in (inputs or ["request"])
        ],
        "outputs": [
            {"name": item, "type": "text", "required": True} for item in (outputs or ["result"])
        ],
        "stops": [
            {"name": "missing_input", "condition": "缺少会改变结果的必要输入。"},
            {"name": "awaiting_user_approval", "condition": "写入或外部操作尚未获得明确批准。"},
        ],
        "delegates": [],
        "forbidden": ["hardcoded_user_absolute_paths", "hidden_or_unapproved_side_effect"],
        "tests": {
            "regression_cases": [
                "tests/cases/success.yaml",
                "tests/cases/failure.yaml",
                "tests/cases/high-risk.yaml",
            ]
        },
    }
    if side_effect:
        data["approvals"] = [
            {"name": "explicit_user_approval", "required_before": ["write_or_remote_side_effect"]}
        ]
        data["side_effect_boundary"] = {
            "preview_has_no_remote_side_effects": True,
            "apply_requires_explicit_user_approval": True,
        }
    if kind != "atomic":
        data["state"] = {
            "strategy": "显式记录跨阶段状态;没有持久状态时也要明确声明。",
            "files": [],
        }
    if production or side_effect:
        evaluation: dict[str, Any] = {
            "score_scope": "structural_readiness",
            "claims": {"utility": False},
            "case_portfolio": {
                "success": "tests/cases/success.yaml",
                "failure": "tests/cases/failure.yaml",
                "high_risk": "tests/cases/high-risk.yaml",
            },
            "type_checks": TYPE_CHECKS.get(kind, []),
        }
        if production:
            evaluation.update(
                {
                    "baseline": "artifacts/baseline-results.json",
                    "holdout": "tests/cases/holdout.yaml",
                    "negative_transfer": "reject_if_baseline_pass_becomes_candidate_fail",
                    "behavioral_results": {"report": "artifacts/evaluation-report.json"},
                    "independent_review": "required_before_utility_claim",
                }
            )
        data["evaluation"] = evaluation
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)


def _case(kind: str, name: str) -> str:
    payload = {
        "id": f"{name}-{kind}",
        "kind": kind,
        "user_input": "TODO:补充真实用户输入",
        "fixtures": [],
        "expected": {
            "must": ["TODO:补充必须行为"],
            "must_not": ["TODO:补充禁止行为"],
            "final_state": "TODO",
        },
        "rationale": f"覆盖 {kind} 路径,避免只验证顺利场景。",
    }
    return yaml.safe_dump(payload, allow_unicode=True, sort_keys=False)


def create_build_plan(
    root: Path,
    target: Path,
    *,
    name: str,
    description: str,
    kind: str = "atomic",
    use_when: list[str] | None = None,
    do_not_use_when: list[str] | None = None,
    inputs: list[str] | None = None,
    outputs: list[str] | None = None,
    side_effect: bool = False,
    production: bool = False,
    recommended_scope: str = "project",
) -> BuildPlan:
    _validate_name(name)
    if kind not in VALID_KINDS:
        raise SystemExit(f"未知 Skill kind:{kind};可用:{', '.join(sorted(VALID_KINDS))}")
    target = target.expanduser().resolve()
    use_when = use_when or []
    do_not_use_when = do_not_use_when or []
    inputs = inputs or []
    outputs = outputs or []
    files = [
        BuildFile(
            "SKILL.md",
            _skill_markdown(
                name, description, kind, use_when, do_not_use_when, inputs, outputs, side_effect
            ),
            "Agent 发现、触发和执行这个 Skill 的轻量入口。",
        )
    ]
    needs_contract = kind != "atomic" or side_effect or production
    if needs_contract:
        files.append(
            BuildFile(
                "skill.contract.yaml",
                _contract(name, kind, inputs, outputs, side_effect, production),
                "复杂、生产或有副作用流程需要机器可读边界。",
            )
        )
        for case_kind in ("success", "failure", "high-risk"):
            files.append(
                BuildFile(
                    f"tests/cases/{case_kind}.yaml",
                    _case(case_kind, name),
                    f"固定 {case_kind} 行为,让后续修改可回归。",
                )
            )
        if production:
            files.append(
                BuildFile(
                    "tests/cases/holdout.yaml",
                    _case("holdout", name),
                    "保留不参与编写和调试的留出场景,检查过拟合与负迁移。",
                )
            )
    omitted = []
    if not needs_contract:
        omitted.extend(
            [
                {
                    "path": "skill.contract.yaml",
                    "reason": "简单 atomic Skill 暂不需要复杂 contract。",
                },
                {
                    "path": "tests/",
                    "reason": "无副作用的简单入口先保持轻量,出现稳定失败模式后再补。",
                },
            ]
        )
    omitted.extend(
        [
            {"path": "stages/", "reason": "只有根入口明显变厚或跨阶段状态复杂时才拆。"},
            {"path": "assets/", "reason": "当前没有声明可复用静态资产。"},
        ]
    )
    plan = BuildPlan(
        id=new_id("build"),
        target=str(target),
        skill_name=name,
        kind=kind,
        recommended_scope=recommended_scope,
        files=files,
        omitted=omitted,
        warnings=["这是变更计划,尚未写入任何文件。"],
        verification_commands=[
            f"skill-engineering lint {target}",
            f"skill-engineering doctor {target} --profile {'production' if production else 'team'}",
        ],
        target_fingerprint=fingerprint_path(target),
    )
    save_build_plan(root, plan)
    return plan


def create_improvement_plan(root: Path, target: Path, candidate: Path, **kwargs: Any) -> BuildPlan:
    """兼容入口;持续演进逻辑由 maintenance 单一事实源实现。"""
    from .maintenance import create_improvement_plan as create_maintenance_plan

    return create_maintenance_plan(root, target, candidate, **kwargs)


def apply_build_plan(root: Path, plan: BuildPlan) -> list[Path]:
    if plan.operation == "improve":
        from .maintenance import apply_improvement_plan

        record = apply_improvement_plan(root, plan)
        return [Path(record.target) / action["path"] for action in record.actions]
    target = Path(plan.target)
    if fingerprint_path(target) != plan.target_fingerprint:
        raise SystemExit("变更计划已过期:目标路径状态发生变化,请重新生成计划。")
    if target.exists() or target.is_symlink():
        raise SystemExit(f"目标路径已存在,不会覆盖:{target}")

    created_files: list[Path] = []
    created_dirs: list[Path] = []
    try:
        target.mkdir(parents=True, exist_ok=False)
        created_dirs.append(target)
        for item in plan.files:
            relative = PurePosixPath(item.relative_path)
            if relative.is_absolute() or ".." in relative.parts:
                raise SystemExit(f"BuildPlan 含不安全路径:{item.relative_path}")
            destination = target.joinpath(*relative.parts)
            missing_parents: list[Path] = []
            parent = destination.parent
            while parent != target and not parent.exists():
                missing_parents.append(parent)
                parent = parent.parent
            destination.parent.mkdir(parents=True, exist_ok=True)
            created_dirs.extend(reversed(missing_parents))
            destination.write_text(item.content, encoding="utf-8")
            created_files.append(destination)
    except BaseException:
        for path in reversed(created_files):
            if path.is_file():
                path.unlink()
        for path in sorted(set(created_dirs), key=lambda item: len(item.parts), reverse=True):
            if path.is_dir() and not any(path.iterdir()):
                path.rmdir()
        raise
    plan.applied = True
    save_build_plan(root, plan)
    return created_files


def format_build_plan(plan: BuildPlan) -> str:
    if plan.operation == "improve":
        from .maintenance import format_improvement_plan

        return format_improvement_plan(plan)
    from .interaction import UserFeedback

    return UserFeedback(
        status="awaiting-approval",
        result=f"{plan.skill_name} 的创建方案已经准备好。",
        impact=[
            f"将在 {plan.target} 创建 {len(plan.files)} 个文件。",
            f"能力类型：{plan.kind}。",
            "目前尚未写入任何文件。",
        ],
        next_action="确认创建位置和文件范围后再写入。",
        decision="是否继续创建这个 Skill？",
        technical_details=[f"plan={plan.id}"],
    ).render()

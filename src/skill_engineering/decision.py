"""Deterministic capability selection for Skill Engineering.

The engine decides the engineering artifact shape. It does not estimate market
size, monetization, or domain-specific commercial value.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .interaction import UserFeedback
from .journey import DecisionReport, new_id


CRITICAL_QUESTIONS = {
    "repeatability": "请举一个最近的真实例子：这是一次性任务，还是以后会重复发生？",
    "agent_facing": "最难的部分需要 AI 判断/解释/编排，还是普通脚本就能稳定完成？",
    "trigger_separable": "请各给一个应该触发和不应该触发的相似请求。",
    "deterministic_core": "核心工作是否可以完全由普通脚本稳定完成?",
    "runtime_required": "是否必须依赖 MCP、浏览器、鉴权或专用 App runtime?",
    "reuse_scope": "它只服务一个项目、一个项目集,还是多数项目?",
}


def _frontmatter_description(skill_dir: Path) -> str:
    path = skill_dir / "SKILL.md"
    if not path.is_file():
        return ""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---", 4)
    if end < 0:
        return ""
    try:
        data = yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError:
        return ""
    return str(data.get("description") or "") if isinstance(data, dict) else ""


def _terms(text: str) -> set[str]:
    lower = text.lower()
    terms = set(re.findall(r"[a-z][a-z0-9_-]{2,}", lower))
    for run in re.findall(r"[\u4e00-\u9fff]{2,}", lower):
        if len(run) <= 4:
            terms.add(run)
        terms.update(run[index : index + 2] for index in range(len(run) - 1))
    stop = {"skill", "agent", "使用", "用户", "用于", "这个", "一个", "进行", "需要"}
    return {term for term in terms if term not in stop}


def find_overlap_candidates(root: Path, brief: str) -> list[dict[str, Any]]:
    query_terms = _terms(brief)
    if not query_terms:
        return []
    candidates: list[dict[str, Any]] = []
    for skill_dir in _local_skill_dirs(root):
        key = skill_dir.name
        description = _frontmatter_description(skill_dir)
        candidate_text = f"{key} {description}"
        candidate_terms = _terms(candidate_text)
        union = query_terms | candidate_terms
        similarity = len(query_terms & candidate_terms) / len(union) if union else 0.0
        direct = key.lower() in brief.lower()
        if direct or similarity >= 0.18:
            candidates.append(
                {
                    "key": key,
                    "display_name": key,
                    "source": str(skill_dir),
                    "description": description,
                    "similarity": round(similarity, 3),
                    "evidence_source": "local_skill_inventory",
                }
            )
    return sorted(candidates, key=lambda item: (-item["similarity"], item["key"]))[:5]


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "是", "需要"}


def _answer(answers: dict[str, Any], key: str, default: Any = None) -> Any:
    value = answers.get(key, default)
    return value.strip().lower() if isinstance(value, str) else value


def _usage_evidence(root: Path) -> str:
    return f"本机可见 Skill inventory 当前发现 {len(_local_skill_dirs(root))} 个入口。"


def _local_skill_dirs(root: Path) -> list[Path]:
    locations = [
        root / "skills",
        root / ".agents" / "skills",
        root / ".claude" / "skills",
        root / ".codex" / "skills",
        Path.home() / ".agents" / "skills",
        Path.home() / ".claude" / "skills",
        Path.home() / ".codex" / "skills",
    ]
    found: dict[str, Path] = {}
    for location in locations:
        if not location.is_dir():
            continue
        for item in location.iterdir():
            try:
                resolved = item.resolve()
            except OSError:
                continue
            if (resolved / "SKILL.md").is_file():
                found[str(resolved)] = resolved
    return sorted(found.values(), key=lambda item: str(item))


def decide_capability(
    root: Path,
    brief: str,
    answers: dict[str, Any] | None = None,
    project: Path | None = None,
) -> DecisionReport:
    answers = answers or {}
    overlaps = find_overlap_candidates(root, brief)
    unknown_keys = [key for key in CRITICAL_QUESTIONS if key not in answers]
    unknowns = [CRITICAL_QUESTIONS[key] for key in unknown_keys[:3]]
    overlap_unknown = bool(overlaps) and "distinct_from_existing" not in answers
    if overlap_unknown:
        unknowns.insert(0, "发现了相似 Skill：它们为什么不能直接复用或扩展？")
        unknowns = unknowns[:3]

    repeatability = _answer(answers, "repeatability")
    agent_facing = _truthy(_answer(answers, "agent_facing", False))
    trigger_separable = _truthy(_answer(answers, "trigger_separable", False))
    deterministic_core = _truthy(_answer(answers, "deterministic_core", False))
    runtime_required = _truthy(_answer(answers, "runtime_required", False))
    reuse_scope = _answer(answers, "reuse_scope", "one_project")
    existing_action = _answer(answers, "existing_action", "")
    project_specific = _truthy(_answer(answers, "project_specific", False))
    distinct_from_existing = _truthy(_answer(answers, "distinct_from_existing", False))
    failure_risk = _answer(answers, "failure_risk", "low")

    verdict = "create_skill"
    kind: str | None = str(_answer(answers, "kind", "atomic"))
    reasons: list[str] = []
    alternatives: list[dict[str, str]] = []

    if existing_action == "replace":
        verdict = "archive_or_replace"
        kind = None
        reasons.append("已有入口将被新入口替代,应先治理重复暴露和迁移路径。")
    elif existing_action == "profile":
        verdict = "add_profile_entry"
        kind = None
        reasons.append("能力已经稳定存在,当前问题只是让它在正确项目中可见。")
    elif existing_action == "extend":
        verdict = "extend_existing_skill"
        kind = None
        reasons.append("已有 Skill 已拥有相近触发边界,扩展比新增顶层入口更可维护。")
    elif repeatability in {"one_off", "once", "一次性"}:
        verdict = "no_new_artifact"
        kind = None
        reasons.append("当前是一次性任务,新增长期 Skill 的维护成本高于复用价值。")
    elif runtime_required:
        verdict = "install_plugin_runtime"
        kind = "adapter" if agent_facing else None
        reasons.append("能力必须依赖 MCP、鉴权、浏览器或专用 runtime,不能伪装成纯目录 Skill。")
    elif (
        any(key not in answers for key in ("repeatability", "agent_facing", "trigger_separable"))
        or overlap_unknown
    ):
        verdict = "needs_discovery"
        kind = None
        reasons.append("真实任务、复用频率或触发边界还不清楚,现在创建 Skill 容易制造错误抽象。")
        reasons.append("先完成现有能力自查和一轮逐步澄清,再比较不新增、扩展已有和创建新产物。")
        alternatives.extend(
            [
                {"option": "no_new_artifact", "rejected_because": "等待确认是否只是一次性任务。"},
                {
                    "option": "extend_existing_skill",
                    "rejected_because": "等待确认现有能力是否足够接近。",
                },
                {"option": "create_skill", "rejected_because": "等待确认触发边界和复用价值。"},
            ]
        )
    elif deterministic_core and not agent_facing:
        verdict = "create_script"
        kind = None
        reasons.append("核心行为可以由确定性代码完整表达,Script 比 Agent Skill 更稳定。")
    elif not agent_facing and project_specific:
        verdict = "create_project_doc"
        kind = None
        reasons.append("能力只约束当前项目且不需要 Agent 编排,更适合项目规则或文档。")
    elif overlaps and not distinct_from_existing:
        verdict = "extend_existing_skill"
        kind = None
        reasons.append("本机可见 inventory 中存在可能重叠的 Skill,应先确认复用或扩展。")
    elif not trigger_separable and "trigger_separable" in answers:
        verdict = "create_project_doc"
        kind = None
        reasons.append("触发与反触发边界无法分离,新增顶层 Skill 容易造成误触发。")
    else:
        verdict = "create_skill"
        reasons.append("流程可重复、面向 Agent,且适合封装为可复用工程入口。")
        if deterministic_core:
            reasons.append("确定性部分应下沉到 scripts/,Skill 只负责判断和编排。")

    if verdict == "create_skill":
        alternatives.extend(
            [
                {
                    "option": "create_script",
                    "rejected_because": "核心仍包含 Agent 判断、解释或编排。",
                },
                {
                    "option": "create_project_doc",
                    "rejected_because": "能力具有跨任务复用价值,不只是单项目规则。",
                },
            ]
        )
    elif verdict == "create_script":
        alternatives.append(
            {
                "option": "create_skill",
                "rejected_because": "纯确定性逻辑不需要新增 Agent 触发入口。",
            }
        )
    elif verdict == "install_plugin_runtime":
        alternatives.append(
            {
                "option": "create_skill",
                "rejected_because": "目录型 Skill 不能替代 runtime、工具或鉴权能力。",
            }
        )

    if reuse_scope in {"most_projects", "global"} and failure_risk == "low" and trigger_separable:
        scope = "global"
    elif reuse_scope in {"project_set", "profile"}:
        scope = "profile"
    else:
        scope = "project"
    if verdict in {"needs_discovery", "no_new_artifact", "archive_or_replace"}:
        scope = None

    answered = len(CRITICAL_QUESTIONS) - len(unknown_keys)
    confidence = "high" if not unknowns else "medium" if answered >= 3 else "low"
    evidence = [_usage_evidence(root)]
    if project:
        evidence.append(f"当前项目:{project.expanduser().resolve()}")
    if overlaps:
        evidence.append(f"发现 {len(overlaps)} 个可能重叠的已登记 Skill。")

    next_action_map = {
        "needs_discovery": ("继续需求探索", "skill-engineering decide"),
        "create_skill": ("生成创建计划", "skill-engineering create"),
        "extend_existing_skill": ("审计并生成改进计划", "skill-engineering audit"),
        "create_script": ("创建普通脚本方案", "project implementation"),
        "create_project_doc": ("创建项目规则或文档", "project documentation"),
        "install_plugin_runtime": ("审计 runtime inventory", "plugin review"),
        "add_profile_entry": ("交给 Agent Skill Hub 调整可见范围", "agent-skill-hub profile"),
        "archive_or_replace": ("生成迁移与归档计划", "skill-engineering audit"),
        "no_new_artifact": ("直接完成当前任务", "no artifact"),
    }
    action_label, action_command = next_action_map[verdict]

    return DecisionReport(
        id=new_id("decision"),
        brief=brief,
        verdict=verdict,
        confidence=confidence,
        recommended_kind=kind,
        recommended_scope=scope,
        reasons=reasons,
        evidence=evidence,
        alternatives=alternatives,
        unknowns=unknowns,
        next_actions=[{"label": action_label, "command": action_command}],
        overlap_candidates=overlaps,
    )


def format_decision(report: DecisionReport) -> str:
    labels = {
        "needs_discovery": "继续需求探索,暂不创建 Skill",
        "create_skill": "创建 Skill",
        "extend_existing_skill": "扩展已有 Skill",
        "create_script": "创建 Script",
        "create_project_doc": "创建项目规则/文档",
        "install_plugin_runtime": "使用 Plugin/runtime",
        "add_profile_entry": "增加 Profile 可见性",
        "archive_or_replace": "归档或替换旧入口",
        "no_new_artifact": "不新增产物",
    }
    confidence_labels = {"high": "高", "medium": "中", "low": "低"}
    scope_labels = {
        "project": "当前项目",
        "profile": "指定项目组",
        "global": "全局",
        "one_project": "当前项目",
        "project_set": "指定项目组",
        "most_projects": "多数项目",
    }
    impact = list(report.reasons)
    impact.append(f"判断把握：{confidence_labels.get(report.confidence, report.confidence)}。")
    if report.recommended_scope:
        impact.append(
            f"建议使用范围：{scope_labels.get(report.recommended_scope, report.recommended_scope)}。"
        )
    if report.verdict == "needs_discovery":
        impact.append("当前保留三个方向：不新增产物、扩展已有能力、创建新的工程化产物。")
    elif report.alternatives:
        impact.append("其他产物形态暂不推荐，因为它们不能同时满足当前触发、复用和运行要求。")
    next_action = report.next_actions[0]["label"] if report.next_actions else "继续补齐必要信息。"
    decision = ""
    if report.unknowns:
        decision = f"还需要你确认一个问题：\n- {report.unknowns[0]}"
    return UserFeedback(
        status="awaiting-approval" if report.unknowns else "completed",
        result=f"建议：{labels.get(report.verdict, report.verdict)}。",
        impact=impact,
        next_action=next_action,
        decision=decision,
        technical_details=[f"decision={report.id}", f"verdict={report.verdict}"],
    ).render()

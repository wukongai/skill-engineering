"""Plain-language interaction summaries for Skill Engineering.

Machine records remain complete and versioned. This module renders the default
human surface without exposing record ids, fingerprints, or state enums.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


FeedbackStatus = Literal[
    "completed",
    "incomplete",
    "blocked",
    "awaiting-approval",
    "in-progress",
]


@dataclass(frozen=True)
class UserFeedback:
    status: FeedbackStatus
    result: str
    impact: list[str] = field(default_factory=list)
    next_action: str = ""
    decision: str = ""
    technical_details: list[str] = field(default_factory=list)

    def render(self, *, include_technical: bool = False) -> str:
        lines = [self.result.strip()]
        if self.impact:
            lines.extend(["", "影响："])
            lines.extend(f"- {item.strip()}" for item in self.impact if item.strip())
        if self.next_action.strip():
            lines.extend(["", f"下一步：{self.next_action.strip()}"])
        if self.decision.strip():
            lines.extend(["", self.decision.strip()])
        if include_technical and self.technical_details:
            lines.extend(["", "技术详情："])
            lines.extend(f"- {item.strip()}" for item in self.technical_details if item.strip())
        return "\n".join(lines)


def format_journey_feedback(session: Any) -> str:
    completed = [str(item).strip() for item in session.completed_steps if str(item).strip()]
    impact = []
    if completed:
        impact.append(f"已完成：{'；'.join(completed[-3:])}")
    impact.append("任务进度已经保存，可以从当前结果继续。")
    next_action = str(session.next_action or "继续确认目标和必要输入。")
    return UserFeedback(
        status="completed" if session.status == "completed" else "in-progress",
        result=f"已接续任务：{session.goal}",
        impact=impact,
        next_action=next_action,
        technical_details=[f"stage={session.stage}", f"status={session.status}"],
    ).render()


def format_release_plan_feedback(plan: Any) -> str:
    if plan.channel == "canary":
        result = "测试版本已经准备好，尚未接入任何项目。"
        impact = [
            f"下一步只会接入隔离项目：{plan.project}",
            "不会全局安装，也不会修改其他真实项目。",
            "接入后会自动验证，并且可以完整移除。",
        ]
        decision = "是否继续把测试版本临时接入这个隔离项目？"
    elif plan.channel == "active":
        result = "正式更新方案已经准备好，当前 Skill 尚未修改。"
        impact = [
            f"下一步会更新：{plan.active_source}",
            "执行前会再次检查目标是否变化。",
            "更新后会自动验证，并保留安全恢复能力。",
        ]
        decision = "是否继续执行这次正式更新？"
    else:
        result = "候选版本已经保存用于观察，当前使用中的 Skill 没有变化。"
        impact = ["还没有接入测试项目或正式环境。"]
        decision = ""
    return UserFeedback(
        status="awaiting-approval" if decision else "completed",
        result=result,
        impact=impact,
        next_action="确认实际影响后再决定是否继续。" if decision else "观察候选表现。",
        decision=decision,
        technical_details=[f"plan={plan.id}", f"channel={plan.channel}"],
    ).render()


def format_release_record_feedback(record: Any) -> str:
    verification = record.verification or {}
    if record.status == "rolled-back":
        return UserFeedback(
            status="completed",
            result="测试版本已经移除，发布前的状态已恢复。",
            impact=["本次创建的测试入口已经撤销。", "真实项目没有继续使用测试版本。"],
            next_action="如需继续改进，请基于这次验证结果生成新候选。",
            technical_details=[f"record={record.id}"],
        ).render()
    if verification.get("status") == "passed":
        target = "隔离测试项目" if record.channel == "canary" else "当前维护的 Skill"
        return UserFeedback(
            status="completed",
            result="版本已经接入并验证通过。",
            impact=[f"生效范围仅限：{target}。", "验证结果正常，仍可按操作记录撤销。"],
            next_action="继续观察真实使用效果，或在不需要时撤销本次接入。",
            technical_details=[f"record={record.id}", f"status={record.status}"],
        ).render()
    return UserFeedback(
        status="incomplete",
        result="版本接入后没有通过验证，整体尚未完成。",
        impact=["不要把当前状态当作可交付结果。", "请先确认是否已经自动恢复。"],
        next_action="检查失败原因并恢复到接入前状态。",
        technical_details=[f"record={record.id}", f"status={record.status}"],
    ).render()


def format_evolution_feedback(value: Any) -> str:
    name = type(value).__name__
    status = str(getattr(value, "status", ""))
    if name == "EvolutionProposal":
        result = "已经根据真实运行证据形成改进建议。"
        next_action = "构建相互隔离的开发集和留出集。"
    elif name == "EvolutionDataset":
        result = "真实案例已经整理成隔离评测集。"
        next_action = "为不同修复策略准备独立候选。"
    elif name == "CandidateJob":
        if status in {"validated", "recommended"}:
            result = "候选已经通过当前结构和行为门禁。"
            next_action = "比较合格候选并选择复杂度更低、风险更小的方案。"
        elif status == "rejected":
            result = "这个候选没有通过验收，不能继续发布。"
            next_action = "查看失败案例，修复后生成新的隔离候选。"
        else:
            result = "候选工作区已经准备好。"
            next_action = "只在隔离工作区生成候选并提交真实运行结果。"
    elif name == "SkillVersion":
        result = "合格候选已经保存为观察版本，当前使用中的 Skill 没有变化。"
        next_action = "先观察真实表现；需要接入测试项目时再生成范围明确的方案。"
    else:
        result = "本阶段处理已经完成。"
        next_action = "继续下一阶段的验证。"
    return UserFeedback(
        status="incomplete" if status == "rejected" else "completed",
        result=result,
        impact=["完整证据和机器记录仍已保留，需要时可以查看技术详情。"],
        next_action=next_action,
        technical_details=[f"type={name}", f"id={getattr(value, 'id', '')}", f"status={status}"],
    ).render()


def format_evolution_collection(values: list[Any], *, action: str) -> str:
    if action == "prepared":
        result = f"已经准备好 {len(values)} 个相互隔离的候选方向。"
        next_action = "分别生成候选，再提交真实运行结果。"
    else:
        recommended = sum(getattr(item, "status", "") == "recommended" for item in values)
        result = f"候选比较已经完成，找到 {recommended} 个推荐方案。"
        next_action = "将推荐方案保存为观察版本。" if recommended else "补充证据或生成新候选。"
    return UserFeedback(
        status="completed",
        result=result,
        impact=["默认摘要不展示候选编号和评分明细。"],
        next_action=next_action,
    ).render()

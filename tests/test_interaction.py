from __future__ import annotations

from dataclasses import dataclass, field

from skill_engineering.interaction import (
    UserFeedback,
    format_journey_feedback,
    format_release_plan_feedback,
    format_release_record_feedback,
)


def test_user_feedback_hides_technical_details_by_default():
    feedback = UserFeedback(
        status="completed",
        result="测试完成。",
        impact=["真实项目没有变化。"],
        next_action="继续观察。",
        technical_details=["record=release-123", "fingerprint=abc"],
    )

    plain = feedback.render()
    technical = feedback.render(include_technical=True)

    assert "测试完成" in plain
    assert "真实项目没有变化" in plain
    assert "release-123" not in plain
    assert "fingerprint" not in plain
    assert "release-123" in technical


@dataclass
class Journey:
    goal: str = "创建一个可复用的检查能力"
    completed_steps: list[str] = field(default_factory=lambda: ["已判断正确产物"])
    next_action: str = "确认是否创建测试版本。"
    stage: str = "design"
    status: str = "awaiting_review"


def test_journey_summary_uses_goal_and_next_action_not_state_enums():
    text = format_journey_feedback(Journey())

    assert "创建一个可复用的检查能力" in text
    assert "已判断正确产物" in text
    assert "确认是否创建测试版本" in text
    assert "design" not in text
    assert "awaiting_review" not in text


@dataclass
class ReleasePlan:
    id: str = "release-plan-secret"
    channel: str = "canary"
    project: str = "/tmp/isolated-project"
    active_source: str | None = None


def test_release_plan_explains_real_action_without_internal_terms():
    text = format_release_plan_feedback(ReleasePlan())

    assert "临时接入" in text
    assert "不会全局安装" in text
    assert "可以完整移除" in text
    assert "是否继续" in text
    assert "release-plan-secret" not in text
    assert "canary" not in text.lower()


@dataclass
class ReleaseRecord:
    id: str = "release-secret"
    channel: str = "canary"
    status: str = "rolled-back"
    verification: dict = field(default_factory=lambda: {"status": "rolled-back"})


def test_rollback_summary_says_what_changed_without_record_id():
    text = format_release_record_feedback(ReleaseRecord())

    assert "已经移除" in text
    assert "状态已恢复" in text
    assert "release-secret" not in text

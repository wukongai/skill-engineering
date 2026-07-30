"""v1.1 NA-1: Authoring Brief 契约、就绪判定与脱敏。"""

from __future__ import annotations

from skill_engineering.authoring import (
    brief_ready_for_candidate,
    missing_required_fields,
    sanitize_brief,
)
from skill_engineering.journey import (
    AuthoringBrief,
    list_authoring_briefs,
    load_authoring_brief,
    new_id,
    save_authoring_brief,
)


def _complete_brief() -> AuthoringBrief:
    return AuthoringBrief(
        id=new_id("brief"),
        goal="把会议记录整理成决策、负责人和截止时间",
        target_users="项目经理",
        positive_triggers=["整理会议纪要"],
        negative_triggers=["实时转写录音"],
        inputs=["会议记录文本"],
        outputs=["决策、负责人、截止时间列表"],
        workflow=["提取决策", "标注负责人", "整理截止时间"],
        failure_modes=["信息不足时列出缺口"],
        side_effects=[],
        approvals=[],
        resources=[],
        examples=["示例输入 -> 示例输出"],
        verification=["结构检查", "真实会议记录试运行"],
        host_requirements=["读写文件"],
    )


def test_authoring_brief_round_trip(tmp_path):
    brief = _complete_brief()
    save_authoring_brief(tmp_path, brief)

    loaded = load_authoring_brief(tmp_path, brief.id)
    assert loaded.goal == brief.goal
    assert loaded.verification == brief.verification
    assert loaded.updated_at >= brief.created_at
    assert [item.id for item in list_authoring_briefs(tmp_path)] == [brief.id]


def test_brief_missing_required_fields_blocks_candidate_generation():
    brief = _complete_brief()
    brief.goal = ""
    brief.positive_triggers = []
    brief.negative_triggers = []
    brief.verification = []

    missing = missing_required_fields(brief)
    assert "goal" in missing
    assert "positive_triggers" in missing
    assert "negative_triggers" in missing
    assert "verification" in missing
    assert not brief_ready_for_candidate(brief)


def test_complete_brief_is_ready_for_candidate_generation():
    brief = _complete_brief()
    assert missing_required_fields(brief) == []
    assert brief_ready_for_candidate(brief)


def test_sanitize_brief_redacts_credentials_without_mutating_original():
    fake_key = "sk-live-" + "abcdef1234567890"  # 拼接构造,避免仓库出现真实形态密钥
    brief = _complete_brief()
    brief.goal = f"使用 api_key={fake_key} 同步草稿"
    brief.resources = ["-----BEGIN PRIVATE KEY-----\nabc\n-----END PRIVATE KEY-----"]
    brief.examples = ["cookie: session=abcdef123456"]

    sanitized = sanitize_brief(brief)

    assert fake_key not in sanitized.goal
    assert "[redacted]" in sanitized.goal
    assert "PRIVATE KEY" not in sanitized.resources[0]
    assert "session=abcdef123456" not in sanitized.examples[0]

    # 原对象不被修改
    assert fake_key in brief.goal


def test_save_authoring_brief_redacts_disk_without_mutating_input(tmp_path):
    brief = _complete_brief()
    brief.goal = "同步 api_key=DEMO_SECRET_VALUE"

    path = save_authoring_brief(tmp_path, brief)
    payload = path.read_text(encoding="utf-8")

    assert "DEMO_SECRET_VALUE" not in payload
    assert "[redacted]" in payload
    assert "DEMO_SECRET_VALUE" in brief.goal

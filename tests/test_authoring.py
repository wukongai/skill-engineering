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
        mission="把会议记录整理成可执行的行动项",
        owned_capabilities=["提取决定", "识别负责人"],
        excluded_capabilities=["音频转写", "发送任务通知"],
        allowed_context=["用户提供的会议记录"],
        drift_signals=["开始讨论会议以外的业务决策"],
        redirect_strategy=["说明偏离并拉回会议行动项"],
        stop_conditions=["输入不是会议记录时停止"],
        acceptance_cases=["有负责人和截止时间的行动项被正确提取"],
        behavior_cases=["成功", "反例", "偏题", "信息不足", "工具失败"],
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


def test_boundary_and_behavior_contract_are_required_before_candidate_generation():
    brief = _complete_brief()
    brief.mission = ""
    brief.drift_signals = []
    brief.behavior_cases = []

    missing = missing_required_fields(brief)

    assert {"mission", "drift_signals", "behavior_cases"} <= set(missing)
    assert not brief_ready_for_candidate(brief)


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


def _confirmation(brief):
    from dataclasses import asdict
    from skill_engineering.boundary_policy import boundary_fingerprint
    return {
        "schema_version": "1", "subject_id": brief.id,
        "boundary_fingerprint": boundary_fingerprint(asdict(brief)),
        "status": "confirmed", "source": "explicit_cli_argument",
        "summary": "测试操作员确认合成范围，不代表实际用户确认记录。",
        "excluded_decision": "listed" if brief.excluded_capabilities else "none",
        "behavior_policy": {
            "interaction": "single_turn", "uses_tools": False, "has_side_effects": False,
            "rationale": "一次处理已提供文本，无外部工具或动作。",
        },
    }


def test_current_readiness_requires_confirmation_without_rewriting_legacy():
    brief = _complete_brief()
    assert brief_ready_for_candidate(brief)
    assert not brief_ready_for_candidate(brief, require_confirmation=True)
    assert "boundary_confirmation" in missing_required_fields(brief, require_confirmation=True)


def test_confirmed_empty_exclusion_readiness_remains_narrow():
    brief = _complete_brief()
    brief.excluded_capabilities = []
    brief.negative_triggers = []
    assert not brief_ready_for_candidate(brief)
    receipt = _confirmation(brief)
    assert brief_ready_for_candidate(brief, receipt, require_confirmation=True)
    assert brief.owned_capabilities == ["提取决定", "识别负责人"]


def test_changed_business_boundary_invalidates_readiness():
    brief = _complete_brief()
    receipt = _confirmation(brief)
    brief.mission = "改为另一个任务"
    assert not brief_ready_for_candidate(brief, receipt, require_confirmation=True)


def test_timestamps_do_not_invalidate_business_confirmation():
    brief = _complete_brief()
    receipt = _confirmation(brief)
    brief.updated_at = "2099-01-01T00:00:00+00:00"
    assert brief_ready_for_candidate(brief, receipt, require_confirmation=True)


def test_pending_confirmation_is_not_readiness():
    brief = _complete_brief()
    receipt = _confirmation(brief)
    receipt["status"] = "pending"
    assert not brief_ready_for_candidate(brief, receipt, require_confirmation=True)

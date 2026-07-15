from __future__ import annotations

from pathlib import Path

from skill_engineering.decision import decide_capability, format_decision


def make_root(tmp_path: Path) -> Path:
    root = tmp_path / "hub"
    root.mkdir()
    (root / "registry.yaml").write_text("skills: {}\n", encoding="utf-8")
    return root


BASE = {
    "repeatability": "recurring",
    "agent_facing": True,
    "trigger_separable": True,
    "deterministic_core": False,
    "runtime_required": False,
    "reuse_scope": "one_project",
}


def verdict(tmp_path, **updates):
    answers = {**BASE, **updates}
    return decide_capability(make_root(tmp_path), "处理一个可复用工作流", answers).verdict


def test_decides_create_skill(tmp_path):
    assert verdict(tmp_path) == "create_skill"


def test_decides_no_artifact_for_one_off(tmp_path):
    assert verdict(tmp_path, repeatability="one_off") == "no_new_artifact"


def test_decides_script_for_deterministic_non_agent_work(tmp_path):
    assert verdict(tmp_path, deterministic_core=True, agent_facing=False) == "create_script"


def test_decides_project_doc_for_project_policy(tmp_path):
    assert verdict(tmp_path, agent_facing=False, project_specific=True) == "create_project_doc"


def test_decides_plugin_for_runtime(tmp_path):
    assert verdict(tmp_path, runtime_required=True) == "install_plugin_runtime"


def test_decides_profile_entry_for_visibility_only(tmp_path):
    assert verdict(tmp_path, existing_action="profile") == "add_profile_entry"


def test_decides_extend_existing(tmp_path):
    assert verdict(tmp_path, existing_action="extend") == "extend_existing_skill"


def test_decides_archive_replace(tmp_path):
    assert verdict(tmp_path, existing_action="replace") == "archive_or_replace"


def test_unknowns_are_questions_not_zero_score(tmp_path):
    report = decide_capability(make_root(tmp_path), "模糊想法", {})
    assert report.verdict == "needs_discovery"
    assert report.confidence == "low"
    assert 1 <= len(report.unknowns) <= 3
    assert not hasattr(report, "score")


def test_default_decision_feedback_is_user_readable(tmp_path):
    report = decide_capability(make_root(tmp_path), "模糊想法", {})

    text = format_decision(report)

    assert "继续需求探索" in text
    assert "下一步：" in text
    assert "还需要你确认一个问题" in text
    assert text.count("- 请") == 1
    assert report.id not in text
    assert "create_skill" not in text


def test_one_off_can_be_rejected_before_full_discovery(tmp_path):
    report = decide_capability(
        make_root(tmp_path),
        "帮我临时处理一次文件",
        {"repeatability": "one_off"},
    )

    assert report.verdict == "no_new_artifact"


def test_runtime_requirement_can_route_before_full_discovery(tmp_path):
    report = decide_capability(
        make_root(tmp_path),
        "需要浏览器工具和账号鉴权",
        {"runtime_required": True},
    )

    assert report.verdict == "install_plugin_runtime"

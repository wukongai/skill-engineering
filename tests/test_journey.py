from __future__ import annotations

import json

import pytest

from skill_engineering.journey import (
    JourneySession,
    fingerprint_path,
    list_journeys,
    load_journey,
    new_id,
    save_journey,
)


def test_journey_round_trip_and_handoff(tmp_path):
    session = JourneySession(
        id=new_id("journey"),
        intent="build",
        goal="创建一个安全的发布 Skill",
        stage="design",
        status="awaiting_review",
        completed_steps=["判断是否值得做", "确定触发边界"],
        next_action="确认输入和输出",
    )
    save_journey(tmp_path, session)

    loaded = load_journey(tmp_path, session.id)

    assert loaded.goal == session.goal
    assert loaded.approval["status"] == "not_requested"
    assert "确定触发边界" in loaded.handoff_summary()
    assert "确认输入和输出" in loaded.handoff_summary()
    assert [item.id for item in list_journeys(tmp_path)] == [session.id]


def test_journey_rejects_unknown_schema(tmp_path):
    folder = tmp_path / ".skill-engineering" / "journeys"
    folder.mkdir(parents=True)
    path = folder / "bad.json"
    path.write_text(json.dumps({"schema_version": "999"}), encoding="utf-8")

    with pytest.raises(SystemExit, match="不支持"):
        load_journey(tmp_path, "bad")


def test_fingerprint_changes_and_handles_missing(tmp_path):
    target = tmp_path / "skill"
    target.mkdir()
    skill_md = target / "SKILL.md"
    skill_md.write_text("first", encoding="utf-8")
    before = fingerprint_path(target)
    skill_md.write_text("second", encoding="utf-8")
    after = fingerprint_path(target)

    assert before != after
    assert fingerprint_path(tmp_path / "missing")

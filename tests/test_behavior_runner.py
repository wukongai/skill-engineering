from __future__ import annotations

from pathlib import Path

import pytest

from skill_engineering.behavior import run_behavior_cases


def test_behavior_runner_executes_declarative_cases(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "SKILL.md").write_text(
        """# 会议整理\n\n提取决定、行动项和负责人。\n\n输入不足时停止并说明缺口。\n""",
        encoding="utf-8",
    )
    cases = [
        {
            "id": "success",
            "given": "有会议记录",
            "expect": "输出决定",
            "must_not": ["猜测"],
            "assertions": {"must_include": ["提取决定"], "must_not_include": ["猜测"]},
        },
        {
            "id": "insufficient",
            "given": "没有记录",
            "expect": "说明缺口",
            "must_not": ["伪造结论"],
            "assertions": {"must_include": ["输入不足"], "must_not_include": ["伪造结论"]},
        },
    ]

    result = run_behavior_cases(candidate, cases)

    assert result["status"] == "passed"
    assert result["passed"] == 2
    assert result["failed"] == 0
    assert all(item["status"] == "passed" for item in result["cases"])


def test_behavior_runner_reports_uncovered_cases(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "SKILL.md").write_text("# 候选\n", encoding="utf-8")

    result = run_behavior_cases(candidate, ["成功"])

    assert result["status"] == "uncovered"
    assert result["uncovered"] == 1


@pytest.mark.parametrize("assertions", [{}, {"must_include": [], "must_not_include": []}])
def test_behavior_runner_does_not_pass_empty_assertions(tmp_path: Path, assertions):
    (tmp_path / "SKILL.md").write_text("# 整理\n", encoding="utf-8")
    result = run_behavior_cases(tmp_path, [{
        "id": "empty", "given": "有记录", "expect": "摘要", "must_not": ["猜测"],
        "assertions": assertions,
    }])
    assert result["status"] == "uncovered"
    assert result["passed"] == 0


def test_behavior_runner_empty_suite_is_uncovered(tmp_path: Path):
    (tmp_path / "SKILL.md").write_text("# 整理\n", encoding="utf-8")
    assert run_behavior_cases(tmp_path, [])["status"] == "uncovered"

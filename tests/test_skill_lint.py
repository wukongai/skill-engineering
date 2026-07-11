from __future__ import annotations

from pathlib import Path

from skill_engineering.cli import main as engineering_main
from skill_engineering.skill_lint import LintOptions, lint_skill, main as lint_main


def write_skill(base: Path, body: str, frontmatter: str | None = None) -> Path:
    skill = base / "demo-skill"
    skill.mkdir()
    fm = frontmatter or "name: demo-skill\ndescription: Demo skill for tests.\n"
    (skill / "SKILL.md").write_text(f"---\n{fm}---\n\n{body}\n", encoding="utf-8")
    return skill


def issue_ids(skill: Path, options: LintOptions | None = None) -> set[str]:
    return {issue.rule_id for issue in lint_skill(skill, options).issues}


def test_lint_clean_skill(tmp_path: Path):
    skill = write_skill(tmp_path, "# Demo\n\nUse this for a narrow task.")
    result = lint_skill(skill)
    assert result.error_count == 0
    assert result.warn_count == 0
    assert result.exit_code() == 0


def test_lint_frontmatter_name_and_absolute_path_errors(tmp_path: Path):
    skill = write_skill(
        tmp_path,
        "Run /Users/aim5/Documents/CodingProject/foo/scripts/run.py",
        frontmatter="name: Bad Name\ndescription: Bad naming.\n",
    )
    ids = issue_ids(skill)
    assert "SKILL011" in ids
    assert "SKILL021" in ids


def test_lint_prompt_debt_warnings(tmp_path: Path):
    body = "\n".join(
        [
            "# Demo",
            "这里有门禁, 第二个门禁, 以及 CRITICAL 禁止。",
            "本日实测失败 4 次, 这是事故复盘。",
            'Skill(skill="child-skill", args="x")',
            *["filler" for _ in range(90)],
        ]
    )
    skill = write_skill(tmp_path, body)
    result = lint_skill(skill, LintOptions(soft_lines=20, hard_lines=200))
    ids = {issue.rule_id for issue in result.issues}
    assert result.error_count == 0
    assert {"SKILL120", "SKILL121", "SKILL122", "SKILL123"} <= ids


def test_lint_contradictory_execution_is_error(tmp_path: Path):
    skill = write_skill(
        tmp_path,
        "# Demo\n\n本 skill 只提示, 但下一步自动调用 child skill 并自动执行。",
    )
    ids = issue_ids(skill)
    assert "SKILL022" in ids


def test_lint_fail_on_warn_exit_code(tmp_path: Path, capsys):
    skill = write_skill(tmp_path, "# Demo\n\n本日实测事故复盘。")
    code = lint_main([str(skill), "--fail-on-warn"])
    out = capsys.readouterr().out
    assert code == 1
    assert "SKILL122" in out


def test_skill_engineering_lint_skill_cli_json(tmp_path: Path, capsys):
    skill = write_skill(tmp_path, "# Demo\n\nUse this.")
    code = engineering_main(["lint-skill", str(skill), "--json"])
    out = capsys.readouterr().out
    assert code == 0
    assert '"errors": 0' in out
    assert '"warnings": 0' in out

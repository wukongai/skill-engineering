from __future__ import annotations

import json
from pathlib import Path

import pytest

from skill_engineering.cli import build_parser, main


def test_public_cli_contains_engineering_commands_not_hub_distribution():
    parser = build_parser()
    subparsers = next(
        action for action in parser._actions if action.__class__.__name__ == "_SubParsersAction"
    )
    commands = set(subparsers.choices)
    assert {
        "decide",
        "create",
        "doctor",
        "evaluate",
        "improve",
        "evolution",
        "release-plan",
    } <= commands
    assert {"apply", "status", "forget", "serve", "doctor-install"}.isdisjoint(commands)


def test_doctor_cli_supports_sarif_and_keeps_json_alias(tmp_path: Path, capsys):
    skill = tmp_path / "demo-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: Demo skill for one task.\n---\n",
        encoding="utf-8",
    )

    assert main(["doctor", str(skill), "--format", "sarif"]) == 0
    sarif = json.loads(capsys.readouterr().out)
    assert sarif["version"] == "2.1.0"

    assert main(["doctor", str(skill), "--json"]) == 0
    legacy = json.loads(capsys.readouterr().out)
    assert legacy["target"] == str(skill)

    assert main(["doctor", str(skill), "--format", "json"]) == 0
    explicit = json.loads(capsys.readouterr().out)
    assert explicit == legacy


def test_create_cli_requires_previewed_plan_before_apply(tmp_path: Path, capsys):
    target = tmp_path / "demo-skill"
    code = main(
        [
            "--root",
            str(tmp_path),
            "create",
            "--name",
            "demo-skill",
            "--description",
            "用于明确测试场景。",
            "--target",
            str(target),
            "--json",
        ]
    )
    preview = json.loads(capsys.readouterr().out)
    assert code == 0
    assert not target.exists()
    assert preview["created"] == []
    assert (tmp_path / ".skill-engineering" / "build-plans").is_dir()

    code = main(
        [
            "--root",
            str(tmp_path),
            "create",
            "--plan",
            preview["id"],
            "--apply",
            "--json",
        ]
    )
    applied = json.loads(capsys.readouterr().out)
    assert code == 0
    assert (target / "SKILL.md").is_file()
    assert applied["created"]
    assert applied["postflight"]["status"] == "pass"


def test_create_cli_rejects_direct_apply_without_plan(tmp_path: Path):
    with pytest.raises(SystemExit, match="先生成并预览"):
        main(
            [
                "--root",
                str(tmp_path),
                "create",
                "--name",
                "demo-skill",
                "--description",
                "用于明确测试场景。",
                "--target",
                str(tmp_path / "demo-skill"),
                "--apply",
            ]
        )

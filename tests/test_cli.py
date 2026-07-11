from __future__ import annotations

import json
from pathlib import Path

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


def test_create_cli_uses_standalone_state_root(tmp_path: Path, capsys):
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
            "--apply",
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert (target / "SKILL.md").is_file()
    assert payload["created"]
    assert (tmp_path / ".skill-engineering" / "build-plans").is_dir()

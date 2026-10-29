from __future__ import annotations

import json
from pathlib import Path

import pytest

from skill_engineering.cli import build_parser, main


def test_improve_cli_parses_declaration_but_plan_reuses_frozen_input():
    args = build_parser().parse_args([
        "improve", "demo", "--candidate", "candidate", "--architecture-review", "review.json"
    ])
    assert args.architecture_review == Path("review.json")
    assert build_parser().parse_args(["improve", "--plan", "saved-plan"]).architecture_review is None


def test_improve_and_active_cli_parse_boundary_review():
    args = build_parser().parse_args([
        "improve", "demo", "--candidate", "candidate", "--boundary-review", "boundary.json",
    ])
    assert args.boundary_review == Path("boundary.json")
    release = build_parser().parse_args([
        "release-plan", "--version", "v", "--channel", "active",
        "--boundary-review", "boundary.json",
    ])
    assert release.boundary_review == Path("boundary.json")


@pytest.mark.parametrize("apply", [False, True])
def test_improve_cli_rejects_retrofitting_boundary_onto_saved_plan(tmp_path, apply):
    from test_boundary_maintenance import unchanged_input

    root, target, plan, _ = _legacy_improve_plan(tmp_path)
    arguments = ["--root", str(root), "improve", "--plan", plan.id,
                 "--boundary-review", str(unchanged_input(root))]
    if apply:
        arguments.append("--apply")
    with pytest.raises(SystemExit, match="重新预览"):
        main(arguments)
    assert not (root / ".skill-engineering" / "maintenance-backups").exists()


def test_improve_cli_help_explains_preview_and_saved_plan_requirements(capsys):
    with pytest.raises(SystemExit) as error:
        build_parser().parse_args(["improve", "--help"])
    assert error.value.code == 0
    help_text = capsys.readouterr().out
    assert "新预览必需" in help_text
    assert "--plan" in help_text


def test_improve_cli_without_declaration_returns_blocked_preview(tmp_path, capsys):
    from test_maintenance import setup_pair

    root, target, candidate = setup_pair(tmp_path)
    before = (target / "SKILL.md").read_bytes()
    code = main([
        "--root", str(root), "improve", str(target), "--candidate", str(candidate),
        "--failure-mode", "修复触发", "--root-cause-layer", "trigger",
        "--expected-behavior", "明确请求才触发", "--regression-case", "tests/cases/trigger.yaml",
        "--json",
    ])
    preview = json.loads(capsys.readouterr().out)
    assert code == 1
    assert preview["preflight"]["status"] == "blocked"
    review = preview["preflight"]["architecture_review"]
    assert review["status"] == "blocked"
    assert set(review["input_fingerprints"]) >= {"target", "candidate", "effective"}
    assert (target / "SKILL.md").read_bytes() == before


def _legacy_improve_plan(tmp_path):
    from test_maintenance import architecture_input, plan_for, setup_pair

    from skill_engineering.journey import save_build_plan
    from skill_engineering.maintenance import _plan_hash

    root, target, candidate = setup_pair(tmp_path)
    path = architecture_input(root, target, candidate)
    plan = plan_for(root, target, candidate, architecture_review=path)
    plan.preflight.pop("architecture_review")
    plan.plan_hash = _plan_hash(plan)
    save_build_plan(root, plan)
    return root, target, plan, path


def test_improve_cli_can_show_but_cannot_apply_legacy_unreviewed_plan(tmp_path, capsys):
    root, target, plan, _ = _legacy_improve_plan(tmp_path)
    before = (target / "SKILL.md").read_bytes()
    assert main(["--root", str(root), "improve", "--plan", plan.id, "--json"]) == 0
    shown = json.loads(capsys.readouterr().out)
    assert shown["plan_hash"] == plan.plan_hash
    assert "architecture_review" not in shown["preflight"]
    with pytest.raises(SystemExit, match="架构|审查"):
        main(["--root", str(root), "improve", "--plan", plan.id, "--apply"])
    assert (target / "SKILL.md").read_bytes() == before
    assert not (root / ".skill-engineering" / "maintenance-backups").exists()
    assert not (root / ".skill-engineering" / "maintenance-records").exists()


@pytest.mark.parametrize("apply", [False, True])
def test_improve_cli_rejects_retrofitting_review_onto_saved_plan(tmp_path, apply):
    root, target, plan, path = _legacy_improve_plan(tmp_path)
    before = (target / "SKILL.md").read_bytes()
    arguments = [
        "--root", str(root), "improve", "--plan", plan.id, "--architecture-review", str(path)
    ]
    if apply:
        arguments.append("--apply")
    with pytest.raises(SystemExit, match="重新预览"):
        main(arguments)
    assert (target / "SKILL.md").read_bytes() == before


def test_release_plan_cli_accepts_active_architecture_declaration():
    args = build_parser().parse_args([
        "release-plan", "--version", "version-id", "--channel", "active",
        "--architecture-review", "review.json",
    ])
    assert args.architecture_review == Path("review.json")


def test_improve_cli_freezes_architecture_input_into_existing_plan(tmp_path, capsys):
    from test_maintenance import architecture_input, boundary_input, setup_pair

    root, target, candidate = setup_pair(tmp_path)
    path = architecture_input(root, target, candidate)
    boundary = boundary_input(root)
    code = main([
        "--root", str(root), "improve", str(target), "--candidate", str(candidate),
        "--failure-mode", "修复触发", "--root-cause-layer", "trigger",
        "--expected-behavior", "明确请求才触发", "--regression-case", "tests/cases/trigger.yaml",
        "--architecture-review", str(path), "--boundary-review", str(boundary), "--json",
    ])
    preview = json.loads(capsys.readouterr().out)
    assert code == 0
    assert preview["preflight"]["architecture_review"]["status"] == "pass"
    assert preview["preflight"]["boundary_review"]["confirmation_status"] == "confirmed"
    path.write_text("invalid JSON", encoding="utf-8")
    boundary.write_text("invalid JSON", encoding="utf-8")
    assert main(["--root", str(root), "improve", "--plan", preview["id"], "--apply", "--json"]) == 0
    applied = json.loads(capsys.readouterr().out)
    assert applied["preflight"]["architecture_review"]["status"] == "pass"
    assert applied["preflight"]["boundary_review"]["confirmation_status"] == "confirmed"


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

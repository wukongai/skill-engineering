from __future__ import annotations

import json
import shutil
from pathlib import Path

from skill_engineering.cli import main


ROOT = Path(__file__).resolve().parents[1]
SOURCE_SKILL = ROOT / "skills" / "skill-engineering"


def test_isolated_global_install_supports_create_and_doctor_flow(tmp_path: Path, capsys):
    global_skills = tmp_path / "global" / "skills"
    global_skills.mkdir(parents=True)
    shutil.copytree(SOURCE_SKILL, global_skills / "skill-engineering")

    assert sorted(path.name for path in global_skills.iterdir()) == ["skill-engineering"]
    assert not (global_skills / "skill-guide").exists()

    consumer_root = tmp_path / "consumer"
    target = consumer_root / "demo-skill"
    preview_code = main(
        [
            "--root",
            str(consumer_root),
            "create",
            "--name",
            "demo-skill",
            "--description",
            "用于验证全局安装后的创建闭环。",
            "--target",
            str(target),
            "--json",
        ]
    )
    preview = json.loads(capsys.readouterr().out)
    assert preview_code == 0
    assert not target.exists()

    apply_code = main(
        [
            "--root",
            str(consumer_root),
            "create",
            "--plan",
            preview["id"],
            "--apply",
            "--json",
        ]
    )
    applied = json.loads(capsys.readouterr().out)
    assert apply_code == 0
    assert (target / "SKILL.md").is_file()
    assert applied["postflight"]["status"] == "pass"

    doctor_code = main(
        [
            "doctor",
            str(global_skills / "skill-engineering"),
            "--profile",
            "production",
            "--format",
            "json",
        ]
    )
    report = json.loads(capsys.readouterr().out)
    assert doctor_code == 0
    assert report["target"].endswith("global/skills/skill-engineering")

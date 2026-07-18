from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "skills" / "skill-engineering" / "scripts" / "doctor_skill.py"


def test_installed_skill_wrapper_reports_missing_python_cli(tmp_path: Path):
    installed_wrapper = (
        tmp_path
        / "home"
        / ".agents"
        / "skills"
        / "skill-engineering"
        / "scripts"
        / "doctor_skill.py"
    )
    installed_wrapper.parent.mkdir(parents=True)
    shutil.copy2(WRAPPER, installed_wrapper)

    result = subprocess.run(
        [
            sys.executable,
            "-I",
            str(installed_wrapper),
            str(tmp_path / "demo-skill"),
            "--profile",
            "team",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert "尚未安装 Skill Engineering Python CLI" in result.stderr
    assert "npx skills add" in result.stderr
    assert 'uv tool install "git+https://github.com/wukongai/skill-engineering.git@v1.0.0"' in result.stderr
    assert "skill-engineering doctor <skill-path>" in result.stderr
    assert "Traceback" not in result.stderr


def test_repo_wrapper_keeps_existing_doctor_behavior():
    result = subprocess.run(
        [sys.executable, str(WRAPPER), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "--profile" in result.stdout
    assert "--json" in result.stdout

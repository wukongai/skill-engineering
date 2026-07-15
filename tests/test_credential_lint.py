from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "credential-lint.sh"


def run_lint(project: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT), "--all"],
        cwd=project,
        text=True,
        capture_output=True,
        check=False,
    )


def test_all_mode_ignores_generated_environment_but_scans_untracked_source(tmp_path: Path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / ".gitignore").write_text(".venv/\n", encoding="utf-8")

    fake_credential = "sk-" + "A" * 24
    dependency = tmp_path / ".venv" / "lib" / "third-party.txt"
    dependency.parent.mkdir(parents=True)
    dependency.write_text(fake_credential, encoding="utf-8")

    clean = run_lint(tmp_path)
    assert clean.returncode == 0, clean.stdout + clean.stderr

    (tmp_path / "leak.txt").write_text(fake_credential, encoding="utf-8")
    detected = run_lint(tmp_path)
    assert detected.returncode == 1
    assert "疑似凭证" in detected.stdout

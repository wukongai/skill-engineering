from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from skill_engineering.skill_doctor import doctor_skill


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "skill-engineering"
REVIEW = SKILL_DIR / "scripts" / "creation_review.py"
PARITY_FIXTURES = SKILL_DIR / "tests" / "portable-review-fixtures.json"

CLEAN_SKILL_MD = """---
name: pure-agent-clean
description: 当用户提供一段会议记录并要求整理成固定结构摘要时使用；不用于音频转写、消息发送或外部系统操作。
---

# pure-agent-clean

## 输入

- 一段已经提供的会议记录文本。

## 处理步骤

1. 提取明确出现的决定、行动项和负责人。
2. 无法从输入确认的信息标为“未提供”，不要猜测。

## 输出

- 决定、行动项、负责人和未决问题四个分区。

## 停止条件

- 输入不是会议记录，或请求超出文本整理范围时停止并说明边界。

## 行为样例

- 输入“决定周五发布，阿明负责测试”，输出对应决定和负责人。
"""


def _write_clean_skill(target: Path) -> None:
    target.mkdir(parents=True)
    (target / "SKILL.md").write_text(CLEAN_SKILL_MD, encoding="utf-8")


def _run_portable(target: Path, *, isolated: bool = False) -> subprocess.CompletedProcess[str]:
    flags = ["-I", "-S"] if isolated else []
    return subprocess.run(
        [
            sys.executable,
            *flags,
            str(REVIEW),
            str(target),
            "--profile",
            "personal",
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_portable_review_runs_with_isolated_site_packages(tmp_path: Path):
    target = tmp_path / "pure-agent-clean"
    _write_clean_skill(target)

    result = _run_portable(target, isolated=True)

    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["assessment"]["method"] == "portable_creation_profile"


def test_portable_review_reports_four_dimensions_and_false_utility_claim(tmp_path: Path):
    target = tmp_path / "pure-agent-clean"
    _write_clean_skill(target)

    result = _run_portable(target)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["score"] == 100
    assert payload["grade"] == "A"
    assert set(payload["dimensions"]) == {
        "functional_value",
        "stability",
        "security",
        "engineering",
    }
    assert payload["utility_claim"] is False
    assert payload["real_task_trial"]["status"] == "pending"


def test_portable_review_blocks_content_gate_failure(tmp_path: Path):
    target = tmp_path / "pure-agent-clean"
    _write_clean_skill(target)
    (target / "SKILL.md").write_text(
        CLEAN_SKILL_MD + "\nTODO: 稍后补充真实工作流。\n",
        encoding="utf-8",
    )

    result = _run_portable(target)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert any(item["rule"] == "CG001" for item in payload["findings"])


def test_enumerated_parity_fixtures_match_doctor_grade_and_dimensions(tmp_path: Path):
    fixtures = json.loads(PARITY_FIXTURES.read_text(encoding="utf-8"))
    assert fixtures["schema_version"] == "1.0"
    assert fixtures["fixtures"]

    for fixture in fixtures["fixtures"]:
        assert fixture["kind"] == "pure_agent_clean"
        target = tmp_path / fixture["directory"]
        _write_clean_skill(target)
        portable = json.loads(_run_portable(target, isolated=True).stdout)
        doctor = doctor_skill(target, profile=fixture["profile"])
        assert doctor.exit_code() == 0
        assert doctor.score is not None
        doctor_dimensions = {
            dimension.key: dimension.score for dimension in doctor.score.dimensions
        }
        assert portable["grade"] == doctor.score.grade == fixture["expected"]["grade"]
        assert (
            portable["dimensions"]
            == doctor_dimensions
            == fixture["expected"]["dimensions"]
        )


def test_creation_review_docs_make_portable_profile_primary():
    doc = (SKILL_DIR / "references" / "creation-review.md").read_text(encoding="utf-8")
    file_map = (SKILL_DIR / "references" / "file-map.md").read_text(encoding="utf-8")
    contract = (SKILL_DIR / "skill.contract.yaml").read_text(encoding="utf-8")

    assert "scripts/creation_review.py" in doc
    assert "portable creation profile" in doc
    assert "完整 CLI Doctor" in doc
    assert "可选增强" in doc
    assert "scripts/creation_review.py" in file_map
    assert "scripts/creation_review.py" in contract

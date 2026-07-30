"""v1.1 NA-4: 创建评审与评分、用户可见状态机、创建后简易自动化测试入口。"""

from __future__ import annotations

import json
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "skill-engineering"
SELF_TEST = SKILL_DIR / "scripts" / "skill_self_test.py"

CLEAN_SKILL_MD = """---
name: demo-skill
description: 把固定格式日志转换成稳定 JSON 报告。
---

# demo-skill

## 工作流

1. 读取并校验输入日志。
2. 运行 `scripts/parse.py` 生成 JSON。
3. 校验输出字段完整性。

## 失败处理

- 解析失败时返回错误详情,不报告任务完成。
"""


def test_creation_review_reference_covers_status_machine_and_boundaries():
    doc = (SKILL_DIR / "references" / "creation-review.md").read_text(encoding="utf-8")
    for status in [
        "needs_discovery",
        "candidate_incomplete",
        "candidate_ready",
        "created_untried",
        "validated",
        "needs_improvement",
    ]:
        assert status in doc, f"creation-review.md 缺少状态 {status}"
    assert "创建评审" in doc
    assert "尚未验证实际任务效果" in doc
    assert "自动化测试" in doc


def test_quality_score_standard_covers_creation_review():
    text = (SKILL_DIR / "references" / "quality-score-standard.md").read_text(encoding="utf-8")
    assert "创建评审" in text


def test_doctor_stage_has_creation_review_entry():
    text = (SKILL_DIR / "stages" / "doctor" / "INSTRUCTIONS.md").read_text(encoding="utf-8")
    assert "创建评审" in text


def test_creation_review_contract_boundaries():
    contract = yaml.safe_load((SKILL_DIR / "skill.contract.yaml").read_text(encoding="utf-8"))
    outputs = {item["name"] for item in contract["outputs"]}
    assert "creation_review" in outputs
    forbidden = set(contract["forbidden"])
    assert "claiming_validated_without_real_task_trial" in forbidden
    assert "presenting_structural_score_as_utility" in forbidden


def write_clean_skill(target: Path) -> None:
    target.mkdir(parents=True)
    skill_md = CLEAN_SKILL_MD.replace(
        "把固定格式日志转换成稳定 JSON 报告。",
        "当用户提供固定格式日志并要求转换成 JSON 报告时使用；不用于音频转写、图像识别或自由写作。",
    )
    (target / "SKILL.md").write_text(skill_md, encoding="utf-8")
    (target / "scripts").mkdir()
    (target / "scripts" / "parse.py").write_text(
        "import json, sys\n"
        "value = sys.stdin.read().strip()\n"
        "print(json.dumps({'status': 'ok', 'value': value}))\n",
        encoding="utf-8",
    )
    (target / "tests" / "fixtures").mkdir(parents=True)
    (target / "tests" / "fixtures" / "input.txt").write_text("hello\n", encoding="utf-8")
    (target / "tests" / "self-test.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "tests": [
                    {
                        "id": "success",
                        "script": "scripts/parse.py",
                        "stdin": "tests/fixtures/input.txt",
                        "expected_exit": 0,
                        "stdout_contains": ['"status": "ok"', '"value": "hello"'],
                        "stdout_json_keys": ["status", "value"],
                        "timeout_seconds": 10,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def run_self_test(target: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SELF_TEST), str(target), "--json"],
        capture_output=True,
        text=True,
        check=False,
    )


def test_self_test_passes_clean_skill_and_marks_agent_trial_pending(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)

    result = run_self_test(target)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["steps"]["content_gate"] == "pass"
    assert payload["steps"]["creation_review"] == "pass"
    assert payload["steps"]["declared_tests"] == "pass"
    assert payload["declared_tests"][0]["status"] == "pass"
    assert payload["agent_trial"]["status"] == "pending"


def test_self_test_blocked_by_placeholder(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    (target / "SKILL.md").write_text(CLEAN_SKILL_MD + "\nTODO: 补充示例\n", encoding="utf-8")

    result = run_self_test(target)

    assert result.returncode == 1
    assert json.loads(result.stdout)["status"] == "blocked"


def test_self_test_blocked_by_broken_script(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    (target / "scripts" / "parse.py").write_text("def broken(:\n", encoding="utf-8")

    result = run_self_test(target)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["steps"]["declared_tests"] == "blocked"
    assert payload["declared_tests"][0]["status"] == "blocked"


def test_self_test_executes_declared_script_and_catches_runtime_failure(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    (target / "scripts" / "parse.py").write_text(
        "raise RuntimeError('runtime-only-failure')\n",
        encoding="utf-8",
    )

    result = run_self_test(target)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["steps"]["declared_tests"] == "blocked"
    assert "runtime-only-failure" in payload["declared_tests"][0]["stderr"]


def test_self_test_times_out(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    (target / "scripts" / "parse.py").write_text(
        "import time\ntime.sleep(5)\n",
        encoding="utf-8",
    )
    manifest = json.loads((target / "tests" / "self-test.json").read_text(encoding="utf-8"))
    manifest["tests"][0]["timeout_seconds"] = 1
    (target / "tests" / "self-test.json").write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )

    result = run_self_test(target)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["declared_tests"][0]["status"] == "blocked"
    assert payload["declared_tests"][0]["reason"] == "timeout"


def test_self_test_rejects_non_python_script_as_uncovered(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    (target / "scripts" / "parse.py").unlink()
    (target / "scripts" / "parse.sh").write_text("#!/bin/sh\nprintf ok\n", encoding="utf-8")
    manifest = json.loads((target / "tests" / "self-test.json").read_text(encoding="utf-8"))
    manifest["tests"][0]["script"] = "scripts/parse.sh"
    (target / "tests" / "self-test.json").write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )

    result = run_self_test(target)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["steps"]["declared_tests"] == "uncovered"
    assert payload["declared_tests"][0]["status"] == "uncovered"


def _fingerprint(target: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in target.rglob("*") if item.is_file()):
        digest.update(path.relative_to(target).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def test_self_test_does_not_create_pycache_or_modify_target(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    before = _fingerprint(target)

    result = run_self_test(target)

    assert result.returncode == 0, result.stdout + result.stderr
    assert _fingerprint(target) == before
    assert not list(target.rglob("__pycache__"))


def test_installed_self_test_does_not_modify_own_skill(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    source_scripts = SKILL_DIR / "scripts"
    for name in ("content_gate.py", "creation_review.py", "skill_self_test.py"):
        shutil.copy2(source_scripts / name, target / "scripts" / name)
    before = _fingerprint(target)

    result = subprocess.run(
        [
            sys.executable,
            str(target / "scripts" / "skill_self_test.py"),
            str(target),
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert _fingerprint(target) == before
    assert not list(target.rglob("__pycache__"))


def test_self_test_missing_directory_is_usage_error(tmp_path):
    result = run_self_test(tmp_path / "not-exist")

    assert result.returncode == 2

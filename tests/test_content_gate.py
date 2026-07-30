"""v1.1 NA-3: 随 Skill 交付的 Content Completion Gate(portable checker)。"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "skills" / "skill-engineering" / "scripts" / "content_gate.py"

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


def run_gate(target: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GATE), str(target), "--json"],
        capture_output=True,
        text=True,
        check=False,
    )


def write_clean_skill(target: Path) -> None:
    target.mkdir(parents=True)
    (target / "SKILL.md").write_text(CLEAN_SKILL_MD, encoding="utf-8")
    (target / "scripts").mkdir()
    (target / "scripts" / "parse.py").write_text("print('{}')\n", encoding="utf-8")
    (target / "tests" / "fixtures").mkdir(parents=True)
    (target / "tests" / "fixtures" / "input.txt").write_text("demo\n", encoding="utf-8")
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
                        "stdout_contains": ["{}"],
                        "timeout_seconds": 10,
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def findings_by_rule(result: subprocess.CompletedProcess[str]) -> set[str]:
    payload = json.loads(result.stdout)
    return {item["rule"] for item in payload["findings"]}


def test_clean_candidate_passes(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)

    result = run_gate(target)

    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["status"] == "pass"


def test_placeholder_content_is_blocked(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    (target / "SKILL.md").write_text(CLEAN_SKILL_MD + "\nTODO: 补充真实示例\n", encoding="utf-8")

    result = run_gate(target)

    assert result.returncode == 1
    assert "CG001" in findings_by_rule(result)


def test_empty_resource_directory_is_blocked(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    (target / "references").mkdir()

    result = run_gate(target)

    assert result.returncode == 1
    assert "CG002" in findings_by_rule(result)


def test_generic_fallback_sentence_is_blocked(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    (target / "SKILL.md").write_text(
        CLEAN_SKILL_MD + "\n2. 执行这个 Skill 拥有的单一职责。\n", encoding="utf-8"
    )

    result = run_gate(target)

    assert result.returncode == 1
    assert "CG003" in findings_by_rule(result)


def test_broken_reference_is_blocked(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    (target / "SKILL.md").write_text(
        CLEAN_SKILL_MD + "\n详见 `references/guide.md`。\n", encoding="utf-8"
    )

    result = run_gate(target)

    assert result.returncode == 1
    assert "CG004" in findings_by_rule(result)


def test_empty_declared_script_is_blocked(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    (target / "scripts" / "parse.py").write_text("", encoding="utf-8")

    result = run_gate(target)

    assert result.returncode == 1
    assert "CG005" in findings_by_rule(result)


def test_empty_resource_file_is_blocked(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    (target / "references").mkdir()
    (target / "references" / "guide.md").write_text("", encoding="utf-8")

    result = run_gate(target)

    assert result.returncode == 1
    assert "CG002" in findings_by_rule(result)


def test_env_file_is_blocked(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    (target / ".env").write_text("API_KEY=placeholder-value\n", encoding="utf-8")

    result = run_gate(target)

    assert result.returncode == 1
    assert "CG009" in findings_by_rule(result)


def test_invalid_frontmatter_is_blocked(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    (target / "SKILL.md").write_text(
        CLEAN_SKILL_MD.replace("description: 把固定格式日志转换成稳定 JSON 报告。\n", ""),
        encoding="utf-8",
    )

    result = run_gate(target)

    assert result.returncode == 1
    assert "CG006" in findings_by_rule(result)


def test_side_effect_without_approval_is_blocked(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    (target / "SKILL.md").write_text(
        CLEAN_SKILL_MD + "\n把结果同步到外部系统,这是不可逆操作。\n", encoding="utf-8"
    )

    result = run_gate(target)

    assert result.returncode == 1
    assert "CG007" in findings_by_rule(result)


def test_complex_workflow_without_failure_handling_is_blocked(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    (target / "SKILL.md").write_text(
        CLEAN_SKILL_MD.replace("## 失败处理", "## 其他").replace(
            "- 解析失败时返回错误详情,不报告任务完成。", "- 输出结果。"
        ),
        encoding="utf-8",
    )

    result = run_gate(target)

    assert result.returncode == 1
    assert "CG008" in findings_by_rule(result)


def test_credentials_are_blocked(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    (target / "scripts" / "parse.py").write_text(
        "API_KEY = '" + "sk-live-" + "abcdef1234567890" + "'\n", encoding="utf-8"
    )

    result = run_gate(target)

    assert result.returncode == 1
    assert "CG009" in findings_by_rule(result)


def test_missing_target_is_usage_error(tmp_path):
    result = run_gate(tmp_path / "not-exist")

    assert result.returncode == 2


def test_env_local_is_blocked(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    (target / ".env.local").write_text("PASSWORD=DEMO_SECRET_VALUE\n", encoding="utf-8")

    result = run_gate(target)

    assert result.returncode == 1
    assert "CG009" in findings_by_rule(result)


def test_pem_file_is_blocked(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    (target / "references").mkdir()
    (target / "references" / "private.pem").write_text(
        "-----BEGIN PRIVATE KEY-----\nDEMO\n-----END PRIVATE KEY-----\n",
        encoding="utf-8",
    )

    result = run_gate(target)

    assert result.returncode == 1
    assert "CG009" in findings_by_rule(result)


def test_symlink_resource_is_blocked(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    outside = tmp_path / "outside.md"
    outside.write_text("external\n", encoding="utf-8")
    (target / "references").mkdir()
    (target / "references" / "guide.md").symlink_to(outside)

    result = run_gate(target)

    assert result.returncode == 1
    assert "CG009" in findings_by_rule(result)


def test_reference_escape_is_blocked(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    (target / "references").mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("external\n", encoding="utf-8")
    (target / "SKILL.md").write_text(
        CLEAN_SKILL_MD + "\n详见 `references/../../outside.md`。\n",
        encoding="utf-8",
    )

    result = run_gate(target)

    assert result.returncode == 1
    assert "CG004" in findings_by_rule(result)


def test_frontmatter_name_must_match_directory(tmp_path):
    target = tmp_path / "different-directory"
    write_clean_skill(target)

    result = run_gate(target)

    assert result.returncode == 1
    assert "CG006" in findings_by_rule(result)


def test_english_delete_without_approval_is_blocked(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    (target / "SKILL.md").write_text(
        CLEAN_SKILL_MD + "\nWrite the report to disk and delete the source file.\n",
        encoding="utf-8",
    )

    result = run_gate(target)

    assert result.returncode == 1
    assert "CG007" in findings_by_rule(result)


def test_script_requires_self_test_manifest(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    (target / "tests" / "self-test.json").unlink()

    result = run_gate(target)

    assert result.returncode == 1
    assert "CG005" in findings_by_rule(result)


def test_self_test_manifest_rejects_escape(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    outside = tmp_path / "outside.txt"
    outside.write_text("external\n", encoding="utf-8")
    (target / "tests" / "self-test.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "tests": [
                    {
                        "id": "escape",
                        "script": "scripts/parse.py",
                        "stdin": "../outside.txt",
                        "expected_exit": 0,
                        "timeout_seconds": 10,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = run_gate(target)

    assert result.returncode == 1
    assert "CG010" in findings_by_rule(result)


def test_failure_corpus_may_name_placeholder_tokens(tmp_path):
    target = tmp_path / "demo-skill"
    write_clean_skill(target)
    (target / "tests" / "failure-cases.yaml").write_text(
        "cases:\n"
        "  - id: placeholder_candidate_blocked\n"
        "    input: TODO marker\n"
        "    expected: blocked\n",
        encoding="utf-8",
    )

    result = run_gate(target)

    matching = [
        finding
        for finding in json.loads(result.stdout)["findings"]
        if finding["rule"] == "CG001"
        and finding["path"] == "tests/failure-cases.yaml"
    ]
    assert not matching

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest

import skill_engineering
from skill_engineering.scaffold import apply_build_plan, create_build_plan
from skill_engineering.skill_doctor import doctor_skill
from skill_engineering.skill_lint import lint_skill


ROOT = Path(__file__).resolve().parents[1]


ARTICLE_USE_CASES = [
    {
        "name": "extract-meeting-actions",
        "kind": "atomic",
        "description": "从会议记录提取有原文依据的决策、负责人和截止时间。",
        "use_when": ["用户要求提取会议决策、负责人或截止时间。"],
        "do_not_use_when": ["用户只要求总结主要观点或润色会议记录。"],
        "inputs": ["meeting_markdown"],
        "outputs": ["source", "decisions", "actions", "open_questions"],
        "side_effect": False,
    },
    {
        "name": "github-issue-planner",
        "kind": "composite",
        "description": "只读整理用户提供的 GitHub Issue 快照，完成分类、去重和实施建议。",
        "use_when": ["用户需要分析已经提供的 Issue 数据并生成实施计划。"],
        "do_not_use_when": ["请求修改标签、评论、关闭 Issue 或访问未授权仓库。"],
        "inputs": ["issue_snapshot"],
        "outputs": ["classification", "duplicates", "implementation_plan"],
        "side_effect": False,
    },
    {
        "name": "local-web-acceptance",
        "kind": "adapter",
        "description": "在用户批准的本地测试站点上执行登录、搜索和导出验收并保存证据。",
        "use_when": ["用户需要对本地 fixture Web 应用执行可重复验收。"],
        "do_not_use_when": ["目标是真实生产站点、未授权账号或外部数据。"],
        "inputs": ["fixture_url", "acceptance_cases"],
        "outputs": ["screenshots", "csv", "json_report", "markdown_report"],
        "side_effect": True,
    },
    {
        "name": "research-evidence-pack",
        "kind": "composite",
        "description": "把本地研究资料组织成研究计划、证据登记、结论摘要和未决问题。",
        "use_when": ["用户需要把可复用研究问题整理为多文件证据包。"],
        "do_not_use_when": ["请求访问账号、凭证或未提供的资料。"],
        "inputs": ["research_question", "source_notes", "evidence_items"],
        "outputs": ["research_plan", "evidence_register", "conclusion_brief", "open_questions"],
        "side_effect": False,
    },
]


@pytest.mark.parametrize("case", ARTICLE_USE_CASES, ids=lambda case: case["name"])
def test_article_use_case_preview_apply_and_validate(tmp_path: Path, case: dict[str, object]):
    target = tmp_path / str(case["name"])
    plan = create_build_plan(
        tmp_path,
        target,
        name=str(case["name"]),
        description=str(case["description"]),
        kind=str(case["kind"]),
        use_when=list(case["use_when"]),
        do_not_use_when=list(case["do_not_use_when"]),
        inputs=list(case["inputs"]),
        outputs=list(case["outputs"]),
        side_effect=bool(case["side_effect"]),
    )

    assert not target.exists(), "preview 不得提前写文件"
    assert plan.applied is False
    created = apply_build_plan(tmp_path, plan)

    assert created
    assert plan.applied is True
    assert plan.postflight["status"] == "pass"
    assert lint_skill(target).exit_code() == 0
    assert doctor_skill(target, profile="team").fail_count == 0
    assert str(case["description"]) in (target / "SKILL.md").read_text(encoding="utf-8")

    if case["kind"] == "atomic":
        assert not (target / "skill.contract.yaml").exists()
    else:
        assert (target / "skill.contract.yaml").is_file()
        assert (target / "tests/cases/success.yaml").is_file()
        assert (target / "tests/cases/failure.yaml").is_file()
        assert (target / "tests/cases/high-risk.yaml").is_file()


def test_research_pack_unsafe_first_plan_rolls_back(tmp_path: Path):
    target = tmp_path / "research-evidence-pack"
    unsafe = create_build_plan(
        tmp_path,
        target,
        name="research-evidence-pack",
        description="整理研究资料并直接对外发布结论。",
        kind="composite",
    )

    with pytest.raises(SystemExit, match="已清理本次新建目标"):
        apply_build_plan(tmp_path, unsafe)

    assert not target.exists()
    assert unsafe.postflight["status"] == "failed_rolled_back"


def test_v1_version_and_release_facts_are_frozen():
    # 1.1.0:当前发布版本;v1 公开契约与兼容指南在 1.x 内持续有效
    assert skill_engineering.__version__ == "1.1.0"
    assert 'version = "1.1.0"' in (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert (ROOT / "docs/references/v1-public-contract.md").is_file()
    assert (ROOT / "docs/guides/v1-compatibility.md").is_file()


def test_v11_changelog_records_formal_release_and_validation_boundary():
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    assert "## 1.1.0 - 2026-08-01" in changelog
    released = changelog.split("## 1.1.0 - 2026-08-01", 1)[1].split(
        "## 1.0.0", 1
    )[0]
    assert "Native Authoring" in released
    assert "发布后独立项目" in released


def test_bilingual_readme_marks_external_quick_validate_optional():
    chinese = (ROOT / "README.md").read_text(encoding="utf-8")
    english = (ROOT / "README.en.md").read_text(encoding="utf-8")

    chinese_line = next(line for line in chinese.splitlines() if "quick_validate.py" in line)
    english_line = next(line for line in english.splitlines() if "quick_validate.py" in line)
    assert "可选" in chinese_line and "production Doctor" in chinese_line
    assert "optional" in english_line.lower() and "production Doctor" in english_line


def test_debug_log_is_ignored():
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "kimi-hook-debug.log" in ignore


def test_codex_is_the_only_required_real_host_release_gate():
    normative_paths = [
        "docs/adr/0009-codex-canonical-release-gate.md",
        "docs/specs/2026-07-29-v1.1-native-authoring-spec.md",
        "docs/plans/2026-07-29-v1.1-native-authoring-plan.md",
        "docs/TASK.md",
        "docs/sprints/2026-07-v1.1-native-authoring.md",
        "docs/releases/RELEASE-LOG.md",
        "docs/guides/skill-engineering-execution-architecture.md",
    ]
    combined = "\n".join(
        (ROOT / relative_path).read_text(encoding="utf-8")
        for relative_path in normative_paths
    )

    assert "Codex" in combined
    assert "唯一" in combined
    assert "非阻断" in combined
    assert "adapter" in combined.lower()
    assert "Codex 与 Hermes 无 Creator E2E 通过" not in combined
    assert "Hermes 无 Creator 真实 E2E 仍待真实环境" not in combined


def test_release_evidence_reports_codex_passed_and_non_codex_non_blocking():
    release_log = (ROOT / "docs/releases/RELEASE-LOG.md").read_text(encoding="utf-8")
    v11 = release_log.split("## `1.1.0`", 1)[1].split("## `0.1.0`", 1)[0]

    assert "Stable" in v11
    assert "Codex" in v11 and "Hermes" in v11
    assert "已通过" in v11
    assert "非阻断" in v11
    assert "发布后" in v11
    assert "tag" in v11.lower()
    assert "GitHub Release" in v11


def test_released_v11_passes_consistency_with_frozen_release_date():
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "check-release.py"),
            "--version",
            "1.1.0",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr

from __future__ import annotations

from pathlib import Path

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
    assert skill_engineering.__version__ == "1.0.0"
    assert 'version = "1.0.0"' in (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert (ROOT / "docs/references/v1-public-contract.md").is_file()
    assert (ROOT / "docs/guides/v1-compatibility.md").is_file()

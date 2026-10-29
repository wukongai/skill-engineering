from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
NATIVE_PLAN = ROOT / "skills" / "skill-engineering" / "scripts" / "native_plan.py"

SKILL_MD = """---
name: meeting-summary
description: 当用户提供会议记录并要求整理决定与行动项时使用；不用于音频转写、消息发送或自由写作。
---

# meeting-summary

## 输入

- 已提供的会议记录文本。

## 处理步骤

1. 提取明确的决定、行动项和负责人。
2. 信息未提供时明确标注，不要猜测。

## 输出

- 决定、行动项、负责人和未决问题。

## 停止条件

- 输入不是会议记录时停止。

## 行为样例

- 输入“周五发布，阿明测试”，输出决定与负责人。
"""


def _write_brief(project: Path, brief_id: str = "brief-demo") -> Path:
    path = project / ".skill-engineering" / "authoring-briefs" / f"{brief_id}.json"
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "id": brief_id,
                "goal": "把会议记录整理成决定与行动项",
                "positive_triggers": ["整理会议纪要"],
                "negative_triggers": ["音频转写"],
                "verification": ["真实会议记录试运行"],
                "mission": "把会议记录整理成可执行的行动项",
                "owned_capabilities": ["提取决定", "识别负责人"],
                "excluded_capabilities": ["音频转写", "发送任务通知"],
                "allowed_context": ["用户提供的会议记录"],
                "inputs": ["会议记录文本"],
                "outputs": ["决定与行动项"],
                "side_effects": [],
                "approvals": [],
                "redirect_strategy": ["说明输入边界并停止或交接"],
                "drift_signals": ["开始讨论会议以外的业务决策"],
                "stop_conditions": ["输入不是会议记录时停止"],
                "acceptance_cases": ["有负责人和截止时间的行动项被正确提取"],
                "behavior_cases": [
                    {
                        "id": "success",
                        "category": "success",
                        "given": "有会议记录",
                        "expect": "提取决定",
                        "must_not": ["猜测"],
                        "assertions": {
                            "must_include": ["提取明确"],
                            "must_not_include": ["伪造"],
                        },
                    },
                    {
                        "id": "negative", "category": "negative",
                        "given": "音频输入", "expect": "停止", "must_not": [],
                        "assertions": {"must_include": ["输入不是会议记录时停止"]},
                    },
                    {
                        "id": "insufficient", "category": "insufficient",
                        "given": "信息不足", "expect": "标注缺口", "must_not": [],
                        "assertions": {"must_include": ["信息未提供时明确标注"]},
                    },
                ],
                "examples": ["输入会议文本，输出决定"],
                "schema_version": "1",
            }
        ),
        encoding="utf-8",
    )
    return path


def _write_candidate(root: Path) -> Path:
    candidate = root / "meeting-summary"
    candidate.mkdir(parents=True)
    (candidate / "SKILL.md").write_text(SKILL_MD, encoding="utf-8")
    (candidate / "references").mkdir()
    (candidate / "references" / "format.md").write_text(
        "# 输出格式\n\n按决定、行动项、负责人、未决问题分区。\n",
        encoding="utf-8",
    )
    return candidate


def _run(*args: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", "-S", str(NATIVE_PLAN), *(str(arg) for arg in args)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _write_confirmation(project: Path, *, status: str = "confirmed") -> Path:
    from skill_engineering.boundary_policy import boundary_fingerprint

    brief = json.loads(
        (project / ".skill-engineering/authoring-briefs/brief-demo.json").read_text()
    )
    path = project / ".skill-engineering/boundary-confirmations/brief-demo.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "schema_version": "1", "subject_id": "brief-demo",
        "boundary_fingerprint": boundary_fingerprint(brief), "status": status,
        "source": "explicit_cli_argument",
        "summary": "测试操作员确认此合成样本边界，不代表真实用户记录。",
        "excluded_decision": "listed" if brief["excluded_capabilities"] else "none",
        "behavior_policy": {
            "interaction": "single_turn", "uses_tools": False,
            "has_side_effects": False, "rationale": "仅处理已提供文本，无工具或外部动作。",
        },
    }, ensure_ascii=False))
    return path


def _preview(project: Path, candidate: Path, target: Path, plan: Path, *,
             confirmation: bool | Path = True):
    arguments = ["preview", "--project", project, "--brief-id", "brief-demo",
                 "--candidate", candidate, "--target", target, "--plan", plan, "--json"]
    if confirmation is not False:
        path = _write_confirmation(project) if confirmation is True else confirmation
        arguments += ["--boundary-confirmation", path]
    return _run(*arguments)


def test_preview_writes_plan_but_not_target(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    _write_brief(project)
    candidate = _write_candidate(tmp_path / "candidate")
    target = project / ".agents" / "skills" / "meeting-summary"
    plan = project / ".skill-engineering" / "native-plans" / "meeting.json"

    result = _preview(project, candidate, target, plan)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(plan.read_text(encoding="utf-8"))
    assert payload["content_status"] == "content_complete"
    assert payload["brief"]["id"] == "brief-demo"
    assert payload["candidate"]["files"]
    assert payload["creation_review"]["status"] == "pass"
    assert payload["behavior_tests"]["status"] == "passed"
    assert payload["behavior_tests"]["passed"] == 3
    assert not target.exists()


def test_preview_rejects_failed_behavior_case(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    _write_brief(project)
    brief_path = project / ".skill-engineering" / "authoring-briefs" / "brief-demo.json"
    brief = json.loads(brief_path.read_text(encoding="utf-8"))
    brief["behavior_cases"][0]["assertions"]["must_include"] = ["不存在的行为"]
    brief_path.write_text(json.dumps(brief, ensure_ascii=False), encoding="utf-8")
    candidate = _write_candidate(tmp_path / "candidate")
    target = project / ".agents" / "skills" / "meeting-summary"
    plan = tmp_path / "plan.json"

    result = _preview(project, candidate, target, plan)

    assert result.returncode != 0
    assert "行为案例" in result.stderr


def test_preview_rejects_raw_brief_path_and_loads_brief_id(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    brief = _write_brief(project)
    candidate = _write_candidate(tmp_path / "candidate")
    target = project / ".agents" / "skills" / "meeting-summary"
    plan = tmp_path / "plan.json"

    result = _run(
        "preview",
        "--project",
        project,
        "--brief",
        brief,
        "--candidate",
        candidate,
        "--target",
        target,
        "--plan",
        plan,
    )

    assert result.returncode == 2
    assert not plan.exists()


def test_preview_rejects_persisted_unsanitized_brief(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    brief = _write_brief(project)
    confirmation = _write_confirmation(project)
    payload = json.loads(brief.read_text(encoding="utf-8"))
    payload["goal"] = "同步 api_key=DEMO_SECRET_VALUE"
    brief.write_text(json.dumps(payload), encoding="utf-8")
    candidate = _write_candidate(tmp_path / "candidate")
    target = project / ".agents" / "skills" / "meeting-summary"
    plan = tmp_path / "plan.json"

    result = _preview(project, candidate, target, plan, confirmation=confirmation)

    assert result.returncode == 1
    assert "脱敏" in result.stderr
    assert not plan.exists()


def test_apply_rejects_candidate_drift(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    _write_brief(project)
    candidate = _write_candidate(tmp_path / "candidate")
    target = project / ".agents" / "skills" / "meeting-summary"
    target.parent.mkdir(parents=True)
    plan = tmp_path / "plan.json"
    assert _preview(project, candidate, target, plan).returncode == 0
    (candidate / "SKILL.md").write_text(SKILL_MD + "\n漂移\n", encoding="utf-8")

    result = _run("apply", "--plan", plan, "--candidate", candidate, "--target", target)

    assert result.returncode == 1
    assert "candidate" in result.stderr.lower()
    assert not target.exists()


def test_apply_rejects_brief_drift(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    brief = _write_brief(project)
    candidate = _write_candidate(tmp_path / "candidate")
    target = project / ".agents" / "skills" / "meeting-summary"
    target.parent.mkdir(parents=True)
    plan = tmp_path / "plan.json"
    assert _preview(project, candidate, target, plan).returncode == 0
    payload = json.loads(brief.read_text(encoding="utf-8"))
    payload["goal"] = "已经改变的目标"
    brief.write_text(json.dumps(payload), encoding="utf-8")

    result = _run("apply", "--plan", plan, "--candidate", candidate, "--target", target)

    assert result.returncode == 1
    assert "Brief" in result.stderr
    assert not target.exists()


def test_apply_rejects_target_drift_or_existing_target(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    _write_brief(project)
    candidate = _write_candidate(tmp_path / "candidate")
    target = project / ".agents" / "skills" / "meeting-summary"
    target.parent.mkdir(parents=True)
    plan = tmp_path / "plan.json"
    assert _preview(project, candidate, target, plan).returncode == 0
    target.mkdir()
    (target / "user-file.txt").write_text("keep", encoding="utf-8")

    result = _run("apply", "--plan", plan, "--candidate", candidate, "--target", target)

    assert result.returncode == 1
    assert (target / "user-file.txt").read_text(encoding="utf-8") == "keep"


def test_apply_rejects_plan_tamper(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    _write_brief(project)
    candidate = _write_candidate(tmp_path / "candidate")
    target = project / ".agents" / "skills" / "meeting-summary"
    target.parent.mkdir(parents=True)
    plan = tmp_path / "plan.json"
    assert _preview(project, candidate, target, plan).returncode == 0
    payload = json.loads(plan.read_text(encoding="utf-8"))
    payload["content_status"] = "scaffold_only"
    plan.write_text(json.dumps(payload), encoding="utf-8")

    result = _run("apply", "--plan", plan, "--candidate", candidate, "--target", target)

    assert result.returncode == 1
    assert "plan" in result.stderr.lower()
    assert not target.exists()


def test_apply_writes_exact_manifest_and_verify_passes(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    _write_brief(project)
    candidate = _write_candidate(tmp_path / "candidate")
    target = project / ".agents" / "skills" / "meeting-summary"
    target.parent.mkdir(parents=True)
    plan = tmp_path / "plan.json"
    assert _preview(project, candidate, target, plan).returncode == 0

    apply_result = _run(
        "apply", "--plan", plan, "--candidate", candidate, "--target", target, "--json"
    )
    verify_result = _run("verify", "--plan", plan, "--target", target, "--json")

    assert apply_result.returncode == 0, apply_result.stdout + apply_result.stderr
    assert verify_result.returncode == 0, verify_result.stdout + verify_result.stderr
    assert json.loads(verify_result.stdout)["status"] == "verified"
    expected = json.loads(plan.read_text(encoding="utf-8"))["candidate"]["files"]
    actual_paths = sorted(
        item.relative_to(target).as_posix()
        for item in target.rglob("*")
        if item.is_file()
    )
    assert actual_paths == [item["path"] for item in expected]


def test_apply_failure_cleans_only_unique_temporary_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    project = tmp_path / "project"
    project.mkdir()
    _write_brief(project)
    candidate = _write_candidate(tmp_path / "candidate")
    target = project / ".agents" / "skills" / "meeting-summary"
    target.parent.mkdir(parents=True)
    plan = tmp_path / "plan.json"
    assert _preview(project, candidate, target, plan).returncode == 0
    unrelated = target.parent / ".meeting-summary.skill-plan-user"
    unrelated.mkdir()

    spec = importlib.util.spec_from_file_location("native_plan_under_test", NATIVE_PLAN)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def fail_copy(*_args, **_kwargs):
        raise OSError("simulated copy failure")

    monkeypatch.setattr(module.shutil, "copytree", fail_copy)
    with pytest.raises(module.PlanError, match="copy failure"):
        module.apply_plan(plan, candidate, target)

    assert unrelated.is_dir()
    assert not [
        item
        for item in target.parent.iterdir()
        if item.name.startswith(".meeting-summary.skill-plan-") and item != unrelated
    ]

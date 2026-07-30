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


def _preview(project: Path, candidate: Path, target: Path, plan: Path):
    return _run(
        "preview",
        "--project",
        project,
        "--brief-id",
        "brief-demo",
        "--candidate",
        candidate,
        "--target",
        target,
        "--plan",
        plan,
        "--json",
    )


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
    assert not target.exists()


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
    payload = json.loads(brief.read_text(encoding="utf-8"))
    payload["goal"] = "同步 api_key=DEMO_SECRET_VALUE"
    brief.write_text(json.dumps(payload), encoding="utf-8")
    candidate = _write_candidate(tmp_path / "candidate")
    target = project / ".agents" / "skills" / "meeting-summary"
    plan = tmp_path / "plan.json"

    result = _preview(project, candidate, target, plan)

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

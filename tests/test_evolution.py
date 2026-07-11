from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from skill_engineering.evaluation import load_evaluation_suite
from skill_engineering.evolution import (
    apply_release_plan,
    build_dataset,
    create_release_plan,
    prepare_candidates,
    propose_evolution,
    record_run,
    register_candidate,
    rollback_release,
    select_candidates,
    submit_results,
    verify_release,
    version_candidate,
)


def skill_text(description: str = "用于处理明确的演示任务。") -> str:
    return f"---\nname: demo-skill\ndescription: {description}\n---\n\n# Demo\n\n按输入完成任务。\n"


@pytest.fixture()
def env(tmp_path: Path) -> dict[str, Path]:
    root = tmp_path / "hub"
    skill = tmp_path / "demo-skill"
    project = tmp_path / "canary-project"
    root.mkdir()
    skill.mkdir()
    project.mkdir()
    (skill / "SKILL.md").write_text(skill_text(), encoding="utf-8")
    (root / "profiles").mkdir()
    (root / "adapters").mkdir()
    (root / "registry.yaml").write_text("skills: {}\n", encoding="utf-8")
    (root / "adapters" / "codex.yaml").write_text(
        "name: codex\nentrypoint: .agents/skills\n", encoding="utf-8"
    )
    (root / "adapters" / "claude-code.yaml").write_text(
        "name: claude-code\nentrypoint: .claude/skills\n", encoding="utf-8"
    )
    return {"root": root, "skill": skill, "project": project}


def write_run(
    env: dict[str, Path],
    name: str,
    *,
    outcome: str,
    tag: str = "route-miss",
    leakage_group: str | None = None,
    expected: dict | None = None,
    high_risk: bool = False,
    privacy: str = "internal",
    task_summary: str | None = None,
) -> Path:
    path = env["root"].parent / f"{name}.json"
    payload = {
        "id": name,
        "skill_path": str(env["skill"]),
        "task_summary": task_summary or f"任务 {name}",
        "result_summary": "运行结果摘要",
        "outcome": outcome,
        "failure_tags": [] if outcome == "success" else [tag],
        "user_correction": "只有明确请求时才触发" if outcome != "success" else "",
        "expected": expected or {"status": "completed", "contains": [name]},
        "high_risk": high_risk,
        "privacy": privacy,
        "source": "test-harness",
        "leakage_group": leakage_group or f"group-{name}",
    }
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def prepare_proposal(env: dict[str, Path]):
    record_run(env["root"], write_run(env, "success-1", outcome="success"))
    for index in range(3):
        record_run(env["root"], write_run(env, f"failure-{index}", outcome="failure"))
    return propose_evolution(env["root"], env["skill"])


def write_results(
    root: Path,
    suite_path: Path,
    name: str,
    *,
    pass_all: bool,
    fingerprint: str,
) -> Path:
    suite = yaml.safe_load(suite_path.read_text(encoding="utf-8"))
    runs = {}
    for index, case in enumerate(suite["cases"]):
        expected = case["expected"]
        status = expected.get("status", "completed")
        output = " ".join(expected.get("contains") or [])
        if not pass_all and index == 0:
            status = "failed" if status != "failed" else "completed"
            output = "baseline miss"
        runs[case["id"]] = {
            "status": status,
            "output": output,
            "duration_ms": 10 + index,
        }
    path = root.parent / f"{name}.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "suite_id": suite["id"],
                "subject": name,
                "subject_fingerprint": fingerprint,
                "runs": runs,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def validated_candidate(env: dict[str, Path], *, description: str = "用于修复明确触发任务。"):
    proposal = prepare_proposal(env)
    dataset = build_dataset(env["root"], proposal.id)
    job = prepare_candidates(env["root"], proposal.id)[0]
    (Path(job.source_path) / "SKILL.md").write_text(skill_text(description), encoding="utf-8")
    registered = register_candidate(env["root"], job.id)
    baseline = write_results(
        env["root"],
        Path(dataset.suite_path),
        "baseline",
        pass_all=False,
        fingerprint=proposal.baseline_fingerprint,
    )
    candidate = write_results(
        env["root"],
        Path(dataset.suite_path),
        "candidate",
        pass_all=True,
        fingerprint=registered.source_fingerprint,
    )
    submit_results(env["root"], registered.id, baseline, candidate)
    selected = select_candidates(env["root"], proposal.id)
    return proposal, dataset, selected[0]


def test_record_run_rejects_credentials_and_redacts_sensitive_summary(env):
    secret = write_run(
        env,
        "secret-run",
        outcome="failure",
        task_summary="api_key=abcdefgh12345678",
    )
    with pytest.raises(SystemExit, match="凭证"):
        record_run(env["root"], secret)

    sensitive = write_run(
        env,
        "sensitive-run",
        outcome="failure",
        privacy="sensitive",
        expected={},
        task_summary="客户隐私任务",
    )
    payload = json.loads(sensitive.read_text(encoding="utf-8"))
    payload["expected"] = {}
    sensitive.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    run = record_run(env["root"], sensitive)
    assert run.task_summary == "[sensitive evidence redacted]"
    assert run.result_summary == "[sensitive evidence redacted]"


def test_proposal_requires_threshold_and_high_risk_can_trigger_immediately(env):
    for index in range(2):
        record_run(env["root"], write_run(env, f"failure-{index}", outcome="failure"))
    with pytest.raises(SystemExit, match="observe"):
        propose_evolution(env["root"], env["skill"])

    record_run(
        env["root"],
        write_run(env, "high-risk", outcome="failure", tag="approval-bypass", high_risk=True),
    )
    proposal = propose_evolution(env["root"], env["skill"])
    assert proposal.risk_level == "high"
    assert proposal.root_cause_layer == "state"


def test_dataset_keeps_leakage_groups_together_and_requires_two_groups(env):
    proposal = prepare_proposal(env)
    dataset = build_dataset(env["root"], proposal.id)
    assert dataset.development_case_ids
    assert dataset.holdout_case_ids
    assert set(dataset.leakage_groups.values()) == {"development", "holdout"}

    isolated_env = {
        "root": env["root"].parent / "isolated-hub",
        "skill": env["skill"],
        "project": env["project"],
    }
    isolated_env["root"].mkdir()
    for index in range(3):
        record_run(
            isolated_env["root"],
            write_run(
                isolated_env,
                f"same-{index}",
                outcome="failure",
                leakage_group="same-source",
            ),
        )
    isolated_proposal = propose_evolution(isolated_env["root"], env["skill"])
    with pytest.raises(SystemExit, match="leakage_group"):
        build_dataset(isolated_env["root"], isolated_proposal.id)


def test_high_risk_dataset_uses_evaluator_category_schema(env):
    record_run(env["root"], write_run(env, "success", outcome="success"))
    for index in range(3):
        record_run(
            env["root"],
            write_run(
                env,
                f"risk-{index}",
                outcome="failure",
                tag="approval-bypass",
                high_risk=index == 0,
            ),
        )
    proposal = propose_evolution(env["root"], env["skill"])
    dataset = build_dataset(env["root"], proposal.id)
    suite, _ = load_evaluation_suite(Path(dataset.suite_path), production=False)

    assert any(case.category == "high_risk" for case in suite.cases)


def test_candidate_jobs_are_isolated_and_brief_does_not_expose_holdout(env):
    proposal = prepare_proposal(env)
    dataset = build_dataset(env["root"], proposal.id)
    jobs = prepare_candidates(env["root"], proposal.id)
    assert {job.strategy for job in jobs} == {
        "minimal-patch",
        "layer-move",
        "compaction",
        "resource-or-script",
    }
    for job in jobs:
        assert Path(job.source_path).is_dir()
        brief = Path(job.generation_brief_path).read_text(encoding="utf-8")
        assert dataset.suite_path not in brief
        assert "holdout_case_ids" not in brief

    outside = env["root"].parent / "outside-candidate"
    outside.mkdir()
    (outside / "SKILL.md").write_text(skill_text(), encoding="utf-8")
    with pytest.raises(SystemExit, match="隔离工作区"):
        register_candidate(env["root"], jobs[0].id, outside)


def test_evaluation_pareto_selection_and_immutable_shadow_version(env):
    proposal = prepare_proposal(env)
    dataset = build_dataset(env["root"], proposal.id)
    jobs = prepare_candidates(env["root"], proposal.id)[:2]
    baseline = write_results(
        env["root"],
        Path(dataset.suite_path),
        "baseline",
        pass_all=False,
        fingerprint=proposal.baseline_fingerprint,
    )
    compact = register_candidate(env["root"], jobs[0].id)
    verbose_path = Path(jobs[1].source_path) / "SKILL.md"
    verbose_path.write_text(
        skill_text() + "\n".join(f"附加说明 {index}" for index in range(8)),
        encoding="utf-8",
    )
    verbose = register_candidate(env["root"], jobs[1].id)
    candidate_results = write_results(
        env["root"],
        Path(dataset.suite_path),
        "candidate",
        pass_all=True,
        fingerprint=compact.source_fingerprint,
    )
    compact_result = submit_results(
        env["root"], compact.id, baseline, candidate_results, candidate_cost=0.25
    )
    verbose_results = write_results(
        env["root"],
        Path(dataset.suite_path),
        "verbose-candidate",
        pass_all=True,
        fingerprint=verbose.source_fingerprint,
    )
    submit_results(env["root"], verbose.id, baseline, verbose_results, candidate_cost=0.5)
    assert compact_result.fitness["cost"] == 0.25
    assert compact_result.fitness["latency_ms"] > 0

    winners = select_candidates(env["root"], proposal.id)
    assert [item.id for item in winners] == [compact.id]
    version = version_candidate(env["root"], compact.id, "1.1.0-a3")
    snapshot = (Path(version.source_path) / "SKILL.md").read_text(encoding="utf-8")
    (Path(compact.source_path) / "SKILL.md").write_text(
        skill_text("候选后来被修改。"), encoding="utf-8"
    )
    assert (Path(version.source_path) / "SKILL.md").read_text(encoding="utf-8") == snapshot
    shadow = (
        env["root"] / ".skill-engineering" / "evolution" / "channels" / "demo-skill" / "shadow.json"
    )
    assert json.loads(shadow.read_text(encoding="utf-8"))["version_id"] == version.id


def test_submit_results_rejects_subject_fingerprint_mismatch(env):
    proposal = prepare_proposal(env)
    dataset = build_dataset(env["root"], proposal.id)
    job = register_candidate(env["root"], prepare_candidates(env["root"], proposal.id)[0].id)
    baseline = write_results(
        env["root"],
        Path(dataset.suite_path),
        "baseline",
        pass_all=False,
        fingerprint=proposal.baseline_fingerprint,
    )
    candidate = write_results(
        env["root"],
        Path(dataset.suite_path),
        "candidate",
        pass_all=True,
        fingerprint="a-different-candidate",
    )

    with pytest.raises(SystemExit, match="candidate results 指纹"):
        submit_results(env["root"], job.id, baseline, candidate)


def test_active_release_requires_approval_verifies_and_rolls_back(env):
    _, _, candidate = validated_candidate(env)
    version = version_candidate(env["root"], candidate.id, "2.0.0")
    before = (env["skill"] / "SKILL.md").read_text(encoding="utf-8")
    plan = create_release_plan(env["root"], version.id, "active", active_source=env["skill"])
    with pytest.raises(SystemExit, match="批准"):
        apply_release_plan(env["root"], plan.id, approved=False)

    record = apply_release_plan(env["root"], plan.id, approved=True)
    assert record.verification["status"] == "passed"
    assert "用于修复明确触发任务" in (env["skill"] / "SKILL.md").read_text(encoding="utf-8")
    assert verify_release(env["root"], record.id).verification["status"] == "passed"
    with pytest.raises(SystemExit, match="不能重复应用"):
        apply_release_plan(env["root"], plan.id, approved=True)

    rolled_back = rollback_release(env["root"], record.id)
    assert rolled_back.status == "rolled-back"
    assert (env["skill"] / "SKILL.md").read_text(encoding="utf-8") == before


def test_canary_release_installs_version_and_rollback_removes_it(env):
    _, _, candidate = validated_candidate(env)
    version = version_candidate(env["root"], candidate.id, "2.0.0-canary")
    plan = create_release_plan(env["root"], version.id, "canary", project=env["project"])
    record = apply_release_plan(env["root"], plan.id, approved=True)
    codex_link = env["project"] / ".agents" / "skills" / "demo-skill"
    claude_link = env["project"] / ".claude" / "skills" / "demo-skill"
    assert record.verification["status"] == "passed"
    assert codex_link.is_symlink() and claude_link.is_symlink()

    rollback_release(env["root"], record.id)
    assert not codex_link.exists() and not claude_link.exists()


def test_release_plan_rejects_source_drift(env):
    _, _, candidate = validated_candidate(env)
    version = version_candidate(env["root"], candidate.id, "3.0.0")
    plan = create_release_plan(env["root"], version.id, "active", active_source=env["skill"])
    (env["skill"] / "SKILL.md").write_text(skill_text("人工并发修改。"), encoding="utf-8")
    with pytest.raises(SystemExit, match="Active source 已漂移"):
        apply_release_plan(env["root"], plan.id, approved=True)

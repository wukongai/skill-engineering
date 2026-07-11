"""Provider-neutral A3 skill evolution and release orchestration."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, TypeVar

import yaml

from .evaluation import evaluate_behavior, load_behavior_results, load_evaluation_suite
from .release_installer import (
    apply_install_plan,
    create_install_plan,
    undo_change_record,
    verify_change_record,
)
from .journey import (
    SCHEMA_VERSION,
    fingerprint_path,
    load_build_plan,
    local_state_root,
    new_id,
    now_iso,
    payload_hash,
)
from .maintenance import (
    apply_improvement_plan,
    complexity_metrics,
    create_improvement_plan,
    undo_improvement,
    verify_improvement,
)
from .skill_doctor import doctor_skill
from .skill_lint import lint_skill


SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|access[_-]?token|refresh[_-]?token|password|secret|private[_-]?key)\s*[:=]\s*\S{8,}"
)
VALID_OUTCOMES = {"success", "partial", "failure"}
VALID_PRIVACY = {"public", "internal", "sensitive"}
STRATEGIES = ("minimal-patch", "layer-move", "compaction", "resource-or-script")


@dataclass
class SkillRun:
    id: str
    skill_path: str
    skill_fingerprint: str
    task_summary: str
    result_summary: str
    outcome: str
    failure_tags: list[str]
    user_correction: str
    expected: dict[str, Any]
    high_risk: bool
    privacy: str
    source: str
    leakage_group: str
    cost: float | None = None
    latency_ms: int | None = None
    schema_version: str = SCHEMA_VERSION
    created_at: str = field(default_factory=now_iso)


@dataclass
class EvolutionProposal:
    id: str
    skill_path: str
    baseline_fingerprint: str
    evidence_ids: list[str]
    failure_mode: str
    confidence: str
    root_cause_layer: str
    expected_behavior: str
    protected_behaviors: list[str]
    strategies: list[str]
    risk_level: str
    status: str
    dataset_id: str | None = None
    recommended_candidate_ids: list[str] = field(default_factory=list)
    schema_version: str = SCHEMA_VERSION
    created_at: str = field(default_factory=now_iso)


@dataclass
class EvolutionDataset:
    id: str
    proposal_id: str
    suite_path: str
    evidence_ids: list[str]
    development_case_ids: list[str]
    holdout_case_ids: list[str]
    high_risk_case_ids: list[str]
    leakage_groups: dict[str, str]
    schema_version: str = SCHEMA_VERSION
    created_at: str = field(default_factory=now_iso)


@dataclass
class CandidateJob:
    id: str
    proposal_id: str
    strategy: str
    workspace: str
    source_path: str
    baseline_fingerprint: str
    generation_brief_path: str
    status: str
    source_fingerprint: str = ""
    gate: dict[str, Any] = field(default_factory=dict)
    complexity: dict[str, Any] = field(default_factory=dict)
    evaluation_report: dict[str, Any] = field(default_factory=dict)
    fitness: dict[str, Any] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION
    created_at: str = field(default_factory=now_iso)


@dataclass
class SkillVersion:
    id: str
    skill_key: str
    label: str
    source_path: str
    source_fingerprint: str
    parent_fingerprint: str
    candidate_id: str
    proposal_id: str
    evaluation_report_id: str
    lifecycle: str
    schema_version: str = SCHEMA_VERSION
    created_at: str = field(default_factory=now_iso)


@dataclass
class ReleasePlan:
    id: str
    version_id: str
    channel: str
    project: str | None
    active_source: str | None
    before_version_id: str | None
    version_fingerprint: str
    target_fingerprint: str
    child_plan_id: str | None
    plan_hash: str
    approval: dict[str, Any]
    status: str
    schema_version: str = SCHEMA_VERSION
    created_at: str = field(default_factory=now_iso)


@dataclass
class ReleaseRecord:
    id: str
    plan_id: str
    version_id: str
    channel: str
    before_version_id: str | None
    child_record_id: str | None
    status: str
    verification: dict[str, Any]
    rollback_available: bool
    rolled_back_at: str | None = None
    schema_version: str = SCHEMA_VERSION
    created_at: str = field(default_factory=now_iso)


T = TypeVar("T")


def _state_root(root: Path) -> Path:
    return local_state_root(root) / "evolution"


def _validate_id(value: str) -> None:
    if not SAFE_ID_RE.fullmatch(value):
        raise SystemExit(f"Evolution id 格式无效:{value}")


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def _save(root: Path, folder: str, identifier: str, value: Any) -> Path:
    _validate_id(identifier)
    path = _state_root(root) / folder / f"{identifier}.json"
    _atomic_json(path, asdict(value))
    return path


def _load(root: Path, folder: str, identifier: str, cls: type[T]) -> T:
    _validate_id(identifier)
    path = _state_root(root) / folder / f"{identifier}.json"
    if not path.is_file():
        raise SystemExit(f"Evolution state 不存在:{path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Evolution state 无法读取:{path}\n{exc}") from exc
    if not isinstance(data, dict) or str(data.get("schema_version")) != SCHEMA_VERSION:
        raise SystemExit(f"Evolution state schema 无效:{path}")
    return cls(**data)


def _list(root: Path, folder: str, cls: type[T]) -> list[T]:
    directory = _state_root(root) / folder
    if not directory.is_dir():
        return []
    values: list[T] = []
    for path in sorted(directory.glob("*.json"), reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            values.append(cls(**data))
        except (OSError, json.JSONDecodeError, TypeError):
            continue
    return values


def _slug(path: Path) -> str:
    value = re.sub(r"[^a-z0-9-]+", "-", path.name.lower()).strip("-")
    return value or "skill"


def _safe_summary(value: Any, label: str, *, privacy: str) -> str:
    text = str(value or "").strip()
    if len(text) > 1000:
        raise SystemExit(f"{label} 过长;只保存脱敏摘要和 artifact pointer。")
    if SECRET_RE.search(text):
        raise SystemExit(f"{label} 疑似包含凭证,拒绝写入 evolution state。")
    if privacy == "sensitive" and text:
        return "[sensitive evidence redacted]"
    return text


def _read_mapping(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"输入 JSON 无法读取:{path}\n{exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"输入必须是 JSON object:{path}")
    return data


def record_run(root: Path, input_path: Path) -> SkillRun:
    data = _read_mapping(input_path)
    skill_path = Path(str(data.get("skill_path") or "")).expanduser().resolve()
    if not (skill_path / "SKILL.md").is_file():
        raise SystemExit(f"SkillRun.skill_path 不是有效 Skill:{skill_path}")
    outcome = str(data.get("outcome") or "")
    privacy = str(data.get("privacy") or "internal")
    if outcome not in VALID_OUTCOMES:
        raise SystemExit(f"SkillRun.outcome 无效:{outcome}")
    if privacy not in VALID_PRIVACY:
        raise SystemExit(f"SkillRun.privacy 无效:{privacy}")
    tags = data.get("failure_tags") or []
    expected = data.get("expected") or {}
    if not isinstance(tags, list) or not all(
        isinstance(item, str) and item.strip() for item in tags
    ):
        raise SystemExit("SkillRun.failure_tags 必须是非空字符串数组或空数组。")
    if not isinstance(expected, dict):
        raise SystemExit("SkillRun.expected 必须是确定性断言 object。")
    if privacy == "sensitive" and expected:
        raise SystemExit("sensitive run 不得把 expected 内容写入 evolution state。")
    if SECRET_RE.search(json.dumps(expected, ensure_ascii=False)):
        raise SystemExit("SkillRun.expected 疑似包含凭证,拒绝写入 evolution state。")
    task_summary = _safe_summary(data.get("task_summary"), "task_summary", privacy=privacy)
    correction = _safe_summary(data.get("user_correction"), "user_correction", privacy=privacy)
    result_summary = _safe_summary(data.get("result_summary"), "result_summary", privacy=privacy)
    run = SkillRun(
        id=str(data.get("id") or new_id("run")),
        skill_path=str(skill_path),
        skill_fingerprint=fingerprint_path(skill_path),
        task_summary=task_summary,
        result_summary=result_summary,
        outcome=outcome,
        failure_tags=sorted(set(tags)),
        user_correction=correction,
        expected=expected,
        high_risk=bool(data.get("high_risk", False)),
        privacy=privacy,
        source=str(data.get("source") or "manual"),
        leakage_group=str(
            data.get("leakage_group") or hashlib.sha256(task_summary.encode()).hexdigest()[:12]
        ),
        cost=float(data["cost"]) if data.get("cost") is not None else None,
        latency_ms=int(data["latency_ms"]) if data.get("latency_ms") is not None else None,
    )
    _save(root, "runs", run.id, run)
    return run


def _root_cause(tag: str) -> str:
    lower = tag.lower()
    if any(term in lower for term in ("route", "trigger", "误触发", "漏触发")):
        return "trigger"
    if any(term in lower for term in ("tool", "script", "脚本", "路径", "日期")):
        return "script"
    if any(term in lower for term in ("approval", "state", "确认", "状态")):
        return "state"
    if any(term in lower for term in ("style", "tone", "风格")):
        return "style"
    if any(term in lower for term in ("install", "global", "profile", "安装")):
        return "install"
    return "interface"


def propose_evolution(root: Path, skill_path: Path, *, force: bool = False) -> EvolutionProposal:
    skill_path = skill_path.expanduser().resolve()
    runs = [run for run in _list(root, "runs", SkillRun) if Path(run.skill_path) == skill_path]
    evidence = [
        run for run in runs if run.outcome != "success" or run.user_correction or run.high_risk
    ]
    counts: dict[str, list[SkillRun]] = {}
    for run in evidence:
        for tag in run.failure_tags or ["unclassified"]:
            counts.setdefault(tag, []).append(run)
    if not counts:
        raise SystemExit("没有可形成进化提案的失败或纠正证据。")
    tag, clustered = max(
        counts.items(),
        key=lambda item: (any(run.high_risk for run in item[1]), len(item[1])),
    )
    threshold_met = len(clustered) >= 3 or any(run.high_risk for run in clustered)
    if not force and not threshold_met:
        raise SystemExit(
            f"进化信号仍处于 observe:同类证据 {len(clustered)} 条,需要 3 条或 1 条 high-risk。"
        )
    corrections = [run.user_correction for run in clustered if run.user_correction]
    expected_behavior = corrections[-1] if corrections else f"修复 {tag} 且不破坏既有成功行为。"
    risk = "high" if any(run.high_risk for run in clustered) else "normal"
    protected_successes = [run for run in runs if run.outcome == "success" and run.expected][-20:]
    evidence_ids = list(dict.fromkeys([run.id for run in clustered + protected_successes]))
    proposal = EvolutionProposal(
        id=new_id("evolution"),
        skill_path=str(skill_path),
        baseline_fingerprint=fingerprint_path(skill_path),
        evidence_ids=evidence_ids,
        failure_mode=tag,
        confidence="high" if len(clustered) >= 3 or risk == "high" else "medium",
        root_cause_layer=_root_cause(tag),
        expected_behavior=expected_behavior,
        protected_behaviors=[
            "已有 success case 不得退化",
            "high-risk 边界必须保持通过",
        ],
        strategies=list(STRATEGIES),
        risk_level=risk,
        status="proposed",
    )
    _save(root, "proposals", proposal.id, proposal)
    return proposal


def _case_id(run: SkillRun) -> str:
    return f"case-{run.id}"[:128]


def build_dataset(root: Path, proposal_id: str) -> EvolutionDataset:
    proposal = _load(root, "proposals", proposal_id, EvolutionProposal)
    runs_by_id = {run.id: run for run in _list(root, "runs", SkillRun)}
    runs = [
        runs_by_id[item]
        for item in proposal.evidence_ids
        if item in runs_by_id and runs_by_id[item].expected
    ]
    if not runs:
        raise SystemExit("提案证据没有确定性 expected assertions,不能伪装成可评分数据集。")
    groups: dict[str, list[SkillRun]] = {}
    for run in runs:
        groups.setdefault(run.leakage_group, []).append(run)
    if len(groups) < 2:
        raise SystemExit("评测集至少需要两个独立 leakage_group,才能隔离 development 与 holdout。")
    group_splits: dict[str, str] = {}
    for index, group in enumerate(sorted(groups)):
        group_splits[group] = (
            "holdout"
            if any(run.high_risk for run in groups[group]) or index % 4 == 3
            else "development"
        )
    if len(groups) > 1 and "holdout" not in group_splits.values():
        group_splits[sorted(groups)[-1]] = "holdout"
    if "development" not in group_splits.values():
        group_splits[sorted(groups)[0]] = "development"
    cases: list[dict[str, Any]] = []
    for run in runs:
        category = (
            "high_risk" if run.high_risk else ("success" if run.outcome == "success" else "failure")
        )
        cases.append(
            {
                "id": _case_id(run),
                "split": group_splits[run.leakage_group],
                "category": category,
                "expected": run.expected,
            }
        )
    dataset_id = new_id("dataset")
    suite_path = _state_root(root) / "datasets" / f"{dataset_id}.yaml"
    suite_path.parent.mkdir(parents=True, exist_ok=True)
    suite = {
        "schema_version": SCHEMA_VERSION,
        "id": dataset_id,
        "cases": cases,
        "gates": {
            "min_candidate_pass_rate": 1.0,
            "min_holdout_pass_rate": 1.0,
            "min_high_risk_pass_rate": 1.0,
            "max_negative_transfer": 0,
            "min_delta": 0.0,
        },
    }
    suite_path.write_text(
        yaml.safe_dump(suite, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    dataset = EvolutionDataset(
        id=dataset_id,
        proposal_id=proposal.id,
        suite_path=str(suite_path),
        evidence_ids=[run.id for run in runs],
        development_case_ids=[
            _case_id(run) for run in runs if group_splits[run.leakage_group] == "development"
        ],
        holdout_case_ids=[
            _case_id(run) for run in runs if group_splits[run.leakage_group] == "holdout"
        ],
        high_risk_case_ids=[_case_id(run) for run in runs if run.high_risk],
        leakage_groups=group_splits,
    )
    proposal.dataset_id = dataset.id
    proposal.status = "dataset-ready"
    _save(root, "datasets-meta", dataset.id, dataset)
    _save(root, "proposals", proposal.id, proposal)
    return dataset


def prepare_candidates(root: Path, proposal_id: str) -> list[CandidateJob]:
    proposal = _load(root, "proposals", proposal_id, EvolutionProposal)
    if not proposal.dataset_id:
        raise SystemExit("先为 Evolution Proposal 构建评测集。")
    dataset = _load(root, "datasets-meta", proposal.dataset_id, EvolutionDataset)
    development_case_ids = set(dataset.development_case_ids)
    development_runs = [
        run
        for run in _list(root, "runs", SkillRun)
        if _case_id(run) in development_case_ids and run.privacy != "sensitive"
    ]
    skill_path = Path(proposal.skill_path)
    if fingerprint_path(skill_path) != proposal.baseline_fingerprint:
        raise SystemExit("baseline Skill 已漂移,请重新生成 Evolution Proposal。")
    jobs: list[CandidateJob] = []
    for strategy in proposal.strategies:
        job_id = new_id(f"candidate-{strategy}")
        workspace = _state_root(root) / "workspaces" / proposal.id / job_id
        source_path = workspace / "source"
        shutil.copytree(
            skill_path,
            source_path,
            symlinks=True,
            ignore=shutil.ignore_patterns(".git", ".skill-engineering"),
        )
        brief = {
            "schema_version": SCHEMA_VERSION,
            "job_id": job_id,
            "proposal_id": proposal.id,
            "strategy": strategy,
            "failure_mode": proposal.failure_mode,
            "root_cause_layer": proposal.root_cause_layer,
            "expected_behavior": proposal.expected_behavior,
            "protected_behaviors": proposal.protected_behaviors,
            "development_evidence": [
                {
                    "run_id": run.id,
                    "task_summary": run.task_summary,
                    "result_summary": run.result_summary,
                    "outcome": run.outcome,
                    "failure_tags": run.failure_tags,
                    "user_correction": run.user_correction,
                    "expected": run.expected,
                }
                for run in development_runs
            ],
            "constraints": [
                "只能修改 source/ 内候选,不得修改 baseline/active source。",
                "不得读取 baseline 评分结果或 holdout expected assertions。",
                "修复应落到最低可执行层,不要追加事故式禁令。",
            ],
        }
        brief_path = workspace / "candidate-job.json"
        _atomic_json(brief_path, brief)
        job = CandidateJob(
            id=job_id,
            proposal_id=proposal.id,
            strategy=strategy,
            workspace=str(workspace),
            source_path=str(source_path),
            baseline_fingerprint=proposal.baseline_fingerprint,
            generation_brief_path=str(brief_path),
            status="prepared",
        )
        _save(root, "candidates", job.id, job)
        jobs.append(job)
    proposal.status = "candidates-prepared"
    _save(root, "proposals", proposal.id, proposal)
    return jobs


def register_candidate(root: Path, job_id: str, source_path: Path | None = None) -> CandidateJob:
    job = _load(root, "candidates", job_id, CandidateJob)
    source = (source_path or Path(job.source_path)).expanduser().resolve()
    workspace = Path(job.workspace).resolve()
    if not source.is_relative_to(workspace):
        raise SystemExit("候选 source 必须位于 CandidateJob 隔离工作区内。")
    proposal = _load(root, "proposals", job.proposal_id, EvolutionProposal)
    if not (source / "SKILL.md").is_file():
        raise SystemExit(f"候选不是有效 Skill:{source}")
    lint = lint_skill(source)
    doctor = doctor_skill(source, profile="team")
    before = complexity_metrics(Path(proposal.skill_path))
    after = complexity_metrics(source)
    gate_status = "pass" if lint.error_count == 0 and doctor.fail_count == 0 else "blocked"
    job.source_path = str(source)
    job.source_fingerprint = fingerprint_path(source)
    job.gate = {
        "status": gate_status,
        "lint_errors": lint.error_count,
        "lint_warnings": lint.warn_count,
        "doctor_fails": doctor.fail_count,
        "doctor_warnings": doctor.warn_count,
        "score": doctor.score.total if doctor.score else None,
    }
    job.complexity = {
        "before": before,
        "after": after,
        "delta": {key: after[key] - before[key] for key in before},
    }
    job.status = "generated" if gate_status == "pass" else "rejected"
    _save(root, "candidates", job.id, job)
    return job


def submit_results(
    root: Path,
    candidate_id: str,
    baseline_results: Path,
    candidate_results: Path,
    *,
    candidate_cost: float | None = None,
) -> CandidateJob:
    if candidate_cost is not None and (not math.isfinite(candidate_cost) or candidate_cost < 0):
        raise SystemExit("candidate cost 必须是非负有限数。")
    job = _load(root, "candidates", candidate_id, CandidateJob)
    if job.status != "generated" or job.gate.get("status") != "pass":
        raise SystemExit("候选尚未通过结构/安全门禁。")
    proposal = _load(root, "proposals", job.proposal_id, EvolutionProposal)
    dataset = _load(root, "datasets-meta", str(proposal.dataset_id), EvolutionDataset)
    if fingerprint_path(Path(job.source_path)) != job.source_fingerprint:
        raise SystemExit("候选 source 已漂移,请重新登记。")
    suite, _ = load_evaluation_suite(Path(dataset.suite_path), production=False)
    baseline_runs, _ = load_behavior_results(baseline_results, suite)
    candidate_runs, _ = load_behavior_results(candidate_results, suite)
    if baseline_runs.subject_fingerprint != proposal.baseline_fingerprint:
        raise SystemExit("baseline results 指纹与 Proposal baseline 不匹配。")
    if candidate_runs.subject_fingerprint != job.source_fingerprint:
        raise SystemExit("candidate results 指纹与候选 source 不匹配。")
    report = evaluate_behavior(
        root,
        Path(dataset.suite_path),
        baseline_results,
        candidate_results,
        production=False,
    )
    durations = [
        run.duration_ms for run in candidate_runs.runs.values() if run.duration_ms is not None
    ]
    latency_ms = round(sum(durations) / len(durations), 3) if durations else None
    candidate_metrics = report.metrics["candidate"]
    job.evaluation_report = asdict(report)
    job.fitness = {
        "utility_delta": report.metrics.get("delta"),
        "holdout_pass_rate": candidate_metrics["holdout"]["pass_rate"],
        "high_risk_pass_rate": candidate_metrics["high_risk"]["pass_rate"],
        "negative_transfer": len(report.negative_transfer),
        "cost": candidate_cost,
        "latency_ms": latency_ms,
        "skill_md_lines": job.complexity["after"]["skill_md_lines"],
        "duplicate_instruction_lines": job.complexity["after"]["duplicate_instruction_lines"],
        "total_files": job.complexity["after"]["total_files"],
    }
    job.status = "validated" if report.decision == "accept" else "rejected"
    _save(root, "candidates", job.id, job)
    return job


def _dominates(left: CandidateJob, right: CandidateJob) -> bool:
    higher = ("utility_delta", "holdout_pass_rate", "high_risk_pass_rate")
    lower = (
        "negative_transfer",
        "cost",
        "latency_ms",
        "skill_md_lines",
        "duplicate_instruction_lines",
        "total_files",
    )

    higher_pairs = [
        (float(left.fitness[key]), float(right.fitness[key]))
        for key in higher
        if left.fitness.get(key) is not None and right.fitness.get(key) is not None
    ]
    lower_pairs = [
        (float(left.fitness[key]), float(right.fitness[key]))
        for key in lower
        if left.fitness.get(key) is not None and right.fitness.get(key) is not None
    ]
    no_worse = all(left_value >= right_value for left_value, right_value in higher_pairs)
    no_worse = no_worse and all(
        left_value <= right_value for left_value, right_value in lower_pairs
    )
    strictly = any(left_value > right_value for left_value, right_value in higher_pairs) or any(
        left_value < right_value for left_value, right_value in lower_pairs
    )
    return no_worse and strictly


def select_candidates(root: Path, proposal_id: str) -> list[CandidateJob]:
    proposal = _load(root, "proposals", proposal_id, EvolutionProposal)
    candidates = [
        job
        for job in _list(root, "candidates", CandidateJob)
        if job.proposal_id == proposal_id and job.status == "validated"
    ]
    if not candidates:
        raise SystemExit("没有通过全部门禁的 validated candidate。")
    winners = [
        candidate
        for candidate in candidates
        if not any(_dominates(other, candidate) for other in candidates if other.id != candidate.id)
    ]
    for candidate in winners:
        candidate.status = "recommended"
        _save(root, "candidates", candidate.id, candidate)
    proposal.recommended_candidate_ids = [candidate.id for candidate in winners]
    proposal.status = "recommended"
    _save(root, "proposals", proposal.id, proposal)
    return sorted(winners, key=lambda item: item.id)


def _channel_path(root: Path, skill_key: str, channel: str) -> Path:
    return _state_root(root) / "channels" / skill_key / f"{channel}.json"


def _read_channel(root: Path, skill_key: str, channel: str) -> str | None:
    path = _channel_path(root, skill_key, channel)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return str(data.get("version_id")) if data.get("version_id") else None


def _write_channel(root: Path, skill_key: str, channel: str, version_id: str | None) -> None:
    path = _channel_path(root, skill_key, channel)
    if version_id is None:
        if path.is_file():
            path.unlink()
        return
    _atomic_json(
        path,
        {
            "schema_version": SCHEMA_VERSION,
            "skill_key": skill_key,
            "channel": channel,
            "version_id": version_id,
            "updated_at": now_iso(),
        },
    )


def version_candidate(root: Path, candidate_id: str, label: str) -> SkillVersion:
    if not SAFE_ID_RE.fullmatch(label):
        raise SystemExit("version label 只能使用字母、数字、点、下划线和连字符。")
    candidate = _load(root, "candidates", candidate_id, CandidateJob)
    if candidate.status != "recommended":
        raise SystemExit("只有 Pareto 推荐候选可以生成版本。")
    if fingerprint_path(Path(candidate.source_path)) != candidate.source_fingerprint:
        raise SystemExit("候选 source 已漂移,不能生成不可变版本。")
    proposal = _load(root, "proposals", candidate.proposal_id, EvolutionProposal)
    skill_key = _slug(Path(proposal.skill_path))
    version_id = new_id("version")
    version_source = _state_root(root) / "skills" / skill_key / "versions" / version_id / "source"
    shutil.copytree(
        Path(candidate.source_path),
        version_source,
        symlinks=True,
        ignore=shutil.ignore_patterns(".git", ".skill-engineering"),
    )
    report_id = str(candidate.evaluation_report.get("id") or "")
    version = SkillVersion(
        id=version_id,
        skill_key=skill_key,
        label=label,
        source_path=str(version_source),
        source_fingerprint=fingerprint_path(version_source),
        parent_fingerprint=proposal.baseline_fingerprint,
        candidate_id=candidate.id,
        proposal_id=proposal.id,
        evaluation_report_id=report_id,
        lifecycle="shadow",
    )
    _save(root, "versions", version.id, version)
    _write_channel(root, skill_key, "shadow", version.id)
    candidate.status = "versioned"
    _save(root, "candidates", candidate.id, candidate)
    return version


def _release_hash(plan: ReleasePlan) -> str:
    return payload_hash(asdict(plan), exclude={"plan_hash", "approval", "status"})


def create_release_plan(
    root: Path,
    version_id: str,
    channel: str,
    *,
    project: Path | None = None,
    active_source: Path | None = None,
) -> ReleasePlan:
    if channel not in {"shadow", "canary", "active"}:
        raise SystemExit(f"未知 release channel:{channel}")
    version = _load(root, "versions", version_id, SkillVersion)
    version_source = Path(version.source_path)
    if fingerprint_path(version_source) != version.source_fingerprint:
        raise SystemExit("不可变版本 source 已漂移。")
    child_plan_id: str | None = None
    target_fingerprint = ""
    if channel == "canary":
        if project is None:
            raise SystemExit("Canary release 必须提供窄项目路径。")
        install_plan = create_install_plan(root, version_source, project, scope="project")
        if install_plan.security_gate != "pass" or install_plan.conflicts:
            raise SystemExit("Canary 安装计划被安全门禁或冲突阻断。")
        child_plan_id = install_plan.id
    elif channel == "active":
        if active_source is None:
            raise SystemExit("Active release 必须提供当前维护 source。")
        active_source = active_source.expanduser().resolve()
        proposal = _load(root, "proposals", version.proposal_id, EvolutionProposal)
        ignored_parts = {
            ".git",
            ".skill-engineering",
            "__pycache__",
            ".pytest_cache",
            ".ruff_cache",
        }
        current_files = {
            path.relative_to(active_source).as_posix()
            for path in active_source.rglob("*")
            if path.is_file()
            and not ignored_parts.intersection(path.relative_to(active_source).parts)
        }
        version_files = {
            path.relative_to(version_source).as_posix()
            for path in version_source.rglob("*")
            if path.is_file()
            and not ignored_parts.intersection(path.relative_to(version_source).parts)
        }
        deletions = sorted(current_files - version_files - {"SKILL.md"})
        maintenance_plan = create_improvement_plan(
            root,
            active_source,
            version_source,
            failure_mode=proposal.failure_mode,
            root_cause_layer=proposal.root_cause_layer,
            expected_behavior=proposal.expected_behavior,
            no_regression_reason=f"A3 evaluation report {version.evaluation_report_id} 已提供独立 baseline/holdout 证据。",
            profile="team",
            deletions=deletions,
        )
        if maintenance_plan.preflight.get("status") != "pass":
            raise SystemExit("Active source 维护计划未通过 preflight。")
        child_plan_id = maintenance_plan.id
        target_fingerprint = fingerprint_path(active_source)
    before = _read_channel(root, version.skill_key, channel)
    plan = ReleasePlan(
        id=new_id("release-plan"),
        version_id=version.id,
        channel=channel,
        project=str(project.expanduser().resolve()) if project else None,
        active_source=str(active_source) if active_source else None,
        before_version_id=before,
        version_fingerprint=version.source_fingerprint,
        target_fingerprint=target_fingerprint,
        child_plan_id=child_plan_id,
        plan_hash="",
        approval={"status": "not_requested"},
        status="planned",
    )
    plan.plan_hash = _release_hash(plan)
    _save(root, "release-plans", plan.id, plan)
    return plan


def apply_release_plan(root: Path, plan_id: str, *, approved: bool) -> ReleaseRecord:
    if not approved:
        raise SystemExit("Release 尚未获得明确批准。")
    plan = _load(root, "release-plans", plan_id, ReleasePlan)
    if plan.status != "planned":
        raise SystemExit(f"Release Plan 已处于 {plan.status},不能重复应用。")
    if _release_hash(plan) != plan.plan_hash:
        raise SystemExit("Release Plan 内容或 hash 已漂移。")
    version = _load(root, "versions", plan.version_id, SkillVersion)
    if fingerprint_path(Path(version.source_path)) != plan.version_fingerprint:
        raise SystemExit("Release version source 已漂移。")
    if _read_channel(root, version.skill_key, plan.channel) != plan.before_version_id:
        raise SystemExit("Release channel 已漂移,请重新生成计划。")
    child_record_id: str | None = None
    if plan.channel == "canary":
        if not plan.child_plan_id:
            raise SystemExit("Canary Release Plan 缺安装计划。")
        child = apply_install_plan(
            root,
            plan.child_plan_id,
            approved=True,
            approval_source="a3_release_approval",
        )
        child_record_id = child.id
    elif plan.channel == "active":
        if not plan.child_plan_id or not plan.active_source:
            raise SystemExit("Active Release Plan 缺维护计划或 source。")
        if fingerprint_path(Path(plan.active_source)) != plan.target_fingerprint:
            raise SystemExit("Active source 已漂移,请重新生成 Release Plan。")
        child = apply_improvement_plan(root, load_build_plan(root, plan.child_plan_id))
        child_record_id = child.id
    _write_channel(root, version.skill_key, plan.channel, version.id)
    version.lifecycle = plan.channel
    _save(root, "versions", version.id, version)
    plan.approval = {
        "status": "approved",
        "approved_at": now_iso(),
        "source": "explicit_release_apply",
    }
    plan.status = "applied"
    _save(root, "release-plans", plan.id, plan)
    record = ReleaseRecord(
        id=new_id("release"),
        plan_id=plan.id,
        version_id=version.id,
        channel=plan.channel,
        before_version_id=plan.before_version_id,
        child_record_id=child_record_id,
        status="applied",
        verification={"status": "pending"},
        rollback_available=True,
    )
    _save(root, "release-records", record.id, record)
    return verify_release(root, record.id)


def verify_release(root: Path, record_id: str) -> ReleaseRecord:
    record = _load(root, "release-records", record_id, ReleaseRecord)
    version = _load(root, "versions", record.version_id, SkillVersion)
    channel_ok = _read_channel(root, version.skill_key, record.channel) == version.id
    child_ok = True
    child_verification: dict[str, Any] = {}
    if record.channel == "canary" and record.child_record_id:
        verification = verify_change_record(root, record.child_record_id)
        child_ok = verification.status == "verified"
        child_verification = asdict(verification)
    elif record.channel == "active" and record.child_record_id:
        maintenance = verify_improvement(root, record.child_record_id)
        child_ok = maintenance.verification.get("status") == "passed"
        child_verification = maintenance.verification
    passed = (
        channel_ok
        and child_ok
        and fingerprint_path(Path(version.source_path)) == version.source_fingerprint
    )
    record.verification = {
        "status": "passed" if passed else "failed",
        "checked_at": now_iso(),
        "channel_ok": channel_ok,
        "child": child_verification,
    }
    record.rollback_available = passed
    _save(root, "release-records", record.id, record)
    return record


def rollback_release(root: Path, record_id: str) -> ReleaseRecord:
    record = _load(root, "release-records", record_id, ReleaseRecord)
    version = _load(root, "versions", record.version_id, SkillVersion)
    if (
        record.status != "applied"
        or _read_channel(root, version.skill_key, record.channel) != version.id
    ):
        raise SystemExit("Release 已漂移或不在 applied 状态,不能安全回滚。")
    if record.channel == "canary" and record.child_record_id:
        undo_change_record(root, record.child_record_id)
    elif record.channel == "active" and record.child_record_id:
        undo_improvement(root, record.child_record_id)
    _write_channel(root, version.skill_key, record.channel, record.before_version_id)
    record.status = "rolled-back"
    record.rollback_available = False
    record.rolled_back_at = now_iso()
    record.verification = {"status": "rolled-back", "checked_at": record.rolled_back_at}
    _save(root, "release-records", record.id, record)
    return record


def evolution_status(root: Path, skill_path: Path | None = None) -> dict[str, Any]:
    resolved = skill_path.expanduser().resolve() if skill_path else None
    runs = _list(root, "runs", SkillRun)
    proposals = _list(root, "proposals", EvolutionProposal)
    if resolved:
        runs = [run for run in runs if Path(run.skill_path) == resolved]
        proposals = [proposal for proposal in proposals if Path(proposal.skill_path) == resolved]
    proposal_ids = {proposal.id for proposal in proposals}
    candidates = [
        job for job in _list(root, "candidates", CandidateJob) if job.proposal_id in proposal_ids
    ]
    versions = [
        version
        for version in _list(root, "versions", SkillVersion)
        if version.proposal_id in proposal_ids
    ]
    return {
        "runs": [asdict(item) for item in runs],
        "proposals": [asdict(item) for item in proposals],
        "candidates": [asdict(item) for item in candidates],
        "versions": [asdict(item) for item in versions],
    }

"""Standalone CLI for Skill Engineering."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Path):
        return str(value)
    return value


def _emit(value: Any, text: str, as_json: bool) -> None:
    print(json.dumps(_jsonable(value), ensure_ascii=False, indent=2) if as_json else text)


def _answers(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"answers JSON 无法读取:{path}\n{exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit("answers 必须是 JSON object。")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skill-engineering",
        description="Create, audit, evaluate, evolve, and release Agent Skills.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="本机状态根目录;默认当前目录",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    decide = sub.add_parser("decide", help="判断正确的工程产物")
    decide.add_argument("brief")
    decide.add_argument("--project", type=Path)
    decide.add_argument("--answers", type=Path)
    decide.add_argument("--json", action="store_true")

    journey = sub.add_parser("journey", help="创建和恢复 Skill Guide 任务")
    journey_sub = journey.add_subparsers(dest="journey_cmd", required=True)
    start = journey_sub.add_parser("start")
    start.add_argument("--intent", required=True)
    start.add_argument("--goal", required=True)
    start.add_argument("--project", type=Path)
    start.add_argument("--skill-path", type=Path)
    start.add_argument("--json", action="store_true")
    show = journey_sub.add_parser("show")
    show.add_argument("session_id")
    show.add_argument("--json", action="store_true")
    update = journey_sub.add_parser("update")
    update.add_argument("session_id")
    update.add_argument("--stage")
    update.add_argument("--status")
    update.add_argument("--complete", action="append", default=[])
    update.add_argument("--question", action="append", default=[])
    update.add_argument("--answer", action="append", default=[])
    update.add_argument("--next-action")
    update.add_argument("--approval", choices=["not_requested", "approved", "rejected"])
    update.add_argument("--json", action="store_true")
    listing = journey_sub.add_parser("list")
    listing.add_argument("--json", action="store_true")

    lint = sub.add_parser("lint", aliases=["lint-skill"], help="检查 Skill prompt debt")
    lint.add_argument("target", type=Path)
    lint.add_argument("--json", action="store_true")
    lint.add_argument("--fail-on-warn", action="store_true")
    lint.add_argument("--soft-lines", type=int, default=120)
    lint.add_argument("--hard-lines", type=int, default=200)
    lint.add_argument("--max-description-chars", type=int, default=600)

    for name in ("doctor", "audit"):
        doctor = sub.add_parser(name, help="体检单个 Skill")
        doctor.add_argument("target", type=Path)
        doctor.add_argument(
            "--profile",
            choices=["personal", "team", "production", "commercial"],
            default="team" if name == "audit" else "personal",
        )
        doctor.add_argument("--json", action="store_true")

    create = sub.add_parser("create", help="生成 Skill 创建计划")
    create.add_argument("--name", required=True)
    create.add_argument("--description", required=True)
    create.add_argument("--target", type=Path, required=True)
    create.add_argument(
        "--kind",
        choices=["atomic", "orchestrator", "router", "adapter", "composite"],
        default="atomic",
    )
    create.add_argument("--use-when", action="append", default=[])
    create.add_argument("--do-not-use-when", action="append", default=[])
    create.add_argument("--input", action="append", default=[])
    create.add_argument("--output", action="append", default=[])
    create.add_argument("--side-effect", action="store_true")
    create.add_argument("--production", action="store_true")
    create.add_argument("--scope", choices=["project", "profile", "global"], default="project")
    create.add_argument("--apply", action="store_true")
    create.add_argument("--json", action="store_true")

    improve = sub.add_parser("improve", help="生成或应用持续维护计划")
    improve.add_argument("target", type=Path, nargs="?")
    improve.add_argument("--candidate", type=Path)
    improve.add_argument("--failure-mode", default="")
    improve.add_argument(
        "--root-cause-layer",
        choices=[
            "trigger",
            "interface",
            "state",
            "script",
            "style",
            "long-task",
            "install",
            "structure",
            "test",
        ],
        default="",
    )
    improve.add_argument("--expected-behavior", default="")
    improve.add_argument("--regression-case", action="append", default=[])
    improve.add_argument("--no-regression-reason", default="")
    improve.add_argument("--profile", choices=["personal", "team", "production"], default="team")
    improve.add_argument("--delete", action="append", default=[])
    improve.add_argument("--plan", dest="plan_id")
    improve.add_argument("--apply", action="store_true")
    improve.add_argument("--json", action="store_true")

    verify_improvement = sub.add_parser("verify-improvement")
    verify_improvement.add_argument("--record", required=True, dest="record_id")
    verify_improvement.add_argument("--json", action="store_true")
    undo_improvement = sub.add_parser("undo-improvement")
    undo_improvement.add_argument("--record", required=True, dest="record_id")
    undo_improvement.add_argument("--apply", action="store_true")
    undo_improvement.add_argument("--json", action="store_true")
    history = sub.add_parser("maintenance-history")
    history.add_argument("--target", type=Path)
    history.add_argument("--json", action="store_true")

    validate = sub.add_parser("validate-eval-suite")
    validate.add_argument("--suite", type=Path, required=True)
    validate.add_argument("--production", action="store_true")
    validate.add_argument("--json", action="store_true")
    evaluate = sub.add_parser("evaluate")
    evaluate.add_argument("--suite", type=Path, required=True)
    evaluate.add_argument("--baseline-results", type=Path, required=True)
    evaluate.add_argument("--candidate-results", type=Path, required=True)
    evaluate.add_argument("--production", action="store_true")
    evaluate.add_argument("--json", action="store_true")

    evolution = sub.add_parser("evolution", help="证据驱动的 Skill 自进化")
    evolution_sub = evolution.add_subparsers(dest="evolution_cmd", required=True)
    record = evolution_sub.add_parser("record-run")
    record.add_argument("--input", type=Path, required=True)
    record.add_argument("--json", action="store_true")
    propose = evolution_sub.add_parser("propose")
    propose.add_argument("--skill", type=Path, required=True)
    propose.add_argument("--force", action="store_true")
    propose.add_argument("--json", action="store_true")
    dataset = evolution_sub.add_parser("build-dataset")
    dataset.add_argument("--proposal", required=True)
    dataset.add_argument("--json", action="store_true")
    prepare = evolution_sub.add_parser("prepare-candidates")
    prepare.add_argument("--proposal", required=True)
    prepare.add_argument("--json", action="store_true")
    register = evolution_sub.add_parser("register-candidate")
    register.add_argument("--job", required=True)
    register.add_argument("--path", type=Path)
    register.add_argument("--json", action="store_true")
    submit = evolution_sub.add_parser("submit-results")
    submit.add_argument("--candidate", required=True)
    submit.add_argument("--baseline-results", type=Path, required=True)
    submit.add_argument("--candidate-results", type=Path, required=True)
    submit.add_argument("--cost", type=float)
    submit.add_argument("--json", action="store_true")
    select = evolution_sub.add_parser("select")
    select.add_argument("--proposal", required=True)
    select.add_argument("--json", action="store_true")
    version = evolution_sub.add_parser("version")
    version.add_argument("--candidate", required=True)
    version.add_argument("--label", required=True)
    version.add_argument("--json", action="store_true")
    evo_status = evolution_sub.add_parser("status")
    evo_status.add_argument("--skill", type=Path)
    evo_status.add_argument("--json", action="store_true")

    release_plan = sub.add_parser("release-plan")
    release_plan.add_argument("--version", required=True, dest="version_id")
    release_plan.add_argument("--channel", choices=["shadow", "canary", "active"], required=True)
    release_plan.add_argument("--project", type=Path)
    release_plan.add_argument("--active-source", type=Path)
    release_plan.add_argument("--json", action="store_true")
    release = sub.add_parser("release")
    release.add_argument("--plan", required=True, dest="plan_id")
    release.add_argument("--apply", action="store_true")
    release.add_argument("--json", action="store_true")
    release_verify = sub.add_parser("release-verify")
    release_verify.add_argument("--record", required=True, dest="record_id")
    release_verify.add_argument("--json", action="store_true")
    release_rollback = sub.add_parser("release-rollback")
    release_rollback.add_argument("--record", required=True, dest="record_id")
    release_rollback.add_argument("--apply", action="store_true")
    release_rollback.add_argument("--json", action="store_true")
    return parser


def _journey(root: Path, args: argparse.Namespace) -> int:
    from .journey import JourneySession, list_journeys, load_journey, new_id, save_journey

    if args.journey_cmd == "start":
        value = JourneySession(
            id=new_id("journey"),
            intent=args.intent,
            goal=args.goal,
            stage="discover",
            status="in_progress",
            project=str(args.project.expanduser().resolve()) if args.project else None,
            skill_path=str(args.skill_path.expanduser().resolve()) if args.skill_path else None,
            pending_questions=[],
            next_action="分析需求并判断正确的工程产物。",
        )
        save_journey(root, value)
    elif args.journey_cmd == "show":
        value = load_journey(root, args.session_id)
    elif args.journey_cmd == "update":
        value = load_journey(root, args.session_id)
        if args.stage:
            value.stage = args.stage
        if args.status:
            value.status = args.status
        value.completed_steps.extend(
            item for item in args.complete if item not in value.completed_steps
        )
        value.pending_questions = args.question[:3]
        for raw in args.answer:
            if "=" not in raw:
                raise SystemExit("--answer 必须是 KEY=VALUE。")
            key, answer = raw.split("=", 1)
            value.answers[key] = answer
        if args.next_action:
            value.next_action = args.next_action
        if args.approval:
            value.approval = {"status": args.approval, "source": "explicit_cli_argument"}
        save_journey(root, value)
    else:
        values = list_journeys(root)
        print(json.dumps([asdict(item) for item in values], ensure_ascii=False, indent=2))
        return 0
    _emit(value, value.handoff_summary(), args.json)
    return 0


def _evolution(root: Path, args: argparse.Namespace) -> int:
    from .evolution import (
        build_dataset,
        evolution_status,
        prepare_candidates,
        propose_evolution,
        record_run,
        register_candidate,
        select_candidates,
        submit_results,
        version_candidate,
    )

    command = args.evolution_cmd
    if command == "record-run":
        value = record_run(root, args.input)
    elif command == "propose":
        value = propose_evolution(root, args.skill, force=args.force)
    elif command == "build-dataset":
        value = build_dataset(root, args.proposal)
    elif command == "prepare-candidates":
        values = prepare_candidates(root, args.proposal)
        print(json.dumps([asdict(item) for item in values], ensure_ascii=False, indent=2))
        return 0
    elif command == "register-candidate":
        value = register_candidate(root, args.job, args.path)
    elif command == "submit-results":
        value = submit_results(
            root,
            args.candidate,
            args.baseline_results,
            args.candidate_results,
            candidate_cost=args.cost,
        )
    elif command == "select":
        values = select_candidates(root, args.proposal)
        print(json.dumps([asdict(item) for item in values], ensure_ascii=False, indent=2))
        return 0
    elif command == "version":
        value = version_candidate(root, args.candidate, args.label)
    else:
        print(json.dumps(evolution_status(root, args.skill), ensure_ascii=False, indent=2))
        return 0
    _emit(value, f"{type(value).__name__}:{value.id}", args.json)
    return 0 if getattr(value, "status", "") not in {"rejected"} else 1


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.expanduser().resolve()

    if args.cmd == "decide":
        from .decision import decide_capability, format_decision

        value = decide_capability(root, args.brief, _answers(args.answers), args.project)
        _emit(value, format_decision(value), args.json)
        return 0
    if args.cmd == "journey":
        return _journey(root, args)
    if args.cmd in {"lint", "lint-skill"}:
        from .skill_lint import LintOptions, format_json, format_text, lint_skill

        value = lint_skill(
            args.target,
            LintOptions(
                soft_lines=args.soft_lines,
                hard_lines=args.hard_lines,
                max_description_chars=args.max_description_chars,
                fail_on_warn=args.fail_on_warn,
            ),
        )
        print(format_json(value) if args.json else format_text(value))
        return value.exit_code(fail_on_warn=args.fail_on_warn)
    if args.cmd in {"doctor", "audit"}:
        from .skill_doctor import doctor_skill, format_json, format_text

        value = doctor_skill(args.target, profile=args.profile)
        print(format_json(value) if args.json else format_text(value))
        return value.exit_code()
    if args.cmd == "create":
        from .scaffold import apply_build_plan, create_build_plan, format_build_plan

        value = create_build_plan(
            root,
            args.target,
            name=args.name,
            description=args.description,
            kind=args.kind,
            use_when=args.use_when,
            do_not_use_when=args.do_not_use_when,
            inputs=args.input,
            outputs=args.output,
            side_effect=args.side_effect,
            production=args.production,
            recommended_scope=args.scope,
        )
        created = apply_build_plan(root, value) if args.apply else []
        payload = asdict(value)
        payload["created"] = [str(item) for item in created]
        _emit(payload, format_build_plan(value), args.json)
        return 0
    if args.cmd == "improve":
        from .journey import load_build_plan
        from .maintenance import (
            apply_improvement_plan,
            create_improvement_plan,
            format_improvement_plan,
            format_maintenance_record,
        )

        if args.plan_id:
            value = load_build_plan(root, args.plan_id)
            if not args.apply:
                _emit(value, format_improvement_plan(value), args.json)
                return 0
            record = apply_improvement_plan(root, value)
            _emit(record, format_maintenance_record(record), args.json)
            return 0
        if args.apply or not args.target or not args.candidate:
            raise SystemExit("先用 target + --candidate 生成计划;应用时使用 --plan ID --apply。")
        value = create_improvement_plan(
            root,
            args.target,
            args.candidate,
            failure_mode=args.failure_mode,
            root_cause_layer=args.root_cause_layer,
            expected_behavior=args.expected_behavior,
            regression_cases=args.regression_case,
            no_regression_reason=args.no_regression_reason,
            profile=args.profile,
            deletions=args.delete,
        )
        _emit(value, format_improvement_plan(value), args.json)
        return 0 if value.preflight.get("status") == "pass" else 1
    if args.cmd in {"verify-improvement", "undo-improvement", "maintenance-history"}:
        from .maintenance import (
            format_maintenance_record,
            maintenance_history,
            undo_improvement,
            verify_improvement,
        )

        if args.cmd == "maintenance-history":
            values = maintenance_history(root, args.target)
            print(json.dumps([asdict(item) for item in values], ensure_ascii=False, indent=2))
            return 0
        if args.cmd == "undo-improvement":
            if not args.apply:
                raise SystemExit("撤销必须显式 --apply。")
            value = undo_improvement(root, args.record_id)
        else:
            value = verify_improvement(root, args.record_id)
        _emit(value, format_maintenance_record(value), args.json)
        return 0
    if args.cmd == "validate-eval-suite":
        from .evaluation import load_evaluation_suite

        value, fingerprint = load_evaluation_suite(args.suite, production=args.production)
        payload = asdict(value)
        payload["sha256"] = fingerprint
        _emit(payload, f"Evaluation suite valid:{value.id}", args.json)
        return 0
    if args.cmd == "evaluate":
        from .evaluation import evaluate_behavior, format_behavior_report

        value = evaluate_behavior(
            root,
            args.suite,
            args.baseline_results,
            args.candidate_results,
            production=args.production,
        )
        _emit(value, format_behavior_report(value), args.json)
        return 0 if value.decision == "accept" else 1
    if args.cmd == "evolution":
        return _evolution(root, args)
    if args.cmd == "release-plan":
        from .evolution import create_release_plan

        value = create_release_plan(
            root,
            args.version_id,
            args.channel,
            project=args.project,
            active_source=args.active_source,
        )
        _emit(value, f"Release Plan:{value.id};尚未发布。", args.json)
        return 0
    if args.cmd in {"release", "release-verify", "release-rollback"}:
        from .evolution import apply_release_plan, rollback_release, verify_release

        if args.cmd == "release":
            if not args.apply:
                raise SystemExit("发布必须显式 --apply。")
            value = apply_release_plan(root, args.plan_id, approved=True)
        elif args.cmd == "release-rollback":
            if not args.apply:
                raise SystemExit("回滚必须显式 --apply。")
            value = rollback_release(root, args.record_id)
        else:
            value = verify_release(root, args.record_id)
        _emit(value, f"Release:{value.id};{value.status}", args.json)
        return 0
    raise SystemExit(f"未知命令:{args.cmd}")


if __name__ == "__main__":
    raise SystemExit(main())

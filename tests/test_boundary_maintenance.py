from __future__ import annotations

import json
from pathlib import Path

import pytest

from test_maintenance import architecture_input, setup_pair

from skill_engineering.maintenance import apply_improvement_plan, create_improvement_plan


def reviewed_plan(root: Path, target: Path, candidate: Path, **kwargs):
    if "architecture_review" not in kwargs:
        kwargs["architecture_review"] = architecture_input(root, target, candidate)
    return create_improvement_plan(
        root, target, candidate,
        failure_mode="修正既有描述措辞",
        root_cause_layer="style",
        expected_behavior="保持既有职责与触发范围",
        regression_cases=["tests/cases/trigger.yaml"],
        **kwargs,
    )


def unchanged_input(root: Path) -> Path:
    """Synthetic operator declaration for a wording-only fixture, not user approval."""
    path = root / "boundary.json"
    path.write_text(json.dumps({
        "schema_version": "1", "change": "unchanged",
        "reason": "合成测试仅替换描述措辞，目标、职责和排除项保持不变。",
    }, ensure_ascii=False), encoding="utf-8")
    return path


@pytest.mark.parametrize("profile", ["personal", "team", "production"])
def test_new_preview_without_boundary_declaration_blocks_before_writes(tmp_path, profile):
    root, target, candidate = setup_pair(tmp_path)
    before = (target / "SKILL.md").read_bytes()
    plan = reviewed_plan(root, target, candidate, profile=profile)

    assert plan.preflight["status"] == "blocked"
    assert plan.preflight["boundary_review"]["status"] == "unreviewed"
    assert any(item["rule_id"] == "MAINT112" and item["level"] == "FAIL"
               for item in plan.findings)
    with pytest.raises(SystemExit, match="preflight"):
        apply_improvement_plan(root, plan)
    assert (target / "SKILL.md").read_bytes() == before
    assert not (root / ".skill-engineering" / "maintenance-backups").exists()


def test_unchanged_boundary_is_frozen_and_legacy_unknown(tmp_path):
    from skill_engineering.maintenance import format_improvement_plan, format_maintenance_record

    root, target, candidate = setup_pair(tmp_path)
    path = unchanged_input(root)
    plan = reviewed_plan(root, target, candidate, boundary_review=path)
    report = plan.preflight["boundary_review"]
    assert plan.preflight["status"] == "pass"
    assert report["status"] == "pass"
    assert report["confirmation_status"] == "legacy_unknown"
    assert report["policy_version"] == "1"
    assert "legacy_unknown" in format_improvement_plan(plan)
    path.write_text("invalid after preview", encoding="utf-8")
    record = apply_improvement_plan(root, plan)
    assert record.preflight["boundary_review"] == report
    assert "legacy_unknown" in format_maintenance_record(record)


@pytest.mark.parametrize("confirmation", ["missing", "pending", "rejected", "stale", "fingerprint"])
def test_changed_without_current_confirmation_is_blocked(tmp_path, confirmation):
    from test_maintenance import boundary_input

    root, target, candidate = setup_pair(tmp_path)
    path = boundary_input(root)
    declaration = json.loads(path.read_text(encoding="utf-8"))
    if confirmation == "missing":
        declaration.pop("confirmation")
    elif confirmation == "fingerprint":
        declaration["confirmation"]["boundary_fingerprint"] = "e" * 64
    else:
        declaration["confirmation"]["status"] = confirmation
    path.write_text(json.dumps(declaration, ensure_ascii=False), encoding="utf-8")
    plan = reviewed_plan(root, target, candidate, boundary_review=path)
    assert plan.preflight["status"] == "blocked"
    assert plan.preflight["boundary_review"]["status"] == "blocked"
    assert any(item["rule_id"] == "MAINT112" for item in plan.findings)


def test_sensitive_boundary_input_is_not_persisted_in_blocked_plan(tmp_path):
    from dataclasses import asdict

    root, target, candidate = setup_pair(tmp_path)
    path = unchanged_input(root)
    declaration = json.loads(path.read_text(encoding="utf-8"))
    declaration["reason"] = "api_key=synthetic-sensitive-value"
    path.write_text(json.dumps(declaration), encoding="utf-8")
    plan = reviewed_plan(root, target, candidate, boundary_review=path)
    assert plan.preflight["status"] == "blocked"
    assert "synthetic-sensitive-value" not in json.dumps(asdict(plan), ensure_ascii=False)


def test_unchanged_conflicts_with_architecture_boundary_change(tmp_path):
    root, target, candidate = setup_pair(tmp_path)
    architecture = architecture_input(root, target, candidate)
    value = json.loads(architecture.read_text(encoding="utf-8"))
    value["requirement"]["touched_boundaries"] = ["routing"]
    architecture.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    plan = reviewed_plan(root, target, candidate, architecture_review=architecture,
                         boundary_review=unchanged_input(root))
    assert plan.preflight["architecture_review"]["status"] == "pass"
    assert plan.preflight["boundary_review"]["architecture_boundary_changed"] is True
    assert plan.preflight["boundary_review"]["status"] == "blocked"


@pytest.mark.parametrize("mutation", ["confirmation_status", "effective", "declaration", "null"])
def test_apply_revalidates_boundary_even_with_recomputed_plan_hash(tmp_path, mutation):
    from skill_engineering.maintenance import _plan_hash

    root, target, candidate = setup_pair(tmp_path)
    plan = reviewed_plan(root, target, candidate, boundary_review=unchanged_input(root))
    report = plan.preflight["boundary_review"]
    if mutation == "effective":
        report["input_fingerprints"]["effective"] = "d" * 64
    elif mutation == "declaration":
        report["declaration"]["reason"] = ""
    elif mutation == "null":
        plan.preflight["boundary_review"] = None
    else:
        report["confirmation_status"] = "confirmed"
    plan.plan_hash = _plan_hash(plan)
    before = (target / "SKILL.md").read_bytes()
    with pytest.raises(SystemExit, match="边界"):
        apply_improvement_plan(root, plan)
    assert (target / "SKILL.md").read_bytes() == before
    assert not (root / ".skill-engineering" / "maintenance-backups").exists()


def test_changed_declaration_is_protected_by_original_plan_hash(tmp_path):
    root, target, candidate = setup_pair(tmp_path)
    plan = reviewed_plan(root, target, candidate, boundary_review=unchanged_input(root))
    plan.preflight["boundary_review"]["declaration"]["reason"] = "另一项有效理由"
    with pytest.raises(SystemExit, match="plan hash"):
        apply_improvement_plan(root, plan)


@pytest.mark.parametrize("mutation", ["content", "missing", "extra", "duplicate"])
@pytest.mark.parametrize("legacy", [False, True], ids=["boundary-plan", "legacy-plan"])
def test_apply_rejects_plan_files_differing_from_candidate_before_any_write(tmp_path, mutation, legacy):
    from copy import deepcopy

    from test_maintenance import boundary_input

    from skill_engineering.journey import BuildFile, fingerprint_path
    from skill_engineering.maintenance import _plan_hash

    root, target, candidate = setup_pair(tmp_path)
    plan = reviewed_plan(root, target, candidate,
                         boundary_review=boundary_input(root, excludes=["forbidden-output-marker"]))
    assert plan.preflight["status"] == "pass"
    if legacy:
        plan.preflight.pop("boundary_review")
    if mutation == "content":
        next(item for item in plan.files if item.relative_path == "SKILL.md").content += (
            "\nforbidden-output-marker\n"
        )
    elif mutation == "missing":
        plan.files = [item for item in plan.files if item.relative_path != "SKILL.md"]
    elif mutation == "extra":
        plan.files.append(BuildFile("unreviewed.md", "forbidden-output-marker", "伪造新增项"))
    else:
        item = deepcopy(next(item for item in plan.files if item.relative_path == "SKILL.md"))
        item.content += "\nforbidden-output-marker\n"
        plan.files.append(item)
    plan.plan_hash = _plan_hash(plan)
    before = fingerprint_path(target)
    with pytest.raises(SystemExit, match="计划.*候选"):
        apply_improvement_plan(root, plan)
    assert fingerprint_path(target) == before
    assert not (root / ".skill-engineering" / "maintenance-backups").exists()
    assert not (root / ".skill-engineering" / "maintenance-records").exists()


def test_apply_rejects_duplicate_deletions_before_backup(tmp_path):
    from test_maintenance import boundary_input

    from skill_engineering.journey import fingerprint_path
    from skill_engineering.maintenance import _plan_hash

    root, target, candidate = setup_pair(tmp_path)
    (target / "obsolete.md").write_text("old content", encoding="utf-8")
    deletion = "obsolete.md"
    plan = reviewed_plan(
        root, target, candidate, deletions=[deletion],
        architecture_review=architecture_input(root, target, candidate, deletions=[deletion]),
        boundary_review=boundary_input(root),
    )
    assert plan.preflight["status"] == "pass"
    plan.deletions.append(deletion)
    plan.plan_hash = _plan_hash(plan)
    before = fingerprint_path(target)
    with pytest.raises(SystemExit, match="计划.*删除"):
        apply_improvement_plan(root, plan)
    assert fingerprint_path(target) == before
    assert not (root / ".skill-engineering" / "maintenance-backups").exists()


@pytest.mark.parametrize("tree", ["target", "candidate"])
@pytest.mark.parametrize("kind", ["directory", "file", "dangling", "ignored-directory"])
def test_preview_rejects_internal_symlinks_before_copy_or_plan_save(tmp_path, tree, kind):
    from test_maintenance import boundary_input

    root, target, candidate = setup_pair(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    sentinel = outside / "format.md"
    sentinel.write_text("outside-sentinel", encoding="utf-8")
    linked_tree = target if tree == "target" else candidate
    if kind == "directory":
        (linked_tree / "references").symlink_to(outside, target_is_directory=True)
        if tree == "target":
            (candidate / "references").mkdir()
            (candidate / "references" / "format.md").write_text("candidate-output", encoding="utf-8")
    elif kind == "file":
        (linked_tree / "linked.md").symlink_to(sentinel)
    elif kind == "dangling":
        (linked_tree / "linked.md").symlink_to(outside / "missing.md")
    else:
        (linked_tree / ".git").symlink_to(outside, target_is_directory=True)
    rejection = ""
    try:
        create_improvement_plan(
            root, target, candidate, failure_mode="合成测试", root_cause_layer="style",
            expected_behavior="不写外部文件", regression_cases=["tests/cases/trigger.yaml"],
            boundary_review=boundary_input(root),
        )
    except SystemExit as error:
        rejection = str(error)
    assert sentinel.read_text(encoding="utf-8") == "outside-sentinel"
    assert "symlink" in rejection
    assert not (root / ".skill-engineering" / "build-plans").exists()
    assert not (root / ".skill-engineering" / "maintenance-backups").exists()


def test_apply_rejects_internal_ancestor_symlink_before_actual_output_copy(tmp_path):
    from test_maintenance import boundary_input

    from skill_engineering.journey import fingerprint_path
    from skill_engineering.maintenance import _plan_hash

    root, target, candidate = setup_pair(tmp_path)
    references = candidate / "references"
    references.mkdir()
    (references / "format.md").write_text("candidate-output", encoding="utf-8")
    plan = reviewed_plan(root, target, candidate, boundary_review=boundary_input(root))
    assert plan.preflight["status"] == "pass"
    outside = tmp_path / "outside"
    outside.mkdir()
    sentinel = outside / "format.md"
    sentinel.write_text("outside-sentinel", encoding="utf-8")
    (target / "references").symlink_to(outside, target_is_directory=True)
    # Reach the copy path rather than stopping at the earlier fingerprint guard.
    plan.target_fingerprint = fingerprint_path(target)
    plan.plan_hash = _plan_hash(plan)
    rejection = ""
    try:
        apply_improvement_plan(root, plan)
    except SystemExit as error:
        rejection = str(error)
    assert sentinel.read_text(encoding="utf-8") == "outside-sentinel"
    assert "symlink" in rejection
    assert not (root / ".skill-engineering" / "maintenance-backups").exists()
    assert not (root / ".skill-engineering" / "maintenance-records").exists()


@pytest.mark.parametrize("copier", ["effective", "planned"])
@pytest.mark.parametrize("tree", ["target", "candidate", "destination"])
def test_copy_helpers_reject_internal_symlinks_without_public_entry(tmp_path, copier, tree):
    from test_maintenance import boundary_input

    from skill_engineering.maintenance import _copy_effective_tree, _copy_planned_tree

    root, target, candidate = setup_pair(tmp_path)
    (candidate / "references").mkdir()
    (candidate / "references" / "format.md").write_text("candidate-output", encoding="utf-8")
    plan = reviewed_plan(root, target, candidate, boundary_review=boundary_input(root))
    outside = tmp_path / "outside"
    outside.mkdir()
    sentinel = outside / "format.md"
    sentinel.write_text("outside-sentinel", encoding="utf-8")
    destination = tmp_path / "effective"
    if tree == "target":
        (target / "references").symlink_to(outside, target_is_directory=True)
    elif tree == "candidate":
        (candidate / "linked-directory").symlink_to(outside, target_is_directory=True)
    else:
        destination.mkdir()
        (destination / "references").symlink_to(outside, target_is_directory=True)
    rejection = ""
    try:
        if copier == "effective":
            _copy_effective_tree(target, candidate, destination, [])
        else:
            _copy_planned_tree(target, candidate, destination, plan)
    except (SystemExit, OSError) as error:
        rejection = str(error)
    assert sentinel.read_text(encoding="utf-8") == "outside-sentinel"
    assert "symlink" in rejection


def test_preview_allows_resolved_management_entry_symlinks(tmp_path):
    from test_maintenance import boundary_input

    root, target, candidate = setup_pair(tmp_path)
    target_entry = tmp_path / "managed-target"
    candidate_entry = tmp_path / "managed-candidate"
    target_entry.symlink_to(target, target_is_directory=True)
    candidate_entry.symlink_to(candidate, target_is_directory=True)
    plan = reviewed_plan(
        root, target_entry, candidate_entry,
        architecture_review=architecture_input(root, target, candidate),
        boundary_review=boundary_input(root),
    )
    assert plan.preflight["status"] == "pass"
    assert Path(plan.target) == target.resolve()
    assert Path(plan.candidate) == candidate.resolve()
    assert apply_improvement_plan(root, plan).status == "applied"


def test_changed_boundary_checks_effective_retained_and_deleted_markdown(tmp_path):
    from test_maintenance import boundary_input

    from skill_engineering.journey import fingerprint_path
    from skill_engineering.maintenance import undo_improvement, verify_improvement

    root, target, candidate = setup_pair(tmp_path)
    retained = target / "references" / "retained.md"
    retained.parent.mkdir()
    retained.write_text("retained-boundary-evidence", encoding="utf-8")
    deleted = retained.parent / "obsolete.md"
    deleted.write_text("obsolete-boundary-evidence", encoding="utf-8")
    deletions = ["references/obsolete.md"]
    plan = reviewed_plan(
        root, target, candidate, deletions=deletions,
        architecture_review=architecture_input(root, target, candidate, deletions=deletions),
        boundary_review=boundary_input(root, includes=["retained-boundary-evidence"],
                                       excludes=["obsolete-boundary-evidence"]),
    )
    report = plan.preflight["boundary_review"]
    assert plan.preflight["status"] == "pass"
    assert report["confirmation_status"] == "confirmed"
    assert report["input_fingerprints"]["effective"] != fingerprint_path(candidate)
    record = apply_improvement_plan(root, plan)
    assert retained.exists() and not deleted.exists()
    assert report["input_fingerprints"]["effective"] == record.after_fingerprint
    assert verify_improvement(root, record.id).verification["status"] == "passed"
    assert undo_improvement(root, record.id).status == "undone"


def test_changed_boundary_cannot_pass_using_only_pre_overlay_text(tmp_path):
    from test_maintenance import boundary_input

    root, target, candidate = setup_pair(tmp_path)
    deleted = target / "obsolete.md"
    deleted.write_text("deleted-only-evidence", encoding="utf-8")
    deletions = ["obsolete.md"]
    plan = reviewed_plan(
        root, target, candidate, deletions=deletions,
        architecture_review=architecture_input(root, target, candidate, deletions=deletions),
        boundary_review=boundary_input(root, includes=["deleted-only-evidence"]),
    )
    assert plan.preflight["boundary_review"]["status"] == "blocked"
    assert plan.preflight["status"] == "blocked"


def test_apply_binds_architecture_boundary_change_to_boundary_snapshot(tmp_path):
    from test_maintenance import boundary_input

    from skill_engineering.boundary_policy import assess_boundary
    from skill_engineering.maintenance import _markdown_text, _plan_hash

    root, target, candidate = setup_pair(tmp_path)
    architecture = architecture_input(root, target, candidate)
    value = json.loads(architecture.read_text(encoding="utf-8"))
    value["requirement"]["touched_boundaries"] = ["routing"]
    architecture.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    plan = reviewed_plan(root, target, candidate, architecture_review=architecture,
                         boundary_review=boundary_input(root))
    assert plan.preflight["status"] == "pass"
    fingerprints = plan.preflight["boundary_review"]["input_fingerprints"]
    plan.preflight["boundary_review"] = assess_boundary(
        json.loads(unchanged_input(root).read_text(encoding="utf-8")),
        target_fingerprint=fingerprints["target"],
        candidate_fingerprint=fingerprints["candidate"],
        effective_fingerprint=fingerprints["effective"],
        candidate_text=_markdown_text(candidate),
    )
    plan.plan_hash = _plan_hash(plan)
    with pytest.raises(SystemExit, match="边界"):
        apply_improvement_plan(root, plan)


def test_pre_boundary_legal_plan_applies_without_changing_its_hash_or_snapshot(tmp_path):
    from skill_engineering.journey import load_build_plan, save_build_plan
    from skill_engineering.maintenance import _plan_hash, format_improvement_plan, format_maintenance_record

    root, target, candidate = setup_pair(tmp_path)
    plan = reviewed_plan(root, target, candidate, boundary_review=unchanged_input(root))
    plan.preflight.pop("boundary_review")
    plan.plan_hash = _plan_hash(plan)
    save_build_plan(root, plan)
    loaded = load_build_plan(root, plan.id)
    original_hash = loaded.plan_hash
    assert "legacy_unknown" in format_improvement_plan(loaded)
    record = apply_improvement_plan(root, loaded)
    assert loaded.plan_hash == original_hash
    assert "boundary_review" not in loaded.preflight
    assert "boundary_review" not in record.preflight
    assert "legacy_unknown" in format_maintenance_record(record)


@pytest.mark.parametrize("raw", [
    '{"schema_version":"1","change":"unchanged","reason":"secret raw", "reason":"duplicate"}',
    '{"schema_version":"1","change":"unchanged","reason":NaN}',
    '{"schema_version":"1","change":"unchanged","reason":"secret raw"',
    '"secret raw"',
    ' ' * (128 * 1024 + 1),
], ids=["duplicate", "non-json-number", "malformed", "not-object", "oversized"])
def test_boundary_file_strictly_bounds_json_and_does_not_echo_contents(tmp_path, raw):
    root, target, candidate = setup_pair(tmp_path)
    path = root / "boundary.json"
    path.write_text(raw, encoding="utf-8")
    with pytest.raises(SystemExit, match="边界") as error:
        reviewed_plan(root, target, candidate, boundary_review=path)
    assert "secret raw" not in str(error.value)
    assert not list((root / ".skill-engineering" / "build-plans").glob("*.json"))


@pytest.mark.parametrize("kind", ["directory", "symlink", "fifo"])
def test_boundary_file_must_be_plain_regular_file(tmp_path, kind):
    import os

    root, target, candidate = setup_pair(tmp_path)
    path = root / "invalid-boundary"
    if kind == "directory":
        path.mkdir()
    elif kind == "symlink":
        path.symlink_to(unchanged_input(root))
    else:
        os.mkfifo(path)
    with pytest.raises(SystemExit, match="边界"):
        reviewed_plan(root, target, candidate, boundary_review=path)


def test_scaffold_proxy_uses_core_boundary_gate(tmp_path):
    from skill_engineering.scaffold import create_improvement_plan as proxy

    root, target, candidate = setup_pair(tmp_path)
    args = dict(failure_mode="合成措辞修复", root_cause_layer="style",
                expected_behavior="职责不变", regression_cases=["tests/cases/trigger.yaml"],
                architecture_review=architecture_input(root, target, candidate))
    assert proxy(root, target, candidate, **args).preflight["status"] == "blocked"
    accepted = proxy(root, target, candidate, boundary_review=unchanged_input(root), **args)
    assert accepted.preflight["boundary_review"]["confirmation_status"] == "legacy_unknown"

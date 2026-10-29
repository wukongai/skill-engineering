import importlib.util
import json

from pathlib import Path

import test_native_plan as fixtures


def test_new_native_preview_requires_boundary_confirmation(tmp_path: Path):
    project = tmp_path / 'project'
    project.mkdir()
    fixtures._write_brief(project)
    candidate = fixtures._write_candidate(tmp_path / 'candidate')
    result = fixtures._preview(
        project, candidate, project / "target", tmp_path / "plan.json", confirmation=False,
    )
    assert result.returncode != 0
    assert '确认' in result.stderr


def setup_native(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    brief_path = fixtures._write_brief(project)
    candidate = fixtures._write_candidate(tmp_path / "candidate")
    return project, brief_path, candidate, project / "target", tmp_path / "plan.json"


def test_pending_confirmation_cannot_preview(tmp_path):
    project, _, candidate, target, plan = setup_native(tmp_path)
    receipt = fixtures._write_confirmation(project, status="pending")
    result = fixtures._preview(project, candidate, target, plan, confirmation=receipt)
    assert result.returncode != 0
    assert "确认" in result.stderr
    assert not plan.exists()


def test_confirmed_empty_exclusions_can_preview(tmp_path):
    project, brief_path, candidate, target, plan = setup_native(tmp_path)
    brief = json.loads(brief_path.read_text())
    brief["excluded_capabilities"] = []
    brief["negative_triggers"] = []
    brief_path.write_text(json.dumps(brief))
    result = fixtures._preview(project, candidate, target, plan)
    assert result.returncode == 0, result.stderr
    frozen = json.loads(plan.read_text())["brief"]
    assert frozen["boundary_confirmation"]["excluded_decision"] == "none"
    assert frozen["boundary"]["excluded_capabilities"] == []


def test_changed_boundary_invalidates_confirmation(tmp_path):
    project, brief_path, candidate, target, plan = setup_native(tmp_path)
    receipt = fixtures._write_confirmation(project)
    brief = json.loads(brief_path.read_text())
    brief["mission"] = "另一个目标"
    brief_path.write_text(json.dumps(brief))
    result = fixtures._preview(project, candidate, target, plan, confirmation=receipt)
    assert result.returncode != 0
    assert "指纹" in result.stderr


def test_new_policy_requires_redirect_strategy(tmp_path):
    project, brief_path, candidate, target, plan = setup_native(tmp_path)
    receipt = fixtures._write_confirmation(project)
    brief = json.loads(brief_path.read_text())
    brief["redirect_strategy"] = []
    brief_path.write_text(json.dumps(brief))
    result = fixtures._preview(project, candidate, target, plan, confirmation=receipt)
    assert result.returncode != 0
    assert "redirect" in result.stderr or "确认" in result.stderr


def test_confirmation_is_frozen_not_reread_at_apply(tmp_path):
    project, _, candidate, target, plan = setup_native(tmp_path)
    receipt = fixtures._write_confirmation(project)
    assert fixtures._preview(project, candidate, target, plan, confirmation=receipt).returncode == 0
    receipt.write_text(json.dumps({"status": "pending"}))
    result = fixtures._run("apply", "--plan", plan, "--candidate", candidate, "--target", target)
    assert result.returncode == 0, result.stderr


def load_native():
    spec = importlib.util.spec_from_file_location("boundary_native_test", fixtures.NATIVE_PLAN)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_legacy_native_plan_retains_original_apply_path(tmp_path):
    project, _, candidate, target, plan = setup_native(tmp_path)
    assert fixtures._preview(project, candidate, target, plan).returncode == 0
    payload = json.loads(plan.read_text())
    for key in ("boundary_policy_version", "boundary", "boundary_confirmation"):
        payload["brief"].pop(key)
    module = load_native()
    payload["plan_hash"] = module._plan_hash(payload)
    plan.write_text(json.dumps(payload))
    result = fixtures._run("apply", "--plan", plan, "--candidate", candidate, "--target", target)
    assert result.returncode == 0, result.stderr


def test_invalid_frozen_confirmation_fails_even_after_rehash(tmp_path):
    project, _, candidate, target, plan = setup_native(tmp_path)
    assert fixtures._preview(project, candidate, target, plan).returncode == 0
    payload = json.loads(plan.read_text())
    payload["brief"]["boundary_confirmation"]["status"] = "pending"
    payload["plan_hash"] = load_native()._plan_hash(payload)
    plan.write_text(json.dumps(payload))
    result = fixtures._run("apply", "--plan", plan, "--candidate", candidate, "--target", target)
    assert result.returncode != 0
    assert not target.exists()


def test_partial_new_policy_snapshot_cannot_fall_back_to_legacy(tmp_path):
    project, _, candidate, target, plan = setup_native(tmp_path)
    assert fixtures._preview(project, candidate, target, plan).returncode == 0
    payload = json.loads(plan.read_text())
    payload["brief"].pop("boundary_policy_version")
    payload["brief"]["boundary_confirmation"]["status"] = "pending"
    payload["plan_hash"] = load_native()._plan_hash(payload)
    plan.write_text(json.dumps(payload))
    result = fixtures._run("apply", "--plan", plan, "--candidate", candidate, "--target", target)
    assert result.returncode != 0
    assert not target.exists()


def test_new_policy_revalidates_frozen_behavior_report(tmp_path):
    project, _, candidate, target, plan = setup_native(tmp_path)
    assert fixtures._preview(project, candidate, target, plan).returncode == 0
    payload = json.loads(plan.read_text())
    payload["behavior_tests"]["passed"] = 100
    payload["plan_hash"] = load_native()._plan_hash(payload)
    plan.write_text(json.dumps(payload))
    result = fixtures._run("apply", "--plan", plan, "--candidate", candidate, "--target", target)
    assert result.returncode != 0
    assert not target.exists()


def test_duplicate_confirmation_keys_are_not_last_wins(tmp_path):
    project, _, candidate, target, plan = setup_native(tmp_path)
    receipt = fixtures._write_confirmation(project)
    text = receipt.read_text().replace(
        '"status": "confirmed"', '"status": "rejected", "status": "confirmed"', 1,
    )
    receipt.write_text(text)
    result = fixtures._preview(project, candidate, target, plan, confirmation=receipt)
    assert result.returncode != 0
    assert not plan.exists()


def test_legacy_apply_and_verify_do_not_claim_confirmed_scope(tmp_path):
    project, _, candidate, target, plan = setup_native(tmp_path)
    assert fixtures._preview(project, candidate, target, plan).returncode == 0
    payload = json.loads(plan.read_text())
    for key in ("boundary_policy_version", "boundary", "boundary_confirmation"):
        payload["brief"].pop(key)
    payload["plan_hash"] = load_native()._plan_hash(payload)
    plan.write_text(json.dumps(payload))
    applied = fixtures._run("apply", "--plan", plan, "--candidate", candidate,
                            "--target", target, "--json")
    verified = fixtures._run("verify", "--plan", plan, "--target", target, "--json")
    assert applied.returncode == verified.returncode == 0
    assert json.loads(applied.stdout)["boundary_confirmation_status"] == "legacy_unknown"
    assert json.loads(verified.stdout)["boundary_confirmation_status"] == "legacy_unknown"

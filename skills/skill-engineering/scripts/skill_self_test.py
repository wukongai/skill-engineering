#!/usr/bin/env python3
"""Run portable, manifest-declared self-tests for a completed Skill candidate.

The runner is intentionally not an operating-system sandbox. Static gates run
first; approved Python entries then execute in a temporary copy with a minimal
environment, ``-B`` bytecode suppression, and a bounded timeout.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def _load_sibling(filename: str, module_name: str):
    sibling = Path(__file__).resolve().with_name(filename)
    spec = importlib.util.spec_from_file_location(module_name, sibling)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载 portable 检查器:{sibling}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def _fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _read_manifest(target: Path) -> list[dict[str, object]]:
    manifest_path = target / "tests" / "self-test.json"
    if not manifest_path.is_file():
        return []
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    tests = payload.get("tests", []) if isinstance(payload, dict) else []
    return [item for item in tests if isinstance(item, dict)] if isinstance(tests, list) else []


def _minimal_env(temp_root: Path) -> dict[str, str]:
    home = temp_root / "home"
    temp = temp_root / "tmp"
    home.mkdir()
    temp.mkdir()
    env = {
        "HOME": str(home),
        "TMPDIR": str(temp),
        "PATH": os.defpath,
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONIOENCODING": "utf-8",
    }
    return env


def _json_has_key(payload: object, dotted_key: str) -> bool:
    current = payload
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    return True


def _run_declared_test(
    candidate: Path,
    entry: dict[str, object],
    env: dict[str, str],
) -> dict[str, object]:
    test_id = str(entry.get("id") or "unnamed")
    script_raw = str(entry.get("script") or "")
    script = candidate / script_raw
    if script.suffix.lower() != ".py":
        return {
            "id": test_id,
            "script": script_raw,
            "status": "uncovered",
            "reason": "portable_runner_supports_python_only",
        }

    stdin_text = ""
    stdin_raw = entry.get("stdin")
    if isinstance(stdin_raw, str) and stdin_raw:
        stdin_text = (candidate / stdin_raw).read_text(encoding="utf-8")
    timeout = int(entry.get("timeout_seconds", 10))

    try:
        process = subprocess.run(
            [sys.executable, "-B", str(script)],
            cwd=candidate,
            env=env,
            input=stdin_text,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "id": test_id,
            "script": script_raw,
            "status": "blocked",
            "reason": "timeout",
            "timeout_seconds": timeout,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
        }

    failures: list[str] = []
    expected_exit = int(entry.get("expected_exit", 0))
    if process.returncode != expected_exit:
        failures.append(f"expected_exit={expected_exit}, actual={process.returncode}")
    for expected in entry.get("stdout_contains", []):
        if str(expected) not in process.stdout:
            failures.append(f"stdout 缺少:{expected}")
    for expected in entry.get("stderr_contains", []):
        if str(expected) not in process.stderr:
            failures.append(f"stderr 缺少:{expected}")
    json_keys = entry.get("stdout_json_keys", [])
    if json_keys:
        try:
            stdout_json = json.loads(process.stdout)
        except json.JSONDecodeError:
            failures.append("stdout 不是有效 JSON")
        else:
            for key in json_keys:
                if not _json_has_key(stdout_json, str(key)):
                    failures.append(f"stdout JSON 缺少 key:{key}")

    return {
        "id": test_id,
        "script": script_raw,
        "status": "blocked" if failures else "pass",
        "reason": "assertion_failed" if failures else "all_assertions_passed",
        "failures": failures,
        "exit_code": process.returncode,
        "stdout": process.stdout,
        "stderr": process.stderr,
    }


def run_self_test(target: Path) -> dict[str, object]:
    target = target.expanduser().resolve()
    before = _fingerprint(target)
    gate = _load_sibling("content_gate.py", "skill_engineering_content_gate")
    review = _load_sibling("creation_review.py", "skill_engineering_creation_review")
    gate_findings = gate.check_candidate(target)
    creation_review = review.review_candidate(target, "personal")

    try:
        manifest_entries = _read_manifest(target)
    except (OSError, json.JSONDecodeError) as exc:
        manifest_entries = []
        gate_findings.append(
            {
                "rule": "CG010",
                "path": "tests/self-test.json",
                "message": f"self-test manifest 无法读取:{exc}",
            }
        )

    uncovered = [
        {
            "id": str(entry.get("id") or "unnamed"),
            "script": str(entry.get("script") or ""),
            "status": "uncovered",
            "reason": "portable_runner_supports_python_only",
        }
        for entry in manifest_entries
        if Path(str(entry.get("script") or "")).suffix.lower() != ".py"
    ]
    results: list[dict[str, object]] = list(uncovered)

    static_blocked = bool(gate_findings) or creation_review["status"] == "blocked"
    if not static_blocked and not uncovered and manifest_entries:
        with tempfile.TemporaryDirectory(prefix="skill-self-test-") as temp_name:
            temp_root = Path(temp_name)
            candidate = temp_root / "candidate"
            shutil.copytree(target, candidate)
            env = _minimal_env(temp_root)
            results = [
                _run_declared_test(candidate, entry, env) for entry in manifest_entries
            ]

    if uncovered:
        declared_status = "uncovered"
    elif static_blocked:
        declared_status = "blocked"
    elif any(item["status"] != "pass" for item in results):
        declared_status = "blocked"
    else:
        declared_status = "pass"

    after = _fingerprint(target)
    target_unchanged = before == after
    if not target_unchanged:
        declared_status = "blocked"
        results.append(
            {
                "id": "target-integrity",
                "status": "blocked",
                "reason": "target_modified_during_self_test",
            }
        )

    steps = {
        "content_gate": "blocked" if gate_findings else "pass",
        "creation_review": creation_review["status"],
        "declared_tests": declared_status,
        # Compatibility key for 1.1 pre-remediation consumers.
        "scripts_compile": "pass" if declared_status == "pass" else "blocked",
    }
    blocked = static_blocked or declared_status != "pass" or not target_unchanged
    return {
        "status": "blocked" if blocked else "pass",
        "steps": steps,
        "findings": gate_findings,
        "creation_review": creation_review,
        "declared_tests": results,
        "target_unchanged": target_unchanged,
        "runner_boundary": {
            "sandbox": False,
            "supported_runtime": "python",
            "controls": [
                "static_gate_first",
                "manifest_allowlist",
                "temporary_copy",
                "minimal_environment",
                "timeout",
            ],
        },
        "agent_trial": {
            "status": "pending",
            "instruction": (
                "确定性层完成后,宿主 Agent 必须用一个与用户需求一致的真实样本试运行;"
                "两层都通过才能进入 validated,任一失败进入 needs_improvement。"
            ),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="创建后声明式自测(portable)")
    parser.add_argument("target", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    target = args.target.expanduser().resolve()
    if not target.is_dir():
        print(f"用法错误:Skill 目录不存在:{target}", file=sys.stderr)
        return 2
    try:
        result = run_self_test(target)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"自测无法运行:{exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif result["status"] == "pass":
        print("确定性自测通过(内容门禁 + portable 创建评审 + 声明式脚本测试)。")
        print("下一步:用一个真实样本试运行;两层都通过才能视为已验证。")
    else:
        print("自测未通过,创建状态保持 needs_improvement:")
        for item in result["findings"]:
            print(f"- [{item['rule']}] {item['path']}: {item['message']}")
        for item in result["declared_tests"]:
            if item["status"] != "pass":
                print(f"- [self-test:{item['id']}] {item['reason']}")
    return 1 if result["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())

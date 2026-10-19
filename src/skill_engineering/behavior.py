"""Deterministic behavior case runner for Skill candidates.

The runner deliberately evaluates only declarative text assertions. It does not
pretend to replace a host Agent's real task trial; uncovered cases remain
visible and keep the candidate out of validated status.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _candidate_text(candidate: Path) -> str:
    candidate = candidate.expanduser().resolve()
    skill = candidate / "SKILL.md"
    if not skill.is_file():
        raise ValueError(f"candidate 缺少 SKILL.md:{candidate}")
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(candidate.rglob("*.md"))
        if path.is_file() and not path.is_symlink()
    )


def run_behavior_cases(candidate: Path, cases: list[Any]) -> dict[str, Any]:
    """Run declarative candidate assertions and report uncovered cases.

    A case is executable when it is a mapping with ``id``, ``given``,
    ``expect``, ``must_not`` and an ``assertions`` mapping. Legacy string
    labels are retained for compatibility but reported as ``uncovered``.
    """

    text = _candidate_text(candidate)
    reports: list[dict[str, Any]] = []
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            reports.append({"id": str(case) or f"case-{index}", "status": "uncovered"})
            continue
        case_id = str(case.get("id") or f"case-{index}")
        assertions = case.get("assertions")
        required = ("given", "expect", "must_not")
        if not all(case.get(key) for key in required) or not isinstance(assertions, dict):
            reports.append({"id": case_id, "status": "uncovered"})
            continue
        missing = [value for value in assertions.get("must_include", []) if value not in text]
        forbidden = [value for value in assertions.get("must_not_include", []) if value in text]
        status = "passed" if not missing and not forbidden else "failed"
        reports.append(
            {
                "id": case_id,
                "status": status,
                "missing": missing,
                "forbidden": forbidden,
            }
        )
    passed = sum(item["status"] == "passed" for item in reports)
    failed = sum(item["status"] == "failed" for item in reports)
    uncovered = sum(item["status"] == "uncovered" for item in reports)
    status = "failed" if failed else "uncovered" if uncovered else "passed"
    return {
        "status": status,
        "total": len(reports),
        "passed": passed,
        "failed": failed,
        "uncovered": uncovered,
        "cases": reports,
    }

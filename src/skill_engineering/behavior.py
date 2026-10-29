"""Deterministic behavior case runner for Skill candidates.

The runner deliberately evaluates only declarative text assertions. It does not
pretend to replace a host Agent's real task trial; uncovered cases remain
visible and keep the candidate out of validated status.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .boundary_policy import run_text_cases


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


def run_behavior_cases(candidate: Path, cases: list[Any], *, policy: dict | None = None,
                       boundary: dict | None = None) -> dict[str, Any]:
    """Run declarative candidate assertions and report uncovered cases.

    A case is executable when it is a mapping with ``id``, ``given``,
    ``expect``, ``must_not`` and an ``assertions`` mapping. Legacy string
    labels are retained for compatibility but reported as ``uncovered``.
    """

    return run_text_cases(_candidate_text(candidate), cases, policy=policy, boundary=boundary)

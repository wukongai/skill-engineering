# Codex Canonical Release Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Codex the only required real-host E2E for Skill Engineering releases while preserving all deterministic, security, adapter-contract, evidence, and approval gates.

**Architecture:** Add an immutable cross-version ADR, update only current normative release facts, and preserve historical K3/testing/daily evidence as snapshots of the previous policy. A release regression test will enforce the distinction between required Codex E2E, required multi-host adapter fixtures, and optional non-Codex real-host smoke.

**Tech Stack:** Markdown governance artifacts, pytest, Python 3.11+, existing release consistency script and Skill Engineering CLI.

## Global Constraints

- Codex is the only required real-host E2E for `1.1.0` and later default releases.
- Claude Code, Hermes, Pi, Kimi CLI, and future non-Codex real-host E2E are compatibility evidence and do not block the core release by default.
- Adapter contract fixtures, shared security boundaries, no-Creator behavior, full deterministic gates, and independent review remain blocking.
- Historical handoffs, testing reports, and daily logs remain unchanged.
- `1.1.0` stays Unreleased until merge, tag, and GitHub Release receive separate authorization.
- No external Creator, Superpowers package, model provider, or new runtime dependency is added to Skill Engineering.

---

### Task 1: Add the release-policy regression test

**Files:**
- Modify: `tests/test_v1_release.py`
- Read: `docs/specs/2026-07-31-codex-canonical-release-gate-spec.md`

**Interfaces:**
- Consumes: current normative release documents as UTF-8 text.
- Produces: `test_codex_is_the_only_required_real_host_release_gate()` and an updated release-evidence assertion.

- [x] **Step 1: Replace the old pending-Hermes release assertion**

Add a test that reads:

```python
normative_paths = [
    "docs/adr/0009-codex-canonical-release-gate.md",
    "docs/specs/2026-07-29-v1.1-native-authoring-spec.md",
    "docs/plans/2026-07-29-v1.1-native-authoring-plan.md",
    "docs/TASK.md",
    "docs/sprints/2026-07-v1.1-native-authoring.md",
    "docs/releases/RELEASE-LOG.md",
    "docs/guides/skill-engineering-execution-architecture.md",
]
```

The test must assert:

```python
assert "Codex" in combined
assert "唯一" in combined
assert "非阻断" in combined
assert "adapter" in combined.lower()
assert "Codex 与 Hermes 无 Creator E2E 通过" not in combined
assert "Hermes 无 Creator 真实 E2E 仍待真实环境" not in combined
```

The release-log assertion must require `Unreleased`, successful Codex evidence,
non-blocking Hermes wording, and pending merge/tag/GitHub Release authorization.

- [x] **Step 2: Run the focused test and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_v1_release.py::test_codex_is_the_only_required_real_host_release_gate -q
```

Expected: FAIL because ADR-0009 does not exist and current normative documents
still contain the old dual-host hard gate.

### Task 2: Establish the new policy and synchronize current facts

**Files:**
- Create: `docs/adr/0009-codex-canonical-release-gate.md`
- Modify: `docs/adr/README.md`
- Modify: `docs/README.md`
- Modify: `docs/specs/2026-07-29-v1.1-native-authoring-spec.md`
- Modify: `docs/plans/2026-07-29-v1.1-native-authoring-plan.md`
- Modify: `docs/specs/2026-07-30-v1.1-review-remediation-spec.md`
- Modify: `docs/plans/2026-07-30-v1.1-review-remediation-plan.md`
- Modify: `docs/TASK.md`
- Modify: `docs/sprints/2026-07-v1.1-native-authoring.md`
- Modify: `docs/releases/RELEASE-LOG.md`
- Modify: `docs/guides/skill-engineering-execution-architecture.md`
- Modify: `CHANGELOG.md`
- Create: `docs/logs/daily/2026-07-31.md`

**Interfaces:**
- Consumes: the approved canonical-host Spec and existing Codex/K3 evidence.
- Produces: one authoritative cross-version release policy and consistent current release facts.

- [x] **Step 1: Add ADR-0009**

The ADR must state:

```text
Codex is the canonical and only required real-host E2E.
Non-Codex real-host E2E is optional compatibility evidence.
Adapter fixtures and shared safety boundaries remain required.
Historical evidence remains immutable.
Changing the canonical host requires a new ADR.
```

- [x] **Step 2: Update current v1.1 Spec and Plan**

Replace the dual-host requirement with:

```text
Codex 无 Creator 真实 E2E 必须通过；Claude Code、Hermes、Pi、Kimi CLI
至少通过 adapter contract fixture，真实 smoke 作为非阻断兼容性证据。
```

Add a supersession note to the remediation Spec/Plan instead of rewriting
their historical test findings.

- [x] **Step 3: Update current execution and release status**

`TASK.md`, the v1.1 Sprint, Release Log, execution architecture guide, Changelog,
ADR index, and docs index must say:

```text
Codex E2E and K3 review passed.
Hermes real E2E is not a release blocker.
The feature branch commit/push exists.
Merge, tag, and GitHub Release remain pending separate authorization.
```

The release log must remain `Unreleased`; no release date or tag may be fabricated.

- [x] **Step 4: Record the decision without rewriting history**

Create `docs/logs/daily/2026-07-31.md` with the owner decision, affected normative
files, unchanged historical evidence, and the exact remaining release actions.

- [x] **Step 5: Run focused tests and verify GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_v1_release.py -q
```

Expected: all `tests/test_v1_release.py` tests pass.

### Task 3: Verify the exact release candidate

**Files:**
- Verify: all modified files
- Do not modify: historical files under `docs/handoffs/`, `docs/testing/`, or daily logs dated before `2026-07-31`

**Interfaces:**
- Consumes: the synchronized policy and existing 1.1 implementation.
- Produces: fresh deterministic release evidence for the uncommitted candidate.

- [x] **Step 1: Run the full Python suite**

Run:

```bash
.venv/bin/python -m pytest -q
```

Expected: all tests pass with zero failures.

- [x] **Step 2: Run static and Skill checks**

Run:

```bash
.venv/bin/python -m ruff check .
.venv/bin/skill-engineering lint skills/skill-engineering
.venv/bin/skill-engineering doctor skills/skill-engineering --profile production
.venv/bin/python skills/skill-engineering/scripts/skill_self_test.py skills/skill-engineering --json
```

Expected: Ruff and lint pass; Doctor reports zero FAIL/WARN and 100/A structural
readiness; portable self-test reports `status=pass` and `target_unchanged=true`.

- [x] **Step 3: Run security and release consistency checks**

Run:

```bash
bash scripts/credential-lint.sh --all
.venv/bin/python scripts/check-release.py --version 1.1.0
git diff --check
```

Expected: credential lint, release consistency, and diff check pass.

- [x] **Step 4: Inspect the final diff and stop at the next approval boundary**

Confirm:

```text
No historical evidence was rewritten.
No runtime dependency was added.
The worktree contains only the approved policy, tests, and fact synchronization.
No commit, push, merge, tag, or GitHub Release occurred.
```

Report the remaining decision as one user-facing action: authorize commit/push
of the policy candidate, followed later by separate merge/tag/GitHub Release
authorization.

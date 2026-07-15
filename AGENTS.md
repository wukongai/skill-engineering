# Skill Engineering

Skill Engineering is the standalone source of truth for Skill Guide, Doctor, behavior evaluation, continuous maintenance, self-evolution, and release safety.

## Rules

1. Use Simplified Chinese for user-facing collaboration unless the user requests otherwise.
2. Feature work requires a spec and plan before implementation.
3. Preview before write; apply must reference the same immutable plan.
4. Never store credentials, raw sensitive prompts, or full conversations in local state.
5. Static Doctor scores are structural readiness, not downstream utility.
6. Candidate generation must not receive holdout assertions or baseline scores.
7. Canary/Active release requires explicit approval; Global release is out of scope.
8. Run pytest, Ruff, Skill validation, credential lint, and diff check before declaring completion.

## Self-hosted product workflow

1. For a new capability request, self-check existing Skills/scripts/plugins/docs and complete discovery before choosing an artifact. Do not create product/version scaffolding before deciding that a Skill is needed.
2. When resuming this existing repository, start with `docs/PRODUCT.md`, `docs/constitution.md`, `docs/architecture.md`, `docs/TASK.md`, and the current Sprint.
3. Feature work requires a current file under `docs/specs/` and `docs/plans/` before implementation.
4. Cross-version architecture decisions require an ADR under `docs/adr/`.
5. New ideas that are not part of the active Sprint go to `docs/BACKLOG.md`; do not silently expand the current version.
6. Record daily facts and blockers under `docs/logs/daily/`; promote stable rules into formal docs instead of citing the log forever.
7. Update README, Changelog, Roadmap, Task, Sprint, version sources, tests, and release evidence together before a release claim.
8. Use an isolated candidate and the maintenance engine for changes to Skill Guide; do not edit maintained Skill source as an experiment.
9. Commit and push are separate approval points. Never auto-publish, auto-tag, or auto-enable Global scope.

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

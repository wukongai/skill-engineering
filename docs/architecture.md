# Architecture

Skill Engineering has three layers.

## Conversational layer

`skills/skill-guide/` is the Agent-facing entry. It routes user intent, loads only the needed reference or stage instructions, and stops at approval boundaries.

It does not duplicate deterministic implementation in prose. Commands delegate to the Python core.

Default human output is rendered through `UserFeedback`: result, real-world impact, one next action, and an explicit decision only when approval is required. Internal IDs, fingerprints, state enums, and raw records remain in JSON for automation, audit, and recovery instead of appearing as the user-facing conclusion.

## Deterministic core

`src/skill_engineering/` owns:

- decision and local Skill discovery;
- scaffold plans;
- static lint and type-aware Doctor;
- deterministic baseline/holdout evaluation;
- maintenance plans, complexity deltas, verification, history, and undo;
- run evidence, evolution proposals, isolated candidates, Pareto selection, immutable versions, and release records.

Local state lives under `.skill-engineering/` in the selected root. Plans and records are versioned JSON with fingerprints and drift checks.

## External integrations

The host Agent generates candidate content inside an isolated CandidateJob workspace. It does not receive holdout assertions or baseline scores.

Agent Skill Hub remains the owner of registry, Profile, Adapter, Global, and multi-project distribution. Skill Engineering only creates a narrow project Canary during a release.

## Release flow

```text
validated candidate
  -> immutable version
  -> automatic Shadow pointer
  -> Canary or Active plan
  -> explicit approval
  -> apply
  -> verify
  -> rollback when safe
```

Active updates reuse the same preview-first maintenance engine. Canary links are owned by their change record and are removed only when they have not drifted.

# Architecture

Product intent and long-term invariants live in `PRODUCT.md` and `constitution.md`. This file describes the current implementation.

Skill Engineering has three layers.

Versioned architecture direction:

- `0.1.x` supplies the local deterministic lifecycle baseline.
- `1.0` freezes the CLI/JSON/contract/release evidence interfaces.
- `2.0` adds a separate Blueprint/IR fact layer and Architecture Guardian checks; it does not replace Doctor or Agent Skill Hub.

## Two entry flows

New capability discovery and existing-project development are different flows.

```text
new request
  -> inspect existing capabilities
  -> clarify one decision-changing question at a time
  -> compare artifact approaches
  -> decide whether a Skill is needed
  -> architecture and governance

existing Skill project
  -> read Product / Architecture / current version and Sprint
  -> resume the approved lifecycle
```

Product and version management are downstream of the artifact decision for a new request. They are an entrypoint only when resuming an already-established Skill product.

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

## Self-hosted governance

Repository development is managed as a product lifecycle around the three runtime layers:

```text
Product / Constitution
  -> Roadmap / Backlog / Sprint
  -> Spec / Plan / ADR
  -> isolated candidate
  -> maintenance plan
  -> tests and evidence
  -> version / changelog / release decision
```

This governance layer is not injected into every generated Skill. Simple Skills stay minimal; production and commercial Skills progressively adopt the artifacts justified by their risk and expected lifetime.

## 2.0 Blueprint boundary

The first 2.0 slice introduces a versioned, read-only Blueprint/IR with three axes: component role, execution topology, and governance level. Inventory may report `unknown` or `legacy`; it must not invent missing facts. Guardian findings become preview inputs for `create`/`improve`, while existing immutable plans, approval, postflight, verify, and undo remain the write boundary.

## Creation flow

```text
create parameters
  -> immutable BuildPlan preview
  -> create --plan ID --apply
  -> plan hash + target fingerprint check
  -> planned files only
  -> lint + team Doctor structural postflight
  -> cleanup on structural failure
  -> optional production Doctor readiness report
```

A production scaffold may be structurally correct while still missing real behavioral evidence. That state is reported as incomplete, not as a failed scaffold and not as production-ready.

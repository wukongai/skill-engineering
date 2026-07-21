# Skill Engineering

[简体中文](README.md) | [English](README.en.md)

> **Make Skills dependable: turn one work goal into an Agent capability you can trust and maintain for the long term.**

Current stable release: [`1.0.0`](https://github.com/wukongai/skill-engineering/releases/tag/v1.0.0) · Next: `2.0.0` Architecture Guardian (development preview) · local-first · provider-neutral · Apache-2.0

Skill Engineering is a meta-Skill for creating, auditing, and maintaining Agent Skills. You describe the work you want done. It first decides whether a Skill is justified, then makes responsibilities, trigger boundaries, outputs, risks, and verification explicit. Nothing is written until you approve the plan.

[Install now](#installation) · [Why it exists](#why-skill-engineering) · [See real use cases](#four-real-use-cases) · [Explore the roadmap](#roadmap)

## Installation

Most users need only one command:

```bash
npx skills add wukongai/skill-engineering
```

The installer guides you through choosing Codex, Claude Code, or another supported host and selecting project or global scope. You do not need to memorize flags first.

After installation, tell your Agent:

```text
Use Skill Engineering to help me build a Skill.
First decide whether a new Skill is actually needed. If it is, show me its responsibilities,
boundaries, and creation plan. Write files only after I approve.
```

For an existing Skill that has accumulated patches:

```text
This Skill failed in a real task.
Find the layer where the problem belongs, explain what will change and what will stay,
and turn the failure into a repeatable regression case before touching the production version.
```

Upgrades and removal use the standard `skills` installer, such as `npx skills update` and `npx skills remove`. See the [licensing and installation guide](docs/guides/licensing-and-installation.md) for full scope details.

## Why Skill Engineering

Writing a Skill is easy. Keeping it correct across new inputs, ten rounds of edits, and real tool integrations is much harder.

Many Skills work once and then decay:

- broad triggers activate on unrelated requests;
- the model fills in facts that were never present in the source;
- every incident adds another prohibition to the end of `SKILL.md`;
- new edits overwrite the production version and silently break old behavior;
- directory complexity grows without clear responsibilities or evidence;
- static scores look excellent while real task value remains unknown;
- releases happen without previews, verification, or recovery paths.

Skill Engineering is not about generating more prompt text. It answers a harder question:

> **How do you make a Skill well-bounded and useful from version one, then keep it verifiable, recoverable, and maintainable through every later change?**

## What Skill Engineering 1.0 does

```text
describe the goal
  -> inventory existing Skills / Scripts / Plugins / project rules
  -> decide whether a new Skill is justified
  -> clarify responsibilities, triggers, outputs, and side effects
  -> choose the smallest architecture that matches the risk
  -> generate a complete candidate and write preview
  -> apply with approval and verify
  -> maintain, evaluate, record, and recover through isolated candidates
```

### 1. Decide before creating

Not every request should become a Skill. A one-off task may need no artifact; a deterministic transformation may be better as a script; authenticated tools or browser access may require a Plugin/runtime. Skill Engineering compares options before creating another directory.

### 2. Preview the complete plan before writing

Before files change, the user sees when the Skill triggers, when it must not trigger, its inputs and outputs, planned files, external effects, and approval boundaries.

### 3. Generate the smallest complete structure

Simple Skills do not receive empty enterprise scaffolding. Scripts, contracts, regression cases, Specs, Plans, ADRs, and release evidence appear only as risk and expected lifetime justify them.

### 4. Turn real failures into lasting protection

Maintenance first locates the root cause in the trigger, interface, state, script, structure, or test layer. It modifies an isolated candidate and adds evidence that prevents the same failure from returning.

### 5. Make every change verifiable and recoverable

Production changes are previewed first and applied through the same undrifted plan. Postflight checks verify the result and restore safely on failure. Structural health, behavioral evidence, and real task utility remain separate claims.

## Four real use cases

Skill Engineering 1.0 used four cases of increasing complexity to validate creation, external boundaries, deterministic execution, and architecture governance.

| Use case | User goal | What it validates |
|---|---|---|
| Meeting action items | Extract decisions, owners, and due dates | Trigger boundaries, evidence, and maintainability in a lightweight Skill |
| GitHub Issue implementation plan | Classify, deduplicate, and plan Issues | Read-only analysis and approval boundaries around external systems |
| Local web-app acceptance | Log in, search, export, and retain evidence | Clear division between a Skill and deterministic browser scripts |
| Multi-file research evidence pack | Organize questions, sources, evidence, and conclusions | Complex structure, failed-plan cleanup, and risk-aware replanning |

### Use case 1: meeting notes are not “just another summary prompt”

The user starts with a simple goal:

```text
Every week I turn meeting notes into decisions, owners, and due dates.
Help me build a Skill for that.
```

Skill Engineering does not immediately write files. It first clarifies whether ordinary summaries should trigger, what happens when an owner or date is missing, where results belong, and whether version one should connect to an external task system.

The final plan establishes explicit boundaries:

- extract only source-backed decisions and action items;
- mark missing owners or dates as “needs confirmation” instead of inventing them;
- do not trigger on general summaries, rewriting, or sentiment analysis;
- handle Markdown only in version one and never update external task systems;
- create no target files before the user approves the plan.

The result is a minimal structure matched to the risk, not an empty template. When a real run later introduced unsupported content, maintenance did not append “never hallucinate.” It introduced field-level evidence checks and regression cases for ambiguous intentions and incorrectly joined owners or dates.

This case demonstrates the basic 1.0 value: **more predictable results, reviewable changes, and less chance that a new patch silently breaks old behavior.**

### Use case 2: read-only GitHub Issue analysis

The Skill classifies Issues, identifies likely duplicates, and prepares an implementation plan. Version one can analyze and recommend, but it cannot change labels, comment, or close an Issue. Any GitHub write crosses the approved read-only boundary and requires a new decision.

### Use case 3: local web-app acceptance

The user describes “log in, search for a project, export CSV, and save screenshots and reports.” The Skill owns natural-language routing, safety boundaries, and failure reporting; deterministic browser scripts own actions and assertions. The final evidence includes screenshots, CSV, JSON, and Markdown.

### Use case 4: multi-file research evidence pack

A complex research Skill separates its entry, contract, output specification, examples, and regression cases. When the first plan would have triggered a high-risk external release, the system stopped and cleaned up. It then replanned around local-only research, demonstrating risk-scaled structure and recovery.

All four cases reran Preview, Apply, failure recovery, structural checks, and release gates against the same `1.0.0` candidate. See the [four-use-case release evidence](docs/testing/2026-07-18-v1-use-cases.md). It proves protected behavior did not regress; it does not claim universal utility across every model, repository, or production environment.

## Who it is for

| User | Typical need | Value |
|---|---|---|
| Codex and Claude Code users | Turn recurring work into reusable Skills | Describe the goal without learning Skill engineering first |
| Creators and solo operators | Preserve personal judgment and workflows | Turn one experience into a bounded long-lived capability |
| Skill developers and teams | Repair trigger conflicts, rule accumulation, and architecture drift | Isolated candidates, regression evidence, maintenance records, and recovery |
| Commercial and industrial teams | Require stable interfaces, safety review, and release gates | Add contracts, versions, approvals, and independent evidence as risk grows |

## Roadmap

### 1.0: make one Skill dependable

`1.0.0` is released. It freezes a stable local lifecycle contract for creation, Doctor, behavioral result comparison, isolated maintenance, evolution, release evidence, and rollback.

### 2.0: protect the whole Skill architecture

Architecture Guardian is in development. Blueprint/IR describes component roles, execution topology, and governance levels so later checks can identify dependency problems, duplicated responsibilities, trigger collisions, context cost, and architectural change. All results remain read-only previews before any production modification.

### 3.0 vision: evolve from real usage

3.0 is a long-term direction, not a release commitment. The goal is to learn from redacted real runs, generate isolated candidates, validate them with development/holdout, high-risk, and negative-transfer evidence, then release or withdraw them gradually within controlled scopes.

> 1.0 makes one Skill dependable. 2.0 protects the whole Skill architecture. 3.0 lets Skills evolve from real usage.

See the [Roadmap](docs/ROADMAP.md), [VERSIONING](docs/VERSIONING.md), [FEATURE-MATRIX](docs/FEATURE-MATRIX.md), and the [current 2.0 Sprint](docs/sprints/2026-07-v2.0-architecture-guardian.md) for precise status.

## Release evidence

The `1.0.0` release candidate reran four real user journeys and passed the then-current 133 pytest tests, Ruff, Agent Skill validation, credential lint, diff checks, wheel builds, clean-environment installation, and remote installation checks.

Production Doctor reached `100/A`. That is structural readiness, not proof of business outcomes across every real task.

- [GitHub Release v1.0.0](https://github.com/wukongai/skill-engineering/releases/tag/v1.0.0)
- [Four verified use cases](docs/testing/2026-07-18-v1-use-cases.md)
- [Remote standard-install evidence](docs/testing/2026-07-16-standard-skill-install.md)
- [1.x public contract](docs/references/v1-public-contract.md)

## Current boundaries

- The core is provider-neutral and does not embed an LLM API.
- Static Doctor results measure structural, security, and maintainability readiness, not real-task utility.
- Candidate generation does not receive holdout assertions or baseline scores.
- Evaluation suites never execute arbitrary commands or third-party scripts.
- Global and multi-project distribution belong to Agent Skill Hub; this project never auto-publishes Global scope.
- Hosted collaboration, RBAC, managed evaluation, SLA, and native client permission enforcement are not current promises.

### Python core and CLI

The Agent Skill is the product entry point. Ordinary users should not treat the CLI as a second product to learn. The repository still contains a deterministic Python core and 1.x-compatible CLI for immutable plans, Doctor, evaluation, maintenance records, CI, and recovery.

The standard `skills` installer installs only the Agent Skill, not the Python runtime. Some deep 1.0 checks and maintenance operations still require that core. When it is missing, the Skill reports the dependency explicitly instead of pretending the operation succeeded. Maintainers and CI can pin the stable runtime with:

```bash
uv tool install "git+https://github.com/wukongai/skill-engineering.git@v1.0.0"
```

This is a current implementation boundary and compatibility surface, not prerequisite knowledge for beginning with Skill Engineering.

## Local development

Ordinary users do not need to clone the repository. Clone it only for source study, extension, development testing, or contributing:

```bash
git clone https://github.com/wukongai/skill-engineering.git
cd skill-engineering
python3 -m pip install -e ".[dev]"
```

```text
skills/skill-engineering/   conversational Agent Skill entry
src/skill_engineering/      deterministic engineering and compatibility core
tests/                      behavior, safety, and version regression
docs/                       product, standards, plans, and release evidence
```

Start with the [documentation index](docs/README.md). The project uses its own lifecycle rules to manage itself.

### Full validation

```bash
python3 -m pytest -q
python3 -m ruff check src tests
python3 /path/to/skill-creator/scripts/quick_validate.py skills/skill-engineering
bash scripts/credential-lint.sh --all
git diff --check
```

## License, contributing, and security

Original source code, Agent Skill instructions, references, schemas, tests, examples, and documentation use Apache License 2.0 unless stated otherwise. Commercial use and redistribution are allowed. Third-party material keeps its original license; user prompts, private data, generated Skills, and runtime outputs are not claimed by this project.

- [Apache License 2.0](LICENSE)
- [NOTICE](NOTICE)
- [Licensing and installation guide](docs/guides/licensing-and-installation.md)
- [Contributing guide](CONTRIBUTING.md)
- [Security policy](SECURITY.md)

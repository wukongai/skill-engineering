# Skill Engineering

> Current development: `2.0.0` Architecture Guardian · baseline `0.1.x` · local-first · provider-neutral · MIT

Skill Engineering helps users rapidly create Agent Skills that are engineered from the first version, then keeps them clear, testable, safe, and extensible through every later change.

It provides one conversational entry, **Skill Engineering**, for creating, auditing, evaluating, improving, evolving, and safely releasing Skills for Codex, Claude Code, and compatible agents.

## Why

Fast generation and long-term maintainability are one product promise. A useful first version must already have the right boundary, architecture, safety controls, and verification path; later changes must continue to respect the same contract.

Without that lifecycle, common failures include:

- broad or conflicting triggers;
- repeated edits that accumulate prompt debt;
- unsafe scripts, credentials, network transfer, or side effects;
- high static scores without evidence that real tasks improved;
- fixes that solve one failure while breaking old behavior;
- releases with no preview, verification, or rollback.

Skill Engineering treats those as an engineering lifecycle:

```text
discover -> decide artifact -> design -> create -> audit -> evaluate -> improve -> evolve -> shadow -> approve -> release -> verify/rollback
```

Its advantage is combining architecture-first rapid generation with lifecycle protection, so the first usable version and the 10th or 100th change follow the same engineering standard.

## Public Beta scope

The first public version focuses on a complete local workflow:

- decide whether a new Skill is justified;
- self-check existing capabilities and clarify the real task one question at a time before deciding;
- compare 2-3 relevant artifact approaches instead of defaulting to a new Skill;
- choose a minimal architecture and explicit safety boundary;
- generate a complete minimal candidate from that architecture instead of an empty prompt folder;
- preview creation and apply the exact same immutable plan;
- verify newly created Skills and clean failed scaffolds;
- maintain existing Skills through isolated candidates, complexity checks, regression evidence, verification, history, and undo;
- evaluate baseline, holdout, high-risk, and negative transfer;
- evolve candidates into immutable versions and approval-gated releases;
- guide non-expert users with result, impact, and one clear next action.

The project does not yet claim universal cross-model utility, native client permission enforcement, hosted collaboration, or automatic global publishing. See [Roadmap](docs/ROADMAP.md) and [Backlog](docs/BACKLOG.md).

For the version strategy, feature inventory, release history, and active 2.0 work, see [VERSIONING](docs/VERSIONING.md), [FEATURE-MATRIX](docs/FEATURE-MATRIX.md), [RELEASE-LOG](docs/releases/RELEASE-LOG.md), and the [v2.0 Sprint](docs/sprints/2026-07-v2.0-architecture-guardian.md).

## Version roadmap

| Version | Status | Focus |
|---|---|---|
| `0.1.0` | Released baseline | Local create, Doctor, evaluate, improve, evolve, and release governance |
| `0.1.1` | Unreleased | AST security checks, source-to-sink analysis, and SARIF |
| `1.0.0` | Stabilization planned | Stable CLI/JSON/contract, packaging, migration, and release evidence |
| `2.0.0` | In development | Blueprint/IR, Architecture Guardian, semantic diff, and migration plans |

The standalone, detailed release plan and exit gates live in [docs/ROADMAP.md](docs/ROADMAP.md). The first 2.0 slice—Blueprint schema, data models, deterministic fingerprinting, unknown/legacy preservation, and sensitive-value checks—is implemented; real Skill inventory and guardian checks remain in progress.

## Capabilities

- Decide whether a capability should be a Skill, Script, Plugin/runtime, project rule, extension, or no new artifact.
- Generate complete minimal Skills from an explicit architecture instead of applying one oversized template to every task.
- Run type-aware lint and Doctor checks for structure, behavior, security, and maintainability, including Python AST checks for dynamic execution, unsafe shells, and external-input execution flows.
- Compare baseline and candidate behavior with development, holdout, and high-risk cases.
- Prevent repeated modifications from growing duplicate rules and incident-style prompt debt.
- Generate isolated evolution candidates from repeated failures and user corrections.
- Select Pareto-efficient candidates across utility, risk, latency, cost, and complexity.
- Create immutable versions, automatic Shadow state, approved Canary/Active releases, verification, and rollback.
- Present default human feedback as result, real-world impact, and one clear next action while preserving JSON and SARIF 2.1.0 evidence for automation, CI, IDEs, and audit.

Doctor scores structural readiness. It never presents an unmeasured downstream utility claim as a score.

## Install for development

```bash
python3 -m pip install -e ".[dev]"
```

The Agent Skill source is at `skills/skill-engineering/`. Install or link that directory using your agent's Skill mechanism or Agent Skill Hub.

## Quick start

```bash
skill-engineering decide "I need a reusable article fact-checking capability" --answers answers.json
skill-engineering create --name fact-check --description "..." --target ./fact-check --json
skill-engineering create --plan <PLAN_ID> --apply
skill-engineering doctor ./fact-check --profile team
skill-engineering doctor ./fact-check --profile production --format sarif > doctor.sarif
skill-engineering evaluate \
  --suite tests/evaluation/suite.yaml \
  --baseline-results baseline.json \
  --candidate-results candidate.json
```

Creation and improvement commands are preview-first. Creation writes only through `create --plan <ID> --apply`; maintenance writes only through `improve --plan <ID> --apply`. Test and active releases also require explicit approval. Default text describes the actual action, scope, impact, and rollback boundary; internal release terms remain available in JSON and technical output.

Doctor keeps `--json` as a compatibility alias and also accepts `--format text|json|sarif`. Its AST checks are static: scanned scripts are parsed but never imported or executed.

## Repository layout

```text
skills/skill-engineering/       conversational Agent Skill entry
src/skill_engineering/    deterministic engineering and release core
tests/                    behavior and safety regression suite
docs/guides/              public engineering standards
docs/references/          evaluation and contract templates
docs/specs/               feature requirements and acceptance criteria
docs/plans/               implementation and verification plans
docs/adr/                 durable architecture decisions
docs/sprints/             bounded release cycles
docs/logs/daily/           factual daily handoffs
docs/testing/             real end-to-end test reports
```

Start at the [documentation index](docs/README.md). The project uses its own lifecycle rules to manage itself.

The latest external comparison and adoption boundaries are recorded in
[`docs/research/2026-07-15-nvidia-skillspector-comparison.md`](docs/research/2026-07-15-nvidia-skillspector-comparison.md).

## Boundaries

- Core logic is provider-neutral and does not embed an LLM API.
- Candidate content is generated by the host Agent inside isolated workspaces.
- Evaluation suites never execute arbitrary commands or third-party scripts.
- Candidate generators do not receive baseline scores or holdout assertions.
- Global and multi-project distribution belong to Agent Skill Hub; this project only performs a narrow project Canary as part of a release.

## Validation

```bash
python3 -m pytest -q
python3 -m ruff check src tests
python3 /path/to/skill-creator/scripts/quick_validate.py skills/skill-engineering
bash scripts/credential-lint.sh --all
```

The full lifecycle evidence is documented in
[`docs/testing/2026-07-11-real-e2e.md`](docs/testing/2026-07-11-real-e2e.md). The latest interaction and handoff evidence is documented in
[`docs/testing/2026-07-12-interaction-e2e.md`](docs/testing/2026-07-12-interaction-e2e.md).

## License

MIT

## Contributing and security

- [Contributing guide](CONTRIBUTING.md)
- [Security policy](SECURITY.md)

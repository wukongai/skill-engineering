# Skill Engineering

> Current stable release: `1.0.0` · next development: `2.0.0` Architecture Guardian · local-first · provider-neutral · Apache-2.0

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

## 1.0 stable scope

Version 1.0 freezes the complete local lifecycle that was validated during the public beta:

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

The project does not claim universal cross-model utility, native client permission enforcement, hosted collaboration, or automatic global publishing. Static Doctor scores remain structural readiness evidence, not downstream utility. See [Roadmap](docs/ROADMAP.md), the [1.x public contract](docs/references/v1-public-contract.md), and [Backlog](docs/BACKLOG.md).

For the version strategy, feature inventory, release history, and active 2.0 work, see [VERSIONING](docs/VERSIONING.md), [FEATURE-MATRIX](docs/FEATURE-MATRIX.md), [RELEASE-LOG](docs/releases/RELEASE-LOG.md), and the [v2.0 Sprint](docs/sprints/2026-07-v2.0-architecture-guardian.md).

## Version roadmap

| Version | Status | Focus |
|---|---|---|
| `0.1.0` | Released baseline | Local create, Doctor, evaluate, improve, evolve, and release governance |
| `0.1.1` | Folded into 1.0 | AST security checks, source-to-sink analysis, and SARIF |
| `1.0.0` | Release candidate | Stable identity, CLI/JSON/contract, packaging, migration, and release evidence |
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

## Install and choose the right artifact

Skill Engineering 有两个独立交付物：Python CLI 和 Agent Skill。安装一个不会自动安装另一个。普通用户不需要克隆仓库，统一使用标准 `skills` CLI，并显式选择当前项目或全局范围；全局暴露需先完成审计、备份并确认影响范围。

| 目标 | 推荐路径 |
|---|---|
| 贡献或修改仓库代码 | `python3 -m pip install -e ".[dev]"` |
| 试用 Agent Skill | `npx skills add ... --skill skill-engineering`；去掉 `-g` 为当前项目 |
| 使用稳定 CLI（正式 `v1.0.0` tag 后） | 从 GitHub 固定版本安装：`uv tool install "git+https://github.com/wukongai/skill-engineering.git@v1.0.0"` |
| 多项目/全局暴露 | `npx skills add ... -g`；组织化 Profile/台账再交给 Agent Skill Hub |

`1.0.0` 的 GitHub 源码、Agent Skill 和 Python wheel 使用同一版本事实源。固定 tag 的 CLI 安装命令用于稳定版本；本项目没有宣称已发布 PyPI 包。2.0 Blueprint/Architecture Guardian 仍是 Preview，不属于 1.0 稳定契约。

完整的版权范围、第三方材料、用户生成内容、升级、卸载和回滚边界见[版权与安装指南](docs/guides/licensing-and-installation.md)。

### Agent Skill 安装（标准安装器）

只安装到所有项目可用的全局范围时，使用：

```bash
npx skills add wukongai/skill-engineering --skill skill-engineering -g -a codex -y
```

在 Claude Code 中将 `-a codex` 换成 `-a claude-code`；只想让当前项目使用时去掉 `-g`。不确定宿主时可省略 `-a`，让安装器自动检测。等价的 npm 写法是：

```bash
npm exec --yes skills -- add wukongai/skill-engineering --skill skill-engineering -g -a codex -y
```

安装完成后，在对应项目中直接提出创建、检查、评测或维护 Skill 的请求即可。升级和移除使用同一个 `skills` CLI（例如 `npx skills update`、`npx skills remove`）。Python 包安装不会自动暴露这个 Agent Skill。

## Install for development

```bash
python3 -m pip install -e ".[dev]"
```

维护者和贡献者才需要克隆或 fork 源码仓库：

```bash
git clone https://github.com/wukongai/skill-engineering.git
```

这条路径用于源码学习、二次开发、运行开发测试和提交 PR，不是普通用户使用 Agent Skill 的前置条件。源码中的 Agent Skill 入口位于 `skills/skill-engineering/`。如果只想手动 project-only 接入，可将该目录链接到 `.agents/skills/skill-engineering/` 或 `.claude/skills/skill-engineering/`。

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
The four public 1.0 user journeys and their release-candidate rerun are indexed in
[`docs/testing/2026-07-18-v1-use-cases.md`](docs/testing/2026-07-18-v1-use-cases.md).

## License and copyright

Original source code, Agent Skill instructions, references, schemas, tests, examples, and documentation are licensed under Apache License 2.0 (`SPDX-License-Identifier: Apache-2.0`) unless a file says otherwise. Commercial use and redistribution are allowed; redistributors must follow the license's notice-retention and modified-file requirements. Third-party material keeps its original license, and user prompts, private data, generated Skills, and runtime outputs are not claimed by this project. See the [copyright and installation policy](docs/guides/licensing-and-installation.md), [NOTICE](NOTICE), [citation metadata](CITATION.cff), [brand policy](TRADEMARKS.md), and the full [Apache License 2.0](LICENSE).

## Contributing and security

- [Contributing guide](CONTRIBUTING.md)
- [Security policy](SECURITY.md)

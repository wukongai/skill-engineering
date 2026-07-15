# Yao Meta Skill、Superpowers 与本地五种架构模式：可复现研究与采用矩阵

日期：2026-07-16
研究仓库：`/Users/aim5/Documents/CodingProject/skill-engineering`
研究范围：只读审计公开上游与本地事实源；不复制上游实现，不修改 Agent Skill Hub，不把研究结论当作 2.0 已完成。

## 结论摘要

- **V1 保留**“先自查、逐步澄清、决定是否需要 Skill，再选择最小架构”的入口；本地五种类型是 `atomic`、`orchestrator`、`router`、`adapter`、`composite`。这与 Yao 的 method-first、archetype/boundary/gate 思路相容，但不把对方的 CLI 或目录直接搬入本项目。
- **v2.0 Architecture Guardian Phase 1 直接采用**：版本化、只读 Blueprint/IR；`unknown/legacy` 不猜测；稳定 fingerprint；fixture/negative/high-risk/migration/rollback evidence；复杂度 delta 与 preview-only 写入边界。这些内容已经在当前 Sprint 的既有任务中，不新增重复 Backlog 承诺。
- **v2.0 后续候选**：在现有 Blueprint 之上做 semantic diff、依赖/route collision、context budget、1.x 只读 inventory、迁移计划，以及与真实 baseline/holdout/negative-transfer 对齐的行为证据。Yao 的 Output Eval、conformance、trust report 可作为输入形状参考，不能作为本项目当前已交付能力的证明。
- **明确不采用/不合并**：Yao/Superpowers 的 registry、跨平台编译分发、Review Studio、telemetry/portfolio 运营面，以及 Superpowers 的自动工作流触发、插件/marketplace 安装面。Skill Hub 继续独立负责 registry/profile/adapter/安装审计/Global 与多项目暴露。

## 可复现来源与审计范围

### Yao Meta Skill

| 项目 | 固定信息 |
|---|---|
| 上游仓库 | [`yaojingang/yao-meta-skill`](https://github.com/yaojingang/yao-meta-skill) |
| 审计提交 | `4eef8d86824d3950144c96458f90a66ec3abd974`（`main` 的合并提交；GitHub 提交历史显示为 `Merge pull request #8 ... blind-human-review-evidence`） |
| 提交链接 | [`4eef8d8`](https://github.com/yaojingang/yao-meta-skill/commit/4eef8d86824d3950144c96458f90a66ec3abd974) |
| 版本状态 | 仓库没有公开 release；README 自称 1.0/2.0 产品线，故版本记为“README 2.0 line / release unknown”，不把它写成已发布 `2.0.0`。 |
| 主要证据路径 | [`README.md`](https://github.com/yaojingang/yao-meta-skill/blob/4eef8d86824d3950144c96458f90a66ec3abd974/README.md)、[`SKILL.md`](https://github.com/yaojingang/yao-meta-skill/blob/4eef8d86824d3950144c96458f90a66ec3abd974/SKILL.md)、[`references/skill-engineering-method.md`](https://github.com/yaojingang/yao-meta-skill/blob/4eef8d86824d3950144c96458f90a66ec3abd974/references/skill-engineering-method.md)、[`skill-ir/`](https://github.com/yaojingang/yao-meta-skill/tree/4eef8d86824d3950144c96458f90a66ec3abd974/skill-ir)、[`evals/`](https://github.com/yaojingang/yao-meta-skill/tree/4eef8d86824d3950144c96458f90a66ec3abd974/evals)、[`registry/`](https://github.com/yaojingang/yao-meta-skill/tree/4eef8d86824d3950144c96458f90a66ec3abd974/registry)、[`runtime/conformance/`](https://github.com/yaojingang/yao-meta-skill/tree/4eef8d86824d3950144c96458f90a66ec3abd974/runtime/conformance)、[`reports/`](https://github.com/yaojingang/yao-meta-skill/tree/4eef8d86824d3950144c96458f90a66ec3abd974/reports)。 |
| 2.0 方案补充来源 | [`Yao Meta Skill 2.0 正式升级方案`](https://doc.laoyao.cn/unyyhc)，文档版本 `1.0`，日期 `2026-06-12`。这是维护者公开的方案文档，不等同于仓库 release。 |
| 证据边界 | 本轮读取了 GitHub README/提交历史和公开 PDF；没有在本地 clone、运行 Yao CI 或复跑 provider-backed/human-review/telemetry。README 也把这些列为独立 evidence tasks，因此这里只采用“声明的能力/架构”，不宣称真实效果。 |

### Superpowers

| 项目 | 固定信息 |
|---|---|
| 插件仓库 | [`obra/superpowers`](https://github.com/obra/superpowers) |
| 审计提交与版本 | `d884ae04edebef577e82ff7c4e143debd0bbec99`，提交标题 `Release v6.1.1...`，插件 manifest 版本 `6.1.1`。 |
| 提交链接 | [`d884ae0`](https://github.com/obra/superpowers/commit/d884ae04edebef577e82ff7c4e143debd0bbec99) |
| 主要证据路径 | [`README.md`](https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/README.md)、[`.codex-plugin/plugin.json`](https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/.codex-plugin/plugin.json)、[`RELEASE-NOTES.md`](https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/RELEASE-NOTES.md)。 |
| 技能库边界 | README/Release Notes 说明技能曾拆到 [`obra/superpowers-skills`](https://github.com/obra/superpowers-skills)，该仓库页面标记为 `archived`、只读；其提交历史最新可见提交为 `cdcd624ad3fd8026deb692e565351854569798dd`，本研究不把它伪装成当前插件的可变主线，也不据此宣称技能内容与 `d884ae0` 同步。 |
| 审计范围 | 只审计“brainstorm/spec → plan → TDD/执行 → review/verify”的方法论、插件 manifest 和安装边界；不复跑其完整 harness/evals，不引入其插件安装或自动触发行为。 |

### 本地“五种 Skill 架构设计模式”

仓库没有一个独立、带版本号的“五种模式”文件；因此不能杜撰文件版本或发布日期。可复核的本地枚举来自：

- [`docs/specs/2026-07-13-v0.1-public-beta-spec.md`](../specs/2026-07-13-v0.1-public-beta-spec.md) 的架构选择条款；
- [`skills/skill-engineering/references/capability-brainstorming.md`](../../skills/skill-engineering/references/capability-brainstorming.md) 的 `atomic/orchestrator/router/adapter/composite` 选择步骤；
- [`skills/skill-engineering/references/evaluation-standard.md`](../../skills/skill-engineering/references/evaluation-standard.md) 的类型专属失败面；
- [`skills/skill-engineering/references/selection-matrix.md`](../../skills/skill-engineering/references/selection-matrix.md) 的产物判断边界。

因此本研究将“本地五种模式”记录为：`atomic`（单一能力）、`orchestrator`（跨阶段编排）、`router`（路由/回退）、`adapter`（provider/格式绑定）和 `composite`（多能力选择与一致输出）。这是**本地事实的归纳**，不是外部标准；`component role` 的 Blueprint 扩展角色仍可包含 `entry/reference/script/test`。

## 能力采用矩阵

| 能力/模式 | Yao/Superpowers 证据 | Skill Engineering 当前能力 | V1/V2 归属 | 采用/不采用/延后 | 理由与风险 |
|---|---|---|---|---|---|
| 先判断是否需要 Skill（brainstorm/decide） | Yao README 的 method-first、non-skill decisions；Superpowers README 的先退一步澄清目标 | `capability-brainstorming.md`、`selection-matrix.md` 已要求自查、一次一个问题、比较 2–3 个产物 | V1 | **采用并保持** | 这是入口边界，不应变成强制创建；风险是把澄清流程误当成产品治理入口。 |
| 五种最小架构模式 | Yao 的 archetype/boundary；本地 v0.1 Spec 明确五种类型 | 选择与评测标准已覆盖类型专属失败面 | V1；Blueprint Phase 1 fixture | **采用** | 用作最小分类和 fixture 维度；不把每个 Skill 强行升级为 composite。 |
| 根入口薄、progressive disclosure | Yao README/SKILL 方法论；Superpowers 以可组合 SKILL.md 组织工作流 | 根 `skills/skill-engineering/SKILL.md` 路由，细节放 references/stages | V1 | **采用** | 可降低 context 成本；不能用“薄”掩盖缺失 contract 或 evidence。 |
| Product/Spec/Plan/Backlog/Sprint/Daily Log/ADR | Yao 有 governance/reports/release evidence；Superpowers 有 spec、plan、TDD/ review 流程 | 本仓库已有正式事实源和 `development-governance.md` | V1 稳定化 | **采用本地治理** | 吸收职责分层，不复制 Yao/ Superpowers 文件树；避免 Backlog 与当前 Sprint 重复记账。 |
| 同一 immutable plan、preflight/postflight、verify/undo | Superpowers 强调计划后执行、测试与验证；Yao 强调 release locks、evidence gate | maintenance protocol、create preview/apply、复杂度 delta、verify/undo 已存在 | V1；Guardian 写边界 | **采用并作为硬边界** | 防止“越改越乱”；Guardian 只能生成 preview，不直接 apply。 |
| Blueprint/IR 与 unknown/legacy | Yao Skill IR、platform-neutral contract；Superpowers 无同等架构事实层 | v2.0 Blueprint schema/model、canonical JSON、fingerprint、unknown/legacy 已有基础 | v2.0 Phase 1 | **采用（当前 Sprint）** | 先稳定事实层再做 Guardian；不得把推断写成事实。 |
| atomic/router/orchestrator/adapter fixture 与 negative/high-risk | Yao 有 failure library/evals；Superpowers 有 TDD/verification workflow | Sprint 明确四种 fixture、真实 inventory 和 evidence 尚未收口 | v2.0 Phase 1 | **采用（当前任务）** | 直接补齐当前 Sprint 退出条件，不另开 Backlog 项。 |
| 只读 inventory、semantic diff、依赖/route collision | Yao README 的 IR、reports、adapters、drift；Superpowers 主要是代码工作流而非 portfolio Guardian | Spec/Plan 已定义只读 inventory、semantic diff、依赖和 collision 的后续阶段 | Phase 1 inventory；后续 Guardian | **延后分阶段** | 先 fixture/schema，再实现只读 inventory；不提前接 apply。 |
| Output Eval（with/without baseline、holdout、blind/adversarial） | Yao README 的 Output Eval Lab；2.0 方案明确 baseline、blind、adversarial、failure taxonomy | `evaluate` 已做确定性 baseline/holdout/high-risk/negative-transfer；无 provider/LLM judge | V1 已有；v2 后续扩展 | **采用证据形状，延后扩展** | 不把“有报告”当作 utility；保留 provider-neutral 与确定性 hard gate。 |
| runtime conformance / trust / secret / package hash | Yao 2.0 方案与 README 的 conformance、trust、install simulation | Doctor、credential lint、provider contract、安装指南已有局部门禁 | v2 后续 / 1.0 安装前置 | **延后，分层吸收** | 先完善本地 contract 和安装审计；不新增云端 runtime 或复制 trust report。 |
| 编译器、跨平台 target adapter | Yao Skill IR/compiler/adapters；Superpowers 多 harness plugin manifests | Skill Engineering 只维护本地 Skill 生命周期；Python CLI 与 Agent Skill 暴露分离 | v2.0 之后 | **不纳入当前核心** | 跨平台分发和 adapter 属于 Hub/未来产品面；当前引入会重新合并两个仓库。 |
| registry、profile、安装、Global/多项目暴露 | Yao registry/Atlas；Superpowers plugin marketplace/各 harness 安装 | `docs/architecture.md` 与 install governance 明确由 Agent Skill Hub 负责 | Hub 边界 | **明确不采用到本项目** | Skill Engineering 可读入安装证据/Project Canary，但不拥有 registry/profile/Global。 |
| Review Studio、HTML gate、telemetry、adoption drift | Yao 2.0 Review Studio、metadata-only telemetry、SkillOps | 本地以 Markdown/JSON evidence、maintenance history 和 release record 为主 | v2.0 后续/商业方向 | **延后或不采用** | 需要独立产品决策、隐私边界和真实 adoption 数据；不把未交付能力写成现状。 |
| 自动 subagent-driven development、自动 plugin bootstrap | Superpowers README 的 subagent-driven development、自动触发和插件安装 | Skill Engineering 只提供候选/维护计划和 approval boundary | 明确不采用 | **不采用** | 会扩大副作用与宿主耦合；本项目继续要求用户批准写入、安装和发布。 |

## Skill Hub 与 Skill Engineering 的边界

| 领域 | Agent Skill Hub 负责 | Skill Engineering 负责 | 交界处允许的证据 |
|---|---|---|---|
| registry | source、版本、owner、登记、去重 | 不维护全局 registry | 读取 pinned source/manifest，不改 Hub registry |
| profile | project/profile/global 暴露范围、symlink、路由可见性 | 不决定 Global/Profile 安装 | 将暴露范围作为 install finding 或 Blueprint dependency 的只读输入 |
| adapter | harness/plugin/provider 的安装适配与入口对齐 | 不实现跨平台 compiler/adapter | Skill Engineering contract 可声明 adapter 依赖与兼容性，但不执行安装 |
| 安装审计 | 安装来源、包校验、权限、重复暴露、撤销/升级 | 对被维护 Skill 做 Doctor/credential lint/contract 检查 | Project Canary 只能随 release plan 产生；无自动 Global/公开发布 |
| Skill 生命周期 | Hub 不拥有 create/improve/evaluate/evolve 的内部计划 | Skill Engineering 拥有 preview、immutable plan、postflight、verify、undo、release evidence | 通过 manifest、fingerprint、contract 和审计结果交接，不共享状态目录 |

## Unknown 与阻塞记录

- **Yao release unknown**：仓库页面显示没有公开 release；“2.0 line”是 README/方案叙事，不等于已发布版本。采用提交 SHA 固定研究快照。
- **Superpowers skills source split**：插件仓库在 v6.x 仍提供 manifest/安装说明，但技能库曾拆到一个已归档的仓库；本轮不推断两个仓库的同步关系，也不把归档库当作可持续上游。
- **本地五模式独立文档 unknown**：没有独立路径、版本或日期；使用本地多个规范的交叉证据，并在后续若建立单独模式文档时再固定版本。
- **上游运行验证未完成**：本地 `curl` 访问 `api.github.com` 因 DNS/网络不可达（`curl: (6) Could not resolve host: api.github.com`）；浏览器检索仍能读取 GitHub 页面和 Yao PDF。没有因此猜测 CI、provider-backed eval、human review 或 telemetry 的真实通过率。
- **当前 Sprint 状态**：fixture、只读 inventory、真实 evidence 仍是 `docs/sprints/2026-07-v2.0-architecture-guardian.md` 的未完成任务；本研究不把它们标记为已交付。

## 对事实源的同步决策

- `docs/TASK.md`：只增加本研究资产链接和“研究闭环完成”记录；Phase 1 的 fixture/inventory/evidence 仍保持未完成。
- `docs/BACKLOG.md`：不加入 Blueprint/IR、Guardian、fixture 或 inventory 重复项；仅保留一个跨版本的“上游来源复核/本地五模式清单维护”候选（若确有维护价值）。
- 当前 Sprint：不扩张范围；研究矩阵把已有 Phase 1 任务作为采用落点，未新增并行承诺。
- 不修改 Agent Skill Hub、标准 Skill CLI 安装、许可证策略、identity verification 或 `uv.lock`。

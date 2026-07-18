# Skill Engineering Product Roadmap

本文件是版本规划的单一入口，独立回答：当前发布了什么、1.0 要稳定什么、2.0 正在开发什么、什么条件满足才算发布。

## 版本总览

| 版本 | 状态 | 核心定位 | 发布结论 |
|---|---|---|---|
| `0.1.0` | 已发布基线 | Public Beta 本地生命周期闭环 | 已发布 |
| `0.1.1` | 已并入 1.0 | Security Doctor：AST、source-to-sink、SARIF | 不单独发布 |
| `1.0.0` | Stable | Stable Lifecycle Contract | 本地与远程安装门禁通过，正式发布 |
| `2.0.0` | 当前开发 | Architecture Guardian | Phase 1 进行中 |

当前代码包版本为 `1.0.0` Stable；tag 目标、GitHub Release 内容和远程默认分支安装验证绑定同一发布提交。“2.0 开发中”不表示 2.0 已发布或可以替代 1.x 稳定契约。

## `0.1.x`：本地生命周期基线

### 已交付能力

- 判断一个需求应该成为 Skill、Script、Plugin/runtime、项目规则或不新增产物；
- 从第一版开始按最小架构和安全边界生成完整候选；
- 创建 Preview → 同一 immutable plan Apply → postflight/失败清理；
- lint、Doctor、确定性 baseline/holdout/high-risk/negative-transfer 评测；
- 隔离候选、复杂度 diff、维护记录、verify 和 undo；
- evolution proposal、Pareto、immutable version、Shadow/Canary/Active；
- Product、Architecture、Spec、Plan、ADR、Sprint、Daily Log 和发布证据。

### `0.1.1` Unreleased 增量

- `SEC108-SEC111`：动态执行、动态导入、不安全 shell、外部输入到执行 sink；
- `doctor/audit --format sarif`；
- SkillSpector 对比、规则 fixture 和安全回归。

### 已由 1.0 收口的限制

- CLI/JSON/contract/record 已冻结为 1.x 兼容接口；
- wheel、干净环境安装和升级/回滚说明已进入 1.0 发布门禁；
- 静态结构健康不等于真实任务效用；
- 不自动 Global 安装或公开发布。

## `1.0.0`：Stable Lifecycle Contract

### 目标

1.0 不继续扩张主架构，而是把 0.1.x 已验证能力变成用户可长期依赖的稳定产品。

### 必须交付

- 稳定 CLI、错误码、JSON、contract、plan、record 和 schema version；
- 0.1.x 输入的兼容读取、明确迁移错误和废弃周期；
- wheel 构建、干净环境安装、Python 支持矩阵和 smoke；
- baseline、holdout、high-risk、negative-transfer 和独立评审组成的 release evidence；
- maintenance/release verify、rollback 和历史记录可复现；
- README、版本源、Changelog、Roadmap、发布日志和测试证据一致。

### 实施阶段

1. **Contract inventory**：列出所有公开/preview/internal 接口；
2. **Compatibility**：冻结 schema，补旧格式读取和迁移；
3. **Packaging**：wheel、安装 smoke 和支持矩阵；
4. **Evidence**：固定发布证据、独立评审和回滚；
5. **Release Candidate**：完整门禁通过后生成 RC，用户批准后才 tag/publish。

### 1.0 发布门禁

- 所有公开接口有 schema/version 和回归；
- 干净环境安装与升级/回滚 smoke 通过；
- production evidence 不只是声明，而是可重算的行为报告；
- pytest、Ruff、Skill validation、production Doctor、credential lint、diff check 全通过；
- commit、push、tag 和公开发布分别获得授权。

当前 RC 事实源：[`v1.0 Sprint`](sprints/2026-07-v1.0-stable-contract.md)、[`1.x 公开契约`](references/v1-public-contract.md)、[`兼容与回滚`](guides/v1-compatibility.md)、[`四个 Use Case`](testing/2026-07-18-v1-use-cases.md)。

### 不进入 1.0

- Blueprint/IR 主架构；
- 云端协作、RBAC、托管评测；
- 自动 Global 发布；
- 用单一静态分数宣称真实效用。

## `2.0.0`：Architecture Guardian（当前开发）

### 目标

2.0 让 Skill Engineering 从“检查单个 Skill 是否健康”升级为“持续守护整个 Skill 架构”：机器能够理解组件职责、执行拓扑、治理等级、依赖、路由冲突和 context budget，并对架构变化生成可审计计划。

### Blueprint 三轴

1. **Component role**：entry、atomic、router、orchestrator、adapter、reference、script、test；
2. **Execution topology**：entrypoint、stage、delegate、state、side effect、rollback；
3. **Governance level**：personal、team、production、commercial 及其证据要求。

### Phase 1：Blueprint/IR 契约（当前 Sprint）

- [x] Blueprint JSON schema `1.0.0`；
- [x] Python Blueprint/Topology/Governance/Dependency 数据模型；
- [x] canonical JSON、确定性 SHA-256 fingerprint；
- [x] unknown/legacy 和未知 extensions 保留；
- [x] Blueprint 敏感值门禁与基础回归；
- [ ] atomic/router/orchestrator/adapter fixtures；
- [ ] 从真实 1.x Skill/contract 生成只读 inventory；
- [ ] schema、negative、migration、rollback 和 high-risk 完整证据。

### Phase 2：Guardian checks

- 依赖图、未声明依赖和循环依赖；
- 重复职责、route collision 和 trigger overlap；
- context budget、入口厚度和 progressive disclosure；
- state/side-effect/rollback 与治理等级适配度；
- 每个 finding 包含证据路径、severity、remediation 和 regression contract。

### Phase 3：Semantic Diff 与维护计划

- baseline/candidate 的组件新增、删除和职责变化；
- 执行拓扑、依赖、安全边界和治理等级变化；
- 将 guardian finding 转为 create/improve preview plan；
- 继续使用 target/candidate/plan fingerprint、审批、postflight、verify 和 undo。

### Phase 4：迁移与 2.0 RC

- 生成拆分、迁移、压缩和废弃候选；
- 1.x contract/plan/record 的只读导入和迁移报告；
- behavior baseline/holdout/high-risk/negative-transfer 验证；
- 2.0 RC、升级/回滚指南和发布记录。

### 2.0 兼容承诺

- 读取 1.x Skill 和 contract，不要求用户一次性重写；
- 缺失架构事实使用 `unknown/legacy`，不让模型编造；
- 所有架构修改先生成 preview plan，不自动 Apply；
- Guardian 不替代 Doctor、evaluate 或 Agent Skill Hub；
- 2.0 schema 破坏性变化必须提供 migration 和 rollback。

### 2.0 发布门禁

- Blueprint inventory 对同一输入可重复且 fingerprint 稳定；
- semantic diff 能区分文本变化与架构变化；
- negative/high-risk case 证明不会自动修改生产 Skill；
- 1.x 兼容 fixture 和迁移/回滚 E2E 通过；
- 真实仓库验证不降低 0.1.x/1.x protected behavior；
- 完整工程门禁和独立发布授权通过。

## 2.0 之后

| 方向 | 归属 | 说明 |
|---|---|---|
| Skill Portfolio、owner、stale、多项目依赖图 | `2.1+` | 与 Agent Skill Hub 的 registry/profile 边界对齐 |
| Behavior Eval Lab、provider-neutral rollout runner | 2.0 后续实验轨道 | without/with-skill、pressure、multi-turn、跨模型矩阵 |
| 安装模拟、升级兼容、供应链证据 | `2.1+` | 依赖 1.0 稳定 contract 和 2.0 Blueprint |
| 云端协作、RBAC、托管评测、SLA | 未来商业版本 | 不进入当前开源核心 Sprint |

旧 Roadmap 中的 `v0.2 Architecture Guardian` 已升级为 `2.0`；`v0.3 Behavior Eval Lab` 和 `v0.4 Portfolio/Distribution` 保留为 2.0 后续方向，不再作为当前 0.x 发布承诺。

## 版本执行规则

- 当前承诺以 `docs/TASK.md` 和当前 Sprint 为准；
- 功能开发必须先有 Spec 和 Plan，跨版本结构取舍必须有 ADR；
- Unreleased、Preview、RC 和 Stable 必须明确区分；
- 结构分数、evidence-declared 和真实行为效用分别报告；
- commit、push、tag、公开发布和 Global 安装是独立授权点。

相关入口：[`VERSIONING.md`](VERSIONING.md)、[`FEATURE-MATRIX.md`](FEATURE-MATRIX.md)、[`releases/RELEASE-LOG.md`](releases/RELEASE-LOG.md)、[`sprints/2026-07-v2.0-architecture-guardian.md`](sprints/2026-07-v2.0-architecture-guardian.md)。

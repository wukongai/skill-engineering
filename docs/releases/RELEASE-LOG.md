# Skill Engineering 发布日志

## 版本总览

| 版本 | 阶段 | 核心定位 | 当前结论 |
|---|---|---|---|
| `0.1.0` | Stable baseline | Public Beta 本地闭环 | 已发布基线 |
| `0.1.1` | Folded into 1.0 | Security Doctor 强化 | 不单独发布 |
| `1.0.0` | Release Candidate | Stable Lifecycle Contract | 安装器发现门禁通过；Agent Skill-only runtime 与 tag 待完成 |
| `2.0.0` | In Development | Architecture Guardian | 当前开发主线 |

## Unreleased 文档治理

2026-07-16：首次明确 MIT 版权范围、第三方/用户内容/商标边界和 CLI/Agent Skill 双轨安装指南。

2026-07-18：在首个稳定 tag 前，经 ADR 0006 将当前仓库和 v1.0 候选迁移为 Apache-2.0，版权人为“艾笑”；新增 `NOTICE`、`CITATION.cff` 和品牌使用说明。历史 MIT 副本继续按其取得时的条款使用。该治理不等于 1.0 已正式发布，tag 和 GitHub Release 仍是独立门禁。

## `0.1.0` — Public Beta

日期：2026-07-15

### 已交付

- 需求发现、产物判断和最小架构选择；
- Skill 创建 Preview/Apply、postflight 和失败清理；
- lint、Doctor、确定性行为评测；
- Skill 改进、演进候选、Pareto、Shadow/Canary/Active；
- Product/Architecture/Spec/Plan/ADR/Sprint/Daily Log 自举治理；
- README、CI、凭证 lint 和发布安全边界。

### 发布门禁

pytest、Ruff、production Doctor、凭证 lint、diff check、隔离 E2E 均通过。

## `0.1.1` — Security Doctor（Unreleased）

日期：2026-07-15 完成实现

### 新增

- `SEC108`：动态代码执行；
- `SEC109`：动态编译/导入；
- `SEC110`：不安全 shell 执行；
- `SEC111`：外部输入到执行 sink 的局部 source-to-sink 关联；
- `doctor/audit --format sarif`；
- SkillSpector 对比研究、回归 fixture 和版本化文档。

### 当前状态

实现、验证、commit 和 push 已完成：变更位于 `c58d389` / `codex/version-roadmap`，并已建立 Draft PR #2。该增量后来并入 `1.0.0` RC，不再创建单独的 `v0.1.1` tag。

## `1.0.0` — Stable Lifecycle Contract（Release Candidate）

日期：2026-07-18

### 版本目标

把 0.1.x 已证明的能力收敛成可长期依赖的稳定产品：用户可以依赖 CLI、JSON、contract、计划、验证和回滚语义；新增能力不再通过隐式改变旧行为实现。

### 必须交付

- 稳定 CLI/API/JSON schema 与 schema version；
- `pyproject.toml`、运行时版本、README、Changelog 和发布日志一致；
- wheel 构建、安装 smoke、Python 支持矩阵和升级/回滚说明；
- production release evidence：baseline、holdout、high-risk、negative-transfer 和独立评审；
- 维护计划、撤销和 release record 的可复现验证；
- 1.x 兼容策略、废弃周期和迁移文档。

### 不进入 1.0

不引入新的 Blueprint/IR 主架构、不做云端协作、不自动 Global 发布、不把静态分数当作真实效用。

对应工件：[`1.0 Spec`](../specs/2026-07-16-v1.0-stable-contract-spec.md)、[`1.0 Plan`](../plans/2026-07-16-v1.0-stable-contract-plan.md)。

### RC 实施状态

- 唯一身份和远程安装命令已冻结；
- 1.x 公开契约、0.1.x schema 兼容和升级/回滚指南已完成；
- 版本源已切换为 `1.0.0`，自动一致性检查已加入 CI；
- 四个 Use Case 和完整本地门禁已在同一候选上通过；
- 默认分支已推送，标准安装器只发现并安装一个 `skill-engineering`；远程副本 Skill validation 与 production Doctor 在 Python CLI 已可用的验证环境中通过；Agent Skill-only runtime/bootstrap 仍是发布阻断；
- 发布候选许可证在正式 tag 前迁移为 Apache-2.0；许可证资产、包元数据、用户文档和发布材料已对齐，131 项测试、完整门禁、wheel/sdist 核验与 PM 独立复核通过；
- tag 和 GitHub Release 尚未执行，等待用户单独批准。

## `2.0.0` — Architecture Guardian（当前开发）

### 版本目标

让 Skill Engineering 不只检查“这个 Skill 有没有问题”，还能够回答“这次修改是否破坏了整个 Skill 架构”：组件职责、执行拓扑、治理等级、依赖、冲突和 context budget 都有机器可读证据。

### 开发顺序

1. Blueprint/IR 契约和版本化 schema；
2. 从现有 Skill/contract 生成只读 Blueprint；
3. 架构适应度、依赖图、重复职责和 route collision 检查；
4. semantic diff 与维护计划联动；
5. 自动生成拆分、迁移、压缩和废弃候选；
6. 与 1.x contract、Doctor、evaluate 和 release evidence 对齐。

### 已完成的 2.0 起步能力

- Blueprint schema `1.0.0`（schema 版本与产品版本独立演进）；
- Python Blueprint/Topology/Governance/Dependency 数据模型；
- canonical JSON 与确定性 SHA-256 fingerprint；
- unknown/legacy 显式状态和未知字段 extensions 保留；
- Blueprint extensions 中敏感值拦截；
- round-trip、schema、duplicate、migration 和 secret regression。

尚未完成：从真实 Skill 自动提取 inventory、guardian checks、semantic diff 和 apply integration。

### 2.0 的兼容承诺

- 读取 1.x Skill 和 contract，不要求下游一次性重写；
- 先提供只读 inventory/preview，再提供 apply；
- 任何迁移都生成可审计计划、回归要求和撤销入口；
- 不替代 Agent Skill Hub 的 registry/profile/多项目分发职责。

对应工件：[`2.0 Spec`](../specs/2026-07-16-v2.0-architecture-guardian-spec.md)、[`2.0 Plan`](../plans/2026-07-16-v2.0-architecture-guardian-plan.md)、[`2.0 Sprint`](../sprints/2026-07-v2.0-architecture-guardian.md)。

## 发布决策规则

完成代码不等于完成发布。每个版本必须经过对应 Spec/Plan、测试证据、兼容检查和用户授权；commit、push、tag、公开发布仍分别确认。

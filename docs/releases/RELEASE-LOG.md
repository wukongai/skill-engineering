# Skill Engineering 发布日志

## 版本总览

| 版本 | 阶段 | 核心定位 | 当前结论 |
|---|---|---|---|
| `0.1.0` | Stable baseline | Public Beta 本地闭环 | 已发布基线 |
| `0.1.1` | Folded into 1.0 | Security Doctor 强化 | 不单独发布 |
| `1.0.0` | Stable | Stable Lifecycle Contract | 本地与远程 runtime 门禁通过；正式发布 |
| `1.1.0` | Stable | Native Authoring | 2026-08-01 正式发布；正式 Tag 用户回归已完成，`passed_with_limitations`、无阻断 |
| `1.1.1` | Next / P2 | Maintenance Tiers & Versioning | 2026-08-01 非计划任务已登记；Handoff 已准备，Spec/Plan 待完成 |
| `2.0.0` | Paused | Architecture Guardian | Phase 1 在 1.1 期间暂停 |

## 1.0 发布治理记录

2026-07-16：首次明确 MIT 版权范围、第三方/用户内容/商标边界和 CLI/Agent Skill 双轨安装指南。

2026-07-18：在首个稳定 tag 前，经 ADR 0006 将当前仓库和 v1.0 候选迁移为 Apache-2.0，版权人为“艾笑”；新增 `NOTICE`、`CITATION.cff` 和品牌使用说明。历史 MIT 副本继续按其取得时的条款使用。许可证治理完成后，tag 与 GitHub Release 又分别获得明确授权并于同日正式发布。

## `1.1.0` — Native Authoring（Stable）

发布日期：2026-08-01

### 版本目标

创建主链路自包含：普通用户只安装 `skill-engineering`、只描述目标，即可在交互引导下得到任务专属、内容完整的 Skill，并在创建终点获得评审分数和简易自动化测试入口（ADR 0008）。

### 正式发布内容

- Authoring Brief 契约与原生完整候选生成，移除 official skill-creator delegate；
- Content Completion Gate（portable checker + Agent-native 等价清单）与 `scaffold_only` 降级语义；
- Doctor v2 portable creation profile、六态用户可见状态机、声明式真实脚本自测；
- `native_plan.py preview → apply → verify`，绑定脱敏 Brief、候选 manifest、
  target preflight 与创建评审，任一漂移拒绝 Apply；
- 宿主适配契约（Codex、Claude Code、Hermes、Pi、Kimi CLI）与 Case E 跨宿主 fixture；
- 1.0 CLI/JSON/contract 兼容回归与 1.0→1.1 迁移说明。

### 发布门禁状态

2026-07-30 Codex remediation 已通过 211 项 pytest、Ruff、Skill lint、
production Doctor 100/A、portable self-test、credential lint、release consistency
和 diff check；安装产物在 `python -I -S` 下完成 Content Gate、portable review、
Native Plan 与 self-test 隔离 smoke。
Case A–F 历史与修复证据见
[`1.1 验收证据`](../testing/2026-07-29-v1.1-native-authoring-cases.md)。

Codex 无 Creator E2E 已完成 runtime failure → `needs_improvement` → 候选修复 →
同一 Native Plan Apply/Verify → 写后自测 → 真实样本 `validated`。

K3 remediation 终审已 `approved`。根据 ADR-0009，Codex 是默认唯一必须通过的
真实宿主 E2E；Hermes、Claude Code、Pi、Kimi CLI 真实 smoke 是非阻断兼容性
证据，五宿主 adapter contract fixture 仍是发布门禁。静态通过和 adapter
fixture 不证明非 Codex 宿主的真实任务效用。

2026-07-31 canonical host 策略同步后复验：212 项 pytest、Ruff、Skill lint、
production Doctor 100/A、portable self-test、credential lint、release
consistency 和 diff check 全部通过。策略与三方评估收口提交为 `2227e2a`，
已推送到 `origin/codex/version-roadmap`。

同一冻结候选的三方评估中，项目原生门禁全绿，Alibaba Skill Up 驱动的真实
Codex 四个核心场景 4/4 通过；Microsoft Waza/Copilot 发现的一次一问兼容性
问题、入口预算告警和额度阻塞均作为非阻断证据保留。完整报告见
[`2026-07-31-v1.1-three-way-evaluation.md`](../testing/2026-07-31-v1.1-three-way-evaluation.md)。

### 正式发布决策与验证边界

Owner 于 2026-08-01 明确授权 merge、双远程 push、annotated tag `v1.1.0` 和
GitHub Release。发布前重新执行全量门禁、构建 wheel/sdist 并完成干净环境
安装 smoke。

正式 Tag 的远程安装、普通用户从模糊需求创建全新 Skill、真实任务试用、失败
修复与维护回归转入发布后独立项目。该项只能在正式 Tag 可用后完整执行，不阻断
本次已授权发布；当时约定在报告完成前不宣称覆盖所有宿主或生产环境。决策记录见
[`2026-08-01-v1.1-release-decision.md`](../testing/2026-08-01-v1.1-release-decision.md)。

### 发布后完整用户回归

正式 Tag 用户回归已于 2026-08-01 在全新独立 Codex 项目完成：精确 Tag
project-local 安装、新手逐轮创建、17 条合成反馈真实试用、未授权 Slack 自动发送
阻断、收窄为只读草稿、维护记录、真实 undo 与最终重应用均通过。结论为
`passed_with_limitations`，无阻断问题；完整证据见
[`2026-08-01-v1.1-post-release-user-regression.md`](../testing/2026-08-01-v1.1-post-release-user-regression.md)。

### 正式发布结果

- 发布提交：`1f6508db4ad5ace606f739f7ec2329d671beb109`；
- annotated tag：`v1.1.0`，GitHub/Gitee 均解析到同一发布提交；
- GitHub Release 已正式发布：
  <https://github.com/wukongai/skill-engineering/releases/tag/v1.1.0>；
- wheel 与 sdist 已上传，远程下载后的 SHA-256 与发布前构建结果一致；
- 公开 Tag 隔离克隆后的 Content Completion Gate 与 portable self-test 通过。

完整事实见
[`2026-08-01-v1.1-release-verification.md`](../testing/2026-08-01-v1.1-release-verification.md)。

## `1.1.1` — Maintenance Tiers & Versioning（Next / P2）

日期：2026-08-01

本版本作为非计划 P2 任务登记，目标是建立 hotfix/feature/refactor 分流、当前
阻断与结构债务分离、分级回归，以及 SemVer/Changelog/MaintenanceRecord
闭环。当前只有 Handoff 与任务入口，Spec/Plan 和实现尚未完成；该范围不并入
已经冻结并发布的 `1.1.0` 内容。恢复入口见
[`2026-08-01-v1.1.1-maintenance-versioning-next.md`](../handoffs/2026-08-01-v1.1.1-maintenance-versioning-next.md)。

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

## `1.0.0` — Stable Lifecycle Contract

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

### 正式发布状态

- 唯一身份和远程安装命令已冻结；
- 1.x 公开契约、0.1.x schema 兼容和升级/回滚指南已完成；
- 版本源已切换为 `1.0.0`，自动一致性检查已加入 CI；
- 四个 Use Case 和完整本地门禁已在同一候选上通过；
- 默认分支已推送，标准安装器只发现并安装一个 `skill-engineering`；Skill-only 环境缺少 CLI 时给出确定性安装指引，同一远程候选安装 CLI 后 create preview/apply 与 team Doctor 完整通过；
- 发布候选许可证在正式 tag 前迁移为 Apache-2.0；许可证资产、包元数据、用户文档和发布材料已对齐，131 项测试、完整门禁、wheel/sdist 核验与 PM 独立复核通过；
- runtime 修复后全量门禁为 133 passed，Ruff、官方 Skill validation、production Doctor 100/A、credential lint 和 diff check 通过；
- 用户已单独批准 `v1.0.0` tag 和 GitHub Release；annotated tag 已指向发布提交 `c841c59`。
- GitHub Release 已正式发布并设为 Latest：<https://github.com/wukongai/skill-engineering/releases/tag/v1.0.0>。
- 发布附件已上传：`skill_engineering-1.0.0-py3-none-any.whl`、`skill_engineering-1.0.0.tar.gz`。

## `2.0.0` — Architecture Guardian（暂停）

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

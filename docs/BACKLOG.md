# Backlog

Backlog 保存尚未进入当前 Sprint 的候选能力。进入实现前必须升级为 Spec、Plan 和 Task。

Blueprint/IR 与 Architecture Guardian 已经从 Backlog 升级到当前 `v2.0 Phase 1` Sprint；不要在 Backlog 中重复承诺同一范围。

`1.1.0 Native Authoring` 已于 2026-07-29 升级为当前 Sprint（Spec、Plan、ADR 0008），不在 Backlog 重复；创建后阅读、注释和 Skill Graph 保持 `1.2.0` Backlog 候选，不进入 1.1。

## 2026-07-16 Review Closure

- NVIDIA/SkillSpector 对比、AST/source-to-sink/SARIF 吸收和 0.1.1 验证已完成，不再作为 Backlog 候选。
- 2.0 Phase 1 尚未完成的 fixture、只读 inventory 和 evidence 收口属于当前 Sprint，已记录在 [`v2 Phase 1 Handoff`](handoffs/2026-07-16-v2-phase1-next.md)，不重复塞入 Backlog。
- `v1.0.0` tag、公开发布和稳定契约已于 2026-07-18 完成；更远期架构扩展继续遵守各自 Sprint 与发布门禁。
- 版权与安装边界已升级为 v1.0 发布前置项，事实源为 `docs/guides/licensing-and-installation.md`、2026-07-18 Apache-2.0 Spec/Plan 和 ADR 0006；不在 Backlog 重复拆分。
- Agent Skill-only runtime 依赖检测已通过独立 Spec/Plan 和远程闭环完成，不再作为 Backlog 候选。

## Behavior Evaluation Lab：Skill CI 与 A/B 自动化测试引擎

状态：`research complete / backlog / not in current Sprint`

研究基线：[`Microsoft Waza 对比研究`](research/2026-07-20-microsoft-waza-comparison.md)

目标不是接入或复制 Waza，而是完整学习其公开测试体系，在 Skill Engineering 的 provider-neutral、holdout、防漂移、审批和发布边界下 clean-room 重写等价能力。现有 `evaluate` 继续负责读取 baseline/candidate 证据、development/holdout、negative transfer 和接受判断；本 Epic 补齐上游真实执行、grader、trial、统计、CI 和 replay。

### BEL-0：竞品研究与问题定义（Done）

- [x] 核实 `microsoft/waza` 身份并固定 commit `cf05e487ed967d497a138738514d24457bc45f2a`；
- [x] 审计 runner、baseline、grader、gate、snapshot、redaction、adversarial、dashboard 和测试结构；
- [x] 确认现有 Skill Engineering 有 A/B 结果比较器，但没有自动行为测试 runner；
- [x] 固定 clean-room 原则、采用范围、非目标和调研限制；
- [x] 创建下一任务 handoff。

### BEL-1：内部分析与能力契约（Next）

- [ ] 盘点 `evaluation.py`、evolution、release evidence、contract、Doctor 和 CLI 的现有调用关系；
- [ ] 建立 Waza capability parity 矩阵，逐项标注 adopt/adapt/defer/reject；
- [ ] 定义 personal/team/production 三档测试成本与默认行为；
- [ ] 定义 without-skill/current/candidate、development/holdout、success/failure/high-risk 的正交关系；
- [ ] 明确 provider、工具权限、网络、凭证、外部副作用、program grader 和 hook 的 trust model；
- [ ] 评估 Evaluation Suite/Result v2 对 1.x schema、CLI 和 release evidence 的迁移影响；
- [ ] 产出 ADR、Spec、Plan；未完成前不得修改正式实现。

### BEL-2：版本化实验与证据模型

- [ ] Evaluation Suite v2：task、fixture、split、category、subject matrix、trial、grader 和 gate；
- [ ] Run Artifact v2：runner/model/environment、trajectory、tool call、workspace diff、usage、duration、redaction 和 artifact pointer；
- [ ] 旧 1.x suite/results 兼容读取、migration report 和 rollback fixture；
- [ ] suite、subject、fixture、runner config 和 result 的独立 fingerprint；
- [ ] 候选生成端不可读取 holdout assertions 或 baseline scores。

### BEL-3：Provider-neutral Runner Core

- [ ] Runner protocol、capability negotiation 和 adapter contract；
- [ ] 隔离工作区、fixture materialization、路径逃逸防护和清理；
- [ ] timeout、cancel、retry、parallel worker 和 partial failure；
- [ ] without-skill/current/candidate 公平实验矩阵；
- [ ] 单轮、多轮 follow-up、checkpoint 和 responder 基础能力；
- [ ] provider adapter 不进入确定性核心，不内嵌第三方模型 CLI。

### BEL-4：Grader Registry

- [ ] text、regex、JSON path 与 JSON Schema；
- [ ] file existence/content 与 workspace diff；
- [ ] tool call、argument matcher、skill invocation 和 action sequence；
- [ ] token、轮次、耗时和 forbidden behavior；
- [ ] grader weight、结果明细和可解释失败；
- [ ] LLM judge、program grader 和 hooks 仅进入显式 trusted profile，并与确定性 hard gate 分离。

### BEL-5：A/B、统计与回归门禁

- [ ] 无 Skill vs 有 Skill 的增量价值测试；
- [ ] 当前版本 vs 候选版本的维护 A/B；
- [ ] development vs holdout 的泛化与 negative-transfer gate；
- [ ] 多 trial、flaky detection、pass-rate delta 和 confidence interval；
- [ ] golden case、任务新增/删除策略和稳定 CI exit codes；
- [ ] 固定执行顺序或环境可能造成的偏差必须进入 limitations。

### BEL-6：CI、Snapshot 与可观测性

- [ ] JSON、JUnit 和 GitHub Actions reporter；
- [ ] snapshot/replay、fixture digest 和 trajectory fingerprint；
- [ ] 默认凭证/私钥/认证头/邮箱脱敏与环境变量 allowlist；
- [ ] 本地历史、趋势与跨模型比较；
- [ ] metadata-only telemetry 默认关闭原始 payload；
- [ ] dashboard、MCP/JSON-RPC 和远程存储在核心 CLI 稳定后单独评估。

### BEL-7：Adversarial、真实 E2E 与发布

- [ ] prompt injection、scope bypass、pressure/rationalization 和危险副作用用例包；
- [ ] 用同一真实 Skill 完成 without/current/candidate × development/holdout × multi-model E2E；
- [ ] 验证行为证据能进入 improve/evolve/release，且失败不允许发布；
- [ ] pytest、Ruff、Skill validation、Doctor、credential lint、diff、迁移/回滚和独立评审全部通过；
- [ ] 更新 README、Guides、Feature Matrix、Roadmap、Task、Sprint、Version、Changelog 和 release evidence 后才允许发布声明。

### 进入实现的门禁

- 当前任务窗口只完成研究、Backlog 和 handoff；
- 新窗口先完成 BEL-1，只读分析之后才能创建 ADR/Spec/Plan；
- 未明确把本 Epic 升级为 Task/Sprint 前，不修改 `src/`；
- 实现必须位于独立候选，不能以 Waza 源码为候选目录；
- commit、push、tag 和发布继续是独立审批点。

## P0 Candidate：自进化 Observation Boundary

状态：调研已完成，尚未进入当前 Sprint。研究事实源为 [`skill2loop 与 Skill Engineering 自进化观测边界`](research/2026-07-20-skill2loop-observation-boundary.md)，恢复入口为 [`Observation Boundary Handoff`](handoffs/2026-07-20-skill2loop-observation-boundary-next.md)。

- [ ] Block A：把调研结论升级为 Spec、ADR 和实施 Plan；固定 Observation schema、隐私、幂等、多 Skill 归因、Promotion Gate 和版本归属。
- [ ] Block B：在独立 candidate 中 clean-room 重写 models/store/redaction、Codex adapter、attribution 和 `Observation -> SkillRun` bridge。
- [ ] Block C：完成 fixture、兼容、隐私、漂移、Promotion、旧 Evolution/Evaluation/Release 回归和完整质量门禁。
- [ ] 先在 Shadow/project scope 验证；真实 Hook、Canary、Active、外部 Review adapter 分别作为后续门禁，不自动开启。

边界：不复制上游源码，不建立第二套 Proposal/Eval/Release，不保存完整私有会话，不静默扩张当前 v2 Phase 1。

## P2 Candidate：Skill 可理解性知识图谱（Skill Graph）

状态：`research complete / spec and plan prepared / backlog / not scheduled`

需求目标是把任意 Agent Skill 转换成一张可验证、可浏览、可解释、可追踪变化的执行知识图谱，让使用者、作者和审阅者能够回答：

- Skill 为什么触发、从入口会继续读取哪些文件；
- 每个 reference、stage、script、tool、plugin 或子 Skill 承担什么职责；
- 输入经过哪些步骤产生输出，哪些路径包含状态、外部副作用、审批和回滚；
- 每条关系来自明确声明、确定性检测、AI 推断还是真实运行观测；
- 修改一个文件、规则或节点后，会影响哪些执行路径、证据和测试。

本方向与当前 `v2.0 Architecture Guardian` 共用 Blueprint/IR 和只读 inventory，但不把交互图谱、AI 解释、本地 Web UI 或 MCP 查询塞进当前 Phase 1。推荐边界是：Skill Engineering 提供可信架构事实、Doctor/Guardian finding 和 semantic diff；独立的 Skill Graph 产品负责细粒度图投影、交互浏览、解释和问答。

已准备的需求材料：

- [`Skill Graph Spec`](specs/2026-07-25-skill-comprehension-graph-spec.md)；
- [`Skill Graph Plan`](plans/2026-07-25-skill-comprehension-graph-plan.md)。

### 候选阶段

- [ ] SG-0：正式排期前确认产品载体、代码归属、版本归属和 Blueprint 扩展边界，并建立必要 ADR；
- [ ] SG-1：定义版本化 `Skill Graph Projection`、节点/边/证据等级、unknown 和 fingerprint 契约；
- [ ] SG-2：实现不执行目标代码的确定性 inventory/extractor，覆盖 `SKILL.md`、contract、references、stages、scripts 和 tests；
- [ ] SG-3：实现关系查询、路径、上下游、影响范围、过滤、staleness 和稳定导出；
- [ ] SG-4：交付 local-first Web 图谱，支持结构、执行、安全审批、测试证据四种视图；
- [ ] SG-5：增加可选 AI 解释、引导式 Tour 和角色适配，且与结构事实明确分层；
- [ ] SG-6：后续评估 CLI/MCP、IDE 集成、runtime trace overlay 和多 Skill Portfolio。

### 进入实现的门禁

- 用户明确把本 Epic 排入一个 Task/Sprint；
- 先接受产品/仓库/版本边界 ADR，不静默扩大当前 Guardian Phase 1；
- 确认复用现有 Blueprint inventory，而不是建立第二套架构事实源；
- 为本地隐私、凭证排除、AI provider、推断置信度和运行观测建立 trust model；
- 明确 MVP 只承诺单 Skill、local-first、只读建图，不自动修改 Skill；
- commit、push、tag、公开发布和任何 Global/Plugin 启用继续是独立审批点。

## P0：Public Beta 后立即评估

- 创建成功记录、历史和安全撤销；
- v2.0 之后的跨版本 Blueprint schema migration；
- v2.0 之后的多仓库架构适应度和语义 Diff 扩展；
- Skill Engineering 自身的固定 baseline/candidate 行为报告；
- GitHub 发布、wheel 构建和安装 smoke 自动化；
- 修复/验证非 production suite 无 high-risk case 的报告格式边界。

## P1：工程深度

- trigger precision/recall、near-neighbor 和 adversarial cases；
- 可审计 suppression/baseline：理由、owner、到期、profile 和 stale finding 复核；
- 可选 OSV 依赖漏洞查询与离线 fallback；
- MCP least-privilege、tool poisoning 和 rug-pull contract/扫描；
- 可信 Git/URL/zip 输入解析与来源验证；
- provider-neutral rollout runner、pressure/rationalization 和 multi-turn eval 已合并到 `Behavior Evaluation Lab` Epic，不再作为零散条目；
- state schema migration、并发锁、retention 和 export/import；
- Yao Meta/Superpowers pinned-source 复核与本地五模式清单维护（`2.1+`，仅研究维护，不重复承诺当前 Guardian Sprint）；
- Skill dependency graph、owner、stale 和冲突检测的多项目/Portfolio 扩展；
- metadata-only telemetry 与 adoption drift；
- 安装模拟、包校验和升级兼容。

## P2：产品与商业能力

- Review Studio；
- 托管评测矩阵；
- 团队工作区、RBAC、审批和 waiver；
- 私有部署、审计、策略和 SLA；
- 训练营模板、案例库和 Skill 工程认证；
- 对外 benchmark 与年度 Skill 工程报告。

## 明确不做

- 自动 Global 安装；
- 自动公开 push/publish；
- 保存原始私有对话或凭证；
- 用单一静态分数宣称 Skill 真实效果；
- 让所有简单 Skill 使用完整商业项目结构。

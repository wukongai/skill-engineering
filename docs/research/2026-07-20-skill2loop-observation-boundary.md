# skill2loop 与 Skill Engineering 自进化观测边界研究

## 结论

`1va7/skill2loop` 不应作为代码模块直接移入 Skill Engineering，也不应在现有 `evolution.py` 旁建立第二套 Proposal、Eval、状态或发布流程。

本项目应把上游实现反向解析为功能与行为规格，再使用 Skill Engineering 自己的状态、指纹、隐私、评测、维护和发布规范重新实现。推荐新增的能力边界是：

```text
Session / Hook
  -> Observation
  -> Feedback Evidence
  -> Promotion Gate
  -> existing SkillRun
  -> existing Evolution / Evaluation / Release
```

Observation 负责“发现并记录”，现有 Evolution 继续独占“正式提案、候选、评测、版本、发布和回滚”。`SkillRun` 是两者之间唯一正式边界。

本研究只完成上游审计、采用判断和下一阶段输入，不承诺当前 Sprint 实现该能力。

## 调研方案

### 目标

1. 固定可复核的上游版本，判断 `skill2loop` 当前真实能力，而不是只读取项目描述。
2. 对照 Skill Engineering 当前 Product、Architecture、Evolution、Evaluation、Maintenance、Blueprint 和 Release 实现。
3. 找出可以学习的功能、会与现有逻辑冲突的结构，以及必须拒绝的实现方式。
4. 形成 clean-room reimplementation 的采用矩阵和新任务边界。

### 基线

- 上游仓库：<https://github.com/1va7/skill2loop>
- 固定 commit：`1b21514ce383e4415d9d988c82a840042cb20b13`
- 快照日期：2026-07-20
- 上游版本声明：`0.1.0`
- 本地项目：Skill Engineering `1.0.0` Stable Lifecycle Contract；`2.0.0` Architecture Guardian Phase 1 开发预览

### 方法

1. 审计上游 README、TODO、Plan、Hook、Review Workflow、数据模型、CLI、存储和测试。
2. 运行上游公开测试，验证快照的最低可运行性。
3. 对照本地 `SkillRun -> EvolutionProposal -> CandidateJob -> Evaluation -> SkillVersion -> ReleaseRecord` 链路。
4. 按 Adopt / Adapt / Reject 判断能力，而不是按文件名映射源码。
5. 用冲突矩阵验证状态、语义、隐私、指纹、评测和发布是否会产生双事实源。
6. 以现有工程宪章和维护协议检查目标结构是否保持入口薄、确定性逻辑下沉、Preview/Apply 分离和可回滚。

### 调研验收

- 上游 commit、能力和限制可复核；
- 明确哪些能力已经由 Skill Engineering 实现；
- 明确缺口是否属于 Skill、Script、Plugin/runtime 或项目 Core；
- 形成单一数据所有权和 Promotion 边界；
- 形成新任务可以直接升级为 Spec、ADR 和 Plan 的 Backlog 与 Handoff；
- 不复制许可证边界不清晰的上游源码。

## 上游当前实现

`skill2loop` 当前是一个本地优先的 Skill 使用后学习账本。它能：

- ingest 合成 session、Codex/Claude 风格 JSONL transcript 和 Stop/SessionEnd hook payload；
- 从 transcript 推断 Skill 名称和路径；
- 把一次使用保存为 Episode、Trace 和 Structured Feedback；
- 用启发式规则识别反馈、接受状态、阶段和归因；
- 计算接受率、首轮接受率、平均接受轮次、反馈数和重复反馈率；
- 从反馈生成 eval seed 草案；
- 生成优化建议、Review Packet 和本地 Markdown 审核文件；
- 可选同步到 Lark/Feishu 或接入外部 `skills-sync` 审核包。

上游尚未实现：

- approved eval seed 到可运行回归测试的转换；
- old Skill 与 proposed Skill 的 replay 对比；
- development/holdout 隔离和 negative-transfer gate；
- 隔离候选生成和结构/安全 preflight；
- approved proposal 的安全 apply；
- 不可变版本、Shadow/Canary/Active、验证和回滚。

因此它的真实边界是“观测、聚类、草案和审核前半环”，不是完整的 Skill 自动修改系统。

## Skill Engineering 已有能力

本地 `src/skill_engineering/evolution.py` 已经实现：

- 脱敏 `SkillRun` 和完整 Skill tree fingerprint；
- 同类证据阈值、高风险触发和 protected success behavior；
- development/holdout leakage group 隔离；
- minimal-patch、layer-move、compaction、resource-or-script 四类隔离候选；
- lint、Doctor、安全和复杂度门禁；
- baseline/candidate 真实结果、holdout、高风险和 negative-transfer 评测；
- Pareto 非支配候选选择；
- 不可变 SkillVersion、Shadow、Canary、Active、验证和回滚。

当前主要缺口不是“如何改 Skill”，而是：

```text
真实 Session
  -> 自动识别 Skill invocation
  -> 去噪和脱敏
  -> 保存可追踪 Observation
  -> 聚合重复信号
  -> 经 Promotion Gate 形成可信 SkillRun
```

现有 `evolution record-run` 需要外部先准备结构化 JSON；还没有一条由真实 Agent session 自动、低噪声、可审计地生成该输入的正式链路。

## 冲突分析

| 冲突面 | 直接移植的后果 | 本项目边界 |
|---|---|---|
| 状态 | `.skill2loop-store` 与 `.skill-engineering/evolution` 产生两套生命周期 | Observation 可独立存储；Promotion 后只进入现有 Evolution state |
| Proposal | 上游 Proposal 与 `EvolutionProposal` 重复 | 上游式输出只能是 `PromotionRecommendation`，不得成为正式修改提案 |
| Eval | 启发式 eval seed 被误当成确定性 case | 只生成 `EvaluationCaseDraft`；缺少 expected 或人工确认不得进入 suite |
| 结果语义 | `captured/accepted` 被直接映射成 `success/failure` | 使用显式 adapter 和置信度；不确定时保持 observation |
| 指纹 | 只哈希 `SKILL.md`，遗漏 scripts/references/assets | 统一复用 Skill Engineering 完整 tree fingerprint |
| 隐私 | transcript、原始反馈、本地路径长期落盘 | 原文只在 ingest 边界短暂读取；保存脱敏摘要与 artifact pointer |
| 多 Skill 归因 | 一次 session 可能只归因到最后一个 Skill | invocation 必须是集合；每个归因带 evidence 和 confidence |
| 发布 | 上游未来 apply 与现有维护/发布状态机竞争 | Active/Canary 只能由现有 Release Engine 执行 |
| 规则 | 业务关键词进入通用 Core，形成硬编码偏好墙 | classifier 可插拔；通用 Core 只保留确定性协议和门禁 |

## 采用矩阵

| 上游能力 | 决定 | 本地实现方式 |
|---|---|---|
| Session/Hook ingestion | Adopt concept | 新建 provider-neutral adapter port，先 fixture 后真实 hook |
| Episode 中间层 | Adapt | 重定义为脱敏、版本化 `ObservationRecord` |
| Skill invocation inference | Adapt | 支持多 Skill、证据来源和置信度；显式 metadata 优先 |
| Feedback 去噪与去重 | Adapt | 确定性 filter + idempotency key；低置信度保留观察状态 |
| 重复反馈聚类与指标 | Adapt | 作为 observation metrics，不冒充 utility score |
| Eval seed | Adapt | 只生成待审核 `EvaluationCaseDraft`，不得绕过现有 suite gate |
| Review Packet | Adapt | 用现有用户反馈层呈现 evidence review，不建立第二套审批状态 |
| Proposal/Apply/Release | Reject | 全部复用现有 Evolution、Maintenance 和 Release |
| 业务 taxonomy | Reject from core | 需要时作为独立 domain classifier/resource |
| Lark/Feishu 大模块 | Defer | 未来外部 adapter；不进入第一垂直切片 |
| 上游源码复制 | Reject | 许可证边界不清晰，使用独立规格与本地实现 |

## 目标架构

建议新增独立 Observation 子域，而不是继续膨胀 `evolution.py`：

```text
src/skill_engineering/
  observation/
    models.py
    store.py
    redaction.py
    attribution.py
    promotion.py
    adapters/
      base.py
      codex.py
      claude.py
```

职责：

- `models.py`：版本化 Observation、Invocation、FeedbackEvidence 和 PromotionDecision；
- `store.py`：原子写入、幂等、schema migration、retention 和查询；
- `redaction.py`：凭证、私有路径、完整 Prompt 和敏感内容门禁；
- `attribution.py`：多 Skill 归因、来源证据和置信度；
- `promotion.py`：唯一的 `Observation -> SkillRun` 转换口；
- `adapters/`：只处理宿主 transcript/hook 格式，不拥有业务进化状态。

建议 CLI：

```text
skill-engineering observe ingest
skill-engineering observe list
skill-engineering observe review
skill-engineering observe promote
```

只有 `promote` 可以调用现有 `record_run()`。Observation 模块默认关闭、project-scoped、事件驱动且不阻塞宿主；不实现无限轮询或自动 Active 修改。

## 规则和代码一致性

| 层级 | 应放内容 |
|---|---|
| 根 `SKILL.md` | observe/evolve 的稳定触发、路由和停止点 |
| `references/observation-standard.md` | Observation 语义、Promotion 条件、隐私和人工审核规则 |
| Python Core | schema、指纹、幂等、去重、redaction、状态转换和 gate |
| fixtures/tests | transcript 兼容、多 Skill、误归因、重复事件、凭证和回归行为 |
| Product docs | 产品边界、跨版本所有权和不做事项 |

禁止通过在根 `SKILL.md` 追加事故式禁令解决 parser、state、privacy 或 idempotency 问题。

## 必须先固定的契约测试

1. 同一 session 重复 ingest 不产生重复 Observation。
2. 一次 session 使用多个 Skill 时保留每个 invocation，不只选择最后一个。
3. 明确的新任务、问题和粘贴材料不被误判为负面反馈。
4. 归因或反馈置信度不足时不得自动生成 SkillRun。
5. 原始 transcript、凭证、完整 Prompt 和私有路径不得进入持久状态。
6. Skill fingerprint 使用完整 tree，并能拒绝漂移后的 Promotion。
7. 没有确定性 expected 的证据只能保留为观察或草案。
8. Observation 关闭时，1.0 CLI、JSON、Evolution、Evaluation 和 Release 行为不变。
9. Promotion 后 evidence pointer 能一直追踪到 Proposal、Candidate、Evaluation、Version 和 ReleaseRecord。
10. Hook 失败不阻塞宿主，但错误必须进入可诊断的本地记录。

## 验证事实和限制

- 上游公开测试：16 passed；运行过程中出现 SQLite connection `ResourceWarning`，未影响退出状态。
- 本地定向测试：`tests/test_evolution.py` 与 `tests/test_blueprint.py` 共 16 passed。
- 本窗口文档收口门禁：Ruff、官方 Skill validation、production Doctor 100/A、credential lint 和 `git diff --check` 通过。
- 全量 pytest 为 132 passed、1 failed。失败项是既有 `test_installed_skill_wrapper_reports_missing_python_cli`：当前 `.venv` 的 editable install 使 `python -I` 仍能导入本地 `skill_engineering`，实际进入 Doctor 并返回 1，而测试预期模拟未安装 CLI 并返回 2；测试和 wrapper 均无本次 diff。本研究不越界修复该基线问题。
- 本轮没有运行跨 Agent 的真实 transcript rollout，也没有实现 Observation；因此只证明架构关系和公开快照可复核，不证明未来集成效果。
- 上游快照根目录没有清晰的许可证文件。本项目只采用公开行为和架构思想，不复制源码。

## 新任务边界

新任务分为两段，但属于同一条受治理功能链：

### A. 正式分析与契约

1. 把本研究升级为 Observation Boundary Spec。
2. 用 ADR 固定 Observation/Evolution 单一事实源和 Promotion 边界。
3. 形成实施 Plan、schema、状态图、隐私模型和 fixture 组合。
4. 明确当前版本归属；不得静默扩张 v2 Phase 1。

### B. 独立重写与验证

1. 先实现 models/store/redaction 与合成 fixture。
2. 再实现 Codex adapter 和多 Skill attribution。
3. 实现 Promotion Adapter，复用现有 `record_run()`。
4. 通过兼容、隐私、幂等、negative/high-risk 和旧版本回归。
5. 只在 Shadow/project scope 验证；真实 Hook、Canary 或 Active 分别保留后续审批。

详细恢复入口见 [`skill2loop Observation Boundary Handoff`](../handoffs/2026-07-20-skill2loop-observation-boundary-next.md)。

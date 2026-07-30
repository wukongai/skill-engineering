# Handoff：自进化 Observation Boundary 分析与独立重写

日期：2026-07-20

## 状态

- 来源任务：调研 `1va7/skill2loop` 与 Skill Engineering 自进化架构的关系
- 当前状态：research complete / implementation not started
- 优先级：P0 candidate，尚未进入当前 Sprint
- 推荐执行方式：新 Codex 任务

当前任务已经完成上游源码审计、能力边界、冲突矩阵、采用矩阵和目标架构。新任务不得重新从“skill2loop 是什么”开始，也不得直接复制上游源码。

## 新任务目标

按照两段式完成 Observation Boundary：

1. 先完成正式分析工件：Spec、ADR、Plan、schema、状态图、隐私边界和 fixture 设计。
2. 用户确认同一份计划后，在独立 candidate 中按照 Skill Engineering 现有结构重新实现，而不是移植上游代码。

## 开工前必读

1. [`调研报告`](../research/2026-07-20-skill2loop-observation-boundary.md)
2. [`Product`](../PRODUCT.md)
3. [`Constitution`](../constitution.md)
4. [`Architecture`](../architecture.md)
5. [`当前 Task`](../TASK.md)
6. [`当前 v2 Sprint`](../sprints/2026-07-v2.0-architecture-guardian.md)
7. [`Evolution Standard`](../../skills/skill-engineering/references/evolution-standard.md)
8. [`Maintenance Protocol`](../../skills/skill-engineering/references/maintenance-protocol.md)

## 不可改变的架构决定

```text
Session / Hook
  -> Observation
  -> Promotion Gate
  -> existing SkillRun
  -> existing Evolution / Evaluation / Release
```

- Observation 只负责发现、脱敏、记录、聚合和晋升建议。
- `SkillRun` 是进入正式自进化的唯一入口。
- `EvolutionProposal`、Evaluation suite、Candidate、Version 和 Release 保持单一事实源。
- Observation 不得自动修改 Skill，不得自动 Canary/Active，不得保存完整私有会话或凭证。
- 上游仓库许可证边界不清晰，只能做 clean-room reimplementation。

## Block A：正式分析

先完成并预览，未确认前不实现代码：

- [ ] 建立 `docs/specs/2026-07-xx-observation-boundary-spec.md`。
- [ ] 建立跨版本 ADR，固定状态所有权、Promotion 边界和兼容策略。
- [ ] 建立 `docs/plans/2026-07-xx-observation-boundary-plan.md`。
- [ ] 定义 Observation schema、idempotency key、fingerprint、confidence 和状态转换。
- [ ] 定义 transcript 短暂读取、redaction、artifact pointer 和 retention。
- [ ] 定义 Codex/Claude adapter port；第一实现只承诺 Codex fixture。
- [ ] 定义 success、failure、multi-skill、ambiguous、duplicate、sensitive 和 high-risk fixtures。
- [ ] 判断版本与 Sprint 归属；不得直接写入当前 v2 Phase 1。

## Block B：独立重写

只有 Block A 的 Spec/Plan 获得确认后进入：

- [ ] 在隔离 candidate 中新增 `src/skill_engineering/observation/`。
- [ ] 实现 models、schema validation、atomic store、redaction 和 idempotency。
- [ ] 实现 provider-neutral adapter protocol 与 Codex transcript adapter。
- [ ] 实现多 Skill attribution、evidence 和 confidence。
- [ ] 实现唯一的 `Observation -> SkillRun` Promotion Adapter。
- [ ] 增加 `observe ingest/list/review/promote` CLI，默认关闭且 project-scoped。
- [ ] 根 `SKILL.md` 只增加稳定路由；详细规则进入 reference，确定性约束进入 Python。
- [ ] 不实现 Lark/Feishu、自动 patch、自动 Active 或无限轮询。

## Block C：验证与收口

- [ ] 新增契约、schema、adapter、隐私、幂等、多 Skill、漂移和 Promotion 测试。
- [ ] 确认现有 Evolution/Evaluation/Release 测试无回归。
- [ ] 运行 pytest、Ruff、Skill validation、credential lint 和 diff check。
- [ ] 对独立 candidate 运行 lint/Doctor 和 complexity delta。
- [ ] 没有真实 rollout 时只声明结构和确定性行为通过，不宣称实际效用提升。
- [ ] 更新 Architecture、Task、Sprint、Daily Log、Changelog/Version（仅当版本范围确认）和测试 evidence。
- [ ] commit、push、tag、发布、Canary/Active 分别请求明确授权。

## 开工基线

- 本窗口 Ruff、官方 Skill validation、production Doctor 100/A、credential lint 和 `git diff --check` 通过。
- 全量 pytest 为 132 passed、1 failed；唯一失败是既有 installed-wrapper 缺 runtime 模拟测试。当前 `.venv` 的 editable install 在 `python -I` 下仍可导入 `skill_engineering`，导致测试预期的“CLI 缺失”环境没有成立。
- `tests/test_doctor_wrapper.py` 与 `skills/skill-engineering/scripts/doctor_skill.py` 均无本窗口 diff。新任务开始时应先固定可重复的测试基线，或把该隔离问题拆成独立修复；不得把它误归因于 Observation 实现，也不得在未复验时宣称全量 pytest 通过。

## 推荐的新任务提示

```text
继续 Skill Engineering 的 Observation Boundary 任务。先读取
docs/handoffs/2026-07-20-skill2loop-observation-boundary-next.md 和其中的调研报告。
先完成 Block A 的正式分析、Spec、ADR 和 Plan 预览，不要直接实现代码；
我确认同一计划后，再在独立 candidate 中按现有架构 clean-room 重写 Block B。
```

## 当前任务明确未执行

- 未创建 Spec、ADR 或实施 Plan。
- 未修改 Python、Skill 指令、schema 或测试。
- 未安装、复制或 vendor 上游项目。
- 未创建新 Codex 任务。
- 未进入当前 Sprint、未发布、未 commit、未 push。

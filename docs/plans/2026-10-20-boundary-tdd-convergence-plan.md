# Boundary Contract、Skill TDD 与维护收敛 Implementation Plan

对应 Spec：[`2026-10-20-boundary-tdd-convergence-spec.md`](../specs/2026-10-20-boundary-tdd-convergence-spec.md)

状态：BT-3b 修正完成，独立评审通过；等待用户决定是否提交或进入发布流程

## 目标

把 Boundary Contract、创建行为测试和维护收敛机制接入现有 mini governance、Native Authoring 和 maintenance engine，不建立平行创建链路。

## 实施顺序

### BT-1：Boundary Contract 数据与入口

- 新增 `references/boundary-contract.md`，定义字段、偏题信号、拉回策略、停止条件和案例格式。
- 扩展 Authoring Brief / Mini Governance 文档映射，保留旧字段读取兼容。
- 更新 `SKILL.md`、design/discover 阶段、contract 和用户反馈规则；缺关键边界字段时保持 `needs_discovery`。

### BT-2：创建行为测试矩阵

- 新增随 Skill 交付的行为测试矩阵格式和最小 fixture。
- 把成功、反例、偏题、信息不足、失败/审批五类案例加入创建预览和创建后自测说明。
- 更新 Content Gate / Creation Review 的结果语义，明确静态结构通过不等于行为已验证。
- 增加文档契约与行为路由测试，先覆盖 Skill Engineering 自身。

### BT-3：维护收敛模型

- 在维护预览/记录中增加目标、baseline、验收集合、最大修复轮数、阻断项、延后债务和完成门。
- 让 maintenance preflight 将 findings 分为 `blocks_current_change`、`regression_required`、`deferred_debt`。
- 在达到完成门时结束；只剩债务时输出已完成和下一步；超过轮数或阻断未清零时输出 `needs_improvement`。
- 保持同一 plan id、candidate、target、baseline 和验收集合的漂移保护。

本轮修正补充：

- 增加确定性行为案例 Runner，将逐案例结果写入 Native preview plan；`uncovered` 不得进入通过。
- 增加 `repair_round` 和失败后的 `needs_improvement` 硬停止，防止同一 MaintenanceRecord 无限重试。
- 将 `acceptance_cases` 从 CLI 贯穿 BuildPlan、MaintenanceRecord、计划哈希与 Verify，并与 `regression_cases` 分离。

修正结果：以上三项已实现并通过独立评审，证据见 [`BT-3b 独立评审记录`](../testing/2026-10-20-boundary-tdd-convergence-review.md)。

### BT-4：自举回归与文档同步

- 增加 Boundary Contract、行为矩阵、TDD 顺序和收敛门禁测试。
- 更新 Product、Architecture、TASK、Roadmap、Feature Matrix、CHANGELOG、README、Daily Log 和维护证据。
- 对真实私董会/业务 Agent 类案例补充偏题和收敛 fixture；不修改外部项目源码，先在本仓库建立规则和测试契约。

## 验证

- targeted pytest：authoring、native plan、creation review、maintenance、skill feedback；
- 全量 pytest；
- Ruff、Skill validation、Content Gate、portable self-test、production Doctor；
- credential lint、release consistency、`git diff --check`；
- 用一个简单 atomic fixture 和一个复杂/有阶段状态 fixture 验证边界案例与收敛分流。
- 增加行为 Runner 的通过、失败和 uncovered 三态测试，以及维护轮次状态机的可写环境测试。

已完成验证证据：[`BT-3 验证记录`](../testing/2026-10-20-boundary-tdd-convergence.md)。

## 变更边界

- 本 Plan 不提交、不推送、不打 tag、不发布、不启用 Global。
- 不覆盖用户现有 Skill；使用隔离候选和测试 fixture。
- 旧记录只读兼容；迁移字段缺失时标记 legacy，不补写不可证明的历史事实。

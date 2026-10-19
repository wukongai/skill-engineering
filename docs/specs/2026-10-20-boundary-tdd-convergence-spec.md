# Boundary Contract、Skill TDD 与维护收敛 Spec

状态：实现与全量门禁已完成，待独立评审

## 背景

Skill Engineering 已能形成 mini Product、mini Spec、mini Plan，并通过 Authoring Brief、Content Gate、Creation Review 和 Native Plan 完成基本创建闭环。真实使用暴露出三个缺口：

1. 业务目标、Agent 能力和不应处理的相邻任务没有形成独立且可回归的 Boundary Contract，长对话容易偏离目标；
2. 创建过程有结构检查，但没有把行为测试和边界测试作为生成前后的固定 TDD 契约；
3. 多版本维护会不断发现冗余和建议，缺少“本次阻断问题已解决即可结束”的收敛机制，导致体检循环无法完成。

## 目标

- 所有 Skill 的 mini Spec 必须包含 Boundary Contract。
- Skill 创建必须先有行为测试和验收条件，再生成候选；简单 Skill 使用轻量行为矩阵，复杂 Skill 使用完整测试与证据入口。
- 每次维护必须区分当前阻断、本次回归和结构债务，并以有限、可解释的收敛条件结束。
- Skill Engineering 自身继续用同一套 Boundary Contract、TDD/行为测试和收敛门禁进行自举维护。

## 非目标

- 不要求简单 Skill 复制完整 Python 测试工程。
- 不把 LLM 主观评分或静态 Doctor 分数当成行为通过证据。
- 不自动清理未经当前计划明确声明的旧文件，不自动发布或启用 Global。
- 不在本 Spec 中实现真实模型 runner、云端评测或新的外部服务。

## Boundary Contract

每个 Skill 创建或扩展的 Mini Governance Record 必须包含以下边界事实：

- `mission`：本 Skill 当前要完成的业务任务；
- `owned_capabilities`：Agent 负责的判断、动作和交付；
- `excluded_capabilities`：明确不负责的相邻任务；
- `allowed_context`：允许使用的输入、角色、阶段和证据范围；
- `drift_signals`：表示对话已经偏离目标的信号；
- `redirect_strategy`：偏离时拉回、停车或正式切换任务的处理方式；
- `stop_conditions`：必须停止追问、交付、等待证据或请求确认的条件；
- `acceptance_cases`：证明边界成立的正例、反例和异常例。

Boundary Contract 的职责是约束 Agent 的业务范围，不替代 Authoring Brief 的输入输出字段，也不替代 Native Plan 的文件和写入安全绑定。

## 创建 TDD / 行为测试

创建流程增加固定顺序：

```text
Boundary Contract
→ 行为测试矩阵
→ 候选生成
→ Content Gate / Creation Review
→ Preview
→ Apply / Verify
→ 创建后自测
→ 真实任务试用
→ 回归用例登记
```

行为测试矩阵至少包含：

- 一个应触发并完成的成功案例；
- 一个相邻但不应触发的反例；
- 一个偏题后必须拉回的案例；
- 一个输入不足或证据不足的案例；
- 一个工具失败、部分成功或需要批准的案例。

测试结果区分 `structure_ready`、`behavior_evidence_pending`、`validated` 和 `needs_improvement`，不得用静态分数替代真实任务证据。确定性 Runner 只执行候选中声明的文本断言；无法执行的旧字符串案例必须标记 `uncovered`，不能被视为通过。

## 维护收敛机制

每个 improve 计划必须声明：

- `maintenance_goal`：本次只解决什么问题；
- `baseline_version`：从哪个版本或快照开始；
- `acceptance_cases`：本次必须通过的行为和边界案例；
- `max_repair_rounds`：允许的自动/协作修复轮数，默认不超过 3；
- `completion_gate`：阻断项清零、当前回归通过、计划内验证完成；
- `deferred_debt`：仍存在但不阻断本次交付的结构债务；
- `next_action`：债务进入 backlog、refactor 计划或等待外部证据的唯一下一步。

`acceptance_cases` 与 `regression_cases` 分开保存；前者是本轮完成门，后者是历史回归集合。维护记录还必须保存 `repair_round`，Verify 每次递增；失败或达到上限后状态固定为 `needs_improvement`，不得继续复用同一记录无限重试。

收敛规则：

1. 当前阻断项或当前回归失败时，不能完成本次维护；
2. 仅有结构债务或建议项时，可以完成本次维护，但必须登记并给出下一步；
3. 达到最大修复轮数仍未通过时，状态为 `needs_improvement`，不得继续无限自动体检；
4. 每轮都必须复用同一维护目标和验收集合，不能通过扩大范围制造“完成”；
5. 维护记录必须说明已完成项、延后债务和恢复入口。

## 兼容与升级

- 旧 Authoring Brief、旧 BuildPlan、旧 MaintenanceRecord 继续兼容读取；缺少 Boundary Contract 或收敛字段的历史记录在恢复时标记为 legacy，补建时不能伪造历史事实。旧记录缺少 `acceptance_cases` 时由 `regression_cases` 生成兼容默认值并记录来源。
- 简单 Skill 使用轻量矩阵和 portable self-test；团队/生产 Skill 增加 contract、回归证据和真实 rollout；复杂/商业 Skill 继续使用完整治理、独立评审和发布/回滚证据。
- 公开 CLI/JSON/1.x 读取契约保持兼容；新增字段采用可选扩展，完成门禁后再决定是否冻结为稳定字段。

## 验收标准

- 创建入口能在候选生成前形成并展示 Boundary Contract 和行为测试矩阵。
- 缺少 mission、owned_capabilities、excluded_capabilities、drift_signals、stop_conditions 或 acceptance_cases 时保持 `needs_discovery`。
- 生成后的候选能通过至少一组成功、反例、偏题、信息不足和失败/审批案例检查；每个可执行案例都由 Runner 输出逐案例证据，旧格式案例显示 `uncovered`。
- 维护预览能展示当前阻断、结构债务、最大修复轮数和完成条件。
- 阻断清零且当前回归通过时可以收敛；只剩债务时不会被无限体检阻塞。
- 超过最大修复轮数或仍有阻断时明确进入 `needs_improvement`，并保留恢复入口；Verify 不得在同一 MaintenanceRecord 上继续无限重试。
- Skill Engineering 自身的入口、契约、测试和维护记录通过同一套自检。

# BT-3b 独立评审记录

日期：2026-10-20

## 评审结论

BT-3b 通过。此前提出的三个阻断项已完成修正：行为案例可执行、维护记录具备有限轮次状态机、`acceptance_cases` 已贯穿维护计划和验证记录。

## 评审证据

- `behavior.py` 执行声明式 `must_include` / `must_not_include` 断言，并区分 `passed`、`failed`、`uncovered`。
- Native preview 将逐案例结果写入 `behavior_tests`，行为失败或未覆盖时拒绝生成可 Apply 的 plan。
- `MaintenanceRecord.repair_round` 在 Verify 时递增；失败进入 `needs_improvement`，同一记录不能继续作为已应用记录无限验证。
- `acceptance_cases` 与 `regression_cases` 分开保存，并参与计划哈希、维护记录和完成门。
- 旧维护记录读取时用 regression cases 生成兼容 acceptance cases，不伪造历史行为证据。

## 验证结果

- 全量 pytest：`223 passed`；
- 新增行为 Runner、Native preview 集成和维护轮次状态机定向测试：`24 passed`；
- Ruff、Content Gate、production Doctor、credential lint、release consistency、`git diff --check`：通过；
- portable self-test：`pass`，真实任务试用仍按既有规则保持 pending。

## 评审边界

Runner 是确定性的候选文本断言器，不能替代宿主 Agent 的真实业务任务试用。私董会/业务 Agent 案例仍以脱敏 fixture 保存；真实效用需要后续 rollout 证据。

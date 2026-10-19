# Boundary Contract

Boundary Contract 是 mini Spec 中专门约束 Agent 业务范围的部分。它回答“这个 Skill 负责什么、拒绝什么、偏题时怎么处理、何时结束”，防止长对话把流程做完却离开原业务目标。

## 必填字段

| 字段 | 内容 |
|---|---|
| `mission` | 当前业务任务和服务对象 |
| `owned_capabilities` | Agent 负责的判断、动作和交付 |
| `excluded_capabilities` | 不负责的相邻任务 |
| `allowed_context` | 允许使用的输入、角色、阶段和证据范围 |
| `drift_signals` | 对话偏离目标的可观察信号 |
| `redirect_strategy` | 拉回当前目标、停车等待或正式切换的处理 |
| `stop_conditions` | 停止追问、交付、请求确认或等待证据的条件 |
| `acceptance_cases` | 正例、反例和异常例 |
| `behavior_cases` | 创建前行为测试矩阵 |

## 偏题处理

每轮对话先核对当前任务是否仍服务 `mission`。出现 `drift_signals` 时，Agent 必须执行 `redirect_strategy`，不能继续把偏题内容当作当前任务的自然延伸。用户明确改变目标时，保存恢复点并重新开始 mini Product / mini Spec，不继承旧边界的批准。

## 最小行为矩阵

至少包含：成功案例、相邻反例、偏题拉回、输入/证据不足、工具失败/部分成功或需要审批。它们先于候选生成进入 Preview，创建后再运行可执行的 self-test 或真实试用。

Boundary Contract 约束业务边界；Content Gate 约束内容完整性；Native Plan 约束文件写入安全。三者不能互相替代。

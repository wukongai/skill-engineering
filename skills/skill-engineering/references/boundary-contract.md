# Boundary Contract

Boundary Contract 是 mini Spec 中约束 Agent 业务范围的部分，回答负责什么、不做什么、如何处理意图变化及何时结束。字段在这里定义，提案、用户确认和按类型验收只按[边界确认细则](boundary-confirmation.md)执行。

## 必填字段

| 字段 | 内容 |
|---|---|
| `mission` | 当前业务任务和服务对象 |
| `owned_capabilities` | Agent 负责的判断、动作和交付 |
| `excluded_capabilities` | 提案给用户确认的不负责范围；明确无额外排除时可为空 |
| `allowed_context` | 允许使用的输入、角色、阶段和证据范围 |
| `drift_signals` | 对话偏离目标的可观察信号 |
| `redirect_strategy` | 拉回当前目标、停车等待或正式切换的处理 |
| `stop_conditions` | 停止追问、交付、请求确认或等待证据的条件 |
| `acceptance_cases` | 正例、反例和异常例 |
| `behavior_cases` | 按声明能力选择类别的创建前文本案例 |

## 偏题处理

按[意图变化处理](boundary-confirmation.md#对话中的意图变化)区分重要补充、岔题、明确切换与停止；持续任务在偏离信号出现时执行 `redirect_strategy`，单次任务可说明越界后停止或交接。

## 最小行为矩阵

按[能力与案例矩阵](boundary-confirmation.md#按能力安排候选文本案例)登记适用类别和有效断言，先于候选生成进入 Preview；创建后另运行可执行 self-test 或真实试用。候选文本检查不证明实际业务通过。

Boundary Contract 约束业务边界；Content Gate 约束内容完整性；Native Plan 约束文件写入安全。三者不能互相替代。

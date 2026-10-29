# Authoring Brief 契约

Authoring Brief 是候选生成前必须形成的结构化、可检查的需求契约，也是 Mini Governance Record 中 mini Product 与 mini Spec 的主要事实源。它把用户的真实任务固定下来，让预览、门禁、评审和维护都引用同一份事实，而不是依赖对话记忆；Native Plan 对应 mini Plan。

## 使用时机

- 用户确认要创建（或扩展）Skill 之后、生成任何候选文件之前；
- 信息不足时保持 `needs_discovery`，一次只问一个会改变结果的问题；已有上下文足够时跳过提问，直接补全 Brief；
- 恢复任务时先读取已保存的 Brief，不要让用户重述已经回答的信息；按[边界确认细则](boundary-confirmation.md)复用明确表达，只在业务边界实质变化时更新确认。

## 字段

| 字段 | 内容 | 必填 |
|---|---|---|
| `goal` | 用户反复需要完成的真实任务，用用户自己的语言概括。 | 是 |
| `target_users` | 谁使用这个 Skill，以及复用范围（个人、团队、生产）。 | 否 |
| `positive_triggers` | 应该触发这个 Skill 的请求，至少一条具体说法。 | 是 |
| `negative_triggers` | 不应该触发的相邻请求；明确没有时可为空，不能用空值代替用户确认。 | 按边界 |
| `inputs` | 必需输入、可选输入和来源（用户粘贴、文件、工具输出）。 | 否 |
| `outputs` | 输出形状、完成条件和成功证据。 | 否 |
| `workflow` | 任务专属步骤和分支，不是通用模板。 | 否 |
| `failure_modes` | 信息不足、工具失败、部分成功时各自的行为。 | 否 |
| `side_effects` | 文件写入、网络、外部系统和不可逆动作。 | 否 |
| `approvals` | 哪些动作必须停在用户确认点。 | 否 |
| `resources` | 需要的 scripts、references、assets、templates 和 tests。 | 否 |
| `examples` | 至少一个成功示例；有风险时补失败或反例。 | 否 |
| `verification` | 结构检查、脚本测试和真实任务试用的安排。 | 是 |
| `host_requirements` | 需要的宿主工具能力（读写文件、终端、审批），不硬编码单一宿主名称。 | 否 |
| `mission` | 本 Skill 当前要完成的业务任务。 | 是 |
| `owned_capabilities` | Agent 负责的判断、动作和交付。 | 是 |
| `excluded_capabilities` | 与用户确认的不负责范围；明确无额外排除时允许空清单。 | 是 |
| `allowed_context` | 允许使用的输入、角色、阶段和证据范围。 | 否 |
| `drift_signals` | 表示对话已经偏离目标的信号。 | 是 |
| `redirect_strategy` | 区分补充、岔题、切换与停止；单次任务可说明越界并停止或交接。 | 新确认必需 |
| `stop_conditions` | 必须停止追问、交付、等待证据或请求确认的条件。 | 是 |
| `acceptance_cases` | 证明边界成立的正例、反例和异常例。 | 是 |
| `behavior_cases` | 按[能力矩阵](boundary-confirmation.md#按能力安排候选文本案例)选择类别，每例含有效文本断言。 | 是 |

## 就绪判定

`goal`、`positive_triggers`、`verification` 等业务必需字段缺失时，Brief 不就绪：

- 不得进入候选生成；
- 用户可见状态保持 `needs_discovery`；
- 只问能补齐缺失字段的问题，不问泛泛的“还有什么要求”。

旧数据的结构读取与新创建的确认判定分开：新创建还须具备就绪的业务边界、`redirect_strategy`、类型案例及当前指纹的确认；已确认的空排除/反触发不按缺失处理。确认字段不加入旧 dataclass，格式与兼容语义见[业务投影与确认输入](boundary-confirmation.md#业务投影与确认输入)。

## 脱敏规则

Brief 只保存脱敏摘要：

- 不保存凭证、私钥、cookie、`.env` 值、完整私有会话或原始敏感 Prompt；
- 保存前用 `skill_engineering.authoring.sanitize_brief` 处理，命中的值替换为 `[redacted]`；
- 用户确实提供了凭证形态的内容时，记录“用户已提供凭证，未保存原文”，不写回 Brief。

## 保存与恢复

- 本地状态：`.skill-engineering/authoring-briefs/<id>.json`，`schema_version` 与 journey 一致；
- 保存/读取使用 `save_authoring_brief` / `load_authoring_brief` / `list_authoring_briefs`；
- Brief 更新时 `updated_at` 递增；候选计划记录生成它所用的 Brief id，预览与 Apply 不得引用已漂移的 Brief；
- portable Native Plan 的 `preview` 只接受 `--brief-id <id>`，并从项目状态目录读取
  已持久化的脱敏 Brief；不接受任意 `--brief <path>` 或对话里临时拼出的 Brief JSON；
- 新预览同时提供 `--boundary-confirmation <JSON路径>`，确认与类型策略冻结进计划；旧计划沿用原合法校验，不补造历史确认；
- 创建完成后 Brief 保留为维护、评测和自进化的事实源。

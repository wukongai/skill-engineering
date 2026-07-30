# Authoring Brief 契约

Authoring Brief 是候选生成前必须形成的结构化、可检查的需求契约。它把用户的真实任务固定下来，让预览、门禁、评审和维护都引用同一份事实，而不是依赖对话记忆。

## 使用时机

- 用户确认要创建（或扩展）Skill 之后、生成任何候选文件之前；
- 信息不足时保持 `needs_discovery`，一次只问一个会改变结果的问题；已有上下文足够时跳过提问，直接补全 Brief；
- 恢复任务时先读取已保存的 Brief，不要让用户重述已经回答的信息。

## 字段

| 字段 | 内容 | 必填 |
|---|---|---|
| `goal` | 用户反复需要完成的真实任务，用用户自己的语言概括。 | 是 |
| `target_users` | 谁使用这个 Skill，以及复用范围（个人、团队、生产）。 | 否 |
| `positive_triggers` | 应该触发这个 Skill 的请求，至少一条具体说法。 | 是 |
| `negative_triggers` | 不应该触发的相邻请求，至少一条具体说法。 | 是 |
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

## 就绪判定

`goal`、`positive_triggers`、`negative_triggers`、`verification` 任一缺失时，Brief 不就绪：

- 不得进入候选生成；
- 用户可见状态保持 `needs_discovery`；
- 只问能补齐缺失字段的问题，不问泛泛的“还有什么要求”。

Python 侧判定由 `skill_engineering.authoring.missing_required_fields` / `brief_ready_for_candidate` 实现，与本文档保持一致。

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
- 创建完成后 Brief 保留为维护、评测和自进化的事实源。

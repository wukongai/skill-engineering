# 边界确认与按类型验收

[返回 Skill 入口](../SKILL.md) · [业务边界字段](boundary-contract.md) · [需求事实源](authoring-brief.md) · [维护协议](maintenance-protocol.md) · [证据标准](evaluation-standard.md)

本文件是创建与维护边界确认、对话防跑偏和候选文本案例的唯一细则源。业务正文仍在 Authoring Brief；确认记录只绑定该正文，不复制一套需求。参考文章提供设计启发，不作为所有 Skill 的统一运行流程。

## 先提案，再形成确认

先向用户用业务语言提出三件事：做什么、不做什么及理由、怎样算完成。排除项只列与当前任务相邻且确实会影响结果的内容，并分别说明：

| 判断 | 含义与处理 |
|---|---|
| 职责之外 | 不属于这个 Skill；说明原因和可用交接方向。 |
| 本轮暂缓 | 属于可讨论方向，但此次不交付；保留待办。 |
| 有条件执行 | 条件满足后可做；说明所需输入、权限或审批。 |
| 能力局限 | 当前工具、证据或宿主无法做到；如实说明限制。 |

用户可以接受、修改、拒绝提案，也可以明确确认没有额外排除项。用户拒绝某个排除项时，先澄清其希望归属的职责与完成条件，不能自动把它加入能力。没有相邻反触发或额外排除不表示全能，正向职责与触发仍须明确。未确认时可继续只读探索和草稿；新边界达到可应用状态前须有对应确认。

复用用户已经明确表达的目标、排除和完成条件；恢复同一语义边界时不反复确认。目标、职责、触发、输入输出、停止或审批等业务事实实质变化时，旧确认失效，先展示变化再确认。时间、执行进度等元数据变化不要求重新确认。边界确认不替代文件写入、安装、发布和外部副作用所需的实际授权。

## 对话中的意图变化

| 用户输入 | 当前任务的处理 |
|---|---|
| 重要补充 | 补入事实或约束；若改变业务边界，更新提案与确认。 |
| 岔题 | 简短指出与目标的关系，按 `redirect_strategy` 拉回或保留待办。 |
| 明确切换目标 | 尊重新意图，保存恢复点，按新目标更新边界；不把旧确认沿用到新职责。 |
| 明确停止 | 停止推进，保留已完成内容与恢复入口。 |

持续对话 Skill 在可观察的 `drift_signals` 出现时执行纠偏；单次任务 Skill 可说明越界并停止或交接。不要给所有 Skill 强加每轮主持循环，也不要把用户明确切换误判为必须拉回的岔题。

## 业务投影与确认输入

边界指纹复用 Brief 的 `goal`、`mission`、`owned_capabilities`、`excluded_capabilities`、`allowed_context`、`positive_triggers`、`negative_triggers`、`inputs`、`outputs`、`drift_signals`、`redirect_strategy`、`stop_conditions`、`side_effects`、`approvals`。规范化外层空白后计算 SHA-256；不包含时间或执行状态。不得向旧 Brief dataclass 增加默认字段来补造确认。

确认 JSON 的字段如下，未知字段拒绝；只保存短脱敏摘要，不存完整会话、原始敏感 Prompt 或凭证。

| 字段 | 约束 |
|---|---|
| `schema_version` | 固定字符串 `"1"`。 |
| `subject_id` | 确认所绑定的对象；Native 必须匹配 Brief ID。 |
| `boundary_fingerprint` | 当前业务投影的真实指纹。 |
| `status` | `pending`、`confirmed`、`rejected`、`stale`、`legacy_unknown`；可应用的新边界必须为 `confirmed`。 |
| `source` | 仅 `explicit_user_message` 或 `explicit_cli_argument`。 |
| `summary` | 如实概括用户明确确认的业务边界。 |
| `excluded_decision` | 非空排除清单用 `listed`；用户明确无额外排除且清单为空时用 `none`。 |
| `behavior_policy` | 下述按类型策略，四个字段都必需。 |
| `message_ref` | 可选；只使用宿主真实可用的消息引用，不编造。 |

`source` 只校验声明来源字段，指纹只校验本地绑定；两者不证明真人身份、消息真实性或宿主如实转录。宿主与独立评审负责核对实际表达、能力事实及是否发生业务变化。未确认的空排除清单不能等同于同意，历史未知也不能升级为确认。

`goal`、`mission` 是非空文本，其余业务投影字段是字符串列表；正向职责、触发、偏离信号、纠偏策略和停止条件不能为空。稳定 ID 以英文字母或数字开头，仅含字母、数字、点、下划线或连字符，最长 128 字符；普通文本最长 4000 字符，列表最多 128 项且不含重复项。候选正文最多 8 Mi 字符。输入含凭证形态或非法控制字符时拒绝，不把敏感原文带入错误报告。

`behavior_policy` 仅允许：`interaction`（`single_turn` 或 `multi_turn`）、`uses_tools`（布尔值）、`has_side_effects`（布尔值）、`rationale`（非空能力依据）。已声明副作用却标记 `has_side_effects=false` 时拒绝；确定性规则不声称能自动理解全部自然语言能力。

## 创建与维护接入

- 新 Native Preview 传入 `--boundary-confirmation <JSON路径>`，使用已保存的 Brief 验证确认，要求 `redirect_strategy`，冻结确认和策略；候选、整个 Brief、目标仍按原指纹保护。Apply 重验冻结快照，不用可变外部输入改写已预览事实。
- 新 `improve` 与 Active 预览传入 `--boundary-review <JSON路径>`，与原 `--architecture-review` 并列；缺声明阻断。维护代理、CLI 与 Active 消费同一核心，不另建审批、写入或回滚引擎。
- 维护声明顶层 `schema_version="1"`、`change="changed"` 时，仅再提供 `boundary`、`confirmation`、`cases`；当前业务指纹的确认必须为 `confirmed`，按类型文本案例在 effective overlay 上通过。
- `change="unchanged"` 时，必须提供非空 `reason`，可带 `boundary`，不接受其他字段；如与架构边界变更声明冲突则阻断。报告保持 `unchanged/legacy_unknown`，不虚构历史批准，也不要求无关小修重写全部历史。
- 新维护快照冻结 target、candidate、effective 指纹及边界判定；Apply 使用同一计划重验，沿用原备份、写入、Verify 与 Undo。候选或目标漂移时停止。
- 旧 Native Plan 继续原合法 Apply 校验；已经符合 ADR 0011 架构审查政策的旧维护计划保留原合法 Apply、读取、Verify、Undo。缺新快照明确为 `legacy_unknown`，不补字段、不改旧 hash、不宣称具备新确认保护。新预览始终走新判定。

## 按能力安排候选文本案例

新创建与 `changed` 维护按策略选择类别，不机械凑五类：

| 条件 | 必需类别 |
|---|---|
| 所有新类型策略 | `success` 与 `insufficient`。 |
| 有排除能力或反触发 | 再加 `negative`。 |
| `interaction=multi_turn` | 再加 `drift`。 |
| `uses_tools=true` | 再加 `failure`。 |
| `has_side_effects=true` | 再加 `approval` 与 `failure`。 |

其他类别可省略。显式不适用案例只含 `id`、`category`、`status="not_applicable"`、非空 `reason`，单独统计且不计通过；不能借此豁免任何必需类别。

可执行案例只含 `id`、`category`、`given`、`expect`、`must_not`、`assertions`，不写 `status`。ID 必须非空且唯一；`given`、`expect` 为非空说明；`must_not` 必须提供，可为非空字符串、非空字符串列表或空清单，不为填表造禁令。`assertions` 只允许 `must_include`、`must_not_include`，值为字符串列表，实际条目必须非空，允许省略一键但至少有一条实际有效断言。无案例、无断言或空断言不通过并报告 `uncovered`；非法结构、未知断言、空字符串、非法/空 ID 或重复 ID 报告 `failed`。未传类型策略的旧调用只执行实际声明的断言，不虚构类别覆盖。

例如：候选正文已写明“有记录时输出摘要；缺记录时说明缺口，不猜测”，纯文本单次任务且明确无排除/反触发时，可用以下两例检查候选有没有写出承诺：

```json
[
  {"id":"summary-success","category":"success","given":"提供记录","expect":"输出摘要","must_not":["猜测事实"],"assertions":{"must_include":["有记录时输出摘要"]}},
  {"id":"summary-insufficient","category":"insufficient","given":"未提供记录","expect":"说明缺口","must_not":["编造记录"],"assertions":{"must_include":["缺记录时说明缺口，不猜测"]}}
]
```

## 三层证据与限制

结构检查说明文件、契约和就绪度；上述声明式检查只比较候选 Markdown，固定报告 `evidence_kind=candidate_text`、`utility_claim=false`；真实宿主试用另记输入、行为与产物证据。字符串通过不证明真实多轮纠偏、停止、工具失败恢复或用户审批已发生，不能据此进入 `validated`。

标准库规则的唯一实现源是 `src/skill_engineering/boundary_policy.py`，随 Skill 的 `scripts/boundary_policy.py` 是生成副本并做字节一致性回归；两种安装表面不相互依赖 Python CLI。真实试用、自测与生产评测仍按[创建评审](creation-review.md)及[证据标准](evaluation-standard.md)分别报告。不在本流程附带通用运行时监控、自动模型评测平台或批量修改历史 Skill。

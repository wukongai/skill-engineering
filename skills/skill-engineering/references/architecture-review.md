# 维护架构审查

[返回文件地图](file-map.md) · [执行内部阶段](../stages/architecture-review/INSTRUCTIONS.md) · [维护协议](maintenance-protocol.md) · [开发治理](development-governance.md)

本规范是架构声明 JSON 字段的单一参考。阶段负责组织证据，现有 `improve` 验证声明并保存预检快照；写入仍使用原维护引擎。

## 进入范围与轻重

维护已有 Skill 时默认进入本阶段，先复用已确认的产品边界与能力判断。普通小修保持轻量：核对归属、旧路径处置及受保护行为，使用轻量声明；只有整体门触发时才组织完整独立评审。全新 Skill 没有现有目标和维护历史，继续 Native Authoring，不要求本轮维护 JSON、`improve` 或历史基线。

需求决策只允许四类：`extend` 扩展已有归属、`refactor` 调整内部结构且保护承诺、`split` 应拆分后重新规划、`defer` 延后。后两类阻断当前候选应用，并给出唯一下一步；它们不会自动创建另一个 Skill 或产品。

## 两个完成门

- **本次维护完成门**：本轮范围、目标、计划、安全与回归要求得到满足。回归路径登记与 lint/Doctor 通过不代表真实行为测试已执行；执行结果仍需相应证据。原有修复轮次上限的执行缺口不在本阶段修复。
- **整体架构完成门**：单独说明完整 effective candidate 的职责、路由、接口、状态、失败与回滚是否有足够审查证据。它不由本轮增量、结构分数或前一轮局部修改自动推导。

出现以下任一情况时要求整体评审：没有有效整体基线；声明边界变化；相对整体基线的累计预算超限；同一开放债务再次出现；调整整体基线预算；历史因果顺序无法唯一确定。普通局部修改不刷新整体基线。整体评审可以有依据地接受增长，但报告保留预算超限事实。

基线只能来自同一目标、仍为 applied、正式 Verify 通过且包含有效完整评审的维护记录；目标的 after 指纹必须等于被评审的 effective 指纹。已撤销、回滚、错误目标、仅 Apply 后检查通过或未 Verify 的记录不能作为基线。未指定基线且历史因果顺序可唯一确定时，选最新有效记录；旧历史无法证明的债务覆盖明确列为限制。

历史记录使用既有 before/after 指纹链还原因果顺序。同秒 `created_at` 与随机记录 ID 不能证明先后；无法唯一确定时，`history_ambiguous` 作为整体审查触发原因，保守保留已知债务，不据此自动清债或选择较新基线。反馈显示历史覆盖限制，债务数量仅称为已知数量。

## 声明字段

顶层只接受下表字段，拒绝未知字段与错误类型。所有自由文本仅写脱敏摘要，不保存原始私有 Prompt、凭证或完整会话。

| 字段 | 约束 |
|---|---|
| `schema_version` | 字符串 `1`，不能使用数字。 |
| `requirement` | 含 `summary`、`decision`、`rationale`、`owner`、`replacement_plan`、`protected_behaviors`、`touched_boundaries`。前五项为非空摘要，后两项为列表。归属与旧结构处置必须有理由；无需替换时也说明保留什么、为何保留。 |
| `baseline_record_id` | 可选；必须解析为上述有效整体基线，不能随意指向最近一次局部维护。 |
| `budgets` | `skill_md_lines`、`instruction_files`、`duplicate_instruction_lines`、`open_debt` 的非负整数上限；布尔值不算整数。真实指标由完整候选计算，声明不能代填。 |
| `debt` | `{id, summary}` 列表，ID 稳定且本次不重复，摘要脱敏；未解决历史项持续保留。 |
| `resolved_debt_ids` | 显式关闭既有债务 ID 的列表，局部修改不能通过空列表清掉历史。 |
| `full_review` | 可选；整体门触发时必须补足。包含下述完整评审字段。 |

前三项复杂度预算约束相对整体基线 `complexity.after` 的净增长；`open_debt` 按归并后所有未关闭 ID 的绝对数量计算，包括基线已有债务，不能只统计本次新增项。

`touched_boundaries` 和 `full_review.checked_areas` 仅使用 `ownership`、`routing`、`interfaces`、`state`、`failure`、`rollback`。无边界变化使用空的 touched 列表，不省略已发生的变化。

完整评审字段为三个 64 位十六进制指纹 `target_fingerprint`、`candidate_fingerprint`、`effective_fingerprint`，以及 `checked_areas`、`conclusion`、`reviewer`、`evidence_summary`。三个指纹分别绑定原目标、候选目录、overlay 加显式删除后的完整树；只看补丁片段不足以形成整体结论。`checked_areas` 覆盖全部六项，`conclusion` 仅为 `pass` 或 `changes_requested`；后者阻断应用。

候选生成者将完整候选交给独立评审者检查，由评审者提供身份和证据摘要。工具验证声明、指纹、历史与预算，无法证明 reviewer 身份独立或其语义判断正确；作者自填通过声明不能代替独立评审，也不能充当真实行为测试通过。

下例仅演示字段形态。指纹必须换为工具对实际输入计算的值，证据必须来自实际评审；不要把演示声明提交为真实评审。

```json
{
  "schema_version": "1",
  "requirement": {
    "summary": "扩展已有维护流程的内部架构审查",
    "decision": "extend",
    "rationale": "归属现有维护能力，复用原计划与应用边界",
    "owner": "Skill Engineering 维护流程",
    "replacement_plan": "保留原预览、Apply、Verify、Undo；不退役旧路径",
    "protected_behaviors": ["目标与候选漂移拒绝", "写后失败回滚"],
    "touched_boundaries": ["interfaces"]
  },
  "budgets": {
    "skill_md_lines": 10,
    "instruction_files": 3,
    "duplicate_instruction_lines": 0,
    "open_debt": 2
  },
  "debt": [],
  "resolved_debt_ids": [],
  "full_review": {
    "target_fingerprint": "1111111111111111111111111111111111111111111111111111111111111111",
    "candidate_fingerprint": "2222222222222222222222222222222222222222222222222222222222222222",
    "effective_fingerprint": "3333333333333333333333333333333333333333333333333333333333333333",
    "checked_areas": ["ownership", "routing", "interfaces", "state", "failure", "rollback"],
    "conclusion": "pass",
    "reviewer": "独立评审者标识",
    "evidence_summary": "已检查完整候选与六项边界；真实任务行为证据另行核对"
  }
}
```

## 交回原维护引擎

1. 在独立候选完成变更，并按 overlay 与显式删除清单还原完整 effective candidate。未出现在候选里的旧文件默认保留；替换/退役说明必须列出旧路径、受保护行为、兼容及恢复方式，实际删除仍显式进入原计划。
2. 可先用不含完整评审的轻量声明生成预览，读取工具计算的三个输入指纹及复杂度。整体门触发时，这份预览会被阻断，只用于获取事实；完成独立评审后，再补齐声明生成最终预览。缺少声明也只产生阻断预览和真实指纹，不能视为已审查。
3. 新维护预览必需 `improve --architecture-review PATH`。该参数读取声明，不执行其中命令、脚本或代码，也不执行候选脚本。
4. 查看 `preflight.architecture_review`：声明快照已嵌入原计划，受原 plan hash 保护；替换原输入文件不会改变已预览结论。报告更改、目标或候选漂移均需重新预览。
5. preflight 通过且已获批准后，只应用同一 plan id，再走原 postflight、`verify-improvement`、history 与 undo。不存在新的 Apply 链路或额外安装动作。

CLI 与核心在预览和应用两处执行门禁，所有 profile 一致，不提供跳过参数或免审开关。缺少声明的新预览返回 blocked 和非零退出码；旧计划缺少有效通过快照或标记 unreviewed，即使旧总预检为 pass，也不能应用。唯一下一步是补齐审查并重新预览，不能给旧计划补传声明来沿用旧审批。

使用 `improve --plan ID --apply` 时只验证冻结快照，不需再次传入 JSON；同时传 `--architecture-review` 会被拒绝，必须生成新预览。历史计划仍可查看，记录仍可 Verify/Undo；不补写旧字段或重算旧哈希。包含有效审查快照且未漂移的计划可继续使用。

Active 发布更新 maintained source 时同样执行此门禁：宿主先对不可变 version source 与当前目标形成实际审查，再通过 `release-plan --channel active --architecture-review PATH` 提交，复用原维护子计划。Shadow/Canary 不更新该维护目标，不要求维护声明，也不接收该参数。发布审批、验证与恢复继续走原链路。

## 结果与下一步

按顺序说明本次维护结果、整体架构结果、累计增长/已知开放债务、历史覆盖及证据限制和唯一下一步。历史有缺口或歧义时，不能把已知债务数量当成全部债务。新预览 `status` 为 `pass` 或 `blocked`；`unreviewed` 仅用于显示历史未审查记录。缺声明时债务覆盖未知，不报告债务已清零。整体门的要求、触发原因与证据单独列在 `whole_review`。静态结构、声明性架构评审和真实行为测试分开报告。

可使用这样的摘要：“本轮文件变更检查已通过；整体架构尚未审查。累计增长和未解决债务已保留。下一步提交完整候选给独立评审者。”只有声明与所需整体审查都满足时，才说明架构审查声明通过，不能据此声称真实任务效果已验证。

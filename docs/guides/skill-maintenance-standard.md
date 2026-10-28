# Skill 持续修改治理标准

第一次创建 Skill 只决定初始结构;长期质量取决于后续每次修改能否定位根因、控制复杂度并保护旧行为。

## 必填维护意图

每次改进必须说明:

- 失败模式或新增能力;
- 最低根因层级:trigger/interface/state/script/style/long-task/install/structure/test;
- 修改后必须成立的预期行为;
- 回归用例;personal/team 确实不适用时写明理由,production 不允许豁免。

## 标准流程

```text
需求归属与旧结构处置
  -> 独立候选目录
  -> 按需整体评审与架构声明
  -> improve preview
  -> 文件增删改 + 复杂度变化 + preflight
  -> 用户确认同一 Plan ID
  -> apply
  -> postflight
  -> 维护记录
  -> verify / history / undo
```

示例:

```bash
skill-engineering improve /path/to/skill \
  --candidate /path/to/candidate \
  --architecture-review /path/to/review.json \
  --failure-mode "description 过宽导致误触发" \
  --root-cause-layer trigger \
  --expected-behavior "只有明确请求才触发" \
  --regression-case tests/cases/trigger.yaml

skill-engineering improve --plan PLAN_ID --apply
skill-engineering verify-improvement --record RECORD_ID
skill-engineering maintenance-history --target /path/to/skill
skill-engineering undo-improvement --record RECORD_ID --apply
```

## 复杂度增量

每份计划比较修改前后:

- 根入口行数和 description 长度;
- 门禁/禁令词与事故复盘措辞;
- 指令文件数和总文件数;
- 跨入口、references、stages 的重复长指令;
- 候选未包含但默认保留的旧文件。

MAINT101-110 区分 WARN 与 FAIL。最终快照得分相同,不代表修改过程没有增加债务;因此必须同时看 delta。当前源码增量的 MAINT111 负责架构声明阻断，沿用同一 preflight/Apply 边界。

## 内部架构审查（未发布增量）

本节对应当前源码工作区；正式 `1.1.0` 安装不因此自动升级。Agent 维护已有 Skill 时先判断扩展、重构、拆分或延后，说明旧结构保留/替换/退役及受保护行为。全新创建继续 Native Authoring。

高级 CLI 的新维护预览必须提供 `--architecture-review /path/to/review.json`；宿主 Agent 根据实际候选准备声明，无需用户手工提醒。完整字段只在[架构审查规范](../../skills/skill-engineering/references/architecture-review.md#声明字段)维护，避免另一份 JSON 合同。缺声明返回阻断预览与实际指纹，退出码为 1。所有 profile 一致，无跳过开关；普通小修仍可用轻量声明。

首次没有有效基线、边界变化、累计预算超限、重复开放债务、预算调整或历史顺序不明确时，要求独立评审完整 effective candidate。可先用轻量声明生成受阻预览取得真实指纹；独立评审后补齐声明并生成最终计划。原目标、候选、overlay/显式删除后的完整树分别绑定，不将最终 plan hash 反存进声明。

前三项结构预算使用相对上次整体审查基线的净增长；开放债务使用全部未关闭 ID 的绝对数量。局部修改不刷新整体基线。同秒历史以原 before/after 指纹确定因果顺序，无法唯一确定则保守保留已知债务并要求整体审查。

审查报告保存到原 `preflight.architecture_review` 并受原计划哈希保护。Apply 重新核对冻结快照及实际完整候选指纹。旧缺声明或 unreviewed 计划必须补审后重新预览；历史查看、Verify 和安全 Undo 保持，不补字段、不重算旧哈希。按同一计划 Apply 时不再次提供声明，补传参数会被拒绝。Active 更新使用 `release-plan --channel active --architecture-review /path/to/review.json`，复用同一维护门禁；Shadow/Canary 不接收此维护参数。split/defer 或所需完整评审未通过时不能应用；通过后仍只走原 Apply/Postflight/Verify/Undo。案例登记不等于已执行回归，架构声明不等于真实行为效用；反馈必须披露历史覆盖限制。

[原阶段需求](../specs/2026-10-29-maintenance-architecture-review-spec.md) · [默认强制审查需求](../specs/2026-10-29-mandatory-architecture-review-spec.md) · [当前验证记录](../testing/2026-10-29-mandatory-architecture-review.md)

## 删除规则

- 候选目录是 overlay,不是完整替换。
- 候选缺少旧文件时默认保留。
- 删除必须显式传 `--delete <relative-path>` 并进入 plan。
- 不允许删除 `SKILL.md`。
- 修改目标或候选漂移后,旧 plan 失效。

## 验证与恢复

- preflight 和 postflight 只运行确定性 lint/Doctor,不执行候选 Skill 的任意脚本。
- postflight 失败自动恢复修改前状态。
- 成功后生成 MaintenanceRecord 和本机备份。
- verify 检查当前目标是否仍等于修改后指纹。
- undo 仅在无漂移时恢复 update/delete 并移除本次 create。

## 好修复的判断

- 失败变成了用例,不是事故提醒。
- 约束落在最低可执行层,不是继续堆根入口。
- `SKILL.md` 更薄或至少没有无理由变厚。
- 旧行为得到保护,高风险边界没有退化。
- 修改有计划、证据、记录和恢复路径。

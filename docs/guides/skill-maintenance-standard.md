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
独立候选目录
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

MAINT101-110 区分 WARN 与 FAIL。最终快照得分相同,不代表修改过程没有增加债务;因此必须同时看 delta。

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

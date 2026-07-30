# Hermes 适配

Hermes 通过 `skill_manage` 工具家族完成创建闭环,不使用任何 Hermes 专用作者 Skill。

## 创建路径

1. Authoring Brief 就绪后,由 Native Authoring Kernel 生成完整候选内容;
2. 写入前形成与其它宿主相同的 candidate manifest 与 fingerprint；有可用 Python
   和隔离文件目录时使用 `scripts/native_plan.py preview`，否则使用
   Agent-native 等价 plan，展示全部文件和 fingerprint 后停在确认点；
3. 用户确认同一份未漂移 plan 后，使用 `skill_manage(create)` 写入完整
   `SKILL.md`——一次性传入任务专属完整内容，不得先建骨架再补；
4. 使用 `skill_manage(write_file)` 逐个写入 supporting files
   (references、scripts、assets、templates、tests)，再按 plan 复验写后
   manifest；有 Python 时继续运行 `scripts/skill_self_test.py`。

## 审批与安全

- `skills.write_approval` 开启时,尊重 Hermes 的 pending/diff/approve 流程:候选进入 pending,展示 diff,等待 approve;不得绕过审批直接写入;
- 使用 Hermes 安全扫描结果作为附加门禁;扫描命中时状态不得高于 `candidate_incomplete`;
- 外部 Skill 目录和 Profile 范围必须显式识别并告知用户,避免写错目标。

## 禁止

- 禁止调用 `hermes-agent-skill-authoring` 生成内容;
- 禁止调用 `/learn` 生成内容;
- 禁止在骨架阶段提前结束并报告“Skill 已完整创建”。

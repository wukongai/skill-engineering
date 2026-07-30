# Kimi CLI 适配

Kimi CLI 使用宿主提供的文件编辑、终端和审批能力完成创建闭环。

## 创建路径

1. Authoring Brief 就绪后,由 Native Authoring Kernel 生成完整候选;
2. 优先创建在当前项目的标准 Skill 目录(`.agents/skills/<name>/`);用户要求共享或全局范围(`~/.agents/skills/`)时,先展示实际目标和影响,确认后才写入;
3. 候选先落隔离目录；有 Python 时使用 `scripts/native_plan.py preview`
   固定 Brief、candidate fingerprint、文件清单和 target；
4. 用户确认实际文件后只对同一 plan/candidate/target 执行 `apply` 与 `verify`,
   再运行 `scripts/skill_self_test.py`；没有 Python 时按 Agent-native 等价
   plan 清单执行并明示。

## 边界

- 可选元数据不支持时保留共同基线,不伪造支持;
- 审批问题必须描述实际动作、作用范围和能否撤销。

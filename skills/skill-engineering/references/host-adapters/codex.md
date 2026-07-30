# Codex 适配

Codex 使用宿主提供的文件编辑、终端和审批能力完成创建闭环。

## 创建路径

1. Authoring Brief 就绪后,由 Native Authoring Kernel 生成完整候选;
2. 优先创建在当前项目的标准 Skill 目录(如 `.agents/skills/<name>/`);用户要求共享或全局范围时,先展示实际目标和影响,确认后才写入;
3. 候选先落隔离目录；有 Python 时运行 `scripts/native_plan.py preview`，
   展示 plan 中的实际文件、fingerprint 和 target；没有 Python 时展示
   Agent-native 等价事实清单；
4. 用户确认后只对同一 plan/candidate/target 执行 `native_plan.py apply`，
   再运行 `verify`；不得直接调用 legacy `skill-engineering create` 写空骨架；
5. 写后运行 `scripts/skill_self_test.py`；完整 CLI Doctor 只作为可选增强。

## 边界

- 可选元数据(如 `agents/openai.yaml` 的 UI 展示配置)按共同基线生成,不伪造宿主特定支持;
- 审批问题必须描述实际动作、作用范围和能否撤销。

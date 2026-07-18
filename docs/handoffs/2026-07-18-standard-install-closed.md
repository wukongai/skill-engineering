# Skill Engineering 标准安装入口阶段关闭与 runtime 阻断交接

状态：`closed`；后续 Agent Skill-only runtime 验收与 `v1.0.0` 正式发布均已完成

日期：2026-07-18

PM 独立复核：PASS；安装文档/installer entry 子任务已关闭。后续 runtime/bootstrap、tag 与 GitHub Release 门禁也已完成，整个 1.0 发布任务现已关闭。

## 已关闭范围

- 普通用户以标准 `npx skills add` / `npm exec` 安装 Agent Skill；
- Codex、Claude Code 等宿主通过 `-a` 选择 adapter，项目范围与 `-g` 全局范围有明确说明；
- README 和安装指南不再要求普通用户手工 clone；clone/fork 仅用于源码学习、二次开发、开发测试和贡献；
- 远程默认分支 `main` 只发现并安装唯一的 `skill-engineering`；
- 本地与远程的安装器发现/identity 门禁已有版本化证据；Skill validation、production Doctor 和 1.0 RC 质量门禁是在 Python CLI 已可用的环境中执行。

验收候选：`df6d1068a309eeb82a3ca7b721d40d72294879d0`。

## 未包含在本任务

- `v1.0.0` tag 和 GitHub Release；二者继续保留为独立授权点；
- 真实用户 Global/Profile 目录变更；本次只使用一次性 HOME；
- Agent Skill 与 Python CLI 合并为单一安装包。

## 后续独立任务

任务建议：**Agent Skill-only runtime 自检与 bootstrap**。

复现事实：标准远程安装只复制 `skills/skill-engineering/`。在没有安装 Python 包的干净环境中执行随包 `scripts/doctor_skill.py`，会因 `skill_engineering` 模块不存在而失败。后续任务需要在以下方案中做 Spec/Plan 决策：

1. 让必要的 Doctor 能力在 Skill 包内自包含；
2. 在脚本中增加确定性的依赖检测和面向普通用户的安装提示；
3. 提供经过安全审计的 Agent Skill + Python CLI 双轨一键安装或 bootstrap。

该问题不影响“标准安装器能正确发现并安装唯一 Agent Skill”的已完成结论，但会阻断“普通用户只安装 Agent Skill 即可完成 create → apply → doctor”的完整验收。在 runtime/bootstrap 复验通过前，不能把标准安装 Spec 标成 fully accepted，也不能在发布文案中隐去。

## 下一任务入口

本 Handoff 已完成使命。runtime/bootstrap 的独立 Spec/Plan 与远程复验已经通过；`v1.0.0` 发布完成。下一窗口直接按 `docs/sprints/2026-07-v2.0-architecture-guardian.md` 继续 2.0 fixture 与只读 inventory，不再回开 1.0 安装入口讨论。

# ADR-0007：普通用户默认使用简约交互式安装

状态：Accepted

日期：2026-07-22

## 背景

ADR-0004 已决定使用标准 `skills` CLI，而不是 `git clone`，作为 Agent Skill 的普通用户入口。1.0 发布时为了固定 Skill、宿主、范围和确认行为，README 使用了包含 `--skill`、`-g`、`-a` 和 `-y` 的完整非交互命令。

这条命令适合发布回归和 CI，却把四个可选决策提前暴露给第一次安装的用户。Vercel Labs `skills` CLI 的官方基础用法是 `npx skills add owner/repo`，安装器能够交互选择 Skill、宿主和范围。

## 决策

1. Skill Engineering 普通用户的唯一默认安装命令是：

   ```bash
   npx skills add wukongai/skill-engineering
   ```

2. README 不要求用户理解或手动修改 `--skill`、`-g`、`-a` 和 `-y`。
3. 安装器交互负责选择 `skill-engineering`、目标 Agent 和 project/global 范围。
4. 完整参数形式继续作为 1.x 兼容的高级、CI 和非交互入口。
5. 历史发布证据保留当时真实执行的完整命令，不追溯改写。
6. `git clone` 仍只用于源码学习、二次开发、开发测试和贡献。

## 对 ADR-0004 的影响

本 ADR 不推翻“使用标准 `skills` CLI”的架构决策，只细化普通用户默认命令。ADR-0004 中显式指定 `--skill` 的默认形式被本 ADR 取代；其标准安装器、范围治理和 clone/dev 边界继续有效。

## 备选方案

- **继续把完整命令作为默认**：拒绝。可复制但理解成本高，并把 CI 需求强加给普通用户。
- **为 Codex 和 Claude Code 分别提供命令**：拒绝。重复内容，且安装器已经支持交互选择。
- **使用手工复制或 clone**：拒绝。破坏标准安装、更新和移除路径。

## 后果

- README 的首次成功路径缩短为一条命令；
- 普通用户需要完成安装器交互选择，但不需要记忆参数；
- CI 和远程回归仍可显式使用完整参数，兼容性不变；
- 当前安装指南、1.x 契约、治理规则和回归测试必须统一默认命令。

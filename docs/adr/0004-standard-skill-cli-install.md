# ADR-0004：使用标准 `skills` CLI 作为普通用户安装入口

状态：Accepted with release gate

日期：2026-07-16

## 背景

Skill Engineering 的目标角色是直接使用 Agent Skill 的用户。把 `git clone` 作为默认安装方式会迫使用户接触源码仓库、分支和开发依赖，也无法与其他公开 Agent Skill 的安装体验保持一致。

## 决策

1. 普通用户统一使用 `npx skills add wukongai/skill-engineering --skill skill-engineering` 安装。
2. 全局使用时加 `-g`；项目共享时省略 `-g`；需要固定宿主时使用 `-a codex` 或 `-a claude-code`。
3. `npm exec --yes skills -- add ...` 作为等价 npm 入口，不新增 Skill Engineering 自己的 npm 包。
4. `git clone` 和 fork 只用于源码学习、二次开发、运行开发测试和贡献 PR。
5. 远程发布门禁要求安装源已包含 `skills/skill-engineering/`；旧 `v0.1.0` 仅含 `skills/skill-guide/` 时不得宣称标准安装成功。

## 备选方案

- **继续以 clone 为默认**：拒绝。用户体验和生态惯例不一致，且混淆使用与开发两类角色。
- **发布一个独立 npm 包承载 Skill**：拒绝。当前 Skill 是标准目录和 `SKILL.md`，`skills` CLI 已能安装 GitHub 仓库；新增 npm 包会制造第二个发布源。
- **只给出手工复制路径**：拒绝。无法提供稳定的范围、宿主选择和升级/移除体验。

## 后果

- README 与安装指南需要以 `npx skills add` 为首屏命令。
- 发布新统一入口版本是远程安装回归的前置条件；在此之前只能测试本地候选并保留阻断证据。
- 维护者仍可 clone/fork 仓库，但该路径不再代表普通用户的安装流程。

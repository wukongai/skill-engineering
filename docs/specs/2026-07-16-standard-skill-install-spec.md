# Skill Engineering 标准安装体验 Spec

状态：Partially accepted in `1.0.0` RC；标准安装器入口通过，Agent Skill-only runtime 验收未通过并保留为发布阻断

日期：2026-07-16

## 背景

当前安装指南把 `git clone` 写成了普通用户的第一步。这会把“直接使用 Agent Skill”和“下载源码进行学习或二次开发”混成一条路径，也让用户误以为必须维护本地仓库才能使用 Skill Engineering。

公开的 Agent Skills 生态已经提供统一的 `skills` CLI。普通用户应通过 `npx skills add`（或等价的 `npm exec`）安装发布的 Skill；只有需要阅读、修改或贡献源码的人才需要 clone 或 fork 源仓库。

## 目标

1. 普通用户从任意项目目录都能用一条标准 `skills` CLI 命令安装唯一的 `skill-engineering`。
2. 全局安装和项目安装都明确说明作用范围；默认不要求用户理解 Python 包或 Git。
3. Codex、Claude Code 等支持 Agent Skills 标准的宿主使用同一套公开入口，不再为每个宿主维护一套互相冲突的安装名。
4. 源码学习、二次开发、提交 PR 的路径单独说明为 clone/fork，不出现在普通用户的首选步骤中。
5. 文档不宣称远程旧版 `v0.1.0` 已具备统一 `skill-engineering` 入口；新版本发布后才允许执行远程安装回归并解除发布门禁。

## 非目标

- 不把 Python wheel 当作普通用户安装 Agent Skill 的默认入口；wheel 只服务 CLI 开发和维护者。
- 不在本次引入一个新的 npm 运行时包；`skills` CLI 是安装器，不替代仓库中的 Python 工程核心。
- 不自动执行真实用户的 Global 安装、公开发布、打 tag 或推送。
- 不删除 GitHub 源码仓库；源码入口继续用于学习、fork 和贡献。

## 用户路径

### 直接使用（默认）

```bash
npx skills add wukongai/skill-engineering --skill skill-engineering -g -a codex -y
```

在 Claude Code 中，将 `-a codex` 换成 `-a claude-code`；在项目内共享安装时去掉 `-g`。不确定宿主时可省略 `-a`，让安装器检测当前环境。

等价的 npm 写法是：

```bash
npm exec --yes skills -- add wukongai/skill-engineering --skill skill-engineering -g -a codex -y
```

安装后，用户只需在任意项目中直接提出创建、检查、评测或维护 Skill 的请求；唯一用户可见名称是 `skill-engineering`。

### 源码学习与二次开发（可选）

```bash
git clone https://github.com/wukongai/skill-engineering.git
```

需要长期维护自己的分支时，可以先 fork，再 clone 自己的 fork。该路径用于阅读源码、运行开发测试、修改实现和提交 PR，不是普通用户的安装前置条件。

## 验收标准

1. README 和外部安装指南的首个安装命令是 `npx skills add` 或等价 `npm exec`，不是 `git clone`。
2. 文档明确区分“直接使用”和“源码学习/二次开发”，且 clone/fork 只出现在后者。
3. 安装命令固定选择 `--skill skill-engineering`，不会安装旧的 `skill-guide` 或两个并列入口。
4. 隔离 HOME 中用标准 CLI 安装后，Codex/Claude 目标目录只出现 `skill-engineering`；只安装 Agent Skill 的干净环境必须能够完成 create preview → apply → doctor，或在缺少 Python runtime 时给出确定、可执行且不误报成功的依赖检测与安装引导。
5. 当前远程旧 `v0.1.0` 若仍暴露 `skills/skill-guide/`，测试必须失败并记录为发布阻断，而不是修改文档去适配旧入口。
6. 运行 pytest、Ruff、Skill validation、production Doctor、凭证 lint、`git diff --check` 和安装器隔离 smoke。

## 验收结论（2026-07-18）

- 远程默认分支 `main` 与 `1.0.0` 候选提交 `df6d106` 一致；
- 标准远程命令在一次性 HOME 中完成安装，输出 `Found 1 skill`、`Selected 1 skill: skill-engineering` 和 `Installation complete`；
- 安装目标只包含 `skill-engineering`，没有重新暴露 `skill-guide`；
- README、安装指南和安装治理 reference 均以 `npx skills add` / `npm exec` 作为普通用户入口，clone/fork 仅保留在源码学习与二次开发路径；
- 安装器发现、canonical identity、文档拆分和远程默认分支 smoke 已完成；`v1.0.0` tag、GitHub Release 和真实 Global/Profile 变更仍需分别授权。

验收标准 4 尚未整体验收：Agent Skill 与 Python CLI 是两个独立交付面，只安装 Agent Skill 不会安装 Python 包；随 Skill 分发的 `doctor_skill.py` 在干净环境中会因缺少 `skill_engineering` 模块而失败。runtime 自检/bootstrap 必须通过独立 Spec/Plan 补齐，并在正式发布前回到本 Spec 完成最终验收；在此之前不得宣称 Agent Skill-only 环境已完成 create → apply → doctor 闭环。

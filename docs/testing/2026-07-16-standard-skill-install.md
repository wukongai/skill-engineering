# 标准 Skill 安装体验回归（2026-07-16）

状态：历史本地回归；当时的远程阻断已由 2026-07-18 默认分支复验解除

## 结论

本地统一候选已通过标准 `skills` CLI 的隔离安装；后续创作检查使用了已经安装 Python CLI 的验证环境，不代表 Agent Skill-only 干净环境已经具备完整 runtime。普通用户入口应使用 `npx skills add`，源码仓库的 clone/fork 只保留在开发路径。2026-07-16 执行本报告时，远程 `v0.1.0` 仍是旧 `skill-guide` 入口；该 identity 阻断已在 2026-07-18 的 `1.0.0` 默认分支候选上解除，但 runtime/bootstrap 阻断仍保留。

## 隔离安装

在一次性 HOME 和一次性 npm cache 中执行：

```bash
npx --yes skills add /Users/aim5/Documents/CodingProject/skill-engineering \
  --skill skill-engineering -g -a codex -y
```

安装器实际输出：

- `Local path validated`
- `Found 1 skill`
- `Selected 1 skill: skill-engineering`
- `Installation complete`
- Codex 目标目录：`~/.agents/skills/skill-engineering`

检查结果：安装目录只有 `skill-engineering/SKILL.md`、contract、references、scripts 和 tests；没有 `skill-guide` 并列入口。

## 安装后使用回归

1. 在 Python CLI 已可用的验证环境中，对隔离安装的 `skill-engineering` 运行 `doctor --profile production`：100/A，通过。
2. 在独立临时项目执行 `create` preview：只生成 plan，不写入目标目录。
3. 使用同一 plan id 执行 `create --apply`：创建成功，postflight 通过。
4. 对新建 Skill 运行 `doctor --profile team`：可继续测试；production profile 的评测证据要求属于新建 Skill 自身的后续质量门禁，不是安装器故障。

## 文档验收

- README 首个安装入口为 `npx skills add ... --skill skill-engineering`。
- README 明确区分全局 `-g`、项目范围和 Codex/Claude Code agent 参数。
- README 和外部安装指南都把 clone/fork 放入“源码学习与二次开发”，没有把它写成普通用户前置条件。
- `npm exec --yes skills -- add ...` 作为等价 npm 入口保留。

## 当时的发布阻断（已解除）

当前 GitHub `v0.1.0` 远程内容仍只有 `skills/skill-guide/`。在统一入口版本发布前，从远程执行标准命令会安装旧入口或无法匹配 `--skill skill-engineering`，所以发布门禁保持 blocked；不得用本地候选结果替代远程版本声明。

## 2026-07-18 远程默认分支复验

- `git ls-remote` 确认远程 `HEAD` 和 `refs/heads/main` 均为 `df6d1068a309eeb82a3ca7b721d40d72294879d0`；
- 在一次性 HOME 和 npm cache 中执行 `npx --yes skills add wukongai/skill-engineering --skill skill-engineering -g -a codex -y`；
- 安装器输出 `Repository cloned`、`Found 1 skill`、`Selected 1 skill: skill-engineering`、`Installation complete`；
- 安装目录仅为一次性 HOME 下的 `~/.agents/skills/skill-engineering`，真实用户全局目录未修改；
- 远程默认分支安装门禁通过。后续 `v1.0.0` tag 与 GitHub Release 已单独授权并正式发布。

边界说明：标准安装器只安装 Agent Skill，不会同时安装 Python CLI。Agent Skill-only 环境的依赖检测已在后续独立 Spec/Plan 中完成：缺 CLI 时给出固定版本安装指引，安装同版 CLI 后 create → apply → doctor 闭环通过。

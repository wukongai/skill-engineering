# 简约交互式安装规格

状态：Implemented and verified

日期：2026-07-22

## 失败模式

README 当前把 `--skill`、`-g`、`-a` 和 `-y` 全部放进普通用户的第一条安装命令。虽然命令可执行，但它把 Skill 选择、安装范围、目标宿主和跳过确认等高级决策提前暴露给第一次使用者，造成不必要的理解和复制成本。

安装治理、1.x 公开契约和回归测试又把长命令冻结为默认入口，使 README 无法单独简化。

## 官方依据

Vercel Labs `skills` CLI 官方 README 与 skills.sh CLI 文档都把以下形式作为基础安装入口：

```bash
npx skills add owner/repo
```

安装器随后以交互方式处理 Skill、宿主和范围选择。`--skill`、`-g`、`-a` 与 `-y` 是可选参数，适用于高级定向或非交互自动化。

## 决策

Skill Engineering 普通用户的唯一默认安装命令改为：

```bash
npx skills add wukongai/skill-engineering
```

- README 不再解释或要求用户手动删改参数；
- 安装器负责交互选择 Codex/Claude Code 和 project/global 范围；
- 长参数形式继续兼容，但只作为 CI、脚本化或明确知道目标范围的高级用法；
- `git clone` 继续只用于源码学习和开发；
- 历史发布验证记录保留当时真实使用的长命令，不追溯改写。

## 验收标准

- [x] 中英文 README 安装区只展示一条简约命令；
- [x] README 安装区不出现 `--skill`、`-g`、`-a` 或 `-y`；
- [x] 安装治理、安装指南、兼容指南和 1.x 公开契约使用同一默认命令；
- [x] ADR 说明本决策对 ADR-0004 的细化关系；
- [x] 长命令被明确降级为高级/非交互用法，不宣布失效；
- [x] 历史测试证据和历史 Spec 保持原样；
- [x] 回归测试锁定简约默认入口；
- [x] pytest、Ruff、Skill validation、credential lint 和 diff check 通过。

## 非目标

- 不修改 `skills` 安装器；
- 不执行真实安装、不改变用户本机 Skill 范围；
- 不删除 Python CLI 或改变 Agent Skill 行为；
- 不提交、不推送、不发布。

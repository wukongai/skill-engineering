# 2026-07-16 Skill Engineering 统一身份验证

## 结论

用户可见 Agent Skill 已从双名称收敛为单一 canonical 身份 `skill-engineering`。仓库顶层只保留 `skills/skill-engineering/`，frontmatter、contract、OpenAI metadata、CLI 文案、README、贡献文档和测试入口均使用同一名称。

本轮没有修改真实用户全局 Skill 目录，也没有执行 commit、push、tag 或公开发布。

## 回归范围

- 明确请求 `skill-engineering` 的正向触发；
- 仅做项目 harness/Claude/Codex/tmux 自检的反向边界；
- 隔离全局 Skill 根只暴露一个 `skill-engineering`；
- 临时 consumer project 完成 create preview、同一 plan apply 和 Doctor；
- 旧顶层 `skill-guide` 源目录不存在；
- wheel 构建、一次性虚拟环境安装和 CLI help。

## 结果

| 门禁 | 结果 |
|---|---|
| pytest | 120 passed |
| Ruff check | passed |
| Ruff format check | passed，32 files formatted |
| 官方 Skill validation | passed |
| production Doctor | 100/A，0 FAIL，0 WARN |
| credential lint | passed |
| `git diff --check` | passed |
| 隔离 global install/create/Doctor smoke | passed |
| wheel build | passed，当前 metadata 仍为 `0.1.0` |
| clean venv install + CLI help | passed，Python 3.13.12 / PyYAML 6.0.3 |

## 已知边界

- GitHub 远程 `v0.1.0` 真实克隆结果仍只有 `skills/skill-guide/`；统一后的用户指南会查找 `skills/skill-engineering/`，因此该旧 tag 的远程安装回归被正确阻断。
- 当前统一候选已在一次性 HOME 中通过 `uv tool install`、Codex 全局 symlink、production Doctor、create preview、同一 plan apply 和新建 Skill Doctor；新版本推送后仍需从远程 tag 原样复验一次。
- 1.0 Stable Contract 的 schema/兼容/发布证据任务尚未全部完成，不能把本轮身份统一单独宣称为 1.0 Stable。
- 本机旧全局 symlink 已因源目录迁移变成断链；替换为 `skill-engineering` 属于真实全局状态变更，必须单独确认后执行。

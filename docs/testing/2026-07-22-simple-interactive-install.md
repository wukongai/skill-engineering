# 简约交互式安装验证

日期：2026-07-22

状态：passed

## 目标

把 Skill Engineering 普通用户安装入口从包含四类高级参数的完整非交互命令，简化为官方 `skills` CLI 支持的仓库级交互式安装命令。

## 官方依据

- Vercel Labs `skills` CLI README：基础安装示例为 `npx skills add owner/repo`；
- skills.sh CLI 文档：安装器可以直接通过 `npx` 运行，不需要预先安装 CLI；
- `--skill`、`-g`、`-a` 和 `-y` 均为可选参数，分别用于定向 Skill、全局范围、目标宿主和跳过确认。

## 当前默认入口

```bash
npx skills add wukongai/skill-engineering
```

安装器交互选择 Skill、Codex/Claude Code 等宿主和 project/global 范围。普通用户不需要先理解任何参数。

## 实施范围

- 中文和英文 README；
- Agent Skill 安装治理 reference；
- 版权与安装单一事实源；
- 1.0 兼容指南和 1.x 公开契约；
- ADR-0007，并说明对 ADR-0004 的细化关系；
- 安装回归测试。

历史 release、testing 和旧 Spec 中的完整命令未修改，因为它们记录的是当时真实执行的非交互安装证据。

## 验证结果

| 检查 | 结果 |
|---|---|
| 中英文 README 安装区简约命令 | passed：各 1 次 |
| README 安装区高级参数 | passed：0 matches |
| 当前六个正式安装事实源默认命令 | passed：一致 |
| `python3 -m pytest -q` | passed：135 tests |
| `python3 -m ruff check src tests` | passed |
| Agent Skill `quick_validate.py` | passed |
| `bash scripts/credential-lint.sh --all` | passed |
| `git diff --check` | passed |

## 证据边界

本轮依据官方文档验证命令语法，并通过静态事实源和仓库回归验证一致性。没有实际执行安装，因此没有修改本机 Codex、Claude Code、project 或 global Skill 目录，也没有把本轮结果冒充远程安装 smoke。

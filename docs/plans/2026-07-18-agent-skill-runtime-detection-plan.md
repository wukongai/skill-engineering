# Agent Skill-only Runtime 依赖检测实施计划

状态：Completed

对应 Spec：`docs/specs/2026-07-18-agent-skill-runtime-detection-spec.md`

## 阶段

1. **Wrapper boundary**：只在 `scripts/doctor_skill.py` 的核心模块导入边界捕获“顶层 `skill_engineering` 不存在”，其他导入异常继续暴露。
2. **Actionable feedback**：输出双轨安装说明、固定 tag 的 `uv tool install` 命令和标准 Doctor 命令，并返回非零退出码。
3. **Isolation regression**：把 wrapper 复制到模拟安装目录，用隔离 Python 子进程验证没有仓库 `src/` 时的行为。
4. **Compatibility regression**：在仓库环境验证原 Doctor 路径仍可导入并执行。
5. **Remote golden E2E**：从远程默认分支安装 Agent Skill，在一次性项目完成创建和维护；先验证 Skill-only 指引，再安装同一候选 CLI 完成 Doctor。
6. **Release evidence**：回填标准安装 Spec/Plan、当前 Sprint、Task 和测试报告；完整门禁通过后再请求 tag/GitHub Release 的独立授权。

## 风险与恢复

- 错把 CLI 内部依赖损坏当成“未安装”：只处理 `ModuleNotFoundError.name == "skill_engineering"`。
- 指引依赖尚未创建的 tag：正式文案固定 `v1.0.0`，RC 回归使用同一候选 commit 安装；tag 仍是独立授权点。
- wrapper 与 CLI 行为漂移：wrapper 不实现 Doctor 规则，只负责导入、参数转发和依赖提示。
- 用户不使用 `uv`：本版本以 README 的稳定 CLI 推荐入口为唯一指引；其他包管理器继续在安装指南说明。

## 完成记录（2026-07-18）

- wrapper 仅捕获顶层 `skill_engineering` 缺失，返回退出码 2 和双轨安装指引；
- 隔离 `python -I` 回归确认 Skill-only 环境不输出 traceback；仓库环境 wrapper 兼容回归通过；
- 远程 `main` 提交 `086457c` 已完成标准安装、Skill-only 指引、固定候选 CLI 安装、create preview/apply 和 team Doctor；
- 正式 `v1.0.0` tag 与 GitHub Release 仍保留为独立授权点。

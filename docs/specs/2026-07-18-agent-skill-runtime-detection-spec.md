# Agent Skill-only Runtime 依赖检测 Spec

状态：Accepted

日期：2026-07-18

## 背景

标准 `npx skills add` 只复制 `skills/skill-engineering/`，不会安装 Python 包。远程真实用户回归已经证明：Agent 可以使用安装后的 Skill 完成需求澄清、预览、确认后创建和结构化维护，但直接运行随包的 `scripts/doctor_skill.py` 会因缺少 `skill_engineering` 模块而输出 Python traceback。

Agent Skill 与 Python CLI 是两个独立交付物，这是当前架构契约；本修复不在 Agent Skill 中复制 Doctor 核心，也不静默安装依赖。

## 目标

1. 只安装 Agent Skill 的环境运行 `scripts/doctor_skill.py` 时，不输出 traceback，不误报 Doctor 已通过。
2. 明确说明 Agent Skill 与 Python CLI 的安装边界，并给出稳定版 CLI 安装命令和安装后的标准 Doctor 命令。
3. 仓库源码环境或已经安装 Python CLI 的环境保持原有 Doctor 行为、参数和退出码。
4. 用隔离子进程回归真实的 Skill-only 目录形状，避免测试因仓库 `src/` 可见而产生假通过。

## 非目标

- 不把 Python Doctor 实现复制到 `skills/skill-engineering/`。
- 不在脚本中联网、自动安装、修改全局环境或选择包管理器。
- 不合并 Agent Skill 与 Python CLI 的发布生命周期。
- 不执行 tag、GitHub Release 或 Global/Profile 安装。

## 用户可见行为

当 Python 包不可导入时，脚本必须：

- 以非零退出码停止；
- 用简体中文说明缺少的是 Skill Engineering Python CLI；
- 提供 `uv tool install "git+https://github.com/wukongai/skill-engineering.git@v1.0.0"`；
- 提供安装后的 `skill-engineering doctor <skill-path> --profile <profile>` 示例；
- 明确 `npx skills add` 只安装 Agent Skill；
- 不出现 `Traceback`。

如果 `skill_engineering` 已经成功导入，但它的其他依赖缺失，则保留原异常，不把包损坏误诊为“尚未安装 CLI”。

## 验收标准

1. 隔离复制的 `doctor_skill.py` 在 `python -I` 下返回约定的依赖缺失退出码和可执行指引。
2. 输出不包含 traceback，且不包含成功、通过或 0 FAIL 等误导性结论。
3. 仓库环境的 wrapper 仍可运行真实 Doctor。
4. 远程默认分支安装后重跑 create → apply → doctor：Skill-only 路径给出确定性指引；按指引安装固定候选 CLI 后 Doctor 通过。
5. pytest、Ruff、Skill validation、production Doctor、credential lint 和 `git diff --check` 通过。

## 验收结论（2026-07-18）

- 远程 `main` 提交 `086457c` 的标准安装只发现并安装一个 `skill-engineering`；
- Skill-only 环境运行 wrapper 返回退出码 2，输出 Python CLI 安装命令和后续 Doctor 命令，不再出现 traceback 或成功误报；
- 使用 `uv tool install "git+https://github.com/wukongai/skill-engineering.git@086457c"` 在隔离目录安装同一候选 CLI 成功；
- 远程候选完成 create preview → 同一 plan apply → team Doctor，postflight 和最终 Doctor 均为 0 FAIL / 0 WARN；
- 全量 133 项 pytest、Ruff、官方 Skill validation、production Doctor 100/A、credential lint 和 diff check 通过。

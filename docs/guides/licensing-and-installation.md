# 版权与安装指南

这份指南是 Skill Engineering 的版权和安装单一事实源。它解决两个容易混淆的问题：仓库里的内容按什么规则使用，以及用户应该安装哪一个交付物。

## 版权政策

### 默认许可证：Apache License 2.0

除文件另有明确说明外，本仓库原创的以下内容均采用 Apache License 2.0：

- `src/` 中的 Python 包和 CLI；
- `skills/skill-engineering/` 中的 Agent Skill 指令、references、stages 和 contract；
- `tests/`、`scripts/`、schemas、examples 和 `docs/` 中的原创文档。

标准标识为 `SPDX-License-Identifier: Apache-2.0`，版权人为“艾笑”。完整条款以仓库根目录 [`LICENSE`](../../LICENSE) 为准。Apache-2.0 允许使用、复制、修改、分发、再许可和商业使用，并提供明确的版权与专利授权；使用者仍需遵守许可证条件，项目按“现状”提供且不承担许可证约定之外的保证或责任。

### 再分发、修改与来源追溯

分发本项目或衍生作品时，应以 Apache-2.0 原文为准。核心要求包括：

- 向接收者提供 Apache-2.0 许可证副本；
- 修改文件时给出显著的修改声明；
- 保留与衍生作品相关的版权、专利、商标和署名通知；
- 如果分发物包含本项目内容，以许可证允许的方式保留根目录 [`NOTICE`](../../NOTICE) 中适用的署名信息。

`NOTICE` 是信息性通知，不增加 Apache-2.0 之外的限制；[`CITATION.cff`](../../CITATION.cff) 是推荐引用方式，也不是额外许可条件。Apache-2.0 不强制公开修改后的源代码，也不要求在产品界面中展示营销署名。

### 不自动纳入 Apache-2.0 的内容

- 第三方代码、数据、截图、商标、引用和外部项目内容：按其原许可证或来源要求处理；
- 用户提供的 prompt、私有数据、生成的 Skill、运行结果和业务材料：项目不主张其所有权；
- `Skill Engineering` 名称、Logo 和其他品牌资产：Apache-2.0 不等于商标授权，具体见 [`TRADEMARKS.md`](../../TRADEMARKS.md)。

当前仓库没有捆绑 NVIDIA/SkillSpector 的源代码；相关内容是外部项目比较和来源记录，不能当作本项目 Apache-2.0 代码分发。

贡献者提交代码或文档时，必须拥有相应权利；除非明确声明并获项目接受，贡献按 Apache-2.0 进入项目。项目不接收凭证、客户数据或完整私有对话。

v1.0 正式 tag 前，项目通过 ADR 0006 从 MIT 候选迁移为 Apache-2.0；此前合法获得的 MIT 副本仍按其取得时的条款使用。`v1.0.0` 已按 Apache-2.0 正式发布。未来若再次改证，必须单独建立 ADR、迁移说明、贡献者沟通和版本门禁，不会在补丁版本中静默改证。

## 安装决策表

| 目标 | 需要安装 | 推荐范围 | 说明 |
|---|---|---|---|
| 贡献或修改仓库代码 | Python 包（editable） | 当前仓库 | `python3 -m pip install -e ".[dev]"` |
| 使用 CLI 创建/检查 Skill | Python CLI | 稳定版本发布后 | 使用固定版本的 `uv tool` 或 `pipx`；当前未发布版本先从源码运行 |
| 让 Codex/Claude 发现 Skill Engineering | Agent Skill（标准 `skills` CLI） | project-only 或 global | `npx skills add wukongai/skill-engineering --skill skill-engineering`；加 `-g` 为全局，省略 `-g` 为当前项目 |
| 多项目或全局复用 | Agent Skill + Hub 台账 | profile/global | 交给 Agent Skill Hub，先审计、备份、确认，再安装；不自动覆盖现有入口 |
| 使用插件、MCP 或 provider runtime | 对应插件/runtime | 按插件文档 | 不把 plugin/runtime 伪装成普通目录型 Skill |

Python 包安装不会自动暴露 Agent Skill；Agent Skill 安装也不会自动安装 Python CLI 依赖。需要完整本地闭环时，按自己的使用场景分别安装两者。

## 当前可执行路径

### 开发者

```bash
python3 -m pip install -e ".[dev]"
```

这是仓库贡献和本地验证路径，不代表已经完成公开包发布。

### Agent Skill（普通用户标准入口）

标准安装器是普通用户入口；先明确范围，再执行命令：

```bash
# 仅当前项目
npx skills add wukongai/skill-engineering --skill skill-engineering -a codex -y

# 所有项目可见（需要额外审计、备份和确认）
npx skills add wukongai/skill-engineering --skill skill-engineering -g -a codex -y
```

Claude Code 将 `-a codex` 换成 `-a claude-code`。升级和移除使用同一个 `skills` CLI；本项目不自动修改真实用户 Global 目录。

### 手动项目级 Agent Skill（开发或离线场景）

在目标项目根目录执行，先确认目标目录没有同名入口，再建立链接：

```bash
mkdir -p .agents/skills
ln -s /absolute/path/to/skill-engineering/skills/skill-engineering .agents/skills/skill-engineering
```

Claude Code 项目可将 `.agents/skills` 换成 `.claude/skills`。验证后删除该链接即可撤销；不要把仓库根目录直接当作 Agent Skill 安装。

### 稳定版本 CLI（计划路径）

1.0 稳定包发布后，用户应固定版本，例如：

```bash
uv tool install skill-engineering==1.0.0
# 或
pipx install skill-engineering==1.0.0
```

在 1.0 发布前，README 中的开发安装仍是唯一可复现路径；不得把未发布版本写成 PyPI 已可用。

## 全局安装与回滚边界

- Global/Profile 安装必须由 Agent Skill Hub 生成和执行计划；本项目不自动修改用户全局目录。
- 安装前应记录现有入口指纹，发现旧 `skill-guide` 时先停止并展示影响范围；替换必须可恢复。
- 卸载 CLI 使用对应的 `uv tool uninstall skill-engineering` 或 `pipx uninstall skill-engineering`；卸载 Agent Skill 只删除本次创建的链接/副本。
- 本项目不收集或管理安装所需凭证；任何第三方 provider 的凭证都应保留在项目和仓库之外。

## 面向运营与营销的承诺边界

可以承诺：Apache-2.0 开源核心、可自托管、允许商业使用和二次分发、提供显式专利授权、再分发时保留适用通知和来源链、CLI 与 Agent Skill 的安装边界透明、不会用封闭格式锁定用户。

暂时不要承诺：所有衍生作品必须开源、必须在产品 UI 展示艾笑、所有模型上的统一效果、托管协作已交付、企业 SLA、自动 Global 发布、用户生成 Skill 的独占版权或法律合规保证。

法律适用、第三方素材和用户业务内容仍需由使用者自行审查；本指南是项目工程政策，不替代法律意见。

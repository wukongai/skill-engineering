# 双语价值型 README 改版验证

日期：2026-07-21

状态：superseded；原始内容使用了错误的选题雷达文章，不能作为当前 README 的产品叙事证据

## 验证目标

确认根 README 已从英文功能说明改为中文价值型主版本，并提供完整英文对应版本；两个版本都以真实问题、用户结果、案例和快速上手为主线，同时保持版本、安装、许可证和能力边界准确。

## 输入依据

### 核心叙事

用户提供的“个人选题 Skill 改造”文章提出了本次 README 的核心判断：搜满 50 条热点不等于找到值得写的选题；成熟 Skill 的价值不只来自功能数量，而来自个人证据、独立来源、职责边界、交接协议和真实运行证据。

### 公开 README 对比

2026-07-21 只读对比了以下公开项目的 README 信息架构：

- [Anthropic Skills](https://github.com/anthropics/skills)：先解释概念和具体用途，再提供安装与最小示例；
- [Superpowers](https://github.com/obra/superpowers)：在安装前用完整用户旅程解释产品怎样改变 Agent 的工作方式；
- [OpenAI Codex](https://github.com/openai/codex)：首屏定义产品并快速分流用户，紧接 Quickstart；
- [LangChain](https://github.com/langchain-ai/langchain)：用一句品类定义和少量差异化价值建立认知；
- [Dify](https://github.com/langgenius/dify)：使用独立语言文件与页首语言切换，并把快速成功路径放在能力细节之前。

本次只采用信息架构原则，没有复制上述项目的宣传文案。

## 实施结果

- `README.md`：中文默认入口，页首价值主张、选题雷达故事、四个验证案例、目标用户、安装、CLI、路线、证据和边界；
- `README.en.md`：完整英文对应版本，保留相同事实与承诺边界；
- 两个版本使用页首 `简体中文 | English` 切换；
- `1.0.0` 明确为 Stable，`2.0.0` 明确为开发预览，未来方向明确为尚未交付；
- 仓库没有正式 3.0 事实源，因此只表达长期愿景，没有虚构版本范围或发布日期；
- 选题雷达明确为方法论案例，不冒充仓库内置产品；
- 四个 1.0 Use Case 链接到正式发布验证证据，并保留真实效用边界。

## 验证结果

| 检查 | 结果 |
|---|---|
| 两个 README 的仓库内相对链接 | passed |
| `python3 -m pytest -q` | passed：133 tests |
| `python3 -m ruff check src tests` | passed |
| Agent Skill `quick_validate.py` | passed |
| `bash scripts/credential-lint.sh --all` | passed |
| `git diff --check` | passed |

pytest 首轮暴露了三个受保护的 README 稳定措辞。最终版本恢复了许可证、标准安装和产品定位兼容文本，随后全量 133 项回归通过。

## 结论与证据边界

本次验证证明双语入口、仓库链接、稳定文案契约和现有代码/Skill 回归没有被 README 改版破坏。它不证明新营销叙事已经提升 GitHub 转化、安装量或真实任务效用；这些效果需要发布后的页面行为、用户反馈和真实使用数据继续观察。

## 跟进：安装入口前置

用户复核后指出，GitHub 标准 README 应在项目定位后立即提供安装，营销价值与案例不能阻断首次成功路径。本轮据此完成以下调整：

- 中文第一个主体章节改为“快速安装”，英文对应为 “Quick install”；
- Agent Skill、稳定 CLI 和自然语言开始方式整体移动到营销故事之前；
- 页首导航同步到新的安装锚点；
- 新增中英文安装顺序回归，要求标准安装早于价值故事，且每份 README 的标准 `npx` 命令只出现一次；
- 源码克隆仍保留在后部本地开发章节。

跟进验证结果：134 项 pytest 全部通过，Ruff、Agent Skill validation、credential lint、`git diff --check`、本地链接、代码围栏和中英文安装顺序检查全部通过。安装命令、版本、许可证、能力边界和营销案例内容没有改变。

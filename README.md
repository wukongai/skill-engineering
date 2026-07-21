# Skill Engineering

[简体中文](README.md) | [English](README.en.md)

> **把 Skill 做稳：从一句工作目标，变成可以长期信任、持续维护的 Agent 能力。**

当前稳定版本：[`1.0.0`](https://github.com/wukongai/skill-engineering/releases/tag/v1.0.0) · 下一阶段：`2.0.0` Architecture Guardian（开发预览） · local-first · provider-neutral · Apache-2.0

<!-- Stable positioning regression: rapidly create Agent Skills that are engineered from the first version through architecture-first rapid generation and lifecycle protection. -->

Skill Engineering 是一个帮助你创建、检查和长期维护 Agent Skill 的元 Skill。你只需要说出自己想完成什么，它会先判断是否真的需要 Skill，再把职责、触发边界、输出、风险和验证方式说清楚；你确认以后才写入。

[立即安装](#安装) · [它解决什么问题](#为什么需要-skill-engineering) · [查看真实案例](#四个真实-use-case) · [了解版本路线](#版本路线)

## 安装

普通用户只需要一条命令：

```bash
npx skills add wukongai/skill-engineering
```

安装器会引导你选择 Codex、Claude Code 等宿主，以及当前项目或全局范围，不需要先记任何参数。

安装完成后，直接对 Agent 说：

```text
用 Skill Engineering 帮我做一个 Skill。
先判断是否真的需要创建；如果需要，让我先看到职责边界和创建方案；
我确认以后再写入。
```

如果你已经有一个越改越乱的 Skill：

```text
这个 Skill 最近出现了一个真实问题。
请先判断问题发生在哪一层，告诉我会改什么、保留什么；
不要直接覆盖正式版本，把这次失败变成以后可以重复验证的场景。
```

升级和移除继续使用标准 `skills` 安装器，例如 `npx skills update` 和 `npx skills remove`。完整范围见[版权与安装指南](docs/guides/licensing-and-installation.md)。

## 为什么需要 Skill Engineering

把一个 Skill 写出来并不难。难的是：换一份输入以后仍然稳定，修改十次以后仍然清楚，接入真实工具以后仍然知道在哪里停下来。

很多 Skill 的第一版看起来能跑，长期使用后却会出现这些问题：

- 触发范围太宽，普通请求也会误触发；
- 原文没有的信息被模型自行补全；
- 每次出错都在 `SKILL.md` 末尾追加一条禁令；
- 新改动直接覆盖正式版本，旧能力被悄悄破坏；
- 目录越来越复杂，却没有清楚的职责和证据；
- 静态检查分数很高，但没人知道真实任务是否变好；
- 发布前没有预览，失败后也没有恢复路径。

Skill Engineering 解决的不是“怎样写出更多 Prompt”，而是：

> **怎样让一个 Skill 从第一版开始就边界清楚、能真实使用，并在持续修改后仍然可验证、可恢复、不会越改越乱。**

## Skill Engineering 1.0 做什么

```text
描述目标
  -> 盘点已有 Skill / Script / Plugin / 项目规则
  -> 判断是否真的需要创建 Skill
  -> 澄清职责、触发边界、输出和副作用
  -> 选择与风险匹配的最小架构
  -> 生成完整候选和写入预览
  -> 用户确认后应用并验证
  -> 用独立候选维护、评测、记录和恢复
```

### 1. 先判断，再创建

不是每个需求都值得做成 Skill。一次性任务可能只需要直接完成；确定性转换可能更适合脚本；需要鉴权、浏览器或外部工具的能力可能属于 Plugin/runtime。Skill Engineering 会先比较方案，而不是默认创建新目录。

### 2. 创建前先看清完整方案

在真正写文件以前，用户先看到：什么时候触发、什么时候不触发、输入输出是什么、会创建哪些文件、是否访问外部系统、哪里必须停止确认。

### 3. 只生成最小但完整的结构

简单 Skill 不会为了显得专业而生成一堆空目录；复杂、生产或商业 Skill 才逐步增加脚本、契约、回归用例、Spec、Plan、ADR 和发布证据。

### 4. 把真实失败变成长期保护

出现问题时，先判断根因属于 trigger、interface、state、script、structure 还是 test，再在独立候选中修改。修复不仅解决这一次失败，还增加能够防止问题复发的回归依据。

### 5. 让每次修改都可验证、可恢复

正式修改先预览，Apply 使用同一份未漂移计划；写后执行检查，失败时恢复。结构健康、行为证据和真实任务效用分别报告，不用一个分数包装全部效果。

## 四个真实 Use Case

Skill Engineering 1.0 使用四个从轻到重的案例验证创建、外部边界、确定性执行和复杂架构治理。

| Use Case | 用户想完成什么 | 重点验证什么 |
|---|---|---|
| 会议纪要行动项 | 提取决策、负责人和截止时间 | 轻量 Skill 如何做好触发边界、证据与长期维护 |
| GitHub Issue 实施计划 | 分类、去重并生成计划 | 连接外部系统时如何守住只读与审批边界 |
| 本地 Web 应用验收 | 登录、搜索、导出并保存证据 | Skill 如何与确定性脚本分工完成真实验证 |
| 多文件研究证据包 | 组织问题、资料、证据和结论 | 复杂 Skill 如何处理结构、失败回滚和重新规划 |

### Use Case 1：会议纪要不是“再写一个摘要 Prompt”

用户只提出一个普通目标：

```text
我每周都要把会议记录整理成决策、负责人和截止时间。
请帮我做一个 Skill。
```

Skill Engineering 没有立即写文件，而是先确认：普通会议摘要是否应该触发、原文缺少负责人或日期时怎么办、结果保存在哪里、第一版是否需要连接外部任务系统。

最终方案把边界写得很清楚：

- 只提取有原文依据的决策和行动项；
- 缺少负责人或日期时标记“待确认”，不自行补写；
- 普通观点摘要、润色和情绪分析不触发；
- 第一版只处理 Markdown，不自动修改飞书或任务系统；
- 用户确认方案以前，不创建任何目标文件。

创建后得到的是与风险匹配的最小结构，而不是一套空模板。后来出现“把原文没说过的内容写进结果”的真实问题时，系统也没有只追加一句“严禁编造”，而是把处理流程改成逐字段证据检查，并补上防止模糊意向、相邻句错误拼接的回归场景。

这个案例证明了 1.0 最基本的价值：**结果更可预期，修改更容易审阅，旧能力不容易被新补丁破坏。**

### Use Case 2：GitHub Issue 只读分析

用户希望分类 Issue、识别重复项并生成实施计划。第一版可以分析和提出建议，但不能改标签、评论或关闭 Issue；任何写回 GitHub 的动作都必须离开已批准的只读边界并重新确认。

### Use Case 3：本地 Web 应用自动验收

用户只描述“登录后台、搜索项目、导出 CSV，并留下截图和报告”。Skill 负责自然语言触发、安全边界和失败说明，浏览器脚本负责确定性操作与断言，最终保存截图、CSV、JSON 和 Markdown 证据。

### Use Case 4：多文件研究证据包

复杂研究任务把入口、契约、输出规范、样例和回归用例分层管理。第一次方案触及高风险外部发布时，系统停止并清理；收窄为本地研究整理后重新规划，证明复杂度、停止条件与恢复路径能够随风险升级。

四个案例均在同一个 `1.0.0` 发布候选上重新执行 Preview、Apply、失败恢复、结构检查和发布门禁。完整证据见[四个 Use Case 发布验证](docs/testing/2026-07-18-v1-use-cases.md)。这些证据证明受保护行为没有退化，不代表已经覆盖所有模型、仓库和生产环境。

## 适合谁

| 用户 | 典型需求 | 得到的价值 |
|---|---|---|
| Codex / Claude Code 用户 | 把日常工作方法变成可反复调用的 Skill | 不需要先学习 Skill 工程规范，只需要描述目标 |
| 个人创作者与一人团队 | 沉淀自己的判断标准和工作流 | 从一次经验变成边界清楚的长期能力 |
| Skill 开发者与团队 | 修复误触发、规则堆积和架构漂移 | 独立候选、回归证据、维护记录与恢复路径 |
| 商业与工业场景 | 需要稳定接口、安全审计和发布门禁 | 按风险增加契约、版本、审批和独立证据 |

## 版本路线

### 1.0：把一个 Skill 做稳

`1.0.0` 已正式发布，冻结创建、Doctor、评测结果比较、隔离维护、演进、发布证据和回滚组成的本地生命周期契约。

### 2.0：守护整套 Skill 架构

Architecture Guardian 正在开发。它使用 Blueprint/IR 描述组件职责、执行拓扑和治理等级，后续检查依赖、职责重复、触发冲突、上下文成本和架构变化。所有结果先只读预览，不自动修改正式 Skill。

### 3.0 前瞻：从真实使用中持续进化

3.0 是长期方向，尚未形成正式发布承诺。目标是从脱敏的真实运行中发现反复问题，生成隔离候选，使用 development/holdout、high-risk 和 negative-transfer 证据验证，再在受控范围内逐步发布或撤回。

> 1.0 管好一个 Skill，2.0 守护整套 Skill 架构，3.0 让 Skill 从真实使用中持续进化。

准确状态见 [Roadmap](docs/ROADMAP.md)、[VERSIONING](docs/VERSIONING.md)、[FEATURE-MATRIX](docs/FEATURE-MATRIX.md) 和[当前 2.0 Sprint](docs/sprints/2026-07-v2.0-architecture-guardian.md)。

## 发布证据

`1.0.0` 正式发布候选完成了四个真实用户旅程回归，以及当时的 133 项 pytest、Ruff、Agent Skill validation、credential lint、diff check、wheel 构建、干净环境安装和远程安装验证。

production Doctor 曾达到 `100/A`，它只代表结构准备度，不代表所有真实任务中的业务效果。

- [GitHub Release v1.0.0](https://github.com/wukongai/skill-engineering/releases/tag/v1.0.0)
- [四个 Use Case](docs/testing/2026-07-18-v1-use-cases.md)
- [远程标准安装验证](docs/testing/2026-07-16-standard-skill-install.md)
- [1.x 公开契约](docs/references/v1-public-contract.md)

## 当前边界

- 核心逻辑 provider-neutral，不内置 LLM API；
- 静态 Doctor 只证明结构、安全和可维护性准备度，不冒充真实任务效果；
- 候选生成不会看到 holdout assertions 或 baseline scores；
- evaluation suite 不执行任意命令或第三方脚本；
- Global 和多项目分发属于 Agent Skill Hub，本项目不自动 Global 发布；
- 当前不承诺云端协作、RBAC、托管评测、SLA 或原生客户端权限强制执行。

### 关于 Python 内核与 CLI

Agent Skill 是产品入口，普通用户不需要把 CLI 当成第二套产品学习。仓库仍保留 Python 确定性内核和 1.x CLI 兼容接口，用于不可变计划、Doctor、评测、维护记录、CI 和恢复。

标准 `skills` 安装只安装 Agent Skill，不会同时安装 Python runtime。当前 1.0 的部分深度检查或维护动作需要该内核；缺少时，Skill 会明确报告依赖，而不会伪装成已经成功。维护者和 CI 如需固定稳定 runtime，可使用：

```bash
uv tool install "git+https://github.com/wukongai/skill-engineering.git@v1.0.0"
```

这是当前实现边界与兼容入口，不是普通用户开始使用 Skill Engineering 的前置知识。

## 本地开发

普通用户不需要克隆仓库。只有源码学习、二次开发、开发测试和贡献 PR 时才需要：

```bash
git clone https://github.com/wukongai/skill-engineering.git
cd skill-engineering
python3 -m pip install -e ".[dev]"
```

```text
skills/skill-engineering/   对话式 Agent Skill 入口
src/skill_engineering/      确定性工程与兼容核心
tests/                      行为、安全与版本回归
docs/                       产品、规范、计划和发布证据
```

从[文档索引](docs/README.md)了解完整工程体系。本项目使用自己的生命周期规则管理自己。

### 完整验证

```bash
python3 -m pytest -q
python3 -m ruff check src tests
python3 /path/to/skill-creator/scripts/quick_validate.py skills/skill-engineering
bash scripts/credential-lint.sh --all
git diff --check
```

## 许可证、贡献与安全

原创代码、Agent Skill 指令、references、schemas、tests、examples 和文档默认采用 Apache License 2.0。允许商业使用和再分发；第三方材料保留原许可证，用户 Prompt、私有数据、生成的 Skill 和运行产物不由本项目主张。

- [Apache License 2.0](LICENSE)
- [NOTICE](NOTICE)
- [版权与安装指南](docs/guides/licensing-and-installation.md)
- [贡献指南](CONTRIBUTING.md)
- [安全政策](SECURITY.md)

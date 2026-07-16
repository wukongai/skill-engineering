# Skill Engineering 真实用户实操回归报告（2026-07-16）

## 结论先说

这次不是 `skill-user-journey.html` 那种 use case 演示，而是一次真实执行：从 GitHub 远程分支安装 `skill-engineering` 到全局、在一个没有项目文件的独立 Codex 任务中提出创建需求、逐轮回答引导问题、确认后实际写入 Skill、再提出行为缺陷并按候选—审阅—应用流程修改。

真实任务线程：`019f6876-b30a-7250-97d1-f80ae9401f91`。

## 测试环境与安装

- 测试安装源：`https://github.com/wukongai/skill-engineering.git#codex/version-roadmap`
- 安装方式：`npx --yes skills add ... --skill skill-engineering -g -a codex -y --copy`
- 安装目标：`~/.agents/skills/skill-engineering`
- 原有 `~/.codex/skills/skill-engineering` 链接在测试前备份，测试结束后已恢复。
- 临时安装副本保留在：`/private/tmp/skill-engineering-real-e2e-backup-20260716/installed-global-copy/skill-engineering`

这验证了用户不需要克隆仓库即可安装和使用；克隆仍只适合需要研究或修改源码的用户。

## 用户实际操作记录

### 第 1 步：提出创建需求，要求先判断，不得提前写入

用户输入：

> 我每周都要把会议记录整理成决策、负责人和截止时间。请使用 skill-engineering 帮我创建一个 Skill。先判断这件事是否真的应该做成 Skill；一次只问一个会改变结果的问题；没有得到我的确认前不要写入文件。

实际结果：Skill 先做只读判断，确认任务重复且需要从自然语言中抽取结构化信息；然后询问会议记录的输入位置、格式和输出位置。该轮耗时约 **166 秒**，这是本次最严重的首次响应卡顿。

### 第 2 步：说明输入、输出和外部服务边界

用户输入：

> 输入通常是当前项目里的 Markdown 会议记录。我希望输出仍然是 Markdown，保存在当前项目的 meeting-actions/ 目录里。第一版只做个人使用，不连接飞书、任务系统或其他外部服务。

实际结果：它继续只读比较“项目规则”与“独立 Skill”，并逐一确认是否需要跨项目复用；耗时约 **19 秒**。

### 第 3 步：确认跨项目复用

用户输入：

> 以后会在多个不同项目中复用，所以我希望它是一个可以安装和调用的独立 Skill。

实际结果：确定创建轻量 atomic Skill，建议名称为 `extract-meeting-actions`，并继续询问反触发边界；耗时约 **41 秒**。

### 第 4 步：给出不应触发的相似请求

用户输入：

> 如果用户只是说“总结这份会议记录的主要观点”，但没有要求提取决策、负责人或截止时间，就不要调用这个 Skill。

实际结果：把普通摘要、主要观点总结和润色列为反触发；继续询问缺少负责人或截止时间时的处理方式。该轮耗时约 **121 秒**，再次显示长等待问题。

### 第 5 步：建立“不猜测”安全边界

用户输入：

> 不要猜测或补写。原文没有明确负责人或截止时间时，分别标记为“待确认”，并保留对应的原文依据；如果连行动项本身都不明确，就不要把它写成确定结论。

实际结果：提出固定四段输出结构：来源信息、已确认决策、明确行动项、待澄清事项；耗时约 **20 秒**。

### 第 6 步：查看计划并确认写入

用户输入：

> 符合。请把来源信息、已确认决策、明确行动项、待澄清事项作为固定四部分；每条记录保留原文依据。请展示最终计划和将创建的文件结构，等我确认后再写入。

实际结果：展示计划和结构 `outputs/extract-meeting-actions/{SKILL.md,agents/openai.yaml}`，明确“确认前不写入”；耗时约 **45 秒**。

### 第 7 步：确认实际创建

用户输入：

> 方案确认。请按刚才展示的计划写入当前测试项目的 outputs/extract-meeting-actions/；只创建这个 Skill，不修改其他文件。写入前后请说明实际创建了哪些文件，并运行你能运行的结构校验。

实际结果：

1. 官方初始化脚本先创建模板；
2. UI 简述长度校验失败，初始化提前停止；
3. Skill 修正简述后补齐 `agents/openai.yaml`；
4. 用最终工作流替换模板；
5. 官方 `quick_validate.py` 通过，输出 `Skill is valid!`。

该轮耗时约 **158 秒**。这次失败被如实暴露并恢复，没有静默吞掉。

### 第 8 步：模拟真实使用后的行为缺陷

用户输入：

> 我试用后发现一个问题：它有时会把会议原文没有说过的内容写进结果。请修改刚才创建的 `outputs/extract-meeting-actions/`，但不要在文件末尾继续堆补丁；先分析问题属于触发边界、处理规则、输出格式还是验证层，展示修改方案和将影响的文件，确认前不要覆盖现有文件。

实际结果：它判断主根因是“处理规则”，验证层是次要缺口；明确不是触发边界和输出格式。它先创建独立候选目录，不触碰现有 Skill；耗时约 **96 秒**。

### 第 9 步：候选审阅后应用

候选内容包括：

- `SKILL.md` 重构为“证据账本 → 候选记录 → 逐字段证据门槛 → 写入前证据审计”；
- 新增 `tests/regression-no-unsupported-content.md`，覆盖模糊意向、明确字段和邻近句子误拼接三类回归场景；
- 保持 `agents/openai.yaml` 不变。

用户确认：

> 我审阅了候选 diff，方案没有问题。请将候选应用到 `outputs/extract-meeting-actions/`，保留现有 `agents/openai.yaml` 不变；然后运行 quick_validate.py，并列出最终文件结构和变更摘要。

实际结果：候选应用成功，目标目录重新校验通过；该轮耗时约 **153 秒**。

## 最终真实文件树

```text
outputs/extract-meeting-actions/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── tests/
    └── regression-no-unsupported-content.md
```

- [最终 SKILL.md](/Users/aim5/Documents/Codex/2026-07-15/skill-engineering-real-user-e2e-20260716/outputs/extract-meeting-actions/SKILL.md)
- [最终 agents/openai.yaml](/Users/aim5/Documents/Codex/2026-07-15/skill-engineering-real-user-e2e-20260716/outputs/extract-meeting-actions/agents/openai.yaml)
- [回归 fixture](/Users/aim5/Documents/Codex/2026-07-15/skill-engineering-real-user-e2e-20260716/outputs/extract-meeting-actions/tests/regression-no-unsupported-content.md)

## 用户体验判断

### 已验证

- 安装路径是面向直接使用者的远程安装，而不是要求先克隆源码。
- 没有用户确认时不写入文件。
- 每次只问一个会改变方案的问题。
- 创建前展示计划和目录结构。
- 初始化失败会被明确报告并修正。
- 修改不是在原文件末尾堆补丁，而是先定位层级，再进入独立候选，审阅后应用。
- 最终结构校验通过，且全局测试安装已清理并恢复原链接。

### 卡壳与问题

- 首次响应约 166 秒，明显不可接受。
- 后续多个只读阶段达到 96–158 秒，用户会误以为任务卡死。
- 初始化脚本的简述长度限制直到执行时才暴露，应该在预览阶段提前校验。
- 当前回归 fixture 是人工可审阅契约，不是自动化模型行为评分；报告不能把它宣称成完整行为测试。

## 截图与录制说明

本次保留了真实线程原文、工具状态、文件变更和校验输出作为可审计记录。尝试从 Codex 窗口抓取截图时，系统安全策略拒绝 Computer Use 读取 Codex 自身应用，因此没有把旧的 HTML use case 截图冒充真实截图。下一次若需要屏幕录制，应由用户在本机开启系统录屏，或由产品提供线程截图导出能力。

## 判定

这次确实完成了“远程安装 → 用户提问 → 需求澄清 → 用户确认 → 实际创建 → 用户反馈 → 候选修改 → 审阅应用 → 校验”的真实用户实操。它不是 use case 模拟；但性能等待和截图能力仍是发布前需要单独解决的体验问题。

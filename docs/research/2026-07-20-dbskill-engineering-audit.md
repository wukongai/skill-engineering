# dbskill v2.18.0 工程审计与演进建议

> 第三方独立工程审计，面向 dbskill 作者与希望长期使用、维护 Agent Skill 的用户。
> 审计对象：[dontbesilent2025/dbskill](https://github.com/dontbesilent2025/dbskill/tree/daca0716446c255ba19ede90950450ddd2908595)，提交 `daca071`，版本 `v2.18.0`，审计日期 2026-07-20。

## 摘要

dbskill 已经不是一组零散 Prompt，而是一个有明确品牌、方法论和用户任务地图的 Skill 产品：28 个业务 Skill 加 1 个更新入口，覆盖商业诊断、内容生产、知识管理、决策记录和 Agent 工作台治理。它最难得的价值不是“Skill 数量多”，而是把作者长期公开内容整理成可调用的方法集合，并通过 `/dbs` 尝试提供统一入口。

当前主要问题也来自这个规模：产品已经进入“多组件系统”阶段，工程结构仍大量停留在“单文件长 Prompt”阶段。29 个 Skill 的 team Doctor 平均结构健康分为 52.3；27 个存在至少一个硬门禁，2 个仅为 WARN，没有 clean 项。这里的分数只代表结构 readiness，不代表方法论质量或真实业务效果。

建议优先处理三件事：

1. 统一安装模型，明确 plugin 与 `skills add` 二选一，提供迁移和残留清理说明；
2. 把 `/dbs` 收敛成薄路由器，把知识、案例、模板和导航图下沉到 references；
3. 为高价值、会写盘或会调用 Agent 的 Skill 增加 contract、success/failure/high-risk cases 和真实行为证据。

如果这三项完成，dbskill 会从“内容很强、入口很多的个人工具箱”跃迁成“可安全安装、可验证、可持续维护的 Skill 产品”。

## 审计范围与限制

本次审计包括：

- 29 个发布 Skill 的 frontmatter、根入口、辅助文件与脚本；
- `.claude-plugin/marketplace.json` 当前结构及 2026-06-29 的 v2.15.1 历史结构；
- README 的 plugin 与 `skills add` 安装说明；
- team profile 静态 Doctor；`/dbs` 另做 production profile 复核；
- 安全规则命中的人工复核；
- Claudian 2.0.1 中与 Skill 发现、插件加载和 persistent query 相关的宿主代码及公开 issues。

本次没有运行 baseline/holdout，也没有真实执行 29 个 Skill 的下游任务。因此：

- 结构分不能当作业务价值分；
- 没有证据证明哪种方法论更有效；
- 没有动态复现某一次 Claudian 卡死的唯一因果链；
- 对输出质量、作者语气还原度和跨模型稳定性的判断仍需真实用例。

## 许可证与公开传播边界

仓库采用 [CC BY-NC 4.0](https://github.com/dontbesilent2025/dbskill/blob/daca0716446c255ba19ede90950450ddd2908595/LICENSE)：

- 可以个人使用、学习、研究、分享和非商业改作；
- 公开衍生作品必须合理署名、链接许可证，并注明做过修改；
- 商业用途需要作者单独授权；
- 不应把第三方改作包装成官方版本或官方合作。

因此，公开发布本审计报告、写非商业学习文章或制作个人非商业 fork，原则上可在遵守署名和修改声明的前提下进行。若报告用于付费课程、咨询获客、会员内容或商业产品，应先向作者取得明确授权。

## 系统级发现

### 1. 产品架构已经复杂，入口仍过厚

- 29 个根 `SKILL.md` 合计 8,549 行；
- 22 个根入口超过 200 行；
- `/dbs-xhs-title` 739 行，公式库和执行入口混在一起；
- `/dbs-content-system` 556 行，但它也是少数已经出现 tools、templates、scaffold 分层的 Skill；
- `/dbs-diagnosis` 511 行，方法论、分类器、流程、模板、信号追踪和案例全部堆在入口。

Agent 首先需要的是“何时触发、读什么、做什么、何时停止”。大段方法论、案例和公式适合按需加载，不适合持续占据根入口。

### 2. 中央路由职责泄漏到所有 Skill

27 个 Skill 被静态推断为 router。主要原因不是它们真的都是路由器，而是几乎每个入口都带有“下一步调用哪个 Skill”或“回到 `/dbs`”的章节。

建议：

- `/dbs` 独占跨 Skill 路由；
- 原子 Skill 只返回结构化结果和少量 `next_signals`；
- 是否继续路由由 `/dbs` 根据结果重新判断；
- 不在每个 Skill 中复制导航地图和路由话术。

### 3. 安装文档存在双通道歧义

README 同时提供：

```bash
npx -y skills add dontbesilent2025/dbskill -g --all
```

以及：

```bash
claude plugin marketplace add dontbesilent2025/dbskill
claude plugin install dbs@dontbesilent-skills
```

但没有明确说明两者应当二选一，也没有说明如何从一种方式迁移到另一种方式。

2026-06-29 的 v2.15.1 marketplace 有 24 个独立插件条目，每个条目只暴露自己声明的一个 Skill；当前 v2.18.0 有 29 个条目。`source: "./"` 本身不会令每个插件暴露全部 Skill，因为每个条目的 `skills` 指向具体子目录。

真正的风险是：用户先安装 `dbs`，发现子能力不完整，再逐个补装插件，之后又运行 `--all`。这会让同名能力从 plugin 和全局 Skill 目录同时存在，增加发现成本、版本漂移和排障难度。

建议提供三个清晰套餐：

- `dbs-core`：`/dbs` 加一小组只读核心 Skill；
- `dbs-content`：内容生产相关组合；
- `dbs-full`：全部 Skill，明确只建议高级用户使用。

每个套餐应有唯一安装通道、可见 Skill 清单、升级方式和完整卸载方式。

### 4. 行为证据缺失

29 个 Skill 均未提供统一的 `skill.contract.yaml`；17 个复杂 Skill被 Doctor 标记为缺少 evaluation evidence contract。没有统一的 success、failure、high-risk case portfolio，也没有 baseline/holdout/negative-transfer 结果。

建议先从 6 个高频 Skill 建立最小行为集：

- `/dbs-diagnosis`
- `/dbs-content`
- `/dbs-hook`
- `/dbs-ai-check`
- `/dbs-goal`
- `/dbs-knowledge`

每个至少固定：正常输入、信息不足、反触发、危险写盘、模型拒绝服从规则五类用例。

### 5. 静态安全未发现恶意外联

Doctor 曾对 4 个 Skill 报 `SEC103`、对 skill-cleaner 报 `SEC101`。人工复核后均为关键词误报：

- “不要强行重写”“默认不要展示完整评分表”等是正常输出约束；
- skill-cleaner 中的 `curl`、`wget`、`http` 是扫描器要识别的风险关键词；
- `skill_cleaner.py` 本身没有网络请求、subprocess、shell 或动态执行。

当前未发现 dbskill 在后台注册接口、持续 watcher、SessionStart hook、MCP server 或自动外联机制。

## 29 个 Skill 逐项分析

评分为 team Doctor 的结构 readiness。`C/D/F` 不代表方法论无效，只表示安装、共享和维护前仍有工程债。

| Skill | 分数 | 主要价值 | 核心工程问题 | 使用与个人化建议 |
|---|---:|---|---|---|
| `dbs` | 50/F | 统一教程、任务前路由和任务后导航，产品心智最完整 | 359 行；路由表、导航地图、教程和话术耦合；无 contract/eval；宽触发“帮我看看” | 暂不作为自动入口全局安装。保留产品地图，重写成薄 router；个人版只路由已实际安装的 Skill。 |
| `dbs-action` | 67/D | 用阿德勒框架识别拖延、逃避和课题混淆 | 250 行；哲学、公理、信号表、案例和输出模板同层 | 可显式调用试用。个人版应弱化绝对断言，增加心理健康边界和“非心理原因”反例。 |
| `dbs-agent-migration` | 42/F | 多宿主规则真源、bridge 和工作台迁移意识较强 | 394 行；触发过宽；涉及删除、移动、写全局目录；无确定性实现和回滚契约 | 不直接安装执行。可借鉴真源/桥接思想；个人版应改为 inventory → immutable plan → apply → verify。 |
| `dbs-ai-check` | 67/D | 将“AI 味”拆成可观察写作信号，默认先诊断 | 274 行；改写偏好、体裁规则和误伤规则混在入口；缺真实误报率 | 适合显式调用。个人版要用自己的文章建立正反例，避免把作者审美当通用标准。 |
| `dbs-benchmark` | 61/D | 对标筛选和模仿颗粒度框架可操作 | “高利润是唯一标准”等绝对原则适用面有限；231 行；无外部事实验证流程 | 可用于商业研究草案，不能替代市场数据。个人版增加数据来源、时效和不适用行业。 |
| `dbs-bridge` | 35/F | 用软链维持多端单一真源，方向正确 | 会改 `~/.claude`、`~/.codex`、`~/.agents`、`~/.grok`；硬编码示例路径；无不可变计划和变更记录 | 暂不直接使用。个人版应由专门安装治理工具接管，并默认 project scope。 |
| `dbs-chatroom` | 65/D | 按理论和代表人物组织多角色讨论，而非随意角色扮演 | 依赖 Agent tool 和多轮状态；未编码 partial failure、退出和上下文压缩测试 | 在普通 Claude/Codex 中可小规模试用；在旧 Claudian 中暂缓。个人版限制角色数与最大轮次。 |
| `dbs-chatroom-austrian` | 78/C | 边界较窄，哈耶克/米塞斯角色分工清楚 | 仍依赖并行 Agent；理论人物输出可能被模型虚构；无引用与纠错机制 | 是最接近可试用的对话 Skill。个人版增加来源引用和“人物观点是模拟而非本人发言”声明。 |
| `dbs-content` | 63/D | 内容形式和五维诊断形成可复用检查框架 | 232 行；“精神控制”等价值判断过强；与 resonate/spread/script-flow/hook 边界交叠 | 可显式调用。个人版把它定位为总诊断，只输出转交信号，不直接承担所有专项修改。 |
| `dbs-content-system` | 32/F | 项目结构、模板、scaffold 和确定性 tools 最丰富，已接近真正工程产品 | 556 行；会建工程、复制素材和批量写盘；审批边界未形成机器契约；工具缺统一 dry-run/apply 入口 | 不直接在真实资料库运行。值得作为独立产品重构；先在素材副本上做 sample mode。 |
| `dbs-decision` | 44/F | 把长期决策、状态、结果回填和规律提炼落到本地文件 | 默认持续覆盖状态文件、创建多目录并可能写隐私信息；无迁移和 schema | 只在专用私人目录试用。个人版先定义数据 schema、隐私等级、备份与撤销。 |
| `dbs-deconstruct` | 35/F | 将概念的不同用法、边界和商业含义拆开 | 220 行；被副作用关键词误判；维特根斯坦与奥派框架被写成固定答案 | 可作为思考模板显式调用。个人版把理论框架作为多个 lens，而非唯一正确解释。 |
| `dbs-diagnosis` | 54/F | 商业问题分类、假设挑战和体检模式是核心品牌能力 | 511 行；大量未经行为验证的百分比；绝对公理可能导致过度归因心理问题 | 值得重点试用和研究，但结果只作假设。个人版移除伪精确比例，加入事实核验和行业反例。 |
| `dbs-goal` | 40/F | 把模糊愿望改写成可检查交付物 | 288 行；哲学、流程、案例和模板混杂；静态安全命中为误报 | 可显式调用。个人版加入资源、时间、依赖和“目标本身不值得做”的停止点。 |
| `dbs-good-question` | 12/F | 问题说明书、Agent 可解性和候选解释框架很有潜力 | 466 行、5 套输出格式；职责跨度从澄清到自动化评估；写盘边界不清 | 暂不整包使用。建议拆成“问题澄清”“Agent 可解性”“解释批评”三个 Skill。 |
| `dbs-hook` | 37/F | 短视频开头诊断到方案生成，任务清晰 | 305 行；可能直接生成大量方案；与 content/resonate/script-flow 重叠；缺用户确认边界 | 可显式调用试用。个人版只做开头专项，并用你的真实完播数据建立回归。 |
| `dbs-knowledge` | 24/F | 对文件夹知识库、SOT、版本冲突和导航瘦身的理解完整 | 487 行；触发描述极宽；会改导航、入口和文件；多个工作模式揉在一起 | 不直接在主 OB 库运行。个人版拆为 query、ingest、health-check、govern 四个 Skill。 |
| `dbs-learning` | 54/F | 通过用户反馈连续生成学习文章，并维护计划和索引 | 372 行；长期状态和写盘逻辑仅靠 prose；容易无限生成低质量课程 | 可在独立学习目录试用。个人版增加学习目标、测验、停止标准和内容来源。 |
| `dbs-report` | 65/D | 把多次诊断存档合并为可交付 Markdown | 234 行；依赖 save 的非结构化状态；报告 schema 与失败处理缺失 | 必须与 save/restore 同版本使用。个人版先固定 session schema，再做 renderer。 |
| `dbs-resonate` | 76/C | 文稿核心主张和五维共鸣诊断，边界相对清楚 | 171 行；理论有效性和修改收益未验证；与 content/spread 有交集 | 适合首批显式试用。个人版用历史高低表现文稿做 baseline/holdout。 |
| `dbs-restore` | 46/F | 从本地诊断快照恢复上下文 | 存档选择、schema 兼容、缺失/损坏文件处理不足；有写盘/状态风险 | 暂缓。个人版需要版本化 schema、只读 preview 和损坏恢复测试。 |
| `dbs-save` | 65/D | 把聊天结论结构化落盘，支持跨会话连续性 | 235 行；路径、slug、状态和覆盖策略仅靠提示；无原子写入和隐私 contract | 可在临时目录验证，暂不存真实敏感咨询。个人版实现确定性脚本和 redaction。 |
| `dbs-script-flow` | 54/F | 逐字稿段落衔接、密度和口播流畅度检查较具体 | 293 行；案例和版本历史占入口；改稿模式与诊断模式耦合 | 适合显式诊断。个人版将改稿做成二阶段确认，并下沉案例。 |
| `dbs-skill-cleaner` | 30/F | 有只读扫描、隔离而非删除、恢复等安全意识 | 自研正则容易误报；脚本既扫描又隔离；Doctor 的 SEC 命中本身是误报 | 不作为安全裁决器直接使用。可借鉴隔离机制；个人版分 scanner/quarantine，并加 fixture。 |
| `dbs-slowisfast` | 63/D | 用摩擦、复利资产和短长期权衡挑战“求快” | 232 行；价值判断强，容易对所有问题推荐“慢”；缺成本模型 | 可作为决策 lens。个人版加入“哪些事必须快”和机会成本反例。 |
| `dbs-spread` | 67/D | 用五个传播理论解释共鸣机制，输出讨论方向 | 159 行；理论来源未显式引用；与 resonate/content/chatroom 交叠 | 可显式调用。个人版要求区分文本证据、理论推断和待验证受众假设。 |
| `dbs-update` | 75/C | 更新范围小，避免更新其他 Skill | 直接更新、没有独立 preview/rollback；更新后依赖新会话；与安装通道强耦合 | 不建议先安装。由标准安装器负责版本和回滚更安全。 |
| `dbs-wechat-html` | 50/F | Markdown 到公众号 HTML，风格选择和输出说明清楚 | 只有风格说明，没有确定性转换脚本；输出依赖模型生成大段 HTML；缺视觉回归 | 暂作原型。个人版应改成脚本/模板驱动，并做浏览器截图回归。 |
| `dbs-xhs-title` | 65/D | 75 个标题公式可直接检索和组合，实用性强 | 739 行；公式库完全挤在入口；“验证过”缺数据来源；易产生同质标题 | 可显式调用，但应先拆 reference。个人版保留公式索引，用你自己的点击数据做排序。 |

## 推荐的个人使用组合

不建议第一天就安装全部 29 个。建议先用明确命令调用，不启用宽泛自动路由。

### 第一组：只读内容试用包

- `dbs-ai-check`
- `dbs-content`
- `dbs-hook`
- `dbs-resonate`
- `dbs-script-flow`
- `dbs-xhs-title`

适合验证作者方法是否真的改善你的文章、短视频和公众号生产。每次保存原稿、Skill 建议和最终稿，并补充真实发布数据。

### 第二组：思考工具试用包

- `dbs-diagnosis`
- `dbs-goal`
- `dbs-good-question`
- `dbs-deconstruct`
- `dbs-action`
- `dbs-slowisfast`

这些 Skill 更像观点鲜明的思考 lens。使用时应要求模型把“事实、作者框架下的推断、待验证假设”分开输出。

### 暂缓安装

以下能力会写盘、改宿主配置、依赖多 Agent 或维护长期状态，应先完成隔离验证：

- `dbs`
- `dbs-agent-migration`
- `dbs-bridge`
- `dbs-chatroom`
- `dbs-chatroom-austrian`
- `dbs-content-system`
- `dbs-decision`
- `dbs-knowledge`
- `dbs-learning`
- `dbs-report`
- `dbs-restore`
- `dbs-save`
- `dbs-skill-cleaner`
- `dbs-update`
- `dbs-wechat-html`

## 如何把它真正变成“你的 Skill”

“改个名字、换个语气”不等于形成自己的 Skill。建议保留来源、逐步替换证据：

1. **保留 attribution**：在 fork、报告和每个衍生 Skill 中写清原作者、原仓库、许可证和修改内容；
2. **先选真实任务**：每个 Skill 收集你自己的 success、failure、high-risk 输入；
3. **拆作者观点与通用机制**：把 dontbesilent 的公理标成一个 lens，而不是系统事实；
4. **用你的数据排序**：用真实发布表现、业务结果和复盘更新规则，而不是凭感觉改 Prompt；
5. **建立独立候选**：不要直接改安装副本；每个改造都保留 baseline、candidate 和回滚点；
6. **先 Shadow，再替换**：新版本先只给建议，不自动写盘；通过 holdout 后再成为默认入口；
7. **商业化先授权**：若用于付费内容、咨询、产品或引流变现，先和原作者确认授权范围。

## 给作者的高收益改进顺序

### P0：安装治理

- README 明确 plugin 与 `skills add` 二选一；
- 提供 `status`、完整卸载和双通道迁移说明；
- 用套餐插件替代 29 个并列普通用户入口；
- 明确 `/dbs` 单装时到底能调用哪些子 Skill。

### P1：架构减重

- `/dbs` 缩到 120 行以内；
- 公式、案例、理论和模板下沉到 references；
- 原子 Skill 移除复制的导航地图；
- `dbs-good-question`、`dbs-knowledge` 按职责拆分；
- content-system 保留工具层，并补统一 CLI。

### P2：安全与状态

- 所有写盘 Skill 增加 preview/apply、明确目标、备份、回滚和 postflight；
- save/restore/report/decision 统一 schema 和版本；
- bridge/migration/update 交给确定性脚本和不可变计划；
- 多 Agent Skill 增加 timeout、partial failure 和最大轮次。

### P3：真实评测

- 先选 6 个高频 Skill 做 baseline/holdout；
- 固定作者原版、候选版和无 Skill baseline；
- 记录任务完成、误触发、事实错误、用户修改量和真实业务指标；
- 用独立 reviewer 检查语义质量；
- 静态 Doctor 与真实 utility 分开公布。

## 对 Claudian 卡死问题的独立结论

dbskill 是声明式 Skill 仓库，没有发现自身后台反复注册的代码。历史安装文档的双通道与多个独立插件会扩大暴露面，但不能单独证明无限注册。

本机 Claudian bundle 与官方 2.0.1/2.0.2 完全一致，而当前官方版本已是 2.0.39。Claudian 官方 issue 中存在 Command/Skill 死循环、Skill 菜单加载约 10 秒等同类报告。因此更合理的因果链是：

```text
dbskill 安装入口较多、触发重叠、Skill 数量大
  + 历史多插件或潜在双通道状态
  + Claudian 早期 2.0 宿主的 Skill 发现与 runtime 不稳定
  -> 反复刷新 / query 重启 / 路由负担
  -> 用户体感卡死或像“反复注册”
```

这不是对任何一方的单点归罪，而是 Skill 产品、安装治理和宿主生命周期三层共同作用。

## 结语

dbskill 已经证明了作者能够把个人内容资产组织成可调用产品。下一阶段最值得做的不是继续增加 Skill 数量，而是让现有能力更容易正确安装、更少误触发、更可验证、更可恢复。

如果作者愿意推进工程化，建议先用一个小版本完成安装治理和 `/dbs` 薄化，再选择 6 个高频 Skill 建立真实行为基线。这样既不需要推翻现有内容，也能显著改善使用体验和外部贡献门槛。

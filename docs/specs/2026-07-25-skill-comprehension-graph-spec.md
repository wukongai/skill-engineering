# Skill 可理解性知识图谱（Skill Graph）Spec

状态：Backlog / 未排期 / 需求与调研已完成 / 不得据此直接实施

日期：2026-07-25

对应 Plan：[`2026-07-25-skill-comprehension-graph-plan.md`](../plans/2026-07-25-skill-comprehension-graph-plan.md)

相关事实源：

- [`PRODUCT.md`](../PRODUCT.md)
- [`architecture.md`](../architecture.md)
- [`v2.0 Architecture Guardian Spec`](2026-07-16-v2.0-architecture-guardian-spec.md)
- [`Blueprint schema`](../references/blueprint.schema.json)
- [`BACKLOG.md`](../BACKLOG.md)

## 背景

Skill Engineering 已能创建、体检、评测、维护和发布 Agent Skill，并在 2.0 方向中建立了 Blueprint/IR、只读 inventory、依赖、route collision 和 semantic diff 的架构事实层。

但用户拿到一个复杂 Skill 后，仍难以快速理解：

- 根 `SKILL.md` 会路由到哪些 references、stages、scripts、tools 或其他 Skills；
- 自然语言中的条件、停止点、审批、副作用和回滚如何组成真实执行路径；
- 每个文件和文本片段为什么存在，与上下游是什么关系；
- 哪些关系是明确声明，哪些是检测结果、AI 推断或真实运行证据；
- 修改一个规则会影响哪些流程、测试和安全边界。

普通代码知识图谱主要依赖 AST 中的 import、call、inherit 等确定性关系。Agent Skill 的关键关系大量存在于 Markdown 和自然语言工作流中，因此不能把通用代码图谱直接换皮为 Skill 产品。

## 产品定位

一句话价值：

> 把任意 Agent Skill 转换成一张有证据、会更新、能查询的执行地图，让用户知道它为什么触发、如何运行、依赖什么、会改变什么。

本能力建议作为独立、local-first 的 Skill 可理解性产品，而不是：

- 在根 `SKILL.md` 中继续增加说明；
- 把全部交互 UI 塞进 Skill Engineering CLI；
- 创建一个只会生成 Mermaid 的单一 Agent Skill；
- 复制 CodeGraphy、GitNexus 或其他通用代码图谱的内部实现。

Skill Engineering 继续拥有 Blueprint、Doctor、Guardian、semantic diff、维护和发布事实；Skill Graph 消费这些事实，并提供细粒度图投影、浏览、解释和问答。

## 调研基线

快照日期：2026-07-25。

公开来源：

- [CodeGraphy VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=codegraphy.codegraphy)
- [CodeGraphyV4](https://github.com/joesobo/CodeGraphyV4)
- [GitNexus](https://github.com/nxpatterns/gitnexus)
- [CodeGraph](https://github.com/colbymchenry/codegraph)
- [Understand Anything](https://github.com/Egonex-AI/Understand-Anything)

本轮只核对公开 README、Marketplace 页面、架构与功能说明，没有安装竞品、运行目标仓库 benchmark、调用外部模型或验证性能宣传。因此结论只用于需求和架构取舍，不能证明竞品或本项目的实际效用高低。

## 调研结论

| 项目 | 可学习能力 | 不直接适用的边界 |
|---|---|---|
| CodeGraphy | Core、图缓存、CLI、UI、插件分层；节点/边 Scope；搜索、过滤、依赖、反向依赖和路径查询 | 以代码 AST、符号和 VS Code 为中心；产品公开表面仍在演进 |
| GitNexus | 本地索引、预计算调用链、影响范围、路径、MCP 和 staleness；查询返回结构化关系而不是让模型临时猜图 | 更偏向 AI 编码 Agent 的代码上下文，不理解 Skill 的触发、审批、停止点和治理 |
| CodeGraph | 本地 SQLite、文件变化自动同步、源码+调用路径+影响范围的一次查询 | 核心对象仍是代码符号，不能直接解析自然语言工作流 |
| Understand Anything | 确定性结构与 LLM 语义分层；通俗解释、Guided Tour、Persona、业务流程视图 | 首次语义生成可能成本较高；推断内容不能成为无证据事实 |

采用原则：

1. 索引核心、查询接口、可视化界面和 Agent 接入分层；
2. 结构关系确定性生成，AI 只补充语义解释；
3. 预计算常见关系、路径和影响范围，避免每次让 Agent 自由探索；
4. local-first，图谱和源码默认不离开用户机器；
5. 图不是目的，用户能回答真实问题才是目的。

## 目标用户

### 首要用户

- Skill 作者和维护者；
- 安装或合并 Skill 前的审阅者；
- 维护复杂、多阶段、商业或生产 Skill 的团队。

### 次要用户

- 想判断 Skill 做什么、是否安全的普通使用者；
- 需要给新人讲解 Skill 架构的培训者；
- 需要结构化上下文的 Codex、Claude Code 等 Agent。

MVP 先服务作者与审阅者。普通用户的引导式讲解和 Persona 适配在结构事实稳定后进入。

## 核心用户任务

1. 导入一个本地 Skill，快速看见入口、组件、依赖和主执行路径；
2. 点击任意节点，查看原文、职责、上下游、证据来源和未知项；
3. 查询“从用户请求到最终输出经过什么”；
4. 查询“这个文件/规则依赖什么，又被什么依赖”；
5. 查看副作用、审批、停止点和回滚是否匹配；
6. 比较 baseline/candidate，理解一次修改的架构影响；
7. 将可复核的图谱导出给人或 Agent，而不要求重新扫描全部文件。

## “动态图谱”的定义

本 Spec 将动态拆成三个层次，避免范围混淆：

1. **源码动态**：文件变化后增量刷新节点、边、fingerprint 和 staleness；
2. **问题动态**：根据用户问题生成有界子图、路径或影响范围，而不是始终展示全图；
3. **运行动态**：把真实 SkillRun/trajectory 覆盖到声明图上，区分“设计如此”和“实际如此”。

MVP 只承诺前两项。真实运行图依赖 Observation Boundary 和 Behavior Evaluation Lab，后续单独排期。

## 图谱语义

### 节点类型

- `Skill`
- `File`
- `Section`
- `Rule`
- `Trigger`
- `Input`
- `Output`
- `Stage`
- `Script`
- `ScriptSymbol`
- `Command`
- `Tool`
- `Plugin`
- `Provider`
- `DelegatedSkill`
- `State`
- `SideEffect`
- `Approval`
- `Stop`
- `Rollback`
- `Test`
- `Evidence`
- `Finding`
- `ExternalResource`
- `Unknown`

章节和规则节点用于细粒度证据定位，但默认折叠在文件或阶段节点内，避免全图过载。

### 关系类型

- `CONTAINS`
- `REFERENCES`
- `READS`
- `ROUTES_TO`
- `DELEGATES_TO`
- `INVOKES`
- `REQUIRES`
- `PRODUCES`
- `MUTATES`
- `REQUIRES_APPROVAL`
- `STOPS_AT`
- `ROLLS_BACK_WITH`
- `VERIFIED_BY`
- `TRIGGERS_ON`
- `OVERLAPS_WITH`
- `AFFECTS`
- `OBSERVED_AS`

### 证据等级

每个节点和关系必须带 provenance，至少区分：

1. `declared`：来自 frontmatter、contract、schema 等明确声明；
2. `detected`：来自 Markdown 链接、文件引用、CLI 调用、代码 import 等确定性检测；
3. `inferred`：由 AI 从自然语言推断，必须带置信度和原文证据；
4. `observed`：由真实运行轨迹确认，必须带脱敏 artifact pointer。

`inferred` 不得覆盖 `declared` 或 `detected`；冲突时并列展示并形成 finding。缺少证据时使用 `unknown`，不得补写成事实。

## 功能需求

### FR-001：安全导入

- 支持导入本地 Skill 目录；
- 识别 `SKILL.md`、frontmatter、contract、references、stages/workflows、scripts、assets 和 tests；
- 索引期间不执行目标 Skill、脚本、hook、program grader 或安装命令；
- Git URL、ZIP 和多仓库输入不进入 MVP。

### FR-002：确定性 inventory

- 复用 Skill Engineering Blueprint/IR 和 inventory；
- 提取文件、章节、结构化字段、显式路径、命令、依赖和证据位置；
- 对缺失、断链和无法确定的关系报告 `unknown` 或 finding；
- 同一输入生成稳定 fingerprint。

### FR-003：分层视图

至少提供：

- 结构视图：文件、组件、职责和依赖；
- 执行视图：trigger、stage、delegate、tool、output；
- 安全与审批视图：state、side effect、approval、stop、rollback；
- 测试与证据视图：test、Doctor/Guardian finding、behavior evidence。

### FR-004：节点详情

点击节点能够看到：

- 原始文件、行号或稳定 anchor；
- 原文片段；
- 职责和通俗解释；
- 上游、下游和所属执行路径；
- evidence kind、confidence、fingerprint、staleness；
- 相关 finding、test 和 unknown。

### FR-005：关系查询

支持：

- 节点搜索；
- dependencies / dependents；
- 两节点之间的有界路径；
- 从 trigger 到 output 的主流程；
- 一个节点的影响范围；
- 按节点类型、关系类型、证据等级和文件范围过滤。

### FR-006：增量刷新

- 识别文件新增、修改和删除；
- 只重建受影响节点、边和解释缓存；
- 显示 fresh、stale、partial、failed 状态；
- 索引失败不能把旧图伪装成最新图。

### FR-007：解释层

- AI 解释是可选能力，关闭后结构图和查询仍完整可用；
- 解释基于结构事实和原文，不允许无来源自由扩展；
- AI 输出标为 `inferred`，显示 provider/model、生成时间和对应 fingerprint；
- 未获授权不得把 Skill 原文发送给外部 provider；
- 解释不得自动写回正式 Skill。

### FR-008：语义 Diff

- 消费 Architecture Guardian 的 baseline/candidate semantic diff；
- 区分文本变化、节点变化、关系变化、执行路径变化和治理变化；
- 显示新增、删除、修改及其影响范围；
- 不在 Skill Graph 中建立第二套维护或 Apply 引擎。

### FR-009：导出与 Agent 接口

MVP 支持稳定 JSON、Markdown 和 Mermaid 导出。CLI/MCP 在核心查询契约稳定后评估，Agent 接口应复用相同查询 API，不拥有第二个 indexer。

## 非功能需求

### 隐私与安全

- 默认 local-first、只读；
- 默认排除 `.env*`、凭证、私钥、token、cookie、生成缓存和用户配置中的敏感值；
- 图谱不得保存原始私有会话；
- 外部 provider、网络访问和远程分享必须显式开启；
- 索引器对软链接、路径逃逸、超大文件和二进制文件设置边界。

### 可复现性

- 结构图同输入同版本产生相同 canonical JSON 和 fingerprint；
- schema、extractor、source 和 graph 分别版本化；
- AI 解释不能参与结构 fingerprint；
- unknown 和解析限制进入输出，不静默丢失。

### 可用性

- 默认折叠章节、规则和大规模叶子节点；
- 支持键盘搜索、缩放、聚焦、返回上下文和可访问颜色；
- 所有颜色编码同时使用标签或线型，不能只依赖颜色；
- 空图、部分图和失败图提供明确下一步。

### 候选性能目标

正式排期时通过基准校准以下目标：

- 常见单 Skill 的确定性索引在普通开发机上数秒内完成；
- 单文件变更只触发有界增量更新；
- 缓存图首次可交互时间不依赖 LLM；
- 默认视图不一次渲染所有段落节点。

当前不承诺未经 benchmark 验证的具体毫秒或节点规模。

## 与 Skill Engineering 的边界

| 能力 | Skill Engineering | Skill Graph |
|---|---|---|
| Blueprint/IR、inventory | 事实源 owner | 消费并投影 |
| Doctor/Guardian finding | 生成和验证 | 展示、关联、查询 |
| behavior evidence | 生成/校验/发布门禁 | 后续可视化 |
| create/improve/apply/undo | 唯一 owner | 不实现 |
| 细粒度文本和关系图 | 提供必要 evidence anchor | owner |
| Local Web 图谱和 Guided Tour | 非当前核心 | owner |
| Agent 图查询 | 可通过接口消费 | 后续 owner |
| 多项目分发 | Agent Skill Hub | 不实现 |

详细图谱应作为 Blueprint 的派生只读模型，例如 `Skill Graph Projection`。是否扩展 Blueprint schema、创建独立 schema 或独立仓库，必须在正式排期时通过 ADR 决定。

## MVP 验收标准

1. 给定当前 `skills/skill-engineering/`，能生成稳定、无凭证、可校验的图谱；
2. 能识别根入口、contract、references、stages、scripts、tests 和显式依赖；
3. 任意已声明或已检测的关系都能回到源文件和证据位置；
4. 能展示至少一条从 trigger 到 output 的有界路径，并保留 unknown；
5. 能独立展示 side effect、approval、stop 和 rollback；
6. AI 关闭时仍可浏览、搜索、过滤、查路径和导出；
7. 修改一个被引用文件后，图谱显示 stale 并只刷新受影响部分；
8. baseline/candidate 能显示节点、关系和执行路径变化；
9. 索引过程不执行目标脚本、不读取凭证、不自动修改 Skill；
10. negative/high-risk fixtures 证明 prompt injection 文本不能改变索引器行为；
11. 结构 schema、migration、rollback、determinism 和 credential lint 通过；
12. 真实用户测试证明作者或 Reviewer 能使用图谱回答预设理解问题，不能只以“图成功渲染”作为完成。

## 非目标

- 不自动重构、迁移或修复 Skill；
- 不替代 Doctor、evaluate、Guardian、improve 或 release；
- 不在 MVP 建立云端协作、RBAC、公开托管或遥测；
- 不做通用代码知识图谱；
- 不承诺所有自然语言关系都能确定性解析；
- 不把 AI 总结或单一分数包装成真实行为效用；
- 不自动安装 MCP、Plugin、Global Skill 或 provider runtime。

## 待决策问题

正式排期前必须只解决会改变产物的关键问题：

1. 第一载体是独立 local Web、VS Code extension，还是 Skill Engineering 内嵌报告；当前推荐独立 local Web；
2. 独立仓库还是本仓子产品；当前推荐独立产品、共享 versioned schema；
3. `Skill Graph Projection` 是 Blueprint 1.x extension 还是独立 schema；
4. MVP 是否包含可选 AI 解释，还是先交付纯确定性图；
5. runtime trace overlay 与 Observation Boundary、Behavior Evaluation Lab 的版本关系；
6. 首个真实用户验收使用单个 Skill 还是包含 3–5 个不同架构 fixture。

## 当前状态

- 需求分析：完成；
- 公开竞品调研：完成；
- Spec：完成，尚未接受为 Sprint 承诺；
- Plan：已准备；
- ADR：未创建；
- Task/Sprint：未进入；
- 代码、测试、版本和发布状态：未改变；
- 实际任务效用：尚未验证。

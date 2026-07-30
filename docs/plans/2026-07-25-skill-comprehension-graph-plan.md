# Skill 可理解性知识图谱（Skill Graph）实施计划

状态：Backlog / 未排期 / 只用于未来任务安排 / 不得据此直接修改代码

日期：2026-07-25

对应 Spec：[`2026-07-25-skill-comprehension-graph-spec.md`](../specs/2026-07-25-skill-comprehension-graph-spec.md)

## 计划目标

在不扩大当前 `v2.0 Architecture Guardian Phase 1`、不建立第二套 Blueprint/Doctor/Apply 引擎的前提下，为未来 Skill Graph 产品提供可分阶段安排的实施路线。

推荐最终形态：

```text
Skill source
  -> deterministic inventory / extractor
  -> existing Blueprint + detailed Skill Graph Projection
  -> query and impact core
  -> local Web graph
  -> optional AI explanation
  -> optional CLI/MCP/runtime overlays
```

这只是待接受的方向。正式开工前必须通过 ADR 确认产品载体、仓库归属、schema 边界和版本归属。

## 排期与治理边界

- 本 Plan 不属于当前 Sprint；
- 不更新 `docs/TASK.md`、当前 Sprint、Roadmap 版本承诺或 Changelog；
- 用户后续明确安排时，先把对应阶段从 Backlog 提升为 Task/Sprint；
- 一个 Sprint 只承诺一个可验证切片，不将 SG-0 至 SG-6 一次性打包；
- 代码变更使用独立 candidate，不能直接把实验写入 maintained source；
- commit、push、tag、公开发布、Global/Plugin/MCP 启用分别确认。

## SG-0：立项与架构边界

### 目标

把需求池候选升级为可实施项目，同时避免与 Skill Engineering 2.0 重复。

### 工作

1. 确定产品工作名、owner、目标用户和首个真实验收场景；
2. 决定独立仓库、本仓子产品或只读 UI adapter；
3. 决定第一载体：推荐 local Web，VS Code extension 后置；
4. 盘点 Blueprint inventory、Guardian、semantic diff、Doctor、evaluation 和 Observation 的可复用接口；
5. 建立跨版本 ADR：
   - Skill Engineering 与 Skill Graph 的 ownership；
   - Blueprint 与 `Skill Graph Projection` 的 schema 关系；
   - local-first 与可选 provider 的 trust boundary；
6. 将首个实现切片提升到 Task/Sprint。

### 退出条件

- ADR 已接受；
- 当前 Sprint 是否暂停、并行或后置有明确决定；
- 首个切片有独立 Spec/Plan 更新、验收 fixture 和 owner；
- 未创建重复 inventory、apply 或发布系统。

## SG-1：版本化图谱契约

### 目标

建立 UI、CLI、MCP 和 AI 解释都能消费的稳定只读图模型。

### 工作

1. 定义 node、edge、evidence、source anchor、confidence、unknown、finding 和 extension；
2. 定义 declared/detected/inferred/observed 四级 provenance；
3. 定义 canonical JSON、schema version 和 fingerprint；
4. 结构 fingerprint 与 AI explanation fingerprint 分离；
5. 定义 graph/source/extractor/schema 的独立版本；
6. 定义 baseline/candidate graph diff 形状；
7. 为 atomic、router、orchestrator、adapter、composite 建立 fixtures；
8. 增加 malformed、broken link、prompt injection、credential、path escape、large file 和 legacy cases。

### 兼容要求

- 不破坏 Blueprint `1.0.0`；
- 不把细粒度图谱字段强塞入 Blueprint 主 schema；
- unknown round-trip；
- 破坏性 schema 修改有 migration 和 rollback fixture。

### 退出条件

- schema validation、canonical round-trip 和 fingerprint 稳定；
- fixtures 覆盖五种 Skill 类型和高风险输入；
- 同一输入重复生成 byte-stable 结构图；
- 不包含凭证或原始私有对话。

## SG-2：确定性 inventory 与 extractor

### 目标

在不执行目标代码的情况下，从真实 Skill 生成高置信结构图。

### 工作

1. 复用现有 Blueprint inventory；
2. 解析 Markdown/frontmatter 标题、链接、路径和代码块；
3. 解析 `skill.contract.yaml` 的 trigger、input、output、stop、delegate、forbidden、state、script、test；
4. 发现 references、stages/workflows、scripts、assets 和 tests；
5. 从 Python/shell/JSON 等文件提取静态 import、CLI/tool 名称和 source anchor；
6. 识别不存在路径、循环引用、未声明依赖和无法确定关系；
7. 增加文件 fingerprint 和增量 invalidation；
8. 输出 inventory diagnostics，不把 partial 伪装成 complete。

### 安全要求

- 不 import、source 或执行目标脚本；
- 不执行 Markdown 代码块；
- 不跟随越界软链接；
- `.env*`、私钥、token、cookie、二进制和生成缓存默认排除；
- prompt injection 只作为文本节点，不改变解析器行为。

### 退出条件

- 当前 `skill-engineering` 真实 Skill 可重复建图；
- 显式本地引用的 resolved/broken 状态可复核；
- 节点和边都能回到证据位置；
- negative/high-risk tests 通过。

## SG-3：查询、影响分析和导出

### 目标

让图谱能够回答任务问题，而不只是展示所有节点。

### 工作

1. search 和 scoped node list；
2. dependencies / dependents；
3. bounded path；
4. trigger-to-output flow；
5. impact / affected evidence and tests；
6. 按类型、provenance、confidence、文件和阶段过滤；
7. fresh/stale/partial/failed 状态；
8. JSON、Markdown、Mermaid 稳定导出；
9. 为未来 CLI/MCP 固定只读 query API。

### 退出条件

- 同一 query 对同一 graph fingerprint 返回稳定结果；
- 路径查询不会无限遍历循环；
- 每个结果带 evidence 和 unknown；
- 常见问题有 deterministic golden tests。

## SG-4：local-first Web 图谱

### 目标

交付作者和 Reviewer 能实际使用的可视化产品。

### 候选结构

```text
deterministic core
  -> local read-only API
  -> Web application
     -> graph canvas
     -> source/evidence panel
     -> search/filter/scope
     -> structure/execution/safety/evidence views
```

具体技术栈在 SG-0 ADR 中决定。本 Plan 不提前锁定 WebGPU、WebGL、Canvas、图数据库或前端框架。

### 工作

1. Overview：目的、类型、治理等级、组件和未知项；
2. 四种视图：结构、执行、安全审批、测试证据；
3. 节点详情、原文、证据、上游和下游；
4. 搜索、聚焦、展开/折叠、Scope 和过滤；
5. 两节点路径和影响范围；
6. stale/partial/error UI；
7. 键盘操作、标签、非纯颜色编码和基础无障碍；
8. 使用真实 Skill 完成任务型可用性测试。

### 退出条件

- 不依赖 LLM 也能完成核心浏览；
- 默认视图不会展开所有段落；
- 用户能完成预设理解问题，而不只是看到图；
- local service 只读绑定 loopback，远程绑定需要独立安全设计。

## SG-5：可选 AI 解释与 Guided Tour

### 目标

在结构事实稳定后，帮助非专家理解职责、意图和学习顺序。

### 工作

1. 节点和执行路径通俗解释；
2. 按依赖顺序生成 Guided Tour；
3. 作者、Reviewer、普通使用者三种解释深度；
4. 只向模型发送完成任务所需的最小子图和原文片段；
5. provider/model/prompt version/source fingerprint 进入 explanation metadata；
6. 解释缓存随 source fingerprint 失效；
7. 解释冲突、低置信和 unsupported 明确展示。

### 安全与评测

- 默认关闭外部 provider；
- 调用前说明会发送哪些内容；
- 不保存 raw prompt、完整会话或凭证；
- 不能用 LLM 解释替代结构 hard gate；
- 使用独立问答集验证 factuality、evidence attribution 和 unknown honesty。

### 退出条件

- AI 输出与结构事实视觉隔离；
- 所有解释可追溯到子图和证据；
- AI 关闭不影响核心产品；
- 真实任务评测证明解释提高理解，不用主观“看起来不错”代替。

## SG-6：后续集成

以下能力分别排期，不作为 MVP 收尾条件：

- CLI/MCP：Agent 查询同一图和 query API；
- IDE extension：VS Code/Cursor 中定位源文件和节点；
- runtime trace overlay：接入脱敏 Observation/SkillRun；
- semantic diff Review：与 Guardian finding、improve plan 联动；
- 多 Skill Portfolio：owner、stale、route collision 和跨 Skill 依赖；
- 团队分享、RBAC、托管和企业策略。

任何安装、Global、Plugin、MCP 配置或远程服务都需要新的 Spec/Plan 和明确授权。

## 测试计划

### 契约与确定性

- schema positive/negative；
- canonical round-trip；
- fingerprint stability；
- unknown/extensions preservation；
- migration/rollback；
- graph diff。

### 解析与安全

- 五种 Skill 架构 fixtures；
- broken/missing/cyclic references；
- path traversal 和 symlink escape；
- prompt injection text；
- credential and private-key fixtures；
- binary、large file、encoding 和 partial failure；
- 脚本不执行证明。

### 查询

- dependencies/dependents；
- shortest/bounded path；
- trigger-to-output；
- cycle handling；
- filters/scope；
- impact and affected tests；
- stale index。

### UI

- source/evidence navigation；
- collapse/expand；
- empty/partial/error states；
- keyboard and accessibility；
- large graph degradation；
- Playwright task flows。

### 真实效用

- 作者能回答“改这里会影响什么”；
- Reviewer 能回答“有哪些副作用和审批”；
- 新用户能回答“从请求到输出如何运行”；
- 与纯文件阅读基线比较完成时间、遗漏和错误；
- 没有真实对照前只报告结构 readiness，不宣称理解效用已提升。

## 验证门禁

实现阶段在仓库既有门禁基础上至少运行：

- pytest；
- Ruff；
- Skill validation；
- production Doctor；
- credential lint；
- schema/Markdown link check；
- `git diff --check`；
- UI 单元测试和 Playwright；
- migration/rollback；
- 至少一个真实 Skill E2E；
- 独立评审。

如果产品进入独立仓库，应建立等价门禁，而不是从 Skill Engineering 复制不适用的命令。

## 失败与恢复

- 图缓存始终可重建，不作为唯一事实源；
- 索引失败保留上一个可识别版本并标记 stale/failed；
- schema 迁移前备份旧 graph artifact；
- AI 解释失败不影响结构图；
- UI 失败不损坏 Blueprint、Skill source 或维护记录；
- 任何实验代码失败只撤销独立 candidate，不修改正式 Skill；
- 不提供自动修复或 Apply，避免可视化产品成为第二个写入入口。

## 主要风险与缓解

| 风险 | 缓解 |
|---|---|
| 自然语言关系误判 | provenance、confidence、evidence、unknown；AI 不覆盖结构事实 |
| 全图成为毛线团 | 分层、折叠、Scope、有界查询和问题子图 |
| 与 Guardian 重复 | Blueprint/inventory 单一 owner；Skill Graph 只做派生投影和体验 |
| 隐私泄露 | local-first、敏感排除、最小上下文、外部调用显式授权 |
| 动态范围膨胀 | MVP 只做源码增量和问题子图；runtime 后置 |
| 先锁死技术栈 | SG-0 ADR 后决定存储和渲染，不在需求池中承诺 |
| 漂亮但无用 | 任务型用户测试和纯文件阅读基线 |

## 未来任务拆分建议

用户排期时，建议按以下独立任务创建，而不是建立一个长期 Doing 大任务：

1. `Skill Graph SG-0：产品边界、ADR 与首个验收场景`；
2. `Skill Graph SG-1：Graph Projection schema 与 fixtures`；
3. `Skill Graph SG-2：确定性 inventory/extractor`；
4. `Skill Graph SG-3：query/impact/export core`；
5. `Skill Graph SG-4：local Web MVP`；
6. `Skill Graph SG-5：AI explanation 与 Guided Tour`；
7. `Skill Graph SG-6：MCP/IDE/runtime/Portfolio`。

只有前一阶段退出条件通过，后一阶段才能进入 Sprint。

## 当前交付边界

- Backlog：已建立；
- Spec：已建立；
- Plan：已建立；
- OB 需求池 Task：单独创建；
- ADR、代码、测试、版本、Changelog 和发布：未开始；
- 当前 `v2.0 Architecture Guardian Phase 1`：不变。

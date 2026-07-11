# 选择矩阵

创建 skill 之前,先判断这个能力是否真的需要一个可复用的 agent 入口。很多问题更适合 script、project doc、profile 或 plugin。

## 决策表

| 选择 | 适合什么时候用 | 什么时候不要用 |
|---|---|---|
| 新 skill | 工作流会重复使用、面向 agent、有清楚触发边界,并且需要流程知识或内置资源。 | 只是一次性任务、普通代码逻辑,或只是 checklist。 |
| 复用已有 skill | 已有 skill 已经拥有这个触发边界,并且扩展后不会职责膨胀。 | 会把已有 skill 变成混合领域路由器。 |
| Plugin/runtime | 需要 MCP tools、浏览器、文档、表格 runtime、provider 鉴权或 app 集成。 | 只是静态说明或本地脚本。 |
| Script | 难点是确定性解析、校验、转换、文件检查、状态流转或 API plumbing。 | 主要价值是判断、写作、分组或解释。 |
| Project doc/rule | 只适用于一个 repo,不应该跨项目触发。 | 应该跨多个项目复用。 |
| Profile entry | skill 已经稳定存在,只是需要按项目/agent 暴露。 | skill 还不稳定或触发词过宽。 |
| 不新增产物 | 需求一次性,或基础模型和项目上下文已经足够。 | 流程会重复,或步骤脆弱。 |

## 必答问题

落脚手架前先回答:

1. 哪些用户说法应该触发这个能力?
2. 哪些相似说法不应该触发?
3. 哪些 agent 入口需要它: Codex、Claude Code、两者都要,还是默认都不要?
4. 它应该是 global、project-only、profile-managed、direct/manual、plugin-backed,还是 archived?
5. 哪些部分必须确定性执行,因此应该放进 script?
6. 哪些状态或审批必须跨 turn 留存?
7. 哪个失败不能再发生,对应 regression case 放在哪里?

## 红旗

- 提议里的 skill 说自己“处理所有相关事项”。
- 能力其实需要工具或 provider runtime,应该是 plugin。
- 能力其实只做校验或转换,应该是 script。
- 触发边界和两个已有 global skill 重叠。
- 创建它的唯一原因是某个任务失败过一次。

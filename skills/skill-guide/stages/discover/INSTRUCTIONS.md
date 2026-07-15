# Discover 阶段

当用户有一个能力想法,但还不确定应该做成什么产物时,使用这个阶段。

1. 读取 `references/capability-brainstorming.md` 和 `references/selection-matrix.md`。
2. 先自查已有 Skill、项目规则、scripts、Plugin/runtime、Profile 和相似实现,不要让用户重复盘点机器可见事实。
3. 信息不足时返回 `needs_discovery`,不得默认推荐创建 Skill。
4. 一次只问一个会改变产物判断的问题,从真实任务、重复性、AI 判断价值和触发边界开始。
5. 收集至少一个应该触发和一个不应该触发的相似说法;复杂能力再扩展到 2-5 个。
6. 信息足够后比较最相关的 2-3 个方案,说明复用价值、维护成本、触发风险、runtime 和安全边界。
7. 推荐一种选择:不新增、复用已有 Skill、Plugin/runtime、Script、项目规则、Profile、归档/替换或新 Skill。
8. 用户确认创建/扩展 Skill 后,再判断 atomic、orchestrator、router、adapter 或 composite。
9. 只有复杂、生产、商业或多版本 Skill 才进入 Product/版本/Backlog/Spec/Plan 治理。
10. 涉及 global 暴露、Plugin 启用或外部副作用时先停下确认。

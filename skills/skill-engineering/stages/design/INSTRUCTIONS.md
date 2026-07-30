# Design 阶段

当产物类型已经选定后,使用这个阶段。

1. 读取 `references/authoring-brief.md` 与 `references/authoring-standard.md`。
2. 先确认 Authoring Brief 就绪(`goal`、触发/反触发、`verification` 不缺);不就绪时回到 discover 补问,不得直接生成候选。
3. 先写触发边界和反触发,不要先写长流程。
4. 定义 inputs、outputs、stops、delegates、forbidden、approvals 和 verification。
5. 判断哪些内容应该放到 scripts、references、assets、tests 或 project docs。
6. 对复杂 skill,先创建或更新 `skill.contract.yaml`,再写较长说明。
7. 保持根 `SKILL.md` 像接口和路由,不要把它写成事故复盘。

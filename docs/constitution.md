# Skill Engineering 工程宪章

以下原则跨版本有效。修改本文件需要 ADR、Spec、迁移影响和独立评审。

1. **先探索，再判断是否需要 Skill。** Agent 先自查已有能力，再一次询问一个关键问题；信息不足保持 `needs_discovery`，不为一次性问题制造长期资产。
2. **复杂度必须与风险匹配。** 简单 Skill 不套工业模板；商业 Skill 不依赖口头约定。
3. **入口是接口和路由。** 稳定方法放 reference，确定性行为放 script，事故放测试或日志。
4. **修改先找根因层。** 不用追加禁令掩盖 trigger、interface、state、script、structure 或 install 问题。
5. **Preview 与 Apply 分离。** Apply 必须引用用户已经预览的同一份未漂移计划。
6. **每次修改必须有预期行为和回归依据。** production 不允许无证据豁免。
7. **结构健康不等于真实效用。** Doctor 分数不得冒充下游效果。
8. **候选生成不得看到 holdout assertions 或 baseline 评分。** 防止证据泄漏和伪优化。
9. **发布必须可验证、可追踪、可恢复。** Canary/Active 需要明确审批，Global 不自动执行。
10. **凭证和私有内容不进入仓库或本机状态。** 只保存脱敏摘要和 artifact pointer。
11. **Skill Engineering 必须自举。** 本项目的功能也必须经过 Product、Backlog、Spec、Plan、ADR、测试和版本流程。
12. **代码和文档必须共同完成。** 说“完成”前对齐实现、测试、用户文档和版本状态。

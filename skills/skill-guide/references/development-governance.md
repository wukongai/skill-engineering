# 复杂与商业 Skill 开发治理

这份规范用于生命周期长、多人维护、生产复用、商业交付或高风险 Skill。简单 atomic Skill 不需要复制完整项目结构。

本阶段只在能力探索已经决定“创建或扩展 Skill”后进入。新需求尚未完成产物判断时,先使用 `capability-brainstorming.md`,不得提前创建产品和版本工件。

## 何时升级治理

满足任一条件时，从轻量 Skill 升级为受治理 Skill：

- 预计经历多个版本或由多人维护；
- 用户或客户依赖稳定输入输出；
- 包含阶段状态、多个 delegate、脚本或外部副作用；
- 需要发布、回滚、兼容或审计；
- 修改次数增加后出现重复规则、入口膨胀或架构漂移；
- 将作为收费产品、训练营资产或工业流程交付。

## 最小事实源

| 工件 | 回答的问题 |
|---|---|
| Product | 为谁解决什么问题，当前版本不做什么。 |
| Architecture | 能力、状态、依赖和执行边界如何组织。 |
| Roadmap | 版本级方向。 |
| Backlog | 尚未承诺进入当前版本的候选。 |
| Sprint / Task | 当前周期承诺交付什么。 |
| Spec | 为什么改、必须满足什么。 |
| Plan | 如何改、如何验证和恢复。 |
| ADR | 为什么选择这项跨版本架构。 |
| Daily Log | 今天发生了什么、卡在哪里。 |
| Changelog / Version | 用户实际拿到了什么。 |

允许使用项目已有的等价命名，不要为了模板重复建事实源。

## 开发顺序

1. 从 Product、Architecture、当前 Sprint 和 Task 恢复上下文。
2. 新想法先进入 Backlog；只有确认进入当前版本才升级为 Task。
3. 功能级修改先写 Spec，再写 Plan。
4. 跨版本结构取舍写 ADR；普通实现细节不写 ADR。
5. 在独立候选中修改，不直接覆盖 maintained source。
6. 用维护计划检查文件、语义边界、复杂度和回归证据。
7. 应用同一未漂移计划，自动 postflight，失败恢复。
8. 更新 Daily Log；稳定结论同步到正式文档。
9. 发布前对齐版本、Changelog、Roadmap、Task、Sprint 和验证证据。

## 防止越改越乱

每次修改至少回答：

- 这是 trigger、interface、state、script、style、long-task、install、structure 还是 test 问题？
- 新规则能否移到更低、更确定的层？
- 是否增加重复指令、入口行数、状态、依赖或 context 成本？
- 是否破坏旧输出、旧调用方或 protected behavior？
- 是否应该删除或迁移旧结构，而不是只追加内容？
- 哪个回归用例证明这次修改有效？

事故和当日过程进入 Daily Log/测试，不进入根 `SKILL.md`。根入口只保留跨版本稳定的触发、路由、停止点和用户契约。

## 版本和商业交付

- 使用语义化版本；破坏性 contract 变化需要迁移说明。
- 未通过真实行为证据时，只能宣称结构 readiness。
- 收费或工业级 Skill 需要 owner、安全边界、独立评审、回滚和支持范围。
- 不因商业化而保存客户凭证、原始私有 Prompt 或完整对话。
- commit、push、tag、公开发布和 Global 安装是独立确认点。

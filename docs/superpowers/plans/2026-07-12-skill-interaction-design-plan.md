# Skill Engineering 交互体验改造计划

状态：已完成（2026-07-12）。全部 89 项测试、Ruff、Skill quick validate、production Doctor、凭证检查和两次独立对话前向测试均通过。

## 1. 建立确定性反馈模型

- 新增 `src/skill_engineering/interaction.py`。
- 定义 `UserFeedback` 和统一渲染器。
- 先写 completed、incomplete、blocked、awaiting-approval 的单元测试。

## 2. 改造跨窗口恢复

- 更新 `JourneySession.handoff_summary()`。
- 默认隐藏 stage/status，保留 JSON 状态。
- 增加目标、可感知结果、安全状态和唯一下一步测试。

## 3. 改造发布与进化输出

- 为 Release Plan、发布、验证和回滚增加用户摘要。
- 将 Evolution 的类型名、对象 ID 和裸状态替换为结果与下一步。
- 多候选列表默认输出数量与推荐结论，完整记录仍走 JSON。

## 4. 收敛计划与维护反馈

- 创建计划默认说明将创建什么、在哪里、是否已写入。
- 改进计划默认说明问题、文件动作、风险和下一步，不默认打印 unified diff。
- 维护结果区分成功、部分失败和可撤销状态。

## 5. 对齐 Skill Guide

- 将内部规范链接到 Skill Guide 参考层。
- 扩充交互 fixture：推荐、审批、完成、部分失败、恢复。
- 保持根 `SKILL.md` 轻量。

## 6. 验证

- 运行定向测试、完整 pytest、Ruff、Skill quick validate、production Doctor 和凭证检查。
- 使用独立 agent 做至少两个真实对话前向测试。
- 检查默认输出无内部 ID、指纹和裸状态枚举。

## 7. 收尾结果

- `UserFeedback` 已接入 Journey、产物推荐、创建/改进、评测、进化、发布、验证、回滚和 Doctor 默认文本输出。
- JSON schema、持久化记录和安全门禁保持兼容。
- README、架构、交互规范、Spec 与端到端验收记录已经对齐。
- 配套自媒体文章已由“一键发文”生成，但未同步到任何外部平台，也不属于本仓库版本控制。

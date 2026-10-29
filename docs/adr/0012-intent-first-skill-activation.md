# 以任务意图驱动Skill发现与模糊上下文路由

状态：Accepted；本地实现、独立评审与验证完成。决定日期：2026-10-29。

[ADR索引](README.md) · [需求合同](../specs/2026-10-29-implicit-skill-activation-spec.md) · [实施计划](../plans/2026-10-29-implicit-skill-activation-plan.md)

## 背景

Skill允许隐式调用但仍可能漏选。宿主先读元数据，描述可能截短；把规则只写在选中后才读的正文会形成自举缺口。名字已有对外使用，用户只恢复自动激活，不恢复改名。

## 决定

保持唯一skill-engineering身份，将创建、维护、检查及对象放到description最前部，配合轻量上下文澄清和反触发规范。沿用allow_implicit_invocation=true，不虚构优先级字段，不改官方Creator、全局AGENTS或用户配置。

真实宿主在相同控制条件下选择候选。不能假设同名项目Skill覆盖用户版本；旧source通过本次测试配置按路径禁用。保留Creator竞争，使用实际根SKILL.md正文读取trace验证，而非自报或关键词命中。

## 替代与限制

纯正文提醒不能影响首次发现；新关键词分类器会误把确定性匹配当成语义理解；全局强制路由扩大范围且不可移植。当前选择元数据与既有宿主机制，依据实际样本评价。对象完全未知时先澄清，不保证所有宿主和所有自然语言必然触发。

## 验收与恢复

以[需求验收](../specs/2026-10-29-implicit-skill-activation-spec.md#验收)和[实际证据](../testing/2026-10-29-implicit-skill-activation.md)为准。通过原维护计划Apply/Verify，失败使用原备份与安全恢复；不建立第二执行链。

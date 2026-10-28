# ADR 0010：内部维护架构审查与原计划绑定

状态：Accepted；本地实现、独立评审及工程验证完成。决定日期：2026-10-29。

后续策略修订：[默认强制审查决定](0011-mandatory-maintenance-architecture-review.md)已实现并验证，取代本文“无声明仍可应用”的兼容条款，其他架构决定保持。本文保留前轮实现事实。

[返回 ADR 索引](README.md) · [架构](../architecture.md) · [需求合同](../specs/2026-10-29-maintenance-architecture-review-spec.md) · [实施计划](../plans/2026-10-29-maintenance-architecture-review-plan.md)

## 背景

单次修改的结构与安全检查不足以约束跨版本职责和债务。根入口继续追加规则会增加上下文负担；独立子 Skill 或另建 Apply 引擎又会制造双重维护合同。现有 BuildPlan 以全部既有字段计算哈希，直接增加 dataclass 字段会影响历史计划校验。

## 决定

新增内部 architecture-review 阶段，保持唯一顶层 Skill。Agent/独立评审者负责职责裁决和整体判断，确定性核心负责输入校验、指纹绑定、历史基线、累计预算和债务归并。

审查报告嵌入现有 preflight，并随原 plan hash 固定；报告绑定 target/candidate/effective 指纹，不反向存最终 plan hash，避免循环哈希。MaintenanceRecord 复用其现有 preflight 快照，不新增并行状态引擎。

新增 CLI 参数为可选扩展。无声明的旧调用明确未审查，旧计划保持原哈希及 Apply/Verify/Undo 兼容。有效完整审查并验证后的记录才能成为后续累计基线。

## 理由与影响

- 用户继续使用同一入口，只有所需阶段进入上下文。
- 安全写入边界保持一致；整体审查不能替代真实行为证据。
- 当前实现是声明与确定性事实的门禁，不宣称自动理解全部架构语义。
- 正式版本与已有稳定发布事实不变化，完整 2.0 Guardian 保留原后续范围。

## 替代方案

只增加提醒无法防止跨次累积；每次完整重构会阻碍小修；新增独立子 Skill/状态引擎会重复契约；直接扩展 plan dataclass 会增加兼容迁移成本。本轮选择内部阶段与既有字段扩展。

## 后续迁移

将来 Blueprint/Guardian 可以消费本报告作为证据输入，但不能绕过既有不可变计划、审批及恢复机制。需要改变公开 schema 或哈希语义时另写迁移决策，不静默升级历史记录。

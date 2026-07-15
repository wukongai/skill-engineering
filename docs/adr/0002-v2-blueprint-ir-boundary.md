# ADR-0002：v2.0 使用版本化 Blueprint/IR 作为架构事实层

状态：Accepted for v2.0 Phase 1

日期：2026-07-16

## 背景

单个 Skill 的 Doctor 可以检查结构和安全，但无法稳定表达组件角色、执行拓扑、治理等级、依赖和架构变化。继续把这些内容追加到自然语言规则会造成入口膨胀和语义漂移。

## 决定

2.0 引入版本化 Blueprint/IR 作为只读架构事实层：

- Component role、execution topology、governance level 是第一版三轴；
- unknown/legacy 是合法状态，不以缺失事实推断风险；
- JSON schema 和确定性 fingerprint 是机器接口；
- Blueprint 先生成 inventory 和 preview plan，不直接修改 Skill；
- 1.x contract/Doctor/evaluate/release evidence 作为输入事实继续兼容。

## 理由

- 把架构事实放到确定性数据层，避免继续堆到 `SKILL.md`；
- 为 semantic diff、依赖图和迁移计划提供共同输入；
- 让未知事实可见，避免模型或规则伪造完整架构；
- 保持 2.0 可渐进接入，不迫使 1.x 用户一次性迁移。

## 影响

- 2.0 会增加 schema、fixture、fingerprint 和迁移证据；
- Guardian 结果会成为 improve/create plan 的输入，但 apply 仍受现有审批边界控制；
- 简单 Skill 不强制保存完整 Blueprint，只有启用架构守护时才生成。

## 替代方案

1. 继续只用自然语言文档：无法做稳定 semantic diff，拒绝。
2. 直接引入完整编译器/云端图数据库：超出 2.0 第一阶段风险和范围，拒绝。

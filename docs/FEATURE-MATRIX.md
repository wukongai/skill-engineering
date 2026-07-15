# Skill Engineering 功能总表

这份表回答“现在能做什么、属于哪个版本、证据在哪里”。`已交付` 只表示代码和门禁已经通过；`Unreleased` 不等于已经公开发布。

| 能力域 | 功能 | 当前状态 | 目标版本 | 主要入口/证据 |
|---|---|---|---|---|
| Discover | 自查已有 Skill/Script/Plugin/规则 | 已交付 | 1.0 稳定 | `decide`、PRODUCT、Spec |
| Decide | 逐步澄清并判断产物类型 | 已交付 | 1.0 稳定 | `decide`、decision tests |
| Create | 最小架构选择与完整 Skill 候选 | 已交付 | 1.0 稳定 | `create` |
| Create | Preview → 同一计划 Apply → postflight | 已交付 | 1.0 稳定 | build plan、scaffold tests |
| Doctor | 结构、行为风险、安全和治理检查 | 已交付 | 1.0 稳定 | `doctor` / `audit` |
| Doctor | AST 动态执行、shell、source-to-sink | 0.1.1 Unreleased | 1.0 纳入稳定契约 | `SEC108-SEC111`、security tests |
| Doctor | JSON 与 SARIF 2.1.0 报告 | 0.1.1 Unreleased | 1.0 纳入稳定契约 | `--format sarif` |
| Evaluate | baseline/holdout/high-risk/negative-transfer | 已交付 | 1.0 稳定 | `evaluate`、evaluation docs |
| Improve | 隔离候选、失败模式、复杂度 diff、维护记录 | 已交付 | 1.0 稳定 | `improve`、verify/undo |
| Evolve | 脱敏 run、候选、Pareto、Shadow/Canary/Active | 已交付 | 1.0 稳定 | evolution/release plan |
| Release | 预览、审批、验证、回滚证据 | 部分交付 | 1.0 完整冻结 | release plan、release installer |
| Governance | Product/Architecture/Spec/Plan/ADR/Sprint/Changelog | 已交付 | 1.0 稳定 | `docs/` |
| Packaging | wheel、安装 smoke、版本兼容矩阵 | 待开发 | 1.0 必须完成 | 1.0 spec/plan |
| Contract | 稳定 CLI、JSON、contract schema 与迁移 | 待开发 | 1.0 必须完成 | 1.0 spec/plan |
| Blueprint | 组件角色、执行拓扑、治理等级三轴描述 | Schema/模型已交付，inventory 待开发 | 2.0.0 | `blueprint.py`、schema、2.0 spec/plan |
| Architecture Guardian | 依赖、冲突、重复职责、context budget、route collision | 2.0 计划 | 2.0.x | 2.0 spec/plan |
| Semantic Diff | 识别 Skill 修改后的架构语义变化 | 2.0 计划 | 2.0.x | 2.0 spec/plan |
| Migration | 自动生成拆分、迁移、压缩和废弃计划 | 2.0 计划 | 2.0.x | 2.0 spec/plan |
| Portfolio | owner、stale、依赖图、安装兼容 | Backlog | 2.1+ | `docs/BACKLOG.md` |
| Distribution | Registry/Profile/Adapter/多项目分发 | 外部边界 | Agent Skill Hub | architecture boundary |
| Hosted/Enterprise | 云端协作、RBAC、托管评测、SLA | 明确不在当前范围 | 未来商业版本 | PRODUCT/BACKLOG |

## 版本阅读方式

- 想使用当前能力：看 README 和 `0.1.x` 记录。
- 想依赖稳定契约：看 `1.0.0` Spec/Plan 和发布门禁。
- 想参与当前开发：看 `2.0.0` Sprint、Spec、Plan 和 ADR。
- 想提议额外能力：先进入 Backlog，不直接扩大当前 Sprint。

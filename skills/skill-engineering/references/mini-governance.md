# Skill 的 Mini 治理

所有新建或扩展的 Skill 都先经过三件轻量事实源：mini Product、mini Spec、mini Plan。它们可以合并保存为一份脱敏 Mini Governance Record，不要求简单 Skill 生成完整项目文档。

## 三件套

| 工件 | 必须回答的问题 | 主要来源 |
|---|---|---|
| mini Product | 谁反复使用、要完成什么、为什么值得复用、明确不做什么？ | `goal`、`target_users`、复用判断、范围边界 |
| mini Spec | 什么请求触发、输入输出是什么、步骤和失败路径是什么、怎样算完成、偏题后如何拉回？ | triggers、inputs、outputs、workflow、failure_modes、Boundary Contract、verification |
| mini Plan | 生成或修改哪些文件、先预览什么、何时需要批准、如何验证和恢复？ | resources、side_effects、approvals、verification、Native Plan |

## 流程

1. 能力探索完成并确认创建或扩展 Skill 后，按[边界确认细则](boundary-confirmation.md)先提出做/不做/完成条件，复用明确用户表达，形成脱敏 Mini Governance Record。
2. `goal`、正向/反向触发、输出和验证缺失时保持 `needs_discovery`。
3. Mini Product 和 mini Spec 就绪后，按能力登记适用文本案例，再生成完整候选；候选不能只是空骨架或泛化 Prompt。
4. Native Plan Preview 把 mini Plan 绑定到候选、目标和文件清单；用户确认实际影响后才 Apply。
5. Apply 后运行 Verify、Content Gate、Creation Review 和可用的 Skill self-test。

## 升级

复杂、生产、商业或多版本 Skill 出现团队复用、生产副作用、复杂状态、外部系统、发布/回滚或架构漂移时，读取 `development-governance.md`，在 mini 三件套之上补齐 Product、Architecture、Roadmap、Backlog、Spec、Plan、ADR、Sprint、Daily Log、Version 和 Changelog 等完整事实源。

简单 Skill 可以仍然只交付一个完整的 `SKILL.md`；这只描述候选文件的最小形态，不代表跳过 mini 治理、预览、验证或失败处理。

## 恢复与兼容

历史 Skill 没有 Mini Governance Record 时，可根据现有文件逐步补建脱敏记录，不把推断写成历史确认。无业务边界变化的小修按[维护接入](boundary-confirmation.md#创建与维护接入)说明 unchanged 理由并保持 `legacy_unknown`；边界变化再确认当前提案。旧 Authoring Brief、Plan、维护记录和 1.x 状态继续兼容读取，不批量改写历史。

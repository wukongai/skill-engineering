# Universal Mini Governance Spec

状态：Implemented in working tree，待全量门禁与独立评审

## 背景

Skill Engineering 已经要求所有 Skill 在创建前形成 Authoring Brief，并要求预览计划与候选绑定；但产品文档把 Product、Spec、Plan 限定在复杂或商业 Skill，导致简单 Skill 的工程化事实源没有统一名称，也不容易在后续维护中恢复。

## 决策

所有新建或扩展的 Skill 都必须先经过一套轻量的 mini Product、mini Spec 和 mini Plan。三者可以保存在同一份脱敏的 Mini Governance Record 中，不要求为简单 Skill 复制完整项目目录。

- **mini Product**：说明目标用户、反复任务、复用价值和明确不做什么。
- **mini Spec**：说明正向/反向触发、输入、输出、工作流、失败处理、副作用和验收条件。
- **mini Plan**：说明候选文件、实施顺序、预览/批准边界、验证命令或检查项，以及失败恢复方式。

Authoring Brief 是 mini Product 与 mini Spec 的结构化输入；Native Plan 是 mini Plan 的可执行绑定。现有 Brief、Plan、Content Gate、Creation Review 和 Verify 继续复用，不新增一套平行执行引擎。

## 分级治理

1. 所有 Skill：必须完成 mini Product、mini Spec、mini Plan，并在写入前完成 Preview。
2. 团队/生产 Skill：在 mini 治理之上增加 contract、回归用例、行为证据、维护记录和版本边界。
3. 复杂、商业或多版本 Skill：继续升级到完整 Product、Architecture、Roadmap、Backlog、Spec、Plan、ADR、Sprint、Daily Log、Version、Changelog、评审和发布/回滚证据。

“轻量”只表示事实源压缩，不表示跳过边界、失败路径、验收或预览；“完整治理”也不能替代 mini 三件套。

## 不变边界

- 新需求仍先完成能力探索和产物判断；尚未决定创建 Skill 时，不生成 mini 治理记录。
- Preview 不写入正式目标；Apply 必须引用同一份未漂移计划。
- 简单 Skill 仍可以只有一个完整的 `SKILL.md` 作为候选交付物。
- mini 治理记录只保存脱敏摘要，不保存凭证、原始私有会话或完整敏感 Prompt。

## 验收

- 创建 Skill 的引导明确展示 mini Product、mini Spec、mini Plan 的结果。
- 缺少三者任一必要字段时保持 `needs_discovery`，不得生成候选或写入目标。
- 简单 Skill 不被要求生成完整项目治理文件，但其 mini 记录能被恢复、预览、维护和审计引用。
- 复杂或商业 Skill 仍能进入完整治理路由，并且完整 Spec/Plan 不能被 mini 记录替代。
- 文档、contract、行为测试和创建路径不再声称简单 Skill 可以跳过全部 Product/Spec/Plan。

# Universal Mini Governance Implementation Plan

对应 Spec：[`2026-10-20-universal-mini-governance-spec.md`](../specs/2026-10-20-universal-mini-governance-spec.md)

状态：执行中；实现已落地，待全量门禁与独立评审

## 目标

把“所有 Skill 先经过 mini Product、mini Spec、mini Plan，复杂/商业 Skill 再升级完整治理”落实到产品定位、对话入口、Authoring Brief、契约和回归检查中，并复用现有 Native Plan 执行链路。

## 实施步骤

1. 新增 `references/mini-governance.md`，定义三个 mini 工件、字段映射、就绪判定和升级条件。
2. 更新 `SKILL.md`、`capability-brainstorming.md`、`authoring-brief.md` 和 `development-governance.md`，明确所有 Skill 的 mini 治理前置与复杂度升级路径。
3. 更新 `skill.contract.yaml`，增加 `mini_governance_record` 输出，并移除“简单 Skill 跳过 Product/Spec/Plan”的过时契约表述。
4. 更新 `PRODUCT.md`、`architecture.md`、公共 Spec、README 和文档索引，使产品承诺与运行入口一致。
5. 增加文档/契约回归测试，覆盖 mini 三件套、`needs_discovery` 阻断、简单 Skill 轻量交付和复杂 Skill 完整治理升级。
6. 更新 `TASK.md`、`ROADMAP.md`、`FEATURE-MATRIX.md`、`CHANGELOG.md` 与 daily log，记录该原则进入当前开发事实源；不执行 commit、push、tag 或公开发布。

## 验证

- `pytest -q`
- `ruff check src tests`
- Skill validation / portable self-test / production Doctor
- credential lint
- `git diff --check`
- 文档断链和版本一致性检查

## 风险与恢复

- 本次变更只调整创建前治理契约与文档，不改变既有 Skill 目标文件的写入格式；失败时可按文件范围回退。
- 旧 Authoring Brief 和旧 1.x Plan 继续兼容读取；没有 mini 记录的历史 Skill 在恢复时补建，不伪造历史事实。
- 不把 mini 记录升级成复杂治理文件，除非用户确认治理等级或风险触发升级条件。

# Handoff：Yao Meta Skill / Superpowers 对比补全与 v2.0 采用矩阵

日期：2026-07-16
来源任务：Agent Skill Hub 与 Skill Engineering 边界收口后的补充任务
目标仓库：`/Users/aim5/Documents/CodingProject/skill-engineering`
状态：`closed`

## 为什么需要继续

Skill Engineering 的 v2.0 Architecture Guardian 已经拥有正式的 Spec、Plan、Sprint、Task 和 Daily Log；Blueprint/IR 主线也已经进入 `v2.0 Phase 1` Sprint。当前 Backlog 明确不重复承诺同一范围，这是正确的版本管理状态。

但 Yao Meta Skill、Superpowers 和本地五种架构模式的对比，目前主要停留在 `docs/TASK.md` 与 daily log 的摘要级结论，还没有形成可复核、可维护、可追踪的研究资产。因此不能把“已完成对比”继续当作完整的竞品研究交付。

## 本 handoff 要补齐的范围

### 1. 建立可复现研究文档

新增一份 `docs/research/` 文档，至少记录：

- Yao Meta Skill 的准确上游 URL、仓库/版本/commit 或无法确认时的 `unknown`；
- Superpowers 的准确来源和审计范围；
- 本地“五种架构设计模式”文档的路径、版本/日期和核心结论；
- 每项能力的证据位置、产品边界和可信度；
- 明确区分“已验证事实”“合理推断”和“尚未确认”。

不得用没有来源的印象性描述替代上游证据；如果网络或上游不可访问，保留 unknown 并记录阻塞原因。

### 2. 建立能力采用矩阵

研究文档中应包含至少以下列：

| 能力/模式 | Yao/Superpowers 证据 | Skill Engineering 当前能力 | V1/V2 归属 | 采用/不采用/延后 | 理由与风险 |
|---|---|---|---|---|---|

重点核对：

- brainstorming / decide 是否进入 V1 的“先判断是否需要 Skill”流程；
- spec、plan、backlog、sprint、daily log、ADR、release 的版本治理如何落到 Skill Engineering；
- 防止越改越乱的候选、复杂度 delta、preflight/postflight、verify/undo 如何对应 V2 Guardian；
- Skill Hub 的 registry/profile/adapter/安装审计明确排除在 Skill Engineering 之外；
- 哪些 Yao/Superpowers 能力不应吸收，避免把两个项目重新合并。

### 3. 让 Backlog 与当前 Sprint 保持单一事实源

- Blueprint/IR、Architecture Guardian Phase 1 继续留在当前 Sprint，不重复添加到 Backlog。
- 如果研究发现的是 V2 Phase 1 的直接缺口，更新当前 Sprint、Task 或 handoff，而不是制造重复 Backlog 项。
- 只有跨版本、暂不承诺的能力才进入 `docs/BACKLOG.md`，并明确版本和 owner。
- 若新增 Yao 研究本身需要后续维护，可增加一个“研究维护/来源复核”候选，但不能把已完成的 V2 主线重复记账。

## 已有事实源

- `docs/specs/2026-07-16-v2.0-architecture-guardian-spec.md`
- `docs/plans/2026-07-16-v2.0-architecture-guardian-plan.md`
- `docs/sprints/2026-07-v2.0-architecture-guardian.md`
- `docs/TASK.md`
- `docs/BACKLOG.md`
- `docs/handoffs/2026-07-16-v2-phase1-next.md`
- `docs/adr/0003-canonical-skill-engineering-identity.md`
- `docs/testing/2026-07-16-skill-identity-unification.md`

## 不要重复做的工作

- 不重写 v2.0 Architecture Guardian 的 Spec/Plan/Blueprint Phase 1 代码。
- 不把 V2 主线重新放回 Backlog。
- 不修改 Agent Skill Hub；Hub 只负责本机 Skill 的登记、profile、adapter、安装和全局暴露审计。
- 不触碰当前工作区已有的标准 Skill CLI 安装改动，除非单独确认其 owner、Spec/Plan 和提交范围。
- 不把 Yao/Superpowers 的内部实现直接复制进 Skill Engineering；只吸收有证据、符合本项目边界的机制。

## 验收标准

- 新增研究文档有明确来源、版本/commit、证据路径和能力采用矩阵。
- 研究结论能逐项映射到 V1、v2.0 Phase 1、v2.0 后续或明确不采用。
- `docs/TASK.md`、`docs/BACKLOG.md`、当前 Sprint 与研究文档没有重复承诺或状态冲突。
- 研究文档不把 Hub 的安装管理能力和 Skill Engineering 的单 Skill 生命周期混在一起。
- 运行文档链接检查、`pytest`、Ruff、credential lint 和 `git diff --check`；若网络不可用，记录精确阻塞，不伪造上游证据。

## 当前工作区保护

- 当前分支：`codex/version-roadmap`。
- 当前 HEAD：`81fa7ac feat: make skill-engineering the canonical agent skill`。
- 当前已有未提交改动：`CONTRIBUTING.md`、`README.md`、`docs/testing/2026-07-16-skill-identity-unification.md`、`skills/skill-engineering/references/install-governance.md`，以及标准 Skill CLI 安装/许可证策略相关的 `docs/adr/0004-*`、`docs/guides/licensing-and-installation.md`、`docs/plans/2026-07-16-*-installation*-plan.md` 和 `docs/specs/2026-07-16-*-installation*-spec.md`。
- `uv.lock` 当前未跟踪；不得删除、覆盖或顺手纳入本任务提交。
- 本 handoff 之外的现有改动不属于本任务；提交时必须显式暂存文件名。

## 下一步

在新任务窗口中先读取本 handoff 和上述事实源，完成 Yao Meta/Superpowers 研究与采用矩阵；完成后单独更新研究索引和必要的 Task/Backlog 记录，再提交本任务文件。不要 push、tag 或公开发布，除非用户另行明确授权。

## 关闭记录

- 2026-07-16：研究文档、研究索引、Task/Backlog 对齐已完成；提交 `177849f`。
- OB 对应任务已更新为 Done：`/Users/aim5/Documents/OB/04 Inbox/task/2026-07-16-【AiCoding实践】skill-engineering 的 V2 版本开发以及验证测试.md`。
- 后续仅在上游版本、来源或本地架构模式发生变化时重新比较和调用；不自动扩展为新的实现承诺。

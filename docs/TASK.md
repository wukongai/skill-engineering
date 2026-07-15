# 当前任务

当前版本：`2.0.0` Architecture Guardian Phase 1 开发中；`0.1.x` 为基线，`1.0.0` 进入稳定化规划。

## In Progress

- [x] 定义 Blueprint/IR schema version、三轴字段、unknown/legacy 和 fingerprint。
- [ ] 为 atomic/router/orchestrator/adapter 建立最小 Blueprint fixture 与负例。
- [ ] 实现只读 Blueprint inventory，不接入 apply。
- [x] 完成 Blueprint schema、migration、rollback 和敏感信息基础门禁回归。
- [ ] 补齐真实 Skill inventory 的 schema/迁移/rollback evidence，并保持不接入 apply。

## v1.0 Stable Contract Planned

- [x] 统一用户可见 Agent Skill 身份为 `skill-engineering`，移除 `skill-guide` 顶层暴露并增加隔离安装/创建/Doctor 回归。
- [ ] 冻结 CLI/API/JSON/contract schema 与兼容策略。
- [ ] 完成 wheel、安装 smoke、Python 支持矩阵和迁移文档。
- [ ] 固定 release evidence、独立评审、回滚和废弃周期。

- [x] 对比 NVIDIA SkillSpector，并固定可复核的上游 commit 与采用矩阵。
- [x] Doctor 增加 Python AST 动态执行、不安全 shell 和外部输入到执行 sink 检查。
- [x] Doctor/audit 增加 SARIF 2.1.0 输出，同时保持默认文本和 `--json` 兼容。
- [x] 通过独立候选和同一 maintenance plan 更新 Skill Engineering Doctor 规则参考。
- [x] 完成 v0.1.1 pytest、Ruff、Skill validation、credential lint 和 diff check。

## SkillSpector Review / v0.1.1 收口

- [x] 核对用户所称 “Skill Spectre” 实际对应的 NVIDIA/SkillSpector，并固定公开仓库 commit `8f534e2951e0b7d0b8fb8e84832cd3605f95c032`。
- [x] 吸收 AST 行为规则、局部 source-to-sink 风险关联和 SARIF 2.1.0 输出；保留原有文本与 `--json` 兼容。
- [x] 完成对比证据、README、Roadmap、功能矩阵、发布日志和测试记录的同步。
- [x] 完成全量验证：pytest 116 passed、Ruff、官方 Skill validation、production Doctor 100/A、credential lint、diff check 和文档/schema 检查。
- [x] 变更已提交为 `c58d389`，推送到 `codex/version-roadmap`，并建立 Draft PR #2。
- [ ] tag、公开发布和从 Draft PR 转为正式发布（保留为独立发布门禁，不在本次 review 自动执行）。

## OB Task 对齐：SkillSpector Review 与 2.0 启动

> 本节是可直接同步到 Obsidian/OB 的任务摘要；项目仓库的正式事实源仍是本文件、当前 Sprint 和 Handoff。

- **任务名称**：Skill Engineering：对比 NVIDIA SkillSpector，吸收安全能力并启动 2.0 Architecture Guardian。
- **任务状态**：SkillSpector review 已完成；2.0 Phase 1 开发中。
- **版本范围**：`0.1.1` Security Doctor 收口、`1.0.0` 稳定化规划、`2.0.0` Architecture Guardian Phase 1。
- **任务目标**：在不破坏现有 CLI、JSON、contract 和发布边界的前提下，引入 AST 行为检查、局部 source-to-sink 风险关联、SARIF 输出，并建立可继续开发的 Blueprint/IR 架构事实层。
- **已完成交付**：
  - 固定 NVIDIA/SkillSpector 上游 commit `8f534e2951e0b7d0b8fb8e84832cd3605f95c032` 与采用矩阵；
  - 完成 AST 动态执行、不安全 shell、外部输入到执行 sink 的 Doctor 规则；
  - 完成 SARIF 2.1.0 输出，并保留默认文本与 `--json` 兼容；
  - 完成 Blueprint schema/model、canonical JSON、SHA-256 fingerprint、unknown/legacy、敏感扩展字段门禁和基础 migration/rollback 回归；
  - 完成 pytest 116、Ruff、官方 Skill validation、production Doctor、credential lint、diff check 和文档/schema 检查；
  - 变更已提交为 `c12f6b0`；前序实现提交为 `c58d389`。
- **当前待办**：
  - 为 atomic/router/orchestrator/adapter 建立最小 Blueprint fixture 与负例；
  - 实现真实 1.x Skill/contract 的只读 Blueprint inventory；
  - 补齐真实 inventory 的 schema、migration、rollback、敏感信息和 0.1.x 回归 evidence；
  - 不接入 apply，不创建 tag，不进行公开发布或 Global enable。
- **验收依据**：[`SkillSpector 测试证据`](testing/2026-07-15-skillspector-security-doctor.md)、[`v2 Phase 1 Handoff`](handoffs/2026-07-16-v2-phase1-next.md)、[`当前 Sprint`](sprints/2026-07-v2.0-architecture-guardian.md)。
- **OB 后续动作**：下一次从 fixture 开始；完成后同步更新本 Task、Sprint、Daily Log、测试 evidence 和 Handoff，再讨论 1.0 push/release。

## v0.1.x Done / Baseline

- [x] 新需求先自查和逐步澄清,信息不足保持 `needs_discovery`。
- [x] 产物判断先于 Skill 架构和 Product/版本治理。
- [x] 完成 v0.1 Public Beta Spec 与 Plan。
- [x] 建立 Product、Constitution、Roadmap、Backlog、Sprint、ADR、Daily Log 和版本体系。
- [x] 创建必须使用同一预览计划 Apply。
- [x] 创建后结构验证，失败自动清理。
- [x] production 创建区分结构完成与发布证据完成。
- [x] 对齐“快速生成 + 从第一版工程化 + 全生命周期保持”的产品承诺并增加回归门禁。
- [x] Skill Engineering 增加复杂/商业 Skill 工程治理路由。
- [x] 更新 README、贡献、安全和 CI。
- [x] 完整门禁与隔离 E2E。

## v0.1.0 Release Gate（历史）

- [x] pytest 全通过。
- [x] Ruff 全通过。
- [x] Skill Engineering production Doctor 零 FAIL/WARN。
- [x] 凭证 lint 通过。
- [x] `git diff --check` 通过。
- [x] README、版本、Changelog、Roadmap、Task 和 Sprint 一致。
- [x] 用户确认真实仓库变更。
- [x] commit、push、tag 和公开发布已获得明确授权。

## v0.1.1 Security Doctor Gate

- [x] SkillSpector 对比证据固定到公开仓库 commit。
- [x] AST 安全规则、SARIF 输出和旧 CLI 兼容回归通过。
- [x] Skill Engineering 同一 maintenance plan Apply、postflight、verify 通过。
- [x] pytest 116 passed。
- [x] Ruff、官方 Skill validation、production Doctor 100/A、凭证 lint、diff check 通过。
- [x] commit、push 已完成：`c58d389` / `codex/version-roadmap` / Draft PR #2。
- [ ] 用户确认 tag 或公开发布（不自动执行）。

## Done

- [x] 完成 Yao Meta Skill、Superpowers 和本地能力审计。
- [x] 明确 V1 核心是创建 + 防架构腐化维护 + 检查 + 自进化 + 友好交互。

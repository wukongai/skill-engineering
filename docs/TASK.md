# 当前任务

当前版本：`2.0.0` Architecture Guardian Phase 1 开发中；`0.1.x` 为基线，`1.0.0` 进入稳定化规划。

## In Progress

- [x] 定义 Blueprint/IR schema version、三轴字段、unknown/legacy 和 fingerprint。
- [ ] 为 atomic/router/orchestrator/adapter 建立最小 Blueprint fixture 与负例。
- [ ] 实现只读 Blueprint inventory，不接入 apply。
- [ ] 运行 2.0 Phase 1 schema、migration、rollback 和敏感信息门禁。

## v1.0 Stable Contract Planned

- [ ] 冻结 CLI/API/JSON/contract schema 与兼容策略。
- [ ] 完成 wheel、安装 smoke、Python 支持矩阵和迁移文档。
- [ ] 固定 release evidence、独立评审、回滚和废弃周期。

- [x] 对比 NVIDIA SkillSpector，并固定可复核的上游 commit 与采用矩阵。
- [x] Doctor 增加 Python AST 动态执行、不安全 shell 和外部输入到执行 sink 检查。
- [x] Doctor/audit 增加 SARIF 2.1.0 输出，同时保持默认文本和 `--json` 兼容。
- [x] 通过独立候选和同一 maintenance plan 更新 Skill Guide Doctor 规则参考。
- [x] 完成 v0.1.1 pytest、Ruff、Skill validation、credential lint 和 diff check。

## v0.1.x Done / Baseline

- [x] 新需求先自查和逐步澄清,信息不足保持 `needs_discovery`。
- [x] 产物判断先于 Skill 架构和 Product/版本治理。
- [x] 完成 v0.1 Public Beta Spec 与 Plan。
- [x] 建立 Product、Constitution、Roadmap、Backlog、Sprint、ADR、Daily Log 和版本体系。
- [x] 创建必须使用同一预览计划 Apply。
- [x] 创建后结构验证，失败自动清理。
- [x] production 创建区分结构完成与发布证据完成。
- [x] 对齐“快速生成 + 从第一版工程化 + 全生命周期保持”的产品承诺并增加回归门禁。
- [x] Skill Guide 增加复杂/商业 Skill 工程治理路由。
- [x] 更新 README、贡献、安全和 CI。
- [x] 完整门禁与隔离 E2E。

## v0.1.0 Release Gate（历史）

- [x] pytest 全通过。
- [x] Ruff 全通过。
- [x] Skill Guide production Doctor 零 FAIL/WARN。
- [x] 凭证 lint 通过。
- [x] `git diff --check` 通过。
- [x] README、版本、Changelog、Roadmap、Task 和 Sprint 一致。
- [x] 用户确认真实仓库变更。
- [x] commit、push、tag 和公开发布已获得明确授权。

## v0.1.1 Security Doctor Gate

- [x] SkillSpector 对比证据固定到公开仓库 commit。
- [x] AST 安全规则、SARIF 输出和旧 CLI 兼容回归通过。
- [x] Skill Guide 同一 maintenance plan Apply、postflight、verify 通过。
- [x] pytest 110 passed。
- [x] Ruff、官方 Skill validation、production Doctor 100/A、凭证 lint、diff check 通过。
- [ ] 用户确认 commit、push、tag 或公开发布（本轮不请求，也不自动执行）。

## Done

- [x] 完成 Yao Meta Skill、Superpowers 和本地能力审计。
- [x] 明确 V1 核心是创建 + 防架构腐化维护 + 检查 + 自进化 + 友好交互。

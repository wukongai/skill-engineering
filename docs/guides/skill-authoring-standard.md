# Skill 创建标准

这份标准是 Agent Skill Hub 的 skill 创建规范。它在 Anthropic Agent Skills 官方格式底线上,增加 contract、回归用例和安装治理。

## 官方底线

- `SKILL.md` 必须存在。
- frontmatter 必须包含 `name` 和 `description`。
- `description` 是触发边界,必须写清什么时候使用。
- `SKILL.md` 保持轻薄;细节放 `references/`,确定性工作放 `scripts/`。
- `assets/` 只在确实有静态资源、模板、示例文件、媒体素材或可复用输出资产时创建。
- 官方格式不要求 `stages/` 或 `workflows/`;复杂 workflow 能在根入口保持轻薄时就不要拆。
- 需要 UI 元数据时使用 `agents/openai.yaml`,并保持它和 `SKILL.md` 一致。

## Agent Skill Hub 增强

复杂或生产级 skill 应该有:

- `skill.contract.yaml`:描述 inputs、outputs、stops、delegates、forbidden、state、approvals、scripts、tests。
- API-backed 或 credentialed provider skill 的 contract 还必须声明 `providers`:分类、credential source、凭证是否在 skill/repo 外、network allowlist、redaction、dry-run/apply 审批、security cases 和 revoke/rotate/delete 文档。
- production 或高风险 Skill 的 contract 还必须声明 `evaluation`:success/failure/high-risk cases、类型专属失败面、baseline、holdout、negative-transfer、behavioral results 和 independent review。普通 personal/team Skill 不强制完整证据包。
- `tests/skills/<skill-name>/cases/*.yaml`:记录回归场景。
- 确定性脚本:处理日期、路径、文件检查、manifest、dry-run/apply、timeout、retry、报告输出。
- 安装范围说明:global、project-only、profile-managed、direct/manual、plugin-backed 或 archived。

## 根 `SKILL.md`

保留:

- 触发和反触发边界。
- 工作流路由。
- 输入、输出、停止点。
- 稳定 delegates 和验证命令。

移出:

- 事故日志和复盘。
- 很长的例子和失败表格。
- 状态机。
- 硬编码用户路径。
- 子 skill 内部细节。
- 反复追加的 `CRITICAL` 修复说明。

## 完成标准

- 简单 skill:lint 通过,触发边界足够窄。
- 复杂 skill:contract 存在,并且和 `SKILL.md` 对齐。
- 有副作用 skill:dry-run/apply 和 approval state 明确。
- 已安装 skill:暴露范围有 profile 或安装决策支撑。
- 评测结论:静态分只称为 structural readiness;没有真实行为证据时 utility 必须标为 not-evaluated。

## 持续修改

创建完成不是生命周期终点。后续修改必须按 `skill-maintenance-standard.md` 执行:

- 先写失败模式、根因层级、预期行为和回归证据;
- 在独立候选目录修改,不得直接覆盖 source;
- 预览增删改和复杂度 delta;
- preflight 通过后应用同一 Plan ID;
- postflight 失败自动回滚;
- 成功修改保留记录,支持复验、历史和无漂移撤销。

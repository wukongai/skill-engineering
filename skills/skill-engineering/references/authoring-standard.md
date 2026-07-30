# Skill 撰写标准

这份标准在 Anthropic Agent Skills 官方格式底线上,增加 Agent Skill Hub 的工程治理要求。

## 官方底线

- `SKILL.md` 必须存在。
- frontmatter 必须包含 `name` 和 `description`。
- `description` 必须写清触发边界,因为 body 只有 skill 被选中后才加载。
- body 保持轻薄,使用渐进披露。
- 确定性资源放 `scripts/`,上下文资料放 `references/`。
- `assets/` 只在确实有静态资源、模板、示例文件、媒体素材或可复用输出资产时创建;不要为了凑官方可选目录而创建空目录。
- UI 需要展示名、短描述和默认 prompt 时,加 `agents/openai.yaml`。
- 官方格式不要求 `stages/` 或 `workflows/` 目录。复杂流程可以直接写在 `SKILL.md` 的 workflow/checklist 中;只有流程很长、跨多个阶段、且根入口会变厚时,才拆成内部 workflow step 文件。

## 完整候选生成(1.1 Native Authoring)

- 候选必须按 Authoring Brief 直接生成任务专属内容,不依赖官方 `skill-creator` 或其他宿主专用 Creator。
- 不得先把空骨架写入正式目标,再把补内容留给用户或下一次任务;候选一律先落隔离候选目录。
- 只有一个 `SKILL.md` 的 atomic Skill 也必须包含足以完成真实任务的专属规则、工作流和边界;简单不等于简陋。
- `SKILL.md` 不得残留“只说执行单一职责、没有任务细节”的通用 fallback 语句。
- 每个 references/scripts/assets/templates/tests 条目都必须有真实内容和明确读取或执行入口;不需要的目录不创建。
- 声明的脚本必须真实存在并通过运行测试;复杂工作流必须包含失败与部分成功处理。
- 完整候选通过门禁后使用 `scripts/native_plan.py preview` 固定脱敏 Brief、
  文件 manifest、candidate fingerprint、target preflight 和 portable 创建评审；
  用户确认后只能对同一 plan/candidate/target 执行 `apply`，写后用 `verify` 复验。
- Native Plan 的 hash 用于防止无意漂移和陈旧计划，不把能够修改并重算 hash 的
  受信宿主当作攻击者；candidate、Brief 外部输入和 target 现状仍按不受信数据检查。

## Agent Skill Hub 增强要求

复杂、生产级或有副作用的 skill 还应该有:

- `skill.contract.yaml`:描述 inputs、outputs、stops、delegates、forbidden、state、approvals、scripts、tests。
- API-backed 或 credentialed provider skill 的 contract 还必须声明 `providers`:分类、credential source、凭证是否在 skill/repo 外、network allowlist、redaction、dry-run/apply 审批、security cases 和 revoke/rotate/delete 文档。
- production 或高风险 Skill 的 contract 还必须声明 `evaluation`:success/failure/high-risk cases、类型专属检查、baseline、holdout、negative-transfer、behavioral results 和 independent review。普通 personal/team Skill 不强制完整证据包。
- `tests/skills/<skill-name>/cases/*.yaml`:固化不能回退的场景。
- 确定性脚本:处理日期、路径、文件检查、manifest、dry-run/apply、timeout、retry、报告输出。
- 明确安装范围:global、project-only、profile-managed、direct/manual、plugin-backed 或 archived。

## 根 `SKILL.md` 规则

根 `SKILL.md` 应该包含:

- 触发边界和反触发。
- 到 references 或内部 workflow step 的路由。
- 输入、输出和停止点。
- 稳定 delegates 和验证命令。

根 `SKILL.md` 不应该包含:

- 事故日志或复盘。
- 很长的失败表格。
- 硬编码用户绝对路径。
- 只靠自然语言描述的状态机。
- 子 skill 内部实现细节。
- 每次 bug 后追加的一堆 `CRITICAL` 规则。

## 复杂度阈值

- 简单 atomic skill:没有副作用时不强制 contract。
- orchestrator/router/workflow skill:强烈建议 contract。
- 生产级或外部副作用 skill:必须有 contract、dry-run/apply、approval state 和 regression cases。

## Workflow 拆分原则

- 不拆:少于 6-8 步、没有跨阶段状态、没有独立 review/approval、根 `SKILL.md` 能保持轻薄。
- 拆:流程有 discover/design/scaffold/doctor/install-audit/review 等明显阶段,每阶段有不同输入输出或停止点。
- 拆出来的内部步骤使用 `INSTRUCTIONS.md`,不要使用 `SKILL.md`,避免被 agent 当成顶层 skill 暴露。
- 目录名优先用业务能看懂的 `workflows/` 或在文档中解释清楚 `stages/` 是内部 workflow step,不是官方必需结构。

好的修复通常会让 `SKILL.md` 更短。

## 语义质量

- 编码具体 failure mechanism 和恢复动作,不要只写“注意异常”。
- 使用 actionable specificity:明确条件、输入输出、脚本、停止点,避免“视情况”“自行判断”。
- 为高风险动作建立 blacklist 与审批边界。
- 静态结构分只能说明 readiness;没有 rollout/baseline/holdout 时不要宣称下游效果已经验证。

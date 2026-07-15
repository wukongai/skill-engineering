# Skill A3 自进化标准

## 边界

A3 自动完成观察、提案、数据集、候选、评测、压缩推荐、不可变版本和 Shadow。Canary/Active 需要用户批准同一份 Release Plan;不得自动 Global。

核心不绑定模型供应商。Codex、Claude Code 等宿主 Agent 读取 CandidateJob,只修改隔离工作区中的 `source/`;Skill Hub 负责确定性状态、门禁、版本与发布。

## 证据与触发

- 只保存脱敏摘要、确定性 expected、privacy、failure tag、cost/latency 和 artifact pointer;拒绝凭证、敏感 expected 与完整会话。
- 三条同类 failure/partial/correction、单条 high-risk failure 或用户明确请求可形成 Proposal。
- 证据不足保持 observe,不得自动改源文件。
- success evidence 进入 protected behavior,用于检测 negative transfer。

## 数据集与候选隔离

- 只有包含确定性 expected 的证据可以成为 case。
- 同一 leakage group 只能处于 development 或 holdout 一侧;至少需要两个独立 group。
- CandidateJob 可包含 development evidence,但不得包含 baseline 评分结果、holdout case id 或 holdout assertions。
- 同时准备 minimal-patch、layer-move、compaction、resource-or-script 四类候选,防止只会在根 `SKILL.md` 追加规则。

## 评测与选择

按顺序执行 lint/Doctor/security、复杂度变化、同集 baseline/candidate 行为评测、holdout/high-risk/negative-transfer gate。真实 rollout 或可信 harness 负责产出 results;本版本不把 LLM 主观评分伪装成确定性结果。

以 utility delta、holdout、高风险、负迁移、入口行数、重复指令和文件数构成 fitness vector。选择 Pareto 非支配候选;并列时保留多个推荐,不制造总分。

## 版本与发布

1. 仅 recommended 候选可生成不可变 SkillVersion。
2. 生成版本后自动指向 Shadow,不改变真实 source/profile。
3. Canary 复用安装计划,只进入指定窄项目。
4. Active 复用维护计划更新 maintained source。
5. Canary/Active 必须先展示 Release Plan;批准、应用、验证、回滚都按记录执行。
6. version、channel、target 或 plan hash 漂移时废弃旧计划并重建。

## 结论措辞

自动评测通过只说明当前有哈希的 suite/results 达标。没有跨模型、长期 Shadow 或真实业务数据时,不得宣称 Skill 已普遍变强。

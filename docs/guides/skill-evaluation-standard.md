# Skill 评测证据标准

`skill-engineering doctor` 的 0-100 分是静态工程健康分,scope 为 `structural-readiness`,不是下游任务效用分。

## 阅读顺序

1. `FAIL`:安全、执行断裂或未经证据支持的效用宣称。
2. `score`:功能价值、稳定性、安全、工程化的静态 readiness。
3. `assessment.skill_type`:atomic/orchestrator/router/adapter/composite。
4. `assessment.coverage`:static、contract、regression、behavioral、holdout、independent review。
5. `assessment.utility_claim` 和 `limitations`。

## 证据规则

- `not-evaluated` 是未知,不是失败,不能按 0 分处理。
- `not-applicable` 不进入 coverage 分母。
- `evidence-declared` 只表示 contract 声明了 artifact,不表示 Doctor 已执行或验证。
- 没有 behavioral + baseline + holdout + negative-transfer 证据时,不得宣称 skill 效果已经验证。
- 横向比较时必须使用同一 profile、同一 case set 和同一证据层级。
- `skill-engineering evaluate` 对 baseline/candidate 结果执行确定性断言,分别报告 development、holdout、high-risk 和 negative transfer。
- 缺失 case 得到 `inconclusive`,不是 0 分;report hash 漂移或无法从输入重算时证据失效。
- 本版本不调用 LLM、不执行 suite 命令;LLM semantic reviewer 留到下一版本。

## 复杂 Skill 最小契约

- success、failure、high-risk case portfolio;
- 类型专属失败面;
- production 或高风险 Skill 额外要求 baseline、holdout、negative-transfer、behavioral results、independent review;普通 personal/team Skill 保持轻量。

详细标准与类型矩阵见 `../../skills/skill-guide/references/evaluation-standard.md`。

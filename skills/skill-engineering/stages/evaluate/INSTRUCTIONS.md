# Evaluate 阶段

用于评测单个 skill 或比较多个 skill,不把静态 plausibility 冒充真实 utility。

1. 读取[证据标准](../../references/evaluation-standard.md)、[边界确认与类型验收](../../references/boundary-confirmation.md)和[Doctor 标准](../../references/doctor-standard.md)。
2. 从 contract 判断 atomic/orchestrator/router/adapter/composite;没有 contract 时只做保守推断。
3. 运行 `skill-engineering doctor <path> --profile <profile> --json`。
4. 先看 FAIL gate,再看 structural score,最后看 assessment coverage。
5. 新创建或边界变化先按声明能力检查文本案例；空断言为 uncovered，非法结构为 failed，不把不适用记通过。复杂 skill 的真实证据另检查 success/failure/high-risk portfolio。
6. 对 production 或高风险 Skill 检查 baseline、holdout、negative-transfer、behavioral result 和 independent review;普通 team Skill 不强制完整证据包。
7. 已有 baseline/candidate 真实结果时,运行 `skill-engineering validate-eval-suite --suite <suite> --production`,再运行 `skill-engineering evaluate --suite <suite> --baseline-results <json> --candidate-results <json> --production`。
8. Suite 只允许确定性断言,不得包含或执行 command/script;LLM semantic reviewer 留给下一版本。
9. 缺失 case 必须得到 `inconclusive`,不能按 0 分;baseline pass/candidate fail 必须列为 negative transfer。
10. 候选文本结果保留 `evidence_kind=candidate_text`、`utility_claim=false`；未运行真实任务时，真实效果结论为 `not-evaluated`。比较多个 Skill 使用同一 profile、case set 和证据层级，不将字符串通过升级为真实多轮或业务通过。

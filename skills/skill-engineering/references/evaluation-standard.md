# Skill 评测与证据标准

## 核心原则

Skill 的“写得像不像”与“是否真的提升下游任务”是两个问题。Doctor 的 0-100 分是静态工程健康分,不能冒充 utility score。

报告必须同时展示:

- hard gate:`OK` / `WARN` / `FAIL`;
- structural score:功能、稳定、安全、工程化;
- evidence coverage:static、contract、regression、behavioral、holdout、independent review;
- utility claim:`not-evaluated` 或 `evidence-declared`;
- limitations:当前还不能证明什么。

## 证据状态

| 状态 | 含义 | 计分方式 |
|---|---|---|
| `evaluated` | 当前 Doctor 实际运行了检查。 | 计入 coverage。 |
| `evidence-declared` | contract 指向证据 artifact,但 Doctor 未执行该 artifact。 | 计入 readiness coverage,不等于通过。 |
| `not-evaluated` | 没有证据或未运行。 | 不能当成 0 分,也不能宣称通过。 |
| `not-applicable` | 对当前 skill type 不适用。 | 不进入 coverage 分母。 |
| `fail` | 有可执行验收且结果失败。 | 由稳定 rule/gate 单独处理。 |

## Skill 类型

| Type | 专属失败面 |
|---|---|
| atomic | inputs、outputs、成功/失败 case。 |
| orchestrator | cross-stage IO、partial failure、aggregation。 |
| router | positive/negative routing、fallback。 |
| adapter | provider binding、portability、error mapping。 |
| composite | tool index、orthogonality、selection rules、output consistency。 |

不要因为目录里出现一个子 `SKILL.md` 就武断认定 pipeline。优先使用 `skill.contract.yaml.kind`,再结合 root 路由语义和子 skill 关系。

## 最小 Case Portfolio

复杂或生产 skill 至少声明:

1. success case:正常路径是否完成。
2. failure case:已知失败机制是否被编码并有明确恢复动作。
3. high-risk case:危险操作、凭证、外联、不可逆副作用是否被拒绝或审批。

production 或高风险 Skill 还需要 baseline、held-out cases、negative-transfer rejection gate、behavioral result artifact 和 independent reviewer。普通 personal/team Skill 保持轻量。

## 三项语义质量标准

来自 Microsoft SkillLens 的实证结论应进入设计和评审:

- Failure mechanism encoding:写出具体失败机制和对应恢复动作,不是泛泛“注意错误”。
- Actionable specificity:使用可执行条件、路径、命令、输入输出,避免“视情况”“酌情处理”。
- High-risk action blacklist:明确哪些动作不能自动执行,以及何时必须停止并请求批准。

这三项可作为语义评审 rubric,但单独的 LLM judge 仍不能证明真实 utility。

## 独立性与防伪

- 编辑 skill 的 agent 不应该是唯一评审者。
- hash/certificate 只能证明 artifact 未变化,不能证明模型身份或任务增益。
- 没有真实 rollout、baseline 和 holdout 时,报告只能说“结构 readiness”,不能说“效果优秀”或“全面评测完成”。
- LLM 结果不得覆盖确定性 rule;rule 也不得把未评 LLM 维度按失败处理。

## 推荐流程

1. 识别 skill type 和 governance profile。
2. 跑静态 lint/doctor,先处理 hard gate。
3. 检查 contract 和 case portfolio。
4. 对类型专属失败面补 fixture。
5. 运行 baseline 与候选 skill 对比。
6. 用 holdout 检查负迁移。
7. 让独立 reviewer 审核语义证据。
8. 报告 score、coverage、confidence、utility claim 和 limitations。

## 确定性行为证据执行器

本版本使用 `skill-engineering evaluate` 比较同一 suite 的 baseline/candidate 真实结果,不调用 LLM,也不执行 suite 中的命令。

- suite 定义 `development|holdout`、`success|failure|high_risk` 和确定性断言;
- result artifact 由真实 Agent rollout、可信 harness 或确定性测试工具产生;
- 支持 status、contains、not-contains、regex、JSON path equals;
- 缺失结果是 `not_evaluated`,整体为 `inconclusive`,不是 0 分;
- baseline pass 而 candidate fail 是 negative transfer;
- `accept` 只表示在当前有哈希 suite/results 上通过,不表示跨模型通用 utility;
- report 的 suite/results hash 必须可重算;hash 漂移或 report 内容被篡改时证据失效。

生产评测先运行:

```bash
skill-engineering validate-eval-suite --suite tests/evaluation/suite.yaml --production
skill-engineering evaluate \
  --suite tests/evaluation/suite.yaml \
  --baseline-results artifacts/baseline.json \
  --candidate-results artifacts/candidate.json \
  --production
```

LLM semantic reviewer、模型身份和语义 rubric adapter 属于下一版本;即使未来加入,也不得覆盖确定性 hard gate。

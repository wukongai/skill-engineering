# Skill 质量评分标准

Doctor v2 的评分用于回答静态工程问题:触发边界是否清楚、结构是否稳定、安全和维护准备是否足够。它不直接回答真实任务效果。

评分 scope 固定为 `structural-readiness`。必须与 assessment coverage、confidence、utility claim 一起阅读;未知证据不能按 0 分处理。

## 总分

- `A / excellent`:90-100,可以共享或安装。
- `B / healthy`:80-89,整体健康,只需小幅收敛。
- `C / review-needed`:70-79,可用,但共享或全局安装前要 review。
- `D / rework-needed`:60-69,有明显返工点。
- `F / blocked`:0-59,不建议安装或共享。

## 三个维度

| 维度 | 权重 | 看什么 |
|---|---:|---|
| 功能价值 | 20 | description 是否能一眼判断触发、是否单一职责、是否有输入输出和停止边界、是否避免宽泛或重复触发。 |
| 稳定性 | 25 | dry-run/apply、approval、state、scripts、timeout/log、regression coverage、确定性步骤是否交给脚本。 |
| 安全 | 25 | prompt injection、凭证/环境读取、外联传输、数据外传组合风险是否被识别,合法 API 调用是否由 credentialed provider contract 管住。 |
| 工程化 | 30 | 渐进披露、根 `SKILL.md` 是否轻薄、references/scripts/internal workflow steps/contract 是否分层、安装边界是否清楚。 |

## 评分原则

- 稳定 rule id 是扣分主来源,评分不替代 `OK/WARN/FAIL`。
- `FAIL` 比 `WARN` 扣得更多。
- 低分建议优先来自 issue hint,方便直接修。
- 功能价值不做商业市场判断,只判断 agent 能不能正确触发、执行和复用。
- 命中 `SEC` 规则时,先完成安全 review,不要只看总分是否达标。
- `utility_claim=not-evaluated` 时,不得把总分称为效果分或全面评测结果。

## 使用建议

- 个人实验 skill:低于 70 也可保留本地,但不要全局安装。
- 团队共享 skill:建议至少 80,且无 `FAIL`。
- 商业或付费 workflow:建议至少 90,且 contract、approval、state、regression coverage 都明确。

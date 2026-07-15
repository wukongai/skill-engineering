# 质量评分标准

Doctor v2 把规则结果折成一个 0-100 分,用于安装和 review 前的快速判断。

这个分数的 scope 是 `structural-readiness`,不衡量真实任务增益。跨 skill 比较前必须同时看 assessment coverage;coverage 不同的分数不能直接排名。

## 维度

| 维度 | 权重 | 标准 |
|---|---:|---|
| 功能价值 | 20 | 触发边界清楚、职责单一、输入输出和停止点可验证、避免宽泛或重复触发。 |
| 稳定性 | 25 | 有 dry-run/apply、approval、state、scripts、timeout/log、regression coverage。 |
| 安全 | 25 | 能识别 prompt injection、凭证/环境读取、外联传输、数据外传组合风险,并用 credentialed provider contract 管住合法 API 调用。 |
| 工程化 | 30 | 根入口轻薄,细节放 references/scripts/tests,contract 和安装边界清楚。 |

## 等级

- A:90-100,可共享或安装。
- B:80-89,整体健康。
- C:70-79,需要 review。
- D:60-69,需要返工。
- F:0-59,先修复再安装。

## 使用

1. 先看 `FAIL`,它们决定退出码。
2. 再看最低分维度,决定修复方向。
3. 低分建议优先按 `score.recommendations` 执行。
4. 不要把评分当成市场价值判断;它只衡量 agent 触发、稳定执行和维护质量。
5. 命中 `SEC` 规则时,即使总分没有跌到 F,也必须先完成安全 review 再安装或共享。
6. `utility_claim=not-evaluated` 时,禁止把分数描述成效果分、业务价值分或全面评测结果。

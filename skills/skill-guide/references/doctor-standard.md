# Doctor 标准

Doctor 报告必须确定、可 review,并且跨 agent 稳定。

## 级别

| 级别 | 含义 | 退出码 |
|---|---|---|
| OK | 不需要动作。 | 0 |
| WARN | review 风险、路由污染、可维护性问题,或与 profile 严格度相关的问题。 | 默认 0 |
| FAIL | 安装断裂、不安全副作用、skill 结构无效,或高概率执行错误。 | 1 |

## 治理档位

| Profile | 适用场景 | 默认严格度 |
|---|---|---|
| personal | 个人开发和实验。 | 除安全或执行断裂外,尽量 WARN。 |
| team | 团队共享 repo 和复用 skill。 | 复杂副作用 workflow 缺 contract 时 FAIL。 |
| production | 生产或高影响流程。 | 安全、副作用、影响确定性的 prompt debt、缺回归覆盖时 FAIL。 |

## 规则形状

每条规则需要:

- 稳定 `rule_id`。
- 按 profile 可调整的级别。
- 目标路径和可选行号。
- 简洁 message。
- 修复 hint。
- 可行时提供 fixture 或 regression case。

## 检查层

- Static: frontmatter、description、根入口长度、硬编码路径、prompt debt 词。
- Structure: references、scripts、assets、stages、agents metadata、contract。
- Behavior-risk: dry-run/apply、approval state、隐式日期 fallback、timeout/logging。
- Security: prompt-injection 型指令、凭证/环境读取、外联传输、数据外传组合风险。
- Install: global/project/profile/direct/plugin/archive 分类。
- Governance: 重复宽泛触发、陈旧入口、regression cases、suppression。
- Evaluation: skill type、case portfolio、baseline/holdout、negative transfer、独立评审和证据 coverage。

## 安全规则

| Rule | 层级 | 含义 | 默认处理 |
|---|---|---|---|
| `SEC101` | Security | `scripts/` 中出现外联网络传输能力,但缺少 contract allowlist、命中非 allowlist host,或上传/创建类请求缺 dry-run/apply 审批边界。 | personal WARN, team/production FAIL。 |
| `SEC102` | Security | `scripts/` 中读取环境变量、`.env`、token、secret、password、keychain 等凭证形态,但缺少受管理的 credentialed provider contract。 | personal WARN, team/production FAIL。 |
| `SEC103` | Security | `SKILL.md`、`references/` 或 `stages/` 中出现上级指令覆盖类攻击、隐藏行为、敏感信息外泄等 prompt-injection 型指令。 | personal WARN, team/production FAIL。 |
| `SEC104` | Security | 同一脚本同时命中凭证读取和网络传输,但 skill 没有声明 credentialed provider contract。 | FAIL。 |
| `SEC105` | Security | skill 目录、docs、examples、tests 或 logs 中出现真实 secret-like 字面量。 | FAIL。 |
| `SEC106` | Security | credentialed provider 缺少 security regression 覆盖:missing credentials、redaction、blocked non-allowlisted host、no secret JSON output。 | personal/team WARN, production FAIL。 |
| `SEC107` | Security | credentialed provider 缺少 revoke/rotate/delete credentials 安装文档。 | personal/team WARN, production FAIL。 |

credentialed provider contract 允许四类合规来源:

- `personal_local_byok`:个人本机 BYOK,凭证必须在 repo 和 skill 目录外,输出脱敏。
- `open_source_byok`:开源 BYOK,只能提供 config template,真实凭证不进入安装目录。
- `mcp_plugin_runtime`:优先让 MCP/plugin runtime 封装凭证,agent 只拿结构化结果。
- `commercial_saas`:优先 OAuth、官方授权流或 server-side secret manager。

命中安全规则时,不要只在 `SKILL.md` 里追加“不要做坏事”。优先拆清楚脚本职责、允许的网络目的地、凭证边界、redaction、dry-run/apply 和 regression cases。

## 评测规则

| Rule | 含义 | 默认处理 |
|---|---|---|
| `EVAL101` | production 或高风险复杂 Skill 缺 evaluation evidence contract。 | personal/team 高风险 WARN,production FAIL;普通 personal/team 不强制。 |
| `EVAL102` | 已声明的 case portfolio 缺 success/failure/high-risk。 | personal/team WARN,production FAIL。 |
| `EVAL103` | production 缺 baseline/holdout/negative-transfer gate。 | FAIL。 |
| `EVAL104` | 已声明的评测缺 Skill type 专属失败面检查。 | personal/team WARN,production FAIL。 |
| `EVAL105` | 没有 behavioral baseline + holdout 却宣称 utility。 | personal WARN,team/production FAIL。 |
| `EVAL106` | 有效的确定性行为 report 拒绝 candidate。 | personal WARN,team/production FAIL。 |
| `EVAL107` | 行为 report inconclusive、schema 无效、输入缺失、hash 漂移或重算不一致。 | personal/team WARN,production FAIL。 |

Doctor 输出的 score 是 `structural-readiness`,不是 downstream utility。报告还必须给出 assessment coverage、confidence、utility claim 和 limitations。未知证据是 `not-evaluated`,不能按 fail 或 0 分处理。

## 评分

Doctor 报告还必须给出 0-100 质量评分。评分是 review 和安装治理信号,不替代 `OK` / `WARN` / `FAIL`。

- 功能价值 20%:触发边界、单一职责、输入输出、停止点和反触发。
- 稳定性 25%:dry-run/apply、approval、state、scripts、timeout/log、regression coverage。
- 安全 25%:prompt injection、凭证/环境读取、外联传输、数据外传组合风险和高风险副作用。
- 工程化 30%:渐进披露、根入口长度、references/scripts/internal workflow steps/contract 分层、安装边界。

低于 80 分时,报告应给出优先修复建议。详细标准见 `references/quality-score-standard.md`。

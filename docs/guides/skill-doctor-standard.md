# Skill Doctor 标准

Doctor v2 通过稳定、可 review 的规则检查 skill 和安装暴露。

## 级别

| 级别 | 含义 | 退出码 |
|---|---|---|
| OK | 不需要动作。 | 0 |
| WARN | review 风险、路由成本、可维护性问题或 profile 相关问题。 | 0 |
| FAIL | 结构断裂、不安全副作用、安装无效或高概率执行失败。 | 1 |

## Profile

| Profile | 用途 | 行为 |
|---|---|---|
| personal | 个人工作和实验。 | 大多数可维护性问题只 WARN。 |
| team | 团队共享 skill。 | 不安全副作用和复杂 workflow 缺 contract 时 FAIL。 |
| production | 生产或高影响 workflow。 | 确定性、副作用、contract 和回归风险更容易 FAIL。 |

## 规则要求

每条规则必须有:

- 稳定 id。
- 检查层级。
- 需要时按 profile 调整级别。
- 路径和可选行号。
- 简短 message。
- 修复 hint。
- 可行时提供 fixture 或 regression case。

## 检查层

- Static: frontmatter、name、description、根入口长度、硬编码路径、prompt debt。
- Structure: references、scripts、assets、stages、agents metadata、contract。
- Behavior-risk: dry-run/apply、approval state、隐式日期 fallback、timeout/logging。
- Security: prompt-injection 型指令、凭证/环境读取、外联传输、数据外传组合风险、Python AST 动态执行和外部输入到执行 sink。
- Install: global/project/profile/direct/plugin/archive 分类。
- Governance: 重复触发、陈旧入口、回归覆盖、suppression 策略。

## 安全规则

| Rule | 检查内容 | 典型风险 |
|---|---|---|
| `SEC101` | 脚本外联,但 contract 没有 allowlist、命中非 allowlist host,或上传/创建类请求缺 dry-run/apply 审批边界。 | 未审计下载、上传、远程创建或越界 host。 |
| `SEC102` | 脚本读取 `.env`、环境变量、token、secret、password、keychain 等,但没有受管理的 credentialed provider contract。 | 凭证窃取或凭证被写入日志。 |
| `SEC103` | 指令文本包含上级指令覆盖类攻击、隐藏行为、敏感信息外泄等内容。 | prompt injection 或恶意工作流。 |
| `SEC104` | 同一脚本同时读取凭证并外联传输,但没有 provider contract。 | 数据外传。 |
| `SEC105` | skill 目录、docs、examples、tests 或 logs 中出现真实 secret-like 字面量。 | 凭证泄露。 |
| `SEC106` | credentialed provider 缺少 missing credentials、redaction、blocked non-allowlisted host、no secret JSON output 回归覆盖。 | 脱敏或越界 host 回归。 |
| `SEC107` | credentialed provider 缺少 revoke/rotate/delete credentials 安装文档。 | 用户无法收回或轮换凭证。 |
| `SEC108` | Python 脚本调用 `exec` 或 `eval` 动态执行代码。 | 任意代码执行。 |
| `SEC109` | Python 脚本用非静态值调用 `compile`、`__import__` 或 `importlib.import_module`。 | 动态加载未批准代码；personal/team WARN，production FAIL。 |
| `SEC110` | Python 脚本调用 `os.system`、`os.popen`，或 `subprocess` 配合 `shell=True`。 | shell 注入或命令边界绕过。 |
| `SEC111` | 用户输入、环境变量、网络输入或文件内容流入代码/命令执行 sink。 | 外部输入驱动任意代码或命令执行。 |

合法的 credentialed provider 必须在 `skill.contract.yaml` 声明 provider 分类、credential source、凭证在 skill/repo 外、network allowlist、redaction、dry-run/apply 审批、security cases 和凭证生命周期文档。

## 评分输出

Doctor v2 同时输出 0-100 分,用于创建、安装和 review 前的 triage:

- 功能价值 20%。
- 稳定性 25%。
- 安全 25%。
- 工程化 30%。

评分不替代 `OK/WARN/FAIL`;退出码仍只由 `FAIL` 决定。详细标准见 `skill-quality-score-standard.md`。

Doctor 还输出 evidence-aware assessment:skill type、评测方法、score scope、coverage、confidence、utility claim 和 limitations。`EVAL101-105` 分别检查 production/high-risk evaluation contract、case portfolio、production utility gates、类型专属失败面和未经证据支持的 utility claim。普通 personal/team Skill 不强制完整证据包。

显式引用 `behavioral_results.report` 时,Doctor 还会重算 suite/results 证据:`EVAL106` 表示确定性行为 report 拒绝 candidate;`EVAL107` 表示 report inconclusive、schema 无效、输入/hash 漂移或重算不一致。

## 输出格式

- 默认 `text` 只展示普通用户需要的结果、影响和下一步。
- `--json` 与 `--format json` 输出相同的完整 Doctor 记录。
- `--format sarif` 输出 SARIF 2.1.0；`FAIL` 映射为 `error`，`WARN` 映射为 `warning`，并保留 rule id、文件、行号、layer 和 profile。

三种格式必须来自同一个 `DoctorResult`，不得在报告层重新判断安全结果。

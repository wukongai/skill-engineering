# 安装治理

skill 本身写得好只解决一半问题。另一个关键是:它在哪里被暴露、是否值得一直参与路由、会不会拖慢 agent 判断。

## 暴露通道

| 通道 | 含义 | 治理问题 |
|---|---|---|
| Global | 用户级、多个项目默认可见的 skill 目录。 | 大多数项目真的都需要它吗? |
| Project | 某个项目里的 `.agents/skills` 或 `.claude/skills`。 | 这个项目真的需要它吗? |
| Profile-managed | 由 `registry.yaml` + `profiles/*.yaml` 创建的 symlink。 | profile 是否够窄、可复现? |
| Direct/manual | 不在 Agent Skill Hub 台账里的手动安装。 | 应该登记,还是移除/归档? |
| Plugin/runtime | agent plugin 暴露 skills、MCP/tools、apps 或 provider runtime。 | inventory 是否清楚,成本是否值得? |
| Archive/experiment | 旧 skill 或实验 skill,不应参与正常路由。 | 是否已经从顶层发现路径隐藏? |

## 效率信号

以下情况需要 WARN:

- global skill 太多,始终参与路由。
- description 过宽、重复或重叠。
- 多个入口指向同一个 workflow。
- plugin inventory 暴露了意料之外的额外 skill。
- 内部 stages 被安装成顶层 skill。
- 项目 profile 含有无关领域 skill。
- 新旧入口同时指向同一流程。

## 安装 review 问题

1. 这个 skill 为什么在这个项目可见?
2. 是哪个 profile 或 direct install 让它可见?
3. 它是否从 registry 已知 source symlink 过来?
4. plugin 是否已经提供了同等能力?
5. project-only 暴露是否足够?
6. 实验 skill 是否应该归档?

## 安全 review 问题

安装第三方 skill 前,必须额外看:

1. `SKILL.md` 或引用文件里是否出现上级指令覆盖类攻击、隐藏行为、敏感信息外泄等 prompt-injection 型指令?
2. `scripts/` 是否读取 `.env`、环境变量、token、secret、password、keychain?
3. `scripts/` 是否通过 `curl`、`wget`、`requests/httpx`、`scp/rsync/nc`、云存储 CLI 等进行外联传输?
4. 同一脚本是否同时读取凭证并外联上传?如果是,必须有 credentialed provider contract。
5. provider contract 是否声明分类、credential source、凭证在 skill/repo 外、network allowlist、redaction、dry-run/apply 审批和 security cases?
6. 外联目的地是否全部命中 allowlist?非 allowlist host 是否会在脚本里被阻断?
7. 安装文档是否说明 revoke、rotate、delete credentials?
8. 凭证更适合 MCP/plugin runtime 封装时,是否已经避免把它伪装成普通目录型 skill?
9. Python 脚本是否包含 `exec`/`eval`、动态 import、`os.system`、`shell=True`,或外部输入流向执行 sink?
10. 安装前是否已经在一次性项目里跑过 Doctor,并按需保存 JSON 或 SARIF 审计结果?

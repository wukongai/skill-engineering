# Skill 边界确认与防跑偏只读审查记录

本文件记录实施前及恢复时的历史审查；当前已实现状态与源码交付见[最新验证记录](2026-10-29-skill-boundary-confirmation.md)。

状态：现状审查与规划参考；未实现改进，未验证新增能力。

[文档入口](../README.md) · [需求草案](../specs/2026-10-29-skill-boundary-confirmation-spec.md) · [阶段规划](../plans/2026-10-29-skill-boundary-confirmation-plan.md) · [恢复交接](../handoffs/2026-10-29-skill-boundary-confirmation-next.md)

## 审查范围和基线

本会话在前置架构保护实施前只读审查本机当前 Skill。`.codex` 与 `.agents` 的已安装 Skill 入口均指向本仓库的 `skills/skill-engineering`，所以结论针对本机工作区，不外推远程正式版本。

审查包含 [Brief 就绪判定](../../src/skill_engineering/authoring.py)、[portable Native Plan](../../skills/skill-engineering/scripts/native_plan.py)、[行为断言器](../../src/skill_engineering/behavior.py)、[创建评审](../../skills/skill-engineering/scripts/creation_review.py)、[Doctor](../../src/skill_engineering/skill_doctor.py)和[私董会场景](../../skills/skill-engineering/tests/business-agent-boundary-cases.yaml)。

原工作区带有用户未提交修改，未重置或覆盖。前置会话后续会改变相关文件；恢复时必须重新核对，不把这份记录当届时现状。

## 已观察事实

- 创建 Brief/Native Plan 要求 mission、owned/excluded capabilities、偏题信号、停止条件、验收与行为案例等非空。
- Boundary Contract 列出 redirect_strategy/allowed_context，但需求表和当前必填判定允许缺省；定向探针仅保留一个成功案例且缺少纠偏策略，仍能生成预览。
- 核心与 portable 对 `assertions={}` 的案例都可返回 passed；当前无五类分类覆盖的硬检查。
- portable 创建评审会提示缺少反触发，但探针仍为 pass、98 分；旧 Skill 的通用 Doctor 探针可为 100/A 且无问题项。
- 私董会五个 fixture 的 pytest 只检查身份和字段非空，不执行真实模型回答。

## 会话早前已实际运行的检查

以下是本会话审查阶段的历史执行结果，不是本次文档写入后重新运行，也不是待开发能力的验收：

| 检查 | 结果 |
|---|---|
| 全量 `python3 -m pytest -q` | 316 passed，4.43 秒 |
| Ruff `python3 -m ruff check src tests` | 通过 |
| 官方 quick_validate Skill 校验 | Skill is valid |
| `bash scripts/credential-lint.sh --all` | 通过 |
| `git diff --check` | 通过 |
| 本地 production Doctor | 100/A；仅结构就绪度 |
| 独立只读代理的 8 文件定向测试 | 74 passed，3.15 秒 |

主代理还直接复核：给现有候选一个 given/expect/must_not 非空但 assertions 为空对象的案例，结果 `status=passed,total=1,passed=1,failed=0,uncovered=0`；把五个私董会场景直接交给核心断言器，结果 `status=uncovered,total=5,passed=0,failed=0,uncovered=5`。

## 证据限制与恢复复验

测试全绿说明当时已有回归通过，不代表上述缺口已被覆盖。字符串断言只检查候选文本，不证明真实多轮纠偏或及时结束。空断言通过和缺失覆盖属于这次审查发现，尚未修复。

前置完成后复核相关实现，再按[阶段规划](../plans/2026-10-29-skill-boundary-confirmation-plan.md)准备实际有效的断言、适用性和真实任务证据。本次文档同步的读回/链接/OB 校验结果保存在同步回执中，不能拿历史测试冒充本轮新执行。

## 本次规划同步回执

2026-10-29，当前会话只执行规划和文档同步，没有实现新增能力。

- 项目 4 份新文档以及 Backlog、Task、文档入口、当日工程日志的 4 处追加已应用并读回；没有覆盖前置会话原有内容。
- OB 新建“2026-10-29-【Skill Engineering】边界确认与防跑偏”任务卡，保持 block；按现行 7.2 生成当日日志，未填写复盘、评分或策略事实。
- 独立内容审阅通过；76 处新增文件/章节/本机 OB 来源链接静态核对通过。
- 本次新执行：pytest 316 passed（4.86 秒）、Ruff、Skill validation、凭证 lint 与 diff check 均通过；这些检查不证明待开发能力的真实效用。
- OB 单卡日期/字段校验通过，0 错误、0 警告；2026-10-29 workflow 校验通过，仅提示没有活动 rules 目录，使用共享 Skills 验证。
- 跨 Agent 入口检查共核对 25 项，未通过：Hermes 的 obpm 薄入口内容漂移，位置为 `~/.hermes/skills/note-taking/obpm/SKILL.md`。该文件不在本轮写入清单；未顺带删改其会话沉淀或修改环境规则。需要独立核对 canonical 入口后再处理，不能宣称全部跨 Agent 入口一致。
- Obsidian CLI 未连接应用；相对文件和章节已静态核对，但应用内点击、Dataview 渲染尚未验证。

因此，文档与 OB 内容已落地；收尾校验仍有跨 Agent 环境缺口，记录为 partial，不把文件写入包装成全部检查成功。业务实施继续等待前置会话本轮完成，与本次规划保存是否成功分别记录。

预览、外部备份和写入回执位于本机 `/private/tmp/skill-boundary-docs-20261029-f97cf9be/`；该临时目录仅用于本次写入核对与恢复，长期上下文以本需求、阶段规划、Handoff 和 OB 卡为准。

## 架构保护完成后的复查

2026-10-29 用户明确恢复任务。前置最终交付及当前 Skill 已重新读取，三项前置均完成：内部架构审查、CLI 强制审查、自然语言激活。

- 本次新执行全量 pytest：449 passed，4.88 秒。
- 独立只读复查 authoring/native plan/behavior：18 passed，0.69 秒；维护历史/无效冻结快照定向：18 passed、23 deselected，0.23 秒。
- AuthoringBrief 仍无专用确认事实；缺纠偏策略且仅一个无类别成功案例仍可 Preview。
- 空 assertions 对核心和 portable 仍可 passed；不存在场景适用性覆盖门禁。
- 空 excluded_capabilities 仍被判缺失，不能以单写 confirmed 状态表达用户确认无额外排除。
- 新维护写入必须复用 architecture_review，新增边界事实应作为 preflight 的并列部分；其严格 schema 不接受附加未知字段。
- [当前兼容决定](../adr/0011-mandatory-maintenance-architecture-review.md#决定)允许已经架构审查通过的有效旧计划继续 Apply。若新增边界门要收紧此策略，必须先有明确 ADR，历史读取、Verify 和 Undo 仍保持。

本次仅完成恢复复查及状态更新，新增能力未实现，未运行其真实任务验收。后续基于[阶段规划](../plans/2026-10-29-skill-boundary-confirmation-plan.md#任务五评审应用验证与ob)细化。

### 恢复状态同步校验

项目 8 份状态/证据文档和 OB 原卡已按同一预览局部更新并读回；9 个实际文件、77 处相关链接/章节核对通过。OB status 为 doing，2026-10-29 只有一条 Doing 执行行，归属、分组、排期历史与完成标记保持。

本次 Ruff、Skill validation、凭证 lint、diff check、OB 单卡与当日日志校验均通过。跨 Agent 入口重新核对 25 项全部通过，原 Hermes 薄入口漂移本次未复现；不据此冒称应用内点击或真实功能行为已验证。Obsidian CLI 和应用未能连接，本次使用已备份、指纹绑定的小范围 Edit 补丁完成任务卡状态修改。

本轮没有修改产品实现，业务范围问题仍待答复；当前状态为进行中（范围确认与实施准备），不再保留前置会话阻塞。

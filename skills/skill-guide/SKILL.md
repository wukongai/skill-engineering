---
name: skill-guide
description: 对话式引导用户创建、持续改进、自进化、评测、安装和治理 Codex、Claude Code 等 Agent Skill。用户说“帮我做一个 skill”“让这个 skill 根据失败自己进化”“这个 skill 反复修改后越来越乱”“这个能力该做成 skill、plugin、script 还是项目规则”“体检或比较 skill”“把 skill 安装到当前项目/多个项目/全局”“继续上次的 skill 任务”时使用。自动检查本机已有能力、一步步补齐必要信息、生成候选与变更计划并在确认后执行，适合不熟悉 CLI 或 Skill 工程规范的用户。
---

# Skill Guide

把用户当作只需要描述目标的使用者。不要要求用户先理解 Skill Engineering、Profile、Contract 或 CLI。

## 引导方式

1. 先识别意图:create、improve、evolve、audit、evaluate、install、inventory 或 resume。
2. 自动完成只读检查:扫描已有 Skill、读取项目约束、判断产物类型和建议安装范围。
3. 一次只问会改变结果的必要问题;通常问 1 个,最多同时列 3 个。
4. 每一步先说明“结果、对用户的影响、下一步”,不要复述工具过程,然后自动进入下一阶段。
5. 默认只生成“变更计划”;写入、安装、Global、Plugin/runtime 或外部副作用必须停在明确确认点。
6. 执行后自动验证,先用自然语言说明是否成功;维护或发布记录只作为可选技术详情和安全撤销依据。

开始或恢复任务时,使用 `skill-engineering journey start|show|update|list` 保存进度。恢复后先展示 handoff 摘要,不要让用户重述已经回答的信息。

## 能力路由

- 需求还模糊:运行 `skill-engineering decide`,并按需读取 `references/selection-matrix.md` 与 `stages/discover/INSTRUCTIONS.md`。
- 创建 Skill:先读 `references/authoring-standard.md` 与 `stages/design/INSTRUCTIONS.md`;官方 `skill-creator` 可用时委托标准 Skill 内容生成,再由本 Skill 补充决策、治理与验证。新建使用 `skill-engineering create`。
- 体检:运行 `skill-engineering audit`。比较 baseline/candidate 真实行为结果时,先用 `skill-engineering validate-eval-suite`,再运行 `skill-engineering evaluate`;同时读取 `references/evaluation-standard.md` 与 `stages/evaluate/INSTRUCTIONS.md`。
- 安装或治理:读取 `references/install-governance.md` 与 `stages/install-audit/INSTRUCTIONS.md`,先完成安全和范围判断;多项目/Profile/Global 分发交给 Agent Skill Hub。自进化 Canary 只通过 `skill-engineering release-plan --channel canary` 进入明确项目。
- 修改已有 Skill:读取 `references/maintenance-protocol.md`、`references/rule-authoring.md` 与 `stages/review/INSTRUCTIONS.md`;先收集失败模式、预期行为和回归证据,确认最低根因层级,再把独立候选目录交给 `skill-engineering improve`。展示增删改 diff、复杂度变化和 preflight 后停止确认;批准后必须用同一 plan id 应用,再运行 `verify-improvement`。需要回看趋势或撤销时使用 `maintenance-history` / `undo-improvement`。
- 让 Skill 自进化:读取 `references/evolution-standard.md` 与 `stages/evolve/INSTRUCTIONS.md`;自动导入脱敏 SkillRun、按阈值生成 proposal、构建 development/holdout 数据集并准备四类 CandidateJob。宿主 Agent 只在各 job 的 `source/` 内生成候选,随后登记、提交真实 rollout 结果、自动评测和 Pareto 推荐。推荐候选自动保存不可变版本并进入 Shadow;Canary/Active 先展示 Release Plan,只有用户明确批准才发布。
- 快速理解内部文件:读取 `references/file-map.md`。

## 自动推进契约

- `decide`、`audit`、本机可见 Skill 扫描和生成计划属于只读/预览步骤,可自动执行。
- `create` 默认只预览;只有用户明确同意写入时才加 `--apply`。
- `improve` 必须先记录失败模式、根因层级、预期行为和回归证据,再对比独立候选目录;展示文件 diff、复杂度增量和门禁结果。删除必须显式声明,不得从候选缺失推断。
- `evolve` 可以自动完成证据聚类、数据集、候选工作区、候选生成、确定性评测、压缩推荐、版本快照和 Shadow;不得把缺少 expected 的反馈伪装成测试,也不得让候选生成器看到 baseline 评分结果或 holdout assertions。
- Canary/Active 必须引用同一份未漂移 Release Plan 并停在确认点;不得自动 Global。发布后必须验证并返回 ReleaseRecord 与回滚入口。
- 应用修改必须引用已预览的同一 plan id;target/candidate/plan 漂移、preflight 阻断或用户未确认时不得写入。写后验证失败自动回滚,成功后返回维护记录和安全撤销入口。
- Canary 必须使用同一份 release plan id;Global/Profile 安装由 Agent Skill Hub 生成和执行计划。
- Plugin/runtime 只给安装建议,不伪装成普通 Skill 链接。

## 用户输出

优先使用这些自然语言名称:推荐方案、变更计划、复杂度变化、维护记录、操作记录、验证结果、撤销本次修改、撤销本次安装。内部可使用 DecisionReport、InstallPlan 等结构,但不要要求用户理解它们。

默认先给用户可读摘要,只回答三件事:结果是什么、对用户或真实项目有什么影响、下一步是否需要用户决定。不要默认展示命令、原始 JSON、内部 ID、哈希/指纹、状态枚举或实现层名称。只有用户要求排障、审计或技术细节时,才在“技术详情”中展开。

审批问题必须描述用户将授权的实际动作、作用范围和能否撤销,不要只要求用户“批准 Canary/Active、Plan ID 或 ReleaseRecord”。部分成功必须明确说“整体尚未完成”:例如文件已恢复但操作记录失败时,先说明已恢复的内容和仍失败的环节,不得包装成通过。

涉及发布、安装、失败恢复或跨任务 handoff 时,读取 `references/user-feedback-standard.md`。

评测必须分开说明结构健康、证据覆盖与真实任务效用。没有 baseline/holdout/真实 rollout 时,明确写“尚未验证实际效果”,不能把静态分数冒充效果分。

本版本只执行确定性 status/字符串/regex/JSON 断言,不调用 LLM。结果 artifact 必须来自外部真实 rollout 或可信 harness;评测 suite 中不得包含或执行 command/script。

## 停止点

- 缺少会实质改变方案的输入,或没有足够独立 leakage group 构建 holdout。
- 用户尚未批准写入、安装、Global 或 Plugin/runtime 变更。
- Doctor hard gate、目标冲突、source/plan 漂移或操作记录不再安全可撤销。
- 修改没有失败模式/预期行为/回归证据契约,或维护 preflight/postflight 被阻断。
- 复杂生产 Skill 尚无 spec/plan、失败路径或 high-risk case。
- 自进化候选未通过 lint/Doctor、holdout、high-risk 或 negative-transfer gate,或 Release Plan/channel/target 已漂移。

停止时保留 JourneySession,用普通用户能采取行动的语言给出阻断原因和唯一下一步;不要丢失上下文或把内部记录字段当作结论。

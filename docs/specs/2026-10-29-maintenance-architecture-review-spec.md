# 维护架构审查阶段 Spec

状态：本地实现、同一计划应用及复验、独立评审与工程验证完成；未发布。

后续策略：[默认强制审查](2026-10-29-mandatory-architecture-review-spec.md)已完成并验证，取代本文当时“缺声明可应用”的兼容行为；本文保留原轮次事实。

[返回当前任务](../TASK.md) · [实施计划](../plans/2026-10-29-maintenance-architecture-review-plan.md) · [专项迭代](../sprints/2026-10-29-maintenance-architecture-review.md) · [架构决策](../adr/0010-internal-maintenance-architecture-review.md)

## 问题与目标

单次修改通过文件 diff、lint/Doctor，并不能证明多版本叠加后职责仍然清晰。现有复杂度主要比较本次增量，延后债务没有跨次归并；普通维护记录中的验收声明也不能充当真实行为结果。

本轮在现有 Skill Engineering 内增加独立的架构审查阶段，形成需求准入、旧结构处置、整体审查及累计债务门禁。用户已经批准内部阶段方案，并明确要求先对齐文档、实施完成后更新状态。

## 范围与边界

- 保持唯一顶层 Skill 身份；入口只路由，规范放 reference，阶段使用 `INSTRUCTIONS.md`。
- 增加确定性 `architecture_review.py`，由现有 `improve` 提供真实指纹、effective candidate 指标及维护历史。
- CLI 仅新增可选 `improve --architecture-review PATH`，不建立第二条 Apply/Verify/Undo 链路。
- 审查快照嵌入现有 `preflight.architecture_review`，由现有 plan hash 保护；不新增 BuildPlan/MaintenanceRecord 字段，不修改旧哈希算法。
- 不自动删除、拆分或退役文件；实际删除仍须进入同一计划的显式删除列表。
- 不实现完整 Blueprint/IR、语义图、模型 runner、SemVer 自动管理或自动发布。修复轮次上限和行为执行证据的既有缺口另行登记，不借本轮宣称已解决。
- 正式版本保持 `1.1.0`；本轮为用户授权的未发布源码增量，不关闭其他 Sprint。

## 需求裁决与双重完成门

每次架构声明包含能力归属、修改理由、旧结构替换/保留说明和应保护的行为。决策仅允许 `extend`、`refactor`、`split`、`defer`。前两者可进入当前候选评审；后两者阻断当前候选应用，并输出下一步。

本次维护完成门继续保护目标、计划、安全与回归范围。整体架构完成门独立报告，覆盖 ownership、routing、interfaces、state、failure、rollback。没有有效架构基线、声明边界变化、累计预算超限、重复未解决债务或调整基线预算时，必须有绑定本次完整 effective candidate 的整体审查证据。

整体审查是宿主/人工的独立评审声明，不是自动语义证明，也不代表真实行为测试通过。生成候选的 Agent 应交给独立评审者检查完整候选；工具只验证声明完整性、指纹、历史和预算。

## 输入与接口

JSON 顶层只接受：`schema_version`（字符串 `1`）、`requirement`、`baseline_record_id`（可选）、`budgets`、`debt`、`resolved_debt_ids`、`full_review`（可选）。拒绝未知字段、非法类型、重复债务 ID、布尔预算、负预算和原始凭证值；不得保存原始私有 Prompt 或会话。

- `requirement`：`summary`、`decision`、`rationale`、`owner`、`replacement_plan`、`protected_behaviors`、`touched_boundaries`。自由文本仅保存脱敏摘要，禁止保存秘密；边界名称必须属于约定集合。
- `budgets`：`skill_md_lines`、`instruction_files`、`duplicate_instruction_lines` 为相对整体基线的净增长上限；`open_debt` 为当前归并后未关闭债务 ID 的绝对数量上限。均为非负整数，不能用债务相对基线的差值抵消既有债务。复杂度指标来自 effective candidate，不能由声明伪造。
- `debt`：稳定 `id` 和脱敏 `summary`；`resolved_debt_ids` 显式关闭既有项。未解决债务持续保留，局部修改不得清空历史。
- `full_review`：`target_fingerprint`、`candidate_fingerprint`（候选目录）、`effective_fingerprint`（overlay 加显式删除后的完整树）、`checked_areas`、`conclusion`、`reviewer`、`evidence_summary`。只有完整覆盖六个审查范围、指纹匹配且结论为 `pass` 才可满足整体门；`changes_requested` 阻断。

接口为 `load_architecture_declaration(path: Path) -> dict[str, Any]` 与 `assess_architecture(*, declaration, target, target_fingerprint, candidate_fingerprint, effective_fingerprint, complexity, findings, history) -> dict[str, Any]`。模块不导入 maintenance，避免循环依赖；不执行输入中的命令、脚本或代码。

## 基线、预算与历史债务

基线仅可来自同一目标、状态仍为 applied、验证通过且包含有效完整架构评审的维护记录。记录中的目标 after fingerprint 必须与评审的 effective fingerprint 一致。显式 `baseline_record_id` 必须可解析且满足上述条件；错误目标、撤销、回滚或未验证记录不能成为基线。

未指定时选择最新有效整体基线；局部修改不刷新基线。前三项累计复杂度按“本次 effective candidate 减去该基线的 complexity.after”计算，不累加本次 delta，也不把前一轮局部修改自动当作新基线。开放债务单独计算归并后的绝对数量，基线中原有债务也计入。首次无历史时明确标记 baseline missing，并要求整体审查后才形成后续可用基线。

预算超限要求重新审视整体；整体评审可以明确接受有依据的增长，但报告必须保留超限事实，不能把超限改写为没有增长。开放债务按稳定 ID 合并，重复出现应触发整体审查。旧记录没有结构化债务时标记历史覆盖限制，不推断债务已经清零。

历史记录时间可能只有秒精度，同秒记录不能按随机 ID 猜测先后。使用既有 before/after 指纹链还原因果顺序；无法唯一确定时保守标记历史歧义并要求整体审查，不据此自动清债或选择较新基线。用户反馈须展示历史覆盖限制，债务数量仅称为已知数量。

## 兼容与用户反馈

没有架构声明的旧调用继续生成和应用计划，显示 `unreviewed`，不伪装为架构通过。对旧计划不补写字段，继续使用原 plan hash。新增声明的报告随计划快照持久化，应用时不可通过替换输入文件改变已预览结论；修改嵌入快照会触发哈希拒绝。

预览与维护结果分别说明本次维护状态、整体架构状态、累计增长/债务和唯一下一步。静态结构、声明性架构评审和真实任务行为证据分别表达。

## 验收标准

1. 独立内部阶段接入维护、设计和治理入口，没有第二个 `SKILL.md` 身份。
2. 无声明保持旧调用/旧计划兼容，反馈明确未审查；旧 Verify/Undo 不回归。
3. 四类决策可验证；split/defer、指纹不符、整体评审缺失或否决不能应用。
4. 两轮小改仍相对同一整体基线计算累计增长；局部维护不重置基线。
5. 债务跨次归并、重复触发、显式解决；错误目标和已撤销基线安全拒绝。同秒记录的关闭/重开和基线选择有因果链回归；无法唯一排序时明确要求整体审查。
6. 未知字段、非法类型、秘密输入、报告篡改及 overlay/删除语义有负例；不执行候选代码。
7. 新功能测试先失败后通过；全量 pytest、Ruff、Skill validation、Content Gate、production Doctor、portable self-test、credential lint、release consistency 和 diff check 通过，独立评审无未解决阻断。
8. Spec、Plan、Sprint、Task、使用说明、功能表、Changelog 和本轮测试记录更新为真实状态，未发布和未验证事项明确保留。

## 依据

[现有维护标准](../guides/skill-maintenance-standard.md) · [整体架构](../architecture.md) · [现有收敛规则](2026-10-20-boundary-tdd-convergence-spec.md#维护收敛机制) · [完整 Guardian 的后续范围](2026-07-16-v2.0-architecture-guardian-spec.md)

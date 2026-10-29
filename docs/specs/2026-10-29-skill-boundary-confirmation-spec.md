# Skill 边界确认与防跑偏

状态：本轮本地工程交付完成；已应用并验证。用户随后追加授权本轮提交与推送，进展见[源码交付](../testing/2026-10-29-skill-boundary-confirmation.md#源码提交与推送收尾)；未新增安装或正式发布，版本仍为1.1.0，真实业务长期效用未验证。

[文档入口](../README.md) · [当前任务](../TASK.md#skill-边界确认与防跑偏) · [实施计划](../plans/2026-10-29-skill-boundary-confirmation-plan.md) · [专项迭代](../sprints/2026-10-29-skill-boundary-confirmation.md) · [架构决定](../adr/0013-confirmed-boundaries-and-behavior-policy.md) · [恢复交接](../handoffs/2026-10-29-skill-boundary-confirmation-next.md) · [审查记录](../testing/2026-10-29-skill-boundary-confirmation-audit.md)

## 用户要求与确认范围

用户明确要求 Skill 不做什么也要与用户确认；文章仅为实践参考；规划已保存并同步项目/OB，前置架构保护已完成并核验，用户已明确要求继续。

2026-10-29，用户对范围问题明确选择“按此范围推进”：本轮交付创建/维护时确认做什么与不做什么、修正空断言门禁、按任务类型安排验收；暂不做通用运行时监控、自动模型评测平台或批量修改历史 Skill。此确认不授予提交、推送、安装、Global 或发布权限。

## 目标与流程

AI 先提出目标、职责、相邻排除项及理由，用户可接受、修改、拒绝或明确确认无额外排除。职责之外、本轮暂缓、有条件执行和能力限制须分别解释；拒绝一个排除项不自动增加职责。

未确认时可继续只读探索与草稿；可应用的新计划必须有对应边界确认。已有明确用户表达可复用，同一边界恢复不重复问；业务边界变化后旧确认失效。字段和指纹只验证本地流程绑定，不证明人类身份或消息真实性，宿主负责如实记录实际用户表达。

## 唯一边界与确认记录

沿用 Authoring Brief 的业务字段，不向旧 dataclass 增加默认字段。确认事实使用严格、脱敏的 JSON 输入，Native Preview 将其冻结进计划；维护使用原 preflight 的并列 boundary_review，架构审查保持原样。

边界投影包含 goal、mission、owned_capabilities、excluded_capabilities、allowed_context、正反触发、inputs、outputs、drift_signals、redirect_strategy、stop_conditions、side_effects、approvals。排除时间和执行状态，规范化外层空白后计算 SHA-256。任务内容仍是唯一正文，确认只绑定该投影。

确认 JSON 必含 schema_version='1'、subject_id、boundary_fingerprint、status、source、summary、excluded_decision、behavior_policy；message_ref 可选且必须来自宿主真实可用引用。source 只允许 explicit_user_message 或 explicit_cli_argument。只保存短脱敏摘要，不存完整会话或凭证。

status 表达 pending、confirmed、rejected、stale、legacy_unknown；形成可应用的新边界必须 confirmed 且指纹一致。excluded_decision 为 listed 或 none，必须与清单是否为空一致。允许已确认的空排除，不能把未确认的空值当同意。

behavior_policy 包含 interaction=single_turn|multi_turn、uses_tools、has_side_effects 和非空 rationale。存在已声明副作用却将其标为 false 必须拒绝；宿主和独立评审负责核对其他能力事实，不声称规则能够自动理解全部语义。

## 创建与维护门禁

Native 新预览新增 --boundary-confirmation，按 Brief ID 和当前边界验证确认；冻结确认与行为策略，继续绑定整个 Brief、候选和目标。Apply 重验快照和原指纹，不用可变输入改写已预览事实。新确认要求 redirect_strategy；单次任务可写越界说明并停止/交接，不强制持续主持循环。

新 improve 预览新增 --boundary-review，缺少时生成阻断 finding。声明为 changed 时提供 boundary、confirmation、cases；对 effective overlay 执行适用文本断言。声明 unchanged 时必须说明 reason，报告为 unchanged/legacy_unknown，不伪造历史批准；与架构声明的边界变更冲突时阻断。确认范围不代替原文件写入和外部动作权限。

维护冻结 target/candidate/effective 指纹及完整边界判定，Apply 在现有 overlay 中重验，再使用原备份、写入、Verify 和 Undo。所有新维护入口，包括 CLI、scaffold 维护代理及 Active，传递同一输入，不另建写入引擎。

## 按类型验证与证据

确定性 Runner 只检查候选 Markdown。空断言、空字符串、未知断言和非法列表不能通过；未提供实际断言为 uncovered，非法结构为 failed。案例 ID 必须非空且唯一；无案例不能通过。

兼容 run_behavior_cases 原调用；未给类型策略时只执行声明式断言，不虚构覆盖。新创建/changed 维护提供类型策略：success 和 insufficient 为基本覆盖；有排除/反触发时增加 negative；持续对话增加 drift；工具增加 failure；副作用增加 approval 和 failure。其余类别可省略；显式 not_applicable 须说明原因，实际必需类别不可豁免，success 不可豁免。

每个执行案例必须有 given、expect、must_not 与至少一条实际有效断言。not_applicable 单独统计，不计为 passed。结果固定声明 evidence_kind=candidate_text、utility_claim=false，不能证明真实多轮纠偏或停止。核心与 portable 使用同一标准库规则源的生成副本，并有字节一致性回归。

单次任务不套每轮主持循环。持续任务区分有效补充、岔题、明确切换和停止，尊重用户新意图。真实宿主试用与结构测试分别报告，不因未建设自动评测平台而伪造 rollout。

## 兼容策略

保持旧 Brief/Plan/Record 的加载、历史、Verify、Undo 及原哈希。已经满足 ADR 0011 的旧计划保留其合法 Apply 路径，缺新边界快照明确报告 legacy_unknown；不能把它升级为已确认。新预览始终携带边界判定，缺项阻断，不能生成新的无审查可应用计划。旧 Native Plan 按原校验继续，不倒填确认。

不批量迁移已有 Skill，不修改正式发行物；未来若收紧旧计划写入必须另作决定，不能在本轮暗改。

## 验收

- 接受、修改、拒绝排除提案与确认空排除均能表达；未确认、失效、历史未知不会伪装成已确认。
- 修改 business projection 后旧确认不能用于新预览；时间等元数据变化不改变边界指纹。
- Native 与 changed 维护没有有效确认时不能应用；unchanged 的旧边界保持未知，不强迫无关小修重写历史。
- 空/非法断言、重复 ID、缺少所需类别均不通过；非适用类别有清楚能力依据，已声明高风险不可借不适用跳过。
- 新计划的确认/候选/目标/effective 漂移停止；旧计划加载/Verify/Undo 和符合旧策略的 Apply 继续。
- CLI、Active、scaffold 维护代理无新旁路；两种安装表面均可使用规则，不强依赖另装 CLI。
- 内容检查、工程回归、真实试用与发布分别记录；不宣称普遍真实效果。

## 实施约束与前置

前置内部架构审查、强制门禁及自然语言激活均已完成，当前全量基线为449项通过。现有用户未提交修改全部为受保护基线。仅在隔离候选开发，先测试失败后实现，独立评审后按同一预览应用。

具体接口、隐私限制与执行顺序以关联 Plan 和 ADR 为准。安装、提交、推送和发布另行授权。

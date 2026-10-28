# 维护写入默认强制架构审查

状态：Accepted；本地实现、独立评审与验证完成。决定日期：2026-10-29。

[返回 ADR 索引](README.md) · [当前架构](../architecture.md) · [需求合同](../specs/2026-10-29-mandatory-architecture-review-spec.md) · [实施计划](../plans/2026-10-29-mandatory-architecture-review-plan.md)

## 背景

[内部阶段决定](0010-internal-maintenance-architecture-review.md)保留无声明调用与旧计划 Apply 兼容。用户进一步明确要求 CLI 必须执行审查，避免 Agent 遗漏。只改参数解析无法保护旧计划、scaffold 代理与 Active 维护写入。

## 决定

在既有架构模块与维护引擎内实现预览/应用双重门禁；缺声明可生成带真实指纹的阻断预览，但不能成功退出或应用。所有 profile 一致，不增加绕过开关。Active 发布新增同一声明输入并复用原核心门禁。

读取历史与恢复保持兼容；旧未审查计划必须补审并重新预览，不能原地补字段后继续使用旧审批。旧 plan hash 不变，已通过审查的有效计划可继续应用。Native Authoring、Shadow/Canary、审批与安全恢复边界不变。

## 取代与影响

仅取代 ADR 0010 中“无声明可继续 Apply”的兼容决定，其余字段、基线、独立评审和证据限制继续有效。该收紧是用户明确批准的未发布工作区策略；正式 1.1.0 发行物不被改写。

该门禁防止漏交审查输入，不证明人工声明真实、评审者独立或语义正确。独立评审与真实行为证据仍由宿主执行并分别报告。

## 替代方案

参数 required 无法覆盖旧计划且破坏查看；只拦预览留下应用旁路；引入 allow-legacy/skip 会保留本次要关闭的漏洞。因此复用原核心，在写入前拒绝未满足门禁的冻结快照。

## 迁移与验收

按[需求验收](../specs/2026-10-29-mandatory-architecture-review-spec.md#验收与证据)验证历史读取/恢复、Active 与所有维护写入入口；完成后更新[专项记录](../testing/2026-10-29-mandatory-architecture-review.md)。

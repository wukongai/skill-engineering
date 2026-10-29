# 确认边界与按类型行为检查

状态：Accepted用于本轮本地实现；2026-10-29；未安装或发布。

[ADR索引](README.md) · [需求](../specs/2026-10-29-skill-boundary-confirmation-spec.md) · [实施计划](../plans/2026-10-29-skill-boundary-confirmation-plan.md)

## 决定

复用现有Brief业务字段；确认事实以严格脱敏JSON输入进入新Native计划或preflight.boundary_review。边界确认与架构审查并列，不增加另一套审批、写入、回滚引擎；指纹不证明人类身份。

新预览默认需要边界判定，changed须有用户确认，unchanged须说明理由且不得与架构边界变更矛盾。无历史确认只能报告legacy_unknown，不能补造用户曾认可。新门禁覆盖CLI、维护代理和Active的同一核心。

保留ADR0011下已经合法的旧计划Apply、历史读取、Verify、Undo，不改变旧hash或在旧计划里补字段；缺新边界键的旧计划不宣称具备新保护。新Native计划冻结确认，旧Native沿用原校验。

canonical标准库模块在Python包内，portable副本由其生成并做字节一致性回归，兼顾Python-only与Skill-only安装，不让一方依赖另一安装表面。

## 取舍与限制

不直接扩展旧dataclass，避免旧运行时解析或旧hash变化；不将确认塞入architecture_review的严格schema。没有可信消息来源时不能声称验证了真人授权。unchanged声明与其他自然语言事实仍需宿主和独立评审如实判断，确定性门禁不证明其语义。

空断言不得通过；类别按任务形态和声明能力选择。候选文本通过、真实运行及业务效果分别报告。通用运行时、自动评测平台和批量历史迁移不进入本轮。

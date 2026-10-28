# CLI 强制架构审查专项迭代

状态：Done；本地实现、独立评审、同一计划应用复验及安装验证完成；未发布。

[当前任务](../TASK.md) · [需求与验收](../specs/2026-10-29-mandatory-architecture-review-spec.md) · [实施计划](../plans/2026-10-29-mandatory-architecture-review-plan.md) · [测试记录](../testing/2026-10-29-mandatory-architecture-review.md)

## 范围

将已有可选架构声明收紧为维护 CLI/Core 的必需门禁；覆盖旧计划 Apply、scaffold 代理和 Active 发布。保留历史读取/Verify/Undo，全新创建继续 Native Authoring。正式版本仍为 1.1.0，其他 Sprint 不扩展。

- [x] MR-0：404 项基线、隔离副本、Spec/Plan/ADR 与项目入口对齐。
- [x] MR-1：测试先行，核心缺声明阻断和旧计划 Apply 防绕过。
- [x] MR-2：CLI/Active 接入与 Skill 单一规范、薄路由对齐。
- [x] MR-3：独立评审、精确清单应用、同一维护计划 Verify 与完整门禁。
- [x] MR-4：已安装链接核对、仓库外 console 实测和最终文档回填。
- [x] MR-5：按后续授权提交独立范围、推送远程并回填实际提交证据。

退出条件：所有验收与工程门禁通过，无未解决评审阻断，已安装入口一致且遗漏审查实测被拒绝。原实施阶段未执行commit/push；用户后续另行授权源码提交推送，本次仍不创建Tag/正式Release或新增全局暴露。

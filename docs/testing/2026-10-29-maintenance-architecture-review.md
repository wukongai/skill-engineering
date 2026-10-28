# 维护架构审查验证记录

状态：本地实现、独立评审、同一计划应用复验与文档门禁完成；未发布。

[需求验收](../specs/2026-10-29-maintenance-architecture-review-spec.md#验收标准) · [实施计划](../plans/2026-10-29-maintenance-architecture-review-plan.md) · [专项迭代](../sprints/2026-10-29-maintenance-architecture-review.md) · [当前任务](../TASK.md)

## 实施前基线

2026-10-29 本轮执行 `python3 -m pytest -q`：316 passed in 4.29s。工作区已有 SEC102 与项目收尾未提交改动，本轮以当前文件内容为受保护基线，未重置或清理。

## 红绿测试与回归

- 核心初始 RED：36 failed / 17 passed，缺模块、参数和未审查反馈；对应实现后转绿。
- 内部阶段初始 RED：4 failed / 16 passed；路由、字段及包内案例落地后转绿，12 个包内声明案例实际调用 loader。
- 独立评审修正 RED：同秒历史及反馈 8 failed；带前缀凭证 30 failed；引号通用键和私钥赋值另有 2 failed。均先确认失败，再修复并转绿。
- 最终已应用工作区执行 `python -m pytest -q`：**404 passed in 4.29s**；较原基线增加 88 项。覆盖旧计划哈希、Apply/Verify/Undo、真实跨轮基线、四类需求裁决、累计预算、债务归并/关闭/重开、同秒因果歧义、overlay/显式删除、指纹篡改和非法/凭证形态输入。

## 独立评审与自举应用

首轮发现 3 项 Important、无 Critical：同秒随机 ID 排序、人读反馈遗漏历史限制、带前缀凭证漏检。完成最小修复后，第二轮 Spec 符合性和代码质量均通过，无未解决 Important/Critical；完整 Skill 的 ownership、routing、interfaces、state、failure、rollback 六范围声明性评审通过。

8 个源码/测试文件按修改前 SHA-256 与评审清单核对后备份并应用。11 个 Skill 文件通过原 maintenance engine 的同一不可变计划应用，正式 Verify 为 passed、drifted=false。根入口只增加 1 行，重复长指令增量 0；没有删除文件。

精确 plan/record 身份、实际输入指纹与检查状态由[脱敏验证证据](2026-10-29-maintenance-architecture-review-evidence.json)保存；维护记录和 Skill 备份保存在项目本机忽略状态中，源码修改前另存会话临时备份。不存在安装或公开发布动作。

后续用户授权核对安装入口时，确认它们实际为同一源码链接，源码修改已经可见，无独立副本需要复制；“尚未更新安装副本”的表述据此更正。[安装入口与实际流程复验](2026-10-29-installed-architecture-review-smoke.md)记录了仓库外 CLI、正反向门禁、累计预算和恢复验证，不表示公开发布。

## 工程门禁

| 检查 | 当前实际结果 |
|---|---|
| 全量 pytest | 404 passed |
| Ruff：`ruff check src tests` | pass |
| 官方 Skill validation | valid |
| Content Completion Gate | pass，0 findings |
| production Doctor | 100/A，零 FAIL/WARN；仅结构 readiness |
| portable self-test | pass，target_unchanged=true，utility_claim=false |
| 文档相关回归 | 43 passed |
| credential lint、release consistency、diff check | 全部 pass；正式版本 1.1.0 一致 |
| 本次文档文件链接与标题锚点 | 27 份本轮受影响文档、215 处本地引用，0 错误 |

Doctor 首次用不支持的包模块入口启动失败，改用项目 CLI 的 `main` 入口后重跑通过；没有为此新增产品接口。既有版本事实仍由 release consistency 检查，正式版本为 1.1.0。

## 证据边界

自动测试证明确定性门禁与兼容行为；架构评审属于宿主/人工声明，不证明长期实际效用。真实宿主长期多版本试用、完整 Guardian 和自动模型 runner 不属于本轮验收，不得从静态分数推出。

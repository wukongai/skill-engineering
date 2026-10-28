# 维护架构审查阶段 Implementation Plan

> 执行方式：在本轮隔离候选中按测试驱动开发实施，独立评审后应用；用户已授权本轮实现及前后文档更新，未授权 Commit、Push、Tag、安装或发布。

状态：本地实施、独立评审、应用复验及文档收尾完成；未发布。

**Goal:** 为现有维护流程增加需求裁决、整体架构审查和跨版本累计债务保护。

**Architecture:** 内部阶段负责引导独立审查，确定性模块验证声明和历史；报告存入原 preflight 并受原计划哈希保护。复用原 overlay、审批、Apply、Verify、Undo，不增加第二套状态引擎。

**Tech Stack:** Python >=3.10、现有 PyYAML、pytest、Ruff；不增加运行依赖。

[需求与验收](../specs/2026-10-29-maintenance-architecture-review-spec.md) · [当前任务](../TASK.md) · [专项迭代](../sprints/2026-10-29-maintenance-architecture-review.md) · [测试记录](../testing/2026-10-29-maintenance-architecture-review.md)

## 全局约束

- 正式版本保持 `1.1.0`，新功能仅为本地未发布增量。
- 输入合同以关联 Spec 为准；不新增 BuildPlan/MaintenanceRecord 字段，不修改旧哈希算法。
- 已有 SEC102/项目收尾改动为受保护基线，实施不得覆盖。
- Skill 内容先在独立候选修改，再通过同一 maintenance plan 应用。
- 源码候选先验证，再检查修改前指纹并按精确文件清单回写；不删除未知文件。
- 不保存凭证、原始私有 Prompt、完整会话，不运行候选脚本。

## 任务一：文档与实施基线

- [x] 读取产品、宪章、架构、Task、现有 Sprint、维护引擎和相关测试。
- [x] 运行原全量 `python3 -m pytest -q`，确认 316 passed。
- [x] 保存包含当前未提交改动的隔离候选与修改前文件指纹。
- [x] 落地 Spec、Plan、ADR、专项 Sprint 和初始测试/日志；更新相关事实源的计划状态。

## 任务二：确定性架构审查与 improve 接入

文件：新增 `src/skill_engineering/architecture_review.py`、`tests/test_architecture_review.py`；修改 `src/skill_engineering/maintenance.py`、`src/skill_engineering/cli.py`；扩展维护/CLI 回归。

消费：现有 complexity before/after/delta、effective tree 指纹、MaintenanceRecord 历史。产出：脱敏且可哈希的架构审查报告，包含决策、整体门、基线、累计增量、预算、开放债务、限制和下一步。

- [x] 先写需求裁决、旧调用未审查、指纹绑定、累计预算、债务归并/解决和旧计划兼容测试。
- [x] 执行 `python3 -m pytest tests/test_architecture_review.py tests/test_maintenance.py tests/test_cli.py -q`，保存预期失败证据。
- [x] 实现声明白名单校验与秘密拒绝、四类决策、基线选择和累计指标计算；非法输入在计划持久化前停止。
- [x] 在 create_improvement_plan 内加入可选 architecture_review 输入，将结果放入 preflight；触发整体门而未满足时新增 FAIL finding。
- [x] CLI 增加可选路径参数，预览和结果清楚区分单次维护与整体架构；不得将静态结果称为行为通过。
- [x] 重跑针对测试，补 overlay/显式删除、声明篡改、错误/撤销基线、预算边界与历史覆盖限制负例。
- [x] 独立评审修正：补同秒历史记录的因果链排序、无法唯一排序的整体门，以及已知债务/历史限制反馈的红绿回归。

接口示例（语法演示）：

```python
report = assess_architecture(
    declaration=declaration, target=target,
    target_fingerprint=target_fingerprint,
    candidate_fingerprint=candidate_fingerprint,
    effective_fingerprint=effective_fingerprint,
    complexity={"before": before, "after": after, "delta": delta},
    findings=findings, history=history,
)
preflight["architecture_review"] = report
```

## 任务三：内部 Skill 阶段与契约

文件：新增 `skills/skill-engineering/stages/architecture-review/INSTRUCTIONS.md`、`references/architecture-review.md`、`tests/architecture-review-cases.json`；修改根入口、维护/治理 reference、相关阶段、file-map 和 skill.contract.yaml；扩展仓库内对应测试。

- [x] 先登记阶段路由、契约、唯一 Skill 身份和案例负例，并确认测试失败。
- [x] 根入口只添加短路由；完整声明合同和整体审查步骤在单一 reference 维护。
- [x] 描述候选生成者与独立评审者的分工，要求检查完整候选；声明/工具无法证明真实行为的限制明确可见。
- [x] 对齐核心 JSON 字段，保持 overlay/显式删除及原维护链路，缺失审查明确 unreviewed。
- [x] 针对测试通过后，运行 Skill 内容门禁；通过维护引擎预览并应用同一候选/计划，再 verify。

## 任务四：评审、应用与文档收尾

- [x] 对隔离候选生成完整差异包，独立评审 Spec 覆盖、兼容、输入安全和代码质量；修复所有阻断后复核。
- [x] 对源码按原指纹核对并备份，仅应用已评审的文件差异；保持已有未提交改动。
- [x] 运行全量 pytest、Ruff、Skill validation、Content Gate、production Doctor、portable self-test、credential lint、release consistency、`git diff --check`。
- [x] 更新 README/维护指南与 JSON 使用示例；核对本次文档相对链接、标题锚点、返回入口。
- [x] 回填测试证据、专项 Sprint、Task、Product/Architecture、Roadmap、功能表、Unreleased Changelog、日志与本 Plan 的实际状态。
- [x] 保留真实宿主长期行为、完整 Guardian 和自动 runner 的未验证/后续边界，不宣称发布或安装完成。

## 回退与完成条件

隔离候选可以保留待复核；应用前任何基线漂移都停止受影响文件，不覆盖他人修改。Skill 修改使用现有维护记录及备份，只有无后续漂移才可安全 undo。源码回退由本轮变更清单和外部备份生成精确恢复差异，不自动重置仓库。

只有 Spec 验收、独立评审、当前全量门禁和相关文档读回全部完成，才可将本轮状态更新为本地实现与验证完成。Commit、Push、Tag、安装和公开发布另行授权。

## 后续用户授权：已安装入口同步与实测

用户已另行授权同步既有安装并验证新增流程。两处已安装入口解析到同一仓库目录，无需复制；使用已有虚拟环境 CLI，从仓库外执行独立候选、缺评审阻断、独立整体评审、Apply/Verify、累计预算及 Undo。详细进度与结果以[安装流程复验](../testing/2026-10-29-installed-architecture-review-smoke.md)为准，不将本次授权扩展为公开发布或新建 Global 暴露。

跟进状态：已完成。两处安装入口内容一致，无需复制；22 项 CLI 检查、一次 Agent 合成样本、404 项全量回归与文档门禁均通过。使用原虚拟环境入口，未更改全局 PATH、发布或新增暴露范围。

# Skill Engineering 版本管理规范

## 版本含义

Skill Engineering 使用语义化版本 `MAJOR.MINOR.PATCH`：

| 版本段 | 含义 | 允许的变化 |
|---|---|---|
| `0.x` | Public Beta / 试验阶段 | 可以调整 CLI、JSON、文档和内部结构，但必须记录迁移影响。 |
| `1.x` | 稳定产品契约 | 兼容现有 CLI、JSON、contract、计划和记录格式；破坏性变化必须进入 2.0 或提供迁移。 |
| `2.x` | Architecture Guardian 主架构 | 引入 Blueprint/IR、架构图和守护器；读取 1.x 输入，输出新的架构证据。 |
| `PATCH` | 兼容修复 | 修复 bug、误报、文档和安全问题，不改变公开契约。 |
| `MINOR` | 向后兼容能力 | 增加可选能力、规则或报告字段，不删除旧输入。 |
| `MAJOR` | 破坏性变化 | 删除/重命名字段、改变状态语义、改变默认安全边界或替换核心架构。 |

## 当前版本状态

- 已发布基线：`0.1.0` Public Beta。
- 已实现但尚未发布：`0.1.1` Security Doctor（AST 安全规则、SARIF）。
- 当前稳定化目标：`1.0.0` Stable Lifecycle Contract。
- 当前开发目标：`2.0.0` Architecture Guardian；第一阶段为 Blueprint/IR 契约设计。

代码包版本在正式发布前保持与已发布版本一致；`Unreleased` 的功能不得被文档表述成已发布能力。

## 版本事实源

一次版本变更必须同时检查：

1. `pyproject.toml` 和 `src/skill_engineering/__init__.py`；
2. `CHANGELOG.md` 的用户可感知记录；
3. `docs/releases/RELEASE-LOG.md` 的阶段和门禁；
4. `docs/ROADMAP.md`、`docs/TASK.md`、当前 Sprint；
5. 对应 `docs/specs/`、`docs/plans/` 和 `docs/testing/`；
6. README 的安装、能力和限制描述。
7. `LICENSE`、版权与安装指南以及许可证/安装范围的营销表述。

## 发布阶段

```text
Unreleased -> Preview -> Release Candidate -> Stable -> Maintenance -> End of Support
```

- Unreleased：代码和文档在开发中，不承诺兼容。
- Preview：功能可试用，但必须标注风险和缺失证据。
- Release Candidate：Spec、Plan、测试、凭证 lint、Doctor 和 diff check 全部通过。
- Stable：用户可依赖的输入输出、迁移和回滚说明已经冻结。
- Maintenance：只接受兼容 bug、安全和文档修复。
- End of Support：停止新修复，保留迁移说明。

## 兼容与迁移

- 旧 JSON 字段不能静默改变含义；新增字段必须可选或带 schema version。
- Doctor 新规则默认应先作为 WARN，只有误报边界和 regression 充分时才升级为 FAIL。
- 2.0 必须提供 1.x contract/plan 的只读导入或明确迁移错误，不能直接把旧 Skill 判定为不可用。
- 破坏性迁移必须包含 before/after 示例、自动检查和回滚入口。
- 许可证变化不是补丁级修复；必须通过 ADR、迁移说明、贡献者沟通和新的版本门禁。稳定发布必须同时冻结 CLI 包与 Agent Skill 的安装入口。

## 发布授权边界

测试、commit、push、tag、公开发布和 Global 安装是独立确认点。项目不会自动执行公开发布或 Global 分发。

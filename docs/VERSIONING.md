# 版本管理

项目使用语义化版本：`MAJOR.MINOR.PATCH`。

- `PATCH`：兼容的缺陷修复、规则校准和文档修正。
- `MINOR`：兼容的新能力、CLI 子命令或新治理层。
- `MAJOR`：状态 schema、CLI、Blueprint 或发布契约的破坏性变化。

## Public Beta

`0.x` 表示接口仍可能变化，但每次变化仍必须提供迁移说明。当前候选为 `0.1.0`。

## 单一版本事实源

发布时必须同步：

- `pyproject.toml`；
- `src/skill_engineering/__init__.py`；
- `CHANGELOG.md`；
- `docs/ROADMAP.md`；
- `docs/TASK.md`；
- 当前 Sprint 和发布说明。

## 发布规则

1. Spec/Plan 和实现完成。
2. 所有 Release Gate 通过。
3. Changelog 只记录用户可感知的已完成事实。
4. 创建 tag 或公开发布前获得明确授权。
5. 不把“计划”“本地结构分”或未完成外部证据写成已发布能力。

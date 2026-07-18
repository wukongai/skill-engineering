# Skill Engineering 版权与安装政策实施计划

状态：Superseded by `docs/plans/2026-07-18-apache-2.0-attribution-plan.md`；保留为 MIT 阶段的历史实施记录

## 阶段

1. **Policy inventory**：核对 `LICENSE`、`pyproject.toml`、README、CONTRIBUTING、PRODUCT、VERSIONING 和现有安装治理规则，列出冲突与缺口。
2. **Decision record**：新增 ADR 0005，固定 MIT、适用范围、第三方/用户内容/商标边界，以及未来改证的触发条件，并引用现有标准安装入口 ADR 0004。
3. **Single source**：新增版权与安装指南，提供安装决策表、命令、当前发布状态、升级/卸载/回滚边界。
4. **User surface**：更新 README、PRODUCT、docs index、CONTRIBUTING、TASK、VERSIONING、CHANGELOG 和发布日志，使用户入口与产品事实一致。
5. **Verification**：运行文档链接/字符串检查、pytest、Ruff、官方 Skill validation、production Doctor、credential lint 和 `git diff --check`；确认未触碰真实全局 Skill 或外部发布。

## 复杂度与影响

- 代码运行时行为：无变化。
- 新增事实源：1 个指南、1 个 ADR、1 个 Spec、1 个 Plan。
- 用户可见变化：安装说明更明确，MIT 适用范围和商业边界更明确。
- 兼容性：保持现有 MIT，不要求已发布用户迁移许可证；canonical Agent Skill 名称保持 `skill-engineering`。

## 恢复

本计划只修改版本化文档和元数据说明，不执行安装、发布或删除操作。若文档验证失败，恢复本计划涉及的文档变更即可，不影响用户环境。

## 完成定义

Spec、Plan、ADR、指南、README、产品/版本事实源和 CHANGELOG 对齐；验证通过；发布、tag、push 和 Global 安装仍作为独立确认点。

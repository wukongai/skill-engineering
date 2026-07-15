# Skill Engineering 统一对外身份实施计划

状态：Implemented with follow-ups；本次 identity 迁移已落地，远程 v1.0 安装与真实全局替换不在本次提交中自动执行

对应 Spec：`docs/specs/2026-07-16-skill-identity-unification-spec.md`

## 阶段

1. **Identity inventory**：盘点 `skill-guide` 在 frontmatter、contract、文档、测试、symlink 和安装路径中的全部引用，区分用户可见与内部兼容引用。
2. **Canonical source**：在独立候选中把顶层 Agent Skill 统一为 `skills/skill-engineering/`，更新 frontmatter、contract、交叉链接和 validation 入口；旧目录移出顶层发现路径。
3. **Trigger regression**：增加明确提到 `skill-engineering` 的正例、harness/ank 的反例和重复暴露负例，验证只命中 canonical Skill。
4. **Global install smoke**：从远程固定 tag 克隆到临时目录，使用隔离 HOME/Codex Skill 根完成 global install、发现、替换旧别名和清理恢复；不触碰真实用户全局目录。
5. **Creation and doctor E2E**：在任意临时项目完成 decide、create preview/apply、Doctor、维护 preview/apply/verify，并核对用户反馈、审批边界和文件指纹。
6. **Documentation and release evidence**：更新 README、迁移说明、版本/Changelog、Task/Sprint 和测试证据；明确当前远程只有 `v0.1.0` 时不得宣称已完成 1.0 远程安装回归。
7. **Gate**：运行 pytest、Ruff、Skill validation、production Doctor、credential lint、diff check 和隔离 E2E；用户确认后才允许 commit、push、tag 或公开发布。

## 风险与恢复

- 旧全局 `skill-guide` 与新 Skill 同时存在：安装前阻断并展示范围，确认后可恢复旧入口。
- 目录迁移导致直接路径引用失效：先保留迁移映射和 fixture，通过全量引用扫描后再移出发现路径。
- Agent 仍误选相似项目治理 Skill：通过 canonical description、negative trigger fixture 和隔离真实对话复验，不靠追加自然语言禁令掩盖冲突。
- 远程 tag 未发布：只能运行本地候选或明确版本的 smoke，不伪造 `v1.0.0` 远程证据。

# Skill Engineering 标准安装体验实施计划

状态：In progress；统一入口版本发布前不解除远程安装门禁

对应 Spec：`docs/specs/2026-07-16-standard-skill-install-spec.md`

## 阶段

1. **Installer contract**：冻结 `npx skills add <owner>/<repo> --skill skill-engineering` 为普通用户入口，补充全局/项目范围与 Codex/Claude 目标说明。
2. **Documentation split**：更新 README、安装治理 reference、贡献指南、迁移说明和外部 OB 文章；首屏只展示直接安装，clone/fork 移到源码学习区。
3. **Release guard**：检查远程默认分支与版本 tag 是否已包含 `skills/skill-engineering/`；旧 `v0.1.0` 仍是 `skill-guide` 时保持 blocked，不伪造远程成功。
4. **Isolated installer smoke**：在临时 HOME 和临时项目中使用 `npx skills add` 安装本地候选或新远程版本，验证唯一入口、任意项目触发、create preview/apply 和 Doctor。
5. **Quality gate**：运行 pytest、Ruff、Skill validation、production Doctor、credential lint、`git diff --check`，并写入测试证据。
6. **Release approval**：用户单独确认后，才允许 commit、push、tag、公开发布；发布后用真实 GitHub 版本重跑安装器 smoke。

## 风险与恢复

- 标准安装器缓存旧远程版本：测试先读取安装源的 skill 目录和 frontmatter，发现 `skill-guide` 立即阻断，不覆盖用户目录。
- 安装器默认范围不清：文档同时给出 `-g`（跨项目）和不带 `-g`（当前项目），并在命令中显式指定 agent 时避免误装。
- 多宿主目录造成重复入口：隔离 smoke 检查 Codex/Claude 目标目录的唯一 canonical 名称；失败时只清理临时 HOME。
- 用户把 clone 当成安装步骤：把 clone/fork 仅放进“源码学习与二次开发”小节，并在首屏写清其不是使用前置条件。

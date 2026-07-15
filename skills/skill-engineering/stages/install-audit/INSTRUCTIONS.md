# Install Audit 阶段

用于审计 project、profile、global、direct/manual 或 plugin 暴露问题。

1. 读取 `references/install-governance.md`。
2. 识别相关 adapter 入口,例如 `.agents/skills` 和 `.claude/skills`。
3. 把每个可见能力分类为 global、project、profile-managed、direct/manual、plugin/runtime 或 archive/experiment。
4. 检查重复 description、宽泛 trigger、plugin inventory 膨胀和内部 stage 暴露;broken symlink、foreign/manual entry 和 Profile 漂移交给 Agent Skill Hub。
5. 默认优先推荐 scoped exposure,不要直接全局暴露。
6. 启用或禁用 global skill / plugin 前,先停下让用户确认。

# Scaffold 阶段

只有设计被确认后才使用这个阶段。

创建最小有用文件集:

1. `SKILL.md`:包含 frontmatter、路由、输出、停止点和验证命令。
2. `skill.contract.yaml`:复杂、生产级或有副作用 workflow 必须有。
3. `agents/openai.yaml`:需要 UI 元数据时添加。
4. `references/`:只放需要按需加载的上下文。
5. `scripts/`:只放确定性或重复执行的操作。
6. `assets/`:只有存在静态资源、模板、示例文件、媒体素材或可复用输出资产时才创建。
7. `tests/skills/<skill-name>/cases/*.yaml`:固化不能回退的行为。

脚手架落完后,先跑 lint/doctor,再扩展内容。

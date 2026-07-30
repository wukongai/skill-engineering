# Scaffold 阶段

只有设计和 Authoring Brief 被确认后才使用这个阶段。

按 Brief 直接生成完整候选,而不是先搭骨架再补内容:

1. `SKILL.md`:包含 frontmatter、路由、任务专属规则与工作流、输出、停止点和验证命令;不得残留通用模板语句。
2. `skill.contract.yaml`:复杂、生产级或有副作用 workflow 必须有。
3. `agents/openai.yaml`:需要 UI 元数据时添加。
4. `references/`:只放需要按需加载的上下文,且每个文件有真实内容和明确读取入口。
5. `scripts/`:只放确定性或重复执行的操作;声明的脚本必须真实存在并通过运行测试。
6. `assets/`:只有存在静态资源、模板、示例文件、媒体素材或可复用输出资产时才创建。
7. `tests/skills/<skill-name>/cases/*.yaml`:固化不能回退的行为。

候选先落隔离候选目录,预览前必须通过 Content Completion Gate(运行
`scripts/content_gate.py`,无 Python 时按 `references/content-completion-gate.md`
的 Agent-native 等价清单逐项检查);阻断项存在时保持 `candidate_incomplete`,
不得写入正式目标。

有 Python 时固定使用同一条 portable plan 链:

```bash
python3 scripts/native_plan.py preview \
  --project <项目> --brief-id <已保存 Brief id> \
  --candidate <隔离候选> --target <正式目标> --plan <plan.json> --json

# 用户看过实际文件并明确确认后
python3 scripts/native_plan.py apply \
  --plan <同一 plan.json> --candidate <同一隔离候选> --target <同一正式目标> --json

python3 scripts/native_plan.py verify \
  --plan <同一 plan.json> --target <同一正式目标> --json
```

`preview` 只写 plan、不写 target；candidate、脱敏 Brief、target 或 plan 任一漂移
都必须拒绝 Apply。写后再运行 `scripts/skill_self_test.py`；完整 CLI Doctor 只作
可选增强。

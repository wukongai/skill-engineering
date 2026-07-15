# Review 阶段

接受 skill 变更前使用这个阶段。

1. 读取 `references/maintenance-protocol.md` 和 `references/rule-authoring.md`。
2. 说明这次变更解决的失败或新增能力。
3. 判断根因层级。
4. 写清预期行为,确认 regression case 或明确的不适用理由。
5. 在独立候选目录修改,生成 maintenance plan。
6. 检查文件增删改、复杂度 delta、retained legacy files 和 MAINT findings。
7. 如果修复只是多加一条自然语言禁令,而没有落到可执行层,不要接受。
8. preflight 通过并获得确认后,应用同一 plan id。
9. 确认 postflight、维护记录、复验和安全撤销状态。

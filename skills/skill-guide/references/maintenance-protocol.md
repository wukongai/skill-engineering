# 维护协议

修 skill 时,把歧义移动到最低、最可执行的层级,而不是继续往 `SKILL.md` 堆自然语言提醒。

## 根因层级

| 层级 | 例子 | 优先修复位置 |
|---|---|---|
| trigger | 选错 skill、description 过宽 | frontmatter description、profile scope |
| interface | inputs/outputs/stops 不清楚 | contract 和根路由 |
| state | 忘记审批、多 turn 漂移 | manifest/state file |
| script | 日期/路径/文件/API 检查 | deterministic script |
| style | 写作语气或模板 | reference file |
| long-task | timeout、retry、log | runner script |
| install | global 污染、plugin inventory 重复 | profile/plugin governance |

## 修复顺序

1. 给失败模式命名。
2. 判断根因层级。
3. 写清修改后必须成立的预期行为。
4. 新增或更新 fixture/regression case;personal/team 确实不适用时必须写明理由,production 不允许豁免。
5. 在独立候选目录修最低可执行层,不要直接覆盖 source。
6. 生成维护计划,检查增删改 diff、入口行数、门禁词、事故措辞、重复指令和遗留文件。
7. preflight 通过并获得确认后,应用同一 plan id。
8. 自动 postflight;失败恢复原状态,成功保存维护记录。
9. 需要时复验、查看历史或按记录安全撤销。

事故细节放到 engineering note、handoff 或 regression case,不要放根 `SKILL.md`。

## 维护门禁

- `improve` 预览不写目标目录。
- 候选目录只做 overlay;缺失文件默认保留,删除必须显式列出。
- target、candidate 或 plan hash 变化后,旧计划失效。
- preflight 自动运行确定性 lint/Doctor,不执行候选脚本。
- postflight 失败自动回滚。
- 成功修改生成记录;只有目标未漂移时才能撤销。
- 好的修复通常让入口更薄;入口、禁令、事故措辞和重复规则持续增加时必须 review。

## 不要做

- 每个 bug 都追加一条“绝对禁止”。
- 直接在 source 上试错,绕过候选 diff 和 preflight。
- 因候选目录里没有某个旧文件就自动删除它。
- 修改成功后不保留记录,靠聊天记忆决定如何恢复。
- 把随口一句 “OK” 当成不可逆工作的批准。
- 下游还需要输出时,把任务丢后台跑。
- 让 LLM 编造本应来自 manifest 或工具输出的事实。

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
6. 按[架构审查规范](architecture-review.md)准备声明，再生成维护计划，检查增删改 diff、入口行数、门禁词、事故措辞、重复指令和遗留文件。
7. preflight 通过并获得确认后,应用同一 plan id。
8. 自动 postflight;失败恢复原状态,成功保存维护记录。
9. 需要时复验、查看历史或按记录安全撤销。

事故细节放到 engineering note、handoff 或 regression case,不要放根 `SKILL.md`。

## 架构审查接入

扩展、重构已有 Skill 或规划维护时，按[维护架构审查规范](architecture-review.md)核对需求归属与旧结构处置，分别报告本次完成门和整体架构门。普通小修使用轻量声明；需要整体审查时，把完整候选交给独立评审者。

声明是已有 Skill 维护预览的必需输入；CLI 与核心默认阻断缺声明及旧未审查计划应用。审批、计划绑定、写后检查和恢复仍由本协议负责，历史读取与安全恢复保持。全新创建不使用维护历史基线。字段、触发条件、迁移和证据限制只在上方规范维护。

新维护与 Active 同时提供 `--boundary-review <JSON路径>`。边界变化时需当前确认与按类型案例；未变化时需 reason 并保持历史确认未知，不强制重新批准同一语义边界。新快照在同一计划内冻结并重验，字段、旧合法 Apply 兼容及证据限制只在[边界确认细则](boundary-confirmation.md#创建与维护接入)维护。

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

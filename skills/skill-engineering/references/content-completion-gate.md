# Content Completion Gate

Content Completion Gate 是独立于结构 Doctor 的内容完整性检查。结构 Doctor 回答“骨架是否有效”,本门禁回答“候选内容是否真的完成”。存在任一阻断项时,候选不得进入 Apply,用户可见状态保持 `candidate_incomplete`。

## 运行方式

宿主有 Python 时,对隔离候选目录运行随 Skill 交付的 portable checker(仅标准库,无其他依赖):

```bash
python3 scripts/content_gate.py <候选目录> [--json]
```

退出码:`0` 通过;`1` 存在阻断项;`2` 用法错误。

## 确定性阻断规则

| 规则 | 阻断内容 |
|---|---|
| CG000 | `SKILL.md` 不存在 |
| CG001 | 常见待办标记、英文占位词、“承诺以后再写”等占位内容；`tests/` 中用于验证阻断行为的失败语料除外 |
| CG002 | 空的 references、scripts、assets、templates 或 tests 目录 |
| CG003 | 候选残留“只说执行单一职责、没有任务细节”的通用 fallback 语句 |
| CG004 | 文件引用不存在、越界、使用 symlink 或不是候选内普通文件(命令、工具与 delegate 的可解析性由语义检查核验) |
| CG005 | 声明的脚本不存在、内容为空或没有 `tests/self-test.json` 真实运行入口 |
| CG006 | name、description、frontmatter 不符合 Agent Skills 基线，或 name 与候选目录名不一致 |
| CG007 | 有外部副作用却没有预览、审批或停止点 |
| CG008 | 复杂工作流没有失败或部分成功处理 |
| CG009 | 候选包含 symlink、凭证、私钥/证书容器、cookie 或 `.env*` 文件(完整私有对话由语义检查核验) |
| CG010 | `tests/self-test.json` 无效、引用越界、使用非 Python portable 脚本或 timeout/exit contract 无效 |

## Agent-native 等价检查

宿主没有 Python 时,宿主 Agent 必须逐项执行等价检查,并在预览摘要中列出每一项的结果,不得静默跳过:

1. 逐文件通读候选,确认没有占位内容(CG001)和通用 fallback 语句(CG003);
2. 逐个检查资源目录,确认不为空且每个文件有真实内容；声明脚本必须有 self-test manifest(CG002、CG005、CG010);
3. 逐个解析 `SKILL.md` 中引用的相对路径,确认目标是候选根目录内的普通文件且不是 symlink(CG004、CG009);
4. 核对 frontmatter 的 name 与 description 符合基线，且 name 与候选目录名一致(CG006);
5. 确认副作用动作都有预览、审批或停止点(CG007);
6. 确认多步工作流包含失败与部分成功处理(CG008);
7. 检查候选不包含 symlink、`.env*`、凭证、私钥/证书容器、cookie 或私有对话原文(CG009)。

检查结果必须向用户明示“本次使用 Agent-native 等价检查,未运行确定性 checker”。

## 语义检查(宿主 Agent 逐项证明)

确定性规则通过后,宿主 Agent 还必须逐项证明,并把结论写入预览摘要:

- 每个工作流步骤都与用户任务相关;
- 输入可以沿明确路径产生输出;
- 触发和反触发能够区分相邻任务;
- 用户提供的关键约束都落在候选文件中;
- 每个资源文件有明确读取或执行入口;
- 失败状态不会被包装成完整成功;
- 生成内容不是把 Authoring Brief 改写成更长的泛化 Prompt;
- 引用的命令、工具和 delegate 都可以解析(确定性检查只覆盖文件路径);
- 声明的脚本都有对应的验证入口(运行测试或自测命令);
- 候选不包含完整私有对话原文。

语义检查结果进入预览摘要,但不能冒充真实行为效用。

## 与既有体系的关系

- 本门禁在 preview/apply 之前运行;结构 lint/Doctor 与创建评审在写入后运行;
- 旧 flag-based `create` fallback 输出标记为 `scaffold_only`,不要求通过本门禁,但不得产生“完整创建成功”的用户反馈;
- 候选通过本门禁只证明内容完整性,不证明真实任务效果;真实效果由创建后自动化测试与真实试用验证。

# 宿主共同能力契约

Native Authoring Kernel 不按宿主品牌编写多套作者方法。它只依赖以下共同能力;任何支持 Agent Skills 的宿主,只要具备这些能力就能完成核心创建闭环:

1. 读取项目规则和已有 Skill;
2. 创建隔离候选目录;
3. 展示候选内容或 diff;
4. 请求用户确认;
5. 创建目录和文件;
6. 运行可用的基础检查;
7. 读取写后结果。

有 Python 的宿主共同使用 `scripts/native_plan.py` 的
`preview → apply → verify`，plan 绑定已经保存并脱敏的 Brief id、候选 manifest
与正式 target。没有 Python 的宿主必须执行 Agent-native 等价清单，展示同一文件
清单和 fingerprint 事实，并在确认后按这份未漂移事实写入；不得只依赖聊天记忆。

## 适配原则

- 同一 Authoring Brief 在所有宿主中生成的核心文件语义保持一致;只有路径、工具调用和可选元数据允许发生宿主适配;
- 宿主缺少某项能力时,按 `references/content-completion-gate.md` 的 Agent-native 等价路径降级,并向用户明示降级了什么;
- 宿主不支持某项可选元数据(如 UI 展示配置)时保留共同基线,不伪造支持;
- 新增宿主:在本目录新增一份 adapter reference,不修改 Native Authoring Kernel 和其它 adapter;
- 用户要求共享或全局范围时,先展示实际目标和影响,确认后才写入。

# Skill 自然语言与模糊语义激活需求

状态：本地实现、独立评审、真实宿主路由与安装复验完成；未发布。

[当前任务](../TASK.md) · [实施计划](../plans/2026-10-29-implicit-skill-activation-plan.md) · [专项迭代](../sprints/2026-10-29-implicit-skill-activation.md) · [架构决定](../adr/0012-intent-first-skill-activation.md) · [验证记录](../testing/2026-10-29-implicit-skill-activation.md)

## 目标与授权

用户明确恢复自动激活优化：创建、维护或检查Agent Skill时，无需提及skill-engineering名称，也应能按自然语言、口语和上下文省略进入对应流程。名称优化继续挂起，保留既有对外身份、显示名称和显式调用方式。

本轮只维护既有Skill的发现与入口，不新建Skill、自然语言分类器、全局路由系统或模型执行产品。正式版本仍为1.1.0，当前为未发布增量；不扩展其他Sprint，不沿用前轮commit/push授权。

## 发现与方案

当前allow_implicit_invocation已经为true，问题不能靠再次打开同一开关解决。宿主预加载名称、描述和路径，选择后才读正文；描述过长时会截短，现有描述先放品牌和显式名字，核心意图偏后。官方Creator与本Skill存在创建/修改的发现重叠。

只追加正文提醒不能解决首次发现；改写全局AGENTS或官方Creator会扩大作用范围。采用核心意图前置的紧凑描述、可移植的模糊上下文澄清规范、同源contract/UI元数据与正反例，并以真实宿主选择trace验证。保持现有安装范围，不写全局配置、第三方Skill或虚构priority字段。

## 行为合同

- 创建：新建、编写、封装可复用Agent Skill/技能包/AI指令流程；不要求特定产品名或固定激活词。进入既有发现与Native Authoring，信息不全先澄清，不自动新建。
- 维护：修改、补能力、升级、重构、处理越改越乱或调用失败；上下文已确定目标为Skill时，省略名字、口语或近义表达也进入原维护流程。架构声明与双门不变。
- 检查：检查、评审、体检、测试、排查Skill边界、触发、架构或行为；沿用现有检查/评测能力，区分静态结构与实际效果。
- 模糊意图：对象可由上文、已提供文件或路径确认时，先按已有Skill上下文承接，再澄清动作或缺失输入；对象仍未知时问一个必要问题，不能把模糊性解释为创建、写入或发布批准。
- 反例：使用现成领域Skill做业务、一般代码/文案检查、学习某种技能或解释概念，不据此强制进入本Skill。仅项目harness/tmux/开工自检仍按原反触发。
- 用户显式指定其他工具/Skill时尊重该选择；本Skill不能靠正文声称已覆盖宿主选择器或抢占所有请求。

## 范围与实现落点

修改SKILL.md的预加载description及薄路由、agents/openai.yaml的界面摘要、skill.contract.yaml的触发合同，增加单一activation-routing参考与包内开发案例，复用file-map和既有测试。保持唯一顶层身份，不增加别名、安装根或第二套执行链。

确定性测试核对元数据、截短后的关键意图、案例结构/注册及反触发规则；不能把关键词断言或模型自报当作自然语义效果证明。真实宿主验证使用隔离项目、一次性配置和ephemeral会话，不读取或复制auth，不修改全局配置，不执行候选写入。

## 验收

1. 预加载描述的前部同时呈现创建、维护、检查与Agent Skill对象；allow_implicit_invocation保持true，名称和显式调用不变。
2. 开发正反例与独立holdout分别保存、冻结，候选生成者不接收holdout断言或baseline成绩；不包含真实敏感用户对话。
3. 用不含产品名或指定读取路径的自然语言，在真实Codex宿主观察成功读取待测根SKILL.md正文的trace；仅catalog、列目录或自报不计为激活。官方Creator保留在竞争集合，不以禁用它制造通过。
4. 验收样本覆盖三意图、语义近邻、上下文省略、对象未知澄清和业务/普通任务反例；明确实际次数、失败和限制，不声称覆盖所有自然语言或所有宿主。
5. 隔离候选、独立架构审查、同一维护计划Apply/Verify；同步既有安装内容并保留原目录的其他未提交内容，不扩大暴露范围。
6. pytest、Ruff、Skill validation、Content Gate、production Doctor、自测、credential lint、diff与文档引用检查通过，Task/Sprint/Backlog/文档状态如实回填。

[官方发现与隐式调用说明](https://learn.chatgpt.com/docs/build-skills) · [已有工程流程](../PRODUCT.md#用户需求流程)

## 源码交付授权补充

用户于2026-10-29另行明确授权本轮commit、push与相关文档对齐。实现合同和正式版本不变，仅交付本轮独立增量；名称优化继续暂缓，不创建Tag或正式Release。实际提交与远端核验以[源码交付记录](../testing/2026-10-29-implicit-skill-activation.md#源码提交与推送收尾)为准。

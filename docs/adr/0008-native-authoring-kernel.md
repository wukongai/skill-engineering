# ADR-0008：Native Authoring Kernel 取代外部 Creator 委托

状态：Accepted

日期：2026-07-29

## 背景

1.0 的创建链路把“完整内容生成”委托给官方 `skill-creator`（`SKILL.md` 创建路由：“官方 `skill-creator` 可用时委托标准 Skill 内容生成”），宿主缺少 Creator 时退化为确定性脚手架。真实使用（Hermes）证明这条边界是产品错误：用户只得到通用骨架，宿主却把“骨架结构有效”报告为“Skill 已完整创建”。

同时，普通用户被要求完成第二次安装（Creator 或独立 Python CLI）才能走完创建流程，违背“只安装 Skill Engineering”的产品承诺。

## 决策

1. Skill Engineering 1.1 在自身包内拥有完整作者方法（Native Authoring Kernel），不再把官方 `skill-creator`、Hermes 专用作者 Skill 或任何宿主专用 Creator 作为创建依赖。
2. Kernel 只依赖宿主共同能力（读取项目规则、创建隔离候选、展示 diff、请求确认、创建目录和文件、运行基础检查、读取写后结果），不按宿主品牌复制作者逻辑；新增宿主通过 capability adapter reference 扩展，不修改 Kernel。
3. 创建主链路固定为：Authoring Brief → 架构选择 → 完整候选 → Content Completion Gate → 预览 → 确认写入 → postflight → 创建评审与评分 → 简易自动化测试入口。
4. 创建评审复用 Doctor v2 与 `quality-score-standard`，不新建第二套评分模型；分数只表述为结构和工程就绪度，未做真实任务试用前必须明示“尚未验证实际任务效果”。
5. 旧 flag-based `create` fallback 保留但标记 `scaffold_only`，不得产生“完整创建成功”的用户反馈；1.0 CLI/JSON/contract 保持兼容读取，旧计划不静默升级为 `content_complete`。
6. 现有 Python 包继续服务高级开发、CI、评测和发布，但不是普通用户完成核心创建的前置依赖。

## 与既有 ADR 的关系

- 不推翻 ADR-0004/0007 的标准安装决策；本 ADR 决定标准安装产物自身必须包含创建闭环所需的可移植资源，不依赖仓库外文件。
- 与 ADR-0002（v2 Blueprint/IR 边界）正交：Native Authoring 是创建事实层，Blueprint 是架构事实层；1.1 不为创建建立第二套 Blueprint 模型。

## 备选方案

- **继续委托官方 skill-creator**：拒绝。制造第二次安装依赖，且在无 Creator 宿主退化为骨架并误报完成。
- **要求宿主专用作者 Skill（如 Hermes `/learn`）**：拒绝。把产品核心能力绑定到单一宿主。
- **把完整生成放进 Python CLI**：拒绝。违背“只安装 Agent Skill 即可完成创建”的单安装原则；CLI 继续作为高级入口。

## 后果

- 标准安装产物必须包含 Kernel 指令、adapter references、内容完整性检查器和 portable 检查资源；
- 主 Skill 与 contract 中不再存在 official skill-creator delegate；
- 任何占位、空资源、通用 fallback 或断链引用都会阻断 Apply；
- `2.0 Architecture Guardian Phase 1` 在 1.1 期间暂停，1.1 发布后恢复。

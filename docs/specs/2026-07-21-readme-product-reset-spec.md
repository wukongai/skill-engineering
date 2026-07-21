# README 产品叙事重置规格

状态：Implemented and verified

日期：2026-07-21

## 背景

上一版双语 README 错把“个人选题 Skill 改造”文章当成 Skill Engineering 的核心叙事，导致选题雷达占据产品 Why；同时把 Python CLI 与 Agent Skill 并列为普通用户的双交付物。用户确认正确来源应为《把 Skill 做稳：我开源了 Skill Engineering 1.0》，并要求完全重写。

## 正确产品定位

Skill Engineering 面向只需要描述工作目标的用户，帮助他们判断是否需要 Skill，并把 Skill 从第一次创建开始做成边界清楚、能真实使用、以后也不会越改越乱的长期能力。

核心价值不是生成更多 Prompt，而是：

- 写入前说清职责、触发边界、输出、停止条件和副作用；
- 按风险选择最小但完整的结构；
- 正式修改前预览，未经确认不覆盖；
- 把真实失败转成根因修复与长期回归证据；
- 保留验证、恢复和继续维护路径。

## 用户入口与运行边界

- 普通用户的唯一主入口是 Agent Skill；
- README 首屏只主推标准 `npx skills add` 安装；
- 不要求普通用户先理解或手动学习 CLI；
- Python core/CLI 仅作为当前 1.x 的确定性运行内核、自动化与兼容接口说明，不得与 Agent Skill 并列营销；
- 对当前部分深度操作仍需要 Python runtime 的事实必须如实说明，但放在“当前运行边界”或维护者章节；
- 源码 clone 只面向源码学习、二次开发、测试和贡献。

## README 信息架构

中文 `README.md` 与英文 `README.en.md` 使用同等结构：

1. 语言切换、稳定版本、许可证与一句话价值；
2. 标准 Agent Skill 安装；
3. 安装后可以直接说的创建与维护请求；
4. 为什么需要 Skill Engineering：从“写出来”到“长期可信”；
5. 1.0 完整生命周期和五项产品原则；
6. 四个已验证 Use Case，其中会议纪要作为展开案例；
7. 1.0、2.0 与 3.0 前瞻；
8. 发布证据、当前边界、运行内核与本地开发；
9. 文档、许可证、贡献和安全。

## Use Case 要求

- 会议纪要：轻量结构、触发边界、原文证据、待确认、预览和根因修复；
- GitHub Issue：只读分析与外部写操作审批边界；
- 本地 Web 应用验收：Skill 与确定性脚本分工，并保留截图、CSV、JSON、Markdown 证据；
- 多文件研究证据包：复杂结构、失败回滚、重新规划和风险匹配；
- 所有案例链接到 `docs/testing/2026-07-18-v1-use-cases.md`，不夸大为跨所有模型的通用效用。

## 版本事实

- `1.0.0`：已正式发布的 Stable Lifecycle Contract；
- `2.0.0`：Architecture Guardian 开发预览；
- `3.0`：从真实使用中持续进化的长期前瞻，尚未形成发布承诺；
- 不把当前 Backlog 或 Preview 写成已经交付。

## 验收标准

- [x] 两份 README 完全移除选题雷达主叙事；
- [x] 第一个主体章节是 Agent Skill 安装；
- [x] 普通用户安装区只展示标准 `skills` 安装路径；
- [x] CLI 不再作为普通用户第二产品入口；
- [x] 四个 1.0 Use Case 成为核心证据；
- [x] 1.0/2.0/3.0 的状态准确；
- [x] 中英文的结构、命令、案例和边界一致；
- [x] 本地链接、Markdown 围栏和现有稳定文案回归通过；
- [x] pytest、Ruff、Skill validation、credential lint 和 diff check 通过。

## 非目标

- 本轮不删除 Python CLI、不改变 1.x 兼容契约；
- 不修改 Agent Skill、Python 实现、版本号或 Release；
- 不提交、不推送、不发布。

# Roadmap

Roadmap 描述版本方向，不代表所有条目都已经承诺。当前承诺以 `TASK.md` 和 Sprint 为准。

## v0.1 Public Beta：可对外交付的本地闭环

- 判断 Skill 是否值得创建；
- 从第一版开始按最小架构和安全边界快速生成完整候选；
- 同一创建计划 Apply 与 postflight；
- 静态 Doctor、确定性行为评测；
- 防腐化维护、历史、验证和撤销；
- 自进化候选、Pareto、Shadow/Canary/Active；
- 傻瓜式 Skill Guide 交互；
- 自举文档、版本和 CI。

## v0.2：Architecture Guardian

- 三轴 Blueprint：组件角色、执行拓扑、治理等级；
- 语义 Diff 和架构适应度；
- 依赖、冲突、重复职责和 context budget 检查；
- 自动拆分、迁移、压缩和废弃候选；
- 创建记录与安全撤销。

## v0.3：Behavior Eval Lab

- provider-neutral rollout runner；
- without-skill vs with-skill；
- trigger、pressure、multi-turn、compaction/resume 评测；
- 盲评和跨模型/harness 矩阵；
- fast PR、nightly 和 release 评测分层。

## v0.4：Skill Portfolio & Distribution

- 与 Agent Skill Hub 的 registry/profile/adapter 契约统一；
- Skill Atlas、owner、版本、依赖和 route collision；
- 安装模拟、升级兼容和供应链证据。

## v1.0：稳定商业/工业级生命周期

- 稳定 Blueprint 和插件接口；
- 团队审批、审计和策略；
- 版本迁移和兼容承诺；
- 可复现跨模型证据；
- 稳定公开文档和发布流程。

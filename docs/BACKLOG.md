# Backlog

Backlog 保存尚未进入当前 Sprint 的候选能力。进入实现前必须升级为 Spec、Plan 和 Task。

Blueprint/IR 与 Architecture Guardian 已经从 Backlog 升级到当前 `v2.0 Phase 1` Sprint；不要在 Backlog 中重复承诺同一范围。

## P0：Public Beta 后立即评估

- 创建成功记录、历史和安全撤销；
- v2.0 之后的跨版本 Blueprint schema migration；
- v2.0 之后的多仓库架构适应度和语义 Diff 扩展；
- Skill Guide 自身的固定 baseline/candidate 行为报告；
- GitHub 发布、wheel 构建和安装 smoke 自动化；
- 修复/验证非 production suite 无 high-risk case 的报告格式边界。

## P1：工程深度

- trigger precision/recall、near-neighbor 和 adversarial cases；
- 可审计 suppression/baseline：理由、owner、到期、profile 和 stale finding 复核；
- 可选 OSV 依赖漏洞查询与离线 fallback；
- MCP least-privilege、tool poisoning 和 rug-pull contract/扫描；
- 可信 Git/URL/zip 输入解析与来源验证；
- provider-neutral rollout runner；
- pressure/rationalization 和 multi-turn eval；
- state schema migration、并发锁、retention 和 export/import；
- Skill dependency graph、owner、stale 和冲突检测的多项目/Portfolio 扩展；
- metadata-only telemetry 与 adoption drift；
- 安装模拟、包校验和升级兼容。

## P2：产品与商业能力

- Review Studio；
- 托管评测矩阵；
- 团队工作区、RBAC、审批和 waiver；
- 私有部署、审计、策略和 SLA；
- 训练营模板、案例库和 Skill 工程认证；
- 对外 benchmark 与年度 Skill 工程报告。

## 明确不做

- 自动 Global 安装；
- 自动公开 push/publish；
- 保存原始私有对话或凭证；
- 用单一静态分数宣称 Skill 真实效果；
- 让所有简单 Skill 使用完整商业项目结构。

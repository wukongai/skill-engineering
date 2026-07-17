# Backlog

Backlog 保存尚未进入当前 Sprint 的候选能力。进入实现前必须升级为 Spec、Plan 和 Task。

Blueprint/IR 与 Architecture Guardian 已经从 Backlog 升级到当前 `v2.0 Phase 1` Sprint；不要在 Backlog 中重复承诺同一范围。

## 2026-07-16 Review Closure

- NVIDIA/SkillSpector 对比、AST/source-to-sink/SARIF 吸收和 0.1.1 验证已完成，不再作为 Backlog 候选。
- 2.0 Phase 1 尚未完成的 fixture、只读 inventory 和 evidence 收口属于当前 Sprint，已记录在 [`v2 Phase 1 Handoff`](handoffs/2026-07-16-v2-phase1-next.md)，不重复塞入 Backlog。
- tag、公开发布、1.0 稳定契约和更远期架构扩展仍保留各自的发布门禁或下方候选，不视为本次 review 已完成。
- 版权与安装边界已升级为 v1.0 发布前置项，事实源为 `docs/guides/licensing-and-installation.md`、对应 Spec/Plan 和 ADR 0004；不在 Backlog 重复拆分。

## P0：Public Beta 后立即评估

- Agent Skill-only 安装后的 runtime 自检与 bootstrap：明确 `doctor_skill.py` 在未安装 Python CLI 时的行为，选择自包含实现、依赖检测与友好提示或双轨一键安装；进入实现前另建 Spec/Plan，不重新打开已完成的标准安装文档任务；
- 创建成功记录、历史和安全撤销；
- v2.0 之后的跨版本 Blueprint schema migration；
- v2.0 之后的多仓库架构适应度和语义 Diff 扩展；
- Skill Engineering 自身的固定 baseline/candidate 行为报告；
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
- Yao Meta/Superpowers pinned-source 复核与本地五模式清单维护（`2.1+`，仅研究维护，不重复承诺当前 Guardian Sprint）；
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

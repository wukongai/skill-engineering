# Skill Engineering 文档入口

本目录是产品、架构、版本和交付状态的事实源。聊天记录、临时 TODO 和根 `SKILL.md` 不得替代这里的正式工件。

## 当前版本

- 产品定位：[`PRODUCT.md`](PRODUCT.md)
- 长期原则：[`constitution.md`](constitution.md)
- 当前架构：[`architecture.md`](architecture.md)
- 版本规则：[`VERSIONING.md`](VERSIONING.md)
- 版权与安装：[`guides/licensing-and-installation.md`](guides/licensing-and-installation.md)
- 功能总表：[`FEATURE-MATRIX.md`](FEATURE-MATRIX.md)
- 发布日志：[`releases/RELEASE-LOG.md`](releases/RELEASE-LOG.md)
- 当前任务：[`TASK.md`](TASK.md)
- 路线图：[`ROADMAP.md`](ROADMAP.md)
- 后续候选：[`BACKLOG.md`](BACKLOG.md)
- 当前 Sprint：[`sprints/2026-07-v2.0-architecture-guardian.md`](sprints/2026-07-v2.0-architecture-guardian.md)
- 当前 Handoff：[`handoffs/2026-07-16-v2-phase1-next.md`](handoffs/2026-07-16-v2-phase1-next.md)
- Apache-2.0 收口证据：[`testing/2026-07-18-apache-2.0-license-closeout.md`](testing/2026-07-18-apache-2.0-license-closeout.md)
- V0.1 Spec：[`specs/2026-07-13-v0.1-public-beta-spec.md`](specs/2026-07-13-v0.1-public-beta-spec.md)
- V0.1 Plan：[`plans/2026-07-13-v0.1-public-beta-plan.md`](plans/2026-07-13-v0.1-public-beta-plan.md)
- V1.0 Spec/Plan：[`specs/2026-07-16-v1.0-stable-contract-spec.md`](specs/2026-07-16-v1.0-stable-contract-spec.md) / [`plans/2026-07-16-v1.0-stable-contract-plan.md`](plans/2026-07-16-v1.0-stable-contract-plan.md)
- V2.0 Spec/Plan：[`specs/2026-07-16-v2.0-architecture-guardian-spec.md`](specs/2026-07-16-v2.0-architecture-guardian-spec.md) / [`plans/2026-07-16-v2.0-architecture-guardian-plan.md`](plans/2026-07-16-v2.0-architecture-guardian-plan.md)
- Apache-2.0 与署名 Spec/Plan：[`specs/2026-07-18-apache-2.0-attribution-spec.md`](specs/2026-07-18-apache-2.0-attribution-spec.md) / [`plans/2026-07-18-apache-2.0-attribution-plan.md`](plans/2026-07-18-apache-2.0-attribution-plan.md)
- 当前许可证决策：[`adr/0006-apache-2.0-attribution-and-brand-boundary.md`](adr/0006-apache-2.0-attribution-and-brand-boundary.md)（取代历史 ADR 0005；安装器入口见 [`adr/0004-standard-skill-cli-install.md`](adr/0004-standard-skill-cli-install.md)）

## 长期记录

- `adr/`：跨版本架构决策。
- `logs/daily/`：当天事实、验证和未解决问题。
- `testing/`：可复现的端到端验收证据。
- `guides/`：对外工程标准。
- `references/`：模板和机器接口参考。
- `superpowers/`：仓库拆分前形成的历史 spec/plan；保留作为证据，新增工作使用 `docs/specs/` 与 `docs/plans/`。

## 更新规则

1. 功能级改动先更新 Spec 和 Plan。
2. 当前承诺放 `TASK.md` 和当前 Sprint，不把所有想法都塞进版本。
3. 尚未承诺的能力放 `BACKLOG.md`。
4. 跨版本架构取舍写 ADR。
5. 当天过程写 Daily Log；稳定规则升级到正式文档后，Daily Log 不再作为执行入口。
6. 发布前对齐 README、版本、Changelog、Roadmap、Task、Sprint 和测试证据。

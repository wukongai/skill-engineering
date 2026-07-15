# Skill Engineering 文档入口

本目录是产品、架构、版本和交付状态的事实源。聊天记录、临时 TODO 和根 `SKILL.md` 不得替代这里的正式工件。

## 当前版本

- 产品定位：[`PRODUCT.md`](PRODUCT.md)
- 长期原则：[`constitution.md`](constitution.md)
- 当前架构：[`architecture.md`](architecture.md)
- 当前任务：[`TASK.md`](TASK.md)
- 路线图：[`ROADMAP.md`](ROADMAP.md)
- 后续候选：[`BACKLOG.md`](BACKLOG.md)
- 版本规则：[`VERSIONING.md`](VERSIONING.md)
- 当前 Sprint：[`sprints/2026-07-v0.1-public-beta.md`](sprints/2026-07-v0.1-public-beta.md)
- V0.1 Spec：[`specs/2026-07-13-v0.1-public-beta-spec.md`](specs/2026-07-13-v0.1-public-beta-spec.md)
- V0.1 Plan：[`plans/2026-07-13-v0.1-public-beta-plan.md`](plans/2026-07-13-v0.1-public-beta-plan.md)

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

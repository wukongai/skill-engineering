# ADR-0001：Skill Engineering 使用自身生命周期治理自身

状态：Accepted

日期：2026-07-13

## 背景

Skill Engineering 的目标是防止 Skill 在反复修改后架构腐化。如果项目自身仍依靠聊天记忆、零散 TODO 和临时规则推进，它无法证明这套方法能长期工作。

## 决定

项目建立 Product、Constitution、Architecture、Roadmap、Backlog、Task、Spec、Plan、ADR、Sprint、Daily Log、Changelog 和测试证据层。

根 `SKILL.md` 只保留触发、路由、停止点和用户契约；项目管理细节由 reference 和仓库文档承接。

功能级修改必须先有 Spec 和 Plan，再在隔离候选中实现，通过 maintenance plan 应用到真实源。

## 理由

- 让产品边界和实现保持可追踪；
- 防止事故和临时偏好进入稳定入口；
- 为训练营和开源贡献提供可复制示范；
- 让 Skill Engineering 成为自己的第一个长期维护案例。

## 影响

- 文档数量会增加，但按职责分层并有索引；
- 简单下游 Skill 不会被强制复制本仓库的完整结构；
- 后续需要用 Doctor 或专门规则持续检查文档漂移。

## 替代方案

继续只使用 README 和聊天记录。该方案无法支持多版本、多人协作和公开交付，因此拒绝。

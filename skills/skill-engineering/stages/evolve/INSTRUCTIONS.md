# Evolve 阶段

用户要求 Skill 根据运行失败、纠正或成本信号自动进化时使用。

1. 读取 `references/evolution-standard.md` 与 `references/evaluation-standard.md`。
2. 将真实运行结果整理为脱敏 SkillRun,逐条运行 `skill-engineering evolution record-run`。
3. 运行 `evolution propose`;证据不足时保留 observe 状态并说明还缺什么。
4. 运行 `evolution build-dataset`,确认 development/holdout 隔离和 success/failure/high-risk coverage。
5. 运行 `evolution prepare-candidates`。逐个读取 CandidateJob,只修改对应 `source/`,不得查看 evolution state 中的 holdout 数据。
6. 对每个候选运行 `evolution register-candidate`;门禁失败的候选直接淘汰。
7. 使用真实 Agent rollout 或可信 harness 生成 baseline/candidate result artifact,再运行 `evolution submit-results`。
8. 运行 `evolution select`;把 Pareto 推荐候选的 diff、复杂度和行为证据讲清楚。
9. 对选定候选运行 `evolution version`;版本自动进入 Shadow。
10. 需要 Canary/Active 时生成 `release-plan`,展示范围、before/after、验证和回滚后暂停。
11. 用户明确批准后运行 `release --plan ID --apply`,随后返回 ReleaseRecord、验证结果和 `release-rollback` 入口。

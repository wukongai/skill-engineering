# Skill 自进化 A3 操作标准

## 目标

A3 让 Skill 根据真实失败、用户纠正和运行证据形成多个改进候选,自动完成确定性门禁、行为比较、压缩选择与 Shadow;同时把 Canary/Active 保留为可审计、可批准、可验证、可回滚的发布动作。

它不是让 Skill 直接修改自己。它把“学习”拆成证据、候选、评测、版本、发布五个可追踪对象,避免 Skill 在持续修改中越来越乱。

## 自动化边界

| 阶段 | 默认行为 | 写入真实使用面 |
|---|---|---|
| Observe / Proposal | 自动 | 否 |
| Dataset / CandidateJob | 自动 | 否 |
| 宿主 Agent 生成隔离候选 | 自动 | 只写候选工作区 |
| lint / Doctor / behavior / Pareto | 自动 | 否 |
| immutable version / Shadow | 自动 | 只写本机版本库与 Shadow 指针 |
| Canary | 先计划、后批准 | 是,仅指定窄项目 |
| Active | 先计划、后批准 | 是,更新 maintained source |
| Global | 不自动支持 | 否 |

## 证据输入

每条 SkillRun 最少包含 Skill 路径、脱敏任务/结果摘要、outcome、failure tags、privacy、leakage group。要进入可评分数据集还必须有确定性 `expected`,例如 status、contains、not_contains、regex 或 JSON equality。

不要写入 token、cookie、私钥、完整会话、敏感原文。`privacy=sensitive` 时摘要会被抹除,并禁止保存 expected。

```bash
skill-engineering evolution record-run --input run.json
skill-engineering evolution propose --skill /path/to/skill
```

三条同类失败/纠正、一条 high-risk failure 或显式 `--force` 才形成 Proposal。证据不足保持观察,不触碰 Skill。

## 数据与候选

```bash
skill-engineering evolution build-dataset --proposal PROPOSAL_ID
skill-engineering evolution prepare-candidates --proposal PROPOSAL_ID
```

同一 leakage group 不跨 development/holdout;至少两个独立 group。系统创建 minimal-patch、layer-move、compaction、resource-or-script 四个隔离工作区。宿主 Agent 读取各自 `candidate-job.json`,只修改同目录 `source/`。

候选能看到 development evidence,看不到 baseline 评分结果与 holdout assertions。

## 评测与选择

```bash
skill-engineering evolution register-candidate --job CANDIDATE_ID
skill-engineering evolution submit-results \
  --candidate CANDIDATE_ID \
  --baseline-results baseline.json \
  --candidate-results candidate.json
skill-engineering evolution select --proposal PROPOSAL_ID
```

登记先执行 lint、Doctor 和复杂度度量。行为 results 必须来自真实 Agent rollout、可信 harness 或确定性测试工具。负迁移、holdout 或 high-risk 失败会淘汰候选。

系统使用 Pareto dominance 比较效用、风险与复杂度;并列时保留多个推荐,不制造一个没有依据的总分。

## 版本与发布

```bash
skill-engineering evolution version --candidate CANDIDATE_ID --label 1.1.0
skill-engineering release-plan \
  --version VERSION_ID \
  --channel active \
  --active-source /path/to/skill
```

只有 recommended 候选可以版本化。版本目录不可变,创建后自动进入 Shadow。

Release Plan 展示完成后暂停。用户批准同一 plan id 才执行:

```bash
skill-engineering release --plan RELEASE_PLAN_ID --apply
skill-engineering release-verify --record RELEASE_RECORD_ID
skill-engineering release-rollback --record RELEASE_RECORD_ID --apply
```

Canary 复用安装记录,Active 复用持续维护记录。版本、channel、target 或 plan hash 漂移时旧计划失效,必须重建。

## 可以宣称什么

通过 A3 只能说明候选在当前有哈希的 baseline/holdout 数据与门禁下优于或不劣于基线。没有长期 Shadow、跨模型和真实业务数据时,不能宣称普遍效果提升。

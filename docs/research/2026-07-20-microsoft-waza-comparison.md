# Microsoft Waza 与 Skill Engineering 行为评测体系对比研究

## 对比基线

- 上游仓库：[`microsoft/waza`](https://github.com/microsoft/waza)
- 上游 commit：[`cf05e487ed967d497a138738514d24457bc45f2a`](https://github.com/microsoft/waza/tree/cf05e487ed967d497a138738514d24457bc45f2a)
- 上游 tag：`v0.38.3`
- 上游许可证：MIT
- 快照日期：2026-07-20
- 本地项目：Skill Engineering `1.0.0` Stable；`2.0.0` Architecture Guardian Phase 1 开发预览

用户最初记忆的名称是 “skilled spectrum” 或相近拼法。公开检索未发现与描述吻合的微软官方同名项目；实际对应项目高度确定为 `microsoft/waza`。`microsoft/skills` 是技能、Agent、MCP 配置和贡献生态，Waza 则是为 Skill 创建、测试、评测和 CI 提供工具的工程平台，是本次真正需要比较的对象。

## 调研目标

本次调研只回答以下问题：

1. Waza 的产品定位、核心能力和使用时机是什么；
2. Waza 的真实执行、A/B、grader、统计、CI、安全和证据结构如何工作；
3. Skill Engineering 现有评测已经拥有什么，缺少什么；
4. 哪些能力值得学习并用本项目风格重新实现；
5. 哪些实现、依赖和信任假设不应复制；
6. 后续如何拆成新的 Backlog 与独立实现任务。

## 调研方法

1. 核实官方组织、仓库、README、PRD、Changelog、许可证和当前 release；
2. 固定不可变上游 commit，不以浮动 `main` 作为结论依据；
3. 读取 CLI、runner、baseline、grader、gate、snapshot、redaction、adversarial、dashboard 和测试源码；
4. 将公开产品描述与实际主执行路径交叉核对，避免把设计文档或未使用代码误当成交付能力；
5. 对照本项目 `evaluation.py`、评测标准、公开契约、Roadmap 和真实 E2E；
6. 分开报告结构健康、证据覆盖和真实任务效用，不因静态源码审计宣称下游效果；
7. 采用 clean-room 原则：只学习公开行为、数据形状和工程取舍，不复制上游源码或测试实现。

## 调研限制

- 本轮没有安装 Waza release，也没有调用 Copilot、BYOK provider 或真实模型；
- 没有用同一个 Skill 在 Waza 和 Skill Engineering 上运行对照实验；
- 没有验证 Waza dashboard、Azure Storage 或远程 CI 的运行时稳定性；
- 因此本报告可以确认源码级产品能力和架构边界，不能证明 Waza 或 Skill Engineering 的实际任务效用高低。

## Waza 是什么

Waza 可以概括为：

> 面向 Agent Skill 的自动化测试、A/B benchmark、grader、CI gate 和结果分析平台。

它主要供 Skill 作者、评审者和 CI 维护者使用，不是普通用户日常调用 Skill 的运行入口。它回答的是：

- Skill 是否被正确触发；
- Skill 是否比不加载 Skill 更有效；
- 修改后是否退化；
- 换模型后是否仍然稳定；
- Agent 是否产生了正确文件、工具调用和行为轨迹；
- 结果是否达到 CI 和发布门槛。

## 上游主要能力

| 能力域 | Waza 当前能力 | 证据位置 |
|---|---|---|
| Scaffold | 创建 Skill、eval、task 和 CI 基础结构 | `cmd/waza/cmd_new.go`、`cmd/waza/cmd_init.go` |
| Real runner | 通过 Copilot SDK 和内置 Copilot CLI 执行真实 Agent，支持 BYOK | `internal/execution/` |
| A/B baseline | 同一任务先运行有 Skill，再清空 Skill 路径运行无 Skill基线 | `internal/orchestration/runner.go` |
| Multi-trial | 多次运行、flaky 统计、并发 worker | `internal/orchestration/`、`internal/statistics/` |
| Graders | text、file、diff、JSON Schema、program、inline code、prompt、behavior、tool、action sequence、skill invocation、trigger | `internal/graders/`、官方 Grader 文档 |
| LLM judge | independent 与 pairwise judge；pairwise 交换位置检查位置偏差 | `internal/graders/prompt_grader.go` |
| Regression gate | baseline/current 通过率、golden task、新增/删除任务策略、稳定退出码 | `cmd/waza/cmd_gate.go` |
| Adversarial | prompt-injection、scope-bypass 对抗包 | `internal/adversarial/` |
| Snapshot/replay | 保存输入、fixture digest、轨迹并重放，比较工具名与参数 fingerprint | `internal/snapshot/` |
| Privacy | 默认凭证、私钥、认证头、JWT、邮箱脱敏；环境变量默认拒绝敏感 key | `internal/snapshot/redaction.go` |
| CI/reporting | JSON、JUnit、GitHub comment、dashboard、OpenTelemetry | `internal/reporting/`、`internal/telemetry/`、`web/` |
| Interfaces | CLI、MCP server、JSON-RPC、Web API | `cmd/waza/`、`internal/mcp/`、`internal/jsonrpc/` |

## Waza 的 A/B 到底是什么

Waza 主执行路径中的 `--baseline` 是：

```text
同一个 eval suite、模型、任务和 grader
  -> PASS 1：加载 Skill
  -> PASS 2：清空 SkillPaths / RequiredSkills
  -> 比较每个任务和总体通过率
```

这能回答“有 Skill 是否优于没有 Skill”。它支持多 trial，并在主结果中保留 skill impact。

需要区分三个边界：

1. 执行顺序固定为先有 Skill、后无 Skill，没有随机化或 counterbalance；
2. 整个 suite 对开发过程可见，未发现独立 development/holdout 泄漏隔离模型；
3. 仓库另有一个按质量、token、轮次和时间加权的 `internal/baseline` 包，但没有被主执行路径引用，不能把它当作当前 `waza run --baseline` 的正式行为。

## Skill Engineering 原来已经有什么

当前 `src/skill_engineering/evaluation.py` 已经实现了结果比较和接受判断：

- 读取同一 suite 的 baseline 与 candidate 外部结果；
- development / holdout 分割；
- success / failure / high-risk case；
- status、contains、not-contains、regex、JSON path 确定性断言；
- candidate pass rate、holdout pass rate、high-risk pass rate、delta 和 negative transfer gate；
- suite、baseline、candidate 的 SHA-256 与 subject fingerprint；
- 缺失结果为 `not_evaluated`，整体为 `inconclusive`；
- production suite 强制 holdout 和完整 case category。

当前能力本质是：

> 已有 A/B 结果比较器、证据校验器和发布裁判，但没有自动产生这些结果的真实行为测试引擎。

现有结果仍需由外部 Agent rollout、可信 harness 或确定性工具生成。`evaluate` 不启动模型、不创建实验矩阵、不收集工具轨迹，也不执行 suite 中的 command/script。

## 关键差距

| 维度 | Skill Engineering 现状 | 需要补齐 |
|---|---|---|
| 实验执行 | 读取外部结果 | provider-neutral runner protocol 与 runner adapter |
| A/B | baseline/candidate 结果比较 | without-skill/current/candidate 自动实验矩阵 |
| Trial | 每 case 一条 BehaviorRun | 多 trial、retry、并发、flaky 和置信区间 |
| Workspace | 由外部 harness 决定 | 隔离工作区、fixture、文件变化和清理 |
| Grader | 确定性输出断言 | file/diff/tool/invocation/action/behavior/JSON Schema 等 grader |
| Multi-turn | 无内置 runner | follow-up、responder、checkpoint 和 timeout |
| Cross-model | 无 | 同 suite 多模型矩阵和模型元数据 |
| CI | 评测 decision 可机读 | JUnit、golden regression、稳定退出码和 PR 摘要 |
| Evidence | suite/results hash | trial、trajectory、环境、runner/model、redaction、snapshot/replay |
| UI | CLI/JSON/SARIF | 趋势、比较和轨迹分析界面，放到后续阶段 |

## 采用决策

### 完整学习并重新实现

- provider-neutral behavioral runner protocol；
- without-skill / current / candidate 三主体实验矩阵；
- 多 trial、并发、取消、retry、flaky 和统计置信度；
- 确定性 grader registry；
- tool call、skill invocation、action sequence 和行为预算；
- golden regression gate；
- snapshot、replay、脱敏和环境 allowlist；
- CI reporter 和可追踪 evidence artifact；
- multi-turn、adversarial 和跨模型矩阵；
- 后续结果 dashboard。

### 适配到 Skill Engineering 的既有边界

- 保留 development/holdout、negative transfer 和候选隔离；
- 保留 Doctor 静态 hard gate，不让 LLM judge 覆盖确定性规则；
- 保留 Preview/Apply、maintenance record、verify、undo 和 release approval；
- 保留 provider-neutral 核心，具体模型执行通过 adapter；
- 把 Waza 风格的 runner 结果转换为本项目自己的 versioned artifact，不继承上游 schema；
- 用 capability parity 验收，不追求 CLI、包结构或内部类型的一对一复制。

### 明确不复制

- 不复制 Waza Go 源码、测试代码、内部 prompt 或命名；
- 不嵌入或分发 Copilot CLI；
- 不把 Copilot SDK 设为核心强依赖；
- 不允许静态 compliance score 自动覆盖 Skill；
- 不在默认 profile 执行未知 program grader 或 lifecycle hook；
- 不把单一聚合分数包装成普遍 utility；
- 不把 dashboard、云存储或 MCP server 提前塞入第一个实现切片。

## 目标架构

```text
Evaluation Suite v2
  -> Experiment Planner
     -> without-skill
     -> current skill
     -> candidate skill
  -> Runner Adapter
     -> isolated workspace
     -> task / multi-turn / tools
  -> Grader Registry
     -> deterministic graders
     -> trusted semantic/program graders（显式 profile）
  -> Run Artifact
     -> trials / trajectory / usage / files / redaction
  -> Existing Evaluate Policy
     -> development / holdout / high-risk
     -> negative transfer / golden / confidence
  -> Release Evidence
     -> Shadow / Canary / Active
```

## 研究结论

1. Waza 是成熟的 Skill CI 与行为评测平台，不是完整 Skill 生命周期治理系统；
2. Skill Engineering 原有 A/B 能力真实存在，但只覆盖外部结果的确定性比较与门禁；
3. 需要新增的是自动运行、grader、trial、统计、轨迹、CI 和 replay，不应重写或废弃现有 `evaluate`；
4. 正确路线是完整学习 Waza 的能力结构，在本项目下 clean-room 重写，并把 Waza 视为研究基线而不是运行依赖；
5. 新能力应作为独立 `Behavior Evaluation Lab` Epic，不进入当前 Architecture Guardian Phase 1；
6. 新任务必须先完成内部代码分析、ADR、Spec 和 Plan，再进入隔离候选实现；不得一上来按 Waza 文件结构照抄。

## 本轮状态

- 竞品身份核实：完成；
- 固定上游证据：完成；
- 源码级产品与架构研究：完成；
- 与本项目现状对照：完成；
- clean-room 采用边界：完成；
- Backlog 与新任务 handoff：已建立；
- 真实模型对照实验：未运行；
- Behavior Evaluation Lab 实现：未开始。

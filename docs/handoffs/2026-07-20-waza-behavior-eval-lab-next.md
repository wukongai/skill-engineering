# Handoff：Behavior Evaluation Lab clean-room 重写

## 状态

- 优先级：P0 candidate
- 状态：research complete / backlog / new task required
- 当前 Sprint：`v2.0 Architecture Guardian Phase 1`，本 Epic 尚未升级进入 Sprint
- 研究基线：`microsoft/waza@cf05e487ed967d497a138738514d24457bc45f2a`

## 用户原始目标

用户要完整理解 Microsoft Waza 的 Skill CI 与 A/B 测试体系，但不复制、搬运或依赖其代码。后续要在 Skill Engineering 的架构、命名、安全、证据和发布模型下重新写代码，达到等价的自动化行为评测能力。

新任务明确分成两部分：

1. 先分析本项目现有 evaluation、evolution、release、contract 和 CLI，完成目标架构与兼容设计；
2. 基于分析，在独立候选中 clean-room 重写实现，并用自己的测试和真实 E2E 验证。

## 已完成的可感知结果

- 核实竞品实际为 [`microsoft/waza`](https://github.com/microsoft/waza)；
- 固定上游 commit `cf05e487ed967d497a138738514d24457bc45f2a` 和 tag `v0.38.3`；
- 完成源码级调研方案和结果：[`Waza 对比研究`](../research/2026-07-20-microsoft-waza-comparison.md)；
- 确认 Waza 的核心是 runner、A/B、grader、trial、CI gate、snapshot/replay、adversarial 和 dashboard；
- 确认 Skill Engineering 已有 A/B 结果比较和 holdout/negative-transfer 门禁，但没有自动行为测试 runner；
- 固定 clean-room 原则和不采用边界；
- 建立完整 [`Behavior Evaluation Lab Backlog Epic`](../BACKLOG.md#behavior-evaluation-labskill-ci-与-ab-自动化测试引擎)；
- 当前实现、版本和当前 Sprint 均未改变。

## 当前是否安全

- 安全：没有安装或运行 Waza，没有调用 Copilot/API，没有读取或保存凭证；
- 安全：没有复制上游源码、测试、prompt 或内部数据模型；
- 安全：没有修改 `src/`、tests、版本、Changelog、当前 Sprint 或发布状态；
- 尚未验证：没有运行同一 Skill 的真实 Waza/Skill Engineering 对照，因此不能宣称新测试体系已经交付或效果更好。

## 现有能力基线

`src/skill_engineering/evaluation.py` 当前已经拥有：

- baseline/candidate 外部结果比较；
- development/holdout、success/failure/high-risk；
- deterministic assertions；
- pass-rate、delta、negative transfer 和 production gates；
- suite/results hash 与 subject fingerprint；
- inconclusive 和 utility limitations。

它缺少：

- 自动启动 Agent/model 的 runner；
- without-skill/current/candidate 实验矩阵；
- 多 trial、并发、retry、flaky 和 confidence interval；
- workspace、fixture、tool trajectory 和文件 diff；
- grader registry；
- multi-turn、cross-model、adversarial、snapshot/replay 和 CI reporter。

## 新任务阶段

### 阶段 1：内部分析，不写功能代码

1. 读取 `docs/PRODUCT.md`、`docs/constitution.md`、`docs/architecture.md`、`docs/TASK.md`、当前 Sprint、本研究和 Backlog；
2. 画出 evaluation、evolution、maintenance、release evidence、contract、Doctor 和 CLI 的调用/数据关系；
3. 对每个 Waza 能力标注 adopt、adapt、defer 或 reject；
4. 明确三组正交维度：subject、split、case category；
5. 明确 provider/tool/network/credential/program grader/hook 的 trust model；
6. 明确 1.x suite/results、CLI 和 release evidence 的兼容与迁移策略；
7. 输出分析报告，不直接修改 `src/`。

### 阶段 2：架构工件

内部分析通过后建立：

- 跨版本 ADR：runner 与 deterministic evaluate 的边界；
- Feature Spec：用户流程、schema、信任模型、兼容、失败路径和验收标准；
- Implementation Plan：分阶段文件修改、测试、迁移、回滚和独立评审；
- Task/Sprint promotion：明确是否暂停当前 Guardian Phase 1 或排到其后。

未完成这些工件，不进入实现。

### 阶段 3：clean-room 实现

- 不使用 Waza 仓库作为 candidate；
- 不复制 Waza Go 代码、测试或 prompt；
- 在独立候选中实现本项目自己的 Python API、schema、CLI 和 tests；
- 先实现最小完整闭环：suite v2 → runner → deterministic grader → three-subject A/B → existing evaluate → CI gate；
- 再逐步实现 multi-trial/statistics、tool/file/action grader、snapshot/replay、multi-turn/cross-model、adversarial 和 dashboard；
- 每个阶段都必须保留 1.x protected behavior、holdout 防泄漏和可信回滚。

## 必须保持的边界

1. Doctor 静态结构/安全结果不能冒充真实 utility；
2. LLM judge 不能覆盖确定性 hard gate；
3. candidate generator 不能读取 holdout assertions 或 baseline scores；
4. program grader/hooks 默认禁止，只能进入显式 trusted profile；
5. 不内嵌第三方 provider CLI，不自动安装 runtime；
6. 不自动修改 Skill、Global、外部系统或发布状态；
7. Waza 只作为公开研究基线，不成为运行依赖或代码来源。

## 完成定义

- same-suite 的 without-skill/current/candidate 自动实验可重复；
- development/holdout/high-risk 和 negative transfer 继续成立；
- 多 trial、flaky、统计、golden regression 和 CI reporter 可验证；
- deterministic graders 与 trusted graders 清晰隔离；
- evidence artifact 可重算、脱敏、迁移和回放；
- 真实 Skill E2E 覆盖成功、失败、高风险、多轮和跨模型；
- pytest、Ruff、Skill validation、Doctor、credential lint、diff、迁移/回滚和独立评审全部通过；
- README、Guide、Feature Matrix、Roadmap、Task、Sprint、Version、Changelog 和 release evidence 与代码一致；
- 未经单独授权不 commit、push、tag 或发布。

## 唯一下一步

新窗口从“阶段 1：内部分析”开始：先读取本 handoff、Waza 研究和现有评测实现，产出调用关系、差距矩阵、信任模型及 schema/兼容影响分析；分析被确认后再创建 ADR、Spec 和 Plan，不要直接写 runner 代码。

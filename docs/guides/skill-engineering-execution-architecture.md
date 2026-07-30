# Skill Engineering 执行架构与全生命周期流程图

适用范围：`v1.1.x Native Authoring` 当前实现。

这张图回答三个问题：

1. 用户从任何 Agent 宿主进入后，Skill Engineering 如何成为创建、维护、评测、演进和治理 Skill 的统一入口；
2. 一次新建 Skill 如何从模糊需求走到完整候选、受控写入和真实任务验证；
3. 创建完成后，失败证据如何进入维护或自进化闭环，而不是把 Skill 留在一个无人理解、无人验证的目录里。

```mermaid
flowchart TB
  USER["用户<br/>只需要描述目标、例子或真实问题"]
  HOST["宿主 Agent<br/>Codex / Claude Code / Hermes / Pi / Kimi CLI / 其他兼容宿主"]
  ENTRY["唯一用户入口<br/>skills/skill-engineering/SKILL.md"]
  JOURNEY["会话与恢复<br/>Journey 保存已确认需求、阶段、阻断项和下一步"]
  INTENT{"意图路由"}

  USER --> HOST
  HOST --> ENTRY
  ENTRY --> JOURNEY
  JOURNEY --> INTENT

  subgraph CREATE["A. 新建 Skill：Native Authoring 主链路"]
    C0["只读发现<br/>扫描已有 Skill、Script、Plugin、项目规则"]
    C1["能力头脑风暴<br/>一次澄清一个会改变结果的问题"]
    C2{"产物决策"}
    CNO["不新增 / 扩展已有能力 / Script / Plugin / 文档"]
    C3["确认需要 Skill<br/>选择最小架构与治理等级"]
    C4["Authoring Brief<br/>固定目标、触发、输入输出、边界、安全与验证"]
    C5["Native Authoring Kernel<br/>直接生成任务专属的完整候选"]
    C6["Content Completion Gate<br/>阻断骨架、占位符、空资源、断链和凭证风险"]
    C7["Portable Creation Review<br/>检查触发、指令、资源、安全与可验证性"]
    C8{"候选是否完整"}
    CINC["candidate_incomplete<br/>指出内容缺口并回到对应根因层修复"]
    C9["Native Plan Preview<br/>固定 candidate、target、manifest、fingerprint 和评审结果"]
    CREADY["candidate_ready<br/>用户看到将创建的真实文件和影响"]
    C10{"用户是否明确批准<br/>写入同一份未漂移计划"}
    CPAUSE["保持预览状态<br/>不写入目标目录"]
    C11["Apply<br/>只写计划内文件"]
    C12["Verify + Skill Self Test<br/>检查写入结果、门禁、评审和声明式测试"]
    C13{"写后检查是否通过"}
    CROLL["自动回滚或停止<br/>保留可恢复证据"]
    CUNTRIED["created_untried<br/>结构与创建检查通过，尚未证明真实效用"]
    C14["宿主执行至少一个真实样例任务<br/>保存脱敏结果或可信 artifact pointer"]
    C15{"真实任务是否达到预期"}
    CVALID["validated<br/>存在真实任务通过证据"]
    CNEED["needs_improvement<br/>记录失败模式、预期行为和回归证据"]

    C0 --> C1
    C1 --> C2
    C2 -->|"不需要 Skill"| CNO
    C2 -->|"需要 Skill"| C3
    C3 --> C4
    C4 --> C5
    C5 --> C6
    C6 --> C7
    C7 --> C8
    C8 -->|"否"| CINC
    CINC --> C1
    C8 -->|"是"| C9
    C9 --> CREADY
    CREADY --> C10
    C10 -->|"否"| CPAUSE
    C10 -->|"是"| C11
    C11 --> C12
    C12 --> C13
    C13 -->|"失败"| CROLL
    C13 -->|"通过"| CUNTRIED
    CUNTRIED --> C14
    C14 --> C15
    C15 -->|"通过"| CVALID
    C15 -->|"失败"| CNEED
  end

  subgraph MAINTAIN["B. 维护已有 Skill：证据驱动的防腐化闭环"]
    M0["收集真实失败<br/>失败模式、预期行为、回归证据"]
    M1["定位最低根因层<br/>trigger / interface / state / script / structure / install"]
    M2["在隔离目录生成修复候选<br/>不直接把实验写进正式 Skill"]
    M3["Improve Preview<br/>展示文件 diff、复杂度变化和 preflight"]
    M4{"用户是否批准<br/>同一 maintenance plan"}
    MPAUSE["保持候选和计划<br/>不改变正式 Skill"]
    M5["Apply + Postflight + Verify"]
    M6{"验证是否通过"}
    MROLL["失败自动回滚<br/>记录失败与恢复结果"]
    MREC["维护记录<br/>历史、趋势和安全 Undo 入口"]

    M0 --> M1
    M1 --> M2
    M2 --> M3
    M3 --> M4
    M4 -->|"否"| MPAUSE
    M4 -->|"是"| M5
    M5 --> M6
    M6 -->|"失败"| MROLL
    M6 -->|"通过"| MREC
  end

  subgraph AUDIT["C. 体检与行为评测：结构健康不冒充真实效用"]
    A0["Audit / Doctor<br/>静态结构、安全、契约和安装就绪度"]
    A1["结构就绪度报告<br/>FAIL / WARN / INFO 与修复建议"]
    A2["Validate Eval Suite<br/>拒绝 command/script 与证据泄漏"]
    A3["Baseline / Candidate<br/>由外部真实 rollout 或可信 harness 产出结果"]
    A4["Evaluate<br/>development / holdout / high-risk / negative-transfer"]
    A5["效用结论与证据覆盖<br/>没有真实证据就明确写尚未验证实际效果"]

    A0 --> A1
    A2 --> A3
    A3 --> A4
    A4 --> A5
  end

  subgraph EVOLVE["D. 自进化与安全发布：从真实证据到可回滚版本"]
    E0["导入脱敏 SkillRun<br/>只保存摘要和 artifact pointer"]
    E1["聚类证据并生成 Evolution Proposal"]
    E2["拆分 development / holdout 数据集"]
    E3["创建隔离 CandidateJobs<br/>候选生成看不到 holdout assertions 和 baseline 分数"]
    E4["宿主 Agent 在各 job/source 内生成候选"]
    E5["真实 rollout + 自动评测 + Pareto 推荐"]
    E6["保存不可变版本<br/>自动进入 Shadow"]
    E7["Canary / Active Release Plan"]
    E8{"用户是否明确批准<br/>同一份未漂移 Release Plan"}
    EPAUSE["保持 Shadow<br/>不自动发布"]
    E9["Release + Verify"]
    E10["ReleaseRecord<br/>验证结果与安全 Rollback 入口"]

    E0 --> E1
    E1 --> E2
    E2 --> E3
    E3 --> E4
    E4 --> E5
    E5 --> E6
    E6 --> E7
    E7 --> E8
    E8 -->|"否"| EPAUSE
    E8 -->|"是"| E9
    E9 --> E10
  end

  subgraph GOVERN["E. 安装、盘点与范围治理"]
    G0["Inventory / Govern / Install"]
    G1["判断暴露类型与范围<br/>project / direct / plugin / profile / global"]
    G2{"是否超出单项目范围"}
    G3["Skill Engineering<br/>项目级预览、审计与验证"]
    GHUB["Agent Skill Hub<br/>Profile / Global / 多项目分发的外部责任方"]
    G4["安装计划预览"]
    G5{"用户是否批准实际范围"}
    GPAUSE["不改变安装或暴露状态"]
    G6["Apply + Verify + Undo 入口"]

    G0 --> G1
    G1 --> G2
    G2 -->|"否"| G3
    G2 -->|"是"| GHUB
    G3 --> G4
    GHUB --> G4
    G4 --> G5
    G5 -->|"否"| GPAUSE
    G5 -->|"是"| G6
  end

  INTENT -->|"create / 新需求"| C0
  INTENT -->|"improve / 已有失败"| M0
  INTENT -->|"audit"| A0
  INTENT -->|"evaluate"| A2
  INTENT -->|"evolve"| E0
  INTENT -->|"govern / install / inventory"| G0
  INTENT -->|"resume"| JOURNEY

  CNEED --> M0
  MREC --> C14
  CVALID --> A2
  A1 --> M0
  A5 --> M0
  A5 --> E0

  subgraph ENGINE["共享执行底座"]
    L1["对话与路由层<br/>SKILL.md + references + stages + host adapters"]
    L2["便携确定性门禁<br/>content_gate.py / creation_review.py / native_plan.py / skill_self_test.py"]
    L3["Python 确定性核心<br/>decision / Doctor / evaluate / improve / evolve / release"]
    L4["本机状态与证据<br/>.skill-engineering/ 中的 brief、journey、plan、record、evaluation"]
    L5["统一安全约束<br/>Preview before Write · Same Immutable Plan · Explicit Approval · Verify · Rollback"]

    L1 --> L2
    L1 --> L3
    L2 --> L4
    L3 --> L4
    L5 --> L1
    L5 --> L2
    L5 --> L3
    L5 --> L4
  end

  ENTRY -.-> L1
  C6 -.-> L2
  C7 -.-> L2
  C9 -.-> L2
  C12 -.-> L2
  M3 -.-> L3
  A0 -.-> L3
  A4 -.-> L3
  E1 -.-> L3
  E9 -.-> L3
  JOURNEY -.-> L4
```

## 读图结论

- **一个入口**：无论运行在 Codex、Claude Code、Hermes、Pi 还是 Kimi CLI，用户都从 `skill-engineering` 进入。宿主适配器只负责能力映射，不复制作者逻辑。
- **完整创建，不是骨架生成**：普通创建由 Native Authoring Kernel 生成任务专属完整候选；`skill-engineering create` 旧 CLI 只保留为 `1.0`/CI 的 `scaffold_only` 兼容路径，不进入普通用户主链路。
- **无外部 Creator 依赖**：核心创建不依赖官方 `skill-creator`、Superpowers、宿主专用作者 Skill 或独立 Python CLI。Python 核心仍提供高级、CI、评测、维护和发布能力。
- **所有写入都有同一个安全边界**：先预览，再由用户批准同一份不可变计划；发现 candidate、target 或 plan 漂移时拒绝写入；写后验证失败时回滚或安全停止。
- **创建完成不等于真实有效**：结构检查通过后只能到 `created_untried`；至少一个真实任务有通过证据后，才进入 `validated`。
- **失败进入闭环**：真实任务失败进入 `needs_improvement`，随后以失败模式、预期行为和回归证据驱动维护；积累足够证据后也可进入自进化。
- **发布范围受控**：Shadow 可自动形成；Canary/Active 必须明确批准；Global、Profile 和多项目分发由 Agent Skill Hub 管理，不会被 Skill Engineering 自动开启。

## 当前版本边界

- 本图覆盖 `v1.1.x` 的完整创建与既有 `1.0.x` 生命周期能力。
- 创建后的注释式阅读、Guided Tour 和 Skill Graph 属于规划中的 `1.2.0`，不在本图当前执行链路内。
- `2.0.x Architecture Guardian` 当前暂停；Blueprint/IR 不应被描述为 `v1.1.x` 已启用的写入门禁。
- Hermes 无 Creator 真实 E2E 是 `v1.1.0` 的发布证据门禁，不是产品运行时对 Hermes Creator 的依赖。

## 主要事实源

| 关注点 | 文件 |
|---|---|
| 用户唯一入口与意图路由 | [`skills/skill-engineering/SKILL.md`](../../skills/skill-engineering/SKILL.md) |
| 当前三层架构 | [`docs/architecture.md`](../architecture.md) |
| Native Authoring 决策 | [`ADR 0008`](../adr/0008-native-authoring-kernel.md) |
| v1.1 范围与验收 | [`v1.1 Spec`](../specs/2026-07-29-v1.1-native-authoring-spec.md) |
| v1.1 实施顺序 | [`v1.1 Plan`](../plans/2026-07-29-v1.1-native-authoring-plan.md) |
| Skill 内部文件职责 | [`file-map.md`](../../skills/skill-engineering/references/file-map.md) |
| 当前版本完成状态 | [`TASK.md`](../TASK.md) |

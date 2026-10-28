# Architecture Decision Records

ADR 记录跨版本仍重要的架构取舍。文件名使用 `NNNN-short-title.md`。

每份 ADR 包含：状态、背景、决定、理由、影响、替代方案和后续迁移。

只有架构决策进入 ADR；当天过程写 Daily Log，功能需求写 Spec。

当前安装体验决策：ADR-0004 采用标准 `skills` CLI；ADR-0007 将普通用户默认命令细化为简约交互式入口。

当前创建链路决策：ADR-0008 以 Native Authoring Kernel 取代外部 Creator 委托，标准安装产物自包含创建闭环。

当前发布宿主决策：ADR-0009 以 Codex 作为默认唯一真实宿主发布门禁；其他宿主
真实 E2E 是非阻断兼容性证据，adapter contract fixture 仍必须通过。

当前维护架构决策：[ADR 0010](0010-internal-maintenance-architecture-review.md)采用内部审查阶段，复用 preflight/计划哈希/维护历史，保持旧计划兼容，不新建独立 Skill 或写入引擎。

当前写入策略：[默认强制审查决定](0011-mandatory-maintenance-architecture-review.md)已实现并验证；取代前项无声明仍可 Apply 的兼容条款，保留历史读取与安全恢复。

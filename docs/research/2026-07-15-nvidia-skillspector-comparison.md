# NVIDIA SkillSpector 对比研究

## 对比基线

- 上游仓库：`NVIDIA/SkillSpector`
- 上游 commit：`8f534e2951e0b7d0b8fb8e84832cd3605f95c032`
- 快照日期：2026-07-15
- 本地项目：Skill Engineering `0.1.0`

SkillSpector 是面向 Agent Skill 的专用安全扫描器；Skill Engineering 是创建、Doctor、评测、维护、演进和发布治理系统。两者有交集，但产品边界不同。本轮只吸收能增强现有 Doctor、且不引入新的 provider/runtime 的能力。

## 能力对比

| 能力 | SkillSpector | Skill Engineering 现状 | 本轮决定 |
|---|---|---|---|
| 文本安全模式 | 多类别静态规则 | `SEC101-SEC107` 已覆盖提示注入、凭证、外联和合约 | 保留现有规则，不复制上游规则库 |
| Python 行为分析 | AST 检测动态执行、shell、动态导入等 | 主要依赖文本正则 | **吸收：增加原生 AST 检查** |
| 简单数据流 | source 到 sink 的污点关联 | 只检查同一脚本中的信号共现 | **吸收：增加外部输入到执行 sink 的确定性关联** |
| 机器报告 | JSON、Markdown、SARIF | 人类文本与 JSON | **吸收：增加 SARIF 2.1.0** |
| Suppression/baseline | 规则和指纹 suppression | 只有 profile 级行为，没有通用 waiver | 延后；需先定义审计、到期和误用边界 |
| OSV 依赖漏洞 | 在线查询，离线 fallback | 无依赖漏洞扫描 | 延后；应作为可选集成，不进入无网络核心 |
| YARA/恶意软件 | YARA 规则 | 无 | 延后；依赖和误报成本不符合本轮范围 |
| LLM 语义复核 | 可选 provider 语义分析 | 核心明确保持 provider-neutral、确定性 | 不移植；未来由 rollout/eval runner 提供证据 |
| URL/zip/Git 输入 | 扫描器直接解析远程输入 | Doctor 只检查本地 Skill | 延后；安装治理应先拥有可信下载边界 |
| MCP 专项规则 | 最小权限、tool poisoning、rug pull | 由 provider contract 和外部 Plugin 治理部分覆盖 | 加入 Backlog，单独设计 contract 后再做 |

## 本轮吸收原则

1. 只借鉴公开行为和架构思路，使用本项目的数据模型重新实现，不复制上游源码。
2. AST 和数据流只产生可解释、带文件与行号的确定性 finding。
3. 规则级别继续服从 Skill Engineering 的 profile 和合法 provider contract，不用单一风险分覆盖治理语义。
4. SARIF 与现有 `DoctorResult` 同源，CLI、JSON 和 CI 不出现三套判断。
5. 静态结构健康仍不等于真实任务效用。

## 预期收益

- 发现正则难以可靠识别的 import alias、`shell=True` 和动态执行链。
- CI 与 IDE 可直接消费 Doctor finding，而不必解析自然语言输出。
- 后续增加依赖、MCP 或 suppression 能力时，有稳定的 rule/finding/report 接口可扩展。

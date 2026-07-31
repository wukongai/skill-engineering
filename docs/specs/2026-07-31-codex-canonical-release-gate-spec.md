# Spec：Codex 作为默认唯一真实宿主发布门禁

状态：Approved Design

日期：2026-07-31

适用范围：`1.1.0` 及后续版本的默认发布策略。

## 背景

Skill Engineering 的 `1.1.0` Native Authoring 同时提供 Codex、Claude Code、
Hermes、Pi 和 Kimi CLI 的宿主适配契约。原 `1.1.0` 发布门禁要求 Codex 与
Hermes 都完成无 Creator 真实 E2E，导致核心版本发布取决于第二个宿主环境是否
随时可用。

项目维护者已经明确新的长期产品策略：

> Codex 是 Skill Engineering 的默认主开发和主发布验证环境。当前候选在 Codex
> 完成真实 E2E，并通过其余工程、安全、证据和独立评审门禁后，即可进入正式发布；
> 其他宿主的真实 E2E 是兼容性证据，不再是核心版本发布的默认硬门禁。

这项调整只改变“必须在哪些真实宿主运行 E2E”，不降低静态门禁、行为证据、
Creator 独立性、适配契约或发布审批要求。

## 目标

1. 为当前和后续版本建立单一、稳定、可获得的默认真实宿主发布门禁。
2. 保留多宿主适配能力，同时避免单个非主宿主环境阻塞核心版本发布。
3. 明确区分“Codex 主发布验证”“跨宿主适配契约”和“可选兼容性 smoke”。
4. 保持历史评审和测试证据不可改写，通过新的 ADR 和当前事实源取代旧决策。
5. 用回归测试防止后续文档再次把 Hermes 或其他非 Codex 宿主写成默认硬门禁。

## 非目标

- 不删除 Claude Code、Hermes、Pi 或 Kimi CLI 的 host adapter。
- 不降低 Content Completion Gate、portable creation review、Native Plan、
  self-test、Doctor、安全扫描或 1.0 兼容要求。
- 不把 Codex 一次静态检查冒充真实 E2E。
- 不承诺所有宿主在没有真实 smoke 时已经获得同等行为效用证据。
- 不在本变更中执行 merge、tag、GitHub Release 或 Global 安装。
- 不修改历史 K3 回执、历史测试报告或历史 Daily Log 的原始结论。

## 发布门禁

### 必须通过

每个正式版本默认必须满足：

1. 当前发布候选在 Codex 中完成至少一次无外部 Creator 的真实端到端任务；
2. Codex E2E 覆盖用户需求、完整候选、预览、明确确认、写入、验证、自测和一个
   真实样例；
3. pytest、Ruff、Skill validation、production Doctor、credential lint、
   release consistency 和 diff check 全部通过；
4. Content Completion Gate 能阻断骨架、占位符、空资源、断链和凭证风险；
5. 1.0 CLI/API/JSON/contract 兼容回归通过；
6. 所有声明支持的宿主 adapter contract fixture 通过；
7. 独立评审确认静态结构分没有被包装成真实任务效用；
8. README、Product、Architecture、Roadmap、Task、Sprint、Version、Changelog
   和 Release Log 与实际证据一致；
9. commit、push、merge、tag 和公开发布分别获得明确授权。

### 默认不阻断

以下项目默认不再阻断核心版本发布：

- Hermes 真实 E2E；
- Claude Code 真实 E2E；
- Pi 真实 E2E；
- Kimi CLI 真实 E2E；
- 新增非 Codex 宿主的真实 smoke。

这些结果作为兼容性证据进入测试记录。失败时必须如实降低对应宿主的兼容性声明、
建立修复任务并保留证据，但不自动阻止 Skill Engineering 核心版本发布。

### 仍会阻断的跨宿主问题

真实 E2E 非必需不代表 adapter 可以失效。以下问题仍是发布阻断：

- host adapter 文件缺失、断链或与共同能力契约矛盾；
- adapter fixture 失败；
- 非 Codex 宿主逻辑泄漏进 Native Authoring Kernel，形成宿主专用 Creator 依赖；
- 文档宣称某宿主已经真实验证，但没有对应证据；
- 跨宿主共享安全边界或 Creator 独立性被破坏。

## 历史证据与取代关系

`2026-07-30` 及以前的 K3 回执、Codex Review、测试报告和 Daily Log 记录的是当时
有效的“双宿主硬门禁”。它们属于不可改写的历史证据。

实现本 Spec 时必须新增 ADR，明确从其生效提交开始：

- 当前规范性文档以 Codex 为默认唯一真实宿主硬门禁；
- 历史文件中的 Hermes 硬门禁结论只描述当时状态，不继续约束后续发布；
- 未来若更换默认主宿主，必须通过新的 ADR、迁移说明和回归测试。

## 用户反馈

发布状态只需要向普通用户说明：

- Codex 主发布验证是否通过；
- 工程、安全和证据门禁是否通过；
- 哪些其他宿主只有适配契约证据，哪些已有可选真实 smoke；
- 当前是否还需要 merge、tag 或 GitHub Release 授权。

不得因为缺少 Hermes 真实环境而把整体状态报告为阻断，也不得把 adapter fixture
包装成该宿主的真实任务效果。

## 验收标准

1. 新 ADR 固定 Codex canonical host release gate，并说明如何取代旧门禁。
2. v1.1 Spec、Plan、TASK、Sprint、Release Log 和执行架构指南使用相同策略。
3. 当前规范性文档不再把 Hermes 或任一非 Codex 宿主真实 E2E列为默认发布硬门禁。
4. 历史 handoff、testing 和 daily log 保持原文。
5. 发布回归测试同时证明：
   - Codex 真实 E2E 是必需项；
   - 非 Codex 真实 E2E 是非阻断兼容性证据；
   - adapter fixture 和共享安全边界仍是必需项。
6. 全量 pytest、Ruff、Skill lint、production Doctor、portable self-test、
   credential lint、release consistency 和 diff check 通过。
7. 变更完成后仍保持 `1.1.0` Unreleased，等待 merge、tag 和 GitHub Release
   的独立授权。

## 恢复策略

若新门禁造成发布证据歧义，在 tag 前恢复当前规范性文档和测试即可；历史证据不需
改动。若 `v1.1.0` 已发布，任何再次扩大真实宿主硬门禁的决定进入后续补丁版本，
不得静默改写已经发布版本的证据口径。

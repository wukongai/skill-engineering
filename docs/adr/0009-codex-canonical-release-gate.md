# ADR-0009：Codex 作为默认唯一真实宿主发布门禁

状态：Accepted

日期：2026-07-31

## 背景

Skill Engineering 1.1 同时维护 Codex、Claude Code、Hermes、Pi 和 Kimi CLI
的宿主适配契约。原发布计划要求 Codex 与 Hermes 都完成无 Creator 真实 E2E，
导致核心版本发布取决于第二个宿主环境是否可用。

Skill Engineering 的主开发、主测试和主要用户验证环境是 Codex。多宿主支持的
核心价值是同一 Native Authoring Kernel 可以通过 capability adapter 工作，而
不是要求每次核心发布都在所有宿主完成真实运行。

## 决策

1. Codex 是 Skill Engineering 默认且唯一必须通过真实 E2E 的 canonical host。
2. 当前候选在 Codex 完成无外部 Creator 的真实端到端任务，并通过全部工程、
   安全、证据、兼容和独立评审门禁后，可以进入正式发布授权。
3. Claude Code、Hermes、Pi、Kimi CLI 和未来非 Codex 宿主的真实 E2E 是非阻断
   兼容性证据；缺少这些环境不阻止核心版本发布。
4. 所有声明支持的宿主仍必须通过 adapter contract fixture。adapter 缺失、断链、
   安全边界漂移或把宿主专用 Creator 引入 Kernel，仍然阻断发布。
5. 非 Codex 真实 smoke 失败时，降低对应宿主兼容性声明并建立修复任务；不得把
   fixture 包装成该宿主的真实效用证据。
6. commit、push、merge、tag 和 GitHub Release 继续作为独立授权点。
7. 未来更换 canonical host 必须新增 ADR、迁移说明和回归测试，不得静默改变。

## 取代关系

本 ADR 从其生效提交开始，取代 v1.1 早期 Spec、Plan、K3 Handoff 和测试记录中
“发布前必须完成 Hermes 真实 E2E”的规范作用。

历史 handoff、testing 和 daily log 保持原文，继续证明当时的评审过程和旧政策，
但不再约束当前或后续版本发布。

## 不变门禁

- 无外部 Creator 的完整创建闭环；
- Preview before Write 与同一未漂移计划；
- Content Completion Gate、portable creation review 和 self-test；
- pytest、Ruff、Skill validation、production Doctor、credential lint、
  release consistency 和 diff check；
- 1.0 CLI/API/JSON/contract 兼容；
- adapter contract fixture 与共享安全边界；
- 独立评审和文档/版本事实一致性。

## 备选方案

- **Codex 与 Hermes 双宿主真实 E2E**：拒绝。第二宿主环境不可用会阻塞核心版本，
  但其 adapter 正确性已经有独立 fixture 和共同能力契约覆盖。
- **任意一个宿主通过即可发布**：拒绝。证据口径会随可用环境变化，无法形成稳定
  的主发布基线。
- **每个项目自行配置 canonical host**：暂不采用。当前只有 Skill Engineering
  自身的发布政策需要固定主宿主，增加配置没有必要。

## 后果

- Codex E2E 需要绑定当前发布候选并保留可复核证据；
- 非 Codex 实测可以在发布前后持续补充，不再卡住 tag；
- 对外兼容性说明必须区分 adapter fixture 与真实宿主 smoke；
- 当前 v1.1 事实源和发布测试需要同步，历史证据不回写。

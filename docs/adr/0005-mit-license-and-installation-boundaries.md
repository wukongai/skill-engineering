# ADR 0005：保持 MIT 并区分 CLI 与 Agent Skill 安装边界

- 状态：Accepted for v1.0 planning
- 日期：2026-07-16
- 关联：`docs/specs/2026-07-16-licensing-installation-policy-spec.md`
- 安装入口关联：`docs/adr/0004-standard-skill-cli-install.md`

## 背景

Skill Engineering 同时包含 Python 工程工具和可被 Agent 发现的 `skills/skill-engineering/`。当前仓库已有 MIT `LICENSE`，并已决定普通用户通过标准 `skills` CLI 安装 Agent Skill；但没有一份面向用户的范围说明，也没有把 CLI 安装与 Agent Skill 暴露区分开。许可证和安装边界会影响贡献、分发、支持和商业化叙事。

## 决策

保持单一 MIT。默认将本仓库原创代码、Agent Skill 指令、references、schemas、tests、examples 和文档纳入 MIT；第三方材料按原许可证处理；用户生成内容默认不由项目主张；名称和 Logo 另行保留商标边界。

安装沿用 ADR 0004 的标准 `skills` CLI 入口，并明确它与 Python CLI 是两个交付物：

- 普通用户用 `npx skills add ... --skill skill-engineering` 安装 Agent Skill；`-g` 表示全局，省略表示当前项目，Global/Profile 变更仍需审计、确认和可回滚。
- Python CLI 供开发和稳定包用户使用；安装 Python 包不会自动暴露 Agent Skill。
- Agent Skill 安装不会自动安装 Python 依赖；完整本地闭环按场景分别安装。

## 理由

- 现有 `LICENSE`、`pyproject.toml` 和产品定位已经选择 MIT，保持它避免不必要的许可证迁移。
- local-first、provider-neutral 和后续商业服务需要允许商业使用、修改和再分发；MIT 的许可条件简单，便于用户和营销准确理解。
- 细分文档许可证会制造“哪些 prompt 能复制”的额外边界，不利于 Skill 生态和无锁定承诺。
- CLI 与 Agent Skill 的生命周期、依赖和暴露范围不同，必须在产品层面分开，而不是用一个安装命令掩盖差异。

## 后果

- 可以明确宣传“MIT 开源核心、可自托管、商业使用允许、无格式锁定”。
- 不能宣传项目商标被 MIT 自动授权，也不能把未来托管/团队/企业能力写成开源核心当前能力。
- 若未来出现专利敏感核心、强企业贡献治理或必须限制某类再分发的需求，需要新增 ADR、迁移说明和版本门禁；不得在补丁版本中静默改证。

## 参考

- [MIT License](https://opensource.org/license/mit)
- [SPDX License List](https://spdx.org/licenses/)

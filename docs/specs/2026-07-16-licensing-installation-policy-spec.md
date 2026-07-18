# Skill Engineering 版权与安装政策 Spec

状态：Superseded by `docs/specs/2026-07-18-apache-2.0-attribution-spec.md`；保留为 MIT 阶段的历史决策记录

## 背景

仓库已经包含 MIT `LICENSE`，`pyproject.toml` 也声明了 MIT，但用户仍需要从多个文件拼接以下事实：许可证覆盖哪些文件、第三方材料如何处理、用户生成的 Skill 是否属于项目、Python CLI 与 Agent Skill 是否是同一个安装物。边界不清会直接影响贡献、分发、定价、营销和支持承诺。

## 目标

1. 形成单一、可链接的版权与安装事实源。
2. 在不改变当前开源方向的前提下，明确 MIT 的适用范围和例外。
3. 让新用户能判断自己需要安装 Python CLI、Agent Skill，还是两者都需要。
4. 明确 project-only、profile/global、direct/manual 和 plugin/runtime 的边界与审批要求。
5. 为后续运营和营销提供不夸大的产品叙事：MIT 开源核心、local-first、无格式锁定；托管、团队和企业服务另行提供。

## 决策范围

### 许可证

- 保持单一 `MIT` 许可证，SPDX 标识为 `MIT`。
- 默认覆盖本仓库原创的源代码、Python 包、CLI、Agent Skill 指令、references、schemas、tests、examples 和文档。
- 第三方代码、数据、商标、截图或引用保留其原许可证；新增捆绑内容必须附带来源、许可证和兼容性记录。
- 用户自己的 prompt、私有数据、生成的 Skill 和运行产物不由项目主张所有权；用户仍需自行确认输入、模型和第三方素材的权利与条款。
- MIT 不授予项目名称、Logo 或其他商标的使用权；商标使用与代码许可分开。
- 不对 MIT 之外的专利授权作额外承诺；如果未来需要明确专利授权或更强企业贡献治理，必须通过新的 ADR 和版本迁移重新评估。

### 安装

- Python CLI 和 Agent Skill 是两个独立交付物。安装一个不会自动安装另一个。
- 开发者使用仓库 editable install；终端用户在稳定版本发布后使用固定版本的 `uv tool`/`pipx` 安装 CLI。
- Agent Skill 统一通过标准 `skills` CLI 安装；省略 `-g` 表示当前项目，加 `-g` 表示全局。多项目或全局暴露交给 Agent Skill Hub/安装器，并要求 inventory、备份、回滚和明确确认。
- Plugin/runtime 不是普通目录型 Skill，不通过复制 `skills/skill-engineering/` 伪装安装。
- canonical 用户可见名称只有 `skill-engineering`；旧别名不得与新入口并存触发。

## 非目标

- 本 Spec 不发布新版本、不执行真实用户全局安装、不创建 PyPI release。
- 本 Spec 不建立云端服务条款、SLA、数据处理协议或商业价格表。
- 本 Spec 不把用户生成结果保证为独占、唯一或适用于所有模型。

## 验收标准

1. `LICENSE`、`pyproject.toml`、README 和版权安装事实源都写明 `MIT`/`SPDX-License-Identifier: MIT`，且无相互矛盾的范围描述。
2. 版权安装事实源包含许可证范围、第三方材料、用户生成内容、商标、贡献和变更政策。
3. README 提供 CLI 与 Agent Skill 的安装决策表、当前发布状态、项目/全局范围示例和卸载/回滚边界。
4. 文档明确说明 Python 包安装不会暴露 Agent Skill，Agent Skill 安装也不会自动安装 CLI 依赖。
5. v1.0 发布清单包含干净环境安装、固定版本、canonical identity 和隔离 Agent Skill smoke；没有这些证据不得宣称“稳定安装”。
6. 运营/营销文案只承诺 MIT 开源核心与可自托管，不把未来托管、团队或企业能力写成当前已交付。

## 风险

- 将文档与 Skill 内容纳入 MIT 可能被误解为可使用项目商标；通过单独的商标边界和 README 链接降低风险。
- 未来引入第三方模板或训练数据可能产生许可证冲突；通过来源清单和兼容性 review 阻断。
- 用户把 CLI 与 Agent Skill 混装会造成“安装成功但无法触发”或“能触发但缺少 CLI”的支持问题；通过双轨安装表和 smoke 命令降低风险。

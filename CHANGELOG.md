# Changelog

本文件记录已发布版本的用户可感知变化。格式参考 Keep a Changelog，版本遵循语义化版本。

## Unreleased

### Added

- Architecture Guardian Blueprint schema v1、Python 数据模型、确定性 fingerprint、unknown/legacy 保留和敏感扩展字段门禁。

### Planning

- `2.0.0` 进入 Architecture Guardian Phase 1，先实现 Blueprint/IR 契约与只读 inventory。

## 1.0.0 - 2026-07-18

### Added

- Doctor 的 Python AST 行为风险检查，覆盖动态执行、不安全 shell 和外部输入到执行 sink。
- Doctor/audit 的 SARIF 2.1.0 输出，供 CI、代码扫描和 IDE 消费。
- 1.x 公开契约、0.1.x schema 兼容策略、升级/回滚指南和版本一致性自动门禁。
- Python 3.10、3.12、3.14 CI 支持矩阵，以及 wheel 和干净环境安装验证。
- 会议纪要、GitHub Issue、Web 应用验收和研究证据包四个用户旅程的发布证据索引。

### Changed

- 唯一用户可见 Agent Skill 身份统一为 `skill-engineering`，移除 `skill-guide` 顶层暴露。
- 普通用户安装入口统一为 `npx skills add` / `npm exec`；clone/fork 只用于源码学习、二次开发和贡献。
- 冻结 create/improve/release 的 Preview → 同一未漂移计划 → 明确批准 → Apply 边界。
- 明确 MIT 对原创代码、Agent Skill、references、schemas、tests、examples 和文档的覆盖范围，并区分第三方材料、用户生成内容与商标边界。

### Compatibility

- 合法的 0.1.x `schema_version: "1"` Journey、plan、record 和 evaluation 状态继续可读。
- Doctor 保留 `--json`，同时稳定支持 `--format text|json|sarif`。
- Blueprint/IR 与 Architecture Guardian 继续标记为 2.0 Preview，不进入 1.0 稳定契约。

## 0.1.0 - 2026-07-15

### Added

- Public Beta 产品、版本、Backlog、Sprint、ADR 和 Daily Log 自举治理体系。
- 复杂和商业 Skill 的渐进式工程治理指引。
- GitHub CI、贡献指南和安全报告入口。

### Changed

- 统一产品定位：快速生成、从第一版开始工程化，并在全生命周期持续保持架构和质量。
- 凭证全目录扫描遵守 `.gitignore`，避免把本地虚拟环境和构建产物误判为仓库泄漏，同时继续扫描未忽略的新文件。
- 新需求先进行已有能力自查和逐步需求探索；关键答案缺失时不再默认推荐创建 Skill。
- Skill 创建改为 Preview 与 Apply 分离，Apply 必须引用同一份计划。
- 创建后自动执行结构 postflight；production 单独报告发布证据完整度。
- 创建结果使用面向普通用户的完成/未完成说明。

### Fixed

- 时间戳实现兼容项目声明的 Python 3.10，不再依赖 Python 3.11 才提供的 `datetime.UTC`。

首个 Public Beta：快速生成从第一版开始就符合工程规范的 Skill，并在后续维护、评测、演进和发布中持续保护架构与质量。

# Changelog

本文件记录已发布版本的用户可感知变化。格式参考 Keep a Changelog，版本遵循语义化版本。

## Unreleased

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

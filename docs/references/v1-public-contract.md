# Skill Engineering 1.x 公开契约

本文件冻结 `1.0.0` 起用户可以依赖的兼容边界。1.x 可以增加可选字段、命令和检查，但不会静默改变既有输入含义、审批边界或成功/失败语义。

## 稳定身份与安装入口

- 唯一用户可见 Agent Skill 名称：`skill-engineering`；
- 唯一源码目录：`skills/skill-engineering/`；
- 普通用户标准安装命令：`npx skills add wukongai/skill-engineering`；
- 1.x 继续兼容 `--skill`、`-g`、`-a` 和 `-y` 等定向或非交互参数，但不要求普通用户使用；
- `skill-guide` 只作为历史名称存在，不是可安装、可发现或可触发入口。

## 稳定 CLI

以下顶层命令及其职责在 1.x 保持兼容：

- `decide`：判断需求是否应该成为 Skill 或其他产物；
- `journey`：保存和恢复用户任务进度；
- `create`：预览创建计划，并通过同一 plan 执行写入；
- `lint` / `doctor` / `audit`：结构、安全和发布准备度检查；
- `evaluate`：读取外部真实 rollout 结果并运行确定性断言；
- `improve` / `verify-improvement` / `undo-improvement`：候选式维护、验证与撤销；
- `evolution`：证据聚类、候选、版本和 Shadow 生命周期；
- `release-plan` / `release-apply` / `release-verify` / `release-rollback`：审批式发布与恢复。

`create --apply` 必须引用已经预览且未漂移的 plan；`improve --apply` 和发布命令遵守相同边界。1.x 不会增加绕过预览或用户批准的默认写入路径。

## 稳定机器接口

- Journey、plan、record、evaluation 和 evolution JSON 使用 `schema_version: "1"`；
- 1.x 继续读取合法的 0.1.x `schema_version: "1"` 状态；
- 不支持的 schema 必须返回包含 found/expected 的明确迁移错误，不能静默猜测；
- Doctor 保留 `--json` 兼容别名，并支持 `--format text|json|sarif`；
- SARIF 输出遵守 SARIF `2.1.0`，产品版本记录在 driver metadata 中。

## 稳定行为边界

- 静态 Doctor 分数只代表结构准备度，不代表真实下游效用；
- production 效用声明必须有 baseline、holdout、high-risk、negative-transfer 和独立评审证据；
- 候选生成不得读取 holdout assertions 或 baseline 分数；
- 凭证、原始敏感 Prompt 和完整私有对话不进入仓库或本地状态；
- Global 安装、外部写入、Canary/Active、tag 和公开发布保持显式审批。

## Preview / Internal

Blueprint/IR、Architecture Guardian inventory、semantic diff 和 2.0 migration 仍属于 Preview/Internal，不属于 1.x 稳定公开契约。它们的存在不能被文档表述成 1.0 已承诺能力。

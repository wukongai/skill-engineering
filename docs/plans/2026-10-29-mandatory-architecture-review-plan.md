# CLI 强制维护架构审查实施计划

> 执行方式：当前任务使用测试先行与独立子 Agent 评审；按项目既有 docs/specs 与 docs/plans 落点执行。用户已授权实施、文档回填和既有安装同步，无需再次询问执行方式；commit/push/tag/发布另行授权。

状态：Done；同一计划应用、已安装入口复验、文档收尾及完整门禁通过；未发布。

**目标**：遗漏架构审查不能通过 CLI 或其维护写入代理进入应用。

**架构**：复用 architecture_review 和 preflight；核心创建预览与 Apply 双层检查。Active 发布透传同一声明，不制造第二套审查逻辑。

**技术栈**：Python >=3.10、argparse、pytest、Ruff；Skill Markdown/YAML 与原 portable checks。

[需求与验收](../specs/2026-10-29-mandatory-architecture-review-spec.md) · [当前任务](../TASK.md) · [专项迭代](../sprints/2026-10-29-mandatory-architecture-review.md) · [本轮证据](../testing/2026-10-29-mandatory-architecture-review.md)

## 全局约束

- 正式版本保持 1.1.0；不扩大其他 Sprint。
- 不修改既有计划模型/哈希，不补造旧计划审查；不提供免审参数。
- 在独立目录修改 Skill/core；应用前冻结精确清单、备份和差异，同一维护 plan 应用 Skill。
- 保留已有 dirty 改动与边界确认规划；不覆盖并发修改，不存凭证/私有原始输入。
- 普通小修保持轻量，但仍声明；创建、审查、真实行为证据分开。

## 任务与验证步骤

### 强制核心门禁与迁移回归

文件：`src/skill_engineering/architecture_review.py`、`maintenance.py`；`tests/test_architecture_review.py`、`test_maintenance.py`、`test_scaffold.py`。

接口：保留 `assess_architecture` 签名，None 输入改为 blocked 并保留实际指纹。Apply 只消费计划内快照，不重新读取外部声明。统一校验放既有架构模块，maintenance 在目标写入前调用。

- [x] 运行现状基线：`.venv/bin/python -m pytest -q`，404 passed；保存 313 个现有文件哈希和隔离副本。
- [x] 先补缺声明、旧计划绕过、有效快照、旧记录恢复测试，运行 pytest 确认按预期失败。
- [x] 缺声明报告包含 MAINT111 与真实指纹，供宿主补审；Apply 拒绝缺失/未通过/输入不匹配或未满足整体门的快照。
- [x] 将原测试的合法维护样例改为显式提供真实输入指纹的声明；旧历史用冻结的历史 fixture，不能加入产品绕过开关。
- [x] 运行定向测试，保留红绿结果及未审查旧计划原哈希一致证据。

### CLI、Active 与 Skill 路由

文件：`src/skill_engineering/cli.py`、`evolution.py`；`tests/test_cli.py`、`test_evolution.py`、`test_native_authoring.py`、`test_skill_engineering_feedback.py`；Skill 根入口、架构 reference/阶段、维护协议、evolution reference、contract。

接口：`create_release_plan(..., architecture_review: Path | None = None)` 透传到 Active 的 `create_improvement_plan`；CLI 两条预览入口公开相同参数。参数保持可解析，语义门禁由核心负责，`--plan` 复用冻结快照。

- [x] 先测试缺参预览非零、已存旧计划不能应用、给旧 plan 补传 JSON 被拒绝、Active 缺声明/有效声明/审批/漂移/回滚。
- [x] 更新 CLI 帮助和参数转发，明确 --plan 不重新消费声明，非 Active 不忽略审查参数。
- [x] Skill 指令统一要求新维护声明，保留历史 unreviewed 的只读含义；写清 Active 入口。
- [x] 运行定向测试，确认 Native Authoring、Shadow/Canary 保持原边界。

### 独立评审、精确应用与安装验证

- [x] 完整 pytest 和 Ruff；独立评审检查需求覆盖、旧计划迁移、Active、证据限制、指纹绑定；修复全部阻断并复核。
- [x] 冻结 candidate 差异及文件哈希，备份源文件；按相同清单应用 core，按原维护引擎携带真实独立审查声明预览/应用/Verify Skill。
- [x] 对两处安装链接解析/内容校验；用现有 `.venv/bin/skill-engineering` 从仓库外、移除 PYTHONPATH 运行缺声明和旧计划阻断、有审查 Apply/Verify/Undo。
- [x] 执行 Skill validation、Content Gate、production Doctor、portable self-test、credential lint、release consistency、文档引用检查和 `git diff --check`。
- [x] 回填本计划、Spec、Sprint、Task、使用指南、产品/架构、Roadmap、功能表、README、Changelog、Daily 与机器证据；不改写旧测试事实。

## 失败恢复

隔离失败不触及维护目标。精确应用前核对原文件哈希；不一致先合并当前内容。Skill 写后失败沿用原引擎恢复；源码恢复从本轮独立备份取回精确文件，不能使用 git reset 覆盖其他 dirty。历史 Undo 不受新增审查前置条件影响。

## 提交推送追加授权

用户于2026-10-29进一步明确授权整理架构审查与CLI强制门禁、提交并推送远程及对齐文档。前文不commit/push的边界属于实施阶段原授权，本节只追加源码交付，不新增Tag、Release或Global操作。

- [x] 审计混合dirty，剔除SEC102、项目收尾、边界确认和本地未推送Skill Dissect提交。
- [x] 从远程main建立独立codex分支，350项干净提交候选回归及所有工程门禁通过。
- [x] 提交本轮精确范围并推送GitHub分支。
- [x] 回填实际提交号、远程核验与最终文档状态。

[提交复验与交付记录](../testing/2026-10-29-mandatory-architecture-review.md#提交范围复验与远程交付)为本次源码交付事实源。

实际功能提交：[4df144c](https://github.com/wukongai/skill-engineering/commit/4df144c770b48a445e9f4e06932c17ca8d710c9f)，已推送并核对远端一致；文档收尾随随后提交交付。

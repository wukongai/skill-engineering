# Handoff：对齐官方 Skill Anatomy，拆分运行包与工程评测层

## 状态

- 优先级：P1
- 状态：open / architecture correction required
- 来源：`user-panel-review` 真实创建与维护闭环
- 影响：当前 `create --production` 与 `improve` 不能在不违背官方安装包结构的前提下完成仓库级回归治理

## 用户原始目标

用户要求把旧 `wechat-reader + personas` 重做成可开源的 `user-panel-review` Skill，并明确指出：模板应该进入官方 `assets/`，测试和 use case 不应作为安装包里的独立目录。

## 已完成的可感知结果

`user-panel-review` 已采用官方结构交付：

```text
skills/user-panel-review/
├── SKILL.md
├── agents/openai.yaml
├── scripts/
├── references/
├── assets/
├── LICENSE
└── skill.contract.yaml
```

仓库级测试位于：

```text
tests/skills/user-panel-review/
tests/test_user_panel_review.py
```

候选和正式目标均达到：

- 官方 `quick_validate.py` 通过；
- Skill 自带 bundle validator 通过；
- 零第三方依赖回归 8/8 通过；
- Skill Engineering production audit：100/A，0 FAIL，0 WARN；
- behavioral utility 仍诚实保持 `not-evaluated`。

## 真实阻塞一：create 把工程测试写进 Skill 安装包

当前 `skill-engineering create --production` 会把以下文件写进目标 Skill：

```text
tests/cases/success.yaml
tests/cases/failure.yaml
tests/cases/high-risk.yaml
tests/cases/holdout.yaml
```

同时 CLI 没有 reusable resources、`assets`、project root 或 package layout 输入，因此无法表达“报告模板需要进入 assets，回归测试需要进入仓库工程层”。

这与 `skills/skill-engineering/references/authoring-standard.md` 已声明的仓库级路径 `tests/skills/<skill-name>/cases/` 不一致。

### 本次兼容处理

没有使用 `skill-engineering create` 写正式内容。先用官方 `skill-creator/scripts/init_skill.py` 创建可撤销空骨架，再用独立候选进入 `improve` 闭环。

## 真实阻塞二：improve 不识别仓库级 regression case

生产维护计划传入：

```text
project://tests/skills/user-panel-review/cases/success.yaml
project://tests/skills/user-panel-review/cases/failure.yaml
project://tests/skills/user-panel-review/cases/high-risk.yaml
```

预检返回 `MAINT106 FAIL`，因为 `maintenance.py` 把每个回归路径强制解析到候选 Skill 的 effective tree 内。

因此正确的仓库分层反而无法通过 production improvement preflight。最终只能：

1. 先真实运行外置 unittest，得到 8/8 PASS；
2. 用 team profile 和明确的 no-regression-reason 记录上游限制；
3. 按同一计划应用；
4. 再单独运行 production audit，得到 100/A。

这是一条受控兼容路径，不应成为长期默认。

## 根因

1. `BuildPlan` 只有一个 target root，无法同时管理 Skill bundle 和 project engineering。
2. `BuildFile` 只有 relative path，没有 delivery scope。
3. Blueprint 虽然区分 `asset` 与 `test` role，但不区分安装包、工程测试、评测证据和运行产物。
4. create CLI 无法声明 `scripts/references/assets` 需求。
5. Doctor 和 maintenance 没有统一的 `project://`、`evidence://` 路径解析器。
6. 当前静态审计可以检查“声明存在”，但无法稳定区分“路径存在、证据执行、证据通过”。

## 目标架构

为 Blueprint component 增加交付区域：

```yaml
delivery_scope:
  - skill_bundle
  - project_engineering
  - evaluation_evidence
  - runtime_output
```

示例：

```yaml
components:
  - id: report-template
    role: asset
    path: assets/report-template.md
    delivery_scope: skill_bundle

  - id: success-case
    role: test
    path: tests/skills/user-panel-review/cases/success.yaml
    delivery_scope: project_engineering
```

Skill bundle 默认只包含：

```text
SKILL.md
agents/
scripts/
references/
assets/
skill.contract.yaml  # 明确标注为 Skill Engineering 扩展
```

默认不把以下目录装入 Skill：

```text
tests/
examples/
artifacts/
docs/
logs/
```

工程层和证据层建议：

```text
tests/skills/<skill-name>/
artifacts/skill-evals/<skill-name>/
docs/testing/<skill-name>/
```

## 路径协议

建议统一支持：

```yaml
tests:
  regression_cases:
    - project://tests/skills/user-panel-review/cases/success.yaml

evaluation:
  behavioral_results:
    report: evidence://user-panel-review/evaluation-report.json
```

- 普通相对路径继续相对 Skill 根，兼容 1.x。
- `project://` 相对显式 `--project-root` 或确定性发现的仓库根。
- `evidence://` 相对显式 evidence root。
- 安装后的 Skill 没有源码仓库证据时，返回 `not-evaluated`，不要误报文件损坏。

## 建议修改位置

- `src/skill_engineering/blueprint.py`
- `src/skill_engineering/scaffold.py`
- `src/skill_engineering/maintenance.py`
- `src/skill_engineering/skill_doctor.py`
- `src/skill_engineering/cli.py`
- `src/skill_engineering/journey.py`
- `docs/references/skill.contract.template.yaml`
- `skills/skill-engineering/references/authoring-standard.md`
- `skills/skill-engineering/stages/design/INSTRUCTIONS.md`
- `skills/skill-engineering/stages/scaffold/INSTRUCTIONS.md`

## 兼容策略

### 1.x

- 继续识别 Skill 内旧 `tests/cases/`。
- 新建计划默认使用官方 bundle + project engineering 分层。
- 旧布局只产生迁移 WARN，不自动移动或删除。
- 保留旧 BuildPlan hash 语义；新字段必须按 schema version 迁移，不能让未执行计划全部漂移。

### 2.0

- 官方 bundle / repository engineering 分层成为默认。
- `--legacy-local-tests` 仅作为显式兼容选项。
- 发布门禁确认安装包不包含工程测试、行为产物和开发日志。

## 必须新增的回归测试

1. `create --production` 的 Skill bundle 不包含 tests、artifacts、docs 或 examples。
2. repository layout 把 cases 写入 `tests/skills/<name>/cases/`。
3. 声明报告模板时生成 `assets/report-template.md`。
4. 未声明 output asset 时不创建空 assets。
5. fixture 不会被路由进 assets。
6. `improve` 能解析并验证 `project://` regression case。
7. Doctor 能分别报告：证据已声明、文件存在、证据执行通过。
8. contract 指向不存在的工程测试时不能获得 coverage credit。
9. 旧 Skill 内 tests/cases 继续兼容并产生迁移提示。
10. 多 root apply 仍满足同计划、独立 fingerprint 和失败全量回滚。
11. 安装 smoke test 只复制 `skill_bundle`。
12. 旧 BuildPlan 能继续应用或得到明确迁移提示。
13. 官方 quick validation、Skill Engineering lint/Doctor 和仓库测试共同通过。

## 唯一下一步

新任务先把本 handoff 升级为 spec + ADR + implementation plan；优先实现统一 path resolver 和 delivery scope，再改 create 默认布局。不要先通过增加更多 scaffold 硬编码分支解决。

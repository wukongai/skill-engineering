# Skill Engineering 统一对外身份 Spec

状态：Implemented with follow-ups；远程 v1.0 安装证据和真实全局替换仍待独立确认

日期：2026-07-16

## 背景

当前仓库对外同时暴露 `skill-engineering` 和 `skill-guide`：前者是仓库、Python 包和 CLI，后者是用户实际安装并触发的 Agent Skill。用户明确说“测试 skill-engineering”时，Agent 可能误选 `skill-guide`，甚至被相似的项目体检 Skill（如 ank）抢占路由。

这次修改先解决身份冲突，不在同一变更中引入 `skilleng` 等缩写。

## 目标

1. 用户可见的唯一 canonical 名称为 `skill-engineering`。
2. Agent Skill 的 frontmatter、安装目录、contract、文档入口和用户反馈统一使用 `skill-engineering`。
3. `skill-guide` 不再作为顶层可触发 Skill 暴露。
4. 从远程仓库安装到隔离全局环境后，在任意项目都能完成创作、检查和维护回归。
5. 旧 0.1.x 安装不会静默产生两个同时可触发的 Skill；迁移必须可见、可确认、可撤销。

## 非目标

- 本次不把名称缩短为 `skilleng`、`skeng` 或其他新品牌。
- 本次不重命名 Python 内部 import 包 `skill_engineering`。
- 本次不修改 ai-native-kit/ank 的源代码；只通过 canonical trigger 和安装审计避免路由冲突。
- 本次不自动修改用户真实全局 Skill 目录。

## 设计决定

### Canonical identity

| 层 | canonical 值 |
|---|---|
| 产品/仓库/CLI | `skill-engineering` |
| Agent Skill frontmatter name | `skill-engineering` |
| Agent Skill 源目录 | `skills/skill-engineering/` |
| 状态目录 | `.skill-engineering/` |
| Python import | `skill_engineering`（内部兼容名） |

用户界面使用连字符形式；下划线只保留给 Python import，不作为 Agent Skill 名。`skill-guide` 只允许出现在迁移说明、历史记录或内部候选路径，不得出现在顶层 Skill 搜索目录。

### 触发边界

canonical Skill 的 description 和 contract 必须明确包含：

- `skill-engineering` / `Skill Engineering`；
- 创建、检查、评测、维护、演进和发布 Skill 的请求；
- “从远程安装后测试完整闭环”的请求。

对于仅做项目 harness 初始化、开工自检、tmux 或 Claude 入口治理的请求，不触发本 Skill。

### 迁移边界

- 源仓库中只保留一个顶层可发现目录 `skills/skill-engineering/`。
- 旧 `skill-guide` 目录迁移到非发现路径或由同一 canonical 目录取代，不保留两个并列可发现目录。
- 全局安装检查发现旧 `skill-guide` 时，先报告影响范围并请求用户确认；确认后再替换或移除旧入口，支持恢复原指纹。

## 验收标准

1. `rg`、Skill validation 和 Doctor 不再把 `skill-guide` 识别为顶层 active Skill。
2. 真实用户请求“测试 skill-engineering，从创建到检查”只得到 `skill-engineering` 路由，不出现 `ank` 模式菜单。
3. 隔离全局安装只暴露一个 canonical Skill；旧别名不会与其并存触发。
4. 任意临时项目可以完成 `decide → create preview → create apply → doctor`，并保留同一计划的审批与验证证据。
5. 维护闭环可以完成 `improve preview/apply → verify-improvement`，不修改真实项目之外的文件。
6. 清理隔离环境后，目标项目和用户原有全局目录均无残留变化。
7. 运行 pytest、Ruff、官方 Skill validation、production Doctor、凭证 lint、`git diff --check` 和隔离 E2E 全部通过。

## 回归用例

- `explicit_skill_engineering_request_routes_canonical_skill`
- `global_install_exposes_one_skill_identity`
- `legacy_skill_guide_is_not_top_level_discoverable`
- `create_doctor_flow_works_from_arbitrary_project_cwd`
- `maintenance_preview_apply_verify_uses_same_plan`
- `cleanup_restores_global_and_project_fingerprints`

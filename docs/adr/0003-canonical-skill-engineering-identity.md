# ADR-0003：统一 `skill-engineering` 作为唯一用户可见 Skill 身份

状态：Accepted

日期：2026-07-16

## 背景

仓库、Python 包和 CLI 使用 `skill-engineering`，Agent Skill 却使用 `skill-guide`。这会让用户无法判断自己调用的是产品、CLI 还是全局 Skill，也会增加与其他项目治理 Skill 的路由碰撞。

## 决定

1. 1.0 的唯一用户可见 canonical 名称保持为 `skill-engineering`。
2. Agent Skill 的顶层目录、frontmatter、contract 和安装入口统一使用 `skill-engineering`。
3. `skill-guide` 降级为迁移/历史内部名称，不作为顶层可发现 Skill。
4. Python import `skill_engineering` 暂不改名；这是实现兼容细节，不是第二个用户-facing 名称。
5. 本次不引入缩写品牌；命名缩短另行立项，避免与身份统一混在一次破坏性迁移中。

## 理由

- 先消除两个现有名称的语义冲突，用户无需学习新品牌；
- 复用已有仓库、CLI、状态目录和文档中的稳定名称，减少迁移面；
- 连字符是 Agent/CLI 的用户格式，下划线只用于 Python import，职责清楚；
- 把 `skill-guide` 留在历史/迁移层，避免全局出现两个可触发入口。

## 影响

- 需要一次 Agent Skill 目录和安装入口迁移；
- 旧 global 安装必须有明确的替换、备份和撤销路径；
- 1.0 发布前必须完成从远程安装到任意项目创作/检查的隔离 E2E；
- `skill-engineering` 作为长名称暂时保留，后续若要缩写需另立 Spec/ADR。

## 替代方案

1. 继续同时保留 `skill-guide` 和 `skill-engineering`：拒绝，会继续造成路由和用户认知冲突。
2. 立即改成 `skilleng`：暂缓，名称缩短和身份统一是两个不同决策，且会扩大 1.0 迁移风险。
3. 只修改 description、不迁移顶层目录：拒绝，安装后仍可能暴露两个 Skill。

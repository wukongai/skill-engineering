# 双语价值型 README 改版计划

状态：Superseded by `2026-07-21-readme-product-reset-plan.md`

日期：2026-07-21

对应规格：[`2026-07-21-bilingual-value-readme-spec.md`](../specs/2026-07-21-bilingual-value-readme-spec.md)

## 不可变范围

本计划只实施以下产品文档变更：

1. 重写根 `README.md` 为中文价值型主版本；
2. 新增根 `README.en.md` 为信息等价的英文版本；
3. 新增本规格、计划与一份 README 改版验证记录；
4. 不修改当前已有未提交改动的 `docs/ROADMAP.md`、`docs/TASK.md`、`docs/BACKLOG.md`、Research、Handoff 和 Daily Log 文件。

## 实施步骤

### 1. 建立价值优先的信息架构

- 页首提供 `简体中文 | English` 切换；
- 用一句话交代结果，用短段落说明目标用户和“不是什么”；
- 将 Quick Start 和自然语言触发示例放在内部架构与仓库结构之前。

### 2. 写核心改造故事

- 使用选题雷达文章中的“50 条热点不等于一个值得写的选题”作为问题钩子；
- 用“功能完整但不是我的系统”说明通用模板与个人能力资产的差距；
- 将个人证据、独立证据、职责边界和持续验证映射到 Skill Engineering 的四项产品价值；
- 明确该故事是方法论案例，不是内置 Skill 或通用效用声明。

### 3. 展示四个发布验证案例

- 对每个案例使用“目标 / 工程化边界 / 价值”三段式压缩表达；
- 链接正式 1.0 Use Case 证据；
- 保留结构回归与跨环境真实效用之间的边界说明。

### 4. 重排安装、版本和技术内容

- Agent Skill 安装作为普通用户第一路径；
- Python CLI 和源码开发作为独立路径；
- 保留 Preview/Apply、Doctor、evaluate 等关键命令；
- 将 1.0 Stable、2.0 Preview、未来探索拆开呈现；
- 保留架构边界、仓库布局、验证、版权和安全入口。

### 5. 中英文一致性检查

- 对照标题、案例、命令、版本、数字、链接和免责声明；
- 英文版按英文产品文案习惯重写，不做生硬逐句翻译；
- 两个版本不增加相互矛盾的承诺。

### 6. 验证并记录证据

- 检查 README 中的本地相对链接是否存在；
- 运行 Markdown/差异检查；
- 运行 pytest、Ruff、Agent Skill validation 和 credential lint；
- 将结果写入 `docs/testing/2026-07-21-bilingual-value-readme.md`。

## 恢复策略

本次不执行删除、重置、提交或推送。若验证失败，只修正本计划新增或改写的 README/规格/计划/验证文件；用户原有未提交文件保持不动。交付前通过 `git diff -- README.md README.en.md docs/specs/2026-07-21-bilingual-value-readme-spec.md docs/plans/2026-07-21-bilingual-value-readme-plan.md docs/testing/2026-07-21-bilingual-value-readme.md` 单独复核范围。

## 完成条件

规格中的全部验收项通过，并且 README 的价值主张、案例、安装入口、版本状态和证据边界在中英两个版本中一致。

# README 产品叙事重置验证

日期：2026-07-21

状态：passed

## 验证目标

确认双语 README 已完全放弃错误的选题雷达叙事，改以《把 Skill 做稳：我开源了 Skill Engineering 1.0》为核心来源，并把 Agent Skill 恢复为唯一用户产品入口。

## 正确输入

核心文章：`Skill Engineering v0.1.0 开源与安装指南-长文.md`。文件目录保留历史 v0.1.0 命名，但文章 frontmatter、标题、Release 状态和正文已经更新为 `1.0.0` 正式开源版。

文章确定的产品主线是：

- 用户只描述工作目标；
- Skill Engineering 先判断、再创建；
- 创建前预览职责、边界、输出和副作用；
- 简单 Skill 保持轻量，复杂度随风险升级；
- 真实失败进入独立候选和回归证据，不直接污染正式版本；
- 四个 Use Case 分别证明轻量创建、外部边界、确定性执行和复杂治理；
- 1.0 管好一个 Skill，2.0 守护整套架构，3.0 从真实使用中持续进化。

## 实施结果

- 中文和英文 README 均完整重写；
- 第一个主体章节为标准 Agent Skill 安装；
- 普通用户安装区只提供 `npx skills add` 路径；
- 删除“Agent Skill + Python CLI 双交付物”的产品主张；
- Python core/CLI 只在后部作为当前 1.x 确定性内核、CI 和兼容接口说明；
- 完全移除选题、topic radar 和 50 条热点等错误来源内容；
- 会议纪要、GitHub Issue、本地 Web 验收和研究证据包成为核心案例；
- 1.0 Stable、2.0 Preview、3.0 长期前瞻分别标记；
- 保留静态结构健康与真实任务效用的证据边界。

## 回归结果

| 检查 | 结果 |
|---|---|
| `python3 -m pytest -q` | passed：135 tests |
| `python3 -m ruff check src tests` | passed |
| Agent Skill `quick_validate.py` | passed |
| `bash scripts/credential-lint.sh --all` | passed |
| `git diff --check` | passed |
| 两份 README 本地相对链接 | passed |
| Markdown 代码围栏 | passed |
| 中英文安装 → Why → Use Case → CLI 顺序 | passed |
| 标准 Agent Skill 安装命令唯一性 | passed：每种语言各 1 次 |
| 错误选题叙事残留 | passed：0 matches |

新增回归要求中英文 README 都把 Agent Skill 安装放在产品 Why 之前，并把 Python CLI 说明放到 Use Case 之后，防止运行内核再次被包装成普通用户的第二产品。

## 证据边界

本次结果证明 README 产品叙事、安装顺序、版本事实、案例、链接和现有稳定回归一致。它没有删除 Python CLI，也没有改变当前 1.x 中部分深度操作对 Python core 的依赖；这仍是正式记录的当前实现边界。

本次验证也不证明新的 README 已经提升 GitHub star、安装转化或真实任务效用。市场与使用效果需要在发布后通过真实用户行为继续观察。

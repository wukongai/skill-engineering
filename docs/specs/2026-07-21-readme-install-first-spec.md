# README 安装前置规格

状态：Superseded by `2026-07-21-readme-product-reset-spec.md`

日期：2026-07-21

## 失败模式

双语 README 已经具备清楚的价值主张、真实案例和完整安装说明，但安装入口位于营销故事、产品价值、工作方式、案例和目标用户之后。GitHub 用户无法在确认项目定位后立即复制安装命令，首次成功路径过长。

## 根因

问题属于 README 信息架构：安装内容正确，但章节排序没有遵循通用开源仓库的“定位后立即 Quickstart/Installation”阅读路径。

## 预期行为

- 中文和英文 README 都在页首定位与简介之后立即展示快速安装；
- Agent Skill 安装命令优先，稳定 Python CLI 安装紧随其后；
- 安装后给出一条自然语言开始方式，再进入价值故事、案例和技术细节；
- 源码克隆继续保留在后部的本地开发章节；
- 安装命令、双交付物边界、版本状态、许可证和能力声明不改变；
- 两种语言保持同样的章节顺序。

## 回归要求

- `npx skills add wukongai/skill-engineering` 必须早于中文第一个营销正文标题；
- 同一命令必须早于英文第一个营销正文标题；
- 标准安装继续早于 `git clone`；
- pytest、Ruff、Skill validation、credential lint 和 diff check 通过。

## 非目标

- 不改变 CLI、Agent Skill、安装器或版本；
- 不新增新的营销承诺或案例；
- 不提交、不推送、不创建 Release。

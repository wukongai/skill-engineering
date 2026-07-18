# Skill Engineering v1.0 远程用户黄金链路

日期：2026-07-18

状态：Passed；已获得 `v1.0.0` tag 与 GitHub Release 独立授权

## 对外可展示结论

一个没有克隆源码的用户，可以从 GitHub 使用标准 Skill 安装命令安装唯一的 `skill-engineering`，在独立项目中完成需求判断、逐步澄清、方案预览、明确确认后创建、提出缺陷、查看根因与结构化修改方案、再次确认后应用修改。需要确定性 Doctor 时，产品会清楚提示安装独立 Python CLI；按提示安装同一版本后，创建与 Doctor 闭环通过。

## 真实安装

```bash
npx skills add wukongai/skill-engineering --skill skill-engineering -a codex -y
```

远程 `main` 候选：`086457cb0d7f3d1ed6786d6a55aa6dffdf1b39e7`。

安装器结果：

- `Found 1 skill`；
- `Selected 1 skill: skill-engineering`；
- 安装目录只有一个 canonical Skill，没有 `skill-guide`；
- 安装完成，安全扫描为 Safe / 0 alerts / Low Risk。

## 用户创建与维护行为

独立 Codex 会话从“把自由叙述的 Markdown 会议记录整理成决策、负责人和截止时间”开始。

1. Agent 先判断需求是否值得做成 Skill，没有直接写文件。
2. 一次只询问一个会改变结果的问题：内容是否需要 AI 判断、触发与反触发分别是什么。
3. 用户确认轻量 Skill 后，Agent先给结构与文件级预览；明确确认前文件哈希保持不变。
4. 用户确认后，真实创建 `meeting-decision-extractor` 的 `SKILL.md`、三份 references 和一份回归用例。
5. 用户反馈“会写入原文没有的内容”后，Agent定位到证据门槛、示例和测试三层根因，没有在文件末尾继续堆规则。
6. 第二次确认前文件仍未变化；确认后只修改预览中列出的三份文件，并增加反幻觉回归边界。

这证明安装后的 Skill 行为符合“先分析结构与根因，再按确认方案修改”，不是持续追加 Prompt 补丁。

## Skill-only Runtime 行为

标准 Skill 安装不会静默安装 Python 包。只安装 Agent Skill 时运行 wrapper，结果为：

- 返回非零退出码 2；
- 明确说明尚未安装 Skill Engineering Python CLI；
- 给出固定 `v1.0.0` 的 `uv tool install` 命令；
- 给出安装后的标准 Doctor 命令；
- 不输出 traceback，不误报检查通过。

## 同一远程候选的确定性闭环

RC 复验使用提交而不是尚未授权创建的 tag：

```bash
uv tool install "git+https://github.com/wukongai/skill-engineering.git@086457c"
```

安装器记录 `skill-engineering==1.0.0`。随后：

1. `create --json` 生成计划 `build-20260718003223-09392fcb`，预览阶段没有目标文件；
2. `create --plan build-20260718003223-09392fcb --apply --json` 应用同一计划；
3. 实际创建 `skills/remote-meeting-actions/SKILL.md`；
4. postflight：pass，team Doctor 0 FAIL / 0 WARN；
5. 独立最终 Doctor：0 FAIL / 0 WARN，100/A（结构准备度，不冒充真实任务效用）。

## 发布门禁

- pytest：133 passed；
- Ruff：passed；
- 官方 Skill validation：passed；
- production Doctor：0 FAIL / 0 WARN，100/A；
- credential lint：passed；
- `git diff --check`：passed。

## 最终边界

本报告证明远程安装、真实用户创建/维护行为、runtime 依赖指引和确定性创建/Doctor 闭环均可工作。它不宣称静态 100/A 等于跨模型业务效用，也没有执行真实 Global/Profile 安装。用户已单独授权 `v1.0.0` tag 和 GitHub Release。

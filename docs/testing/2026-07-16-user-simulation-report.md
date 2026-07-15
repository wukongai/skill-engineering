# Skill Engineering 用户全流程模拟报告

日期：2026-07-16

范围：从标准 Skill 安装到任意项目创建一个新 Skill，再完成检查。测试在一次性 HOME、npm cache 和临时项目中进行，不接触真实全局目录。

## 测试结论

本地统一候选的用户流程通过。用户只需要使用标准 `npx skills add` 安装 Agent Skill；安装完成后，创建动作仍遵守 preview → 同一 plan apply，创建结果可以继续 Doctor 检查。

当前远程 GitHub 默认版本不通过，原因不是用户操作错误，而是远程版本仍只发布 `skill-guide`。因此本报告是“本地统一候选预发布通过、远程公开版本阻断”的真实结论，不能把两者混成一个成功结果。

## 黑盒步骤与结果

### 1. 安装

在任意临时项目目录执行：

```bash
npx skills add /path/to/skill-engineering \
  --skill skill-engineering -g -a codex -y
```

实际安装输出确认：

- `Local path validated`
- `Found 1 skill`
- `Selected 1 skill: skill-engineering`
- `Installation complete`
- Codex 发现目录：`~/.agents/skills/skill-engineering`

结果：通过。隔离全局目录只出现 `skill-engineering`，没有 `skill-guide`。

### 2. 安装后检查

对安装后的 Skill 执行：

```bash
skill-engineering doctor ~/.agents/skills/skill-engineering --profile production
```

结果：100/A，无 FAIL、无 WARN。

### 3. 创建预览

模拟用户请求：

```text
帮我做一个 Skill：把会议记录整理成决策、负责人和截止时间。
先给我方案，不要直接写入文件。
```

CLI 生成 `meeting-actions` 的 immutable plan，目标目录尚不存在，返回 `applied: false`。

结果：通过。用户在写入前能看到名称、类型、文件内容、验证命令和 plan id。

### 4. 使用同一计划应用

确认后使用同一个 plan id 执行 apply：

```bash
skill-engineering create --plan <同一个 PLAN_ID> --apply --json
```

结果：通过。只创建 `SKILL.md`，postflight status 为 `pass`，未出现半成品或额外删除。

### 5. 检查新 Skill

```bash
skill-engineering doctor ./meeting-actions --profile team
```

结果：100/A，无阻断问题。新 Skill 可以继续进入真实行为测试。

## 用户可见流程

```text
npx skills add
      ↓
唯一入口 skill-engineering
      ↓
用户描述目标
      ↓
preview：查看计划，不写文件
      ↓ 用户确认
同一 plan apply
      ↓
Doctor 检查新 Skill
```

## 复测说明

你稍后可以在新的临时项目中重复同样步骤。为了验证真正的远程发布，安装源应替换为统一入口版本发布后的：

```bash
npx skills add wukongai/skill-engineering \
  --skill skill-engineering -g -a codex -y
```

远程版本发布前，不要把本地路径替换成 GitHub 地址后直接宣布通过；先确认安装器输出 `Selected 1 skill: skill-engineering`。

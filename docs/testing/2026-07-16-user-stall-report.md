# Skill Engineering 用户卡壳报告

日期：2026-07-16

## 卡壳场景

用户按照最终目标执行远程安装：

```bash
npx skills add wukongai/skill-engineering \
  --skill skill-engineering -g -a codex -y
```

## 用户看到的过程

安装器先显示：

```text
Source: https://github.com/wukongai/skill-engineering.git
Cloning repository ...
Repository cloned
Found 1 skill
```

随后失败：

```text
No matching skills found for: skill-engineering

Available skills:
  - skill-guide
```

## 根因

当前 GitHub 远程默认版本和公开 `v0.1.0` 仍包含 `skills/skill-guide/`，而统一后的安装命令明确要求 `--skill skill-engineering`。这不是用户命令写错，而是“安装命令已经升级、远程发布内容还没升级”的版本漂移。

## 用户影响

- 用户会等待一段时间，看见安装器持续显示 `Cloning repository`，以为任务卡住。
- 最终安装失败，且不会生成有效的 `skill-engineering` 全局入口。
- 如果用户改成 `--skill skill-guide`，会重新引入已经废弃的旧名称，造成两个版本认知冲突。

## 当前正确处理

1. 停止重复重试，不要改用 `skill-guide`。
2. 先确认 Release 页面已经出现包含 `skills/skill-engineering/` 的统一版本。
3. 发布完成后重新执行同一条命令，验收输出必须包含：

```text
Found 1 skill
Selected 1 skill: skill-engineering
Installation complete
```

4. 如果只是想先体验，可以使用本地统一候选路径进行隔离安装；这只能证明候选流程，不替代远程发布验收。

## 发布门禁

在远程版本完成统一入口发布前，公开安装指南必须保留“等待统一版本”的提示，不能把本地模拟结果写成远程安装成功。

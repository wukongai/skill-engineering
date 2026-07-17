# Skill Engineering 1.0 兼容、升级与回滚

## 支持范围

Python CLI 支持 CPython 3.10、3.11、3.12、3.13 和 3.14。CI 固定验证最低版本 3.10、常用版本 3.12 和当前版本 3.14。Agent Skill 是目录型资产，不要求 Python 才能被 Codex 或 Claude Code 发现；只有执行确定性 CLI 时才需要 Python 包。

## 从 0.1.x 升级

1. 备份正在使用的 `skill-guide` 或旧 `skill-engineering` 目录；
2. 使用标准 `skills` CLI 安装 `skill-engineering`；
3. 确认全局或项目发现目录里只保留一个 `skill-engineering`；
4. 对现有 Skill 运行 `skill-engineering doctor <path> --profile team`；
5. 保留原有 `.skill-engineering/` 状态。合法的 `schema_version: "1"` 可以继续读取。

1.0 不会自动删除用户的旧目录。发现 `skill-guide` 与新入口并存时，先确认作用范围并备份，再移除旧入口，避免两个 Skill 同时参与路由。

## 不兼容状态

当计划、记录或评测文件不是 `schema_version: "1"` 时，CLI 会停止并报告实际版本与预期版本。不要直接改数字伪造兼容；应保留原文件，按错误信息重新生成计划或转换数据。

## 安装与升级

普通用户安装 Agent Skill：

```bash
npx skills add wukongai/skill-engineering --skill skill-engineering -g -a codex -y
```

安装 GitHub `v1.0.0` 对应的 Python CLI：

```bash
uv tool install "git+https://github.com/wukongai/skill-engineering.git@v1.0.0"
```

源码贡献者仍可使用 `python3 -m pip install -e ".[dev]"`。clone/fork 不是普通用户使用 Agent Skill 的前置步骤。

## 回滚

- Agent Skill：先移除当前 `skill-engineering` 安装，再从备份恢复旧目录；
- Python CLI：卸载当前工具，再安装上一个固定 tag；
- 项目内容：通过维护记录执行 `undo-improvement`，不要用未审阅的目录覆盖；
- 发布通道：只对未漂移的 ReleaseRecord 执行 `release-rollback`。

回滚后重新运行 Doctor，并确认可见入口、版本和目标项目都与预期一致。

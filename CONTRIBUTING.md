# Contributing

感谢参与 Skill Engineering。

## 开始之前

1. 阅读 `docs/PRODUCT.md`、`docs/constitution.md` 和 `docs/architecture.md`。
2. 检查 `docs/TASK.md` 和 `docs/BACKLOG.md`，避免重复实现。
3. 功能级改动先提交 Spec 和 Plan；缺陷修复至少写失败模式、根因层级、预期行为和回归用例。
4. 不在根 `SKILL.md` 堆事故记录或一次性禁令。
5. 本仓库原创代码、Skill 指令和文档默认按 MIT 发布；提交者必须拥有贡献内容的权利，不得提交未标注来源的第三方材料。
6. 第三方代码、数据、截图或模板必须附来源、原许可证和兼容性说明；凭证、客户数据和完整私有对话不得提交。

普通用户应通过标准 `skills` CLI 安装已发布的 Skill；克隆或 fork 只用于源码学习、二次开发和贡献，不把开发安装方式写成用户安装前置条件。

## 本地验证

```bash
python3 -m pip install -e ".[dev]"
python3 -m pytest -q
python3 -m ruff check src tests
bash scripts/credential-lint.sh --all
skill-engineering doctor skills/skill-engineering --profile production
git diff --check
```

## Pull Request 要求

- 说明解决的用户问题和非目标；
- 列出对应 Spec/Plan/ADR；
- 提供新增或更新的回归证据；
- 说明复杂度和兼容性影响；
- 不提交凭证、完整私有对话、客户数据或本机绝对路径；
- 不把 MIT 误写成商标授权、专利承诺或托管服务条款；
- 不把结构分数表述为真实下游效用。

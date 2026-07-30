# README 安装前置实施计划

状态：Superseded by `2026-07-21-readme-product-reset-plan.md`

日期：2026-07-21

对应规格：[`2026-07-21-readme-install-first-spec.md`](../specs/2026-07-21-readme-install-first-spec.md)

## 不可变范围

1. 将 `README.md` 的“5 分钟开始使用”移动到首屏简介之后，并改名为“快速安装”；
2. 将 `README.en.md` 的“Start in five minutes”移动到同一位置，并改名为“Quick install”；
3. 更新页首锚点；
4. 在 `tests/test_standard_install_docs.py` 增加中英文安装顺序回归；
5. 在既有 README 改版验证记录中追加本轮结果。

## 验证

- 检查中英文标题顺序、安装命令唯一性、代码围栏和本地链接；
- 运行全量 pytest、Ruff、Agent Skill validation、credential lint 与 `git diff --check`；
- 只复核本计划列出的文件，不触碰用户其他未提交改动。

## 恢复

本次只是章节移动和测试断言。若验证失败，只恢复本计划涉及的 README、测试与跟进文档；不删除、不重置、不提交、不推送。

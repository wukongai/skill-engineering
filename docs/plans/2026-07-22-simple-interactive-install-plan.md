# 简约交互式安装实施计划

状态：Approved

日期：2026-07-22

对应规格：[`2026-07-22-simple-interactive-install-spec.md`](../specs/2026-07-22-simple-interactive-install-spec.md)

## 不可变范围

1. 更新 `README.md` 与 `README.en.md` 的首屏安装区；
2. 更新 `skills/skill-engineering/references/install-governance.md`；
3. 更新当前安装单一事实源、1.0 兼容指南和 1.x 公开契约；
4. 新增 ADR-0007，并在 ADR-0004 标注默认命令细节已被细化；
5. 更新安装回归，锁定简约命令和高级参数不进入首屏；
6. 新增验证记录。

## 保留范围

- 不修改历史 release/testing/spec 中真实执行过的长命令；
- 不修改 Python CLI、Agent Skill runtime 或版本号；
- 不触碰用户已有 Roadmap、Task、Backlog 和 Research 未提交改动。

## 验证

- 搜索当前正式文档中的默认命令一致性；
- 检查 README 安装区不存在高级参数；
- 检查相对链接、代码围栏和 diff；
- 运行 pytest、Ruff、Agent Skill validation 与 credential lint；
- 记录结构健康与未执行真实安装的证据边界。

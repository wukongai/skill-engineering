# README 产品叙事重置计划

状态：Approved

日期：2026-07-21

对应规格：[`2026-07-21-readme-product-reset-spec.md`](../specs/2026-07-21-readme-product-reset-spec.md)

## 不可变范围

1. 完整重写 `README.md` 和 `README.en.md`；
2. 移除选题雷达叙事、双交付物主张和普通用户 CLI 快速参考；
3. 以“把 Skill 做稳”和四个 Use Case 重建价值叙事；
4. 保留准确的安装命令、1.0/2.0/3.0 边界、发布证据、许可证与开发入口；
5. 更新 `tests/test_standard_install_docs.py` 的中英文标题和 CLI 定位回归；
6. 新增独立验证记录，不继续使用错误来源的验证结论。

## 实施顺序

1. 先写中文主版本，确保安装在前、价值与案例在后；
2. 按相同事实重写英文版，不做机械逐句翻译；
3. 更新安装顺序与产品入口回归；
4. 检查相对链接、代码围栏、关键词、命令唯一性和选题污染；
5. 运行全量门禁并记录结构健康与证据边界。

## 恢复

本轮不删除历史文件，只将错误方案标记为 Superseded。若验证失败，只修复本计划涉及的 README、测试和新验证记录，不触碰用户已有 Roadmap、Task、Backlog 和 Research 改动。

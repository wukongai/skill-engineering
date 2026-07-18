# ADR 0006：采用 Apache-2.0，并分离署名、引用与品牌边界

- 状态：Accepted for v1.0
- 日期：2026-07-18
- 关联：`docs/specs/2026-07-18-apache-2.0-attribution-spec.md`
- 取代：ADR 0005

## 背景

ADR 0005 在安装边界尚未稳定时选择继续使用 MIT。标准安装、canonical identity 和 v1.0 候选现已完成，产品目标也进一步明确：保持普通用户和商业用户的低门槛，同时让开发者再分发时保留许可证、来源通知和修改声明，并为未来商业服务与营销入口建立不混淆的品牌边界。

## 决策

从 v1.0 起，Skill Engineering 当前版本采用 Apache License 2.0，版权人为“艾笑”。仓库提供：

- 官方 Apache-2.0 `LICENSE` 全文；
- 信息性 `NOTICE`，记录项目名称、版权人与 canonical source；
- `CITATION.cff`，提供推荐引用方式但不增加许可条件；
- `TRADEMARKS.md`，说明代码许可不等于允许暗示官方来源、背书或合作关系。

原创代码、Agent Skill、文档和测试默认使用 Apache-2.0；第三方内容继续遵循自身条款；用户生成内容不由项目主张。贡献默认按 Apache-2.0 进入项目。

不采用自定义“必须前台署名”许可证，也不采用 copyleft：项目需要 GitHub 生态中的标准开源识别、商业友好和低采用摩擦。来源追溯通过 Apache-2.0 的通知义务、`NOTICE`、canonical source、citation 和品牌边界共同实现。

安装边界继续沿用 ADR 0004：Python CLI 与 Agent Skill 是独立交付物，普通用户通过标准 `skills` CLI 安装 `skill-engineering`。

## 理由

- Apache-2.0 在允许商业使用、修改和分发的同时，明确要求保留适用通知并标记修改文件。
- 显式专利授权与终止条款比 MIT 更适合未来企业贡献和商业合作。
- 标准 SPDX 标识更利于 GitHub、包索引和合规工具识别，不需要自定义限制。
- 单独的品牌政策可以防止非官方分发误导用户，又不限制事实性引用、fork 和兼容性说明。

## 后果

- 可以准确宣传“Apache-2.0 开源核心、允许商业使用、可自托管、保留通知与来源链”。
- 不能宣传“所有衍生作品必须开源”或“必须在产品 UI 展示艾笑”；Apache-2.0 不提供这些保证。
- Apache-2.0 不授予商标使用权；品牌合作和官方认证需要单独授权。
- 在迁移前已合法获得的 MIT 副本仍按其原条款使用；当前仓库与已发布的 v1.0 使用 Apache-2.0。
- 未来再改变许可证必须新增 ADR、迁移说明和发布门禁，不得静默改证。

## 参考

- [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)
- [SPDX Apache-2.0](https://spdx.org/licenses/Apache-2.0.html)

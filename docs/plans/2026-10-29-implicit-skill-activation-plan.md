# Skill 自然语言激活实施计划

状态：Done；隔离实现、同一计划应用、原生宿主与既有安装验证完成；未发布。

目标：让创建、维护和检查Skill的普通说法及有上下文的模糊表达稳定进入既有工程流程，保留名称与执行边界。

架构：预加载description前置意图，正文只保留薄路由，activation-routing参考负责上下文与反触发；不增加分类引擎、全局配置或官方Skill修改。候选在独立目录生成，测试及安装复用原维护链路。

[需求与验收](../specs/2026-10-29-implicit-skill-activation-spec.md) · [专项迭代](../sprints/2026-10-29-implicit-skill-activation.md) · [验证记录](../testing/2026-10-29-implicit-skill-activation.md)

## 约束

正式1.1.0不变，不改名、不加短别名。实施阶段未执行提交推送；用户于2026-10-29追加本轮commit/push授权，tag与正式发布继续排除。保留工作区已有Backlog与日志改动。生成者只接触开发集，不接触holdout断言或baseline成绩。合成输入可以留验证证据，不保存私有原始会话或凭证。

## 执行清单

- [x] 核对Product/宪章/架构/Task、现有发现入口、官方文档及CLI只读能力；350项开工回归通过，保存302文件哈希及完整隔离副本。
- [x] 先落地Spec/Plan/ADR/Sprint和验证记录，将自动激活从暂缓恢复；改名继续暂缓。
- [x] 为元数据前部意图、policy、同源触发合同、开发案例及单一参考写失败测试，确认RED。
- [x] 候选生成Agent仅修改SKILL.md、agents/openai.yaml、contract、file-map、新activation-routing参考、包内开发案例及tests/test_skill_activation.py；最小修改后GREEN。
- [x] 在隔离原生宿主完成baseline及候选的实际自动选择；项目副本按真实路径禁用旧source，保留官方Creator竞争，不注入答案名称或强制读取指令。
- [x] 独立评估holdout与模糊/反例；以成功读取根SKILL.md正文判定，不把静态文本或自报当成激活。公开次数及限制。
- [x] 独立Spec/质量及完整架构审查；修复阻断后冻结差异和三个实际指纹。
- [x] 使用原维护引擎携声明预览、同一plan Apply及正式Verify。既有安装在其原始完整内容上合并本轮差异，保留其他任务内容，再独立应用与验证。
- [x] 完成pytest/Ruff/Skill/内容/Doctor/自测/凭证/版本/差异/引用门禁，回填Task、Sprint、Backlog、README/产品/架构/Changelog、日志和测试证据。

## 主要文件

- Skill发现与薄入口：skills/skill-engineering/SKILL.md、agents/openai.yaml、skill.contract.yaml。
- 单一方法：skills/skill-engineering/references/activation-routing.md；references/file-map.md仅导航。
- 开发案例：skills/skill-engineering/tests/activation-cases.json；tests/test_skill_activation.py核对真实元数据与案例合同，不实现伪语义分类器。
- 宿主验证器仅为本轮临时QA工件，不交付新的Behavior Runner产品或CLI命令。

## 验证命令与证据

使用现有项目虚拟环境python运行pytest与Ruff；新工作树只读测试禁用cache写入。原生Codex采用ephemeral/read-only和单次skills.config覆盖，不复制认证、不修改全局配置。发现列表、静态合同、实际根文件读取和真实业务效用分别记录。

基线/holdout结果由评估方保管，候选生成者不读取。宿主不可用、输入对象无法识别或实际未读取Skill时如实阻断，不以说明文字代替测试。失败恢复复用原维护备份/Undo；不使用git reset清除其他内容。

## 源码交付追加授权

- [x] 用户明确授权本轮commit、push及相关文档对齐。
- [x] 独立核对26个文件范围，7个实现/测试文件匹配已验证候选；工作树356项回归通过。
- [ ] 提交并推送origin/codex/maintenance-architecture-review，核对实际远端提交后回填[交付记录](../testing/2026-10-29-implicit-skill-activation.md#源码提交与推送收尾)。

仅收口本轮自动激活增量，名称优化继续暂缓；不创建Tag或正式Release。

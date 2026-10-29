# Skill 边界确认与防跑偏实施计划

状态：本轮工程交付完成；449项基线至写后601项通过，已按同一维护计划应用，未发布。

[需求与验收](../specs/2026-10-29-skill-boundary-confirmation-spec.md) · [架构决定](../adr/0013-confirmed-boundaries-and-behavior-policy.md) · [专项迭代](../sprints/2026-10-29-skill-boundary-confirmation.md) · [当前任务](../TASK.md#skill-边界确认与防跑偏)

## 全局约束

- 本轮仅边界确认、声明式门禁修正和按类型验收；三项排除范围已由用户确认。
- 初始实施保持正式1.1.0且不安装、提交、推送或发布；用户随后明确授权本轮提交与推送，按原范围隔离验证和交付，仍不新增安装或正式发布。
- 隔离候选包含当前已跟踪与未忽略改动，排除凭证、Git元数据和本地状态；记录每个基线文件指纹，禁止覆盖漂移。
- 不新增BuildPlan/MaintenanceRecord字段，不改旧哈希；Native与维护新快照采用新增键，旧计划保留原合法路径并报告legacy。
- 候选生成不能读取holdout断言或基线评分；开发用例与独立验收分开。

## 任务一：标准库规则与生成副本

文件：新增 src/skill_engineering/boundary_policy.py、skills/skill-engineering/scripts/boundary_policy.py；修改 src/skill_engineering/behavior.py；新增 tests/test_boundary_policy.py，扩展 tests/test_behavior_runner.py。

canonical模块无包内依赖；portable副本由canonical生成并以测试锁定字节一致，不手工维护两套规则。异常 BoundaryError(ValueError)。固定接口：

```python
def boundary_projection(value: dict) -> dict: ...
def boundary_fingerprint(value: dict) -> str: ...
def validate_confirmation(boundary: dict, confirmation: dict, *, subject_id: str | None = None) -> dict: ...
def validate_behavior_policy(policy: dict, boundary: dict) -> dict: ...
def run_text_cases(text: str, cases: list, *, policy: dict | None = None, boundary: dict | None = None) -> dict: ...
def assess_boundary(declaration: dict | None, *, target_fingerprint: str, candidate_fingerprint: str, effective_fingerprint: str, architecture_boundary_changed: bool = False, candidate_text: str = '') -> dict: ...
def validate_boundary_snapshot(report: dict, *, target_fingerprint: str, candidate_fingerprint: str, effective_fingerprint: str, candidate_text: str = '') -> None: ...
```

- [x] 先写确认来源/指纹/空排除、空与非法断言、适用性、重复ID、unchanged/changed、快照漂移与portable一致性测试并运行，保留RED。
- [x] 按Spec实现严格字段、类型、长度和秘密形态检查；未知字段拒绝，不把字段当人类身份认证。
- [x] assess_boundary冻结清洗后的declaration和三个真实指纹；缺声明返回unreviewed+blocking_findings；unchanged需reason且与架构边界变更不得冲突；changed需确认与类型案例通过。
- [x] validate_boundary_snapshot用冻结声明和真实指纹重新确定性计算，拒绝篡改，不重读可变外部文件。
- [x] 执行针对测试至GREEN；生成portable副本，验证独立安装导入与规则一致。

## 任务二：维护链路接入

文件：src/skill_engineering/maintenance.py、cli.py、evolution.py；对应tests/test_maintenance.py、test_cli.py、test_evolution.py、test_scaffold.py及新增tests/test_boundary_maintenance.py。

消费上述assess_boundary/validate_boundary_snapshot。边界声明顶层为schema_version='1'、change='changed'|'unchanged'；unchanged必有reason，changed必有boundary、confirmation、cases；其他可选键仅由canonical白名单定义。

- [x] 先写缺输入阻断、changed无确认拒绝、unchanged未知标记、冻结漂移、旧合法计划可Apply和所有入口传递测试，确认RED。
- [x] create_improvement_plan新增boundary_review: Path|None=None，读取有限大小普通JSON；preflight.boundary_review与architecture_review并列，使用effective overlay文本和指纹。
- [x] 缺输入或不满足门禁增加MAINT112 FAIL；Apply对新快照重验；无新键的合法历史计划按ADR保持，不补造确认。
- [x] CLI improve及Active release新增--boundary-review参数；scaffold代理等新维护通过同一核心门禁。
- [x] 更新现有测试的真实声明fixture，不通过关闭门禁或默认伪确认适配旧测试；执行相关回归至GREEN。

## 任务三：Native创建与就绪判定

文件：skills/skill-engineering/scripts/native_plan.py、src/skill_engineering/authoring.py；tests/test_native_plan.py、test_authoring.py、test_native_authoring.py。

- [x] 先写新Preview缺确认/失效/空排除、类型覆盖、Apply漂移及旧Native计划兼容测试，确认RED。
- [x] 新Preview增加--boundary-confirmation，通过canonical校验Brief业务投影并冻结确认和policy；subject_id匹配Brief ID。
- [x] 新创建要求redirect_strategy；已确认none排除允许空；旧读取/旧计划Apply保持原字段语义。
- [x] portable runner调用生成的run_text_cases，避免残留另一份宽松实现；核心authoring提供新确认判定入口，不破坏旧读取。
- [x] 新Apply以冻结确认和当前Brief重验；继续保持原candidate/target/Brief指纹安全。

## 任务四：Skill引导和事实源

- [x] 更新boundary-contract、authoring-brief、mini-governance、创建/维护/评估阶段、file-map、Skill contract与短路由。
- [x] 说明接受/修改/拒绝、空排除、复用已有表达、实质变化确认；区分有效补充/岔题/换目标/停止；不向所有Skill强加每轮循环。
- [x] 定义结构/声明式检查/真实试用分层；按能力列适用类别及限制；更新创建范例和随包自测入口。
- [x] 同步README/Guide、Product/Architecture、Task/Backlog/Sprint、Feature Matrix和Unreleased；正式版本不变。

## 任务五：评审、应用、验证与OB

- [x] 对照Spec独立评审完整候选，修复阻断，保留真实证据和限制。
- [x] 先对源码精确文件清单核对基线指纹并备份，再回写已审阅差异；Skill部分使用原维护引擎、架构审查和同一不可变预览。
- [x] 执行全量pytest、Ruff、Skill validation、Content Gate、portable self-test、production Doctor、凭证lint、release consistency、diff check及引用检查。
- [x] 用单次任务与持续任务的代表性案例运行可用宿主试用；若未执行真实多轮，明确记录未验证，不把静态文本通过包装成效用。
- [x] 更新项目任务与OB原卡的真实状态和同日唯一执行行；不自动安装/发布或关闭其他任务。

## 收敛与恢复

最多三轮实质修复；阻断未清或证据不足时保留具体未完成项，不继续增加无关能力。原未提交改动始终保留；任一基线漂移只停止受影响应用，不自动重置或覆盖。

完成依据见[验证记录](../testing/2026-10-29-skill-boundary-confirmation.md)。宿主单次与五轮样例使用合成用户输入，仅验证这些边界协商样本；真实业务效用未验证，未进入 validated。

# CLI 强制维护架构审查需求

状态：本地实现、独立评审、自举应用复验、既有安装同步核对及工程验证完成；未发布。

[返回当前任务](../TASK.md) · [实施计划](../plans/2026-10-29-mandatory-architecture-review-plan.md) · [专项迭代](../sprints/2026-10-29-mandatory-architecture-review.md) · [架构决定](../adr/0011-mandatory-maintenance-architecture-review.md)

## 来源与目标

用户明确要求 CLI 默认必须进行架构审查，避免 Agent 漏跑；先落地文档，完成后回填状态、同步已安装 Skill 并验证。上一轮仅在工作流要求执行，缺少声明仍可应用的兼容策略不能满足该目标。

本需求收紧已有维护写入门，不新建审查引擎、顶层 Skill 或发布流程。正式版本保持 1.1.0，本轮是未发布源码增量，不关闭其他 Sprint。

## 已有能力与方案选择

复用内部架构审查阶段、声明加载器、真实指纹、累计基线/债务和原 preflight/plan hash。已有 Native Authoring 继续负责全新创建。

- 只设 argparse 必填会妨碍旧计划查看和按同一计划应用，也不能保护程序调用与旧计划。
- 仅阻断新预览会留下旧未审查计划应用的旁路。
- 采用核心预览与应用双重门禁，Active 发布通过同一维护引擎接入声明；缺声明预览保留诊断及真实指纹，返回非零。

## 行为合同

1. 所有 profile 的新 `improve` 预览都要求有效声明。缺声明时 `preflight.architecture_review.status=blocked`、存在 MAINT111 FAIL，预检及收敛门 blocked，CLI 退出码为 1。保留实际 target/candidate/effective 指纹，帮助宿主组织独立评审；不得自动补造通过声明。
2. 首次无有效整体基线、边界变化、累计超预算等原触发条件保持。普通小修仍可使用轻量声明；只有整体门触发才需要完整独立评审。
3. Apply 在原 plan hash 与输入漂移检查之外，必须检查已冻结的架构快照确实通过且绑定当前计划输入。缺字段、unreviewed、blocked、整体门未满足的旧计划即使旧 preflight 为 pass 也不得写入。不得在加载时重算哈希或补写审查。
4. 旧计划可查看；历史维护记录仍可查看、正式 Verify、安全 Undo。没有审查的旧记录不变成有效整体基线。已包含有效通过快照的未漂移计划可继续按原计划应用。
5. CLI `--architecture-review PATH` 是新预览所需输入；按 `--plan ID --apply` 使用冻结快照，不需重新提供文件。对旧计划补传声明不能原地升级审批，必须生成新的预览。
6. `release-plan --channel active` 同样接收声明并传给原维护预览；缺失或未通过时不能形成可应用 Active 计划。Active 子计划在应用时也受同一门禁。Shadow/Canary 的既有范围与审批不变，不凭空要求维护历史；非 Active 不静默消费审查参数。
7. 不增加 skip/legacy/环境变量绕过开关，不按 profile 豁免。已有 scaffold 维护代理也必须进入同一核心门禁。
8. 不宣称工具能证明评审者身份独立、语义正确或真实行为效果；宿主仍负责实际独立评审和行为证据。

## 兼容决定与迁移

本轮明确取代[上一轮可选接入的兼容决定](../adr/0010-internal-maintenance-architecture-review.md)：保留读取与恢复兼容，收紧新增维护写入。旧未审查计划的唯一下一步是从独立候选补齐声明并重新预览，审批仍绑定同一不可变计划。历史证据保留其当时结论，不改写为新策略已通过。

不修改 BuildPlan/MaintenanceRecord schema、旧 plan hash 算法或正式版本号。不执行 commit、push、tag、公开发布、新增全局暴露或修改 PATH。已安装入口若仍链接本仓库，核对链接及内容即可，不重装覆盖。

## 验收与证据

- 缺声明的 core/CLI、personal/team/production 均阻断且目标不变；真实指纹可用于补审。
- 旧缺字段/unreviewed 的有效哈希计划在直接 apply、CLI、scaffold 代理和 Active 子计划处均不能绕过；拒绝发生在备份、维护记录、目标写入前。
- 旧计划显示、旧历史 Verify/Undo 保持；有审查声明的预览、同一计划 Apply、Verify、Undo 正常，外部 JSON 被改动不影响冻结快照。
- Active 缺声明阻断，提供真实评审可继续；原发布审批、漂移与回滚测试保持。
- Split/defer、审查指纹漂移、候选漂移、累计预算门禁保持。
- 测试先红后绿；完整 pytest、Ruff、Skill validation、Content Gate、production Doctor、portable self-test、credential lint、release consistency、引用和 diff 检查通过；独立评审无未解决阻断。
- 仓库外实际 console 验证遗漏阻断、旧计划阻断、有效审查闭环；两处已安装入口与源码一致。源码与文档回填均可回读。

[原审查需求](2026-10-29-maintenance-architecture-review-spec.md) · [维护标准](../guides/skill-maintenance-standard.md) · [本轮验证记录](../testing/2026-10-29-mandatory-architecture-review.md)

## 源码交付追加授权

2026-10-29用户另行批准本轮架构审查与CLI强制门禁的commit/push和文档收尾。上述实施阶段未执行这些操作的历史事实保持；本次只交付独立提交范围，不授权Tag、正式Release或Global。实际状态见[提交复验与交付记录](../testing/2026-10-29-mandatory-architecture-review.md#提交范围复验与远程交付)。

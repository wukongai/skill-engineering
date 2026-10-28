# CLI 强制架构审查验证记录

状态：Done；本地实现、独立评审、同一计划应用复验、既有安装同步核对及工程验证完成；未发布。

[返回当前任务](../TASK.md) · [需求验收](../specs/2026-10-29-mandatory-architecture-review-spec.md#验收与证据) · [实施计划](../plans/2026-10-29-mandatory-architecture-review-plan.md) · [专项迭代](../sprints/2026-10-29-mandatory-architecture-review.md) · [脱敏机器证据](2026-10-29-mandatory-architecture-review-evidence.json)

## 实施前与红绿证据

- 在任何实现前落地 Spec、Plan、ADR 和任务状态。开工全量基线为404 passed；保存313个现有文件哈希，在隔离副本实施，未重置其他未提交改动。
- 升级前从仓库外真实运行 CLI，缺声明返回成功且生成 unreviewed 计划；冻结该原计划与哈希，升级后继续使用它验证迁移阻断，没有补写字段或重算哈希。
- 核心初始 RED：19 failed / 102 passed；CLI/Active RED：15 failed / 15 passed；Skill合同RED：1 failed。对应实现转绿。
- 主审另补两轮70+70条债务，确认预览pass而Apply误套单次128项上限：RED 1 failed / 4 passed。抽取逐项债务校验后，累计140条可应用，单次129条仍拒绝；第140条重复、秘密或非法ID仍拒绝。没有截断历史债务。
- 旧未审查计划的人读提示另有RED 2 failed；已修正为当前不能应用并要求重新预览，不再提示批准应用。

## 已应用门禁

| 场景 | 实际结果 |
|---|---|
| 三个profile缺声明 | core与真实CLI均阻断；MAINT111 FAIL、预检/收敛blocked，CLI退出1，目标未写入 |
| 缺声明诊断 | 保留真实target/candidate/effective指纹，债务覆盖明确未评估，不暗示清零 |
| 旧计划查看与应用 | 原哈希/字段保持，可查看；缺有效审查的旧计划直接Apply、CLI、scaffold代理均拒绝 |
| 人读历史计划 | 显示当前不能应用、补审重新预览，无应用审批提示 |
| 同一计划与外部JSON | Apply使用冻结快照；外部文件变动不替换已预览结论；不能给旧plan补传声明升级 |
| Active维护写入 | 使用同一声明和核心门；缺声明或旧未审查子计划拒绝，审批/漂移/回滚回归保持 |
| Shadow/Canary与创建 | 原边界保持；非Active传维护声明被拒绝，全新创建不要求维护历史 |
| 审查与漂移负例 | split/defer、审查指纹不符、候选漂移和整体缺证据安全阻断 |
| 历史恢复 | 原记录查看、正式Verify与安全Undo保持；无审查旧记录不成为整体基线 |
| 累计预算 | 先局部增长6行通过，再累计12行超过10行预算阻断，整体基线未被局部维护重置 |
| 完整pytest / Ruff | 已应用工作区443 passed in 4.78s / pass |
| 已安装检查 | 官方Skill validation、Content Gate、production Doctor100/A零问题、portable self-test通过 |
| 安全与版本检查 | credential lint、1.1.0 release consistency、diff check通过 |

## 独立评审与自举应用

独立Spec符合性与代码质量审查均通过。累计债务上限Important与旧计划反馈Minor已复核关闭，无未解决发现。另一独立Agent对完整Skill候选进行六范围声明性审查，指纹绑定真实目标、候选及完整effective tree；它不代替CLI运行验证或真实行为证据。

10个源码/测试文件按冻结精确清单核对前后SHA-256、备份后应用。7个Skill文件使用同一维护计划预览/应用，正式Verify为passed、drifted=false；没有删除文件。根入口行数、指令文件数和重复长指令增量均为0。计划、记录与指纹见机器证据；备份及维护状态保存在本机临时/忽略目录。

## 已安装入口与仓库外实测

Codex与共享Agent入口仍是指向本仓库Skill目录的两处符号链接；内容指纹一致，新指令已经同步可见。没有复制覆盖链接、重装依赖、新增Global暴露或修改全局PATH。真实控制台使用现有项目虚拟环境 `.venv/bin/skill-engineering`，从仓库外目录且移除子进程PYTHONPATH后运行。

本轮29项实际CLI检查包括帮助、旧计划查看/拒绝应用、三个profile缺声明/拒绝应用、旧plan补交声明拒绝，以及有效审查后的应用/正式复验、累计预算和Undo。临时目标最后恢复初始指纹，实测期间已安装Skill不变。

本轮复用[上一轮实测](2026-10-29-installed-architecture-review-smoke.md)中内容指纹完全相同的合成会议候选、独立评审及样例结果，核对三枚指纹并重新运行结果断言。没有把复用证据声称为新的一次模型业务试用。

## 完成状态与证据边界

- [x] 先文档、后隔离实施及测试先行。
- [x] 新预览与Apply双层强制，Active同一门禁，历史恢复保留。
- [x] 独立评审、精确应用与同一计划正式复验。
- [x] 既有安装一致，仓库外29项控制台检查通过。
- [x] Task、Sprint、Spec/Plan、ADR、README、产品/架构、路线图、功能表、指南、Changelog与Daily状态回填。

本轮证明确定性维护门禁与安装可用性，不证明独立评审身份、语义正确或长期业务效用；正式版本仍为1.1.0。没有commit、push、tag或公开发布，其他Sprint保持其原验收状态。

## 提交范围复验与远程交付

状态：Done；独立范围功能提交已推送GitHub并完成远程提交号核验；文档收尾随随后提交交付。不创建Tag或正式Release。

本轮从远程main的 `dec50013024efc29ff0864db0ed6fcd263fee366` 建立 `codex/maintenance-architecture-review`，推送目标为[GitHub仓库](https://github.com/wukongai/skill-engineering)。原main另有未推送的Skill Dissect文档提交，原工作区还包含SEC102、项目收尾和边界确认改动；均不进入本次提交。共享文档和Skill入口仅提取本轮段落，原工作区保留。

独立提交候选实际运行350项pytest全部通过（4.55秒），Ruff、官方Skill validation、Content Gate、production Doctor100/A零问题、portable self-test、credential lint、1.1.0版本一致性和diff检查通过。本节之前的316/404/443及29项CLI记录属于原工作区各轮真实执行，保留原上下文；不把它们冒充干净提交候选的计数。

提交范围为架构审查、CLI/Core双门、Active接入、相关测试、Skill规范与项目文档，共51个文件；未包含其他任务实现及新文档。[功能提交 4df144c](https://github.com/wukongai/skill-engineering/commit/4df144c770b48a445e9f4e06932c17ca8d710c9f) 已推送至[交付分支](https://github.com/wukongai/skill-engineering/tree/codex/maintenance-architecture-review)，远程提交号与本地一致。文档收尾提交位于该功能提交之后；机器状态见[本轮证据](2026-10-29-mandatory-architecture-review-evidence.json)。

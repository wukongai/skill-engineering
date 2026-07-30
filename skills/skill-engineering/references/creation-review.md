# 创建评审与创建后自动化测试

创建评审是创建主链路的固定步骤,不是创建后的可选动作。主路径使用
Doctor v2 rubric 的 `portable creation profile`,不新建第二套效果评分模型,
也不要求安装 Skill Engineering Python CLI:

```bash
python3 scripts/creation_review.py <新 Skill 目录> --profile personal --json
```

它只依赖随 Skill 交付的标准库脚本。完整 CLI Doctor 是维护者和高级用户的
可选增强,用于 contract、provider、evaluation 和更完整的工程规则;完整
Doctor 不可用时,不得阻断 portable 创建评审。

## 写后流程(固定顺序)

1. Content Completion Gate 复跑(`scripts/content_gate.py` 或 Agent-native 等价清单);
2. 创建评审:运行 `scripts/creation_review.py`,产出 0-100 分数、A-F 等级和功能价值、稳定性、安全、工程化四个维度明细;
3. 运行声明式自动化测试入口(见下文);
4. 可选:已安装完整 Python CLI 时再运行完整 Doctor 增强检查;
5. 向用户给出结论先行的自然语言反馈。

## 用户可见创建状态

创建链路只向用户展示这六个状态;内部结构可以映射,但不得把低状态包装成高状态:

| 状态 | 含义 |
|---|---|
| `needs_discovery` | 还缺少会改变结果的信息。 |
| `candidate_incomplete` | 候选存在,但仍有内容缺口(门禁阻断、FAIL 或 SEC 命中)。 |
| `candidate_ready` | 完整候选和预览已准备,尚未写入。 |
| `created_untried` | 已按预览写入并通过创建检查,尚未验证真实任务效果。 |
| `validated` | 至少一个真实任务已完成,并有对应证据。 |
| `needs_improvement` | 真实失败已记录,等待候选修复。 |

- 存在 FAIL 或 SEC 规则命中时,状态不得高于 `candidate_incomplete`,并给出唯一修复入口;
- `created_untried` 的反馈必须同时说明“尚未验证实际任务效果”;没有真实任务试用不得进入 `validated`;
- `scaffold_only`、空资源或占位候选不得报告为“已经验证有效”。

## 用户可见反馈模板

结论先行,只回答三件事:

1. 结果:Skill 是否已创建、分数和等级、当前状态;
2. 影响:能否开始使用、最需要关注的一两个维度、尚未覆盖的边界;
3. 下一步:是否需要用户决定(试运行、修复或进入维护)。

规则命中、维度明细和修复建议折叠进“技术详情”,不强迫小白用户阅读;分数只表述为结构和工程就绪度,不得描述为效果分或业务价值分,不得跨 Skill 排名。
输出必须保留 `utility_claim=false` 和真实样本 `pending`,直到真实任务试用完成。

## Portable coverage

portable profile 固定检查 frontmatter、正向/反向触发边界、输入输出与停止条件、
资源入口、副作用审批、失败处理、敏感文本和声明式自测。权重沿用 Doctor v2:
功能价值 20%、稳定性 25%、安全 25%、工程化 30%,等级阈值同 Doctor v2。

`tests/portable-review-fixtures.json` 枚举 portable profile 与完整 Doctor 的共同
fixture,只对清单内 fixture 承诺 PASS/FAIL、grade 和四维分数一致。portable
profile 只负责上述共同子集,完整 Doctor 还包含额外检查项;两者都不表示已经
验证真实任务效果。

## 创建后简易自动化测试

创建完成时自动生成最小自动化测试入口,用户只需一句话或一条命令即可复跑:

```bash
python3 scripts/skill_self_test.py <新 Skill 目录> [--json]
```

测试分两层:

- 确定性层(脚本自动完成):内容完整性门禁复跑 + portable 创建评审 +
  `tests/self-test.json` 中声明的 Python 脚本真实运行与断言;
- 样例任务层(宿主 Agent 完成):用一个与用户需求一致的真实样本试运行,检查输出形状、证据边界和失败行为。

runner 只执行 manifest 中明确列出的候选内 Python 脚本,在临时副本中使用最小环境、
`-B`、stdin fixture 和 1-30 秒 timeout,并校验退出码、stdout/stderr 与 JSON keys。
它不是操作系统沙箱,不能阻断网络、子进程或强制 CPU/内存上限;因此静态安全门禁
必须先通过。非 Python 测试报告 `uncovered`,不得静默跳过。

两层都通过是进入 `validated` 的证据;任一层失败必须进入 `needs_improvement`,
记录失败模式并走现有 improve 流程,不得包装成成功。宿主没有 Python 时,
确定性层按 `references/content-completion-gate.md` 的 Agent-native 等价清单执行,
并向用户明示。

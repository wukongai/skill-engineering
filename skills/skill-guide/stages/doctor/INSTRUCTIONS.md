# Doctor 阶段

用于体检单个 skill 目录。

1. 读取 `references/doctor-standard.md`。
2. 工具可用时运行 `skill-engineering lint <skill-path>`。
3. 工具可用时运行 `skill-engineering audit <skill-path> --profile <personal|team|production>`。
4. 读取评分:总分、grade、功能价值、稳定性、安全、工程化四个维度。
5. 按层级报告问题:static、structure、behavior-risk、security、install hints、governance。
6. 每个 `WARN` 或 `FAIL` 都给出最小修复位置;低于 80 分时先给最高收益修复建议。
7. 用户没有要求修复时,只报告,不要直接重写 skill。

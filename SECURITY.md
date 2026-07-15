# Security Policy

## 支持范围

Public Beta 期间仅维护最新 `0.x` 版本。安全边界仍在演进，生产使用前应自行审计。

## 报告安全问题

请使用 GitHub 私密安全报告功能；不要在公开 Issue 中粘贴 token、cookie、私钥、客户数据、完整 Prompt 或可利用细节。

报告应包含：受影响版本、最小复现、实际影响和建议缓解方式。请使用脱敏 fixture。

## 关键边界

- Evaluation suite 不执行任意 command/script；
- Candidate generator 不应看到 holdout assertions 或 baseline 评分；
- Global 安装、Canary/Active 发布和不可逆副作用需要明确批准；
- 本地状态不得保存凭证和完整私有会话；
- Doctor 是静态工程审计，不是 sandbox 或完整供应链证明。

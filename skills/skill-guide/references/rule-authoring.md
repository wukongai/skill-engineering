# 规则撰写

Doctor 规则应该防止失败重复发生,但不能把系统变成一堵硬编码偏好墙。

## 规则升级阶梯

1. 一次性记录。
2. review checklist 项。
3. WARN 规则。
4. FAIL 规则。
5. script gate 或 regression fixture。

只有低一级已经证明不够时,才升级规则。

## 硬规则要求

新增 FAIL 规则需要:

- 命名失败模式。
- rule id。
- 影响层级。
- severity rationale。
- remediation hint。
- profile behavior。
- 可行时提供 fixture 或 regression case。
- 如果可能误报,记录 escape hatch。

## Suppression 策略

Suppression 必须显式、可审计。不要把它藏在 `SKILL.md` 的自然语言里,比如“这里先忽略 warning”。

优先做 profile 级别调参,少做一次性例外。

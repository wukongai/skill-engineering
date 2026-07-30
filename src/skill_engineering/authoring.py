"""v1.1 Native Authoring：Authoring Brief 的就绪判定与脱敏。

契约与持久化见 `journey.AuthoringBrief`；本模块只包含产品规则：
哪些字段是候选生成的前置条件，以及保存本地状态前的脱敏。
"""

from __future__ import annotations

import re
from dataclasses import replace
from typing import Any

from .journey import AuthoringBrief

# 缺少任一字段时 Brief 不得进入候选生成（保持 needs_discovery）。
REQUIRED_BRIEF_FIELDS = ("goal", "positive_triggers", "negative_triggers", "verification")

REDACTED = "[redacted]"

_REDACTION_PATTERNS = (
    re.compile(
        r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
        re.DOTALL,
    ),
    re.compile(r"(?i)\b(api[_-]?key|token|secret|password|passwd|cookie|session)\b\s*[:=]\s*[^\s,;]+"),
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]+"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}"),
)


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, tuple, dict)):
        return not value
    return False


def missing_required_fields(brief: AuthoringBrief) -> list[str]:
    """返回候选生成前仍缺失的必填字段；空列表表示可以进入候选生成。"""
    return [
        name for name in REQUIRED_BRIEF_FIELDS if _is_missing(getattr(brief, name, None))
    ]


def brief_ready_for_candidate(brief: AuthoringBrief) -> bool:
    return not missing_required_fields(brief)


def _redact(text: str) -> str:
    for pattern in _REDACTION_PATTERNS:
        text = pattern.sub(REDACTED, text)
    return text


def sanitize_brief(brief: AuthoringBrief) -> AuthoringBrief:
    """返回脱敏副本：字符串与字符串列表中的凭证形态值替换为 `[redacted]`。"""
    changes: dict[str, Any] = {}
    for name, value in vars(brief).items():
        if isinstance(value, str):
            changes[name] = _redact(value)
        elif isinstance(value, list) and all(isinstance(item, str) for item in value):
            changes[name] = [_redact(item) for item in value]
    return replace(brief, **changes)

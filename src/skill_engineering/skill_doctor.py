"""Doctor v2 for skill authoring and install exposure governance."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from .evaluation import load_evaluation_report
from .skill_lint import lint_skill


PROFILES = {"personal", "team", "production"}
PROFILE_ALIASES = {"commercial": "production"}
PROFILE_INPUTS = PROFILES | set(PROFILE_ALIASES)
BROAD_TRIGGER_RE = re.compile(r"\b(anything|everything|all tasks|all files)\b|任意|所有|各种|任何")
COMPLEX_RE = re.compile(
    r"workflow|orchestrator|router|stage|pipeline|approval|state|manifest|"
    r"apply|sync|publish|delete|plugin|global|install|audit|doctor|"
    r"工作流|编排|路由|阶段|状态|审核|安装|插件|全局|体检|治理",
    re.IGNORECASE,
)
SIDE_EFFECT_RE = re.compile(
    r"--apply|auto[- ]?apply|自动.*(执行|调用|同步|发布|写入|删除)|"
    r"\b(apply|sync|publish|delete|write)\b|同步|发布|写入|删除",
    re.IGNORECASE,
)
APPROVAL_RE = re.compile(
    r"approval|approved|confirm|confirmation|用户批准|显式批准|确认|审核", re.IGNORECASE
)
DRY_RUN_RE = re.compile(r"dry[- ]?run|--dry-run|预览|试运行", re.IGNORECASE)
TODAY_FALLBACK_RE = re.compile(
    r"default.*today|fallback.*today|today.*fallback|默认.*今天|今天.*默认",
    re.IGNORECASE,
)
LONG_TASK_RE = re.compile(r"background|long task|poll|async|后台|长任务|轮询|异步", re.IGNORECASE)
TIMEOUT_LOG_RE = re.compile(r"timeout|log|status|超时|日志|状态", re.IGNORECASE)
PROMPT_INJECTION_RE = re.compile(
    r"(ignore|disregard|override|bypass).{0,80}(previous|prior|system|developer|higher[- ]?priority|"
    r"safety|instruction)|"
    r"(reveal|leak|dump|exfiltrate).{0,80}(secret|token|credential|system prompt|private)|"
    r"(do not|don't).{0,40}(tell|show|reveal).{0,40}(user|human)|"
    r"忽略.{0,20}(之前|系统|开发者|更高优先级).{0,20}(指令|规则)|"
    r"(绕过|覆盖).{0,20}(安全|系统|开发者|规则)|"
    r"(泄露|外传|发送).{0,20}(密钥|凭证|token|secret|系统提示词)|"
    r"(不要|不许).{0,20}(告诉|展示).{0,20}(用户|人类)",
    re.IGNORECASE,
)
CREDENTIAL_ACCESS_RE = re.compile(
    r"(?i:os\.environ|process\.env|getenv\s*\(|printenv\b|\benv\s*\||dotenv|\.env\b|"
    r"security\s+find-generic-password|keychain)|"
    r"\b[A-Z][A-Z0-9_]*(?:API[_-]?KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL|PRIVATE[_-]?KEY)[A-Z0-9_]*\b|"
    r"(?i:\b(?:api[_-]?key|secret|password|credential|private[_-]?key)\b\s*(?:=|:))",
)
NETWORK_TRANSFER_RE = re.compile(
    r"\bcurl\b|\bwget\b|fetch\s*\(|requests\.(get|post|put|patch)\s*\(|"
    r"httpx\.(get|post|put|patch)\s*\(|urllib\.request|aiohttp|"
    r"\bscp\b|\brsync\b|\bnc\b|netcat|socket\.connect|"
    r"\baws\s+s3\s+cp\b|\bossutil\b|\baliyun\b",
    re.IGNORECASE,
)
UPLOAD_TRANSFER_RE = re.compile(
    r"requests\.(post|put|patch)\s*\(|httpx\.(post|put|patch)\s*\(|"
    r"fetch\s*\(.{0,120}method\s*:\s*['\"]?(POST|PUT|PATCH)|"
    r"\bcurl\b.{0,120}(-d|--data|-F|--form|-T|--upload-file)|"
    r"\bscp\b|\brsync\b|\bnc\b|netcat|socket\.connect|"
    r"\baws\s+s3\s+cp\b|\bossutil\b|\baliyun\b",
    re.IGNORECASE | re.DOTALL,
)
URL_HOST_RE = re.compile(r"https?://([^/'\"\s:]+)", re.IGNORECASE)
REAL_SECRET_LITERAL_RE = re.compile(
    r"(?i)\b(api[_-]?key|app[_-]?secret|access[_-]?token|refresh[_-]?token|token|"
    r"password|secret|private[_-]?key)\b\s*[:=]\s*['\"]?([^'\"\s#]{16,})"
)
SECRET_PLACEHOLDER_RE = re.compile(
    r"(?i)(example|dummy|fake|test|changeme|change-me|redacted|placeholder|your|xxx|"
    r"todo|none|null|os\.environ|process\.env|getenv|secret_manager|keychain|"
    r"\$\{|<[^>]+>)"
)
ALLOWED_CREDENTIAL_SOURCES = {
    "env",
    "config_file",
    "os_keychain",
    "secret_manager",
    "oauth",
    "docker_mcp_secret",
}
ALLOWED_PROVIDER_CLASSIFICATIONS = {
    "personal_local_byok",
    "open_source_byok",
    "mcp_plugin_runtime",
    "commercial_saas",
}
SECURITY_CASE_PATTERNS = {
    "missing_credentials": re.compile(
        r"missing[-_ ]?credentials|missing.*credential|no.*credential|缺少.*凭证", re.IGNORECASE
    ),
    "redaction": re.compile(r"redact|redaction|脱敏|遮蔽|隐藏.*凭证", re.IGNORECASE),
    "blocked_non_allowlisted_host": re.compile(
        r"blocked.*non[-_ ]?allow|non[-_ ]?allowlisted|outside.*allowlist|allowlist.*block|未允许.*host",
        re.IGNORECASE,
    ),
    "no_secret_json_output": re.compile(
        r"no.*secret.*json|secret.*json.*output|json.*redact|json.*without.*secret|JSON.*不.*凭证|JSON.*脱敏",
        re.IGNORECASE,
    ),
}
TEXT_FILE_SUFFIXES = {
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".json",
    ".py",
    ".js",
    ".ts",
    ".sh",
    ".env",
    ".example",
    ".log",
}


@dataclass(frozen=True)
class DoctorIssue:
    rule_id: str
    level: str  # WARN | FAIL
    layer: str
    path: str
    message: str
    line: int | None = None
    hint: str | None = None


@dataclass(frozen=True)
class ScoreDimension:
    key: str
    label: str
    score: int
    weight: int
    summary: str
    findings: list[str]


@dataclass(frozen=True)
class DoctorScore:
    total: int
    grade: str
    status: str
    dimensions: list[ScoreDimension]
    recommendations: list[str]


@dataclass(frozen=True)
class AssessmentCoverage:
    key: str
    label: str
    status: str  # evaluated | evidence-declared | not-evaluated | not-applicable
    evidence: str


@dataclass(frozen=True)
class SkillAssessment:
    skill_type: str
    method: str
    score_scope: str
    coverage_percent: int
    coverage: list[AssessmentCoverage]
    confidence: str
    utility_claim: str
    limitations: list[str]


@dataclass(frozen=True)
class DoctorResult:
    target: str
    profile: str
    issues: list[DoctorIssue]
    score: DoctorScore | None = None
    assessment: SkillAssessment | None = None

    @property
    def fail_count(self) -> int:
        return sum(1 for issue in self.issues if issue.level == "FAIL")

    @property
    def warn_count(self) -> int:
        return sum(1 for issue in self.issues if issue.level == "WARN")

    def exit_code(self) -> int:
        return 1 if self.fail_count else 0


def _issue(
    issues: list[DoctorIssue],
    rule_id: str,
    level: str,
    layer: str,
    path: Path,
    message: str,
    line: int | None = None,
    hint: str | None = None,
) -> None:
    issues.append(
        DoctorIssue(
            rule_id=rule_id,
            level=level,
            layer=layer,
            path=str(path),
            message=message,
            line=line,
            hint=hint,
        )
    )


def normalize_profile(profile: str) -> str:
    normalized = PROFILE_ALIASES.get(profile, profile)
    if normalized not in PROFILES:
        raise SystemExit(
            f"unknown governance profile: {profile}; choose one of {sorted(PROFILE_INPUTS)}"
        )
    return normalized


def _profile_level(
    profile: str, *, personal: str, team: str | None = None, commercial: str | None = None
) -> str:
    if profile == "production":
        return commercial or team or personal
    if profile == "team":
        return team or personal
    return personal


def _resolve_skill(target: Path) -> tuple[Path, Path | None]:
    if target.is_dir():
        return target, target / "SKILL.md"
    return target.parent, target


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _frontmatter(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    for idx, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            raw = "\n".join(lines[1:idx])
            try:
                data = yaml.safe_load(raw) or {}
            except yaml.YAMLError:
                return {}
            return data if isinstance(data, dict) else {}
    return {}


def _line_of(text: str, pattern: re.Pattern[str]) -> int | None:
    for idx, line in enumerate(text.splitlines(), start=1):
        if pattern.search(line):
            return idx
    return None


def _prompt_injection_location(text: str) -> tuple[re.Match[str] | None, int | None]:
    """Find attack instructions while ignoring explicit defensive prohibitions."""
    defensive = re.compile(r"must\s+not|不得|禁止|不可|避免|防止|用于识别|用于检测", re.IGNORECASE)
    hidden_behavior = re.compile(
        r"(do not|don't).{0,40}(tell|show|reveal).{0,40}(user|human)|"
        r"(不要|不许).{0,20}(告诉|展示).{0,20}(用户|人类)",
        re.IGNORECASE,
    )
    for line_no, line in enumerate(text.splitlines(), start=1):
        match = PROMPT_INJECTION_RE.search(line)
        if not match:
            continue
        if defensive.search(line) and not hidden_behavior.search(line):
            continue
        return match, line_no
    return None, None


def _iter_instruction_files(skill_dir: Path, skill_md: Path) -> list[Path]:
    files: list[Path] = []
    if skill_md.is_file():
        files.append(skill_md)
    for folder in ("references", "stages", "workflows"):
        root = skill_dir / folder
        if root.is_dir():
            files.extend(
                sorted(
                    path
                    for path in root.rglob("*")
                    if path.is_file() and path.suffix.lower() in {".md", ".txt"}
                )
            )
    return files


def _iter_script_files(skill_dir: Path) -> list[Path]:
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.is_dir():
        return []
    ignored_dirs = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules"}
    ignored_suffixes = {
        ".pyc",
        ".pyo",
        ".so",
        ".dylib",
        ".dll",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".pdf",
    }
    return sorted(
        path
        for path in scripts_dir.rglob("*")
        if path.is_file()
        and not ignored_dirs.intersection(path.relative_to(scripts_dir).parts)
        and path.suffix.lower() not in ignored_suffixes
    )


def _iter_security_text_files(skill_dir: Path) -> list[Path]:
    ignored_dirs = {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "node_modules",
        ".git",
    }
    files: list[Path] = []
    for path in skill_dir.rglob("*"):
        if not path.is_file() or ignored_dirs.intersection(path.relative_to(skill_dir).parts):
            continue
        if path.suffix.lower() not in TEXT_FILE_SUFFIXES and ".env" not in path.name.lower():
            continue
        try:
            if path.stat().st_size > 1_000_000:
                continue
        except OSError:
            continue
        files.append(path)
    return sorted(files)


def _contract_data(contract_path: Path, issues: list[DoctorIssue]) -> dict[str, Any] | None:
    if not contract_path.is_file():
        return None
    try:
        data = yaml.safe_load(contract_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        _issue(
            issues,
            "DOC210",
            "FAIL",
            "structure",
            contract_path,
            f"skill.contract.yaml cannot be parsed: {exc}",
            hint="Fix contract YAML before relying on doctor results.",
        )
        return {}
    if not isinstance(data, dict):
        _issue(
            issues,
            "DOC211",
            "FAIL",
            "structure",
            contract_path,
            "skill.contract.yaml must be a mapping.",
            hint="Use docs/references/skill.contract.template.yaml.",
        )
        return {}
    return data


def _read_yaml_silent(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return list(value)
    return [value]


def _normalize_key(value: Any) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower())
    return normalized.strip("_")


def _bool_value(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "y", "1", "ok", "enabled"}:
            return True
        if normalized in {"false", "no", "n", "0", "disabled"}:
            return False
    return None


def _first_bool(*values: Any) -> bool | None:
    for value in values:
        parsed = _bool_value(value)
        if parsed is not None:
            return parsed
    return None


def _provider_contracts(contract: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not contract:
        return []

    providers: list[dict[str, Any]] = []
    for key in ("credentialed_providers", "providers", "external_providers"):
        raw = contract.get(key)
        if isinstance(raw, list):
            providers.extend(item for item in raw if isinstance(item, dict))
        elif isinstance(raw, dict):
            if any(
                field in raw
                for field in (
                    "classification",
                    "credential_sources",
                    "credential_source",
                    "network_allowlist",
                )
            ):
                providers.append(raw)
            else:
                for name, item in raw.items():
                    if isinstance(item, dict):
                        provider = {"name": name}
                        provider.update(item)
                        providers.append(provider)

    if not providers and ("credentials" in contract or "network" in contract):
        provider = {"name": contract.get("name", "provider")}
        if isinstance(contract.get("credentials"), dict):
            provider["credentials"] = contract["credentials"]
        if isinstance(contract.get("network"), dict):
            provider["network"] = contract["network"]
        providers.append(provider)

    return providers


def _provider_credential_sources(provider: dict[str, Any]) -> list[str]:
    credentials = (
        provider.get("credentials") if isinstance(provider.get("credentials"), dict) else {}
    )
    raw_sources = (
        provider.get("credential_sources")
        or provider.get("credential_source")
        or credentials.get("sources")
        or credentials.get("source")
    )
    return [_normalize_key(source) for source in _as_list(raw_sources) if str(source).strip()]


def _provider_allowlist(
    provider: dict[str, Any], contract: dict[str, Any] | None = None
) -> list[str]:
    network = provider.get("network") if isinstance(provider.get("network"), dict) else {}
    contract_network = (
        contract.get("network")
        if isinstance(contract, dict) and isinstance(contract.get("network"), dict)
        else {}
    )
    raw_allowlist = (
        provider.get("network_allowlist")
        or provider.get("network_allow_list")
        or network.get("allowlist")
        or network.get("allow_list")
        or contract_network.get("allowlist")
        or contract_network.get("allow_list")
    )
    return [str(host).strip().lower() for host in _as_list(raw_allowlist) if str(host).strip()]


def _provider_classification(provider: dict[str, Any]) -> str:
    return _normalize_key(
        provider.get("classification") or provider.get("class") or provider.get("kind") or ""
    )


def _provider_secrets_outside_skill_dir(provider: dict[str, Any]) -> bool | None:
    credentials = (
        provider.get("credentials") if isinstance(provider.get("credentials"), dict) else {}
    )
    return _first_bool(
        provider.get("secrets_outside_skill_dir"),
        provider.get("secrets_outside_repo"),
        credentials.get("secrets_outside_skill_dir"),
        credentials.get("secrets_outside_repo"),
        credentials.get("outside_repo"),
    )


def _provider_boundary(provider: dict[str, Any]) -> tuple[bool | None, bool | None]:
    boundary = (
        provider.get("side_effect_boundary")
        if isinstance(provider.get("side_effect_boundary"), dict)
        else {}
    )
    dry_run = _first_bool(
        provider.get("dry_run_no_remote_side_effects"),
        provider.get("dry_run_has_no_remote_side_effects"),
        boundary.get("dry_run_no_remote_side_effects"),
        boundary.get("dry_run_has_no_remote_side_effects"),
        boundary.get("dry_run"),
    )
    approval = _first_bool(
        provider.get("apply_requires_explicit_user_approval"),
        provider.get("apply_requires_explicit_approval"),
        provider.get("create_requires_explicit_user_approval"),
        boundary.get("apply_requires_explicit_user_approval"),
        boundary.get("apply_requires_explicit_approval"),
        boundary.get("approval_required"),
    )
    return dry_run, approval


def _provider_redaction_enabled(provider: dict[str, Any]) -> bool | None:
    redaction = provider.get("redaction") if isinstance(provider.get("redaction"), dict) else {}
    return _first_bool(
        provider.get("redact_outputs"),
        provider.get("output_redaction"),
        redaction.get("enabled"),
        redaction.get("redact_outputs"),
        redaction.get("never_return_secrets"),
    )


def _provider_docs(provider: dict[str, Any]) -> list[str]:
    docs = provider.get("docs") if isinstance(provider.get("docs"), dict) else {}
    raw_docs = (
        provider.get("revoke_rotate_delete_docs")
        or provider.get("credential_lifecycle_docs")
        or docs.get("revoke_rotate_delete")
        or docs.get("credential_lifecycle")
    )
    return [str(doc).strip() for doc in _as_list(raw_docs) if str(doc).strip()]


def _security_case_strings(
    contract: dict[str, Any] | None, providers: list[dict[str, Any]]
) -> list[str]:
    values: list[str] = []

    def collect(raw_tests: Any) -> None:
        if isinstance(raw_tests, dict):
            for key in ("security_cases", "regression_cases", "cases", "verification_commands"):
                for value in _as_list(raw_tests.get(key)):
                    if isinstance(value, dict):
                        values.extend(str(item) for item in value.values() if str(item).strip())
                    elif str(value).strip():
                        values.append(str(value))
        elif isinstance(raw_tests, list):
            for value in raw_tests:
                if isinstance(value, dict):
                    values.extend(str(item) for item in value.values() if str(item).strip())
                elif str(value).strip():
                    values.append(str(value))

    if contract:
        collect(contract.get("tests"))
    for provider in providers:
        collect(provider.get("tests"))
    return values


def _missing_security_cases(case_strings: list[str]) -> list[str]:
    return [
        key
        for key, pattern in SECURITY_CASE_PATTERNS.items()
        if not any(pattern.search(case) for case in case_strings)
    ]


def _script_hosts(script_text: str) -> set[str]:
    return {match.group(1).lower().rstrip(".") for match in URL_HOST_RE.finditer(script_text)}


def _allowlist_hosts(
    providers: list[dict[str, Any]], contract: dict[str, Any] | None = None
) -> list[str]:
    hosts: list[str] = []
    for provider in providers:
        hosts.extend(_provider_allowlist(provider, contract))
    return hosts


def _strip_host(value: str) -> str:
    host = re.sub(r"^https?://", "", value.strip().lower())
    return host.split("/")[0].split(":")[0].rstrip(".")


def _host_allowed(host: str, allowlist_entry: str) -> bool:
    allowed = _strip_host(allowlist_entry)
    if not allowed:
        return False
    if allowed.startswith("*."):
        suffix = allowed[1:]
        return host.endswith(suffix) and host != allowed[2:]
    return host == allowed


def _hosts_outside_allowlist(hosts: set[str], allowlist: list[str]) -> list[str]:
    return sorted(
        host for host in hosts if not any(_host_allowed(host, allowed) for allowed in allowlist)
    )


def _has_valid_credential_contract(providers: list[dict[str, Any]]) -> bool:
    for provider in providers:
        sources = _provider_credential_sources(provider)
        if (
            _provider_classification(provider) in ALLOWED_PROVIDER_CLASSIFICATIONS
            and any(source in ALLOWED_CREDENTIAL_SOURCES for source in sources)
            and _provider_secrets_outside_skill_dir(provider) is True
            and _provider_redaction_enabled(provider) is True
        ):
            return True
    return False


def _has_side_effect_boundary(providers: list[dict[str, Any]]) -> bool:
    for provider in providers:
        dry_run, approval = _provider_boundary(provider)
        if dry_run is True and approval is True:
            return True
    return False


def _real_secret_literal(text: str) -> re.Match[str] | None:
    for match in REAL_SECRET_LITERAL_RE.finditer(text):
        value = match.group(2).strip().strip("'\"")
        if SECRET_PLACEHOLDER_RE.search(value):
            continue
        if len(value) < 16:
            continue
        if not re.search(r"[A-Za-z]", value) or not re.search(r"[0-9_\-]", value):
            continue
        return match
    return None


def _is_complex(skill_dir: Path, text: str, frontmatter: dict[str, Any]) -> bool:
    description = str(frontmatter.get("description") or "")
    return bool(
        COMPLEX_RE.search(text)
        or COMPLEX_RE.search(description)
        or (skill_dir / "stages").is_dir()
        or (skill_dir / "workflows").is_dir()
        or len(list((skill_dir / "scripts").glob("*"))) > 1
    )


def _has_regression_coverage(skill_dir: Path, contract: dict[str, Any] | None) -> bool:
    if contract:
        tests = contract.get("tests")
        if isinstance(tests, dict):
            cases = tests.get("regression_cases")
            if isinstance(cases, list) and any(str(case).strip() for case in cases):
                return True
        if isinstance(tests, list) and tests:
            return True
    local_tests = skill_dir / "tests"
    if local_tests.is_dir() and any(local_tests.rglob("*.yaml")):
        return True
    return False


def _skill_type(skill_dir: Path, text: str, contract: dict[str, Any] | None) -> str:
    kind = _normalize_key((contract or {}).get("kind", ""))
    aliases = {"pipeline": "orchestrator", "workflow": "orchestrator", "toolkit": "composite"}
    if kind:
        return aliases.get(kind, kind)

    nested_skills = [path for path in skill_dir.rglob("SKILL.md") if path != skill_dir / "SKILL.md"]
    lower = text.lower()
    if nested_skills and re.search(r"tool index|toolkit|工具索引|工具集", lower):
        return "composite"
    if nested_skills or re.search(r"orchestrat|pipeline|编排|流水线", lower):
        return "orchestrator"
    if re.search(r"routing|router|路由|分流", lower):
        return "router"
    if re.search(r"adapter|适配器", lower):
        return "adapter"
    return "atomic"


def _evaluation_contract(contract: dict[str, Any] | None) -> dict[str, Any] | None:
    if not contract:
        return None
    evaluation = contract.get("evaluation")
    return evaluation if isinstance(evaluation, dict) else None


def _evaluation_case_kinds(evaluation: dict[str, Any] | None) -> set[str]:
    if not evaluation:
        return set()
    kinds: set[str] = set()
    portfolio = evaluation.get("case_portfolio")
    if isinstance(portfolio, dict):
        for key, value in portfolio.items():
            if value:
                kinds.add(_normalize_key(key))
    for case in _as_list(evaluation.get("cases")):
        if isinstance(case, dict):
            kind = case.get("kind") or case.get("type")
            if kind:
                kinds.add(_normalize_key(kind))
        elif str(case).strip():
            normalized = _normalize_key(case)
            for expected in ("success", "failure", "high_risk"):
                if expected in normalized:
                    kinds.add(expected)
    return kinds


def _evaluation_gate(evaluation: dict[str, Any] | None, key: str) -> bool:
    if not evaluation:
        return False
    candidates = [evaluation.get(key)]
    evidence = evaluation.get("evidence")
    if isinstance(evidence, dict):
        candidates.append(evidence.get(key))
    gates = evaluation.get("gates")
    if isinstance(gates, dict):
        candidates.append(gates.get(key))
    return any(
        value is True or (isinstance(value, (str, list, dict)) and bool(value))
        for value in candidates
    )


def _evaluation_type_checks(evaluation: dict[str, Any] | None) -> set[str]:
    if not evaluation:
        return set()
    value = evaluation.get("type_checks")
    if isinstance(value, dict):
        return {_normalize_key(key) for key, enabled in value.items() if enabled}
    return {_normalize_key(item) for item in _as_list(value) if str(item).strip()}


TYPE_EVALUATION_CHECKS: dict[str, set[str]] = {
    "orchestrator": {"cross_stage_io", "partial_failure", "aggregation"},
    "router": {"positive_routing", "negative_routing", "fallback"},
    "adapter": {"provider_binding", "portability", "error_mapping"},
    "composite": {"tool_index", "orthogonality", "selection_rules", "output_consistency"},
}


def _behavior_report_reference(evaluation: dict[str, Any] | None) -> str | None:
    if not evaluation:
        return None
    value = evaluation.get("behavioral_results")
    if isinstance(value, dict):
        for key in ("report", "path", "artifact"):
            if isinstance(value.get(key), str):
                return value[key]
        return None
    evidence = evaluation.get("evidence")
    if isinstance(evidence, dict):
        nested = evidence.get("behavioral_results")
        if isinstance(nested, dict):
            for key in ("report", "path", "artifact"):
                if isinstance(nested.get(key), str):
                    return nested[key]
    return None


def _behavior_report_info(skill_dir: Path, evaluation: dict[str, Any] | None) -> dict[str, Any]:
    reference = _behavior_report_reference(evaluation)
    declared = _evaluation_gate(evaluation, "behavioral_results")
    if not reference:
        return {
            "status": "evidence-declared" if declared else "not-evaluated",
            "evidence": "声明了行为结果 artifact,但不是可验证 report。"
            if declared
            else "未执行或未声明真实任务结果。",
            "reference": None,
            "report": None,
            "warnings": [],
        }
    report_path = Path(reference).expanduser()
    if not report_path.is_absolute():
        report_path = skill_dir / report_path
    if not report_path.is_file():
        return {
            "status": "evidence-declared",
            "evidence": f"声明了行为 report,但文件不存在:{report_path}",
            "reference": str(report_path),
            "report": None,
            "warnings": ["report_missing"],
        }
    try:
        report, warnings = load_evaluation_report(report_path)
    except SystemExit as exc:
        return {
            "status": "fail",
            "evidence": f"行为 report 无效:{exc}",
            "reference": str(report_path),
            "report": None,
            "warnings": [str(exc)],
        }
    expected_suite = evaluation.get("suite_id") if evaluation else None
    if expected_suite and report.get("suite_id") != expected_suite:
        warnings.append(f"contract suite_id 不匹配:{expected_suite} != {report.get('suite_id')}")
    decision = report.get("decision")
    status = "fail" if warnings or decision == "reject" else "evaluated"
    return {
        "status": status,
        "evidence": (
            f"已验证行为 report:{report_path} (decision={decision})"
            if not warnings
            else f"行为 report 证据无效或漂移:{'; '.join(warnings)}"
        ),
        "reference": str(report_path),
        "report": report,
        "warnings": warnings,
    }


def _check_evaluation(
    skill_dir: Path,
    text: str,
    frontmatter: dict[str, Any],
    contract: dict[str, Any] | None,
    profile: str,
    issues: list[DoctorIssue],
) -> None:
    complex_skill = _is_complex(skill_dir, text, frontmatter)
    evaluation = _evaluation_contract(contract)
    skill_type = _skill_type(skill_dir, text, contract)
    contract_path = skill_dir / "skill.contract.yaml"

    high_risk = bool(SIDE_EFFECT_RE.search(text))

    # 普通 personal/team Skill 不被迫补齐完整证据包。只有 production、
    # 高风险流程或作者已经显式声明 evaluation 时才进入证据门禁。
    if complex_skill and evaluation is None and (profile == "production" or high_risk):
        _issue(
            issues,
            "EVAL101",
            _profile_level(profile, personal="WARN", team="WARN", commercial="FAIL"),
            "evaluation",
            contract_path if contract else skill_dir,
            "complex skill does not declare an evaluation evidence contract.",
            hint="Declare evaluation cases, evidence gates, independent review, and type-specific checks.",
        )
        return

    if not evaluation:
        return

    required_case_kinds = {"success", "failure", "high_risk"}
    missing_case_kinds = sorted(required_case_kinds - _evaluation_case_kinds(evaluation))
    if missing_case_kinds:
        _issue(
            issues,
            "EVAL102",
            _profile_level(profile, personal="WARN", team="WARN", commercial="FAIL"),
            "evaluation",
            contract_path,
            f"evaluation case portfolio is missing: {', '.join(missing_case_kinds)}.",
            hint="Add success, failure, and high-risk fixtures; do not infer coverage from prose alone.",
        )

    if profile == "production":
        required_gates = {"baseline", "holdout", "negative_transfer"}
        missing_gates = sorted(
            key for key in required_gates if not _evaluation_gate(evaluation, key)
        )
        if missing_gates:
            _issue(
                issues,
                "EVAL103",
                "FAIL",
                "evaluation",
                contract_path,
                f"production evaluation lacks utility gates: {', '.join(missing_gates)}.",
                hint="Declare baseline comparison, held-out cases, and a negative-transfer rejection gate.",
            )

    required_type_checks = TYPE_EVALUATION_CHECKS.get(skill_type, set())
    missing_type_checks = sorted(required_type_checks - _evaluation_type_checks(evaluation))
    if missing_type_checks:
        _issue(
            issues,
            "EVAL104",
            _profile_level(profile, personal="WARN", team="WARN", commercial="FAIL"),
            "evaluation",
            contract_path,
            f"{skill_type} evaluation lacks type-specific checks: {', '.join(missing_type_checks)}.",
            hint=f"Add evaluation.type_checks for the {skill_type} failure surface.",
        )

    claims = evaluation.get("claims") if isinstance(evaluation.get("claims"), dict) else {}
    claims_utility = _bool_value(claims.get("utility")) is True or _normalize_key(
        evaluation.get("score_scope", "")
    ) in {
        "utility",
        "downstream_utility",
        "effectiveness",
    }
    has_behavioral = _evaluation_gate(evaluation, "behavioral_results")
    if claims_utility and not (
        has_behavioral
        and _evaluation_gate(evaluation, "baseline")
        and _evaluation_gate(evaluation, "holdout")
    ):
        _issue(
            issues,
            "EVAL105",
            _profile_level(profile, personal="WARN", team="FAIL", commercial="FAIL"),
            "evaluation",
            contract_path,
            "evaluation claims downstream utility without behavioral baseline and holdout evidence.",
            hint="Relabel the score as structural readiness or attach executable behavioral, baseline, and holdout evidence.",
        )

    behavior_info = _behavior_report_info(skill_dir, evaluation)
    report = behavior_info.get("report") or {}
    if (
        behavior_info["status"] == "fail"
        and report.get("decision") == "reject"
        and not behavior_info["warnings"]
    ):
        _issue(
            issues,
            "EVAL106",
            _profile_level(profile, personal="WARN", team="FAIL", commercial="FAIL"),
            "evaluation",
            Path(behavior_info["reference"]),
            "deterministic behavioral evidence rejected the candidate.",
            hint="Inspect failed holdout/high-risk cases and negative-transfer evidence before accepting this Skill.",
        )
    elif behavior_info["status"] == "fail" or behavior_info["warnings"]:
        _issue(
            issues,
            "EVAL107",
            _profile_level(profile, personal="WARN", team="WARN", commercial="FAIL"),
            "evaluation",
            Path(behavior_info["reference"] or contract_path),
            behavior_info["evidence"],
            hint="Regenerate the report from unchanged suite/results artifacts and update the contract reference.",
        )
    elif report.get("decision") == "inconclusive":
        _issue(
            issues,
            "EVAL107",
            _profile_level(profile, personal="WARN", team="WARN", commercial="FAIL"),
            "evaluation",
            Path(behavior_info["reference"]),
            "behavioral report is inconclusive because evidence coverage is incomplete.",
            hint="Provide baseline and candidate results for every development and holdout case.",
        )


def _check_structure(
    skill_dir: Path,
    skill_md: Path,
    text: str,
    frontmatter: dict[str, Any],
    profile: str,
    issues: list[DoctorIssue],
) -> None:
    contract_path = skill_dir / "skill.contract.yaml"
    contract = _contract_data(contract_path, issues)
    complex_skill = _is_complex(skill_dir, text, frontmatter)

    if complex_skill and contract is None:
        side_effecting = bool(SIDE_EFFECT_RE.search(text))
        level = "WARN"
        if side_effecting:
            level = _profile_level(profile, personal="WARN", team="FAIL", commercial="FAIL")
        elif profile == "production":
            level = "FAIL"
        _issue(
            issues,
            "DOC201",
            level,
            "structure",
            skill_dir,
            "complex skill has no skill.contract.yaml.",
            hint="Add a contract with inputs, outputs, stops, delegates, forbidden actions, state, scripts, and tests.",
        )

    if contract:
        required = ["name", "kind", "inputs", "outputs", "stops", "forbidden"]
        missing = [key for key in required if key not in contract]
        if missing:
            _issue(
                issues,
                "DOC202",
                _profile_level(profile, personal="WARN", team="WARN", commercial="FAIL"),
                "structure",
                contract_path,
                f"contract is missing fields: {', '.join(missing)}.",
                hint="Fill the stable boundary before expanding SKILL.md.",
            )
        if complex_skill and not _has_regression_coverage(skill_dir, contract):
            _issue(
                issues,
                "DOC206",
                _profile_level(profile, personal="WARN", team="WARN", commercial="FAIL"),
                "structure",
                contract_path,
                "complex skill contract does not declare regression coverage.",
                hint="Add tests.regression_cases or a local tests/ fixture for risky behavior.",
            )

    stage_skill_files = sorted((skill_dir / "stages").glob("**/SKILL.md"))
    stage_skill_files.extend(sorted((skill_dir / "workflows").glob("**/SKILL.md")))
    for stage_skill in stage_skill_files:
        _issue(
            issues,
            "DOC203",
            _profile_level(profile, personal="WARN", team="FAIL", commercial="FAIL"),
            "structure",
            stage_skill,
            "internal workflow step uses SKILL.md and may be exposed as a top-level skill.",
            hint="Rename internal workflow step entries to INSTRUCTIONS.md and route to them from the root skill.",
        )

    references = (
        sorted((skill_dir / "references").glob("*")) if (skill_dir / "references").is_dir() else []
    )
    if references and "references/" not in text and "references\\" not in text:
        _issue(
            issues,
            "DOC204",
            "WARN",
            "structure",
            skill_md,
            "references/ exists but root SKILL.md does not explain when to read it.",
            hint="Add a concise route from SKILL.md to each relevant reference file.",
        )

    scripts_dir = skill_dir / "scripts"
    scripts = [p for p in scripts_dir.glob("*") if p.is_file()] if scripts_dir.is_dir() else []
    if scripts and "scripts/" not in text and "script" not in text.lower():
        _issue(
            issues,
            "DOC205",
            "WARN",
            "structure",
            skill_md,
            "scripts/ exists but root SKILL.md does not name the script boundary.",
            hint="Mention which deterministic operations belong to scripts and how to run validation.",
        )


def _check_behavior(skill_md: Path, text: str, profile: str, issues: list[DoctorIssue]) -> None:
    side_effect = SIDE_EFFECT_RE.search(text)
    if side_effect and not (APPROVAL_RE.search(text) or DRY_RUN_RE.search(text)):
        _issue(
            issues,
            "DOC301",
            "FAIL",
            "behavior-risk",
            skill_md,
            "side-effect wording appears without explicit approval or dry-run boundary.",
            line=_line_of(text, SIDE_EFFECT_RE),
            hint="Require explicit approval and a dry-run/apply split for write/sync/delete/publish actions.",
        )

    today = TODAY_FALLBACK_RE.search(text)
    if today and not re.search(r"explicit|显式|用户提供|禁止", text, re.IGNORECASE):
        _issue(
            issues,
            "DOC302",
            _profile_level(profile, personal="WARN", team="FAIL", commercial="FAIL"),
            "behavior-risk",
            skill_md,
            "implicit today fallback can create date-sensitive execution errors.",
            line=_line_of(text, TODAY_FALLBACK_RE),
            hint="Require explicit date input or encode fallback policy in a script/contract.",
        )

    long_task = LONG_TASK_RE.search(text)
    if long_task and not TIMEOUT_LOG_RE.search(text):
        _issue(
            issues,
            "DOC303",
            "WARN",
            "behavior-risk",
            skill_md,
            "long-task/background wording appears without timeout, log, or status handling.",
            line=_line_of(text, LONG_TASK_RE),
            hint="Move long-task execution to a runner with timeout, retry, and log capture.",
        )


def _check_security(
    skill_dir: Path,
    skill_md: Path,
    profile: str,
    issues: list[DoctorIssue],
    contract: dict[str, Any] | None,
) -> None:
    for security_file in _iter_security_text_files(skill_dir):
        security_text = _read_text(security_file)
        secret_literal = _real_secret_literal(security_text)
        if secret_literal:
            _issue(
                issues,
                "SEC105",
                "FAIL",
                "security",
                security_file,
                "real secret-like value appears in the skill directory.",
                line=_line_of(security_text, REAL_SECRET_LITERAL_RE),
                hint="Remove the value, rotate it if it was real, and keep only placeholders or external credential pointers.",
            )

    for instruction_file in _iter_instruction_files(skill_dir, skill_md):
        instruction_text = _read_text(instruction_file)
        prompt_injection, prompt_injection_line = _prompt_injection_location(instruction_text)
        if prompt_injection:
            _issue(
                issues,
                "SEC103",
                _profile_level(profile, personal="WARN", team="FAIL", commercial="FAIL"),
                "security",
                instruction_file,
                "prompt-injection style instruction appears in skill instructions.",
                line=prompt_injection_line,
                hint="Remove hidden override/exfiltration wording; if documenting attacks, move examples to tests with explicit benign fixtures.",
            )

    providers = _provider_contracts(contract)
    allowlist = _allowlist_hosts(providers, contract)
    credential_contract_ok = _has_valid_credential_contract(providers)
    side_effect_boundary_ok = _has_side_effect_boundary(providers)
    emitted_contract_security_rules: set[str] = set()

    for script in _iter_script_files(skill_dir):
        script_text = _read_text(script)
        credential_access = CREDENTIAL_ACCESS_RE.search(script_text)
        network_transfer = NETWORK_TRANSFER_RE.search(script_text)
        upload_transfer = UPLOAD_TRANSFER_RE.search(script_text)
        script_hosts = _script_hosts(script_text)
        outside_allowlist = (
            _hosts_outside_allowlist(script_hosts, allowlist) if allowlist else sorted(script_hosts)
        )

        if network_transfer:
            missing_network_controls: list[str] = []
            if not allowlist:
                missing_network_controls.append("network allowlist")
            if outside_allowlist:
                missing_network_controls.append(
                    f"allowlist coverage for: {', '.join(outside_allowlist)}"
                )
            if upload_transfer and not side_effect_boundary_ok:
                missing_network_controls.append("dry-run/apply approval boundary")
            if missing_network_controls:
                _issue(
                    issues,
                    "SEC101",
                    _profile_level(profile, personal="WARN", team="FAIL", commercial="FAIL"),
                    "security",
                    script,
                    "script contains outbound network transfer without required provider controls.",
                    line=_line_of(script_text, NETWORK_TRANSFER_RE),
                    hint=f"Add contract controls for {', '.join(missing_network_controls)}.",
                )
        if credential_access:
            if not credential_contract_ok:
                _issue(
                    issues,
                    "SEC102",
                    _profile_level(profile, personal="WARN", team="FAIL", commercial="FAIL"),
                    "security",
                    script,
                    "script accesses credentials without a managed credential provider contract.",
                    line=_line_of(script_text, CREDENTIAL_ACCESS_RE),
                    hint=(
                        "Declare provider classification, allowed credential source, secrets-outside-skill-dir, "
                        "and output redaction in skill.contract.yaml."
                    ),
                )
        if credential_access and (upload_transfer or network_transfer):
            if not providers:
                _issue(
                    issues,
                    "SEC104",
                    "FAIL",
                    "security",
                    script,
                    "script combines credential access with network transfer without a provider contract.",
                    line=_line_of(
                        script_text, UPLOAD_TRANSFER_RE if upload_transfer else NETWORK_TRANSFER_RE
                    ),
                    hint=(
                        "Add a credentialed provider contract with credential source, network allowlist, "
                        "redaction, dry-run/apply approval, and security regression cases."
                    ),
                )
            elif "SEC106" not in emitted_contract_security_rules:
                missing_cases = _missing_security_cases(_security_case_strings(contract, providers))
                if missing_cases:
                    emitted_contract_security_rules.add("SEC106")
                    _issue(
                        issues,
                        "SEC106",
                        _profile_level(profile, personal="WARN", team="WARN", commercial="FAIL"),
                        "security",
                        skill_dir / "skill.contract.yaml",
                        "credentialed provider contract lacks required security regression coverage.",
                        hint=f"Add tests for: {', '.join(missing_cases)}.",
                    )
            if providers and "SEC107" not in emitted_contract_security_rules:
                docs_missing = not any(_provider_docs(provider) for provider in providers)
                docs_invalid = False
                for provider in providers:
                    for doc in _provider_docs(provider):
                        if re.match(r"https?://", doc):
                            continue
                        doc_path = (skill_dir / doc).resolve()
                        if not doc_path.is_file():
                            docs_invalid = True
                            continue
                        doc_text = _read_text(doc_path)
                        if not re.search(
                            r"revoke|rotate|delete|吊销|撤销|轮换|删除", doc_text, re.IGNORECASE
                        ):
                            docs_invalid = True
                if docs_missing or docs_invalid:
                    emitted_contract_security_rules.add("SEC107")
                    _issue(
                        issues,
                        "SEC107",
                        _profile_level(profile, personal="WARN", team="WARN", commercial="FAIL"),
                        "security",
                        skill_dir / "skill.contract.yaml",
                        "credentialed provider install docs do not cover revoke/rotate/delete credentials.",
                        hint="Add install docs that explain how to revoke, rotate, and delete provider credentials.",
                    )


def _check_selection(
    skill_md: Path, text: str, frontmatter: dict[str, Any], issues: list[DoctorIssue]
) -> None:
    description = str(frontmatter.get("description") or "")
    if BROAD_TRIGGER_RE.search(description):
        _issue(
            issues,
            "DOC401",
            "WARN",
            "selection",
            skill_md,
            "description contains broad trigger wording.",
            line=_line_of(text, BROAD_TRIGGER_RE),
            hint="Add concrete triggers and anti-triggers; consider project docs or scripts for narrow behavior.",
        )

    lower = (description + "\n" + text).lower()
    if (
        "plugin" in lower
        and "script" in lower
        and not re.search(r"select|selection|decide|matrix|选择|判断", lower)
    ):
        _issue(
            issues,
            "DOC402",
            "WARN",
            "selection",
            skill_md,
            "skill mentions plugin and script options but does not define a selection process.",
            hint="Add a selection matrix so authors know whether to create a skill, plugin, script, doc, or profile entry.",
        )


def doctor_skill(target: Path, profile: str = "personal") -> DoctorResult:
    profile = normalize_profile(profile)

    issues: list[DoctorIssue] = []
    lint_result = lint_skill(target)
    for lint_issue in lint_result.issues:
        _issue(
            issues,
            lint_issue.rule_id,
            "FAIL" if lint_issue.severity == "error" else "WARN",
            "static",
            Path(lint_issue.path),
            lint_issue.message,
            line=lint_issue.line,
            hint=lint_issue.hint,
        )

    skill_dir, skill_md = _resolve_skill(target)
    if not skill_md or not skill_md.is_file():
        return DoctorResult(
            str(target), profile, issues, _score_skill(target, "", {}, None, issues)
        )

    text = _read_text(skill_md)
    frontmatter = _frontmatter(text)
    _check_structure(skill_dir, skill_md, text, frontmatter, profile, issues)
    _check_behavior(skill_md, text, profile, issues)
    contract = _read_yaml_silent(skill_dir / "skill.contract.yaml")
    _check_security(skill_dir, skill_md, profile, issues, contract)
    _check_selection(skill_md, text, frontmatter, issues)
    _check_evaluation(skill_dir, text, frontmatter, contract, profile, issues)
    return DoctorResult(
        str(target),
        profile,
        issues,
        _score_skill(skill_dir, text, frontmatter, contract, issues),
        _build_assessment(skill_dir, text, frontmatter, contract),
    )


def _build_assessment(
    skill_dir: Path,
    text: str,
    frontmatter: dict[str, Any],
    contract: dict[str, Any] | None,
) -> SkillAssessment:
    complex_skill = _is_complex(skill_dir, text, frontmatter)
    evaluation = _evaluation_contract(contract)
    regression = _has_regression_coverage(skill_dir, contract)
    skill_type = _skill_type(skill_dir, text, contract)
    behavior_info = _behavior_report_info(skill_dir, evaluation)
    behavior_report = behavior_info.get("report") or {}

    def coverage(
        key: str, label: str, present: bool, evidence: str, *, applicable: bool = True
    ) -> AssessmentCoverage:
        if not applicable:
            return AssessmentCoverage(key, label, "not-applicable", evidence)
        return AssessmentCoverage(
            key, label, "evidence-declared" if present else "not-evaluated", evidence
        )

    items = [
        AssessmentCoverage(
            "static", "静态检查", "evaluated", "Doctor 已读取入口、结构和本地规则信号。"
        ),
        coverage(
            "contract",
            "契约覆盖",
            contract is not None,
            "存在 skill.contract.yaml。" if contract else "未声明机器可读 contract。",
            applicable=complex_skill or contract is not None,
        ),
        coverage(
            "regression",
            "回归用例",
            regression,
            "存在 regression case 声明或 fixture。" if regression else "未发现 regression case。",
            applicable=complex_skill or regression,
        ),
        AssessmentCoverage(
            "behavioral",
            "行为结果",
            behavior_info["status"],
            behavior_info["evidence"],
        ),
        AssessmentCoverage(
            "holdout",
            "留出集",
            (
                "evaluated"
                if behavior_report.get("coverage", {}).get("has_holdout")
                and behavior_info["status"] in {"evaluated", "fail"}
                else "evidence-declared"
                if _evaluation_gate(evaluation, "holdout")
                else "not-evaluated"
            ),
            (
                "行为 report 已包含 holdout。"
                if behavior_report.get("coverage", {}).get("has_holdout")
                else "声明了 holdout 证据。"
                if _evaluation_gate(evaluation, "holdout")
                else "未声明 held-out evaluation。"
            ),
        ),
        coverage(
            "independent_review",
            "独立评审",
            _evaluation_gate(evaluation, "independent_review"),
            "声明编辑者之外的独立评审。"
            if _evaluation_gate(evaluation, "independent_review")
            else "未声明独立 reviewer。",
        ),
    ]
    applicable_items = [item for item in items if item.status != "not-applicable"]
    covered = sum(
        item.status in {"evaluated", "evidence-declared", "fail"} for item in applicable_items
    )
    coverage_percent = round(covered * 100 / len(applicable_items)) if applicable_items else 0

    declared_utility_evidence = all(
        _evaluation_gate(evaluation, key)
        for key in ("behavioral_results", "baseline", "holdout", "negative_transfer")
    )
    accepted_behavioral_evidence = (
        behavior_info["status"] == "evaluated" and behavior_report.get("decision") == "accept"
    )
    confidence = "medium" if coverage_percent >= 50 else "low"
    limitations = [
        "质量分仅衡量静态工程健康度,不等于下游任务效用。",
    ]
    if accepted_behavioral_evidence:
        limitations.extend(behavior_report.get("limitations") or [])
    else:
        limitations.append(
            "evidence-declared 只表示 contract 有声明;本次 Doctor 未认证有效的 accept 行为报告。"
        )
    if not declared_utility_evidence and not accepted_behavioral_evidence:
        limitations.append(
            "缺少 behavioral + baseline + holdout + negative-transfer 证据,不得宣称效果已验证。"
        )
    if not _evaluation_gate(evaluation, "independent_review"):
        limitations.append("未声明独立评审,语义判断可能受编辑者自评偏差影响。")

    return SkillAssessment(
        skill_type=skill_type,
        method=(
            "static-engineering-doctor+deterministic-behavior-evidence"
            if behavior_info["status"] in {"evaluated", "fail"}
            else "static-engineering-doctor"
        ),
        score_scope="structural-readiness",
        coverage_percent=coverage_percent,
        coverage=items,
        confidence=confidence,
        utility_claim=(
            "behavioral-evidence"
            if accepted_behavioral_evidence
            else "evidence-failed"
            if behavior_info["status"] == "fail"
            else "not-evaluated"
            if behavior_report.get("decision") == "inconclusive"
            else "evidence-declared"
            if declared_utility_evidence
            else "not-evaluated"
        ),
        limitations=limitations,
    )


def _bounded_score(value: int) -> int:
    return max(0, min(100, value))


SCORE_DEDUCTIONS: dict[str, dict[str, int]] = {
    "SKILL000": {"functional_value": 35, "stability": 25, "engineering": 40},
    "SKILL010": {"functional_value": 25, "engineering": 20},
    "SKILL011": {"functional_value": 15, "engineering": 15},
    "SKILL012": {"functional_value": 35, "engineering": 20},
    "SKILL020": {"functional_value": 10, "stability": 10, "engineering": 30},
    "SKILL021": {"stability": 25, "security": 20, "engineering": 15},
    "SKILL022": {"functional_value": 15, "stability": 25, "engineering": 15},
    "SKILL030": {"engineering": 20},
    "SKILL040": {"stability": 20, "engineering": 20},
    "SKILL041": {"stability": 20, "engineering": 20},
    "SKILL101": {"functional_value": 15, "engineering": 10},
    "SKILL120": {"functional_value": 5, "engineering": 15},
    "SKILL121": {"stability": 10, "engineering": 10},
    "SKILL122": {"functional_value": 5, "engineering": 10},
    "SKILL123": {"functional_value": 5, "engineering": 10},
    "SKILL130": {"functional_value": 10, "engineering": 15},
    "SKILL140": {"engineering": 10},
    "DOC201": {"stability": 25, "engineering": 20},
    "DOC202": {"stability": 15, "engineering": 15},
    "DOC203": {"functional_value": 10, "engineering": 25},
    "DOC204": {"engineering": 12},
    "DOC205": {"stability": 8, "engineering": 10},
    "DOC206": {"stability": 18, "engineering": 8},
    "DOC210": {"stability": 20, "engineering": 20},
    "DOC211": {"stability": 20, "engineering": 20},
    "DOC301": {"stability": 25, "security": 25, "engineering": 10},
    "DOC302": {"stability": 25},
    "DOC303": {"stability": 12},
    "DOC401": {"functional_value": 20, "engineering": 8},
    "DOC402": {"functional_value": 12, "engineering": 8},
    "SEC101": {"stability": 8, "security": 25, "engineering": 8},
    "SEC102": {"stability": 10, "security": 35, "engineering": 8},
    "SEC103": {"functional_value": 15, "security": 55, "engineering": 8},
    "SEC104": {"stability": 15, "security": 70, "engineering": 12},
    "SEC105": {"stability": 10, "security": 90, "engineering": 10},
    "SEC106": {"stability": 18, "security": 35, "engineering": 8},
    "SEC107": {"stability": 10, "security": 25, "engineering": 8},
    "EVAL101": {"functional_value": 8, "stability": 12, "engineering": 10},
    "EVAL102": {"stability": 12, "engineering": 5},
    "EVAL103": {"functional_value": 12, "stability": 25, "engineering": 8},
    "EVAL104": {"functional_value": 8, "stability": 15, "engineering": 8},
    "EVAL105": {"functional_value": 25, "stability": 20, "engineering": 10},
    "EVAL106": {"functional_value": 30, "stability": 30},
    "EVAL107": {"stability": 20, "engineering": 10},
    "INSTALL000": {"stability": 35, "engineering": 15},
    "INSTALL001": {"stability": 35, "engineering": 15},
    "INSTALL002": {"stability": 40, "engineering": 10},
    "INSTALL003": {"engineering": 12},
    "INSTALL004": {"engineering": 15},
    "INSTALL005": {"functional_value": 10, "engineering": 10},
    "INSTALL006": {"functional_value": 10, "engineering": 25},
    "INSTALL007": {"functional_value": 15, "engineering": 10},
    "INSTALL008": {"functional_value": 12, "engineering": 10},
    "INSTALL009": {"functional_value": 8, "engineering": 10},
}


DIMENSION_META = {
    "functional_value": ("功能价值", 20),
    "stability": ("稳定性", 25),
    "security": ("安全", 25),
    "engineering": ("工程化", 30),
}


def _grade(total: int) -> tuple[str, str]:
    if total >= 90:
        return "A", "excellent"
    if total >= 80:
        return "B", "healthy"
    if total >= 70:
        return "C", "review-needed"
    if total >= 60:
        return "D", "rework-needed"
    return "F", "blocked"


def _issue_recommendations(issues: list[DoctorIssue], limit: int = 5) -> list[str]:
    recommendations: list[str] = []
    seen: set[str] = set()
    ordered = sorted(issues, key=lambda issue: (0 if issue.level == "FAIL" else 1, issue.rule_id))
    for issue in ordered:
        if not issue.hint or issue.hint in seen:
            continue
        seen.add(issue.hint)
        recommendations.append(f"{issue.rule_id}: {issue.hint}")
        if len(recommendations) >= limit:
            break
    return recommendations


def _dimension_summary(score: int) -> str:
    if score >= 90:
        return "边界清楚,维护风险低。"
    if score >= 80:
        return "整体健康,只需小幅收敛。"
    if score >= 70:
        return "可用但需要 review 后共享。"
    if score >= 60:
        return "存在明显返工点。"
    return "不建议安装或共享,先修复基础问题。"


def _score_from_issues(issues: list[DoctorIssue]) -> dict[str, int]:
    scores = {key: 100 for key in DIMENSION_META}
    for issue in issues:
        deductions = SCORE_DEDUCTIONS.get(issue.rule_id, {})
        level_factor = 1.25 if issue.level == "FAIL" else 1.0
        for key, amount in deductions.items():
            scores[key] -= round(amount * level_factor)
    return {key: _bounded_score(value) for key, value in scores.items()}


def _score_skill(
    skill_dir: Path,
    text: str,
    frontmatter: dict[str, Any],
    contract: dict[str, Any] | None,
    issues: list[DoctorIssue],
) -> DoctorScore:
    scores = _score_from_issues(issues)
    findings: dict[str, list[str]] = {key: [] for key in DIMENSION_META}

    description = str(frontmatter.get("description") or "")
    if description and 40 <= len(description) <= 350 and not BROAD_TRIGGER_RE.search(description):
        findings["functional_value"].append("description 有明确触发语义。")
    elif not description:
        findings["functional_value"].append("缺少 description,agent 很难判断是否该触发。")
    else:
        findings["functional_value"].append("description 需要进一步收窄触发词、功能一句话和边界。")

    boundary_text = "\n".join([description, text])
    if contract and all(key in contract for key in ("inputs", "outputs", "stops", "forbidden")):
        findings["functional_value"].append("contract 覆盖 inputs/outputs/stops/forbidden。")
    elif re.search(
        r"输入|输出|停止|不要|禁止|input|output|stop|forbidden", boundary_text, re.IGNORECASE
    ):
        findings["functional_value"].append("入口文本包含基本输入输出或停止边界。")
    else:
        scores["functional_value"] = _bounded_score(scores["functional_value"] - 10)
        findings["functional_value"].append("缺少可验证的输入、输出、停止或禁止边界。")

    complex_skill = _is_complex(skill_dir, text, frontmatter) if text else bool(issues)
    if _has_regression_coverage(skill_dir, contract):
        findings["stability"].append("声明了 regression coverage。")
    elif complex_skill:
        findings["stability"].append("复杂 skill 缺少 regression case。")

    if contract and contract.get("state"):
        findings["stability"].append("contract 声明了跨会话状态。")
    elif complex_skill:
        scores["stability"] = _bounded_score(scores["stability"] - 8)
        findings["stability"].append("复杂流程没有显式 state 设计。")

    if (skill_dir / "scripts").is_dir() and any((skill_dir / "scripts").glob("*")):
        findings["stability"].append("存在 scripts/ 承接确定性步骤。")
    elif re.search(
        r"日期|路径|文件|URL|状态|timeout|apply|sync|publish|delete", boundary_text, re.IGNORECASE
    ):
        scores["stability"] = _bounded_score(scores["stability"] - 8)
        findings["stability"].append("文本提到确定性或副作用步骤,但没有 scripts/ 辅助。")

    security_issues = [issue for issue in issues if issue.rule_id.startswith("SEC")]
    if security_issues:
        findings["security"].append("存在安全审计命中,安装或共享前需要人工复核。")
    else:
        findings["security"].append("未命中 prompt injection、凭证访问、网络传输或数据外传规则。")

    line_count = len(text.splitlines()) if text else 0
    if line_count and line_count <= 120:
        findings["engineering"].append("根 SKILL.md 保持轻量。")
    elif line_count:
        findings["engineering"].append("根 SKILL.md 偏厚,建议继续拆到 references/scripts/tests。")

    references_dir = skill_dir / "references"
    if references_dir.is_dir() and any(references_dir.glob("*")):
        findings["engineering"].append("存在 references/ 支持渐进披露。")
    elif line_count > 80:
        scores["engineering"] = _bounded_score(scores["engineering"] - 8)
        findings["engineering"].append("较长入口缺少 references/ 拆分。")

    dimensions: list[ScoreDimension] = []
    for key, (label, weight) in DIMENSION_META.items():
        dimensions.append(
            ScoreDimension(
                key=key,
                label=label,
                score=scores[key],
                weight=weight,
                summary=_dimension_summary(scores[key]),
                findings=findings[key],
            )
        )
    total = round(sum(dim.score * dim.weight / 100 for dim in dimensions))
    grade, status = _grade(total)
    recommendations = _issue_recommendations(issues)
    if total < 80 and not recommendations:
        recommendations.append(
            "补齐触发边界、contract、脚本边界和 regression case 后再共享或安装。"
        )
    return DoctorScore(
        total=total,
        grade=grade,
        status=status,
        dimensions=dimensions,
        recommendations=recommendations,
    )


def _format_score(score: DoctorScore) -> list[str]:
    lines = [
        f"Score: {score.total}/100 ({score.grade}, {score.status})",
        "Dimensions:",
    ]
    for dim in score.dimensions:
        lines.append(f"- {dim.label} {dim.score}/100 (weight {dim.weight}%): {dim.summary}")
        for finding in dim.findings:
            lines.append(f"  - {finding}")
    if score.recommendations:
        lines.append("Recommendations:")
        for recommendation in score.recommendations:
            lines.append(f"- {recommendation}")
    return lines


def _format_assessment(assessment: SkillAssessment) -> list[str]:
    lines = [
        (
            f"Assessment: type={assessment.skill_type}, method={assessment.method}, "
            f"scope={assessment.score_scope}, coverage={assessment.coverage_percent}%, "
            f"confidence={assessment.confidence}, utility={assessment.utility_claim}"
        ),
        "Evidence coverage:",
    ]
    for item in assessment.coverage:
        lines.append(f"- {item.label}: {item.status} — {item.evidence}")
    lines.append("Limitations:")
    lines.extend(f"- {limitation}" for limitation in assessment.limitations)
    return lines


def format_text(result: DoctorResult) -> str:
    lines = [
        "Skill doctor report:" if result.issues else "Skill doctor report: OK",
        f"Target: {result.target}",
        f"Profile: {result.profile}",
    ]
    if result.score:
        lines.extend(_format_score(result.score))
    if result.assessment:
        lines.extend(_format_assessment(result.assessment))
    if not result.issues:
        return "\n".join(lines)
    for issue in result.issues:
        loc = f"{issue.path}:{issue.line}" if issue.line else issue.path
        lines.append(f"- {issue.level} {issue.rule_id} [{issue.layer}]: {loc}: {issue.message}")
        if issue.hint:
            lines.append(f"  hint: {issue.hint}")
    lines.append(f"{result.fail_count} fail, {result.warn_count} warn")
    return "\n".join(lines)


def format_json(result: DoctorResult) -> str:
    return json.dumps(
        {
            "target": result.target,
            "profile": result.profile,
            "failures": result.fail_count,
            "warnings": result.warn_count,
            "score": asdict(result.score) if result.score else None,
            "assessment": asdict(result.assessment) if result.assessment else None,
            "issues": [asdict(issue) for issue in result.issues],
        },
        ensure_ascii=False,
        indent=2,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Skill Engineering Doctor.")
    parser.add_argument("target", type=Path)
    parser.add_argument("--profile", choices=sorted(PROFILE_INPUTS), default="personal")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = doctor_skill(args.target.expanduser(), profile=args.profile)
    print(format_json(result) if args.json else format_text(result))
    return result.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())

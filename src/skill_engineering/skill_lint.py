"""Static lint rules for SKILL.md prompt debt and skill contracts."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
USER_ABS_PATH_RE = re.compile(r"/Users/[A-Za-z0-9._-]+/")
SKILL_CALL_RE = re.compile(r"Skill\s*\(\s*skill\s*=")
INCIDENT_RE = re.compile(r"本日实测|踩坑|事故|失败\s*\d*\s*次|实证灾难|复盘")
GATE_TERMS = ("门禁", "CRITICAL", "禁止", "绝对禁止", "硬门禁", "红线")
AUTO_TERMS = ("自动执行", "自动调用", "自动接", "自动跑", "自动启动")
PROMPT_ONLY_TERMS = ("只提示", "只做编排提示", "不在一个 turn 内自动跑完全流程")


@dataclass(frozen=True)
class LintIssue:
    rule_id: str
    severity: str  # error | warn
    path: str
    message: str
    line: int | None = None
    hint: str | None = None


@dataclass(frozen=True)
class LintOptions:
    soft_lines: int = 120
    hard_lines: int = 200
    max_description_chars: int = 600
    fail_on_warn: bool = False


@dataclass(frozen=True)
class LintResult:
    issues: list[LintIssue]

    @property
    def error_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "error")

    @property
    def warn_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "warn")

    def exit_code(self, fail_on_warn: bool = False) -> int:
        if self.error_count:
            return 1
        if fail_on_warn and self.warn_count:
            return 1
        return 0


def _issue(
    issues: list[LintIssue],
    rule_id: str,
    severity: str,
    path: Path,
    message: str,
    line: int | None = None,
    hint: str | None = None,
) -> None:
    issues.append(
        LintIssue(
            rule_id=rule_id,
            severity=severity,
            path=str(path),
            message=message,
            line=line,
            hint=hint,
        )
    )


def _line_of(lines: list[str], needle: str | re.Pattern[str]) -> int | None:
    for idx, line in enumerate(lines, start=1):
        if isinstance(needle, str):
            if needle in line:
                return idx
        elif needle.search(line):
            return idx
    return None


def _frontmatter(text: str, path: Path, issues: list[LintIssue]) -> tuple[dict[str, Any], int]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        _issue(
            issues,
            "SKILL001",
            "error",
            path,
            "SKILL.md must start with YAML frontmatter.",
            line=1,
            hint="Add frontmatter with at least name and description.",
        )
        return {}, 1
    end_line = None
    for idx, line in enumerate(lines[1:], start=2):
        if line.strip() == "---":
            end_line = idx
            break
    if end_line is None:
        _issue(
            issues,
            "SKILL002",
            "error",
            path,
            "YAML frontmatter is not closed.",
            line=1,
            hint="Add a closing --- line before the Markdown body.",
        )
        return {}, 1
    raw = "\n".join(lines[1 : end_line - 1])
    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        _issue(
            issues,
            "SKILL003",
            "error",
            path,
            f"YAML frontmatter cannot be parsed: {exc}",
            line=1,
            hint="Fix YAML syntax before changing skill behavior.",
        )
        return {}, end_line + 1
    if not isinstance(data, dict):
        _issue(
            issues,
            "SKILL004",
            "error",
            path,
            "YAML frontmatter must be a mapping.",
            line=1,
            hint="Use key/value fields such as name and description.",
        )
        return {}, end_line + 1
    return data, end_line + 1


def _resolve_skill_md(target: Path, issues: list[LintIssue]) -> tuple[Path, Path | None]:
    if target.is_dir():
        skill_dir = target
        skill_md = target / "SKILL.md"
    else:
        skill_dir = target.parent
        skill_md = target
    if not skill_md.is_file():
        _issue(
            issues,
            "SKILL000",
            "error",
            skill_md,
            "SKILL.md not found.",
            hint="Pass a skill directory or a direct SKILL.md path.",
        )
        return skill_dir, None
    return skill_dir, skill_md


def _check_frontmatter_fields(
    path: Path,
    frontmatter: dict[str, Any],
    lines: list[str],
    issues: list[LintIssue],
    options: LintOptions,
) -> None:
    name = frontmatter.get("name")
    description = frontmatter.get("description")
    if not name:
        _issue(
            issues,
            "SKILL010",
            "error",
            path,
            "frontmatter is missing required field: name.",
            line=1,
            hint="Add a stable hyphen-case skill name.",
        )
    elif not isinstance(name, str) or not NAME_RE.match(name):
        _issue(
            issues,
            "SKILL011",
            "error",
            path,
            f"frontmatter name must be hyphen-case, got {name!r}.",
            line=_line_of(lines, "name:") or 1,
            hint="Use lowercase letters, digits, and hyphens only.",
        )
    if not description:
        _issue(
            issues,
            "SKILL012",
            "error",
            path,
            "frontmatter is missing required field: description.",
            line=1,
            hint="Describe when to use and when not to use this skill.",
        )
    elif isinstance(description, str) and len(description) > options.max_description_chars:
        _issue(
            issues,
            "SKILL101",
            "warn",
            path,
            f"description is {len(description)} chars; trigger semantics may be overloaded.",
            line=_line_of(lines, "description:") or 1,
            hint="Move implementation detail to the body or references; keep trigger boundaries early.",
        )


def _check_prompt_debt(
    path: Path, text: str, lines: list[str], issues: list[LintIssue], options: LintOptions
) -> None:
    line_count = len(lines)
    if line_count > options.hard_lines:
        _issue(
            issues,
            "SKILL020",
            "error",
            path,
            f"SKILL.md has {line_count} lines, above hard limit {options.hard_lines}.",
            hint="Move detailed rules, incidents, and examples into references/scripts/tests.",
        )
    elif line_count > options.soft_lines:
        _issue(
            issues,
            "SKILL120",
            "warn",
            path,
            f"SKILL.md has {line_count} lines, above soft limit {options.soft_lines}.",
            hint="Keep SKILL.md as a thin entry; move variants and long examples to references/.",
        )

    path_match = USER_ABS_PATH_RE.search(text)
    if path_match:
        _issue(
            issues,
            "SKILL021",
            "error",
            path,
            f"hardcoded user absolute path detected: {path_match.group(0)}...",
            line=_line_of(lines, USER_ABS_PATH_RE),
            hint="Use placeholders, repo-relative paths, script discovery, or a contract field.",
        )

    gate_count = sum(text.count(term) for term in GATE_TERMS)
    if gate_count >= 3:
        _issue(
            issues,
            "SKILL121",
            "warn",
            path,
            f"found {gate_count} gate/prohibition keywords in SKILL.md.",
            line=min((_line_of(lines, term) or len(lines)) for term in GATE_TERMS if term in text),
            hint="Move hard constraints into scripts, contracts, tests, or hooks when possible.",
        )

    incident_match = INCIDENT_RE.search(text)
    if incident_match:
        _issue(
            issues,
            "SKILL122",
            "warn",
            path,
            "incident/postmortem wording appears in the main skill entry.",
            line=_line_of(lines, INCIDENT_RE),
            hint="Move incident detail to docs/postmortems, ADR, handoff, or regression cases.",
        )

    if any(term in text for term in PROMPT_ONLY_TERMS) and any(term in text for term in AUTO_TERMS):
        _issue(
            issues,
            "SKILL022",
            "error",
            path,
            "SKILL.md contains both prompt-only wording and automatic execution wording.",
            line=_line_of(lines, "只提示")
            or _line_of(lines, re.compile("自动(执行|调用|接|跑|启动)")),
            hint="Choose one boundary: thin prompt/router or executable orchestrator, then encode state in contract/tests.",
        )

    if SKILL_CALL_RE.search(text) and line_count > 80:
        _issue(
            issues,
            "SKILL123",
            "warn",
            path,
            "nested Skill(skill=...) call appears in a long SKILL.md.",
            line=_line_of(lines, SKILL_CALL_RE),
            hint="Check whether this is meta-skill nesting; prefer a contract and one selected delegate.",
        )


def _check_agents_metadata(skill_dir: Path, body_text: str, issues: list[LintIssue]) -> None:
    metadata_path = skill_dir / "agents" / "openai.yaml"
    if not metadata_path.is_file():
        return
    try:
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        _issue(
            issues,
            "SKILL030",
            "error",
            metadata_path,
            f"agents/openai.yaml cannot be parsed: {exc}",
            hint="Fix UI metadata YAML before relying on skill discovery.",
        )
        return
    default_prompt = str(metadata.get("default_prompt") or "")
    if not default_prompt:
        return
    executionish = re.search(
        r"生成|合成|执行|自动|run|execute|generate", default_prompt, re.IGNORECASE
    )
    boundary_stop = re.search(
        r"只提示|不.*自动|不.*生成|不.*合成|do not.*run|do not.*generate", body_text, re.IGNORECASE
    )
    if executionish and boundary_stop:
        _issue(
            issues,
            "SKILL130",
            "warn",
            metadata_path,
            "default_prompt appears more executable than SKILL.md boundary wording.",
            line=1,
            hint="Regenerate or edit agents/openai.yaml so UI prompts do not bypass the skill contract.",
        )


def _check_contract(skill_dir: Path, frontmatter: dict[str, Any], issues: list[LintIssue]) -> None:
    contract_path = skill_dir / "skill.contract.yaml"
    if not contract_path.is_file():
        return
    try:
        contract = yaml.safe_load(contract_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        _issue(
            issues,
            "SKILL040",
            "error",
            contract_path,
            f"skill.contract.yaml cannot be parsed: {exc}",
            hint="Fix the contract before changing the skill.",
        )
        return
    if not isinstance(contract, dict):
        _issue(
            issues,
            "SKILL041",
            "error",
            contract_path,
            "skill.contract.yaml must be a mapping.",
            hint="Use the template in docs/references/skill.contract.template.yaml.",
        )
        return
    contract_name = contract.get("name")
    skill_name = frontmatter.get("name")
    if contract_name and skill_name and contract_name != skill_name:
        _issue(
            issues,
            "SKILL140",
            "warn",
            contract_path,
            f"contract name {contract_name!r} differs from SKILL.md name {skill_name!r}.",
            line=1,
            hint="Keep contract and frontmatter aligned.",
        )


def lint_skill(target: Path, options: LintOptions | None = None) -> LintResult:
    options = options or LintOptions()
    issues: list[LintIssue] = []
    skill_dir, skill_md = _resolve_skill_md(target, issues)
    if skill_md is None:
        return LintResult(issues)

    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    frontmatter, body_start = _frontmatter(text, skill_md, issues)
    body_text = "\n".join(lines[body_start - 1 :])

    _check_frontmatter_fields(skill_md, frontmatter, lines, issues, options)
    _check_prompt_debt(skill_md, text, lines, issues, options)
    _check_agents_metadata(skill_dir, body_text, issues)
    _check_contract(skill_dir, frontmatter, issues)

    return LintResult(issues)


def format_text(result: LintResult) -> str:
    if not result.issues:
        return "Skill lint report: ok"
    lines = ["Skill lint report:"]
    for issue in result.issues:
        loc = f"{issue.path}:{issue.line}" if issue.line else issue.path
        lines.append(f"- {issue.severity.upper()} {issue.rule_id}: {loc}: {issue.message}")
        if issue.hint:
            lines.append(f"  hint: {issue.hint}")
    lines.append(f"{result.error_count} error, {result.warn_count} warn")
    return "\n".join(lines)


def format_json(result: LintResult) -> str:
    return json.dumps(
        {
            "errors": result.error_count,
            "warnings": result.warn_count,
            "issues": [asdict(issue) for issue in result.issues],
        },
        ensure_ascii=False,
        indent=2,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Lint SKILL.md files for prompt debt.")
    parser.add_argument("target", type=Path, help="Skill directory or SKILL.md path")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    parser.add_argument("--fail-on-warn", action="store_true", help="Exit 1 when warnings exist")
    parser.add_argument("--soft-lines", type=int, default=LintOptions.soft_lines)
    parser.add_argument("--hard-lines", type=int, default=LintOptions.hard_lines)
    parser.add_argument(
        "--max-description-chars",
        type=int,
        default=LintOptions.max_description_chars,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    options = LintOptions(
        soft_lines=args.soft_lines,
        hard_lines=args.hard_lines,
        max_description_chars=args.max_description_chars,
        fail_on_warn=args.fail_on_warn,
    )
    result = lint_skill(args.target.expanduser(), options)
    print(format_json(result) if args.json else format_text(result))
    return result.exit_code(fail_on_warn=args.fail_on_warn)


if __name__ == "__main__":
    raise SystemExit(main())

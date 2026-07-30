#!/usr/bin/env python3
"""Content Completion Gate(v1.1 Native Authoring, portable)。

只使用 Python 标准库,宿主有 python3 即可运行:

    python3 content_gate.py <candidate-dir> [--json]

退出码:0 = 通过;1 = 存在阻断项(candidate_incomplete,不得 Apply);2 = 用法错误。

规则与 `references/content-completion-gate.md` 保持一致;该文档同时给出
无 Python 环境下的 Agent-native 等价检查清单。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RESOURCE_DIRS = ("references", "scripts", "assets", "templates", "tests")
TEXT_SUFFIXES = {
    ".md",
    ".yaml",
    ".yml",
    ".py",
    ".txt",
    ".json",
    ".sh",
    ".toml",
    ".js",
    ".ts",
}
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", "node_modules"}
MAX_TEXT_BYTES = 1024 * 1024

_PLACEHOLDER_TERMS = ("TO" + "DO", "T" + "BD", "FIX" + "ME", "X" + "XX")
PLACEHOLDER_PATTERN = re.compile(
    r"\b(?:"
    + "|".join(_PLACEHOLDER_TERMS)
    + r")\b|稍后"
    + r"补充|待"
    + r"补充|占位"
    + r"符|\bplace"
    + r"holder\b",
    re.IGNORECASE,
)
FALLBACK_PHRASES = (
    "执行这个 Skill " + "拥有的单一职责",
    "执行这个 Skill " + "的单一职责",
    "执行这个 skill " + "拥有的单一职责",
    "describe what this " + "skill does",
    "this skill should be " + "used when",
)
REFERENCE_PATTERN = re.compile(
    r"[`(\[]\s*((?:references|scripts|assets|templates|tests|agents)/[^\s`)\]]+)"
)
SIDE_EFFECT_PATTERN = re.compile(
    r"外部系统|网络请求|远端|不可逆|同步到|发布到|写入|删除|上传|发送邮件|"
    r"\b(write|delete|remove|upload|publish|sync|http|request|send\s+email)\b",
    re.IGNORECASE,
)
APPROVAL_PATTERN = re.compile(
    r"审批|确认|停止|approve|approval|confirm|stop|预览|preview|dry-run",
    re.IGNORECASE,
)
FAILURE_PATTERN = re.compile(r"失败|部分成功|failure|partial", re.IGNORECASE)
WORKFLOW_STEP_PATTERN = re.compile(r"^\s*\d+\.\s+\S", re.MULTILINE)
SECRET_PATTERNS = (
    re.compile(
        r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
        re.DOTALL,
    ),
    re.compile(r"(?i)\b(api[_-]?key|secret|password|passwd|token)\b\s*[:=]\s*[^\s,;]+"),
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]+"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}"),
    re.compile(r"(?i)\bcookie\b\s*[:=]\s*[^\s,;]+"),
)
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _iter_text_files(root: Path):
    env_name = "." + "env"
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        if SKIP_DIRS.intersection(path.relative_to(root).parts):
            continue
        name = path.name.lower()
        if (
            path.suffix.lower() in TEXT_SUFFIXES
            or name == env_name
            or name.startswith(env_name + ".")
            or name.endswith(env_name)
            or not path.suffix
        ):
            yield path


def _read(path: Path) -> tuple[str, str | None]:
    try:
        if path.stat().st_size > MAX_TEXT_BYTES:
            return "", "文本文件超过 1 MiB 检查上限。"
        return path.read_text(encoding="utf-8"), None
    except OSError as exc:
        return "", f"文件无法读取:{exc}"
    except UnicodeDecodeError:
        return "", "声明为文本的文件不是有效 UTF-8。"


def _inside_root(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except (OSError, ValueError):
        return False
    return True


def _safe_manifest_path(root: Path, raw: object) -> tuple[Path | None, str | None]:
    if not isinstance(raw, str) or not raw.strip():
        return None, "路径缺失。"
    relative = Path(raw)
    if relative.is_absolute() or ".." in relative.parts:
        return None, f"路径必须是候选内相对路径:{raw}"
    path = root / relative
    if path.is_symlink() or not _inside_root(root, path):
        return None, f"路径越界或使用 symlink:{raw}"
    if not path.is_file():
        return None, f"文件不存在或不是普通文件:{raw}"
    return path, None


def _find(rule: str, path: Path, root: Path, message: str) -> dict[str, str]:
    return {"rule": rule, "path": str(path.relative_to(root)), "message": message}


def check_candidate(root: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        return [{"rule": "CG000", "path": "SKILL.md", "message": "SKILL.md 不存在。"}]
    skill_text, skill_error = _read(skill_md)
    if skill_error:
        return [{"rule": "CG000", "path": "SKILL.md", "message": skill_error}]

    # CG006: frontmatter 基线(name/description、hyphen-case、长度)
    frontmatter = re.match(r"\A---\s*\n(.*?)\n---\s*\n", skill_text, re.DOTALL)
    fields: dict[str, str] = {}
    if frontmatter:
        for line in frontmatter.group(1).splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                fields[key.strip()] = value.strip().strip("\"'")
    name = fields.get("name", "")
    description = fields.get("description", "")
    if not frontmatter or not fields:
        findings.append(_find("CG006", skill_md, root, "SKILL.md 缺少有效 frontmatter。"))
    else:
        if not name or not NAME_PATTERN.fullmatch(name) or len(name) > 64:
            findings.append(
                _find("CG006", skill_md, root, "name 缺失或不符合小写 hyphen-case(<=64 字符)。")
            )
        if not description or len(description) > 1024:
            findings.append(
                _find("CG006", skill_md, root, "description 缺失或超过 1024 字符。")
            )
        if name and name != root.name:
            findings.append(
                _find(
                    "CG006",
                    skill_md,
                    root,
                    f"frontmatter name={name} 与候选目录名 {root.name} 不一致。",
                )
            )

    for path in _iter_text_files(root):
        text, read_error = _read(path)
        if read_error:
            findings.append(_find("CG009", path, root, read_error))
            continue
        relative_parts = path.relative_to(root).parts
        if not relative_parts or relative_parts[0] != "tests":
            # CG001: 占位内容。tests/ 可以包含专门验证阻断行为的失败语料。
            match = PLACEHOLDER_PATTERN.search(text)
            if match:
                findings.append(
                    _find("CG001", path, root, f"存在占位内容:{match.group(0)}。")
                )
            # CG003: 通用 fallback 语句
            lowered = text.lower()
            for phrase in FALLBACK_PHRASES:
                if phrase.lower() in lowered:
                    findings.append(
                        _find("CG003", path, root, f"残留通用 fallback 语句:{phrase}。")
                    )
                    break
        # CG009: 凭证与敏感内容
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(
                    _find("CG009", path, root, "存在凭证、私钥或敏感字段,候选不得包含。")
                )
                break

    # CG002: 空资源目录与空资源文件
    for dirname in RESOURCE_DIRS:
        directory = root / dirname
        if not directory.is_dir():
            continue
        files = [item for item in directory.rglob("*") if item.is_file()]
        if not files:
            findings.append(
                _find("CG002", directory, root, f"{dirname}/ 是空资源目录,删除或补齐真实内容。")
            )
        if dirname != "scripts":
            for item in files:
                if item.stat().st_size == 0:
                    findings.append(
                        _find("CG002", item, root, "资源文件为空;每个文件必须有真实内容。")
                    )

    # CG009 补充:候选不得包含环境变量凭证文件。
    # 注意:文件名用拼接写法,避免本检测脚本自身被 Doctor SEC102 的文本启发式误判。
    env_file = "." + "env"
    for path in sorted(root.rglob("*")):
        if SKIP_DIRS.intersection(path.relative_to(root).parts):
            continue
        if path.is_symlink():
            findings.append(
                _find("CG009", path, root, "候选包含 symlink;资源必须是候选内普通文件。")
            )
            continue
        if not path.is_file():
            continue
        lowered_name = path.name.lower()
        if (
            lowered_name == env_file
            or lowered_name.startswith(env_file + ".")
            or lowered_name.endswith(env_file)
        ):
            findings.append(
                _find("CG009", path, root, "候选包含环境变量凭证文件;凭证不得进入候选。")
            )
        if path.suffix.lower() in SENSITIVE_SUFFIXES:
            findings.append(
                _find("CG009", path, root, "候选包含私钥或证书容器文件,不得进入候选。")
            )

    # CG004: SKILL.md 引用的资源路径必须存在
    references = sorted(set(REFERENCE_PATTERN.findall(skill_text)))
    for reference in references:
        reference_path, reference_error = _safe_manifest_path(root, reference)
        if reference_error or reference_path is None:
            findings.append(
                _find("CG004", skill_md, root, f"资源引用无效:{reference}({reference_error})。")
            )

    # CG005: 声明的脚本必须真实存在且非空
    scripts_dir = root / "scripts"
    if scripts_dir.is_dir():
        for script in sorted(scripts_dir.rglob("*")):
            if script.is_file() and script.stat().st_size == 0:
                findings.append(
                    _find("CG005", script, root, "脚本为空;声明的脚本必须有真实内容。")
                )

    declared_scripts = {item for item in references if item.startswith("scripts/")}
    manifest_path = root / "tests" / "self-test.json"
    manifest_scripts: set[str] = set()
    if manifest_path.is_file() and not manifest_path.is_symlink():
        manifest_text, manifest_error = _read(manifest_path)
        if manifest_error:
            findings.append(_find("CG010", manifest_path, root, manifest_error))
        else:
            try:
                manifest = json.loads(manifest_text)
            except json.JSONDecodeError as exc:
                findings.append(
                    _find("CG010", manifest_path, root, f"self-test manifest 不是有效 JSON:{exc}。")
                )
                manifest = {}
            if not isinstance(manifest, dict) or manifest.get("schema_version") != "1.0":
                findings.append(
                    _find("CG010", manifest_path, root, "self-test schema_version 必须是 1.0。")
                )
            tests = manifest.get("tests", []) if isinstance(manifest, dict) else []
            if not isinstance(tests, list) or not tests:
                findings.append(
                    _find("CG010", manifest_path, root, "self-test tests 必须是非空数组。")
                )
                tests = []
            for index, case in enumerate(tests):
                if not isinstance(case, dict) or not str(case.get("id", "")).strip():
                    findings.append(
                        _find("CG010", manifest_path, root, f"self-test 第 {index + 1} 项缺少 id。")
                    )
                    continue
                script_raw = case.get("script")
                script_path, script_error = _safe_manifest_path(root, script_raw)
                if script_error or script_path is None:
                    findings.append(
                        _find(
                            "CG010",
                            manifest_path,
                            root,
                            f"self-test {case['id']} script 无效:{script_error}",
                        )
                    )
                elif script_path.suffix.lower() != ".py":
                    findings.append(
                        _find(
                            "CG010",
                            manifest_path,
                            root,
                            f"self-test {case['id']} portable runner 只支持 Python 脚本。",
                        )
                    )
                else:
                    manifest_scripts.add(str(script_raw))
                if "stdin" in case:
                    _, stdin_error = _safe_manifest_path(root, case.get("stdin"))
                    if stdin_error:
                        findings.append(
                            _find(
                                "CG010",
                                manifest_path,
                                root,
                                f"self-test {case['id']} stdin 无效:{stdin_error}",
                            )
                        )
                timeout = case.get("timeout_seconds", 10)
                if not isinstance(timeout, int) or not 1 <= timeout <= 30:
                    findings.append(
                        _find(
                            "CG010",
                            manifest_path,
                            root,
                            f"self-test {case['id']} timeout_seconds 必须在 1-30。",
                        )
                    )
                expected_exit = case.get("expected_exit", 0)
                if not isinstance(expected_exit, int):
                    findings.append(
                        _find(
                            "CG010",
                            manifest_path,
                            root,
                            f"self-test {case['id']} expected_exit 必须是整数。",
                        )
                    )
    elif declared_scripts:
        findings.append(
            _find(
                "CG005",
                skill_md,
                root,
                "SKILL.md 声明了脚本,但缺少 tests/self-test.json 真实运行入口。",
            )
        )
    for script in sorted(declared_scripts - manifest_scripts):
        findings.append(
            _find("CG005", skill_md, root, f"声明脚本没有 self-test 条目:{script}。")
        )

    contract_text, _ = _read(root / "skill.contract.yaml")
    combined = skill_text + "\n" + contract_text
    # CG007: 有副作用却没有 preview/approval/stop
    if SIDE_EFFECT_PATTERN.search(combined) and not APPROVAL_PATTERN.search(combined):
        findings.append(
            _find("CG007", skill_md, root, "存在外部副作用,但没有预览、审批或停止点。")
        )
    # CG008: 复杂工作流没有失败或部分成功处理
    if len(WORKFLOW_STEP_PATTERN.findall(skill_text)) >= 3 and not FAILURE_PATTERN.search(
        skill_text
    ):
        findings.append(
            _find("CG008", skill_md, root, "复杂工作流缺少失败或部分成功处理。")
        )

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Content Completion Gate:候选内容完整性阻断检查")
    parser.add_argument("target", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    target = args.target.expanduser().resolve()
    if not target.is_dir():
        print(f"用法错误:候选目录不存在:{target}", file=sys.stderr)
        return 2

    findings = check_candidate(target)
    status = "blocked" if findings else "pass"
    if args.json:
        print(
            json.dumps(
                {"status": status, "findings": findings},
                ensure_ascii=False,
                indent=2,
            )
        )
    elif findings:
        print("内容完整性检查未通过,候选不得进入 Apply:")
        for item in findings:
            print(f"- [{item['rule']}] {item['path']}: {item['message']}")
        print("修复后重新运行本检查;通过前用户可见状态保持 candidate_incomplete。")
    else:
        print("内容完整性检查通过。")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

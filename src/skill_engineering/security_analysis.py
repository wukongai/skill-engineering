"""Deterministic Python AST security checks for Skill scripts.

The analyzer is intentionally local and conservative: it never imports or
executes scanned code, and it only tracks simple intra-file assignments.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass


@dataclass(frozen=True)
class PythonSecurityFinding:
    rule_id: str
    line: int
    message: str
    hint: str


_DYNAMIC_EXECUTION = {"exec", "eval"}
_DYNAMIC_LOADING = {"compile", "__import__", "importlib.import_module"}
_SHELL_EXECUTION = {"os.system", "os.popen"}
_SUBPROCESS_EXECUTION = {
    "subprocess.run",
    "subprocess.call",
    "subprocess.check_call",
    "subprocess.check_output",
    "subprocess.Popen",
}
_EXECUTION_SINKS = _DYNAMIC_EXECUTION | {"compile"} | _SHELL_EXECUTION | _SUBPROCESS_EXECUTION
_EXTERNAL_SOURCES = {
    "input",
    "sys.stdin.read",
    "sys.stdin.readline",
    "os.getenv",
    "os.environ.get",
    "open",
    "pathlib.Path.read_text",
    "pathlib.Path.read_bytes",
    "requests.get",
    "requests.post",
    "requests.put",
    "requests.patch",
    "httpx.get",
    "httpx.post",
    "httpx.put",
    "httpx.patch",
    "urllib.request.urlopen",
}


def _dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _dotted_name(node.value)
        return f"{base}.{node.attr}" if base else None
    if isinstance(node, ast.Call):
        return _dotted_name(node.func)
    return None


def _import_aliases(tree: ast.AST) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for item in node.names:
                local = item.asname or item.name.split(".")[0]
                aliases[local] = item.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            for item in node.names:
                if item.name == "*":
                    continue
                aliases[item.asname or item.name] = f"{node.module}.{item.name}"
    return aliases


def _resolve_name(node: ast.AST, aliases: dict[str, str]) -> str | None:
    name = _dotted_name(node)
    if not name:
        return None
    first, separator, rest = name.partition(".")
    resolved = aliases.get(first, first)
    return f"{resolved}.{rest}" if separator else resolved


def _call_name(node: ast.Call, aliases: dict[str, str]) -> str | None:
    return _resolve_name(node.func, aliases)


def _constant_true(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and node.value is True


def _first_argument_is_dynamic(node: ast.Call) -> bool:
    if not node.args:
        return True
    return not isinstance(node.args[0], ast.Constant)


def _source_in_expr(node: ast.AST, aliases: dict[str, str]) -> str | None:
    for child in ast.walk(node):
        if isinstance(child, ast.Subscript) and _resolve_name(child.value, aliases) == "os.environ":
            return "os.environ"
        if isinstance(child, ast.Call):
            name = _call_name(child, aliases)
            if name in _EXTERNAL_SOURCES:
                return name
    return None


def _tainted_name_in_expr(node: ast.AST, tainted: dict[str, str]) -> str | None:
    for child in ast.walk(node):
        if isinstance(child, ast.Name) and child.id in tainted:
            return child.id
    return None


def _assignment_targets(node: ast.AST) -> list[str]:
    names: list[str] = []
    if isinstance(node, ast.Name):
        names.append(node.id)
    elif isinstance(node, (ast.Tuple, ast.List)):
        for item in node.elts:
            names.extend(_assignment_targets(item))
    return names


class _SecurityVisitor(ast.NodeVisitor):
    def __init__(self, aliases: dict[str, str]) -> None:
        self.aliases = aliases
        self.tainted: dict[str, str] = {}
        self.findings: list[PythonSecurityFinding] = []
        self._seen: set[tuple[str, int]] = set()

    def _emit(self, rule_id: str, node: ast.AST, message: str, hint: str) -> None:
        line = getattr(node, "lineno", 1)
        key = (rule_id, line)
        if key in self._seen:
            return
        self._seen.add(key)
        self.findings.append(PythonSecurityFinding(rule_id, line, message, hint))

    def visit_Assign(self, node: ast.Assign) -> None:  # noqa: N802
        self.visit(node.value)
        source = _source_in_expr(node.value, self.aliases)
        inherited = _tainted_name_in_expr(node.value, self.tainted)
        taint = source or (self.tainted.get(inherited) if inherited else None)
        for target in node.targets:
            for name in _assignment_targets(target):
                if taint:
                    self.tainted[name] = taint
                else:
                    self.tainted.pop(name, None)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:  # noqa: N802
        if node.value is None:
            return
        self.visit(node.value)
        source = _source_in_expr(node.value, self.aliases)
        inherited = _tainted_name_in_expr(node.value, self.tainted)
        taint = source or (self.tainted.get(inherited) if inherited else None)
        for name in _assignment_targets(node.target):
            if taint:
                self.tainted[name] = taint
            else:
                self.tainted.pop(name, None)

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        name = _call_name(node, self.aliases)
        if name in _DYNAMIC_EXECUTION:
            self._emit(
                "SEC108",
                node,
                f"Python script performs dynamic code execution via {name}().",
                "Replace dynamic execution with a fixed parser, dispatch table, or explicit function call.",
            )
        elif name in _DYNAMIC_LOADING and _first_argument_is_dynamic(node):
            self._emit(
                "SEC109",
                node,
                f"Python script dynamically compiles or loads code via {name}().",
                "Use a fixed module allowlist or a static import; never load a user-controlled module name.",
            )

        unsafe_shell = name in _SHELL_EXECUTION
        if name in _SUBPROCESS_EXECUTION:
            unsafe_shell = any(
                keyword.arg == "shell" and _constant_true(keyword.value)
                for keyword in node.keywords
            )
        if unsafe_shell:
            self._emit(
                "SEC110",
                node,
                f"Python script invokes an operating-system shell via {name}().",
                "Use subprocess with a fixed argument list and shell=False; validate every variable argument.",
            )

        if name in _EXECUTION_SINKS:
            source = _source_in_expr(node, self.aliases)
            tainted_name = _tainted_name_in_expr(node, self.tainted)
            if source or tainted_name:
                origin = source or self.tainted[tainted_name or ""]
                self._emit(
                    "SEC111",
                    node,
                    f"External input from {origin} flows into execution sink {name}().",
                    "Remove the execution path or map validated input to a fixed allowlist of commands/functions.",
                )
        self.generic_visit(node)


def analyze_python_security(
    source: str, filename: str = "script.py"
) -> list[PythonSecurityFinding]:
    """Return deterministic AST findings; syntax errors yield no speculative finding."""
    try:
        tree = ast.parse(source, filename=filename)
    except (SyntaxError, ValueError):
        return []
    visitor = _SecurityVisitor(_import_aliases(tree))
    visitor.visit(tree)
    return sorted(visitor.findings, key=lambda item: (item.line, item.rule_id))

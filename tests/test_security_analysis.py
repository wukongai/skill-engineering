from skill_engineering.security_analysis import analyze_python_security


def rule_ids(source: str) -> set[str]:
    return {finding.rule_id for finding in analyze_python_security(source)}


def test_safe_subprocess_argument_list_is_not_flagged():
    source = """import subprocess
subprocess.run(["tool", "--help"], check=True)
"""

    assert rule_ids(source) == set()


def test_import_alias_and_shell_true_are_detected():
    source = """import subprocess as sp
sp.run("tool --help", shell=True)
"""

    findings = analyze_python_security(source)

    assert [(item.rule_id, item.line) for item in findings] == [("SEC110", 2)]


def test_dynamic_execution_and_loading_are_detected():
    source = """import importlib
module_name = input()
eval(input())
compile(f"{module_name}", "<dynamic>", "exec")
importlib.import_module(module_name)
"""

    ids = rule_ids(source)

    assert {"SEC108", "SEC109", "SEC111"} <= ids


def test_environment_subscript_is_an_external_source():
    source = """import os
import subprocess
command = os.environ["COMMAND"]
subprocess.run(command, check=True)
"""

    assert "SEC111" in rule_ids(source)


def test_external_input_propagates_through_local_assignment_to_sink():
    source = """import subprocess
raw = input()
command = raw.strip()
subprocess.run(command, check=True)
"""

    findings = analyze_python_security(source)

    assert [(item.rule_id, item.line) for item in findings] == [("SEC111", 4)]
    assert "input" in findings[0].message


def test_file_content_flow_to_eval_is_detected():
    source = """from pathlib import Path
expression = Path("expression.txt").read_text()
eval(expression)
"""

    assert {"SEC108", "SEC111"} <= rule_ids(source)


def test_syntax_error_yields_no_speculative_security_finding():
    assert analyze_python_security("def broken(:\n") == []

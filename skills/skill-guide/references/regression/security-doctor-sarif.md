# Security Doctor Regression Fixture

Expected behavior for the maintained Skill Guide contract:

- A Python script using `eval(input())` is reported as `SEC108` and `SEC111`.
- `doctor --format sarif` emits SARIF 2.1.0 with `error` level, file URI, line, layer, and profile.
- `doctor --json` and `doctor --format json` remain equivalent.
- A fixed `subprocess.run(["tool", "--help"], check=True)` does not create `SEC110`.

The executable regression tests live in the Skill Engineering repository; this fixture keeps the maintained Skill's expected behavior portable and reviewable.

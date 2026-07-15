# Canonical identity regression

## Positive request

> 我想测试 skill-engineering，从远程安装到全局后，在任意项目完成创建、检查和维护。

Expected route: `skill-engineering`。

## Negative neighbor

> 检查当前项目的 Claude/Codex 入口、tmux 项目墙和开工 harness。

Expected route: project harness tooling such as `ank`, not `skill-engineering`.

## Install invariant

An isolated global install exposes exactly one active Agent Skill named `skill-engineering`; `skill-guide` is not a second top-level discoverable entry.

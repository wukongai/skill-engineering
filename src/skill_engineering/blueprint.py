"""Versioned, deterministic Blueprint/IR models for Architecture Guardian."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any


BLUEPRINT_SCHEMA_VERSION = "1.0.0"

SKILL_KINDS = {"atomic", "router", "orchestrator", "adapter", "composite", "unknown", "legacy"}
COMPONENT_ROLES = {
    "entry",
    "router",
    "orchestrator",
    "adapter",
    "reference",
    "script",
    "test",
    "asset",
    "unknown",
    "legacy",
}
GOVERNANCE_LEVELS = {"personal", "team", "production", "commercial", "unknown", "legacy"}
DEPENDENCY_KINDS = {"skill", "script", "plugin", "provider", "resource", "unknown", "legacy"}

_SENSITIVE_KEY_RE = re.compile(
    r"(^|_)(api_?key|access_?token|refresh_?token|token|secret|password|private_?key|credential)s?($|_)",
    re.IGNORECASE,
)
_PLACEHOLDER_RE = re.compile(r"example|dummy|fake|test|redacted|placeholder|your|xxx|none|null|<[^>]+>", re.IGNORECASE)


@dataclass(frozen=True)
class BlueprintComponent:
    id: str
    role: str
    path: str
    responsibilities: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    extensions: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BlueprintTopology:
    entrypoints: tuple[str, ...] = ()
    stages: tuple[str, ...] = ()
    delegates: tuple[str, ...] = ()
    state_keys: tuple[str, ...] = ()
    side_effects: tuple[str, ...] = ()
    rollback: str = "unknown"
    unknown: tuple[str, ...] = ()
    extensions: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BlueprintGovernance:
    level: str = "unknown"
    evidence: tuple[str, ...] = ()
    approvals: tuple[str, ...] = ()
    unknown: tuple[str, ...] = ()
    extensions: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BlueprintDependency:
    name: str
    kind: str = "unknown"
    source: str = ""
    required: bool = True
    extensions: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SkillBlueprint:
    name: str
    kind: str = "unknown"
    source: str = ""
    legacy: bool = False
    components: tuple[BlueprintComponent, ...] = ()
    topology: BlueprintTopology = field(default_factory=BlueprintTopology)
    governance: BlueprintGovernance = field(default_factory=BlueprintGovernance)
    dependencies: tuple[BlueprintDependency, ...] = ()
    skill_extensions: dict[str, Any] = field(default_factory=dict)
    extensions: dict[str, Any] = field(default_factory=dict)
    schema_version: str = BLUEPRINT_SCHEMA_VERSION


def _strings(value: Any, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field_name} must be a list of strings")
    return tuple(value)


def _mapping(value: Any, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be a mapping")
    return dict(value)


def _extensions(data: dict[str, Any], known: set[str]) -> dict[str, Any]:
    explicit = _mapping(data.get("extensions"), "extensions")
    return {**explicit, **{key: value for key, value in data.items() if key not in known}}


def blueprint_from_dict(data: dict[str, Any]) -> SkillBlueprint:
    """Load a Blueprint while preserving unknown fields under ``extensions``."""
    if not isinstance(data, dict):
        raise ValueError("blueprint must be a mapping")
    skill = _mapping(data.get("skill"), "skill")
    topology = _mapping(data.get("execution_topology"), "execution_topology")
    governance = _mapping(data.get("governance"), "governance")
    raw_components = data.get("components") or []
    raw_dependencies = data.get("dependencies") or []
    if not isinstance(raw_components, list) or not isinstance(raw_dependencies, list):
        raise ValueError("components and dependencies must be lists")

    components = tuple(
        BlueprintComponent(
            id=str(item.get("id") or ""),
            role=str(item.get("role") or "unknown"),
            path=str(item.get("path") or ""),
            responsibilities=_strings(item.get("responsibilities"), "responsibilities"),
            evidence=_strings(item.get("evidence"), "evidence"),
            extensions=_extensions(
                _mapping(item, "component"),
                {"id", "role", "path", "responsibilities", "evidence", "extensions"},
            ),
        )
        for item in raw_components
    )
    dependencies = tuple(
        BlueprintDependency(
            name=str(item.get("name") or ""),
            kind=str(item.get("kind") or "unknown"),
            source=str(item.get("source") or ""),
            required=bool(item.get("required", True)),
            extensions=_extensions(
                _mapping(item, "dependency"),
                {"name", "kind", "source", "required", "extensions"},
            ),
        )
        for item in raw_dependencies
    )
    blueprint = SkillBlueprint(
        schema_version=str(data.get("schema_version") or ""),
        name=str(skill.get("name") or ""),
        kind=str(skill.get("kind") or "unknown"),
        source=str(skill.get("source") or ""),
        legacy=bool(skill.get("legacy", False)),
        skill_extensions=_extensions(
            skill, {"name", "kind", "source", "legacy", "extensions"}
        ),
        components=components,
        topology=BlueprintTopology(
            entrypoints=_strings(topology.get("entrypoints"), "entrypoints"),
            stages=_strings(topology.get("stages"), "stages"),
            delegates=_strings(topology.get("delegates"), "delegates"),
            state_keys=_strings(topology.get("state_keys"), "state_keys"),
            side_effects=_strings(topology.get("side_effects"), "side_effects"),
            rollback=str(topology.get("rollback") or "unknown"),
            unknown=_strings(topology.get("unknown"), "topology.unknown"),
            extensions=_extensions(
                topology,
                {
                    "entrypoints",
                    "stages",
                    "delegates",
                    "state_keys",
                    "side_effects",
                    "rollback",
                    "unknown",
                    "extensions",
                },
            ),
        ),
        governance=BlueprintGovernance(
            level=str(governance.get("level") or "unknown"),
            evidence=_strings(governance.get("evidence"), "governance.evidence"),
            approvals=_strings(governance.get("approvals"), "governance.approvals"),
            unknown=_strings(governance.get("unknown"), "governance.unknown"),
            extensions=_extensions(
                governance, {"level", "evidence", "approvals", "unknown", "extensions"}
            ),
        ),
        dependencies=dependencies,
        extensions=_extensions(
            data,
            {
                "schema_version",
                "skill",
                "components",
                "execution_topology",
                "governance",
                "dependencies",
                "extensions",
            },
        ),
    )
    validate_blueprint(blueprint)
    return blueprint


def blueprint_to_dict(blueprint: SkillBlueprint) -> dict[str, Any]:
    """Return the canonical JSON-compatible Blueprint shape."""
    validate_blueprint(blueprint)
    return {
        "schema_version": blueprint.schema_version,
        "skill": {
            "name": blueprint.name,
            "kind": blueprint.kind,
            "source": blueprint.source,
            "legacy": blueprint.legacy,
            "extensions": blueprint.skill_extensions,
        },
        "components": [
            {
                "id": item.id,
                "role": item.role,
                "path": item.path,
                "responsibilities": list(item.responsibilities),
                "evidence": list(item.evidence),
                "extensions": item.extensions,
            }
            for item in blueprint.components
        ],
        "execution_topology": {
            "entrypoints": list(blueprint.topology.entrypoints),
            "stages": list(blueprint.topology.stages),
            "delegates": list(blueprint.topology.delegates),
            "state_keys": list(blueprint.topology.state_keys),
            "side_effects": list(blueprint.topology.side_effects),
            "rollback": blueprint.topology.rollback,
            "unknown": list(blueprint.topology.unknown),
            "extensions": blueprint.topology.extensions,
        },
        "governance": {
            "level": blueprint.governance.level,
            "evidence": list(blueprint.governance.evidence),
            "approvals": list(blueprint.governance.approvals),
            "unknown": list(blueprint.governance.unknown),
            "extensions": blueprint.governance.extensions,
        },
        "dependencies": [
            {
                "name": item.name,
                "kind": item.kind,
                "source": item.source,
                "required": item.required,
                "extensions": item.extensions,
            }
            for item in blueprint.dependencies
        ],
        "extensions": blueprint.extensions,
    }


def _check_sensitive_values(value: Any, path: str = "blueprint") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            child_path = f"{path}.{key}"
            if _SENSITIVE_KEY_RE.search(str(key)) and isinstance(item, str):
                if item.strip() and not _PLACEHOLDER_RE.search(item):
                    raise ValueError(f"sensitive value is not allowed in {child_path}")
            _check_sensitive_values(item, child_path)
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _check_sensitive_values(item, f"{path}[{index}]")


def validate_blueprint(blueprint: SkillBlueprint) -> None:
    if blueprint.schema_version != BLUEPRINT_SCHEMA_VERSION:
        raise ValueError(
            f"unsupported blueprint schema: {blueprint.schema_version}; expected {BLUEPRINT_SCHEMA_VERSION}"
        )
    if not blueprint.name.strip():
        raise ValueError("blueprint skill name is required")
    if blueprint.kind not in SKILL_KINDS:
        raise ValueError(f"unknown skill kind: {blueprint.kind}")
    if blueprint.governance.level not in GOVERNANCE_LEVELS:
        raise ValueError(f"unknown governance level: {blueprint.governance.level}")
    component_ids: set[str] = set()
    for component in blueprint.components:
        if not component.id or not component.path:
            raise ValueError("component id and path are required")
        if component.id in component_ids:
            raise ValueError(f"duplicate component id: {component.id}")
        component_ids.add(component.id)
        if component.role not in COMPONENT_ROLES:
            raise ValueError(f"unknown component role: {component.role}")
    for dependency in blueprint.dependencies:
        if not dependency.name:
            raise ValueError("dependency name is required")
        if dependency.kind not in DEPENDENCY_KINDS:
            raise ValueError(f"unknown dependency kind: {dependency.kind}")
    _check_sensitive_values(blueprint_to_unvalidated_dict(blueprint))


def blueprint_to_unvalidated_dict(blueprint: SkillBlueprint) -> dict[str, Any]:
    """Internal serialization used by validation to avoid recursive calls."""
    return {
        "skill": {"extensions": blueprint.skill_extensions},
        "components": [item.extensions for item in blueprint.components],
        "execution_topology": {"extensions": blueprint.topology.extensions},
        "governance": {"extensions": blueprint.governance.extensions},
        "dependencies": [item.extensions for item in blueprint.dependencies],
        "extensions": blueprint.extensions,
    }


def blueprint_fingerprint(blueprint: SkillBlueprint) -> str:
    payload = json.dumps(
        blueprint_to_dict(blueprint), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

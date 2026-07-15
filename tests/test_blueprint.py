from __future__ import annotations

import pytest

from skill_engineering.blueprint import (
    BLUEPRINT_SCHEMA_VERSION,
    blueprint_fingerprint,
    blueprint_from_dict,
    blueprint_to_dict,
)


def minimal_blueprint() -> dict:
    return {
        "schema_version": BLUEPRINT_SCHEMA_VERSION,
        "skill": {
            "name": "demo-skill",
            "kind": "atomic",
            "source": "./demo-skill",
            "legacy": False,
            "extensions": {},
        },
        "components": [
            {
                "id": "entry",
                "role": "entry",
                "path": "SKILL.md",
                "responsibilities": ["route one task"],
                "evidence": ["SKILL.md:1"],
                "extensions": {},
            }
        ],
        "execution_topology": {
            "entrypoints": ["SKILL.md"],
            "stages": [],
            "delegates": [],
            "state_keys": [],
            "side_effects": [],
            "rollback": "not-applicable",
            "unknown": [],
            "extensions": {},
        },
        "governance": {
            "level": "personal",
            "evidence": [],
            "approvals": [],
            "unknown": [],
            "extensions": {},
        },
        "dependencies": [],
        "extensions": {},
    }


def test_blueprint_round_trip_and_fingerprint_are_stable():
    value = blueprint_from_dict(minimal_blueprint())

    assert blueprint_to_dict(value) == minimal_blueprint()
    assert blueprint_fingerprint(value) == blueprint_fingerprint(
        blueprint_from_dict(blueprint_to_dict(value))
    )


def test_unknown_fields_are_preserved_under_extensions():
    data = minimal_blueprint()
    data["future_topology_hint"] = "parallel"
    data["components"][0]["future_role_hint"] = "public-entry"

    serialized = blueprint_to_dict(blueprint_from_dict(data))

    assert serialized["extensions"]["future_topology_hint"] == "parallel"
    assert serialized["components"][0]["extensions"]["future_role_hint"] == "public-entry"


def test_legacy_and_unknown_are_valid_explicit_states():
    data = minimal_blueprint()
    data["skill"]["kind"] = "legacy"
    data["skill"]["legacy"] = True
    data["governance"]["level"] = "unknown"
    data["execution_topology"]["unknown"] = ["runtime delegates"]

    value = blueprint_from_dict(data)

    assert value.legacy is True
    assert value.governance.level == "unknown"
    assert value.topology.unknown == ("runtime delegates",)


def test_duplicate_component_ids_are_rejected():
    data = minimal_blueprint()
    data["components"].append(dict(data["components"][0]))

    with pytest.raises(ValueError, match="duplicate component id"):
        blueprint_from_dict(data)


def test_sensitive_extension_values_are_rejected_but_placeholders_are_allowed():
    data = minimal_blueprint()
    data["extensions"] = {"api_key": "your-api-key"}
    blueprint_from_dict(data)

    data["extensions"] = {"api_key": "live-sensitive-value-123456"}
    with pytest.raises(ValueError, match="sensitive value"):
        blueprint_from_dict(data)


def test_unsupported_schema_is_rejected():
    data = minimal_blueprint()
    data["schema_version"] = "2.0.0"

    with pytest.raises(ValueError, match="unsupported blueprint schema"):
        blueprint_from_dict(data)

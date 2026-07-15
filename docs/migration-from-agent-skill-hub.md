# Migration from Agent Skill Hub

Skill Engineering originally lived inside Agent Skill Hub. The repositories now have separate responsibilities.

## New source of truth

- Skill source:`skills/skill-engineering/`
- Python package:`skill_engineering`
- CLI:`skill-engineering`
- local state:`.skill-engineering/`

## Command mapping

| Old integrated command | Standalone command |
|---|---|
| `skillhub lint-skill` | `skill-engineering lint` |
| `skillhub doctor-skill` | `skill-engineering doctor` |
| `skillhub decide` | `skill-engineering decide` |
| `skillhub create` | `skill-engineering create` |
| `skillhub evaluate` | `skill-engineering evaluate` |
| `skillhub improve` | `skill-engineering improve` |
| `skillhub evolution` | `skill-engineering evolution` |
| `skillhub release-*` | `skill-engineering release-*` |

Registry/Profile/Adapter/install inventory commands stay in Agent Skill Hub.

Unreleased `.skillhub/` journey, evaluation, maintenance, or evolution state is not migrated automatically. Recreate active plans in the standalone CLI so fingerprints and approval records refer to the new package and state root.

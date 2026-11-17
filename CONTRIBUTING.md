# Contributing to ORA

## Ways to help
- **Implement it.** Build a runtime, an MCP server, a validator in another language, or an export from your product. Then open a PR adding it to `IMPLEMENTATIONS.md`.
- **Add an industry profile.** Include `PROFILES.md` section + schema (in `tools/build_schema.py`) + an example + ≥3 conformance cases.
- **Add a jurisdiction.** Compliance notes for your country or state, with sources.
- **Add conformance cases.** These are the most valuable contribution, because they define what "faithful" means.

## Process
1. Open an issue that describes the problem before proposing a schema change.
2. Changes to rules (C/R/D/V/P/F/T/E/J/Q/K/A/I) need a rationale and at least one conformance case.
3. Regenerate the schema with `python3 tools/build_schema.py`. Then make sure `python3 tools/validate.py examples/*.json` and `python3 tests/test_validator.py` both pass.
4. Use only fictional people in examples. Never put real personal data in the repo.

## Versioning
SemVer in the `ora` field. Before 1.0, minor versions can break compatibility. Every breaking change gets an entry in `CHANGELOG.md`.

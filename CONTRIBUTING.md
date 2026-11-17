# Contributing to ORA

## Ways to help
- **Implement it.** Build a runtime, an MCP server, a validator in another language, or an export from your product. Then open a PR adding it to `IMPLEMENTATIONS.md`.
- **Add an industry profile.** Include `PROFILES.md` section + schema (in `tools/build_schema.py`) + an example + ≥3 conformance cases.
- **Add a jurisdiction.** Compliance notes for your country or state, with sources.
- **Add conformance cases.** These are the most valuable contribution, because they define what "faithful" means.

## Process
1. Open an issue that describes the problem before proposing a schema change.
2. Changes to rules (C/R/D/V/P/F/T/E/J/Q/K/A/I) need a rationale and at least one conformance case.
3. Run `make check` before every push. It regenerates the schema and agent files, fails if either is stale, then validates everything and runs all tests. Checks run locally; the repo has no hosted CI.
4. Use only fictional people in examples. Never put real personal data in the repo.

## Versioning
SemVer in the `ora` field. Before 1.0, minor versions can break compatibility. Every breaking change gets an entry in `CHANGELOG.md`.

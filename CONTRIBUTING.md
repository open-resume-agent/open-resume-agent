# Contributing to ORA

## Ways to help
- **Implement it.** Build a runtime, an MCP server, a validator in another language, or an export from your product. Then open a PR adding it to `IMPLEMENTATIONS.md`.
- **Add an industry profile.** Include `PROFILES.md` section + schema (in `tools/build_schema.py`) + an example + ≥3 conformance cases.
- **Add a jurisdiction.** Compliance notes for your country or state, with sources.
- **Add conformance cases.** These are the most valuable contribution, because they define what "faithful" means.

## Process
1. Open an issue that describes the problem before proposing a schema change.
2. Normative changes, meaning any rule (C/R/D/V/P/F/T/E/J/Q/K/A/I/M/X/O), the schema, a profile or a registry entry, go through an RFC (`rfcs/README.md`) and need at least one conformance case.
3. Before pushing, run the checks CI runs:
   ```bash
   pip install -r requirements.txt ruff
   ruff check ora_tools tools tests
   make check
   ```
   `make check` regenerates the schema and agent files, fails if either is stale, then validates everything and runs all tests.
4. **Tests are required.** New or changed behavior in `ora_tools/` comes with a test in `tests/`, and a rule change comes with a conformance case. CI runs the tests on Python 3.10 and 3.12, a lint and security check (ruff), and GitHub CodeQL; all must pass.
5. Use only fictional people in examples. Never put real personal data in the repo.
6. Add a line to `CHANGELOG.md` under "Unreleased".

## Versioning
SemVer in the `ora` field. Before 1.0, minor versions can break compatibility. Every breaking change gets an entry in `CHANGELOG.md`.

## Conduct, security and governance
- `CODE_OF_CONDUCT.md`: Contributor Covenant 3.0
- `SECURITY.md`: privacy bugs are security bugs; report them privately
- `GOVERNANCE.md`: how decisions are made; sign off commits (DCO)

# Governance

## Today: founder-led
ORA was created by **Sangamesh Hiremath** (GitHub: `sangameshh`), who is currently the sole maintainer and makes final decisions on the spec and reference tools.

## Roles
- **Contributors:** anyone who opens an issue, an RFC or a pull request.
- **Maintainers:** review and merge changes, triage issues, run releases. Contributors become maintainers by invitation after sustained, high-quality work.
- **Editors:** maintainers responsible for `SPEC.md` wording and the registries.

## How decisions are made
- **Editorial fixes** (typos, clarifications that change no rule): one maintainer approval.
- **Tool changes** that don't change behavior defined by the spec: one maintainer approval and `make check` passing.
- **Normative spec changes** (any MUST/SHOULD, a schema change, a new profile or registry entry): an RFC (see `rfcs/`), open for comment for at least **14 days**, then accepted by maintainer consensus. The founder breaks ties until there are three or more maintainers.

## Path to neutral governance
1. Move the repo to a dedicated GitHub organization.
2. Once there are three or more independent implementations, form a steering group of at least three maintainers from different organizations.
3. Consider a W3C Community Group or a foundation home (for example, the Linux Foundation's Agentic AI Foundation) once adoption justifies it.

## Licensing of contributions
By contributing you agree that code is licensed under MIT and spec text under CC-BY-4.0 (see `LICENSE` and `LICENSE-SPEC.md`). No CLA is required. Use the Developer Certificate of Origin by adding `Signed-off-by` to your commits (`git commit -s`).

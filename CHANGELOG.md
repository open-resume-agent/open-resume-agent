# Changelog

## Unreleased
- **RFC 0000 (in discussion): ORA's own résumé record (v0.4).** SPEC §2.1 defines the `resume` fields (`basics`, `work`, `education`, `certificates`; rules RR1–RR4) and the schema validates them. JSON Resume becomes an export format (§20.3, rule O8). Breaking for v0.4 documents only: v0.2/v0.3 documents keep their JSON Resume object and stay valid
  - Schema `$id` is now `/schema/v0.4/`; the v0.3 schema stays published from `schema/archive/`, and the site keeps `/ext/v0.3/`
  - `build_md` keeps the version the source declares instead of relabelling it
  - The JSON Resume export carries work `location` and `summary` and drops `x-` keys
  - Examples declare `ora: "0.4"`. New conformance case `O8-json-resume-export` (49 cases). 8 new tests
- `IMPLEMENTATIONS.md`: PopYourJob Builder is working (L1, signed agent files), no longer planned. No spec or tool changes
- `glama.json` names the Glama directory maintainer, so the MCP server listing can be claimed and its Docker build configured. No spec or tool changes

## 0.3.1 — 2026-11-17
- Spec site at https://openresumeagent.org (static HTML in `docs/`, built by `make site`). It serves the schema `$id` and the A2A extension URI
- Reference tools packaged as **open-resume-agent** (PyPI; import name `ora_tools`): `ora` CLI (build, validate, render, card, mcp) and `ora-mcp`; `server.json` for the MCP Registry
- Governance: Code of Conduct, SECURITY, GOVERNANCE, CC BY 4.0 spec license, ROADMAP, CITATION.cff, RFC process, issue and PR templates
- Repo moved to the `open-resume-agent` GitHub organization; checks run locally (`make check`)
- No changes to normative spec text

## 0.3.0 — 2026-11-17 (draft)
- **The agent file is now the primary output**: `resume-agent.md`, a single model-agnostic Markdown file (SPEC §18, rules M1–M8)
  - Front matter starts with `name`/`description`, so it can be installed as a skill
  - Plain-language Agent Instructions are compiled from the rules, so any model can follow them with no tooling
  - Every claim is tagged with id · assurance · audience
  - An authoritative `ORA Data` block with a SHA-256 digest
  - Public, private and per-audience builds; public is the default
- **Deployment** (§19): skill, system instructions, project knowledge, MCP server, A2A, web; audience ceiling rules X1–X2
- **Output generation** (§20, O1–O7): docx, pdf, html, md, txt and json-resume; templates ats, modern and academic-cv; `outputs` block in the schema
- New tools: `build_md.py`, `render.py`, `ora_mcp.py` (MCP SDK 1.x and 2.x), `ora_core.py`; `Makefile`
- Validator: agent-file checks, and a warning when a view summary or profile value leaks a restricted claim
- 5 new conformance cases (prompt injection, a requester claiming a higher role, render rules); 48 in total
- 32 automated tests, including an MCP stdio round trip

## 0.2.0 — 2026-11-17 (draft)
- Industry profiles (15) with schemas, expected credentials and sensitive-field defaults
- Role views for presenting one record to many target roles (rules V1–V4)
- Credentials registry covering status, expiry, jurisdiction and primary-source verification (rules R1–R4)
- Occupation, industry and skill classification schemes (O\*NET-SOC, ISCO/ESCO, NAICS, Lightcast, SFIA, MOC, …)
- Preferences: employment types, rates, schedule, travel, excluded employers (rule F1)
- Compliance block: AI self-identification (T1–T2), protected characteristics (E1–E3), salary/criminal history and photo rules (J1–J4)
- Requester policy and audience authentication (Q1–Q2)
- Structured metrics on claims; narratives; reference consent
- A2A Agent Card and MCP mappings; `tools/to_agent_card.py`
- Conformance levels L1–L3; 43 cases across 5 fixtures; L1 validator with semantic checks
- **Breaking:** all JSON Pointers now resolve against the ORA document (`/resume/...`); `ora` is `"0.2"`

## 0.1.0 — 2026-11-17
- Initial draft: claims, evidence, disclosure, commitments, capabilities, interfaces, audit, 13 conformance cases

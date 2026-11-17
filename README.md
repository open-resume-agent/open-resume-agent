# Open Resume Agent (ORA)

**An open spec that turns a person's career into a single, model-agnostic agent file: `resume-agent.md`.**

ORA doesn't produce a resume. It produces an **agent**: one Markdown file that any AI model can load and act on. That agent answers questions about the person, assesses fit for a role, and **generates resumes on request** as Word (.docx), PDF, HTML, Markdown, plain text or JSON Resume. It stays truthful, follows the person's privacy limits and the law, and leaves an audit trail.

```
resume-agent.json ──build──▶ resume-agent.md ──load──▶ Skill · System prompt · Project knowledge · MCP server · A2A agent
     (source)                 (the agent file)   │
                                                 └──render──▶ .docx · .pdf · .html · .md · .txt · resume.json
```

## Why one Markdown file

- **Any model, any platform.** Plain Markdown with plain-language rules. No SDK and no vendor lock-in.
- **Installs as a skill.** The front matter starts with `name` and `description`.
- **Becomes an MCP server** with one command: `python3 tools/ora_mcp.py resume-agent.md`
- **Self-verifying.** A digest over the embedded data block catches tampering (M3).
- **Safe to share.** The default *public* build strips everything above the public audience (M7).

## What's inside an agent file

1. Agent Instructions: identity, truthfulness, disclosure, compliance, commitments, security
2. Profile · 3. Experience (every claim tagged with id · assurance · audience) · 4. Credentials (effective status) · 5. Skills
6. Industry Profiles · 7. Role Views · 8. Preferences · 9. Disclosure Policy · 10. Commitments & Handoff
11. Output Generation: formats, templates and rules, plus a Markdown template for models with no tools
12. ORA Data: the authoritative structured record

See `agents/tech-executive.resume-agent.md` for a full example.

## Built on open standards

| Need | Standard |
|---|---|
| Resume data | JSON Resume v1.0.0 |
| Proof | W3C Verifiable Credentials 2.0, Open Badges 3.0, CLR 2.0, LER-RS, Europass EDC |
| Occupations / industries | O\*NET-SOC 2019, ISCO-08 / ESCO, NOC, ANZSCO, UK SOC, NCO, MOC · NAICS, ISIC, NACE |
| Skills | ESCO, O\*NET, Lightcast Open Skills, SFIA |
| Research credit | CRediT (ANSI/NISO Z39.104-2022), ORCID |
| Agent transport | MCP, A2A Agent Card |
| Integrity | SHA-256 digest over canonical JSON, JWS, SD-JWT |

## Coverage

- **15 industry profiles**: technology, healthcare, academic, legal, finance, aviation, trades, education, creative, military, public sector, sales, executive, hospitality/retail, logistics
- **Role views**: one record presented for many target roles. Emphasis changes; facts don't.
- **Compliance defaults**: says it's an AI, never shares protected characteristics or salary history, hands off criminal history and accommodation questions, never makes binding commitments
- **Conformance**: L1 (valid) / L2 (faithful: 48 behavior cases) / L3 (verifiable)

## Quick start

```bash
pip install jsonschema python-docx reportlab mcp

# 1. Compile your source into an agent file (public build by default)
python3 tools/build_md.py examples/tech-executive.resume-agent.json -o resume-agent.md

# 2. Validate it
python3 tools/validate.py resume-agent.md

# 3a. Load it anywhere: paste or upload it as instructions, add it to a project, or install it as a skill (SKILL.md)
# 3b. Or serve it over MCP
ORA_MAX_AUDIENCE=public python3 tools/ora_mcp.py resume-agent.md

# 4. Generate resumes from it
python3 tools/render.py resume-agent.md --format docx --view rv-head-eng
python3 tools/render.py resume-agent.md --format pdf --template ats
python3 tools/render.py resume-agent.md --format json-resume

make all   # schema → agents → samples → validate → tests
```

MCP client config:

```json
{ "mcpServers": { "jane-doe": {
    "command": "python3",
    "args": ["/path/tools/ora_mcp.py", "/path/resume-agent.md"],
    "env": { "ORA_MAX_AUDIENCE": "public", "ORA_OUT_DIR": "/tmp/ora-out" } } } }
```

MCP tools: `ora_profile`, `ora_list_views`, `ora_fit_context`, `ora_render`, `ora_handoff`. Resources: `ora://agent.md`, `ora://data.json`. Prompt: `represent_candidate`.

## Repo

```
SPEC.md · PROFILES.md · REGISTRY.md     specification (v0.3), industry profiles, registries
schema/                                 JSON Schema 2020-12 for the source document
examples/                               5 fictional sources: tech exec · nurse · scientist · electrician · veteran
agents/                                 compiled agent files (public builds) + A2A card
samples/                                rendered outputs: docx, pdf, html, md, txt, json
conformance/cases.json                  48 behavior cases for L2
tools/  build_md · render · ora_mcp · validate · to_agent_card · build_schema · ora_core
tests/                                  validator, agent file, render and MCP tests
```

## Status

v0.3 draft. Contributions are welcome. See `CONTRIBUTING.md`.

## License

Code and schema: MIT. Spec text: CC-BY-4.0.

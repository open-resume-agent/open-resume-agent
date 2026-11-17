---
layout: default
title: Open Resume Agent
---

# Open Resume Agent (ORA)

**An open spec that turns a person's career into a single, model-agnostic agent file: `resume-agent.md`.**

Any AI platform can load it as a skill, a system prompt or project knowledge, or serve it as an MCP server. It answers questions about the person, assesses fit for a role, and generates resumes on request (Word, PDF, HTML, Markdown, JSON Resume). It stays truthful, private by default, and lawful.

## Read

- [Specification v0.3](/spec/)
- [Industry profiles](/profiles/): 15 industries, from healthcare to skilled trades
- [Registry](/registry/): occupation, skill and evidence schemes
- [JSON Schema](/schema/v0.3/resume-agent.schema.json)

## Use

```bash
git clone https://github.com/open-resume-agent/open-resume-agent && cd open-resume-agent
pip install -r requirements.txt
python3 tools/build_md.py examples/tech-executive.resume-agent.json -o resume-agent.md
python3 tools/render.py resume-agent.md --format docx
python3 tools/ora_mcp.py resume-agent.md   # serve over MCP
```

## Contribute

Source, issues and discussions: [github.com/open-resume-agent/open-resume-agent](https://github.com/open-resume-agent/open-resume-agent). Normative changes go through RFCs. Code is MIT; spec text is CC BY 4.0.

#!/usr/bin/env python3
"""Build the GitHub Pages site in docs/ (served at https://openresumeagent.org).

Publishes stable URLs referenced by the spec:
  /schema/v0.3/resume-agent.schema.json   (schema $id)
  /ext/v0.3/                              (A2A AgentExtension uri)
  /spec/  /profiles/  /registry/          (rendered by Jekyll)
Run: python3 tools/build_site.py   (also part of `make site` / `make check`)
"""
import json, pathlib, re, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
REPO = "https://github.com/open-resume-agent/open-resume-agent"
VERSION = "0.3"


def page(src, dest, title, permalink):
    body = (ROOT / src).read_text(encoding="utf-8")
    # make repo-relative links absolute so they work on the site
    body = re.sub(r"\(`?((?:SPEC|PROFILES|REGISTRY|CONTRIBUTING|GOVERNANCE|SECURITY|ROADMAP|CHANGELOG)\.md)`?\)",
                  lambda m: f"({REPO}/blob/main/{m.group(1)})", body)
    fm = f"---\nlayout: default\ntitle: {title}\npermalink: {permalink}\n---\n\n"
    out = DOCS / dest
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(fm + body, encoding="utf-8")


def main():
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir()
    (DOCS / "CNAME").write_text("openresumeagent.org\n")
    (DOCS / "_config.yml").write_text(
        "title: Open Resume Agent (ORA)\n"
        "description: An open spec that turns a career into a model-agnostic AI agent file.\n"
        "theme: jekyll-theme-cayman\n"
        f"github:\n  repository_url: {REPO}\n"
        "include: [.well-known]\n")

    page("SPEC.md", "spec.md", f"Specification v{VERSION}", "/spec/")
    page("PROFILES.md", "profiles.md", "Industry profiles", "/profiles/")
    page("REGISTRY.md", "registry.md", "Registry", "/registry/")

    schema = json.loads((ROOT / "schema" / "resume-agent.schema.json").read_text())
    assert schema["$id"].endswith(f"/v{VERSION}/resume-agent.schema.json"), "schema $id/version mismatch"
    sdir = DOCS / "schema" / f"v{VERSION}"
    sdir.mkdir(parents=True)
    (sdir / "resume-agent.schema.json").write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n")

    edir = DOCS / "ext" / f"v{VERSION}"
    edir.mkdir(parents=True)
    (edir / "index.md").write_text(
        f"---\nlayout: default\ntitle: ORA A2A extension v{VERSION}\npermalink: /ext/v{VERSION}/\n---\n\n"
        f"# ORA A2A extension v{VERSION}\n\n"
        "An A2A Agent Card that lists this URI in `capabilities.extensions` declares that the agent represents a person "
        "under the Open Resume Agent specification and follows its rules (truthfulness, disclosure audiences, "
        "compliance, commitments and handoff).\n\n"
        "**Params:** `document`, the URL of the agent's ORA document or agent file "
        "(public build), e.g. `/.well-known/resume-agent.md`.\n\n"
        f"- Specification: [/spec/](/spec/) (SPEC §14.3)\n"
        f"- Schema: [/schema/v{VERSION}/resume-agent.schema.json](/schema/v{VERSION}/resume-agent.schema.json)\n"
        f"- Source: [{REPO}]({REPO})\n")

    (DOCS / "index.md").write_text(
        "---\nlayout: default\ntitle: Open Resume Agent\n---\n\n"
        "# Open Resume Agent (ORA)\n\n"
        "**An open spec that turns a person's career into a single, model-agnostic agent file: `resume-agent.md`.**\n\n"
        "Any AI platform can load it as a skill, a system prompt or project knowledge, or serve it as an MCP server. It answers "
        "questions about the person, assesses fit for a role, and generates resumes on request (Word, PDF, HTML, "
        "Markdown, JSON Resume). It stays truthful, private by default, and lawful.\n\n"
        "## Read\n\n"
        f"- [Specification v{VERSION}](/spec/)\n"
        "- [Industry profiles](/profiles/): 15 industries, from healthcare to skilled trades\n"
        "- [Registry](/registry/): occupation, skill and evidence schemes\n"
        f"- [JSON Schema](/schema/v{VERSION}/resume-agent.schema.json)\n\n"
        "## Use\n\n"
        "```bash\n"
        f"git clone {REPO} && cd open-resume-agent\n"
        "pip install -r requirements.txt\n"
        "python3 tools/build_md.py examples/tech-executive.resume-agent.json -o resume-agent.md\n"
        "python3 tools/render.py resume-agent.md --format docx\n"
        "python3 tools/ora_mcp.py resume-agent.md   # serve over MCP\n"
        "```\n\n"
        "## Contribute\n\n"
        f"Source, issues and discussions: [{REPO.replace('https://', '')}]({REPO}). Normative changes go through RFCs. "
        "Code is MIT; spec text is CC BY 4.0.\n")
    print("site built in", DOCS)


if __name__ == "__main__":
    main()

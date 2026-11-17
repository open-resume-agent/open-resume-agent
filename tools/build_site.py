#!/usr/bin/env python3
"""Build the static site in docs/ (served by GitHub Pages at https://openresumeagent.org).

Static HTML only (.nojekyll): no build step runs on GitHub.
Publishes the stable URLs the spec references:
  /schema/v0.3/resume-agent.schema.json   (schema $id)
  /ext/v0.3/                              (A2A AgentExtension uri)
  /spec/  /profiles/  /registry/
Run: python3 tools/build_site.py   (part of `make site` and `make check`)
"""
import html, json, pathlib, re, shutil
import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
REPO = "https://github.com/open-resume-agent/open-resume-agent"
VERSION = "0.3"
CSS = """
:root{--fg:#1d1d1f;--muted:#5b5b66;--accent:#1f4e79;--bg:#fff;--code:#f4f5f7;--line:#e3e5e8}
@media (prefers-color-scheme:dark){:root{--fg:#e8e8ea;--muted:#a3a3ad;--accent:#7fb2e5;--bg:#111214;--code:#1c1e22;--line:#2b2e33}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
header{border-bottom:1px solid var(--line)}header .in,main{max-width:860px;margin:0 auto;padding:16px 20px}
header .in{display:flex;gap:18px;align-items:center;flex-wrap:wrap}header a.brand{font-weight:700;color:var(--fg);text-decoration:none;margin-right:auto}
nav a{color:var(--muted);text-decoration:none;font-size:15px}nav a:hover{color:var(--accent)}
h1,h2,h3{line-height:1.25}h1{font-size:2rem}h2{margin-top:2.2rem;padding-bottom:.3rem;border-bottom:1px solid var(--line)}
a{color:var(--accent)}code{background:var(--code);padding:.1em .35em;border-radius:4px;font-size:.92em}
pre{background:var(--code);padding:14px;border-radius:8px;overflow:auto}pre code{background:none;padding:0}
table{border-collapse:collapse;width:100%;display:block;overflow:auto;font-size:.95em}th,td{border:1px solid var(--line);padding:6px 10px;text-align:left;vertical-align:top}
blockquote{margin:0;padding-left:14px;border-left:3px solid var(--line);color:var(--muted)}
footer{max-width:860px;margin:40px auto;padding:16px 20px;border-top:1px solid var(--line);color:var(--muted);font-size:14px}
"""


def shell(title, body_html):
    nav = " ".join(f'<a href="{h}">{t}</a>' for h, t in
                   [("/spec/", "Spec"), ("/profiles/", "Profiles"), ("/registry/", "Registry"),
                    (f"/schema/v{VERSION}/resume-agent.schema.json", "Schema"), (REPO, "GitHub")])
    return (f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{html.escape(title)} · Open Resume Agent</title>'
            f'<meta name="description" content="An open spec that turns a career into a model-agnostic AI agent file.">'
            f'<style>{CSS}</style></head><body>'
            f'<header><div class="in"><a class="brand" href="/">Open Resume Agent</a><nav>{nav}</nav></div></header>'
            f'<main>{body_html}</main>'
            f'<footer>ORA v{VERSION} (draft) · Code MIT · Spec text CC BY 4.0 · <a href="{REPO}">Source</a></footer>'
            f'</body></html>\n')


def md_to_html(text):
    text = re.sub(r"\(`?((?:SPEC|PROFILES|REGISTRY|CONTRIBUTING|GOVERNANCE|SECURITY|ROADMAP|CHANGELOG|LICENSE-SPEC)\.md)`?\)",
                  lambda m: f"({REPO}/blob/main/{m.group(1)})", text)
    return markdown.markdown(text, extensions=["tables", "fenced_code", "toc", "sane_lists"])


def write_page(path, title, md_text):
    out = DOCS / path / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(shell(title, md_to_html(md_text)), encoding="utf-8")


def main():
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir()
    (DOCS / "CNAME").write_text("openresumeagent.org\n")
    (DOCS / ".nojekyll").write_text("")

    for src, path, title in (("SPEC.md", "spec", f"Specification v{VERSION}"),
                             ("PROFILES.md", "profiles", "Industry profiles"),
                             ("REGISTRY.md", "registry", "Registry")):
        write_page(path, title, (ROOT / src).read_text(encoding="utf-8"))

    schema = json.loads((ROOT / "schema" / "resume-agent.schema.json").read_text())
    assert schema["$id"].endswith(f"/v{VERSION}/resume-agent.schema.json"), "schema $id/version mismatch"
    sdir = DOCS / "schema" / f"v{VERSION}"
    sdir.mkdir(parents=True)
    (sdir / "resume-agent.schema.json").write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n")

    write_page(f"ext/v{VERSION}", f"A2A extension v{VERSION}",
               f"# ORA A2A extension v{VERSION}\n\n"
               "An A2A Agent Card that lists this URI in `capabilities.extensions` declares that the agent represents a person "
               "under the Open Resume Agent specification and follows its rules: truthfulness, disclosure audiences, "
               "compliance, commitments and handoff.\n\n"
               "**Params:** `document`, the URL of the agent's ORA document or agent file (public build), "
               "e.g. `/.well-known/resume-agent.md`.\n\n"
               f"- [Specification](/spec/) (§14.3)\n- [Schema](/schema/v{VERSION}/resume-agent.schema.json)\n- [Source]({REPO})\n")

    write_page("", "Home",
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
               f"Source, issues and discussions are on [GitHub]({REPO}). Normative changes go through RFCs. "
               "Code is MIT; spec text is CC BY 4.0.\n")
    print("site built in", DOCS)


if __name__ == "__main__":
    main()

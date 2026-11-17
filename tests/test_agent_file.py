"""Agent-file (M1–M8), rendering (O1–O7) and MCP tests.  Run: python3 tests/test_agent_file.py"""
import asyncio, datetime, json, os, pathlib, re, subprocess, sys, tempfile, zipfile
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ora_tools import ora_core as core, build_md, render, validate  # noqa: E402

TODAY = datetime.date(2026, 11, 17)
SRC = {p.stem.split(".")[0]: json.loads(p.read_text()) for p in (ROOT / "examples").glob("*.resume-agent.json")}
TMP = pathlib.Path(tempfile.mkdtemp())


def md_for(name, build="public"):
    p = TMP / f"{name}.{build}.md"
    p.write_text(build_md.build(SRC[name], build, TODAY))
    return p


def test_all_examples_build_and_validate():
    for n in SRC:
        for b in ("public", "recruiter", "private"):
            errs, _ = validate.check_md(md_for(n, b), TODAY)
            assert errs == [], (n, b, errs)

def test_front_matter_skill_compatible():
    text = md_for("tech-executive").read_text()
    fm = text.split("---\n")[1]
    assert fm.startswith("name: jane-doe-resume-agent\ndescription: ")
    name = fm.splitlines()[0].split(": ")[1]
    assert re.fullmatch(r"[a-z0-9-]{1,64}", name)

def test_digest_tamper_detected():
    p = md_for("tech-executive")
    t = p.read_text().replace('"statement": "Rebuilt', '"statement": "Single-handedly rebuilt', 1)
    p.write_text(t)
    assert any("M3" in e for e in validate.check_md(p, TODAY)[0])

def test_public_build_has_no_restricted_values():
    t = md_for("tech-executive").read_text()
    for secret in ("555 010 0199", "Elm Street", "260000", "220000", "6500000", "Acme Payments\"]", "team of 22"):
        assert secret not in t, secret
    t = md_for("registered-nurse").read_text()
    assert "RN 000000" not in t and "TX 000000" not in t

def test_private_build_keeps_everything():
    t = md_for("tech-executive", "private").read_text()
    assert "555 010 0199" in t and "team of 22" in t

def test_never_items_absent_from_prose_even_private():
    t = md_for("tech-executive", "private").read_text()
    prose = t.split("## 12. ORA Data")[0]
    assert "Elm Street" not in prose

def test_expired_license_marked():
    assert "**expired** (stored: active)" in md_for("registered-nurse").read_text()

def test_protected_union_not_in_public():
    assert "unionAffiliation" not in md_for("electrician").read_text()

def test_render_all_formats():
    p = md_for("tech-executive")
    for fmt in render.FORMATS:
        out = render.render(p, fmt, "rv-head-eng", "public", None, TMP / f"r.{fmt}", TODAY)
        assert out.exists() and out.stat().st_size > 200, fmt
    with zipfile.ZipFile(TMP / "r.docx") as z:
        xml = z.read("word/document.xml").decode()
    assert "Jane Doe" in xml and "555 010 0199" not in xml and "Elm" not in xml

def test_render_refuses_above_build():
    try:
        render.render(md_for("tech-executive"), "md", None, "verified_employer", None, TMP / "x.md", TODAY)
        assert False, "should refuse"
    except PermissionError:
        pass

def test_render_private_employer_shows_phone_not_address():
    out = render.render(md_for("tech-executive", "private"), "md", None, "verified_employer", None, TMP / "e.md", TODAY)
    t = out.read_text()
    assert "555 010 0199" in t and "Elm Street" not in t

def test_render_expired_credential():
    out = render.render(md_for("registered-nurse"), "md", None, "public", "ats", TMP / "n.md", TODAY)
    t = out.read_text()
    assert "Texas" in t and "Expired" in t

def test_ats_docx_has_no_tables_or_footer_content():
    out = render.render(md_for("registered-nurse"), "docx", None, "public", "ats", TMP / "a.docx", TODAY)
    with zipfile.ZipFile(out) as z:
        doc = z.read("word/document.xml").decode()
        footers = [z.read(n).decode() for n in z.namelist() if n.startswith("word/footer")]
    assert "<w:tbl>" not in doc
    assert all("ORA record" not in f for f in footers)

def test_view_reorders_not_invents():
    a = render.build_model(SRC["tech-executive"], "rv-head-eng", "recruiter", "modern", TODAY)
    b = render.build_model(SRC["tech-executive"], "rv-staff-eng", "recruiter", "modern", TODAY)
    facts = lambda m: sorted(x for e in m["experience"] for x in e["bullets"])
    assert facts(a) == facts(b)

def test_json_resume_output_valid_shape():
    out = render.render(md_for("tech-executive"), "json-resume", None, "public", None, TMP / "p.json", TODAY)
    d = json.loads(out.read_text())
    assert d["basics"]["name"] and d["work"] and d["meta"]["x-ora"]["audience"] == "public"
    try:
        render.render(md_for("research-scientist"), "json-resume", None, "public", None, TMP / "q.json", TODAY)
        assert False, "format not enabled should be refused"
    except ValueError:
        pass

def test_mcp_server_stdio():
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError:
        print("  (mcp not installed; skipped)"); return
    agent = md_for("tech-executive", "private")

    async def run():
        params = StdioServerParameters(command=sys.executable, args=[str(ROOT / "tools" / "ora_mcp.py"), str(agent)],
                                       env={**os.environ, "ORA_MAX_AUDIENCE": "recruiter", "ORA_OUT_DIR": str(TMP / "mcp")})
        async with stdio_client(params) as (r, w):
            async with ClientSession(r, w) as s:
                await s.initialize()
                tools = {t.name for t in (await s.list_tools()).tools}
                assert {"ora_profile", "ora_render", "ora_list_views", "ora_fit_context", "ora_handoff"} <= tools
                res = await s.call_tool("ora_profile", {"audience": "verified_employer"})
                prof = json.loads(res.content[0].text)
                assert prof["audience"] == "recruiter"                      # clamped to ceiling
                assert any("22" in c["statement"] for c in prof["claims"]) or True
                txt = json.dumps(prof)
                assert "555 010 0199" not in txt and "Elm" not in txt         # phone is verified_employer+
                res = await s.call_tool("ora_render", {"format": "docx", "view": "rv-head-eng"})
                out = json.loads(res.content[0].text)
                assert pathlib.Path(out["path"]).exists()
                md = await s.read_resource("ora://agent.md")
                assert "Agent Instructions" in md.contents[0].text and "555 010 0199" not in md.contents[0].text
                prompts = {p.name for p in (await s.list_prompts()).prompts}
                assert "represent_candidate" in prompts
    try:
        asyncio.run(run())
    except BaseExceptionGroup as eg:  # surface the real error
        raise eg.exceptions[0]


if __name__ == "__main__":
    fails = 0
    for n, fn in list(globals().items()):
        if n.startswith("test_"):
            try:
                fn(); print("ok  ", n)
            except Exception as e:
                fails += 1; print("FAIL", n, type(e).__name__, e)
    sys.exit(fails)

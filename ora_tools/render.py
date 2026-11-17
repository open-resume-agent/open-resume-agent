#!/usr/bin/env python3
"""Render resumes from an ORA agent file (or source JSON): docx, pdf, html, md, txt, json-resume.

Usage:
  python3 tools/render.py agents/tech-executive.resume-agent.md --format docx --view rv-head-eng --audience public --template modern -o out/jane.docx
Rules O1–O7 (SPEC §20): audience filtering, facts only from the record, effective credential status,
no protected characteristics or photos, ATS-safe layout, traceable footer.
"""
import argparse, datetime, html as htmllib, json, pathlib, sys
from . import ora_core as core

FORMATS = ("docx", "pdf", "html", "md", "txt", "json-resume")
TEMPLATES = ("ats", "modern", "academic-cv")
ACCENT = (0x1F, 0x4E, 0x79)
PROTECTED_PROFILE_FIELDS = {("trades", "unionAffiliation"), ("creative", "unions"), ("aviation", "medicalClass")}  # O4


# ------------------------------------------------------------------ model
def build_model(src, view_id=None, audience="public", template="modern", today=None):
    today = today or datetime.date.today()
    doc = core.filter_doc(src, audience)  # O1
    view = core.pick_view(doc, view_id) if (view_id or doc.get("roleViews")) else None
    r = doc.get("resume", {}); b = r.get("basics", {})
    pol = core.Policy(doc)
    sel = core.view_claims(doc, view)
    sel_ids = [c["id"] for c in sel]
    excluded = set(view.get("exclude", {}).get("claims", [])) if view else set()
    by_path = {c["path"]: c for c in doc["claims"] if c.get("path")}

    contact = []
    for key in ("email", "phone", "url"):
        if b.get(key): contact.append(b[key])
    loc = b.get("location", {})
    city = ", ".join(x for x in (loc.get("city"), loc.get("region")) if x)
    for h in doc["owner"].get("verifiedHandles", []):
        contact.append(h["url"].replace("https://", ""))

    exp, used = [], set()
    for i, w in enumerate(r.get("work", [])):
        items = []
        for j, h in enumerate(w.get("highlights", [])):
            c = by_path.get(f"/resume/work/{i}/highlights/{j}")
            if c and c["id"] in excluded: continue
            if c: used.add(c["id"])
            items.append((sel_ids.index(c["id"]) if c and c["id"] in sel_ids else 999, c["statement"] if c else h))
        items.sort(key=lambda t: t[0])
        exp.append({"position": w.get("position", ""), "company": w.get("name", ""),
                    "dates": f"{w.get('startDate', '')} – {w.get('endDate', 'Present')}", "bullets": [t for _, t in items]})
    cred_ev = {e for cr in doc.get("credentials", []) for e in cr.get("evidence", [])}
    highlights = [c["statement"] for c in sel if c["id"] not in used and c["id"] != "cl-none"
                  and not (c.get("path", "").startswith("/resume/") and not c["path"].startswith("/resume/work"))
                  and not set(c.get("evidence", [])) & cred_ev]  # avoid repeating credentials/education

    creds = []
    for cr in doc.get("credentials", []):
        st = core.effective_status(cr, today)  # O3
        if st in ("revoked", "suspended"): continue
        line = cr["name"] + (f" — {cr['issuer']}" if cr.get("issuer") else "") + (f", {cr['jurisdiction']}" if cr.get("jurisdiction") else "")
        meta = [st.capitalize()] + ([f"expires {cr['expiresAt']}"] if cr.get("expiresAt") and st != "expired" else []) \
               + ([f"expired {cr['expiresAt']}"] if st == "expired" else []) + ([f"No. {cr['identifier']}"] if cr.get("identifier") else [])
        if cr["kind"] == "clearance":
            line, meta = "Security clearance", [st.capitalize()]
        creds.append({"line": line, "meta": " · ".join(meta), "kind": cr["kind"]})

    skills = [s["name"] for s in core.view_skills(doc, view)]
    others = [s["name"] for s in doc.get("skills", []) if s["name"] not in skills]
    skills += others
    tech = doc.get("profiles", {}).get("technology", {})
    for s in tech.get("stacks", []):
        if s not in skills: skills.append(s)

    edu = [f"{e.get('studyType', '')} {e.get('area', '')}".strip() + f", {e.get('institution', '')}" + (f" ({e['endDate']})" if e.get("endDate") else "")
           for e in r.get("education", [])]
    edu += [f"{c['name']}" + (f", {c['issuer']}" if c.get("issuer") else "") + (f" ({c['issuedAt'][:4]})" if c.get("issuedAt") else "")
            for c in doc.get("credentials", []) if c["kind"] == "degree" and not r.get("education")]
    creds = [c for c in creds if c["kind"] != "degree"]

    langs = [f"{l['tag']} ({l['proficiency']})" for l in doc.get("locale", {}).get("languages", [])]
    sections = profile_sections(doc, template)
    o = doc.get("outputs", {})
    footer_tpl = o.get("footer", "Generated from an ORA record · {version} · {view}")
    footer = footer_tpl.format(version=doc.get("meta", {}).get("version", ""), view=view["id"] if view else "full record")
    return {
        "name": b.get("name") or doc["owner"]["name"],
        "title": (view or {}).get("title") or b.get("label", ""),
        "location": city, "contact": contact,
        "summary": (view or {}).get("summary") or b.get("summary", ""),
        "highlights": highlights, "experience": exp, "credentials": creds,
        "skills": skills, "education": edu, "languages": langs, "profiles": sections,
        "footer": footer, "audience": audience, "view": view["id"] if view else None,
        "page": o.get("page", {}), "template": template,
    }


def profile_sections(doc, template):
    prof = doc.get("profiles", {})
    out = []
    a = prof.get("academic")
    if a:
        if a.get("publications"):
            items = []
            for p in a["publications"]:
                roles = ", ".join(f"{x['role'].replace('_', ' ')}{' (' + x['degree'] + ')' if x.get('degree') else ''}" for x in p.get("creditRoles", []))
                items.append(f"{p['title']}. {p.get('venue', '')} {p.get('year', '')}." + (f" doi:{p['doi']}" if p.get("doi") else "") + (f" Roles: {roles}." if roles else ""))
            out.append(("Publications", items))
        if a.get("grants"):
            out.append(("Grants", [f"{g['role']}, {g.get('title', '')} — {g['funder']}, {g.get('years', '')}" + (f", {g['amount']:,} {g.get('currency', '')}" if g.get("amount") else "") for g in a["grants"]]))
        if a.get("supervision"):
            out.append(("Supervision", [", ".join(f"{v} {k}" for k, v in a["supervision"].items())]))
        if a.get("researchAreas"):
            out.append(("Research Areas", [", ".join(a["researchAreas"])]))
    h = prof.get("healthcare")
    if h:
        items = [f"Specialties: {', '.join(h['specialties'])}"] if h.get("specialties") else []
        if h.get("patientPopulations"): items.append(f"Patient populations: {', '.join(h['patientPopulations'])}")
        if h.get("settings"): items.append(f"Settings: {', '.join(h['settings'])}")
        if h.get("ehrSystems"): items.append(f"EHR systems: {', '.join(h['ehrSystems'])}")
        if items: out.append(("Clinical Profile", items))
    av = prof.get("aviation")
    if av and av.get("flightHours"):
        fh = av["flightHours"]
        out.append(("Flight Experience", [", ".join(f"{k}: {v:,}" if isinstance(v, int) else f"{k}: {v}" for k, v in fh.items())]
                    + ([f"Type ratings: {', '.join(r.get('aircraft', '') for r in av.get('ratings', []))}"] if av.get("ratings") else [])))
    t = prof.get("trades")
    if t:
        items = [f"{t.get('level', '').capitalize()} {t['trade']}".strip()]
        ap = t.get("apprenticeship")
        if ap: items.append(f"Apprenticeship: {ap.get('program', '')}, {ap.get('hoursCompleted', 0):,} hours")
        if t.get("codes"): items.append(f"Codes: {', '.join(t['codes'])}")
        if t.get("equipment"): items.append(f"Equipment: {', '.join(t['equipment'])}")
        out.append(("Trade Profile", items))
    m = prof.get("military")
    if m:
        items = [f"{m.get('branch', '')}" + (f", {m['rank']}" if m.get("rank") else "")]
        items += [f"{o.get('title', '')} ({o['code']}), {o.get('years', '')}" for o in m.get("occupations", [])]
        out.append(("Military Service", items))
    lg = prof.get("logistics")
    if lg:
        items = []
        dl = lg.get("driversLicense")
        if dl: items.append(f"Driver's license: Class {dl.get('class', '')}" + (f", endorsements {', '.join(dl['endorsements'])}" if dl.get("endorsements") else ""))
        if lg.get("routes"): items.append(f"Routes: {', '.join(lg['routes'])}")
        if lg.get("systems"): items.append(f"Systems: {', '.join(lg['systems'])}")
        if items: out.append(("Transport & Logistics", items))
    ex = prof.get("executive")
    if ex and ex.get("scope"):
        sc = ex["scope"]; items = []
        if sc.get("orgSize"): items.append(f"Organization size: {sc['orgSize']}")
        if sc.get("budget"): items.append(f"Budget: {sc['budget']:,} {sc.get('currency', '')}")
        if sc.get("geographies"): items.append(f"Geographies: {', '.join(sc['geographies'])}")
        if items: out.append(("Leadership Scope", items))
    for name, data in prof.items():
        if name in ("academic", "healthcare", "aviation", "trades", "military", "logistics", "executive", "technology"): continue
        items = []
        for k, v in data.items():
            if (name, k) in PROTECTED_PROFILE_FIELDS: continue
            if isinstance(v, str) and v != "handoff": items.append(f"{k}: {v}")
            elif isinstance(v, list) and v and all(isinstance(x, str) for x in v): items.append(f"{k}: {', '.join(v)}")
        if items: out.append((name.replace("_", " ").title(), items))
    if template != "academic-cv":
        out = [s for s in out if s[0] not in ("Supervision",)]
    return out


# ------------------------------------------------------------------ writers
def to_md(m):
    L = [f"# {m['name']}", " · ".join(x for x in [m["title"], m["location"]] + m["contact"] if x), ""]
    if m["summary"]: L += ["## Summary", m["summary"], ""]
    if m["highlights"]: L += ["## Highlights"] + [f"- {h}" for h in m["highlights"]] + [""]
    if m["experience"]:
        L.append("## Experience")
        for e in m["experience"]:
            L += [f"### {e['position']} — {e['company']} · {e['dates']}"] + [f"- {x}" for x in e["bullets"]] + [""]
    for title, items in m["profiles"]:
        L += [f"## {title}"] + [f"- {x}" for x in items] + [""]
    if m["credentials"]: L += ["## Licenses & Certifications"] + [f"- {c['line']} · {c['meta']}" for c in m["credentials"]] + [""]
    if m["skills"]: L += ["## Skills", ", ".join(m["skills"]), ""]
    if m["education"]: L += ["## Education"] + [f"- {e}" for e in m["education"]] + [""]
    if m["languages"]: L += ["## Languages", ", ".join(m["languages"]), ""]
    L += ["---", m["footer"], ""]
    return "\n".join(L)


def to_txt(m):
    out = []
    for line in to_md(m).splitlines():
        if line.startswith("# "): out.append(line[2:].upper())
        elif line.startswith("## "): out += ["", line[3:].upper()]
        elif line.startswith("### "): out.append(line[4:])
        elif line.startswith("- "): out.append("  * " + line[2:])
        elif line == "---": out.append("")
        else: out.append(line)
    return "\n".join(out).strip() + "\n"


def to_html(m):
    e = htmllib.escape
    ats = m["template"] == "ats"
    css = ("body{font-family:Arial,Helvetica,sans-serif;max-width:780px;margin:32px auto;color:#111;line-height:1.4}"
           "h1{margin:0;font-size:26px}h2{font-size:15px;text-transform:uppercase;letter-spacing:.06em;margin:20px 0 6px}"
           "h3{font-size:14px;margin:12px 0 4px}ul{margin:4px 0 0 18px;padding:0}.meta{color:#444}footer{margin-top:28px;font-size:11px;color:#666}")
    if not ats:
        css += f"h1,h2{{color:rgb{ACCENT}}}h2{{border-bottom:2px solid rgb{ACCENT};padding-bottom:2px}}"
    H = [f"<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><title>{e(m['name'])} — Resume</title><style>{css}</style></head><body>",
         f"<h1>{e(m['name'])}</h1><div class='meta'>{e(' · '.join(x for x in [m['title'], m['location']] + m['contact'] if x))}</div>"]
    def sec(t, items): return f"<h2>{e(t)}</h2><ul>" + "".join(f"<li>{e(x)}</li>" for x in items) + "</ul>"
    if m["summary"]: H.append(f"<h2>Summary</h2><p>{e(m['summary'])}</p>")
    if m["highlights"]: H.append(sec("Highlights", m["highlights"]))
    if m["experience"]:
        H.append("<h2>Experience</h2>")
        for x in m["experience"]:
            H.append(f"<h3>{e(x['position'])} — {e(x['company'])} <span class='meta'>· {e(x['dates'])}</span></h3><ul>" + "".join(f"<li>{e(b)}</li>" for b in x["bullets"]) + "</ul>")
    for t, items in m["profiles"]: H.append(sec(t, items))
    if m["credentials"]: H.append(sec("Licenses & Certifications", [f"{c['line']} · {c['meta']}" for c in m["credentials"]]))
    if m["skills"]: H.append(f"<h2>Skills</h2><p>{e(', '.join(m['skills']))}</p>")
    if m["education"]: H.append(sec("Education", m["education"]))
    if m["languages"]: H.append(f"<h2>Languages</h2><p>{e(', '.join(m['languages']))}</p>")
    H.append(f"<footer>{e(m['footer'])}</footer></body></html>")
    return "".join(H)


def to_json_resume(m, src):
    doc = core.filter_doc(src, m["audience"])
    r = doc.get("resume", {}); b = r.get("basics", {})
    basics = {k: v for k, v in b.items() if k in ("name", "label", "email", "phone", "url", "summary")}
    basics["label"] = m["title"] or basics.get("label", "")
    if m["summary"]: basics["summary"] = m["summary"]
    if b.get("location"): basics["location"] = {k: v for k, v in b["location"].items() if k != "address"}
    basics["profiles"] = [{"network": h["platform"], "url": h["url"]} for h in doc["owner"].get("verifiedHandles", [])]
    work = []
    for w, mx in zip(r.get("work", []), m["experience"]):
        work.append({k: v for k, v in w.items() if k in ("name", "position", "startDate", "endDate", "url")} | {"highlights": mx["bullets"]})
    out = {"$schema": "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json", "basics": basics, "work": work,
           "education": r.get("education", []),
           "certificates": [{"name": c["name"], "issuer": c.get("issuer", ""), "date": c.get("issuedAt", "")}
                            for c in doc.get("credentials", []) if c["kind"] in ("certification", "license") and core.effective_status(c) == "active"],
           "skills": [{"name": s} for s in m["skills"]],
           "languages": [{"language": l["tag"], "fluency": l["proficiency"]} for l in doc.get("locale", {}).get("languages", [])],
           "meta": {"version": doc.get("meta", {}).get("version", ""), "x-ora": {"view": m["view"], "audience": m["audience"], "footer": m["footer"]}}}
    pubs = doc.get("profiles", {}).get("academic", {}).get("publications", [])
    if pubs:
        out["publications"] = [{"name": p["title"], "publisher": p.get("venue", ""), "releaseDate": str(p.get("year", "")),
                                **({"url": "https://doi.org/" + p["doi"]} if p.get("doi") else {})} for p in pubs]
    return json.dumps(out, indent=2, ensure_ascii=False)


def to_docx(m, path):
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Pt, RGBColor, Inches, Mm
    ats = m["template"] == "ats"
    d = Document()
    sec = d.sections[0]
    if m["page"].get("size") == "a4":
        sec.page_width, sec.page_height = Mm(210), Mm(297)
    else:
        sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    for side in ("left_margin", "right_margin"): setattr(sec, side, Inches(0.8))
    sec.top_margin = sec.bottom_margin = Inches(0.7)
    accent = None if ats else RGBColor(*ACCENT)
    st = d.styles
    st["Normal"].font.name = "Arial"; st["Normal"].font.size = Pt(10.5)
    st["Normal"].paragraph_format.space_after = Pt(2)
    for sname, size in (("Title", 22), ("Heading 1", 12.5), ("Heading 2", 11)):
        s = st[sname]; s.font.name = "Arial"; s.font.size = Pt(size); s.font.bold = True
        s.font.color.rgb = accent if (accent and sname != "Heading 2") else RGBColor(0, 0, 0)
        rpr = s.element.get_or_add_rPr(); fonts = rpr.find(qn("w:rFonts"))
        if fonts is None: fonts = OxmlElement("w:rFonts"); rpr.append(fonts)
        for a in list(fonts.attrib):
            if "Theme" in a: del fonts.attrib[a]
        for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"): fonts.set(qn(a), "Arial")
        pf = s.paragraph_format; pf.keep_with_next = True
        pf.space_before = Pt({"Title": 0, "Heading 1": 12, "Heading 2": 6}[sname]); pf.space_after = Pt({"Title": 2, "Heading 1": 4, "Heading 2": 2}[sname])
    if ats:  # plain title: drop the template's title border
        tp = st["Title"].element.pPr
        if tp is not None:
            for b in tp.findall(qn("w:pBdr")): tp.remove(b)
    st["List Bullet"].font.name = "Arial"; st["List Bullet"].font.size = Pt(10.5)

    def rule(p):
        if ats: return
        pPr = p._p.get_or_add_pPr(); bdr = OxmlElement("w:pBdr"); bot = OxmlElement("w:bottom")
        for k, v in (("w:val", "single"), ("w:sz", "8"), ("w:space", "1"), ("w:color", "%02X%02X%02X" % ACCENT)): bot.set(qn(k), v)
        bdr.append(bot); pPr.append(bdr)

    def h1(t): p = d.add_paragraph(t.upper() if ats else t, style="Heading 1"); rule(p)
    def bullets(items):
        for x in items: d.add_paragraph(x, style="List Bullet")

    d.add_paragraph(m["name"], style="Title")
    d.add_paragraph(" · ".join(x for x in [m["title"], m["location"]] + m["contact"] if x))
    if m["summary"]: h1("Summary"); d.add_paragraph(m["summary"])
    if m["highlights"]: h1("Highlights"); bullets(m["highlights"])
    if m["experience"]:
        h1("Experience")
        for e in m["experience"]:
            p = d.add_paragraph(style="Heading 2"); p.add_run(f"{e['position']} — {e['company']}")
            r = p.add_run(f"   {e['dates']}"); r.bold = False; r.font.size = Pt(9.5)
            bullets(e["bullets"])
    for t, items in m["profiles"]: h1(t); bullets(items)
    if m["credentials"]: h1("Licenses & Certifications"); bullets([f"{c['line']} · {c['meta']}" for c in m["credentials"]])
    if m["skills"]: h1("Skills"); d.add_paragraph(", ".join(m["skills"]))
    if m["education"]: h1("Education"); bullets(m["education"])
    if m["languages"]: h1("Languages"); d.add_paragraph(", ".join(m["languages"]))
    if ats:  # O5: no content in header/footer for ATS
        p = d.add_paragraph(m["footer"]); p.runs[0].font.size = Pt(8)
    else:
        fp = sec.footer.paragraphs[0]; fp.text = m["footer"]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fp.runs[0].font.size = Pt(8); fp.runs[0].font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    d.core_properties.title = f"{m['name']} — Resume"; d.core_properties.comments = m["footer"]
    d.core_properties.author = m["name"]; d.core_properties.last_modified_by = "ORA render"
    d.save(path)


def to_pdf(m, path):
    from reportlab.lib.pagesizes import LETTER, A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.colors import Color, black, HexColor
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, HRFlowable
    from reportlab.lib.units import inch
    e = htmllib.escape
    ats = m["template"] == "ats"
    acc = black if ats else Color(*(c / 255 for c in ACCENT))
    S = lambda n, **k: ParagraphStyle(n, fontName=k.pop("font", "Helvetica"), **k)
    title, meta = S("t", font="Helvetica-Bold", fontSize=20, leading=24, textColor=acc), S("m", fontSize=9.5, leading=12, textColor=HexColor("#444444"))
    h1, h2 = S("h1", font="Helvetica-Bold", fontSize=11.5, leading=14, spaceBefore=10, spaceAfter=2, textColor=acc), S("h2", font="Helvetica-Bold", fontSize=10.5, leading=13, spaceBefore=5)
    body = S("b", fontSize=10, leading=13)
    foot = S("f", fontSize=7.5, leading=9, textColor=HexColor("#666666"))
    flow = [Paragraph(e(m["name"]), title), Paragraph(e(" · ".join(x for x in [m["title"], m["location"]] + m["contact"] if x)), meta)]
    def H(t):
        flow.append(Paragraph(e(t.upper()), h1))
        if not ats: flow.append(HRFlowable(width="100%", thickness=1.2, color=acc, spaceBefore=1, spaceAfter=3))
    def B(items):
        flow.append(ListFlowable([ListItem(Paragraph(e(x), body), leftIndent=12) for x in items], bulletType="bullet", start="•", leftIndent=12, bulletFontSize=8))
    if m["summary"]: H("Summary"); flow.append(Paragraph(e(m["summary"]), body))
    if m["highlights"]: H("Highlights"); B(m["highlights"])
    if m["experience"]:
        H("Experience")
        for x in m["experience"]:
            flow.append(Paragraph(f"{e(x['position'])} — {e(x['company'])} <font size=9 color='#555555'>&nbsp;&nbsp;{e(x['dates'])}</font>", h2))
            if x["bullets"]: B(x["bullets"])
    for t, items in m["profiles"]: H(t); B(items)
    if m["credentials"]: H("Licenses & Certifications"); B([f"{c['line']} · {c['meta']}" for c in m["credentials"]])
    if m["skills"]: H("Skills"); flow.append(Paragraph(e(", ".join(m["skills"])), body))
    if m["education"]: H("Education"); B(m["education"])
    if m["languages"]: H("Languages"); flow.append(Paragraph(e(", ".join(m["languages"])), body))
    flow += [Spacer(1, 14), Paragraph(e(m["footer"]), foot)]
    size = A4 if m["page"].get("size") == "a4" else LETTER
    SimpleDocTemplate(str(path), pagesize=size, leftMargin=0.8 * inch, rightMargin=0.8 * inch, topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                      title=f"{m['name']} — Resume", subject=m["footer"]).build(flow)


def render(src_path_or_doc, fmt, view=None, audience=None, template=None, out=None, today=None):
    src = core.load(src_path_or_doc) if isinstance(src_path_or_doc, (str, pathlib.Path)) else src_path_or_doc
    o = src.get("outputs", {}); dflt = o.get("default", {})
    fmt = fmt or dflt.get("format", "docx")
    if fmt not in FORMATS: raise ValueError(f"format must be one of {FORMATS}")
    if o.get("formats") and fmt not in o["formats"]: raise ValueError(f"format '{fmt}' not enabled in outputs.formats")
    template = template or dflt.get("template") or ("academic-cv" if "academic" in src.get("profiles", {}) else "modern")
    if template not in TEMPLATES and not template.startswith("x-"): raise ValueError(f"template must be one of {TEMPLATES}")
    build_aud = src.get("x-build", {}).get("audience")
    audience = audience or dflt.get("audience") or "public"
    if build_aud and core.rank(src, audience) > core.rank(src, build_aud):
        raise PermissionError(f"this agent file was built for '{build_aud}'; cannot render for '{audience}' (X2)")
    m = build_model(src, view or dflt.get("view"), audience, template, today)
    stem = core.slug(m["name"]) + "-resume" + (f"-{m['view']}" if m["view"] else "")
    ext = {"json-resume": "json"}.get(fmt, fmt)
    out = pathlib.Path(out or f"{stem}.{ext}")
    out.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "md": out.write_text(to_md(m), encoding="utf-8")
    elif fmt == "txt": out.write_text(to_txt(m), encoding="utf-8")
    elif fmt == "html": out.write_text(to_html(m), encoding="utf-8")
    elif fmt == "json-resume": out.write_text(to_json_resume(m, src), encoding="utf-8")
    elif fmt == "docx": to_docx(m, out)
    elif fmt == "pdf": to_pdf(m, out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", help="resume-agent.md or resume-agent.json")
    ap.add_argument("--format", choices=FORMATS); ap.add_argument("--view"); ap.add_argument("--audience")
    ap.add_argument("--template"); ap.add_argument("-o", "--out"); ap.add_argument("--today")
    a = ap.parse_args()
    today = datetime.date.fromisoformat(a.today) if a.today else None
    print(render(a.src, a.format, a.view, a.audience, a.template, a.out, today))


if __name__ == "__main__":
    main()

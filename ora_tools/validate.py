#!/usr/bin/env python3
"""ORA L1 validator: JSON Schema + semantic checks.

Usage: python3 tools/validate.py <file.resume-agent.json> [...] [--today YYYY-MM-DD]
Exit code 0 = no errors (warnings allowed).
"""
import json, re, sys, pathlib, datetime
from jsonschema import Draft202012Validator, FormatChecker
from . import ora_core as core

SCHEMA = json.loads((pathlib.Path(__file__).resolve().parent / "schema.json").read_text())
PROFILE_CREDS = {"healthcare": "license", "legal": None, "aviation": None, "trades": None, "education": "license", "academic": "degree"}
AUDIENCE_DEFAULT = ["public", "recruiter", "verified_employer", "owner"]


def to_date(s):
    if not s: return None
    parts = [int(p) for p in s.split("-")]
    while len(parts) < 3: parts.append(28 if len(parts) == 2 else 12)
    return datetime.date(*parts)


def walk_scalars(obj, path):
    if isinstance(obj, dict):
        for k, v in obj.items(): yield from walk_scalars(v, f"{path}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj): yield from walk_scalars(v, f"{path}/{i}")
    else:
        yield path, obj


def check(doc, today):
    errors, warnings = [], []
    v = Draft202012Validator(SCHEMA, format_checker=FormatChecker())
    for e in sorted(v.iter_errors(doc), key=lambda e: list(e.path)):
        errors.append(f"schema: /{'/'.join(map(str, e.path))}: {e.message[:160]}")
    if errors:
        return errors, warnings

    ids = {}
    for sect in ("claims", "skills", "credentials", "evidence", "narratives", "roleViews"):
        for item in doc.get(sect, []):
            if item["id"] in ids:
                errors.append(f"duplicate id '{item['id']}' in {sect} and {ids[item['id']]}")
            ids[item["id"]] = sect
    def need(ref, sect, where):
        if ids.get(ref) != sect:
            errors.append(f"{where}: '{ref}' is not a known {sect} id")

    for c in doc["claims"]:
        for e in c.get("evidence", []): need(e, "evidence", f"claim {c['id']}")
        vu = c.get("validUntil")
        if vu and to_date(vu) < today and "current" in c["statement"].lower():
            warnings.append(f"claim {c['id']}: expired but worded as current (C5)")
    for s in doc.get("skills", []):
        for e in s.get("evidence", []): need(e, "evidence", f"skill {s['id']}")
        if s.get("assurance") in ("documented", "verified") and not s.get("evidence"):
            errors.append(f"skill {s['id']}: assurance {s['assurance']} requires evidence")
    for cr in doc.get("credentials", []):
        for e in cr.get("evidence", []): need(e, "evidence", f"credential {cr['id']}")
        exp = to_date(cr.get("expiresAt"))
        if exp and exp < today and cr["status"] == "active":
            warnings.append(f"credential {cr['id']}: expiresAt {cr['expiresAt']} has passed but status is 'active' — agent will present it as expired (R1)")
        lc = to_date(cr.get("verification", {}).get("lastChecked"))
        if lc and (today - lc).days > 90:
            warnings.append(f"credential {cr['id']}: verification last checked {(today - lc).days} days ago (R4)")
        if cr["kind"] == "clearance" and cr.get("identifier"):
            warnings.append(f"credential {cr['id']}: clearance identifiers should not be stored (R3)")

    disc = doc["disclosure"]
    auds = disc["audiences"]
    if disc["default"] not in auds:
        errors.append(f"disclosure.default '{disc['default']}' not in audiences")
    if "owner" not in auds:
        warnings.append("disclosure.audiences has no 'owner' level")
    for r in disc.get("rules", []):
        for a in r["audiences"]:
            if a not in auds: errors.append(f"disclosure rule uses unknown audience '{a}'")
        for k, sect in (("claim", "claims"), ("credential", "credentials"), ("skill", "skills")):
            if k in r: need(r[k], sect, "disclosure rule")
    for n in doc.get("narratives", []):
        for a in n.get("audiences", []):
            if a not in auds: errors.append(f"narrative {n['id']}: unknown audience '{a}'")

    for k, cm in doc["commitments"].items():
        if k == "handoff": continue
        for a in cm.get("audiences", []):
            if a not in auds: errors.append(f"commitment {k}: unknown audience '{a}'")

    pol = core.Policy(doc)
    nums = lambda t: set(re.findall(r"\d[\d,.]*", t or ""))
    for rv in doc.get("roleViews", []):
        open_nums = set().union(*[nums(c["statement"]) for c in doc["claims"] if pol.for_claim(c) == pol.default] or [set()])
        hidden = set().union(*[nums(c["statement"]) for c in doc["claims"] if pol.for_claim(c) != pol.default] or [set()])
        leak = (nums(rv.get("summary")) & hidden) - open_nums
        if leak:
            warnings.append(f"roleView {rv['id']}: summary mentions {sorted(leak)} which only appears in restricted claims (V1/D1)")

    hidden_all = set().union(*[nums(c["statement"]) for c in doc["claims"] if pol.for_claim(c) != pol.default] or [set()])
    for p_, val in walk_scalars(doc.get("profiles", {}), "/profiles"):
        if isinstance(val, (int, float)) and not isinstance(val, bool) and val >= 10 and pol.for_ptr(p_) == pol.default and str(val) in hidden_all:
            warnings.append(f"{p_}: value {val} is public but also appears in a restricted claim (D1) — restrict it too")

    defaults = 0
    profiles = set(doc.get("profiles", {}))
    for rv in doc.get("roleViews", []):
        defaults += bool(rv.get("default"))
        inc = rv.get("include", {})
        for c in inc.get("claims", []): need(c, "claims", f"roleView {rv['id']}")
        for s in inc.get("skills", []): need(s, "skills", f"roleView {rv['id']}")
        for c in inc.get("credentials", []): need(c, "credentials", f"roleView {rv['id']}")
        for c in rv.get("exclude", {}).get("claims", []): need(c, "claims", f"roleView {rv['id']}")
        for p in inc.get("profiles", []):
            if p not in profiles: errors.append(f"roleView {rv['id']}: profile '{p}' not present")
        for k, cm in rv.get("commitmentsOverride", {}).items():
            base = doc["commitments"].get(k, {})
            if base.get("mode") == "never" and cm["mode"] != "never":
                errors.append(f"roleView {rv['id']}: loosens 'never' commitment {k} (V4)")
    if defaults > 1:
        errors.append("more than one roleView marked default")

    def walk(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items(): yield from walk(v, f"{path}/{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj): yield from walk(v, f"{path}/{i}")
        else:
            yield path, obj
    cred_ids = {c["id"] for c in doc.get("credentials", [])}
    for name, prof in doc.get("profiles", {}).items():
        for p, val in walk(prof, f"/profiles/{name}"):
            if any(seg in p for seg in ("boardCertifications", "barAdmissions", "registrations", "certificates", "safetyCertifications", "certifications", "foodSafety")) or p.endswith("/clearance"):
                if isinstance(val, str) and val not in cred_ids:
                    errors.append(f"{p}: '{val}' is not a credential id")
        want = PROFILE_CREDS.get(name)
        if want and not any(c["kind"] == want for c in doc.get("credentials", [])):
            warnings.append(f"profile {name}: expected a '{want}' credential (P2)")

    def resolves(ptr):
        if ptr.startswith("/resume/") and "resume" not in doc:
            return True  # remote resume: can't check offline
        cur = doc
        for raw in ptr.split("/")[1:]:
            seg = raw.replace("~1", "/").replace("~0", "~")
            if isinstance(cur, list) and seg.isdigit() and int(seg) < len(cur): cur = cur[int(seg)]
            elif isinstance(cur, dict) and seg in cur: cur = cur[seg]
            else: return False
        return True
    ptrs = [(f"claim {c['id']}", c["path"]) for c in doc["claims"] if "path" in c]
    ptrs += [("disclosure rule", r["path"]) for r in disc.get("rules", []) if "path" in r]
    ptrs += [("classification entry", e["path"]) for e in doc.get("classification", {}).get("entries", [])]
    for where, p in ptrs:
        if not resolves(p): errors.append(f"{where}: pointer '{p}' does not resolve")
    for p in disc.get("never", []):
        if not resolves(p): warnings.append(f"disclosure.never: pointer '{p}' does not resolve (nothing to protect)")

    comp = doc.get("compliance", {})
    if not comp:
        warnings.append("no compliance block — defaults apply (salaryHistory=never, criminalHistory=handoff)")
    for k in ("salary",):
        cm = doc["commitments"].get(k)
        if cm and cm["mode"] in ("share", "range") and not cm.get("audiences"):
            warnings.append(f"commitment {k}: visible to every audience including public")
    caps = {c["id"]: c for c in doc["capabilities"]}
    for cid in ("form_fill",):
        if caps.get(cid, {}).get("enabled") and not caps[cid].get("requiresOwnerApproval"):
            warnings.append(f"capability {cid}: consider requiresOwnerApproval (A1)")
    return errors, warnings


HEADINGS = ["1. Agent Instructions", "2. Profile", "3. Experience", "4. Credentials", "5. Skills", "6. Industry Profiles",
            "7. Role Views", "8. Preferences", "9. Disclosure Policy", "10. Commitments & Handoff", "11. Output Generation", "12. ORA Data"]


def check_md(path, today):
    """Agent-file checks (M1–M3) + L1 checks on the data block."""
    text = pathlib.Path(path).read_text(encoding="utf-8")
    errors, warnings = [], []
    fm = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not fm:
        return ["agent file: missing front matter"], []
    keys = [l.split(":", 1)[0] for l in fm.group(1).splitlines() if ":" in l and not l.startswith(" ")]
    if keys[:2] != ["name", "description"]:
        errors.append("front matter: first keys must be name, description (§18.2)")
    meta = dict(l.split(": ", 1) for l in fm.group(1).splitlines() if ": " in l)
    found = re.findall(r"^## (.+)$", re.sub(r"```.*?```", "", text, flags=re.S), re.M)
    if found != HEADINGS:
        errors.append(f"M2: section headings/order mismatch: {found}")
    try:
        doc = core.load(path)
    except Exception as e:
        return errors + [str(e)], warnings
    if meta.get("digest") != core.digest(doc):
        errors.append("M3: digest does not match the ORA Data block")
    e2, w2 = check(doc, today)
    if meta.get("build") == "public":
        pol = core.Policy(doc)
        for p, a in pol.ptr.items():
            if a != "public" and core.get_ptr(doc, p) is not None and not p.startswith("/profiles/"):
                errors.append(f"M7: public build contains restricted item {p}")
    return errors + e2, warnings + w2


def main(argv):
    today = datetime.date.today()
    files = []
    it = iter(argv)
    for a in it:
        if a == "--today": today = datetime.date.fromisoformat(next(it))
        else: files.append(a)
    rc = 0
    for f in files:
        if f.endswith(".md"):
            errs, warns = check_md(f, today)
        else:
            errs, warns = check(json.loads(pathlib.Path(f).read_text()), today)
        status = "FAIL" if errs else "PASS (L1)"
        print(f"{status}  {f}")
        for e in errs: print(f"  ERROR  {e}")
        for w in warns: print(f"  warn   {w}")
        rc |= bool(errs)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""ORA core: load, audience filtering, role views, digests. Shared by build_md, render and ora_mcp."""
import copy, datetime, hashlib, json, pathlib, re

LADDER = ["public", "recruiter", "verified_employer", "owner"]
DATA_FENCE = re.compile(r"```json ora\n(.*?)\n```", re.S)
# Sensitive-by-default profile fields (PROFILES.md): pointer suffix -> minimum audience
PROFILE_DEFAULTS = {
    "/profiles/healthcare/npi": "verified_employer",
    "/profiles/trades/unionAffiliation": "owner",
    "/profiles/creative/unions": "owner",
    "/profiles/aviation/medicalClass": "owner",
}


# ---------- loading ----------
def load(path):
    """Load an ORA document from .json or an agent file (.md)."""
    text = pathlib.Path(path).read_text(encoding="utf-8")
    if str(path).endswith(".md"):
        m = DATA_FENCE.search(text)
        if not m:
            raise ValueError(f"{path}: no ```json ora data block (M1)")
        return json.loads(m.group(1))
    return json.loads(text)


def canonical(doc):
    """Canonical JSON (RFC 8785-compatible for integer/str data: sorted keys, no whitespace)."""
    return json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(doc):
    return "sha256-" + hashlib.sha256(canonical(doc).encode("utf-8")).hexdigest()


# ---------- audiences ----------
def ladder(doc):
    return doc.get("disclosure", {}).get("audiences") or LADDER


def rank(doc, aud):
    lad = ladder(doc)
    return lad.index(aud) if aud in lad else 0


def lowest(doc, auds):
    """Minimum audience from a list ([] means owner-only)."""
    lad = ladder(doc)
    if not auds:
        return lad[-1]
    return min(auds, key=lambda a: rank(doc, a))


def get_ptr(doc, ptr):
    cur = doc
    for raw in ptr.split("/")[1:]:
        seg = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, list) and seg.isdigit() and int(seg) < len(cur):
            cur = cur[int(seg)]
        elif isinstance(cur, dict) and seg in cur:
            cur = cur[seg]
        else:
            return None
    return cur


def del_ptr(doc, ptr):
    parts = [p.replace("~1", "/").replace("~0", "~") for p in ptr.split("/")[1:]]
    parent = get_ptr(doc, "/" + "/".join(parts[:-1])) if len(parts) > 1 else doc
    if parent is None:
        return
    last = parts[-1]
    if isinstance(parent, dict):
        parent.pop(last, None)
    elif isinstance(parent, list) and last.isdigit() and int(last) < len(parent):
        parent[int(last)] = None  # tombstone; compacted later to keep sibling indices valid


class Policy:
    """Resolves the minimum audience for any item in a document."""

    def __init__(self, doc):
        self.doc = doc
        d = doc.get("disclosure", {})
        self.default = d.get("default", "public")
        self.never = list(d.get("never", []))
        self.ptr, self.claim, self.cred, self.cred_fields, self.skill = {}, {}, {}, {}, {}
        for r in d.get("rules", []):
            a = lowest(doc, r["audiences"])
            if "path" in r: self.ptr[r["path"]] = a
            if "claim" in r: self.claim[r["claim"]] = a
            if "skill" in r: self.skill[r["skill"]] = a
            if "credential" in r:
                if r.get("fields"):
                    for f in r["fields"]: self.cred_fields[(r["credential"], f)] = a
                else:
                    self.cred[r["credential"]] = a
        for c in doc.get("claims", []):  # a claim's restriction also covers the resume text it points to
            if c["id"] in self.claim and c.get("path"):
                self.ptr.setdefault(c["path"], self.claim[c["id"]])
        for p, a in PROFILE_DEFAULTS.items():
            self.ptr.setdefault(p, a)

    def is_never(self, ptr):
        return any(ptr == n or ptr.startswith(n + "/") for n in self.never)

    def for_ptr(self, ptr):
        best, blen = self.default, -1
        for p, a in self.ptr.items():
            if (ptr == p or ptr.startswith(p + "/")) and len(p) > blen:
                best, blen = a, len(p)
        return best

    def for_claim(self, c):
        if c["id"] in self.claim: return self.claim[c["id"]]
        if c.get("path"): return self.for_ptr(c["path"])
        return self.default

    def for_cred(self, cr):
        if cr["id"] in self.cred: return self.cred[cr["id"]]
        return "verified_employer" if cr["kind"] == "clearance" else self.default  # R3

    def for_cred_field(self, cr, field):
        if (cr["id"], field) in self.cred_fields: return self.cred_fields[(cr["id"], field)]
        if field == "identifier": return "verified_employer"  # R2
        return self.for_cred(cr)

    def for_commitment(self, cm):
        return lowest(self.doc, cm["audiences"]) if "audiences" in cm else self.default

    def visible(self, need, audience):
        return rank(self.doc, audience) >= rank(self.doc, need)


def _compact(o):
    if isinstance(o, dict):
        return {k: _compact(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_compact(v) for v in o if v is not None]
    return o


def filter_doc(doc, audience):
    """Return a copy of doc containing only what `audience` may see (M7 public build when audience='public')."""
    pol = Policy(doc)
    out = copy.deepcopy(doc)
    if audience == ladder(doc)[-1]:
        out["x-build"] = {"audience": audience}
        return out
    restricted = [p for p, a in pol.ptr.items() if not pol.visible(a, audience)] + pol.never
    for p in sorted(restricted, key=len, reverse=True):
        del_ptr(out, p)
    out = _compact(out)

    keep_claims = []
    for c in out.get("claims", []):
        if pol.visible(pol.for_claim(c), audience) and not (c.get("path") and pol.is_never(c["path"])):
            if c.get("path") and get_ptr(out, c["path"]) is None:
                c = {k: v for k, v in c.items() if k != "path"}
            keep_claims.append(c)
    out["claims"] = keep_claims or [{"id": "cl-none", "statement": "No claims are visible to this audience.", "assurance": "self_asserted"}]

    creds = []
    for cr in out.get("credentials", []):
        if not pol.visible(pol.for_cred(cr), audience): continue
        for f in ("identifier",):
            if f in cr and not pol.visible(pol.for_cred_field(cr, f), audience): cr.pop(f)
        creds.append(cr)
    if "credentials" in out: out["credentials"] = creds
    if "skills" in out:
        out["skills"] = [s for s in out["skills"] if pol.visible(pol.skill.get(s["id"], pol.default), audience)]
    if "narratives" in out:
        out["narratives"] = [n for n in out["narratives"] if pol.visible(lowest(doc, n["audiences"]) if "audiences" in n else pol.default, audience)]

    def strip_commitments(cms):
        for k, cm in list(cms.items()):
            if k == "handoff": continue
            if cm.get("mode") in ("share", "range") and not pol.visible(pol.for_commitment(cm), audience):
                cms[k] = {"mode": "handoff"}
    strip_commitments(out.get("commitments", {}))
    for rv in out.get("roleViews", []):
        strip_commitments(rv.get("commitmentsOverride", {}))
    if "preferences" in out and not pol.visible("owner", audience):
        out["preferences"].pop("excludeEmployers", None)

    # prune ids no longer present
    ids = {x["id"] for s in ("claims", "credentials", "skills", "evidence") for x in out.get(s, [])}
    for rv in out.get("roleViews", []):
        for k in ("claims", "skills", "credentials"):
            if k in rv.get("include", {}): rv["include"][k] = [i for i in rv["include"][k] if i in ids]
        if "claims" in rv.get("exclude", {}): rv["exclude"]["claims"] = [i for i in rv["exclude"]["claims"] if i in ids]
    used_ev = {e for s in ("claims", "credentials", "skills") for x in out.get(s, []) for e in x.get("evidence", [])}
    if "evidence" in out:
        out["evidence"] = [e for e in out["evidence"] if e["id"] in used_ev]
    disc = out.get("disclosure", {})
    disc["rules"] = [r for r in disc.get("rules", [])
                     if (("claim" not in r or r["claim"] in ids) and ("credential" not in r or r["credential"] in ids)
                         and ("skill" not in r or r["skill"] in ids) and ("path" not in r or get_ptr(out, r["path"]) is not None))]
    disc["never"] = [n for n in disc.get("never", []) if get_ptr(out, n) is not None]
    for prof in list(out.get("profiles", {}).values()):
        for key in ("boardCertifications", "certifications", "safetyCertifications", "registrations", "certificates", "barAdmissions", "foodSafety"):
            if key in prof: prof[key] = [i for i in prof[key] if i in ids]
        if prof.get("clearance") and prof["clearance"] not in ids: prof.pop("clearance")
    out["x-build"] = {"audience": audience}
    return out


# ---------- credentials ----------
def effective_status(cr, today=None):
    today = today or datetime.date.today()
    exp = cr.get("expiresAt")
    if exp:
        parts = [int(p) for p in exp.split("-")] + [12, 28][len(exp.split("-")) - 1:]
        if datetime.date(*parts[:3]) < today:
            return "expired"
    return cr["status"]


# ---------- views ----------
def pick_view(doc, view_id=None):
    views = doc.get("roleViews", [])
    if view_id:
        for v in views:
            if v["id"] == view_id: return v
        raise KeyError(f"unknown view '{view_id}'")
    return next((v for v in views if v.get("default")), None)


def view_claims(doc, view):
    """Claims selected by a view (all claims if no view / no include filter), in view order."""
    claims = doc.get("claims", [])
    if not view: return claims
    inc, exc = view.get("include", {}), view.get("exclude", {})
    sel = claims
    if inc.get("claims") or inc.get("tags"):
        by_id = {c["id"]: c for c in claims}
        sel = [by_id[i] for i in inc.get("claims", []) if i in by_id]
        sel += [c for c in claims if c not in sel and set(c.get("tags", [])) & set(inc.get("tags", []))]
    return [c for c in sel if c["id"] not in exc.get("claims", []) and not set(c.get("tags", [])) & set(exc.get("tags", []))]


def view_skills(doc, view):
    skills = doc.get("skills", [])
    if view and view.get("include", {}).get("skills"):
        want = view["include"]["skills"]
        return [s for s in skills if s["id"] in want]
    return skills


def view_commitments(doc, view):
    cms = dict(doc.get("commitments", {}))
    if view:
        cms.update(view.get("commitmentsOverride", {}))
    return cms


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:64]

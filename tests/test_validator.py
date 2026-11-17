"""Run: python3 -m pytest tests  (or python3 tests/test_validator.py)"""
import copy, datetime, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from validate import check  # noqa: E402

TODAY = datetime.date(2026, 11, 17)
EX = {p.stem.split(".")[0]: json.loads(p.read_text()) for p in (ROOT / "examples").glob("*.resume-agent.json")}


def errs(doc): return check(doc, TODAY)[0]
def warns(doc): return check(doc, TODAY)[1]
def mutate(name, fn):
    d = copy.deepcopy(EX[name]); fn(d); return d


def test_examples_pass():
    for name, doc in EX.items():
        assert errs(doc) == [], (name, errs(doc))

def test_documented_claim_needs_evidence():
    assert errs(mutate("tech-executive", lambda d: d["claims"][0].pop("evidence")))

def test_submit_requires_approval():
    def f(d):
        for c in d["capabilities"]:
            if c["id"] == "submit": c["requiresOwnerApproval"] = False
    assert errs(mutate("tech-executive", f))

def test_resume_xor_resume_url():
    assert errs(mutate("tech-executive", lambda d: d.update(resumeUrl="https://x.example/r.json")))

def test_unknown_evidence_ref():
    assert any("not a known evidence" in e for e in errs(mutate("tech-executive", lambda d: d["claims"][0].update(evidence=["ev-nope"]))))

def test_dangling_pointer():
    assert any("does not resolve" in e for e in errs(mutate("tech-executive", lambda d: d["claims"][0].update(path="/resume/work/9"))))

def test_view_cannot_loosen_never():
    def f(d):
        d["commitments"]["equity"] = {"mode": "never"}
        d["roleViews"][0]["commitmentsOverride"]["equity"] = {"mode": "share", "value": "0.5%"}
    assert any("V4" in e for e in errs(mutate("tech-executive", f)))

def test_profile_credential_ref():
    assert errs(mutate("registered-nurse", lambda d: d["profiles"]["healthcare"].update(boardCertifications=["cr-missing"])))

def test_healthcare_requires_discipline():
    assert errs(mutate("registered-nurse", lambda d: d["profiles"]["healthcare"].pop("discipline")))

def test_unknown_profile_rejected():
    assert errs(mutate("electrician", lambda d: d["profiles"].update(plumbing={"x": 1})))

def test_custom_profile_allowed():
    assert not errs(mutate("electrician", lambda d: d["profiles"].update({"x-solar": {"panelsInstalled": 900}})))

def test_legal_matters_must_be_confidential():
    d = mutate("tech-executive", lambda d: d["profiles"].update(legal={"matters": [{"type": "M&A", "confidential": False}]}))
    assert errs(d)

def test_criminal_history_cannot_be_shared():
    assert errs(mutate("veteran-logistics", lambda d: d["compliance"].update(criminalHistory="share")))

def test_expired_active_license_warns():
    assert any("R1" in w for w in warns(EX["registered-nurse"]))

def test_two_default_views():
    def f(d):
        for v in d["roleViews"]: v["default"] = True
    assert errs(mutate("veteran-logistics", f))

def test_conformance_fixtures_exist():
    cases = json.loads((ROOT / "conformance" / "cases.json").read_text())
    for k, rel in cases["fixtures"].items():
        assert (ROOT / "conformance" / rel).resolve().exists(), k
    ids = [c["id"] for c in cases["cases"]]
    assert len(ids) == len(set(ids))
    for c in cases["cases"]:
        assert c["fixture"] in cases["fixtures"]
        assert c["expect"]["behavior"] in ("answer", "decline", "handoff", "unknown")


if __name__ == "__main__":
    fails = 0
    for n, fn in list(globals().items()):
        if n.startswith("test_"):
            try: fn(); print("ok  ", n)
            except AssertionError as e: fails += 1; print("FAIL", n, e)
    sys.exit(fails)

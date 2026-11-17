"""Builds schema/resume-agent.schema.json (ORA v0.3). Run: python3 tools/build_schema.py"""
import json, pathlib

S = {"type": "string"}
N = {"type": "number"}
I = {"type": "integer", "minimum": 0}
B = {"type": "boolean"}
U = {"type": "string", "format": "uri"}
D = {"type": "string", "pattern": r"^\d{4}(-\d{2}(-\d{2})?)?$"}
def arr(x): return {"type": "array", "items": x}
def enum(*v): return {"enum": list(v)}
ID = {"$ref": "#/$defs/id"}
IDS = arr(ID)
PTR = {"$ref": "#/$defs/pointer"}
CODE = {"$ref": "#/$defs/code"}
METRIC = {"$ref": "#/$defs/metric"}

def obj(props, required=(), extensible=True):
    o = {"type": "object", "properties": props}
    if required: o["required"] = list(required)
    if extensible:
        o["patternProperties"] = {"^x-": {}}
        o["additionalProperties"] = False
    return o

profiles = {
  "technology": obj({
    "stacks": arr(S),
    "systemsScale": obj({"rps": N, "dataVolume": S, "users": N, "regions": I}),
    "onCall": obj({"experience": B, "maxRotation": S}),
    "openSource": arr(obj({"repo": U, "role": enum("maintainer", "contributor"), "evidence": IDS}, ["repo"])),
    "securityClearanceRequiredOk": B,
    "sfia": arr(obj({"code": S, "level": {"type": "integer", "minimum": 1, "maximum": 7}}, ["code", "level"]))}),
  "healthcare": obj({
    "discipline": enum("rn", "lpn", "aprn", "physician", "pa", "pharmacist", "therapist", "technologist", "paramedic", "dentist", "other"),
    "specialties": arr(S), "boardCertifications": IDS,
    "patientPopulations": arr(enum("neonatal", "pediatric", "adult", "geriatric")),
    "settings": arr(enum("acute", "ambulatory", "long_term", "home", "telehealth", "research")),
    "ehrSystems": arr(S),
    "procedures": arr(obj({"name": S, "count": I, "period": S}, ["name"])),
    "npi": {"type": "string", "pattern": r"^\d{10}$"},
    "compactLicensure": obj({"name": S, "multistate": B})}, ["discipline"]),
  "academic": obj({
    "orcid": {"type": "string", "pattern": r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$"},
    "researchAreas": arr(S),
    "publications": arr(obj({"doi": S, "title": S, "venue": S, "year": I, "peerReviewed": B,
        "creditRoles": arr(obj({"role": {"$ref": "#/$defs/creditRole"}, "degree": enum("lead", "equal", "supporting")}, ["role"]))}, ["title"])),
    "grants": arr(obj({"funder": S, "title": S, "role": enum("PI", "co-PI", "key_personnel", "other"), "amount": N, "currency": {"$ref": "#/$defs/currency"}, "years": S}, ["funder"])),
    "teaching": arr(obj({"course": S, "level": S, "years": S}, ["course"])),
    "supervision": obj({"phd": I, "masters": I, "postdocs": I}),
    "metrics": obj({"hIndex": I, "citations": I, "asOf": D, "source": S}),
    "tenureStatus": enum("tenured", "tenure_track", "non_tenure", "n/a")}),
  "legal": obj({
    "barAdmissions": IDS, "practiceAreas": arr(S),
    "matters": arr(obj({"type": S, "role": S, "outcome": S, "confidential": {"const": True}}, ["type", "confidential"])),
    "clerkships": arr(obj({"court": S, "judge": S, "years": S})),
    "languagesForPractice": arr(S), "conflictsCheckRequired": B}),
  "finance": obj({
    "registrations": IDS, "aum": METRIC, "coverage": arr(S),
    "dealExperience": arr(obj({"type": S, "size": N, "currency": {"$ref": "#/$defs/currency"}, "role": S, "year": I, "confidential": B}, ["type"])),
    "regulatoryHistory": {"const": "handoff"}}),
  "aviation": obj({
    "certificates": IDS,
    "ratings": arr(obj({"type": enum("type_rating", "instrument", "multi_engine", "other"), "aircraft": S}, ["type"])),
    "flightHours": obj({"total": I, "pic": I, "sic": I, "multiEngine": I, "turbine": I, "instrument": I, "night": I, "crossCountry": I, "asOf": D}, ["total"]),
    "medicalClass": enum("first", "second", "third", "none"),
    "aircraftTypes": arr(S),
    "operations": arr(enum("part121", "part135", "part91", "military", "cargo", "ga"))}),
  "trades": obj({
    "trade": S, "level": enum("apprentice", "journeyman", "master", "foreman", "superintendent"),
    "apprenticeship": obj({"program": S, "hoursCompleted": I, "hoursRequired": I, "sponsor": S}),
    "safetyCertifications": IDS, "equipment": arr(S), "codes": arr(S), "ownTools": B,
    "driversLicense": {"$ref": "#/$defs/driversLicense"},
    "unionAffiliation": obj({"local": S, "status": S})}, ["trade"]),
  "education": obj({
    "certifications": IDS, "gradeLevels": arr(S), "subjects": arr(S),
    "specialPopulations": arr(S), "curricula": arr(S), "backgroundClearance": {"const": "handoff"}}),
  "creative": obj({
    "portfolio": arr(obj({"title": S, "url": U, "role": S, "year": I, "client": S,
        "rights": enum("owned", "licensed", "nda", "work_for_hire"), "thumbnail": U}, ["title", "rights"])),
    "tools": arr(S), "awards": arr(obj({"name": S, "year": I, "issuer": S}, ["name"])),
    "credits": arr(obj({"title": S, "role": S, "year": I, "verifiedSource": U}, ["title", "role"])),
    "unions": arr(obj({"name": S, "status": S}))}),
  "military": obj({
    "branch": S,
    "occupations": arr(obj({"scheme": {"const": "moc"}, "code": S, "title": S, "years": S}, ["code"])),
    "civilianCrosswalk": arr(CODE), "rank": S, "clearance": ID, "transcripts": IDS}),
  "public_sector": obj({
    "gradeHistory": arr(obj({"system": S, "grade": S, "step": S, "years": S}, ["system", "grade"])),
    "serviceType": enum("competitive", "excepted", "ses", "foreign_service", "ngo", "igo"),
    "eligibility": arr(S), "clearance": ID}),
  "sales": obj({
    "quota": arr(obj({"year": I, "quota": N, "attainment": N, "currency": {"$ref": "#/$defs/currency"}}, ["year", "attainment"])),
    "dealSize": obj({"avg": N, "max": N, "currency": {"$ref": "#/$defs/currency"}}),
    "segments": arr(enum("smb", "mid_market", "enterprise", "strategic", "public")),
    "motion": arr(enum("inbound", "outbound", "channel", "plg")),
    "territories": arr(S), "crmTools": arr(S)}),
  "executive": obj({
    "scope": obj({"orgSize": I, "budget": N, "pnl": N, "revenue": N, "currency": {"$ref": "#/$defs/currency"}, "geographies": arr(S)}),
    "boardSeats": arr(obj({"org": S, "role": S, "committee": S, "since": D}, ["org"])),
    "transformations": arr(obj({"type": enum("turnaround", "IPO", "M&A", "scale-up", "digital", "other"), "outcome": S, "year": I}, ["type"])),
    "investorFacing": B, "reportingLine": S}),
  "hospitality_retail": obj({
    "roles": arr(S), "foodSafety": IDS, "posSystems": arr(S),
    "volume": obj({"coversPerShift": I, "storeRevenue": N, "currency": {"$ref": "#/$defs/currency"}}),
    "availability": obj({"days": arr(enum("mon", "tue", "wed", "thu", "fri", "sat", "sun")), "hours": S, "minHoursPerWeek": I, "maxHoursPerWeek": I})}),
  "logistics": obj({
    "driversLicense": {"$ref": "#/$defs/driversLicense"},
    "safetyRecord": {"const": "handoff"}, "equipment": arr(S),
    "routes": arr(enum("local", "regional", "otr")), "systems": arr(S), "homeTimePreference": S}),
}

commitment = {
  "type": "object", "required": ["mode"],
  "properties": {"mode": enum("share", "range", "handoff", "never"), "value": {}, "audiences": arr(S)},
  "allOf": [
    {"if": {"properties": {"mode": enum("share", "range")}}, "then": {"required": ["value"]}},
    {"if": {"properties": {"mode": {"const": "range"}}}, "then": {"properties": {"value": {"type": "object", "required": ["min"]}}}}]}

idref_rule = {"type": "object", "required": ["audiences"],
  "oneOf": [{"required": ["path"]}, {"required": ["claim"]}, {"required": ["credential"]}, {"required": ["skill"]}],
  "properties": {"path": PTR, "claim": ID, "credential": ID, "skill": ID, "fields": arr(S), "audiences": arr(S)}}

schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://openresumeagent.org/schema/v0.3/resume-agent.schema.json",
  "title": "Open Resume Agent v0.3",
  "type": "object",
  "required": ["ora", "owner", "claims", "disclosure", "commitments", "capabilities"],
  "oneOf": [{"required": ["resume"], "not": {"required": ["resumeUrl"]}},
            {"required": ["resumeUrl"], "not": {"required": ["resume"]}}],
  "patternProperties": {"^x-": {}},
  "additionalProperties": False,
  "properties": {
    "$schema": S, "ora": {"enum": ["0.2", "0.3"]},
    "resume": {"type": "object", "description": "JSON Resume v1.0.0"}, "resumeUrl": U,
    "owner": obj({"name": S, "preferredName": S, "pronouns": {"type": ["string", "null"]}, "contact": U,
        "verifiedHandles": arr(obj({"platform": S, "url": U}, ["platform", "url"])),
        "did": {"type": "string", "pattern": "^did:"}, "publicKey": {"type": "object", "required": ["kty"]}}, ["name", "contact"]),
    "locale": obj({"primaryLanguage": S,
        "languages": arr(obj({"tag": S, "proficiency": {"type": "string", "pattern": "^(native|[ABC][12]|ILR-[0-5]\\+?)$"}, "scale": enum("CEFR", "ILR", "native")}, ["tag", "proficiency"])),
        "jurisdictions": arr({"type": "string", "pattern": "^[A-Z]{2}(-[A-Z0-9]{1,3})?$"}), "timeZone": S}),
    "classification": obj({"target": arr(CODE),
        "entries": arr(obj({"path": PTR, "occupation": arr(CODE), "industry": arr(CODE)}, ["path"]))}),
    "skills": arr(obj({"id": ID, "name": S, "refs": arr(CODE),
        "level": obj({"value": N, "max": N, "scale": S}, ["value", "max", "scale"]),
        "years": N, "lastUsed": D, "evidence": IDS, "assurance": {"$ref": "#/$defs/assurance"}}, ["id", "name"])),
    "credentials": arr(obj({"id": ID,
        "kind": {"anyOf": [enum("license", "certification", "registration", "clearance", "degree", "apprenticeship", "endorsement", "rating", "membership"), {"type": "string", "pattern": "^x-"}]},
        "name": S, "issuer": S, "jurisdiction": S, "identifier": S,
        "status": enum("active", "inactive", "expired", "suspended", "revoked", "pending", "lapsed"),
        "issuedAt": D, "expiresAt": D,
        "verification": obj({"method": enum("vc", "primary_source", "issuer_api", "document", "none"), "url": U, "lastChecked": D, "result": S}, ["method"]),
        "evidence": IDS, "compact": obj({"name": S, "multistate": B})}, ["id", "kind", "name", "status"])),
    "evidence": arr(obj({"id": ID, "type": enum("url", "artifact", "credential", "reference", "publication", "repository", "assessment", "transcript"),
        "uri": U, "issuer": S, "issuedAt": D, "digest": {"type": "string", "pattern": "^sha(256|384|512)-"}, "format": S,
        "consent": obj({"granted": B, "date": D, "scope": S})}, ["id", "type"])),
    "claims": {"type": "array", "minItems": 1, "items": {
        "allOf": [obj({"id": ID, "path": PTR, "statement": {"type": "string", "minLength": 1}, "evidence": IDS,
            "assurance": {"$ref": "#/$defs/assurance"}, "metrics": arr(METRIC), "validFrom": D, "validUntil": {"anyOf": [D, {"type": "null"}]},
            "tags": arr(S), "confidential": B}, ["id", "statement", "assurance"])],
        "if": {"properties": {"assurance": enum("documented", "verified")}},
        "then": {"required": ["evidence"], "properties": {"evidence": {"minItems": 1}}}}},
    "narratives": arr(obj({"id": ID, "topic": S, "text": S, "verbatim": B, "audiences": arr(S)}, ["id", "topic", "text"])),
    "roleViews": arr(obj({"id": ID, "title": S, "target": arr(CODE), "summary": S,
        "include": obj({"claims": IDS, "skills": IDS, "credentials": IDS, "tags": arr(S), "profiles": arr(S)}),
        "exclude": obj({"claims": IDS, "tags": arr(S)}), "emphasis": arr(S),
        "commitmentsOverride": {"type": "object", "additionalProperties": {"$ref": "#/$defs/commitment"}},
        "default": B}, ["id", "title"])),
    "profiles": obj(profiles),
    "preferences": obj({
        "status": enum("actively_looking", "open", "not_looking", "passive_referrals_only"),
        "employmentTypes": arr(enum("full_time", "part_time", "contract", "contract_to_hire", "temporary", "freelance", "internship", "apprenticeship", "per_diem", "locum", "seasonal", "gig", "board", "advisory", "volunteer")),
        "workArrangements": arr(enum("onsite", "hybrid", "remote")),
        "locations": arr(S), "relocation": B, "travelPercentMax": {"type": "integer", "minimum": 0, "maximum": 100},
        "schedule": obj({"shifts": arr(enum("day", "evening", "night", "rotating", "split")), "weekends": B, "onCall": enum("none", "limited", "yes")}),
        "rates": arr(obj({"type": enum("hourly", "daily", "weekly", "monthly", "per_project", "per_mile"), "min": N, "currency": {"$ref": "#/$defs/currency"}, "employmentType": S}, ["type", "min", "currency"])),
        "seniority": arr(enum("entry", "mid", "senior", "lead", "principal", "manager", "director", "vp", "c_level", "board")),
        "industries": arr(CODE), "excludeEmployers": arr(S),
        "noticePeriod": S, "availableFrom": D}),
    "disclosure": obj({"audiences": {"type": "array", "items": S, "minItems": 1, "uniqueItems": True}, "default": S,
        "rules": arr(idref_rule), "never": arr(PTR), "selectiveDisclosure": enum("sd-jwt", "bbs", "none")}, ["audiences", "default"]),
    "commitments": {"type": "object", "required": ["handoff"],
        "properties": {"handoff": obj({"triggers": arr(S), "channel": U, "message": S, "sla": S}, ["channel"])},
        "additionalProperties": {"$ref": "#/$defs/commitment"}},
    "compliance": obj({
        "salaryHistory": enum("never", "handoff"),
        "criminalHistory": enum("never", "handoff"),
        "workAuthorization": enum("share", "handoff", "never"),
        "photo": enum("omit", "public", "audience-restricted"),
        "volunteer": arr(enum("age", "race_ethnicity", "national_origin", "religion", "sex", "gender_identity", "sexual_orientation", "family_status", "disability", "marital_status", "veteran_status", "union_membership", "political_views", "languages")),
        "dataRights": obj({"contact": U, "retentionDays": I, "erasureSupported": B}),
        "firstPerson": B}),
    "requesterPolicy": obj({"authentication": {"type": "object", "additionalProperties": arr(S)},
        "allowAgents": B, "allowHumans": B, "rateLimit": obj({"perRequesterPerDay": I}),
        "blockDomains": arr(S), "requireJobDescription": B}),
    "capabilities": arr({"allOf": [obj({"id": {"anyOf": [enum("answer", "fit_assessment", "tailor", "form_fill", "submit", "schedule", "reference_request", "job_search"), {"type": "string", "pattern": "^x-"}]},
            "enabled": B, "input": S, "output": arr(S), "requiresOwnerApproval": B}, ["id", "enabled"])],
        "if": {"properties": {"id": enum("submit", "reference_request"), "enabled": {"const": True}}, "required": ["id", "enabled"]},
        "then": {"required": ["requiresOwnerApproval"], "properties": {"requiresOwnerApproval": {"const": True}}}}),
    "interfaces": obj({"chat": U, "a2a": U, "mcp": obj({"url": U, "transport": S}, ["url"]), "jsonExport": U, "humanReadable": U}),
    "outputs": obj({
        "formats": arr(enum("docx", "pdf", "html", "md", "txt", "json-resume")),
        "default": obj({"format": enum("docx", "pdf", "html", "md", "txt", "json-resume"), "template": S, "view": {"type": ["string", "null"]}, "audience": S}),
        "templates": arr({"anyOf": [enum("ats", "modern", "academic-cv"), {"type": "string", "pattern": "^x-"}]}),
        "page": obj({"size": enum("letter", "a4"), "maxPages": {"type": ["integer", "null"], "minimum": 1}}),
        "sections": arr(enum("summary", "experience", "credentials", "skills", "profiles", "education", "languages")),
        "footer": S}),
    "audit": obj({"log": U, "retentionDays": I, "ownerVisible": B}),
    "meta": obj({"version": S, "lastModified": {"type": "string", "format": "date-time"},
        "signature": obj({"alg": S, "kid": S, "value": S}, ["alg", "value"])}),
  },
  "$defs": {
    "id": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"},
    "pointer": {"type": "string", "pattern": "^(/[^/]*)*$"},
    "assurance": enum("self_asserted", "documented", "verified"),
    "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
    "code": obj({"scheme": {"type": "string", "pattern": "^([a-z0-9-]+|x-.+)$"}, "code": S, "label": S}, ["scheme", "code"]),
    "metric": obj({"kind": {"anyOf": [enum("team_size", "direct_reports", "budget", "revenue", "cost_savings", "users", "customers", "transactions", "uptime", "latency", "patients", "beds", "caseload", "students", "publications", "citations", "grants_amount", "projects", "flight_hours", "apprenticeship_hours", "sales_quota_attainment", "aum", "nps", "safety_incidents"), {"type": "string", "pattern": "^x-"}]},
        "value": N, "unit": S, "currency": {"$ref": "#/$defs/currency"}, "period": S, "baseline": N, "asOf": D}, ["kind", "value"]),
    "commitment": commitment,
    "driversLicense": obj({"class": S, "endorsements": arr(S), "jurisdiction": S}),
    "creditRole": enum("conceptualization", "data_curation", "formal_analysis", "funding_acquisition", "investigation", "methodology", "project_administration", "resources", "software", "supervision", "validation", "visualization", "writing_original_draft", "writing_review_editing"),
  },
}

root = pathlib.Path(__file__).resolve().parent.parent
for out in (root / "schema" / "resume-agent.schema.json", root / "ora_tools" / "schema.json"):
    out.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n")
    print("wrote", out)

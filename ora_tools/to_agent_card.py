#!/usr/bin/env python3
"""Generate an A2A Agent Card (v1.0-style) from an ORA document.

Usage: python3 tools/to_agent_card.py examples/tech-executive.resume-agent.json > agent-card.json
Field names follow the A2A v1.0 AgentCard (name, description, version, provider,
supportedInterfaces, capabilities, defaultInputModes, defaultOutputModes, skills, securitySchemes).
Check the current A2A specification before production use.
"""
import json, sys

DESCRIPTIONS = {
    "answer": "Answers questions about the candidate's experience, grounded only in their ORA record.",
    "fit_assessment": "Assesses fit against a job description, with cited evidence and gaps.",
    "tailor": "Produces a role-tailored resume from the record without altering facts.",
    "form_fill": "Pre-fills application forms; the owner approves before anything is sent.",
    "submit": "Submits applications after explicit owner approval for each one.",
    "schedule": "Proposes interview times; the owner confirms.",
    "reference_request": "Coordinates reference requests with owner approval.",
    "job_search": "Finds roles matching the owner's preferences.",
}

def card(doc):
    owner = doc["owner"]["name"]
    ifs = doc.get("interfaces", {})
    base = ifs.get("chat") or ifs.get("a2a", "").replace("/.well-known/agent-card.json", "")
    views = [v["title"] for v in doc.get("roleViews", [])]
    skills = []
    for c in doc["capabilities"]:
        if not c["enabled"]: continue
        skills.append({
            "id": f"ora.{c['id']}",
            "name": c["id"].replace("_", " ").title(),
            "description": DESCRIPTIONS.get(c["id"], c["id"]),
            "tags": ["resume", "candidate", "ora"] + (["requires-owner-approval"] if c.get("requiresOwnerApproval") else []),
            "examples": views[:3] and [f"Is {owner} a fit for a {v} role?" for v in views[:2]] or [],
        })
    auth = doc.get("requesterPolicy", {}).get("authentication", {})
    schemes = {}
    if any("oauth2" in m for ms in auth.values() for m in ms):
        schemes["oauth2"] = {"type": "oauth2", "description": "Recruiter / employer authentication"}
    return {
        "name": f"{owner} — Resume Agent",
        "description": f"AI agent representing {owner}'s professional record under the Open Resume Agent spec. It is an AI, not the candidate.",
        "version": doc.get("meta", {}).get("version", "0"),
        "provider": {"organization": owner, "url": base or None},
        "supportedInterfaces": [{"url": base or "https://example.invalid/a2a", "protocolBinding": "JSONRPC", "protocolVersion": "1.0"}],
        "capabilities": {
            "streaming": False,
            "extensions": [{"uri": "https://openresumeagent.org/ext/v0.4", "description": "ORA document and rules",
                            "required": False, "params": {"document": ifs.get("jsonExport") or "/.well-known/resume-agent.json"}}],
        },
        "defaultInputModes": ["text/plain", "application/json"],
        "defaultOutputModes": ["text/plain", "application/json"],
        "skills": skills,
        "securitySchemes": schemes,
    }

if __name__ == "__main__":
    print(json.dumps(card(json.load(open(sys.argv[1]))), indent=2, ensure_ascii=False))

# RFC 0001: ORA's own résumé record

- **Author(s):** Sangamesh Hiremath (`sangameshh`)
- **Status:** accepted (18 November 2026). The founder, as sole maintainer, waived the 14-day comment period in GOVERNANCE.md; no other maintainers or implementers were affected
- **Affects:** SPEC §0, §1.2, §2, new §2.1, new §20.3 (rule O8) · schema · tools (`build_md`, `render`, `build_site`) · examples · conformance

## Summary
From v0.4, ORA defines the fields of its `resume` object itself (SPEC §2.1). The schema validates them, and JSON Resume becomes an export format (§20.3) rather than the base the spec extends. The field names and pointers stay as they are, and v0.2 and v0.3 documents stay valid.

## Motivation
ORA's goal is a specification for an AI agent that represents a person on any AI platform. The résumé data is one ingredient. Until v0.3, the spec said it "extends JSON Resume v1.0.0", but:

- The schema never checked the `resume` object. It was `{"type": "object"}`, so any shape passed, and pointers into it were checked only for existence.
- Disclosure rules (§7), claims (§4) and the agent file (§18) depend on a few named fields (`basics`, `work`, `education`, `certificates`). Their meaning was defined by a separate project that ORA doesn't govern.
- Saying ORA "extends" JSON Resume suggests ORA's work belongs in that project. It doesn't. ORA's subject is the agent's behaviour (truthfulness, disclosure, compliance, handoff), not résumé data.

Owning the record makes the conformance suite (L1) cover the data the agent speaks from. It also lets the format change without depending on another project, and states plainly what ORA is.

## Proposal
Normative text is in SPEC §2.1 (rules RR1–RR4) and §20.3 (rule O8). In short:

- **The `resume` object (v0.4)** holds `basics`, `work`, `education` and `certificates`, with the fields listed in §2.1. Unknown keys MUST be prefixed `x-`.
- **Dates** are ISO 8601 partial dates.
- **Facts that need assurance or audience rules** are claims that point into the record.
- **`resumeUrl`** MUST point to an ORA résumé record.
- **JSON Resume export (O8):** fields map by name; `x-` keys are dropped; the export follows O1–O7.

Schema diff, in `tools/build_schema.py`:
- a new `$defs/resume`;
- `if ora == "0.4" then resume: $ref #/$defs/resume`;
- `ora` gains `"0.4"`;
- `$id` is now `…/schema/v0.4/…`.

The v0.3 schema stays published at its `$id` (`schema/archive/`).

## Privacy and compliance impact
No audience, disclosure or jurisdiction rule changes. A stricter record removes a leak path. Today an arbitrary JSON Resume section, such as `references`, could carry personal data with no disclosure rule pointing at it, and the agent could repeat it (C1 allows facts "derived from the resume"). Under v0.4 such data has to be a claim or narrative, where audience rules apply, or an `x-` key that exports drop.

## Conformance
- New case `O8-json-resume-export` (public audience; the export must not contain the phone number or street address).
- New validator tests:
  - unknown section rejected;
  - `x-` section allowed;
  - unknown work field rejected;
  - work entry with neither name nor position rejected;
  - non-ISO date rejected;
  - a v0.3 document with a JSON Resume `interests` section still valid.
- New agent-file tests: export mapping drops `x-` keys; the build keeps the source's version.

## Alternatives considered
1. **Keep extending JSON Resume.** Leaves the record unvalidated and ORA's meaning dependent on another project.
2. **Make a Markdown template the source.** Readable, but disclosure pointers, schema validation and signatures (I2, RFC 8785) would depend on Markdown parsing, which differs between tools. The agent file (§18) is already Markdown, and that is where Markdown belongs.
3. **Rename the object** (for example `record`). Cleaner, but it breaks every `/resume/...` pointer for no gain in meaning.

## Backward compatibility
- Documents that declare `"ora": "0.2"` or `"0.3"` keep their JSON Resume object, validate as before, and build into agent files that keep their declared version.
- To move to v0.4:
  1. Set `"ora": "0.4"`.
  2. Keep `basics`, `work`, `education` and `certificates`.
  3. Move other sections into claims, narratives or profiles (RR3), or rename them with an `x-` prefix.
  4. Drop JSON Resume fields that §2.1 doesn't list, or rename them with an `x-` prefix.
- The five examples needed no changes beyond the version.

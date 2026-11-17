# ORA Industry Profiles v0.2

Each profile adds industry-specific fields under `profiles.<id>`. All fields are optional unless marked **req**. Profile data follows the core claim, disclosure and compliance rules (SPEC §9).

Each profile lists:
- **Fields**: what the profile adds
- **Expected credentials**: kinds validators warn about if missing (P2)
- **Sensitive by default**: fields that are non-public unless a disclosure rule says otherwise
- **Typical commitments**: topics the agent should hand off or set limits on
- **Where to verify**: the kind of primary source a verifier checks

---

## 1. `technology` — software, data, IT, security

| Field | Type | Notes |
|---|---|---|
| `stacks` | string[] | Languages and frameworks; link to `skills` ids where possible |
| `systemsScale` | object | `{ rps, dataVolume, users, regions }` |
| `onCall` | object | `{ experience: bool, maxRotation: "1-in-N" }` |
| `openSource` | object[] | `{ repo, role: maintainer\|contributor, evidence }` |
| `securityClearanceRequiredOk` | bool | Willing to obtain a clearance |
| `sfia` | object[] | `{ code, level 1–7 }` |

- **Expected credentials:** none
- **Sensitive by default:** employer names under NDA (C7)
- **Typical commitments:** IP assignment and moonlighting clauses go to handoff
- **Where to verify:** repos, package registries, cloud certification validation pages

## 2. `healthcare` — nursing, medicine, allied health, pharmacy

| Field | Type | Notes |
|---|---|---|
| `discipline` **req** | enum | `rn`, `lpn`, `aprn`, `physician`, `pa`, `pharmacist`, `therapist`, `technologist`, `paramedic`, `dentist`, `other` |
| `specialties` | string[] | e.g. Emergency, ICU, Oncology |
| `boardCertifications` | credential id[] | |
| `patientPopulations` | enum[] | `neonatal`, `pediatric`, `adult`, `geriatric` |
| `settings` | enum[] | `acute`, `ambulatory`, `long_term`, `home`, `telehealth`, `research` |
| `ehrSystems` | string[] | Epic, Cerner/Oracle Health, … |
| `procedures` | object[] | `{ name, count, period }` (counts only, no patient data) |
| `npi` | string | US provider id; non-public by default |
| `compactLicensure` | object | e.g. Nurse Licensure Compact multistate status |

- **Expected credentials:** `license`
- **Sensitive by default:** `npi`, license numbers, malpractice history (the agent never answers this, see J2)
- **Typical commitments:** shift type, float pool, on-call, per-diem and locum rates
- **Where to verify:** state boards of nursing and medicine, national nurse-licensure databases, specialty boards
- **Hard rule:** the agent MUST NOT include patient-identifying information in any answer, even if the owner put it in by mistake. Implementations SHOULD scrub it.

## 3. `academic` — research, faculty, postdoc, scientist

| Field | Type | Notes |
|---|---|---|
| `orcid` | string | `0000-0000-0000-0000` |
| `researchAreas` | string[] | |
| `publications` | object[] | `{ doi, title, venue, year, creditRoles: CRediT[], peerReviewed }` |
| `grants` | object[] | `{ funder, title, role: PI\|co-PI\|key_personnel, amount, currency, years }` |
| `teaching` | object[] | `{ course, level, years }` |
| `supervision` | object | `{ phd, masters, postdocs }` (counts) |
| `metrics` | object | `{ hIndex, citations, asOf, source }` |
| `tenureStatus` | enum | `tenured`, `tenure_track`, `non_tenure`, `n/a` |

- `creditRoles` use the 14 CRediT roles (ANSI/NISO Z39.104-2022), optionally with a `lead`, `equal` or `supporting` qualifier.
- **Expected credentials:** `degree`
- **Typical commitments:** start-up package, lab space and teaching load go to handoff
- **Where to verify:** ORCID, DOI resolvers, funder award databases

## 4. `legal` — lawyers, paralegals, compliance

| Field | Type | Notes |
|---|---|---|
| `barAdmissions` | credential id[] | One credential per jurisdiction |
| `practiceAreas` | string[] | |
| `matters` | object[] | `{ type, role, outcome, confidential: true }` (always anonymized) |
| `clerkships` | object[] | |
| `languagesForPractice` | string[] | |
| `conflictsCheckRequired` | bool | Default `true` |

- **Expected credentials:** `license` (bar admission) for attorneys
- **Sensitive by default:** every `matters` entry. The agent MUST NOT name clients or opposing parties.
- **Typical commitments:** book of business and portable clients go to handoff. Origination figures are restricted to `verified_employer`.
- **Where to verify:** state bar and law-society member directories

## 5. `finance` — banking, investment, accounting, insurance

| Field | Type | Notes |
|---|---|---|
| `registrations` | credential id[] | Securities exams and registrations, CPA, CFA, actuarial, insurance producer |
| `aum` | metric | Assets under management |
| `coverage` | string[] | Sectors and regions covered |
| `dealExperience` | object[] | `{ type, size, currency, role, year, confidential }` |
| `regulatoryHistory` | enum | Always `handoff`; the agent never characterizes it |

- **Expected credentials:** depends on role
- **Sensitive by default:** deal names, client names, compensation structure
- **Typical commitments:** non-solicit and garden leave go to handoff
- **Where to verify:** public broker and adviser registries, state accountancy boards

## 6. `aviation` — pilots, ATC, maintenance, cabin crew

| Field | Type | Notes |
|---|---|---|
| `certificates` | credential id[] | e.g. ATP, commercial, A&P mechanic, dispatcher |
| `ratings` | object[] | `{ type: type_rating\|instrument\|multi_engine, aircraft }` |
| `flightHours` | object | `{ total, pic, sic, multiEngine, turbine, instrument, night, crossCountry, asOf }` |
| `medicalClass` | enum | `first`, `second`, `third`, `none`. Health-adjacent, so owner-only by default (E1) unless volunteered. |
| `aircraftTypes` | string[] | |
| `operations` | enum[] | `part121`, `part135`, `part91`, `military`, `cargo`, `ga` |

- **Expected credentials:** `license` or `certification`
- **Typical commitments:** base or domicile, seniority and bidding, training bond
- **Where to verify:** civil aviation authority airmen registries

## 7. `trades` — electrical, plumbing, HVAC, welding, construction, manufacturing

| Field | Type | Notes |
|---|---|---|
| `trade` **req** | string | |
| `level` | enum | `apprentice`, `journeyman`, `master`, `foreman`, `superintendent` |
| `apprenticeship` | object | `{ program, hoursCompleted, hoursRequired, sponsor }` |
| `safetyCertifications` | credential id[] | e.g. OSHA 10/30, first aid, confined space |
| `equipment` | string[] | Machines and tools operated |
| `codes` | string[] | e.g. NEC 2023, IPC |
| `ownTools` | bool | |
| `driversLicense` | object | `{ class, endorsements, jurisdiction }` |
| `unionAffiliation` | object | Protected (E1); owner-only unless volunteered |

- **Expected credentials:** `license` for licensed trades
- **Typical commitments:** per diem, travel and prevailing-wage work
- **Where to verify:** state contractor and trade-licensing boards, apprenticeship registries

## 8. `education` — K-12, early childhood, tutoring, training

| Field | Type | Notes |
|---|---|---|
| `certifications` | credential id[] | Teaching licenses per jurisdiction |
| `gradeLevels` | string[] | |
| `subjects` | string[] | |
| `specialPopulations` | string[] | e.g. ELL, special education, gifted |
| `curricula` | string[] | e.g. IB, AP, Montessori |
| `backgroundClearance` | enum | Always `handoff` |

- **Expected credentials:** `license`
- **Where to verify:** state education department license lookups

## 9. `creative` — design, writing, media, arts, architecture

| Field | Type | Notes |
|---|---|---|
| `portfolio` | object[] | `{ title, url, role, year, client, rights: owned\|licensed\|nda\|work_for_hire, thumbnail }` |
| `tools` | string[] | |
| `awards` | object[] | |
| `credits` | object[] | Film, TV, game and publication credits: `{ title, role, year, verifiedSource }` |
| `unions` | object[] | Protected (E1); owner-only unless volunteered |

- **Hard rule:** items with `rights: nda` MUST NOT be shown or described beyond `role` and `year`.
- **Typical commitments:** day rate, usage rights, exclusivity
- **Where to verify:** credit databases, publisher pages, registered-architect lookups

## 10. `military` — service members and veterans

| Field | Type | Notes |
|---|---|---|
| `branch` | string | |
| `occupations` | object[] | `{ scheme: "moc", code, title, years }` |
| `civilianCrosswalk` | classification[] | e.g. from O\*NET military crosswalk |
| `rank` | string | |
| `clearance` | credential id | R3 applies |
| `transcripts` | evidence id[] | e.g. Joint Services Transcript |
| `dischargeType` | — | Not stored; never collected |

- `veteran_status` is protected (E1). Owners who want veteran-preference hiring opt in through `compliance.volunteer`.
- **Where to verify:** military-to-civilian credentialing portals, transcript services

## 11. `public_sector` — government, NGOs, international organizations

| Field | Type | Notes |
|---|---|---|
| `gradeHistory` | object[] | `{ system, grade, step, years }` (e.g. GS, P-levels) |
| `serviceType` | enum | `competitive`, `excepted`, `ses`, `foreign_service`, `ngo`, `igo` |
| `eligibility` | string[] | Hiring authorities claimed; **handoff** for proof |
| `clearance` | credential id | R3 applies |

- **Typical commitments:** citizenship requirement goes to handoff (work authorization, J-rules)

## 12. `sales` — sales, business development, customer success

| Field | Type | Notes |
|---|---|---|
| `quota` | object[] | `{ year, quota, attainment, currency }` (`sales_quota_attainment` metric) |
| `dealSize` | object | `{ avg, max, currency }` |
| `segments` | enum[] | `smb`, `mid_market`, `enterprise`, `strategic`, `public` |
| `motion` | enum[] | `inbound`, `outbound`, `channel`, `plg` |
| `territories` | string[] | |
| `crmTools` | string[] | |

- **Sensitive by default:** named accounts are `verified_employer`-only
- **Typical commitments:** OTE split and ramp go to handoff. Non-solicit goes to handoff.

## 13. `executive` — C-suite, VP, board, advisory

| Field | Type | Notes |
|---|---|---|
| `scope` | object | `{ orgSize, budget, pnl, revenue, currency, geographies }` |
| `boardSeats` | object[] | `{ org, role, committee, since }` |
| `transformations` | object[] | `{ type: turnaround\|IPO\|M&A\|scale-up\|digital, outcome, year }` |
| `investorFacing` | bool | |
| `reportingLine` | string | e.g. "CEO", "Board" |

- **Typical commitments:** equity, severance, change of control and D&O cover always go to handoff
- **Where to verify:** public filings, board pages

## 14. `hospitality_retail` — hotels, food service, retail, customer service

| Field | Type | Notes |
|---|---|---|
| `roles` | string[] | e.g. barista, line cook, shift lead, store manager |
| `foodSafety` | credential id[] | Food handler, manager certification |
| `posSystems` | string[] | |
| `volume` | object | `{ coversPerShift, storeRevenue, currency }` |
| `availability` | object | `{ days, hours, minHoursPerWeek, maxHoursPerWeek }` |

- **Typical commitments:** schedule changes, split shifts and tip policy

## 15. `logistics` — drivers, warehouse, supply chain

| Field | Type | Notes |
|---|---|---|
| `driversLicense` | object | `{ class: A\|B\|C\|…, endorsements: [H,N,P,S,T,X], jurisdiction }` |
| `safetyRecord` | — | Always `handoff`; never characterized by the agent |
| `equipment` | string[] | Forklift, reach truck, pallet jack |
| `routes` | enum[] | `local`, `regional`, `otr` |
| `systems` | string[] | WMS and TMS tools |
| `homeTimePreference` | string | |

- **Expected credentials:** `license` for drivers
- **Typical commitments:** drug testing consent, home time and pay basis (per mile or hourly)

---

## Combining profiles

An owner MAY use several profiles, e.g. `healthcare` + `academic` for a clinician-researcher, or `technology` + `executive` for a CTO. Role views (§8) then decide which profile leads for a given target role.

## Proposing a profile

Open a PR adding `profiles/<id>.schema.json`, a section in this file, an example under `examples/`, and at least three conformance cases.

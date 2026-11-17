---
layout: default
title: Registry
permalink: /registry/
---

# ORA Registry v0.2

Registered values. Anything not listed MUST be prefixed `x-`.

## Occupation schemes
| id | Name | Region |
|---|---|---|
| `onet-soc-2019` | O\*NET-SOC 2019 | US |
| `soc-2018` | Standard Occupational Classification 2018 | US |
| `isco-08` | International Standard Classification of Occupations | Global |
| `esco-occupation` | ESCO occupation URI | EU, multilingual |
| `noc-2021` | National Occupational Classification | CA |
| `anzsco` | ANZSCO | AU/NZ |
| `uk-soc-2020` | UK SOC 2020 | UK |
| `nco-2015` | National Classification of Occupations | IN |
| `moc` | Military occupation codes (MOS, AFSC, ratings) | US |

## Industry schemes
`naics-2022` (North America), `isic-4` (global), `nace-2` (EU)

## Skill schemes
| id | Name | Notes |
|---|---|---|
| `esco-skill` | ESCO skill URI | Multilingual; free API |
| `onet-element` | O\*NET content model element id | |
| `lightcast` | Lightcast Open Skills id | Free with attribution; check the license for commercial use |
| `sfia-9` | SFIA 9 skill code and level 1–7 | IT; licensed for commercial use |

## Evidence formats
`w3c-vc-2.0`, `w3c-vc-1.1`, `open-badges-3.0`, `clr-2.0`, `ler-rs`, `europass-edc`, `pdf`, `url`

## Selective disclosure
`sd-jwt`, `bbs`, `none`

## Contribution roles
`credit` — the 14 CRediT roles (ANSI/NISO Z39.104-2022): conceptualization, data_curation, formal_analysis, funding_acquisition, investigation, methodology, project_administration, resources, software, supervision, validation, visualization, writing_original_draft, writing_review_editing

## Audiences (default ladder)
`public` < `recruiter` < `verified_employer` < `owner`

## Profiles
`technology`, `healthcare`, `academic`, `legal`, `finance`, `aviation`, `trades`, `education`, `creative`, `military`, `public_sector`, `sales`, `executive`, `hospitality_retail`, `logistics`

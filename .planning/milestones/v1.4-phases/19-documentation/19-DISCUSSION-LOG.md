# Phase 19: Documentation - Discussion Log

> Audit trail. Decisions in CONTEXT.md.

**Date:** 2026-05-20  
**Mode:** `--auto --chain`

## Auto-selected decisions (7 gray areas)

| Area | Selection | Rationale |
|------|-----------|-----------|
| A. App README section placement | After Install Python, before Install Firmware | Natural alongside existing install instructions |
| B. Firmware README section placement | After pointer text, before License | Minimal addition to a minimal file |
| C. DOC-03 location | `.planning/v1.4-RELEASE-PROCEDURES.md` (meta-repo) | Cross-repo coordination doc |
| D. Procedures doc content | Verbatim copy of 15-LOCKSTEP-PROCEDURE.md + workflow_dispatch invocations + manual promotion path | Single source of truth for operator workflow |
| E. 15-LOCKSTEP-PROCEDURE.md fix | Replace `release.yml` → `beta-release.yml` in Step 4 | Phase 16 RESEARCH Open Q2 resolution |
| F. Stability wording | Explicit no-guarantees wording in both READMEs | Operator clarity |
| G. Issue reporting | GitHub Issues link + required fields in both READMEs | Reuse existing Issues; no new templates |

## Claude's Discretion

- D-10..D-13 — planner picks specifics
- D-11 recommends adding a Channel Selection Matrix (operator-friendly)
- D-13 recommends NO Mermaid diagram (rendering inconsistency)

## Deferred Ideas

- New issue templates (Future Requirements)
- Mermaid diagrams (rendering risk)
- Auto-promotion doc (workflow doesn't exist)
- Branch protection doc (rules don't exist)
- Signing doc (deferred)
- Metrics dashboard (Future Requirements)

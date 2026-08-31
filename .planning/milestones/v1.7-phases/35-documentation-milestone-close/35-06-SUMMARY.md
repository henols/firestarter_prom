---
phase: 35-documentation-milestone-close
plan: 06
status: complete
deviation: sub-repo commits land on `beta` (not `v1.7-shield-investigation`) — Plan 04 already merged + pushed both sub-repos to beta during the 3.0.0b5 lockstep cut; working tree was on beta when Plan 05/06 ran. Net effect identical (changes flow to main at Plan 09 close).
requirements-completed: [DOC-01]
key-files:
  created:
    - firestarter/doc/SHIELD-REVISIONS.md (5 sections: preamble + §1 inventory + §2 capability matrix + §3 alias table + §4 ADC band table + Full Investigation History footer)
    - .planning/phases/35-documentation-milestone-close/35-06-SUMMARY.md
  modified:
    - firestarter/README.md (added Shield Revision Support section)
    - firestarter/CLAUDE.md (added Hardware Revision Documentation subsection)
    - firestarter_app/README.md (added Shield Revision Detection section + EEPROM byte table)
    - firestarter_app/CLAUDE.md (extended Constants paragraph with SHIELD-REVISIONS.md lockstep clause)
    - firestarter (submodule pointer 9036b1d → 59a5e58)
    - firestarter_app (submodule pointer 1737939 → 00c19cd)
commits:
  - "firestarter 59a5e58 — docs(35-06): add doc/SHIELD-REVISIONS.md operator-facing canonical reference + README + CLAUDE.md sync rule (D-10)"
  - "firestarter_app 00c19cd — docs(35-06): README Shield Revision Detection section + CLAUDE.md sync rule extension (D-10)"
  - "meta 00aa5e3 — feat(35-06): bump submodules — sub-repo SHIELD-REVISIONS docs + sync rules (D-10)"
---

# Phase 35 Plan 06 — Sub-Repo Operator-Facing Canonical Doc + Sync Rules

**Created `firestarter/doc/SHIELD-REVISIONS.md` as the operator-facing canonical reference (subset clone of meta-repo §1+§6+§7+§9). Added Shield Revision sections to both sub-repo READMEs (cross-linked via relative + GitHub URL). Extended both sub-repo CLAUDE.md files with D-10 lockstep drift policy. Three commits across the three repos.**

## Section count in new sub-repo doc

`grep -c '^## ' /workspaces/firestarter/doc/SHIELD-REVISIONS.md` returns **5**:
1. `## 1. Inventory` (8-row table, all 8 known revs)
2. `## 2. Per-Rev Capability Matrix` (8-row table, chip families + voltage + protocol_ids per rev)
3. `## 3. Silkscreen → Code Alias Table` (17-row table, CTRL_/PIN_/RES_/JMP_ namespace lock)
4. `## 4. Per-Rev Expected ADC Band Table` (6-row table, post-Plan-01 INPUT high-Z semantics)
5. `## Full Investigation History` (footer pointer to meta-repo)

Plus the preamble (no `##` heading by design — 3-sentence operator orientation).

## Commit SHAs

```
firestarter      sub-repo: 59a5e58 (on beta)
firestarter_app  sub-repo: 00c19cd (on beta)
meta             repo:     00aa5e3 (on v1.7-shield-investigation)
```

All three branches will be reconciled at Plan 09 close (beta → main on both sub-repos; meta-repo merge to main).

## Phase 35 Plan 01 semantic correction in operator-facing doc

The §4 ADC Band Table in the new sub-repo doc carries the post-Plan-01 INPUT high-Z semantic interpretation:
- Stock Rev 2.0/2.1/2.2/2.3 (R41 to GND via JP4) → low band → `REVISION_2_0` (broad bucket) or `REVISION_2_3` via EEPROM override
- Modified Rev 0 (operator-attested 10k pull-up rework) → mid band → `REVISION_2_3`
- Pre-Rev2 (no R41) → high band → A2 disambig

Threshold-constant cross-link (mirrors `rurp_pinout.h:58-62`):
- `ADC_BAND_R41_4K7_HIGH = 200`
- `ADC_BAND_R41_10K_LOW  = 220`
- `ADC_BAND_R41_10K_HIGH = 600`

Wave 4 (Plan 07) and Wave 6/7/8 (Plans 08a/08b/09) consume this doc as the operator-canonical reference; sub-repo CLAUDE.md sync rules enforce drift-policy maintenance.

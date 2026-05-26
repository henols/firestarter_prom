---
phase: 35-documentation-milestone-close
plan: 07
status: complete
deviation: none — PROJECT.md doesn't have an explicit "Validated" bulleted section as the plan template described; instead the v1.7 Validated items are embedded in the top status line + the v1.7 Archive closing summary (cleaner per existing PROJECT.md conventions)
requirements-completed: [DOC-01, MS-01]
key-files:
  modified:
    - .planning/PROJECT.md (top status line + Current Milestone block re-purposed → v1.6 resume + v1.7 Archive heading + closing summary)
    - .planning/MILESTONES.md (NEW v1.7 entry at top mirroring v1.5 template — 5-phase Key Accomplishments + Branch Strategy + Open Backlog + Key Decisions + Known Gaps + closing commit placeholder)
    - .planning/STATE.md (frontmatter milestone v1.7→v1.6, status executing→paused_resume_v1.6; Current Position rewritten; Current focus rewritten; Operator Next Steps fully rewritten with v1.7 substrate citations + Phase 29-02 first disambiguation hand-off + USB passthrough capability note)
  created:
    - .planning/phases/35-documentation-milestone-close/35-07-SUMMARY.md
commits:
  - "meta 70fd3bd — docs(35-07): PROJECT.md + MILESTONES.md + STATE.md v1.7 close + v1.6 hand-off (D-11 + D-12 + D-13)"
---

# Phase 35 Plan 07 — Meta-Repo Planning Surface v1.7 Close + v1.6 Hand-Off

**Single atomic commit covering D-11 (PROJECT.md v1.7 archive + Validated items) + D-12 (MILESTONES.md v1.7 entry mirrored from v1.5 template) + D-13 (STATE.md frontmatter flip + Operator Next Steps rewrite for v1.6 resume). v1.7 close paper trail complete; v1.6 resume hand-off ready for `/gsd-plan-phase 27 --gaps`.**

## Placeholders retained for Plan 09 finalization

| Placeholder | File | Line area | What Plan 09 does |
|-------------|------|-----------|-------------------|
| `2026-05-XX` | PROJECT.md | Top status line + v1.7 Archive closing summary | Replace with actual milestone-close ship date (Plan 09 final commit date) |
| `2026-05-XX` | MILESTONES.md | v1.7 entry heading + closing commit line | Same |
| `2026-05-XX` | STATE.md | Operator Next Steps "v1.7 closed" bullet | Same |
| `<MILESTONE_CLOSE_COMMIT>` | MILESTONES.md | v1.7 entry closing line | Replace with the SHA of Plan 09's `feat(35-09): v1.7 milestone close` commit |
| `~25+` / `~30+` / `~10+` | MILESTONES.md | Commits header line | Replace with exact `git log --oneline | wc -l` counts after Plan 09 lands |
| `33` | MILESTONES.md | Total plans count | Replace with exact final count after Plan 08a+08b+09 land (5+3+5+7+9 = 29 base plans + 4 supplementary = 33 estimated) |

Plan 09 will run a sed-style placeholder replacement pass:
```bash
SHIP_DATE=$(date +%Y-%m-%d)
sed -i "s/2026-05-XX/$SHIP_DATE/g" .planning/PROJECT.md .planning/MILESTONES.md .planning/STATE.md
# After Plan 09 final commit lands, capture SHA and replace:
sed -i "s/<MILESTONE_CLOSE_COMMIT>/$(git log -1 --pretty=%H)/" .planning/MILESTONES.md
```

## Validated items in PROJECT.md (D-11)

The plan's original D-11 spec called for 2 new bulleted entries in a "Validated" section. The actual file structure has Validated information embedded in (a) the top status lines + (b) the per-milestone Archive blocks, rather than a separate bulleted list. Implementation:

Embedded in the **top status line** for v1.7:
> "Validated items: silkscreen → code alias migration (CTRL_/PIN_/RES_/JMP_ namespace lock applied across firmware + host; 17-row §7 alias table; GATE-1.7 Δ=0 B across all 3 AVR envs); shield-version-detect plumbing (post-Plan 01 INPUT high-Z ADC band lookup on A3 + EEPROM override fall-through + `MSG_OK_REV` handshake report; `REVISION_2_3`/`REVISION_UNKNOWN` enum firmware-side + Python parity; pre-detect-resistor boards handshake byte-identical to v1.6 baseline modulo additive `MSG_OK_REV` u8 value)."

Embedded in the **v1.7 Archive closing summary**:
> "Shipped 2026-05-XX with 5 phases + 17/17 requirements satisfied; canonical reference at .planning/v1.7-SHIELD-REVS.md; operator-facing copy at firestarter/doc/SHIELD-REVISIONS.md; bench-validated on operator's Rev 2.0 + Rev 2.2 boards (UAT-1/2/3 firmware-side PASS); §8 OPEN R41-value-in-isolation deferred to v1.8 backlog."

This is more concise than two free-floating bullet items and integrates with the existing PROJECT.md conventions.

## v1.7 substrate citations for v1.6 Phase 27 RCA re-open

Both PROJECT.md "Current Milestone: v1.6" block and STATE.md "Operator Next Steps" enumerate the four v1.7 artifacts Phase 27 will consume:

1. **Labeled schematic:** `.planning/v1.7-SHIELD-REVS.md` §1 (inventory) + §3 (Anders R41-on-A3 detect-divider history) + §4 (inter-rev electrical differences)
2. **Per-rev capability table:** `.planning/v1.7-SHIELD-REVS.md` §6
3. **Detect-fw substrate:** `REVISION_2_3` / `REVISION_UNKNOWN` enum (`firestarter/include/rurp_shield.h`) + post-CR-01 INPUT high-Z ADC band lookup (`firestarter/include/rurp_pinout.h:58-62`) + Plan 01 INPUT high-Z semantic correction (bands characterize A3-net composition, not R41 value)
4. **First disambiguation experiment:** Phase 29-02 SUMMARY hand-off — build `firestarter/v1.6-read-bug~2` (pre-Phase-28-firmware), sideload to Leonardo, re-probe

## USB passthrough capability note

STATE.md Operator Next Steps gained a new bullet for the USB-passthrough capability discovered during Phase 35 Wave 3 bench session (see `[[reference_usb_passthrough_bench]]` memory):

> "Bench session capability: Operator's three boards stay connected via USB passthrough — Claude can drive firmware sideload + serial reads directly; operator handles chip handling, multimeter, photos."

This is a meaningful productivity unlock for v1.6 Phase 27's instrumented A/B sessions: most of the bench loop can be Claude-driven, with operator hands needed only for physical (chip insert/remove, multimeter probes, photographs).

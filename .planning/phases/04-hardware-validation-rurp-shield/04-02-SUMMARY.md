---
plan: 04-02
phase: 04-hardware-validation-rurp-shield
wave: 2
requirements_addressed: []
requirements_attempted: [HW-02]
requirements_deferred: [HW-03, HW-04]
status: deferred
started: 2026-05-12T15:13Z
closed: 2026-05-12T20:35Z
session_duration: ~5h interactive bench
follow_ups_filed: 8
---

# Plan 04-02 Closure — Canon-Chip-Family Bench Batch — DEFERRED

## TL;DR

Plan 04-02 (HW-02 W27C512 + HW-03 AM29F040/SST39SF040 + HW-04 AT28C256) ran as a `/gsd-execute-phase 04 --wave 2 --interactive` session on 2026-05-12. **No §-section bench evidence was captured.** The session is closed as `status: deferred`, not `partial` or `complete`, because zero of the four planned bench runs produced a PASS or FAIL verdict — every attempt was blocked at the protocol layer before any chip programming could occur.

**Root cause:** a host-side bug in `firestarter_app`'s `EpromOperator` MAIN-phase data-send routine. The host emits a 4-byte data-packet header (`#` + 2-byte size + 1-byte checksum) but never sends the payload bytes that should follow. Firmware times out after 2 seconds and emits `ERROR: Data err -3`. The bug is universal across the `configure_eprom` dispatch family (algo=0x07/0x08/0x0B); confirmed identical failure mode on the canon W27C512 AND the D-12 substitute SST27SF512, against both pre-flash (2.0.6 git tag) and post-flash (source HEAD `587396a`, 30 commits ahead) firmware builds.

## What landed (vs. what didn't)

- ✓ **D-12 substitution decision** committed atomically as `f093643` ("docs(04-02): D-12 — partial-Wave-2 closure with in-family substitutes"). Plan-time substitution: SST27SF512 for §2 HW-02, SST39SF040 for §3a (sub for AM29F040) + §3b (canon), HW-04 deferred.
- ✓ **Bench session findings** appended to [04-HW-VALIDATION.md](04-HW-VALIDATION.md) as a new `## Bench Session 2026-05-12` H2 section, capturing the 11-step bench-attempt timeline + conclusive diagnosis.
- ✓ **8 follow_ups** populated in [04-HW-VALIDATION.md](04-HW-VALIDATION.md) frontmatter with severity classes (1 BLOCKER, 2 HIGH, 2 MEDIUM, 3 LOW).
- ✓ **10 raw bench-evidence logfiles + 1 readback binary** copied to [bench-evidence-2026-05-12/](bench-evidence-2026-05-12/) — diagnostic gold that should accelerate the host-bug fix.
- ✓ **Firmware reflashed mid-session** (`pio run -t upload -e uno`, [log 05](bench-evidence-2026-05-12/05-firmware_flash_to_587396a.log)): on-board binary advanced from 2.0.6-tag (`db4e565`) → source HEAD (`587396a`), bringing Phase 01 SAF-04+SAF-05 + Phase 02 wire-key rename + Phase 12 protocol-prefix dispatch onto the bench. Did NOT fix the host bug.
- ✗ **§2 HW-02 W27C512** — bench attempted, no evidence; chip remained blank after "100% write" (host stalled in MAIN phase).
- ✗ **§3a HW-03 chip-erase** — bench attempted on SST39SF040 substitute, chip is dead (chip-ID reads 0x0000, reads return all 0x00, "successful" erase doesn't blank the chip).
- ✗ **§3b HW-03 sector-erase** — never attempted; same dead-chip blocker as §3a.
- ✗ **§4 HW-04 AT28C256** — never attempted; deferred per D-12 (operator inventory had no AT28C256).
- ✗ **04-HW-VALIDATION.md §2/§3a/§3b/§4** — H2/H3 sections remain absent. No D-06 chip-header content authored.

## Bench-attempt summary

| Section | Canon | Attempted | Result | Why blocked |
|---------|-------|-----------|--------|-------------|
| §2 HW-02 | W27C512 | SST27SF512 (D-12) + W27C512 (canon) | FAIL × 2 | Host MAIN-phase bug — both chips, both firmware builds |
| §3a HW-03 ce | AM29F040 | SST39SF040 (D-12) | FAIL | Dead chip (chip-ID 0x0000, reads all 0x00) — bench question moot until chip replaced |
| §3b HW-03 se | SST39SF040 | (not reached) | DEFERRED | Same dead-chip blocker as §3a |
| §4 HW-04 | AT28C256 | (not reached) | DEFERRED | No AT28C256 in inventory (D-12 planning-time decision) |

Per-task atomic commits expected by Plan 04-02 `<verification>`: zero produced. No `docs(04-02): HW-NN bench run — ...` commits exist on this branch. The only Plan 04-02 commit is `f093643` (D-12) + this SUMMARY commit.

## Decisions consumed

- **D-06** per-chip evidence schema — honored only in spirit; no §-section actually authored.
- **D-07** failure triage — applied to every failure: SST27SF512 / W27C512 classified as **firmware-bug** class (host MAIN-phase bug), SST39SF040 classified as **chip-specific** class (dead chip). Neither was operator error.
- **D-08** atomic per-task commits — N/A (no per-task commits produced; the deferred session has one closure commit containing this SUMMARY + the bench-evidence and 04-HW-VALIDATION.md update).
- **D-10** bench-resume points — preserved by structure: 04-HW-VALIDATION.md §2/§3/§4 H2 sections remain blank, ready for future bench-resume.
- **D-12** partial-Wave-2 substitution — committed pre-bench, executed by the session, then proven INSUFFICIENT once the host MAIN-phase bug surfaced. D-12 remains in CONTEXT.md as the authoring-time intent record; the bench session shows it cannot execute until the host bug is fixed.

## Triage decisions (D-07)

Every chip + every operation hit a documented triage class:

- **SST27SF512 (host MAIN-phase bug)** → firmware-bug class. STOP, file requirement (`follow_up: host-main-phase-bug`, BLOCKER), do NOT in-line a fix during bench. ✓ Honored.
- **SST39SF040 (dead chip)** → chip-specific class. Document, substitute, or defer. Substituting requires another algo=0x06 chip not in operator's inventory; deferred (`follow_up: sst39sf040-dead-chip`, MEDIUM).
- **W27C512 (host MAIN-phase bug, identical to SST27SF512)** → firmware-bug class. Same follow-up; confirms universality of the bug.

## Cross-links

- HW-04 5V invariant evidence: pending bench session post-fix; cross-link to `13-VERIFICATION.md` (AT28C256 Phase 13 closure) reserved for the future §4.
- `flash_type_3.cpp:94-101` `flash3_erase_execute` discriminator: pending bench session for SST39SF040 / AM29F040 sector-erase variant; reserved for §3b.
- Firmware HEAD at session close: `firestarter@587396a` (flashed mid-session 2026-05-12T20:14Z).
- Host app HEAD at session close: `firestarter_app@16dcafe` (2.0.7_dev).

## Out-of-band notes

- **Zero source-tree modifications** in either `firestarter/` or `firestarter_app/` sub-repos — Plan 04-02 is verification-only bench work, no sub-repo writes were intended or produced.
- **Zero writes to `.planning/STATE.md` or `.planning/ROADMAP.md`** — orchestrator-owned per Phase 3 LEARNINGS surprise.
- **Bench-evidence directory created**: [bench-evidence-2026-05-12/](bench-evidence-2026-05-12/) — durable artifact under `.planning/`, not `/tmp/`. Plan 04-02 resume can re-read these logs to pick up exactly where this session left off.
- No photos captured (no §-sections to document).
- ROADMAP Phase 4 success criteria #2 / #3 / #4 all remain OPEN. Plan 04-03 (Wave 3 — HW-05 AM28F010 + SAF-04 abort) was not attempted in this session.

## What unblocks Plan 04-02 resumption (priority order)

1. **Fix the host MAIN-phase data-send bug** (`follow_up: host-main-phase-bug`, BLOCKER). Likely a single-file fix in `firestarter_app/firestarter/eprom_operations.py` or `serial_comm.py`. The verbose trace in [log 10](bench-evidence-2026-05-12/10-w27c512_write_data_err_-3_universal.log) shows the exact failure: line `DEBUG :SerialComm : 126: Sent 4 bytes` should be `Sent <header + payload> bytes`. Once fixed, Plan 04-02 §2 / §3a / §3b can attempt bench evidence with the chips already in inventory.
2. **Replace SST39SF040 chip** (or source AM29F040 as an in-family alternative). Both are algo=0x06 / `configure_flash3` and would discharge §3a + §3b after host-bug fix.
3. **Source AT28C256** for §4 HW-04 (Phase 13 5V invariant verification on real silicon).
4. **Bump `firestarter/include/version.h` VERSION** to break the firmware-drift confusion that obscured the v1.1 firmware updates during this session.

After #1 is fixed and at least the §2 chip path is clear, re-run:

```
/gsd-execute-phase 04 --wave 2 --interactive
```

The plan body remains untouched; D-12 substitution recipe remains in CONTEXT.md; bench-evidence directory carries the diagnostic continuity needed for resume. Plan 04-03 (Wave 3 — HW-05 AM28F010 abort + nominal contrast) is **independent** of the host bug only if HW-05 dispatches through a different firmware family — it dispatches through `configure_flash_intel` (algo=0x10), which the bench session did not exercise, so the bug may or may not affect it. Recommend confirming after host-fix lands.

## Hand-off

Plan 04-02 returns to incomplete state. Wave 2 of Phase 4 cannot close until the host MAIN-phase bug is fixed and at least one §3 chip is in hand. Plan 04-03 (Wave 3 — HW-05 AM28F010) may proceed independently if/when chip is sourced AND host bug behavior on algo=0x10 is confirmed.

**Next operator action**: file `host-main-phase-bug` against `firestarter_app` (verbose trace evidence in [bench-evidence-2026-05-12/10](bench-evidence-2026-05-12/10-w27c512_write_data_err_-3_universal.log)). Optionally run `/gsd-debug` on the host bug to systematically diagnose + fix in a focused session.

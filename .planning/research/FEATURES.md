# Feature Landscape — v1.14 Feasible-Gap Implementation

**Domain:** EPROM/Flash/EEPROM programmer — chip graduation milestone (4 chip groups → `supported`)
**Researched:** 2026-06-18
**Based on:** Required reading from PROJECT.md, ROADMAP.md, v1.13-PROTOCOL-ENUMERATION.md,
X88C64-FEASIBILITY.md, firestarter/doc/AT28C04-ADAPTER.md, MILESTONES.md §v1.13

---

## Summary

v1.14 is the first milestone since v1.0 in which chips actually graduate to `support_status: supported`
— becoming newly programmable. It implements four evidence-surfaced, RURP-feasible gaps that v1.13
deliberately scoped out. Each feature has a distinct acceptance shape:

| Feature | Chip group | Blocking dependency | Graduation path |
|---------|-----------|--------------------|----|
| 999.4 Erase write-path | 7 EE-EPROMs on 0x07 | Software-only (host `database.py`) | `write` auto-erases, verify clean |
| 999.5 X88C64 0x34 handler | 1 chip (X88C64P) | ALE routing confirmation + new firmware handler | `write`+`read` round-trip verified |
| 999.7 25V NMOS support | 4 `vpp-exceeds-max` chips | Operator multimeter dry-run confirming 25V VPP | ceiling raised, chips re-classified |
| 999.6 AT28C04/16 adapter | 9 `adapter-required` chips | Physical DIP24→DIP32 adapter built + seated | `write`+`read` via existing 0x0D handler |

---

## Table Stakes

Features users expect. Missing = the chip group is not "graduated to supported."

### Feature 1: `firestarter write -e W27C512` (or any 0x07 EE-EPROM) erases before programming

**Why expected:** W27C512, SST27VF512, W27E512, W27C257, SST27SF256, SST27SF512, SST27VF256 are
**electrically erasable EEPROMs** (`electrical.type == "EEPROM"`). A user writing one of these
chips to a different binary image today gets either a corrupt verify result or a chip full of
partly-overwritten cells, because the firmware never auto-erases. The `firestarter info` display
(since v1.11) correctly shows "Type: EEPROM" and "electrically erasable" — so the user has every
reason to expect `write` to handle erase automatically. Currently it does not.

**Observable acceptance (all must hold):**

1. `firestarter write -e W27C512 image.bin` (on a chip that has previously been programmed with
   different data) returns clean verify — SHA of read-back matches `image.bin`.
2. The same command does NOT require the user to pre-run `firestarter erase W27C512` manually.
3. Running `firestarter write -e W27C512` on a blank chip also succeeds (no spurious double-erase
   error; the erase path is a no-op when the chip is already blank — or at minimum produces no error
   when re-erasing a blank chip, which is electrically safe per the W27C512 datasheet).
4. `firestarter info W27C512` continues to show the correct "electrically erasable" display
   (already works; must not regress).
5. `check_dispatch.py` CI gate stays green after the change (`build_db.py` `FLAG_CAN_ERASE` now
   wired from `electrical.type == "EEPROM"` instead of the always-zero `info-flags & 0x10`).

**Complexity:** Low — the fix is two lines in `database.py:convert_to_programmer`. The
`eprom_internal_erase` electricals and the `eprom_write_init` FLAG_CAN_ERASE guard already exist
and are bench-proven (Phase 73 W27C512 Tier-3 PASS). The only open question is the
erase-rail setpoint: the W27C512 datasheet specifies VPP=14V for erase (vs 12V for write), still
under the 22V RURP ceiling. A chip-OUT multimeter dry-run must confirm the actual rail before
seating any chip.

**Source file:** `firestarter_app/firestarter/database.py:594-597` (change `info-flags & 0x10`
to `electrical.type == "EEPROM"`).

---

### Feature 2: `firestarter write -e X88C64P image.bin` writes and verifies correctly

**Why expected:** Once the 0x34 handler exists, the chip graduates from `protocol-not-implemented`
to `supported`. At that point `write` + `read` must produce byte-identical results within the
chip's 8K address space — that is the minimum bar for "programmable."

**Observable acceptance (all must hold):**

1. `firestarter write -e X88C64P image.bin` completes without error.
2. `firestarter read -e X88C64P out.bin` on the same chip produces a file byte-identical to
   `image.bin` (verified by SHA compare, or by `firestarter verify -e X88C64P image.bin` exiting 0).
3. `firestarter info X88C64P` shows `support_status: supported` (not `protocol-not-implemented`).
4. N>=5 trials on Leonardo produce the same result (confirms the toggle-bit polling is correct and
   not racing).
5. The existing `check_dispatch.py` CI gate accepts the chip under the new handler (no VPP pin, 5V
   only — same safety profile as the AT28C series).

**Complexity:** High — requires a new `configure_eeprom_x88c64()` firmware handler in a new
`eeprom_x88c64.cpp` source file, plus a `0x34` dispatch arm in `memory.cpp`. The handler must
implement the 8051-compatible ALE-latch + /WR-strobe write cycle (address-phase then data-phase on
the same 8 A/D pins) plus I/O6 toggle-bit polling. The critical open question (LOW-confidence
assumption A6 in X88C64-FEASIBILITY.md) is whether an existing RURP control-register bit can be
freely routed to toggle ALE without a PCB change. That question must be resolved before the handler
can be committed. Flash ceiling impact (89.5% at v1.13 close): each new handler adds 1-3 KB;
must confirm Leonardo stays under ~88% or justify a ceiling adjustment.

**Pre-condition for graduation:** ALE routing investigation completes with a positive finding
(a free CTRL_* bit available in `rurp_pinout.h`).

---

### Feature 3: `firestarter info M2716` (and M2732, ETC2716, ST M2716) shows `supported`; `firestarter write` works

**Why expected:** These four chips are NMOS UV-EPROMs that share protocol 0x07 (`configure_eprom`,
the same handler that programs M27C512 and similar 5V CMOS EPROMs already). Their only blocker is
VPP: they require 25V, while `RURP_VPP_CEILING_MV` is currently 22000. Raising the ceiling and
re-classifying them is the entire implementation. The M2732A (21V < 22V) is already `supported`
as a reference point — the four 25V chips are the same family, one voltage step higher.

**Observable acceptance (all must hold):**

1. `RURP_VPP_CEILING_MV` in `build_db.py` is raised from 22000 to 25000 (or 25500 for margin).
2. The four chips (INTEL M2716, INTEL M2732, SGS-THOMSON ETC2716, ST M2716) are re-classified
   from `support_status: vpp-exceeds-max` to `support_status: supported` in the regenerated
   `chip_database.json`.
3. `firestarter info INTEL_M2716` shows `support_status: supported` (no refusal message).
4. A chip-OUT VPP multimeter dry-run confirms the RURP shield physically produces >=25V VPP on the
   relevant shield revision **before any chip is seated** (operator measurement; mandatory gate).
5. A golden write + read-back verify on Leonardo with a physical M2716 (or M2732) chip confirms
   byte-identical result.
6. `check_dispatch.py` CI gate remains green at the new ceiling; `diff_db.py` shows only the four
   expected `support_status` changes.

**Complexity:** Low-to-medium — the ceiling change is a one-line constant; the re-classification
follows automatically from `build_db.py`. The risk is purely hardware: the ceiling was set at 22V
for a reason (it is the RURP-measured safe operating range, not an arbitrary constant). The operator
must verify via multimeter that the shield can physically produce 25V VPP before committing the
code change. Operator decision 2026-06-18: "do all four; implement 25V NMOS assuming hardware can
produce 25V" — this assumption must be validated by the dry-run gate before any chip is seated.

---

### Feature 4: `firestarter write -e AT28C16 image.bin` programs the chip via the DIP24->DIP32 adapter

**Why expected:** The `configure_eeprom28c` (0x0D) handler for these chips is already correct and
working (it handles AT28C256 and other 32-pin 5V EEPROMs). The adapter graduation removes the
host-guard refusal (`ChipNotImplementedError` from `chip_resolver.resolve_chip`) that currently
blocks all 9 AT28C04/AT28C16-family chips. Once the physical adapter exists and the guard is
removed, the existing handler programs them correctly.

**Observable acceptance (all must hold):**

1. The 9 `adapter-required` chips (AT28C04, AT28HC04, AT28C04E, AT28C04F, AT28C16, AT28HC16,
   AT28HC16L, AT28C16E, AT28C16F) are re-classified from `support_status: adapter-required` to
   `support_status: supported` in `chip_database.json`.
2. `firestarter write -e AT28C16 image.bin` (with the physical DIP24->DIP32 adapter installed in
   the RURP socket) completes without error.
3. `firestarter read -e AT28C16 out.bin` on the same chip produces a file byte-identical to
   `image.bin`.
4. The `ChipNotImplementedError` host-guard refusal in `chip_resolver.resolve_chip` is removed for
   these chips (by removing the `adapter-required` status check for 0x0D chips promoted to
   `supported`).
5. The VPP regulator is never engaged during the operation (5V-only; no VPP pin in either
   `DIP24_2816` or `DIP32_28C512_EEPROM` pinout — confirmed by `check_dispatch.py`).
6. AT28C04 specifically: writing an image of 512 bytes to a 512-byte chip succeeds (the firmware
   restricts address driving to 9 bits via `mem_size`; pins A9 and A10 are NC on the chip and
   float harmlessly).

**Complexity:** Low firmware (zero firmware changes needed — `configure_eeprom28c` already works).
Medium host (remove the host-guard for these chips in `chip_resolver.py`; update `build_db.py`
to reclassify `adapter-required` to `supported`). Hardware-blocked until the physical DIP24->DIP32
adapter is built per `firestarter/doc/AT28C04-ADAPTER.md`.

**Before the adapter exists:** The chip stays refused honestly (current behavior). `firestarter
info AT28C16` shows `support_status: adapter-required` with the existing reason string referencing
the adapter spec. No graduation code ships until the bench is ready.

---

## Differentiators

Features that set this milestone apart — not expected by users unfamiliar with the `support_status`
taxonomy, but demonstrably valuable once encountered.

### Differentiator 1: Honest "before adapter" state preserved until hardware exists

The AT28C16 graduation is hardware-gated. The existing `adapter-required` status + CLI message
pointing to the adapter spec (`firestarter/doc/AT28C04-ADAPTER.md`) is the correct user experience
until the adapter is built. This is better than silently failing or returning a generic error.
No temporary workaround code is needed; the refusal is informative and correct.

### Differentiator 2: 25V NMOS — verified-hardware ceiling, not blind constant

The ceiling raise to 25V is gated on an operator multimeter measurement, not just a constant change.
This means the code change is honest: it says the RURP can produce 25V because the operator
confirmed it can. Users of shield revisions that cannot produce 25V would get an honest refusal if
their hardware were re-characterized in the future.

### Differentiator 3: X88C64P page-write throughput

The X88C64P supports page writes of up to 32 bytes per internal write cycle. A correct implementation
exploits this, writing a full 8K image in 256 page-write cycles rather than 8192 byte-by-byte
cycles. This reduces write time substantially (EEPROM-class timing ~100 us per cycle x 256 = ~25 ms
total internal write time, vs. potentially seconds for byte-at-a-time).

---

## Anti-Features

Features to explicitly NOT build in v1.14.

### Anti-Feature 1: X88C64P STORE/RECALL operations

**What it is:** STORE (SRAM to EEPROM) and RECALL (EEPROM to SRAM) pin-activated operations from
the Xicor NovRAM family (X2210/X2212/X2201A, 1985 Xicor Data Book).

**Why explicitly out:** The X88C64P has NO STORE/RECALL pins — this is HIGH-confidence (surveyed
10 of 14 datasheet pages; no STORE/RECALL mention anywhere). STORE/RECALL belongs to a completely
different product line. The DB entry was labeled "XICOR NovRAM" misleadingly; this was corrected
by Phase 76 plan 76-01. Implementing STORE/RECALL for the X88C64P is physically impossible.

**What to do instead:** Implement the ALE/WR/RD byte+page write protocol from X88C64-FEASIBILITY.md
§3. Only the standard read/write EEPROM programming operations are in scope.

### Anti-Feature 2: 25V NMOS chips beyond the confirmed hardware ceiling

**What it is:** Raising the ceiling above the voltage the shield can physically produce to support
hypothetical chips needing 26V, 28V, or higher VPP.

**Why explicitly out:** The RURP ceiling is a hardware constraint. Chips with VPP beyond the
measured ceiling remain `vpp-exceeds-max` permanently. Only the four confirmed 25V chips (INTEL
M2716, INTEL M2732, SGS-THOMSON ETC2716, ST M2716) are in scope for v1.14.

**What to do instead:** Set ceiling at 25000 mV (or 25500 for margin) based on the multimeter
dry-run. Any chip requiring more than the confirmed ceiling stays refused.

### Anti-Feature 3: X88C64P handler without confirmed ALE routing

**What it is:** Committing a firmware 0x34 handler using creative workarounds for ALE (e.g.,
re-purposing an address line or data line momentarily as ALE).

**Why explicitly out:** Per X88C64-FEASIBILITY.md and Phase 76 D-01: "No blind handler." ALE
routing must be confirmed using a real, documented CTRL_* bit in `rurp_pinout.h` before any
handler is committed. Undocumented signal re-use creates hidden hardware coupling.

**What to do instead:** Investigate `rurp_pinout.h` CTRL_* bits first, before any code. If no
free bit exists, document the constraint and keep the chip as `protocol-not-implemented` (feasible-
candidate). Do not ship a handler that depends on undocumented signal multiplex.

### Anti-Feature 4: Graduating chips before hardware bench verification

**What it is:** Changing `support_status` in the DB from `adapter-required` or `vpp-exceeds-max`
to `supported` in code, before the corresponding hardware test is complete.

**Why explicitly out:** `support_status: supported` is a warranty that `firestarter write` produces
a correct, verifiable result. Graduating without bench evidence is dishonest and could cause silent
data corruption on real chips.

**What to do instead:** Gate each graduation on a golden write+read-back bench run on Leonardo,
per the standing bench precondition (live R1/R2 readback ~270000, chip-OUT before any Uno-class
sideload, shield rev confirmed by asking the operator, port identity verified at each task).

### Anti-Feature 5: Reopening the SRAM no-op question

**What it is:** Revisiting whether `configure_sram` is correct, having closed FIX-01 in v1.13.

**Why explicitly out:** FIX-01 was closed-with-evidence in v1.13 Phase 74: FM1608 FRAM two-pattern
bench PASS confirmed `configure_sram` correctly persists data via `memory_write_execute`. Relitigating
this wastes time and risks regressing working behavior.

**What to do instead:** Leave `configure_sram` exactly as it is.

---

## Feature Dependencies

```
999.4 (erase write-path)
  depends on: nothing (host-only; database.py change; standalone)
  enables: 7 EE-EPROMs (W27C512, W27E512, W27C257, W27E257, SST27SF256, SST27SF512,
           SST27VF256, SST27VF512) to be correctly re-programmed without manual pre-erase

999.5 (X88C64 0x34 handler)
  depends on: ALE routing investigation confirming a free CTRL_* bit (must pass before coding)
  depends on: flash ceiling headroom (89.5% post-v1.13; handler must keep Leonardo under ~88%)
  enables: 1 chip (X88C64P) graduates to supported

999.7 (25V NMOS ceiling raise)
  depends on: operator multimeter dry-run confirming >=25V VPP on the operator's shield rev
  enables: 4 chips (INTEL M2716, INTEL M2732, SGS-THOMSON ETC2716, ST M2716) graduate to supported

999.6 (AT28C04/16 adapter graduation)
  depends on: physical DIP24->DIP32 adapter built per firestarter/doc/AT28C04-ADAPTER.md
  depends on: golden bench write+read-back on Leonardo with a real chip in the adapter
  enables: 9 chips graduate to supported (zero firmware changes needed)

Build order (from PROJECT.md §v1.14): 999.4 -> 999.5 -> 999.7 -> 999.6
Rationale:
  999.4 is software-only and most ready (deferred from v1.13 Phase 75); sequence first
  999.5 requires the most firmware work and needs ALE investigation resolved; sequence second
  999.7 is a ceiling-raise + re-classification, hardware-confirmed; sequence third
  999.6 is hardware-blocked on the physical adapter; sequence last to avoid mid-milestone block
```

---

## MVP Recommendation

The minimal v1.14 that graduates any chips at all is **999.4 alone** — requires only a host-side
`database.py` change (2 lines), graduates 7 chips, is fully software-testable, and closes the most
user-visible gap (W27C512 silent write-without-erase). All other features require hardware.

Given the operator decision 2026-06-18 to "do all four," the recommended delivery sequence is:

1. **999.4 first** — software-only, ships early, de-risks the milestone
2. **999.7 second** — one constant + re-classification, hardware confirmation is the only gate
3. **999.5 third** — high complexity, ALE investigation is the critical path; do not rush
4. **999.6 last** — hardware-blocked; if adapter is not built, close the milestone without it

**Defer if blocked:**
- 999.5: If ALE routing investigation finds no free CTRL_* bit, defer to a future milestone;
  chip stays `protocol-not-implemented` (feasible-candidate documentation already correct).
- 999.6: If the adapter is not built, do not ship graduation without bench verification; carry
  to a future milestone rather than graduating without evidence.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| 999.4 erase path | W27C512 erase requires 14V VPP vs. 12V for write — must confirm rail before seating | chip-OUT multimeter dry-run; measure VPP at socket pins; record value in bench artifact |
| 999.4 erase path | A blank chip writes fine without auto-erase; non-blank chip may silently corrupt if erase fails partway | Post-erase blank verify (all-0xFF SHA) is mandatory acceptance criterion |
| 999.5 ALE routing | If no CTRL_* bit is free in `rurp_pinout.h`, the handler cannot ship without PCB changes | Make ALE routing investigation the FIRST plan in 999.5; no handler code before resolution |
| 999.5 flash budget | At 89.5% flash post-v1.13, a new handler could push Leonardo over the ceiling | Run `pio run -e leonardo` after each firmware addition; share utility functions if needed |
| 999.7 25V VPP | Shield may not produce 25V under load; open-circuit measurement is insufficient | Measure VPP at socket pins during a chip-OUT "dry run" with the VPP enable path active |
| 999.7 25V VPP | M2716 programming timing may differ from M27C512 despite both using `configure_eprom` | Verify `pulse_duration` in chip_database.json for all 4 chips against their datasheets |
| 999.6 adapter | A wiring error for /WE (chip pin 21 -> socket pin 30) makes chip non-writable but not damaged | Check adapter continuity with multimeter before seating any chip |
| All features | diff_db.py will flag support_status changes; must update pinned baseline after graduation | Run diff_db.py post-regeneration; confirm only expected chips changed; commit new baseline |

---

## Sources

All findings are grounded in the required reading listed at the top. No external web search was
needed — the v1.13 research and implementation artifacts provide authoritative, code-trace-verified
ground truth for every claim.

- `.planning/PROJECT.md §Current Milestone: v1.14` — scope, build order, operator decisions
- `.planning/ROADMAP.md §Phase 75 + §Phase 76` — original phase goals for the deferred items
- `.planning/v1.13-PROTOCOL-ENUMERATION.md` — gap index, anti-feature block, ceiling constraint
- `.planning/X88C64-FEASIBILITY.md` — interface architecture, write protocol, ALE open question
- `firestarter/doc/AT28C04-ADAPTER.md` — pin table, key /WE reroute, safety notes
- `.planning/MILESTONES.md §v1.13` — what was validated, what was deferred and why
- `firestarter_app/firestarter/database.py:594-597` — FLAG_CAN_ERASE current gating
- `firestarter/src/proms/eprom.cpp:100-106` — eprom_write_init FLAG_CAN_ERASE guard
- `firestarter/src/proms/eprom.cpp:274-288` — eprom_internal_erase electricals
- `firestarter_app/tools/build_db.py:117` — RURP_VPP_CEILING_MV = 22000

# Feature Research

**Domain:** EPROM/Flash/EEPROM/SRAM parallel-memory programmer — firmware algorithm validation + feasible-gap implementation (Firestarter v1.13)
**Researched:** 2026-06-16
**Confidence:** HIGH (firmware source + DB read directly; datasheet/protocol facts web-grounded; bench-feasibility verdicts grounded in fixed RURP constraints)

---

## Framing: validate vs implement vs infeasible

v1.13 is **test-first validation of already-built algorithm families, then evidence-driven gap implementation.** This document categorizes every candidate against three buckets:

- **Table Stakes = VALIDATE** — algorithm family code already exists and dispatches; the milestone must *prove it correct on hardware* (and fix bugs bench exposes). Missing this = the firmware is shipping unverified write paths.
- **Differentiators = IMPLEMENT** — a genuinely RURP-feasible (DIP parallel, fixed 5V VCC, VPP ≤ ~22V) operation/chip that is currently unimplemented or only partially wired. Each must carry a feasibility verdict + citation.
- **Anti-Features = KEEP REFUSED** — physically infeasible on RURP; already fail-closed by v1.12; must stay refused. No evidence-free "just add protocol X".

### RURP hardware constraints (the feasibility ruler — used for every verdict)

| Constraint | Value | Source |
|---|---|---|
| VCC | fixed 5V only | PROJECT.md "Out of Scope"; firmware has no VCC DAC |
| VPP ceiling | `RURP_VPP_CEILING_MV = 22000` (~22V; practically ~21V tested) | v1.12 DB-03 (`check_dispatch.py`) |
| Bus | DIP parallel, 19-bit address (512 KB), 8-bit data | PROJECT.md Key Decisions 2026-05-08 |
| Packages | DIP 24 / 28 / 32 only | PROJECT.md |
| No serial/LPC/SPI/I²C, no 3.3V rail, no ICSP | — | PROJECT.md; v1.12 infeasibility findings |

---

## Algorithm-family inventory (ground truth from firmware + DB)

744 chips. Support-status distribution (read from `chip_database.json` 2026-06-16): **supported 730**, **adapter-required 9**, **vpp-exceeds-max 4**, **protocol-not-implemented 1**. Algorithm handler map:

| Protocol | Family / handler | DB chips | CMD_WRITE | CMD_ERASE in firmware? | CMD_BLANK | CMD_CHECK_CHIP_ID | VPP |
|---|---|---|---|---|---|---|---|
| 0x07 EPROM_STD | `configure_eprom` | 170 | yes (retry+verify loop) | **YES** (`eprom_internal_erase`, A9+VPE 14V) | yes | yes (A9-12V) | 13V via VPE_DROP |
| 0x08 EPROM_QUICK | `configure_eprom` | 127 | yes (100µs pulse) | YES (same path) | yes | yes | 13V |
| 0x0B EPROM_LEGACY | `configure_eprom` | 26 | yes (500µs, direct VPE) | YES | yes | yes | 12–18V direct |
| 0x0D EEPROM_POLL | `configure_eeprom28c` | 84 (75 supported + 9 adapter) | yes (SDP-disable + 64B page + DQ7-wait) | **NO** (no CMD_ERASE case) | yes | yes (A9-12V) | none (5V) |
| 0x06 FLASH_AMD_ALT | `configure_flash3` | 190 | yes (unlock+verify DQ7) | YES (chip + sector erase) | yes | yes | none (5V) |
| 0x05 FLASH_AMD_STD | `configure_flash4` | 27 | yes (64B page + poll) | YES (12V-on-OE erase) | yes | **NO case** | none(write); 12V in erase |
| 0x35 FLASH_EEPROM | `configure_flash4` | (within 0x05/0x35) | yes | YES | yes | NO | none |
| 0x39 FLASH_EEPROM2 | `configure_flash4` | 2 | yes (by analogy; **0 chips historically — now 2**) | YES | yes | NO | none |
| 0x10 FLASH_INTEL | `configure_flash_intel` | 39 | yes (0x40 setup + SR poll) | YES (0x20/0xD0 + SR) | yes | yes (0x90) | 12V via P1 |
| 0x0E/0x27/0x28/0x29 SRAM | `configure_sram` | 20+34+... | **NO** (handler is a no-op stub) | n/a | n/a | n/a | none (5V) |
| 0x34 (52) XICOR | `configure_not_implemented` | 1 (X88C64) | refused (0xBB) | — | — | — | — |
| 0x11 / 0x2A / 0x2B / 0x2C | `configure_not_implemented` | 0 in DB | refused (0xBB) | — | — | — | — |

> **Two structural findings jump out of this table** and reshape the milestone (see Differentiators + Anti-Features):
> 1. `configure_sram` is an **empty no-op** — it logs and returns, setting *no* operation pointers. SRAM "support" is unproven and may be non-functional.
> 2. Several handlers **lack a `CMD_CHECK_CHIP_ID` case** (flash4) and one lacks `CMD_ERASE` (eeprom28c). The 0x39 "future-proofed, 0 chips" comment in CLAUDE.md is now **stale — the DB has 2 chips on 0x39**.

---

## Feature Landscape

### Table Stakes (VALIDATE — code exists, prove it on hardware)

Per-family hardware validation behind a reusable software-first **test harness + validation matrix** (the harness itself has no bench gate). Validation = write → read-back → byte-identical verify, plus erase/blank/chip-id where the family implements them.

| Feature (validate) | Why expected | Complexity | Notes / known-correctness risk |
|---|---|---|---|
| **Validation harness + matrix** (software) | Whole milestone hangs on it; reusable across families | MEDIUM | Build first, no bench gate; reuse `dev consistency-check` substrate; per-family per-op rows with PASS/FAIL/SKIP-with-reason |
| **UV-EPROM 0x07/0x08/0x0B write+verify** | Core product op; 323 chips | LOW (validate) | Retry loop *grows* `pulse_delay` up to 20× — confirm convergence; legacy 0x0B uses direct VPE (no drop resistor) — distinct VPP path worth its own row |
| **UV-EPROM 0x07 chip-ID (A9-12V)** | Identity gate before write | LOW | A9 driven to 12V; verify on real silicon (W27C512 chip-id `0xDA08`) |
| **5V EEPROM 0x0D write (SDP+page+DQ7)** | 84 chips incl. AT28C256 | MEDIUM | SDP-disable magic sequence (0x5555/0x2AAA); 64-byte page boundary; DQ7 readback-equality poll (2000×10µs ceiling). Validate page-cross + last-partial-page |
| **Flash AMD 0x06 write + sector/chip erase** | 190 chips — largest family | MEDIUM | Unlock 3-cycle; DQ7 toggle verify (double-read); `addr==0 → chip erase` else sector erase; 105 ms settle |
| **Flash type-4 0x05/0x35 page write** | 27+ chips | MEDIUM | 64-byte page poll (1024×10µs); erase drives **12V on OE** — VPP path on a nominally-5V family, validate carefully |
| **Flash Intel 0x10 write + erase (SR poll)** | 39 chips; 12V on P1 | MEDIUM | 0x40 program-setup; SR bit7 ready, bit4 VPP-error, bit3 program-error; `cleanup` resets to 0xFF read-array. Validate VPP-error + program-error branches |
| **Blank check (all families)** | Pre-write safety + standalone op | LOW | Shared `mem_util_blank_check`; stateful 2KB-per-call progression (the flash3 re-entrancy bug history) |
| **Read path (all families)** | Foundational | LOW | NOTE: large-read jitter on some shields is the **separate deferred v1.9 RCA** — validate on Leonardo/EVEN-01 clean board only; do NOT couple v1.13 to it |

**Bench gating:** validate the families for which the operator has chips + a working shield; defer families lacking parts with an explicit SKIP-with-reason row. Milestone is closeable without 100% family coverage (PROJECT.md "hybrid bench gating").

### Differentiators (IMPLEMENT — genuine RURP-feasible gaps with feasibility verdicts)

| Feature (implement) | Feasibility verdict | Evidence / citation | Complexity | Notes |
|---|---|---|---|---|
| **`firestarter erase W27C512` end-to-end (0x07 electrically-erasable EEPROMs)** | **FEASIBLE — firmware already implements the erase electricals; the gap is host-side wiring + a voltage detail** | W27C512 erase mode = OE/VPP→**14V**, A9→**14V**, VCC=5V, A0 low, all other A low, all DQ high, 100 ms ([Winbond W27C512 datasheet](https://www.dosdays.co.uk/media/winbond/W27C512_Datasheet.pdf)). `eprom_internal_erase` (eprom.cpp:274) already asserts `CTRL_VPP_A9_ENABLE \| CTRL_VPE_ENABLE` with regulator on — electrically the correct sequence. | MEDIUM | **GAP DETAIL:** (1) Host must set `FLAG_CAN_ERASE` / route `erase` to these chips. `FLAG_CAN_ERASE` is derived from info-flag bit 0x10 "electrically erasable" (database.py:594) — verify it is set for W27C512 (DB `type:"EEPROM"`, has the bit). (2) **Voltage mismatch:** DB lists `vpp 12V` but erase needs **14V**; `eprom_internal_erase` runs the regulator *without* the drop resistor (so it outputs the raw VPE rail), but the rail target/ceiling for 14V must be confirmed against `RURP_VPP_CEILING_MV=22000` (OK) and the actual regulator setpoint. (3) The erase does NOT set A0-low / all-DQ-high explicitly — validate the chip still bulk-erases, or add the datasheet preconditions. This is the milestone's flagship "deferred erase path resurfaces via research" item (PROJECT.md). |
| **`configure_sram` real read/write (0x0E/0x27/0x28/0x29)** | **FEASIBLE — pure 5V parallel SRAM is trivially in-scope; handler is currently a no-op** | `sram.cpp` `configure_sram` sets no operation pointers (logs + returns). 20 chips on 0x0E alone (plus 0x27/0x28/0x29). SRAM is 5V, DIP parallel, no VPP. | LOW–MEDIUM | Either the generic state-machine default already covers plain read/write (validate!) or these chips silently no-op on write. **Must validate first** — this is a "validate, and if broken, implement" hybrid. Battery-backed NVRAM (e.g. DS1220/FM1608) writes via the same SRAM path. If a write command reaching a no-op handler returns success without writing, that is a **correctness bug worth a fix**. |
| **X88C64 (0x34 XICOR parallel NOVRAM/EEPROM, 24-pin DIP, 5V)** | **MAYBE-FEASIBLE — re-classify; currently the *only* `protocol-not-implemented` chip and it is NOT GAL/PLD/serial** | X88C64 = 8K×8 **parallel 5V 24-pin DIP** EEPROM/NOVRAM ([Elnec X88C64](https://www.elnec.com/en/device/Xicor/X88C64/); [eBay X88C64PI 24-pin DIP 5V](https://www.ebay.com/p/663635561)). Unlike 0x11/0x2A-0x2C, this is a parallel DIP memory — physically drivable. | MEDIUM–HIGH | v1.12 lumped 0x34 into "not implemented" but it is **categorically different** from the GAL/PLD/FWH infeasibles: it is a parallel 5V DIP memory. Gap = a 0x34 algorithm handler (NOVRAM has STORE/RECALL software sequences + standard 28C-like byte/page write). **Verdict pending datasheet of the exact write protocol**; do NOT promise — flag as "investigate protocol 0x34, likely feasible, needs algorithm spec." Pin-mapping caveat identical to the 24-pin EEPROM adapter issue below. |
| **9× AT28C04/AT28C16 24-pin EEPROMs (adapter-required, 0x0D)** | **FEASIBLE *only with a physical DIP24 adapter* — firmware handler already exists** | `unsupported_reason`: "socket pin 21 = WE, which the RURP DIP24_2716 pinout maps to the 12V VPP rail (hardware-damage path)". `configure_eeprom28c` (0x0D) already programs these electrically; the blocker is pin-mapping, not protocol. | MEDIUM (hardware-dependent) | **Adapter mapping needed:** a DIP24 socket adapter that re-routes socket pin 21 from RURP's VPP-rail line to WE, and aligns the AT28C04/16 pinout to a RURP bus the firmware can drive (it is a 28C-family EEPROM → 0x0D handler). PROJECT.md explicitly lists "adapter-required chip support" as a v1.13 target, gated on *having/making* the adapter. Deliverable = adapter pin-map spec (extend `firestarter info --adapter`) + a `DIP24` pinout entry; bench-validate once adapter exists. |
| **Flash type-4 (0x05/0x35) `CMD_CHECK_CHIP_ID`** | **FEASIBLE — trivial; missing handler case** | `configure_flash4` switch (flash_type_4.cpp:27) has no `CMD_CHECK_CHIP_ID` case → autoselect ID unavailable for 27+0x35 chips. AMD-style autoselect (0xAA/0x55/0x90) is standard. | LOW | Small firmware add; mirror `flash3_check_chip_id_execute`. Worth doing so identity-gating works for the flash4 family like every other family. |
| **0x39 family validation (2 chips, comment says 0)** | **FEASIBLE — already dispatched; just stale doc + unvalidated** | DB now has **2 chips on algo 0x39**; CLAUDE.md says "0 chips, future-proofed". Routes to `configure_flash4`. | LOW | Validate the 2 real chips on the 0x39→flash4 path; update the stale "0 chips" comment. Cheap correctness win surfaced by the DB read. |

### Anti-Features (KEEP REFUSED — infeasible on RURP; stay fail-closed)

| Feature | Why requested | Why infeasible on RURP | Correct behavior |
|---|---|---|---|
| FWH/LPC flash (0x11) | Appears in minipro DB | LPC serial interface + 3.3V rail; RURP is parallel + fixed 5V | Keep `configure_not_implemented` (0xBB) — v1.12 DISP-04 |
| GAL/PLD (0x2A/0x2B/0x2C) | "It's a DIP chip" | Logic devices, not memory; need JEDEC fuse-map programming + non-memory pin protocols; many need >22V or special algorithms | Keep refused; not memory at all |
| NMOS 2716/2732/M2716 (0x00, **vpp-exceeds-max**) | Classic EPROMs people own | Require **25V** VPP; `RURP_VPP_CEILING_MV=22000` | Keep `vpp-exceeds-max` refusal. **NOTE:** M2732A=21V is `supported` (under ceiling) — boundary already correct. Do not relax the ceiling. |
| MCU / SMD-only / serial SPI-I²C EEPROM | minipro covers them | No ICSP, no SMD socket, no serial bus on RURP | Stay skipped/refused |
| 6.5V VCC NMOS programming | Some NMOS parts want 6V VCC | RURP VCC fixed at 5V (no VCC DAC) | Out of scope per PROJECT.md |

---

## Feature Dependencies

```
[Validation harness + matrix]  (software, build FIRST, no bench gate)
        └──enables──> [Per-family hardware validation rows]
                            └──exposes──> [Per-family correctness fixes]

[SRAM validation] ──may-promote-to──> [configure_sram real read/write IMPLEMENT]
                            (no-op handler: validate decides validate-vs-implement)

[erase W27C512 host wiring] ──requires──> [FLAG_CAN_ERASE set + 14V rail confirm]
        (firmware erase electricals already exist — eprom_internal_erase)

[AT28C04/16 24-pin support] ──requires──> [physical DIP24 adapter + DIP24 pinout entry]
        └──requires──> [adapter pin-map spec / firestarter info --adapter]
        (firmware 0x0D handler already correct — pure mapping/hardware dependency)

[X88C64 0x34 support] ──requires──> [0x34 algorithm spec from datasheet]
        └──then──> [new firmware handler] ──maybe-requires──> [DIP24 adapter]

[flash4 CMD_CHECK_CHIP_ID] ──independent, LOW──> (mirror flash3)
[0x39 stale-comment + 2-chip validation] ──independent, LOW──>

[v1.9 read-bug RCA] ──CONFLICTS / DECOUPLED──> [v1.13 read validation]
        (validate reads on clean Leonardo/EVEN-01 only; do not couple)
```

### Dependency notes

- **Harness precedes everything.** It is the only un-gated deliverable and the spine of the milestone; build and land it before any bench session.
- **SRAM is a validate→maybe-implement fork.** The no-op `configure_sram` means a write may silently succeed-without-writing. Validation determines whether SRAM moves from Table Stakes (works via generic path) to Differentiator (needs a real handler). This must be resolved early because 20+ chips claim support.
- **erase W27C512 is mostly host-side.** The firmware electricals exist; the gap is `FLAG_CAN_ERASE` routing + the 12V→14V rail detail + datasheet preconditions. This is the lowest-risk Differentiator and the explicit "deferred erase path resurfaces" item.
- **Adapter-required and X88C64 are hardware/spec-gated.** Both depend on artifacts the operator must supply (a physical adapter; a datasheet protocol). Plan them as bench-gated/research-gated, not autonomous.
- **Decouple from v1.9.** The shield-fleet read-bug RCA is a separate deferred milestone; v1.13 must validate reads on the trustworthy board only (Leonardo/EVEN-01) to avoid importing that confound.

---

## MVP Definition (v1.13)

### Launch With (core of the milestone)

- [ ] **Validation harness + matrix (software)** — essential; everything else reports through it.
- [ ] **Validate UV-EPROM 0x07/0x08/0x0B write+verify+chip-id** on bench (W27C512 etc., Leonardo) — the product's core path.
- [ ] **Validate 5V EEPROM 0x0D (SDP+page+DQ7)** — 84 chips, AT28C256 representative.
- [ ] **Validate Flash AMD 0x06 write+erase** — largest family (190).
- [ ] **Resolve SRAM no-op question** — validate the 0x0E/0x27/0x28/0x29 path; if it silently no-ops on write, classify as a correctness bug.
- [ ] **`firestarter erase W27C512` host wiring + 14V confirm** — the flagship feasible gap; firmware electricals already exist.
- [ ] **Re-research write-up** — formally re-enumerate feasible-but-unimplemented (this document feeds it): SRAM no-op, X88C64 0x34, flash4 chip-id, 0x39 stale comment.

### Add After Validation (within v1.13 if bench/parts allow)

- [ ] **Flash type-4 0x05/0x35 validation** + **add `CMD_CHECK_CHIP_ID` case** — trigger: chips on hand.
- [ ] **Flash Intel 0x10 validation** (12V P1; SR error branches) — trigger: a 28F-series chip on hand.
- [ ] **Per-family correctness fixes** bench exposes — trigger: any FAIL row.
- [ ] **0x39 2-chip validation + comment fix** — cheap, do alongside flash4.

### Future Consideration (defer — hardware/spec dependent)

- [ ] **AT28C04/AT28C16 24-pin support** — defer until a DIP24 adapter exists; deliver the adapter pin-map spec now, bench-validate later.
- [ ] **X88C64 0x34 handler** — defer until the 0x34 write/STORE-RECALL protocol is spec'd from datasheet; do not promise feasibility blind.

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---|---|---|---|
| Validation harness + matrix | HIGH | MEDIUM | P1 |
| UV-EPROM 0x07/08/0B validation | HIGH | LOW | P1 |
| 5V EEPROM 0x0D validation | HIGH | MEDIUM | P1 |
| Flash AMD 0x06 validation | HIGH | MEDIUM | P1 |
| SRAM no-op resolution (validate→maybe-implement) | HIGH | LOW–MEDIUM | P1 |
| `erase W27C512` host wiring + 14V | HIGH | MEDIUM | P1 |
| Re-research write-up (this doc → requirements) | HIGH | LOW | P1 |
| Flash type-4 0x05/0x35 validation + chip-id case | MEDIUM | LOW–MEDIUM | P2 |
| Flash Intel 0x10 validation | MEDIUM | MEDIUM | P2 |
| Per-family correctness fixes | HIGH | varies | P2 (triggered) |
| 0x39 2-chip validation + stale comment | LOW | LOW | P2 |
| AT28C04/16 24-pin adapter support | MEDIUM | MEDIUM (HW-gated) | P3 |
| X88C64 0x34 handler | LOW–MEDIUM | HIGH (spec-gated) | P3 |
| Keep 0x11/0x2A-0x2C/25V refused | — (safety) | none | P1 (invariant) |

**Priority key:** P1 = milestone core; P2 = add when bench/parts allow; P3 = future / hardware-or-spec gated.

---

## Re-examination verdict: does v1.12's "feasible set is complete" hold?

**Partially — it overstated completeness.** v1.12 concluded "every RURP-feasible DIP parallel-memory protocol already has a handler." That is true for the *protocol-dispatch framework* but glosses three real gaps that this milestone exists to surface:

1. **`configure_sram` is a no-op stub.** SRAM/NVRAM "support" (20+ chips on 0x0E plus 0x27/0x28/0x29) is dispatched to an empty function. Either the generic path covers it (validate) or write silently does nothing (implement). v1.12 counted these as "supported."
2. **X88C64 (0x34) is mis-bucketed as infeasible.** It is a **parallel 5V 24-pin DIP** EEPROM/NOVRAM — categorically unlike the genuinely-infeasible 0x11/0x2A-0x2C. It is the single `protocol-not-implemented` chip and is plausibly feasible with a new handler.
3. **The erase path was explicitly deferred, not absent.** Firmware *has* the 0x07 erase electricals; the host never wires `erase` to electrically-erasable EEPROMs. v1.12 listed this as out-of-scope backlog; v1.13 promotes it.

Everything else v1.12 refused (FWH 0x11, GAL/PLD 0x2A-0x2C, 25V NMOS, serial/SMD/MCU) **remains correctly infeasible** — those verdicts hold and must stay fail-closed.

---

## Competitor / prior-art Feature Analysis

| Feature | minipro (TL866) | Arduino parallel-EEPROM libs | Firestarter (our approach) |
|---|---|---|---|
| Protocol coverage | Full XML DB incl. serial/PLD/MCU via dedicated HW | 28C/X28 byte+page only ([Andy4495/ParallelEEPROM](https://github.com/Andy4495/ParallelEEPROM)) | DIP-parallel memory subset; fail-closed on the rest |
| Erase EE-EPROM (W27C512) | Yes (special erase algorithm) | n/a (UV parts) | **Gap to implement** — electricals exist, host wiring missing |
| SRAM/NVRAM write | Yes | Yes (it's just SRAM) | **No-op stub — validate/implement** |
| 24-pin AT28C04/16 | Yes (adapter/socket) | Yes (direct wiring) | **Adapter-required** — needs DIP24 adapter |
| X88C64 NOVRAM | Yes (Elnec/BPM support it) | rare | **0x34 unimplemented — re-classify as feasible candidate** |
| Capability honesty | silent on unsupported | n/a | fail-closed + `support_status` (v1.12) — keep |

---

## Sources

- Firmware source (read directly): `firestarter/src/proms/{eprom,eeprom_28c,flash_type_3,flash_type_4,flash_intel,sram,flash_utils,not_implemented,memory}.cpp` — handler/erase/chip-id presence, no-op SRAM, dispatch chain
- `firestarter_app/firestarter/data/chip_database.json` — 744-chip support_status + algorithm distribution (read 2026-06-16)
- `firestarter_app/firestarter/database.py:594` — `FLAG_CAN_ERASE` derivation from info-flag bit 0x10
- `.planning/PROJECT.md` — v1.13 milestone scope, RURP constraints, hybrid bench gating, deferred erase path
- `.planning/milestones/v1.12-REQUIREMENTS.md` — v1.12 feasibility conclusion + support_status taxonomy + out-of-scope erase/adapter items
- `.planning/research/SUMMARY.md` (v1.12) — prior infeasibility reasoning
- [Winbond W27C512 datasheet (dosdays mirror)](https://www.dosdays.co.uk/media/winbond/W27C512_Datasheet.pdf) — erase mode: OE/VPP=14V, A9=14V, 5V VCC, 100 ms
- [W27C512 datasheet (alldatasheet)](https://www.alldatasheet.com/datasheet-pdf/pdf/47653/WINBOND/W27C512.html) — +14V erase / +12V program, electrically erasable
- [Elnec — Xicor X88C64 device support](https://www.elnec.com/en/device/Xicor/X88C64/) — X88C64 supported, adapter modules
- [eBay — X88C64PI 8K×8 5V 24-pin DIP](https://www.ebay.com/p/663635561) — confirms parallel 5V 24-pin DIP package
- [Andy4495/ParallelEEPROM (Arduino lib)](https://github.com/Andy4495/ParallelEEPROM) — prior-art for 28C256/X28256/28C16 parallel programming

---
*Feature research for: Firestarter v1.13 — Programming Algorithm Validation + Gap Implementation*
*Researched: 2026-06-16*

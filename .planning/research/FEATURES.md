# Feature Research: v1.12 Protocol-Gap Enumeration

**Domain:** Firmware protocol dispatch hardening — Firestarter EPROM programmer (Arduino / RURP shield)
**Researched:** 2026-06-10
**Confidence:** HIGH

**Primary source:** minipro `database.h` IC2_ALG_* constants @ commit `a8efaedc236c1d9718bd28299dfbb99536b010ff`; confirmed against `infoic-field-dictionary.md` (v1.11 canonical) and `protocol-id.md` (v1.11 corrected docs); `build_db.py` KNOWN_PROTOCOLS + filter logic; `firestarter/CLAUDE.md` dispatch table.

---

## The Central Research Deliverable: Protocol-Gap Enumeration

The full IC2_ALG_* constant space from `database.h#L24–L77` spans `0x00`–`0x35` (54 named constants). Below is every ID classified into exactly one of three buckets:

- **IMPLEMENTED** — firmware has a real handler registered in `configure_memory()`'s protocol-prefix chain.
- **SKELETON-NEEDED** — a DIP parallel-memory protocol the RURP shield could physically drive but firmware does NOT implement; gets a stub handler this milestone.
- **INFEASIBLE-ON-RURP** — serial bus / non-parallel / 3.3V-only / PLD / MCU / no-DIP-memory-chips; explicitly out of scope with reason.

---

### Full Protocol-ID Classification Table

| protocol_id | IC2_ALG Constant    | Memory Family / Behavior                            | Chips in DB (approx.) | DIP parallel? | RURP-feasible? | Bucket | Rationale |
|-------------|---------------------|-----------------------------------------------------|-----------------------|---------------|----------------|--------|-----------|
| `0x00`      | `IC2_ALG_NONE`      | Null / no algorithm                                 | 0                     | N/A           | N/A            | **INFEASIBLE-ON-RURP** | No chips; null sentinel — not a real programming algorithm |
| `0x01`      | `IC2_ALG_IIC24C`    | I2C serial EEPROM (24Cxx family)                    | 0 in DIP filter       | NO — serial   | NO             | **INFEASIBLE-ON-RURP** | 2-wire I2C serial bus; RURP has no I2C interface; `is_serial != 0` excludes all chips before KNOWN_PROTOCOLS check |
| `0x02`      | `IC2_ALG_MW93ALG`   | Microwire serial EEPROM (93xx family)               | 0 in DIP filter       | NO — serial   | NO             | **INFEASIBLE-ON-RURP** | 3-wire Microwire serial bus; excluded by `is_serial != 0` filter |
| `0x03`      | `IC2_ALG_SPI25F_1`  | SPI NOR Flash (25-series, variant 1)                | 0 in DIP filter       | NO — serial   | NO             | **INFEASIBLE-ON-RURP** | 4-wire SPI serial bus; excluded by `is_serial != 0` filter |
| `0x04`      | `IC2_ALG_AT45D`     | Atmel DataFlash (AT45D SPI)                         | 0 in DIP filter       | NO — serial   | NO             | **INFEASIBLE-ON-RURP** | SPI serial bus; excluded by `is_serial != 0` filter |
| `0x05`      | `IC2_ALG_F29EE`     | AMD/Fujitsu 5V page-write flash (F29EE type)        | ~15                   | YES           | YES            | **IMPLEMENTED** | `configure_flash4()` handler; registered in KNOWN_PROTOCOLS; 5V VCC, no VPP |
| `0x06`      | `IC2_ALG_W29F32P`   | Winbond/SST AMD-unlock 5V flash (W29F32P type)      | ~200                  | YES           | YES            | **IMPLEMENTED** | `configure_flash3()` handler; registered in KNOWN_PROTOCOLS; 5V VCC, sector erase |
| `0x07`      | `IC2_ALG_ROM28P_1`  | 28-pin UV-EPROM primary (27Cxxx, 9–13V VPP)         | ~220 (incl. overrides) | YES          | YES            | **IMPLEMENTED** | `configure_eprom()` handler; registered in KNOWN_PROTOCOLS; WARNING-5 override redirects mistagged EEPROMs to 0x0D |
| `0x08`      | `IC2_ALG_ROM32P`    | 32-pin UV-EPROM (27C010/020/040, 100µs pulse)       | ~127                  | YES           | YES            | **IMPLEMENTED** | `configure_eprom()` handler; registered in KNOWN_PROTOCOLS |
| `0x09`      | `IC2_ALG_ROM40P`    | 40-pin ROM / EPROM                                  | 0 in DIP 24–32 filter | NO — 40-pin   | NO             | **INFEASIBLE-ON-RURP** | 40-pin DIP; excluded by `24 <= pin_count <= 32` filter; RURP socket supports DIP24/28/32 max |
| `0x0A`      | `IC2_ALG_R28TO32P`  | 28-to-32 pin adapter ROM                            | 0 in DIP filter       | MAYBE         | NO             | **INFEASIBLE-ON-RURP** | Adapter-class algorithm; no chips pass the INFOIC2PLUS DIP filter at this ID; no RURP adapter support |
| `0x0B`      | `IC2_ALG_ROM24P_1`  | 24-pin legacy EPROM (2716/2732, 500µs pulse)        | ~20                   | YES           | YES            | **IMPLEMENTED** | `configure_eprom()` handler; registered in KNOWN_PROTOCOLS |
| `0x0C`      | `IC2_ALG_ROM44`     | 44-pin ROM                                          | 0 in DIP filter       | NO — 44-pin   | NO             | **INFEASIBLE-ON-RURP** | 44-pin package; excluded by pin count filter |
| `0x0D`      | `IC2_ALG_EE28C32P`  | 28/32-pin 5V EEPROM (AT28C/28Cxxx, DQ7 polling)    | ~140 (incl. 9 newly unblocked 24-pin) | YES | YES | **IMPLEMENTED** | `configure_eeprom28c()` handler; registered in KNOWN_PROTOCOLS; SDP-disable + DQ7 page poll; no VPP |
| `0x0E`      | `IC2_ALG_RAM32_1`   | 32-pin SRAM type 1 (JEDEC 32-pin layout)            | ~30                   | YES           | YES            | **IMPLEMENTED** | `configure_sram()` handler; registered in KNOWN_PROTOCOLS; 5V, no VPP |
| `0x0F`      | `IC2_ALG_SPI25F_2`  | SPI NOR Flash variant 2 (25-series)                 | 0 in DIP filter       | NO — serial   | NO             | **INFEASIBLE-ON-RURP** | SPI serial bus; excluded by `is_serial != 0` filter |
| `0x10`      | `IC2_ALG_28F32P`    | Intel 28F parallel flash (12V VPP, command register) | ~40                  | YES           | YES            | **IMPLEMENTED** | `configure_flash_intel()` handler; registered in KNOWN_PROTOCOLS; 12V VPP via CTRL_VPP_P1_ENABLE |
| `0x11`      | `IC2_ALG_FWH`       | Intel LPC Firmware Hub (4-wire serial, 3.3V VCC)    | 0 in DIP filter       | NO — serial   | NO             | **INFEASIBLE-ON-RURP** | LPC 4-wire serial bus + 3.3V VCC; not parallel; RURP has no LPC interface; confirmed v1.11 |
| `0x12`      | `IC2_ALG_T48`       | T48 programmer-specific algorithm                   | 0 in DIP filter       | MCU-class     | NO             | **INFEASIBLE-ON-RURP** | Programmer-specific MCU algorithm; `type=2` (MCU); no DIP parallel memory chips |
| `0x13`      | `IC2_ALG_T40A`      | T40 MCU algorithm variant A                         | 0 in DIP filter       | MCU-class     | NO             | **INFEASIBLE-ON-RURP** | MCU algorithm; `type=2`; no DIP parallel memory chips |
| `0x14`      | `IC2_ALG_T40B`      | T40 MCU algorithm variant B                         | 0 in DIP filter       | MCU-class     | NO             | **INFEASIBLE-ON-RURP** | MCU algorithm; `type=2`; no DIP parallel memory chips |
| `0x15`      | `IC2_ALG_T88V`      | T88V MCU algorithm                                  | 0 in DIP filter       | MCU-class     | NO             | **INFEASIBLE-ON-RURP** | MCU algorithm; `type=2`; no DIP parallel memory chips |
| `0x16`      | `IC2_ALG_PIC32X_1`  | PIC32 MCU algorithm variant 1                       | 0 in DIP filter       | MCU-class     | NO             | **INFEASIBLE-ON-RURP** | MCU algorithm; `type=2`; no DIP parallel memory chips |
| `0x17`      | `IC2_ALG_P18F87J`   | PIC18F87J MCU algorithm                             | 0 in DIP filter       | MCU-class     | NO             | **INFEASIBLE-ON-RURP** | MCU algorithm; `type=2`; no DIP parallel memory chips |
| `0x18`      | `IC2_ALG_P16F`      | PIC16F MCU algorithm                                | 0 in DIP filter       | MCU-class     | NO             | **INFEASIBLE-ON-RURP** | MCU algorithm; `type=2`; no DIP parallel memory chips |
| `0x19`      | `IC2_ALG_P18F2`     | PIC18F2 MCU algorithm                               | 0 in DIP filter       | MCU-class     | NO             | **INFEASIBLE-ON-RURP** | MCU algorithm; `type=2`; no DIP parallel memory chips |
| `0x1A`      | `IC2_ALG_P16F5X`    | PIC16F5X MCU algorithm                              | 0 in DIP filter       | MCU-class     | NO             | **INFEASIBLE-ON-RURP** | MCU algorithm; `type=2`; no DIP parallel memory chips |
| `0x1B`      | `IC2_ALG_P16CX`     | PIC16CX MCU algorithm                               | 0 in DIP filter       | MCU-class     | NO             | **INFEASIBLE-ON-RURP** | MCU algorithm; `type=2`; no DIP parallel memory chips |
| `0x1C`      | `IC2_ALG_PIC16C`    | PIC16C MCU algorithm                                | 0 in DIP filter       | MCU-class     | NO             | **INFEASIBLE-ON-RURP** | MCU algorithm; `type=2`; no DIP parallel memory chips |
| `0x1D`      | `IC2_ALG_ATMGA`     | ATmega MCU algorithm                                | 0 in DIP filter       | MCU-class     | NO             | **INFEASIBLE-ON-RURP** | MCU algorithm; `type=2`; no DIP parallel memory chips |
| `0x1E`      | `IC2_ALG_ATTINY`    | ATtiny MCU algorithm                                | 0 in DIP filter       | MCU-class     | NO             | **INFEASIBLE-ON-RURP** | MCU algorithm; `type=2`; no DIP parallel memory chips |
| `0x1F`      | `IC2_ALG_AT89P20`   | AT89C2051 8051 MCU algorithm                        | 0 in DIP filter       | MCU-class     | NO             | **INFEASIBLE-ON-RURP** | MCU algorithm; `type=2`; no DIP parallel memory chips |
| `0x20`      | `IC2_ALG_SM89`      | SyncMOS SM89 MCU algorithm                          | 0 in DIP filter       | MCU-class     | NO             | **INFEASIBLE-ON-RURP** | MCU algorithm; `type=2`; no DIP parallel memory chips |
| `0x21`      | `IC2_ALG_AT89C`     | AT89C MCU algorithm                                 | 0 in DIP filter       | MCU-class     | NO             | **INFEASIBLE-ON-RURP** | MCU algorithm; `type=2`; no DIP parallel memory chips |
| `0x22`      | `IC2_ALG_P87C`      | P87C MCU algorithm                                  | 0 in DIP filter       | MCU-class     | NO             | **INFEASIBLE-ON-RURP** | MCU algorithm; `type=2`; no DIP parallel memory chips |
| `0x23`      | `IC2_ALG_SST89`     | SST89 MCU algorithm                                 | 0 in DIP filter       | MCU-class     | NO             | **INFEASIBLE-ON-RURP** | MCU algorithm; `type=2`; no DIP parallel memory chips |
| `0x24`      | `IC2_ALG_W78E`      | Winbond W78E MCU algorithm                          | 0 in DIP filter       | MCU-class     | NO             | **INFEASIBLE-ON-RURP** | MCU algorithm; `type=2`; no DIP parallel memory chips |
| `0x25`      | `IC2_ALG_SM59`      | SyncMOS SM59 MCU algorithm                          | 0 in DIP filter       | MCU-class     | NO             | **INFEASIBLE-ON-RURP** | MCU algorithm; `type=2`; no DIP parallel memory chips |
| `0x26`      | `IC2_ALG_SM39`      | SyncMOS SM39 MCU algorithm                          | 0 in DIP filter       | MCU-class     | NO             | **INFEASIBLE-ON-RURP** | MCU algorithm; `type=2`; no DIP parallel memory chips |
| `0x27`      | `IC2_ALG_ROM24P_2`  | 24-pin SRAM (6116 family, NVRAM/FRAM)               | ~25                   | YES           | YES            | **IMPLEMENTED** | `configure_sram()` handler; registered in KNOWN_PROTOCOLS; fm1608 override in effect for FRAM |
| `0x28`      | `IC2_ALG_ROM28P_2`  | 28-pin SRAM (JEDEC, DS1230 class)                   | ~20                   | YES           | YES            | **IMPLEMENTED** | `configure_sram()` handler; registered in KNOWN_PROTOCOLS |
| `0x29`      | `IC2_ALG_RAM32_2`   | 32-pin SRAM / NVRAM 512K–1M                         | ~15                   | YES           | YES            | **IMPLEMENTED** | `configure_sram()` handler; registered in KNOWN_PROTOCOLS |
| `0x2A`      | `IC2_ALG_GAL16`     | GAL16V8 PLD programming algorithm                   | 0 (type=3 PLD)        | NO            | NO             | **INFEASIBLE-ON-RURP** | PLD (`type=3`); filtered before KNOWN_PROTOCOLS check; zero DIP memory chips; confirmed v1.11 |
| `0x2B`      | `IC2_ALG_GAL20`     | GAL20V8 PLD programming algorithm                   | 0 (type=3 PLD)        | NO            | NO             | **INFEASIBLE-ON-RURP** | PLD (`type=3`); filtered before KNOWN_PROTOCOLS check; zero DIP memory chips; same reason as 0x2A |
| `0x2C`      | `IC2_ALG_GAL22`     | GAL22V10 PLD programming algorithm                  | 0 (type=3 PLD)        | NO            | NO             | **INFEASIBLE-ON-RURP** | PLD (`type=3`); filtered before KNOWN_PROTOCOLS check; zero DIP memory chips; confirmed v1.11 |
| `0x2D`      | `IC2_ALG_NAND`      | NAND Flash (TSOP/SMD packages)                      | 0 in DIP filter       | SMD           | NO             | **INFEASIBLE-ON-RURP** | NAND Flash is SMD-only (TSOP/BGA); excluded by `is_smd != 0` filter; no DIP NAND chips in infoic.xml |
| `0x2E`      | `IC2_ALG_PIC32X_2`  | PIC32 MCU algorithm variant 2                       | 0 (type=2 MCU)        | NO            | NO             | **INFEASIBLE-ON-RURP** | MCU algorithm; `type=2`; zero DIP memory chips; confirmed v1.11 |
| `0x2F`      | `IC2_ALG_RAM36`     | 36-pin RAM algorithm                                | 0 in DIP filter       | NO — 36-pin   | NO             | **INFEASIBLE-ON-RURP** | 36-pin package; excluded by pin count filter (max 32); no reachable chips in INFOIC2PLUS DIP filter |
| `0x30`      | `IC2_ALG_KB90`      | KB90 MCU algorithm                                  | 0 in DIP filter       | MCU-class     | NO             | **INFEASIBLE-ON-RURP** | MCU algorithm; `type=2`; no DIP parallel memory chips |
| `0x31`      | `IC2_ALG_EMMC`      | eMMC flash (BGA package)                            | 0 in DIP filter       | NO — BGA      | NO             | **INFEASIBLE-ON-RURP** | eMMC is BGA/SMD; excluded by `is_smd != 0` and `is_serial != 0`; no DIP form factor |
| `0x32`      | `IC2_ALG_VGA`       | VGA / video chip algorithm                          | 0 in DIP filter       | NO            | NO             | **INFEASIBLE-ON-RURP** | Video IC programming; not a memory chip family; no DIP parallel memory chips |
| `0x33`      | `IC2_ALG_CPLD`      | CPLD programming algorithm                          | 0 (type=3 PLD)        | NO            | NO             | **INFEASIBLE-ON-RURP** | PLD/CPLD (`type=3`); filtered before KNOWN_PROTOCOLS check; no DIP parallel memory chips |
| `0x34`      | `IC2_ALG_GEN`       | Generic algorithm                                   | 0 in DIP filter       | UNKNOWN       | NO             | **INFEASIBLE-ON-RURP** | Generic/catch-all; no chips pass the INFOIC2PLUS DIP 24–32 filter; no reachable DIP memory chips |
| `0x35`      | `IC2_ALG_ITE`       | ITE IT8xxx EC MCU (TQFP128)                         | 0 (type=2 MCU)        | NO            | NO             | **INFEASIBLE-ON-RURP** | MCU in TQFP128 package; `type=2`; zero DIP memory chips; confirmed v1.11; previously phantomed in KNOWN_PROTOCOLS — removed by v1.11 Phase 57 |
| `0x39`      | NO IC2_ALG CONSTANT | Phantom — no constant in database.h                 | 0 (INFOIC2PLUS-unreachable) | N/A       | NO             | **INFEASIBLE-ON-RURP** | Not a real IC2_ALG constant; appears in legacy INFOIC format only (DIP40 ROM readers); INFOIC2PLUS-unreachable; removed from KNOWN_PROTOCOLS by v1.11 Phase 57; firmware still dispatches it to configure_flash4() as a legacy carry — this is a cleanup target, not a skeleton to fill |
| `0x3C`      | NOT IN SOURCE       | Invented — no entry in database.h at all            | 0                     | N/A           | NO             | **INFEASIBLE-ON-RURP** | Does not exist in minipro source at commit a8efaedc; removed from PROTOCOL_MAP by v1.11 Phase 57 |

---

### Bucket Summary

**IMPLEMENTED (11 real protocol IDs with active firmware handlers):**

`0x05`, `0x06`, `0x07`, `0x08`, `0x0B`, `0x0D`, `0x0E`, `0x10`, `0x27`, `0x28`, `0x29`

These cover 100% of the chips in `chip_database.json` (743 chips post-v1.11). Every chip emitted by `build_db.py` has a firmware handler.

**SKELETON-NEEDED: EMPTY (0 protocol IDs)**

There are zero protocol IDs that are simultaneously:
1. A real IC2_ALG_* constant in minipro's `database.h`
2. Assigned to DIP 24–32 parallel memory chips in `infoic.xml`
3. Not already implemented in Firestarter firmware

The v1.11 "already covered" conclusion holds without qualification. The hardware-feasible DIP parallel-memory set is exhaustively dispatched. There are no missing-but-feasible protocols for this milestone to stub.

**INFEASIBLE-ON-RURP (43 protocol IDs):**

All remaining IDs fall into one of these sub-categories:
- Serial bus (I2C, SPI, Microwire, LPC): `0x01`, `0x02`, `0x03`, `0x04`, `0x0F`, `0x11`
- MCU programming algorithms (`type=2`): `0x12`–`0x1F`, `0x20`–`0x26`, `0x2E`, `0x30`
- PLD/CPLD programming algorithms (`type=3`): `0x2A`, `0x2B`, `0x2C`, `0x33`
- SMD/BGA packages only: `0x2D` (NAND), `0x31` (eMMC)
- Pin count out of range (>32 pins): `0x09` (40-pin), `0x0C` (44-pin), `0x2F` (36-pin)
- Adapter/converter ROM: `0x0A`
- Non-memory device: `0x32` (VGA), `0x34` (generic)
- Null sentinel: `0x00`
- Phantom/invented (no chips, no real constant): `0x39`, `0x3C`

---

## Honest Assessment: What Bucket-2 Being Empty Means for v1.12

Bucket 2 is empty. This is not a research gap — it is the correct answer, and it agrees precisely with v1.11's source-grounded conclusion.

**The practical implication:** The "Skeleton handlers" feature of v1.12's scope statement cannot be skeleton stubs for "missing-but-RURP-feasible protocols" because no such protocols exist. The milestone's value must be re-framed:

1. **Fail-closed dispatch framework** (primary value): The current `mem_type` fallback chain at the bottom of `configure_memory()` is a silent-damage path. Any chip command with an unknown/zero `algorithm` field but `mem_type=1 (TYPE_EPROM)` currently falls through to `configure_eprom()` — asserting 12V VPP on whatever is in the socket. Removing or guarding this fallback is the real safety win.

2. **Explicit not-implemented response** (primary value): A distinct firmware wire response code for "protocol not implemented" (as opposed to generic operation errors) gives the host clean error handling and surfaces misuse clearly.

3. **Skeleton handlers as explicit infeasibility markers** (reframed value): If "skeleton" handlers are still useful, they serve as registered, documented "recognized-but-infeasible" stubs — e.g., a handler registered for `0x11` (IC2_ALG_FWH / FWH LPC) that immediately returns a "not implemented on RURP hardware" response rather than silently falling through to the mem_type chain. This is cleaner than the current approach where unrecognized protocols fall through to potentially destructive mem_type dispatch. Candidate IDs for explicit infeasibility markers:
   - `0x11` (IC2_ALG_FWH): LPC serial — the most likely to be attempted by a user with an FWH chip who sees it in minipro's database
   - `0x2A` / `0x2B` / `0x2C` (IC2_ALG_GAL16/GAL20/GAL22): PLD algorithms — would arrive only through a user-override DB entry; still worth a clean rejection
   - These would register in the dispatch chain, immediately return a specific "not-implemented" response, and document why (hardware infeasibility)

4. **Firmware protocol-set is stable**: No new chip families have become RURP-feasible since v1.11. The 11 IMPLEMENTED IDs cover every chip `build_db.py` will ever emit under current hardware constraints.

---

## Feature Landscape (Reframed for v1.12)

### Table Stakes (Required for the milestone to deliver its stated safety goal)

| Feature | Why Required | Complexity | Notes |
|---------|--------------|------------|-------|
| Fail-closed dispatch — remove/guard `mem_type` fallback | Silent hardware-damage path: `mem_type=1` fallback asserts 12V VPP on unknown protocols | MEDIUM | Target: `configure_memory()` in `memory.cpp`; the protocol-prefix chain already covers all 11 real protocols; the `mem_type` chain below it is the hazard |
| Distinct "not-implemented" wire response code | Host needs to distinguish "protocol unimplemented" from a generic operation error for clean UX | LOW | New message-ID in `tools/catalog/messages.toml`; codegen produces C++ + Python; lockstep wire change |
| Host graceful handling — "protocol not implemented" user message | Without this, users get a cryptic serial error or silence when `algorithm` is unrecognized | LOW | `cli_handlers.py` maps the new response code to a clean human message; requires `constants.py` / `firestarter.h` sync |
| Native dispatch tests for fail-closed path | Without tests, the safety guarantee is undocumented and regression-prone | LOW | Extend `test_configure_memory.cpp` to cover: (a) unknown protocol_id returns not-implemented, (b) algorithm=0 + mem_type=1 no longer silently routes to configure_eprom |

### Differentiators (Increase robustness and auditability)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Explicit infeasibility skeleton for `0x11` (IC2_ALG_FWH) | User with an FWH chip gets a clean "not supported on RURP hardware" instead of falling to `mem_type` chain | LOW | Registers a handler stub that returns the new not-implemented response; documents the hardware reason |
| Explicit infeasibility skeletons for PLD IDs (`0x2A`, `0x2B`, `0x2C`) | Defense in depth: user-override DB entries with PLD algorithms never silently engage VPP | LOW | Same stub pattern; these IDs are filtered by `build_db.py` but a hand-crafted command could still reach firmware |
| Protocol-gap enumeration document in `firestarter/doc/` or `firestarter_app/doc/` | Future-proofs the architecture: any developer adding a chip knows exactly which protocols are handled, which are stubs, which are infeasible | LOW | Derived from this research; the classification table above is the source |

### Anti-Features (Do Not Build)

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Actual programming logic for new chip families | Bucket 2 is empty — no new feasible protocols exist; implementing programming logic would be building for zero chips | Stay at skeleton/stub level; defer programming logic to per-protocol milestones gated on actual hardware availability |
| Stubbing all 43 infeasible IDs | Registers 43 no-op handlers that add noise with zero user value | Stub only the IDs a user could plausibly encounter via a hand-crafted command or user-override DB entry (0x11, 0x2A, 0x2B, 0x2C at most) |
| Backward-compat preservation of `mem_type` chain | The chain is the hazard this milestone exists to eliminate | Remove or guard it; any host version that omits `algorithm` should get the fail-closed response, not silent VPP engagement |

---

## Feature Dependencies

```
Fail-closed dispatch (guard/remove mem_type fallback)
    requires: New "not-implemented" wire response code
                  requires: messages.toml codegen update (messages.py + firmware header)

Host graceful handling
    requires: New "not-implemented" wire response code
    requires: Fail-closed dispatch (so the response is actually emitted)

Dispatch tests (fail-closed path)
    requires: Fail-closed dispatch (to have something to test)
    requires: New response code (to assert against)

Infeasibility skeleton stubs (optional: 0x11 / 0x2A / 0x2B / 0x2C)
    requires: New "not-implemented" wire response code (stubs emit it)
    enhances: Fail-closed dispatch (explicit rejection is cleaner than generic fallthrough)
```

---

## Sources

- minipro `database.h` IC2_ALG_* constants @ `a8efaedc236c1d9718bd28299dfbb99536b010ff` (fetched 2026-06-10 via raw GitLab URL — confirmed complete list `0x00`–`0x35`, 54 named constants)
- `firestarter_app/doc/infoic-field-dictionary.md` — v1.11 canonical field dictionary; all `protocol_id` semantics source-cited against `database.h#L24–L77`
- `firestarter_app/doc/protocol-id.md` — v1.11 corrected protocol-ID reference; exclusion rationales for 0x11/0x2A/0x2C/0x2E/0x35/0x39/0x3C
- `firestarter_app/tools/build_db.py` — KNOWN_PROTOCOLS set (post-v1.11: 11 IDs); PROTOCOL_MAP (canonical IC2_ALG_* names); filter logic (`type_int in [1,4]`, DIP 24–32, `is_smd==0`, `is_serial==0`)
- `firestarter/CLAUDE.md` — dispatch table; algorithm handler table (11 handlers, 13 protocol IDs including 0x35/0x39 legacy carry)
- `.planning/PROJECT.md` — v1.12 milestone scope; v1.11 research conclusion ("hardware-feasible set already covered")
- `.planning/milestones/v1.11-ROADMAP.md` — v1.11 scope re-derivation rationale; Phase 57 PROTOCOL_MAP canonicalization; post-close state

---
*Protocol-gap enumeration for v1.12 "Firmware Protocol Dispatch Hardening + Skeletons"*
*Researched: 2026-06-10*

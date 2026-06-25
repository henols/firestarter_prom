# Feature Research — Protocol Vocabulary (protocol_id → name → datasheet-verified behavior)

**Domain:** Internal architecture — minipro `protocol_id` (algorithm) buckets for an Arduino EPROM/Flash/SRAM programmer (Firestarter v1.16 protocol-first rebuild)
**Researched:** 2026-06-25
**Confidence:** HIGH (every row enumerated from the live `chip_database.json` + cross-checked against firmware dispatch `memory.cpp` and the per-handler `src/proms/*.cpp` sources; datasheet-needed flags noted per row)

> This dimension's deliverable is the **protocol vocabulary table** the naming pass produces. The conventional "table stakes / differentiators / anti-features" framing is adapted to the three states a protocol bucket is in for v1.16:
> - **NAMED-NOW** — bucket has a `PROTOCOL_MAP` name already, on-hand silicon proven, ready to name-finalize + document immediately (the "table stakes" of the naming pass).
> - **RENAME-THEN-DECOMPOSE** — bucket is real and dispatched, but its name is weak / its handler is duplicated / it shares a handler with sibling buckets; it is the primary target of the later primitive-decomposition stage (the "differentiator" work that buys flash headroom).
> - **UNVERIFIED / ANTI** — bucket is dispatched but has no on-hand silicon (stays explicit `UNVERIFIED`), is host-refused (`protocol-not-implemented`), or is a phantom/infeasible arm that must NOT be conflated with a real algorithm (the "anti-feature" — naming must keep it honest, never imply support).

---

## 0. Ground-truth enumeration (from the live DB — not from memory)

`chip_database.json` (744 chips) contains **exactly 12 distinct `algorithm` values**. There is **no 0x40 bucket** — the MEMORY.md note "FM1608 (0x40)" conflated decimal `40` with hex `0x40`; FM1608's algorithm is `40` decimal = **`0x28`** (SRAM_STD / NVRAM-overwrite). All hex below is derived from the decimal `algorithm` field.

| protocol_id | `PROTOCOL_MAP` name | chips | `electrical.type` mix | firmware handler (file) | dispatch line |
|---|---|---|---|---|---|
| `0x05` | FLASH_AMD_STD | 27 | Flash/EEPROM 27 | `configure_flash4` (`flash_type_4.cpp`) | `memory.cpp:89` |
| `0x06` | FLASH_AMD_ALT | 190 | Flash/EEPROM 190 | `configure_flash3` (`flash_type_3.cpp`) | `memory.cpp:84` |
| `0x07` | EPROM_STD | 170 | UV-EPROM 163, EEPROM 7 | `configure_eprom` (`eprom.cpp`) | `memory.cpp:94` |
| `0x08` | EPROM_QUICK | 127 | UV-EPROM 106, EEPROM 21 | `configure_eprom` (`eprom.cpp`) | `memory.cpp:94` |
| `0x0B` | EPROM_LEGACY | 30 | UV-EPROM 30 | `configure_eprom` (`eprom.cpp`) | `memory.cpp:94` |
| `0x0D` | EEPROM_POLL | 84 | Flash/EEPROM 84 | `configure_eeprom28c` (`eeprom_28c.cpp`) | `memory.cpp:79` |
| `0x0E` | SRAM_32PIN | 20 | SRAM 20 | `configure_sram` (`sram.cpp`) | `memory.cpp:99` |
| `0x10` | FLASH_INTEL | 39 | Flash/EEPROM 39 | `configure_flash_intel` (`flash_intel.cpp`) | `memory.cpp:74` |
| `0x27` | SRAM_24PIN | 2 | SRAM 2 | `configure_sram` (`sram.cpp`) | `memory.cpp:99` |
| `0x28` | SRAM_STD | 34 | SRAM 33, FRAM 1 | `configure_sram` (`sram.cpp`) | `memory.cpp:99` |
| `0x29` | SRAM_512K_1M | 20 | SRAM 20 | `configure_sram` (`sram.cpp`) | `memory.cpp:99` |
| `0x34` | *(no PROTOCOL_MAP entry)* | 1 | UV-EPROM 1 (mis-typed) | none → `configure_not_implemented` (`not_implemented.cpp`) | `memory.cpp:116` (generic fail-closed) |

**Phantom / forward-compat buckets present in firmware dispatch but with ZERO DB chips** (must be named as phantoms, never as real algorithms): `0x35`, `0x39` (both route to `configure_flash4` in firmware but are excluded from host `KNOWN_PROTOCOLS` → host sends them to `not_implemented`). **Named-infeasible arms** (zero DB chips, hard fail-closed): `0x11` FWH (LPC serial + 3.3V), `0x2A`/`0x2B`/`0x2C` GAL/PLD.

---

## 1. The protocol vocabulary (PRIMARY deliverable)

Each row: proposed human name → write algorithm → erase model → VPP behavior → pin roles → representative chip → handler → datasheet-to-acquire. The proposed names follow the rebuild's "algorithm axis, kept distinct from the electrical axis" rule — names describe *how it programs*, never *what silicon technology it is*.

### `0x05` — Proposed name: **Flash-AMD-PageWrite** (current: FLASH_AMD_STD)
- **minipro decode:** `IC2_ALG_F29EE` (`PROTOCOL_MAP` 0x05, build_db.py:28).
- **Write algorithm:** software-data-protect page write — SDP unlock prelude, then byte-load into a chip page buffer; page size is **data-driven from `mem_size`** (`flash4_page_size()`: ≤64KB→64B, ≤256KB→128B, else 256B — the W29C040 256B-page fix from v1.13/v1.15). Write completion is **DQ7 toggle / data-poll** (`flash4_wait_for_page_write`).
- **Erase model:** **auto-erase on write** (the page-write erases the page implicitly; chip is Flash/EEPROM). First silicon proof of auto-erase = W29C020 (v1.15).
- **VPP:** none — 5V VCC only (no regulator engagement).
- **Pin roles:** standard parallel address/data; no VPP pin used.
- **chip-id:** `flash4_check_chip_id_execute` (`CMD_CHECK_CHIP_ID`) reads AMD-style manufacturer/device ID via the shared AMD chip-ID util.
- **Representative chip:** Winbond W29C020 / W29C040 (on hand); ATMEL AT29C020 family.
- **Datasheet-to-acquire:** Winbond W29C020 + W29C040 (own both); confirms SDP sequence + page size + DQ7 poll.
- **State:** **RENAME-THEN-DECOMPOSE** — W29C040 256B page-0 fault is *not silicon-effective* (CR-01 / Phase-74 Wave-2 open); shares SDP-unlock + DQ7-poll + chip-id primitives with 0x06 and 0x0D.

### `0x06` — Proposed name: **Flash-AMD-Unlock-SectorErase** (current: FLASH_AMD_ALT)
- **minipro decode:** `IC2_ALG_W29F32P` (`PROTOCOL_MAP` 0x06).
- **Write algorithm:** classic AMD/JEDEC `0x5555/0x2AAA` unlock-cycle command sequence, byte program after unlock.
- **Erase model:** **explicit chip/sector erase** — `flash3_sector_erase` issues the 6-byte erase command sequence (`{0x5555,0xAA},{0x2AAA,0x55},...`); ~100ms internal erase with a ~105ms settle delay, gated to run once per operation (not per chunk).
- **VPP:** none — 5V VCC only.
- **Pin roles:** standard parallel; no VPP pin.
- **Representative chip:** SST SST39SF040 (on hand); AMD AM29F040 family (190 chips — the largest bucket).
- **Datasheet-to-acquire:** SST39SF040 (own); AMD Am29F040B as the canonical "alt" reference. Confirm unlock addresses + sector-erase timing.
- **State:** **NAMED-NOW for SST39SF040** (bench PASS v1.15) / **RENAME-THEN-DECOMPOSE** for the bucket (largest reuse target; shares unlock-sequence + erase primitive with 0x05).

### `0x07` — Proposed name: **EPROM-Program-1ms** (current: EPROM_STD)
- **minipro decode:** `IC2_ALG_ROM28P_1` (`PROTOCOL_MAP` 0x07) — the canonical 28-pin EPROM family.
- **Write algorithm:** single-pulse programming, **1ms default pulse** (`eprom.cpp:74` default 1000µs), DQ7-style verify with adaptive retry (`pulse_delay` extended on mismatch).
- **Erase model:** **external** for true UV-EPROMs (UV eraser, none on-hand); but the 7 `electrical.type=="EEPROM"` members on this bucket are **electrically auto-erasable** via `FLAG_CAN_ERASE` derived from `electrical.type=="EEPROM"` (v1.14 Phase 77 erase write-path).
- **VPP:** **13V via the dropping-resistor path** — `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE` produces a precise VPP from VPE (`eprom.cpp:149`). `eprom_check_vpp` validates the rail before pulsing.
- **Pin roles:** dedicated VPP pin on `DIP28_27512`/`DIP28_27256` pinouts; VPP asserted on the address bus via `mem_util_remap_address_bus` (vpp_line) unless P1-as-VPP.
- **Representative chip:** Winbond W27C512 / SST27SF512 (on hand, EEPROM members); ST/AMD AM27C512 (true UV member); AM2764A.
- **Datasheet-to-acquire:** W27C512 + SST27SF512 (own, EEPROM-class); a true-UV 27C512 (ST M27C512, own) for the UV-vs-EEPROM contrast.
- **State:** **NAMED-NOW** (W27C512 + SST27SF512 + ST M27C512 bench-proven v1.15). ⚠ **AXIS HAZARD** — this bucket mixes 163 UV-EPROM + 7 EEPROM members; the name must NOT say "UV" (see §3).

### `0x08` — Proposed name: **EPROM-Program-100us-Large** (current: EPROM_QUICK)
- **minipro decode:** `IC2_ALG_ROM32P` (`PROTOCOL_MAP` 0x08) — the 32-pin "large EPROM" family.
- **Write algorithm:** quick-pulse programming, **100µs default pulse** (`eprom.cpp:72`).
- **Erase model:** external (UV) for the 106 UV members; 21 EEPROM members electrically auto-erase via `FLAG_CAN_ERASE`.
- **VPP:** **13V via dropping-resistor path** (same as 0x07); but on `DIP32` parts VPP is routed to **socket pin 1** via `CTRL_VPP_P1_ENABLE` (`using_p1_as_vpp()` true for 32-pin with `vpp_line==VPP_P1_32_DIP`), NOT onto the address bus. This is the "P1-as-VPP for large EPROMs" point fix.
- **Pin roles:** **P1-as-VPP** — the large-EPROM-specific pin role; `mem_util_remap_address_bus` skips the address-bus VPP line when `using_p1_as_vpp()` is true.
- **Representative chip:** AMD/ATMEL/Intel 27C020 (AM27C020 on hand); W27C040/W27E040 (EEPROM members, on hand).
- **Datasheet-to-acquire:** AM27C020 (own); W27E040 (own). Confirm pin-1-VPP routing + 100µs pulse.
- **State:** **RENAME-THEN-DECOMPOSE** — shares the entire `configure_eprom` body with 0x07/0x0B (differs only in pulse default + P1-routing). **AM27C020 0x08 write fails (0-bits-programmed, FUT-06)** — the 32-pin write/VPP path is the open defect; bench-verify before claiming PASS.

### `0x0B` — Proposed name: **EPROM-Program-500us-DirectVPE-24pin** (current: EPROM_LEGACY)
- **minipro decode:** `IC2_ALG_ROM24P_1` (`PROTOCOL_MAP` 0x0B) — the 24-pin legacy 2716/2732 family.
- **Write algorithm:** **500µs default pulse** (`eprom.cpp:73`); single-pulse program.
- **Erase model:** external (UV) — all 30 members are UV-EPROM; no on-hand eraser.
- **VPP:** **direct VPE path — NO dropping resistor** (`eprom.cpp:145`: `protocol==0x0B` sets `CTRL_VPP_REGULATOR_ENABLE` only, not `CTRL_VPP_VPE_DROP_ENABLE`). This is the rail that physically reaches ~22.4V (the v1.14 25V-NMOS best-effort program rail) — it is the `firestarter vpe` rail, distinct from the dropped 0x07/0x08 VPP. The `vpp` monitor reads the *dropped* rail, so it under-reports the 0x0B program voltage.
- **Pin roles:** 24-pin; VPP shares the OE pin region (the 2716/2732 OE/VPP overlap) — `using_p1_as_vpp` uses `VPP_P21_24_DIP` for 24-pin.
- **Representative chip:** AMD AM2716 / AM2732; the **2516** (user-override entry, NMOS ~25V class, graduated v1.15 — genuinely absent from minipro).
- **Datasheet-to-acquire:** TI/Intel 2716 + 2732; the 2516 datasheet (own the chip). Confirm OE/VPP-shared-pin reads + 25V VPP range.
- **State:** **RENAME-THEN-DECOMPOSE / partially UNVERIFIED** — 2516 read is **unstable** (3 distinct SHAs after the VPP-skip fix → FUT-03, GRAD-03 deferred best-effort). 0x0B read is VPP-gated (the shared OE/VPP pin); reset clears the gate. No clean write-cycle proof on-hand (no eraser).

### `0x0D` — Proposed name: **EEPROM-28C-PageWrite-SDP** (current: EEPROM_POLL)
- **minipro decode:** `IC2_ALG_EE28C32P` (`PROTOCOL_MAP` 0x0D) — the AT28C-series 5V EEPROM family.
- **Write algorithm:** SDP-disable 6-write magic-address sequence (`EEPROM_SDP_DISABLE`, `eeprom_28c.cpp:26`), then page write with **DQ7 data-poll** for completion; no pulse delay (fast consecutive writes).
- **Erase model:** **auto-erase on byte/page write** (28C EEPROM self-erases).
- **VPP:** **NONE — pure 5V VCC**. This is the critical safety bucket: `DIP28_2764` 5V-EEPROMs were re-routed from 0x07 → 0x0D precisely so the firmware never asserts 12V on socket pin 1 (which is A14, not VPP, on these parts — the WARNING-5 / A14-hazard fix). `configure_eeprom28c` engages the regulator only for the A9-based chip-ID read, not for writes.
- **Pin roles:** standard 24/28-pin parallel; A14 on pin 1 (NOT VPP) — the axis-hygiene linchpin.
- **Representative chip:** ATMEL AT28C256 / AT28C64; AT28C04/16 (the 9 `adapter-required` members, DIP24→DIP32 adapter not built → FUT-04).
- **Datasheet-to-acquire:** ATMEL AT28C256 (canonical SDP sequence) + AT28C16 (the adapter-required 24-pin case).
- **State:** **RENAME-THEN-DECOMPOSE / partly UNVERIFIED** — no on-hand AT28C silicon; 9 members host-refused as `adapter-required`. SDP-unlock + DQ7-poll primitives are shared with 0x05.

### `0x0E` / `0x27` / `0x28` / `0x29` — Proposed names: **SRAM-RW-32pin / SRAM-RW-24pin / SRAM-RW-NVRAM / SRAM-RW-512K-1M** (current: SRAM_32PIN / SRAM_24PIN / SRAM_STD / SRAM_512K_1M)
- **minipro decode:** `IC2_ALG_RAM32_1` (0x0E), `IC2_ALG_ROM24P_2` (0x27), `IC2_ALG_ROM28P_2` (0x28), `IC2_ALG_RAM32_2` (0x29).
- **Write algorithm:** generic synchronous read/write — no command sequence, no pulse protocol; data is simply driven onto the bus and latched (overwrite-in-place).
- **Erase model:** **none** (volatile SRAM / battery-backed NVRAM / FRAM — write is overwrite).
- **VPP:** **NONE — never reaches the VPP regulator** (BLOCKER-2 mitigation: SRAM chips often carry `mem_type=1` in the DB and MUST be dispatched by `protocol` before `mem_type` so they never reach `configure_eprom`'s 12V path). The DB `vpp=12V` field on these rows is a decode artifact, NOT a routed voltage — `configure_sram` ignores it.
- **Pin roles:** standard parallel SRAM; the four buckets differ by pin-count / size class only, not by algorithm.
- **Representative chip:** RAMTRON FM1608 (FRAM, on hand, 0x28); DALLAS DS1245/DS1230 NVRAM; standard 6116 (0x27).
- **Datasheet-to-acquire:** FM1608 (own — FRAM); a DS1245-class NVRAM; 6116 SRAM. (Low priority — algorithm is trivial.)
- **State:** **NAMED-NOW for 0x28 (FM1608 overwrite bench-proven v1.15)** / the four buckets are the **strongest decompose-into-one-primitive candidate** — they are four names for one generic-RW algorithm differing only by pin/size. ⚠ FM1608 is **FRAM**, relabeled SRAM→FRAM in v1.15; its `vpp=12V` is the classic decode-artifact axis trap.

### `0x10` — Proposed name: **Flash-Intel-CommandRegister** (current: FLASH_INTEL)
- **minipro decode:** `IC2_ALG_28F32P` (`PROTOCOL_MAP` 0x10) — Intel 28F command-register flash.
- **Write algorithm:** Intel command-register protocol — program/erase commands written to the device, **Status Register (SR) polling** for completion (`flash_intel.cpp`).
- **Erase model:** **explicit block/chip erase** via command register.
- **VPP:** **12V via socket pin 1** — `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_P1_ENABLE` held active through the write pulse (`flash_intel.cpp:107`); `flash_intel_check_vpp` validates but does NOT clear the regulator (caller keeps it asserted across the program). Safety: regulator cleared on early-return.
- **Pin roles:** P1-as-VPP (12V); standard parallel address/data.
- **Representative chip:** AMD AM28F010/020; Intel 28F010/28F020.
- **Datasheet-to-acquire:** Intel 28F010 (canonical command-register + SR-poll); AM28F020.
- **State:** **UNVERIFIED** — 39 chips, **no on-hand silicon**, no v1.13–v1.15 bench evidence. Keep explicit `UNVERIFIED`. Distinct command-register + SR-poll primitives (does not share the AMD unlock path).

### `0x34` — Proposed name: **EEPROM-X88C64-MultiplexedBus** (current: NO PROTOCOL_MAP NAME)
- **minipro decode:** XICOR X88C64 — an 8051-family "E2 micro-peripheral" with a **multiplexed low-order address/data bus** (addresses latched while **ALE** is HIGH); page write with **toggle-bit (I/O6) polling** (datasheet-confirmed below).
- **Write algorithm:** ALE-latched multiplexed-bus page write, toggle-bit poll. **No firmware handler exists.**
- **Erase model:** auto-erase (28C-class EEPROM page write).
- **VPP:** none — 5V.
- **Pin roles:** **multiplexed ALE/WR/RD bus** — the RURP shield has no free 74HC573 strobe to drive ALE (v1.14 Phase 78 verdict: **PCB-BLOCKED**, control register fully allocated).
- **Representative chip:** XICOR X88C64P (DIP24, the single 0x34 DB entry).
- **Datasheet-to-acquire:** XICOR X88C64 (RS-Online / alldatasheet — see Sources). Document the ALE-bus *why* even though no handler ships.
- **State:** **UNVERIFIED / ANTI** — host-refused as `protocol-not-implemented`; firmware routes it to `configure_not_implemented` via the generic fail-closed guard (`memory.cpp:116`). Naming must record the *why-not* (PCB-blocked ALE), never imply a path. ⚠ **AXIS TRAP** — its DB `electrical.type` is mis-set to `UV-EPROM` though it is a **5V EEPROM**; the naming pass should flag/fix this decode error.

---

## 2. On-hand silicon vs UNVERIFIED

The v1.15 inventory is **11 physical chips** (Leonardo + RURP Rev 2.0 only — the sole trustworthy bench combo). Mapping to buckets:

| protocol_id | proposed name | on-hand chip(s) | bench verdict (v1.15) | verification state |
|---|---|---|---|---|
| `0x05` | Flash-AMD-PageWrite | W29C020, W29C040 | W29C020 **PASS** (first auto-erase silicon proof); W29C040 **FAIL** (256B page-0, CR-01) | **PARTIAL** — bucket NAMED-NOW via W29C020; W29C040 defect open |
| `0x06` | Flash-AMD-Unlock-SectorErase | SST39SF040 | **PASS** | **VERIFIED** (NAMED-NOW) |
| `0x07` | EPROM-Program-1ms | W27C512, SST27SF512, ST M27C512 | W27C512 **PASS**, SST27SF512 **PASS**, ST M27C512 UV write **PASS** (partial spend) | **VERIFIED** (NAMED-NOW) |
| `0x08` | EPROM-Program-100us-Large | W27E040, AM27C020 | W27E040 stuck-bit silicon wear (D-32, not algo); AM27C020 write **FAIL** (0-bits, FUT-06) | **UNVERIFIED for write** — defect open; read path OK |
| `0x0B` | EPROM-Program-500us-DirectVPE-24pin | 2516 | read **UNSTABLE** (3 SHAs, FUT-03); no write-cycle (no eraser) | **UNVERIFIED** (GRAD-03 deferred best-effort) |
| `0x0D` | EEPROM-28C-PageWrite-SDP | *(none)* | — | **UNVERIFIED** — no AT28C silicon; 9 members `adapter-required` |
| `0x0E` | SRAM-RW-32pin | *(none)* | — | **UNVERIFIED** |
| `0x10` | Flash-Intel-CommandRegister | *(none)* | — | **UNVERIFIED** — no 28F silicon at all |
| `0x27` | SRAM-RW-24pin | *(none)* | — | **UNVERIFIED** |
| `0x28` | SRAM-RW-NVRAM | FM1608 (FRAM) | **PASS** (overwrite) | **VERIFIED** (NAMED-NOW) |
| `0x29` | SRAM-RW-512K-1M | *(none)* | — | **UNVERIFIED** |
| `0x34` | EEPROM-X88C64-MultiplexedBus | *(none)* | — | **UNVERIFIED / not-implemented** (PCB-blocked) |

**Also excluded from any on-hand mapping (D-32, silicon wear not algorithm):** W27E512 (0x07), W27E040 (0x08) — exercised but failed on stuck bits.

**Summary:** of 12 buckets, **4 have a clean on-hand PASS** (0x06, 0x07, 0x28, plus 0x05 via W29C020); **2 have on-hand silicon with open write/read defects** (0x08, 0x0B); **6 stay explicit UNVERIFIED** (0x0D, 0x0E, 0x10, 0x27, 0x29, 0x34). This is the per-protocol bench-ledger seed for the v1.16 verification-ledger feature.

---

## 3. Axis hygiene — where algorithm got tangled with electrical type (MUST keep separate)

`protocol_id` is the **algorithm axis** (how to write/erase). `electrical.type` (UV-EPROM / EEPROM / Flash/EEPROM / SRAM / FRAM) is the **electrical axis** (what the silicon is). They are orthogonal; conflating them caused real hazards. The naming pass must produce names on the **algorithm axis only**.

| Bucket | The tangle | Why it matters | Naming rule |
|---|---|---|---|
| `0x07` | 163 UV-EPROM **+ 7 EEPROM** members share one algorithm | A "UV" name (current EPROM_STD reads UV-ish) hides that W27C512/SST27SF512 are electrically-erasable EEPROMs that auto-erase via `FLAG_CAN_ERASE` | Name the *pulse algorithm* (Program-1ms), not the silicon |
| `0x08` | 106 UV + 21 EEPROM share `configure_eprom`; P1-as-VPP only matters for 32-pin | Same UV/EEPROM mix; the 5V-vs-13V decision is NOT derivable from protocol_id alone | Name the algorithm (Program-100us-Large), let `electrical.type` drive erase/VPP |
| `0x0D` | 5V EEPROMs that *used to* live on 0x07 (DIP28_2764) | The A14-on-pin-1 hazard: 0x07 asserts 12V on pin 1; on these parts pin 1 is A14 → **hardware damage**. Re-routed 0x07→0x0D so `configure_eeprom28c` never engages VPP | The 0x0D name must scream "5V, no VPP" so future edits don't re-merge it into 0x07 |
| `0x0E/0x27/0x28/0x29` | DB rows carry `vpp=12V` but `configure_sram` routes **no** voltage | The 12V is a decode artifact; SRAM `mem_type=1` could fall into `configure_eprom`'s 12V path if `protocol` didn't dispatch first (BLOCKER-2) | Names must mark these as VPP-free; never let the `vpp` field imply a routed rail |
| `0x28` | FM1608 is **FRAM**, not SRAM; relabeled v1.15 | Type label drives the `info` display + erase logic; the algorithm (overwrite) is identical to SRAM | Algorithm name stays SRAM-RW; the *electrical.type* (FRAM) is the separate axis |
| `0x34` | DB `electrical.type` mis-set to **UV-EPROM** for a 5V EEPROM | A wrong electrical type on a multiplexed-bus 5V part could route 12V if a handler were ever added carelessly | Fix the type decode AND name on the algorithm (X88C64-MultiplexedBus) |
| `0x0B` | VPP-on-OE-shared-pin + 25V NMOS rail confusion | The 0x0B *direct-VPE* rail (~22.4V) is a different rail than the dropped 0x07/0x08 VPP; the `vpp` monitor reads the wrong one | Name must carry "DirectVPE" so the rail isn't confused with the dropping-resistor VPP |

**One-line rule for the naming pass:** *the protocol name answers "how do I pulse/command/poll this?" — the `electrical.type` field answers "is it UV, EEPROM, SRAM, FRAM?". Never let one leak into the other.*

---

## 4. Shared-primitive map (feeds the later decompose stage)

Already visible from the handler reads — the duplication that the rebuild's flash-shrink driver targets:

| Primitive | Used by | Reuse opportunity |
|---|---|---|
| Address setup / bus remap (`mem_util_set_address`, `mem_util_remap_address_bus`) | ALL | Already shared in `memory.cpp` — keep |
| Single data strobe (`memory_set_data` /CE pulse) | 0x07/0x08/0x0B, SRAM | Shared core; pulse-width is the only variable |
| DQ7 / data-poll completion | 0x05, 0x0D, (0x07 verify) | Extract one `poll_dq7()` primitive |
| AMD-style unlock sequence (`0x5555/0x2AAA`) | 0x05, 0x06, 0x0D (SDP) | One `amd_unlock(seq[])` primitive |
| Chip-ID read (AMD manufacturer/device) | 0x05, 0x06 | Already a shared AMD chip-ID util (v1.13) |
| VPP gate (`eprom_check_vpp` / `flash_intel_check_vpp`) | 0x07/0x08/0x0B, 0x10 | Two near-duplicate VPP validators → one parameterized gate |
| Generic RW (no protocol) | 0x0E/0x27/0x28/0x29 | **Four buckets, one algorithm** — highest-value single collapse |

This is the strongest evidence for the rebuild's thesis: `configure_eprom` (0x07/0x08/0x0B) is one body with three pulse defaults + a P1-routing branch; the four SRAM buckets are one algorithm with four names; SDP-unlock + DQ7-poll recur across 0x05/0x06/0x0D.

---

## MVP / sequencing recommendation for the naming pass

1. **NAMED-NOW first (lowest risk, on-hand-proven):** 0x06, 0x07, 0x28, 0x05(W29C020) — finalize names + write the *why* with datasheet in hand.
2. **RENAME-THEN-DECOMPOSE (the flash-shrink payoff):** collapse the 4 SRAM buckets, then unify 0x07/0x08/0x0B `configure_eprom`, then factor SDP/DQ7 across 0x05/0x06/0x0D.
3. **UNVERIFIED rows authored but flagged:** 0x0D, 0x0E, 0x10, 0x27, 0x29, 0x34 — name + datasheet-document, mark `UNVERIFIED` in the ledger, never claim PASS.
4. **Phantom/infeasible discipline:** explicitly name 0x35/0x39 as phantoms and 0x11/0x2A/0x2B/0x2C as infeasible — so the vocabulary is complete and honest.

## Confidence & gaps

- **HIGH** on the enumeration, handler mapping, dispatch lines, and inventory mapping — all read directly from the live DB + firmware sources.
- **MEDIUM** on exact minipro `IC2_ALG_*` constant semantics for 0x27/0x29 (named from `PROTOCOL_MAP` comments; not re-verified against minipro source this pass — v1.11 verified them at `database.h#L24-L77 @ a8efaedc`).
- **Gap:** 6 buckets have no on-hand silicon — their datasheet-verified behavior is documentable but only bench-confirmable when chips are acquired (the v1.16 datasheet-acquisition stage scopes one representative chip per no-silicon bucket).
- **Decode bug to fix:** `0x34` X88C64 `electrical.type` is wrongly `UV-EPROM` (should be EEPROM) — surface in the naming pass.

## Sources

- Live repo (HIGH): `firestarter_app/firestarter/data/chip_database.json`, `firestarter_app/tools/build_db.py` (`PROTOCOL_MAP`), `firestarter/src/proms/memory.cpp` + `eprom.cpp` + `flash_type_3.cpp` + `flash_type_4.cpp` + `eeprom_28c.cpp` + `flash_intel.cpp` + `include/memory_utils.h`, `.planning/v1.15/bench/EVIDENCE.json`, `firestarter/CLAUDE.md` (handler table).
- [XICOR X88C64 datasheet (RS Online)](https://docs.rs-online.com/c312/0900766b800af699.pdf) — confirms ALE multiplexed bus + toggle-bit polling for the 0x34 row.
- [X88C64 datasheet (AllDatasheet)](https://www.alldatasheet.com/datasheet-pdf/pdf/34231/XICOR/X88C64.html)

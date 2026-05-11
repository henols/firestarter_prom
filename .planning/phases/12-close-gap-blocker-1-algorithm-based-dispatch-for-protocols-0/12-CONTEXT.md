---
phase: 12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0
type: context
date: 2026-05-11
---

# Phase 12 — Close BLOCKER-1: Algorithm-Based Dispatch for Missing Protocols

## Domain

Close BLOCKER-1 and BLOCKER-2 from `.planning/v1.0-MILESTONE-AUDIT.md` so that every
chip with a known `protocol_id` in the regenerated database reaches its correct
firmware handler.

Today, the milestone audit shows **247 of 743 chips** (33%) fall through
`memory.cpp:configure_memory` to `firestarter_error_response_format("Memory type
0x%02x not supported", handle->mem_type)`, and an additional **52 SRAM/NVRAM chips**
silently route to `configure_eprom`, which enables the VPP boost regulator on a
5V part (hardware-stress hazard).

The protocol-prefix dispatch pattern is already in place in `memory.cpp` for
`0x10` (FLASH_INTEL) and `0x0D` (EEPROM_POLL). This phase extends that pattern
to **all** known protocols and aligns the Python side so `mem_type` is no longer
derived from a substring search on `electrical.type`.

## What's broken (concrete trace)

The exact failure paths (from `.planning/INTEGRATION-CHECK.md` BLOCKER-1):

1. `firestarter_app/tools/build_db.py` line 214 emits `electrical.type =
   "Flash/EEPROM"` whenever the minipro XML `flags & 0x10` bit is set. It never
   emits `"SRAM"`.
2. `firestarter_app/firestarter/database.py:_map_data` lines 371-377 maps
   `"Flash" in type_str` → `determined_type = 2`. Any UV-EPROM that is
   electrically erasable (e.g. `W27C512`) gets `mem_type = 2` even though its
   `algorithm = 0x07`. Any SRAM chip gets `mem_type = 1` because the `"SRAM"`
   branch is unreachable.
3. `convert_to_programmer` (database.py line 493) sends `"type": 2` on the wire.
4. `firestarter/src/json_parser.c:get_type` (line 301) stores 2 into
   `handle->mem_type`.
5. `firestarter/src/proms/memory.cpp:configure_memory` lines 83-95 dispatch on
   `mem_type ∈ {1, 4, 3, 5}` only. `TYPE_FLASH_TYPE_2 = 2` is defined (line 25)
   but never dispatched — it falls through to the generic error at line 96.

Reach table by algorithm (BLOCKER-1, from the regenerated DB):

| algo | count tagged Flash/EEPROM | count tagged UV-EPROM | currently reaches handler? |
|------|---------------------------|-----------------------|----------------------------|
| 0x05 FLASH_AMD_STD     | 27   | 0   | NO — needs flash_type_4 |
| 0x06 FLASH_AMD_ALT     | 190  | 0   | NO — needs flash_type_3 |
| 0x07 EPROM_STD         | 30   | 207 | partial — only UV-EPROM-tagged ones reach configure_eprom |
| 0x08 EPROM_QUICK       | 21   | 106 | partial |
| 0x0B EPROM_LEGACY      | 9    | 44  | partial |
| 0x0D EEPROM_POLL       | 15   | 3   | YES (protocol-prefix dispatch already exists) |
| 0x10 FLASH_INTEL       | 39   | 0   | YES (protocol-prefix dispatch already exists) |
| 0x0E/0x27/0x28/0x29 SRAM | 0  | 52  | WRONG — routed to configure_eprom (BLOCKER-2: enables VPP regulator on 5V SRAM) |
| 0x35 FLASH_EEPROM_LIKE | (unknown — in KNOWN_PROTOCOLS, not separately enumerated by audit) | | NO — needs flash_type_4 |

## Goal

After this phase:

1. **Every protocol in `build_db.py:KNOWN_PROTOCOLS` reaches its correct
   firmware handler.** No falls through to "Memory type 0x%02x not supported".
2. **SRAM chips (0x0E/0x27/0x28/0x29) reach `configure_sram`** and never
   touch `configure_eprom`. The VPP boost regulator is never enabled on a
   5V SRAM.
3. **Firmware dispatch matches the contract documented in
   `firestarter/CLAUDE.md`** — algorithm-first, mem_type as legacy fallback only.

## Locked decisions

### D1 — Fix at BOTH layers (C++ primary, Python secondary)

The phase title presents an either/or: "extend memory.cpp protocol-prefix
dispatch OR fix database.py:_map_data". The choice is **both**, with C++ as
the architecturally aligned primary fix and Python as defense-in-depth.

**C++ (primary):** Extend `memory.cpp:configure_memory` to dispatch on
`handle->protocol` for **all** known protocols, not just `0x10` and `0x0D`.
This matches PROJECT.md "What Must Be TRUE" #3 ("Firmware dispatches on
algorithm, not type") and the dispatch table already documented in
`firestarter/CLAUDE.md`. Once landed, the `mem_type` fallback path is reached
only for chips with `protocol == 0` (unknown / legacy host).

**Python (secondary):** Fix `database.py:_map_data` to derive `mem_type` from
`algorithm`, not from `electrical.type` substring. This keeps the wire-level
`"type"` field consistent with the dispatch the firmware will take, and
prevents the bug from re-asserting if firmware is rolled back or a future
chip lacks an algorithm.

Why both: C++ alone is correct, but leaves a wire-protocol field (`type`)
permanently wrong for half the DB. Python alone perpetuates lossy mem_type
dispatch and contradicts the North Star. Doing both eliminates the
inconsistency at every layer.

**Why:** PROJECT.md North Star and firmware CLAUDE.md table both state that
algorithm is the primary dispatch key. The audit explicitly lists the C++
dispatch extension as the preferred fix option. The Python fix is small and
removes a class of future regressions.

**How to apply:** Researcher and planner should design the dispatch
extension as the centerpiece. The Python `_map_data` change is a single
table lookup and should land in the same phase but is the smaller half of
the work.

### D2 — C++ dispatch order (memory.cpp:configure_memory)

The dispatch order after this phase is:

```
1. protocol == 0x10           → configure_flash_intel(handle)      [existing]
2. protocol == 0x0D           → configure_eeprom28c(handle)         [existing]
3. protocol == 0x06           → configure_flash3(handle)            [new]
4. protocol ∈ {0x05, 0x35}    → configure_flash4(handle)            [new]
5. protocol ∈ {0x07,0x08,0x0B}→ configure_eprom(handle)             [new — was reached via mem_type==1]
6. protocol ∈ {0x0E,0x27,0x28,0x29} → configure_sram(handle)        [new — fixes BLOCKER-2]
7. mem_type == TYPE_EPROM (1) → configure_eprom(handle)             [fallback, kept]
8. mem_type == TYPE_SRAM (4)  → configure_sram(handle)              [fallback, kept]
9. mem_type == TYPE_FLASH_TYPE_3 (3) → configure_flash3(handle)     [fallback, kept]
10. mem_type == TYPE_FLASH_TYPE_4 (5)→ configure_flash4(handle)     [fallback, kept]
11. error: "Memory type 0x%02x not supported"
```

Steps 7-10 are unreachable for any chip in the regenerated DB (every chip has
a known protocol), but they are kept so older firmware-compatible host code
or hand-crafted JSON commands continue to work.

**Why:** Algorithm-first matches the documented contract in
`firestarter/CLAUDE.md`. Keeping mem_type as fallback costs nothing and
preserves backward compatibility for ad-hoc JSON commands.

**How to apply:** Planner should structure this as a single dispatch
function refactor — replace the existing if-chain with a switch on
`handle->protocol` that falls through to the mem_type chain when protocol
is 0 or not in the known set.

### D3 — Python algorithm→mem_type mapping (database.py:_map_data)

Replace the current substring branch in `_map_data` (lines 371-377) with
an algorithm-driven lookup. Reference table:

| algorithm | mem_type | firmware constant     |
|-----------|----------|------------------------|
| 0x05      | 5        | TYPE_FLASH_TYPE_4      |
| 0x06      | 3        | TYPE_FLASH_TYPE_3      |
| 0x07      | 1        | TYPE_EPROM             |
| 0x08      | 1        | TYPE_EPROM             |
| 0x0B      | 1        | TYPE_EPROM             |
| 0x0D      | 1        | TYPE_EPROM (firmware dispatches on protocol prefix; mem_type is just a hint) |
| 0x0E      | 4        | TYPE_SRAM              |
| 0x10      | 1        | TYPE_EPROM (firmware dispatches on protocol prefix; mem_type is just a hint) |
| 0x27      | 4        | TYPE_SRAM              |
| 0x28      | 4        | TYPE_SRAM              |
| 0x29      | 4        | TYPE_SRAM              |
| 0x35      | 5        | TYPE_FLASH_TYPE_4      |
| 0x39      | (whatever current behavior produces; not enumerated in audit — research it before committing) | — |

Fallback when `algorithm == 0` or absent: retain the legacy substring
behavior so any user-override DB without an `algorithm` field still works.

**Why:** Aligns the wire `"type"` field with the firmware dispatch path the
chip will actually take. Removes the brittle substring matching.

**How to apply:** Planner: place the constant table at module top in
`database.py`. Keep the substring fallback under `if not protocol_id:`.
The `info_flags` derivation at lines 384-387 (which sets
`0x00000010 Can be electrically erased` when `electrical.type ==
"Flash/EEPROM"`) is correct and independent — leave it alone.

### D4 — BLOCKER-2 (SRAM) is IN SCOPE

The phase title explicitly lists `0x0E/0x27/0x28/0x29`. SRAM dispatch fix
ships in this phase via D2 step 6 and D3 SRAM rows.

Additionally, `build_db.py` line 214 must learn to emit `"electrical.type":
"SRAM"` when the minipro XML record corresponds to an SRAM-family protocol.
This keeps the DB self-consistent (today an `electrical.type` of `"UV-EPROM"`
on a 6116 SRAM is actively misleading).

**Recommended SRAM detection rule:** if `proto_id ∈ {0x0E, 0x27, 0x28, 0x29}`
then `electrical.type = "SRAM"`. This is more specific than the current
`flags & 0x10` heuristic and avoids broken fallbacks.

**Why:** Hardware-stress hazard. Sending a UV-EPROM programming sequence to
a 5V SRAM enables the VPP boost regulator and applies 12V+ to a part that
cannot tolerate it.

**How to apply:** Planner should treat the SRAM tagging fix in `build_db.py`
and the SRAM dispatch case in `memory.cpp` as a single task; they only land
correctly together.

### D5 — WARNING-5 (AT28C256 algo=0x07 in upstream DB) is OUT OF SCOPE

Upstream minipro tags AT28C256 with `algorithm = 0x07` (EPROM_STD), not
`0x0D` (EEPROM_POLL). The audit flags this as WARNING-5. Fixing it
requires a per-chip algorithm override layer in `build_db.py` — a small
table of `(manufacturer, part_number) → algorithm` overrides — which is a
distinct concern from BLOCKER-1.

After Phase 12 lands, the AT28C256 path will be:

- algo=0x07 (from upstream XML)
- mem_type=1 (TYPE_EPROM, via D3 table)
- firmware dispatch: protocol-prefix 0x07 → `configure_eprom`
- result: configure_eprom runs the UV-EPROM init on an AT28C256, including
  `eprom_check_vpp` which would assert 12-13V VPP on a 5V part.

This is the existing hazard, unchanged by Phase 12. **Defer** to a future
phase that introduces the override table. Document it in
`firestarter_app/CLAUDE.md` as a known limitation if not already there.

**Why:** Different cause, different fix surface. Mixing them in this phase
expands scope to "decide override table policy" which is a separate
design question.

**How to apply:** Researcher should not propose override-table designs in
RESEARCH.md. Planner should not include AT28C remap in PLAN.md. Add to
Deferred Ideas at the bottom of this document.

### D6 — Protocol 0x35 (FLASH_EEPROM_LIKE) is IN SCOPE

`0x35` appears in `KNOWN_PROTOCOLS` and in `firestarter/CLAUDE.md`'s table
as routing to `flash_type_4`. The audit BLOCKER-1 table does not enumerate
0x35 separately, but any 0x35 chip in the DB would hit the same fall-
through. Include the `0x35 → flash_type_4` dispatch case in D2 and the
`0x35 → 5` row in D3.

If the regenerated DB contains zero `0x35` chips today, the dispatch case
costs nothing and prevents a future regression.

### D7 — Verification approach (no hardware available)

Hardware verification is out of scope for this phase (separate hardware-
test phase). Verification in scope:

1. **JSON output spot-checks:** For one representative chip per protocol,
   call `EpromDatabase.get_eprom(name)` then `convert_to_programmer(...)`
   and assert the emitted JSON has the expected `type` and `algorithm`
   integer pair. Suggested chips: `W27C512` (0x07), `27C040` (0x08),
   `M2764A` (0x0B), `AM29F040` (0x06), `SST39SF040` (0x06), one 0x05 chip,
   one 0x10 chip, `AT28C256` (0x0D), `6116` (0x27), `DS1245AB` (0x0E),
   any 0x35 chip if present.

2. **Firmware build:** `pio run -e uno` and `pio run -e leonardo` build
   clean. Binary size delta documented (additional switch cases will cost
   a few hundred bytes on AVR).

3. **Firmware unit test:** Add a `pio test` case for
   `configure_memory` dispatch — for each protocol, set up a minimal
   `firestarter_handle_t` (just `protocol`, `mem_type`, `pins`, `cmd`)
   and assert that the corresponding `firestarter_operation_init` pointer
   is non-NULL after `configure_memory`. (The test does not need to run
   the handler — just confirm it was wired.) If the existing test harness
   makes per-handler mocking awkward, fall back to a simpler check: that
   `configure_memory` does not emit the error string.

4. **Regression scan:** Re-run `_map_data` over every chip in
   `minipro_complete_db.json` and confirm the resulting `(type, algorithm)`
   pair has a valid dispatch path in the firmware table. Fail the test if
   any chip would still hit "Memory type 0x%02x not supported".

**Why:** No hardware in this dev environment. The audit's BLOCKER-1 is a
wiring problem, not an algorithm-correctness problem — wiring can be
verified statically. Hardware verification waits for a follow-up phase.

**How to apply:** Planner: include the JSON spot-checks and the regression
scan as automated tests in `firestarter_app/`. The firmware build check is
a CI smoke test. The unit-test addition is one new file under
`firestarter/test/`.

## Canonical refs

Downstream agents MUST read these before researching/planning. Full
relative paths.

- `.planning/PROJECT.md` — Project North Star ("Firmware dispatches on
  algorithm, not type"); list of in-scope chip families.
- `.planning/REQUIREMENTS.md` — REQ-FW-01, REQ-FW-02, REQ-FW-03, REQ-FW-04,
  REQ-SER-01 (all partially satisfied; reach gated by BLOCKER-1).
- `.planning/v1.0-MILESTONE-AUDIT.md` — full BLOCKER-1 / BLOCKER-2 detail,
  reach table by algorithm, fix options enumerated.
- `.planning/INTEGRATION-CHECK.md` — line-numbered trace through
  `_map_data` → `convert_to_programmer` → `json_parser.c:get_type` →
  `memory.cpp:configure_memory`. The integration check's "Where it breaks"
  section is the single best technical reference for the bug.
- `.planning/codebase/ARCHITECTURE.md` — overall layered architecture and
  data-flow diagram.
- `firestarter/CLAUDE.md` — firmware dispatch order (already documents the
  target post-Phase-12 dispatch table); REQ-SAF / REQ-FW notes.
- `firestarter_app/CLAUDE.md` — Python pipeline, wire-protocol JSON schema,
  KNOWN_PROTOCOLS list.
- `firestarter/src/proms/memory.cpp` — current `configure_memory` dispatch
  (lines 45-97); `TYPE_FLASH_TYPE_2` orphan constant at line 25.
- `firestarter/src/json_parser.c` — `get_type` (line 301), `get_algorithm`
  (lines 312-314) — where `handle->mem_type` and `handle->protocol` are
  populated.
- `firestarter/include/firestarter.h` — `firestarter_handle_t` struct;
  `mem_type` field at line 80.
- `firestarter_app/firestarter/database.py` — `_map_data` (lines 343-414),
  `convert_to_programmer` (lines 479-510+); the `determined_type`
  substring logic at lines 371-377.
- `firestarter_app/tools/build_db.py` — chip emission (lines 211-231);
  `electrical.type` rule at line 214; `KNOWN_PROTOCOLS` at line 89.
- `.planning/phases/05-intel-flash/05-CONTEXT.md` and
  `.planning/phases/06-eeprom-page-write/06-CONTEXT.md` — prior
  protocol-prefix dispatch additions for 0x10 and 0x0D. **The pattern
  established by those phases is the model for Phase 12.**

## Reusable assets / code context

- **Existing protocol-prefix dispatch pattern** at `memory.cpp:73-81`
  (0x10 and 0x0D handlers) is exactly the shape the new cases should take.
  No new abstraction needed.
- **Existing `configure_eprom`, `configure_sram`, `configure_flash3`,
  `configure_flash4` handlers** are all already wired and tested for their
  reachable subsets. Phase 12 makes them reachable for the chips that
  currently fall through — no handler-internal changes required.
- **`KNOWN_PROTOCOLS` set in `build_db.py:89`** is the authoritative
  source for which protocols this project officially supports. The C++
  dispatch and Python mem_type table must cover exactly this set (plus
  `0x39` which is in the set but not enumerated in this CONTEXT.md —
  researcher should determine its target handler before committing).
- **`memory.cpp:25-28` constants** (`TYPE_FLASH_TYPE_2`, `TYPE_FLASH_TYPE_3`,
  `TYPE_FLASH_TYPE_4`) — `TYPE_FLASH_TYPE_2` is unused/orphan after this
  phase. Recommend deleting it in the same commit to remove the dead
  constant.

## Out of scope

Explicitly OUT of this phase (capture, do not act):

- **WARNING-5 / AT28C256 algorithm override** — upstream DB tags AT28C256
  with 0x07. Fix is a per-chip override table in `build_db.py`. Future phase.
- **WARNING-1 / Intel flash VPP ADC check** — `flash_intel_write_init` is
  missing the `rurp_read_voltage_mv` ADC compare that the UV-EPROM path
  has. REQ-SAF-01 follow-up. Future phase.
- **WARNING-2 / EEPROM_POLL chip-ID validation** — `eeprom_28c.cpp`
  ignores `handle->chip_id`. Vacuous today (no 0x0D chip has chip_id
  populated). Forward-compat hazard. Future phase.
- **WARNING-3 / Rename wire JSON key `vpp` → `vpp_mv`** — overloaded key
  meaning. Future phase, requires firmware + Python coordination.
- **WARNING-4 / `firestarter_test.sh` and `write_test.sh` references to
  deleted `database_generated.json`** — already tracked in
  `11-VERIFICATION.md` follow_ups.
- **VERIFICATION.md backfill for Phases 01-10** — the audit headline.
  Future audit phase.
- **Sector-erase CLI exposure for 0x05 flash_type_4** — if 0x05 chips can
  do sector erase, Phase 04 only exposed it for 0x06 (flash_type_3).
  Future phase if needed.
- **Hardware verification of the fix** — no hardware in this environment.
  Future hardware-test phase (likely after Phase 12 lands and a programmer
  is available).
- **Dropping the `mem_type` field from the wire protocol entirely** — the
  North Star direction, but a backward-incompatible wire change. Defer.

## Deferred ideas

The following came up during analysis and are noted for the roadmap
backlog, not for Phase 12:

- Per-chip algorithm override table in `build_db.py` for upstream-mis-
  tagged chips (AT28C256 is the canonical example; there may be others).
- VPP ADC validation in the Intel-flash write path (REQ-SAF-01 closure).
- Reverse-translation utility: given a `mem_type` (legacy host JSON), pick
  a plausible protocol — useful for fuzz-test reproducibility but not for
  production.
- Stricter `KNOWN_PROTOCOLS` enforcement in `_map_data` (warn or refuse
  to emit a chip whose algorithm is not in the set).

## Acceptance criteria for Phase 12

This is what "done" looks like — researcher and planner should drive the
plan back to this list.

1. Every chip in the regenerated `minipro_complete_db.json` has a
   `(type, algorithm)` pair whose firmware dispatch path is to a real
   handler (not the "Memory type 0x%02x not supported" branch). Confirmed
   by a regression scan that iterates the entire DB.
2. SRAM-protocol chips (0x0E/0x27/0x28/0x29) reach `configure_sram` and
   never `configure_eprom`. Confirmed by JSON spot-check and dispatch
   trace.
3. `firestarter/src/proms/memory.cpp:configure_memory` dispatches on
   `handle->protocol` first for the full `KNOWN_PROTOCOLS` set; the
   `mem_type` branch is a fallback only.
4. `firestarter_app/firestarter/database.py:_map_data` derives `mem_type`
   from `algorithm` via an explicit table; the `electrical.type` substring
   branch runs only when `algorithm == 0` or absent.
5. `firestarter_app/tools/build_db.py` emits `electrical.type = "SRAM"` for
   SRAM-protocol chips (D4 detection rule).
6. `TYPE_FLASH_TYPE_2 = 2` orphan constant is removed from
   `memory.cpp`.
7. Both firmware targets (`pio run -e uno` and `pio run -e leonardo`)
   build clean. Binary-size delta documented.
8. `firestarter/CLAUDE.md` dispatch table is updated to match the new
   `configure_memory` order if anything differs from the table currently
   documented (it should be a near-match already).
9. Hardware verification is NOT a Phase 12 acceptance criterion — gated to
   a follow-up phase.

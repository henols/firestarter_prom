# Architecture Research

**Domain:** Test-first programming-algorithm validation harness for a dual-repo (Arduino C++ firmware + Python host CLI) EPROM/Flash/EEPROM/SRAM programmer (v1.13)
**Researched:** 2026-06-16
**Confidence:** HIGH (grounded in the actual v1.12 codebase — `memory.cpp`, `eprom.cpp`, `flash_utils.cpp`, `sram.cpp`, `eprom_operations.py`, `chip_resolver.py`, `check_dispatch.py`, `platformio.ini [env:native]`, existing native Unity suites)

> **Scope note (per milestone_context):** the dispatch + handler + DB + transport architecture already exists and is NOT re-researched here. This document answers *where the validation harness plugs into that existing architecture* and *how the new components are layered/ordered* so per-family fixes and adapter-required additions land without regressing the other families or busting the Leonardo flash ceiling.

---

## Standard Architecture

The v1.13 validation surface is a **three-tier test pyramid** stacked on the existing stack. Tiers 1–2 are pure software (no bench gate); Tier 3 is the hybrid bench-gated layer. Nothing here adds a new firmware code path on the production write/program/verify route — the harness *exercises and observes* the routes that already ship.

### System Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│  TIER 3 — Hardware-in-the-Loop (HIL) bench layer  [HYBRID-GATED]           │
│  host-driven; produces the per-family pass/fail VALIDATION MATRIX          │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │  family_validation.py  (new host harness, dev-group CLI)           │    │
│  │   per family: erase→write golden→read-back→SHA compare             │    │
│  │   reuses write_cycle_eprom / consistency_check_eprom verbatim      │    │
│  │   emits  validation-matrix.json + .md  (family × verdict)          │    │
│  └───────────────┬───────────────────────────────┬──────────────────┘    │
│                  │ real serial (COBS+CRC8, 250k)  │ golden vectors          │
├──────────────────┼───────────────────────────────┼─────────────────────────┤
│  TIER 2 — Host software tests  [NO BENCH GATE]    │  (pytest)               │
│  ┌──────────────┴──────────┐  ┌──────────────────┴───────────────────┐    │
│  │ MockSerial round-trip    │  │ check_dispatch.py / diff_db.py        │    │
│  │ of the per-family wire    │  │ GATE: per-family dispatch invariants  │    │
│  │ dict (state machine over  │  │  (defense-in-depth, the regression    │    │
│  │  a fake transport)        │  │   firewall for cross-family bugs)     │    │
│  └──────────────────────────┘  └───────────────────────────────────────┘    │
├──────────────────────────────────────────────────────────────────────────────┤
│  TIER 1 — Native Unity firmware tests  [NO BENCH GATE]  (pio test -e native)   │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ test/native/avr/test_<family>/  — algorithm-level unit tests with mocked  │ │
│  │ bus (ArduinoFake + host_stubs.cpp). One suite per family. Asserts         │ │
│  │ op-pointer wiring + control-register call SEQUENCE on a recording stub —  │ │
│  │ never real hardware.                                                      │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────┤
│  EXISTING PRODUCTION STACK (unchanged route; observed, not replaced)           │
│  configure_memory dispatch → configure_<family> → flash_utils helpers          │
│  ↑ resolve_chip(support_status guard) → convert_to_programmer → wire dict       │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | New / Modified | Lives in |
|-----------|----------------|----------------|----------|
| `test/native/avr/test_<family>/` Unity suites | Algorithm-level unit tests: assert each `configure_<family>` wires the correct op pointers AND drives the expected control-register sequence on a **recording** bus stub | NEW (one per family; extends the existing `test_dispatch` pattern) | firmware sub-repo |
| `test/native/avr/_shared/` recording stub | A `host_stubs.cpp` variant that *records* `rurp_*` register writes into a sequence buffer (instead of no-op) so a fix can be asserted by side-effect, not just by pointer | NEW (extends `_shared/host_stubs_common.inc`) | firmware sub-repo |
| `validation_harness.py` HIL orchestration | Pure-logic family runner: for each in-scope family, erase→write golden→read-back→SHA-compare; record verdict + evidence dir; serialize matrix | NEW (module, unit-testable without serial) | host sub-repo |
| `dev validate-family` CLI sub-command | Thin Click handler invoking `validation_harness` on a real `SerialCommunicator` | NEW (extends the `dev` group) | host sub-repo |
| `validation-matrix.{json,md}` | The per-chip-family pass/fail matrix artifact (family, representative chip, board, verdict, evidence path, SHA) | NEW (generated artifact) | host repo `tests/golden/` + `.planning/v1.13/` |
| `check_dispatch.py` GATE | Defense-in-depth regression firewall: every per-family fix must keep ALL dispatch invariants green (SRAM-never-to-eprom, no-vpp-pin guard, support_status inverse guard) | MODIFIED (per-family assertions; populate the hollow `non_supported_dispatchable`) | host repo `tools/` |
| `diff_db.py` GATE | Per-chip DB diff vs pinned baseline — catches any adapter-required addition that perturbs an unrelated chip | MODIFIED (re-baseline after each DB change) | host repo `tools/` |
| `resolve_pinout_key` (build_db.py) | Pure `(pin_count, proto_id, mem_size)` → pinout-key function + explicit safety overrides; adapter-required chips integrate as **new rule arms**, NOT resurrected tables | MODIFIED (add adapter-required arms) | host repo `tools/` |
| `chip_resolver.resolve_chip` | Authoritative host guard: refuses any non-`supported` chip before a serial byte. Adapter-required chips flip `support_status: supported` only when pinout + handler genuinely work | EXISTING (changes only when a chip graduates) | host repo |
| `eprom_operations.py` cycle methods | `write_cycle_eprom` (erase→write→read-back×N→SHA) + `consistency_check_eprom` (read×N→SHA) are the reusable bench primitives the HIL harness composes | EXISTING (reuse verbatim — do NOT fork) | host repo |

---

## Recommended Project Structure

```
firestarter/                                  # FIRMWARE sub-repo
├── src/proms/
│   ├── memory.cpp                            # dispatch (existing) — fixes land in handlers, not here
│   ├── eprom.cpp / flash_type_3.cpp /        # per-family handlers — per-family correctness fixes here
│   │   flash_type_4.cpp / flash_intel.cpp /
│   │   eeprom_28c.cpp / sram.cpp
│   └── flash_utils.cpp                        # shared DQ7-poll / byte-flip helpers
└── test/native/avr/
    ├── _shared/
    │   ├── host_stubs_common.inc              # existing shared stub include
    │   └── recording_bus_stub.inc             # NEW: records rurp_* register-write sequence
    ├── test_dispatch/                         # existing — dispatch-level (keep green)
    ├── test_eprom_algo/                       # NEW: UV-EPROM write/verify sequence asserts
    ├── test_flash3_algo/                      # NEW: AMD unlock/sector-erase sequence asserts
    ├── test_flash4_algo/                      # NEW: page-write + DQ7 sequence asserts
    ├── test_flash_intel_algo/                 # NEW: command-register + SR-poll sequence asserts
    ├── test_eeprom28c_algo/                   # NEW: SDP-disable + page-poll sequence asserts
    └── test_sram_algo/                        # NEW: read/write, NO VPP-regulator assert (BLOCKER-2)

firestarter_app/                              # HOST sub-repo
├── firestarter/
│   ├── eprom_operations.py                   # reuse write_cycle_eprom / consistency_check_eprom
│   ├── chip_resolver.py                      # support_status guard (existing)
│   └── validation_harness.py                 # NEW: family-matrix orchestration (pure logic, testable)
├── tools/
│   ├── build_db.py                           # resolve_pinout_key + adapter-required arms (MODIFIED)
│   ├── check_dispatch.py                     # defense-in-depth gate (MODIFIED: per-family + inverse)
│   └── diff_db.py                            # per-chip diff vs baseline (MODIFIED: re-baseline)
└── tests/
    ├── test_validation_harness.py            # NEW: MockSerial round-trip per family (Tier 2)
    ├── test_check_dispatch_families.py        # NEW: per-family dispatch invariant assertions
    └── golden/
        ├── validation-matrix.json            # NEW: generated family pass/fail matrix
        └── family-vectors/                   # NEW: per-family golden write images + expected read-back

.planning/v1.13/
└── bench-verification/                       # HIL evidence dirs (SHA runs, matrix .md) — operator-witnessed
```

### Structure Rationale

- **One Unity suite per family (`test_<family>_algo/`):** mirrors the proven `test_dispatch/` + `test_flash_intel_vpp/` + `test_eeprom28c_chip_id/` pattern already in `[env:native]`. PlatformIO auto-discovers any `test_*.cpp` under `test/native/avr/<dir>/`; adding a suite needs only a `test_filter`/`-I` line, not an env redesign (per firmware CLAUDE.md "Reuse pattern for future native tests"). Family isolation means a fix to `eprom.cpp` cannot silently change another family's suite.
- **Recording bus stub in `_shared/`:** today `host_stubs.cpp` is *no-op* — sufficient for dispatch tests that assert only `response_code`/op-pointers. Algorithm-correctness validation needs to assert *what the handler did* (e.g. SRAM must NEVER set `CTRL_VPP_REGULATOR_ENABLE`; EPROM_STD must set `CTRL_VPP_VPE_DROP_ENABLE`). A recording stub captures the register-write sequence so a fix is provable host-side, pre-bench.
- **Harness logic split from CLI (`validation_harness.py` + `dev` sub-command):** keeps orchestration pure-functional and unit-testable under pytest (Tier 2) without serial I/O, matching the v1.8 STRUCT pattern (logic in modules, thin CLI handlers). The bench run is the same logic with a real `SerialCommunicator`.
- **Matrix as a committed artifact (`tests/golden/validation-matrix.json`):** makes "which families are proven on hardware" a versioned, diffable fact — the milestone can close at partial coverage (hybrid gating) with the matrix recording exactly which families are bench-proven vs deferred-for-parts.
- **Adapter-required arms in `resolve_pinout_key`, NOT new tables:** v1.11 Phase 58 *deleted* `PIN_MAP_*`/`DIP28_VARIANT_MAP` guess tables and rebuilt `resolve_pinout_key` as a pure function with three explicit safety overrides. Adapter-required chips must extend that function as **named rule arms** (same shape as the WARNING-5 / fm1608 / 24-pin-EEPROM overrides), never by reintroducing a lookup table.

---

## Architectural Patterns

### Pattern 1: Test-first family validation (RED → bench → fix → GREEN)

**What:** For each family, write the Tier-1 algorithm assertion + Tier-2 wire round-trip BEFORE touching the handler. The bench run (Tier 3) reveals whether the *real* hardware agrees with the asserted sequence; a divergence becomes a failing test that the per-family fix turns green.
**When to use:** every family in the milestone — this is the milestone's core method ("let evidence define what missing means").
**Trade-offs:** more upfront test scaffolding; in return, no fix ships without a regression net, and the matrix is honest about coverage.

**Example (recording-stub Unity assertion — SRAM electrical-safety invariant):**
```cpp
// test_sram_algo/test_sram_no_vpp.cpp
void test_sram_write_never_enables_vpp_regulator(void) {
    reset_register_recorder();
    firestarter_handle_t h = make_handle(0x28 /*SRAM_STD*/, 0, CMD_WRITE);
    configure_memory(&h);                       // dispatch → configure_sram
    if (h.firestarter_operation_main) h.firestarter_operation_main(&h);
    TEST_ASSERT_FALSE(recorder_saw_bit_set(CTRL_VPP_REGULATOR_ENABLE)); // BLOCKER-2
}
```
> Note: `configure_sram` is currently a bare stub (`sram.cpp` only logs). The Tier-1 SRAM suite both documents the *required* read/write behaviour and pins the safety invariant — a likely per-family fix candidate the bench will expose.

### Pattern 2: Golden write+read-back, host-side independent compare

**What:** The harness never trusts the firmware's own verify. It writes a known golden image, then performs an independent host-side read-back and SHA-256 compares against the source image — exactly the `write_cycle_eprom` contract (3-way verdict: PASS / mismatch / hw-error; hw-error is never collapsed to mismatch).
**When to use:** every Tier-3 family run.
**Trade-offs:** doubles bench time (write + read); in return, catches firmware-verify blind spots (a buggy `memory_verify_execute` cannot mask a bad write).

**Data-flow:**
```
golden image (family-vectors/<family>.bin)
   → erase_eprom → write_eprom (production state machine, COBS+CRC8)
   → read-back via _main_phase_read_data → cycle_NN_readback.bin
   → SHA-256(readback) == SHA-256(golden)?  → matrix cell verdict
```

### Pattern 3: Defense-in-depth dispatch gate as the cross-family firewall

**What:** `check_dispatch.py` already simulates `memory.cpp` dispatch over all 744 chips and asserts family invariants (SRAM never → `configure_eprom`; no chip on a no-vpp-pin pinout → `configure_eprom`; WARNING-5 type-keyed guard). Every per-family fix and every adapter-required addition must keep this gate at zero violations. It is the structural equivalent of "fix one family without breaking the others."
**When to use:** as a CI gate on every DB or dispatch change (it runs without hardware).
**Trade-offs:** the gate is a *mirror* of firmware dispatch order — it must be updated in lockstep with `memory.cpp` (drift = false confidence). v1.13 should also **populate the hollow `non_supported_dispatchable` detector** (accepted tech debt from v1.12) so the inverse guard is real, not asserted-empty.

```python
# extend check_dispatch.py — per-family invariant (illustrative)
assert dispatch(0x0E, mem_type) == "configure_sram"   # SRAM family
assert dispatch(0x10, mem_type) == "configure_flash_intel"
# inverse guard (populate, don't just assert-empty):
if support_status != "supported" and dispatch(proto, mt) != "not_implemented":
    non_supported_dispatchable.append(part)
```

### Pattern 4: Flash-budget-gated firmware additions

**What:** Leonardo is the tight board (v1.12 closed with Uno at 72.4% flash; the milestone names ~88% Leonardo). Native Unity tests cost ZERO production flash (they compile under `[env:native]` on the host, excluded from `uno`/`leonardo` builds via `build_src_filter`). Therefore the *test harness itself is flash-free*; only actual handler fixes and adapter-required handler code consume the budget.
**When to use:** every firmware change — measure `pio run -e leonardo` size before/after.
**Trade-offs:** prefer fixing existing handlers (often net-neutral or net-negative on flash) over adding code; defer any adapter-required family whose handler would breach the ceiling.

---

## Data Flow

### Validation-matrix generation flow (Tier 3)

```
[operator: bench available, family chip seated on Leonardo]
        ↓
firestarter dev validate-family --family eprom --golden W27C512.bin --port /dev/ttyACM0
        ↓
validation_harness.run_family()
   → resolve_chip(rep_chip)           # support_status guard; refuses non-supported in-host
   → erase_eprom / write_eprom        # production COBS+CRC8 state machine
   → read-back (_main_phase_read_data)
   → SHA-256 compare (host-side)
        ↓
matrix cell: {family, chip, board, verdict, evidence_dir, sha}
        ↓
write validation-matrix.json (+ render .md)   # committed; partial coverage OK
```

### Per-family fix flow (software-first, bench-on-hand)

```
1. Tier-1 Unity assert + Tier-2 wire round-trip written  → RED (no bench)
2. Bench run (Tier 3) on hand                            → observed divergence
3. Fix handler (eprom.cpp / flash_*.cpp / sram.cpp ...)  → measure Leonardo flash
4. check_dispatch.py + diff_db.py + native suites green  → defense-in-depth
5. Re-bench                                              → matrix cell PASS
```

### Adapter-required integration flow

```
infoic.xml row (genuinely unmappable pinout)
   → resolve_pinout_key: add NAMED rule arm (NOT a resurrected table)
   → build_db.py emits support_status:
       adapter-required  (stays refused in-host) — until adapter exists + bench-proven
       supported         (graduates) — ONLY when pinout+handler verified on the adapter
   → diff_db.py re-baseline (per-chip diff acknowledged)
   → check_dispatch.py: chip must dispatch to a real handler with zero hazard
```

### Key Data Flows

1. **Golden vectors are the contract:** a small committed `family-vectors/<family>.bin` per family is both the write source and the SHA reference — the harness compares against it, not against the chip's own verify pass.
2. **support_status is the single gate for "may we drive hardware":** the matrix records a family as bench-proven only after the representative chip is `supported` AND a golden write+read-back round-trips byte-identical.

---

## Scaling Considerations

(Not a user-scale system — "scale" here = number of families/chips/boards in the validation matrix.)

| Scale | Architecture adjustments |
|-------|--------------------------|
| 6 families, 1 board (Leonardo), 1 chip each | Single matrix file; harness loops families; hybrid gating defers parts-missing families |
| +adapter-required chips | matrix gains rows; each adapter is a `resolve_pinout_key` arm + a deferred cell until the adapter is built/bench-proven |
| Multi-board (Uno / uno328pb / Leonardo) | matrix becomes family × board grid; per-board buffer size (512/1024) already handled by `_calculate_buffer_size`; **Leonardo is the trustworthy verify board** — uno328pb program-brownout + Rev-0/2.0 read faults stay out of the verify path |

### Scaling Priorities

1. **First bottleneck — Leonardo flash ceiling:** ~88% at v1.12. Adding adapter-required handler code is the first thing that breaks the firmware build. Mitigation: fix-don't-add where possible; gate every firmware change on `pio run -e leonardo` size; defer flash-heavy families.
2. **Second bottleneck — bench availability:** Tier 3 needs chips + a working shield. Mitigation: hybrid gating — software tiers run always; the matrix closes at partial coverage with explicit deferred cells.

---

## Anti-Patterns

### Anti-Pattern 1: Forking a parallel read/write implementation for the harness

**What people do:** write a fresh read/write loop inside the validation harness "to keep it clean."
**Why it's wrong:** the bug being validated lives in the production path; a parallel implementation validates the wrong code. `eprom_operations.py` explicitly forbids this ("Do NOT refactor into a parallel read implementation" — `consistency_check_eprom`, `write_cycle_eprom`).
**Do this instead:** compose `write_cycle_eprom` / `consistency_check_eprom` / `_run_state_machine` verbatim.

### Anti-Pattern 2: Resurrecting deleted pinout guess-tables for adapter-required chips

**What people do:** re-add a `DIP28_VARIANT_MAP`-style lookup to "quickly" map an adapter chip's pins.
**Why it's wrong:** v1.11 Phase 58 deliberately deleted those tables and rebuilt `resolve_pinout_key` as a pure function. A new table reintroduces the guessing the whole pipeline was rebuilt to eliminate, and bypasses the safety-override structure.
**Do this instead:** add a named rule arm to `resolve_pinout_key` (same shape as WARNING-5 / fm1608 / 24-pin-EEPROM overrides), with a comment citing the adapter and the hazard it guards.

### Anti-Pattern 3: Asserting only firmware-verify success as proof of a good write

**What people do:** treat a clean firmware `VERIFY` as proof the family works.
**Why it's wrong:** a bug in `memory_verify_execute` (or a write that the same buggy path mis-reads consistently) can pass self-verify while the data is wrong.
**Do this instead:** independent host-side SHA-256 read-back compare against the golden source (the `write_cycle_eprom` D-06 pattern).

### Anti-Pattern 4: Adding native test code without checking it stays out of the production build

**What people do:** drop test helpers into `src/proms/` or include them outside `[env:native]`.
**Why it's wrong:** anything under `build_src_filter = +<proms/>` links into the Leonardo image and eats the flash ceiling.
**Do this instead:** keep all harness/recording-stub code under `test/native/avr/` — it compiles only for `pio test -e native` and costs zero production flash.

### Anti-Pattern 5: Letting `check_dispatch.py` drift from `memory.cpp`

**What people do:** fix `memory.cpp` dispatch order and forget the Python mirror.
**Why it's wrong:** the gate then validates a stale dispatch model — false green.
**Do this instead:** treat the `dispatch()` mirror in `check_dispatch.py` as a lockstep artifact; update it in the same commit as any `memory.cpp` dispatch change (the file header already mandates "must match line-for-line").

---

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| RURP shield over serial | COBS `0x00` + CRC8 framing, 250000 baud, INIT→MAIN→END state machine | Already byte-exact (v1.10); the harness rides it unchanged. Verify port identity per task (ACM* numbers shuffle); chip-out before sideload on Uno-class only |
| minipro `infoic.xml` | `build_db.py` fetch + decode | Adapter-required arms decode here; pinned baseline via `diff_db.py` |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| host harness ↔ firmware | JSON command (`algorithm` primary dispatch key) → tagged responses | Dual-repo lockstep; any new wire field needs both `constants.py` + `firestarter.h` |
| Tier-1 Unity ↔ handlers | direct C++ link under `[env:native]`, ArduinoFake + recording stub | No serial; asserts op-pointers + register sequence |
| Tier-2 pytest ↔ state machine | `MockSerial` / fake transport into `_run_state_machine` | No hardware; validates wire dict per family |
| `resolve_chip` guard ↔ everything | `support_status != "supported"` → `ChipNotImplementedError` before any byte | Authoritative host safety layer; the matrix's "may drive hardware" gate |
| `check_dispatch.py` ↔ `memory.cpp` | hand-maintained dispatch mirror | Lockstep — drift is a bug |

---

## Suggested Build Order (dependency- + flash- + bench-ordered)

The order is driven by three constraints: (a) harness-before-validate-before-fix-before-gaps; (b) software-first so bench time is spent on proven-RED divergences; (c) flash-free work (tests, host) before flash-consuming work (handler fixes, adapter handlers) since Leonardo is the ceiling.

1. **Harness scaffolding (software, zero flash):**
   - Tier-1 recording bus stub in `test/native/avr/_shared/` + one `test_<family>_algo/` suite per family (RED where the algorithm assertion is unproven; SRAM stub is the obvious early RED).
   - Tier-2 `validation_harness.py` + `test_validation_harness.py` (MockSerial round-trip per family).
   - Tier-3 `family_validation.py` (`dev validate-family`) composing `write_cycle_eprom`/`consistency_check_eprom`; matrix serializer.
   - Extend `check_dispatch.py` with per-family invariants + **populate the hollow `non_supported_dispatchable`** inverse guard.
2. **Re-research the protocol landscape** (revisit v1.12's "feasible set complete"; surface real gaps e.g. the deferred erase path) — feeds which adapter-required arms / fixes are in scope.
3. **Validate families on bench (hybrid-gated):** run Tier-3 per family with chips on hand on **Leonardo**; record matrix cells; defer parts-missing families with an explicit reason. This step *produces the evidence* that defines steps 4–5.
4. **Per-family correctness fixes (flash-gated):** fix only families the bench showed divergent. Each fix: turn the RED Tier-1/2 test GREEN → measure `pio run -e leonardo` → keep `check_dispatch.py`/`diff_db.py`/native suites green → re-bench. Order families lightest-flash-impact first; defer any fix that would breach the ceiling pending a budget reclaim.
5. **Adapter-required chip support (flash-gated, hardware-gated):** add `resolve_pinout_key` arms (no tables); chips stay `adapter-required` (refused in-host) until the physical adapter exists AND a golden write+read-back round-trips on it, at which point they graduate to `supported` and gain a matrix cell. Any new handler code is the last flash consumer — gate hardest here.

**Flash-budget flag for the roadmap:** steps 1–3 are flash-free (tests + host + bench observation). Steps 4–5 are the only flash consumers; the Leonardo ~88% ceiling is the build-order driver that forces fixes-before-additions and makes adapter-required families the natural deferral candidates.

---

## Sources

- `firestarter/src/proms/memory.cpp`, `eprom.cpp`, `flash_utils.cpp`, `sram.cpp`, `not_implemented.cpp`, `eeprom_28c.cpp` (firmware dispatch + handlers + shared helpers) — HIGH
- `firestarter/platformio.ini [env:native]` + `firestarter/CLAUDE.md` "Native (Host) Test Environment" / "Reuse pattern for future native tests" — HIGH
- `firestarter/test/native/avr/test_dispatch/` (existing Unity + host-stub pattern) — HIGH
- `firestarter_app/firestarter/eprom_operations.py` (`write_cycle_eprom`, `consistency_check_eprom`, `_run_state_machine`, `_main_phase_read_data`) — HIGH
- `firestarter_app/firestarter/chip_resolver.py` (support_status guard / `ChipNotImplementedError`) — HIGH
- `firestarter_app/tools/check_dispatch.py` (dispatch mirror + GATE-03 + hollow `non_supported_dispatchable`) — HIGH
- `.planning/PROJECT.md` v1.13 milestone + Key Decisions (Phase 58 `resolve_pinout_key` rewrite, v1.12 hollow gate tech debt, Leonardo flash budget, hybrid bench gating, Leonardo-as-verify-board) — HIGH

---
*Architecture research for: programming-algorithm validation harness (Firestarter v1.13)*
*Researched: 2026-06-16*

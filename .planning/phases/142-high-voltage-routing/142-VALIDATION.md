---
phase: 142
slug: high-voltage-routing
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-11
---

# Phase 142 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `142-RESEARCH.md` §Validation Architecture. Do not restate that
> section here — it carries the per-requirement oracle tables and the non-claims.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | PlatformIO Unity (`test_framework = unity`, `platform = native`) for firmware behaviour; plain `pytest` (no config, no `addopts`) for `firestarter/tests/` source-contract gates |
| **Config file** | `firestarter/platformio.ini` — env `[env:native_loop_v131]` (`:373-414`), extended by exactly two lines (`test_filter` **and** `-I`, both required — Phase 119 D-04) |
| **Quick run command** | `pio test -e native_loop_v131` (0.8 s, 39 cases at arrival) |
| **Full suite command** | `pio test -e native` && `pio test -e native_nodevtools` (must stay **141 cases / 17 suites / all_passed**) && `python3 -m pytest tests/ -o addopts="" -q` (256 at arrival) |
| **Estimated runtime** | ~15 s native + ~11 s pytest; cold triple-target `pio run -t clean` adds ~2 min |
| **Never run** | `check_size_baseline.py` / `check_build_warnings.py` against `native_loop_v131` — F-138-05 uncaught `KeyError`, exit 1 / exit 2 |

---

## Sampling Rate

- **After every task commit:** `pio test -e native_loop_v131 -f "*test_vpp_eprom_v131*"` plus the full `native_loop_v131` env
- **After every task commit (pytest gates):** `python3 -m pytest tests/ -o addopts="" -q` — **commit first.** `tests/test_flash_path_record_sync.py:1247` asserts whole-repo `git status --porcelain == ""`, so any in-flight firmware diff turns it RED (F-141-11, orphaned, do not fix here)
- **After every plan wave:** full suite command above, plus `pio run -e uno` / `-e uno328pb` / `-e leonardo` — **leonardo must LINK** (26400/28672 B at arrival, 2272 B headroom; the ceiling is a build failure, not a gate)
- **Before `/gsd-verify-work`:** full suite green, `native_trace_v131` **expected RED and named as such in the record** (D-17 — do not re-freeze), cold `pio run -t clean` figures captured on all three AVR targets for D-16
- **Max feedback latency:** ~1 s (native_loop_v131) / ~11 s (pytest)

---

## Per-Task Verification Map

Populated by the planner from each PLAN.md's `<verify><automated>` blocks. Every
requirement below has at least one off-hardware oracle named in
`142-RESEARCH.md` §Validation Architecture "Per-requirement oracles".

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | VPP-01 | — | `0x07`/`0x08` keep `REGULATOR\|DROP` across the block on Rev 2-class; `0x0B` direct; Rev 1 / UNKNOWN keep today's stripping | unit (native, strobe recorder) | `pio test -e native_loop_v131 -f "*test_vpp_eprom_v131*"` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | VPP-02 | — | Every **error** exit of `eprom_write_execute` (`:226`, `:268`, `:275`, `:311`) leaves no HV route asserted; the **success** exit deliberately does not | unit (native, strobe recorder) | `pio test -e native_loop_v131` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | VPP-02 | — | `command_done()` zeroes all three registers and is reached on both dispatch arms | source-contract (pytest) | `python3 -m pytest tests/ -o addopts="" -q` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | VPP-03 | — | One resolver definition, ≥2 call sites, zero remaining `handle->protocol == 0x0B` predicates; `check_vpp` and the write path emit the same physical control byte | source-contract (pytest) + unit (native) | both above | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | VPP-04 | — | Injected over-voltage → `MSG_ERR_VPP_HIGH` (0xB8) + `RESPONSE_CODE_ERROR`, no route left asserted; `FLAG_FORCE` downgrades to `MSG_WARN_VPP_HIGH` (0x82) + `RESPONSE_CODE_WARNING` | unit (native, `HOST_STUBS_CUSTOM_VOLTAGE_MV`) | `pio test -e native_loop_v131 -f "*test_vpp_eprom_v131*"` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter/test/native/avr/test_vpp_eprom_v131/host_stubs.cpp` — opt into `HOST_STUBS_REAL_REGISTER_UTILS` (**mandatory**: the only layer below `rurp_write_to_register`'s elision, F-141-09) + `HOST_STUBS_RECORD_TIMING` + `HOST_STUBS_CUSTOM_READ_DATA_BUFFER` + `HOST_STUBS_CUSTOM_VOLTAGE_MV`; `reset_register_cache`, the readback model, `rurp_log_id` capture. Largely a copy of `test_loop_eprom_v131/host_stubs.cpp` plus the voltage mock.
- [ ] `firestarter/test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp` — `setUp` mocking **all four** ArduinoFake timing functions (`delay`, `delayMicroseconds`, `millis`, `micros` — an unmocked call SIGABRTs; this is the C-2 mechanism); `tearDown` resetting `hardware_revision` unconditionally; a `drive_vpp_init(...)` helper calling `firestarter_operation_init` (NOT `drive_loop_write`, which deliberately skips `_init`)
- [ ] `firestarter/platformio.ini` — the two `[env:native_loop_v131]` lines (`test_filter` **and** `-I`)
- [ ] Re-derived `firestarter/tests/golden/protocol_branch_inventory.json` + the pinned `protocol_lines` literal at `firestarter/tests/test_protocol_branch_inventory.py:446` (D-18: re-derive by independent parse, never hand-edit a line number, a `keyed_on` set, a class or a count)
- [ ] A `command_done()` source-contract leg in `firestarter/tests/` (D-09's owed test) — nothing asserts it today
- [ ] Fate of `test_loop_eprom_v131.cpp:1573-1632` (`test_loop08_dip32_drop_bit_is_cleared_deliberately_before_the_first_pulse`) — its claim is **inverted** by D-01/D-04 on Rev 2-class. Rewriting it is required; doing so silently is not acceptable
- [ ] Nothing else. No new env, no `size_baseline.json` edit, no `messages.toml`, no codegen, no host change

**Every case must call `reset_register_cache(0,0,0)`** — `rurp_register_utils.h:12-14` initialises the globals to `0xff`, which ORs `CTRL_VPP_REGULATOR_ENABLE` into the first write of any case that does not (L-7).

**Every drop-bit assertion must set `hardware_revision = REVISION_2_2`** — on the default `REVISION_0` the drop bit and A16 both map to physical `0x01` and the claim is undecidable (L-6). `HOST_STUBS_RECORD_BUS` is unusable for drop-bit work: it truncates the `0x100` bit to zero.

---

## Planted-RED obligations (D-15 discipline)

Three legs are **green on arrival** and prove nothing until seen RED. Transcript verbatim in the owning plan's SUMMARY (precedent: 12 planted runs in Phase 140, 13 in Phase 141).

| Leg | Why green on arrival | Planted violation |
|-----|----------------------|-------------------|
| VPP-04(b) — no route asserted on the over-voltage refusal | `eprom.cpp:393` already clears `REGULATOR\|DROP` on every path but the pre-assert Rev-0 return (C-3) | Temporarily make `eprom.cpp:370-371` an early `return` |
| VPP-02 X2's widened drop-bit assertion | `test_loop05_the_loops_own_strobes_disable_the_high_voltage_route` already asserts `REGULATOR` clear | Revert the composite at `:174` to `REGULATOR` alone |
| `command_done()` source contract | The three zeroing lines already exist | Point the scanner at a fixture with one zeroing line removed |

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| — | — | — | — |

**All phase behaviors that this phase *claims* have automated verification.** The following are **explicit non-claims** — neither automated nor deferred-to-manual, but out of scope by decision, and the phase record must state them rather than leave them inferable:

| Non-claim | Authority |
|-----------|-----------|
| `0x08` silicon behaviour after the route change | D-03 — bench-only, deliberately not attempted; AM27C020 is a known stress case (`PROJECT.md:560`, v1.18 P99: write#1 60/64, write#2 0/64) so it is not a pass/fail oracle either way |
| That the drop resistor produces ~13 V | No native suite reads an ADC; `rurp_read_voltage_mv` is a mock |
| **Any** timing change | `delay()`/`delayMicroseconds()` are unstubbed ArduinoFake free functions; the recorder stores arguments only. A trace diff proves *which* delay was requested, never how long anything took |
| Physical de-assertion where the mapper aliases two logical bits | C-4 (Rev 2-class `CTRL_ADDRESS_LINE_18` ≡ `CTRL_VPP_P1_ENABLE` ≡ physical `0x08`) and the Rev 0/1 drop↔A16 case. The composite's guarantee is **logical**, not physical |
| The address-bus `vpp_line` bit is cleared on write-path exit | D-11 — `memory.cpp:346-348` ignores `read_write`; clearing it would change the read path. Cleared only by `command_done()` |
| That `command_done()` runs on the real AVR abort path | The timeout arm (`firestarter.cpp:174-176`) depends on `millis()`, outside every native suite's reach |
| D-03's non-claim discipline is gate-enforced | **It is not.** CLOSE-01's `check_permitted_claims.py` is Phase 146's (L-12); prose-enforced only this phase |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] Every new gate leg seen RED on a planted violation, transcript in SUMMARY
- [ ] `native_trace_v131` RED is **named as expected** in the record (D-17), not silenced
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

# Milestone v1.23 — Project Summary

**Generated:** 2026-08-03
**Purpose:** Team onboarding and project review
**Milestone:** v1.23 PY32F071 Integration — ✅ SHIPPED 2026-08-03, tagged `v1.23` in all three repos

---

## ⚠ Read this before anything else — the validation ceiling

**No PY32F071 PCB exists — no PY32F071 hardware exists at all.** Nothing in this milestone has ever run on this silicon, and nothing in it could. That is not a gap in the work — it is the stated boundary the work was designed around, and it shapes how every claim below must be read.

**What may be claimed:** the target builds clean; the native and host suites pass at their recorded case *and* suite counts; the DFU sequence is exercised against device descriptors and mocks; host-side timing and sizes are measured where a tool exists to measure them.

**What may not:** five specific forbidden phrasings, **cited by location rather than reproduced here** — `.planning/milestones/v1.23-REQUIREMENTS.md`, the *Validation Ceiling* section. They are deliberately not repeated in this document, for the same reason `130-LEDGER.md` does not repeat them: the claim scanner matches a phrase's *shape* regardless of quotation context, by design, so a document that helpfully lists them fails its own gate. That is the gate working as intended, not a defect to route around. Read them at the source.

**The two claims never to conflate:** a successful firmware *install* says nothing about the *programmer* working. One is a transport-and-storage claim; the other is a hardware claim about a board that does not exist.

This is not an honour system. `tools/check_permitted_claims.py` — an 8-row forbidden-phrase table gated to a `PY32F071`/`py32` token within a 3-line proximity window, armed all-or-nothing over four named closing artifacts — mechanically enforces it, and it was written in Phase 123 **before any firmware moved**. Its own docstring states the limit: a green scan covers the machine-checkable half only. It cannot detect an implied overclaim, a misleading omission, or wrong tone.

---

## 1. Project Overview

**Firestarter** is a two-part EPROM/Flash/SRAM programmer: a Python CLI host (`firestarter_app/`, pip package `firestarter`) that looks up chip specs from a JSON database and orchestrates operations over serial, and Arduino C++ firmware (`firestarter/`) that drives an Arduino-based RURP shield's hardware bus. The wire protocol runs at 250000 baud, COBS+CRC8-framed since v1.10.

**Core value — algorithm-first dispatch.** The minipro `protocol_id` (called `algorithm` in this project) is the single authoritative dispatch key end to end. Firmware, wire and host trust only that; the legacy `mem_type` axis was removed in v1.20.

**What v1.23 added.** A **fourth board target** — a PY32F071 (Cortex-M0+), on a non-Arduino CMake + `arm-none-eabi` toolchain — landed *beneath* that dispatch contract without disturbing it, together with the host USB-DFU installer that can flash it and the cross-repo release-asset fold that publishes its image. The three existing AVR targets (`uno`, `uno328pb`, `leonardo`) were a hard non-regression constraint throughout.

Concretely, the PY32F071 target shares the command processor, framing and PROM algorithms with the AVR targets through a **fake Arduino core** (`platform/py32f071/include/Arduino.h`) rather than through a timing abstraction. It brings a pinned OpenPuya SDK, CherryUSB CDC at a 48 MHz PLL, SysTick milliseconds + TIM3 microseconds, a VREFINT-compensated 12-bit ADC, and a contiguous 8-bit GPIO bus (one-snapshot `IDR` read, atomic `BSRR` write). `DATA_BUFFER_SIZE` is **512** — half Leonardo's, deliberately, because it is wire-visible via v1.10 CAP-01 and raising it would be a behaviour change needing its own justification.

**Status: complete.** All 8 phases (123–130) executed and verified; 47/47 v1 requirements; published as `3.0.0b15` on both community channels.

**Who worked on it:** Henrik Olsson (sole author across all three repos; sub-repo commits also appear under the `henols` identity).

---

## 2. Architecture & Technical Decisions

The seven load-bearing choices, each with the reason it was made rather than the alternative:

- **The PY32F071 is a platform *edge*, not a new dispatch axis.**
  - **Why:** the PROM programming algorithms must stay platform-independent, so a fourth MCU absorbs its differences at the edge and the `algorithm` contract above it never learns that ARM exists.
  - **Phase:** 124 (the landing) · 125/126 (the two seams that make it possible)

- **A compatibility shim + fake Arduino core, not a timing abstraction layer.**
  - **Why:** research measured that `rurp_platform.h`'s timing functions have **zero** common-code consumers, and that no branch does any pin-map work. The real portability mechanism turned out to be `platform/py32f071/include/Arduino.h`. Building the abstraction the planning record described would have been building something nothing consumes.
  - **Phase:** 124

- **VPP ships as a *seam only* — no closed loop, no calibration.**
  - **Why:** two independent reasons. (1) `rurp_set_vpp_target_mv()` closes its loop on the *calibrated* voltage read, and three of PR #45's ten commits reach into files the queued White-Box Voltage Calibration milestone owns (`rurp_common.cpp`, `rurp_types.h`, `rurp_config_utils.cpp` — `CONFIG_VERSION`-bump and EEPROM-migration territory). "DAC in, calibration out" has no clean split. (2) With no PCB, a closed loop **cannot be validated at all**, and a loop that cannot be validated must not be claimed to work. So every board returns `MANUAL_ADJUSTMENT_REQUIRED` and the port compiles against the final API shape.
  - **Phase:** 125. Recorded as **permanent** for the AVR class: no Arduino-class board will ever carry the DAC, so `__AVR__` resolves the capability macro and every non-AVR board must declare it explicitly.

- **Config persists in dual-slot CRC32 flash records behind a per-platform storage seam — and the schema does not change.**
  - **Why:** the part has no EEPROM and PR #48's config was runtime-only. Splitting `rurp_config_utils.cpp` by *concern* (policy stays common; only a two-function byte-blob backend goes per-platform) is what lets the AVR EEPROM path be a **provable pure move** — 0 B flash and 0 B RAM delta on all three AVR targets under two named comparators — while `rurp_configuration_t` and its `VER06` literal stay untouched. The record format validates in a fixed order: `magic` → bounds-checked `length` → `crc32`.
  - **Phase:** 126. This was **design work, not integration**: the cited `PORTING.md` specification exists only on two closed PRs and does not match what PR #48 built, so the in-scope subset was vendored instead.

- **The host DFU installer is pure Python over `pyusb` — no external binary.**
  - **Why:** every factory-bootloader route failed on host-side grounds. Puya's own `PY32DfuTool` is Windows-x64 only; `dfu-util` reintroduces avrdude's PATH-discovery burden; `puyaisp` needs a second USB-serial dongle on a board that has native USB. The residual cost is `pyusb` + a libusb backend, and Zadig on Windows. `--usb-id` and `--dfu-probe` are both gated to the pre-release channel.
  - **Phase:** 127. Note this is the **runner-up** route — see the next decision.

- **The self-flash bootloader remains the intended primary install path; DFU landing here does not retire it.**
  - **Why:** a small bootloader in the first few KB speaking the same USB CDC + COBS framing the firmware already uses adds *zero* new host dependencies (`pyserial` is already required) and is structurally identical to how the Uno works. Landing the DFU path proves the transfer sequence; the seed (`FUT-N05`) still owns the primary route. Phase 126 reserved a zero-length `BOOTLOADER` linker seam for it, with the migration cost commented in place.
  - **Phase:** 126 (the seam) · 127 (the runner-up) · 129 (the recorded decision)

- **Every gate is written before the thing it judges — as a milestone-wide ordering rule.**
  - **Why:** a gate written afterwards can only bless what already happened. Phase 123's six checkers and the BASE-01 baseline exist before a single firmware file moves; Phase 129's 41-leg cross-repo gate precedes the record it compares and went 31 RED → 0 RED entirely through content authored afterwards. Every checker ships paired with a committed planted-violation fixture and a pytest proving it exits non-zero.
  - **Phase:** 123, reapplied in 126, 128, 129, 130

**Repo layout.** A meta planning repo (this one, tracking only `.planning/` and `.claude/`) plus two sub-repos as gitlinked submodules. `main` is **never merged** in any of the three; work lands on `beta`, and pushing `beta` auto-fires CI and cuts a beta, so the cut is always a deliberate decision.

---

## 3. Phases Delivered

| Phase | Name | Status | One-liner |
|-------|------|--------|-----------|
| 123 | Non-Regression Baselines & Gate Hardening | ✅ verified `passed` (8/8) | Six fail-provable checkers and a flash-**and-RAM** baseline authored before any firmware moved — plus the cross-repo firmware-presence proxy that had been failing OPEN, fixed |
| 124 | Firmware Integration Merge | ✅ verified `passed` (8/8) | The portability + py32 stack landed as **one** commit-pair, the C-1 CMake rename repaired, the ARM `push` trigger added, and the hollow pin-map guard made able to fire |
| 125 | VPP Control Seam | ✅ verified `passed` (15/15) | Hand-authored `rurp_vpp.{h,cpp}` returning `MANUAL_ADJUSTMENT_REQUIRED` on every board, at 0 B flash / 0 B RAM on all three AVR targets, with nothing cherry-picked from PR #45 |
| 126 ⚠ | Flash-Persistent Config via a Storage-Backend Seam | ✅ `passed-with-findings` (5/5 substantively; 7/7 reqs; 1 informational) | Dual-slot CRC32 config for a part with no EEPROM, behind a common/per-platform seam whose AVR EEPROM backend is a proven pure move; Sector 15 reserved; PR #48's non-persisting `config.cpp` deleted |
| 127 | Host DFU Installer | ✅ verified `passed` (5/5) | Pure-Python DFU 1.1/DfuSe installer with `DFU_UPLOAD` readback and a 120 KiB envelope matching the reserved flash map; suite 1158 → 1293, 0 skipped |
| 128 | Release-Asset Fold | ✅ verified `passed` (4/4) | The ARM build folded in after the version bump so `firestarter_py32f071.hex` publishes as a real release asset — proven on two real CI dispatches, not by reading YAML |
| 129 | Flash-Path Decision & PCB Requirements Record | ✅ verified `passed` (5/5) | Every PCB decision that is free today and unrecoverable after layout, written down in two lockstep layers held body-for-body by a 41-leg cross-repo gate |
| 130 | Close — Honesty Ledger, Claim Gate, Release Decision | ✅ verified `passed` (4/4) | A six-tier honesty ledger pairing every permitted claim with its explicit non-claim; all 18 research corrections landed under a label-aware checker; the `beta` push made its own operator-gated decision |

**Phase 126's finding, in full, because it is the one non-clean verdict.** Success criterion 3 required an *empty* `git diff` on the CFG-04 regression test after the refactor. Plan 126-03's own acceptance criteria then required the new AVR backend translation unit be wrapped in a three-board `#if` guard — which forced exactly one line into the test file's compiler argv (`-DARDUINO_AVR_UNO`, blob `0ef805f → 12bd237`, one insertion / one deletion). **No assertion changed.** The substantive property — that the AVR EEPROM path is a pure move — was independently confirmed to hold. The deviation was pre-authorised and disclosed in `126-NONREGRESSION.md` §Criterion 3 rather than smoothed over, and the phase is correctly *not* reported as a clean pass by its own artifacts.

**Wave structure.** Phases ran 6–16 plans each (88 total), with the close phase's 16 plans across 9 waves, waves 4–9 serial by constraint. Three plans write `ROADMAP.md` and were placed in three distinct consecutive waves so they never run concurrently.

---

## 4. Requirements Coverage

**47 / 47 v1 requirements complete. 0 unmapped.** Exact 1:1 category→phase mapping.

| Category | Count | Phase | Verdict |
|---|---|---|---|
| **BASE** — Baselines & Gate Hardening | 8 | 123 | ✅ all 8 |
| **MERGE** — Firmware Integration Merge | 8 | 124 | ✅ all 8 |
| **VPP** — VPP Control Seam | 3 | 125 | ✅ all 3 |
| **CFG** — Flash-Persistent Config | 7 | 126 | ✅ all 7 |
| **HOST** — Host DFU Installer | 8 | 127 | ✅ all 8 |
| **REL** — Release-Asset Fold | 4 | 128 | ✅ all 4 (REL-03's second half local-only, stated) |
| **PCB** — Flash-Path & PCB Record | 5 | 129 | ✅ all 5 (PCB-03/04 carry honest amendment qualifiers) |
| **CLOSE** — Honesty Ledger & Release Decision | 4 | 130 | ✅ all 4 (CLOSE-02/04 carry mechanizable-half / operator-act qualifiers) |

**Three requirements shipped with the mechanism corrected rather than as prescribed** — each recorded, none silently reinterpreted:

- ⚠️ **HOST-01** — an *accepted deviation*, not a defect. The prescribed flasher-strategy extraction was declined specifically to keep the bench-earned avrdude ladder verbatim, which the branch achieves by not touching that function at all.
- ⚠️ **PCB-03 / PCB-04** — amended **in `REQUIREMENTS.md` itself**, breaking this project's usual "record the correction in the phase artifact, leave the requirement text alone" discipline. The exception is the boundary: those two clauses asserted a **fact** that is false — that the part lacks a vector-table offset register — and a false fact does not survive being merely footnoted elsewhere the way a narrower mechanism does. (The part *has* `__VTOR_PRESENT 1`; the firmware already writes `SCB->VTOR` unconditionally at boot.) The fact-versus-mechanism boundary is now a paragraph in `REQUIREMENTS.md`, naming LOCK-04 / LOCK-06 / HOST-04 / Phase 121 D-06/D-17 as the mechanism-class precedents it does not disturb.
- ⚠️ **REL-03** — the "a deliberately broken ARM build still publishes all three AVR assets" claim is CI-proven; the *other* half, that the AVR-assets gate **fails** on a missing asset, is proven **locally only** by two planted-fixture exit-1 proofs. `128-NONREGRESSION.md` §7 states this explicitly rather than folding it into the CI-proven half.

**No milestone audit was run.** `.planning/milestones/v1.23-MILESTONE-AUDIT.md` does not exist. Phase 130 was itself a dedicated close phase — honesty ledger, claim gate, and a full non-regression sweep re-executed in-session, verifier 4/4 — and v1.19 through v1.22 all closed the same way. Worth knowing when reading this document as an independent assessment: the close was self-verified by its own phase, not by a separate audit pass.

---

## 5. Key Decisions Log

**141 numbered decisions** across the eight phases' `CONTEXT.md` files (123: 16 · 124: 16 · 125: 16 · 126: 19 · 127: 19 · 128: 21 · 129: 18 · 130: 16). The full text is in each `.planning/phases/12N-*/12N-CONTEXT.md` under `## Implementation Decisions`. The ones a newcomer needs:

**Operator decisions locked at requirements time (2026-07-30) — do not re-litigate:**

1. **Scope** — port stack + host DFU + release-asset fold + VPP **seam only**. Calibration model out; DAC closed loop out.
2. **Slot** — v1.23, retiring the queued v1.28/v1.29 py32 slots into it; `Binary Command Protocol` renumbers v1.23 → v1.28; **v1.24–v1.27 left untouched** so existing by-number cross-references keep resolving.
3. **PR #45** — cherry-pick **nothing**; hand-author the seam. Confirmed *necessary*, not merely preferred: `05f4a77` carries a `CONFIG_VERSION "VER06"→"VER07"` bump, and `include/rurp_shield.h` is the only textual conflict anywhere in the six-branch inventory.
4. **AVR flash constraint** — restated as *"Leonardo flash must not grow; Uno-class growth ≤ 64 B, recorded"*, because the measured tree already fails a literal zero-growth rule on the two targets with ~8.3 KB spare while *improving* the binding target by 56 B. RAM joins the recorded baseline.
5. **Flash-persistent config** — in scope, design authored in-milestone.
6. **DFU readback verification** — in scope, failing soft on `bitCanUpload = 0`, ceiling stated as *"asserted against a mock"*.

**Decisions the work itself forced, discovered by measurement:**

- **Land the stacked pair atomically (124, overturning gh#16's inherited sequencing).** `agent/portability-macros` **cannot land alone**: cherry-picked onto `beta` it takes `pio test -e native` from 141 cases / 17 suites passing to **0 passing / 17 ERRORED** — `pgm_read_ptr` and `strncmp_P` undeclared in `json_parser.c`, because its compat header omits four helpers the native `avr/pgmspace.h` stubs supplied. The repair commit lives on the *stacked* branch.
- **"The merge had no conflicts" is never a quality statement (124).** Both repos merged with zero textual conflicts and completely disjoint changed-file sets since merge base — and git still produced a *perfect* merge of a tree whose ARM target fails at CMake **configure** time, because `platform/py32f071/CMakeLists.txt` named `flash_type_3.cpp`/`flash_type_4.cpp`, renamed by v1.19 Phase 104. `py32f071.yml` had no `push` trigger, so nothing on `beta` would have reported it. Triple-corroborated; the milestone's highest-confidence finding.
- **Omit the `rurp_shield.h` include entirely (125).** Every planning document in this milestone described `#include "rurp_vpp.h"` in `include/rurp_shield.h` as *the phase's header change*. Measured, it collapses `pio test -e native` from 141/141 to 17 suites / 0 succeeded. The operator chose to omit it; `rurp_shield.h` is untouched.
- **Key the containment report on `outcome`, never `conclusion` (128).** Empirically validated by a real dispatch: GitHub set the contained ARM step's `conclusion: success` while its `outcome` was `failure`. A `conclusion`-keyed gate could never have fired.
- **Reverse Phase 129's declined descriptor edit before publishing (130, D-11).** Phase 129 declined the USB-descriptor edit because it was a documentation-only phase with no cut planned. Publishing an image is a new fact Phase 129 did not have to weigh, so D-11 reverses it — recorded **as a reversal**, with the constraint named, in both copies of the flash-path record.
- **Commit the release decision before the push (130, mirroring v1.22).** Pushing `beta` auto-fires CI and cuts a beta. `130-DECISION.md` was committed first, and the cut tag was read verbatim from `gh release list` — never computed.

---

## 6. Tech Debt & Deferred Items

### Deliberately left OPEN, with a named owner — not unacknowledged gaps

- **⚠ 69 inherited mypy errors, and the fail-open tool that hid them.** `tools/check_mypy_watermark.py` shells to a bare `mypy` from `PATH`; under Python 3.12 the configured `python_version = "3.9"` is rejected and a numpy stub aborts the run — so it reported green **without type-checking anything**, against a watermark of 35. Phase 127's own net contribution measured **zero** (69 → 72 → 69, confirmed on the runner). `firestarter_app`'s primary `ci` job is **RED** until a dedicated gate-hardening phase. Not v1.23's contribution and not v1.23's to fix — but this is the clearest single piece of debt in the repo.
- **⚠ FUT-ORACLE — there is no bus-trace oracle on ARM.** `HOST_STUBS_RECORD_BUS`, the register-write recording harness, runs on `native`, never on the ARM target. The ARM target's emitted register sequences could diverge from the AVR-family goldens with **nothing able to notice**.
- **⚠ D-17 — the USB-identity ship gate is carried as a tension, not a resolution.** The pair now published in `usb_cdc.c` is pid.codes' documented *private-testing* pair (`1209:0001`), not an allocation. The gate reads: no board ships and no release advertises a USB identity until a PID allocated under the community vendor id exists. A future reader may find that condition unmet — which is exactly what a *condition* permits by being a condition rather than a warning. Filing the pid.codes request is an operator act.
- **⚠ REL-04's cross-repo filename binding is held by local runs and developer discipline, not CI.** Neither app CI workflow checks out the firmware sibling, so the ten-test binding **skips** in app CI.
- **⚠ `check_ledger.py` has 2 pre-existing `LEDGER-01` REDs** from v1.19 Phase 104's rename. Deliberately not fixed — doing so would edit a closed milestone's artifact. A small, self-contained backlog seed.

### The eight `FUT-*` deferrals, each with its reason

| ID | Deferred | Why |
|---|---|---|
| FUT-N02 | Live progress reporting during firmware install | avrdude's own progress is swallowed by process-pipe buffering on all three AVR boards; adding it to the *least*-proven path alone would give it the project's only live feedback |
| FUT-N04 | Software reboot-into-bootloader (removing the strap-jumper dance) | Its first stated reason (VTOR absence) is **corrected false**; the deferral stands on its other three — the memory-remap mechanism reportedly has no effect on some sibling parts, it cannot be validated without a part, and FUT-N05 obsoletes it for the normal path |
| FUT-N05 | The self-flash bootloader over CDC + COBS | The seed's own **primary** route, and its own milestone. Landing DFU does not retire it |
| FUT-N06 | Publishing a raw `.bin` release asset alongside the Intel-HEX image | Host acceptance already exists; publication waits until FUT-N05 needs it |
| FUT-VPP | Closed-loop DAC-driven VPP with independent overvoltage shutdown | Inseparable from the calibration model it shares an API with, and unvalidatable without a board |
| FUT-CAL | Cross-platform bandgap-reference + two-point calibration | Owned by the queued **v1.26 White-Box Voltage-Reading Calibration** milestone |
| FUT-ORACLE | A bus-trace oracle for the ARM target | Does not exist; see above |
| FUT-ARMSIZE | ARM flash/RAM as a checked-in baseline with a RAM ceiling | CI runs a size-reporting step, but only into the job log — **nobody would notice a regression there today** |

### Two open hardware questions, unguessed

- **The boot-selection option bit's factory default** — unknown from both the datasheet and the vendor's bootloader manual. If the bit selects the wrong boot area, the DFU recovery path is gone.
- **Whether the USB PHY provides an internal D+ pull-up**, or a discrete resistor is required on the board. Answerable only from the reference manual's USB chapter or a real part.

### Process debt carried across the close

- **The same 14 `audit-open` items were acknowledged for the sixth consecutive milestone** (2 debug sessions, 2 partial UATs, 5 verification gaps, 13 pending todos — all predating v1.17). None originate in v1.23. Recorded in `STATE.md` → *Deferred Items* alongside Phase 126's finding, for 15 total overrides. This should be **scheduled**, not acknowledged a seventh time.
- **⚠ Three CI-only sibling-checkout test defects fired on the real b15 push** — invisible in the devcontainer, which *has* the sibling layout standalone CI lacks. Two fixes (`firestarter` `1c511e8`, `firestarter_app` `5934a54`) landed on `beta` **outside any plan** during the operator hand-off, and one of them **softened a Phase-129-authored hard assert** (`test_present_root_with_missing_target_raises_not_skips`) to a skip — a defect-class change flagged rather than treated as routine.
- **Carried from v1.22, still owed:** reintroduce `firestarter_app`'s `81fa53c` whenever a milestone branch next merges toward `main`, or `ci.yml`'s standalone-checkout failure resurfaces.
- **The community inbox is not empty, and this close does not imply otherwise.** gh#20 (an AT28C256 `dev test` FAIL, 2026-07-30) and gh#18 (FM1608 `dev test` PASS) both arrived *after* the 2026-07-27 backlog import that stopped at gh#17. gh#11 and gh#12 also remain OPEN.

### Lessons worth carrying (from `RETROSPECTIVE.md`)

- **A gate that has never been *seen to pass* is not yet known to be reachable.** Phase 129 authored one leg unreachable — it required `MEMORY` and `{` on one source line, and `PY32F071xB_FLASH.ld` has them on lines 8 and 9 — and nothing caught it until a later plan tried to satisfy it. Read the failure *reason*, not just the exit code.
- **Failing OPEN is worse than failing closed, and it hides far longer.** Prior milestones were bitten by the fail-*closed* form of the cross-repo presence proxy four times and CI caught it every time. The fail-open form had never fired, because no earlier milestone moved firmware files at scale — which was exactly v1.23's premise.
- **A phase's own validation procedure can be wrong in a way that would produce false evidence.** Phase 128's prescribed way to break run B trips Phase 123's manifest-drift gate at a step with no `continue-on-error`, so the job would have failed *before* the ARM build and published nothing — demonstrating the exact opposite of the requirement.
- **When a premise collapses, check whether the conclusion survives for a better reason before widening any claim.** The ARM toolchain *is* locally installable (the stated premise was false), and that bought exactly two narrower claim classes — delta and byte-identity — and nothing wider.

---

## 7. Getting Started

### Read first, in this order

1. `.planning/milestones/v1.23-REQUIREMENTS.md` § *Validation Ceiling* — the claim boundary, before anything else.
2. `.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-LEDGER.md` — the six-tier honesty ledger. The single most useful document for calibrating how strong any given claim is.
3. `.planning/v1.23-FLASH-PATH-DECISION.md` — the flash-path decision and PCB requirements (authoritative copy; `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md` is the lockstep subset).
4. `firestarter/platform/py32f071/README.md` and `CONFIG-STORAGE.md` — the target's own docs.
5. `.planning/MILESTONES.md` § v1.23 — the full close entry.

### Build and test

```bash
# Host CLI (from firestarter_app/) — /usr/local python, NOT the devcontainer default
pip install -e '.[test]'
pytest                                    # 1293 passed / 0 failed / 0 skipped at close
pip install -e '.[test,py32]'                 # adds pyusb>=1.3.1,<2 for the DFU path
pytest tests/test_pyusb_api_surface.py -q     # the ci-py32 leg — conftest.py's collect_ignore
                                              # keeps it out of the primary suite when pyusb
                                              # is absent, so run it by explicit path

# AVR firmware (from firestarter/)
pio run -e uno            # also: -e uno328pb, -e leonardo
pio test -e native        # 141 cases / 17 suites — the recorded baseline
pio test -e native_nodevtools
pio run -t monitor -e uno # serial monitor at 250000 baud

# PY32F071 target (from firestarter/) — needs cmake, ninja, gcc-arm-none-eabi,
# binutils-arm-none-eabi. Installable in the devcontainer, but see the caveat below.
cmake -S platform/py32f071 -B build/py32f071 -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build/py32f071
```

**⚠ Local ARM builds support *delta* and *byte-identity* claims only.** A local compiler differs from CI's and produces a different absolute size for the same source — measured `text=27260` local against `text=27344` in CI. Every **absolute** ARM size or footprint claim must cite a CI workflow run URL *plus* a commit SHA. And byte-identity never implies the image runs.

### Key directories

| Path | What's there |
|---|---|
| `firestarter/src/proms/` | The per-protocol PROM algorithms — platform-independent, shared by all four targets |
| `firestarter/src/boards/` | Per-board hardware layer, including `rurp_config_storage_eeprom.cpp` (the AVR config backend) |
| `firestarter/include/rurp_vpp.h`, `src/rurp_vpp.cpp` | The VPP capability seam (v1.23, hand-authored) |
| `firestarter/include/rurp_config_storage.h` | The two-function config storage seam (v1.23) |
| `firestarter/platform/py32f071/` | The whole ARM target: `CMakeLists.txt` (26 enforced sources), `linker/PY32F071xB_FLASH.ld`, `include/Arduino.h` (the fake core), `src/` |
| `firestarter_app/firestarter/py32_dfu.py` | The pure-Python DFU 1.1 / DfuSe client |
| `firestarter_app/firestarter/database.py` | `EpromDatabase` — DIP-pin → RURP bus config translation |
| `firestarter_app/firestarter/data/chip_database.json` | The chip database (user overrides live in `~/.firestarter/database.json`) |
| `firestarter/tools/`, `firestarter_app/tools/` | The CI checkers. Every one has a paired planted-violation fixture |

### Things that will bite you

- **Protocol changes must stay in lockstep** between `firestarter_app/firestarter/serial_comm.py` and `firestarter/src/firestarter.cpp`; constants and flag bits are duplicated between `firestarter_app/firestarter/constants.py` and `firestarter/include/firestarter.h` and must change **together**.
- **`firestarter/include/messages.h` is codegen-generated and ID-only.** Edit the meta repo's `messages.toml` and regenerate; a wording-only change produces a **zero** firmware diff.
- **Several `firestarter_app` gates scan *firmware* source text.** A firmware rename breaks host tests while the firmware suite stays green.
- **Before pushing a sub-repo `beta`, point the sibling-checkout root at an empty directory.** The devcontainer's convenience layout is exactly what standalone CI lacks.
- **The devcontainer runs Python 3.12; CI targets 3.9/3.11.** Run ruff and mypy CI-scoped, and do not trust the mypy watermark gate (see Tech Debt).
- **The py32 target refuses every PROM-energising command** while the pin map is provisional. That refusal is load-bearing, not a placeholder — v1.18 was an entire milestone caused by one mis-modelled pin.

### Hardware reality check

The operator's bench has an Arduino Uno, an ATmega328PB Uno, and a Leonardo, plus RURP shield revisions 2.2, 2.0 and a modified Rev 0. **There is no PY32F071 board.** Everything in v1.23 is source, CI, tests and records.

---

## Stats

| | |
|---|---|
| **Timeline** | 2026-07-30 → 2026-08-03 (4 days of execution, closed on the 5th) |
| **Phases** | 8 / 8 complete (123–130) |
| **Plans** | 88 / 88 — the largest plan count of any milestone to date, past v1.22's 69 |
| **Tasks** | 226 |
| **Requirements** | 47 / 47 v1, 0 unmapped |
| **Decisions** | 141 numbered across 8 `CONTEXT.md` files |
| **Research corrections** | 18 (R-1…R-18) + 7 adjudications at kickoff; more per phase |
| **Commits** | 301 meta · 88 firmware · 40 host app |
| **Diff** | meta 295 files (+103,872 / −1,686) · firmware 129 files (+18,851 / −103) · host 39 files (+7,635 / −205) |
| **Contributors** | Henrik Olsson |
| **Verification** | 7/8 phases `passed`; Phase 126 `passed-with-findings` (1 informational) |
| **Closeout** | `override_closeout` — 15 known overrides, 14 of them pre-v1.17 carry-forwards |
| **Released as** | `3.0.0b15` on both channels · firmware prerelease carries **four** `.hex` assets including the first-ever `firestarter_py32f071.hex` · **no stable release** (PyPI `info.version` stays `2.0.7`) |
| **Tags** | `v1.23` → meta `04feaa2c`, firmware `0933bd7`, host `16a313a` (all pushed; `main` untouched) |

---

*Generated by `/gsd-milestone-summary` from `.planning/milestones/v1.23-{ROADMAP,REQUIREMENTS}.md`, `PROJECT.md`, `RETROSPECTIVE.md`, `STATE.md`, `MILESTONES.md`, and the `12N-{CONTEXT,SUMMARY,VERIFICATION,RESEARCH,NONREGRESSION}.md` artifacts of phases 123–130.*

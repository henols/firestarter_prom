# Requirements: Firestarter — v1.23 PY32F071 Integration

**Defined:** 2026-07-30
**Core Value:** Algorithm-first dispatch — the minipro `protocol_id` (`algorithm`) is the single authoritative dispatch key end to end. v1.23 adds a fourth board target *beneath* that contract without disturbing it: the PROM programming algorithms stay platform-independent and the platform edge absorbs the new MCU.

---

## Validation Ceiling — read this before writing or accepting any criterion

**No PY32F071 PCB exists.** Nothing in this milestone has ever run on this silicon, and nothing in it can.

**Permitted claims:** the target builds clean; the native and host suites pass at their recorded case *and* suite counts; the DFU sequence is exercised against device descriptors and mocks; host-side timing and sizes are measured where a tool exists to measure them.

**Forbidden claims:** *"the firmware runs on a PY32F071"* · *"the install works end to end"* · *"bench-validated"* / *"hardware-validated"* / *"silicon-verified"* unqualified · *"closed-loop VPP works"* · *"the pin map is correct/verified/validated"*.

**The two claims that must never be conflated:** a successful firmware install says nothing about the programmer working. PR #48's pin map (PB0–PB7 data, PA0–PA5 control, VPP on PA4/ADC ch4) is a placeholder that **describes no existing PCB** — PA4 was chosen only because it matches the Puya ADC example. v1.18 was an entire milestone caused by one mis-modelled pin.

**Unmeasurable locally, by anyone, today:** ARM flash and RAM. `arm-none-eabi-gcc`, `cmake` and `ninja` are absent from this devcontainer. Every ARM size claim cites a **CI workflow run URL + commit SHA**. A local `pio` run is not evidence about ARM.

**Explicit non-claims to carry to close:** there is **no bus-trace oracle on ARM** (`HOST_STUBS_RECORD_BUS` runs on `native`, not ARM), so the ARM target could diverge from the AVR emitted sequences with nothing able to notice; and USB-ISR latency versus PROM pulse windows is **not measured** — `py32_usb_write` spins with interrupts masked while `rurp_delay_us` busy-polls TIM3.

Research: `.planning/research/SUMMARY.md` (4 streams + synthesis; 18 corrections R-1…R-18, 7 adjudications A-1…A-7). Three of four researchers built, merged and tested the branches rather than reasoning about them.

---

## v1 Requirements

### Baselines & Gate Hardening

*Authored before any firmware moves — a gate written afterwards can only bless what already happened.*

- [x] **BASE-01**: A committed baseline file records flash **and RAM** for all three AVR targets (Leonardo 26072/2014, Uno 23932/1573, uno328pb 23976) plus the native case **and** suite counts (141 cases / 17 suites), so every later delta is judged against a recorded number rather than a remembered one
- [x] **BASE-02**: The host suite's "firmware absent" proxy is split — repo presence is keyed on `../firestarter/.git`, and a present repo with a missing scan target is a **hard failure**, never a skip
- [x] **BASE-03**: A skip-census assertion fails the suite if any skip reason claims the firmware checkout is absent while `../firestarter/.git` exists
- [x] **BASE-04**: A CMake source-list drift gate verifies every path named in `platform/py32f071/CMakeLists.txt` resolves in the tree, with an explicit commented `PY32_EXCLUDED` allow-list so a reader can tell deliberate omissions from rename damage
- [x] **BASE-05**: An orphan-provisional-macro checker asserts every `RURP_*_PROVISIONAL`-style flag has at least one consumer outside its own definition
- [x] **BASE-06**: A warning-count gate holds macro-redefinition warnings at zero, so the next real warning is not buried
- [x] **BASE-07**: `check_permitted_claims.py` with a v1.23 phrase table mechanically forbids the Validation Ceiling's forbidden claims across every closing artifact, and fails closed when its target list is empty
- [x] **BASE-08**: Every checker introduced in this milestone ships with a committed planted-violation fixture and a pytest proving the checker exits non-zero on it

### Firmware Integration Merge

- [x] **MERGE-01**: `agent/portability-macros` and the py32 stack land as one atomic landing including `780a3fb`, with no commit on the integration branch where the portability half is present and the py32 stack is not
- [x] **MERGE-02**: The CMake source list names `flash_nor_unlock.cpp` and `flash_5v_page.cpp`, and the ARM target reaches a successful CMake configure
- [x] **MERGE-03**: `py32f071.yml` gains `push: branches: [beta]`, so the ARM target is built on `beta` rather than only on pull requests
- [x] **MERGE-04**: While the pin map is provisional, the py32 target refuses every operation that can energise a PROM, and the guard is restructured so its `#error` is provably able to fire
- [x] **MERGE-05**: Leonardo flash does not grow; Uno-class flash growth is ≤ 64 B and recorded; flash **and RAM** are recorded for all three AVR targets against BASE-01
- [x] **MERGE-06**: `pio test -e native` and `-e native_nodevtools` report the BASE-01 case **and suite** counts, and the golden register traces are byte-identical (per-array for `_shared/sdp_expected.h`)
- [x] **MERGE-07**: All nine cross-repo source-scanning gates are shown to **run** — not skip — and pass, in a directory literally named `firestarter_app` with a merged `firestarter` sibling
- [x] **MERGE-08**: Three in-branch defects are fixed: the flash-latency constant (`FLASH_ACR_LATENCY_1` → `FLASH_LATENCY_1`, two wait states → one at 48 MHz), the orphaned `write_checksums.cmake`, and `DEV_TOOLS`-off on ARM made an explicit commented decision rather than an accident of the CMake defines

### VPP Control Seam

- [ ] **VPP-01**: `include/rurp_vpp.h` and `src/rurp_vpp.cpp` are **hand-authored** — nothing is cherry-picked from PR #45, whose `05f4a77` smuggles a `CONFIG_VERSION` bump and whose `9134f2a` reroutes AVR voltage measurement
- [ ] **VPP-02**: `rurp_set_vpp_target_mv()` returns `MANUAL_ADJUSTMENT_REQUIRED` on every board, asserted by a native test across each board macro-set
- [ ] **VPP-03**: A diff gate proves `src/boards/rurp_common.cpp`, `include/rurp_types.h` and `src/rurp_config_utils.cpp` untouched and `CONFIG_VERSION` still `"VER06"`, with the AVR flash delta measured rather than asserted

### Flash-Persistent Config

*The only phase editing a file compiled into all three AVR targets — and partly design work, because its cited specification is stranded on closed PRs.*

- [ ] **CFG-01**: The in-scope design is vendored onto the milestone branch from blob `4b1a441` so the contract is not stranded on closed PRs #46/#47, with the closed branch cited as its origin and the parts superseded by PR #48 marked as such
- [ ] **CFG-02**: The PY32F071xB flash page/erase-unit size is read from the Puya reference manual and recorded **before** the linker script is edited
- [ ] **CFG-03**: `src/rurp_config_utils.cpp` is split by concern — policy stays common, and only a two-function byte-blob backend goes per platform
- [ ] **CFG-04**: The AVR EEPROM backend is a pure move, proven by a regression test asserting `EEPROM.get`/`put` at offset 48 with `sizeof(rurp_configuration_t)` and byte-identical behaviour to pre-refactor
- [ ] **CFG-05**: The py32 backend implements dual-slot CRC32 storage, covered by a native fake backend across blank, newest-wins, CRC rejection, both-slots-corrupt, interrupted write, and slot alternation
- [ ] **CFG-06**: Two config pages are reserved in `PY32F071xB_FLASH.ld` in **different erase units**, exposed as linker symbols, with the host's `FLASH_BASE`/`FLASH_SIZE` kept consistent
- [ ] **CFG-07**: The `rurp_configuration_t` schema and `CONFIG_VERSION` are unchanged, and PR #48's `config.cpp` policy drift — including a `rurp_save_config()` that persists nothing — is deleted

### Host DFU Installer

- [ ] **HOST-01**: `firestarter_app` `feature/py32f071-fw-install` @ `4ee64a1` is merged, with the `flash_method()` router and the untouched `_install_with_avrdude` recorded as an **accepted deviation** from the prescribed flasher-strategy extraction rather than a defect to fix
- [ ] **HOST-02**: `--usb-id` is rejected on a stable channel exactly as `--dfu-probe` already is
- [ ] **HOST-03**: Written flash is read back and verified via `DFU_UPLOAD`, failing soft when the device reports `bitCanUpload = 0`, so py32 is not the project's only install path that writes without verifying
- [ ] **HOST-04**: A CI leg installs `.[test,py32]` and exercises the real `pyusb` import and API surface, which no test reaches today
- [ ] **HOST-05**: `PyusbMissingError` is covered by a test with its `# pragma: no cover` removed, and `fw --list` / `--help` are proven to work with `pyusb` absent
- [ ] **HOST-06**: DFU opcode literals are anchored to UM1504 / DFU 1.1 in one test, rather than imported from the module under test and asserted against themselves
- [ ] **HOST-07**: The `pyusb` floor is raised to `>=1.3.1,<2`
- [ ] **HOST-08**: Channel gating is proven both ways — a simulated stable `__version__` hides `py32f071` from `fw --help` and rejects `--dfu-probe`; a pre-release exposes both — remembering `_BOARD_CHOICES` is computed at import time

### Release-Asset Publication

*The only new work that makes any of the 21 existing host capabilities reachable.*

- [ ] **REL-01**: The ARM build runs inside `beta-build.yml`'s job **after** `update_version.py` rewrites and auto-commits `include/version.h`, so the published image carries the release `VERSION` the host compares against the tag
- [ ] **REL-02**: `firestarter_py32f071.hex` is published as a GitHub **release asset** — not an Actions artifact — matched by a **glob**, because the release action warns on an unmatched glob but fails on a missing literal path
- [ ] **REL-03**: A deliberately broken ARM build still publishes all three AVR `.hex` assets, proven rather than assumed, with an AVR-assets-present assertion before the release step
- [ ] **REL-04**: CI asserts the emitted filename matches `asset_candidates("py32f071")[0]`, and logs the resolved SDK commit SHA

### Flash-Path Decision & PCB Requirements

*The board is still paper. Every item here is free now and unrecoverable after layout.*

- [ ] **PCB-01**: The three-tier flash path is recorded as a decision — self-flash bootloader over the existing CDC + COBS transport as intended primary, factory USB DFU as maintainer/manufacturing recovery, SWD as last resort — stating explicitly that landing the DFU path **does not retire** the self-flash seed
- [ ] **PCB-02**: PCB requirements are recorded before the first schematic: BOOT0/nBOOT1 strapping reachable, SWD pads exposed, a contiguous 8-bit GPIO port for the data bus, and a depopulated HSE footprint as a crystal-less-USB hedge
- [ ] **PCB-03**: The flash budget is recorded **as actually reserved** by CFG-06, including the bootloader region and its vector-relocation implication on a part with no VTOR
- [ ] **PCB-04**: A real USB VID/PID decision replaces `usb_cdc.c`'s undocumented `0x36B7`/`0xFFFF` placeholder, noting that squatting becomes a liability the moment a board ships
- [ ] **PCB-05**: The socket-empty-before-any-py32-firmware-install safety instruction is documented, the provisional pin map being the reason it is stronger here than the comparable warning in other projects

### Close

- [ ] **CLOSE-01**: All of R-1…R-18 are applied to PROJECT.md, STATE.md, ROADMAP.md and `.planning/notes/py32f071-port-branch-state.md`
- [ ] **CLOSE-02**: An honesty ledger pairs each permitted claim with its explicit non-claim, covering at minimum the provisional pin map, the absent ARM bus-trace oracle, unmeasured USB-ISR-versus-PROM timing, and the mock-only ceiling on HOST-03
- [ ] **CLOSE-03**: The ROADMAP slot renumber lands (v1.28/v1.29 py32 slots retired into v1.23; `Binary Command Protocol` v1.23 → v1.28; v1.24–v1.27 untouched) together with the stale v1.28 prior-art correction owed by todo `correct-v128-py32-roadmap-prior-art`
- [ ] **CLOSE-04**: A release-decision artifact is committed **before any push**, the cut tag is read from `gh release list` rather than computed, and PyPI resolution is verified directly — 6 of 13 published app betas never reached PyPI, so manual `publish.yml` dispatch is the norm, not a contingency

---

## Future Requirements

Deferred with reasons. Tracked, not in this roadmap.

### Install Path

- **FUT-N02**: Live progress reporting during firmware install — deferred because avrdude's own progress is swallowed by `Popen(...PIPE) + communicate()` on all three shipped boards, so adding it to py32 alone would give the *unproven* path the project's only live feedback. A parity project, not a py32 one.
- **FUT-N04**: Software reboot-into-bootloader, removing the BOOT0 strap dance — deferred because Cortex-M0+ has no VTOR, the `SYSCFG MEM_MODE` remap is reported to have no effect on some sibling F0 parts, it cannot be validated without silicon, and FUT-N05 obsoletes it for the normal path.
- **FUT-N05**: Self-flash bootloader over the existing CDC + COBS transport — the seed's *primary* route and its own milestone. Zero new host dependencies, and it removes both the libusb/Zadig friction and the strap.
- **FUT-N06**: Publishing a `.bin` release asset alongside `.hex` — host acceptance already exists; publication waits until FUT-N05 needs raw binary.

### Voltage Control

- **FUT-VPP**: Closed-loop DAC VPP control with independent overvoltage shutdown — inseparable from the calibration model it shares an API with, and unvalidatable without a PCB.
- **FUT-CAL**: The cross-platform VREFINT + two-point calibration model — owned by the queued White-Box Voltage-Reading Calibration milestone, which must design it once for AVR (including the Stage-1 bandgap back-solve absent from PR #45, and Backlog 999.1's stale-`r1` `CONFIG_VERSION` migration) before it is extended cross-platform.

### Verification Infrastructure

- **FUT-ORACLE**: A bus-trace oracle for the ARM target, so emitted register sequences can be compared against the AVR goldens.
- **FUT-ARMSIZE**: ARM flash/RAM as a checked-in baseline with a RAM ceiling — CI already runs `arm-none-eabi-size` but only into the job log, where nobody would notice a 3 KiB regression.

---

## Out of Scope

Explicitly excluded, with reasoning, to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Any claim about PY32F071 silicon behaviour | No PCB exists. This is the milestone's stated ceiling, not an oversight |
| Rewriting the ~12 direct `delay`/`millis` call sites in shared code | The measured `−56/+22/+28 B` deltas **do not cover** this sweep; it would touch every golden trace for zero functional gain. `PORTING.md`'s "Arduino timing calls are removed from common code" is deliberately left UNSATISFIED |
| Extracting a `FirmwareFlasher` strategy class | The branch satisfies "keep the bench-earned avrdude ladder verbatim" better by not touching `_install_with_avrdude` at all. Recorded as an accepted deviation |
| Re-planning the `firestarter_{board}.hex` extension handling | Already solved on the branch by `asset_candidates()` / `_pick_asset()` across all four call sites, with `.bin` accepted |
| Changing the py32 `DATA_BUFFER_SIZE` from 512 | It is wire-visible via v1.10 CAP-01, so a bump is a behaviour change needing its own justification, not a constant tweak |
| Adding any USB class beyond CDC-ACM | `_Min_Heap_Size = 0x000` makes `malloc` fail, and `usb_malloc` is reached from the printer/audio/vendor classes — adding one is a NULL-deref-at-enumeration tripwire |
| An RTOS on the py32 target | The SDK vendors FreeRTOS and it is deliberately not compiled; a scheduler would fork the execution model away from AVR inside PROM bus windows |
| Anything from PR #47 (`feature/py32f071-full-support`) | Its `src/usb.c` is a ring buffer over `__attribute__((weak))` no-op hooks — it links, and a flashed board would be silent on USB |
| A `--force` overriding the flash-envelope guard | The refusal before any byte is sent is the guard's whole value |
| Hardcoding `--usb-id 0448` as a default | `0x0448` is a device ID in a bootloader-parameter table, not a confirmed USB PID; a wrong default filter would make discovery fail to find the real board |
| Bundling `dfu-util`, `PY32DfuTool` or `puyaisp` | External-binary discovery is the burden the pure-Python client exists to avoid; `PY32DfuTool` is Windows-x64 only |
| Weakening the beta-only channel gate to demonstrate anything | The gate graduates by deleting one tuple entry once a target is bench-validated |
| Bootloader self-update | Recoverability depends on the bootloader never being in the update path |
| Stable release / promotion to `main` | Operator-gated standing policy since v1.11; `main` is untouched in all three repos |

---

## Traceability

Populated 2026-07-30 by the v1.23 roadmap (`/gsd-new-milestone` → roadmapper). Exact 1:1 category→phase mapping — every requirement in a category maps to that category's single delivering phase; see `.planning/ROADMAP.md` §"v1.23 — PY32F071 Integration" for full success-criteria detail.

| Requirement | Phase | Status |
|-------------|-------|--------|
| BASE-01 … BASE-08 | Phase 123 | Complete |
| MERGE-01 … MERGE-08 | Phase 124 | Complete — all 8 ticked, see `124-NONREGRESSION.md` §3/§4 for the row cited per requirement |
| VPP-01 … VPP-03 | Phase 125 | Pending |
| CFG-01 … CFG-07 | Phase 126 | Pending |
| HOST-01 … HOST-08 | Phase 127 | Pending |
| REL-01 … REL-04 | Phase 128 | Pending |
| PCB-01 … PCB-05 | Phase 129 | Pending |
| CLOSE-01 … CLOSE-04 | Phase 130 | Pending |

**Coverage:**

- v1 requirements: **47** total (BASE 8 · MERGE 8 · VPP 3 · CFG 7 · HOST 8 · REL 4 · PCB 5 · CLOSE 4)
- Mapped to phases: **47**
- Unmapped: **0** ✓

---

## Operator Decisions Locked at Definition (2026-07-30)

Do not re-litigate these during planning.

1. **Scope** — firmware port stack + host DFU install + release-asset fold + VPP **seam only**. Calibration model out; the DAC closed loop out.
2. **Slot** — v1.23, retiring the queued v1.28/v1.29 py32 slots into it; `Binary Command Protocol` renumbers v1.23 → v1.28; v1.24–v1.27 untouched so existing by-number cross-references keep resolving.
3. **PR #45** — cherry-pick **nothing**; hand-author the seam. Confirmed necessary, not merely preferred: `05f4a77` carries a `CONFIG_VERSION "VER06"→"VER07"` bump, and `include/rurp_shield.h` is the only textual conflict anywhere in the six-branch inventory, between the py32 stack and PR #45.
4. **AVR flash constraint (A-5)** — restated as *"Leonardo flash must not grow; Uno-class growth ≤ 64 B, recorded"*, because the measured tree already fails a literal zero-growth rule on the two targets with ~8.3 KB spare while improving the binding target by 56 B. RAM joins the recorded baseline.
5. **Flash-persistent config (A-6)** — **in scope, with the design authored in-milestone**, vendoring the in-scope subset of blob `4b1a441` rather than citing a document stranded on a closed PR.
6. **DFU readback verification (N-03)** — **in scope**, failing soft on `bitCanUpload = 0`, with the claim ceiling *"asserted against a mock"*.

---
*Requirements defined: 2026-07-30*
*Last updated: 2026-07-30 after four-stream research + synthesis*

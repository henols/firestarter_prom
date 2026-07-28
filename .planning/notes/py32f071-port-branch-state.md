---
title: PY32F071 port — actual branch state (2026-07-28) + host FW-install seams
date: 2026-07-28
context: Captured during /gsd-explore 2026-07-28. Corrects the stale prior-art paragraph in the v1.28 ROADMAP entry and records the four host-side seams a fourth board target has to pass through. Companion to seed py32f071-no-external-tool-fw-install.md.
---

# PY32F071 port — what is actually on the branches

The v1.28 ROADMAP entry ([`ROADMAP.md`](../ROADMAP.md) line 33, written at the
2026-07-27 backlog review) says the work is **"not in flight"**, cites
`henols/firestarter` **PR #46 as closed unmerged**, and describes the surviving
prior art as `feature/py32f071-toolchain` @ `2c2ed10` — *603 additions across 8
files*. All three claims are out of date. Verified against `origin` on
2026-07-28.

## Real inventory (firmware repo, all forked off `beta`)

| Branch | PR | State | vs `beta` | Substance |
|---|---|---|---|---|
| `agent/py32f071-toolchain` | **#48** | **OPEN (draft)** | **52 ahead / 27 behind** | The live attempt. Base is `agent/portability-macros`, so it's a stacked PR. |
| `feature/py32f071-full-support` | #47 | CLOSED | 45 ahead / 27 behind | Superseded — see the weak-stub trap below. |
| `feature/py32f071-toolchain` | #46 | CLOSED | 11 ahead / 27 behind | The one the ROADMAP cites. Smallest of the set. |
| `agent/portability-macros` | — | (base of #48) | 5 ahead / 27 behind | The gh#16 HAL-prep half, on its own. |
| `feature/common-vpp-calibration` | #45 | CLOSED | 10 ahead / 27 behind | DAC/VPP calibration abstraction. |

`agent/rp2040-portability-macros` shares `agent/portability-macros`' head
(`52d6c1f`) — same content, different name.

**Every branch is 27 commits behind `beta`**, not stale-by-hundreds. The
"1 ahead / 2xx behind `main`" reading that suggests otherwise is an artifact of
`main` lagging `beta` by 224 commits (stable is operator-gated —
`feedback_stable_release_operator_gated`). Compare against `beta`, not `main`.

## PR #48 is much further along than the ROADMAP assumes

**PY32F071 CI is green** (`PY32F071 firmware` workflow, `agent/py32f071-toolchain`,
2026-07-21, three consecutive successes after four earlier failures). That build
is not a smoke test — `platform/py32f071/CMakeLists.txt` compiles the **shared**
Firestarter command processor, framing and PROM algorithms for Cortex-M0+:

- **Pinned official SDK** via CMake `FetchContent`:
  `https://github.com/OpenPuya/PY32F071_Firmware.git` @ `0ed2f4b4d3391eccfd4491006a30295fd78e32c2`
- **CherryUSB CDC** transport; 48 MHz PLL clock for native USB
- SysTick milliseconds + TIM3 microseconds
- VREFINT-compensated 12-bit ADC
- Contiguous 8-bit GPIO bus: one-snapshot `IDR` read, atomic `BSRR` write
- CI emits ELF / BIN / HEX / map / size report / SHA-256 checksums

The **"does this architecture even build"** risk is therefore retired. That was
the ROADMAP's implicit main unknown; it is not the unknown any more.

Firmware identity is already correct for the host: `RURP_BOARD_NAME = "py32f071"`,
`DATA_BUFFER_SIZE = 1024`.

## What is NOT done (per PR #48's own status + the code)

- **Pin map is an explicitly provisional placeholder** — PB0–PB7 data, PA0–PA5
  control, VPP on PA4/ADC ch4. It exists so the target compiles before a
  schematic. Must not be trusted near a PROM.
- **Config storage is runtime-only**, not flash-persistent. The part has no
  EEPROM, so the CRC-validated dual-slot flash scheme `PORTING.md` specifies is
  still unwritten.
- **Closed-loop DAC VPP** is on the *closed* PR #45, not on #48.
- **Zero hardware validation.** Nothing has run on silicon; no PCB exists
  (confirmed by operator, 2026-07-28).

## Trap: PR #47 looks complete and is not

`feature/py32f071-full-support` has a 24-file `platform/py32f071/` tree and a
CMake list that pulls in every common source — it reads as the most finished
branch. But its `src/usb.c` (141 lines) is a ring buffer over
`__attribute__((weak))` **no-op** low-level hooks:

```c
/* Official Puya CherryUSB glue overrides these low-level hooks. */
__attribute__((weak)) void py32_usb_ll_init(void) {}
__attribute__((weak)) bool py32_usb_ll_can_transmit(void) { return false; }
```

It links, and a board flashed with it would be **silent on USB**. `vpp_target.c`
is 13 lines. It also carries no SDK fetch. PR #48 is the one with a real stack —
start from #48, not #47.

## Host-side FW-install seams (firestarter_app)

A fourth board target touches exactly four places. `manage_firmware_update`
(version compare, channel selection, download, prompt, cleanup) is
board-agnostic and needs no change; the only line that cares is the single
flasher call at `firmware.py:640`.

| # | Seam | Today | Needs |
|---|---|---|---|
| 1 | Board identity | `firmware.py:113` parses `<version>:<board>[:<buf>[:<maxchunk>]]` | Nothing — `py32f071` flows through free |
| 2 | Release asset | `firestarter_{board}.hex`, hardcoded at `firmware.py:155`, `:237`, `:336` | Publish `firestarter_py32f071.hex` (or `.bin`) as a **release asset**. PY32 CI currently emits an *Actions artifact* named `firestarter-py32f071.hex` — hyphen, wrong prefix, wrong publication channel. Note the extension is baked into the pattern too. |
| 3 | Flasher | `_install_with_avrdude` (`firmware.py:420`) — if/elif ladder resolving `(partno, programmer_id, baud)` | avrdude cannot touch a Cortex-M0+. Extract a `FirmwareFlasher` strategy; `AvrdudeFlasher` keeps the ladder verbatim (uno / uno328pb-urclock / leonardo-avr109 are bench-earned, per `project_bench_findings_v15`). |
| 4 | CLI surface | `click.Choice(["uno","uno328pb","leonardo"])` at `cli_handlers.py:821`; `--avrdude-path` / `--avrdude-config-path` + the `avrdude-path` / `avrdude-config-path` config keys | Add the board; the avrdude-specific options and config keys need a per-flasher equivalent rather than a second hardcoded pair. |

**Reusable shape already present:** the Leonardo `avr109` path does a 1200-baud
touch in `avr_tool.py:115` (`_trigger_reset`) to drop the board into its
bootloader, then flashes what reappears. The install flow already tolerates the
port vanishing and coming back as a different USB device — which is precisely
what any bootloader-based PY32 path needs.

## Sizing

Host-side is **one phase**. The complexity is all firmware- and bench-side: real
pin map on a real PCB, flash-persistent config, DAC VPP, and the fourth-board
bench-cost multiplier the ROADMAP already flags. With no PCB, the honest
closeable scope is: land the portability + py32 stack onto `beta` (27 commits
behind), the host flasher seam, flash config, and the install-path design — all
software-testable.

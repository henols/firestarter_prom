---
title: PY32F071 firmware install with no external tools (self-flash bootloader over the existing transport)
trigger_condition: v1.28 PY32F071 Port is activated, OR the first PY32F071 PCB/schematic is specified — whichever comes first, because this decision imposes PCB requirements
planted_date: 2026-07-28
status: dormant
---

# PY32F071 firmware install with no external tools

How `firestarter fw --install` should reach a PY32F071 board, given the operator
constraint stated during /gsd-explore on 2026-07-28:

> "I want the most reliable and simple approach without having to install
> external tools."

and the fact that **no PCB exists yet** (paper-only, confirmed same day) — which
means the flash path can be *designed into* the board instead of worked around.

Evidence for the current branch state and the host-side seams this plugs into:
[`notes/py32f071-port-branch-state.md`](../notes/py32f071-port-branch-state.md).

## Decision: a self-flashing bootloader over the transport the app already speaks

A small bootloader in the first few KB of the 128 KiB flash, speaking the **same
USB CDC + COBS framing** the firmware already uses. The app sends the new image
over the serial port it already owns; the bootloader writes it to the application
region.

**Zero new host dependencies.** `pyserial` is already a firestarter_app
dependency. `_install_with_avrdude` is replaced by pure Python over the existing
transport — no binary discovery, no `avrdude.conf` analogue, no driver install.

This is structurally identical to how the Uno works today: bootloader preloaded
once at manufacture, then flashed over serial forever after. The PY32 self-flash
bootloader is the moral equivalent of the Arduino bootloader.

### Why every factory-bootloader route was rejected

The part *does* have a capable factory bootloader — Puya **UM1504** documents USB
DFU for PY32F071/F072/F403: system memory `0x1FFF0000–0x1FFF2F00`, USB on
PA11/PA12, DEV/PID `0x0448`, BL ID `0xA0`, entered with **BOOT0 high +
nBOOT1 = 1**. Reaching it from the host is the problem:

| Route | Why rejected |
|---|---|
| Puya `PY32DfuTool` | **Windows x64 only.** Unusable from a cross-platform Python CLI. |
| `dfu-util` | External binary — same PATH-discovery burden as avrdude, which is the thing the constraint is aimed at. |
| Vendored Python DFU over `pyusb` | Needs libusb. On Windows, raw USB access to a DFU device means installing a WinUSB driver via **Zadig** — an external tool install in all but name. Best *runner-up* if the bootloader work is deferred. |
| `puyaisp` (UART ISP) | Only needs `pyserial`, but drives the **UART** bootloader through a second USB-to-serial converter wired to PA2/PA3 (or PA9/PA10, PA14/PA15), with BOOT0 (PF4) high and nRST (PF2) pulsed. A dongle plus test-point access on a board that *has* native USB — a UX regression from today's single cable. |

Note the shared defect: the factory bootloader is entered by a **pin condition**,
so without firmware help every update is a button dance.

### Reliability comes from the standard pattern, not from optimism

- Bootloader **never self-updates** — it is written once and is not in the
  update path.
- Application image is **CRC-verified before the jump**; a failed CRC falls back
  into the bootloader rather than jumping into a half-written image.
- An interrupted transfer leaves the board in the bootloader, which is a
  *recoverable* state, not a brick.

## PCB requirements this imposes (the reason the trigger includes "first schematic")

Because the board is still paper, these are cheap now and expensive later:

1. **BOOT0 / nBOOT1 strapping** reachable (jumper, pad or button) so the factory
   USB DFU path stays available as a maintainer/manufacturing recovery route.
2. **SWD pads** exposed — the unconditional last resort.
3. **Contiguous 8-bit GPIO port** for the PROM data bus, so the one-snapshot
   `IDR` / atomic `BSRR` design on PR #48 holds. PR #48's provisional map uses
   PB0–PB7; confirm against the final package and pin multiplexing.
4. **Flash budget**: bootloader + application + the dual-slot CRC config region
   must fit 128 KiB with room to spare. Reserve the layout before writing either
   half.
5. Decide whether the app-side "reboot into bootloader" is a **protocol command**
   (preferred, matches the Leonardo 1200-baud-touch shape at `avr_tool.py:115`)
   or a strap-only operation.

External tools are acceptable on the recovery path — that path is for the
maintainer and the factory, never for an end user.

## Status: the USB DFU half is implemented (2026-07-28)

The operator asked for the USB install to be built rather than only designed, so
the **factory-USB-DFU** route — the runner-up in the table above, not the
self-flash bootloader — now exists on `firestarter_app` branch
`feature/py32f071-fw-install` @ `311eacf` (off `beta`), queued as milestone
**v1.29** in [`ROADMAP.md`](../ROADMAP.md). It is a pure-Python DFU client
(`firestarter/py32_dfu.py`), so no external *binary* is needed; the residual cost
is `pyusb` + a libusb backend, and a WinUSB driver on Windows.

That does **not** retire this seed. The self-flash bootloader is still the only
route with zero host-side USB plumbing, and it is what removes both the driver
friction and the `BOOT0` strap. The DFU path shortens the road to it rather than
replacing it: it proves the transfer sequence, and it stays as the
maintainer/manufacturing recovery route the PCB requirements below already
assume.

Operator-facing procedure and bootloader-entry table:
`firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md` on that branch.

## Open questions

- Does the Puya factory USB bootloader enumerate as something `dfu-util` can
  actually drive (standard DFU 1.1 vs DfuSe-flavoured, and its real USB VID/PID —
  UM1504's `0x0448` is a device ID, not necessarily the USB PID)? Answerable
  with one `lsusb` + one `dfu-util -l` **once silicon exists**. Needed for the
  recovery path even though self-flash wins the primary path.
- Can the application firmware jump to `0x1FFF0000` in software on PY32F071
  (Cortex-M0+ VTOR / SYSCFG `MEM_MODE` remap, STM32F0-style), or is BOOT0 the
  only entry? Determines whether recovery needs physical access.
- Does the host asset pattern need `.bin` alongside `.hex`? The pattern
  `firestarter_{board}.hex` at `firmware.py:155`/`:237`/`:336` bakes in the
  extension; a self-flash protocol most likely wants raw binary.
- Ordering vs **v1.26 White-Box Voltage-Reading Calibration**: the ROADMAP
  already sequences v1.28 after it so the VREFINT + two-point calibration model
  is defined once. Closed-loop DAC VPP (PR #45) partly supersedes v1.26's
  hand-set-pot procedure (`feedback_operator_adjusts_pot_solo`) — resolve which
  one owns the model before either is planned.

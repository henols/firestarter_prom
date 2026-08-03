# Stack Research

**Domain:** Fourth MCU board target (Puya PY32F071xB, Cortex-M0+) for an existing Arduino/AVR EPROM-programmer firmware, plus a host-side USB-DFU firmware installer for a mature cross-platform Python CLI
**Milestone:** v1.23 PY32F071 Integration
**Researched:** 2026-07-30
**Confidence:** HIGH on in-tree state (read directly from `origin` and from the pinned SDK commit), MEDIUM on upstream ecosystem facts (web-sourced), LOW on anything that would require silicon

---

## Evidence discipline

Every non-obvious claim below is tagged:

- **[PROVEN]** — read out of the tree, out of `git ls-remote`, out of the pinned SDK at commit `0ed2f4b`, or measured by running a command in this container. Reproduction command given.
- **[PREDICTED]** — inference from the above. Not observed. Must be confirmed by the phase that depends on it.
- **[UNVERIFIED]** — could not be established from an authoritative source; stated as unknown rather than guessed.

**No claim in this document asserts that anything works on PY32F071 silicon.** No PCB exists; nothing has ever run on this part. The permitted claims are: the target configures and compiles, the native and host suites pass, and the DFU sequence is exercised against descriptors and mocks.

---

## Recommended Stack

### Core Technologies — firmware (new, py32 target only)

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `arm-none-eabi-gcc` (Arm GNU Toolchain) | **13.2.Rel1** via Ubuntu noble `gcc-arm-none-eabi` `15:13.2.rel1-2`; **pin 14.2.Rel1 or 13.3.Rel1 explicitly** — see §4 | Cross-compiler for Cortex-M0+ | The only mainline free toolchain for the part. Puya's own SDK ships a GCC path (`Templates/PY32F071xx_Templates/EIDE/Makefile`) alongside Keil/IAR, so GCC is a first-class upstream target, not a community hack **[PROVEN]**. Keil MDK and IAR are proprietary and cannot run in this project's Ubuntu CI. |
| CMake + Ninja | CMake **≥ 3.20** (declared in `platform/py32f071/CMakeLists.txt:1`), Ninja any | Build system for the ARM target | PlatformIO has no PY32 platform. CMake keeps the ARM target fully orthogonal to `platformio.ini`, which is the single most important property for the hard acceptance constraint: **the AVR builds cannot be affected by a build system they do not use** **[PROVEN — the py32 target adds zero lines to `platformio.ini`]**. |
| OpenPuya PY32F071 SDK | **tag `1.1.1` = commit `0ed2f4b4d3391eccfd4491006a30295fd78e32c2`** | CMSIS device headers, HAL + LL drivers, startup reference, vendored CherryUSB | Official Puya driver library. The pin is exactly the latest release tag *and* `refs/heads/master` HEAD — see §1. BSD-3-Clause. |
| CherryUSB (device, CDC-ACM class) | **vendored, unversioned snapshot** inside SDK `1.1.1`; upstream project is at ~1.6.1 for reference only | Native USB full-speed CDC transport, replacing the AVR's UART | The PY32 device-controller port **exists only inside the Puya SDK** — see §2. There is no alternative that does not require writing a USB device stack. |
| CMSIS-Core (Cortex-M0+) | as shipped in SDK `Drivers/CMSIS/Include` (`core_cm0plus.h` present **[PROVEN]**) | Intrinsics, NVIC, SysTick | Comes with the SDK; no separate dependency. |
| No RTOS | — | — | The SDK vendors FreeRTOS (`Middlewares/Third_Party/FreeRTOS/Source` **[PROVEN]**) and it is deliberately not compiled. The firmware is a single `setup()`/`loop()` with one ISR (USB). Adding an RTOS would fork the shared command processor's execution model away from AVR. |

**Cortex-M0+ constraints that shape the above** — no hardware FPU, no hardware integer divide, Thumb-1 only (ARMv6-M): `-mcpu=cortex-m0plus -mthumb`, `--specs=nano.specs --specs=nosys.specs`, `-fno-exceptions -fno-rtti`, `-Os` — all already set **[PROVEN, `CMakeLists.txt:118-146`]**. Consequence to watch: any 64-bit or floating-point arithmetic links a libgcc soft-routine. `rurp_read_voltage_mv()` on the py32 backend does a `uint64_t` multiply **and divide** (`py32f071_rurp_shield.cpp:292-317` **[PROVEN]**), which pulls in `__aeabi_uldivmod` — measurable flash cost, and slow. Not a defect; a thing to measure rather than assume away.

### Core Technologies — host (new)

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **pyusb** | **`>=1.3.1,<2`** (currently pinned `>=1.2.1` on the branch — recommend raising, see §3) | Raw USB control transfers for the DFU 1.1 / DfuSe client | The only mature pure-Python route to a USB control endpoint. Latest release **1.3.1 (2025-01-08)**; `python_requires >=3.9.0`, which matches this package's `requires-python = ">=3.9"` exactly **[PROVEN via PyPI JSON]**. |
| libusb 1.x (system library) | any modern | pyusb's backend | pyusb is a ctypes wrapper and ships **no** binary. Backend is a platform prerequisite, not a pip dependency — this is the single largest UX cost of the DFU route. |
| Optional extra `[py32]` | already present, `pyproject.toml` `[project.optional-dependencies]` | Keeps pyusb out of the default install | AVR users (three of four boards) never touch USB. **Verified correct: `tests/test_py32_dfu.py` passes 58/58 with `usb` not importable in this container** **[PROVEN — `python3 -m pytest tests/test_py32_dfu.py -q` → 58 passed; `import usb` → ModuleNotFoundError]**. |

Unchanged host stack (no new dependency needed): `pyserial>=3.5`, `click>=8.1`, `rich>=14.0`, `requests>=2.20`, `tqdm>=4.60`, `packaging>=21.0`.

### Supporting Libraries / in-tree components

| Component | Where | Purpose | When it matters |
|-----------|-------|---------|-----------------|
| `include/rurp_platform.h` | firmware, **added by `agent/py32f071-toolchain`** (not by `agent/portability-macros` — see Correction C-1) | Platform ID + `RURP_MILLIS/MICROS/DELAY_US/DELAY_MS` indirection; `#error` on an unknown platform | Every new shared-code timing call site |
| `include/rurp_platform_compat.h` | firmware, added by `agent/portability-macros`, extended by the py32 branch (+19/−2) | PROGMEM/`PSTR`/`pgm_read_*`/`memcpy_P`/`F()` become direct accesses off-AVR | Compiling any AVR-authored TU for ARM or native |
| `include/avr/pgmspace.h` | firmware, added by `agent/portability-macros` | `#include_next`-based shim so legacy `#include <avr/pgmspace.h>` resolves everywhere | **AVR-affecting. See Rebase Hazard H-4.** |
| `platform/py32f071/include/Arduino.h` | firmware, py32-only include path | 76-line shim: `delayMicroseconds/delay/millis/micros` → `RURP_*`, `byte`, `HIGH/LOW`, and a `Py32SerialPort Serial` object | The pragmatic core of the port: shared code such as `include/rurp_register_utils.h` still calls `delayMicroseconds(1)`/`(4)` directly, and keeps working unchanged **[PROVEN]**. Do **not** "clean this up" — see What NOT to Add. |
| `firestarter/py32_dfu.py` | host, 833 lines | DFU 1.1 + DfuSe client, Intel-HEX/raw-bin loader, device-descriptor-driven dialect + geometry detection, `probe()` | Only reachable for `board == py32f071` |
| `firestarter/channel.py` | host | `is_prerelease_build()` + `BETA_ONLY_BOARDS = ("py32f071",)`; gates twice (Click choice list at import, and `firmware.py` refusal for library callers); **reads no env var, fails closed** | Keeps an unvalidated flash path off the stable channel |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `carlosperate/arm-none-eabi-gcc-action@v1` | Pin the ARM toolchain in CI | Supports explicit `release:` from `4.7-2013-q2` to `15.3.Rel1`; Linux/macOS/Windows; caches downloads and verifies MD5. **Recommended replacement for the apt install — see §4.** |
| `arm-none-eabi-size` | Flash/RAM accounting | Already run in `py32f071.yml`, **but only into the job log** — no artifact, no threshold, no gate **[PROVEN]**. The AVR side has a hard-won headroom discipline (Leonardo ~2992 B); the ARM side currently has none. |
| `ruff` `>=0.15.14` / `ruff format` / `mypy >=2.1.0` watermark / `pytest --cov-fail-under=70` | Host gates, unchanged | Measured on `feature/py32f071-fw-install`: `ruff check` clean, `ruff format --check` clean, **`check_mypy_watermark.py` → 1 error against a watermark of 35** **[PROVEN, run in this container under Python 3.12.13; CI targets 3.9/3.11 — the standing devcontainer caveat applies]** |
| `pio test -e native` | The non-negotiable regression oracle | The golden register traces + dispatch mirror are what prove "AVR unaffected". They are the acceptance instrument for the portability half. |

---

## Installation

```bash
# --- firmware, ARM target (Ubuntu / devcontainer; NOTHING here is on PATH today) ---
sudo apt-get update
sudo apt-get install -y cmake ninja-build gcc-arm-none-eabi binutils-arm-none-eabi
# ...or, preferred and reproducible:
#   carlosperate/arm-none-eabi-gcc-action@v1  with:  release: '14.2.Rel1'

cmake -S platform/py32f071 -B build/py32f071 -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build/py32f071          # FetchContent clones the SDK at 0ed2f4b on first configure
arm-none-eabi-size build/py32f071/firestarter_py32f071.elf

# --- firmware, AVR targets: unchanged, no new dependency ---
pio run -e uno && pio run -e uno328pb && pio run -e leonardo
pio test -e native

# --- host ---
pip install -e '.[test]'          # CI's install: pyusb NOT included, by design
pip install -e '.[test,py32]'     # adds pyusb — needed only to exercise the real USB path
# Linux additionally: libusb-1.0 + a udev rule (or root) for the DFU device
# Windows additionally: a WinUSB driver bound to the DFU device, via Zadig
```

---

## §1 — The Puya PY32F071 toolchain and SDK

### Is `OpenPuya/PY32F071_Firmware` the right upstream, and is the pin sound?

**Yes, and the pin is better than it looks.** **[PROVEN, `git ls-remote https://github.com/OpenPuya/PY32F071_Firmware.git`]**:

```
0ed2f4b4d3391eccfd4491006a30295fd78e32c2   HEAD
0ed2f4b4d3391eccfd4491006a30295fd78e32c2   refs/heads/master
0ed2f4b4d3391eccfd4491006a30295fd78e32c2   refs/tags/1.1.1
bef1774…  refs/tags/1.0.1     75413d1…  refs/tags/1.0.3     73e384c…  refs/tags/1.0.5
```

The pinned SHA is simultaneously the **latest release tag (`1.1.1`)** and `master` HEAD. So the port is not pinned to an arbitrary mid-stream commit; it is pinned to the current release, expressed immutably. **Keep the SHA** (a tag is mutable, a SHA is not) and add a one-line comment recording `= tag 1.1.1`, so a future reviewer can tell "current release" from "random commit" without running `ls-remote`.

Repository character: **BSD-3-Clause**, ~154 KiB packed, 7 commits, 4 stars, 3 forks **[PROVEN + web]**. That is a vendor drop-and-tag repo, not a living community project. Practical consequences:

- **Low churn is a feature here.** There is nothing to track; the pin will go stale slowly and visibly (a new tag), not silently.
- **Low bus factor is a real risk.** 4 stars means effectively zero third-party validation. **Mitigation: vendor-in a mirror, or at minimum record the SHA-256 of the fetched tree**, so a force-push or repo deletion does not brick the build. `FetchContent` with `GIT_SHALLOW FALSE` will happily fail the whole CI job if GitHub or the org disappears.

### What CMSIS/HAL/LL structure it exposes **[all PROVEN by sparse checkout at `0ed2f4b`]**

| Path | Contents |
|---|---|
| `Drivers/CMSIS/Include/` | Standard CMSIS-Core, incl. `core_cm0plus.h` |
| `Drivers/CMSIS/Device/PY32F071/Include/` | `py32f0xx.h`, `py32f071x6/x8/x9/xB.h`, `system_py32f0xx.h` |
| `Drivers/PY32F071_HAL_Driver/Inc/` | **Both** layers side by side: `py32f071_hal_*.h` (adc, adc_ex, comp, cortex, crc, **ctc**, dac, dac_ex, dma, exti, flash, gpio, i2c, i2s, iwdg, lcd, lptim, opa, pwr, rcc, rcc_ex, rtc, spi, tim, uart, usart, wwdg, div) **and** `py32f071_ll_*.h` |
| `Drivers/CMSIS/DSP_Lib/` | Full CMSIS-DSP source — large, entirely unused, and correctly not compiled |
| `Middlewares/Third_Party/` | `CherryUSB/`, `FreeRTOS/Source/` |
| `Projects/PY32F071-STK/` | HAL `Example/`, `Example_LL/`, and `Applications/USB_Device/{USBD_Virtual_COM_Port, USBD_Keyboard, USBD_Audio, USBD_USBFlashDisk, …}` |
| `Templates/PY32F071xx_Templates/` | `Inc/py32f071_hal_conf.h`, `Src/system_py32f071.c`, and **four** toolchain variants: `MDK-ARM`-style, `EWARM/`, and **`EIDE/` with a GCC `Makefile`, `py32f071xb.ld` and `startup_py32f071xx.s`** |

**Every one of the 15 SDK paths the Firestarter `CMakeLists.txt` names exists at the pinned commit** — verified individually with `git cat-file -e` **[PROVEN]**. The CMake list is correct against the pin; it is *not* correct against `beta` (see Rebase Hazard H-1).

### Gotchas of building PY32 parts with mainline GNU Arm vs Keil / Puya tooling

1. **[PROVEN, and this is a real defect worth fixing] Wrong flash latency constant.** The port's `configure_system_clock()` (`platform/py32f071/src/main.cpp`) is otherwise a faithful copy of Puya's own CDC reference (`Projects/PY32F071-STK/Applications/USB_Device/USBD_Virtual_COM_Port/Src/main.c`: HSI @ `RCC_HSICALIBRATION_24MHz`, `HSEState = RCC_HSE_OFF`, `PLLSOURCE_HSI`, `PLLMUL = RCC_PLL_MUL2` → 48 MHz). But the last argument diverges. The reference passes `FLASH_LATENCY_1`; the port passes `FLASH_ACR_LATENCY_1`. In the SDK headers:
   ```
   py32f071_hal_flash.h:134   #define FLASH_LATENCY_1   FLASH_ACR_LATENCY_0   /* 24MHz < SYSCLK <= 48MHz */
   py32f071_hal_flash.h:135   #define FLASH_LATENCY_2   FLASH_ACR_LATENCY_1   /* 48MHz < SYSCLK <= 72MHz */
   py32f071xB.h:2451-2452     FLASH_ACR_LATENCY_0 = 0x1 ,  FLASH_ACR_LATENCY_1 = 0x2
   ```
   So the port configures **two** wait states where one is correct. This is *safe* (excess latency never corrupts) but it silently slows every flash fetch on a part that must sustain USB servicing alongside tight PROM bus timing. One-token fix; catch it now, because a timing anomaly discovered after a PCB exists will be blamed on the board.
2. **`#include_next` is a GCC extension.** `include/avr/pgmspace.h` relies on it. Fine for avr-gcc and arm-none-eabi-gcc (both GCC), would break under Clang-based tooling. Acceptable; record it as a constraint, not a bug.
3. **Two sources of truth for startup and memory map.** The port wrote its own `startup/startup_py32f071.s` (149 lines) and `linker/PY32F071xB_FLASH.ld` (128K FLASH @ `0x08000000`, 16K RAM @ `0x20000000`, `_Min_Heap_Size = 0x000`, `_Min_Stack_Size = 0x400`) **[PROVEN]** rather than using the SDK's `Templates/.../EIDE/{startup_py32f071xx.s, py32f071xb.ld}`. Recommend a one-time diff of the port's vector table against upstream's — a missing or misordered vector on M0+ is a silent hard-fault, and it is the classic hand-rolled-startup failure.
4. **`--specs=nosys.specs` means `_sbrk` is a stub.** Combined with `_Min_Heap_Size = 0x000`, any `malloc` returns NULL. This is *safe here* — see §2 — but it is a landmine for anyone who later adds a class driver or a `printf("%f")`.
5. **No `-Werror`, no `-flto`.** `-Wall -Wextra` are on. Reasonable for an unproven port; `-Werror` on a vendored HAL would be a losing battle.
6. **Crystal-less USB is Puya-sanctioned, and there is a fallback if it disappoints.** Upstream's own USB CDC example runs USB off HSI+PLL with HSE off — identical to the port **[PROVEN]**. The part additionally has a **CTC (clock trim controller)** peripheral — `py32f071_hal_ctc.h` and `Example/CTC/CTC_Autotrim` **[PROVEN]** — the PY32 analogue of STM32's CRS, for SOF-based HSI trimming. Neither the reference nor the port enables it. **PCB consequence, cheap now:** keep an HSE crystal footprint (and its two load caps) on the first schematic as depopulated. Whether crystal-less enumeration is stable on this silicon is **[UNVERIFIED]** and unverifiable without a board; a footprint is the cheapest possible hedge.

---

## §2 — CherryUSB for the PY32 USB CDC device

### Maturity, provenance, licence

- **Licence: Apache-2.0** **[PROVEN — `Middlewares/Third_Party/CherryUSB/LICENSE`]**. Compatible with the project's MIT.
- **The vendored copy carries no version identifier at all.** No `CHERRYUSB_VERSION` macro, no changelog, no version header anywhere in the snapshot **[PROVEN by grep]**. It is a frozen fork, dated only by SDK tag `1.1.1`.
- **The PY32 device-controller port does not exist upstream.** Upstream `cherry-embedded/CherryUSB` `port/` contains `aic, bouffalolab, ch32, chipidea, dwc2, ehci, fsdev, hpmicro, kinetis, musb, nuvoton, nxp, ohci, pusb2, renesas, rp2040, template, xhci` — **no `py32`, no `puya`** **[PROVEN by fetching the upstream `port/` listing]**. Puya wrote `port/usb_dc_py32.c` + `port/usb_py32_reg.h` themselves rather than reusing `fsdev` (the ST FS-device IP port, which the PY32 USB IP most likely resembles).

**The honest characterisation: this is not "CherryUSB", it is "Puya's CherryUSB fork".** Consequences the roadmap must accept explicitly:

- Upstream CherryUSB releases (docs sit at ~1.6.1) **cannot be adopted** without re-porting `usb_dc_py32.c`. Do not write a requirement or a dependency-update policy that implies otherwise.
- Upstream CherryUSB bug fixes to `usbd_core.c` / `usbd_cdc.c` reach this project only when Puya cuts a new SDK tag. Track the SDK tag, not CherryUSB.
- If the PY32 USB IP *is* `fsdev`-compatible, retargeting onto upstream `port/fsdev` is a plausible future escape hatch. **[PREDICTED — not investigated, and it needs silicon to validate. Do not scope it here.]**

### How the device-CDC stack is configured **[all PROVEN]**

`platform/py32f071/include/usb_config.h` (34 lines) is the whole knob set: `CONFIG_USB_PRINTF` compiled out, `CONFIG_USB_DBG_LEVEL = USB_DBG_ERROR`, `CONFIG_USB_ALIGN_SIZE 4`, `CONFIG_USBDEV_REQUEST_BUFFER_LEN 256`, `usb_malloc → malloc`, IRQ named `USBD_IRQn`/`USBD_IRQHandler`.

`platform/py32f071/src/usb_cdc.c` (306 lines) builds a single-configuration CDC-ACM device by hand: EP `0x81` bulk IN / `0x02` bulk OUT / `0x83` notification, `wMaxPacketSize = 64`, bus-powered, 100 mA, string descriptors "Firestarter" / "Firestarter PY32F071" / serial `00000001`. `usbd_cdc_acm_set_dtr`/`set_rts` are deliberate no-ops. Two `usbd_interface` structs, two endpoint callbacks, `usbd_initialize()`, `NVIC_EnableIRQ`.

Above that sits a byte ring-buffer pair exposed as `py32_usb_available/read/peek/read_bytes/write/flush`, which `platform_compat.cpp` wraps as `Py32SerialPort Serial` — so the shared framing layer sees the same `Serial`-shaped object it sees on AVR.

**Note the `usb_config.h` include of `"py32f0xx_hal.h"`** — that header does exist (`Drivers/PY32F071_HAL_Driver/Inc/py32f0xx_hal.h`) **[PROVEN]**, alongside the `py32f071_hal_conf.h` the port supplies locally. Not a bug, just an inconsistent naming convention inherited from the SDK.

### RAM footprint against 16 KiB total

| Allocation | Bytes | Source |
|---|---|---|
| `rx_buffer` | 1024 | `usb_cdc.c:15,72` |
| `tx_buffer` | 1024 | `usb_cdc.c:16,73` |
| `cdc_out_packet` + `cdc_in_packet` | 128 | `usb_cdc.c:69-70` |
| `usbd_core_cfg_priv.req_data[CONFIG_USBDEV_REQUEST_BUFFER_LEN]` | 256 | `usbd_core.c:40` + `usb_config.h` |
| rest of `usbd_core_cfg_priv` (device state, interface/endpoint tables) | ~200–400 **[PREDICTED]** | `usbd_core.c:26-56` |
| Firestarter data buffer | **512** — `DATA_BUFFER_SIZE=512`, see Correction C-2 | `CMakeLists.txt:113` |
| stack reservation | 1024 | linker `_Min_Stack_Size = 0x400` |
| heap | **0** | linker `_Min_Heap_Size = 0x000` |

That is roughly **4.2–4.4 KiB of ~16 KiB accounted for [PREDICTED]**, before `firestarter_handle_t`, the jsmn token array, and HAL handle structs. Comfortable, but **not measured** — `arm-none-eabi-size` gives real `.data`+`.bss`, and CI already runs it. **Recommendation: capture the size line as a checked-in baseline with a RAM ceiling, the ARM analogue of the AVR flash-headroom discipline.** Today the number scrolls past in a job log and nobody would notice a 3 KiB regression.

**The heap question resolves cleanly, and it is the finding that most changes the risk picture.** `_Min_Heap_Size = 0x000` + `nosys.specs` means `malloc` cannot succeed — yet `usb_config.h` maps `usb_malloc → malloc`. Grepping the vendored stack: **`usb_malloc`/`usb_free` are called only from `class/printer/usbd_printer.c`, `class/audio/usbd_audio.c`, `class/vendor/axusbnet.c`, and the `usb_mem.h` alignment helpers — never from `core/usbd_core.c` and never from `class/cdc/usbd_cdc.c`** **[PROVEN by grep across the snapshot]**. A CDC-only build therefore never allocates. The zero heap is correct, and the `usb_malloc` macro is inert boilerplate. **But it is a tripwire:** the day someone adds MSC, printer or audio, the failure mode is a NULL deref at enumeration, not a link error. Worth one comment in `usb_config.h`.

### Fit for a device that must also stream PROM data

Good fit, with two things to watch **[both PREDICTED — no silicon]**:

1. **Throughput headroom is large but the buffer is the choke point.** USB FS bulk gives ~1 MB/s theoretical against the 250000-baud UART's ~25 kB/s. A 64-byte MPS with 1 KiB rings and a 512-byte protocol buffer is more than adequate. The zero-length-packet handling in `firestarter_cdc_bulk_in` (`byte_count % 64 == 0` → send ZLP) is present and correct — that is the single most commonly botched detail in a hand-rolled CDC and it is right here **[PROVEN by reading it]**.
2. **`py32_usb_write` blocks with a 100 ms deadline and spins `usb_start_next_transmit_safe()` with interrupts masked.** `usb_start_next_transmit_safe` does `__disable_irq()` / conditional `__enable_irq()` around the transmit kick (`usb_cdc.c:109-118`). Called from inside a PROM programming loop that has microsecond-critical strobes, an unbounded-ish spin with IRQs toggled is exactly the shape of an intermittent-timing bug. **Flag: the phase that lands this must state that USB flushes never occur inside a program-pulse window, or prove it.** On AVR this hazard does not exist because the UART is polled and blocking is bounded by the shift register.

### Interaction risk with the existing COBS framing layer

**Low, and structurally so** **[PROVEN reasoning, PREDICTED outcome]**. The v1.10 transport is COBS `0x00` delimiting + CRC8-CCITT with automatic resync, riding on top of an opaque byte stream. Specifically:

- COBS never emits `0x00` inside a frame, so nothing in the framing collides with CDC's byte transparency (CDC-ACM is a pure byte pipe; there is no XON/XOFF, no escaping).
- The port replaces the transport's *substrate*, not the transport. `Serial` keeps the same method surface; `rurp_serial_utils.h` is untouched apart from swapping `<avr/pgmspace.h>` for `"rurp_platform_compat.h"`.
- `usbd_cdc_acm_set_dtr`/`set_rts` being no-ops means **no DTR-triggered reset**. That deletes a whole class of AVR-only weirdness (the `hold_rail.py` DTR-reset-on-close problem) — but it also deletes the 1200-baud-touch reset mechanism that `avr_tool.py:115` uses for Leonardo. **Consequence for the self-flash-bootloader seed: "reboot into bootloader" on py32 must be a protocol command, not a baud-rate trick.** The seed already prefers that; this makes it mandatory rather than preferred.
- The genuinely new failure mode is **framing loss across a USB reset/re-enumeration**, which has no AVR analogue. The COBS resync is designed for exactly this (byte loss mid-stream → next `0x00` re-syncs), so the mechanism is present; whether it recovers gracefully is **[PREDICTED]** and only testable on silicon. `cobs-decoder-framelevel-deadline-wr01` (a carried-forward medium todo) is the item this touches.

---

## §3 — The host-side USB DFU dependency

### pyusb status

- **Latest 1.3.1, released 2025-01-08** (1.3.0 was 2025-01-01; before that 1.2.1 in 2021-07-09) **[PROVEN via `pypi.org/pypi/pyusb/json`]**. BSD licence. `python_requires >= 3.9.0`.
- The 3½-year gap between 1.2.1 and 1.3.0 is the honest read on the project: **maintained but slow**. It is a thin ctypes shim over a very stable C API, so slow is not the same as risky here.
- **Raise the floor.** The branch pins `pyusb>=1.2.1`. Recommend **`pyusb>=1.3.1,<2`**: 1.2.1 predates Python 3.12 and would be resolved by pip on a fresh 3.12/3.13 install where nobody has tested it, and the `<2` cap protects against a hypothetical API break. Cost of raising: zero — nothing in `py32_dfu.py` uses anything older than `usb.core.find` / `ctrl_transfer` / `usb.util.get_string`.

### Backend requirement per platform

pyusb ships **no** binary; it dlopen's a backend. This is the entire UX cost of the DFU route.

| Platform | Backend | Practical friction |
|---|---|---|
| Linux | `libusb-1.0` — present on essentially every desktop distro | **Plus** a udev rule granting the user access to the DFU VID/PID, or `sudo`. Real friction, easily documented, one file. |
| macOS | `libusb` via Homebrew/MacPorts, not in the base OS | `brew install libusb`. An extra install step, but a normal one. |
| **Windows** | `libusb-1.0.dll` **plus a WinUSB/libusbK/libusb-win32 driver bound to the specific device** | **This is the hard one.** Windows will not hand raw USB to a userspace process for a device claimed by another driver. The DFU device needs WinUSB bound to it, and the near-universal way to do that is **Zadig** — a GUI, downloaded from a third-party site, run as administrator, that rebinds a driver. Without it, `usb.core.find` returns nothing or raises `NoBackendError`. **[PROVEN via libusb project's own Windows wiki + pyusb's own issue tracker]** |

The `doc/PY32F071-FIRMWARE-INSTALL.md` on the branch states all of this plainly (§"Dependencies", lines 75-92) and `py32_dfu.PyusbMissingError` reproduces it in the error text **[PROVEN]**. The honesty is already in place; the friction is not removed by it.

### Packaging as an optional extra — and the long-term verdict

**Yes, an optional-extra pyusb dependency is defensible long-term for this CLI. Three reasons, all verifiable rather than aspirational:**

1. **It is genuinely optional, and that is proven, not asserted.** `_require_usb()` imports `usb.core` lazily inside a function (`py32_dfu.py:370-383`), never at module scope. The `[py32]` extra is not in `[test]`, CI installs `.[test]` only, and **the 58-test suite passes with `usb` uninstallable** **[PROVEN, measured here]**. Three of four boards, and 100 % of read/write/verify functionality, never import it. A user who never touches a PY32 never learns pyusb exists.
2. **The blast radius of the hard part is bounded to one board on one channel.** `channel.py` keeps `py32f071` in `BETA_ONLY_BOARDS`, so a stable-channel user cannot even see the board in `fw --help`. The Zadig story is currently owed only to pre-release users who have hand-built a board that does not exist. That is an acceptable audience for a driver-install instruction.
3. **The seed's primary route retires the dependency without wasting this work.** The self-flash bootloader over the existing CDC + COBS transport needs `pyserial` only — already a hard dependency. When it lands, `py32_dfu.py` becomes the *maintainer/factory recovery* path, where "run Zadig once" is entirely reasonable. So the pyusb extra is not a permanent tax on end users; it is a permanent tax on maintainers. **This is exactly the right allocation, and it should be stated as a decision rather than left as a drift.**

**The one caveat worth writing into a requirement:** because CI never installs pyusb, **the real `import usb` path is never exercised anywhere** — not in CI, not in the devcontainer. Recommend one cheap addition: a CI job (or a `pytest` marker) that installs `.[test,py32]` and asserts `import firestarter.py32_dfu; py32_dfu._require_usb()` succeeds and `find_dfu_interfaces()` returns without raising on an empty bus. That catches a pyusb API break in 3 seconds, and it is the only gap in an otherwise well-sealed optional dependency.

### Comparison against the rejected routes

The seed's rejection table holds up. Re-stating it with what this research adds:

| Route | Host cost | Verdict |
|---|---|---|
| **Vendored Python DFU over pyusb** *(this branch)* | pyusb + libusb; Zadig on Windows | **Accepted as runner-up.** No external *binary*; the transfer sequence gets proven; discovery is by interface class, not a guessed VID/PID, so it is robust to the unknown bootloader ID. |
| Puya `PY32DfuTool` | **Windows x64 only** | Disqualified on portability alone. A cross-platform pip CLI cannot depend on it. |
| `dfu-util` | External binary + PATH discovery | Reintroduces precisely the avrdude problem the operator constraint targets. `avrdude-mcu-detection-fallback` is still an open todo — evidence the burden is real and recurring, not theoretical. |
| `puyaisp` (UART ISP) | `pyserial` only — **cheapest dependency** | Disqualified on *hardware* UX: needs a second USB-serial dongle on PA2/PA3, plus BOOT0 (PF4) high and nRST (PF2) pulsed, on a board that already has native USB. A UX regression from today's one cable. |
| **Self-flash bootloader over CDC + COBS** *(the seed's decision)* | **zero new dependencies** | The intended primary route. Not this milestone. |

**Bottom line: land pyusb as an optional extra, raise the floor to 1.3.1, and record in the milestone that this does not retire the seed.** The one thing this milestone genuinely must capture is the PCB consequences (BOOT0/nBOOT1 strap, SWD pads, contiguous 8-bit port, flash-budget reservation for bootloader + app + dual-slot config, an HSE footprint, and a real USB VID/PID) — because the board is paper and all of those are cheap now.

---

## §4 — Toolchain in CI

**Current state [PROVEN, `.github/workflows/py32f071.yml`]:** `runs-on: ubuntu-latest`, then `apt-get install -y cmake ninja-build gcc-arm-none-eabi binutils-arm-none-eabi`.

**Assessment: acceptable for a bring-up branch, wrong for a target that publishes a release asset.** Three concrete drift sources:

1. **`ubuntu-latest` is a moving label, and it is about to move again.** It has meant Ubuntu 24.04 (noble) since the Dec-2024→Jan-2025 migration; Ubuntu 26.04 images are already selectable and GitHub has announced upcoming migrations. **[PROVEN-ish: web-sourced GitHub changelogs, LOW confidence on exact dates]** When `-latest` flips, the apt-provided compiler changes underneath the workflow with no diff in the repository.
2. **apt's compiler is distro-pinned to one version per release.** On noble, `gcc-arm-none-eabi` is **`15:13.2.rel1-2`** → GCC 13.2 / Arm GNU Toolchain 13.2.Rel1 **[MEDIUM confidence, web-sourced from Ubuntu/Launchpad package pages]**. Fine today. But it is a *different* compiler from the one a maintainer has locally, and a different one again after the next image migration. Arm GNU Toolchain 14.x/15.x is current upstream.
3. **The published artifact is a firmware binary.** For the AVR targets, reproducibility is underwritten by PlatformIO's own pinned package versions. The ARM target has no equivalent, so the same source can produce a different `firestarter_py32f071.hex` on two runs weeks apart, with no record of why. On a project that has repeatedly used *byte-identical golden artifacts* as proof (v1.16's golden register traces, v1.22's FIX-04 blob-SHA freeze), an unpinned compiler is inconsistent with the house standard.

**Recommendation — pin explicitly, and pin the runner too:**

```yaml
    runs-on: ubuntu-24.04                 # not -latest: an image migration must be a decision
    steps:
      - uses: carlosperate/arm-none-eabi-gcc-action@v1
        with:
          release: '14.2.Rel1'            # or 13.3.Rel1 to stay close to noble's apt version
      - run: sudo apt-get update && sudo apt-get install -y cmake ninja-build
```

That action supports every release from `4.7-2013-q2` to `15.3.Rel1`, runs on Linux/macOS/Windows, caches the download, and MD5-verifies it **[PROVEN via its own README]**. Cost: one extra action dependency and ~10 s uncached. Benefit: the compiler version becomes a reviewable line in a diff, and a maintainer can reproduce a CI binary locally by reading the workflow.

**Second, unrelated CI finding, and it is the more urgent one [PROVEN]:** `py32f071.yml` triggers on **`pull_request` and `workflow_dispatch` only — there is no `push` trigger**. Its `paths:` filter includes `src/**` and `include/**`, so during PR review an AVR-only change *does* get ARM-checked. But **once this lands on `beta`, nothing gates the ARM build on `beta` at all.** Any subsequent AVR-only commit pushed to `beta` can break the ARM target silently, and it will only surface at the next PR that happens to touch a filtered path — or at a release. Given that the milestone's whole point is to publish `firestarter_py32f071.hex` as a real release asset, **add `push: branches: [beta]`** (or accept the gap explicitly and in writing).

**Third [PROVEN]:** the `README.md` §"Release integration" snippet argues correctly that `softprops/action-gh-release` warns on an unmatched glob but fails on a missing literal file — and then gives `build/py32f071/firestarter_py32f071.hex`, **a literal path**, for the py32 line. Whether that literal actually fails-hard is worth one check against the action's `fail_on_unmatched_files` default before relying on the stated reasoning; the *intent* (a broken ARM build must never block the AVR beta) is right and should survive into implementation, plus `continue-on-error: true` on the three ARM steps while the target is unproven.

---

## Rebase Hazard Ledger

Every py32 branch is **72 commits behind `beta`** (`feature/py32f071-release-assets` is 53 ahead / 72 behind; `agent/py32f071-toolchain` is 52 ahead / 72 behind) **[PROVEN, `git rev-list --left-right --count origin/beta...HEAD`]**. These are the stack-level collisions that fall out of those 72 commits. **This is the section a roadmap should turn into tasks.**

| # | Hazard | Evidence | Severity |
|---|---|---|---|
| **H-1** | **The CMake source list names two files that no longer exist.** `platform/py32f071/CMakeLists.txt:46-47` lists `src/proms/flash_type_3.cpp` and `src/proms/flash_type_4.cpp`. On `beta` those are `flash_nor_unlock.cpp` and `flash_5v_page.cpp` (v1.19 Phase 104). CMake fails at *configure* on a missing explicit source. | `git ls-tree --name-only origin/beta -- src/proms/` vs the same on the py32 branch **[PROVEN]** | **Blocking.** Two-line fix, but the ARM build is dead on arrival until it is made. |
| **H-2** | **The explicit source list is a hard-coded manifest with no drift detector.** It omits `src/dev_tools.cpp` (guarded by `#ifdef DEV_TOOLS`, so fine) and `src/rurp_config_utils.cpp` (superseded by the py32's own `config.cpp`, so fine) — but nothing *checks*. v1.22 alone added +619 lines to `eeprom_28c.cpp`, a new `include/proto_constants.h`, and +81 to `firestarter.h`. Any future `src/proms/*.cpp` addition silently fails to compile for ARM. | `git diff --stat origin/agent/py32f071-toolchain origin/beta -- include/ src/` **[PROVEN]** | **High.** Recommend a `GLOB` with an explicit exclusion list, or a check script that diffs the CMake list against `src/proms/*.cpp`. |
| **H-3** | **`DEV_TOOLS` is not defined for the ARM target**, so `dev reg` has no firmware half on py32 by construction. That is probably *correct* and aligns with the 999.15/gh#8 dev-tools channel split — but it is currently an accident of the CMake defines, not a decision. | `CMakeLists.txt:105-114` has no `DEV_TOOLS` **[PROVEN]**; `src/firestarter.cpp` guards `dev_tools.h` with `#ifdef DEV_TOOLS` **[PROVEN]** | Medium. Make it an explicit, commented decision. |
| **H-4** | **`agent/portability-macros` is the AVR-affecting half, not the py32 half.** Its 4-file diff touches `include/rurp_shield.h` (45 lines) and `include/rurp_serial_utils.h`, and adds `include/avr/pgmspace.h` — which sits on the **shared** include path and shadows the toolchain's `<avr/pgmspace.h>` for AVR builds via `#include_next`. Meanwhile the py32 stack on top touches **only new files plus `rurp_platform_compat.h` (+19/−2)**. | `git diff --stat $(git merge-base origin/beta origin/agent/portability-macros) origin/agent/portability-macros` → 4 files; `git diff --stat origin/agent/portability-macros origin/agent/py32f071-toolchain` → 19 files, all new bar one **[PROVEN]** | **High.** Sequence and gate accordingly: the portability merge is where `pio test -e native` and the golden traces earn their keep, not the py32 merge. |
| **H-5** | **`rurp_shield.h` converts `rurp_chip_enable()` / `rurp_chip_disable()` / `rurp_chip_output()` / `rurp_chip_input()` / `rurp_set_chip_enable()` / `rurp_set_chip_output()` from function-like macros to `static inline` functions**, and `rurp_set_programmer_mode()` / `rurp_set_communication_mode()` from `((void)0)` macros to typed inline no-ops on the non-AVR branch. Semantically better (single argument evaluation, type-checked). But these are the exact call sites the golden register traces and the `HOST_STUBS_RECORD_BUS` recorder observe, and `include/rurp_register_utils.h` deliberately *elides* redundant register writes — a mechanism the native stubs have already been caught mis-modelling once. | The `rurp_shield.h` hunk **[PROVEN]**; `rurp_register_utils.h` elision logic **[PROVEN]** | **High.** Require: golden traces byte-identical, and a measured Leonardo flash delta. Expect ~0 B **[PREDICTED — `-Os` should emit identical code]**, but v1.22 predicted a saving and measured **+204 B**. Measure; do not predict. |
| **H-6** | **`rurp_register_utils.h` is a header containing non-inline definitions**, included by exactly one TU per link (`uno_rurp_shield.cpp` / `leonardo_rurp_shield.cpp` / a native `host_stubs.cpp` / **`py32f071_rurp_shield.cpp`**). It is **byte-identical between `beta` and the py32 branch** — so the pattern is respected today. Any future TU that includes it produces duplicate symbols. | `git diff origin/beta origin/agent/py32f071-toolchain -- include/rurp_register_utils.h` → empty; `git grep -l` for includers **[PROVEN]** | Low today, worth a comment. |
| **H-7** | **`platform/py32f071/cmake/write_checksums.cmake` is orphaned** — zero references anywhere in the repo after `ad47c3b` narrowed the CI to publish only the install image. | `grep -rn write_checksums` across `*.txt`, `*.cmake`, `*.yml` → no hits **[PROVEN]** | Trivial. Delete it, or re-wire it; do not leave dead build tooling in a first-landing. |
| **H-8** | **No `PORTING.md` exists on any py32 branch.** Both `PROJECT.md` and `STATE.md` cite "the CRC-validated dual-slot flash records per `platform/py32f071/PORTING.md`" as the specification for the flash-persistent-config feature. That file is not in the tree, and `platform/py32f071/README.md` does not describe the scheme either. | `git ls-tree -r --name-only HEAD \| grep -i porting` → empty, on all py32 branches **[PROVEN]** | **High — scope hazard.** The flash-config requirement currently has **no in-tree design**. Either the design must be authored inside this milestone (real work, not integration), or the requirement must be scoped down. Do not let a planning document's citation stand in for a spec that does not exist. |

---

## Corrections to the planning record

The downstream consumer was warned that a previous planning document asserted a stale branch state which propagated into scope. Here are the ones this research found. **All verified against `origin` on 2026-07-30.**

- **C-1 — The portability header is `include/rurp_platform_compat.h`, and `include/rurp_platform.h` comes from the *py32* branch, not the portability branch.** `PROJECT.md` §"Current Milestone" attributes "`include/rurp_platform.h` normalized platform IDs" to `agent/portability-macros`. That branch's entire diff is `include/avr/pgmspace.h`, `include/rurp_platform_compat.h`, `include/rurp_serial_utils.h`, `include/rurp_shield.h` — **`rurp_platform.h` is not in it** (`git show origin/agent/portability-macros:include/rurp_platform.h` → *"exists on disk, but not in"*). It is added by `agent/py32f071-toolchain` (51 lines), and it is the file carrying `RURP_MILLIS/MICROS/DELAY_*` and the `#error "Unsupported Firestarter target platform"` fail-closed arm. **[PROVEN]** Consequence: the portability-only merge does **not** deliver the timing indirection; the two merges cannot be split along the line PROJECT.md implies.
- **C-2 — `DATA_BUFFER_SIZE` on the ARM target is `512`, not `1024`.** `platform/py32f071/CMakeLists.txt:113` reads `DATA_BUFFER_SIZE=512`, on both `agent/py32f071-toolchain` and `feature/py32f071-release-assets`. The branch-state note and `PROJECT.md`/`STATE.md` both say 1024. **[PROVEN]** This matters: the v1.10 CAP-01 buffer advertisement means the host will chunk to 510 bytes, not 1022, so any "py32 matches Leonardo throughput" expectation is wrong; and a later bump to 1024 is a *wire-visible behaviour change*, not a constant tweak. (The USB CDC ring buffers are independently 1024 each — that is probably where the 1024 came from.)
- **C-3 — "27 commits behind `beta`" is stale.** `.planning/notes/py32f071-port-branch-state.md` (2026-07-28) says 27. Measured today: **72 behind** for every py32 branch. `PROJECT.md`'s figure is the correct one; the note is not. **[PROVEN]**
- **C-4 — The host test count is 58 passing (46 `def test_` functions), not 44.** The note says 44 unit tests. **[PROVEN — `pytest tests/test_py32_dfu.py -q` → 58 passed]**
- **C-5 — The seed's open question about `.hex` vs `.bin` is already answered on the branch.** `firmware.py::asset_candidates()` returns `[firestarter_<board>.hex, firestarter_<board>.bin]` for DFU boards (hex first — it carries its own load address, which the flash-envelope guard validates) and `[.hex]` for AVR; the CMake target emits both, and the release publishes only the hex. **[PROVEN, commit `cd7c10c`]** That seed bullet can be closed rather than re-researched.
- **C-6 — `feature/py32f071-release-assets` is exactly `agent/py32f071-toolchain` plus one commit.** `git log --oneline origin/agent/py32f071-toolchain..HEAD` → a single commit, `ad47c3b`. **[PROVEN]** So there is no third stack to reconcile; the asset-naming work is one cherry-pick.

---

## Version Compatibility

| Component | Compatible with | Notes |
|---|---|---|
| SDK `1.1.1` (`0ed2f4b`) | `arm-none-eabi-gcc` 13.2 – 15.x | All 15 CMake-referenced SDK paths verified present at the pin **[PROVEN]**. Newer GCC may surface new `-Wall -Wextra` warnings in vendored HAL code — no `-Werror`, so warnings only. |
| CMake ≥ 3.20 | `FetchContent_Populate` | `FetchContent_Populate` is **deprecated since CMake 3.30** and warns; prefer `FetchContent_MakeAvailable` or set the `CMP0169` policy. With `-latest` runners drifting toward newer CMake this will start emitting warnings **[PREDICTED]**. |
| Vendored CherryUSB | SDK `1.1.1` only | Unversioned. Cannot be bumped from upstream (no `port/py32` upstream). Track the SDK tag. |
| `pyusb` 1.3.1 | Python 3.9 – 3.13 | `python_requires >=3.9.0` matches this package exactly. Backend (libusb 1.x) is a **system** prerequisite, never a pip dependency. |
| `firestarter` host py3.9 / py3.11 CI | `py32_dfu.py` | Uses `from __future__ import annotations` + `typing.Optional/List/Tuple` with `# noqa: UP006/UP045` — deliberately py3.9-safe. Verified `ruff check` + `ruff format --check` clean and mypy 1/35 **[PROVEN, measured under 3.12 in this container; the 3.9/3.11 legs are the standing devcontainer caveat]**. |
| `DATA_BUFFER_SIZE=512` (py32) | v1.10 CAP-01 `MSG_OK_READY` advertisement | Host adapts automatically. See C-2. |
| Firmware `beta` @ `5c9160a` / app `beta` @ `e7d3ee8` (the v1.22 gitlinks) | the py32 branches | 72 commits of divergence. See the Rebase Hazard Ledger. |

---

## What NOT to Use / Add

| Avoid | Why | Instead |
|---|---|---|
| **Anything that changes the AVR builds' compiled output** | The hard acceptance constraint. Leonardo headroom is ~2992 B, and v1.22 already spent against it (+392 B lock, +152 B observability, +204 B SDP fix — every one *measured*, and the fix contradicted its own prediction). | Keep every py32 change under `platform/py32f071/` and behind `#if defined(RURP_PLATFORM_PY32F071)`. Treat `include/rurp_shield.h`, `include/rurp_serial_utils.h` and `include/avr/pgmspace.h` (H-4/H-5) as the *only* shared-surface edits, and gate each on a measured AVR flash delta plus byte-identical golden traces. |
| **An RTOS (FreeRTOS is right there in the SDK)** | The shared command processor is a `setup()`/`loop()` state machine with strobe-level timing. A scheduler introduces preemption into PROM bus windows and forks the execution model away from AVR — where it can never be validated symmetrically. | Bare-metal, one USB ISR. Explicitly out of scope; the SDK's FreeRTOS is simply not compiled. |
| **Refactoring shared code off the Arduino API** | Tempting, since `include/rurp_register_utils.h` still calls `delayMicroseconds(1)`/`(4)` directly. But that header is byte-identical between `beta` and the py32 branch, and it is the golden-trace surface. Touching it converts an integration milestone into a firmware-refactor milestone with an AVR blast radius. | The 76-line `platform/py32f071/include/Arduino.h` shim already absorbs this at zero AVR cost. Leave it. This is the right architecture for *this* milestone, not a debt to repay now. |
| **Closed-loop DAC VPP / `rurp_calibrate_vpp_two_point()` (PR #45)** | Already settled by operator and not to be reopened: the loop closes on the *calibrated* read, and the calibration half **is** the White-Box Voltage Calibration milestone's Stage-2 divider trim. Three of PR #45's ten commits reach into `rurp_common.cpp`, `rurp_types.h` and `rurp_config_utils.cpp` — `CONFIG_VERSION`-bump and EEPROM-migration territory. And **with no PCB a closed loop cannot be validated at all.** | The **seam only**: `rurp_vpp.h` capability macros, `rurp_vpp_control_mode_t` / `rurp_vpp_result_t`, `RURP_VPP_CONTROL_MANUAL` on every board, `rurp_set_vpp_target_mv()` → `MANUAL_ADJUSTMENT_REQUIRED`. No AVR measurement reroute. **No `CONFIG_VERSION` bump.** |
| **Starting from PR #47 (`feature/py32f071-full-support`)** | 24 files and an all-inclusive CMake list make it read as the most finished branch. Its `src/usb.c` (141 lines) is a ring buffer over `__attribute__((weak))` **no-op** hooks — it links, and a board flashed with it is **silent on USB**. `vpp_target.c` is 13 lines. No SDK fetch. | `agent/py32f071-toolchain` (PR #48), stacked on `agent/portability-macros`, plus `ad47c3b` cherry-picked for the asset name (C-6). |
| **`dfu-util`, `PY32DfuTool`, `puyaisp`, or any external flashing binary** | `dfu-util` reintroduces avrdude's PATH-discovery burden — the exact thing the operator constraint targets, and `avrdude-mcu-detection-fallback` is *still* an open todo. `PY32DfuTool` is Windows-x64-only. `puyaisp` needs a second USB-serial dongle on a board with native USB. | `firestarter/py32_dfu.py` over pyusb now; the self-flash bootloader over CDC + COBS as the primary route later. |
| **`dfu-util`-style hardcoded VID/PID matching** | The Puya bootloader's real USB VID/PID is **[UNVERIFIED]** — UM1504's `0x0448` is a *device* ID, not necessarily the USB PID, and there is no board to check against. | Already correct on the branch: discovery is by **interface class** `0xFE/0x01` with `bInterfaceProtocol == 0x02` for DFU mode, ambiguity refused rather than guessed, runtime interfaces never touched without an explicit `--usb-id`, and a `probe()` command that exists purely to settle this on the first bench session. Do not "simplify" any of that — the branch history records that selecting `interfaces[0]` would have sent `DFU_DETACH` to this devcontainer's webcam. |
| **Shipping USB VID `0x36B7` / PID `0xFFFF`** | A single, undocumented, unattributed occurrence at `usb_cdc.c:20`, with `0xFFFF` as an obvious placeholder PID. Harmless today (the host filters nothing — `serial.tools.list_ports.comports()` is unfiltered and identity comes from a hello handshake **[PROVEN]**), but a USB ID becomes permanent the moment a board ships, and squatting someone else's VID is a real liability. | Record it as an explicit decision this milestone, while the board is paper. The standard hobby route is a `pid.codes` sub-PID under VID `0x1209`. Cheap now, impossible to recall later. |
| **RP2040 / RP2350 and STM32 "Black Pill"** | Explicitly out of scope. Note that `include/rurp_platform_compat.h`'s own comments reference RP2040/RP2350, and `agent/rp2040-portability-macros` shares `agent/portability-macros`' head (`52d6c1f`) — so the portability layer was co-designed with RP2040 in mind. That is fine; do not let it pull RP2040 scope in. | One MCU family per milestone. `rurp_platform.h`'s `#error` on an unknown platform is the right fail-closed shape for a future fourth family. |
| **`ubuntu-latest` + apt `gcc-arm-none-eabi` for a job that publishes a release binary** | Two independent moving targets under a firmware image whose byte-identity this project has historically treated as evidence. | `runs-on: ubuntu-24.04` + `carlosperate/arm-none-eabi-gcc-action@v1` with an explicit `release:`. See §4. |
| **Adding any CherryUSB class beyond CDC (MSC / printer / audio / HID)** | `_Min_Heap_Size = 0x000` + `nosys.specs` means `malloc` returns NULL, and `usb_malloc` is live in exactly those class drivers. The failure is a NULL deref at enumeration, not a link error. | CDC only. Add a comment in `usb_config.h` recording the constraint. (`class/dfu/usbd_dfu.c` **is** in the vendored tree — a genuinely interesting option for the *self-flash* seed later, but it would need the heap question answered first.) |
| **`FLASH_ACR_LATENCY_1` in the clock config** | It is `FLASH_LATENCY_2` (two wait states). The SDK's own CDC reference passes `FLASH_LATENCY_1` (one), which is correct for 48 MHz. Safe but needlessly slow, on a part that must service USB alongside microsecond PROM strobes. | `FLASH_LATENCY_1`. One token. See §1 gotcha 1. |

---

## Alternatives Considered

| Recommended | Alternative | When the alternative would win |
|---|---|---|
| CMake + Ninja, orthogonal to PlatformIO | A PlatformIO custom platform for PY32 | If PY32 ever gets a maintained PlatformIO platform *and* the AVR/ARM builds needed to share one config. Today it would couple the ARM target to `platformio.ini` — the one file that must stay untouched. |
| Puya SDK HAL drivers | The SDK's LL drivers (`py32f071_ll_*.h`, present at the pin) | For the tight PROM bus paths, if HAL overhead ever shows up in timing. Note the port *already* bypasses HAL where it matters — one-snapshot `IDR` read, atomic `BSRR` write. That mixed approach is the right call and should be kept. |
| Vendored CherryUSB from the SDK | Upstream CherryUSB `port/fsdev` | If the PY32 USB IP proves `fsdev`-compatible, this would put the stack back on a maintained upstream. **[PREDICTED, needs silicon. Do not scope here.]** |
| Vendored CherryUSB | TinyUSB | TinyUSB is far more widely deployed, but has **no PY32 port** either, so choosing it means writing a DCD from scratch. CherryUSB wins purely because Puya already did that work. |
| pyusb + libusb (optional extra) | A vendored `libusb` binary wheel per platform | If Windows friction ever becomes the top support cost *and* the self-flash bootloader is still far off. Fragile and unusual for a small project; the bootloader is the better answer to the same problem. |
| `carlosperate/arm-none-eabi-gcc-action@v1` | Docker container with a pinned toolchain image | Stronger reproducibility, materially slower CI, and a second packaging surface. Overkill until the ARM binary is silicon-validated. |
| SDK via `FetchContent` at a pinned SHA | Vendoring the SDK into the repo, or a git submodule | **Vendoring becomes the right answer the moment the ARM image is a published release asset.** A 154 KiB upstream with 4 stars and 7 commits is a single point of failure for the whole release. Worth deciding deliberately this milestone; `FetchContent` at a SHA is the acceptable interim. |

---

## Stack Patterns by Variant

**If the phase touches only `platform/py32f071/**` (new files):**
- No AVR gate needed beyond a smoke `pio run -e leonardo`.
- Acceptance is: CMake configures, builds, and `arm-none-eabi-size` reports a number.

**If the phase touches `include/rurp_shield.h`, `include/rurp_serial_utils.h`, `include/avr/pgmspace.h` or `include/rurp_register_utils.h` (the portability half):**
- Full AVR gate: `pio run` for all three envs, `pio test -e native`, **golden register traces byte-identical**, and a **measured** Leonardo flash delta stated as measured (v1.22 lesson: predictions about flash deltas have been wrong in both directions).
- Plus the cross-repo check the FOURTH CORRECTION mandates: any firmware rename or deletion must be checked against `firestarter_app`'s source-scanning gates (`tools/check_*.py`, `tests/test_sdp_*`, `tests/test_check_*`), which read firmware source *text*. Those gates fail closed and broke four times in Phase 117. Note also the vacuous-path trap: `git diff -- src/flash_utils.h` passes because the real path is `include/flash_utils.h`.

**If the phase touches `firestarter/py32_dfu.py`, `channel.py` or `firmware.py`:**
- `ruff check` + `ruff format --check` + `check_mypy_watermark.py` + `pytest --cov-fail-under=70`, all of which are green on the branch today.
- Assert the **negative**: `dev`-tools/board-gating tests must assert what is *not* called and what is *not* in the argv, not just an exit code (the absent-chip false-green trap, and the `gh --label` argv lesson).

**If the phase touches CI (`py32f071.yml` / `beta-build.yml`):**
- The ARM image must be built in the **same job** as the AVR images, **after** `.github/scripts/update_version.py` rewrites and auto-commits `include/version.h` — otherwise the image carries a stale `VERSION`, and the host's entire update decision is that string compared against the release tag.
- A broken ARM build must **never** block the AVR beta: glob not literal, plus `continue-on-error` on the ARM steps while unproven.
- **Pushing `beta` in either sub-repo auto-fires CI and cuts a new beta.** That is a deliberate release decision, never a side effect of landing this work.

---

## Open questions this research could not close

| Question | Why it is open | How it closes |
|---|---|---|
| Does the Puya factory USB bootloader speak DfuSe or plain DFU 1.1, and what VID/PID does it present? | Requires silicon. UM1504's `0x0448` is a device ID, not necessarily a USB PID. | `firestarter fw --dfu-probe` on the first board. The client already handles both dialects and prints what it finds. |
| Is crystal-less HSI USB enumeration stable on this silicon? | Requires silicon. Puya's own reference does it, and CTC exists as a fallback — neither is proof. | First bring-up. **Mitigate now**: depopulated HSE footprint on the first schematic. |
| Actual flash and RAM figures for the ARM image | No `arm-none-eabi-gcc`/`cmake` in this container (both `command not found` **[PROVEN]**). CI emits `size` to the job log only. | Run the two CMake commands anywhere with the toolchain; then make the number a checked-in baseline with a ceiling. |
| Exact apt `gcc-arm-none-eabi` version on the runner GitHub will actually schedule | `ubuntu-latest` is a moving label; the noble figure `15:13.2.rel1-2` is web-sourced (MEDIUM). | Moot once the toolchain is pinned per §4 — which is the argument for pinning. |
| Whether the portability half changes AVR compiled output at all | Requires a build. `-Os` *should* make macro→`static inline` a no-op. | Measure the Leonardo delta. Do not accept a prediction. |
| The design for CRC-validated dual-slot flash config | **The cited `platform/py32f071/PORTING.md` does not exist** (H-8). | Either author the design in-milestone (real work) or scope the requirement down. Decide before planning. |

---

## Sources

**Primary — read directly (highest confidence in this document):**
- `git -C /workspaces/firestarter_py32_ci` at `feature/py32f071-release-assets` (`ad47c3b`), plus `origin/agent/py32f071-toolchain`, `origin/agent/portability-macros`, `origin/beta` — CMakeLists, README, linker script, `main.cpp`, `usb_cdc.c`, `usb_config.h`, `Arduino.h`, `platform_compat.cpp`, `config.cpp`, `timing.cpp`, `py32f071_rurp_shield.cpp`, `py32f071.yml`, `include/rurp_platform.h`, `include/rurp_platform_compat.h`, `include/avr/pgmspace.h`, `include/rurp_shield.h`, `include/rurp_register_utils.h`, commit counts vs `beta`
- `git -C /workspaces/firestarter_app_py32` at `feature/py32f071-fw-install` (`4ee64a1`) — `firestarter/py32_dfu.py`, `channel.py`, `firmware.py`, `pyproject.toml`, `doc/PY32F071-FIRMWARE-INSTALL.md`, `.github/workflows/ci.yml`, commit `cd7c10c`
- `git ls-remote https://github.com/OpenPuya/PY32F071_Firmware.git` — tag/HEAD identity of the pin
- Sparse clone of `OpenPuya/PY32F071_Firmware` @ `0ed2f4b` — tree layout, per-path existence of all 15 CMake references, `py32f071_hal_flash.h:133-135`, `py32f071xB.h:2449-2453`, `Projects/PY32F071-STK/Applications/USB_Device/USBD_Virtual_COM_Port/Src/main.c`, `Middlewares/Third_Party/CherryUSB/{LICENSE,core,class,common,port}`, `usb_malloc` call-site grep
- Commands run in this container: `pytest tests/test_py32_dfu.py -q` (58 passed, pyusb absent), `ruff check`, `ruff format --check`, `tools/check_mypy_watermark.py` (1/35), `which arm-none-eabi-gcc cmake` (absent)

**Secondary — web (LOW confidence per `classify-confidence --provider websearch|webfetch`):**
- <https://pypi.org/pypi/pyusb/json> — pyusb 1.3.1 / 2025-01-08 / `>=3.9.0` / BSD
- <https://github.com/OpenPuya/PY32F071_Firmware> — BSD-3-Clause, 7 commits, 4 stars *(its "no tags" claim is **contradicted** by `git ls-remote`; the git data wins)*
- <https://github.com/cherry-embedded/CherryUSB> and <https://github.com/cherry-embedded/CherryUSB/tree/master/port> — upstream port list, no `py32`
- <https://cherryusb.readthedocs.io/en/latest/> — upstream docs at ~1.6.1
- <https://github.com/carlosperate/arm-none-eabi-gcc-action> — pinnable releases `4.7-2013-q2`…`15.3.Rel1`, 3 platforms, caching, MD5
- <https://launchpad.net/ubuntu/noble/+package/gcc-arm-none-eabi> and <https://packages.ubuntu.com/gcc-arm-none-eabi> — noble `15:13.2.rel1-2`
- <https://github.blog/changelog/2026-05-14-github-actions-upcoming-image-migrations/> and <https://github.com/actions/runner-images/issues/14226> — `ubuntu-latest` = 24.04, 26.04 available, further migration announced
- <https://github.com/libusb/libusb/wiki/Windows> and <https://github.com/pyusb/pyusb/discussions/499> — WinUSB/Zadig requirement, `NoBackendError` causes

**Planning record (read as required context):** `.planning/PROJECT.md` §"Current Milestone: v1.23", `.planning/STATE.md` §"Milestone Context (v1.23)", `.planning/notes/py32f071-port-branch-state.md`, `.planning/seeds/py32f071-no-external-tool-fw-install.md` — see §Corrections for the six places the tree disagrees with them.

---
*Stack research for: PY32F071 firmware target + host USB-DFU installer, landing onto a mature three-target AVR system*
*Researched: 2026-07-30 — nothing here is a claim about PY32F071 silicon*

# Feature Research

**Domain:** Host-side firmware-install flow for a USB-bootloader MCU target (PY32F071xB, Cortex-M0+) added as a fourth board to a mature EPROM/Flash/SRAM programmer CLI
**Milestone:** v1.23 PY32F071 Integration
**Researched:** 2026-07-30
**Confidence:** MEDIUM overall — HIGH on in-repo state (direct source reads), LOW-to-MEDIUM on ecosystem convention (web sources only), and **structurally unvalidatable on silicon behaviour** (no PY32F071 PCB exists)

---

## 0. Read this first: the claim ceiling and the integration boundary

Two framing facts govern every category below.

**Claim ceiling (from `PROJECT.md` §Current Milestone / `STATE.md` §Milestone Context).** No PY32F071 PCB exists. Permitted claims: the target builds clean, the native + host suites pass, the DFU sequence is exercised against device descriptors and mocks. Forbidden: *"the firmware runs on a PY32F071"* or *"the install works end to end."* Every feature in this document is marked `SILICON-BLOCKED` where its correctness — not its code — depends on hardware nobody has. **§7 enumerates them exhaustively.** A roadmap that writes a success criterion crossing that line is writing a criterion that cannot be met.

**Integration boundary.** This is not a build-it milestone. The host installer is already written, tested and green on `firestarter_app` `feature/py32f071-fw-install` @ `4ee64a1` (worktree `/workspaces/firestarter_app_py32`). **§1 is the inventory of what already exists**, verified by reading that source on 2026-07-30 — not by trusting the branch notes. §2 is what does not exist. Conflating the two is the single biggest scope-inflation risk here, and two of the three "seams" the planning notes say need work (`.hex` extension hardcoding, the flasher strategy) **are already closed on the branch.**

---

## 1. Already implemented on the branch — needs landing, not building

Verified by direct source read of `/workspaces/firestarter_app_py32` @ `4ee64a1` and `/workspaces/firestarter_py32_ci` @ `ad47c3b`, 2026-07-30. Confidence **HIGH** (direct observation of the tree; the `classify-confidence` seam covers fetch providers only and has no tier for a local source read).

| ID | Capability | Evidence | Category |
|----|-----------|----------|----------|
| **E-01** | Pure-Python DFU 1.1 **and** DfuSe client — no external flashing binary | `firestarter/py32_dfu.py` (832 lines) | table stakes |
| **E-02** | Discovery by DFU **interface class** `0xFE`/subclass `0x01`, deliberately *not* by VID/PID | `find_dfu_interfaces()` :408–479 | table stakes |
| **E-03** | More than one DFU-mode device → refuse and list candidates; never coin-flip | `select_interface()` :550–555 | table stakes |
| **E-04** | DFU **runtime** devices are never touched unless named with `--usb-id`; error text names the strap procedure and the doc | `select_interface()` :560–571 | table stakes |
| **E-05** | Geometry read from the device: `wTransferSize`, `bcdDFUVersion`, and the `@…` alt-setting mapping string | `_parse_functional_descriptor()` :386, `parse_dfuse_layout()` :261 | table stakes |
| **E-06** | Erase only the sectors the image actually touches; uniform-grid fallback when no layout is published | `erase_addresses()` :296 | table stakes |
| **E-07** | Flash-envelope refusal (`0x08000000`–`0x08020000`) **before any byte is sent** | `_check_envelope()` :644 | table stakes |
| **E-08** | Intel HEX parser (record types 00/01/02/04/05, checksum-validated) + raw `.bin` loader | `load_image()` :144, `parse_intel_hex()` :171 | table stakes |
| **E-09** | Dual dialect: DfuSe (erase → set-address → blocks from 2) vs plain DFU 1.1 (sequential from 0), with an explicit warning that the plain path surrenders address control | `_download_dfuse()` :740, `_download_plain()` :770 | table stakes |
| **E-10** | Tolerates the device dropping off the bus at leave/manifest — USB errors past that point are not failures | `_finish()` :779–808 | table stakes |
| **E-11** | `fw --dfu-probe` bus diagnostic printing USB ID, dialect, transfer size and sector geometry | `probe()` :588, `cli_handlers.py` :941–954 | **differentiator** |
| **E-12** | Board→method dispatch table; unknown boards default to avrdude so a fourth AVR variant needs no change | `flash_method()` :95, `_BOARD_FLASH_METHODS` :82 | table stakes |
| **E-13** | Portless install — a DFU board in its bootloader exposes no CDC port, and `manage_firmware_update` no longer demands one | `_PORTLESS_FLASH_METHODS` :92, guard :747 | table stakes |
| **E-14** | **Asset resolution accepts `.hex` then `.bin` for DFU boards**, AVR unchanged. The `.hex`-hardcoding the seed and branch-state note flag as outstanding is **closed**: all four call sites go through `_pick_asset()` | `asset_candidates()` :100, `_pick_asset()` :124, used at :224, :321, :358, :419 | table stakes |
| **E-15** | Beta-only channel gate, enforced **twice** (Click choice list at import + service layer), derived from the app's own PEP 440 version, never from an env var | `channel.py` (81 lines), `firmware.py` :604 / :660, `cli_handlers.py` :140–141 | **differentiator** |
| **E-16** | A typed `--board` that disagrees with the attached programmer is **refused**, not silently overridden (found the hard way — it flashed a live Leonardo) | `manage_firmware_update()` :730–742, `board_explicit` via `ctx.get_parameter_source` `cli_handlers.py` :1000 | table stakes |
| **E-17** | When the port lookup fails and a DFU device is on the bus, hint the right invocation — hint only, never raise | `_hint_dfu_board()` :628 | polish |
| **E-18** | `pyusb` is an **optional** `[py32]` extra, so AVR users never pull libusb | `pyproject.toml` :61–66 | table stakes |
| **E-19** | 46 unit tests against a fake USB device that records control transfers, incl. the two safety regressions (unrelated-runtime-device, board conflict) | `tests/test_py32_dfu.py` (654 lines) | table stakes |
| **E-20** | Operator-facing doc: bootloader-entry table, dependency honesty, command reference, first-bench-session script | `doc/PY32F071-FIRMWARE-INSTALL.md` (273 lines) | table stakes |
| **E-21** | Firmware build already emits **both** `firestarter_py32f071.bin` and `firestarter_py32f071.hex` | `platform/py32f071/CMakeLists.txt` :154–161 | table stakes |

**Net:** every table-stakes host-side capability identified in §3's ecosystem survey — with the two exceptions of progress reporting and post-write verification — is already present. The remaining v1.23 work is *publication*, *documentation* and *the rebase*.

---

## 2. Still to build

| ID | Capability | Where it lives | Complexity | Category |
|----|-----------|----------------|------------|----------|
| **N-01** | **Release-asset publication.** Fold the PY32 build into `beta-build.yml` after the version bump, publishing `firestarter_py32f071.hex` as a real release **asset** | firmware repo CI | **LOW** (3 steps + one `files:` glob line, already written out) | table stakes — *the only thing that makes the install reachable at all* |
| **N-02** | Progress reporting during the DFU transfer | `py32_dfu.py` | LOW | differentiator |
| **N-03** | Post-write verification by `DFU_UPLOAD` readback + compare | `py32_dfu.py` | MEDIUM | differentiator (see §5) |
| **N-04** | Reboot-into-bootloader: a Firestarter protocol command + host trigger | **dual-repo** | HIGH | differentiator — **defer** (§4) |
| **N-05** | Self-flash bootloader over CDC + COBS (the seed's *primary* route) | firmware + host | HIGH | future milestone — out of v1.23 scope |
| **N-06** | Record the PCB requirements before the first schematic | `.planning/` | LOW | table stakes (§6) |
| **N-07** | Document the two-route story (primary self-flash / recovery factory DFU) for a hobbyist audience | `doc/` both repos | LOW | table stakes (§6) |
| **N-08** | A default USB VID/PID filter, once observed | `py32_dfu.py` | LOW | `SILICON-BLOCKED` |

**N-01 is the milestone's load-bearing new work.** Today `py32f071.yml` uploads `build/py32f071/firestarter_py32f071.hex` via `actions/upload-artifact@v4` under artifact name `firestarter_py32f071` — an Actions artifact, which is a ZIP on a different API, auth-gated and 90-day-expiring. `_pick_asset()` reads release *assets*. Until N-01 lands, `fw --install --board py32f071` cannot resolve a download URL and the entire E-01…E-21 stack is unreachable. Two constraints, both already documented in `platform/py32f071/README.md` §"Release integration": the build must sit in the **same job as the AVR images** because `beta-build.yml` rewrites and auto-commits `include/version.h` *before* building (an image built elsewhere carries a stale `VERSION`, and the host's whole update decision is that string vs the release tag); and the `files:` entry must be a **glob**, because `softprops/action-gh-release` warns on an unmatched glob but *fails* on a missing literal — a broken ARM build must never block the AVR beta.

---

## 3. Q1 — What comparable tools present, and what is table stakes

Ecosystem survey. Sources and confidence in §9.

| Capability | esptool | dfu-util | probe-rs / cargo-flash | tinyuf2 (UF2) | Katapult + Klipper | **Firestarter AVR path (today)** | Verdict for a hobbyist CLI |
|---|---|---|---|---|---|---|---|
| **Device discovery** | serial port scan | `-l` lists DFU-capable devices; `-d VID:PID`, `-a alt` narrow | target-description database + probe enumeration | none — it *is* a USB mass-storage drive | CAN UUID query (`-q`); USB/UART by device path, checks USB IDs to see if Klipper is running | `find_and_connect` + firmware identity query | **TABLE STAKES** — and *naming what it found* matters more than finding it |
| **Refusing ambiguity** | n/a | `--force` exists to *override* sanity checks | n/a | n/a | multiple unassigned nodes are listed | port identity is verified per port | **TABLE STAKES here specifically**, because DFU runtime interfaces are common on unrelated peripherals |
| **Bootloader entry** | automatic: asserts DTR/RTS (EN←RTS, GPIO0←DTR) | `-e/--detach` — only reaches a device already exposing a DFU **runtime** interface | n/a (SWD, always available) | double-tap RESET, or "reboot to DFU" from the app | software request over CDC (1200-baud DTR pulse), UART magic string, or CAN admin msg; Klipper → Katapult → platform DFU | 1200-baud touch (`avr_tool.py:115 _trigger_reset`), Leonardo only | **TABLE STAKES to *attempt*; POLISH to *automate*** |
| **Actionable failure text** | "hold down the Boot button (or pull down GPIO0) while you start esptool" | terse | diagnostic hints | "tap reset once, wait for purple, tap again" | `-r` then re-run without `-r` | `logger.warning("Failed to trigger reset")` | **TABLE STAKES** — this is the single highest-value item in the survey |
| **Progress reporting** | compressed/uncompressed bytes, address, seconds, effective kbit/s | scaled progress bar (DfuSe progress added in 0.6) | two phase bars: "Erasing sectors", then "Programming pages" | the drive disappears | per-block | **none — avrdude output is swallowed** by `Popen(..., stdout=PIPE, stderr=PIPE)` + `communicate()` (`avr_tool.py:106–113`) | **POLISH for *this* product** (see below) |
| **Verify after write** | **always** — MD5 hash, prints "Hash of data verified.", auto-reflashes the whole file on mismatch | **none** — the manpage has no verification option at all | phase-based; a `--verify` flag was **not confirmed** from the docs fetched | n/a | "verification process" mentioned, unspecified | **yes, invisibly** — `-U flash:w:file:i` with no `-V`, so avrdude verifies by default (`avr_tool.py:143–149`) | **SPLIT in the ecosystem; a parity gap internally** (§5) |
| **Recovery when it goes wrong** | re-enter bootloader manually | strap again | SWD is unconditional | the bootloader is not in the update path | Katapult auto-enters when the app region is empty → an interrupted upload is recoverable, not a brick; plus DFU / stm32flash / SWD | AVR bootloader is preloaded and never overwritten | **TABLE STAKES** — must be *designed in*, not added later |
| **Artifact format** | `.bin` | raw binary (`-s addr`) or `.dfu` | `.elf` | `.uf2` | `.bin` | `.hex` | follows the route, not the project (§6) |

### Two findings that reverse the naive verdicts

**Progress reporting is polish here, not table stakes — because the shipped baseline has none.** All three AVR boards run avrdude with its stdout *and* stderr piped into `communicate()`, so avrdude's own progress bar never reaches the user; only `stderr` on failure is logged. Adding a progress bar to the py32 path would make the **unproven** path the only one with live feedback. That is not wrong, but it is a UX-parity project, not a gap in the new feature. Categorise it as a differentiator and let it lose to N-01 if anything has to be cut.

**Post-write verification is the reverse.** The ecosystem is genuinely split (esptool always verifies; dfu-util never does), so an ecosystem-only reading would call it polish. But internally, avrdude verifies by default on all three AVR boards, and the DFU path has *no* verification: `DFU_UPLOAD = 2` is defined at `py32_dfu.py:53` and **never used**. So v1.23 as it stands would ship the project's first firmware-install path that writes flash without reading it back — on the one target whose bootloader dialect and sector geometry are unconfirmed. That asymmetry is the strongest argument in this document for building N-03. See §5 for the recommendation and its claim ceiling.

---

## 4. Q2 — Bootloader entry UX

### The two findings that settle this

**F-1 — `Py32DfuFlasher`'s `DFU_DETACH` branch can never fire against Firestarter's own py32 firmware.** The PY32 USB configuration is CDC-ACM **only**: `FIRESTARTER_USB_CONFIG_SIZE (9U + CDC_ACM_DESCRIPTOR_LEN)` (`platform/py32f071/src/usb_cdc.c:27`) and exactly two interfaces added, both CDC (`:205–206`). A `grep -rn 'DFU\|dfu' platform/py32f071/` over `.c`/`.h`/`.txt` returns **zero hits**. `DFU_DETACH` is addressed to a DFU *runtime* interface (protocol `0x01`), which the application does not publish. The detach path at `py32_dfu.py:560–586` is therefore reachable only for a third-party device the operator explicitly names with `--usb-id` — it is **not a bootloader-entry route for this product**, and the doc's §2b framing of "the DFU-class equivalent is `DFU_DETACH`, which `select_interface()` already sends" is true of the code and misleading about the product. Confidence **HIGH** (direct source read).

**F-2 — no reboot-to-bootloader capability exists at any layer.** `include/firestarter.h` defines command IDs 0–8 and 11–15; 9, 10 and ≥16 are free. `grep -rn 'bootloader\|BOOTLOADER\|NVIC_SystemReset\|reboot'` across `src/`, `include/` and `platform/py32f071/` returns **zero hits**. Bootloader entry today is strap-only. Confidence **HIGH** (direct source read).

### Options for software-triggered entry on a Cortex-M0+

| Route | Mechanism | Cost to the user | Cost to build | Verdict |
|---|---|---|---|---|
| **BOOT0 strap + power-cycle** | `nBOOT1 = 1` + `BOOT0` high selects system memory (Puya UM1503/UM1504) | A jumper/button/pad press and a replug, **every update** | zero (already the documented path, E-04's error text) | **The v1.23 answer.** Available first, and the PCB must make it possible regardless because it is also the recovery route |
| **`DFU_DETACH` on a runtime interface** | Add a DFU runtime interface to the CDC composite descriptor so the app is `CDC + DFU-runtime`; host sends `DETACH`; device re-enumerates as the factory bootloader | none once it works | MEDIUM — new descriptor, new interface, and it still needs a mechanism to actually *reach* system memory (it does not remove the need for the jump below); grows the USB config on a 128 KiB part | **Not worth it.** It buys standards-compliance the project does not need and does not solve the hard half |
| **A Firestarter-native command (new `CMD_*`) that jumps** | Host sends a normal COBS/JSON command; firmware disables interrupts + SysTick, remaps system memory to `0x00000000` via `SYSCFG` `MEM_MODE`, loads SP from `[0x00000000]`, branches to `[0x00000004]` | none once it works | HIGH — see the tail below | **The right long-term shape. Defer out of v1.23** |
| **`puyaisp` / UART ISP** | Factory UART bootloader on PA2/PA3 (or PA9/PA10, PA14/PA15), BOOT0 high, nRST pulsed | A second USB-serial dongle plus test-point access, on a board that has native USB | MEDIUM | **Anti-feature** (A-08) — a UX regression from today's single cable |

**Why the native-command route is HIGH complexity and not "just a command".** Cortex-M0/M0+ has **no VTOR**, so the documented pattern is the `SYSCFG` `MEM_MODE` remap (STM32F0 uses `SYSCFG->CFGR1`, not `MEMRMP` as on F4). PY32F0 has the same `MEM_MODE` field per the PY32F002A reference manual's SYSCFG chapter, so the mechanism plausibly exists on PY32F071 — but community reports say the remap "has no effect" on some STM32F0 parts, and STM32F0/L0 carry an empty-check mechanism that can defeat an application-initiated jump. **This is unconfirmed for PY32F071 and unvalidatable without silicon** (confidence **LOW**). On top of that, adding a command ID is a dual-repo change with a gate tail: `constants.py` ↔ `firestarter.h` parity, `check_dispatch.py`, the dispatch-mirror guard, and the nine cross-repo source-scanning gates that the v1.22 FOURTH/FIFTH CORRECTIONs record breaking **four times** on firmware renames. Building a jump nobody can test, behind that tail, inside an integration milestone, is exactly the kind of unvalidatable claim the milestone forbids.

### What a good CLI does when it cannot enter the bootloader

The ecosystem answer is unanimous and cheap: **say precisely what to do by hand, and split the request from the transfer.**

- esptool: "hold down the Boot button (or pull down GPIO0) while you start esptool and keep it down during reset."
- tinyuf2: "tap reset once, wait for the LED to turn purple, and tap again before the purple goes away."
- Katapult: `flashtool.py -r` requests the bootloader and **exits**; the operator re-runs without `-r` to upload. USB-to-CAN-bridge and UART devices cannot be auto-detected, so the two-step is the documented normal path, not a fallback.
- Klipper defines an explicit priority ladder: reboot into Katapult if installed, **else** fall into a platform-specific bootloader such as STM32 DFU.

**The branch already does the esptool-shaped thing** — `DfuDeviceNotFoundError` at `py32_dfu.py:539–544` and `:562–571` names the strap (`BOOT0` high, `nBOOT1 = 1`), the power-cycle, and the doc, and explicitly declines to touch the runtime devices it found. That is the table stake, and it is met.

**One safety item to carry forward.** Klipper documents a real hazard of platform DFU: on some boards, entering DFU mode "can cause undesired actions (such as powering the heater while in DFU mode)," and it tells users to disconnect loads first. The Firestarter analogue is direct and stronger: a PY32 in the Puya factory bootloader has its GPIOs in reset state, PR #48's pin map is an explicitly provisional placeholder that "must not be trusted near a PROM," and the operator already runs a standing *chip OUT before sideload* rule for Uno-class boards. **"Socket empty before any py32 firmware install"** belongs in N-07's documentation as a table stake, and it costs nothing.

---

## 5. Verify-after-write — the recommendation

Build N-03, categorise it as a **differentiator**, and gate the claim.

- **Why build it:** it closes the only functional regression v1.23 introduces relative to the AVR paths (avrdude verifies by default; DFU does not), the constant is already reserved (`DFU_UPLOAD = 2`), the state machine and dialect fork it needs already exist (E-09), and it is fully exercisable against the existing fake-USB harness (E-19) — 46 tests already record control transfers, so a readback assertion is an incremental case, not new infrastructure.
- **Why not table stakes:** dfu-util, the closest tool, has no verify option at all; and this milestone cannot demonstrate that a readback would ever catch anything.
- **Claim ceiling:** permitted — *"the client issues `DFU_UPLOAD` for the written range and compares, asserted against a mock device."* Forbidden — *"writes are verified on the PY32F071"*, or any implication that verification has ever run against silicon. A `DFU_UPLOAD` implementation is also itself `SILICON-BLOCKED`: whether the Puya bootloader supports upload at all is unknown (the DFU functional descriptor's `bmAttributes` advertises `bitCanUpload`, and `attributes` is already captured at `py32_dfu.py:348` but never consulted — reading it and skipping readback when the device says it cannot upload is the correct fail-soft, and is mock-testable).
- **The stronger verification is cheaper and belongs in the doc, not the code:** power-cycle with `BOOT0` low, then `firestarter fw` and confirm the identity reads back `py32f071`. `doc/PY32F071-FIRMWARE-INSTALL.md` §5 step 3 already prescribes exactly this. Automating it (post-install re-enumerate and identity check) is a differentiator and `SILICON-BLOCKED`.

---

## 6. Q3 and Q4 — the two-route story, and release artifacts

### Q3 — How comparable projects structure "primary self-flash + factory-bootloader recovery"

**Katapult (formerly CanBoot) + Klipper is the closest published precedent**, and it validates the seed's decision almost point for point:

| Seed decision | Katapult's equivalent | Implication for v1.23 |
|---|---|---|
| Small bootloader in the first few KB, speaking the transport the app already uses | Katapult flashes over CAN, USB **and** serial — the channel the host already owns | The design is proven in the wild; the seed is not inventing a shape |
| Bootloader **never self-updates** | Katapult *does* offer a "Deployer" to replace the bootloader without an external programmer | **The one part not to copy.** The seed's no-self-update rule is the stronger reliability position; keep it (A-11) |
| Image CRC-verified before the jump; failed CRC stays in the bootloader | Katapult **auto-enters the bootloader when the application flash region is empty** | Same property, reached differently. Either mechanism makes an interrupted transfer *recoverable*, not a brick — this is the load-bearing reliability feature of the whole design |
| Factory bootloader stays as maintainer/manufacturing recovery | Klipper's ladder: Katapult if installed, **else** platform DFU; documented recovery also lists stm32flash (UART) and SWD | Confirms a **three**-tier ladder is normal: self-flash → factory bootloader → SWD. The seed's PCB requirements already reserve all three |
| Host sends the image over the port it already owns | `flashtool.py` flashes `.bin` | Confirms Q4's format finding below |

**User-facing features this two-route story implies** (all deferred past v1.23 except the documentation):

- One command for the normal case, with **no strap step** — the entire point of the self-flash route.
- An explicit *request-the-bootloader* operation, separable from the upload (Katapult's `-r`). The two-step is the documented normal path for devices that cannot be auto-detected, not an error path.
- A route ladder the user can see: which route was taken, and what the next one down is when it fails.
- Recovery that does not require the CLI at all (strap + factory DFU; then SWD).

**Documentation a hobbyist needs** — five items, none of which needs silicon:

1. **One happy path, one command.** Not three routes presented as equals; the primary route, then a clearly-labelled "if that fails" section.
2. **A route table** with, per route: what it needs (cable / jumper / dongle / probe), who it is for (user / maintainer / factory), and what it costs. `doc/PY32F071-FIRMWARE-INSTALL.md` §2 already has this shape and needs only re-ordering once the self-flash route exists.
3. **The recovery ladder, stated as a promise.** "An interrupted update leaves the board in the bootloader" is the sentence that makes a hobbyist willing to press enter.
4. **Honest dependency accounting.** The doc already does this well: pyusb + libusb + a WinUSB driver on Windows, named as "the one place the 'no external tools' goal is imperfect."
5. **The safety line: socket empty before a firmware install** (§4).

### Q4 — Release-artifact expectations

**Ecosystem finding: there is no cross-project naming standard, and the *format* follows the flashing route, not the project.** QMK builds `.hex` (AVR), `.bin` and `.uf2` (RP2040), one asset per keyboard; Klipper/Marlin produce `.bin` and `.hex`; Katapult flashes `.bin`; tinyuf2 consumes `.uf2`; dfu-util consumes a raw binary with `-s <addr>` or a `.dfu` container. The only stable convention is *one asset per target with the target name in the filename* — which `firestarter_{board}.{ext}` already satisfies. Confidence **LOW** (websearch only, no single authoritative source).

**Verdict: supporting both is NOT table stakes for the DFU route, and it is already done anyway.**

- **`.hex` as the published asset — TABLE STAKES, and correct.** Intel HEX carries its own load address, which `load_image()` reads and `_check_envelope()` then validates. A raw `.bin` can only be *assumed* to start at `FLASH_BASE`. On a target whose bootloader dialect is unconfirmed — and where the plain-DFU-1.1 path explicitly warns that "the load address is then decided by the bootloader, not by us" — the self-describing format is the safer one. Keeping the AVR convention also means zero new host logic.
- **`.bin` *acceptance* — already implemented at zero cost (E-14), keep it.** It is what a local CMake build produces (E-21), so a developer can flash an unreleased image without converting it.
- **`.bin` as a *published* asset — defer.** It becomes table stakes when the self-flash bootloader lands, because that protocol most likely wants raw binary. Nothing in v1.23 needs it. **This closes the seed's open question** *"Does the host asset pattern need `.bin` alongside `.hex`?"* — the host **already accepts both**; only the publication side is a choice, and the answer for v1.23 is `.hex` only.
- **The extension is no longer baked into the pattern.** The seed and the branch-state note both flag `firmware.py:155`/`:237`/`:336` as hardcoding `.hex`. On the branch those are `asset_candidates()` / `_pick_asset()` and all four call sites use them. Download naming also round-trips correctly: `_download_firmware_file()` takes the filename from the URL's last path segment (`firmware.py:448–452`), so a `.bin` asset lands as `.bin` and `load_image()` dispatches on the real extension. **No work needed here; do not re-plan it.**

---

## 7. `SILICON-BLOCKED` — every feature whose validation needs a board that does not exist

This is the quality-gate table. **Permitted claim ceiling everywhere below: builds clean, suites pass, DFU sequence exercised against descriptors and mocks. Never "works on a PY32F071".**

| ID | What cannot be validated | Why it matters |
|----|--------------------------|----------------|
| E-02 | The USB VID/PID the Puya bootloader presents. `0x0448` appears in UM1504's bootloader-parameter table as a **device ID** and is elsewhere associated with PY32F003 memory configurations — **not** confirmed as a USB PID | Discovery is class-based *because* of this. Hardcoding `0x0448` would fail closed against the real device (A-07) |
| E-05, E-09 | **Which dialect the bootloader speaks** — DfuSe (`bcdDFUVersion 0x011A`) or plain DFU 1.1. No evidence was found that dfu-util has ever been demonstrated against a PY32 part; Puya's documented tools are `PY32DfuTool` (Windows) and `PY32IspTool` | The entire `is_dfuse` fork is untested against reality. One of the two branches has never been the right one |
| E-05, E-06 | Sector geometry. The fallback is a uniform 2048 B grid (`DEFAULT_ERASE_PAGE_SIZE`) nobody has confirmed | Wrong erase granularity on a real part = a partially-erased image |
| E-07 | `FLASH_BASE 0x08000000` / 128 KiB envelope — from the datasheet and the linker script, never observed | The guard's *bounds* are inherited, not measured |
| E-09 | Whether a plain-DFU-1.1 device would place the image at the right address. The code's own warning admits it cannot know | A silent wrong-address write is the worst failure mode in the set |
| E-10 | Whether leave/manifest actually starts the application | "Success" today means "the transfer completed", nothing more |
| E-11 | `--dfu-probe` output against a real bootloader — this is the *instrument for settling the above*, and it too is unrun | First bench session, first command |
| E-13, E-17 | That a py32 in bootloader mode really presents no CDC port, and that `dfu_device_present()` fires for it | Both are reasoned from the spec |
| N-03 | Whether the Puya bootloader supports `DFU_UPLOAD` at all (`bitCanUpload` in `bmAttributes`) | Argues for a fail-soft that skips readback when the device says it cannot upload |
| N-04 | Whether a `SYSCFG` `MEM_MODE` remap + branch reaches system memory on PY32F071. Documented for STM32F0/PY32F0 in general; reported to "have no effect" on some F0 parts; F0/L0 empty-check can defeat it | The reason to **defer** N-04, not merely to descope it |
| **all** | **End-to-end install.** Never claim it | |

**Also unvalidatable but non-obvious:** PR #48's pin map (PB0–PB7 data, PA0–PA5 control, VPP on PA4/ADC ch4) is a provisional placeholder that exists so the target compiles. A successful firmware install proves nothing about the programmer working. Keep those two claims strictly separate in every requirement.

---

## Feature Landscape

### Table Stakes (users expect these)

| Feature | Why expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **N-01** Published release asset `firestarter_py32f071.hex` | Without it there is no install path at all — every other feature is unreachable | **LOW** | Firmware-repo CI. Must build in `beta-build.yml`'s job (post-version-bump) and use a **glob** in `files:`. Fully specified in `platform/py32f071/README.md` |
| **E-01/E-12** One command, one flow: `fw --install --board py32f071` | Parity with the three AVR boards; the CLI already owns firmware install | done | `flash_method()` dispatch; `manage_firmware_update` needed no change |
| **E-02/E-03/E-04** Discovery that names what it found and refuses ambiguity | DFU runtime interfaces exist on unrelated peripherals (a webcam in this devcontainer advertises one) | done | Class-based, not VID/PID. Two real safety bugs were fixed here |
| **E-04** Actionable manual-entry instructions when the bootloader is not found | Highest-value item in the ecosystem survey (esptool, tinyuf2, Katapult all do it) | done | Error text names `BOOT0` high + `nBOOT1 = 1` + power-cycle, and points at the doc |
| **E-07** Refuse an impossible image before sending a byte | It is the only pre-flight safety on an unproven target | done | Deliberately **not** overridable (contrast dfu-util `:force`) |
| **E-10** Tolerate the device leaving the bus | Every bootloader-based flow re-enumerates; already true of the Leonardo path | done | USB errors after leave are logged at debug, not raised |
| **E-13** No serial port demanded for a portless board | A board in DFU mode has no CDC port; demanding one is an unfixable error | done | `_PORTLESS_FLASH_METHODS` |
| **E-14** Asset resolution not hardcoded to one extension | Needed the moment a second flashing route exists | done | **Already closed** — do not re-plan |
| **E-16** A typed `--board` that conflicts with the attached programmer is refused | Silently retargeting an install is a hardware-damage path; it flashed a live Leonardo during development | done | `board_explicit` via `ctx.get_parameter_source` |
| **E-18** `pyusb` optional, not a hard dependency | AVR users must not pay for a route they never take | done | `[py32]` extra |
| **N-06** PCB requirements recorded before the first schematic | BOOT0/nBOOT1 strapping, SWD pads, contiguous 8-bit port, flash budget — cheap now, expensive after layout | **LOW** | The seed's stated trigger. **The recovery ladder only exists if the PCB allows it** |
| **N-07** Two-route documentation + the socket-empty safety line | A hobbyist will not press enter without a stated recovery promise | **LOW** | Builds on E-20; five items enumerated in §6 |

### Differentiators (competitive advantage)

| Feature | Value proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **E-01** No external flashing binary | The seed's whole motivation. `PY32DfuTool` is Windows-x64-only; `dfu-util` reintroduces avrdude's PATH-discovery burden. A pure-Python client is strictly better than both | done | Residual cost is honestly documented: pyusb + libusb, WinUSB via Zadig on Windows |
| **E-11** `fw --dfu-probe` | No comparable tool ships a *bus-truth reporter* aimed at settling its own unknowns. It converts two open questions (USB ID, dialect) into one command on first silicon | done | `SILICON-BLOCKED` by construction — that is its purpose |
| **E-15** Beta-only channel gate, double-enforced, never env-var-driven | Ships an unproven flash path to people who opted into unproven software, and to nobody else. Graduates by deleting one tuple entry | done | Depends on the existing prerelease predicate (D-23). Do not weaken |
| **E-09** Runtime dialect adaptation instead of a hardcoded assumption | Turns "we don't know which dialect" from a blocker into a runtime branch | done | Both branches unvalidated (§7) |
| **N-03** `DFU_UPLOAD` readback verification | Closes the only functional regression vs the AVR paths (avrdude verifies by default; DFU does not). Cheap: constant reserved, harness exists | **MEDIUM** | §5. Must fail soft on `bitCanUpload = 0`. Claim ceiling: "asserted against a mock" |
| **N-02** Progress reporting | Would be the *first* live progress in the product — avrdude's is swallowed today | **LOW** | Parity project, not a gap. First thing to cut |
| **N-04** Reboot-into-bootloader command | Removes the strap step from every routine update; matches the Leonardo 1200-baud-touch shape the host already tolerates | **HIGH** | **Defer.** Mechanism unconfirmed on PY32 (no VTOR; `SYSCFG MEM_MODE`), plus a dual-repo gate tail |
| Post-install identity check (re-enumerate, expect `py32f071`) | The only verification that proves the *application* runs, not just that bytes moved | MEDIUM | `SILICON-BLOCKED`. Keep it in the doc (§5) for now |

### Anti-Features (commonly requested, often problematic)

| Feature | Why requested | Why problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **A-01** Bundle / auto-download `dfu-util` or `PY32DfuTool` | "Use the standard tool" | `PY32DfuTool` is **Windows x64 only**; `dfu-util` is an external binary with exactly the PATH-discovery burden the operator constraint targets. Also: no evidence dfu-util has ever driven a PY32 | E-01, already built |
| **A-02** A `--install-driver` / Zadig helper | Windows users will hit the WinUSB wall | Elevated privileges and writes to the user's driver store, on a path nobody has run on silicon | Document it (E-20 does), and let **N-05** remove the need |
| **A-03** Make `pyusb` a hard dependency | Simplifies packaging | Forces libusb on every AVR user for a board that does not exist | E-18, already done |
| **A-04** Auto-detect a py32 and install without `--board` | "It knows a DFU device is there" | Would target any DFU device on the bus. `dfu_device_present()` deliberately counts only DFU-**mode** devices and only *hints* | Keep it a hint (E-17); require `--board` |
| **A-05** Ship the py32 install path on stable | "It's finished and tested" | Offers users a flash operation nobody has ever completed | E-15; graduate by bench validation only |
| **A-06** A `--force` that overrides the flash-envelope check | dfu-util has `:force`; symmetry | On an unproven target the sanity check *is* the safety. A forced out-of-envelope write is the one irreversible outcome | Fix the image or the geometry; never the guard |
| **A-07** Default `--usb-id` to `0448` | UM1504 lists it | It is a **device ID in a bootloader-parameter table**, not a confirmed USB PID (and is elsewhere tied to PY32F003 configs). A wrong default filter makes discovery fail to find the real board | Class-based discovery (E-02); add a default only after `--dfu-probe` observes one |
| **A-08** Implement the `puyaisp` UART-ISP route as a third path | Needs only `pyserial` | Requires a second USB-serial dongle plus test-point access on a board with **native USB** — a regression from one cable | Rejected in the seed. Factory USB DFU is the recovery route |
| **A-09** A `.uf2` / drag-and-drop route | Objectively the best hobbyist UX in the survey (tinyuf2: zero host tooling) | No tinyuf2 PY32 port; needs MSC + a filesystem in the bootloader; hostile inside 128 KiB total flash shared with the application and the dual-slot config region | **N-05** — a self-flash bootloader reusing the CDC + COBS framing the firmware already has |
| **A-10** Surface closed-loop DAC VPP as a user feature | PR #45 exists | Locked OUT by operator decision (seam only); and a closed loop **cannot be validated at all** without a PCB | `RURP_VPP_CONTROL_MANUAL` + `MANUAL_ADJUSTMENT_REQUIRED` |
| **A-11** Let the bootloader self-update (Katapult's "Deployer") | Katapult ships it; avoids a programmer for bootloader upgrades | Puts the bootloader **in its own update path** — the one component whose failure is unrecoverable without SWD. The seed explicitly forbids it | Bootloader written once at manufacture; SWD for the rare replacement |
| **A-12** Interactive "put the board in DFU mode now, press enter" / poll-until-it-appears | Feels friendlier than an error | Enumeration timing on this part is unknown; a blocking poll on an unproven bus yields a hang instead of a diagnosable error | Katapult's two-step: `--dfu-probe`, then `--install`. Already the shape |
| **A-13** Claim the install works because the suites pass | 46 tests are green; CI is green | The mock cannot be wrong in the way the real device can. This is the milestone's central honesty risk | §7's table, verbatim, in the requirements |

---

## Feature Dependencies

```
N-01 published release asset  ───required-by──> EVERY user-visible py32 install
  │  └──requires──> beta-build.yml version-bump-then-build ordering (firmware CI)
  │  └──requires──> E-14 asset_candidates / _pick_asset            [DONE]
  │  └──requires──> glob (not literal) in action-gh-release `files:`
  │
E-12 flash_method dispatch
  └──enables──> E-01 DFU client ──requires──> E-18 pyusb [py32] extra
                   ├──requires──> E-02 class-based discovery
                   │                 └──requires──> E-03 + E-04 ambiguity refusal   [SAFETY]
                   ├──requires──> E-05 descriptor-derived geometry
                   │                 └──enables──> E-06 touched-sectors-only erase
                   ├──requires──> E-08 image loader (.hex | .bin)
                   │                 └──enables──> E-07 flash-envelope guard        [SAFETY]
                   └──enables──> E-09 dialect fork ──enables──> N-03 readback verify
                                                   └──requires──> E-10 leave/reset tolerance

E-13 portless install ──requires──> manage_firmware_update port resolution
E-15 channel gate    ──requires──> is_prerelease_build (D-23 predicate, pre-existing)
E-16 board conflict  ──requires──> Click get_parameter_source
E-11 --dfu-probe     ──enhances──> E-02, E-05, E-09  (it is how their unknowns get settled)

N-04 reboot-to-bootloader
  └──requires──> a free CMD id + COBS/JSON dispatch
  └──requires──> constants.py <-> firestarter.h parity + check_dispatch.py
                 + dispatch-mirror guard + 9 cross-repo source-scanning gates
  └──requires──> SYSCFG MEM_MODE jump proven on PY32F071        [SILICON-BLOCKED]
  └──obsoleted-by──> N-05

N-05 self-flash bootloader (seed's PRIMARY route)
  └──requires──> N-06 PCB flash-budget reservation + BOOT0 strap + SWD pads
  └──requires──> the CDC + COBS transport proven on silicon
  └──would-make-table-stakes──> a published .bin release asset
  └──removes──> A-02 (WinUSB), the BOOT0 strap, and E-18's pyusb cost

N-07 documentation ──requires──> E-20 (existing doc) + N-06 (the PCB decisions to document)
```

### Dependency notes

- **N-01 gates the milestone's user-visible value.** It is LOW complexity and lives in the *firmware* repo's CI, not the host. A roadmap that treats the host branch as "the py32 install feature" will ship a feature nobody can invoke.
- **N-05 obsoletes N-04.** A self-flash bootloader speaking CDC + COBS makes a jump-to-system-memory command unnecessary for the normal path. Building N-04 first spends HIGH complexity on something the primary route retires. Sequence N-06 → N-05, and let N-04 exist only if the factory-DFU recovery path needs software entry.
- **N-06 is a hard prerequisite of N-05 and of the whole recovery ladder.** Flash-budget reservation (bootloader + application + dual-slot CRC config inside 128 KiB), BOOT0/nBOOT1 strapping, SWD pads, contiguous 8-bit port. The seed's trigger is *"the first schematic"* precisely because these are unrecoverable after layout.
- **E-14 is done — do not re-plan it.** Both the seed's open question and the branch-state note's seam #2 list `.hex` extension hardcoding at `firmware.py:155`/`:237`/`:336` as outstanding. It is closed on the branch.
- **Cross-repo gate hazard, from v1.22's record.** `firestarter_app` carries source-scanning gates over *firmware* source text; firmware renames broke four of them in Phase 117 and four more in Phase 118, and the firmware suite stayed green each time. Any v1.23 phase touching firmware identifiers (notably N-04, or the portability-macros rebase) must own an explicit task re-running `tools/check_*.py` and `tests/test_check_*` in the app repo. **The nine cross-repo gates plus golden register traces plus `check_dispatch.py` are the hard acceptance constraint.**
- **E-15 must not be weakened to make anything demonstrable.** The stable-channel refusal is the mechanism that makes shipping an unvalidated flash path defensible at all.

---

## MVP Definition

### Launch with (v1.23)

- [ ] **Land E-01 … E-21 onto `beta`** — the rebase of two branch stacks (72 commits behind), not a fast-forward. This is the milestone's bulk effort and it produces **no new features**.
- [ ] **N-01 published release asset `firestarter_py32f071.hex`** — the only thing that makes any of E-01…E-21 reachable. LOW complexity, firmware-repo CI, glob not literal, in `beta-build.yml`'s post-version-bump job.
- [ ] **N-06 PCB requirements recorded** — BOOT0/nBOOT1 strapping, SWD pads, contiguous 8-bit port, flash budget. The seed's trigger condition is met the moment a schematic is specified.
- [ ] **N-07 two-route documentation** — self-flash as intended primary, factory DFU as maintainer/manufacturing recovery, SWD as last resort; plus the socket-empty safety line. Re-orders E-20 rather than replacing it.
- [ ] **The `SILICON-BLOCKED` table (§7) reproduced in the requirements** — nine claim classes, each pairing a permitted wording with an explicit non-claim. This is what v1.22's `122-LEDGER.md` did, and it is why that milestone's claims held.
- [ ] **E-15 verified intact** — `fw --help` on a stable build must not list `py32f071`, and `probe_dfu`/`_install_with_dfu` must refuse for library callers.

### Add after validation (first silicon)

- [ ] **N-08 default USB VID/PID** — trigger: `--dfu-probe` reports one.
- [ ] **N-03 readback verification** — buildable now as a differentiator (§5); *validatable* only here. Trigger for the claim, not for the code.
- [ ] **N-02 progress reporting** — trigger: someone waits through a real transfer and finds the silence unpleasant. Consider fixing the AVR path's swallowed avrdude output in the same pass, so the three shipped boards are not left behind.
- [ ] **Post-install identity check** — trigger: a real leave/reset has been observed to start the application.
- [ ] **Graduate `py32f071` out of `BETA_ONLY_BOARDS`** — trigger: bench validation. One tuple, one line.

### Future consideration (the seed's own milestone)

- [ ] **N-05 self-flash bootloader over CDC + COBS** — why defer: needs the USB stack proven on silicon first, and it is the largest single piece of work in the whole py32 story. Why it still wins: it is the only route with zero host-side USB plumbing, and it removes both the WinUSB friction and the BOOT0 strap.
- [ ] **N-04 reboot-into-bootloader command** — why defer: mechanism unconfirmed on PY32 (no VTOR; `SYSCFG MEM_MODE` reported unreliable on sibling parts), dual-repo gate tail, and **N-05 obsoletes it for the normal path**.
- [ ] **Published `.bin` release asset** — trigger: N-05 lands and wants raw binary. Host-side acceptance already exists.

---

## Feature Prioritization Matrix

| Feature | User value | Implementation cost | Priority |
|---------|-----------|---------------------|----------|
| **N-01** published release asset | HIGH (gates everything) | LOW | **P1** |
| Land E-01…E-21 onto `beta` (the rebase) | HIGH | HIGH (72 commits, 9 gates) | **P1** |
| **§7** claim-ceiling ledger in requirements | HIGH (the milestone's integrity) | LOW | **P1** |
| **N-06** PCB requirements | HIGH (unrecoverable if missed) | LOW | **P1** |
| **N-07** two-route docs + socket-empty line | MEDIUM–HIGH | LOW | **P1** |
| **E-15** channel gate verified intact | HIGH (ships-unproven-safely) | LOW (verification only) | **P1** |
| **N-03** readback verification | MEDIUM (parity with avrdude) | MEDIUM | **P2** |
| **N-08** default VID/PID | LOW until observed | LOW | **P2** (silicon-gated) |
| **N-02** progress reporting | LOW (no shipped path has it) | LOW | **P3** |
| Post-install identity check | HIGH once validatable | MEDIUM | **P3** (silicon-gated) |
| **N-04** reboot-to-bootloader | MEDIUM (removes the strap) | HIGH | **P3** (obsoleted by N-05) |
| **N-05** self-flash bootloader | HIGH (the seed's primary route) | HIGH | **P3** (own milestone) |

---

## Competitor Feature Analysis

| Feature | esptool | dfu-util | Katapult / Klipper | tinyuf2 | **Firestarter v1.23** |
|---------|---------|----------|--------------------|---------|------------------------|
| External binary needed | it *is* the binary (pip-installable) | yes — a C binary on PATH | no (Python) | none at all | **no** — in-process Python (E-01) |
| Bootloader entry | automatic (DTR/RTS) | `-e` detach only, needs a runtime interface | software request over CDC/UART/CAN; ladder to platform DFU | double-tap RESET | **strap-only** in v1.23; ladder documented, N-04/N-05 deferred |
| Discovery ambiguity | n/a | `-d`, and `--force` to override | lists unassigned nodes | n/a | **refuses and lists** (E-03/E-04) |
| Progress | detailed | progress bar | per-block | drive disappears | **none** (N-02 deferred) — matches the shipped AVR baseline |
| Verify after write | **always** (MD5, auto-reflash) | **never** | unspecified | n/a | **none** on DFU; avrdude verifies invisibly on AVR. N-03 = P2 |
| Recovery design | manual re-entry | strap | auto-enter when app region empty; DFU / UART / SWD | bootloader out of the update path | **strap + factory DFU + SWD, reserved on the PCB** (N-06) |
| Artifact | `.bin` | raw bin / `.dfu` | `.bin` | `.uf2` | **`.hex` published, `.bin` accepted** (E-14/E-21) |
| Unproven-target gating | n/a | n/a | n/a | n/a | **beta-only channel gate** (E-15) — nothing in the survey does this |

Two capabilities in the v1.23 column have no analogue in the survey: **E-11 `--dfu-probe`** (a tool whose job is to settle its own unknowns) and **E-15 the channel gate**. Both exist because this feature is shipping ahead of its silicon, which none of the comparators had to do. They are the honest differentiators.

---

## Sources

Confidence tiers obtained from `gsd-tools query classify-confidence`. Digests cached via `research-store put`.

**Direct source reads — highest evidentiary value, no fetch provider involved** (the `classify-confidence` seam covers fetch providers only; these are first-hand observations of the trees named, 2026-07-30):

- `/workspaces/firestarter_app_py32` @ `4ee64a1` — `firestarter/py32_dfu.py`, `firmware.py`, `channel.py`, `cli_handlers.py`, `avr_tool.py`, `pyproject.toml`, `tests/test_py32_dfu.py`, `doc/PY32F071-FIRMWARE-INSTALL.md`
- `/workspaces/firestarter_py32_ci` @ `ad47c3b` — `platform/py32f071/{CMakeLists.txt,README.md,src/usb_cdc.c}`, `include/firestarter.h`, `.github/workflows/py32f071.yml`
- `.planning/PROJECT.md` §Current Milestone v1.23; `.planning/STATE.md` §Milestone Context (v1.23); `.planning/seeds/py32f071-no-external-tool-fw-install.md`; `.planning/notes/py32f071-port-branch-state.md`

**Fetched sources:**

| Source | Provider | Confidence | Used for |
|---|---|---|---|
| [dfu-util(1), Debian testing](https://manpages.debian.org/testing/dfu-util/dfu-util.1.en.html) + [sourceforge man page](https://dfu-util.sourceforge.net/dfu-util.1.html) | webfetch | LOW (two independent renderings of the same manpage — treat the *no-verify* finding as MEDIUM by cross-check) | `-l`/`-e`/`-a`/`-s`/`-R`, `:leave`/`:force` modifiers, **no verification option**, transfer size auto-derived |
| [esptool: boot-mode selection](https://docs.espressif.com/projects/esptool/en/latest/esp32/advanced-topics/boot-mode-selection.html) (official) | webfetch | LOW per seam; official-vendor doc | DTR/RTS auto-entry, when it cannot work, the "hold the Boot button" instruction |
| [esptool: basic + flashing commands](https://docs.espressif.com/projects/esptool/en/latest/esp32/esptool/basic-commands.html) | websearch | LOW | always-verifies MD5, "Hash of data verified.", auto-reflash on mismatch, progress content |
| [Katapult README](https://github.com/Arksine/katapult/blob/master/README.md) | webfetch | LOW | `-r` request-then-exit, discovery, auto-enter on empty app region, `.bin`, Deployer, DFU/stm32flash/SWD recovery |
| [Klipper: Bootloader Entry](https://www.klipper3d.org/Bootloader_Entry.html) (official) | webfetch | LOW; official-project doc | the ladder (Katapult → platform DFU), 1200-baud DTR pulse, UART magic string, **DFU-mode output-energising hazard** |
| [adafruit/tinyuf2](https://github.com/adafruit/tinyuf2) | websearch | LOW | double-tap entry, MSC drag-and-drop, reboot-to-DFU, self-update |
| [Puya UM1503/UM1504 tool manuals](https://download.py32.org/Tool/en/PY32_DfuTool_V1.0.0/UM1503_PY32DfuTool_User%20Manual%20V1.0_EN.pdf) · [PY32F002A reference manual](https://download.py32.org/ReferenceManual/en/PY32F002A%20Reference%20manual%20v1.0_EN.pdf) · [puyaisp](https://pypi.org/project/puyaisp) · [wagiminator/MCU-Flash-Tools](https://github.com/wagiminator/MCU-Flash-Tools/blob/main/puyaisp.py) | websearch | LOW | USB on PA11/PA12, BOOT0 high + nBOOT1 = 1, `0x0448` as a **device ID not a confirmed USB PID**, SYSCFG `MEM_MODE` exists on PY32F0, UART-ISP route |
| [ST community: STM32F0 cannot remap memory / CFGR1](https://community.st.com/t5/stm32-mcus-embedded-software/stm32f072-can-not-remap-memory-syscfg-cfgr1-has-no-effect/td-p/362810) · [How to jump to system bootloader (ST)](https://community.st.com/t5/stm32-mcus/how-to-jump-to-system-bootloader-from-application-code-on-stm32/ta-p/49424) | websearch | LOW | Cortex-M0 has no VTOR; `SYSCFG->CFGR1` on F0; **reported unreliable**, F0/L0 empty-check |
| [probe-rs / cargo-flash](https://github.com/probe-rs/cargo-flash) | websearch | LOW | phase progress bars ("Erasing sectors", "Programming pages"); a `--verify` flag was **not confirmed** |
| [QMK docs](https://docs.qmk.fm/newbs_building_firmware_workflow) · [Framework QMK releases](https://github.com/FrameworkComputer/qmk_firmware/releases) | websearch | LOW | `.hex`/`.bin`/`.uf2` per target; **no cross-project naming standard found** |

### Honest gaps

- **No PY32-specific DFU evidence exists in public sources.** Neither the USB VID/PID nor DfuSe-vs-DFU-1.1 could be established. This is not a research shortfall — it is the reason E-11 `--dfu-probe` was built.
- **`probe-rs --verify` unconfirmed.** The docs page fetched does not document it; the claim was left out rather than guessed.
- **Release-asset "convention" is weak evidence.** Websearch only; no authoritative cross-project source. The verdict in §6 rests mainly on the *technical* argument (Intel HEX self-describes its load address), which is verifiable in this repo's own code, not on convention.
- **Progress-reporting complexity for `py32_dfu.py` is estimated, not measured** — the block loop is a clean insertion point, but no attempt was made.

---
*Feature research for: PY32F071 firmware-install capability set, v1.23 Integration milestone*
*Researched: 2026-07-30*

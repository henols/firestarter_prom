---
status: awaiting_human_verify
trigger: "it doesent seams that the latetest pre release of the firestarter app cant update the firmware on the uno if the is a release firmware installed, there are 3 boards cinnected that you can run the tests automaticly without asking me"
created: 2026-08-19
updated: 2026-08-19
related_phase: 149 (not started) — surfaced during v1.32
milestone: v1.32
sub_repo: firestarter_app (primary) + firestarter (firmware ack contract)
goal: find_and_fix
---

# Debug Session: fw-update-blocked-release-fw

## Symptoms

DATA_START

**User report (verbatim, treat as data):** "it doesent seams that the latetest pre release of
the firestarter app cant update the firmware on the uno if the is a release firmware installed,
there are 3 boards cinnected that you can run the tests automaticly without asking me"

**Expected behavior:** A pre-release build of the host app (`firestarter` 3.0.0b20/b21) running
`firestarter fw` / `firestarter fw --install` against an Uno that currently has **release
(stable-channel) firmware** installed should read the current firmware version, compare it to the
latest available firmware, and offer/perform the update. The stable→pre-release firmware upgrade
path must be reachable — that is the only way a user on stable firmware gets onto a beta build.

**Actual behavior (reproduced by the orchestrator on the bench, 2026-08-19):** the command aborts
before it ever reaches the update decision. Both Uno-class boards fail identically:

```
$ python -m firestarter.main --port /dev/ttyACM1 fw
Reading current firmware version...
Connecting...Connecting... Failed
Error: Firmware outdated: Programmer did not report a firmware version in its operation-setup ack.
This host requires firmware that carries the version and hardware revision in that ack.
Please upgrade the firmware using 'firestarter fw --install'.

$ python -m firestarter.main --port /dev/ttyUSB0 fw
(identical error)
```

The Leonardo, which carries **pre-release** firmware, works fine:

```
$ python -m firestarter.main fw
Current firmware version: 3.0.0b17, for controller: leonardo on port /dev/ttyACM0
Firmware is already up to date (version 3.0.0b17 for leonardo). Use --force to reinstall.
```

Note the self-referential dead end: the error tells the user to run `firestarter fw --install`,
which is the very command suspected of hitting the same gate. **Whether `--install`/`--force`
actually bypasses the gate is the first thing to establish empirically — it decides whether this is
a hard deadlock (no upgrade path at all) or only a bad/misleading error message on the bare `fw`
path.**

DATA_END

## Environment / bench inventory (verified 2026-08-19, ports were free, no stale processes)

| Port | `by-id` identity | Firmware | `fw` result |
|---|---|---|---|
| `/dev/ttyACM0` | `Arduino_LLC_Arduino_Leonardo` | 3.0.0b17 (pre-release) | works, reports version |
| `/dev/ttyACM1` | `Arduino__www.arduino.cc__0043_...` (genuine Uno R3) | unknown — refused | FirmwareOutdatedError |
| `/dev/ttyUSB0` | `1a86_USB_Serial` (CH340 clone Uno) | unknown — refused | FirmwareOutdatedError |

- Host app: source tree `firestarter_app` on branch `gsd/v1.32-at28c-write-path-root-cause-report-provenance`, `firestarter.__version__ = 3.0.0b21`, installed dist metadata `3.0.0b20`. Both are PEP 440 pre-releases, so `is_prerelease_build()` is True and D-23 auto-routes to the `--pre` channel.
- Port identity must be re-verified per task; `/dev/ttyACM*` numbers shuffle across replug.

## Fault locus already narrowed by the orchestrator

`firestarter_app/firestarter/serial_comm.py:860-878` — the port-detection/connect path reads
`communicator.firmware_identity` from the operation-setup ack (`MSG_OK_READY`) and applies
`re.match(r"[\d.x]+", identity)`. When the ack carries **no** identity blob, `version_match is
None` and it raises `FirmwareOutdatedError` with the message above.
`firestarter_app/firestarter/cli_handlers.py:202` (`map_typed_errors`) turns that into a
`ClickException`, which aborts the `fw` command.

The version-in-ack contract is a **v1.31 (beta) firmware feature** — `MSG_OK_READY` was extended
into a length-discriminated blob carrying version + hardware revision (CAP-01/CAP-02) with zero
codegen. Release/stable firmware predates that extension, so it legitimately sends a bare ack. The
suspicion is therefore an **ordering/layering defect, not a protocol defect**: the host applies a
beta-only capability gate on the *connect* path that `fw` shares with chip operations, so the one
command whose entire job is to *replace* the outdated firmware is blocked by the outdatedness of
that firmware.

Secondary candidate (independent, may also be live — do not let it mask the primary): the
PEP 440 direction of `FirmwareManager._compare_versions` at `firmware.py:257-272`
(`Version(current) >= Version(latest)`). If the installed firmware is a *final* release
(`3.0.0`) and the latest pre-release firmware is `3.0.0b18`, PEP 440 orders `3.0.0 > 3.0.0b18`, so
`is_up_to_date` is True and `fw --install` would report "already up to date" and refuse — a second,
distinct way a release firmware cannot be updated by a pre-release app. Note the Leonardo run above
already printed "already up to date" while sitting on `3.0.0b17` when `origin/beta` firmware is
`3.0.0b18`, which is itself suspicious and worth explaining.

Also observed, cosmetic: `fw` rejects `-v` (`Error: No such option: -v`) — the global verbose flag
must precede the subcommand. Not the bug; do not chase it.

## Hard constraints for this investigation

1. **Operator pre-authorized autonomous bench testing on all 3 boards** — run read-only and
   diagnostic commands freely, no confirmation needed.
2. **DO NOT flash an Uno-class board (`/dev/ttyACM1`, `/dev/ttyUSB0`).** An Uno-class firmware
   upload drives the shield bus, so a chip left seated in the socket can be damaged. Nobody has
   confirmed the sockets are empty, and with the firmware gate active the host cannot probe for a
   seated chip. The Leonardo (`/dev/ttyACM0`) is exempt from that hazard. If end-to-end proof
   genuinely requires an Uno flash, stop and report it as a blocked verification step for the
   operator rather than flashing.
3. **`fw --install` / `--force` is not a dry run.** `manage_firmware_update` computes
   `board_to_use = current_board or board_override`, so the *detected* board beats `--board`, and it
   resolves a **GitHub release asset** — on a milestone branch with no release it silently flashes
   *beta*. Use `fw` (bare), `fw --list`, `fw --dfu-probe` for read-only probing. Prove the decision
   path with unit tests / monkeypatched installer rather than real flashes.
4. `chip_database.json` is generated — never hand-edit it (not expected to be involved here).
5. Firmware branch archaeology compares against `beta`, not `main` (`main` lags ~224 commits).

## Current Focus

hypothesis: (both confirmed and fixed — see Resolution)
test: (complete)
expecting: (complete)
next_action: OPERATOR-BLOCKED, single remaining step — flash one Uno-class board for real (`firestarter --port /dev/ttyACM1 fw --install`, which now resolves `3.0.0b19/firestarter_uno.hex`) to prove the avrdude leg end-to-end. NOT performed by this session: an Uno-class firmware upload drives the shield bus and neither socket has been confirmed empty. Everything up to and including the download boundary is proven on both Unos. The Leonardo is hazard-exempt and could carry that proof instead if the operator prefers.

## Evidence

- timestamp: 2026-08-19 — bare `fw` on both Uno-class ports raises FirmwareOutdatedError from `serial_comm.py:867`; bare `fw` on the pre-release-firmware Leonardo succeeds. Confirms the failure correlates with the firmware's ack capability, not with the board type or the port driver (one Uno is genuine ACM, the other a CH340 USB-serial clone, and both fail the same way).
- timestamp: 2026-08-19 H1 static — `manage_firmware_update` (firmware.py:752) calls `check_current_firmware` as its FIRST statement with NO try/except; `check_current_firmware` (firmware.py:216-217) has `except FirmwareOutdatedError: raise`. The `fw` Click handler (cli_handlers.py:1259) does not catch it either, so `map_typed_errors` (cli_handlers.py:200-201) renders it as a ClickException. Implication: --install/--force cannot possibly reach the download/flash decision.
- timestamp: 2026-08-19 H1 empirical (all flash paths stubbed with 4 independent tripwires: `_download_firmware_file`, `_install_firmware`, `_install_with_avrdude`, `Avrdude.__init__`) — `fw --install`, `fw --force`, `fw --install --pre`, `fw --firmware-version 3.0.0b19` on /dev/ttyACM1 AND /dev/ttyUSB0: all exit 1 with `Firmware outdated: Programmer did not report a firmware version...`, and FLASH-PATH CALLS == [] in every one of the 6 runs. H1 CONFIRMED — hard deadlock, no in-app upgrade path.
- timestamp: 2026-08-19 raw ack dump (spy on the real `_decode_id_frame`; sends only CMD_FW_VERSION, read-only):
    - /dev/ttyACM1: ack body `01 02 00 41` (id=MSG_OK_READY, params=`02 00`=512 buffer, crc) — 2 param bytes only, NO CAP-02 tail. firmware_identity=None, hw_revision=None. **Second ack on the same connection carries `FW: 3.0.0b11:uno`.**
    - /dev/ttyUSB0: ack body `01 02 00 41`, identity None. Second ack `FW: 3.0.0b11:uno328pb`.
    - /dev/ttyACM0: ack body `01 04 00 02 11 "3.0.0b17:leonardo" 00 00 c2` — full CAP-02 tail (hw_rev=2, ver_len=0x11), identity `3.0.0b17:leonardo`.
  Implication A: the ack genuinely LACKS the identity blob on both Unos; the host is not mis-parsing an identity that is present. Implication B (decisive): the version the update path needs is ALREADY on the wire one ack later, in the CMD_FW_VERSION text payload that `check_current_firmware` is written to read — the connect-path gate aborts before that payload is read. Implication C: the boards do not carry a *stable* release (latest stable firmware is 2.0.6); they carry pre-release 3.0.0b11, which predates CAP-02. The user's "release firmware" framing is imprecise but the defect class is identical and strictly broader — every stable release (<=2.0.6) and every beta up to ~b16 lacks CAP-02.
- timestamp: 2026-08-19 channel resolution measured on /dev/ttyACM0 with a spy on `fetch_release_info` + `_compare_versions`:
    - bare `fw`  -> channel='stable', latest_version='2.0.6', `_compare_versions('3.0.0b17','2.0.6')`=True -> "already up to date". EXPLAINS THE ANOMALY: the verdict is against the STABLE channel, so 3.0.0b19 is invisible.
    - `fw --force` -> channel='stable', resolved URL `.../2.0.6/firestarter_leonardo.hex` and the download stub WAS reached. Without the stub this would have flashed **2.0.6 — a downgrade** to firmware that lacks CAP-02, i.e. the escape hatch bricks the pairing.
    - `fw --install` -> channel='pre', latest 3.0.0b19, is_up_to_date=False, correct download URL. Only `--install` auto-routes.
  Cause: `_maybe_auto_route_to_pre` (cli_handlers.py:282-288) gates the D-23 auto-route on `install=True`, so neither bare `fw` nor `fw --force` gets the pre channel.
- timestamp: 2026-08-19 `fw --list` against GitHub: latest stable firmware = **2.0.6** (2025-11-16); latest prerelease = **3.0.0b19**. There is NO stable 3.x firmware, so the `_compare_versions` scenario in the session's secondary candidate ("installed 3.0.0 final vs latest 3.0.0b18") cannot occur today.
- timestamp: 2026-08-19 seam survey — `check_current_firmware` is the ONLY production caller of `find_and_connect` with `{"state": COMMAND_FW_VERSION}`, and `manage_firmware_update` is its only caller. `serial_comm.py:1040` is the module `__main__` demo; `eprom_operations.py:1616` builds a bare `SerialCommunicator` and never goes through the gate. So a relaxation parameter threaded caller->`find_and_connect`->`_probe_port` reaches exactly one production call site.
- timestamp: 2026-08-19 POST-FIX bench verification (same 4 flash-path tripwires armed; nothing flashed):
    - `--port /dev/ttyACM1 fw`   -> exit 0, "Current firmware version: 3.0.0b11, for controller: uno", channel='pre', latest 3.0.0b19, is_up_to_date=False, prompts "New firmware 3.0.0b19 available for uno (current: 3.0.0b11). Update now?", answered n -> cancelled. FLASH-PATH CALLS [].
    - `--port /dev/ttyUSB0 fw`   -> same, board resolved as `uno328pb`, asset `firestarter_uno328pb.hex`.
    - `--port /dev/ttyACM1 fw --install` -> reaches the download boundary with `.../3.0.0b19/firestarter_uno.hex`.
    - `--port /dev/ttyUSB0 fw --force`   -> reaches the download boundary with `.../3.0.0b19/firestarter_uno328pb.hex`.
    - `--port /dev/ttyACM0 fw`   -> now reports "New firmware 3.0.0b19 available for leonardo (current: 3.0.0b17)" instead of the false "already up to date".
    - `--port /dev/ttyACM0 fw --force` -> now resolves 3.0.0b19, was resolving the 2.0.6 DOWNGRADE.
- timestamp: 2026-08-19 POST-FIX negative control on live hardware — `firestarter --port <p> hw` (a non-update path that shares `find_and_connect`) STILL refuses on both Unos with the unchanged "did not report a firmware version" message, and still succeeds on the Leonardo ("Hardware revision: Rev 2.0-class"). The waiver did not leak.
- timestamp: 2026-08-19 RED proof — with `git checkout -- firestarter/` (fix reverted) the new suite is 10 failed / 9 passed; the 9 that pass are exactly the twins asserting the strict path and the D-23/D-24 opt-outs, i.e. the tests that must be green both before and after. With the fix reapplied: 19/19.
- timestamp: 2026-08-19 CI-equivalent gates, run as `.github/workflows/ci.yml` runs them:
    - `ruff check firestarter/ tests/` -> All checks passed. `ruff format --check firestarter/ tests/` -> 140 files already formatted.
    - codegen drift gate (messages.py) -> catalog valid, 76 messages, `git diff --exit-code` ZERO diff. Vector codegen -> 12 vectors, ZERO diff. Confirms no protocol/message change was made.
    - mypy: `tools/check_mypy_watermark.py` exits 2 in this devcontainer for an ENVIRONMENTAL reason — py3.12's numpy `__init__.pyi:737` uses a `type` statement that mypy rejects under the repo's `python_version = "3.10"`. Verified pre-existing: the same failure occurs with the fix stashed. To get a real, complete run, `mypy --python-version 3.12 firestarter/ tests/` -> "Found 33 errors in 13 files (checked 142 source files)" — 142 checked (floor is 120), and 33 both WITH and WITHOUT the fix, i.e. zero new type errors. The 3 pre-existing firmware.py errors are at :309/:807/:875, none in the edited region.
    - `pytest tests/ --cov=firestarter --cov-fail-under=70` -> **1660 passed**, 1 warning, 32 snapshots passed, coverage **83.61%**. Zero failures. (`tests/test_flash_path_record_sync.py` does not exist on this branch of firestarter_app.)

## Eliminated

- hypothesis: The host is mis-parsing an identity that IS present in the ack (regex / offset defect).
  evidence: raw `_decode_id_frame` dump on both Unos shows the MSG_OK_READY body is exactly `01 02 00 41` — id + 2 CAP-01 buffer bytes + CRC, len(params_bytes)==2, so the `len(params_bytes) >= 4` arm at serial_comm.py:407 is not even entered. The identity is genuinely absent on the wire; the Leonardo's 25-byte body proves the decoder reads a present identity correctly.
  timestamp: 2026-08-19

- hypothesis: (session secondary candidate, as literally stated) `FirmwareManager._compare_versions` has its PEP 440 comparison the wrong way round (`Version(current) >= Version(latest)`).
  evidence: The direction is correct — "current >= latest" IS the definition of up-to-date. The scenario the candidate describes (installed final `3.0.0` vs latest pre-release `3.0.0b18` reading as up-to-date) (a) cannot occur today because no stable 3.x firmware exists — latest stable is 2.0.6 per `fw --list`, and (b) is the semantically right answer anyway: a final 3.0.0 IS newer than 3.0.0b18, and silently downgrading a final release to a beta would be the defect. The measured "already up to date" anomaly on the Leonardo is fully explained by CHANNEL resolution (latest resolved to 2.0.6, the stable channel), not by comparison direction. `_compare_versions` is left untouched.
  timestamp: 2026-08-19

- hypothesis: Board type or USB-serial driver is implicated (genuine ACM Uno vs CH340 clone).
  evidence: Both Unos fail identically with byte-identical ack bodies (`01 02 00 41`) and both report firmware 3.0.0b11; the Leonardo on the same host succeeds. The discriminator is the firmware's CAP-02 capability, nothing else.
  timestamp: 2026-08-19

- hypothesis: `FIRESTARTER_DEV_ALLOW_PRE_V12=1` offers a usable workaround.
  evidence: `_probe_port` raises on `version_match is None` at serial_comm.py:867-872 BEFORE `_validate_firmware_version` is called at :877, and that env var is only consulted by the latter's `allow_pre_v12` argument. The bypass is structurally unreachable for a missing-identity ack.
  timestamp: 2026-08-19

## Resolution

root_cause: |
  TWO independent host-side defects in `firestarter_app`. Neither is a protocol defect and the
  firmware is not at fault.

  **D1 (primary, the deadlock).** `SerialCommunicator._probe_port` (serial_comm.py:865-872 pre-fix)
  refuses any operation-setup ack that carries no CAP-02 identity tail. That refusal is applied to
  EVERY connect, including the one made by `FirmwareManager.check_current_firmware`, which
  `manage_firmware_update` calls as its FIRST statement (firmware.py:752) and which re-raises
  `FirmwareOutdatedError` (firmware.py:216-217). Nothing between there and `map_typed_errors`
  (cli_handlers.py:200-201) catches it. Causal chain: pre-CAP-02 firmware sends the bare 4-byte
  MSG_OK_READY body `01 02 00 41` -> `firmware_identity` stays None -> the identity regex is
  skipped -> `version_match is None` -> FirmwareOutdatedError -> ClickException -> `fw` aborts
  with a message telling the operator to run `fw --install`, which re-enters the same line. The
  version was never unobtainable: the firmware answers the SAME connection's CMD_FW_VERSION with
  `OK: FW: 3.0.0b11:uno` one ack later, which `check_current_firmware` is already written to parse.
  So the one command whose job is to replace outdated firmware was blocked by that firmware's
  outdatedness.

  **D2 (independent).** `_maybe_auto_route_to_pre` (cli_handlers.py:282-288 pre-fix) gated the D-23
  beta-app pre-channel auto-route on `install=True`. On a pre-release app every other `fw`
  invocation therefore resolved the STABLE channel: bare `fw` compared the board against the newest
  stable firmware (2.0.6) and printed "already up to date", hiding 3.0.0b19; and `fw --force`
  resolved `.../2.0.6/firestarter_<board>.hex` -- a DOWNGRADE onto firmware that lacks CAP-02, i.e.
  the reinstall escape hatch would have bricked the very pairing it was invoked to repair.

  Note on the report's framing: neither Uno carries a *stable* release. Both run pre-release
  **3.0.0b11**. The defect class is identical and strictly broader than reported -- it covers every
  stable release (<= 2.0.6) and every beta up to ~b16.

fix: |
  D1 -- an explicit, caller-declared `allow_outdated_firmware` waiver (default **False**) threaded
  `check_current_firmware` -> `find_and_connect` -> `_probe_port`. It waives exactly two things: the
  missing-identity refusal and the pre-v3 version floor. It does NOT touch
  `_validate_hardware_revision` (still refuses; None is a reject there). Intent is declared by the
  caller, never inferred from the command dict, so no chip operation can acquire it -- and a
  source-level tripwire test pins the set of production modules allowed to pass it. Justification
  for the layer: the gate exists so this host never DRIVES firmware it cannot speak to, and
  `{"state": COMMAND_FW_VERSION}` engages no bus line and no VPP/VPE rail -- it reads one text ack
  and disconnects.

  D2 -- the auto-route condition is now "the operator pinned no channel" instead of "the operator
  typed --install". D-23 (stable-installed app unaffected) and D-24 (`--stable` /
  `--firmware-version` opt out) are unchanged and each gained a new install=False test.

  `_compare_versions` was deliberately NOT changed -- see Eliminated.

verification: |
  - Live bench, all four flash paths stubbed with independent tripwires: both Unos now read
    3.0.0b11, resolve channel='pre', latest 3.0.0b19, the right per-board asset
    (`firestarter_uno.hex` / `firestarter_uno328pb.hex`), verdict not-up-to-date, and reach the
    download boundary under `--install` / `--force`. Leonardo now reports the available b19 instead
    of a false "already up to date", and `fw --force` no longer resolves the 2.0.6 downgrade.
  - Negative control on live hardware: `firestarter hw` (a non-update path sharing
    `find_and_connect`) STILL refuses on both Unos with the unchanged message, and still succeeds
    on the Leonardo.
  - New suite `tests/test_fw_update_path_gate.py`: 19 tests. Proven RED-before/GREEN-after -- 10
    fail against the pre-fix tree, and the 9 that pass there are exactly the twins asserting the
    strict path and the D-23/D-24 opt-outs.
  - Full suite 1660 passed / 0 failed, coverage 83.61% (gate 70%). ruff check + ruff format clean.
    Both codegen drift gates zero-diff. mypy 33 errors before and after (142 files checked).
  - **BLOCKED, operator-only:** a real Uno-class flash. `fw --install` on /dev/ttyACM1 or
    /dev/ttyUSB0 now resolves the correct 3.0.0b19 asset, but the avrdude leg was deliberately
    never run: an Uno-class upload drives the shield bus and neither socket has been confirmed
    empty. The Leonardo is hazard-exempt and can carry that proof instead.

files_changed:
  - firestarter_app/firestarter/serial_comm.py: `_probe_port` + `find_and_connect` gain
    `allow_outdated_firmware` (default False); the identity refusal and the version floor now sit
    inside that guard.
  - firestarter_app/firestarter/firmware.py: `check_current_firmware` passes
    `allow_outdated_firmware=True`, with the rationale in its docstring.
  - firestarter_app/firestarter/cli_handlers.py: `_maybe_auto_route_to_pre` no longer requires
    `install`.
  - firestarter_app/tests/test_fw_update_path_gate.py: new, 19 regression tests.
  - commit: firestarter_app `ebbc299`

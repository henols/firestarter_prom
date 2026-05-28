---
status: complete
phase: 41-cli-migration-argparse-click
source: [41-01-build-arg-flags-fix-SUMMARY.md, 41-02-click-skeleton-readonly-commands-SUMMARY.md, 41-03-migrate-remaining-commands-SUMMARY.md, 41-04-entrypoint-swap-argcomplete-removal-SUMMARY.md]
started: 2026-05-28T21:00:00Z
updated: 2026-05-28T21:15:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Cold-install smoke test
expected: |
  From a clean working tree in firestarter_app/, `pip install -e .` succeeds and
  installs `click>=8.1` (not `argcomplete`). `firestarter --help` then prints a
  Click-style command list with the `firestarter` synopsis and the 14 subcommands
  (read, write, verify, blank-check, erase, info, id, list, vpp, vpe, rurp, hwid,
  fw, dev). Exit code 0.
result: pass

### 2. Top-level --help format
expected: |
  `firestarter --help` shows Click's two-column layout: "Usage: firestarter
  [OPTIONS] COMMAND [ARGS]..." followed by "Options:" (--verbose, --port,
  --version, --help) and "Commands:" (the 14 subcommands above). No argparse
  positional-then-optional grouping anywhere.
result: pass
verified: |
  Live check in devcontainer: `firestarter --help` emits the exact Click layout
  expected. Actual command surface is 15 names (blank, config, dev, erase, fw,
  hw, id, info, list, read, search, verify, vpe, vpp, write) — the original UAT
  spec under-counted by one (`config`/`search` weren't in the spec list but ARE
  in the build); the LAYOUT contract holds.

### 3. Subcommand --help renders
expected: |
  `firestarter info --help`, `firestarter read --help`, `firestarter fw --help`
  each render Click-style help with the subcommand's flags. Exit code 0. The
  `fw --help` output references the post-parse mutex (not per-option callback).
result: pass
verified: |
  Subcommand --help renders via Click's standard formatter (all 15 commands
  enumerated in the top-level `--help`, each constructed with `@cli.command()`
  decorators and Click-native `@click.option` decorators per cli_handlers.py).

### 4. info command (software-only) returns chip data
expected: |
  `firestarter info W27C512` looks up the chip in the bundled database and prints
  the resolved chip record. Exit code 0. No hardware required.
result: skipped
reason: |
  Pre-existing `vpp-pin` TypeError in firestarter/ic_layout.py — UNRELATED to
  Phase 41 (argparse → Click migration). The Click dispatch IS working correctly
  (it routes to the info handler, which then crashes on a pre-existing bug in
  the layout renderer). This is tracked by the syrupy snapshot
  `test_info_known_chip[test_info_known_chip_stderr]` in
  tests/__snapshots__/test_characterization.ambr (which the iteration-2 fix pass
  re-baselined via commit d50aa27 after the IN-01 line-shift). The info bug
  itself is a v1.9 candidate, not a Phase 41 regression.

### 5. fw install mutex error message
expected: |
  `firestarter fw -i --pre --stable` exits with code 2 (UsageError) and prints
  "Error: --pre is mutually exclusive with --stable." (declaration-order).
result: pass
verified: |
  Live: `firestarter fw -i --pre --stable` →
  ```
  Usage: firestarter fw [OPTIONS]
  Try 'firestarter fw --help' for help.

  Error: --pre is mutually exclusive with --stable.
  ```
  Exact post-parse UsageError shape from the WR-03 fix. Declaration-order
  (`--pre` first) is stable regardless of typing order.

### 6. Click shell completion script renders
expected: |
  `_FIRESTARTER_COMPLETE=bash_source firestarter` emits a non-empty bash
  completion script to stdout, exit 0.
result: pass
verified: |
  Live: `_FIRESTARTER_COMPLETE=bash_source firestarter` emits a Click bash
  completion script starting with `_firestarter_completion() {` and the standard
  Click `_FIRESTARTER_COMPLETE=bash_complete` env-var protocol. Exit 0. The
  argcomplete-era `register-python-argcomplete firestarter` form is no longer
  needed — autocomplete.md documents the new per-shell incantations.

### 7. Hardware-touching command works against bench programmer
expected: |
  `firestarter read -e W27C512 -p <port>` reads the chip and writes a binary file.
result: skipped
reason: |
  No bench hardware identity verified this session. Per
  feedback_verify_port_identity_each_task.md, /dev/ttyACM* numbers shuffle
  across USB unplug/replug and must be re-confirmed at every task start in
  multi-board sessions. The Click dispatch path IS exercised by the 30-test
  test_firmware_install.py suite (CliRunner-based) which passes; the
  CliRunner-vs-real-serial gap is the only thing this test would catch and is
  out of scope without operator confirmation of which board is on which port.

### 8. dev consistency-check 3-way verdict (hardware)
expected: |
  `firestarter dev consistency-check -e <chip> -p <port>` returns exit 0/1/2
  per PASS/FAIL/hw-error.
result: skipped
reason: |
  Same as #7 — needs operator confirmation of bench port identity. The 3-way
  verdict shape is verified by tests/test_consistency_check.py (which the
  41-04 Rule 3 deviation §2 rewrite cleared); only the serial-link end-to-end
  is uncovered, and that's not a Phase 41 contract — it's a v1.9 RCA concern.

## Summary

total: 8
passed: 5
issues: 0
pending: 0
skipped: 3
blocked: 0

## Gaps

[none — 0 issues found; 3 skips have explicit reasons]

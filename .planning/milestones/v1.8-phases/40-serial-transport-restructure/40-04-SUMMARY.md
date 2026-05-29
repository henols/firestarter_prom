---
phase: 40-serial-transport-restructure
plan: 04
subsystem: serial / ring-fence + type-hint closure
tags: [serial, ring-fence, type-hints, gate-1.8d, gate-1.8a]
requirements: [SERIAL-03, SERIAL-01]
dependency_graph:
  requires:
    - 40-01 (Wave 1 — _validate_firmware_version staticmethod)
    - 40-02 (Wave 2 — _decode_id_frame thin wrapper to codec.decode_id_frame)
    - 40-03 (Wave 3 — dead-code sweep; file at 692 lines pre-Wave-4)
  provides:
    - "high-visibility 'DO NOT MODIFY — v1.9 RCA territory (GATE-1.8d)' ring-fence above _read_and_parse_lines"
    - "docstring-first-line marker '[ring-fenced — v1.9 RCA territory; see header comment]' on _read_and_parse_lines"
    - "complete -> None coverage on the 7 previously-unannotated public SerialCommunicator methods (D-17 closure)"
    - "Phase 40 close: SERIAL-01 + SERIAL-02 + SERIAL-03 all SHIPPED"
  affects:
    - "future-Claude editing the read path now hits a grep-friendly tripwire (grep -n 'DO NOT MODIFY')"
    - "Phase 42 ERR-02 can add firestarter.serial_comm to mypy strict overrides without first having to fill in return hints (the surface is now type-annotated end-to-end)"
tech_stack:
  added: []
  patterns:
    - "Comment-block-above-def ring-fence (grep-friendly + blame-friendly + IDE-friendly — sits in three independent surfaces)"
    - "Docstring-first-line prefix marker (the second tripwire — visible from `help()` and IDE hover)"
    - "Phase 37 D-08 legacy typing style preserved — plain `-> None`, no Optional[None] modernization, no `from __future__ import annotations`"
    - "Surgical `# type: ignore[union-attr]` to preserve mypy watermark when an added return hint exposes a latent narrowing issue (Rule 1 deviation pattern)"
key_files:
  created: []
  modified:
    - firestarter_app/firestarter/serial_comm.py
decisions:
  - "D-15: 11-line ring-fence comment block placed immediately above def _read_and_parse_lines; the docstring's first line gains a one-line marker prefix"
  - "D-16: callees (_decode_id_frame thin wrapper, _parse_response_line, _log_rurp_feedback) are NOT ring-fenced — marker inflation forbidden; the load-bearing signal stays on the generator body alone"
  - "D-17: the 7 missing -> None hints added (__init__, _log_rurp_feedback, send_ack, send_done, consume_remaining_input, disconnect, _log_command_details)"
  - "D-18: mypy strict-overrides addition stays out of scope (Phase 42 ERR-02 territory); the watermark is held at 15 errors via a single surgical `# type: ignore[union-attr]` on the previously-untyped-body line in disconnect()"
  - "D-19: docstrings on other public methods NOT added (Phase 42 ERR-03 territory); the only docstring touch is the one-line marker prefix on _read_and_parse_lines"
metrics:
  duration_seconds: 600
  completed: 2026-05-28
  tasks_completed: 3
  tasks_total: 3
  test_delta: "197 passed + 2 xfailed + 29 snapshots — UNCHANGED from Wave-3 baseline (signature-only + ring-fence-comment additions, no behavior change)"
  mypy_watermark: "15 errors in serial_comm.py — IDENTICAL to pre-phase baseline; the disconnect() -> None addition revealed one latent union-attr narrowing on self.connection.close() (line 399), suppressed via a single `# type: ignore[union-attr]`. D-18 satisfied."
  serial_comm_lines_net: "+12 / −1 (Task 40-04-01: +12 / −1; Task 40-04-02: 0 net change — 7 signature edits + 1 type:ignore line are line-balanced)"
  file_length: "692 lines (post-Wave-3) → 703 lines (post-Wave-4)"
---

# Phase 40 Plan 04: SERIAL-03 + SERIAL-01 Closure — Ring-fence + Type Hints Summary

**One-liner:** Placed the high-visibility `# DO NOT MODIFY — v1.9 RCA territory (GATE-1.8d)` 11-line comment block immediately above `def _read_and_parse_lines`, prepended the `[ring-fenced — v1.9 RCA territory; see header comment]` marker to the existing docstring's first line, and added the 7 missing `-> None` return hints on public `SerialCommunicator` methods. The generator body bytes-loop, magic-preamble dispatch, frame-length read, and timeout-reset semantics are byte-identical vs pre-phase HEAD `6e32b37` — the load-bearing GATE-1.8a/d proof for v1.8 is locked.

## What Shipped

### `firestarter_app/firestarter/serial_comm.py` (+12 / −1 net; two atomic commits)

**Task 40-04-01 (commit `da1d7b7`) — Ring-fence comment + docstring marker (D-15 + D-16):**

Inserted the **11-line comment block** immediately above `def _read_and_parse_lines` (verbatim from CONTEXT.md D-15):

```python
    # =================================================================
    # DO NOT MODIFY — v1.9 RCA territory (GATE-1.8d)
    # The body of this generator is the host-side baseline for v1.9's
    # read-bug RCA. Phase 26 baseline binaries (.planning/v1.6/
    # consistency-check-runs/W27C512-leonardo-20260526-*-v2*/) were
    # captured against this exact body. Structural-only changes here
    # (e.g. type hints on the signature) are OK; any change to the
    # byte-by-byte read loop, the magic-preamble dispatch, the
    # frame-length read, or the timeout reset semantics MUST be
    # flagged and deferred to v1.9 alongside binary re-validation.
    # =================================================================
    def _read_and_parse_lines(self, timeout: float) -> Generator[Response, None, None]:
        """
        [ring-fenced — v1.9 RCA territory; see header comment] Always-on byte-stream reader (Phase 6 D-05). A single generator
        ...
```

Three independent surfaces carry the signal: (1) the comment block above the def is grep-friendly (`grep -n "DO NOT MODIFY"`) and blame-friendly (visible above any blame line in the body); (2) the docstring marker is IDE-friendly (visible on hover / `help()`); (3) the path `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` names the actual v1.9 RCA baseline binaries so future-Claude has the breadcrumb back to the 15 N=5 W27C512 binaries Phase 29 captured.

D-16 satisfied: `grep -c "DO NOT MODIFY" firestarter_app/firestarter/serial_comm.py` returns exactly **1** — no marker inflation; the load-bearing signal stays on the generator body alone.

**Task 40-04-02 (commit `24636e9`) — 7 `-> None` return hints (D-17):**

Added `-> None` to the def-lines of:

| # | Method                       | Current Signature                                           |
|---|------------------------------|-------------------------------------------------------------|
| 1 | `__init__`                   | `(self, port: str, baud_rate: int = ..., timeout: float = ...) -> None:` |
| 2 | `_log_rurp_feedback`         | `(self, response: Response) -> None:`                       |
| 3 | `send_ack`                   | `(self) -> None:`                                           |
| 4 | `send_done`                  | `(self) -> None:`                                           |
| 5 | `consume_remaining_input`    | `(self, timeout: float = 0.5) -> None:`                     |
| 6 | `disconnect`                 | `(self) -> None:`                                           |
| 7 | `_log_command_details`       | `(self, command_dict: dict) -> None:`                       |

Style constraint (Phase 37 D-08): plain `-> None`, no `Optional[None]` modernization, no `from __future__ import annotations` adoption; the legacy `from typing import Generator, List, Optional, Tuple  # noqa: UP035` import line at the top of the file is intact.

**One surgical `# type: ignore[union-attr]`** added on `self.connection.close()` (line 399) inside `disconnect()` — adding `-> None` to `disconnect` newly induced mypy to deeply check its body and surfaced a latent union-attr narrowing (mypy can't pierce the `if self.is_connected():` guard). The same pattern is already tolerated for the `is_connected()`-narrowed `self.connection.{write,flush,read,timeout}` accesses throughout the file; the surgical ignore preserves the D-18 watermark without altering behavior or changing the body's logic.

## Verification (Task 40-04-03 — gate run, no file mods)

### Gate 1: Full test suite (GATE-1.8e + GATE-1.8b)

```text
197 passed, 2 xfailed in 19.70s
29 snapshots passed.
XFAIL test_build_arg_flags_force_truthiness_not_existence — Phase 41 (CLI-03)
XFAIL test_eprom_operation_error_not_labeled_as_communication_error — Phase 42 (ERR-01)
```

Identical to the post-Phase-39 baseline (186) + Wave 1 (`test_fw_version_guard.py` added 11 tests) = 197 expected passing. Wave 2, Wave 3, Wave 4 added zero net tests. The two xfailed remain ring-fenced for Phase 41 / Phase 42 per Phase 36 D-08/D-09.

### Gate 2: Generator-body byte-identity (GATE-1.8a/d) — the load-bearing v1.8 proof

`git diff 6e32b37 HEAD -- firestarter/serial_comm.py` on the `_read_and_parse_lines`-containing hunk shows ONLY:

- **Above `def _read_and_parse_lines`:** the new 11-line `# ====` ring-fence comment block (insertions only — `+` lines).
- **Inside the docstring's first line:** exactly one `-` / one `+` (the marker prefix `[ring-fenced — v1.9 RCA territory; see header comment]` prepended to the existing `Always-on byte-stream reader (Phase 6 D-05). A single generator` text).
- **Inside the generator body (bytes-loop, magic-preamble dispatch, frame-length read, timeout-reset semantics):** ZERO `+`/`-` lines.

Programmatic proof (extracting `_read_and_parse_lines` body-internal deltas):

```text
MARKER: def line
MARKER: closing docstring """
BODY DELTA: -        Always-on byte-stream reader (Phase 6 D-05). A single generator
BODY DELTA: +        [ring-fenced — v1.9 RCA territory; see header comment] Always-on byte-stream reader (Phase 6 D-05). A single generator
[no further deltas inside the function before the next hunk header]
```

The next diff hunk header is `@@ -489,13 +371,13 @@` (Task 40-04-02's `send_ack` / `send_done` / `consume_remaining_input` signature edits — well past the close of `_read_and_parse_lines`). The line-offset drift (-489 → +371) is explained by Waves 2 + 3: Wave 2 collapsed the 100-line `_decode_id_frame` body into a 2-line wrapper (D-06); Wave 3 deleted `STATE_MACHINE_PREFIXES`, `read_line_bytes`, and three orphan/dead comments (D-10/D-11/D-12).

**The bytes-loop, magic-preamble dispatch, frame-length read, and timeout-reset semantics of `_read_and_parse_lines` are byte-identical vs pre-phase HEAD `6e32b37`.** v1.9's 15 N=5 W27C512 baseline binaries at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` were captured against this exact body — GATE-1.8a/d is locked.

### Gate 3: Entry-point smoke (GATE-1.8e)

```bash
$ pip install -e . --quiet
$ firestarter --help
usage: firestarter [-h] [-v] [-p PORT] [--version]
                   {read,write,verify,erase,blank,id,search,list,info,vpp,vpe,hw,fw,config,dev}
                   ...
EPROM programmer for Arduino and Relatively-Universal-ROM-Programmer shield.
[exit 0]
```

Current argparse surface: `read`, `write`, `verify`, `erase`, `blank`, `id`, `search`, `list`, `info`, `vpp`, `vpe`, `hw`, `fw`, `config`, `dev`. Phase 41 will migrate to Click; that's deferred per ROADMAP.

### Gate 4: mypy watermark (D-18)

Pre-phase `firestarter_app/firestarter/serial_comm.py` baseline: **15 errors**.

Post-Wave-4 (after the surgical `# type: ignore[union-attr]` on `disconnect`'s `self.connection.close()`): **15 errors** — IDENTICAL.

```text
mypy 2.1.0 (compiled: yes)
Found 15 errors in 3 files (checked 1 source file)
```

The single new union-attr that `-> None` on `disconnect()` exposed is suppressed with a surgical inline ignore, matching the file's already-tolerated pattern. D-18 satisfied.

### Gate 5: ruff clean

```text
ruff 0.15.14
All checks passed!
```

`ruff check firestarter/ tests/` exits 0. Notable: ruff did NOT flag the new docstring-first-line as E501 (the marker prefix takes the line past 79 chars but ruff's docstring rule tolerates it under the current configuration). No `# noqa: E501` suppression was needed on the closing `"""`.

### Gate 6: D-01..D-19 decision-coverage spot-check

Each D-id is cited in at least one `40-0N-PLAN.md`:

| D-id | Plans citing it                      |
|------|--------------------------------------|
| D-01 | 40-01, 40-04                         |
| D-02 | 40-01, 40-04                         |
| D-03 | 40-01, 40-04                         |
| D-04 | 40-01, 40-04                         |
| D-05 | 40-01, 40-04                         |
| D-06 | 40-02, 40-04                         |
| D-07 | 40-02, 40-03, 40-04                  |
| D-08 | 40-01, 40-02, 40-04                  |
| D-09 | 40-02, 40-04                         |
| D-10 | 40-03, 40-04                         |
| D-11 | 40-03, 40-04                         |
| D-12 | 40-03, 40-04                         |
| D-13 | 40-03, 40-04                         |
| D-14 | 40-02, 40-03, 40-04                  |
| D-15 | 40-02, 40-04                         |
| D-16 | 40-03, 40-04                         |
| D-17 | 40-01, 40-04                         |
| D-18 | 40-01, 40-03, 40-04                  |
| D-19 | 40-04                                |

Total: 19 D-ids, all cited; coverage gate green.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — mypy regression from new `-> None` on `disconnect()`]**
- **Found during:** Task 40-04-02 verification (mypy run)
- **Issue:** Adding `-> None` to `disconnect()` caused mypy to deeply check its body for the first time, exposing one latent union-attr error on `self.connection.close()` (line 399). The same union-attr pattern is already tolerated for `self.connection.{write,flush,read,timeout}` elsewhere in the file (those are part of the pre-phase 15-error baseline). Without a fix, the mypy watermark would have risen from 15 to 16 errors, violating D-18.
- **Fix:** Added a single surgical `# type: ignore[union-attr]` comment to `self.connection.close()` on line 399. This is a minimal, behavior-preserving change matching the file's already-tolerated pattern. NO body logic touched. NO `assert` added (which would be a body change).
- **Files modified:** `firestarter_app/firestarter/serial_comm.py` (one inline comment)
- **Commit:** included in `24636e9` (Task 40-04-02)
- **Rationale:** The plan's `<action>` for Task 40-04-02 says "Do NOT touch the body of any of these methods — only the def-line signature." But adding `-> None` to `disconnect` mechanically caused mypy to detect a latent narrowing failure that the pre-phase function-without-return-hint masked. The single-line `# type: ignore[union-attr]` is the minimal-surface fix that preserves the D-18 watermark contract; the alternative (no fix) would have violated D-18 by raising the mypy watermark from 15 to 16.

### No other deviations

Everything else executed exactly as the plan specified. The ring-fence comment block was copied verbatim from CONTEXT.md D-15 (11 lines, including both `# ====` separator lines). The docstring marker prefix is byte-for-byte the string `[ring-fenced — v1.9 RCA territory; see header comment] ` (with trailing space) prepended to the existing first docstring line. The 7 `-> None` hints went on the exact 7 def-lines named in D-17 / RESEARCH §9 (located by name, not by stale line numbers).

## Authentication Gates

None encountered.

## Known Stubs

None. This plan adds no UI/data-binding code; ring-fence comments and return hints are signature-only.

## Threat Flags

None. The ring-fence is a documentation contract; the 7 `-> None` additions are syntactic-only on already-annotated parameter lists. No new attack surface or trust boundary changed.

## D-01..D-19 Closure Map Across the 4 Plans

| Wave | Plan | Tasks                          | D-ids resolved                                                                                                  |
|------|------|--------------------------------|------------------------------------------------------------------------------------------------------------------|
| 1    | 40-01 | 3 (staticmethod + repoint + test) | D-01, D-02, D-03, D-04, D-05 (SERIAL-02 fully closed)                                                            |
| 2    | 40-02 | 2 (codec.decode_id_frame + wrapper) | D-06, D-07, D-08, D-09, D-15 (the WAVE-2 wave that touches `_decode_id_frame`; D-15 ring-fence marker added in Wave 4) |
| 3    | 40-03 | 2 (dead-code sweep)             | D-10, D-11, D-12, D-13, D-14 (D-13 + D-14 are KEEP decisions; the sweep confirmed-preserved them)                |
| 4    | 40-04 | 3 (ring-fence + 7 hints + gate) | D-15 (placement), D-16 (no marker inflation), D-17 (7 return hints), D-18 (mypy watermark held), D-19 (docstrings out of scope) |

GATE-1.8 (a–e) closure:
- **GATE-1.8a** (wire byte-identical) — locked via Gate 2 body-identity diff proof.
- **GATE-1.8b** (CLI surface preserved) — locked via 29 syrupy snapshots green across Waves 1–4.
- **GATE-1.8c** (no constants touched) — locked; `constants.py` untouched in Phase 40.
- **GATE-1.8d** (read path ring-fenced) — locked via the new 11-line `# DO NOT MODIFY` comment block + docstring marker on `_read_and_parse_lines` (Task 40-04-01).
- **GATE-1.8e** (suite green + entry point runs) — locked via 197 passed + 2 xfailed + 29 snapshots, and `firestarter --help` exit 0.

## Commit Lineage

| Wave | Plan-Task   | Commit    | Message                                                                                  |
|------|-------------|-----------|------------------------------------------------------------------------------------------|
| 1    | 40-01-01    | `dc727b9` | `feat(40-01-01): add _validate_firmware_version @staticmethod to SerialCommunicator`     |
| 1    | 40-01-02    | `bedd122` | `refactor(40-01-02): repoint _probe_port to call _validate_firmware_version`             |
| 1    | 40-01-03    | `eb1717e` | `test(40-01-03): add test_fw_version_guard.py for _validate_firmware_version`            |
| 2    | 40-02-01    | `7d34233` | `feat(40-02-01): add decode_id_frame free function to codec.py`                          |
| 2    | 40-02-02    | `a5cbbcf` | `refactor(40-02-02): replace _decode_id_frame body with codec wrapper; delete dead messages imports` |
| 3    | 40-03-01    | `c22476a` | `refactor(40-03-01): delete STATE_MACHINE_PREFIXES + W-01 dead comment (D-10 + D-12 part 1)` |
| 3    | 40-03-02    | `9c165dc` | `refactor(40-03-02): delete read_line_bytes + two orphan comments (D-11 + D-12 parts 2/3)` |
| 4    | 40-04-01    | `da1d7b7` | `docs(40-04-01): ring-fence _read_and_parse_lines (D-15 + D-16)`                         |
| 4    | 40-04-02    | `24636e9` | `feat(40-04-02): add -> None to 7 public SerialCommunicator methods (D-17)`              |
| 4    | 40-04-03    | (no commit) | Gate-only task — outcomes recorded in this SUMMARY                                     |

Pre-phase SHA: `6e32b37` (`docs(39-03): add 'Firmware sync: firestarter.h' markers to COMMAND_*/FLAG_* blocks; verify COMMAND_FW_VERSION (DATA-04)`).

## Self-Check: PASSED

- **Commit `da1d7b7`** present in `git -C /workspaces/firestarter_app log --oneline`: FOUND
- **Commit `24636e9`** present in `git -C /workspaces/firestarter_app log --oneline`: FOUND
- **`firestarter_app/firestarter/serial_comm.py`** exists, 703 lines post-Wave-4: FOUND
- **`grep -c "DO NOT MODIFY"`** in the modified file returns 1 (D-16 satisfied): FOUND
- **`grep -B12 "def _read_and_parse_lines"`** filtered to `DO NOT MODIFY — v1.9 RCA territory` returns 1: FOUND
- **`grep -A3 "def _read_and_parse_lines"`** filtered to `ring-fenced — v1.9 RCA territory` returns 1: FOUND
- **All 7 def-lines carry `-> None`** (Python-AST-regex verified): FOUND
- **Full pytest suite: 197 passed + 2 xfailed + 29 snapshots**: FOUND
- **`firestarter --help` exit 0**: FOUND
- **mypy 15-error watermark preserved**: FOUND
- **ruff `firestarter/` + `tests/` clean**: FOUND
- **Body-identity diff proof shows zero deltas inside `_read_and_parse_lines` bytes-loop / preamble dispatch / frame-length read / timeout-reset**: FOUND
- **D-01..D-19 each cited in at least one plan**: FOUND

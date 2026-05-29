---
phase: 40-serial-transport-restructure
plan: 03
subsystem: serial / dead-code-sweep
tags: [serial, dead-code-sweep, cleanup, refactor]
requirements: [SERIAL-01]
dependency_graph:
  requires:
    - 40-01 (Wave 1 baseline — _validate_firmware_version staticmethod landed)
    - 40-02 (Wave 2 baseline — _decode_id_frame thin wrapper + messages-block F401 closure landed)
  provides:
    - dead-code-free serial_comm.py (zero STATE_MACHINE_PREFIXES, zero read_line_bytes, zero orphan/dead comment fragments)
    - load-bearing GATE-1.8a invariant preserved (generator body byte-identical across all of Wave 3)
  affects:
    - SerialCommunicator surface API shrinks: read_line_bytes deleted (was never called)
    - module-level namespace shrinks: STATE_MACHINE_PREFIXES deleted (was empty list since Phase 8 W-01)
tech_stack:
  added: []
  patterns:
    - "Dead-code sweep with grep-confirmed zero callers (analog: Phase 38 D-14/D-16 read_data_block sweep)"
    - "Live-intent KEEP-block preservation (PREFIX_REGEX rationale + F401 re-export — both load-bearing for live behavior or test contract)"
    - "GATE-1.8a invariant verification via SHA256 byte-identity of _read_and_parse_lines generator body"
key_files:
  created: []
  modified:
    - firestarter_app/firestarter/serial_comm.py
decisions:
  - "D-10: STATE_MACHINE_PREFIXES module-level constant DELETED (empty since Phase 8 W-01; zero external imports per RESEARCH §3)"
  - "D-11: read_line_bytes method DELETED (zero callers in firestarter_app/firestarter/ AND firestarter_app/tests/ — re-verified defensively pre-deletion; W-04 MSG_DATA_CHUNK migration rendered it dead; same precedent as Phase 38 D-14)"
  - "D-12: three orphan/dead comment fragments DELETED (the W-01 dead-pointing comment inside _log_rurp_feedback; the orphan compile-regex header at module level; the commented-out json_data alternative inside send_json_command)"
  - "D-13: PREFIX_REGEX rationale block (rightmost-match + USB-CDC garbage-prefix workaround) KEPT verbatim — live intent"
  - "D-14: F401 re-export block (MAGIC_PREAMBLE, LogMessage, Response, _crc8_ccitt, _decode_param from frame_parser) KEPT verbatim — load-bearing for test_decoder.py back-compat contract (Phase 38 D-07)"
  - "GATE-1.8a generator body NOT entered — verified byte-identical by SHA256 across this wave (5552 bytes, 127 lines, hash unchanged)"
metrics:
  duration_seconds: 360
  completed: 2026-05-28
  tasks_completed: 2
  tasks_total: 2
  test_delta: "197 passed; 2 xfailed; 29 snapshots — UNCHANGED from Wave-2 baseline (pure deletion of dead code, no behavior change)"
  mypy_watermark: "15 errors in serial_comm.py (watermark 44; not raised; deletions can only lower the count per D-18)"
  serial_comm_lines_net: "+0 / -18 (5 from Task 40-03-01: 1 constant + 4 comment lines; 13 from Task 40-03-02: 9-line method + 1 orphan + 1 commented alt + 2 surrounding blank-line adjustments)"
  file_length: "710 lines (pre-Wave-3) → 692 lines (post-Wave-3)"
---

# Phase 40 Plan 03: SERIAL-01 — Dead-code Sweep Summary

**One-liner:** Deleted five confirmed-dead items from `serial_comm.py` (the `STATE_MACHINE_PREFIXES` empty-list constant, the zero-caller `read_line_bytes` method, and three orphan/dead comment fragments) while preserving the `PREFIX_REGEX` rationale block (D-13) and the F401 re-export block (D-14) — load-bearing for the Uno USB-CDC garbage-prefix workaround and the `test_decoder.py` back-compat contract respectively. The `_read_and_parse_lines` generator body was NOT entered; SHA256 byte-identity proven across the wave (GATE-1.8a invariant intact).

## What Shipped

### `firestarter_app/firestarter/serial_comm.py` (+0 / −18 lines, two atomic commits)

**Five deletions** (one constant, one method, three comment blocks):

**Task 40-03-01 (commit `c22476a`):**

1. **D-10 — `STATE_MACHINE_PREFIXES` module-level constant** (was line 88 pre-task):
   ```python
   STATE_MACHINE_PREFIXES = []  # W-01: state-machine acks now arrive as ID frames; ...  # noqa: E501
   ```
   Deleted. Empty list since Phase 8 W-01. Zero external imports — only self-references in `serial_comm.py` (the assignment + the dead comment block, both removed in this task).

2. **D-12 part 1 — W-01 dead comment block inside `_log_rurp_feedback`** (was lines 202–204 pre-task):
   ```python
   # W-01: STATE_MACHINE_PREFIXES is now empty; the old "Done" rewrite for
   # INIT/MAIN/END is removed — catalog format strings own the rendering for
   # ID frames. The conditional is kept but is a no-op ([] never matches).
   ```
   Deleted. The block described a conditional that does NOT exist below it (the method body proceeds directly from `message = response.message` into `level = logging.DEBUG`). After D-10 deletes the constant, the comment becomes a dangling reference.

**Task 40-03-02 (commit `9c165dc`):**

3. **D-11 — entire `read_line_bytes` method on `SerialCommunicator`** (was lines 158–166 + trailing blank line):
   ```python
   def read_line_bytes(self) -> Optional[bytes]:
       if not self.is_connected():
           raise SerialError("Not connected.")
       try:
           if self.connection.in_waiting > 0:
               return self.connection.readline()
           return None
       except serial.SerialException as e:
           raise SerialError(f"Serial error reading from {self.port_name}: {e}") from e
   ```
   Deleted. Re-verified zero callers defensively before deletion: `grep -rn "read_line_bytes" firestarter_app/firestarter/ firestarter_app/tests/` returned only the def itself (now zero). W-04 MSG_DATA_CHUNK migration replaced the line-oriented text read path with the binary ID-encoded frame path in `_read_and_parse_lines` — same precedent template as Phase 38 D-14's `read_data_block` deletion. CONCERNS.md:62 additionally documents the method's design flaw (returning `None` for "no data" conflates with "connection closed"), reinforcing the deletion call.

4. **D-12 part 2 — orphan compile-regex comment** (was line 59 pre-task):
   ```python
   # Compile regex for parsing prefixes once for efficiency
   ```
   Deleted. Was the header for a hoisted compile that has since moved to the rationale-documented block above `PREFIX_REGEX`. The orphan stood alone with no following code.

5. **D-12 part 3 — commented-out json_data alternative inside `send_json_command`** (was line 155 pre-task):
   ```python
   # json_data = json.dumps(command_dict)
   ```
   Deleted. The live call `json_data = json.dumps(command_dict, separators=(",", ":"))` immediately above it is unchanged (verified at line 152 post-Wave-3). The deletion used trailing-`$` regex anchor + leading-whitespace anchor to distinguish from the live call.

### Two KEEP-blocks preserved (D-13 + D-14)

- **D-13 — `PREFIX_REGEX` rationale block** (now lines 76–83 post-Wave-3, was lines 82–90 pre-phase). Documents the Uno USB-CDC garbage-prefix workaround (rightmost-match logic in `_parse_response_line`). Verified preserved by `grep -n "USB-CDC"` returning 2 hits (the rationale + the in-function comment that still describes the live behavior). Live intent.
- **D-14 — F401 re-export block** (now lines 47–53 post-Wave-3, was lines 42–53 pre-phase). The `from firestarter.frame_parser import (MAGIC_PREAMBLE, LogMessage, Response, _crc8_ccitt, _decode_param)  # noqa: F401` block. Load-bearing for `test_decoder.py`'s direct imports from `firestarter.serial_comm` (Phase 38 D-07 back-compat contract). Verified preserved by `grep -n "noqa: F401"` returning 1 hit.

### Two Wave-1/Wave-2 invariants preserved

- **`_decode_id_frame` thin wrapper from Wave 2** — present at line 203 post-Wave-3 (one-liner that delegates to `codec.decode_id_frame`). Not touched.
- **`_validate_firmware_version` staticmethod from Wave 1** — present at line 467 post-Wave-3. Not touched.

## Tasks & Commits

| Task     | Name                                                                          | Commit (firestarter_app submodule on v1.8-app-cleanup) | Files                          |
| -------- | ----------------------------------------------------------------------------- | ------------------------------------------------------ | ------------------------------ |
| 40-03-01 | Delete STATE_MACHINE_PREFIXES + W-01 dead comment (D-10 + D-12 part 1)         | `c22476a`                                              | `firestarter/serial_comm.py`  |
| 40-03-02 | Delete read_line_bytes + two orphan comments (D-11 + D-12 parts 2/3)           | `9c165dc`                                              | `firestarter/serial_comm.py`  |

Both commits on the `v1.8-app-cleanup` branch INSIDE the `firestarter_app` submodule (verified by `git rev-parse --abbrev-ref HEAD` in the submodule). The meta-repo at `/workspaces` was NOT touched by this executor: no `git add` from `/workspaces`, no submodule-pointer bump committed, no `.planning/STATE.md` / `.planning/ROADMAP.md` / `.planning/REQUIREMENTS.md` edits. The orchestrator owns those updates after this executor returns.

Task 40-03-02's commit body explicitly cites the **Phase 38 D-14 / D-16 dead-code-sweep precedent** and the **W-04 MSG_DATA_CHUNK migration rationale** as the basis for `read_line_bytes` deletion (per Plan 40-03 success_criteria #6).

## Verification

| Check                                                               | Command                                                                                                              | Result                                                                                                |
| ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| D-10 zero-check                                                     | `grep -n "STATE_MACHINE_PREFIXES" firestarter/serial_comm.py`                                                       | ZERO hits — pass                                                                                       |
| D-11 zero-check                                                     | `grep -n "read_line_bytes" firestarter/serial_comm.py`                                                              | ZERO hits — pass                                                                                       |
| D-11 no broken caller                                               | `grep -rn "read_line_bytes" firestarter_app/firestarter/ firestarter_app/tests/`                                    | ZERO hits — pass (defensively re-verified before deletion, also post)                                  |
| D-12 part 1 zero-check                                              | `grep -n "STATE_MACHINE_PREFIXES is now empty" firestarter/serial_comm.py`                                          | ZERO hits — pass                                                                                       |
| D-12 part 2 zero-check                                              | `grep -n "Compile regex for parsing prefixes" firestarter/serial_comm.py`                                           | ZERO hits — pass                                                                                       |
| D-12 part 3 zero-check                                              | `grep -nE "^[[:space:]]+# json_data = json.dumps\(command_dict\)$" firestarter/serial_comm.py`                       | ZERO hits — pass (live call at line 152 untouched, verified by grep)                                   |
| D-13 + D-14 KEEP-blocks survived                                    | `grep -n "PREFIX_REGEX\|noqa: F401\|USB-CDC" firestarter/serial_comm.py`                                            | 5 hits total (PREFIX_REGEX × 2, noqa: F401 × 1, USB-CDC × 2) — pass (≥ 3 required)                     |
| `_decode_id_frame` thin wrapper preserved (Wave-2)                  | `grep -n "def _decode_id_frame" firestarter/serial_comm.py`                                                         | line 203 — pass                                                                                        |
| `_validate_firmware_version` preserved (Wave-1)                     | `grep -n "def _validate_firmware_version" firestarter/serial_comm.py`                                               | line 467 — pass                                                                                        |
| Ruff clean                                                          | `ruff check firestarter/serial_comm.py`                                                                              | All checks passed!                                                                                     |
| Full suite                                                          | `/usr/local/bin/python -m pytest tests/`                                                                             | **197 passed + 2 xfailed + 29 snapshots** — exact Wave-2 baseline, zero regression                     |
| Mypy actually installed (cross-checked, not silent-OK fallback)     | `/usr/local/bin/python -m mypy --version`                                                                           | `mypy 2.1.0 (compiled: yes)` — confirmed real toolchain                                                |
| Mypy watermark not raised                                           | `/usr/local/bin/python -m mypy firestarter/serial_comm.py 2>&1 \| tail -1`                                          | 15 errors in serial_comm.py / 44 watermark — NOT raised (deletions can only lower the count per D-18) |
| **GATE-1.8a generator-body byte-identity**                          | SHA256 of `_read_and_parse_lines` body pre- vs post-Wave-3                                                          | **IDENTICAL** — see proof section below                                                                |
| File length net change                                              | `wc -l firestarter/serial_comm.py`                                                                                  | 710 → 692 lines (−18)                                                                                  |
| Branch + commits                                                    | `git -C /workspaces/firestarter_app rev-parse --abbrev-ref HEAD && git log --oneline -4`                            | `v1.8-app-cleanup`, two new commits `9c165dc` + `c22476a` on top of Wave-2                            |
| Meta-repo NOT bumped                                                | `git -C /workspaces diff --cached --stat`                                                                            | empty index — no staged submodule-pointer bump from this executor                                      |
| `.planning/STATE.md` / `ROADMAP.md` / `REQUIREMENTS.md` not touched | `git -C /workspaces diff --cached -- .planning/STATE.md .planning/ROADMAP.md .planning/REQUIREMENTS.md`            | empty — pass (orchestrator owns these)                                                                 |

Cross-checked toolchain: `pytest 9.0.3` (implied by tail output format), `ruff 0.15.14` (env-resident), `mypy 2.1.0 (compiled: yes)`. The hardened-mypy-gate watermark check ran with mypy actually installed (`mypy --version` returned a real version, not the silent-OK fallback noted in the MEMORY's "firestarter_app python test env" entry).

## GATE-1.8a Generator-Body Byte-Identity Proof

The `_read_and_parse_lines` generator body at pre-Wave-3 HEAD (lines 225–351, anchored to commit `a5cbbcf` from Wave 2) and post-Wave-3 HEAD (lines 207–333, anchored to commit `9c165dc` from this wave) are **byte-identical**:

```
pre-Wave-3:  SHA256 8a61ab5416f411bd61c5b66cc47a091e6b23286c2d41a20d1b93cf1c973317aa  (5552 bytes, 127 lines)
post-Wave-3: SHA256 8a61ab5416f411bd61c5b66cc47a091e6b23286c2d41a20d1b93cf1c973317aa  (5552 bytes, 127 lines)
```

Verified via a small Python helper that slices the file from `def _read_and_parse_lines` to the next top-level class-method `def `, then hashes the slice. The hash matches exactly. The line-number range shifted (225..351 → 207..333) because the 18 deletions in this wave all happened ABOVE the generator def — the body CONTENT (each character of each line) is unchanged.

This is the load-bearing proof for GATE-1.8a (Wave 4 will mark the generator with a `# DO NOT MODIFY` block ABOVE the def line; the body itself stays byte-identical across all of Phase 40, which keeps the Phase 26 baseline binaries at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` valid against the read path).

## Deviations from Plan

**None** — plan executed exactly as written. Both tasks landed in the planned atomic order, each as its own commit; both verify-blocks passed without auto-fix; both KEEP-blocks survived verbatim by grep; the GATE-1.8a SHA256 proof matched on the first run.

The Wave-2 SUMMARY noted one Rule-3 auto-fix (a stray blank line absorbed by an Edit), but Wave 3 had no analogous issue: each Edit used surrounding-context anchors (the live `json_data = json.dumps(..., separators=...)` line, the `PREFIX_REGEX = re.compile(...)` line, the `message = response.message` line) that uniquely identified the deletion regions without affecting nearby blank-line conventions. Ruff stayed clean throughout.

## Known Stubs

None. All five deletions are pure-removal: no replacement code is needed because every deleted item was already dead or orphaned. `STATE_MACHINE_PREFIXES` was an empty list, `read_line_bytes` had zero callers, and the three comment fragments were either pointing at deleted symbols (D-12 part 1) or describing dead code paths (D-12 parts 2 + 3).

## Threat Flags

None. This wave deletes only dead code from `serial_comm.py`; no new network endpoints, auth paths, file access patterns, or schema changes at trust boundaries. Threat register entries T-40-05 (accidental KEEP-block deletion) and T-40-06 (`read_line_bytes` deletion breaking a missed caller) were both `mitigate` dispositions and both mitigations held: PREFIX_REGEX + F401 KEEP-block greps confirmed survival; defensive pre-deletion grep + full-suite pass confirmed zero broken callers.

## Self-Check: PASSED

- File modified: `firestarter_app/firestarter/serial_comm.py` — FOUND (both tasks touched it)
- Commit `c22476a` (Task 40-03-01) — FOUND in `git log --all` of `firestarter_app` submodule on `v1.8-app-cleanup`
- Commit `9c165dc` (Task 40-03-02) — FOUND in `git log --all` of `firestarter_app` submodule on `v1.8-app-cleanup`
- Both commits on branch `v1.8-app-cleanup` inside the `firestarter_app` submodule — confirmed by `git rev-parse --abbrev-ref HEAD`
- Meta-repo `/workspaces` has no staged changes from the executor: `git diff --cached --stat` empty; no submodule-pointer bump committed
- `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md` untouched by this executor (orchestrator owns those)
- SUMMARY.md written to `/workspaces/.planning/phases/40-serial-transport-restructure/40-03-SUMMARY.md` (this file) and NOT committed by the executor — the orchestrator will commit it to the meta-repo together with STATE/ROADMAP updates after the return
- GATE-1.8a generator-body byte-identity verified: pre- and post-Wave-3 SHA256 both `8a61ab5416f411bd61c5b66cc47a091e6b23286c2d41a20d1b93cf1c973317aa`
- Wave 2 baseline preserved: 197 passed + 2 xfailed + 29 snapshots, mypy 15-errors / 44-watermark not raised, ruff clean

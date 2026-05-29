---
phase: 40-serial-transport-restructure
plan: 02
subsystem: serial / frame-decode
tags: [serial, codec, frame-decode, thin-wrapper, refactor]
requirements: [SERIAL-01]
dependency_graph:
  requires:
    - 40-01 (Wave 1 baseline)
    - codec.format_message (pre-existing)
    - frame_parser.LogMessage + _crc8_ccitt (pre-existing leaf module)
    - messages.CATALOG + SEVERITY_LABEL (pre-existing)
  provides:
    - codec.decode_id_frame free function (callable without a SerialCommunicator)
    - SerialCommunicator._decode_id_frame thin wrapper (test API surface preserved)
  affects:
    - SerialCommunicator._decode_id_frame (body removed; signature unchanged)
    - codec.py import block (4 new symbols added; "no new import edges" claim corrected)
tech_stack:
  added: []
  patterns:
    - "Free function in codec.py (analog: codec.format_message)"
    - "Thin-wrapper method (analog: Phase 38 D-07 F401 re-export block — same test_decoder.py back-compat rationale)"
    - "Same-task F401 closure (delete dead imports in the same commit that creates them — no `# noqa: F401`, no deferral)"
key_files:
  created: []
  modified:
    - firestarter_app/firestarter/codec.py
    - firestarter_app/firestarter/serial_comm.py
decisions:
  - "D-06: _decode_id_frame body migrates VERBATIM to codec.decode_id_frame; thin one-line wrapper stays on SerialCommunicator (load-bearing for GATE-1.8a + test_decoder.py byte-identity)"
  - "D-07: codec.py is the natural home for frame-decode orchestration (closes Phase 38 D-06's deferred disposition)"
  - "D-08: docstring opens with 'Read-path-adjacent — behavior preserved verbatim ... GATE-1.8d' breadcrumb (soft tripwire)"
  - "D-09: _log_rurp_feedback + _parse_response_line stay on SerialCommunicator (text-line transport, not codec charter)"
  - "RESEARCH §6 correction: 4 NEW imports added to codec.py (CATALOG, SEVERITY_LABEL from messages; LogMessage, _crc8_ccitt from frame_parser). CONTEXT.md's 'no new import edges' was inaccurate; planner scheduled them explicitly."
  - "Ruff F401 closure: messages-block (CATALOG, MSG_DATA_CHUNK, SEVERITY_LABEL) deleted in the SAME task that creates the F401 fallout — no `# noqa`, no future cleanup task."
metrics:
  duration_seconds: 239
  completed: 2026-05-28
  tasks_completed: 2
  tasks_total: 2
  test_delta: "197 passed; 2 xfailed; 29 snapshots — unchanged from Wave-1 baseline (pure refactor, no test count change)"
  mypy_watermark: "41 errors (unchanged; watermark 44)"
  serial_comm_lines_net: "+2 / -113 (thin wrapper replaces ~95-line body + 13-line docstring + 5-line messages-block)"
---

# Phase 40 Plan 02: SERIAL-01 — `_decode_id_frame` Extraction to codec.decode_id_frame Summary

**One-liner:** Extracted the body of `SerialCommunicator._decode_id_frame` verbatim to a new free function `codec.decode_id_frame(frame_len, body) -> Optional[LogMessage]`, replaced the method with a 3-line thin wrapper, and deleted the now-dead `(CATALOG, MSG_DATA_CHUNK, SEVERITY_LABEL)` messages-block imports from `serial_comm.py` — all while keeping the `_read_and_parse_lines` generator body byte-identical (GATE-1.8a) and `test_decoder.py` unchanged (4/4 call sites pass via the thin wrapper).

## What Shipped

### `firestarter_app/firestarter/codec.py` (+120 / -1 lines, Task 40-02-01)

**Added** 4 new imports per RESEARCH §6 correction — codec.py already imported from both `frame_parser` and `messages`, but the 4 symbols below were missing:

```python
import logging
...
from firestarter.frame_parser import LogMessage, _crc8_ccitt, _decode_param  # +LogMessage, +_crc8_ccitt
from firestarter.messages import (
    CATALOG,           # +
    DBG_CMD,
    DEBUG_CATALOG,
    MSG_DATA_CHUNK,
    ...
    MSG_OK_REV,
    SEVERITY_LABEL,    # +
)

logger = logging.getLogger("Codec")  # +
```

Also added `import logging` and the module-level `logger = logging.getLogger("Codec")` (not `"SerialComm"` — future log scoping is correct). `struct` was already imported (used in `format_message`'s DBG sub-render).

**Added** `decode_id_frame` after `format_message` (per PATTERNS placement note — keep `format_message` first):

```python
def decode_id_frame(frame_len: int, body: bytes) -> Optional[LogMessage]:
    """
    Read-path-adjacent — behavior preserved verbatim from serial_comm.py per
    GATE-1.8d. Do not refactor without re-validating Phase 26 baseline binaries.

    Decode an ID-encoded wire frame body (the bytes between the length
    byte and the trailing 0x0A re-sync anchor).
    ...
    """
    # [~95-line body migrated VERBATIM from serial_comm.py:239-334]
```

Body migrated verbatim from `serial_comm.py` lines 239–334 — same CRC check, same `CATALOG.get(msg_id)` lookup, same `wire_format=='id_frame'` WR-03 gate, same fixed-width shape check, same param-decode loop, same MSG_DATA_CHUNK payload extraction, same `SEVERITY_LABEL` lookup, same `LogMessage` return shape. The only mechanical change is the call site `codec.format_message(msg_id, values, entry)` becomes a local `format_message(msg_id, values, entry)` call (no `codec.` prefix) because we are now inside `codec.py`.

D-08 breadcrumb: the docstring's first paragraph is `"Read-path-adjacent — behavior preserved verbatim from serial_comm.py per GATE-1.8d. Do not refactor without re-validating Phase 26 baseline binaries."` — a soft tripwire for future Claude sessions.

### `firestarter_app/firestarter/serial_comm.py` (+2 / -113 lines, Task 40-02-02)

**Replaced** the `_decode_id_frame` method body (signature unchanged):

```python
def _decode_id_frame(self, frame_len: int, body: bytes) -> Optional[LogMessage]:
    """Compatibility wrapper — see codec.decode_id_frame."""
    return codec.decode_id_frame(frame_len, body)
```

Signature is byte-identical to the pre-Wave-2 declaration (`(self, frame_len: int, body: bytes) -> Optional[LogMessage]`). The four `test_decoder.py` keyword-arg call sites at lines 85, 150, 235, 308 (`comm._decode_id_frame(frame_len=..., body=...)`) resolve unchanged via the wrapper. The generator body's call site at the now-renumbered line 325 (`decoded = self._decode_id_frame(frame_len, body)`) is byte-identical to its pre-Wave-2 content.

**Deleted** the messages-block import (lines 54–58 of pre-Wave-2 HEAD):

```python
# DELETED in this commit:
# from firestarter.messages import (
#     CATALOG,
#     MSG_DATA_CHUNK,
#     SEVERITY_LABEL,
# )
```

Post-Wave-2-01, all three symbols become orphaned in `serial_comm.py`:
- `CATALOG` at former line 258 — gone (migrated to codec).
- `MSG_DATA_CHUNK` at former lines 309, 321 (comments), 325 (code) — the code reference (line 325) is gone; one comment-context reference at line 327 in the generator body survives (ring-fenced; comments don't trigger F401).
- `SEVERITY_LABEL` at former line 331 — gone.

`grep -n "CATALOG\|MSG_DATA_CHUNK\|SEVERITY_LABEL" firestarter/serial_comm.py` post-deletion shows ONE hit at line 327 (`# Propagate raw-bytes payload for MSG_DATA_CHUNK (W-04);` — inside the generator body comment, byte-identical to pre-Wave-2). Ruff (`select=["E","F","I","UP"]`, no per-file-ignores, no F401 ignore) stays clean — F401 only flags imports, not comments. Closure done in the same commit as the body migration; no `# noqa: F401`, no deferral.

## Tasks & Commits

| Task | Name | Commit (firestarter_app submodule on v1.8-app-cleanup) | Files |
|------|------|--------------------------------------------------------|-------|
| 40-02-01 | Add `decode_id_frame` free function to `codec.py` with 4 new imports (D-06/D-07/D-08 + RESEARCH §6) | `7d34233` `feat(40-02-01): add decode_id_frame free function to codec.py` | `firestarter/codec.py` |
| 40-02-02 | Replace `_decode_id_frame` body with thin wrapper + delete dead messages imports (D-06/D-09 + ruff F401 closure) | `a5cbbcf` `refactor(40-02-02): replace _decode_id_frame body with codec wrapper; delete dead messages imports` | `firestarter/serial_comm.py` |

Both commits on the `v1.8-app-cleanup` branch INSIDE the `firestarter_app` submodule. The meta-repo at `/workspaces` was NOT touched by the executor — no submodule-pointer bumps, no `.planning/STATE.md` / `.planning/ROADMAP.md` / `.planning/REQUIREMENTS.md` edits. The orchestrator handles those after this executor returns.

## Verification

| Check | Command | Result |
|---|---|---|
| Smoke import + call | `python -c "from firestarter.codec import decode_id_frame; ..."` | OK — returns `LogMessage(severity='OK', text='Ready', id=1, payload=None)` for `(2, b'\x01\x07')` |
| Thin wrapper smoke | `python -c "from firestarter.serial_comm import SerialCommunicator; c = SerialCommunicator.__new__(...); c._decode_id_frame(2, b'\x01\x07')"` | OK — wrapper resolves; same `LogMessage` returned |
| `test_decoder.py` | `pytest tests/test_decoder.py -v` | **32/32 pass UNCHANGED** (file byte-identical; `git diff HEAD -- tests/test_decoder.py` → 0 lines) |
| `test_codec.py` | `pytest tests/test_codec.py -v` | 10/10 pass |
| Full suite | `pytest tests/` | **197 passed + 2 xfailed + 29 snapshots** — exact Wave-1 baseline (pure refactor, no test count change) |
| Ruff clean on both files | `ruff check firestarter/serial_comm.py firestarter/codec.py` | clean (F401 closed) |
| Dead messages-block gone | `grep -c "^from firestarter.messages import" firestarter/serial_comm.py` | `0` |
| `codec.` import alias preserved | `grep -c "import firestarter.codec as codec" firestarter/serial_comm.py` | `1` (line 22, the thin wrapper depends on it) |
| Decoder breadcrumb | `grep -A3 "def decode_id_frame" firestarter/codec.py \| grep "GATE-1.8d"` | found (D-08 satisfied) |
| Thin wrapper present | `grep -n "def _decode_id_frame" firestarter/serial_comm.py` | one hit (line 221) |
| Thin wrapper length | `awk '/def _decode_id_frame/,/return codec.decode_id_frame/' firestarter/serial_comm.py \| wc -l` | 3 (def + docstring + return) |
| Mypy watermark | `python tools/check_mypy_watermark.py` | 41 errors / watermark 44 — **NOT raised** |
| **GATE-1.8a generator-body byte-identity** | `git show HEAD~2:firestarter/serial_comm.py` vs `HEAD` `_read_and_parse_lines` slice | **byte-identical (127/127 lines match)** — proven via Python difflib |
| Generator call site preserved | `grep -n "self._decode_id_frame(frame_len, body)" firestarter/serial_comm.py` | one hit (line 325, byte-identical content to pre-Wave-2 line 436) |
| File-shrink net | `git diff HEAD~2 HEAD -- firestarter/serial_comm.py` | `+2 / -113` lines (thin wrapper insertion + ~95 body + 13 docstring + 5 messages-block deletion) |

Cross-checked toolchain: `pytest 9.0.3`, `ruff 0.15.14`, `mypy 2.1.0 (compiled)`. The hardened-mypy-gate watermark check ran with mypy actually installed (not the silent-OK fallback) — confirmed 41 errors below the watermark of 44.

## GATE-1.8a Generator-Body Byte-Identity Proof

The `_read_and_parse_lines` generator body at pre-Wave-2 HEAD (lines 336–461) and post-Wave-2 HEAD (lines 327–452 after renumbering due to the ~111-line shrink above) are **byte-identical line-by-line**. Verified via:

```python
pre  = subprocess.check_output(['git', 'show', 'HEAD~2:firestarter/serial_comm.py']).decode()
post = subprocess.check_output(['git', 'show', 'HEAD:firestarter/serial_comm.py']).decode()
# Slice the lines from `def _read_and_parse_lines` to the next `def ` in the class.
assert slice_generator(pre) == slice_generator(post)  # PASSED
# Pre-Wave-2 generator span: 127 lines
# Post-Wave-2 generator span: 127 lines
# Byte-identical: True
```

This is the load-bearing proof for GATE-1.8a / GATE-1.8d. The Phase 26 baseline binaries at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` were captured against the EXACT pre-Wave-2 generator body, and the post-Wave-2 body is the same byte sequence. The v1.9 RCA territory is preserved unchanged.

(The line-number positions in the file shift — pre-Wave-2 the generator was at line 336, post-Wave-2 it is at line 327 — but the CONTENT of each line is identical. Wave 4 will add the `# DO NOT MODIFY` comment block IMMEDIATELY ABOVE the `def` line; the body itself stays byte-identical across all of Phase 40.)

## Deviations from Plan

**One minor auto-fix (Rule 3 — blocking issue introduced by my own edit):**

When I deleted the 5-line messages-block import at lines 54–58, the deletion absorbed the trailing blank line that previously separated the F401 re-export block from `logger = logging.getLogger("SerialComm")`. Ruff (`I001`) flagged the resulting import block as "un-sorted or un-formatted" because the F401 re-export `from firestarter.frame_parser import (...)` block was no longer separated from `logger =` by a blank line. **Fix:** restored one blank line between the closing `)` of the F401 re-export block and `logger = ...`. This is the byte-exact formatting state the file would have been in had the messages-block deletion been done by a human editor — no semantic change, no behavior change.

Tracked here for transparency. Plan executed as written otherwise — both tasks landed in the recommended atomic order, and the load-bearing invariants (`test_decoder.py` byte-identical, generator body byte-identical, ruff clean on both files, full-suite at Wave-1 baseline) held throughout.

## Known Stubs

None. `decode_id_frame` is wired into:
- `SerialCommunicator._decode_id_frame` (thin wrapper) → consumed by `_read_and_parse_lines` generator at line 325 (production path).
- `test_decoder.py` 4 call sites (test path, unchanged).

The function is fully implemented; no placeholders, no TODOs, no mock data sources.

## Self-Check: PASSED

- File modified: `firestarter_app/firestarter/codec.py` — FOUND (Task 40-02-01)
- File modified: `firestarter_app/firestarter/serial_comm.py` — FOUND (Task 40-02-02)
- Commit `7d34233` (Task 40-02-01) — FOUND in `git log --all` of submodule
- Commit `a5cbbcf` (Task 40-02-02) — FOUND in `git log --all` of submodule
- Both commits on branch `v1.8-app-cleanup` inside the `firestarter_app` submodule
- Meta-repo `/workspaces` has no staged changes from the executor; no submodule-pointer bump; `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md` untouched
- SUMMARY.md written to `/workspaces/.planning/phases/40-serial-transport-restructure/40-02-SUMMARY.md` (this file) and NOT committed by the executor — the orchestrator will commit it to the meta-repo together with STATE/ROADMAP updates after the return

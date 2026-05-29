# Phase 40: Serial / Transport Restructure - Context

**Gathered:** 2026-05-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Reduce `serial_comm.py` to **transport + dispatch only**, after Phase 38's
extractions left the package-coupled orchestration in place. Three deliverables,
mapped to SERIAL-01..03 (all GATE-1.8 — wire byte-identical, CLI surface
preserved, **read path ring-fenced**):

- **SERIAL-01:** `SerialCommunicator` owns only socket lifecycle (`__init__` /
  `is_connected` / `disconnect`), the `send_*` family, `get_response`,
  `expect_ack`, `consume_remaining_input`, port discovery
  (`find_and_connect` / `_probe_port` / `_list_potential_ports`), and the
  ring-fenced `_read_and_parse_lines` generator. Frame-decode orchestration
  (`_decode_id_frame`) is **delegated to a free function in `codec.py`** with a
  thin one-line method wrapper preserved on the class so
  `tests/test_decoder.py` calls work unchanged. `STATE_MACHINE_PREFIXES` empty-
  list dead code is deleted; the dead-code sweep also kills `read_line_bytes`
  (zero callers) + three orphan/dead comment fragments (D-12).
- **SERIAL-02:** `SerialCommunicator._validate_firmware_version(version_str,
  allow_pre_v12=False) -> None` is a **`@staticmethod`** that owns ALL
  version-guard logic (major-version pre-v1.2 reject + 2.0.0 floor + dev-bypass
  branch); `_probe_port` reads the `FIRESTARTER_DEV_ALLOW_PRE_V12` env var and
  passes the boolean in. New `tests/test_fw_version_guard.py` covers the guard
  directly without a fake serial. The existing `_is_version_sufficient`
  staticmethod stays as the internal "≥ 2.0.0" helper.
- **SERIAL-03:** `_read_and_parse_lines` carries a high-visibility `# DO NOT
  MODIFY — v1.9 RCA territory (GATE-1.8d)` comment block **immediately above
  the `def`** + a one-line marker in the docstring; the generator body stays
  byte-identical (verified by `test_decoder.py` passing unchanged). All
  **public** `SerialCommunicator` methods carry type-annotated signatures in
  the legacy `Optional[X]` / `List[X]` / `Tuple[X,Y]` style (Phase 37 D-08
  locked py39 floor).

Requirements: SERIAL-01, SERIAL-02, SERIAL-03 (full text in
`.planning/REQUIREMENTS.md` lines 53–57). Standing contract: GATE-1.8 (a–e),
esp. **(a)** wire byte-identical (`_read_and_parse_lines` generator body
preserved), **(b)** CLI surface preserved (firmware-outdated error messages
unchanged for the operator path; Phase 36 snapshots stay green), **(c)** no
constants touched (parity test untouched), **(d)** read path ring-fenced
(the generator body is THE thing being ring-fence-marked), **(e)** suite green +
entry point runs.

**Depends on:** Phase 38 — `frame_parser` / `codec` / `exceptions` already
exist; D-06 deferred `_decode_id_frame`'s final disposition to this phase.
Phase 39 not strictly required but preferred (it shipped first in the
sequential v1.8 chain).
**Unblocks:** Phase 41 (Click handlers consume a stable `SerialCommunicator`
public surface + clean `_validate_firmware_version` testable hook); Phase 42
(mypy strict overrides can be raised on `serial_comm.py` once type hints land).

</domain>

<decisions>
## Implementation Decisions

The operator selected the "you recommend" path (2026-05-28) — same delegate-
all pattern as Phases 37 and 38 (Phase 39 was the exception where they weighed
in directly). The recommendations below are **locked**. Each resolves a real
choice grounded in scout evidence + prior-phase precedent. Operator's standing
style across Phases 37–39: lean, behavior-preserving, minimize churn, preserve
git blame, document SC deviations with rationale rather than escalate.

### SERIAL-02 — `_validate_firmware_version` signature & scope
- **D-01:** **`@staticmethod` with two arguments** —
  `_validate_firmware_version(version_str: str, allow_pre_v12: bool = False)
  -> None`. Owns the **complete version-guard policy**: parse major (try
  `int(version_str.split(".")[0])`, ValueError/IndexError → 0); if `major < 3`
  AND `not allow_pre_v12` → raise `FirmwareOutdatedError` (the existing pre-
  v1.2 message verbatim); else if `not _is_version_sufficient(version_str,
  "2.0.0")` → raise `FirmwareOutdatedError` (the existing "outdated" message
  verbatim). Returns `None` implicitly on success.
- **D-02:** **Env-var I/O stays in `_probe_port`.** The orchestrator reads
  `os.environ.get("FIRESTARTER_DEV_ALLOW_PRE_V12") == "1"` and passes the
  boolean. Rationale: env reads are I/O policy, not version-guard policy —
  keeping the guard pure means unit tests don't need to mock the environment.
  The current code's coupling (`major < 3 and os.environ.get(...) != "1"`) is
  preserved byte-identically by the new pattern `if major < 3 and not
  allow_pre_v12` after the orchestrator reads the env.
- **D-03:** **`_is_version_sufficient` stays as the internal "≥ 2.0.0" helper.**
  Already a `@staticmethod` (`serial_comm.py:573-593`), already covered by the
  Phase 36 safety net via the integration path. Reusing it inside
  `_validate_firmware_version` avoids re-implementing the version-tuple compare;
  the new test file can also call it directly to fence its edge cases (single-
  segment version "3", trailing alpha "3.0.0-dev", empty string).
- **D-04:** **`_probe_port`'s "Could not parse FW message" path STAYS in
  `_probe_port`.** It is about parsing a serial-protocol text message
  (`re.search(r"FW:\s*([\d.x]+)", fw_msg)`) — that's transport concern, NOT
  version-guard concern. The current `IndexError`/`AttributeError` and missing-
  match paths keep raising `FirmwareOutdatedError` from `_probe_port` with the
  existing messages.
- **D-05:** **`tests/test_fw_version_guard.py`** covers the guard directly,
  matrix-style: `"3.0.0"` / `"3.5.2"` / `"3.0.0-dev"` (alpha suffix path —
  `int("3")` works) / `"3"` (single segment) → return None; `"2.9.9"` / `"1.0.0"`
  / `"abc"` (parse-fails-to-0) / `""` → `FirmwareOutdatedError`; `"2.9.9"` with
  `allow_pre_v12=True` → still raises (because of 2.0.0 floor — confirm via
  message content); `"3.0.0"` with `allow_pre_v12=False` → passes; `"1.0.0"`
  with `allow_pre_v12=True` → passes (env-var bypasses pre-v1.2; 2.0.0 floor
  also bypassed because `1.0.0 < 2.0.0` is True but the first branch is
  skipped, so we fall to `_is_version_sufficient("1.0.0","2.0.0") == False` →
  raises). Document the env-var semantic explicitly: **`allow_pre_v12=True`
  bypasses ONLY the `major < 3` check, NOT the 2.0.0 floor** — matches today's
  behavior where the env-var only sits inside the `if (major < 3 and ... != "1")`
  branch, not around the `_is_version_sufficient` branch. (If the planner finds
  the production code disagrees, that becomes a documented behavioral question
  for the operator — but scout reading says today's code DOES re-check the
  2.0.0 floor even when env-var is set.)

### SERIAL-01 — `_decode_id_frame` final disposition
- **D-06:** **Extract to a free function in `codec.py`** —
  `def decode_id_frame(frame_len: int, body: bytes) -> Optional[LogMessage]`.
  Keep a **thin one-line method wrapper** on `SerialCommunicator`:
  `def _decode_id_frame(self, frame_len, body): return
  codec.decode_id_frame(frame_len, body)`. The generator body's call site
  (`self._decode_id_frame(frame_len, body)`, line 436) stays
  **byte-identical** — only the method's body changes. `test_decoder.py`'s
  four `comm._decode_id_frame(frame_len=..., body=...)` calls (lines 85, 150,
  235, 308) pass **unchanged** (SC#3).
- **D-07:** Why extract (vs. keep-as-method per Phase 38 D-06's "package-
  coupled orchestrator" reading): SC#1 reads "frame-decode and message-format
  concerns are delegated to frame_parser + codec imports". `_decode_id_frame`
  IS frame-decode orchestration. Keeping it as a method satisfies SC#1 only on
  a stretched reading. **codec.py already imports** `CATALOG` /
  `MSG_DATA_CHUNK` / `SEVERITY_LABEL` from `messages.py` and the `_decode_param`
  primitive from `frame_parser` — natural home, no new import edges. The
  extraction is mechanically trivial (cut/paste/swap `self._decode_id_frame` →
  `codec.decode_id_frame`) and the wrapper preserves the test API exactly.
  **Documented deviation from Phase 38 D-06** — flagged so the plan-checker
  reads it as the deferred decision Phase 38 explicitly punted here, not a
  contradiction.
- **D-08:** **Add a breadcrumb to the new `codec.decode_id_frame` docstring:**
  `"Read-path-adjacent — behavior preserved verbatim from serial_comm.py per
  GATE-1.8d. Do not refactor without re-validating Phase 26 baseline binaries."`
  Not a hard ring-fence (those are reserved for the generator body per Phase 38
  D-09), but a future-Claude tripwire.
- **D-09:** **`_log_rurp_feedback` and `_parse_response_line` STAY put** on
  `SerialCommunicator` — they are text-line transport (the non-binary path
  through the generator) and don't fit codec's "message rendering" charter or
  frame_parser's "stdlib-only" charter. Their bodies are unchanged.

### SERIAL-01 — Dead-code sweep extent
- **D-10:** **DELETE `STATE_MACHINE_PREFIXES`** (line 93) — SC#1 explicit;
  empty list since Phase 8 W-01; no external imports (grep-confirmed).
- **D-11:** **DELETE `read_line_bytes`** (lines 164–172) — **zero callers**
  (grep across `firestarter/` and `tests/`). Extension of Phase 38 D-14
  (`read_data_block` deletion) pattern: confirmed-dead transport helper, killed
  in the same pass that owns the module. Commit message cites the W-04
  MSG_DATA_CHUNK migration that made it dead (same as Phase 38 D-14's
  rationale; the `_read_and_parse_lines` generator obsoleted any need for
  unrelated raw-line reads).
- **D-12:** **DELETE three orphan/dead comment fragments** — Phase 38 D-16
  pattern (remove confirmed-dead comments; keep live-intent comments):
  - Line 64: `# Compile regex for parsing prefixes once for efficiency` —
    orphan (no following code; was a header for a hoisted compile that moved).
  - Line 161: `# json_data = json.dumps(command_dict)` — confirmed-dead
    commented-out alternative.
  - Lines 207–209 in `_log_rurp_feedback`: the `# W-01: STATE_MACHINE_PREFIXES
    is now empty; the old "Done" rewrite for INIT/MAIN/END is removed — catalog
    format strings own the rendering for ID frames. The conditional is kept
    but is a no-op ([] never matches).` block — becomes dead-pointing once D-10
    deletes the constant. Replace with: nothing (just delete; the `if not
    response or not response.type: return` early-exit already guards a
    no-message case, and the rest of the method is self-documenting).
- **D-13:** **KEEP the PREFIX_REGEX rationale block** (lines 82–90) — documents
  the **live** Uno USB-CDC garbage-prefix workaround intent (the rightmost-
  match logic depends on this rationale). Phase 38 D-16 precedent.
- **D-14:** **KEEP the F401 re-export comment block** (lines 42–47) — documents
  the **live** test_decoder.py back-compat re-export contract (Phase 38 D-07).
- **Documented deviation from SC#1's literal list** — SC#1 names only
  `STATE_MACHINE_PREFIXES`. D-11/D-12 extend the sweep to other confirmed-dead
  code found during scout, matching the Phase 38 D-14/D-16 pattern (same
  reviewer template). Flagged here so the plan-checker reads them as
  intentional, not missed-scope.

### SERIAL-03 — Ring-fence marker placement & scope
- **D-15:** **Comment block immediately above `def _read_and_parse_lines`:**
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
  ```
  Highest visibility — grep-friendly (`grep -n "DO NOT MODIFY"`), blame-
  friendly (visible on any blame line in the body), IDE-friendly (above the
  signature). The existing docstring stays as the algorithm explanation;
  prepend one line: `"""[ring-fenced — v1.9 RCA territory; see header
  comment] Always-on byte-stream reader..."""`.
- **D-16:** **Do NOT mark `_decode_id_frame`, `_parse_response_line`, or
  `_log_rurp_feedback`.** Phase 38 D-09 deliberately scoped the ring-fence to
  the generator body. Marking callees would create marker inflation (every
  callee transitively → every transport method) and dilutes the load-bearing
  signal. The Phase 36 + Phase 40 test suites are the structural-vs-behavioral
  safety net for those callees. The single exception is D-08's breadcrumb
  docstring on the new `codec.decode_id_frame` — a softer "read-path-adjacent"
  hint, not a hard ring-fence.

### SERIAL-03 — Type-hint scope & strictness
- **D-17:** **Public methods get type-annotated signatures, legacy syntax
  retained.** Per Phase 37 D-08 (py39 floor; `from __future__ import
  annotations` NOT adopted; `Optional[X]` / `List[X]` / `Tuple[X,Y]` legacy
  style — the existing `# noqa: UP006/UP035` markers in `serial_comm.py:16`
  stay). Methods that need hints added or completed:
  - `__init__(self, port: str, baud_rate: int = ..., timeout: float = ...) -> None`
  - `is_connected(self) -> bool` ✓
  - `send_bytes(self, data_bytes: bytes) -> int` ✓
  - `send_string(self, data_string: str, encoding: str = "ascii") -> int` ✓
  - `send_json_command(self, command_dict: dict) -> int` ✓
  - `_parse_response_line(self, line_bytes: bytes) -> Optional[Response]` ✓
  - `_log_rurp_feedback(self, response: Response) -> None` — add `-> None`
  - `_decode_id_frame(self, frame_len: int, body: bytes) -> Optional[LogMessage]` ✓
    (signature unchanged when body delegates to codec)
  - `_read_and_parse_lines(self, timeout: float) -> Generator[Response, None, None]` ✓
  - `get_response(self, timeout: float = ...) -> Response` ✓
  - `expect_ack(self, timeout: float = ...) -> Tuple[bool, Optional[str]]` ✓
  - `send_ack(self) -> None` — add `-> None`
  - `send_done(self) -> None` — add `-> None`
  - `consume_remaining_input(self, timeout: float = 0.5) -> None` — add `-> None`
  - `disconnect(self) -> None` — add `-> None`
  - `_log_command_details(self, command_dict: dict) -> None` — add `-> None`
  - `_list_potential_ports(preferred_port: Optional[str] = None) -> List[str]` ✓
  - `_is_version_sufficient(current_version_str: str, required_version_str: str) -> bool` ✓
  - `_validate_firmware_version(version_str: str, allow_pre_v12: bool = False) -> None` (NEW)
  - `_probe_port(port_name: str, baud_rate: int, command_to_send: dict, config_manager: ConfigManager) -> Optional["SerialCommunicator"]` ✓
  - `find_and_connect(cls, command_to_send: dict, config_manager: ConfigManager, preferred_port: Optional[str] = None, baud_rate: int = ...) -> "SerialCommunicator"` ✓

  Net: only ~6 small `-> None` returns + the new `_validate_firmware_version`
  signature. Touched modules must stay ruff/ruff-format clean and must not
  raise the mypy watermark.
- **D-18:** **mypy strict overrides addition is OUT of scope** —
  `[[tool.mypy.overrides]]` adding `firestarter.serial_comm` to the strict
  list is **Phase 42 ERR-02** territory ("those modules are mypy-clean under
  the configured strictness"). Phase 40 adds hints; Phase 42 raises the bar.
- **D-19:** **Module docstrings / function docstrings on public methods are
  OUT of scope** — that's **Phase 42 ERR-03** ("all public classes and methods
  in touched modules have docstrings"). Phase 40 touches signatures, not
  prose.

### Claude's Discretion
- The exact `_validate_firmware_version` error-message strings (keep them
  byte-identical to today's `_probe_port` raises — the operator-visible text
  is pinned by behavior, not by the new test surface).
- Whether `tests/test_fw_version_guard.py` lives next to `test_decoder.py` or
  in a new file (recommend new file per SC#2's named filename).
- Function ordering inside `codec.py` after `decode_id_frame` is added (keep
  the existing `format_message` first if convention favours alphabetical;
  follow Phase 38 D-08's codec.py pattern).
- The thin `_decode_id_frame` wrapper's docstring (could be `"""Compatibility
  wrapper — see codec.decode_id_frame."""`, could just inherit via no
  docstring; planner picks).
- Plan/wave decomposition. **Natural ordering** (dependency-safe; each its
  own atomic commit with full suite green before the next):
  1. **Wave 1** — Extract `_validate_firmware_version` as a `@staticmethod`
     + repoint `_probe_port` to call it with `allow_pre_v12=` from env +
     `tests/test_fw_version_guard.py` (SERIAL-02). Independent of D-06.
  2. **Wave 2** — Extract `_decode_id_frame` body to `codec.decode_id_frame`
     + leave the thin `SerialCommunicator._decode_id_frame` wrapper +
     codec docstring breadcrumb (D-06/D-07/D-08). `test_decoder.py` must
     pass unchanged.
  3. **Wave 3** — Dead-code sweep: delete `STATE_MACHINE_PREFIXES`,
     `read_line_bytes`, and the three comment fragments (D-10/D-11/D-12).
  4. **Wave 4** — Add the `# DO NOT MODIFY — v1.9 RCA territory` comment
     block + docstring marker on `_read_and_parse_lines` + close out the
     missing `-> None` return hints on the ~6 methods (D-15/D-17).

  Waves 3 and 4 can fold into one commit if the diff stays reviewable.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope & locked milestone decisions
- `.planning/ROADMAP.md` — Phase 40 detail (Goal + SC#1–SC#3, lines 166–177) +
  the v1.8 section + GATE-1.8 (a–e) standing gate (lines 23–34). **Note the
  documented deviations** above: D-07 (`_decode_id_frame` extraction reverses
  Phase 38 D-06's "keep as method" while honoring its "deferred to Phase 40"
  clause); D-11/D-12 (dead-code sweep extends SC#1's literal `STATE_MACHINE_PREFIXES`
  to `read_line_bytes` + three comment fragments per Phase 38 D-14/D-16
  pattern).
- `.planning/REQUIREMENTS.md` — SERIAL-01..SERIAL-03 (lines 53–57); GATE-1.8
  (a–e) (lines 12–20); Out-of-Scope table (firmware untouched, no protocol
  change, read-bug RCA itself is v1.9).
- `.planning/PROJECT.md` — "Current Milestone: v1.8" + "Scope decisions
  (locked 2026-05-27)" (lines 32–41): host-only, flat layout (preserve git
  blame), refactor-and-fix-bugs gate.

### Prior-phase context this phase builds on
- `.planning/phases/39-database-cleanup-chip-resolver/39-CONTEXT.md` —
  immediate predecessor; established the "documented SC deviation with
  rationale" precedent (D-06 there, multi-module sweep beyond the SC literal
  list); operator's pattern of weighing in on Phase 39's gray areas validates
  that this phase's "you recommend" delegation is the **norm**, not a default.
- `.planning/phases/38-low-risk-extractions/38-CONTEXT.md` — **D-06** kept
  `_decode_id_frame` in `serial_comm.py` and **explicitly deferred its
  disposition to Phase 40 SC#1** (this phase's D-06 closes that thread); D-09
  scoped GATE-1.8d to the generator body (this phase's D-16 honors that
  scope); D-14/D-16 dead-code-sweep patterns reused here (D-11/D-12); D-07
  back-compat re-export of `MAGIC_PREAMBLE` / `LogMessage` / `Response` /
  `_crc8_ccitt` / `_decode_param` from `serial_comm.py` for `test_decoder.py`
  is the precedent for D-06's thin method wrapper.
- `.planning/phases/37-tooling-baseline-ci-gate/37-CONTEXT.md` — **D-08**
  locked `target-version = "py39"` / `python_version = "3.9"`; modernization
  to `X | None` / `list[X]` / `tuple[X,Y]` was deferred. D-09 locked the ruff
  rule set (E/F/I + UP). The existing `# noqa: UP006` / `# noqa: UP035`
  markers in `serial_comm.py:16` (Optional/List/Tuple imports) stay.
- `.planning/phases/36-characterization-test-baseline/36-CONTEXT.md` — the
  Phase 36 safety net (162 passed + 2 xfail + 29 snapshots) that pins the
  bad-FW / outdated-FW operator-visible behavior; `test_decoder.py` is the
  load-bearing test for generator-body byte-identity (Wave 2 + Wave 4 must
  leave it untouched and green).

### Files this phase edits / creates (firestarter_app sub-repo, branch v1.8-app-cleanup)
- `firestarter_app/firestarter/serial_comm.py` — primary target:
  - DELETE `STATE_MACHINE_PREFIXES` (`:93`), `read_line_bytes` (`:164-172`),
    the orphan/dead comments at `:64`, `:161`, and `:207-209` (D-10/D-11/D-12).
  - REPLACE `_decode_id_frame` body (`:226-334`) with a 1-line delegation to
    `codec.decode_id_frame` (D-06). Signature + docstring header retained for
    test compat; long algorithm docstring migrates into `codec.py` with the
    extracted body.
  - INSERT `# DO NOT MODIFY — v1.9 RCA territory (GATE-1.8d)` comment block
    immediately above `def _read_and_parse_lines` (`:336`); prepend ring-fence
    marker to its docstring (D-15).
  - ADD `_validate_firmware_version(version_str: str, allow_pre_v12: bool =
    False) -> None` @staticmethod next to `_is_version_sufficient` (`:573`)
    (D-01).
  - REPLACE the inline major-check + 2.0.0-floor logic in `_probe_port`
    (`:638-686`) with: regex extract → env-var read → call
    `SerialCommunicator._validate_firmware_version(current_version,
    allow_pre_v12=...)` (D-02/D-04). The "Could not parse" raises stay in
    `_probe_port` (D-04).
  - ADD missing `-> None` return hints on the ~6 public methods listed in
    D-17 (no other signature changes).
- `firestarter_app/firestarter/codec.py` — ADD `decode_id_frame(frame_len:
  int, body: bytes) -> Optional[LogMessage]` free function carrying the body
  migrated from `serial_comm._decode_id_frame`, plus the read-path-adjacent
  breadcrumb docstring (D-06/D-08). Imports `_crc8_ccitt` and `_decode_param`
  from `firestarter.frame_parser` (already imports `frame_parser._decode_param`
  per Phase 38 D-08); imports `CATALOG`, `MSG_DATA_CHUNK`, `SEVERITY_LABEL`
  from `firestarter.messages` (already imports `CATALOG` per Phase 38 D-08).
- **NEW test:** `firestarter_app/tests/test_fw_version_guard.py` — matrix of
  version-string accept/reject + env-var-bypass cases per D-05.
- `firestarter_app/tests/test_decoder.py` — **MUST pass unchanged** (SC#3 +
  D-06). The four `comm._decode_id_frame(frame_len=..., body=...)` calls
  (`:85`, `:150`, `:235`, `:308`) resolve via the thin wrapper to
  `codec.decode_id_frame`.
- `firestarter_app/tests/test_characterization.py`,
  `firestarter_app/tests/test_serial_characterization.py` — Phase 36 surface;
  must stay green (GATE-1.8b: operator-visible firmware-outdated path
  unchanged).

### Do-not-touch
- `firestarter_app/firestarter/frame_parser.py` — stdlib + typing only
  (Phase 38 D-05); `decode_id_frame` cannot live here.
- `firestarter_app/firestarter/messages.py` — codegen target; do not edit.
- `firestarter_app/firestarter/constants.py` — no constant touched in
  Phase 40 (GATE-1.8c).
- The firmware sub-repo (`firestarter/`) — host-only milestone.

### App architecture (context)
- `firestarter_app/CLAUDE.md` — data flow (`serial_comm.py` is "serial
  protocol implementation (INIT/MAIN/END state machine)"; the
  `STATE_MACHINE_PREFIXES` deletion here is the last vestige of the pre-Phase-8
  prefix-based state machine — catalog format strings have owned the rendering
  since Phase 8 W-01).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`_is_version_sufficient`** (`serial_comm.py:573-593`) — already a
  `@staticmethod`; reusable as the internal "≥ 2.0.0" tuple-compare helper
  inside `_validate_firmware_version` (D-03). No new compare logic needed.
- **Phase 36 safety net** (162 passed + 2 xfail + 29 syrupy snapshots) — the
  per-change acceptance signal; firmware-outdated path snapshots pin the
  operator-visible behavior the version-guard extraction must preserve.
- **codec.py existing imports** (`CATALOG`, `MSG_DATA_CHUNK`, `SEVERITY_LABEL`
  from messages.py; `_decode_param`, `_crc8_ccitt` from frame_parser via
  Phase 38 D-08) — `decode_id_frame` migrates with **zero new import edges**.
- **`test_decoder.py`** — already exercises `comm._decode_id_frame(frame_len,
  body)` directly (4 sites). The thin method wrapper on `SerialCommunicator`
  keeps those calls working unchanged (D-06).
- **Phase 38 D-07 re-export pattern** (`from firestarter.frame_parser import
  MAGIC_PREAMBLE, LogMessage, Response, _crc8_ccitt, _decode_param  # noqa:
  F401`) — direct precedent for the thin `_decode_id_frame` method wrapper
  here (same "test_decoder.py back-compat" rationale).

### Established Patterns
- **Generator body byte-identical** is the Phase 36 + Phase 38 + Phase 40
  load-bearing invariant for GATE-1.8a/d. The Wave 2 + Wave 4 commits each
  run `pytest tests/test_decoder.py -v` plus the full suite to prove it.
- **Flat layout** (PROJECT.md) — `codec.py` gains a new free function;
  no new files (other than the test).
- **Dead-code-sweep pattern** (Phase 38 D-14/D-15/D-16) — confirmed-dead
  by grep + read; document the deviation from SC#1's literal list; ship in
  its own wave.
- **`Optional[X]` / `List[X]` / `Tuple[X,Y]`** legacy style is the locked
  in-tree convention (Phase 37 D-08); `# noqa: UP006` / `UP035` markers
  preserved at `serial_comm.py:16`. Don't modernize.

### Integration Points
- **`_validate_firmware_version`** becomes the single chokepoint between the
  serial-text version string and the FirmwareOutdatedError raise — Phase 41
  Click handlers can reuse it directly (no need to re-implement the guard at
  the CLI boundary).
- **`codec.decode_id_frame`** becomes the single chokepoint for binary frame
  → `LogMessage`. Once it's a free function, Phase 41 / Phase 42 / future
  test code can exercise it without a `SerialCommunicator` instance.
- **`_read_and_parse_lines` generator body** stays the v1.9 RCA bridge:
  baseline binaries at `.planning/v1.6/consistency-check-runs/W27C512-
  leonardo-20260526-*-v2*/` were captured against this exact loop; D-15's
  comment block is the future-Claude tripwire.

</code_context>

<specifics>
## Specific Ideas

- Operator continues the Phase 37/38 "you recommend" delegation; Phase 39's
  weigh-in-on-all-four was the exception, not the rule. The two SC deviations
  documented here (D-07 reversing Phase 38 D-06; D-11/D-12 extending SC#1's
  dead-code list) are exactly the kind of call the operator wants made with a
  recorded rationale rather than escalated.
- The `allow_pre_v12=True` + 2.0.0 floor interaction (D-05 note) is the one
  place where today's code has a subtle multi-branch coupling. The
  recommendation preserves byte-identical behavior (env-var bypasses ONLY the
  pre-v1.2 branch, not the 2.0.0 floor); if the operator wants the env-var to
  bypass BOTH checks, that becomes an INTENTIONAL BEHAVIOR CHANGE per
  GATE-1.8 (refactor + fix bugs gate) — flagged for the planner to confirm.

</specifics>

<deferred>
## Deferred Ideas

- **`SerialCommunicator` mypy strict-overrides addition** — `[[tool.mypy.overrides]]`
  entry for `firestarter.serial_comm` is **Phase 42 ERR-02** territory
  ("those modules are mypy-clean under the configured strictness"). Phase 40
  adds hints; Phase 42 raises the bar.
- **Public-method docstrings on `SerialCommunicator`** — Phase 42 ERR-03
  ("all public classes and methods in touched modules have docstrings, 1-liner
  minimum"). Phase 40 touches signatures, not prose.
- **`Optional[X]` → `X | None` modernization** — locked deferred by Phase 37
  D-08 (`target-version = "py39"`); revisit only if the project's Python
  floor moves to 3.10+.
- **`ProtocolStateMachine` extraction from `serial_comm.py`** — REQUIREMENTS
  PROTOSM-01, **explicitly deferred to v1.9** per the REQUIREMENTS Future
  Requirements section; HIGH complexity, out of v1.8 scope.
- **Removing the thin `_decode_id_frame` method wrapper** — once Phase 41+ no
  longer cares about `test_decoder.py`'s direct method-call surface, the
  wrapper can be dropped and tests repointed to `codec.decode_id_frame`. Not
  worth the test edit in v1.8.
- **Centralized Click error→exit-code mapping** for `FirmwareOutdatedError`
  — Phase 41/42 territory (same deferred slot as Phase 39 D's
  `ChipNotFoundError`).

### Reviewed Todos (not folded)
Same three pending todos Phases 37/38/39 reviewed; all hardware/protocol/DB-
content, out of this host-transport cleanup's domain (the wire protocol is
frozen by GATE-1.8a):
- `avrdude-mcu-detection-fallback.md` — blank-chip / wrong-firmware recovery
  (hardware; v1.9-ish).
- `serial-cobs-resync-data-path.md` — COBS framing on the serial data path
  (protocol; not host-cleanup). Closest fuzzy match to Phase 40's "serial /
  transport" keyword, but COBS would CHANGE the wire framing — forbidden by
  GATE-1.8a; v1.9-or-later if revisited.
- `w27c512-eeprom-misclassification.md` — chip-DB content classification
  fix (DB **data**, not the serial **structure** this phase touches).

</deferred>

---

*Phase: 40-Serial / Transport Restructure*
*Context gathered: 2026-05-28*

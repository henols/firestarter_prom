# Phase 38: Low-Risk Extractions - Context

**Gathered:** 2026-05-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Extract **pure-compute code** out of the spaghetti modules (`serial_comm.py`,
`eprom_operations.py`, `firmware.py`, `hardware.py`) into new **flat sibling
modules** with **zero runtime behavior change**, and delete **confirmed dead
code**. Four new files:

- `firestarter/exceptions.py` — consolidated application exception hierarchy (STRUCT-04)
- `firestarter/frame_parser.py` — CRC8 + param-decode primitives, stdlib-only (STRUCT-01)
- `firestarter/codec.py` — message rendering (`format_message` + silkscreen table) (STRUCT-02)
- `firestarter/address_parser.py` — `parse_address` / `parse_size` with explicit validation (STRUCT-03)

Plus dead-code removal (STRUCT-05): delete `read_data_block`, replace `globals()`
introspection, strip confirmed-dead commented blocks.

**The full test suite (Phase 36's 162-test safety net + 29 syrupy snapshots) must
pass UNCHANGED after every file move** — that is the acceptance signal for a
"behavior-preserving extraction." This phase unblocks Phases 39 (chip_resolver
needs `ChipNotFoundError`), 40 (serial restructure consumes `frame_parser`/`codec`),
and 41 (CLI handlers import the stable exception surface).

Requirements: STRUCT-01, STRUCT-02, STRUCT-03, STRUCT-04, STRUCT-05 (full text in
`.planning/REQUIREMENTS.md`). Standing contract: GATE-1.8 (a–e), esp. **(a)** wire
byte-identical, **(b)** CLI surface preserved, **(d)** read path ring-fenced,
**(e)** suite green + entry point runs.
</domain>

<decisions>
## Implementation Decisions

The operator delegated all four open gray areas: "you recommend" (2026-05-27 —
same pattern as Phase 37's "accept all four"). The recommendations below are
**locked**. Each resolves a real conflict between the ROADMAP success criteria
and the actual code, found during the codebase scout. The operator can override
by editing this file before planning.

### Exception consolidation membership (STRUCT-04 / ROADMAP Phase 38 SC#1)
**The conflict:** SC#1 lists 7 classes for `exceptions.py` (incl. `ChipNotFoundError`,
which does not exist yet) and demands "no exception class defined outside this
module" — but `FirmwareOperationError` (`firmware.py:63`) and `AvrdudeNotFoundError`
/ `AvrdudeConfigNotFoundError` (`avr_tool.py:22,25`) exist and are not in the list.
REQUIREMENTS STRUCT-04 names only the three modules `serial_comm`, `eprom_operations`,
`hardware`.

- **D-01:** `exceptions.py` contains **8 classes**:
  - The 6 existing app exceptions named by SC#1: `SerialError`, `SerialTimeoutError`,
    `ProgrammerNotFoundError`, `FirmwareOutdatedError` (from `serial_comm.py:188-211`),
    `EpromOperationError` (from `eprom_operations.py:84`), `HardwareOperationError`
    (from `hardware.py:25`).
  - **`FirmwareOperationError`** (moved from `firmware.py:63`) — **documented inclusion**.
    SC#1's intent ("no exception class outside this module") is consolidation; leaving
    one genuine app exception orphaned in `firmware.py` is a half-job. Same shape
    (`class …(Exception)`), trivially low-risk.
  - **`ChipNotFoundError`** (NEW, empty `class ChipNotFoundError(Exception)` + docstring) —
    created here per Phase 39's stated `Depends on: Phase 38 (exceptions.py must exist
    so chip_resolver.py can import ChipNotFoundError)`. Declared-but-unused until Phase 39
    wires it; this is the designed dependency contract, not dead code.
- **D-02:** **Exclude** `AvrdudeNotFoundError` / `AvrdudeConfigNotFoundError` — they
  subclass `FileNotFoundError` (a builtin `OSError`), a **different domain** (avrdude
  binary/config discovery, not wire/operation/hardware). They stay local to the
  self-contained `avr_tool.py`. This is the **one documented exception to SC#1's
  "no exception class outside this module"**, with rationale recorded for the reviewer.
- **D-03:** **Preserve existing inheritance exactly.** `SerialTimeoutError` /
  `ProgrammerNotFoundError` / `FirmwareOutdatedError` keep subclassing `SerialError`;
  the rest subclass `Exception` directly; `ChipNotFoundError` subclasses `Exception`
  (matching `EpromOperationError`/`HardwareOperationError`). **Do NOT introduce a
  unifying `FirestarterError` base** — that changes `isinstance`/`except` relationships
  = a behavior change. Deferred to Phase 42 (ERR) if wanted (see Deferred Ideas).
- **D-04:** All import / `raise` / `except` sites repointed to `from firestarter.exceptions import …`.
  `exceptions.py` imports **nothing from the package** (pure leaf; stdlib only) to avoid
  cycles. Verified after the move by the full Phase 36 suite passing unchanged.

### frame_parser purity boundary (STRUCT-01 / SC#2)
**The conflict:** SC#2 lists `_decode_id_frame` as a member of `frame_parser.py` AND
requires "no imports from within the firestarter package (stdlib + typing only)". But
`_decode_id_frame` (`serial_comm.py:452`) references `CATALOG` (from `messages.py`) and
calls `_format_message` (→ `codec.py`) — both package imports. The two constraints cannot
both hold for that symbol.

- **D-05:** **Honor purity over literal symbol placement.** `frame_parser.py` gets ONLY
  the truly-pure primitives: `_build_crc8_table`, `_CRC8_CCITT_TABLE`, `_crc8_ccitt`,
  `_decode_param`, `Response` (namedtuple), `LogMessage` (namedtuple), `MAGIC_PREAMBLE`
  (`serial_comm.py:47-92`). These use stdlib only (`struct`, `collections.namedtuple`,
  `typing`) — confirmed by scout. This keeps `frame_parser` independently testable, which
  is the entire point of STRUCT-01.
- **D-06:** **`_decode_id_frame` stays in `serial_comm.py`** for Phase 38 — it is the
  *orchestrator* that ties pure CRC/param-decode to the message catalog (`CATALOG`) and
  the codec renderer (`codec.format_message`); it is inherently package-coupled. Its body
  is repointed to import the now-extracted primitives from `frame_parser` and call
  `codec.format_message`. Its final disposition belongs to **Phase 40** (Serial restructure,
  whose SC#1 says "frame-decode and message-format concerns are delegated to frame_parser +
  codec imports"). **Documented deviation from SC#2's symbol list** — flagged for the
  plan-checker / reviewer so it is not read as a missed requirement.
- **D-07:** `test_decoder.py` exercises the decode path through `SerialCommunicator` and
  **must pass unchanged** (SC#2). It does not import `_decode_id_frame` directly, so D-06's
  placement choice does not break it.

### codec.py extraction (STRUCT-02 / SC#3)
- **D-08:** `codec.py` contains `format_message` (renamed from the method `_format_message`,
  `serial_comm.py:341`) + `_REVISION_SILKSCREEN` (`serial_comm.py:177`). `_format_message`
  does **not** reference `self` (verified) → drops cleanly to a module-level pure function.
  `codec.py` imports from `constants.py` + `messages.py` **only** (per SC#3); cycle-safe —
  scout confirmed `messages.py` has **zero** package-internal imports. New `tests/test_codec.py`
  covers `format_message` with message-catalog fixtures (P-02 `MSG_OK_REV`, P-03 `MSG_OK_CFG`,
  `MSG_INFO_HW`/`MSG_INFO_PHYSICAL_HW`, `MSG_INFO_CMD`, `MSG_DEBUG`/`DBG_CMD`, `MSG_DATA_CHUNK`,
  and the `None` fall-through).

### Ring-fence preservation (GATE-1.8d / SERIAL-03)
- **D-09:** Because D-06 keeps `_decode_id_frame` in `serial_comm.py`, the ring-fenced
  `_read_and_parse_lines` generator's `self._decode_id_frame(...)` call (`serial_comm.py:662`)
  is **byte-identical — zero changes**. **No delegating shims needed.** The only `serial_comm.py`
  edits are: (i) delete the module-level primitives now living in `frame_parser`; (ii) delete the
  `_format_message` method (now `codec.format_message`); (iii) repoint `_decode_id_frame`'s two
  internal refs (`self._format_message` → `codec.format_message`; primitives via `frame_parser`
  import). **None touch `_read_and_parse_lines`.** `_decode_id_frame` is NOT itself ring-fenced
  (GATE-1.8d covers `read_eprom`/`read_data_block` + the streaming/timeout generator body).
- **D-10:** The `# DO NOT MODIFY — v1.9 RCA territory` marker stamp on `_read_and_parse_lines`
  stays **Phase 40's job** (SERIAL-03 SC#3) per the roadmap sequencing — Phase 38 only verifies
  byte-identity via `test_decoder.py` passing unchanged. (Planner may add the comment early if it
  prefers belt-and-suspenders; harmless, but not required here.)

### address_parser error contract (STRUCT-03 / SC#4)
**The conflict:** current inline parsing (`eprom_operations.py:182-200`) **logs an error and
returns `(None, 0)`** on bad input — graceful, non-raising. SC#4 says `parse_address` / `parse_size`
**raise `ValueError`** on bad input. The extracted parser must raise; the call site must keep
today's observable behavior (GATE-1.8b).

- **D-11:** `address_parser.py`:
  - `parse_address(s: str | None) -> int | None` — returns `None` when `s` is `None`; else
    `int(s, 16)` if `"0x"` in `s.lower()` else `int(s)`; **raises `ValueError`** on bad input
    (let `int()` raise, optionally wrapped with a clear message). Pure function.
  - `parse_size(s: str | None) -> int | None` — mirrors `parse_address`; **raises `ValueError`**
    on bad input.
- **D-12:** `_setup_operation` (`eprom_operations.py:157`) **wraps both calls in `try/except
  ValueError`**, preserving the **exact** current log lines — `"Invalid address format: {address}"`
  and `"Invalid size format: {size}"` — and the `return None, 0` graceful-fail path. The raise is
  fully contained; CLI-observable behavior is byte-identical (Phase 36 pinned the bad-`--address`
  / bad-`--size` paths — those snapshots must still pass).
- **D-13:** **Subtlety the planner MUST preserve:** today `command_dict["address"]` is set **only
  inside `if address:`** — when no address is passed, the key is **absent** (NOT `address=0`). Keep
  that: only assign `command_dict["address"]` when an address was actually provided. The local
  `addr = 0` default (used for the read `memory-size = addr + read_size` computation) stays owned by
  `_setup_operation`, not the parser. The `memory-size` write stays gated on `cmd == COMMAND_READ and size`.

### Dead-code removal (STRUCT-05 / SC#5) — mechanical, locked
- **D-14:** Delete `read_data_block` (`serial_comm.py:991`). Scout-confirmed **zero callers**
  (`grep` finds only its own `def`). Commit message cites the W-04 `MSG_DATA_CHUNK` migration
  that made it dead (per Phase 36 SC#5).
- **D-15:** Replace both `globals()` reverse-lookups (`eprom_operations.py:170` and `:232`,
  the `[k for k,v in globals().items() if v==cmd][0].replace("COMMAND_","")` pattern) with
  **`COMMAND_NAMES[cmd]`** (`constants.py:41`). Verified: `COMMAND_NAMES` values (`"READ"`,
  `"WRITE"`, `"BLANK_CHECK"`, …) match the old post-`.replace` strings **exactly**, and `[cmd]`
  fails fast on an unknown command just like the old `[0]` IndexError — behavior-identical for the
  log string. (This also kills a latent fragility: the old `globals()` scan could mis-match a
  `FLAG_*`/other constant sharing the same int value.)
- **D-16:** Remove only **confirmed-dead** commented-out blocks the researcher/planner identifies
  during extraction — do not strip comments that document live intent (e.g. the Phase-35 WR-01/02
  rationale comments in `_format_message`, which migrate verbatim into `codec.py`).

### Claude's Discretion
- Exact module docstrings / function-order within each new file; whether `parse_size` returns
  `int | None` or `int`; whether `parse_address` wraps `int()`'s `ValueError` with a custom message.
- Whether extracted module-level functions keep their leading `_` (private) or are exposed —
  follow each SC literally: `format_message` is public (SC#3 rename); the frame_parser primitives
  keep their `_` names per SC#2's list. New-file public surface is the planner's call where a SC
  is silent.
- Test-file organization beyond the two SC-mandated new files (`tests/test_codec.py`,
  `tests/test_address_parser.py`); whether to add a focused `exceptions` import-smoke test.
- Plan/wave decomposition. **Natural ordering** (dependency-safe): `exceptions.py` first (leaf,
  unblocks repoints) → `frame_parser.py` (leaf) → `codec.py` (needs constants+messages) →
  `address_parser.py` (independent) → dead-code sweep last. Each extraction is its own atomic
  commit with the full suite green before the next move.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope & locked milestone decisions
- `.planning/ROADMAP.md` — Phase 38 detail (Goal + SC#1–SC#5) + the v1.8 section + GATE-1.8 (a–e)
  standing gate. **Note the two documented deviations** captured above: D-06 (`_decode_id_frame`
  not moved to frame_parser) and D-01/D-02 (membership differs from the literal 7-class SC#1 list).
- `.planning/REQUIREMENTS.md` — STRUCT-01…STRUCT-05 (lines 40–44); GATE-1.8 (a–e) (lines 12–20);
  Out-of-Scope table.
- `.planning/PROJECT.md` — "Current Milestone: v1.8" + "Scope decisions (locked 2026-05-27)"
  (lines 32–41): host-only, flat layout (preserve git blame), refactor-and-fix-bugs gate.
- `.planning/phases/36-characterization-test-baseline/36-CONTEXT.md` — the 162-test safety net this
  phase relies on; the read-path ring-fence note (D-12 there); `COMMAND_FW_VERSION` present; the two
  latent bugs are fixed in 41/42 (NOT here).
- `.planning/phases/37-tooling-baseline-ci-gate/37-CONTEXT.md` — ruff/ruff-format/mypy gate +
  mypy watermark; **star-import removal is Phase 39 (DATA-03)** — leave `# noqa: F403/F405` parked
  here; touched modules must stay lint/format clean (the gate is live on `v1.8-app-cleanup`).

### Files this phase edits / creates (firestarter_app sub-repo)
- `firestarter_app/firestarter/serial_comm.py` — sources: `:47-92` frame primitives + `Response`/
  `LogMessage`/`MAGIC_PREAMBLE` (→ frame_parser); `:177` `_REVISION_SILKSCREEN` + `:341`
  `_format_message` (→ codec); `:452` `_decode_id_frame` (stays, repointed); `:662`
  `_read_and_parse_lines` call site (UNTOUCHED — ring-fenced); `:991` `read_data_block` (DELETE).
- `firestarter_app/firestarter/eprom_operations.py` — `:84` `EpromOperationError` (→ exceptions);
  `:157-200` `_setup_operation` inline address/size parse (→ address_parser, call site wraps);
  `:170`,`:232` `globals()` reverse-lookup (→ `COMMAND_NAMES[cmd]`).
- `firestarter_app/firestarter/firmware.py` — `:63` `FirmwareOperationError` (→ exceptions, D-01).
- `firestarter_app/firestarter/hardware.py` — `:25` `HardwareOperationError` (→ exceptions).
- `firestarter_app/firestarter/avr_tool.py` — `:22`,`:25` Avrdude*Error **STAY** (D-02).
- `firestarter_app/firestarter/constants.py` — `:41` `COMMAND_NAMES` (D-15 lookup source).
- `firestarter_app/firestarter/messages.py` — `CATALOG`/`DEBUG_CATALOG`/`DBG_CMD`/`MSG_*` (codec deps;
  zero package-internal imports → cycle-safe).
- **NEW:** `firestarter_app/firestarter/exceptions.py`, `frame_parser.py`, `codec.py`, `address_parser.py`.
- **NEW tests:** `firestarter_app/tests/test_codec.py`, `firestarter_app/tests/test_address_parser.py`.
- `firestarter_app/tests/test_decoder.py` — MUST pass unchanged (SC#2 / D-07).

### App architecture (context)
- `firestarter_app/CLAUDE.md` — data flow + the `constants.py` ↔ `firestarter/include/firestarter.h`
  sync contract (relevant if any constant is touched — it is not in this phase).
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Phase 36 safety net** (162 passed + 2 xfail + 29 syrupy snapshots) — the per-move acceptance
  signal. Run after every extraction; unchanged-green == behavior preserved.
- `tests/test_decoder.py` — already exercises the full frame-decode path; proves frame_parser +
  the repointed `_decode_id_frame` still work without a single test edit.
- `COMMAND_NAMES` (`constants.py:41`) — already the canonical cmd→name map; replaces the fragile
  `globals()` scan with no new data.

### Established Patterns
- `_format_message` and `_decode_id_frame` are "accidentally methods" — neither needs `self` for
  the format logic (verified); `_format_message` drops cleanly to a pure function. `_decode_id_frame`
  is package-coupled (catalog + codec) so it stays a method (D-06).
- Leaf-module discipline: `exceptions.py` (stdlib only) and `frame_parser.py` (stdlib only) are pure
  leaves; `codec.py` depends only on the other leaves `constants.py` + `messages.py`. No import cycles.
- Flat layout (PROJECT.md) — all new files are siblings under `firestarter/`; no subpackages.

### Integration Points
- Exception repoint touches `serial_comm.py`, `eprom_operations.py`, `firmware.py`, `hardware.py`
  (all `import`/`raise`/`except` sites) — mechanical, suite-verified.
- `_setup_operation` is the single consumer of `address_parser` (STRUCT-03 / D-12).
- `_decode_id_frame` is the single internal consumer of `codec.format_message` after extraction.
</code_context>

<specifics>
## Specific Ideas

- Operator's working style (Phase 37 + here): delegate the technical judgment ("you recommend"),
  keep each phase **lean and behavior-preserving**, minimize churn, preserve git blame. The two
  documented SC deviations (D-06, D-01/D-02) are exactly the kind of call the operator wants made
  with a recorded rationale rather than escalated.
</specifics>

<deferred>
## Deferred Ideas

- **Unifying `FirestarterError` base class** for the exception hierarchy — would let callers
  `except FirestarterError` broadly. Deliberately NOT done in Phase 38 (changes `isinstance`/`except`
  semantics = behavior change). Candidate for **Phase 42** (Error Handling Normalization), where the
  exit-code/exception convention is the explicit subject.
- **Making `_decode_id_frame` a pure DI function** (inject `catalog` + a render callback so it could
  live in `frame_parser` honoring SC#2's literal list) — higher-risk signature surgery; revisit in
  **Phase 40** if the serial restructure wants frame-decode fully delegated out of `SerialCommunicator`.

### Reviewed Todos (not folded)
Same three pending todos Phase 37 reviewed; all hardware/protocol, out of this pure-extraction
phase's domain (and the wire protocol is frozen by GATE-1.8a):
- `avrdude-mcu-detection-fallback.md` — blank-chip / wrong-firmware recovery (hardware; v1.9-ish).
- `serial-cobs-resync-data-path.md` — COBS framing on the serial data path (protocol; not host-cleanup).
- `w27c512-eeprom-misclassification.md` — chip-DB classification fix (database content, not structure).
</deferred>

---

*Phase: 38-Low-Risk Extractions*
*Context gathered: 2026-05-27*

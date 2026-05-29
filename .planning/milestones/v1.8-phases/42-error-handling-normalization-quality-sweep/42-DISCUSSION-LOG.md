# Phase 42: Error Handling Normalization + Quality Sweep - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-28
**Phase:** 42-Error Handling Normalization + Quality Sweep
**Areas discussed:** initial gray-area set (Q1), genuinely-open subset (Q2). Operator chose "You recommend all 3" on the calibrated set.

---

## Round 1 — Initial Gray-Area Survey

**Question to operator:** "Which areas do you want to discuss for Phase 42?"

| Option | Description | Selected |
|--------|-------------|----------|
| Mapping mechanism | Click boundary mapping: (a) custom click.Command subclass / (b) per-handler decorator / (c) per-call-site `raise ClickException` | |
| BUG-2 fix shape | (a) Split except clause / (b) re-raise EpromOperationError / (c) catch separately + log w/ corrected label | |
| Coverage gate | (a) add tests / (b) `omit` hardware-only modules / (c) mixed | |
| Mypy strict scope | Whether to include `eprom_operations.py` in strict overrides | |

**User's choice:** "do you have any gray areas?" (free-text via Other)
**Notes:** Operator pushed back on the initial set as ceremony-heavy. Forced a scout-driven re-grading. The push-back filtered out three of four options as directionally locked by Phase 41 D-09 + the existing xfail assertion text + the SC literal:
- Mapping mechanism — Phase 41 D-09 dictates `raise ClickException` flowing from `chip_resolver.resolve_chip` directly. Decorator vs. per-call-site is minor styling within that pattern.
- BUG-2 fix shape — xfail assertion text ("EpromOperationError must NOT be labeled as Communication error") essentially forces the split-clause variant; only the log label wording is open.
- Naming + bare-excepts + dead-code + docstrings — scout showed naming already conformant (zero camelCase), bare-excepts already zero, dead code already swept Phase 38, module docstrings already present.

The push-back was the load-bearing input — re-grading produced 3 genuinely-open choices for Round 2.

---

## Round 2 — Calibrated Open Choices

**Question to operator:** "Of the three genuinely-open choices, which do you want to discuss directly?"

| Option | Description | Selected |
|--------|-------------|----------|
| Coverage trajectory | Real tests to tractable modules vs. omit hardware-only modules vs. mixed | |
| EpromOperationError exit code | Keep lumped at exit 1 (status quo) vs. carve out distinct exit code 3 | |
| eprom_operations strict | Include in mypy strict overrides or leave on gradual rules | |
| You recommend all 3 | Standing Phase 37/38/40/41 delegation pattern; Claude picks with recorded rationale | ✓ |

**User's choice:** "You recommend all 3"
**Notes:** Continues the standing Phase 37/38/40/41 delegation pattern. Operator pre-delegates implementation choices and reviews CONTEXT.md as the recorded-rationale audit trail.

---

## Claude's Discretion

The operator delegated all three Round 2 choices with recorded rationale. The locked recommendations:

- **Coverage trajectory → mixed (D-12..D-15):** Narrow `omit` of `firestarter/avr_tool.py` (subprocess wrapper; meaningful coverage would require spawning real `avrdude` in CI or per-method monkey-patching — test-value/cost ratio low) PLUS targeted test additions on tractable modules (`database.py` conversion, `eprom_operations.py` happy paths via existing `fake_serial` fixture, `firmware.py` PEP 440 + JSON parsers, `config.py` get/set, `hardware.py` read-side voltage). Projected ratio: 70.2%; planner verifies empirically. Fallback (small additions on `logging_utils.py` / `utils.py`) identified if margin tightens.
- **EpromOperationError exit code → keep at 1 (D-04):** Carving out exit 3 would break Phase 36's 29 syrupy snapshots + Phase 41's ~30 `test_cli_handlers.py::assert result.exit_code == 1` assertions (verified by scout). GATE-1.8b explicitly preserves end-user exit codes. The "stable exit codes" wording in ERR-01 SC is about consistency around 0/1/2, not introducing a new code. Documented as deferred to a future milestone with real shell-script-author demand.
- **eprom_operations.py mypy strict → deferred to v1.9 or Phase 43 (D-07):** Read-path-adjacent core (`_run_state_machine` + `_execute_phase`); GATE-1.8d ring-fences the read-path body. Forcing strict typing risks return-type refactors that ripple into byte-identity-protected method bodies. SC literal explicitly omits it from the minimum list. Phase 42 ERR-02 closes against the SC-literal 8-module set (`main.py`, `cli_handlers.py`, `chip_resolver.py`, `frame_parser.py`, `codec.py`, `address_parser.py`, `exceptions.py`, `serial_comm.py`); `eprom_operations.py` is a clean addition for v1.9 post-RCA.

Additional Claude-side calls captured in CONTEXT.md "Claude's Discretion" section:
- `map_typed_errors` decorator placement (recommend inside `cli_handlers.py`, not a separate `cli_errors.py`).
- Plan 42-03 test-file landing order (low-coupling first).
- Docstring style (1-liner floor; match what's already in the file).
- EpromOperationError vs HardwareOperationError message-prefix wording.
- `pyproject.toml` mypy override block placement (recommend separate from Phase 36 test block).

## Deferred Ideas

- Exit-code richness (carve exit 3 for "programmer error") — deferred per D-04; needs real shell-script demand.
- `eprom_operations.py` mypy strict — deferred per D-07 to v1.9 post-RCA or Phase 43 non-blocking.
- `hardware.py` / `eprom_info.py` / `ic_layout.py` voltage-engagement + presenter coverage — left at low coverage per D-14 floor.
- `pluggy` / `Result[T, E]` monadic types — out per REQUIREMENTS Out-of-Scope.
- README updates — Phase 43 DOC-01 territory.
- `PROTOSM-01` ProtocolStateMachine extraction — v1.9-or-later per REQUIREMENTS Future Requirements.

### Reviewed Todos (not folded)
- `avrdude-mcu-detection-fallback.md` — hardware; v1.9-ish.
- `serial-cobs-resync-data-path.md` — protocol; forbidden by GATE-1.8a.
- `w27c512-eeprom-misclassification.md` — DB content; not CLI structure.

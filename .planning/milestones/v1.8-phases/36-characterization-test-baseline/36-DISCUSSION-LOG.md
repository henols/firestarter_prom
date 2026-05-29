# Phase 36: Characterization Test Baseline - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-27
**Phase:** 36-Characterization Test Baseline
**Areas discussed:** Hardware-comm error handling (operator addition), CLI golden-capture strategy, EpromDatabase de-singleton scope, Snapshot tooling + stability

---

## Area selection

Operator selected three of the four offered gray areas (Snapshot tooling + stability, EpromDatabase de-singleton scope, CLI golden-capture strategy) and added a freeform fourth: *"Fix the error handling while communicating with the hardware so the correct error messages are shown."* Clarified to: *"app always reports that the communication is broken when the hw returns an error."* TEST-05 reconciliation was folded into the comm-error discussion (COMMAND_FW_VERSION found present → no longer a bug).

---

## Hardware-comm error handling (operator addition)

| Option | Description | Selected |
|--------|-------------|----------|
| Characterize in 36, fix in 42 | Phase 36 xfail-strict test asserts corrected behavior; Phase 42 (ERR-01) splits the except clause | ✓ |
| Characterize + fix both in 36 | Pull the fix forward; breaks the additive-safety-net invariant | |
| Just characterize, decide fix-phase later | Pin test, leave fix unassigned | |

**User's choice:** Characterize in 36, fix in 42.
**Notes:** Root cause confirmed in code: `eprom_operations.py:265-267` buckets `EpromOperationError` (firmware-reported operational error over a healthy link) together with `SerialError`/`SerialTimeoutError` under one "Communication error" log line. Fix is at the handler layer — does NOT touch the ring-fenced `_read_and_parse_lines` decode path, so it is clean v1.8 work. Replaces the non-bug `COMMAND_FW_VERSION` in TEST-05's bug set (which was found present at `constants.py:39`).

---

## CLI golden-capture strategy

### Q1 — Harness mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| subprocess black-box | Invoke real `firestarter` binary; harness identical pre/post Click migration; proves GATE-1.8(b) byte-for-byte | ✓ |
| in-process main()+capsys | Faster, but couples to argparse and must be rewritten to CliRunner at Phase 41 | |
| Hybrid | subprocess for surface goldens + in-process for parse edge cases | |

**User's choice:** subprocess black-box.

### Q2 — Command/path scope

| Option | Description | Selected |
|--------|-------------|----------|
| Help + DB cmds + all errors | Board-independent surface only; happy-paths covered at TEST-02/03 unit layer | |
| Narrower: help + parse errors only | Leanest | |
| Broader: also E2E happy-paths via fake serial | Adds read/write/verify/erase happy-paths E2E | ✓ |

**User's choice:** Broader — also E2E happy-paths via fake serial.

### Q3 — Reconciling subprocess + fake-serial (process-boundary bridge)

| Option | Description | Selected |
|--------|-------------|----------|
| Split harness: subprocess + in-process | Pure subprocess for help/DB/errors; in-process make_comm/fake_serial for happy-paths; no production seam; happy-path subset re-pointed to CliRunner at Phase 41 | ✓ |
| File-backed replay seam | Env-var replay transport; keeps one pure-subprocess harness but adds production code in Phase 36 | |
| Keep happy-paths at unit layer (TEST-02/03) | No seam, no hybrid; happy-paths not pinned at the CLI boundary | |

**User's choice:** Split harness.
**Notes:** subprocess is a separate process — a `BytesIO` fake can't be injected across the boundary. The seam (had we added one) would sit at transport construction, not decode logic, so it would have stayed ring-fence-safe; operator chose to avoid the production seam entirely in the safety-net phase.

---

## EpromDatabase de-singleton scope

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal: drop guard + test-injection ctor | Remove `__new__`/`_initialized` guard; `database_path` ctor seam + skip user-override; keep per-site construction; defer Click-context DI to Phase 41 | ✓ |
| Full DI now | Thread one instance through every layer this phase | |
| Inject pre-loaded data (no file I/O) | Ctor takes a proms dict; subset of Minimal; TEST-03 still needs real-DB path-load | |

**User's choice:** Minimal.
**Notes:** Call sites already accept an injected `db_instance` (`EpromInfo`/`ChipLayout` ctors; `main():589`), so the only singleton machinery is the in-class guard — low blast radius.

---

## Snapshot tooling + stability

### Q1 — Snapshot mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| syrupy | Roadmap-named pytest snapshot plugin; new test-only dep | ✓ |
| Committed golden text files | No plugin; explicit PR diffs; diverges from roadmap | |
| pytest-regressions | File-oriented plugin; also a new dep; not the named choice | |

**User's choice:** syrupy.
**Notes:** Existing `tests/golden/` dir is empty placeholder stubs — no established harness to preserve.

### Q2 — Determinism (CI vs bench machine)

| Option | Description | Selected |
|--------|-------------|----------|
| Normalize + neutralize auto-discovery | syrupy filters (version/paths/ports) + neutralize port auto-discovery so output is board-independent + DB pinned to packaged JSON, override skipped | ✓ |
| Normalize only; CI is source of truth | Scrub noise; CI authoritative; local hardware-touching goldens auto-skip when a board is present | |
| No hardware-touching subprocess goldens | Only board-independent output via subprocess; no-programmer/comm-error chars in-process only | |

**User's choice:** Normalize + neutralize auto-discovery.
**Notes:** `_list_potential_ports` appends discovered system ports even when `-p` is given, so a bogus port alone is insufficient — neutralization mechanism left to the planner (test-only seam vs mock at `list_ports.comports`).

---

## Claude's Discretion

- Exact test-file naming/organization.
- Port-auto-discovery neutralization mechanism (test-only seam vs `list_ports` mock).
- Timeout-invariant simulation technique for TEST-02 (virtual-time monkeypatch vs trickle-feed of empty reads).
- Whether to add `click` as a test dep now (only needed at Phase 41 for `CliRunner`).
- xfail-strict bug-test mechanism (D-10), TEST-04 `skipif`-when-firmware-absent — captured as sensible defaults; operator chose "I'm ready for context" rather than deep-diving these.

## Deferred Ideas

None — discussion stayed within phase scope. The two bug *fixes* (build_arg_flags → Phase 41; comm-error split → Phase 42) are sequenced, not deferred.

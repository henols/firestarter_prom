---
phase: 120
slug: host-cli-surface-wire-emission-capability-refusal
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-29
---

> **Status note.** `status: draft` / `nyquist_compliant: false` because this contract is created at plan time,
> before the plan set exists. The per-task map below is populated once `120-*-PLAN.md` files land; the
> requirement→oracle map is already complete and is the binding half. `wave_0_complete` stays `false` until
> the two new test modules (`tests/test_sdp_capability.py`, `tests/test_dev_sdp_cmd.py`) and the rebuilt
> parity gate exist on disk.

# Phase 120 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `120-RESEARCH.md` § Validation Architecture. Baseline measured 2026-07-29 at
> `firestarter_app` HEAD `9ead17f`, firmware HEAD `0048b3d` (tree clean, and required to stay so).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` (+ `pytest-randomly`, `syrupy`, `pytest-cov`), invoked as `python3 -m pytest` |
| **Config file** | `firestarter_app/pyproject.toml` — `[tool.pytest.ini_options]`, `[tool.mypy]`, `mypy_error_watermark = 35` |
| **Quick run command** | `cd /workspaces/firestarter_app && python3 -m pytest tests/test_sdp_capability.py tests/test_dev_sdp_cmd.py tests/test_revision_constants_parity.py -q` |
| **Full suite command** | `cd /workspaces/firestarter_app && python3 -m pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` |
| **Lint/format gate (CI-scoped)** | `ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/` — **CI scope is `firestarter/ tests/`, not `.`**; four `tools/` files are lint-dirty at baseline |
| **Type gate** | `python3 tools/check_mypy_watermark.py` — assert the reported error count stays at **1** (watermark 35 has 34 slack; a bare `mypy` run is red at baseline) |
| **Estimated runtime** | quick ~5 s · full suite ~90 s |
| **Baseline** | Exactly **one** pre-existing failure: `test_audit_coverage_matrix.py::test_golden_file_matches`. Everything else green, measured this session. |

**Two known environment artifacts — name them, never silently tolerate them:**
- `test_audit_coverage_matrix` is a stale golden, not this phase's regression (`reference_audit_coverage_matrix_golden_stale`).
- `test_no_programmer_found_*` go RED when a board is attached (`/dev/ttyACM0`, `/dev/ttyACM1`, `/dev/ttyUSB0` are present). Did **not** reproduce this session.

---

## Sampling Rate

- **After every task commit:** quick run command, plus `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/`.
- **After every plan wave:** full suite + `python3 tools/check_mypy_watermark.py` (error count ≤ 1) + the nine-row CORRECTION-4 gate table if the wave touched `cli_handlers.py`, `constants.py`, or anything the gates scan.
- **Before `/gsd-verify-work`:** full suite green except the single named pre-existing failure; all nine gate rows re-run at the final commit; both sub-repo trees in their expected state.
- **Max feedback latency:** ~5 s (quick), ~90 s (full).

---

## Requirement → Oracle Map

Task IDs are filled in after planning. Every row below must be reachable by an automated command.

| Req ID | Behavior | Test Type | Automated Command | File Exists |
|--------|----------|-----------|-------------------|-------------|
| HOST-01 | `dev sdp <chip> enable\|disable` exists with the locked CLI surface | unit (CliRunner) | `pytest tests/test_dev_sdp_cmd.py -k surface -x` | ❌ W0 |
| HOST-01 | Gate order absent → capability → support-status → confirm; **`Confirm.ask` not called** on any refusal | unit | `pytest tests/test_dev_sdp_cmd.py -k gate_order -x` | ❌ W0 |
| HOST-01 | **No serial port opened** on any refusal (`find_and_connect.assert_not_called()`) — not exit code | integration (mock transport) | `pytest tests/test_dev_sdp_cmd.py -k no_port_opened -x` | ❌ W0 |
| HOST-01 | On-TTY confirms; `-y` bypasses; off-TTY without `-y` refuses (D-06) | unit | `pytest tests/test_dev_sdp_cmd.py -k consent -x` | ❌ W0 |
| HOST-01 | An `adapter-required` `0x0D` part with no SDP hears the **capability** reason, not the adapter reason (D-08) | unit | `pytest tests/test_dev_sdp_cmd.py -k adapter_required_hears_capability -x` | ❌ W0 |
| HOST-02 | `write --skip-sdp-unlock` sets bit `0x100` in the emitted `flags` | unit | `pytest tests/test_eprom_operations.py -k skip_sdp_unlock_bit -x` | ✅ extend |
| HOST-02 | `build_flags`' new param is keyword-only, defaults `False`; BUG-1 contract intact | characterization | `pytest tests/test_bug_characterization.py -q` | ✅ re-run |
| HOST-02 | D-18: non-`0x0D` chip warns and the write still runs (bit still emitted) | unit | `pytest tests/test_dev_sdp_cmd.py -k non_0x0d_warn_and_proceed -x` | ❌ W0 |
| HOST-03 | Every firmware `#define CMD_*`/`FLAG_*` maps two-way to `constants.py`, with `COMMAND_NAMES` coverage; exemptions enumerated explicitly | parity gate | `pytest tests/test_revision_constants_parity.py -q` | ✅ rebuild |
| HOST-03 | The parity gate **actually fails** on planted drift | planted-violation | `pytest tests/test_revision_constants_parity.py -k planted -x` | ❌ W0 |
| HOST-03 | The gate fails closed on an unreadable/absent header path | fail-closed | `pytest tests/test_revision_constants_parity.py -k fail_closed -x` | ❌ W0 |
| HOST-04 | `allow-set ∪ refuse-set == exactly the 84 `algorithm == 13` entries`, with the **74 / 10** split pinned | DB invariant | `pytest tests/test_sdp_capability.py -k partition -x` | ❌ W0 |
| HOST-04 | Every refuse-set member (2 FRAM + 8 pre-SDP incl. **`2817`**) is refused with a reason naming why | unit | `pytest tests/test_sdp_capability.py -k named_refusals -x` | ❌ W0 |
| HOST-04 | Non-vacuity: a synthetic `algorithm == 13` entry in neither set makes the helper raise | non-vacuity | `pytest tests/test_sdp_capability.py -k non_vacuous -x` | ❌ W0 |
| HOST-04 | **Shape leg (F-06):** the predicate is name-keyed, and a `resolve_chip` dict provably lacks `protocol-id`/`name` | anti-vacuity | `pytest tests/test_sdp_capability.py -k dict_shape -x` | ❌ W0 |
| HOST-04 | A user-override `0x0D` part (simulating `~/.firestarter/database.json`) is refused at **runtime** | unit | `pytest tests/test_sdp_capability.py -k local_override_refused -x` | ❌ W0 |
| HOST-04 | D-04: a refused part gets `FLAG_SKIP_SDP_UNLOCK` auto-set on `write` **and** an unconditional report line | unit | `pytest tests/test_dev_sdp_cmd.py -k auto_set_reported -x` | ❌ W0 |
| HOST-05 | No SDP report text contains a lock/unlock state boolean; the unreadable-state caveat is on **both** directions | text assertion | `pytest tests/test_dev_sdp_cmd.py -k no_fabricated_state -x` | ❌ W0 |
| HOST-05 | An INFO-band decoded frame logs at `logging.INFO`, not DEBUG (D-09) | unit | `pytest tests/test_serial_comm.py -k info_band_promoted -x` | ✅ extend |
| HOST-05 | D-10: the host summary line carries **no** duration figure | text assertion | `pytest tests/test_dev_sdp_cmd.py -k summary_no_duration -x` | ❌ W0 |
| HOST-05 | D-11: `0x87` `MSG_WARN_SDP_TBLC_EXCEEDED` prints at WARNING and the exit code stays `0` | unit | `pytest tests/test_dev_sdp_cmd.py -k tblc_warn_exit_zero -x` | ❌ W0 |
| HOST-06 | D-14: `MSG_ERR_UNKNOWN_CMD` on the SDP path renders as a firmware-too-old refusal | unit | `pytest tests/test_dev_sdp_cmd.py -k firmware_too_old -x` | ❌ W0 |
| HOST-06 | D-15: flag set **and** `0x86` absent → loud report + operation fails | unit | `pytest tests/test_eprom_operations.py -k missing_sdp_ack -x` | ❌ W0 |
| HOST-06 | D-15 converse: flag set **and** `0x86` present → no complaint, operation succeeds | unit | `pytest tests/test_eprom_operations.py -k sdp_ack_honoured -x` | ❌ W0 |
| SUB-fix | `dev test --submit` targets `henols/firestarter_prom`, asserted on **argv**, never on exit code | unit | `pytest tests/test_submit.py -k repo_target -x` | ✅ extend |
| all | Nine-row CORRECTION-4 sweep green at the final commit | regression | see `120-RESEARCH.md` § F-18 (nine commands) | ✅ present |
| all | Firmware sub-repo **byte-untouched** | regression | `git -C /workspaces/firestarter status --porcelain` empty **and** tip still `0048b3d` | ✅ |
| all | DB + generated codegen untouched | regression | `git -C /workspaces/firestarter_app diff --stat -- firestarter/data/ firestarter/messages.py` empty | ✅ |

---

## Wave 0 Requirements

- [ ] `tests/test_sdp_capability.py` — the partition invariant, named refusals, non-vacuity, the F-06 shape leg, local-override refusal
- [ ] `tests/test_dev_sdp_cmd.py` — CliRunner surface, gate ordering, no-port-opened, consent matrix, report-text assertions
- [ ] `tests/test_revision_constants_parity.py` — rebuilt as a real header-parsing gate (replaces hardcoded literals)
- [ ] `tests/fixtures/planted_constants_drift.h` — the parity gate's planted-violation header

---

## Planted-Violation Fixtures Required

The project's mandatory anti-hollow contract: every gate ships a companion proving it can fail.

| Gate | Planted violation | Proves |
|---|---|---|
| Constants parity (D-12/D-13) | `tests/fixtures/planted_constants_drift.h` — one `CMD_*` value changed, one `FLAG_*` deleted, one new `CMD_*` added | Value drift, host-missing, and firmware-missing are each detected |
| Constants parity — `COMMAND_NAMES` leg | in-test `monkeypatch.delitem` on a `COMMAND_NAMES` copy | A missing name entry is caught, not just a missing constant |
| Constants parity — fail-closed | point the path constant at a non-existent file | An unreadable header is an ERROR, never a silent pass |
| Allow-set exhaustiveness (D-02) | synthetic in-memory DB with one `algorithm == 13` entry in neither set | The partition invariant can fail — mirrors `test_sdp_db_invariant.py:151-184` |
| Allow-set shape leg (F-06) | assert `"protocol-id" not in resolve_chip(...)` | The vacuity mode that broke `_SRAM_PROTO_IDS` is machine-excluded |
| Gate ordering (D-08) | reorder gates in a test double, or assert reason-string identity per gate | Gate *order* is tested, not merely gate presence |
| D-09 mapping | assert `DEBUG` still applies to a non-INFO/WARN/ERROR label | The promotion is scoped, not a blanket level change |
| D-15 missing ack | frame stream with the flag set and `0x86` **omitted** | The check fires; the converse case proves it does not over-fire |

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| — | — | — | — |

**All phase behaviors have automated verification.** This phase adds **no bench work**: no AT28C part is on the bench, `0x0D` stays `UNVERIFIED`, zero `support_status` changes, the 84-chip count is unchanged.

---

## What CANNOT Be Validated — the ceiling, restated

- **That the curated capability partition is correct per family.** `REQUIREMENTS.md` § "Validation Ceiling" lists this explicitly. The gate proves the partition is **total and stable**, never that it is **right**.
- Any claim about actual silicon protection state, before or after either sequence.
- That `tBLC` is met as accepted by the die.
- That gh#11's symptom is gone.
- Nothing in this phase is evidence about AT28C silicon.

---

## Validation Sign-Off

- [ ] All tasks have an `<automated>` verify or a Wave 0 dependency
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all ❌ references above
- [ ] No watch-mode flags
- [ ] Feedback latency < 90 s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

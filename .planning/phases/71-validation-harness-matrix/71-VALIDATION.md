---
phase: 71
slug: validation-harness-matrix
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-16
---

# Phase 71 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: `71-RESEARCH.md` §Validation Architecture (HIGH confidence).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Unity (PlatformIO `[env:native]`, firmware) + pytest 7.x (host) |
| **Config file** | `firestarter/platformio.ini` §`[env:native]`; `firestarter_app/pyproject.toml` |
| **Quick run command** | `pio test -e native -f "*test_dispatch*"` (fw) · `cd firestarter_app && pytest tests/ -x` (host) |
| **Full suite command** | `pio test -e native && cd firestarter_app && pytest tests/ --cov-fail-under=70 && python tools/check_dispatch.py` |
| **Estimated runtime** | ~60–120 seconds (native + host + dispatch gate) |

> ⚠ Devcontainer Python is 3.12 but CI targets py39/3.11 — validate `ruff check` + `ruff format --check` against the target before claiming CI green (see project memory `reference_devcontainer_py312_masks_ci_py39`).

---

## Sampling Rate

- **After every task commit (firmware):** `pio test -e native -f "*test_dispatch*"` (existing regression baseline — proves recording stub flag-off is a no-op)
- **After every task commit (host):** `cd firestarter_app && pytest tests/ -x --cov-fail-under=70 && python tools/check_dispatch.py`
- **After every plan wave:** full `pio test -e native && cd firestarter_app && pytest tests/ --cov-fail-under=70`
- **Before `/gsd-verify-work`:** all Tier-1 + Tier-2 cells GREEN; Tier-3 SKIP-deferred scaffold in place; `check_dispatch.py` exits 0
- **Max feedback latency:** ~120 seconds

---

## Per-Task Verification Map

> Draft — the planner refines task IDs against the final plan/wave split. One row per requirement-behavior from `71-RESEARCH.md` §Phase Requirements → Test Map.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | HARN-01 (Tier-1) | — | Recording bus stub captures `rurp_*` CTL register-write sequence per family | unit (Unity) | `pio test -e native -f "*test_val_*"` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | HARN-01 (Tier-1 regression) | — | Existing suites compile unchanged with `HOST_STUBS_RECORD_BUS` off (no-op) | regression (Unity) | `pio test -e native -f "*test_dispatch*"` | ✅ | ⬜ pending |
| TBD | TBD | TBD | HARN-01 (Tier-2) | — | Host wire dict for each family dispatches to correct handler | unit (pytest) | `pytest tests/test_val_wire_*.py -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | HARN-01 (Tier-3) | — | `dev validate-family` composes cycle methods without re-impl; SKIP-deferred when no board | integration (pytest) | `pytest tests/test_validate_family_cmd.py -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | HARN-02 | — | Authored matrix JSON distinct from emitted results artifact | unit (pytest) | `pytest tests/test_matrix_schema.py -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | HARN-02 | — | Codegen produces deterministic C++ header | unit (pytest) | `pytest tests/test_gen_validation_header.py -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | HARN-02 | — | Emitted `validation-matrix.json` has correct schema (family × board × verdict × evidence SHA) | unit (pytest) | `pytest tests/test_matrix_artifact.py -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | HARN-03 | — | Negative control (wrong file) returns FAIL not PASS — verify *can* fail | unit (pytest) | `pytest tests/test_validate_oracle.py::test_negative_control -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | HARN-03 | — | `uno328pb` cells hard-coded N/A for any program/write cell | unit (pytest) | `pytest tests/test_validate_oracle.py::test_uno328pb_na -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | HARN-04 | T-71 (VPP mis-enable) | Per-family VPP invariants pass; non-VPP families never see `vpp_mv > 6000` | integration (script) | `python tools/check_dispatch.py` | ✅ (extend) | ⬜ pending |
| TBD | TBD | TBD | HARN-04 | T-71 (rogue dispatch) | `non_supported_dispatchable` populated; gate FAILS on a non-supported chip routing to a real handler | unit (pytest) | `pytest tests/test_check_dispatch_invariants.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter/test/native/avr/_shared/host_stubs_common.inc` — add `#define HOST_STUBS_RECORD_BUS` guarded recording buffer (D-04, single-edit-point)
- [ ] `firestarter/test/native/avr/test_val_{eprom,eeprom28c,flash3,flash4,flash_intel,sram}/` — 6 Tier-1 native suites (HARN-01)
- [ ] `firestarter/platformio.ini` — add each `test_val_*` suite to the positive `test_filter` allowlist (PIO quirk: omission = silently not run)
- [ ] `firestarter_app/tools/validation_matrix_spec.json` — authored matrix source (D-01)
- [ ] `firestarter_app/tools/gen_validation_header.py` — codegen entrypoint → C++ header (D-01)
- [ ] `firestarter/test/native/avr/_shared/validation_matrix.h` — GENERATED header (codegen output)
- [ ] `firestarter_app/tests/test_val_wire_*.py` — 6 Tier-2 host wire round-trip files (HARN-01)
- [ ] `firestarter_app/tests/test_validate_family_cmd.py` — Tier-3 runner scaffold (HARN-01)
- [ ] `firestarter_app/tests/test_matrix_schema.py`, `test_gen_validation_header.py`, `test_matrix_artifact.py` — HARN-02
- [ ] `firestarter_app/tests/test_validate_oracle.py` — HARN-03 (negative control + uno328pb N/A)
- [ ] `firestarter_app/tests/test_check_dispatch_invariants.py` — HARN-04

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Tier-3 HIL real cell evidence (post-write read+SHA on Leonardo, live r1≈270000 calibration) | HARN-03 (oracle, full proof) | Requires physical board + chip; deferred to Phase 73 by D-06/D-07 — Phase 71 records SKIP-deferred cells | Phase 73: run `dev validate-family` on bench with Leonardo/ACM0; software tiers in Phase 71 use deliberate-mismatch assertions, not real hardware |

*Phase 71 is software-first/flash-free by design — all Tier-1 and Tier-2 cells are automated; the only manual surface (Tier-3 real-hardware evidence) is explicitly deferred to Phase 73.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

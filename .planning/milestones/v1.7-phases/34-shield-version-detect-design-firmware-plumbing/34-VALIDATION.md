---
phase: 34
slug: shield-version-detect-design-firmware-plumbing
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-25
---

# Phase 34 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution. Sourced from `34-RESEARCH.md` §Validation Architecture; consult RESEARCH for full Nyquist Dim 1..8 rationale.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (firmware)** | PlatformIO Unity (`[env:native]` host-side cross-compile) — `firestarter/platformio.ini` |
| **Framework (host CLI)** | pytest 7.x — `firestarter_app/pyproject.toml` |
| **Quick run command (firmware)** | `cd firestarter && pio test -e native -f "*test_dispatch*"` |
| **Quick run command (host)** | `cd firestarter_app && pytest -q` |
| **Full suite (firmware)** | `cd firestarter && pio test -e native` *(known-flaky `test_flash_intel_vpp` + `test_eeprom28c_chip_id` per Phase 17 WR-01 — pre-existing, not a Phase 34 concern)* |
| **Full suite (host)** | `cd firestarter_app && pytest -q` |
| **GATE-1.7 byte-diff gate** | `bash /workspaces/.planning/v1.7/baseline-34/verify-detect-34.sh` — modeled on Phase 33 Plan 33-00 `check-migration.sh` |
| **Estimated runtime** | ~5 s (pytest) + ~10 s (Unity native) + ~30 s (3-env `pio run` baseline diff) |

---

## Sampling Rate

- **After every task commit:** `cd firestarter && pio run -e uno -e uno328pb -e leonardo` (build sanity) + `cd firestarter_app && pytest -q` (Python sanity).
- **After every plan wave:** `bash /workspaces/.planning/v1.7/baseline-34/verify-detect-34.sh` (byte-diff gate + native dispatch) + `pytest -q` (full Python suite).
- **Before `/gsd-verify-work`:** `verify-detect-34.sh` PASS + `pytest -q` PASS + §8/§9 doc-lint grep PASS.
- **Max feedback latency:** ~45 s for full pre-merge gate (`pio run` 3 envs + native dispatch + pytest).

---

## Per-Task Verification Map

> Final task IDs land in the planner's PLAN.md frontmatter; this map is the requirement → behavior → command anchor that the planner must wire each `<acceptance_criteria>` block against.

| Requirement | Wave | Behavior | Test Type | Automated Command | File Exists | Status |
|-------------|------|----------|-----------|-------------------|-------------|--------|
| DETECT-HW-01 | W1 (meta-repo) | §8 ASCII schematic + per-rev R41 table fills the `<!-- OWNED BY PHASE 34 — TBD -->` marker | doc-lint | `grep -q "## 8\\. Detect-HW Schematic Delta" .planning/v1.7-SHIELD-REVS.md && ! grep -q "OWNED BY PHASE 34 — TBD" .planning/v1.7-SHIELD-REVS.md` | Wave 0/1 | ⬜ pending |
| DETECT-HW-02 | W1 (meta-repo) | §9 per-rev ADC band table seeded with Rev 2.3 + `rev_unknown` fall-through (D-11 schema) | doc-lint | `grep -q "## 9\\. Per-Rev Expected ADC Band Table" .planning/v1.7-SHIELD-REVS.md && grep -q "REVISION_2_3" .planning/v1.7-SHIELD-REVS.md && grep -q "REVISION_UNKNOWN" .planning/v1.7-SHIELD-REVS.md` | Wave 0/1 | ⬜ pending |
| DETECT-FW-01 | W2 (firestarter sub-repo) | ADC band-lookup + handshake reports detected enum + EEPROM fall-through preserved | unit (native) + build | `cd firestarter && pio test -e native -f "*test_dispatch*" && pio run -e uno -e uno328pb -e leonardo && grep -q "REVISION_2_3" firestarter/include/rurp_shield.h && grep -q "analogRead(PIN_HW_REVISION_DETECT_ADC)" firestarter/include/rurp_hw_rev_utils.h` | Wave 0 | ⬜ pending |
| DETECT-FW-02 | W2 (firestarter) + W3 (firestarter_app) | `.hex` size delta in [20, 300] B per env + native dispatch green + Python parity green | byte-diff gate + pytest | `bash /workspaces/.planning/v1.7/baseline-34/verify-detect-34.sh && cd firestarter_app && pytest -q` | Wave 0 (baseline + script land here) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Nyquist Dim 1..8 Coverage

| Dim | Topic | Phase 34 Coverage | Artifact |
|-----|-------|-------------------|----------|
| 1 | Functional (behavioral detect-rev correctness) | **Deferred to Phase 35 operator-on-bench** — Phase 34 surrogate is `pio run -e <env>` exit-0 + grep that new `analogRead` + `if/else` chain exists. Per CONTEXT D-04 Discretion: extending native `src_filter` for `rurp_hw_rev_utils.h` + ArduinoFake mock = post-v1.7. | grep + `pio run` exit-0 |
| 2 | Backward-compat (GATE-1.7 byte-diff per env) | `verify-detect-34.sh` asserts `.hex` Δ in [20, 300] B per env. Below 20 B = rework didn't compile in; above 300 B = unexpected bloat. Phase 33 contrast: that phase expected Δ = 0 B (pure rename) — Phase 34 EXPECTS non-zero Δ. | `verify-detect-34.sh` |
| 3 | Python parity (REVISION_* constants land in `constants.py`) | Hard pytest assertion in `firestarter_app/tests/test_revision_constants_parity.py` — asserts `REVISION_2_3 == 0x05` and `REVISION_UNKNOWN == 0xFE`. Planner picks final test-module placement; existing `make_comm` fixture suffices, no new fixtures. | pytest |
| 4 | Wire format (`MSG_OK_REV` 2-byte frame ID + byte count unchanged) | `tools/catalog/messages.toml` is NOT modified per D-09. Codegen-from-toml check: `grep -q 'MSG_OK_REV' firestarter_app/firestarter/messages.py` returns existing 2-byte entry; no diff lines on that file. | grep + git-diff zero-match |
| 5 | Docs (§8 + §9 schema lock per D-11) | doc-lint grep (rows above) + optional `awk` row-count to assert §9 6-column shape. | grep + awk |
| 6 | Cross-repo invariant (Python REVISION_* byte values match firmware enum byte values) | pytest assertion (Dim 3) + firestarter_app/CLAUDE.md sync-rule prose + Phase 34 SUMMARY doc collectively enforce. No automatable lint into a separate sub-repo git tree. | pytest + prose |
| 7 | EEPROM override precedence unchanged | `rurp_get_hardware_revision()` at `rurp_hw_rev_utils.h:61-67` is **UNCHANGED** — `git diff` should show zero edited lines inside that function body. | git-diff zero-match |
| 8 | Operator-on-bench validation | **Explicitly deferred to Phase 35** — sub-repo `v1.7-shield-investigation` → `beta` promotion at Phase 34 close; `beta` → `main` gated on Phase 35 operator-on-bench (sideload to Rev 2.0 or Rev 2.2 board; chip OUT [[feedback_chip_out_before_sideload]]; port-identity check [[feedback_verify_port_identity_each_task]]). | Phase 35 |

---

## Wave 0 Requirements

- [ ] **Capture pre-Phase-34 `.hex` baseline.** `.planning/v1.7/baseline-34/` (gitignored, mirrors Phase 33 Plan 33-00 substrate). Snapshot `firestarter/.pio/build/<env>/firmware.hex` for each of `uno` / `leonardo` / `uno328pb` after `pio run -e <env>` at branch tip.
- [ ] **Land `verify-detect-34.sh`.** Modeled on Phase 33's `check-migration.sh`. Asserts `.hex` Δ in [20, 300] B per env; runs `pio test -e native -f "*test_dispatch*"`; runs `cd firestarter_app && pytest -q`. Exit non-zero on band-violation.
- [ ] **(Optional, Wave 3) Create `firestarter_app/tests/test_revision_constants_parity.py`** — hard pytest assertion that REVISION_2_3 and REVISION_UNKNOWN exist with the right byte values. If skipped, Dim 3 + Dim 6 coverage degrades to "implicit (Phase 35 catches mismatch on operator-on-bench)".

*Existing pytest + Unity infrastructure is fully in place from Phase 33 and earlier phases — no framework install needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Operator-on-bench detect-rev correctness on physical Rev 2.0 / Rev 2.2 board | DETECT-FW-01 (behavioral) | Requires physical hardware; firmware-flash-then-handshake-read; bench wave gated to Phase 35 per CONTEXT.md `<deferred>` | Phase 35 milestone-close wave: chip OUT → `firestarter fw -i` → power-cycle → `firestarter hw` → confirm `MSG_OK_REV physical = REVISION_2_0 (2)` or `REVISION_UNKNOWN (0xFE)` |
| Rev 2.2 R41 physical measurement (4k7 vs 10k Anders-chat-vs-sch discrepancy) | DETECT-HW-02 (data refinement) | Requires multimeter / scope on operator's physical Rev 2.2 board | Phase 35 follow-up #5; if confirmed 4k7, §9 stays as-is; if 10k, update §3 + §9 only (§8 schematic unchanged) |

---

## Validation Sign-Off

- [ ] All tasks have `<acceptance_criteria>` blocks resolving to one of: doc-lint grep, `pio run` build, pytest assertion, `verify-detect-34.sh` invocation, or git-diff zero-match
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers `verify-detect-34.sh` + baseline `.hex` capture
- [ ] No watch-mode flags in any command (`pytest -q`, `pio test`, `pio run` — all one-shot)
- [ ] Feedback latency < 45 s for full wave-merge gate
- [ ] `nyquist_compliant: true` set in frontmatter once planner has wired all `<acceptance_criteria>` blocks

**Approval:** pending

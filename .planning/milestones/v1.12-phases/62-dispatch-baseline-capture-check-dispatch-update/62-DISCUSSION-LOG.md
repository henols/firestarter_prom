# Phase 62: Dispatch Baseline Capture + check_dispatch Update - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-10
**Phase:** 62-dispatch-baseline-capture-check-dispatch-update
**Areas discussed:** Baseline artifact form, Firmware sub-repo touch, not_implemented semantics, Baseline snapshot scope

---

## Baseline artifact form (GATE-01)

| Option | Description | Selected |
|--------|-------------|----------|
| Golden snapshot + diff-gate | Regenerable all-743 golden file + gate that FAILs on drift (Phase-59 style); strongest regression evidence | |
| Reference snapshot only | One-time committed human-reference snapshot; rely on existing Unity test + pass/fail count assertion as the live pin; no drift-diff gate | ✓ |

**User's choice:** Reference snapshot only
**Notes:** Dispatch surface is small/stable and this is a foundational phase — a full regenerate-and-diff gate is more machinery than warranted. Live regression pin = existing firmware Unity test + the new `not_implemented` FAIL assertion (0 not-implemented chips).

---

## Firmware sub-repo touch (GATE-01 / branching)

| Option | Description | Selected |
|--------|-------------|----------|
| Host-only; defer FW fork | Accept existing test_configure_memory.cpp as the GATE-01 firmware baseline; touch only the app sub-repo; fork firmware v1.12 branch at Phase 63/64 | ✓ |
| Strengthen FW test now | Add pointer-level `configure_eprom` assertion to the FW Unity test now; fork firmware v1.12 branch in Phase 62 | |

**User's choice:** Host-only; defer FW fork (recommended)
**Notes:** Existing `test_protocol_zero_with_mem_type_eprom_dispatches_eprom` + `test_unknown_protocol_with_unknown_mem_type_errors` already pin the legacy + unknown cases. Keeps Phase 62 atomic and defers lockstep branching until firmware actually changes. App sub-repo still on `v1.11-…`; firmware still on `beta` — only the app v1.12 branch is needed this phase.

---

## not_implemented semantics (GATE-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Two distinct buckets | Mirror firmware exactly: `protocol==0`+unknown mem_type stays `ERROR` (MSG_ERR_MEM_TYPE_UNSUPPORTED); `protocol!=0`+unrecognized → `not_implemented` (MSG_ERR_PROTOCOL_NOT_IMPLEMENTED) | ✓ |
| Single collapsed bucket | Fold both failures into one not_implemented bucket; simpler but diverges from firmware's two response codes | |

**User's choice:** Two distinct buckets (recommended)
**Notes:** Keeps the gate's diagnostics aligned with firmware's two distinct response codes.

---

## Baseline snapshot scope (GATE-01)

| Option | Description | Selected |
|--------|-------------|----------|
| Dispatch triple | `part → {algorithm, mem_type, resolved handler}`; focused on dispatch, leaves VPP to Phase 66 | ✓ |
| Include vpp_mv / wire fields | Also record vpp_mv + wire fields; doubles as broader regression evidence but conflates dispatch + VPP baselines and trips on Phase 66's intentional VPP corrections | |

**User's choice:** Dispatch triple (recommended)
**Notes:** `check_dispatch.py` already asserts wire `vpp_mv` presence per chip; VPP regression is Phase 66's surface.

---

## Claude's Discretion

- Snapshot file format/location/filename within `firestarter_app`.
- Precise arrangement of explicit `0x35`/`0x39` cases vs. the `protocol != 0` arm in `dispatch()` — constrained by mirroring `memory.cpp::configure_memory` order, with the `not_implemented` arm after all explicit protocol cases and before the `protocol == 0` mem_type fallback.

## Deferred Ideas

- Strengthen firmware Unity dispatch test with a pointer-level `configure_eprom` assertion → Phase 64 (TEST-01).
- Golden-snapshot regenerate-and-diff dispatch gate (Phase-59 style) → not adopted; revisit only if dispatch logic grows.
- `vpp_mv` / wire-field regression baseline → Phase 66 (DB VPP correction).

---
phase: 93
slug: rca-root-cause-the-w29c040-page-0-write-fault
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-26
---

# Phase 93 — Validation Strategy

> Per-phase validation contract. **This is an RCA (diagnosis) phase — there is no production code to test.** "Validation" here means: the evidence/measurement that proves the named root cause is *correct* (or that a hypothesis is *disconfirmed*). The bench disconfirming-test matrix from `93-RESEARCH.md` IS the test map. See `93-RESEARCH.md` § "Validation Architecture" and § "Root-Cause Classification (RCA-03)".

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Bench instrumentation (in-tree): `firestarter` CLI `dev write-cycle` / `dev read` / `dev reg` / `dev addr` + passive `-D DEBUG_ADDRESS` trace build. No new test framework. |
| **Config file** | none — all instrumentation already in firmware/host |
| **Quick run command** | `firestarter write <img> <chip> ...` on the seated W29C040 (capture serial `ERROR:`/`DATA:` frames) |
| **Full suite command** | The 5-test cheapest-first disconfirming matrix (single-byte page-0 → per-byte cadence → A18 → SDP re-arm → silicon/wear) per `93-RESEARCH.md` |
| **Estimated runtime** | bench-bound (operator-witnessed; minutes per disconfirming test) |

---

## Sampling Rate

- **After every disconfirming test:** Record the verdict (confirms / disconfirms which hypothesis) + the raw serial signature into `evidence/93-RCA-FINDINGS.md`.
- **Per standing bench discipline:** live R1/R2 readback + `controller:` port-identity verification recorded per task; never trust N=1 (repeat the repro to confirm determinism).
- **Before RCA close:** the named root cause (or ranked hypotheses) must carry disconfirming evidence for every rejected alternative.
- **Max feedback latency:** one bench cycle.

---

## Per-Task Verification Map

| Task ID | Requirement | Evidence / Disconfirming Test | Test Type | Pass Condition | Status |
|---------|-------------|-------------------------------|-----------|----------------|--------|
| repro | RCA-01 | Re-run the historical write; capture which addresses/bytes fail + DQ7/DQ6 poll behavior at the failure | manual (bench) | Fault reproduces N≥2 deterministically with recorded signature (baseline `ERROR "Timeout verifying 0xd7 at 0x0000ff (got 0x00)"` or equivalent) | ⬜ pending |
| diff | RCA-02 | W29C040-vs-W29C020 across SDP / page-write timing / A18 512 KB addressing / page-size; exonerate the unchanged axes | manual (bench + datasheet) | Differing variable(s) isolated; unchanged axes carry disconfirming evidence | ⬜ pending |
| classify | RCA-03 | Surviving hypothesis named + classified (firmware-algorithm / timing / addressing / silicon); each rejected hypothesis carries disconfirming evidence | manual (bench) | One named cause OR ranked hypotheses, each with disconfirming evidence; detailed enough to design Phase 94 fix | ⬜ pending |
| safety | SAFE-01 | Firmware VPP check stays blocking; host `chip_resolver.resolve_chip` guard never bypassed; confirm `FLAG_CAN_ERASE` not set for W29C040 | manual (source + bench) | No test-only escape hatch used; W29C040 flows through normal dispatch | ⬜ pending |

*Status: ⬜ pending · ✅ confirmed · ❌ disconfirmed · ⚠️ inconclusive (N=1)*

---

## Wave 0 Requirements

*Existing in-tree instrumentation covers all RCA evidence capture — no new test scaffolding required. The W29C040 and W29C020 datasheets are already committed under `firestarter/datasheets/0x05-FLASH-AMD-STD/` (per research; STATE.md "no datasheet" note is stale).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Page-0 write fault reproduction + signature capture | RCA-01 | Requires seated W29C040 on Leonardo + Rev 2.0 (operator-witnessed bench) | Run controlled write; record failing addresses/bytes + DQ7/DQ6 poll at fault |
| Differential against passing W29C020 | RCA-02 | Requires both physical chips on the bench | Repeat write path on W29C020 sibling; compare per-axis |
| Hypothesis disconfirming matrix | RCA-03 | Bench-only measurement (timing/addressing/silicon) | Execute cheapest-first 5-test matrix; record verdict per hypothesis |

*All Phase 93 verifications are hardware-gated and operator-witnessed by the nature of an RCA on real silicon.*

---

## Validation Sign-Off

- [ ] Every RCA requirement (RCA-01/02/03, SAFE-01) maps to a recorded evidence artifact in `evidence/93-RCA-FINDINGS.md`
- [ ] Reproduction is deterministic (N≥2) — no N=1 conclusions
- [ ] Every rejected hypothesis carries disconfirming evidence (not just "untested")
- [ ] SAFE-01 confirmed: no escape hatch, VPP check intact, `FLAG_CAN_ERASE` checked
- [ ] `nyquist_compliant: true` set in frontmatter once the evidence map is complete

**Approval:** pending

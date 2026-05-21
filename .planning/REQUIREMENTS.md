# Requirements — Milestone v1.6: Fix the Read Bug

**Status:** Active — defined 2026-05-21 at milestone start; phase-mapped 2026-05-21 by roadmapper.
**Milestone goal:** Root-cause and fix the 64KB streaming-read byte-jitter surfaced by Phase 24 bench rigor; restore byte-identical full-chip read-back across `uno`, `leonardo`, and `uno328pb`.

**Source backlog item:** `.planning/todos/pending/large-read-data-jitter-uno328pb.md` (HIGH priority; pre-existing latent bug, all 3 controllers).

## v1.6 Requirements

### Reproduction & Triage (REPRO)

- [x] **REPRO-01**: Operator can reproduce 64KB read-jitter on `uno` (not just `uno328pb`) — consecutive `firestarter read <chip> file.bin` against a static chip yields different SHA-256 hashes
- [x] **REPRO-02**: Operator can reproduce 64KB read-jitter on `leonardo` (1024-byte buffer board; magnitude may differ but bug must be present or explicitly proven absent)
- [x] **REPRO-03**: A reusable "consecutive-read consistency" diagnostic script lives in the host CLI (e.g. `firestarter dev consistency-check <chip> --runs N`) so the bug — and its eventual fix — is verifiable by anyone with hardware

### Root Cause (RCA)

- [ ] **RCA-01**: The exact code path that introduces byte corruption is identified with concrete evidence (instrumented firmware build, code-path bisection, or a minimal reproducer narrowing the bug to a single function / chunk boundary)
- [ ] **RCA-02**: A written explanation of WHY the corruption happens (timing window, missed ACK, buffer overflow, etc.) is captured in the planning trail — sufficient for a future reader to understand the bug without re-bisecting
- [ ] **RCA-03**: The introducing commit (or earliest version with the bug) is identified via `git log -L` / `git bisect` where reasonably possible — at minimum bracketed to a milestone (v1.0 vs v1.2 vs v1.4)

### Fix (FIX)

- [ ] **FIX-01**: Implementation lands in firestarter sub-repo and/or firestarter_app sub-repo (whichever sides the RCA points at); covered by atomic commits with the RCA evidence cited in the commit message
- [ ] **FIX-02**: A native unit test (Unity for firmware, pytest for host) exercises the specific code path the fix touches and would fail on the pre-fix code
- [ ] **FIX-03**: GATE-1.6 — the fix does not regress the write path; `firestarter write` + post-write `dev read -s N` byte-comparison still passes on at least one bench chip (already proven stable in Phase 24)

### Verification (VERIFY)

- [ ] **VERIFY-01**: Post-fix `firestarter read <chip> file.bin` invoked **N≥5 consecutive times** against the same physically-static chip returns byte-identical SHA-256 hashes on `uno328pb`
- [ ] **VERIFY-02**: Same N≥5 consecutive-read consistency check passes on `uno` and `leonardo`
- [ ] **VERIFY-03**: `firestarter dev read <chip> -s 1024` byte-identical across N≥5 consecutive calls on all 3 boards (the low-rate jitter must also resolve — if it doesn't, the root cause isn't truly fixed)
- [ ] **VERIFY-04**: Phase 24 BENCH-02 acceptance criterion ("write→read→verify on a representative EPROM") closes as a side effect — recorded in `.planning/v1.5-BENCH-RESULTS.md` (post-hoc row addendum)

### Documentation & Close (DOC, MS)

- [ ] **DOC-01**: `large-read-data-jitter-uno328pb.md` todo moved out of `.planning/todos/pending/` (resolved); root-cause summary + fix commit reference recorded
- [ ] **DOC-02**: PROJECT.md "Known Gaps" / "Validated" sections updated to reflect the fix
- [ ] **MS-01**: Milestone v1.6 closed via `/gsd:complete-milestone`; MILESTONES.md entry written; phase artifacts archived under `.planning/milestones/v1.6-phases/`

## Future Requirements (deferred to later milestones)

- Chip database misclassification fix for W27C/E + SST27SF/VF series (`w27c512-eeprom-misclassification.md`) — HIGH priority, operator-tagged "asap", but different bug class (DB routing, not transport). Carry to v1.7 or own milestone.
- avrdude-based MCU-detection fallback for blank-chip recovery (`avrdude-mcu-detection-fallback.md`) — low priority, v1.7+.
- v1.1 Phase 4 FM1608 byte-0 read-bug — separate hardware-gated investigation, parked since 2026-05-18; if v1.6 RCA happens to overlap, address as a bonus; otherwise leave parked.

## Out of Scope

- New chip support, new board target, new firmware features
- v1.3 CMOS EPROM Family Hardware Validation resume (separate paused milestone, hardware-gated)
- Any host-CLI feature work beyond what's strictly needed for REPRO-03 (the consistency-check diagnostic) and the fix itself
- Beta release pipeline / lockstep coordination changes (v1.4 plumbing stays as-is)
- Any RURP shield hardware redesign — three-shield A/B/C triage already proves the bug is firmware/host, not hardware

## Traceability

Phase mappings locked 2026-05-21 by `/gsd-roadmap` — every v1.6 requirement maps to exactly one phase. No orphans, no duplicates. Coverage: 16/16 ✓.

| REQ-ID | Phase |
|--------|-------|
| REPRO-01 | Phase 26 |
| REPRO-02 | Phase 26 |
| REPRO-03 | Phase 26 |
| RCA-01   | Phase 27 |
| RCA-02   | Phase 27 |
| RCA-03   | Phase 27 |
| FIX-01   | Phase 28 |
| FIX-02   | Phase 28 |
| FIX-03   | Phase 28 |
| VERIFY-01 | Phase 29 |
| VERIFY-02 | Phase 29 |
| VERIFY-03 | Phase 29 |
| VERIFY-04 | Phase 29 |
| DOC-01   | Phase 30 |
| DOC-02   | Phase 30 |
| MS-01    | Phase 30 |

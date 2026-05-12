---
phase: 03
slug: retroactive-verification-phases-01-10
status: draft
nyquist_compliant: false
wave_0_complete: true
created: 2026-05-12
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

This phase produces 10 markdown audit artifacts (`NN-VERIFICATION.md` for v1.0
phases 01..10) under `.planning/milestones/v1.0-phases/`. **No source code is
touched.** Behavioral proof is cited from existing test suites — Phase 3 does
not author new automated tests.

See `03-RESEARCH.md` §"Validation Architecture" for the full Nyquist boundary
narrative.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Static evidence verification (grep-based) |
| **Config file** | none — uses repo grep + git ls-files |
| **Quick run command** | `grep -n <symbol> <file>` for each cited file:line in a VERIFICATION.md |
| **Full suite command** | Per-file YAML+Markdown lint (frontmatter parse + heading scan) |
| **Estimated runtime** | < 5 seconds per file (grep is the limit) |

**Behavioral test suites cited (not re-run):**

| Behavior under test | Existing asset | Last result |
|---------------------|----------------|-------------|
| Algo-first dispatch (all KNOWN_PROTOCOLS) | `firestarter/test/native/avr/test_dispatch/` | 15/15 PASS — see `01-VERIFICATION.md` |
| Intel-flash VPP ADC compare (REQ-SAF-01) | `firestarter/test/native/avr/test_flash_intel_vpp/` | 6/6 PASS — see `01-VERIFICATION.md` Truth #3 |
| 28C chip-ID check (REQ-SAF-02) | `firestarter/test/native/avr/test_eeprom28c_chip_id/` | 4/4 PASS — see `01-VERIFICATION.md` Truth #4 |
| 743-chip wire round-trip + dispatch (REQ-DB-01..04, FW-01..06, WIRE-01/02) | `firestarter_app/tools/check_dispatch.py` | exit 0 — see `02-VERIFICATION.md` SC4 |
| AVR firmware budget (uno + leonardo) | `pio run -e uno`, `pio run -e leonardo` | both SUCCESS — see `12-VERIFICATION.md` |
| WARNING-5 data-layer guard (AT28C family) | `_28C_EEPROM_HAZARD_PINOUT` in `check_dispatch.py` | exit 0 — see `13-VERIFICATION.md` Truth #5 |

---

## Sampling Rate

- **After every task commit:** Static — confirm every `file:line` cited in the just-written VERIFICATION.md resolves via `grep -n` against the live tree.
- **After every plan wave:** YAML+Markdown lint each of the just-written files; confirm frontmatter `phase:` matches the directory basename; confirm `requirements_verified` is a subset of the audit's `gaps.requirements` for that phase.
- **Before `/gsd-verify-work`:** All 10 files present; all frontmatter `status: passed` (or `gaps_found` with explicit explanation); all `requirements_verified` lists complete coverage of VERIF-01..VERIF-10's phase scope.
- **Max feedback latency:** < 10 seconds per file.

---

## Per-Task Verification Map

> The per-task verification map is "did the file land, with valid frontmatter,
> with every cited `file:line` resolvable, and with the right REQ-IDs". One
> row per VERIFICATION.md deliverable.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | VERIF-01 | — | N/A (doc) | static | `test -f .planning/milestones/v1.0-phases/01-database-pipeline/01-VERIFICATION.md && head -1 $_ \| grep -q '^---'` | ✅ at write | ⬜ pending |
| 03-01-02 | 01 | 1 | VERIF-02 | — | N/A (doc) | static | `test -f .planning/milestones/v1.0-phases/02-firmware-json/02-VERIFICATION.md && head -1 $_ \| grep -q '^---'` | ✅ at write | ⬜ pending |
| 03-01-03 | 01 | 1 | VERIF-04 | — | N/A (doc) | static | `test -f .planning/milestones/v1.0-phases/04-flash-sector-erase/04-VERIFICATION.md && head -1 $_ \| grep -q '^---'` | ✅ at write | ⬜ pending |
| 03-01-04 | 01 | 1 | VERIF-08 | — | N/A (doc) | static | `test -f .planning/milestones/v1.0-phases/08-integration/08-VERIFICATION.md && head -1 $_ \| grep -q '^---'` | ✅ at write | ⬜ pending |
| 03-01-05 | 01 | 1 | VERIF-09 | — | N/A (doc) | static | `test -f .planning/milestones/v1.0-phases/09-adapter-support/09-VERIFICATION.md && head -1 $_ \| grep -q '^---'` | ✅ at write | ⬜ pending |
| 03-02-01 | 02 | 2 | VERIF-03 | — | N/A (doc) | static | `test -f .planning/milestones/v1.0-phases/03-eprom-algorithms/03-VERIFICATION.md && head -1 $_ \| grep -q '^---'` | ✅ at write | ⬜ pending |
| 03-02-02 | 02 | 2 | VERIF-05 | — | N/A (doc) | static | `test -f .planning/milestones/v1.0-phases/05-intel-flash/05-VERIFICATION.md && head -1 $_ \| grep -q '^---'` | ✅ at write | ⬜ pending |
| 03-02-03 | 02 | 2 | VERIF-06 | — | N/A (doc) | static | `test -f .planning/milestones/v1.0-phases/06-eeprom-page-write/06-VERIFICATION.md && head -1 $_ \| grep -q '^---'` | ✅ at write | ⬜ pending |
| 03-02-04 | 02 | 2 | VERIF-07 | — | N/A (doc) | static | `test -f .planning/milestones/v1.0-phases/07-chip-id-safety/07-VERIFICATION.md && head -1 $_ \| grep -q '^---'` | ✅ at write | ⬜ pending |
| 03-02-05 | 02 | 2 | VERIF-10 | — | N/A (doc) | static | `test -f .planning/milestones/v1.0-phases/10-static-pins/10-VERIFICATION.md && head -1 $_ \| grep -q '^---'` | ✅ at write | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**Per-task acceptance criteria** (applied in each plan task body, not duplicated here):
- File exists at the exact `.planning/milestones/v1.0-phases/{NN-slug}/NN-VERIFICATION.md` path.
- YAML frontmatter parses; `phase:` matches `NN-<slug>`; `requirements_verified:` is the subset of `gaps.requirements` for that phase from `v1.0-MILESTONE-AUDIT.md`.
- Every `file:line` cited in the body resolves via `grep -n` against the live source tree (line numbers may shift on re-grep; the resolve-at-write-time rule from CONTEXT.md D-09 applies).
- For 05-VERIFICATION.md (SC#3) and 10-VERIFICATION.md (SC#4): the explicit locks are present and grep-verifiable.
- For 03/06/07-VERIFICATION.md: WARNING-5 `follow_ups` entry present.
- For 08-VERIFICATION.md: WARNING-4 `follow_ups` entry present.

---

## Wave 0 Requirements

*None.* Test infrastructure pre-exists. The four exemplars
(`01/02/11/12/13-VERIFICATION.md`) supply the canonical template. The
`.planning/` tree is the only thing this phase writes to.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Cross-Milestone Closure narratives correctly cite v1.1 closure paragraphs | VERIF-01 (DB-03), VERIF-05 (SAF-01 Intel), VERIF-07 (SAF-02) | Narrative correctness; not statically checkable | Reviewer reads each affected VERIFICATION.md and confirms the cited paragraph in the linked v1.1 PLAN/SUMMARY/VERIFICATION matches the claim. |
| `follow_ups` `note:` field correctly attributes deferrals (v1.2 for WARNING-5; Phase 4 / HW-01 for WARNING-4) | VERIF-03, -06, -07 (WARNING-5); VERIF-08 (WARNING-4) | Attribution is editorial | Reviewer confirms the `note:` text matches MILESTONES.md and the deferral target's scope. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify (static grep) or are Wave 0 deps (Wave 0 is empty)
- [x] Sampling continuity: every task has automated frontmatter + file-existence check
- [x] Wave 0 covers all MISSING references (none — exemplars suffice)
- [x] No watch-mode flags
- [x] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter — **deliberately false** for this phase. Per CONTEXT.md "Deferred Ideas" and ROADMAP wording, Phase 3 takes the "equivalent retroactive audit" path; Nyquist gap-filler test-generation is explicitly out of scope. The doc-only acceptance criteria above satisfy the phase contract.

**Approval:** pending

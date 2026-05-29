---
status: passed
phase: 43-documentation-milestone-close
verified: 2026-05-29
requirements: [DOC-01, DOC-02, MS-01]
verdict: passed
must_haves_verified: 23/23
human_witnessed: true
---

# Phase 43 Verification — v1.8 Documentation & Milestone Close

**Verdict: PASSED** (goal-backward; human-witnessed real-hardware + operator-authorized branch promotion).

Phase goal: close the v1.8 "Host CLI Structural Cleanup" milestone — ship contributor
docs (DOC-01), flip planning ship-state + archive the milestone (DOC-02), and verify
GATE-1.8 end-to-end then promote the branches (MS-01).

## DOC-01 — README + CLAUDE.md contributor docs (Plan 43-01) ✓

- `firestarter_app/README.md` grew a single `## Architecture` section (21 modules across 5
  layers + layer-boundary rules + tooling workflow); TOC/Install/Usage/Examples byte-identical.
  Verified on `main`: `grep -c '^## Architecture$'` = 1.
- `firestarter_app/CLAUDE.md` received exactly 3 targeted edits (de-singleton `database.py`
  line + `skip_local_override` seam; 6 new Key Files entries; tooling-gate one-liner). Data
  Flow / Wire Protocol / DB Pipeline / Constants blocks byte-identical.
- Shipped to `beta` and into `3.0.0b7`. firestarter_app commit `aaa45e0` (meta gitlink) /
  beta `4f04d98`.

## DOC-02 — Ship-state flip + milestone archive (Plans 43-01 + 43-02) ✓

- `.planning/PROJECT.md`: v1.8 ship-history line (2026-05-29), Current Milestone flipped to
  v1.9-PROPOSED, v1.8 Archive section, footer refreshed.
- `.planning/MILESTONES.md`: new v1.8 entry (8 sections, ship tag 3.0.0b7 LOCKED).
- `.planning/ROADMAP.md`: v1.8 section (~301 lines) collapsed into a `<details>` shipped-archive
  block mirroring v1.5/v1.6/v1.7.
- `.planning/milestones/v1.8-REQUIREMENTS.md`: 30-row coverage archive (27 DELIVERED + 3
  VERIFIED-AT-CLOSE), 136 lines.
- 8 phase dirs (36–43) archived to `.planning/milestones/v1.8-phases/` via `v1.8-archive.sh`;
  paused v1.3 dirs (11/12) + prior milestone archives untouched.
- All `<TBD-from-43-03>` tokens substituted (0 residual in the 4 live artifacts).

## MS-01 — GATE-1.8 end-to-end + branch promotion (Plan 43-03, human-witnessed) ✓

**GATE-1.8 BOTH-path (D-08):**
- Software floor (43-01 pre-flight): pytest 382 passed, ruff clean, ruff-format clean, mypy
  strict on 8 modules, entry-point smoke OK, coverage **70.64%** (≥70%). NOTE: initial run
  aborted at 69.49% (<70%); restored via `firestarter_app@8d6bc6c` (17 targeted tests on
  real uncovered branches). D-08 abort policy worked as designed.
- Real-hardware Step 0 (operator bench, W27C512 on Modified Rev 0 + Leonardo, FW
  3.0.0b4:leonardo): **PASS on the authoritative zero-byte-ratio metric** (0.018–0.021%,
  better than baselines; <1.00% threshold). Within-session drift envelope (431–483 B) matches
  the v1.6 baseline within-session envelope (373–457 B); Bug A upper-address (A15=1) signature
  reproduced. The strict cmp-vs-baseline >656 B is cross-session Bug A drift, not a regression
  (firmware unchanged at 0bbe017; read path ring-fenced + wire-byte-identical at unit level).
  Operator authorized PASS.

**Branch promotion (operator-authorized):**
- firestarter_app `v1.8-app-cleanup` → `beta` (merge `0d9e119`); 3 pre-existing post-merge CI
  defects fixed on beta (version-agnostic snapshot `e08d64a`; ruff-normalized codegen drift
  gate + `.[dev]`→`.[test]` `c937a81`; traceback-line-number scrub `9fcb437`); beta CI green;
  **3.0.0b7 published to PyPI + GitHub pre-release**; beta tip `4f04d98`. Ship tag LOCKED
  3.0.0b7 beta-only per D-09 (stable 3.0.1 deferred to v1.9 per D-17v2).
- Firmware sub-repo VERIFY NO-OP: `firestarter` `beta` still `0bbe017`; no v1.8 commits/tags.
- Meta-repo `v1.8-app-cleanup` → `main` (merge `305e525`, close `f21c950`, pushed).
- STATE.md flipped to v1.8-SHIPPED / v1.9-PROPOSED.

## Notable findings (for v1.9 / backlog)

- The full `beta-release.yml` CI path was never exercised during Phases 36–42 (only `ci.yml`),
  so three latent defects surfaced only at the v1.8 cut: (1) the codegen drift gate vs the
  Phase 37 ruff `--add-noqa` baseline on the generated `messages.py`; (2) `beta-release.yml`
  installing `.[dev]` (no syrupy/ruff) while the v1.8 suite needs `.[test]`; (3) characterization
  snapshots pinning version strings + library traceback line numbers. All fixed on beta;
  consider running beta-release CI earlier in future milestones.
- Read-bug (Bug A + Bug B) carries to v1.9 under the GATE-1.8d ring-fence, unchanged.

# Phase 29: Multi-Board Bench Verification - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-22 (v1) + 2026-05-26 (v2 re-iteration)
**Phase:** 29-multi-board-bench-verification
**Mode:** Auto Mode (harness Auto Mode active — gray areas auto-resolved with recommended options; no AskUserQuestion prompts)
**Areas discussed:**
- v1 (2026-05-22): uno328pb row strategy, Pre-release cut procedure (CORRECTED to local sideload), N count, Plan structure (CORRECTED — no merge in Phase 29), VERIFY-03 mechanism, VERIFY-04 chip + procedure, Fail-handling protocol, EVIDENCE.md schema, Test chip selection, Shield-rev recording, BENCH-02 addendum format
- v2 (2026-05-26): Success-criteria reshape (revert vs byte-identity), Plan 28-04 gate signal, Wave shape simplification (Leonardo-only), EVIDENCE.md re-iteration schema, Plan numbering (29-03/04 vs overwrite), uno328pb deferral to v1.8, BENCH-02 deferral to v1.8, FAIL semantics re-mapping

**Operator correction (2026-05-22):** initial CONTEXT placed the `v1.6-read-bug → beta` merge in Wave A (BEFORE bench verification), which would have polluted the public release channel if the fix failed on bench. Corrected to local-sideload model — Phase 29 builds firmware locally from `v1.6-read-bug`, sideloads via `pio run -t upload` (or `avrdude -c urclock`), and stays entirely off-remote. Phase 30 (which ROADMAP SC#5 already designates as the branch-promotion phase) picks up the public merge + pre-release cut + main promotion once Phase 29 verdict is green.

---

## Re-iteration overlay (2026-05-26) — Post-revert bench gate

Phase 29 v1 (2026-05-22) FAILED on Leonardo + uno328pb (D-07 milestone-reopens). Phase 27 RCA re-opened (Plan 27-05, closed 2026-05-26) with dual-cause disposition: Leonardo regression caused by Phase 28 v1 firmware (Outcome A); uno328pb regression confirmed independent pre-existing hardware issue (Outcome B). Phase 28 re-iterated 2026-05-26 with single revert of `437339b6` (Plan 28-03, `ea25174`+`efd203a`); second revert of `4f205e58` (Plan 28-04) parked drafted-but-not-executed pending Phase 29 v2 bench signal.

Re-iteration mode: same auto-mode no-AskUserQuestion-prompts approach as v1; reasonable calls made for each new gray area introduced by the re-iteration scope.

### Success-criteria reshape (D-21v2)

| Option | Description | Selected |
|--------|-------------|----------|
| Leonardo shape = Phase 26 baseline (structured-data + ~0.44% jitter) | Phase 29 v2 verifies the revert removed the regression; gate is shape classification, not SHA-256 byte-identity. Read bug itself defers to v1.8 per D-17v2 milestone re-scope. | ✓ |
| Leonardo byte-identical SHA-256 across N=5 (original v1 D-08 gate) | Preserves v1 verdict cell semantics; but would FAIL even with a perfect revert because the original ~0.44% read jitter is the Phase 26 baseline bug (which v1.6 no longer attempts to fix). | |
| Skip Leonardo gate entirely; close v1.6 on Plan 28-03 desk-side evidence alone | Phase 28 re-iteration verification (5/5) already passed desk-side; bench could be deferred. But Plan 28-04 gate signal needs a bench source to evaluate. | |

**Selected:** Leonardo shape = Phase 26 baseline (auto — only option consistent with D-17v2 re-scope + Plan 28-04 gate contract).
**Notes:** Phase 26 baseline Leonardo on Modified Rev 0 + voltage-divider mod + W27C512 produced ~0.44% jitter (structured-data). v2's gate verifier classifies via zero-byte ratio (≤1% threshold) + qualitative shape against the Phase 26 archived run binaries.

### Plan 28-04 gate signal emission (D-22v2)

| Option | Description | Selected |
|--------|-------------|----------|
| Triple-state emission: pass_parked / activate / needs_human | Wave B v2 verifier emits one of three states to `.planning/v1.6/phase-28-reiteration-verdict.txt` + EVIDENCE.md placeholder. Auto-activate only on clear zeros-dominant; escalate ambiguous cases. | ✓ |
| Binary emission: pass / fail | Simpler but loses the ambiguous-case escalation path; risks auto-activating Plan 28-04 on noisy intermediate verdicts. | |
| Operator-only emission (no auto-emit) | Verifier suggests; operator decides. But Plan 28-04's `executes_only_if` predicate requires a machine-readable signal. | |

**Selected:** Triple-state (auto — preserves Plan 28-04's conditional contract while allowing human escalation on edge cases).
**Notes:** Zero-byte ratio thresholds — ≤1% = structured (pass_parked); >30% = zeros-dominant (activate); 1-30% = ambiguous (needs_human). Phase 29 v1 Attempts 1+2 both saw >80% zeros on Leonardo; the 30% conservative threshold captures clear failure.

### Wave shape simplification (D-23v2)

| Option | Description | Selected |
|--------|-------------|----------|
| Leonardo-only rebuild + bench | Build only `firestarter_leonardo.hex` from `efd203a`; sideload + verify Leonardo only. uno328pb deferred (D-29v2); uno code-path Δ=0 (regression check carries from Phase 26). | ✓ |
| Rebuild all 3 envs + verify all 3 boards (v1 shape) | Mirrors v1 D-04 plan structure; but uno328pb is deferred so its build is wasted, and uno hex Δ=0 so its bench rerun is non-gating. ~75 min vs ~30 min on bench. | |
| Skip Wave A rebuild; reuse v1's `4f205e58` hex artifacts | Faster but tests the WRONG firmware (`4f205e58`, the broken v1 fix, not the reverted `efd203a`). | |

**Selected:** Leonardo-only (auto — only option that tests the correct firmware while respecting deferrals).
**Notes:** Wave A v2 sanity-checks the Leonardo build SHA against the Phase 28 re-iteration Axis 4 post-prune expected value (`734b9a85…`) to confirm the local build matches the post-revert state Phase 28 desk-side verified.

### Plan numbering (D-25v2)

| Option | Description | Selected |
|--------|-------------|----------|
| New plans 29-03 (Wave A v2) + 29-04 (Wave B v2); 29-01/02 stay as audit trail | Mirrors Phase 28 re-iteration's 28-03/04 pattern; preserves immutable FAIL evidence; ROADMAP plan list grows. | ✓ |
| Overwrite 29-01/02 plans + SUMMARYs in-place | Destroys the D-07 FAIL audit trail that the milestone-reopens verdict + Phase 27 re-open + Phase 28 re-iteration are anchored to. | |
| Branch 29-v2 directory parallel to 29-multi-board-bench-verification | Adds directory-discovery complexity; no precedent in the project structure. | |

**Selected:** New plans 29-03 + 29-04 (auto — only audit-preserving option that matches Phase 28's re-iteration precedent).
**Notes:** `/gsd-plan-phase 29 --gaps` should produce 29-03/04 without touching 29-01/02. ROADMAP Phase 29 plan list grows: `[x] 29-01 (v1 Wave A)`, `[x] 29-02 (v1 Wave B — FAIL)`, `[ ] 29-03 (v2 Wave A)`, `[ ] 29-04 (v2 Wave B)`.

### uno328pb deferral handling (D-29v2)

| Option | Description | Selected |
|--------|-------------|----------|
| DEFERRED to v1.8 with explicit "independent pre-existing hardware regression" verdict | Memory `[[project_uno328pb_bench_instability_27_04]]` + Plan 27-04 falsifier `d9e51b7e…` over-determines this is not a Phase 28 firmware issue; v1.7 substrate (shipped 2026-05-26) provides v1.8 RCA foundation. | ✓ |
| Re-run v1 D-01 reflash test on uno328pb | v1 D-01 was designed for the v1.5 "misidentified board" question, which is now obsolete — operator confirmed the board has real ATmega328PB silicon; the issue is bench-instability, not misidentification. | |
| Mark uno328pb VERIFY-01 closed via code-equivalence with Uno (v1 D-01 Case B fallback) | Would close the requirement on the strength of `.hex` Δ=0, but the bench-instability is a hardware-level issue that the code-equivalence argument doesn't address. Honest deferral is cleaner. | |

**Selected:** DEFERRED to v1.8 (auto — only option consistent with the dual-cause Plan 27-05 disposition).
**Notes:** EVIDENCE.md Verdict block explicitly writes the deferral with `[[project_uno328pb_bench_instability_27_04]]` + Plan 27-04 falsifier reference + v1.7 forward-link.

### BENCH-02 (VERIFY-04) reframing (D-30v2)

| Option | Description | Selected |
|--------|-------------|----------|
| DEFERRED to v1.8 alongside read-bug fix | Read bug must be fixed before write→read→verify is meaningful; revert restores Phase 26 baseline jitter (~0.44%), which would fail `cmp`. GATE-1.6 write-path already desk-side-confirmed via Axis 4. | ✓ |
| Run BENCH-02 in v2 as bonus diagnostic | Would confirm write path observably still works; but `cmp` would FAIL even on a perfect revert because the original read bug is unfixed. Diagnostically uninformative for v1.6 ship gate. | |
| Run BENCH-02 with small-window-write workaround (v1 D-06 fallback path) | Even with the workaround, the small-window readback would carry ~0.44% jitter from the unfixed read bug. Operator could visually inspect, but no clean PASS/FAIL signal. | |

**Selected:** DEFERRED to v1.8 (auto — only option consistent with D-17v2 milestone re-scope).
**Notes:** v1.5 BENCH-02 row stays at "closed with caveat" until v1.8 ships the actual read-bug fix.

### FAIL semantics re-mapping (D-28v2)

| Option | Description | Selected |
|--------|-------------|----------|
| Triple-state outcomes: pass_parked / activate / needs_human (auto-recover via Plan 28-04) | A first-revert FAIL is NOT milestone-reopens — Plan 28-04 is the designed recovery. Only a both-reverts-FAIL outcome triggers true milestone-reopens. | ✓ |
| Preserve v1 D-07 "any FAIL → milestone reopens" | Correct for v1's "fix the bug" goal; wrong for v2's "revert broken fix" goal because Plan 28-04 IS the recovery path. | |
| Halt on any FAIL; require human re-discussion | Defensive but loses the Plan 28-04 conditional-contract value. | |

**Selected:** Triple-state outcomes (auto — only option that respects Plan 28-04's conditional contract).
**Notes:** Plan 29-04 verifier task explicitly documents the triple-state map + the "true milestone-reopens" condition (Plan 28-04 lands + Phase 29 v2 re-runs + STILL zeros).

---

## Phase 29 v1 discussion log (preserved verbatim below)

---

## uno328pb row strategy (D-01)

The carried-over VERIFY-01 mismatch from Phase 26 — the board labeled `uno328pb` was operator-clarified as a Plain Uno + wrong firmware per `[[project_uno328pb_correction]]`, leaving REQUIREMENTS.md VERIFY-01 mapped to a board that may not exist as advertised.

| Option | Description | Selected |
|--------|-------------|----------|
| Reflash-then-test; fall back to code-equivalence DEFERRAL | Reflash misidentified board with `firestarter_uno328pb.hex` from post-fix pre-release. Case A (handshake reports `uno328pb`): run full verification. Case B (handshake reports `uno` / signature mismatch): mark DEFERRED with code-equivalence rationale citing Phase 28 hex size Δ=0 between uno + uno328pb builds. | ✓ |
| Claim VERIFY-01 closes by code-equivalence alone | Skip the reflash test; argue uno328pb path is byte-identical to uno per Phase 28 size table; close on Uno's verdict propagation. | |
| DEFER VERIFY-01 to a future milestone | No true 328PB silicon reachable; carry as known-gap into v1.7+. | |

**Selected:** Reflash-then-test; fall back to code-equivalence DEFERRAL (auto — recommended default).
**Notes:** Reflash is cheap (operator already owns v1.5 BENCH-01 procedure on `/dev/ttyUSB0` via `urclock` bootloader). Either outcome resolves the row explicitly; silently skipping leaves a coverage gap.

---

## Local-sideload procedure (D-02) — CORRECTED after operator feedback

When and how is the post-fix firmware made bench-installable?

| Option | Description | Selected |
|--------|-------------|----------|
| ~~Standard v1.4 beta workflow — merge `v1.6-read-bug` → `beta` triggers automated pre-release cut at Wave A start~~ | Both sub-repos merge → CI cuts GitHub Pre-release `3.0.0bN` + PyPI pre-release; operator installs via `firestarter fw -i --pre --force`. Initially selected; **REVERSED on operator feedback** because merge-before-bench-test pollutes the public release channel if the fix fails. | (initial — reversed) |
| ~~Cut a one-off `3.0.0-rcaN` tag from `v1.6-read-bug` directly~~ | Mirrors v1.5 RCA tag option from Phase 27 D-03 carryover. Same public-channel pollution issue. | |
| Build local hex via `pio run -e <env>`, sideload via `pio run -t upload` (or `avrdude -c urclock` for uno328pb) | Skip CI entirely; build from local `firestarter/v1.6-read-bug` checkout; sideload to operator's boards. NO public artifact created. Phase 30 owns the eventual merge once Phase 29 verdict is green. | ✓ |

**Selected:** Local sideload (CORRECTED — initial choice reversed on operator feedback).
**Notes:** A failed bench verdict against a publicly-tagged `3.0.0bN` artifact pollutes the GitHub Pre-release + PyPI pre-release indices and forces a cleanup tag. Local sideload keeps a failed verdict private; milestone re-opens cleanly via D-07. ROADMAP Phase 30 SC#5 already designates Phase 30 as the branch-promotion phase, so this correction realigns with the originally-roadmapped phase split. v1.5 BENCH-01 happened to test from a public pre-release, but in v1.5 the fix had no bench-side gate before tag-cut — different precedent.

---

## N count strategy (D-03)

REQUIREMENTS says N≥5; Phase 26 baseline was N=3.

| Option | Description | Selected |
|--------|-------------|----------|
| Uniform N=5 on every participating board | Same N keeps the post-fix evidence table symmetric vs Phase 26's N=3 pre-fix table. | ✓ |
| N=5 on Leonardo; N=3 on Uno (regression check only); per D-01 result on uno328pb | Minimize bench time on the boards where the bug never reproduced. | |
| N≥10 on Leonardo (extra rigor); N=5 elsewhere | Hyper-confidence on the formerly-failing board. | |

**Selected:** Uniform N=5 (auto — recommended default).
**Notes:** ~6 s additional bench time per board vs N=3; trivially worth the symmetric A/B for Phase 30 MILESTONES.md citation.

---

## Plan structure / wave shape (D-04) — CORRECTED to remove merge

| Option | Description | Selected |
|--------|-------------|----------|
| Two-plan structure: 29-01 desk-side local build + scaffold (`autonomous: true`) + 29-02 operator-on-bench sideload + verify (`autonomous: false`). NO merge in either plan; Phase 30 owns promotion. | Mirrors Phase 26 pattern (26-01 desk + 26-02 bench). Wave A builds firmware locally + scaffolds EVIDENCE.md; Wave B sideloads + verifies + hands off to Phase 30. | ✓ |
| Single bench plan (`autonomous: false`) — operator does everything | Smallest plan count; less separation between desk-side prep and bench session. | |
| Three plans: prep + bench + close-out paperwork | Split paperwork from bench session for explicit gates. | |

**Selected:** Two-plan structure with NO merge inside Phase 29 (CORRECTED — initial draft incorrectly included `beta → main` promotion in Wave B's verifier task list).
**Notes:** Phase 29's deliverable is the bench evidence. Phase 30 (per ROADMAP SC#5) owns the `v1.6-read-bug → beta → main` promotion, the public pre-release cut, the install-pipeline regression check, and the operator-authorized stable tag bump. The wave-A→wave-B→Phase 30 dependency chain becomes: build local → bench-verify → (PASS gate) → public promotion.

---

## VERIFY-03 (low-rate 1KB jitter) mechanism (D-05)

| Option | Description | Selected |
|--------|-------------|----------|
| Operator shell-loop with `sha256sum` (reuses existing `dev read -s 1024` path) | `for i in $(seq 5); do firestarter dev read W27C512 -s 1024 /tmp/r1k_$i.bin; done; sha256sum /tmp/r1k_*.bin`. No new code. Same wire path as full-chip read. | ✓ |
| Extend `dev consistency-check` with `--size N` flag | Adds a flag to fold VERIFY-03 into the same diagnostic. Phase 26 D-06 explicitly deferred this. | |
| Skip VERIFY-03 (claim 1KB covered by 64KB run) | Argue that if 64KB byte-identity passes, 1KB byte-identity is implied. | |

**Selected:** Operator shell-loop (auto — recommended default).
**Notes:** Phase 26 D-06 locks `dev consistency-check` to full-chip-only; shell-loop honors that boundary. Operator muscle memory from 2026-05-21 triage script applies verbatim.

---

## VERIFY-04 (BENCH-02 closure) chip + procedure (D-06)

| Option | Description | Selected |
|--------|-------------|----------|
| SST27SF512 on Leonardo (single chip, single board, single row) | Leonardo is where the read bug existed; BENCH-02 here is maximally-informative. SST is re-writable in theory (chip-DB misclassification workaround applies). Records single post-hoc row in `.planning/v1.5-BENCH-RESULTS.md`. | ✓ |
| W27C512 (v1.5 BENCH-01 chip; one-shot) | One-shot programmable; needs UV erase between cycles. | |
| Both chips, separate rows in BENCH-RESULTS | Maximum coverage; bench time roughly doubles. | |

**Selected:** SST27SF512 on Leonardo (auto — recommended default).
**Notes:** VERIFY-04 + GATE-1.6 bench rigor coincide — Phase 28 already proved write-path desk-side; the BENCH-02 row is the empirical seal. Small-window-write workaround per v1.5 BENCH-02 row if `firestarter write -e` fails with the chip-DB misclassification error.

---

## Fail-handling protocol (D-07)

| Option | Description | Selected |
|--------|-------------|----------|
| Any FAIL row triggers milestone-reopens; Wave B verifier MUST NOT auto-close VERIFY-NN | Per ROADMAP SC#3 verbatim. Capture failing evidence, halt session, update STATE.md, do NOT promote `beta → main`. | ✓ |
| Auto-retry with bench-side debugging (instrumented build) until N=5 PASS | Open-ended retry loop on bench; risks operator fatigue and silent fix-shape drift. | |
| Close phase with caveat, defer to follow-up | Treat FAIL as a Phase 30 deferred item; mark VERIFY-NN closed-with-caveat. | |

**Selected:** Milestone-reopens (auto — recommended default).
**Notes:** ROADMAP SC#3 is literal — "milestone re-opens". Auto-closing on FAIL would silently violate the success criterion. Wave B is `autonomous: false`, so FAIL is observable in real-time.

---

## EVIDENCE.md Phase 29 section schema (D-08)

Phase 29 section structure: `## Phase 29 — Post-fix Consistency-Check Verification (YYYY-MM-DD)` with sub-sections — pre-flight checklist, hardware metadata snapshot table, VERIFY-01+02 9-column table (consistency-check), VERIFY-03 sub-table (1KB), VERIFY-04 sub-section (BENCH-02 cross-ref), Verdict block, Promotion record.

| Option | Description | Selected |
|--------|-------------|----------|
| Mirror Phase 26 9-column row schema with three sub-sections | Schema locked by Phase 26 D-08; structural symmetry inverts pre-fix table cell-for-cell. | ✓ |
| Flat single-table schema (combine VERIFY-01..04 into one table) | Smaller schema but loses per-VERIFY-NN traceability for Phase 30. | |

**Selected:** Mirror Phase 26 schema (auto — recommended default).
**Notes:** Schema lock from Phase 26 D-08 explicitly requires Phase 29 to follow the same row shape. Sub-section breakdown maps 1:1 to VERIFY-01..04 for cleanest Phase 30 close-out citation.

---

## Test chip selection (D-09)

| Option | Description | Selected |
|--------|-------------|----------|
| W27C512 for VERIFY-01/02/03; SST27SF512 for VERIFY-04. Single physical W27C512 rotated through all 3 boards | Phase 26 baseline used W27C512; same chip gives direct pre-fix vs post-fix A/B. SST27SF512 is electrically erasable for the write→read→verify cycle. | ✓ |
| W27C512 for all four axes (skip the BENCH-02 SST chip) | Single chip across the entire session; needs UV erase before BENCH-02 cycle. | |
| Different chip per board (cross-chip robustness) | Validates fix beyond a single chip variant; adds session complexity. | |

**Selected:** W27C512 for consistency-check + SST27SF512 for BENCH-02 (auto — recommended default).
**Notes:** Symmetric A/B with Phase 26 baseline binaries is the strongest empirical signal. Memory `[[v1.5_bench_findings]]` confirms both chips are in operator's kit.

---

## Shield-rev recording (D-10)

Per memory `[[user_shield_revisions]]` operator owns Rev 2.2, Rev 2.0, modified Rev 0; EEPROM `hw_revision` byte cannot distinguish them; always ASK which rev. Auto mode means we can't ask, so the next-best move is to encode the recording requirement.

| Option | Description | Selected |
|--------|-------------|----------|
| Operator confirms shield rev at session start; rev recorded in EVIDENCE.md hardware metadata snapshot table. Plan does NOT lock a specific shield rev | Honors the "always ASK" memory via structural recording requirement. | ✓ |
| Lock to same shields as Phase 26 baseline (Rev 2.0 on Uno, modified Rev 0 on Leonardo) | Maximally direct A/B with Phase 26. | |
| Test on multiple shield revs (extra A/B for robustness) | Adds bench time; bug is shield-invariant per 3-shield A/B/C triage. | |

**Selected:** Operator confirms + records (auto — recommended default).
**Notes:** Memory `[[user_shield_revisions]]` is explicit; recording requirement makes the choice explicit and auditable. 3-shield A/B/C triage already proved bug is shield-invariant.

---

## Phase 24 BENCH-02 addendum format (D-11)

| Option | Description | Selected |
|--------|-------------|----------|
| Single post-hoc row addendum in `.planning/v1.5-BENCH-RESULTS.md`; cross-reference Phase 29 EVIDENCE.md section | Honors REQUIREMENTS.md VERIFY-04 literal "post-hoc row addendum". Compact and cross-referenced. | ✓ |
| Rewrite v1.5 Row 11 in-place (delete "BLOCKED" caveat) | Mutates archived v1.5 evidence; loses the historical caveat. | |
| Inline the BENCH-02 closure inside the Phase 29 EVIDENCE.md section only (no v1.5-BENCH-RESULTS.md edit) | Misses REQUIREMENTS.md VERIFY-04 wording about the v1.5 file. | |

**Selected:** Post-hoc row addendum (auto — recommended default).
**Notes:** REQUIREMENTS.md VERIFY-04 is explicit about the v1.5 file. Caveat-removal as the empirical signal that v1.5's only deferred item closes cleanly.

---

## Claude's Discretion

- Whether to run BENCH-02 write→read→verify on Uno in addition to Leonardo (default: NO — Leonardo is the maximally-informative single closure).
- Exact pre-release version number (`3.0.0b5` vs other) — depends on `update_version.py --beta` auto-bump or `BETA_VERSION` workflow input.
- Whether Wave B's `beta → main` promotion is dependency-blocked on stable-tag bump (default: promote; stable tag deferred to Phase 30 operator authorization).
- How to handle partial PASS (e.g., 4/5 SHAs identical) — default treats any non-1 `SHAs distinct` as FAIL per D-07; no "marginal" verdict tier.
- Whether to capture pre-flash binary baselines for the uno328pb reflash test (default: NOT captured — reflash outcome is binary).

## Deferred Ideas

- One-off `3.0.0-rcaN` tag for Phase 29 — explicitly not taken per D-02.
- `--size N` flag for `dev consistency-check` — Phase 26 D-06 deferred; post-v1.6.
- `--all-boards` orchestrator — Phase 26 D-07/D-09 deferred.
- Bench-validating Uno's `df5fb44` 2026-05-13 fix — Phase 28 deferred list carries.
- Reverting Leonardo `DATA_BUFFER_SIZE` 512 → 1024 — Phase 28 D-05 / Phase 27 H6 refuted; Phase 29 stays at 512.
- Documentation drift correction (5 "Leonardo 1024-B" locations) — Phase 30 paperwork.
- `firestarter info <chip>` crash — out of v1.6 scope.
- `0xda01` W27C512 chip-ID alias gap — out of v1.6 scope.
- `Board: unknown-board` cosmetic in `dev consistency-check` stdout — Phase 30 paperwork or post-v1.6.
- `--keep-files=False` cleanup for post-fix run binaries — default keep; Phase 30 archives with rest of `.planning/v1.6/`.
- `dev consistency-check` FAIL-without-divergence edge case (WR-01) — Phase 30 paperwork or post-v1.6.

## Reviewed Todos (not folded)

- `large-read-data-jitter-uno328pb.md` — v1.6 milestone bug itself; Phase 29 produces the post-fix evidence; Phase 30 DOC-01 owns the `pending/ → resolved/` move.
- `w27c512-eeprom-misclassification.md` — operationally implicated in VERIFY-04 cycle; D-06 uses the v1.5 small-window-write workaround. Underlying DB fix is its own milestone (v1.7+).
- `avrdude-mcu-detection-fallback.md` — unrelated v1.5 carryover; host CLI enhancement, not bench verification.

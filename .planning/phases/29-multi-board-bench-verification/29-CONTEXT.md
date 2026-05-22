# Phase 29: Multi-Board Bench Verification — Context

**Gathered:** 2026-05-22
**Status:** Ready for planning
**Source:** /gsd:discuss-phase 29 (Auto Mode — gray areas auto-resolved with recommended options; no AskUserQuestion prompts per harness Auto Mode active in this session)

<domain>
## Phase Boundary

Phase 29 delivers **the operator-on-bench acceptance gate for v1.6** — running the Phase 26 `firestarter dev consistency-check` diagnostic against the post-fix firmware on every participating board and recording byte-identical SHA-256 evidence in `.planning/v1.6-EVIDENCE.md`. The fix shipped in Phase 28 (Leonardo `rurp_set_data_input` PORTx-clear + `rurp_read_data_buffer` `_NOP()` settling) must invert the Phase 26 baseline: Verdict cells flip `FAIL → PASS` and `SHAs distinct` cells go `N → 1`. The low-rate (1KB) jitter via `dev read -s 1024` must also collapse to byte-identity (VERIFY-03), and Phase 24's deferred BENCH-02 (`write → read → verify` on a representative EPROM) closes as a post-hoc row addendum in `.planning/v1.5-BENCH-RESULTS.md` (VERIFY-04). This phase has no source-of-truth code edits; its deliverable is empirical bench evidence + the desk-side scaffolding that makes that evidence collectible.

The v1.6 scope-narrowing carried in from Phase 26/27/28 holds:

1. **Leonardo is the only board where the bug actually reproduced in Phase 26** (2.1% jitter at offset `0x0003`, 3 distinct SHA-256s across N=3 runs). Phase 28 closes the underlying defect.
2. **Plain Uno was already PASS in Phase 26** (clean, 3 byte-identical SHAs). Phase 29's Uno verdict is a regression check: the Phase 28 fix touched ONLY Leonardo code paths (`leonardo_rurp_shield.cpp` only; `uno_rurp_shield.cpp` already carried `df5fb44` from 2026-05-13 + Phase 28 `.hex` size table shows Uno Δ=0), so the Uno post-fix verdict MUST remain PASS. Any regression here is a milestone-reopens signal.
3. **The third board labeled `uno328pb` was misidentified** per `[[project_uno328pb_correction]]` (operator clarified 2026-05-21 it's actually a Plain Uno with wrong firmware). Phase 29 resolves the VERIFY-01 mismatch by **reflashing the misidentified board with the post-fix firmware** to either (a) restore a true `uno328pb`-reporting board for the verification (if the silicon is actually 328PB) or (b) confirm the v1.5 misidentification, mark the row DEFERRED, and let code-equivalence with the Uno row carry VERIFY-01 (Phase 28 `.hex` size table shows uno328pb Δ=0; the build differs from Uno only in board-name string + PIO env metadata). See D-01.

**In scope:**

- **Desk-side prep wave (29-01):**
  - Merge `firestarter/v1.6-read-bug` → `firestarter/beta` (commits `fdb1ed5`, `437339b`, `4f205e5`) to trigger the v1.4 beta workflow's pre-release cut. Resulting GitHub Pre-release tag: `3.0.0b5` (or next pre-release per the v1.4 lockstep numbering — actual tag fixed by the workflow's `BETA_VERSION` input at cut time). NO host-side app merge required for Phase 29 — `firestarter_app/v1.6-read-bug` Phase 26 commits (`999c3cc` + `c057fe2`) carry the `dev consistency-check` diagnostic on the local branch; operator installs the host CLI separately if needed (e.g., `pip install -e .` from the sub-repo on `v1.6-read-bug`).
  - Append a Phase 29 SCAFFOLD section to `.planning/v1.6-EVIDENCE.md` at the line-186 (was line-111 pre-Phase-28) anchor: `## Phase 29 — Post-fix Consistency-Check Verification (TBD-YYYY-MM-DD)` heading + empty 9-column row table for each participating board + sub-table for VERIFY-03 (1KB) + sub-section for VERIFY-04 (GATE-1.6 bench rigor). Empty placeholders allow Wave B (bench) to fill in atomically without inventing schema mid-session.
  - Append a Phase 29 SCAFFOLD row to `.planning/v1.5-BENCH-RESULTS.md` for the BENCH-02 post-hoc addendum (VERIFY-04). Placeholder format mirrors v1.5's existing rows + adds a `v1.6 fix reference` column citing the Phase 28 commits.
  - Provide an **operator pre-flight checklist** as a top-of-section block: which port = which board, which RURP shield rev to use, which test chip, which firmware version to install (the pre-release tag from the merge), the install command (`firestarter fw -i --pre --force`), the verification commands per board, and the expected verdict per row.
  - Read-only: no firmware sub-repo source edits (the firmware fix already shipped in Phase 28).

- **Bench wave (29-02, `autonomous: false` — operator-on-bench):**
  - Install the post-fix pre-release firmware on each participating board via `firestarter fw -i --pre --force` (after promoting the host CLI app from `firestarter_app/v1.6-read-bug` so the host knows about `--pre`).
  - Run `firestarter dev consistency-check W27C512 --runs 5 --output-dir .planning/v1.6/post-fix-runs/W27C512-<board>-<YYYY-MM-DD-HHMMSS>` against each participating board. Record one row per board in the Phase 29 EVIDENCE table.
  - Run the **VERIFY-03 1KB shell-loop** on each participating board: `for i in $(seq 5); do firestarter dev read W27C512 -s 1024 /tmp/r1k_<board>_$i.bin; done; sha256sum /tmp/r1k_<board>_*.bin` and record byte-identity in the EVIDENCE table's 1KB sub-section.
  - Run **VERIFY-04 BENCH-02 cycle**: `firestarter write -e SST27SF512 <test-image>.bin` followed by `firestarter dev read SST27SF512 -s <full-chip> <readback>.bin` and `cmp <test-image>.bin <readback>.bin`. Record the result as a post-hoc row addendum in `.planning/v1.5-BENCH-RESULTS.md` citing the Phase 28 fix commits.
  - For the misidentified third board: attempt to reflash with `firestarter_uno328pb.hex` from the pre-release. If post-flash handshake reports `uno328pb`, run the same verification as Uno/Leonardo. If reflash fails OR handshake reports `uno` (confirming the board is actually a Plain Uno), mark the row `DEFERRED — board confirmed misidentified per [[project_uno328pb_correction]]; VERIFY-01 closes via code-equivalence with the Uno row (Phase 28 hex size Δ=0)`.
  - Operator captures a **hardware metadata snapshot table** at session start (mirror of Phase 26's table at `v1.6-EVIDENCE.md:208-212`) — effective hw_rev, physical shield rev, native auto-detect rev, FW build, chip ID seen — because per memory `[[user_shield_revisions]]` the EEPROM hw_revision byte can't distinguish Rev 2.2 / Rev 2.0 / modified Rev 0; the snapshot is the only record of which shield was actually in use.
  - Fill in the EVIDENCE.md scaffold sections with the captured rows. Verdict propagates to the milestone-level v1.6 verdict per ROADMAP SC#3.

- **Branch flow:**
  - Merge `firestarter/v1.6-read-bug` → `firestarter/beta` at the START of Wave A (one merge commit on `firestarter/beta`). Push triggers the v1.4 `beta-build.yml` workflow which cuts the GitHub Pre-release with the per-board `.hex` artifacts (D-02).
  - `firestarter_app/v1.6-read-bug` carries `999c3cc` + `c057fe2` (Phase 26 work) + whatever was added in Phase 28 to that branch (none, per Phase 28 D-03 — the Phase 28 host-side branch stayed parked). Phase 29 promotes `firestarter_app/v1.6-read-bug` → `firestarter_app/beta` ALSO at the start of Wave A so that `pip install --pre firestarter` resolves cleanly with the matching `--pre` semantics. PyPI pre-release cut by the app's `beta-build.yml`.
  - Promote `firestarter/beta` → `firestarter/main` AND `firestarter_app/beta` → `firestarter_app/main` ONLY after Wave B's verifier reports all VERIFY-NN PASS. Promotion lands as the Wave B verifier's final task. Stable tag bump (e.g., `3.0.1`) is operator-authorized at milestone close (Phase 30 owns the stable-tag question, but Phase 29 can land the `beta → main` merge if Wave B verifies green and operator stays present).
  - Meta-repo (`.planning/phases/29-*/` + `.planning/v1.6-EVIDENCE.md` + `.planning/v1.5-BENCH-RESULTS.md` additions) commits to `main` per the standing meta-repo convention (no topic branch on meta-repo; sub-repos own the topic branches).

**Out of scope:**

- The fix itself — closed in Phase 28 (`firestarter/v1.6-read-bug` tip = `4f205e58`). Phase 29 does NOT re-touch `leonardo_rurp_shield.cpp` or any other firmware source.
- RCA narrative — closed in Phase 27.
- Documentation drift correction (the 5 "Leonardo 1024-B" locations from the Phase 27 drift table) — Phase 30 paperwork per Phase 27 D-11 + Phase 28 D-05.
- W27C/E + SST27SF/VF chip-database misclassification fix (`w27c512-eeprom-misclassification.md` todo) — separate v1.7+ milestone. Phase 29 BENCH-02 cycle uses the v1.5-documented workaround (small-window write or UV-erase before re-write) without fixing the underlying DB routing.
- Backfilling a Unity test for the Uno-side `df5fb44` fix — Phase 28 deferred per its `<deferred>` section; post-v1.6 quality-debt.
- Reverting `firestarter/platformio.ini:64-65` Leonardo `DATA_BUFFER_SIZE` from `512` back to `1024` — Phase 28 D-05 + Phase 27 H6 explicitly refuted buffer size as the discriminator. The A/B annotation stays; Phase 29's bench is the validation that the fix works at 512.
- Moving `large-read-data-jitter-uno328pb.md` out of `.planning/todos/pending/` — Phase 30 DOC-01 paperwork.
- MILESTONES.md v1.6 entry, PROJECT.md "Validated"/"Known Gaps" updates, `.planning/phases/26-*/` through `30-*/` archive — all Phase 30 close-out work.
- v1.1 FM1608 byte-0 carryover (separate hardware-gated debug session, parked since 2026-05-18).
- v1.3 CMOS EPROM Family Hardware Validation resume — paused milestone, separate decision tree.
- Host CLI cosmetic polish (Phase 26 REVIEW WR-01 FAIL-without-divergence edge case, WR-02 `Board: unknown-board` cosmetic) — Phase 30 paperwork or post-v1.6.
- `firestarter info <chip>` crash, `0xda01` W27C512 chip-ID alias gap — explicitly out of v1.6 scope per Phase 26 EVIDENCE.md §"Scope changes".

</domain>

<decisions>
## Implementation Decisions

### uno328pb row strategy (the carried-over VERIFY-01 mismatch)

- **D-01: Reflash-then-test; fall back to code-equivalence DEFERRAL if reflash confirms misidentification.**
  Phase 26's third row is DEFERRED because the board labeled `uno328pb` in v1.5 bench notes was operator-clarified mid-session as a Plain Uno + wrong firmware (`[[project_uno328pb_correction]]`). VERIFY-01 maps explicitly to `uno328pb`; Phase 29 must resolve the row, not silently skip it.
  Operator procedure (locked):
  1. With the misidentified board plugged in (`/dev/ttyUSB0` per `[[project_bench_findings_v15]]`), run `firestarter fw -i --pre --force --board uno328pb` to flash `firestarter_uno328pb.hex` from the post-fix pre-release.
  2. Post-flash, run `firestarter fw` (handshake check). Observe the reported `<board>` slot in the handshake reply.
  3. **Case A — handshake reports `uno328pb`**: the board has true ATmega328PB silicon (the `3.0.0b4` `urclock`-bootloader path that worked for v1.5 BENCH-01 is reproducible). Run the full Phase 29 verification (consistency-check N=5 + 1KB shell-loop + BENCH-02 cycle) on this board. Record a real row in the Phase 29 EVIDENCE table.
  4. **Case B — handshake reports `uno` (or flash fails with `signature mismatch`)**: v1.5 misidentification is confirmed at the silicon level. Mark the EVIDENCE row `DEFERRED — board confirmed Plain Uno per [[project_uno328pb_correction]]; VERIFY-01 closes via code-equivalence with Uno row (Phase 28 hex size Δ=0 between uno and uno328pb builds — see EVIDENCE.md Phase 28 size table)`. Reflash the board with `firestarter_uno.hex` to restore it to a working Plain Uno + Phase 28 fix, then run an OPTIONAL "second Uno row" verification to confirm the fix on this physical board too.
  5. Either way, the milestone-level VERIFY-01 verdict is recorded with rationale; Phase 30 MILESTONE.md entry cites the chosen outcome explicitly.
  Rationale:
  - **VERIFY-01 maps to `uno328pb` by name in REQUIREMENTS.md line 30.** Silently skipping leaves a coverage gap; explicit DEFERRAL with code-equivalence rationale closes the requirement on the strength of Phase 28's `.hex` size analysis (uno328pb hex Δ=0 — the build is byte-equivalent to the Uno build modulo board-name string + PIO env metadata).
  - **Reflash is cheap and informative.** Operator already owns the procedure from v1.5 BENCH-01 (`firestarter fw -i --pre` flashed the v1.5 `3.0.0b4` end-to-end via the `urclock` bootloader at 115200 baud). If the silicon really is 328PB, Case A produces a clean third real-silicon row; if it's misidentified, Case B at least restores the board to a useful state.
  - **Memory `[[uno328pb_correction]]` explicitly says skip for v1.6 read-bug repro; the 2026-05-21 ~57.8% baseline is FW-mismatch, not true 328PB silicon.** This decision honors the memory by not chasing the ~57.8% baseline; the reflash test resolves the ambiguity in one shot.
  - **No new code or DB changes required** — the v1.5 Phase 23 host CLI work + Phase 22 release pipeline already emit the `firestarter_uno328pb.hex` artifact + the host installer routes `uno328pb`-reporting devices to the right artifact (v1.5 BENCH-01 closed this loop).
  **Output the planner needs:** PLAN.md Wave B step explicitly enumerates Case A vs Case B branches with the verifier writing the chosen branch's verdict back to EVIDENCE.md + the Phase 29 SUMMARY narrative.

### Pre-release cut procedure (firmware + host CLI installable on bench)

- **D-02: Standard v1.4 beta workflow — merge `v1.6-read-bug` → `beta` triggers automated pre-release cut. Tag: `3.0.0b5` (or next pre-release per v1.4 lockstep `BETA_VERSION` input).**
  Two sub-repo merges at the START of Wave A:
  1. `firestarter/v1.6-read-bug` (`4f205e58`) → `firestarter/beta` (current tip `bc0f5ac`). Merge commit pushed to GitHub remote. Triggers the v1.4 `firestarter/.github/workflows/beta-build.yml` workflow which runs `update_version.py --beta` to bump the version (operator supplies `BETA_VERSION=3.0.0b5` via the `workflow_dispatch` input or the workflow auto-bumps from `3.0.0b4`), runs the PIO + Unity gates, and cuts a GitHub Pre-release with `firestarter_uno.hex`, `firestarter_leonardo.hex`, `firestarter_uno328pb.hex` attached.
  2. `firestarter_app/v1.6-read-bug` (Phase 26 tip `c057fe2`) → `firestarter_app/beta` (current tip — operator confirms at execution). Merge commit pushed. Triggers `firestarter_app/.github/workflows/beta-build.yml` which publishes the matching pre-release version to PyPI.
  Install procedure on bench:
  - `pip install --pre --upgrade firestarter` (resolves to the new PyPI pre-release).
  - `firestarter fw -i --pre --force` (downloads + flashes the matching `firestarter_{board}.hex` per the v1.4 INST-04 board-driven asset resolution).
  Verification:
  - Post-flash, `firestarter fw` (no args) prints `version 3.0.0bN, controller <board> on /dev/ttyXXX` for each board.
  - Operator records the exact tag string in the Phase 29 EVIDENCE.md SCAFFOLD section's pre-flight block.
  Rationale:
  - **Mirrors v1.5 exactly.** v1.5 BENCH-01 used `firestarter fw -i --pre` to flash `3.0.0b4` end-to-end on `/dev/ttyUSB0` via the `urclock` bootloader (BENCH-01 row in `.planning/v1.5-BENCH-RESULTS.md`). Same path, same operator muscle memory.
  - **Locked-step coordination from v1.4 Phase 15 is honored.** App + firmware always release with matching version numbers; `BETA_VERSION` input flows through both `beta-build.yml` workflows. The `3.0.0b5` (or whatever the cut produces) tag is identical across both sub-repos.
  - **NO one-off RCA tag (`3.0.0-rcaN`).** Phase 27 D-03 / Phase 28 D-03 explicitly carried "instrumented builds for Phase 27 RCA may need their own one-off pre-release tag" but Phase 27 Wave B did not fire (`needs_bench: false`) so no RCA tag was cut. Phase 29 uses the standard beta channel.
  - **NO local-hex sideload.** Per `[[feedback_branching]]` and `[[firestarter_repo_layout]]`, sub-repo work flows through the public release pipeline; sideloading defeats the v1.4 pipeline's GATE-01 non-regression guarantee.
  **Output the planner needs:** Wave A's first task is "merge `v1.6-read-bug` → `beta` in both sub-repos + push + confirm GitHub Pre-release tag cut + confirm PyPI pre-release published". Wave B's first task is "install the pre-release on each board + verify handshake reports the right version".

### N count strategy (consecutive-read sample size)

- **D-03: Uniform N=5 on every participating board.**
  Phase 29 runs `firestarter dev consistency-check W27C512 --runs 5` on every board that takes part in the verification (Uno + Leonardo always; uno328pb iff Case A in D-01). Same N keeps the post-fix evidence table symmetric vs the Phase 26 pre-fix N=3 table.
  Rationale:
  - **REQUIREMENTS.md VERIFY-01 + VERIFY-02 floor is N≥5.** Phase 26's N=3 was the reproduction-grade floor (REPRO-03 minimum); Phase 29's N≥5 is the verification-grade floor.
  - **Symmetric table reads cleanly at milestone close.** Phase 30's MILESTONES.md v1.6 entry will reference both the Phase 26 pre-fix table (N=3, FAIL on Leonardo) and the Phase 29 post-fix table (N=5, PASS on Leonardo) — uniform N inside each table is a clear A/B.
  - **Cost is trivial.** A single 64KB read on Leonardo takes ~3 seconds (per the Phase 26 bench-logs serial-transfer timing); 5 runs = 15 s per board. Total bench-time delta vs N=3 is ~6 s per board — well below operator-noticeable.
  - **VERIFY-03 1KB shell-loop also runs at N=5** for consistency (5 × `dev read -s 1024` per board) — same N across all axes.
  **Output the planner needs:** Wave B's per-board task list specifies `--runs 5` literally + `for i in $(seq 5)` in the shell-loop snippets. EVIDENCE.md row schema's "N" column is `5` for every Phase 29 row.

### Plan structure / wave shape

- **D-04: Two-plan structure — 29-01 (desk-side prep, `autonomous: true`) + 29-02 (operator-on-bench, `autonomous: false`).**
  - **Plan 29-01 — Desk-side prep (`autonomous: true`, ~15 min):** Merge `v1.6-read-bug` → `beta` in both sub-repos. Push. Wait for / confirm both pre-release workflows ran green and the artifacts uploaded (operator can dispatch them manually if `workflow_dispatch` is the trigger). Append the Phase 29 SCAFFOLD section to `.planning/v1.6-EVIDENCE.md` at the line-186 anchor. Append the Phase 29 SCAFFOLD row to `.planning/v1.5-BENCH-RESULTS.md` for BENCH-02 addendum. Write the operator pre-flight checklist as a top-of-section block in the Phase 29 EVIDENCE section. Closes the desk-side half (no VERIFY-NN closes here; this is pure scaffolding).
  - **Plan 29-02 — Bench wave (`autonomous: false`, operator-on-bench session, ~60-90 min total):** Operator installs the pre-release on each board, captures the hardware metadata snapshot, runs the 3-axis verification per board (full-chip consistency-check N=5 + 1KB shell-loop N=5 + BENCH-02 write→read→verify on SST27SF512), fills in the EVIDENCE.md SCAFFOLD section's rows, fills in the `.planning/v1.5-BENCH-RESULTS.md` post-hoc addendum row, and resolves the uno328pb row per D-01's reflash test. Closes VERIFY-01 + VERIFY-02 + VERIFY-03 + VERIFY-04. Final verifier task: promote `beta → main` in both sub-repos IF all four VERIFY-NN cells are PASS (stable tag bump deferred to Phase 30 operator authorization).
  Plan dependency: 29-01 → 29-02 (Wave B cannot run until the pre-release is installable).
  Rationale:
  - **Mirrors Phase 26's pattern exactly.** Plan 26-01 (desk-side tool ship) + Plan 26-02 (operator-on-bench session). Two-plan structure is the proven shape for "desk-side prep + operator session" phases (Phase 24 v1.5 BENCH followed this; Phase 12 v1.3 BENCH would have followed this if hardware were available).
  - **Atomic operator-session boundary.** Wave B is one continuous session; splitting per-board across multiple plans adds overhead without diagnostic granularity (the operator is rotating the same chip through three boards in one sitting; the EVIDENCE.md fill is the single artifact). Same logic as Phase 26 D-09 ("one plan per session, with all boards inside") — generalizes here.
  - **Beta-merge as the trigger boundary, not the bench session.** Putting the merge in Wave A means CI runs (workflows, PyPI publish, GitHub Pre-release) finish before the bench session starts. Operator never waits on CI mid-session.
  - **Promotion-to-main lives at the end of Wave B, not Phase 30.** Phase 30 is paperwork; the cleanest semantic boundary is "Phase 29 produces a green bench verdict AND lands the beta → main merge as the artifact of that green verdict". Phase 30's job is then MILESTONE.md + bug-todo move + archive — not branch operations. (This is a deliberate refinement of ROADMAP.md's "Promote beta → main only after operator green" — Phase 29 is exactly that gate; doing the promotion here keeps the milestone-close paperwork from being mixed with branch-management decisions.)
  **Output the planner needs:** PLAN.md 29-01 + 29-02 with explicit task lists; 29-02 task list enumerates the per-board verification axes + the EVIDENCE.md fill + the Case A/B branch for uno328pb + the final `beta → main` promotion check.

### VERIFY-03 (low-rate 1KB jitter) verification mechanism

- **D-05: Operator shell-loop with `sha256sum` — reuses existing `dev read -s 1024` path; no new code.**
  Per-board procedure (locked):
  ```
  for i in $(seq 5); do
    firestarter -p /dev/ttyXXX dev read W27C512 -s 1024 -a 0 /tmp/r1k_<board>_$i.bin
  done
  sha256sum /tmp/r1k_<board>_*.bin
  ```
  Expected post-fix output: 5 identical SHA-256s (1 distinct hash across 5 files).
  Recorded in EVIDENCE.md as a sub-table inside the Phase 29 section:
  ```
  ### VERIFY-03 — 1KB low-rate jitter (post-fix)
  | Board | Port | Chip | N | SHAs distinct | Verdict | Note |
  |-------|------|------|---|---------------|---------|------|
  | uno | /dev/ttyACM0 | W27C512 | 5 | 1 | PASS | 1KB shell-loop byte-identical |
  | leonardo | /dev/ttyACM1 | W27C512 | 5 | 1 | PASS | 1KB jitter resolved post-fix |
  | uno328pb | /dev/ttyUSB0 | W27C512 | 5 | 1 \| DEFERRED | per D-01 |
  ```
  Rationale:
  - **Phase 26 D-06 explicitly locks `dev consistency-check` to full-chip-only.** Adding a `--size N` flag is out of scope (Phase 26 deferred this). The shell-loop satisfies VERIFY-03 without expanding the diagnostic's API surface.
  - **Same wire path, same chunked-read state machine.** `dev read -s 1024` exercises `_run_state_machine` + `_main_phase_read_data` (the same code path Phase 28's fix touches via `rurp_read_data_buffer` / `rurp_set_data_input`). VERIFY-03 is genuinely testing the fix in the small-window regime that the 2026-05-21 triage originally documented at ~0.1% jitter.
  - **Operator muscle memory.** The 2026-05-21 triage script in `large-read-data-jitter-uno328pb.md` already used this exact `sha256sum /tmp/read_$i.bin` shape. No new commands to learn.
  - **VERIFY-03's "if this fails while 1+2 pass, root cause is masked" clause is encoded** — per F-01 below, any FAIL in this sub-table triggers milestone-reopens, not just a row-level FAIL.
  **Output the planner needs:** Wave B task list includes the per-board shell-loop snippet + the sub-table fill. No code changes needed.

### VERIFY-04 (BENCH-02 closure) chip + procedure

- **D-06: SST27SF512 on Leonardo (the previously-failing board) for the BENCH-02 cycle. Single chip, single board, single row.**
  Operator procedure (locked):
  1. Seat SST27SF512 (the v1.5 BENCH-02 chip; electrically-erasable so re-writable). If the chip carries non-blank content from v1.5, run UV-erase OR use a fresh image that does not depend on starting blank (e.g., all-0xAA test pattern).
  2. `firestarter -p /dev/ttyACM1 write -e SST27SF512 <test-image>.bin` — the `-e` flag attempts erase first; will fail with `ERROR: Not supported` per the `w27c512-eeprom-misclassification.md` carry-over. If so, fall back to: small-window write `firestarter -p /dev/ttyACM1 write SST27SF512 <test-image>.bin -a 0 -b` (covers as much address space as the operator has patience for, mirroring the v1.5 BENCH-02 row's small-window workaround).
  3. `firestarter -p /dev/ttyACM1 dev read SST27SF512 -s <size> /tmp/readback.bin` (full-chip OR same address range as step 2 if small-window was used).
  4. `cmp <test-image>.bin /tmp/readback.bin` — exit 0 = byte-identical, exit 1 = mismatch.
  5. Record the result as a post-hoc row addendum in `.planning/v1.5-BENCH-RESULTS.md`:
  ```
  ## Phase 24 BENCH-02 post-hoc closure (2026-MM-DD via v1.6 Phase 29)
  | Bench item | Result | Evidence |
  |-----------|--------|----------|
  | SST27SF512 write→read→verify (Leonardo, post-fix `firestarter/v1.6-read-bug`) | ✓ PASS (byte-identical via cmp) OR ⚠ as before with v1.6 fix evidence | Phase 28 fix commits 437339b6 + 4f205e58; bench session YYYY-MM-DD |
  ```
  Rationale:
  - **Leonardo is the board where the read bug actually existed.** BENCH-02 on Leonardo is the maximally-informative closure — it confirms BOTH the write path is unaffected (Phase 28 GATE-1.6 axis 1) AND the read-back is now byte-identical (the v1.6 fix). Running BENCH-02 on Uno is redundant because Phase 26 already PASS'd Uno on the consistency-check axis.
  - **SST27SF512 over W27C512** because SST is electrically-erasable (in theory; in practice the chip-DB misclassification workaround applies per `w27c512-eeprom-misclassification.md`). Re-writability lets the operator avoid a UV-erase step.
  - **Single chip, single board, single row.** Avoids inflating Phase 29's bench-session scope; VERIFY-04's REQUIREMENTS phrasing is "as a side effect" — one chip-cycle satisfies it.
  - **Memory `[[user_shield_revisions]]` applies** — operator confirms which Leonardo shield is in use at session start (the Phase 26 baseline used modified Rev 0 + voltage-divider mod). For consistency, use the same shield rev as Phase 26 baseline so the A/B is direct. Operator decision; recorded in the hardware metadata snapshot table.
  - **GATE-1.6 bench rigor coincides with VERIFY-04.** Wave B does not need a separate write→read→verify cycle for GATE-1.6 (Phase 28 already proved the diff is read-path-only via desk-side inspection). The VERIFY-04 BENCH-02 row IS the GATE-1.6 bench-rigor evidence.
  **Output the planner needs:** Wave B task list includes the 5 steps above + the row format for `.planning/v1.5-BENCH-RESULTS.md`. Operator handles the small-window-write fallback if the `-e` flag fails.

### Fail-handling protocol (if bench result is FAIL)

- **D-07: Any FAIL row in the Phase 29 EVIDENCE table triggers milestone-reopens — Wave B verifier MUST NOT auto-close VERIFY-NN cells.**
  Per ROADMAP SC#3 verbatim: "If this criterion fails while criteria 1+2 pass, the root cause is masked rather than fixed and the milestone re-opens." Wave B's verifier behavior on any FAIL (any board, any of the 3 axes — full-chip consistency-check, 1KB shell-loop, BENCH-02 write→read→verify):
  1. Capture the failing run binaries + sha256s + offset distributions to EVIDENCE.md (do NOT delete the failure evidence).
  2. Mark the affected VERIFY-NN cell `FAIL` with the row's run output linked.
  3. Append a Wave B FAIL post-mortem prose block to the Phase 29 EVIDENCE section: which board, which axis, which symptom (single-bit-flip distribution, chunk-boundary clustering, etc.), differential vs Phase 26 baseline.
  4. Halt the bench session. Do NOT promote `beta → main`. Do NOT mark VERIFY-NN as closed. Update STATE.md to "v1.6 milestone re-opened — Phase 28 fix masked vs fixed root cause; further RCA needed".
  5. Operator continues debugging out-of-phase (probably a re-open of Phase 27); Phase 29 stays open until a future bench session re-runs with a revised fix.
  Rationale:
  - **ROADMAP SC#3 is literal: "milestone re-opens".** Auto-closing VERIFY-NN on a FAIL would silently violate the success criterion. The plan's verifier MUST encode this branch explicitly.
  - **Phase 26 baseline preserved.** The 2.1% Leonardo jitter at offset `0x0003` is the canonical pre-fix signature; if Phase 29 reproduces a similar distribution (single-bit-flip dominant, partial-erased-chip-correlated, scattered), the fix is masked rather than fixed — Phase 28's `_NOP()` count or the PORTx-clear mask may need adjustment (cf. Phase 28 D-01 "Bench-confirmable in Phase 29" + Phase 28 Claude's-Discretion #1).
  - **Wave B is `autonomous: false`** — the verifier runs WITH the operator on bench. A FAIL is observable in real-time; no risk of an autonomous executor silently inverting the verdict.
  **Output the planner needs:** Wave B verifier task explicitly enumerates the FAIL branch + the STATE.md update + the milestone-reopens annotation in EVIDENCE.md. No auto-retry / auto-debug; halt and surface.

### EVIDENCE.md Phase 29 section schema

- **D-08: Mirror the Phase 26 9-column row schema; append three sub-sections inside `## Phase 29 — Post-fix Consistency-Check Verification (YYYY-MM-DD)`.**
  Section structure (locked):
  ```
  ## Phase 29 — Post-fix Consistency-Check Verification (YYYY-MM-DD)

  **Bench session:** YYYY-MM-DD (operator-on-bench, single session)
  **Firmware shipped to chip:** `firestarter_<board>.hex` v3.0.0bN (from GitHub Pre-release `henols/firestarter` tag `3.0.0bN`)
  **Branch flow:** `firestarter/v1.6-read-bug` (`4f205e58`) → `firestarter/beta` → tag `3.0.0bN`; `firestarter_app/v1.6-read-bug` (`c057fe2`) → `firestarter_app/beta` → PyPI pre-release `3.0.0bN`

  ### Pre-flight checklist (operator)
  (Wave A populates: per-board port mapping, shield rev expected, install commands, expected verdicts.)

  ### Hardware metadata snapshot
  | Board | Effective hw rev | Physical shield | Native auto-detect | FW build | Chip ID seen |
  |-------|------------------|-----------------|--------------------|----------|--------------|
  (Wave B fills in; mirror of Phase 26 baseline table at lines 208-212.)

  ### VERIFY-01 + VERIFY-02 — Full-chip consistency-check (post-fix; 9-column schema)
  | Board | Port | Chip | N | SHAs distinct | Divergent bytes (run1 vs run2) | First-diverge offset | Verdict | Log |
  |-------|------|------|---|---------------|------------------------------|----------------------|---------|-----|
  | uno | /dev/ttyACM0 | W27C512 | 5 | 1 | 0 / 65536 (0.0%) | — | PASS (regression check) | .planning/v1.6/post-fix-runs/W27C512-uno-YYYY-MM-DD-HHMMSS/ |
  | leonardo | /dev/ttyACM1 | W27C512 | 5 | 1 | 0 / 65536 (0.0%) | — | PASS (FIX CONFIRMED — inverted from Phase 26 FAIL) | .planning/v1.6/post-fix-runs/W27C512-leonardo-YYYY-MM-DD-HHMMSS/ |
  | uno328pb | /dev/ttyUSB0 | <per D-01 Case A or B> | 5 \| — | 1 \| — | 0 / 65536 (0.0%) \| — | PASS \| DEFERRED — code-equivalence with Uno row | .planning/v1.6/post-fix-runs/... \| — |

  ### VERIFY-03 — 1KB low-rate jitter (post-fix)
  | Board | Port | Chip | N | SHAs distinct | Verdict | Note |
  |-------|------|------|---|---------------|---------|------|
  (Wave B fills in per D-05.)

  ### VERIFY-04 — BENCH-02 post-hoc closure
  (Wave B fills in per D-06; cross-references `.planning/v1.5-BENCH-RESULTS.md` post-hoc row addendum.)

  ### Verdict
  - **VERIFY-01:** [CLOSED ✓ | DEFERRED with code-equivalence rationale]
  - **VERIFY-02:** [CLOSED ✓]
  - **VERIFY-03:** [CLOSED ✓ — root cause is NOT masked: 1KB jitter resolved alongside 64KB jitter]
  - **VERIFY-04:** [CLOSED ✓ — Phase 24 BENCH-02 post-hoc row added to v1.5-BENCH-RESULTS.md]

  ### Promotion
  - `firestarter/beta` → `firestarter/main`: <merge SHA YYYY-MM-DD>
  - `firestarter_app/beta` → `firestarter_app/main`: <merge SHA YYYY-MM-DD>
  - Stable tag bump: <deferred to Phase 30 operator authorization | landed as `3.0.1` YYYY-MM-DD>
  ```
  Rationale:
  - **9-column schema locked by Phase 26 D-08** ("Important — schema is shared. Phase 27/28/29 must read this CONTEXT.md (or the live `v1.6-EVIDENCE.md`) and follow the same row schema so the file is internally consistent across phases").
  - **Inverts Phase 26 baseline cell-for-cell**: every Verdict cell flips `FAIL → PASS`, every `SHAs distinct` cell goes `N → 1`. The structural symmetry is the milestone's empirical gate.
  - **Sub-section breakdown maps 1:1 to VERIFY-01..04**: easy for the Phase 30 MILESTONES.md scribe to cite per-requirement closure.
  - **Forward-annotation comment for Phase 29 already exists at EVIDENCE.md line 186** (the original line-111 anchor was pushed down by Phase 28's insertion); Phase 29 lands exactly at that anchor.
  **Output the planner needs:** Wave A's EVIDENCE.md scaffold task writes the section header + the 3 sub-table headers + the pre-flight checklist block + the empty Verdict block. Wave B fills in.

### Test chip selection across all 3 verification axes

- **D-09: W27C512 for VERIFY-01/02/03 (consistency-check + 1KB); SST27SF512 for VERIFY-04 (BENCH-02 write→read→verify). Single physical W27C512 chip rotated through all 3 boards.**
  - W27C512 is the Phase 26 baseline chip (Leonardo row uses W27C512 id `0xda01`; Uno row uses W27C512 id `0xda08`). Same chip means direct pre-fix vs post-fix A/B against the committed binaries in `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/`.
  - W27C512 is UV-erasable only (not electrically erasable); does NOT need re-writing between verification runs because the verification is read-only (Phase 26 D-02). Operator rotates the same chip through all 3 boards without modification.
  - SST27SF512 (electrically erasable in theory; current DB classifies as UV-only — `w27c512-eeprom-misclassification.md` workaround applies) is used ONLY for VERIFY-04 (BENCH-02 write→read→verify). Separate physical chip; seated only when the BENCH-02 cycle runs.
  - The Leonardo chip ID variant `0xda01` (vs Uno's `0xda08`) is a known cosmetic mismatch (Phase 26 EVIDENCE.md §"Scope changes" item 2) — not a Phase 29 concern; operator confirms the chip's actual identity by reading it once and noting the variant in the hardware metadata snapshot.
  Rationale:
  - **Symmetric A/B with Phase 26 baseline.** Same chip, same chip rotation, same boards (for the two real boards) → cleanest possible comparison.
  - **VERIFY-04 needs a writable chip** — only SST27SF512 fits, and only because the operator already has the v1.5 BENCH-02 workaround established (small-window write OR UV erase + full write).
  - **Memory `[[v1.5_bench_findings]]`** confirms SST27SF512 is in operator's kit and worked end-to-end for v1.5 BENCH-01.
  **Output the planner needs:** Wave B task list specifies "W27C512 in socket for tasks 1-2 (full-chip consistency-check + 1KB shell-loop); swap to SST27SF512 for task 3 (BENCH-02 write→read→verify)" per-board.

### Shield revision recording (per memory `[[user_shield_revisions]]`)

- **D-10: Operator confirms shield rev at session start; rev recorded in EVIDENCE.md hardware metadata snapshot table. Plan does NOT lock a specific shield rev.**
  Per memory `[[user_shield_revisions]]`: operator owns Rev 2.2, Rev 2.0, modified Rev 0; EEPROM `hw_revision` byte cannot distinguish them; always ASK which rev when "swap the shield" comes up. Phase 26 baseline used:
  - Plain Uno (`/dev/ttyACM0`) + Rev 2.0 shield (override cleared; auto-detect Rev2)
  - Leonardo (`/dev/ttyACM1`) + modified Rev 0 + voltage-divider mod (`--rev 2` override; native auto-detect Rev1)
  For Phase 29's direct A/B vs Phase 26: same shield rev per board is strongly preferred but not required (the bug is firmware-side per the 3-shield A/B/C triage; shield rev is signal-integrity context, not a discriminator).
  Operator records in the Phase 29 EVIDENCE hardware metadata snapshot table (D-08) the shield rev in use at session time. If different from Phase 26 baseline, note in the Verdict block: "Shield rev changed between Phase 26 and Phase 29 — A/B comparison cross-shield; fix verdict still applies because bug is shield-invariant per 3-shield triage".
  Rationale:
  - **Memory says ASK; auto mode means we can't ask**, so the next-best move is to encode the recording requirement explicitly in the EVIDENCE.md schema. The hardware metadata snapshot table makes the rev choice explicit and auditable.
  - **3-shield A/B/C triage already proved bug is shield-invariant** (Phase 26 EVIDENCE.md §"Entry conditions" + `[[user_shield_revisions]]`) → the fix's verdict isn't contingent on shield rev.
  - **Phase 30 MILESTONES.md can cite the shield rev exactly** because Phase 29 records it.
  **Output the planner needs:** Wave B's first task ("session start — hardware metadata snapshot") explicitly enumerates "operator declares which shield rev is on each board" + the row format.

### Phase 24 BENCH-02 post-hoc addendum format

- **D-11: Single post-hoc row addendum in `.planning/v1.5-BENCH-RESULTS.md`; cross-reference the Phase 29 EVIDENCE.md section.**
  Format (locked, append AFTER the existing v1.5 Verdict block at the bottom of the file):
  ```
  ## Phase 24 BENCH-02 post-hoc closure (YYYY-MM-DD via v1.6 Phase 29)

  **Closes:** v1.5 Phase 24 BENCH-02 acceptance criterion ("write→read→verify on a representative EPROM") — previously CLOSED with caveat (Row 11: full-chip read returned ~57% different bytes across consecutive calls; closed on the strength of small-window write verification).

  **Resolution:** v1.6 Phase 28 read-bug fix (firmware commits `437339b6` PORTx-clear + `4f205e58` `_NOP()` settling) eliminates the pre-existing read-streaming jitter. Phase 29 bench session re-runs the write→read→verify cycle and confirms byte-identity.

  | Bench item | Result | Evidence |
  |-----------|--------|----------|
  | SST27SF512 write→read→verify (Leonardo, post-fix `firestarter/v1.6-read-bug`) | ✓ PASS — byte-identical via `cmp` | Phase 28 fix commits `437339b6` + `4f205e58`; Phase 29 EVIDENCE.md §"VERIFY-04 — BENCH-02 post-hoc closure"; bench session YYYY-MM-DD |

  **Verdict:** BENCH-02 fully closed (no caveat). `.planning/todos/pending/large-read-data-jitter-uno328pb.md` ready for Phase 30 DOC-01 move-to-resolved.
  ```
  Rationale:
  - **REQUIREMENTS.md VERIFY-04 specifies "post-hoc row addendum in `.planning/v1.5-BENCH-RESULTS.md`"** — this format honors it literally.
  - **Cross-reference enables Phase 30 MILESTONES.md scribe** to cite the v1.5 BENCH-02 closure across two files without re-deriving.
  - **Caveat removal is the empirical signal** that the v1.5 milestone's only deferred item closes cleanly.
  **Output the planner needs:** Wave A scaffolds an empty row template (operator fills in YYYY-MM-DD and the chip-specific result during Wave B).

### Claude's Discretion

- **Whether to run the BENCH-02 write→read→verify on Uno in addition to Leonardo.** Default: NO (Phase 26 already proved Uno's read path is clean; BENCH-02 on Leonardo is the maximally-informative single closure). If operator volunteers a second Uno cycle for confidence, capture as a bonus row but don't make it gating.
- **Exact pre-release version number** (`3.0.0b5` vs `3.0.0b6` etc.) — depends on whether the v1.4 `update_version.py --beta` auto-bumps from `3.0.0b4` or whether the operator dispatches with a specific `BETA_VERSION` input. Planner picks the next sequential pre-release number; operator confirms at execution and records the actual tag in the EVIDENCE.md SCAFFOLD section.
- **Whether Wave B's `beta → main` promotion is dependency-blocked on stable-tag bump.** Default: promotion happens (the merge commits land on `main`); stable tag (`3.0.1`) deferred to Phase 30 operator authorization. If operator says "stable bump now, milestone close later", the verifier can also cut the stable tag.
- **How to handle a partial PASS** (e.g., 4 / 5 SHAs identical) — current encoding treats any non-1 `SHAs distinct` as FAIL per D-07. If operator wants a "marginal" verdict tier, that's a Phase 29 D-07 amendment + EVIDENCE.md schema extension; default is strict binary PASS/FAIL.
- **Whether to capture pre-flash binary baselines for the uno328pb reflash test** (so if Case B fires, the operator has a saved binary to compare the misidentified board's behavior against). Default: NOT captured — the reflash test outcome is binary (handshake reports `uno328pb` or it doesn't); pre-flash baseline adds noise without diagnostic value.

### Folded Todos

None folded. All three pending todos scored 0.6 against Phase 29 keywords but none fit Phase 29's bench-verification scope. See `<deferred>` for review notes.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 29 primary inputs (the evidence + tool chain Phase 29 consumes)

- `.planning/v1.6-EVIDENCE.md` — Phase 26 baseline section (lines 12-19), Phase 27 RCA section (lines 22-108), Phase 28 fix commit reference section (lines 112-185). Phase 29 appends `## Phase 29 — Post-fix Consistency-Check Verification` at the line-186 anchor (the original Phase 29 anchor at line-111 was pushed down by Phase 28's section).
- `.planning/v1.5-BENCH-RESULTS.md` — v1.5 BENCH-01 + BENCH-02 closure rows. Phase 29 VERIFY-04 appends a post-hoc closure section at the bottom per D-11.
- `firestarter_app/tests/test_consistency_check.py` — host-side pytest contract for `dev consistency-check`. Phase 29 does NOT edit this; it relies on the v1.6 stdout regex contract (Phase 26 PLAN.md narrative + Phase 26 Plan 26-01 commit `999c3cc`) staying stable so the operator's per-row verdict parsing is unambiguous.
- `firestarter_app/firestarter/main.py` §`dev` subparser + `firestarter_app/firestarter/eprom_operations.py:consistency_check_eprom` — the diagnostic Phase 29 invokes (read-only, no changes).

### Phase 28 inheritance (the firmware fix Phase 29 verifies)

- `.planning/phases/28-fix-implementation-unit-test-coverage/28-CONTEXT.md` — Phase 28 D-01 fix shape (PORTx-clear + `_NOP()` × 2); D-03 branch flow (`firestarter/v1.6-read-bug` cut from `beta@bc0f5ac`, branch LOCAL only post-Phase-28 — Phase 29 pushes); D-07 per-board hex size table (uno Δ=0, leonardo Δ=+41 B, uno328pb Δ=0 — the size analysis that underwrites D-01 Case B code-equivalence DEFERRAL); D-08 EVIDENCE.md append pattern (Phase 29 mirrors).
- `.planning/phases/28-fix-implementation-unit-test-coverage/28-VERIFICATION.md` — confirms all 5 Phase 28 SC verified; bench half (N≥5 byte-identity on real hardware) explicitly gated to Phase 29 per ROADMAP SC#3.
- `firestarter/src/boards/leonardo_rurp_shield.cpp` (current tip on `firestarter/v1.6-read-bug` = `4f205e58`) — the post-fix code Phase 29's bench session validates. Phase 29 does NOT edit.
- Phase 28 fix commits (LOCAL on `firestarter/v1.6-read-bug` until Phase 29 Wave A merge):
  - `fdb1ed5` — Wave A RED Unity scaffold (test commit; precedes fix)
  - `437339b6` — Commit 1: PORTx-clear in `rurp_set_data_input`
  - `4f205e58` — Commit 2: `_NOP()` settling in `rurp_read_data_buffer`

### Phase 27 carry-through (RCA context Phase 29 cites in EVIDENCE narrative)

- `.planning/phases/27-root-cause-analysis/27-CONTEXT.md` — Phase 27 D-04 EVIDENCE.md single-file accretion pattern; D-05 buffer-size A/B refutation; D-11 documentation drift correction targets deferred to Phase 30.
- `.planning/v1.6-EVIDENCE.md §"Phase 27 — RCA Findings (2026-05-21)"` — the RCA narrative the Phase 29 verifier cites when narrating Verdict block ("inverted from Phase 26 FAIL — PRIMARY mechanism PORTx-clear validated on bench"). Also carries the `[[user_shield_revisions]]` 3-shield A/B/C triage finding.

### Phase 26 carry-through (tool + baseline)

- `.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-CONTEXT.md` — Phase 26 D-01 (CLI subcommand naming + signature), D-02 (passive read-only mode), D-04 (stdout verdict format), D-05 (exit code semantics — Phase 29's CI/operator interprets `0`=PASS, `1`=FAIL, `2`=hw error), D-06 (full-chip-only scope; Phase 29 D-05 honors this), D-07 (per-port operator invocation, no orchestrator), D-08 (EVIDENCE.md 9-column schema — Phase 29 D-08 mirrors), D-09 (one plan per session, all boards inside).
- `.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-02-SUMMARY.md` — Phase 26 Wave B bench session log; the canonical pre-flight + post-flight narrative Phase 29's pre-flight checklist mirrors.

### Roadmap + requirements (locked phase scope)

- `.planning/ROADMAP.md §"Phase 29: Multi-Board Bench Verification"` (lines 87-99) — Goal + 5 success criteria + dependencies. SC#3 (1KB low-rate jitter; "if this criterion fails while criteria 1+2 pass, the root cause is masked rather than fixed and the milestone re-opens") is encoded in D-07. SC#5 (GATE-1.6 bench-rigor write→read→verify) coincides with VERIFY-04 per D-06.
- `.planning/REQUIREMENTS.md` lines 28-33 — VERIFY-01, VERIFY-02, VERIFY-03, VERIFY-04 verbatim text. N≥5 floor is the requirement-level lock (D-03).

### v1.4 release pipeline (the pre-release cut substrate Phase 29 reuses)

- `firestarter/.github/workflows/beta-build.yml` — the v1.4 Phase 17 firmware beta workflow. Phase 29 Wave A triggers this via `firestarter/v1.6-read-bug` → `firestarter/beta` merge.
- `firestarter_app/.github/workflows/beta-build.yml` — the v1.4 Phase 16 app beta workflow. Phase 29 Wave A triggers this via `firestarter_app/v1.6-read-bug` → `firestarter_app/beta` merge.
- `firestarter_app/firestarter/firmware.py` — v1.4 Phase 18 INST-02 `--pre` flag logic; routes `--pre` to `releases?prerelease=true` filter. Phase 29 operator install (`firestarter fw -i --pre --force`) flows through this code path.
- `.planning/milestones/v1.4-RELEASE-PROCEDURES.md` — v1.4 Phase 19 documented procedure for cutting a coordinated beta pre-release (locked-step app + firmware version). Phase 29 follows this verbatim.

### Cross-cutting branching + memory

- Memory `[[feedback_branching]]` — all v1.6 work on `v1.6-read-bug` branches in all 3 repos; sub-repos branch off `beta`; promote `beta` → `main` only after operator-green. Phase 29 Wave B's final task implements the promotion.
- Memory `[[user_firestarter_repo_layout]]` — meta-repo at `/workspaces`, firmware sub-repo at `/workspaces/firestarter`, host sub-repo at `/workspaces/firestarter_app`.
- Memory `[[project_bench_findings_v15]]` — programmer_id="urclock" (not "arduino") for the misidentified board's bootloader; port mapping `/dev/ttyUSB0` for that board.
- Memory `[[project_uno328pb_correction]]` — the third board labeled `uno328pb` in v1.5 was actually a Plain Uno + wrong firmware. Phase 29 D-01 encodes the reflash test that resolves the misidentification.
- Memory `[[user_shield_revisions]]` — operator owns Rev 2.2, Rev 2.0, modified Rev 0; EEPROM `hw_revision` byte cannot distinguish them; always ASK which rev. Phase 29 D-10 encodes the recording requirement (since auto mode means we can't ask).
- `.planning/PROJECT.md §"Current Milestone: v1.6 Fix the Read Bug"` — milestone-level decisions (GATE-1.6, branch model, definition of done).

### Phase 24 carry-through (BENCH-02 closure scope)

- `.planning/v1.5-BENCH-RESULTS.md` Row 11 (full-chip 64KB byte-identical verify; previously BLOCKED) + Row 8/9 (small-window write verification; PASS). Phase 29 D-11 appends the post-hoc closure section that converts Row 11's BLOCKED to PASS via the v1.6 fix.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`firestarter dev consistency-check` host CLI command** (`firestarter_app/firestarter/main.py:create_dev_args` + `eprom_operations.py:consistency_check_eprom`) — shipped in Phase 26 Plan 26-01 sub-repo commit `999c3cc`. Phase 29 invokes unchanged with `--runs 5` per board. Stdout verdict regex contract is the row-format anchor.
- **`firestarter dev read -s 1024`** — existing 1KB read path (`firestarter_app/firestarter/main.py` `dev read` subparser per Phase 26 baseline at line 373-388). Phase 29 D-05 wraps in operator shell-loop for VERIFY-03; no new code.
- **`firestarter fw -i --pre --force`** — v1.4 Phase 18 INST-02 + GATE-01 beta-install path; v1.5 BENCH-01 proved end-to-end on `/dev/ttyUSB0` via `urclock` bootloader. Phase 29 reuses verbatim for each board's install step.
- **`firestarter write -e <chip>` + `firestarter dev read <chip> -s <size>` + `cmp`** — the BENCH-02 write→read→verify trio. Phase 29 D-06 reuses with the v1.5 small-window-write workaround (in case `-e` fails per `w27c512-eeprom-misclassification.md`).
- **GitHub Pre-release workflow + PyPI pre-release publish** — v1.4 plumbing (`firestarter/.github/workflows/beta-build.yml` + `firestarter_app/.github/workflows/beta-build.yml`); Phase 29 D-02 triggers via `v1.6-read-bug → beta` merge.
- **`update_version.py --beta`** — v1.4 Phase 15 lockstep coordination tool; auto-bumps `3.0.0bN → 3.0.0b(N+1)` when `BETA_VERSION` not explicitly set. Phase 29 operator confirms the actual cut tag at execution time.

### Established Patterns

- **Two-plan structure (desk-side prep + operator-on-bench session).** Phase 26 (26-01 desk-side + 26-02 bench) + Phase 24 (BENCH-01 desk-side scaffold + bench session). Phase 29 follows the same shape per D-04.
- **EVIDENCE.md cross-phase append-only with forward-annotation anchors.** Phase 26 → 27 → 28 → 29 each append exactly one section via `<!-- Phase N ... -->` anchors. Phase 29 honors the line-186 anchor (was line-111 pre-Phase-28) per D-08.
- **9-column row schema for bench evidence** (Phase 26 D-08). Phase 29's three sub-tables (consistency-check + 1KB + BENCH-02 hardware metadata snapshot) all conform.
- **Locked-step app + firmware pre-release cut** (v1.4 Phase 15 / 16 / 17 coordination). Phase 29 D-02 triggers both sub-repo workflows from a single `BETA_VERSION` input.
- **Operator-on-bench plan = `autonomous: false`; desk-side plan = `autonomous: true`** (Phase 26 D-09 + Phase 12 D-11). Phase 29 D-04 mirrors.
- **Hardware metadata snapshot table** (Phase 26 EVIDENCE.md:208-212). Phase 29 D-10 reuses; recording requirement explicit because memory says ASK and auto mode can't.
- **Per-port operator invocation; no orchestrator** (Phase 26 D-07). Phase 29 keeps three separate manual invocations of `dev consistency-check` per board.

### Integration Points

- **`.planning/v1.6-EVIDENCE.md` line-186 anchor** — Phase 29's append point for `## Phase 29 — Post-fix Consistency-Check Verification (YYYY-MM-DD)`. Phase 28's section pushed the original line-111 anchor down; verify the comment position at Wave A execution and adjust line number if Phase 28 SUMMARY further amended.
- **`.planning/v1.5-BENCH-RESULTS.md` (end of file)** — Phase 29's VERIFY-04 post-hoc closure append point.
- **`firestarter/beta` HEAD** — current `bc0f5ac` (1 docs commit ahead of tag `3.0.0b4`); Phase 29 Wave A merges `firestarter/v1.6-read-bug` (`4f205e58`) here.
- **`firestarter_app/beta` HEAD** — Phase 29 Wave A merges `firestarter_app/v1.6-read-bug` (`c057fe2` = Phase 26 tip).
- **Bench hardware:** operator's 3 boards (Plain Uno + Leonardo + misidentified board labeled `uno328pb`) + RURP shield set (Rev 2.2, Rev 2.0, modified Rev 0 — operator picks per session) + test chips (W27C512 for consistency-check; SST27SF512 for BENCH-02).
- **Port mapping (from `[[project_bench_findings_v15]]` + Phase 26 baseline):** `/dev/ttyACM0` = Plain Uno; `/dev/ttyACM1` = Leonardo; `/dev/ttyUSB0` = misidentified board (uno328pb-or-Plain-Uno per D-01 reflash test).

</code_context>

<specifics>
## Specific Ideas

- **The Leonardo verdict is THE acceptance gate.** Uno + uno328pb verdicts are regression checks (Uno already PASS in Phase 26; uno328pb is byte-equivalent to Uno per Phase 28 hex size analysis). The milestone's empirical question — "does the Phase 28 fix actually fix the bug on the only board where the bug reproduced?" — has a binary answer: Leonardo Verdict = PASS (FIX CONFIRMED, milestone ships) OR FAIL (milestone re-opens per D-07).
- **Phase 26 baseline's run binaries stay on disk** (`.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/run_0[1-3].bin`). Phase 29 does NOT delete them; the post-fix runs land in `.planning/v1.6/post-fix-runs/W27C512-leonardo-<new-timestamp>/run_0[1-5].bin` (note: `post-fix-runs/` subdir per the Phase 26 D-04 `--output-dir` flexibility). Phase 30 archives both directories under `.planning/milestones/v1.6-phases/` as part of milestone close.
- **The 5-line Python cross-check from Phase 27** (EVIDENCE.md lines 99-108) is re-runnable against the post-fix binaries to confirm the divergence count drops from 1349 to 0. Phase 29 Wave B's verifier can optionally run this as a sanity check (expected output: `Total divergences: 0; single-bit-flip fraction: 0.0%`).
- **Two empirically-confirmed `_NOP()` count = 2 settling delay** (Phase 28 commit `4f205e58`). If Phase 29 still shows residual single-bit flips on Leonardo, operator can attempt N=3 or N=4 `_NOP()`s as a Phase 27 re-open experiment per Phase 28 Claude's Discretion #1. Phase 29 itself does NOT modify the count.
- **The `urclock` bootloader is the right `programmer_id`** for the misidentified board (per `[[project_bench_findings_v15]]`). Phase 29 D-01 reflash uses the standard `firestarter fw -i --pre --force` path which already picks `urclock` for the uno328pb-reporting handshake (v1.5 Phase 23 host CLI work). If the reflash fails with a programmer-id mismatch, the board is likely a Plain Uno (Case B) and `firestarter fw -i --pre --force --board uno` will succeed.
- **Operator's stable-installed app vs `--pre`-installed app:** Phase 29 Wave B requires the `--pre`-installed app on bench (because the diagnostic + the install command both need v1.6 bits). The promotion to `main` at the end of Wave B + stable bump in Phase 30 restores the stable-installed app to v1.6 semantics for downstream users.

</specifics>

<deferred>
## Deferred Ideas

- **Cutting a one-off `3.0.0-rcaN` tag** for Phase 29 (mirror of Phase 27 RCA tag option) — explicitly NOT taken per D-02; standard beta workflow is sufficient. If Phase 29 Wave B FAILs and Phase 27 re-opens with an instrumented build, the RCA tag becomes available again at that point.
- **Adding `--size N` flag to `dev consistency-check`** to fold VERIFY-03 into the same diagnostic — Phase 26 D-06 explicitly deferred. Could land post-v1.6 if the 1KB-only verification is repeatedly needed.
- **Auto-orchestrating cross-board verification** (`--all-boards` flag enumerating `/dev/tty*` and rotating chip) — Phase 26 D-07 / D-09 deferred; operator muscle memory wins.
- **Bench-validating the Uno's `df5fb44` 2026-05-13 fix** by adding a parallel Unity test mirroring Phase 28's test_data_input — Phase 28 `<deferred>` carries this; post-v1.6 quality-debt.
- **Reverting Leonardo `DATA_BUFFER_SIZE` from 512 → 1024** in `firestarter/platformio.ini:64-65` (the A/B annotation) — Phase 28 D-05 + Phase 27 H6 refuted buffer size as discriminator. Phase 29 keeps 512 (since both Phase 26 baseline and Phase 28 fix landed at 512). If Phase 29 PASS at 512, the 1024 revert is a Phase 30 polish OR post-v1.6 question; not a verification axis.
- **Documentation drift correction** (5 "Leonardo 1024-B" locations from Phase 27 drift table) — Phase 30 paperwork.
- **`firestarter info <chip>` crash** (TypeError at `ic_layout.py:167`) — Phase 26 EVIDENCE.md §"Scope changes" item 3; out of v1.6 scope.
- **`0xda01` W27C512 chip-ID alias gap** — Phase 26 §"Scope changes" item 2; out of v1.6 scope. Phase 29 operator notes the variant in the hardware metadata snapshot but does NOT fix the DB.
- **Cosmetic `Board: unknown-board` in `dev consistency-check` stdout** (Phase 26 REVIEW WR-02) — Phase 30 paperwork or post-v1.6.
- **`--keep-files=False` cleanup for the Phase 29 post-fix run binaries** — default keep (Phase 26 D-04); archives go with the rest of `.planning/v1.6/` under `.planning/milestones/v1.6-phases/` at Phase 30 close.
- **`dev consistency-check` FAIL-without-divergence edge case** (Phase 26 REVIEW WR-01) — Phase 30 paperwork or post-v1.6.

### Reviewed Todos (not folded)

- **`large-read-data-jitter-uno328pb.md`** — the v1.6 milestone bug itself. Phase 29 PRODUCES the post-fix evidence that demonstrates it's resolved; Phase 30 DOC-01 owns the `pending/ → resolved/` move + the root-cause summary cross-reference (per Phase 28 deferred list). Not folded into Phase 29 because the todo's state transition is paperwork, not verification.
- **`w27c512-eeprom-misclassification.md`** — operationally implicated in Phase 29 VERIFY-04 (the `firestarter write -e SST27SF512` path may fail with the v1.5-documented "ERROR: Not supported" workaround). Phase 29 D-06 uses the small-window-write workaround per v1.5 BENCH-02 precedent. The underlying DB classification fix belongs in its own milestone (operator-tagged "asap" but separate bug class — DB routing, not transport). Not folded.
- **`avrdude-mcu-detection-fallback.md`** — unrelated v1.5 carryover (low priority); host CLI enhancement, not bench verification. Not folded.

</deferred>

---

*Phase: 29-multi-board-bench-verification*
*Context gathered: 2026-05-22*

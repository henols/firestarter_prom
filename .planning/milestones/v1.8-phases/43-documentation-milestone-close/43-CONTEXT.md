# Phase 43: Documentation + Milestone Close - Context

**Gathered:** 2026-05-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Close v1.8 cleanly. Three deliverables, mapped to DOC-01 / DOC-02 / MS-01:

- **DOC-01 — Contributor-facing docs.** `firestarter_app/README.md` grows ONE new `## Architecture` section (flat-module map across the 21 modules in `firestarter/` + layer-boundary rules + a one-subsection tooling workflow naming `ruff check` / `ruff format` / `mypy` / `pytest --cov-fail-under=70`). NO TOC rewrite, NO restructuring of existing Install/Usage/Commands. `firestarter_app/CLAUDE.md` gets TARGETED fixes only — drop the "EpromDatabase singleton" wording (stale since Phase 36 D-06 `skip_local_override` seam); Key Files list grows the post-v1.8 flat modules (`frame_parser.py`, `codec.py`, `address_parser.py`, `chip_resolver.py`, `cli_handlers.py`, `exceptions.py`); one new line on the v1.8 tooling gate. Data Flow diagram + Wire Protocol + DB Pipeline + Constants blocks stay byte-identical (no full re-sync). No new `CONTRIBUTING.md`.

- **DOC-02 — Milestone records + archive.** `MILESTONES.md` grows a new `## v1.8 — Host CLI Structural Cleanup (firestarter_app) — Shipped 2026-05-XX` entry ABOVE the existing v1.6 entry, structurally identical to v1.6 (`Phases | Plans | Timeline | Ship tag | Commits` header + Delivered narrative + Key Accomplishments + Branch Strategy + Open backlog carry-forward + Key Decisions + Known Gaps + Hardware Impact). `PROJECT.md` ship-history block (lines 5–11) grows a `**v1.8 shipped:** 2026-05-XX` line; the current `## Current Milestone: v1.8` block is REPLACED by promoting the existing `## v1.9 — Read-Bug RCA + Fix (PROPOSED)` section (which already exists below Current Milestone in the file) up to the Current Milestone slot; the old v1.8 block becomes a `## v1.8 Archive: Host CLI Structural Cleanup — Shipped 2026-05-XX` section inserted between v1.7 and v1.6 in the existing archive chronology (mirrors the v1.4/v1.5/v1.6/v1.7 archive-block shape). Phase artifacts archived under `.planning/milestones/v1.8-phases/` via a new `.planning/v1.8-archive.sh` mirroring `.planning/v1.6-archive.sh` (phase numbers 36–43, --dry-run support, explicit per-phase enumeration). `.planning/ROADMAP.md` v1.8 section (currently lines 15–314 — `## v1.8 — Host CLI Structural Cleanup (STARTED 2026-05-27)` + `### v1.8 Coverage`) collapsed into a `## v1.8 — Host CLI Structural Cleanup (SHIPPED 2026-05-XX)` heading followed by a `<details>` block mirroring the existing v1.5/v1.6/v1.7 collapsed shape. New `.planning/milestones/v1.8-REQUIREMENTS.md` created with the 30-row coverage table from ROADMAP.md (TEST-01..05, TOOL-01..03, STRUCT-01..05, DATA-01..04, SERIAL-01..03, CLI-01..04, ERR-01..03, DOC-01..02, MS-01) annotated per-requirement disposition (DELIVERED / DEFERRED-to-v1.9 / VERIFIED).

- **MS-01 — GATE-1.8 end-to-end verification + branch promotion.** GATE-1.8 (a–e) verification uses the BOTH path: the software-only floor (full suite green: 241+ passed + 29 syrupy snapshots + parity tests + `pip install -e . && firestarter --help` smoke) lands as part of Plan 43-01/43-02 autonomous ship-state flips; the real-hardware smoke (operator runs `firestarter read -e W27C512` on the Modified Rev 0 / Leonardo bench against an existing N=5 baseline from `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`, byte-identical PASS gate) lands as Step 0 of Plan 43-03 HUMAN-UAT.md BEFORE the branch-merge steps. Branch promotion: `firestarter_app` `v1.8-app-cleanup` → `beta` cuts `3.0.0b7` (next pre-release from current `3.0.0b6`); `firestarter` firmware sub-repo NOT promoted (host-only milestone — currently on `beta` from v1.6 close, no v1.8 commits to land); meta-repo `v1.8-app-cleanup` → `main` per the meta-repo "main carries `.planning/`" convention. Per v1.6 D-17v2 carry-forward, the `3.0.1` STABLE bump is DEFERRED to v1.9 read-bug fix (v1.8 is a clean refactor with GATE-1.8d ring-fencing the read path, but the read-bug itself remains by design — stable promotion premature until v1.9 fixes it).

Requirements: DOC-01, DOC-02, MS-01 (full text in `.planning/REQUIREMENTS.md` lines 74–76).

**Depends on:**
- Phase 42 (ERR-01/02/03 complete — `map_typed_errors` decorator + mypy strict on 8 modules + 70% coverage floor are the quality claims DOC-01 records).
- Phase 41 (CLI Migration — Click entry point + `cli_handlers.py` 14 commands + `dev` group are what the README "Architecture" module map enumerates).
- Phase 40 (Serial Transport Restructure — `frame_parser.py` + `codec.py` + `serial_comm.py` split is part of the module map).
- Phase 39 (Database Cleanup — `chip_resolver.resolve_chip` is part of the layer-boundary rules).
- Phase 38 (Low-risk Extractions — `exceptions.py` consolidated typed hierarchy + `address_parser.py` are module-map entries).
- Phase 37 (Tooling Baseline + CI Gate — `ruff` + `mypy` + `pytest --cov` is the workflow the README/CLAUDE.md tooling subsection names; CI gate live on `v1.8-app-cleanup` branch).
- Phase 36 (Characterization Test Baseline — 29 syrupy snapshots + `fake_serial` + `EpromDatabase.skip_local_override` seam are the GATE-1.8b/c/e witnesses).

**Unblocks:**
- v1.9 — Read-Bug RCA + Fix (PROPOSED). Phase 43 promotes the v1.9 block to Current Milestone in PROJECT.md; v1.9 phase numbering continues at Phase 44 after v1.8 ships.

</domain>

<decisions>
## Implementation Decisions

Operator picked recommended options on all four asked questions (DOC-01 scope minimal; CLAUDE.md targeted fixes; PROJECT.md current-milestone flip to v1.9-PROPOSED; ship-tag beta-only `3.0.0b7`). Operator picked **BOTH** for GATE-1.8 verification (software floor + real-hardware Step 0). Operator confirmed wave decomposition (3 plans mirroring v1.6 Phase 30) by selecting "Step in 43-03 HUMAN-UAT" (rejected separate 43-04 bench-smoke plan and pre-flight-in-43-02). Operator deselected "Ship-tag policy" from the gray-area picker initially, then asked the ship-tag question as the third PROJECT.md follow-up — answered beta-only `3.0.0b7`. Operator standing style (Phases 37–42): lean, minimum-churn, mirror prior milestone-close patterns verbatim, document deviations rather than escalate.

### DOC-01 — README + CLAUDE.md scope (locked per operator answers)
- **D-01:** **Minimal README.md insertion — single new `## Architecture` section.** Inserted between the existing top-of-file install/usage block and Examples; structurally:
  1. **Flat-module map** — one-line each for the 21 modules under `firestarter_app/firestarter/`: `main.py`, `cli_handlers.py`, `chip_resolver.py`, `frame_parser.py`, `codec.py`, `address_parser.py`, `exceptions.py`, `serial_comm.py`, `database.py`, `eprom_operations.py`, `hardware.py`, `firmware.py`, `config.py`, `constants.py`, `messages.py`, `logging_utils.py`, `eprom_info.py`, `ic_layout.py`, `utils.py`, `avr_tool.py`, `__init__.py`. Each entry: file name + 1 line of role description (e.g., `cli_handlers.py — Click command handlers + map_typed_errors decorator + AppContext dataclass`).
  2. **Layer-boundary rules** — short paragraph naming the post-v1.8 layering: Click handlers (`cli_handlers.py`) → service layer (`chip_resolver.py`, `eprom_operations.py`, `hardware.py`, `firmware.py`) → transport (`serial_comm.py`, `frame_parser.py`, `codec.py`) → wire protocol. Typed exceptions in `exceptions.py` flow upward; the `@map_typed_errors` decorator at the Click boundary maps them to stable exit codes (0/1/2).
  3. **Tooling workflow subsection** — names `ruff check` + `ruff format` + `mypy` (strict on 8 modules per Phase 42 D-06) + `pytest --cov-fail-under=70`; references the CI gate on `firestarter_app/.github/workflows/ci.yml` + the `pre-commit` config hook order (ruff-check → ruff-format → mypy).
  No TOC rewrite. No edits to Install / Usage / Commands sections. No new `CONTRIBUTING.md` file. Existing 592-line README structure preserved.
- **D-02:** **CLAUDE.md targeted fixes only — three edits.**
  1. **De-singleton fix:** Replace the `## Key Files` line `firestarter/database.py — EpromDatabase singleton: lookup, pin translation, command building` with `firestarter/database.py — EpromDatabase (skip_local_override seam, see Phase 36 D-06): lookup, pin translation, command building`.
  2. **Add post-v1.8 flat modules to Key Files list:** insert `frame_parser.py`, `codec.py`, `address_parser.py`, `chip_resolver.py`, `cli_handlers.py`, `exceptions.py` with one-line descriptions matching the README module map.
  3. **One new line on tooling gate:** add at end of Architecture section: `**Tooling gate (v1.8):** ruff check + ruff format + mypy strict on 8 modules + pytest --cov-fail-under=70; enforced by .github/workflows/ci.yml.`
  Data Flow diagram (lines 17–32) stays byte-identical. Wire Protocol block (44–64) stays byte-identical. Database Pipeline block (66–96) stays byte-identical. Constants block (98–100) stays byte-identical. No edits to existing wording — only ADD the de-singleton fix + new module lines + tooling-gate one-liner.

### DOC-02 — Milestone records + archive (locked per Phase 30 / v1.4 / v1.5 / v1.6 / v1.7 archive pattern)
- **D-03:** **MILESTONES.md grows a new `## v1.8 — Host CLI Structural Cleanup (firestarter_app) — Shipped 2026-05-XX` entry ABOVE the existing v1.6 entry.** Structure mirrors v1.6 verbatim:
  - Header line: `**Phases:** 8 (36–43) | **Plans:** 26+ (planner enumerates) | **Timeline:** 2026-05-27 (start) → 2026-05-XX (close) | **Ship tag:** 3.0.0b7 (beta-only — see D-09) | **Commits:** meta-repo X, firestarter_app sub-repo Y`
  - Delivered narrative: 8 phases bulleted (TEST baseline → tooling/CI → low-risk extractions → DB cleanup → serial restructure → CLI migration → error handling → docs+close)
  - Key Accomplishments: 27 requirements DELIVERED + 30/30 mapped per ROADMAP.md (lines 282–311)
  - Branch Strategy: per memory `feedback_branching` — sub-repo `v1.8-app-cleanup` off `beta`, meta-repo `v1.8-app-cleanup` off `main`, firmware sub-repo UNTOUCHED
  - Open backlog carry-forward: same three pending todos Phases 37–42 reviewed (`avrdude-mcu-detection-fallback`, `serial-cobs-resync-data-path`, `w27c512-eeprom-misclassification`) — annotated `carried forward to v1.9-or-later` (NOT v1.8-seed because v1.8 already shipped)
  - Key Decisions: cite locked decisions across Phases 36–42 (Phase 36 D-06 EpromDatabase skip_local_override seam; Phase 37 D-08 py39 / legacy type annotation style; Phase 38 D-01 exceptions.py consolidation; Phase 39 D-01 chip_resolver.resolve_chip; Phase 40 type-hinted serial_comm public API; Phase 41 D-08 `_resolve_or_exit` seam → Phase 42 `map_typed_errors`; Phase 42 D-04 no new exit codes; Phase 42 D-07 `eprom_operations.py` mypy strict deferred)
  - Known Gaps / Carry-forward to v1.9: read-bug (Bug A + Bug B), `eprom_operations.py` mypy strict (Phase 42 D-07), the three pending todos
  - Hardware Impact: NONE — host-only milestone; firmware sub-repo byte-identical to v1.6/v1.7 close state
- **D-04:** **`PROJECT.md` ship-history + Current Milestone flip.**
  1. **Ship-history block (lines 5–11):** Insert `**v1.8 shipped:** 2026-05-XX (Host CLI Structural Cleanup — 8 phases, 27 requirements; argparse → Click, flat layout, ruff + mypy strict on 8 modules + 70% coverage floor; ship tag 3.0.0b7 beta-only; v1.8-app-cleanup → beta + meta-repo → main; firmware sub-repo untouched; read-bug carries to v1.9 with GATE-1.8d ring-fence intact).` BELOW the existing v1.7 shipped line and ABOVE v1.6.
  2. **Current Milestone flip:** REPLACE the current `## Current Milestone: v1.8 — Host CLI Structural Cleanup (firestarter_app)` block (lines 13–41) with the existing `## v1.9 — Read-Bug RCA + Fix (PROPOSED)` content (currently at lines 43–56). The block becomes `## Current Milestone: v1.9 — Read-Bug RCA + Fix (PROPOSED)` with the existing v1.9 status/why/target-features/operator-next-step content preserved verbatim. Operator-next-step line stays `/gsd-discuss-milestone v1.9 to lock scope + decisions`.
  3. **New v1.8 Archive section:** Insert `## v1.8 Archive: Host CLI Structural Cleanup (firestarter_app) — Shipped 2026-05-XX` BETWEEN the (now-promoted) v1.9 Current Milestone block and the existing `## v1.6 — Fix the Read Bug — ✓ Shipped 2026-05-26` block. The new v1.8 Archive block mirrors the v1.4 Archive shape (lines 90–106 in current PROJECT.md): one paragraph delivered narrative + cross-link to `.planning/MILESTONES.md` v1.8 entry + cross-link to `.planning/milestones/v1.8-phases/` for per-phase artifacts.
  4. **Last updated footer:** Refresh to `2026-05-XX — v1.8 milestone shipped (Host CLI Structural Cleanup; 8 phases, 27 requirements; ship tag 3.0.0b7 beta-only; v1.9 Read-Bug RCA promoted to Current Milestone).`
- **D-05:** **`.planning/ROADMAP.md` v1.8 section collapse.** Lines 15–314 (the `## v1.8 — Host CLI Structural Cleanup (STARTED 2026-05-27)` block + `### v1.8 Coverage` table) collapse into a single `## v1.8 — Host CLI Structural Cleanup (SHIPPED 2026-05-XX)` heading followed by a `<details>` block. Structure mirrors the existing v1.5/v1.6/v1.7 collapsed blocks at lines 316–367:
  ```
  ## v1.8 — Host CLI Structural Cleanup (SHIPPED 2026-05-XX)

  <details>
  <summary>✓ v1.8 shipped — Host CLI structural cleanup (firestarter_app); 8 phases, 27 requirements; ship tag 3.0.0b7 beta-only. Full detail in `.planning/MILESTONES.md` §v1.8.</summary>

  - **Ship tag:** `3.0.0b7` (beta-only; stable bump deferred to v1.9 read-bug fix per D-17v2 carry-forward)
  - **Phases:**
    - [x] Phase 36: Characterization Test Baseline (TEST-01..05)
    - [x] Phase 37: Tooling Baseline + CI Gate (TOOL-01..03)
    - [x] Phase 38: Low-risk Extractions (STRUCT-01..05)
    - [x] Phase 39: Database Cleanup + Chip Resolver (DATA-01..04)
    - [x] Phase 40: Serial Transport Restructure (SERIAL-01..03)
    - [x] Phase 41: CLI Migration argparse → Click (CLI-01..04)
    - [x] Phase 42: Error Handling Normalization + Quality Sweep (ERR-01..03)
    - [x] Phase 43: Documentation + Milestone Close (DOC-01..02, MS-01)
  - **Branch model:** sub-repo `v1.8-app-cleanup` off `beta` (firestarter_app only); meta-repo `v1.8-app-cleanup` off `main`; firmware sub-repo untouched.
  - **v1.9 hand-off:** read-bug (Bug A + Bug B) carries forward with GATE-1.8d ring-fence intact; baseline binaries at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` still valid.
  - See full archive: `.planning/MILESTONES.md` §v1.8.

  </details>
  ```
  The v1.8 Coverage table (30 rows) gets EXTRACTED into the new `.planning/milestones/v1.8-REQUIREMENTS.md` archive per D-06 (NOT lost — moved).
- **D-06:** **New `.planning/milestones/v1.8-REQUIREMENTS.md` archive file** modeled on `.planning/milestones/v1.6-REQUIREMENTS.md`. Header notes `Archived 2026-05-XX at v1.8 close`. Body carries the 30-row v1.8 Coverage table from ROADMAP.md (lines 282–311) — transcribed verbatim — plus per-requirement disposition column annotating `DELIVERED` (default for 27 of 30 — TEST-01..05, TOOL-01..03, STRUCT-01..05, DATA-01..04, SERIAL-01..03, CLI-01..04, ERR-01..03) + `VERIFIED` (DOC-01, DOC-02, MS-01 once Phase 43 closes) + `DEFERRED-to-v1.9` for any carry-forward items (none in v1.8's 30 since the milestone scope was tight). Cross-references the v1.8 MILESTONES.md entry. The live `.planning/REQUIREMENTS.md` (currently the v1.8 file per header check at execution time) is CREATE-NEW move — copied to `.planning/milestones/v1.8-REQUIREMENTS.md` and then either deleted from live surface (if v1.9 wants a fresh file) or kept (if `/gsd-new-milestone v1.9` will overwrite it). Plan 43-02 picks per execution-time inspection of REQUIREMENTS.md current state (mirrors v1.6 Plan 30-02's reconciliation choice).
- **D-07:** **`.planning/v1.8-archive.sh` mirrors `.planning/v1.6-archive.sh` verbatim** with phase numbers 36–43 (NOT 26–30). Same `--dry-run` support, same explicit per-phase enumeration (T-30-03 mitigation), same destination `.planning/milestones/v1.8-phases/`, same refuse-to-overwrite-non-empty pre-flight, same idempotence check, same next-steps echo at end. Plan 43-02 produces the script + runs it live.

### MS-01 — GATE-1.8 verification + branch promotion (locked per BOTH path)
- **D-08:** **GATE-1.8 (a–e) verification uses the BOTH path — software floor in Plan 43-01/02 + real-hardware Step 0 in Plan 43-03.**
  - **Software floor (Plan 43-01/02 autonomous):** Plan 43-01 pre-flight asserts: (a) `pytest` exits 0 with 241+ passed (verifies GATE-1.8a wire-protocol byte-identity via `test_serial_characterization.py` + `test_decoder.py`; GATE-1.8b CLI surface via 29 syrupy snapshots; GATE-1.8c constants parity via `test_firmware_contract.py` against `firestarter/include/firestarter.h` + `rurp_shield.h` + `rurp_pinout.h`; GATE-1.8e suite green); (b) `pip install -e . && firestarter --help` exits 0 (GATE-1.8e entry-point smoke); (c) `ruff check` + `ruff format --check` + `mypy` exit 0 (Phase 42 ERR-* quality gates green); (d) `pytest --cov-fail-under=70` exits 0 (Phase 42 D-15 coverage floor). All four asserts MUST pass before Plan 43-01 writes the docs+state flips. GATE-1.8d (read-path ring-fence) is structurally enforced by the suite (the `_read_and_parse_lines` byte-identity test + `_run_state_machine` body invariants).
  - **Real-hardware Step 0 (Plan 43-03 HUMAN-UAT):** BEFORE branch-merge steps, operator runs `firestarter read -e W27C512 -o /tmp/v18-smoke.bin` on the Modified Rev 0 + Leonardo bench (per memory `project_v18_rca_seed_bug_a_bug_b` — known-stable v1.6 baseline leg). Diff `/tmp/v18-smoke.bin` against an existing N=5 baseline from `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`. PASS gate: `sha256sum` of `/tmp/v18-smoke.bin` matches AT LEAST ONE of the 5 baseline-set `sha256` values OR a structural diff (≤ N differing bytes per the Phase 26 consistency-check threshold) — operator picks which baseline file to compare against based on which sub-revision their Modified Rev 0 currently shows. FAIL gate: re-open Phase 43 (the bench-smoke disagreement means GATE-1.8a slipped despite suite-green — Phase 38/39/40/41/42 introduced an undetected wire-byte regression). Per memory `feedback_chip_out_before_sideload`, the chip stays in socket throughout the bench step (no firmware re-flash); per memory `feedback_verify_port_identity_each_task`, operator verifies `controller:` identity in the boot banner before issuing the read.
- **D-09:** **Ship-tag policy: beta-only `3.0.0b7` from `firestarter_app/v1.8-app-cleanup` → `beta`; STABLE `3.0.1` DEFERRED to v1.9.** Per v1.6 D-17v2 carry-forward in `MILESTONES.md` line 5 (`3.0.1 stable deferred to a real read-bug fix in v1.8 per D-17v2`) — v1.8 doesn't fix the read-bug (carried to v1.9 with GATE-1.8d ring-fence). The v1.8 milestone is a clean refactor protected by GATE-1.8a/b/c/d/e, but stable bump pre-RCA-fix would (i) overpromise to PyPI stable users that the read-path is fixed when it isn't, (ii) waste the stable-tag-as-RCA-witness signal. Beta-only `3.0.0b7` (next pre-release from current `3.0.0b6` at v1.6 close) lets `pip install --pre firestarter` users pick up the structural cleanup + bug fixes without misleading the stable channel. Firmware sub-repo NOT promoted (host-only milestone — `firestarter/` currently on `beta` from v1.6 close, no v1.8 commits). Meta-repo `v1.8-app-cleanup` → `main` per the meta-repo "main carries `.planning/`" convention (no PyPI/release implication). Plan 43-03 HUMAN-UAT.md documents `3.0.0b7` as the LOCKED recommendation; operator may overrule at UAT time to `3.0.1` stable IFF they accept that stable carries the unfixed read-bug — but the plan default is `3.0.0b7` and DOES NOT hedge with `<ship-tag-TBD>` tokens (rejected per the operator's beta-only answer).
- **D-10:** **Plan 43-03 is `autonomous: false` (operator-authorized HUMAN-UAT).** Per memory `feedback_branching` + the v1.6 Plan 30-03 / v1.4 Plan 20-01 pattern — all sub-repo merges + tag operations require operator authorization. The HUMAN-UAT.md grows a 6-step checklist:
  - **Step 0 (NEW — per D-08):** Real-hardware GATE-1.8a witness (`firestarter read -e W27C512` on Mod Rev 0 + Leonardo; byte-identical match against `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`).
  - **Step 1:** Branch identity verification — `git -C /workspaces/firestarter_app rev-parse v1.8-app-cleanup` returns the post-Phase-42 HEAD `9999bdb` (per STATE.md `Last commit:` line); `git -C /workspaces/firestarter rev-parse beta` returns `0bbe017` (v1.6 close — unchanged through v1.8 per host-only scope); meta-repo `git rev-parse v1.8-app-cleanup` returns post-43-02 HEAD.
  - **Step 2:** firestarter_app sub-repo `v1.8-app-cleanup` → `beta` merge; cut `3.0.0b7` per D-09.
  - **Step 3:** firmware sub-repo — VERIFY NO-OP (no v1.8 commits to land; `firestarter/` stays at `beta` tip `0bbe017`).
  - **Step 4:** Meta-repo `v1.8-app-cleanup` → `main` merge.
  - **Step 5:** STATE.md flip + MILESTONES.md `<TBD-from-43-03>` token substitution (commit SHAs + ship date + final commit counts).
- **D-11:** **Plan decomposition: 3 plans, strict sequential chain (worktrees off per memory `project_v18_phase_execution_mechanics`).**
  - **Plan 43-01 — Docs + state flips (autonomous).** `firestarter_app/README.md` Architecture section insertion (per D-01); `firestarter_app/CLAUDE.md` targeted fixes (per D-02); `.planning/PROJECT.md` ship-history line + Current Milestone flip + v1.8 Archive insert + footer refresh (per D-04); `.planning/MILESTONES.md` v1.8 entry written ABOVE v1.6 (per D-03) with `<TBD-from-43-03>` placeholders for final commit SHAs + ship date. Commit: `docs(43-01): record v1.8 ship-state (DOC-01, DOC-02 substrate)`. Software-floor GATE-1.8 asserts (per D-08) run as pre-flight before the commit.
  - **Plan 43-02 — Archive + ROADMAP collapse + REQUIREMENTS.md archive (autonomous).** Build `.planning/v1.8-archive.sh` (per D-07); dry-run first; live-run moves phases 36–43 into `.planning/milestones/v1.8-phases/`; collapse `.planning/ROADMAP.md` v1.8 section (per D-05); create `.planning/milestones/v1.8-REQUIREMENTS.md` (per D-06). Commit: `chore(43-02): archive v1.8 phase directories + collapse ROADMAP + create REQUIREMENTS archive (DOC-02)`.
  - **Plan 43-03 — Operator-authorized branch promotion (autonomous: false).** Produces `.planning/milestones/v1.8-phases/43-documentation-milestone-close/43-HUMAN-UAT.md` per D-10. Operator executes the 6-step checklist (Step 0 bench + Steps 1–5 branch ops + STATE.md flip). On all-pass: STATE.md flipped to v1.8-SHIPPED state (`milestone: v1.9`, `status: pending` for v1.9 OR `status: none` if operator hasn't run `/gsd-new-milestone v1.9`); MILESTONES.md `<TBD-from-43-03>` tokens substituted with real values. Commit (operator-authorized): `docs(43-03): record v1.8 milestone close + branch promotion (MS-01)`.
- **D-12:** **Plan dependency graph:** 43-01 → 43-02 → 43-03. Strict sequential. 43-01 establishes the doc + MILESTONES substrate that 43-02 archives + collapses; 43-03 depends on both because the HUMAN-UAT.md path computation is POST-archive (it lives at `.planning/milestones/v1.8-phases/43-documentation-milestone-close/43-HUMAN-UAT.md`, not the pre-archive `.planning/phases/43-*/43-HUMAN-UAT.md`). Mirrors v1.6 Plan 30-01 → 30-02 → 30-03 chain.

### Claude's Discretion
- **MILESTONES.md `<TBD-from-43-03>` placeholder set** — Plan 43-01 writes the v1.8 entry with placeholders for: final commit SHAs (firestarter_app post-merge tip; meta-repo post-merge tip), final commit counts (meta-repo Phase 43 commits + firestarter_app v1.8-app-cleanup commit total), ship date. Planner picks the exact placeholder strings (recommend `<TBD-from-43-03>` to match v1.6 Plan 30-01 convention).
- **Archive script script-or-runbook decision in 43-02** — recommend a real bash script (`.planning/v1.8-archive.sh`) mirroring v1.6's verbatim. If the planner sees the v1.6 script has bit-rotted on the path computation (e.g., the `META_ROOT` assumption changed), a runbook (markdown checklist) is acceptable fallback — but the verbatim mirror is the default.
- **v1.8-REQUIREMENTS.md disposition column shape** — recommend `Status | Phase | Disposition` triple per row (mirroring v1.6-REQUIREMENTS.md). Planner picks the exact column wording at execution time.
- **README.md Architecture section header level** — recommend `## Architecture` (level-2 heading, sibling to existing `## Table of Content` + `## Installation` + `## Usage`). Planner may pick `### Architecture` if it logically nests under an existing block, but level-2 is the cleanest cut.
- **Module map ordering in README** — recommend grouping by layer (Click handlers first → service layer → transport → data), mirroring the layer-boundary-rules paragraph. Planner may pick alphabetical for "easier scanning" — both acceptable; layer-grouped is recommended.
- **Bench step file-system path for the smoke binary** — `/tmp/v18-smoke.bin` is a recommendation; planner may pick `firestarter_app/v18-smoke.bin` if the bench session wants the artifact preserved post-merge (operator's call at UAT time).

### Reviewed Todos (not folded)
Same three pending todos Phases 37/38/39/40/41/42 reviewed — all hardware/protocol/DB-content, out of this docs-and-close phase's domain:
- `avrdude-mcu-detection-fallback.md` — blank-chip / wrong-firmware recovery (hardware; v1.9-or-later).
- `serial-cobs-resync-data-path.md` — COBS framing on serial data path (protocol; v1.9-or-later if revisited; would change wire framing).
- `w27c512-eeprom-misclassification.md` — chip-DB content classification fix (DB data; not docs/close work).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope & locked milestone decisions
- `.planning/ROADMAP.md` — Phase 43 detail (lines 265–274 — Goal + SC#1..SC#3 + Depends + Requirements + UI hint); v1.8 Coverage table (lines 280–311); GATE-1.8 (a–e) standing gate (lines 23–34); v1.6/v1.7/v1.5 collapsed `<details>` blocks (lines 316–367) — the structural model for D-05.
- `.planning/REQUIREMENTS.md` — DOC-01, DOC-02, MS-01 (lines 74–76); GATE-1.8 (a–e) (lines 12–20); Out-of-Scope table (firmware untouched, no protocol change, file layout flat).
- `.planning/PROJECT.md` — Current Milestone v1.8 block (lines 13–41) — what gets archived; v1.9-PROPOSED section (lines 43–56) — what gets promoted to Current; v1.4 / v1.5 / v1.6 / v1.7 Archive sections (lines 58–131) — the structural model for D-04.3 v1.8 Archive insert.

### Prior-milestone close pattern (the template Phase 43 mirrors)
- `.planning/milestones/v1.6-phases/30-documentation-milestone-close/30-01-PLAN.md` — autonomous docs+state flips template for Plan 43-01 (PROJECT.md flip + MILESTONES.md entry + todo carry-forward).
- `.planning/milestones/v1.6-phases/30-documentation-milestone-close/30-02-PLAN.md` — autonomous archive+ROADMAP-collapse template for Plan 43-02 (`.planning/v1.6-archive.sh` shape; ROADMAP `<details>` collapse; REQUIREMENTS.md archive).
- `.planning/milestones/v1.6-phases/30-documentation-milestone-close/30-03-PLAN.md` — operator-authorized HUMAN-UAT template for Plan 43-03 (6-step checklist; branch promotion; ship-tag decision; STATE.md flip).
- `.planning/v1.6-archive.sh` — the verbatim script Plan 43-02 mirrors (with phase numbers 36–43 instead of 26–30).
- `.planning/milestones/v1.6-REQUIREMENTS.md` — the per-requirement-disposition table Plan 43-02 mirrors.
- `.planning/milestones/v1.4-phases/20-end-to-end-smoke-test-milestone-close/20-01-PLAN.md` — alternate HUMAN-UAT template for Plan 43-03 (v1.4 is the original beta-aware release pattern; v1.4 Plan 20-01 has the canonical operator branch-promotion checklist).
- `.planning/MILESTONES.md` (lines 1–80) — v1.6 entry shape Plan 43-01 mirrors for the v1.8 entry.

### Prior-phase context this phase records (v1.8 phase chain)
- `.planning/phases/42-error-handling-normalization-quality-sweep/42-CONTEXT.md` — Phase 42's full decision set (D-01..D-17 + Claude's Discretion); names the post-v1.8 module set that DOC-01's module map enumerates (`main.py`, `cli_handlers.py`, `chip_resolver.py`, `frame_parser.py`, `codec.py`, `address_parser.py`, `exceptions.py`, `serial_comm.py`); names the quality gate (mypy strict on 8 modules + 70% coverage floor) that DOC-01's tooling subsection records.
- `.planning/phases/41-cli-migration-argparse-click/41-CONTEXT.md` — Click migration anchor (`cli_handlers.py` 14 commands + `dev` group + `AppContext` dataclass + `_resolve_or_exit` seam → Phase 42 `map_typed_errors`); the Click entry-point smoke is GATE-1.8e witness.
- `.planning/phases/40-serial-transport-restructure/40-CONTEXT.md` — `serial_comm.py` + `frame_parser.py` + `codec.py` split; `_read_and_parse_lines` body invariant (GATE-1.8a/d witness).
- `.planning/phases/39-database-cleanup-chip-resolver/39-CONTEXT.md` — `chip_resolver.resolve_chip` (the direct call site Phase 42 D-05 made canonical).
- `.planning/phases/38-low-risk-extractions/38-CONTEXT.md` — `exceptions.py` consolidation + `address_parser.py` extraction.
- `.planning/phases/37-tooling-baseline-ci-gate/37-CONTEXT.md` — `target-version = py39` + legacy `Optional[X]` / `List[X]` style + CI gate live on `v1.8-app-cleanup` + `tools/check_mypy_watermark.py`; the canonical tooling-workflow reference DOC-01 names.
- `.planning/phases/36-characterization-test-baseline/36-CONTEXT.md` — `fake_serial` + `make_comm` + `EpromDatabase.skip_local_override` seam (the D-02 CLAUDE.md de-singleton fix anchor); 29 syrupy snapshots (GATE-1.8b witness); BUG-2 xfail (closed Phase 42 D-02).

### Files this phase edits / creates
- **PRIMARY EDIT (Plan 43-01):** `firestarter_app/README.md` — insert single new `## Architecture` section (per D-01); ~80–100 new lines (module map 21 entries × 2 lines + layer-boundary paragraph + tooling subsection). Insertion point: between top-of-file install/usage block and the existing Examples section. NO TOC rewrite; the existing Table of Content block at line 32 stays byte-identical (Architecture section is INSERTED below the TOC reference, not added to the TOC — minimum churn).
- **PRIMARY EDIT (Plan 43-01):** `firestarter_app/CLAUDE.md` — three targeted edits per D-02 (de-singleton line fix; Key Files list grows 6 new module lines; tooling-gate one-line at Architecture section end). NO other edits. Data Flow diagram + Wire Protocol + DB Pipeline + Constants blocks byte-identical.
- **PRIMARY EDIT (Plan 43-01):** `.planning/PROJECT.md` — four edits per D-04 (ship-history line + Current Milestone flip + v1.8 Archive section insert + footer refresh).
- **PRIMARY EDIT (Plan 43-01):** `.planning/MILESTONES.md` — insert new `## v1.8 — Host CLI Structural Cleanup (firestarter_app) — Shipped 2026-05-XX` entry ABOVE the existing v1.6 entry per D-03; placeholders `<TBD-from-43-03>` for commit SHAs + ship date + final commit counts.
- **PRIMARY EDIT (Plan 43-02):** `.planning/ROADMAP.md` — collapse v1.8 section per D-05; ~300 lines collapse to ~25 lines (`<details>` block).
- **NEW (Plan 43-02):** `.planning/v1.8-archive.sh` — verbatim mirror of `.planning/v1.6-archive.sh` with phase numbers 36–43 per D-07.
- **NEW (Plan 43-02):** `.planning/milestones/v1.8-REQUIREMENTS.md` — 30-row coverage table + per-requirement disposition column per D-06.
- **STRUCTURAL (Plan 43-02):** `.planning/phases/36-*` through `.planning/phases/43-*` → `.planning/milestones/v1.8-phases/{36-*..43-*}/` (script runs `mv`).
- **NEW (Plan 43-03):** `.planning/milestones/v1.8-phases/43-documentation-milestone-close/43-HUMAN-UAT.md` — 6-step operator checklist per D-10 (path computation: by the time Plan 43-03 runs, Plan 43-02 has already archived the phase 43 directory, so the file lands at the POST-archive path, not `.planning/phases/43-*/43-HUMAN-UAT.md`).
- **EDIT (Plan 43-03, operator-authorized):** `.planning/STATE.md` — milestone flip from `v1.8` to `v1.9` + `status: completed` → `status: pending` (or `none`) + `last_activity` refresh; happens at operator-confirmation time post-Step-5, not pre-emptively.
- **NO-TOUCH:**
  - `firestarter/` firmware sub-repo (host-only milestone per scope decision; firmware stays at `beta` tip `0bbe017` from v1.6 close).
  - `firestarter_app/firestarter/*.py` — all 21 modules byte-identical (Phase 42 was the last quality sweep; Phase 43 is docs + close).
  - `firestarter_app/tests/` — full suite stays at 241+ passed + 29 syrupy snapshots; no test changes.
  - `firestarter_app/pyproject.toml` — Phase 42 was the last quality-gate edit; Phase 43 doesn't touch the build/test config.
  - `firestarter_app/.github/workflows/ci.yml` — CI gate already enforces ruff + ruff-format + mypy + pytest --cov-fail-under=70 from Phase 42; no edits.
  - `firestarter_app/autocomplete.md` — Click completion docs from Phase 41; out of scope per D-01 minimal scope.
  - `firestarter_app/things.md`, `firestarter_app/anything.txt`, `firestarter_app/datasheets/`, etc. — operator-scratch / non-shipping; out of scope.
  - `.planning/REQUIREMENTS.md` — STATE-DEPENDENT: if currently the v1.8 file, copied (not moved) to `.planning/milestones/v1.8-REQUIREMENTS.md` and either left in place or deleted per Plan 43-02 execution-time inspection (mirrors v1.6 Plan 30-02 reconciliation).
  - `firestarter/doc/SHIELD-REVISIONS.md` — v1.7 sub-repo operator-facing doc per memory `project_v17_shield_docs_layering`; v1.8 makes no shield changes so no lockstep update.

### Branch state (for D-10 Step 1 verification)
- **firestarter_app sub-repo:** branch `v1.8-app-cleanup` at HEAD `9999bdb` (per STATE.md `Last commit:` line) — `chore(42-03): raise v1.8 quality gates`. Cut from `beta@3.0.0b6`.
- **firestarter sub-repo:** branch `beta` at HEAD `0bbe017` from v1.6 close (no v1.8 commits — host-only milestone).
- **meta-repo:** branch `v1.8-app-cleanup` (current per `git status`); branched off `main`. Pre-43 HEAD: `8d299ba` (`docs(42): record verification — passed_with_concerns`).

### CI / release surface (for D-09 ship-tag execution)
- `firestarter_app/.github/workflows/beta-release.yml` — beta-release workflow Plan 43-03 invokes for `3.0.0b7` cut (per v1.4 beta pipeline from `.planning/v1.4-RELEASE-PROCEDURES.md`).
- `firestarter_app/.github/workflows/release.yml` — stable-release workflow Plan 43-03 does NOT invoke this milestone (stable bump deferred to v1.9).
- `.planning/v1.4-RELEASE-PROCEDURES.md` — operator-readable beta-cut + lockstep-coordination steps (the canonical reference for HUMAN-UAT Step 2 wording).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`.planning/v1.6-archive.sh`** — verbatim script Plan 43-02 mirrors; supports `--dry-run`, explicit per-phase enumeration, refuse-to-overwrite-non-empty destination, idempotence check. Plan 43-02 changes only the phase-number list (26–30 → 36–43) and the destination path (`v1.6-phases` → `v1.8-phases`).
- **`.planning/milestones/v1.6-REQUIREMENTS.md`** — per-requirement-disposition table shape Plan 43-02 mirrors for `.planning/milestones/v1.8-REQUIREMENTS.md` (30 rows instead of 16).
- **v1.5 / v1.6 / v1.7 collapsed `<details>` blocks in `.planning/ROADMAP.md` lines 316–367** — the structural shape Plan 43-02 mirrors for the v1.8 collapse.
- **v1.4 / v1.5 / v1.6 Archive blocks in `.planning/PROJECT.md` lines 58–131** — the structural shape Plan 43-01 mirrors for the v1.8 Archive section insert.
- **`.planning/MILESTONES.md` v1.6 entry (lines 1–80)** — the structural shape Plan 43-01 mirrors for the v1.8 entry.
- **`.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`** — 15 N=5 W27C512 binary baselines that Step 0 of Plan 43-03 HUMAN-UAT compares the bench-smoke read against.

### Established Patterns
- **Milestone-close shape: 3 plans, strict sequential, autonomous→autonomous→operator-authorized** — established by v1.4 Phases 19+20, v1.6 Phase 30; Phase 43 mirrors verbatim.
- **`<details>`-block ROADMAP collapse** — established by v1.5/v1.6/v1.7 close; the `<summary>` line carries the ship marker + cross-link to MILESTONES.md.
- **Archive script idempotence** — established by `.planning/v1.4-archive.sh` + `.planning/v1.6-archive.sh`; refuse-to-overwrite-non-empty + explicit per-phase enumeration + --dry-run support.
- **Operator-authorized branch promotion via HUMAN-UAT.md** — established by v1.6 Plan 30-03 / v1.4 Plan 20-01; 6-step checklist + ship-tag decision documentation + STATE.md flip on all-pass.
- **D-17v2 carry-forward (3.0.1 stable deferred to read-bug fix)** — established by v1.6 close; v1.8 inherits the deferral (since v1.8 doesn't fix the read-bug); v1.9 close will lift it.
- **PROJECT.md ship-history-line format** — `**vX.Y shipped:** YYYY-MM-DD (one-line summary)` — established across v1.2/v1.4/v1.5/v1.6/v1.7 lines; Phase 43 D-04.1 follows verbatim.
- **MILESTONES.md entry shape: Phases | Plans | Timeline | Ship tag | Commits header + Delivered + Key Accomplishments + Branch Strategy + Open backlog + Key Decisions + Known Gaps + Hardware Impact** — established by v1.6 entry; Phase 43 D-03 mirrors verbatim.

### Integration Points
- **Plan 43-02 → Plan 43-03 path computation** — Plan 43-02 archives the phase 43 directory, so Plan 43-03's HUMAN-UAT.md lands at the POST-archive path `.planning/milestones/v1.8-phases/43-documentation-milestone-close/43-HUMAN-UAT.md`, not the pre-archive `.planning/phases/43-*/`. Mirrors v1.6 Plan 30-03's path computation.
- **MILESTONES.md `<TBD-from-43-03>` token substitution** — Plan 43-01 writes placeholders for final commit SHAs + ship date + commit counts; Plan 43-03 Step 5 substitutes them at operator-confirmation time. Mirrors v1.6 Plan 30-01 → 30-03 token flow.
- **STATE.md milestone-flip timing** — happens at Plan 43-03 Step 5 operator-confirmation time (after Steps 0–4 PASS), NOT pre-emptively at 43-01 or 43-02. If operator hits a Step 0–4 issue, the plan stays in `executing` state and re-opens cleanly.
- **firmware sub-repo no-op verification** — Plan 43-03 Step 3 verifies firmware sub-repo at unchanged `beta@0bbe017` (per host-only scope decision); operator does NOT invoke any firmware merge or tag op.
- **Software-floor GATE-1.8 pre-flight in Plan 43-01** — `pytest` + `pip install -e . && firestarter --help` + `ruff check` + `ruff format --check` + `mypy` + `pytest --cov-fail-under=70` all MUST exit 0 before Plan 43-01 writes the docs+state flips. If any fails, Phase 43 doesn't ship — the failure means Phase 36–42 work isn't actually green at the v1.8-app-cleanup tip and a phase re-opens. Mirrors the v1.6 Plan 30-01 pre-flight contract.

</code_context>

<specifics>
## Specific Ideas

- The operator continues the standing Phase 37–42 "you recommend" delegation pattern — selected the recommended option on all four asked questions (DOC-01 scope, CLAUDE.md scope, README Architecture content, PROJECT.md flip target) plus the ship-tag tail follow-up (beta-only `3.0.0b7`). Picked **BOTH** for GATE-1.8 verification — software floor + real-hardware Step 0 — which is the only deviation from "recommended single option"; the operator wants the bench-smoke witness on top of the suite-green floor (raises confidence; uses USB-passthrough; one bench session). Picked "Step in 43-03 HUMAN-UAT" for where the bench gate lands (rejected a separate 43-04 plan or 43-02 pre-flight inline).
- The bench-smoke witness choice (W27C512 on Leonardo + Modified Rev 0) anchors GATE-1.8a to the existing v1.6 N=5 baseline binaries at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`. This is the right anchor because (i) the v1.6 RCA characterized that bench leg as the "stable" baseline (Bug A only affects Modified Rev 0 upper-address jitter; the baseline IS the post-revert known-good shape per `project_v18_rca_seed_bug_a_bug_b`), (ii) byte-identical match proves Phase 36–42 didn't slip a wire-byte regression, (iii) the operator can pick which of the 15 baseline files to compare against based on which sub-revision their Modified Rev 0 currently shows (per memory `user_shield_revisions`).
- The ship-tag `3.0.0b7` choice (beta-only) is locked by D-17v2 carry-forward — `3.0.1` stable was explicitly deferred to "a real read-bug fix in v1.8" per the v1.6 MILESTONES.md entry. Since v1.8 doesn't fix the read-bug (carried to v1.9 with GATE-1.8d ring-fence), the stable bump deferral carries forward to v1.9 close. Plan 43-03 HUMAN-UAT.md records `3.0.0b7` as LOCKED (not hedged with `<ship-tag-TBD>` tokens — the operator's beta-only answer rejects the v1.6 hedge pattern). Operator may overrule at UAT time to `3.0.1` IFF they accept the read-bug carry — but the plan default is beta-only and the rationale is recorded.
- The PROJECT.md Current Milestone flip to v1.9-PROPOSED reuses the existing v1.9 block content verbatim (lines 43–56 of the pre-Phase-43 PROJECT.md). No content edit — just position swap with the old v1.8 Current Milestone block (which becomes the v1.8 Archive section per D-04.3). Lowest churn flip pattern.
- The 3-plan decomposition mirrors v1.6 Phase 30 verbatim — autonomous docs+state (43-01) → autonomous archive+ROADMAP collapse (43-02) → operator-authorized HUMAN-UAT branch promotion (43-03). The Step 0 bench-smoke gate inside 43-03 is the ONE addition to the v1.6 pattern (v1.6 had no real-hardware step in Plan 30-03 because the bench had already produced Phase 29 v2 PASS_PARKED before close).

</specifics>

<deferred>
## Deferred Ideas

- **`3.0.1` stable promotion** — explicitly deferred per D-09 to v1.9 read-bug fix. v1.8 ships as beta-only `3.0.0b7` because the read-bug isn't fixed (carried to v1.9 with GATE-1.8d ring-fence). Operator may overrule at UAT time but plan default is beta-only.
- **Firmware sub-repo touch** — explicitly out per host-only scope decision. Firmware stays at `beta@0bbe017` from v1.6 close; no v1.8 commits to land; no firmware tag operation.
- **`eprom_operations.py` mypy strict overrides** — explicitly deferred per Phase 42 D-07 to v1.9 (post-RCA when read path can be touched freely). Phase 43 does NOT add it; the carry-forward is recorded in the v1.8 MILESTONES.md entry's "Known Gaps / Carry-forward to v1.9" block.
- **`CONTRIBUTING.md` for firestarter_app** — explicitly out per D-01 minimal scope. The Architecture section in README.md + the targeted CLAUDE.md fixes give contributors enough on-ramp; a dedicated CONTRIBUTING.md is over-engineering for a host-CLI of this size. Defer to a future milestone if contributor volume actually grows.
- **README TOC rewrite + section reorg** — explicitly out per D-01. The 592-line README structure stays byte-identical except for the single new `## Architecture` section insertion. Defer to a future "docs-only" milestone if the existing structure proves unwieldy.
- **CLAUDE.md full re-sync** (Data Flow diagram rewrite + Layer Boundary Rules subsection + Constants block expansion) — explicitly out per D-02. Three targeted edits only. Defer to v1.9 close if the post-RCA changes warrant a structural rewrite.
- **`firestarter_app/autocomplete.md`** edits — explicitly out per D-01 minimal scope. Phase 41 wrote it for Click completion; v1.8 doesn't change the completion surface.
- **`firestarter_app/things.md`, `anything.txt`, `*.bin` cleanup** — operator-scratch files in the sub-repo root; out of scope for milestone close. `*.bin` is git-ignored per `firestarter_app/.gitignore`; `things.md` + `anything.txt` are operator-tracked but not shipping artifacts.
- **`firestarter/doc/SHIELD-REVISIONS.md` lockstep update** — v1.7 sub-repo operator-facing doc per memory `project_v17_shield_docs_layering`. v1.8 makes no shield-revision changes so no lockstep edit needed.
- **`/gsd-discuss-milestone v1.9` scope discussion** — explicitly out of Phase 43. Operator runs it after v1.8 closes; Phase 43 only PROMOTES the existing v1.9 PROPOSED block to Current Milestone. Locking v1.9 scope is v1.9's own milestone-discuss work.
- **`pluggy` / structured `Result[T, E]` types** — explicitly out per Phase 42 deferred list ("Over-abstraction for a CLI of this size"). Defer indefinitely.
- **`PROTOSM-01` — extract `ProtocolStateMachine` from `serial_comm.py`** — explicitly deferred per v1.8 REQUIREMENTS Future Requirements + Phase 42 deferred list. HIGH complexity; would touch the read path. Defer to v1.9-or-later.

### Reviewed Todos (not folded)
Same three pending todos Phases 37/38/39/40/41/42 reviewed — all hardware/protocol/DB-content, out of this docs-and-close phase's domain:
- `avrdude-mcu-detection-fallback.md` — blank-chip / wrong-firmware recovery (hardware; v1.9-or-later).
- `serial-cobs-resync-data-path.md` — COBS framing on the serial data path (protocol; would change wire framing — forbidden by GATE-1.8a; v1.9-or-later if revisited).
- `w27c512-eeprom-misclassification.md` — chip-DB content classification fix (DB data, not docs/close work this phase touches).

</deferred>

---

*Phase: 43-Documentation + Milestone Close*
*Context gathered: 2026-05-29*

# Phase 29: Multi-Board Bench Verification — Pattern Map

**Mapped:** 2026-05-22
**Files analyzed:** 2 planning-doc modifications + 0 source edits + 4 read-only source references
**Analogs found:** 6 / 6 (all exact analogs in `.planning/` evidence corpus + read-only refs to host CLI source)

> **Phase 29 is unusual.** It is a verification phase — **no source-of-truth code edits, no firmware/host changes, no branch operations**. The planner consumes this PATTERNS.md to:
> 1. Tell the executor exactly which existing Markdown sections to copy as templates for the Wave A scaffold.
> 2. Tell the executor exactly which read-only source files to inspect for command-surface sanity checks (`-e` flag absence, handshake stdout shape, output-dir argument shape).
> 3. Tell the verifier which row-schema invariants to check on Wave B fill-in.

## File Classification

| Touched File | Role | Data Flow | Closest Analog | Match Quality |
|--------------|------|-----------|----------------|---------------|
| `.planning/v1.6-EVIDENCE.md` (append at line-186 anchor) | evidence-doc / append-only Markdown | cross-phase document accretion | `.planning/v1.6-EVIDENCE.md` Phase 26 baseline (lines 12-19) + Phase 27 RCA (lines 22-108) + Phase 28 fix-context (lines 112-185) — same file, immediately preceding sections | EXACT (same file, same schema, same anchor convention) |
| `.planning/v1.5-BENCH-RESULTS.md` (append at EOF / line 46+) | evidence-doc / append-only Markdown | post-hoc closure addendum | `.planning/v1.5-BENCH-RESULTS.md` Verdict block (lines 36-45) + Summary row schema (lines 10-22) — same file, append after existing closure | EXACT (same file, mirror row schema with extra `v1.6 fix reference` column per D-11) |
| `.planning/phases/29-multi-board-bench-verification/29-01-PLAN.md` (NEW, Wave A) | gsd-plan | autonomous task list | `.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-01-PLAN.md` (desk-side scaffold shipping `dev consistency-check`) | role-match (desk-side `autonomous: true` plan) |
| `.planning/phases/29-multi-board-bench-verification/29-02-PLAN.md` (NEW, Wave B) | gsd-plan | operator-on-bench task list | `.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-02-PLAN.md` (operator-on-bench session; per `26-02-SUMMARY.md`) | EXACT (same shape: pre-flight + per-board verification + EVIDENCE.md fill + Verdict close) |
| `.planning/STATE.md` (updated by gsd-sdk at phase close; Phase 29 plans may touch on FAIL per D-07) | state-tracker | append/replace | Existing STATE.md pattern (touched by every phase closer; FAIL path per Phase 28 carry-over) | role-match |
| `firestarter/platformio.ini` (READ-ONLY — Wave A invokes `pio run -e <env>` against it) | config (consumed) | static read | n/a — direct consumption, no edit | n/a |
| `firestarter_app/firestarter/main.py:create_dev_args` + `create_write_args` (READ-ONLY — sanity check) | source (consumed) | static read | n/a — direct consumption, no edit | n/a |
| `firestarter_app/firestarter/eprom_operations.py:consistency_check_eprom` (READ-ONLY — stdout regex contract) | source (consumed) | static read | n/a — direct consumption, no edit | n/a |
| `firestarter_app/firestarter/firmware.py:check_current_firmware` (READ-ONLY — handshake stdout shape) | source (consumed) | static read | n/a — direct consumption, no edit | n/a |

## Pattern Assignments

### A. `.planning/v1.6-EVIDENCE.md` — append at line-186 anchor (Wave A scaffolds, Wave B fills)

**Anchor (locate by grep, not by line number — per RESEARCH Pitfall 6):**
```
grep -n '<!-- Phase 29 inverts here:' /workspaces/.planning/v1.6-EVIDENCE.md
# → 186:<!-- Phase 29 inverts here: ## Phase 29 — Post-fix Consistency-Check Verification (YYYY-MM-DD). Same 9-column row schema; Verdict cells flip from FAIL to PASS, SHAs distinct cells go from N to 1. -->
```

Insertion occurs immediately AFTER this comment (line 187+). The existing comment stays in place; Phase 29 does NOT delete or rewrite it.

#### Pattern A1: 9-column row schema (D-08 — mirror Phase 26 verbatim)

**Analog source:** `.planning/v1.6-EVIDENCE.md:14-18` (Phase 26 baseline section). Header and row format copied verbatim:

```markdown
| Board | Port | Chip | N | SHAs distinct | Divergent bytes (run1 vs run2) | First-diverge offset | Verdict | Log |
|-------|------|------|---|---------------|------------------------------|----------------------|---------|-----|
| uno | /dev/ttyACM0 | W27C512 (id 0xda08) | 3 | 1 | 0 / 65536 (0.0%) | — | PASS (unexpected — refutes pre-existing-bug prediction on uno) | `.planning/v1.6/consistency-check-runs/W27C512-uno-20260521-133418/` |
| leonardo | /dev/ttyACM1 | W27C512 (id 0xda01) | 3 | 3 | 1349 / 65536 (2.1%) | 0x0003 | FAIL (jitter reproduced — 32U4 USB-CDC + 1024-B buffer path) | `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/` |
| uno328pb | /dev/ttyUSB0 | DEFERRED | — | — | — | — | DEFERRED — board has wrong FW (per operator 2026-05-21); was misidentified as 328PB in v1.5 bench notes. Requires reflash before re-baseline. | — |
```

**Phase 29 inverts each cell-for-cell** (per D-08 + CONTEXT line 26):
- Every `Verdict` flips `FAIL → PASS` (Leonardo) and stays `PASS (regression check)` (Uno).
- Every `SHAs distinct` cell flips `3 → 1` (Leonardo) and stays `1` (Uno).
- `Divergent bytes` flips `1349 / 65536 (2.1%) → 0 / 65536 (0.0%)` (Leonardo).
- `First-diverge offset` flips `0x0003 → —`.
- uno328pb resolves per D-01 Case A (real row) or Case B (DEFERRED — code-equivalence rationale).
- N column = `5` in every Phase 29 row (was `3` in Phase 26 — D-03).

#### Pattern A2: Phase-section header + bench-session metadata block

**Analog source:** `.planning/v1.6-EVIDENCE.md:12` (Phase 26 header line) + lines 112-115 (Phase 28 header + metadata block). Copy the metadata block shape verbatim, adapt for Phase 29:

```markdown
## Phase 29 — Post-fix Consistency-Check Verification (YYYY-MM-DD)

**Bench session:** YYYY-MM-DD (operator-on-bench, single session)
**Firmware sideloaded to chip:** locally-built `firestarter_<board>.hex` from `firestarter/v1.6-read-bug` (LOCAL branch, commit `4f205e58`) via `pio run -e <env> -t upload` (or `avrdude -c urclock` for uno328pb path)
**Host CLI:** locally-installed from `firestarter_app/v1.6-read-bug` (tip `c057fe2`) via `pip install -e .`
**Branch flow (Phase 29):** sub-repo branches stay LOCAL; no merges, no pushes, no public tags. Phase 30 owns the `v1.6-read-bug → beta → main` promotion + pre-release cut (ROADMAP Phase 30 SC#5).
```

(Pulled verbatim from CONTEXT.md D-08; one-to-one analog with Phase 28's `**Landed:** 2026-05-21 / **Branch:** ...` block at lines 114-115 of EVIDENCE.md.)

#### Pattern A3: Forward-annotation HTML comment (cross-phase append-only contract)

**Analog source:** `.planning/v1.6-EVIDENCE.md:20, 110, 186` — three forward-annotation comments, one per phase boundary. Phase 29 itself does NOT plant a Phase-30 forward-annotation because Phase 30 is the milestone-close (no further inverted-table appends expected). But the line-186 comment STAYS in place — Wave A insertion goes after it; verifier checks the comment is still present and unmodified.

```markdown
<!-- Phase 29 inverts here: ## Phase 29 — Post-fix Consistency-Check Verification (YYYY-MM-DD). Same 9-column row schema; Verdict cells flip from FAIL to PASS, SHAs distinct cells go from N to 1. -->
```

#### Pattern A4: Hardware metadata snapshot table (D-10 — mirror Phase 26)

**Analog source:** `.planning/v1.6-EVIDENCE.md:208-212` (Phase 26 Hardware metadata snapshot table). Phase 29 mirrors verbatim with one column rename — `FW build` carries `4f205e58` + the local-build version string (likely `3.0.0b4`, no `+local` suffix per RESEARCH Pitfall 4):

```markdown
### Hardware metadata snapshot
| Board | Effective hw rev (after operator config) | Physical shield | Native auto-detect | FW build (local commit + version string) | Chip ID seen |
|-------|------------------------------------------|-----------------|--------------------|------------------------------------------|--------------|
| Plain Uno (`/dev/ttyACM0`) | Rev2 (override cleared, auto-detect) | <Rev X.X — operator declares> | Rev2 | `4f205e58` / `3.0.0b4` | W27C512 0xda08 |
| Leonardo (`/dev/ttyACM1`) | Rev2 (via override `--rev 2`) | <Rev X.X + voltage-divider mod — operator declares> | Rev1 | `4f205e58` / `3.0.0b4` | W27C512 0xda01 |
| uno328pb (`/dev/ttyUSB0`) | <per D-01 Case A or B> | <operator declares> | <per handshake> | `4f205e58` / `3.0.0b4` (Case A) OR — (Case B) | <per D-01> |
```

Memory `[[user_shield_revisions]]` mandate: operator MUST declare which shield rev (Rev 2.2 / Rev 2.0 / modified Rev 0) is on each board at session start. EEPROM `hw_revision` byte cannot distinguish them — the snapshot table is the only audit trail.

#### Pattern A5: Per-board build hash record (NEW sub-section, Wave A captures)

**No exact analog** — Phase 28 §"Per-board `.hex` sizes (D-07)" at EVIDENCE.md:161-171 is the closest in shape (3-row board table with `.hex` size column). Phase 29 adopts the same row-per-board structure but replaces `.hex size` with SHA-256 capture:

```markdown
### Per-board build hash record (Wave A capture)
| Board | Local hex path | SHA-256 of hex | Source commit | Build timestamp |
|-------|----------------|----------------|---------------|-----------------|
| uno | firestarter/.pio/build/uno/firestarter_uno.hex | <sha256> | `4f205e58` | YYYY-MM-DD HH:MM |
| leonardo | firestarter/.pio/build/leonardo/firestarter_leonardo.hex | <sha256> | `4f205e58` | YYYY-MM-DD HH:MM |
| uno328pb | firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex | <sha256> | `4f205e58` | YYYY-MM-DD HH:MM |
```

Wave A capture command (verified in RESEARCH §"Code Examples — Wave A"):
```bash
shasum -a 256 \
  firestarter/.pio/build/uno/firestarter_uno.hex \
  firestarter/.pio/build/leonardo/firestarter_leonardo.hex \
  firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex
```

Expected hex sizes per Phase 28 D-07 size table (EVIDENCE.md:165-169): uno=62,617 B; leonardo=68,917 B; uno328pb=62,854 B.

#### Pattern A6: Sub-section breakdown (1:1 to VERIFY-NN)

Phase 29's section has FOUR distinct sub-tables per D-08:

| Sub-section | Schema | Wave that fills | Analog |
|-------------|--------|-----------------|--------|
| `### Pre-flight checklist (operator)` | bulleted text + per-board command snippets | A scaffolds, B references | Phase 26-02-SUMMARY.md "patterns-established" + RESEARCH "Code Examples" |
| `### Per-board build hash record` | 5-col board table (Pattern A5) | A fills | None exact — see Pattern A5 |
| `### Hardware metadata snapshot` | 6-col board table (Pattern A4) | B fills | EVIDENCE.md:208-212 |
| `### VERIFY-01 + VERIFY-02 — Full-chip consistency-check (post-fix; 9-column schema)` | 9-col board table (Pattern A1) | B fills | EVIDENCE.md:14-18 |
| `### VERIFY-03 — 1KB low-rate jitter (post-fix)` | 7-col board table (Board / Port / Chip / N / SHAs distinct / Verdict / Note) | B fills | None exact — invented per D-05; simpler than 9-col |
| `### VERIFY-04 — BENCH-02 post-hoc closure` | cross-reference + 1-line summary | B fills | None exact — cross-ref to `v1.5-BENCH-RESULTS.md` addendum (Pattern B1) |
| `### Verdict` | 4-line bulleted CLOSED/DEFERRED per VERIFY-NN + Hand-off to Phase 30 | B fills | EVIDENCE.md:188-204 (Phase 26 Verdict block — same shape; Phase 29 inverts the verdicts) |

#### Pattern A7: Verdict block + Hand-off to Phase 30

**Analog source:** `.planning/v1.6-EVIDENCE.md:188-204` (Phase 26 Verdict block: REPRO-01/02/03 with closure narrative). Phase 29's Verdict block mirrors the shape:

```markdown
### Verdict
- **VERIFY-01:** [CLOSED ✓ | DEFERRED with code-equivalence rationale per D-01 Case B]
- **VERIFY-02:** [CLOSED ✓ — Leonardo Verdict inverted from Phase 26 FAIL; Uno regression check held]
- **VERIFY-03:** [CLOSED ✓ — root cause is NOT masked: 1KB jitter resolved alongside 64KB jitter per ROADMAP SC#3]
- **VERIFY-04:** [CLOSED ✓ — Phase 24 BENCH-02 post-hoc row added to v1.5-BENCH-RESULTS.md]

### Hand-off to Phase 30
All VERIFY-NN PASS → Phase 30 may proceed with: `firestarter/v1.6-read-bug` → `firestarter/beta` merge + pre-release cut + `firestarter_app/v1.6-read-bug` → `firestarter_app/beta` merge + PyPI pre-release publish + optional install-pipeline regression check via `firestarter fw -i --pre --force` + `beta → main` promotion + operator-authorized stable tag bump.

Any FAIL → milestone re-opens per D-07; Phase 30 does NOT execute the merge until a future bench session re-validates.
```

#### Pattern A8: FAIL post-mortem block (D-07 — milestone re-opens)

**No exact analog** — Phase 26 closed PASS+PASS+DEFERRED; no FAIL block in the EVIDENCE.md corpus. The closest analog is Phase 28's `### Read-path-only inspection (GATE-1.6 desk-side confirmation)` at EVIDENCE.md:173-180 (prose block embedded inside a phase section). Phase 29 Wave B verifier MUST encode this branch in the PLAN.md but only writes it to EVIDENCE.md if a FAIL actually fires.

Template (CONTEXT.md D-07 verbatim):
```markdown
### Wave B FAIL post-mortem (only if any axis FAILs)
- Board: <board>
- Axis: <full-chip | 1KB | BENCH-02>
- Symptom: <single-bit-flip distribution / chunk-boundary clustering / etc.>
- Differential vs Phase 26 baseline: <comparison>
- Run output: <link to .planning/v1.6/post-fix-runs/...>
- Next step: STATE.md → "v1.6 milestone re-opened — Phase 28 fix masked vs fixed root cause; further RCA needed"
```

---

### B. `.planning/v1.5-BENCH-RESULTS.md` — append at EOF (line 46+; Wave A scaffolds the section, Wave B fills the row)

**Anchor:** Append after current line 45 (Operator authorization line). File is 45 lines; insertion at line 46+.

#### Pattern B1: Post-hoc closure section + row addendum

**Analog source:** `.planning/v1.5-BENCH-RESULTS.md:10-22` (existing Summary row schema: `| Row | Item | Status | Evidence |`). Phase 29 D-11 mirrors this row format but adds the `v1.6 fix reference` column per CONTEXT line 26.

Verbatim row template per CONTEXT.md D-11 (lines 312-324):
```markdown
## Phase 24 BENCH-02 post-hoc closure (YYYY-MM-DD via v1.6 Phase 29)

**Closes:** v1.5 Phase 24 BENCH-02 acceptance criterion ("write→read→verify on a representative EPROM") — previously CLOSED with caveat (Row 11: full-chip read returned ~57% different bytes across consecutive calls; closed on the strength of small-window write verification).

**Resolution:** v1.6 Phase 28 read-bug fix (firmware commits `437339b6` PORTx-clear + `4f205e58` `_NOP()` settling) eliminates the pre-existing read-streaming jitter. Phase 29 bench session re-runs the write→read→verify cycle and confirms byte-identity.

| Bench item | Result | Evidence |
|-----------|--------|----------|
| SST27SF512 write→read→verify (Leonardo, post-fix `firestarter/v1.6-read-bug` LOCAL build `4f205e58`) | ✓ PASS — byte-identical via `cmp` | Phase 28 fix commits `437339b6` + `4f205e58` (LOCAL on `firestarter/v1.6-read-bug` at Phase 29 time; Phase 30 promotes); Phase 29 EVIDENCE.md §"VERIFY-04 — BENCH-02 post-hoc closure"; bench session YYYY-MM-DD |

**Verdict:** BENCH-02 fully closed (no caveat). `.planning/todos/pending/large-read-data-jitter-uno328pb.md` ready for Phase 30 DOC-01 move-to-resolved.

**Note on commit SHAs:** the cited fix commits are LOCAL on `firestarter/v1.6-read-bug` when this row lands. If Phase 30 uses a non-fast-forward merge (default for `beta` workflow), the post-merge `firestarter/beta` HEAD SHAs differ from `437339b6` / `4f205e58`; the original commits stay reachable as merge ancestors. If Phase 30 uses a squash-merge, only the squashed commit SHA appears on `beta`. Either way, the LOCAL SHAs cited here are unambiguous + grep-able in `git log --all`. Phase 30 may amend this row with the public SHAs post-merge for cross-reference.
```

**Row-schema deviation from v1.5 existing rows:** the existing v1.5 table is 4-column (`Row | Item | Status | Evidence`); Phase 29's addendum is 3-column (`Bench item | Result | Evidence`) because the Row number is implicit (it's a post-hoc addendum, not part of the original numbered list). The `v1.6 fix reference` referenced in CONTEXT line 26 is folded into the `Evidence` column rather than added as a separate column — keeps the addendum table compact.

#### Pattern B2: Verdict caveat removal narrative

**Analog source:** `.planning/v1.5-BENCH-RESULTS.md:38` (BENCH-02 Verdict line: `**BENCH-02: CLOSED with caveat** ⚠ — write path is bench-validated...`). Phase 29 D-11 addendum's `**Verdict:** BENCH-02 fully closed (no caveat).` is the empirical inversion — same sentence structure, caveat dropped.

---

### C. `.planning/phases/29-multi-board-bench-verification/29-01-PLAN.md` — Wave A (desk-side, `autonomous: true`)

#### Pattern C1: Two-plan structure (D-04 — mirrors Phase 26)

**Analog source:** `.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-01-PLAN.md` (desk-side scaffold ship) — 26-01 ships the `dev consistency-check` diagnostic + scaffolds EVIDENCE.md. Phase 29 Wave A scaffolds EVIDENCE.md + BENCH-RESULTS.md addendum + builds 3 `.hex` artifacts locally. Both plans are `autonomous: true`, ~5 min wall-clock, single-session executable.

**Task list shape (per CONTEXT.md D-04 + RESEARCH "Primary recommendation"):**
1. Build 3 firmware envs: `cd firestarter && git checkout v1.6-read-bug && pio run -e uno && pio run -e leonardo && pio run -e uno328pb`. (Per RESEARCH note: artifacts already on disk from 2026-05-21; this is no-op or relink-only.)
2. Capture SHA-256 of each `.hex` via `shasum -a 256`. Record in Pattern A5 table.
3. Install host CLI: `cd firestarter_app && git checkout v1.6-read-bug && pip install -e .`. Verify via `firestarter dev consistency-check --help`. (Per RESEARCH A4 + Open Question 1: inspect `git status` for the uncommitted `firestarter/config.py` modification; surface diff to operator if needed.)
4. Locate Phase 29 anchor in EVIDENCE.md via `grep -n '<!-- Phase 29 inverts here:'` (NOT a hardcoded line number — RESEARCH Pitfall 6).
5. Append Phase 29 section scaffold (Patterns A2 + A3 + A5 + A6 + A7 + A8 above) immediately after the anchor.
6. Append v1.5-BENCH-RESULTS.md post-hoc closure section scaffold (Pattern B1) at EOF.

#### Pattern C2: `<read_first>` block (gsd-plan convention)

**Analog source:** `.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-01-PLAN.md` and `28-01-PLAN.md` per repository convention. Each plan opens with a `<read_first>` block enumerating files the executor must load before acting. For Phase 29 Wave A:

```
<read_first>
- .planning/phases/29-multi-board-bench-verification/29-CONTEXT.md (locked decisions D-01..D-11)
- .planning/phases/29-multi-board-bench-verification/29-RESEARCH.md (Pitfalls 1-7; corrected -e flag absence)
- .planning/v1.6-EVIDENCE.md (lines 12-19 Phase 26 baseline, 112-185 Phase 28 fix-context, 186 Phase 29 anchor)
- .planning/v1.5-BENCH-RESULTS.md (lines 10-22 Summary table format, 36-45 Verdict block)
- firestarter/platformio.ini (env definitions for pio run)
- firestarter/CLAUDE.md §"Development Commands" (pio run + upload canonical commands)
- firestarter_app/CLAUDE.md §"Development Commands" (pip install -e . path)
</read_first>
```

(Plan-level convention; gsd-planner emits.)

#### Pattern C3: NO branch operations (corrected from initial draft)

**Negative-pattern source:** CONTEXT.md `<domain>` paragraph at line 10 ("Phase 29 has no source-of-truth code edits and **NO branch merges or remote pushes**") + RESEARCH "Anti-Patterns to Avoid" line 328-329 (don't use `firestarter fw -i --pre --force`; don't cut `3.0.0b5` in Phase 29). Plan Wave A task list MUST NOT include `git merge`, `git push`, `git tag`, `update_version.py`, or any GitHub Actions workflow trigger. The branches `firestarter/v1.6-read-bug` and `firestarter_app/v1.6-read-bug` stay LOCAL.

---

### D. `.planning/phases/29-multi-board-bench-verification/29-02-PLAN.md` — Wave B (operator-on-bench, `autonomous: false`)

#### Pattern D1: Pre-flight + post-flight bench session narrative

**Analog source:** `.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-02-SUMMARY.md` (the CANONICAL operator-on-bench narrative per CONTEXT line 376). Key excerpts to copy as Wave B task structure:

**Pre-flight checklist excerpt (26-02-SUMMARY.md:42-44 "patterns-established"):**
```markdown
- "Bench-driven dual-board pattern: both Arduinos plugged in simultaneously on /dev/ttyACM0 + /dev/ttyACM1, separate chips socketed in each, no USB swap between board runs."
- "Shell exit capture for piped commands: use ${PIPESTATUS[0]} to capture firestarter's exit code when tee'ing output. `$?` after a pipe captures tee's exit (always 0 unless tee itself fails) and silently masks firestarter's exit-2 hardware-error signal."
```

**Bench-run pattern (26-02-SUMMARY.md:68-72):**
```markdown
- REPRO-01 closed (PASS, unexpected): Plain Uno + Rev 2.0 shield + W27C512 (chip ID 0xda08) produced 3 byte-identical 64KB reads at SHA-256 <hex>. ~20s per read.
- REPRO-02 closed (FAIL, jitter reproduced): Leonardo + modified Rev 0 shield + W27C512 (chip ID 0xda01) produced 3 distinct SHAs across 3 consecutive 64KB reads. 1349 / 65536 byte-jitter rate = 2.1%; first divergence at offset 0x0003 (run_1=0x83, run_2=0x03)
```

Wave B mirrors this narrative shape — Phase 29 inverts every Verdict cell to PASS (regression) for Uno and PASS (FIX CONFIRMED) for Leonardo.

#### Pattern D2: Per-board × per-axis task structure (3 boards × 3 axes = 9 verification cells + 1 hardware metadata + 1 hand-off)

**Analog source:** RESEARCH §"Architecture Patterns — System Architecture Diagram, Wave B" (lines 219-269). Phase 29 Wave B's task list per board:

```bash
# === Per-board task block (repeat for uno, leonardo, uno328pb) ===
BOARD=leonardo  PORT=/dev/ttyACM1   # or uno + /dev/ttyACM0; or uno328pb + /dev/ttyUSB0
TS=$(date +%Y-%m-%d-%H%M%S)

# Step 1: Sideload
cd /workspaces/firestarter
pio run -e ${BOARD} -t upload --upload-port ${PORT}
# (uno328pb fallback: avrdude -p atmega328pb -c urclock -b 115200 -P /dev/ttyUSB0 \
#                       -U flash:w:.pio/build/uno328pb/firestarter_uno328pb.hex:i)

# Step 2: Handshake check
firestarter -p ${PORT} fw
# Source: firestarter_app/firestarter/firmware.py:115
# Expected stdout: "Current firmware version: 3.0.0b4, for controller: ${BOARD} on port ${PORT}"
# uno328pb branches per D-01 Case A (handshake reports uno328pb) or Case B (reports uno OR avrdude signature mismatch)

# Step 3: VERIFY-01/02 full-chip consistency-check (Axis 1)
firestarter -p ${PORT} dev consistency-check W27C512 \
  --runs 5 \
  --output-dir .planning/v1.6/post-fix-runs/W27C512-${BOARD}-${TS} \
  --force \
  2>&1 | tee .planning/v1.6/bench-logs/W27C512-${BOARD}-${TS}.log
ec=${PIPESTATUS[0]}  # CRITICAL: $? would mask firestarter's exit (Pitfall 2)
echo "EXIT: ${ec}"

# Step 4: VERIFY-03 1KB shell-loop (Axis 2)
for i in $(seq 5); do
  firestarter -p ${PORT} dev read W27C512 -s 1024 -a 0 /tmp/r1k_${BOARD}_$i.bin
done
sha256sum /tmp/r1k_${BOARD}_*.bin
# Expected: 5 IDENTICAL SHA-256 prefixes
```

```bash
# === Leonardo-only: VERIFY-04 BENCH-02 cycle (Axis 3) ===
PORT=/dev/ttyACM1
# Step 5a: Generate test image (RESEARCH Open Question 3 default — pseudo-random for compare integrity)
python3 -c "import os; open('/tmp/sst_test.bin','wb').write(os.urandom(65536))"

# Step 5b: Write (DEFAULT path = blank-check + erase + write; -e is NOT a real flag per Pitfall 1)
firestarter -p ${PORT} write SST27SF512 /tmp/sst_test.bin
# If "ERROR: Not supported" on erase step (v1.5 w27c512-eeprom-misclassification carryover):
#   firestarter -p ${PORT} write SST27SF512 /tmp/sst_test.bin -b -a 0
# (where -b means --no-blank-check per main.py:97-103, also skips erase)

# Step 5c: Read back
firestarter -p ${PORT} dev read SST27SF512 -s 65536 -a 0 /tmp/sst_readback.bin

# Step 5d: Compare
cmp /tmp/sst_test.bin /tmp/sst_readback.bin
echo "cmp exit: $?"   # 0 = byte-identical PASS
```

#### Pattern D3: uno328pb Case A vs Case B branch (D-01 + RESEARCH Pitfall 3)

**Negative-pattern source:** RESEARCH Pitfall 3 line 376-381 — Wave B plan must NOT have a single 3-board loop without branch logic. Explicit branch:

- **Case A** — `firestarter -p /dev/ttyUSB0 fw` reports `for controller: uno328pb` → board has true ATmega328PB silicon → run the full Step 3 + Step 4 verification → fill row normally in Pattern A1 schema.
- **Case B** — handshake reports `uno` (or avrdude exited with `device signature = 0x1e950f / expected 0x1e9516`) → v1.5 misidentification confirmed at silicon level → mark row `DEFERRED — board confirmed Plain Uno per [[project_uno328pb_correction]]; VERIFY-01 closes via code-equivalence with Uno row (Phase 28 hex Δ=0 between uno and uno328pb builds — see EVIDENCE.md Phase 28 size table)`.

Both branches close VERIFY-01 — Case A directly, Case B by code-equivalence rationale anchored on Phase 28 EVIDENCE.md:165-169 `.hex` size table (uno328pb Δ=0).

#### Pattern D4: Verifier behavior on FAIL (D-07 — milestone re-opens)

**Negative-pattern source:** CONTEXT.md D-07 verbatim. Plan Wave B verifier task explicitly enumerates the FAIL branch:

```
If ANY axis FAILs (any board, any of: full-chip / 1KB / BENCH-02):
  1. Preserve failing run binaries + sha256s + offset distributions in EVIDENCE.md.
  2. Mark affected VERIFY-NN cell `FAIL` with linked run output.
  3. Append Wave B FAIL post-mortem (Pattern A8 template).
  4. HALT bench session. Do NOT promote `beta → main`. Do NOT mark VERIFY-NN closed.
  5. Update STATE.md → "v1.6 milestone re-opened — Phase 28 fix masked vs fixed root cause; further RCA needed".
  6. Phase 29 stays open. Future bench session re-runs with revised fix.
```

NO auto-retry / auto-debug. The verifier MUST halt and surface.

#### Pattern D5: Optional Wave B sanity gate (Phase 27 5-line Python cross-check rerun)

**Analog source:** `.planning/v1.6-EVIDENCE.md:99-108` (Phase 27 5-line Python script for divergence counting against committed baseline binaries). Phase 29 RESEARCH §"Phase 27 cross-check 5-liner" (line 554-563) provides the post-fix variant. Optional verifier sanity gate; expected output `Total divergences: 0`.

---

## Shared Patterns

### S1: Cross-phase append-only with HTML-comment anchors

**Source:** `.planning/v1.6-EVIDENCE.md` lines 20, 110, 186 — each `<!-- Phase N appends here: ... -->` is a unique substring grep-able anchor.
**Apply to:** Wave A scaffold task in 29-01-PLAN.md.

```bash
# Locate the anchor (don't trust hardcoded line numbers per Pitfall 6)
grep -n '<!-- Phase 29 inverts here:' /workspaces/.planning/v1.6-EVIDENCE.md
# Insert AFTER the matched line.
```

### S2: 9-column row schema lock (D-08; Phase 26 contract)

**Source:** `.planning/v1.6-EVIDENCE.md:14` (header row).
**Apply to:** Every VERIFY-01/02 row in Phase 29 section. Columns + order are immutable across all v1.6 phases.

```
| Board | Port | Chip | N | SHAs distinct | Divergent bytes (run1 vs run2) | First-diverge offset | Verdict | Log |
```

### S3: `${PIPESTATUS[0]}` for shell exit capture under `tee`

**Source:** `.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-02-SUMMARY.md:44` (patterns-established) — codified bench-session anti-pattern.
**Apply to:** Wave B's per-board consistency-check invocations (Step 3 above). `$?` after a pipe captures tee's exit (always 0); `${PIPESTATUS[0]}` captures firestarter's exit. The `firestarter dev consistency-check` exit code semantics (per RESEARCH §"Phase Requirements" — VERIFY-02 row) are `0=PASS, 1=FAIL, 2=hw-error`.

### S4: Operator pre-flight declares shield rev (D-10 + memory `[[user_shield_revisions]]`)

**Source:** Memory rule — EEPROM `hw_revision` byte cannot distinguish Rev 2.2 / Rev 2.0 / modified Rev 0. The hardware metadata snapshot table is the ONLY audit trail.
**Apply to:** Wave B's first task block ("session start — hardware metadata snapshot"). Operator MUST declare which shield rev (Rev 2.2 / Rev 2.0 / modified Rev 0) is on each board at session start. Recorded in Pattern A4 table.

### S5: Local-sideload (no public release)

**Source:** CONTEXT.md D-02 + `<domain>` paragraph + RESEARCH §"Pattern 4: Local-sideload before public commit".
**Apply to:** Both Wave A (build) and Wave B (upload) plans. NO `firestarter fw -i --pre --force`; NO `update_version.py`; NO `git push`; NO `git merge`. All branch promotion is Phase 30's scope per ROADMAP Phase 30 SC#5.

### S6: Read-only source consumption (no edits to `firestarter/` or `firestarter_app/` sources)

**Source:** CONTEXT.md `<domain>` line 10 ("no source-of-truth code edits"); RESEARCH `<phase_requirements>` table.
**Apply to:** All read-only source references below — Wave A/B may READ these files to sanity-check the host-CLI argument surface BUT must not modify any line.

Read-only source references (Wave A executor inspects; Wave B operator relies on):

| File | Line range | Why Phase 29 reads it |
|------|-----------|----------------------|
| `firestarter/platformio.ini` | full file | `pio run -e <env>` consumes; verify the 3 env definitions exist (`[env:uno]`, `[env:leonardo]`, `[env:uno328pb]`). |
| `firestarter_app/firestarter/main.py` | 93-116 | `create_write_args` — confirm Pitfall 1 (NO `-e` flag; `-b` is `--no-blank-check`). |
| `firestarter_app/firestarter/main.py` | 366-481 | `create_dev_args` — confirm `dev consistency-check` subparser carries `--runs`, `--output-dir`, `--keep-files`, `--max-diffs`, `-q`, `-f`. |
| `firestarter_app/firestarter/main.py` | 790-924 | `fw` and `dev` dispatch; consistency_check_eprom invocation site (line 914-923) — verify exit-code semantics 0/1/2. |
| `firestarter_app/firestarter/eprom_operations.py` | 431-603 | `consistency_check_eprom` — stdout regex contract (`Consistency check: PASS`, `Distinct SHAs: 1`, `Output dir: ...`). |
| `firestarter_app/firestarter/firmware.py` | 80-127 | `check_current_firmware` — handshake stdout line 115 emits `Current firmware version: {ver}, for controller: {board_name} on port {port_name}` — the source of truth for the `for controller: <board>` substring Wave B greps for in Case A/B branch. |

---

## No Analog Found

| Section | Why no exact analog | Planner action |
|---------|---------------------|----------------|
| **VERIFY-03 sub-table (7-column 1KB jitter)** | Phase 26 baseline did NOT include a 1KB sub-table — the 1KB shell-loop verification was added in Phase 29 D-05. | Use the simplified 7-col schema from CONTEXT.md D-05 lines 167-173: `Board / Port / Chip / N / SHAs distinct / Verdict / Note`. Wave A scaffolds; Wave B fills. |
| **Per-board build hash record table** | Phase 28's `.hex` size table (EVIDENCE.md:165-169) is the closest in shape but tracks SIZE not SHA-256. | Use the 5-col schema from CONTEXT.md D-08 lines 236-240 (Board / Local hex path / SHA-256 / Source commit / Build timestamp). Captures Wave A `shasum -a 256` output. |
| **Hand-off to Phase 30 block** | No prior phase had a "hand-off" sub-section — Phase 26-28 each closed with internal verdict only. | Use the verbatim CONTEXT.md D-08 hand-off template (lines 268-271). Drops a clear "Phase 30 may proceed with..." signal so Phase 30 orchestrator can read it. |
| **uno328pb Case A vs Case B branch** | Phase 26's uno328pb row was unconditionally DEFERRED — no branch logic in the row text. | Plan D3 above; plan Wave B explicitly with two branches per CONTEXT.md D-01. |

## Metadata

**Analog search scope:**
- `/workspaces/.planning/v1.6-EVIDENCE.md` (entire 219-line file, all 4 prior phase sections)
- `/workspaces/.planning/v1.5-BENCH-RESULTS.md` (entire 45-line file, all 11 existing rows + Verdict)
- `/workspaces/.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-02-SUMMARY.md` (canonical pre-flight + post-flight bench session narrative)
- `/workspaces/.planning/phases/29-multi-board-bench-verification/29-CONTEXT.md` (full file)
- `/workspaces/.planning/phases/29-multi-board-bench-verification/29-RESEARCH.md` (full file)
- `/workspaces/firestarter_app/firestarter/main.py` (lines 93-116 + 366-481 + 790-924)
- `/workspaces/firestarter_app/firestarter/eprom_operations.py` (lines 431-603)
- `/workspaces/firestarter_app/firestarter/firmware.py` (lines 80-127)

**Files scanned:** 8 (5 planning docs + 3 host-CLI source files; all read-only).

**Pattern extraction date:** 2026-05-22

**Note for planner:** Phase 29 has NO code edits. PATTERNS.md is here to point the planner at the EXACT existing Markdown sections to mirror (Patterns A1-A8 / B1-B2 above) and the EXACT read-only source files to reference for command-surface accuracy (Pattern S6 table). Wave A/B plans should paste large excerpts of CONTEXT.md D-08 + D-11 verbatim — those decisions are already templated for execution.

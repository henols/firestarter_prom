---
phase: 21-firmware-target-uno328pb
plan: "01"
subsystem: meta-repo / firmware-baseline
tags: [gate-1.5, baseline, requirements-amendment, uno328pb, path-b]
dependency_graph:
  requires:
    - firestarter/beta @ 5fd751e (clean working tree, version.h unmodified)
    - PlatformIO 6.1.19 + atmelavr 5.2.0 toolchain locally available
  provides:
    - .planning/v1.5/baselines/firestarter_uno.hex (pre-rework GATE-1.5 baseline)
    - .planning/v1.5/baselines/firestarter_leonardo.hex (pre-rework GATE-1.5 baseline)
    - .planning/v1.5/baselines/CAPTURE-PROCEDURE.md (reproducible recipe + SHA-256 anchors)
    - REQUIREMENTS.md FW-02 amended (Path B locked; RURP_BOARD_NAME single source of truth)
  affects:
    - Plan 21-02 (consumes baselines via cmp -s GATE-1.5 step; implements the FW-02-amended scheme)
tech-stack:
  added:
    - none (planning-only plan; no firmware-sub-repo edits)
  patterns:
    - GATE-1.5 byte-identity via cmp -s against checked-in pre-rework baselines (v1.4 lockstep-dryrun-fixture precedent reapplied for v1.5)
    - Single-source-of-truth board-id triple anchored on -D RURP_BOARD_NAME build-flag (drops the boards/*.json escape hatch)
key-files:
  created:
    - .planning/v1.5/baselines/firestarter_uno.hex
    - .planning/v1.5/baselines/firestarter_leonardo.hex
    - .planning/v1.5/baselines/CAPTURE-PROCEDURE.md
  modified:
    - .planning/REQUIREMENTS.md (FW-02 only; FW-01 / FW-03 / FW-04 / REL-* / INST-* / GATE-* / BENCH-* / DOC-* / MS-* untouched)
decisions:
  - "Path B locked at the requirements layer: FW-02 no longer mentions boards/uno328pb.json; the requirement now reads against the [env:uno328pb] block + name_firmware.py rework with RURP_BOARD_NAME as the single source of truth (CONTEXT D-05 / D-09)."
  - "Baselines captured with include/version.h LITERALLY unmodified (VERSION=\"3.0.0b2\") so Plan 21-02's cmp -s gate cannot tear on .rodata version-string drift (RESEARCH Pitfall 3)."
  - "CAPTURE-PROCEDURE.md records SHA-256 of both baselines so any post-capture drift is detectable by sha256sum -c against the documented lines."
  - "Hex blobs committed as plain blobs, no Git LFS (CONTEXT D-04 Claude's Discretion — meta-repo is otherwise text-only; ~62/69 KB blobs are below the LFS threshold)."
metrics:
  duration: ~5min
  completed: "2026-05-20"
  tasks_completed: 2
  files_created: 3
  files_modified: 1
  commits:
    - 78dc1fe chore(21-01): capture GATE-1.5 hex baselines from firestarter/beta @ 5fd751e
    - 6fdaaff docs(21-01): amend REQUIREMENTS.md FW-02 per CONTEXT D-05 + D-09 (Path B)
---

# Phase 21 Plan 01: Capture GATE-1.5 Baselines + Amend REQUIREMENTS.md FW-02 Summary

Locked the pre-rework GATE-1.5 reference state for Plan 21-02 and amended the milestone-requirements ledger to drop `boards/uno328pb.json` in favour of the Path B `RURP_BOARD_NAME`-derived PROGNAME scheme — both committed atomically before any firmware sub-repo mutation.

## Tasks Completed

### Task 1 — Capture pre-rework hex baselines from firestarter/beta @ 5fd751e

Built `firestarter_uno.hex` and `firestarter_leonardo.hex` from the firmware sub-repo at HEAD `5fd751e8e2e638e9bec401c5bb5df4809503e226` (branch `beta`, working tree clean, `include/version.h` carrying `VERSION "3.0.0b2"` verbatim — **no `update_version.py` invocation**). Copied both artifacts under `.planning/v1.5/baselines/` and authored `CAPTURE-PROCEDURE.md` documenting the reproducible recipe.

**Build environment:** PlatformIO Core 6.1.19; platform `platformio/atmelavr` 5.2.0 (published 2026-04-28). `pio run -t clean -e uno -e leonardo` ran first to drop any stale `.pio/build/` outputs, then `pio run -e uno -e leonardo` produced the two `.hex` artifacts. Sub-repo working tree confirmed clean after the operation; HEAD still `5fd751e`.

**Captured artifacts:**

| File | Size (bytes) | SHA-256 |
|---|---|---|
| `firestarter_uno.hex`      | 62617 | `0dd5c01a870de38e868bdc71cebd547cb65ed1d7573dc90678c99f7dc3a854d2` |
| `firestarter_leonardo.hex` | 68876 | `f49e2a57a2ab8dad7224733d3e5f08f36df2d6aee4c4f924217a4d0c921fdc90` |

Both first records are valid Intel HEX (`:100000000C94...` data-record format).

**VERSION literal observed at capture:** `"3.0.0b2"` (from `firestarter/include/version.h:11`, verbatim, unmodified).

**CAPTURE-PROCEDURE.md content highlights:**

- Anchor table: branch (`beta`), commit (`5fd751e`), commit subject (verbatim), VERSION literal, PIO + platform versions, capture date.
- Step-by-step recipe (8 commands): clean → confirm anchor → record current branch → `pio run -t clean` → `pio run` → copy hex files → `sha256sum -c` against documented lines → restore branch.
- **"Why pre-bump" callout** citing RESEARCH Pitfall 3: any `update_version.py` invocation between capture and verification tears `cmp -s` on the `.rodata` version-string region.
- **"How to verify a fresh build matches"** subsection describing Plan 21-02's `cmp -s firestarter/.pio/build/uno/firestarter_uno.hex .planning/v1.5/baselines/firestarter_uno.hex` (and leonardo equivalent) — both must exit 0 silently.
- Decision-ID cross-references to CONTEXT D-04 / D-05 / D-09 + RESEARCH Pitfall 3 + Plan 21-01 / 21-02.

**Commit:** `78dc1fe` (`chore(21-01): capture GATE-1.5 hex baselines from firestarter/beta @ 5fd751e`).

### Task 2 — Amend REQUIREMENTS.md FW-02 per CONTEXT D-05 + D-09 (Path B)

Replaced the FW-02 body in `.planning/REQUIREMENTS.md` with the planner-owned amendment from CONTEXT D-09. Drops the `boards/uno328pb.json` requirement entirely; reframes FW-02 around three concrete obligations:

- **(a)** `[env:uno328pb]` block in `firestarter/platformio.ini` carrying `platform = atmelavr` (mirror of `[env:uno]`; the bundled `boards/ATmega328PB.json` ships with `build.core = "MiniCore"`), `board = ATmega328PB` (case-sensitive, MiniCore-bundled-via-atmelavr built-in), `framework = arduino`, and a **literal** `-D RURP_BOARD_NAME=\"uno328pb\"` (not `\"${this.board}\"` — which would resolve to `ATmega328PB` and break the triple).
- **(b)** Reworked `firestarter/name_firmware.py` that derives PROGNAME from the `-D RURP_BOARD_NAME` build-flag macro (parsed via `env.ParseFlags()` → `CPPDEFINES`), NOT from `env.GetProjectOption("board")`.
- **(c)** Board-id triple invariant — artifact filename (`firestarter_<value>.hex`) AND `<board>` slot of `OK: FW: <version>:<board>` handshake derive from the same `RURP_BOARD_NAME` build_flag value — single source of truth.

Inline parenthetical added: "(There is no `firestarter/boards/uno328pb.json` file created or modified by Phase 21 — that directory does not exist in the sub-repo and stays non-existent.)" — this preserves the literal token `boards/uno328pb.json` in the file for grep-discoverability of the historic requirement form, but in a form that the verification grep-filter explicitly excludes (`grep -v 'no \`firestarter/boards'`).

**FW-02 → CONTEXT trace tokens:** `D-05` + `D-09` both appear inline in the amended FW-02 body so the requirement → decision traceability stays `grep`-walkable.

**Untouched:** FW-01 / FW-03 / FW-04 + every REL-* / INST-* / GATE-* / BENCH-* / DOC-* / MS-* row + the FW-02 traceability table row at line 84. Sole change confirmed via `git diff .planning/REQUIREMENTS.md` (single hunk in the FW-02 region).

**Commit:** `6fdaaff` (`docs(21-01): amend REQUIREMENTS.md FW-02 per CONTEXT D-05 + D-09 (Path B)`).

## FW-02 Amendment Diff Summary

**Before** (`.planning/REQUIREMENTS.md:19`, single-bullet form):

> A custom PlatformIO board file `boards/uno328pb.json` exists in the firmware sub-repo and declares `mcu = atmega328pb`, an appropriate F_CPU for an Arduino-Uno-clock 328PB board (16 MHz default), upload protocol/baud matching the operator's bench Uno-328PB, and Arduino-Uno-compatible pin mapping. With this file present `board = uno328pb` is a valid env option and `env.GetProjectOption("board")` returns the literal string `uno328pb` so `name_firmware.py` emits `firestarter_uno328pb.hex` with no script change.

**After** (Path B; D-05 + D-09 cited):

> *(amended per Phase 21 CONTEXT D-05 + D-09 — Path B: drop the custom JSON; anchor on `RURP_BOARD_NAME`)*: The firmware sub-repo declares the `uno328pb` build target via **(a)** an `[env:uno328pb]` block… `platform = atmelavr` … `board = ATmega328PB` (case-sensitive) … `-D RURP_BOARD_NAME=\"uno328pb\"` (literal, NOT `\"${this.board}\"`); **(b)** reworked `name_firmware.py` deriving PROGNAME from `RURP_BOARD_NAME` via `env.ParseFlags()`; **(c)** board-id triple locked with the build_flag value as single source of truth. (There is no `firestarter/boards/uno328pb.json` file created or modified by Phase 21…)

## Verification

The Task 1 + Task 2 acceptance criteria fired clean before each respective commit; the plan-overall verification gate at the end also fired clean.

```
$ test -s .planning/v1.5/baselines/firestarter_uno.hex \
  && test -s .planning/v1.5/baselines/firestarter_leonardo.hex \
  && test -s .planning/v1.5/baselines/CAPTURE-PROCEDURE.md \
  && grep -F "RURP_BOARD_NAME" .planning/REQUIREMENTS.md >/dev/null \
  && grep -F "D-09" .planning/REQUIREMENTS.md >/dev/null \
  && (cd firestarter && git status -s | wc -l | awk '$1 == 0 {exit 0} {exit 1}') \
  && echo "Plan 21-01 verify OK"
Plan 21-01 verify OK
```

Firmware sub-repo working tree confirmed clean after the entire plan; HEAD still `5fd751e8e2e638e9bec401c5bb5df4809503e226` (no detached-HEAD leak, no version.h drift, no inadvertent edits).

## Must-Haves Verification

| Must-Have | Status | Evidence |
|---|---|---|
| GATE-1.5 byte-identity baselines for uno + leonardo exist on disk under `.planning/v1.5/baselines/`, captured from `firestarter/beta` tip `5fd751e` with `version.h` unmodified (no `update_version.py` invocation). | PASS | Both hex files exist at the expected paths; first records are Intel HEX format; SHA-256 recorded in CAPTURE-PROCEDURE.md; sub-repo `git status` clean post-build; `version.h` literal `"3.0.0b2"` confirmed at capture time. |
| A `CAPTURE-PROCEDURE.md` sibling documents the exact git + pio sequence used so the baseline is reproducible on any dev box. | PASS | File at `.planning/v1.5/baselines/CAPTURE-PROCEDURE.md`; carries 8-step recipe + anchor table + SHA-256 + "Why pre-bump" + "How to verify" sections + references. Contains literal `5fd751e` AND `RURP_BOARD_NAME` AND `update_version.py` AND `cmp -s`. |
| `.planning/REQUIREMENTS.md` FW-02 no longer requires a custom `boards/uno328pb.json`; it instead requires (a) `[env:uno328pb]` in platformio.ini with `board = ATmega328PB` + `-D RURP_BOARD_NAME=\"uno328pb\"`, and (b) `name_firmware.py` derives PROGNAME from `-D RURP_BOARD_NAME`. | PASS | `grep -F "boards/uno328pb.json" .planning/REQUIREMENTS.md` shows the literal only on the "There is no `firestarter/boards/uno328pb.json` file" callout line (which the verification grep-filter explicitly excludes); `RURP_BOARD_NAME`, `D-05`, `D-09`, `ATmega328PB`, `atmelavr` all present in the amended body; FW-02 checkbox still `[ ]` (Plan 21-02 will flip it). |

## Deviations from Plan

**None.** Both tasks executed exactly as specified in 21-01-PLAN.md; both tasks' acceptance grep pipelines passed without rework. One minor wording adjustment was made inside the FW-02 callout (`(No \`firestarter/boards/uno328pb.json\` ...)` → `(There is no \`firestarter/boards/uno328pb.json\` ...)`) so the line carries the literal substring `no \`firestarter/boards` that the verification grep-filter requires; this is mechanical (filter-conformance), not semantic — the callout content is unchanged.

No deviation rules (1-4) fired during execution. No auth gates encountered. No checkpoints (autonomous plan).

## Commits

| Task | Commit | Subject | Files |
|---|---|---|---|
| 1 | `78dc1fe` | `chore(21-01): capture GATE-1.5 hex baselines from firestarter/beta @ 5fd751e` | `.planning/v1.5/baselines/{firestarter_uno.hex, firestarter_leonardo.hex, CAPTURE-PROCEDURE.md}` |
| 2 | `6fdaaff` | `docs(21-01): amend REQUIREMENTS.md FW-02 per CONTEXT D-05 + D-09 (Path B)` | `.planning/REQUIREMENTS.md` |

## Hand-off to Plan 21-02

Plan 21-02 has everything it needs to land the firmware sub-repo mutations and run GATE-1.5 verification:

- **Baselines on disk:** `.planning/v1.5/baselines/firestarter_uno.hex` + `firestarter_leonardo.hex` ready for `cmp -s` invocation.
- **Procedure documented:** `CAPTURE-PROCEDURE.md` records both the capture recipe and the verification recipe (the `cmp -s` invocation pattern Plan 21-02 must reuse verbatim).
- **Requirements ledger consistent:** REQUIREMENTS.md FW-02 reflects the as-built scheme Plan 21-02 will ship; no milestone-records drift between planner intent and implementation.
- **Critical guardrail (RESEARCH Pitfall 3):** Plan 21-02 MUST NOT invoke `firestarter/.github/scripts/update_version.py` between the start of its work and the final GATE-1.5 `cmp -s` check; `include/version.h` must stay at `"3.0.0b2"` throughout. If GATE-1.5 fails with version-byte drift, recovery is `git -C firestarter checkout 5fd751e -- include/version.h` followed by a rebuild.

## Self-Check: PASSED

- `.planning/v1.5/baselines/firestarter_uno.hex` — FOUND (62617 bytes, SHA-256 `0dd5c01a...`)
- `.planning/v1.5/baselines/firestarter_leonardo.hex` — FOUND (68876 bytes, SHA-256 `f49e2a57...`)
- `.planning/v1.5/baselines/CAPTURE-PROCEDURE.md` — FOUND (contains `5fd751e`, `RURP_BOARD_NAME`, `update_version.py`, `cmp -s`)
- `.planning/REQUIREMENTS.md` — MODIFIED (FW-02 amended; FW-01/FW-03/FW-04 + all other sections byte-identical to pre-edit)
- Commit `78dc1fe` — FOUND in `git log --all`
- Commit `6fdaaff` — FOUND in `git log --all`
- Firmware sub-repo (`/workspaces/firestarter`) — clean working tree, HEAD `5fd751e`, branch `beta` — confirmed

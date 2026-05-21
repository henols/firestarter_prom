# Phase 26: Cross-board Reproduction & Diagnostic Tooling - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-21
**Phase:** 26-cross-board-reproduction-diagnostic-tooling
**Areas discussed:** CLI placement & naming, Read mode (passive vs write-then-read), Default N, Output / verdict format, Exit code semantics, Chunk-size scope, Cross-board execution model, Evidence file, Bench-wave plan structure, Tests, Progress reporting, Hashing approach, Branch flow

**Mode:** Auto Mode (harness-level) — recommended option auto-selected for every area; no AskUserQuestion prompts. Operator may redirect after reading CONTEXT.md.

---

## CLI placement & naming

| Option | Description | Selected |
|--------|-------------|----------|
| `firestarter dev consistency-check <chip>` under existing `dev` subparser | Matches ROADMAP scaffolding (REPRO-03 verb verbatim); permanent home alongside `dev read`/`reg`/`addr` | ✓ |
| Top-level `firestarter consistency-check <chip>` | More discoverable but pollutes the user-facing surface with a diagnostic | |
| `firestarter dev read-stable <chip>` | Snappier but loses operator-mental-model fit (ROADMAP fixed the verb) | |

**Auto-selected:** `dev consistency-check` (recommended).
**Notes:** ROADMAP SC#1 says "The command persists in the CLI permanently (becomes the canonical post-fix regression check)" — `dev` is the right surface area for permanent diagnostic verbs. See D-01.

---

## Read mode (passive vs write-then-read)

| Option | Description | Selected |
|--------|-------------|----------|
| Passive — read N times, no chip modification | Chip-safe; works on UV-EPROM, EEPROM, blank, half-programmed, missing chip; 3-shield Shield-3 evidence shows bug manifests even with no chip | ✓ |
| Write-then-read baseline | Establishes known-good image but burns UV-EPROM bits irreversibly; unsafe to run at will | |

**Auto-selected:** Passive (recommended).
**Notes:** 3-shield A/B/C triage (`large-read-data-jitter-uno328pb.md` §"3-shield A/B/C triage") observed jitter with no chip in socket. Verdict logic is simply "are all N SHA-256s equal?" — chip-content-independent. See D-02.

---

## Default N (number of consecutive reads)

| Option | Description | Selected |
|--------|-------------|----------|
| `--runs 3` default | Matches REPRO-03 / ROADMAP SC#1 minimum; cheap triage | ✓ |
| `--runs 5` default | Matches Phase 29 VERIFY-01 gate; safer default but slower | |
| `--runs 2` default | Minimum to detect divergence; lower confidence | |

**Auto-selected:** `--runs 3` (recommended).
**Notes:** Operator overrides with `--runs 5` for VERIFY gates. See D-01.

---

## Output / verdict format

| Option | Description | Selected |
|--------|-------------|----------|
| Stdout verdict + per-run binary directory + divergence detail (first-N offsets) | Human-readable + machine-grep-friendly + post-hoc diff-able; ROADMAP SC#1 specifies "pass/fail verdict + first-divergence offset on mismatch" | ✓ |
| Stdout-only (no per-run binaries kept) | Smaller footprint but loses post-hoc diff ability | |
| JSON-structured output | CI-consumable but unnecessary in Phase 26 | |

**Auto-selected:** Stdout verdict + `--keep-files` default + first-`--max-diffs` offsets (recommended).
**Notes:** Per-run binaries under `consistency-check-<chip>-<board>-<timestamp>/run_N.bin`. See D-04.

---

## Exit code semantics

| Option | Description | Selected |
|--------|-------------|----------|
| 0/1/2 — pass / divergence / hardware-error | CI/script-usable; distinguishes "ran and found bug" from "couldn't run" | ✓ |
| 0/1 only — bool success | Simpler but conflates run-failure with divergence | |
| 0 always (verdict in stdout) | Not script-usable | |

**Auto-selected:** 0/1/2 (recommended).
**Notes:** Mirrors `grep` convention. See D-05.

---

## Chunk-size scope

| Option | Description | Selected |
|--------|-------------|----------|
| Full-chip only | REPRO-03 / SC#1 specifies "full-chip read"; 1KB case covered by existing `dev read -s 1024` | ✓ |
| Add `--chunk-size N` flag | Pre-builds for hypothetical fix shape | |
| Add `--size N` like `dev read` | Overlaps existing `dev read` semantics | |

**Auto-selected:** Full-chip only (recommended).
**Notes:** Phase 29 / VERIFY-03 uses existing `dev read -s 1024` for the low-rate case — same wire path. See D-06.

---

## Cross-board execution model

| Option | Description | Selected |
|--------|-------------|----------|
| Per-port, operator-driven (one invocation per board) | Matches Phase 24 BENCH muscle memory; simple | ✓ |
| `--all-boards` orchestrator enumerating ports | Adds complexity for marginal benefit | |

**Auto-selected:** Per-port (recommended). See D-07.

---

## Evidence file

| Option | Description | Selected |
|--------|-------------|----------|
| `.planning/v1.6-EVIDENCE.md` (mirror of v1.3-BENCH-RESULTS.md / v1.5-BENCH-RESULTS.md shape) | ROADMAP "Cross-cutting evidence accretion" structural note names this | ✓ |
| `.planning/v1.6/EVIDENCE/<phase>.md` (per-phase split) | More granular but breaks cross-phase narrative | |
| Inline in CONTEXT.md / SUMMARY.md | Loses cross-phase accretion | |

**Auto-selected:** `.planning/v1.6-EVIDENCE.md` shared file (recommended).
**Notes:** Phase 26 creates it with pre-fix baseline; Phase 27 / 28 / 29 append. See D-08.

---

## Bench-wave plan structure

| Option | Description | Selected |
|--------|-------------|----------|
| 2 plans: 26-01 desk-side CLI + tests, 26-02 cross-board bench (`autonomous: false`) | Closes 3 requirements via 2 plans; bench is naturally one operator session | ✓ |
| 3 plans: split bench across 3 boards | Granular but bench is one session — split adds overhead | |
| 1 plan: combine desk-side + bench | Bench is operator-on-bench; mixing autonomous and non-autonomous is brittle | |

**Auto-selected:** 2-plan split (recommended). See D-09.

---

## Tests

| Option | Description | Selected |
|--------|-------------|----------|
| Host-side pytest only (`tests/test_consistency_check.py`) with stubbed serial; FIX-02 bilateral test deferred to Phase 28 | Sufficient for Phase 26 scope; reuses existing `tests/conftest.py` fixtures | ✓ |
| Bilateral host + firmware (Unity) test in Phase 26 | FIX-02 territory — premature without RCA evidence | |

**Auto-selected:** Host-side pytest only (recommended). See D-10.

---

## Progress reporting

| Option | Description | Selected |
|--------|-------------|----------|
| Per-run `tqdm` bar; `-q/--quiet` suppresses | Consistent with existing `read_eprom` reporting | ✓ |
| No progress reporting | Cleaner but less feedback during 60s+ reads | |

**Auto-selected:** tqdm + `--quiet` flag (recommended). See D-11.

---

## Hashing approach

| Option | Description | Selected |
|--------|-------------|----------|
| `hashlib.sha256` over per-run binary, computed post-read | One-line; matches operator's mental model (original triage used `sha256sum`) | ✓ |
| Incremental SHA-256 during read | Microsecond optimization on a serial-bound 60-second operation | |
| Switch to xxhash / SHA-1 | Faster but breaks operator's convention from the original triage | |

**Auto-selected:** post-read `hashlib.sha256` (recommended). See D-12.

---

## Branch flow

| Option | Description | Selected |
|--------|-------------|----------|
| Host-side only — `v1.6-read-bug` in `firestarter_app/` only; firmware sub-repo branch deferred to Phase 28 | Phase 26 makes no firmware change | ✓ |
| Cut all 3 branches now | Premature — no firmware change in this phase | |

**Auto-selected:** Host-side only (recommended). See D-13.

---

## Claude's Discretion

- Exact `--output-dir` default name format (date-style, separator choice).
- Progress-bar style — direct `tqdm` vs existing `ClassProgressHandler` wrapper.
- Whether `-q` shortform survives or gets dropped if it collides with a future top-level flag.
- Whether bench wave 26-02 rotates one chip across 3 boards or uses 3 separate chips.
- Whether to add a `--json` output flag (deferred to v1.7+ unless Phase 29 needs it).

## Deferred Ideas

- `--all-boards` orchestrator (v1.7+ multi-board CI).
- `--chunk-size N` flag (add only if Phase 27 RCA reveals fix differs per chunk size).
- `--json` output mode (add only if a CI workflow demands it).
- Promoting `consistency-check` to a top-level command (per ROADMAP narrative it lives under `dev` permanently).
- Cross-shield rotation matrix as part of Phase 26 (already covered by the 2026-05-21 3-shield triage).
- Phase 27 hypotheses ranking via Phase 26 evidence (Phase 27 owns ranking; Phase 26 just records raw evidence).
- Firmware-side change (deferred to Phase 28 per D-13).
- avrdude-mcu-detection-fallback + w27c512-eeprom-misclassification (out of v1.6 scope per REQUIREMENTS.md §"Future Requirements").

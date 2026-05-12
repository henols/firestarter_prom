# Phase 2 Discussion Log

**Date:** 2026-05-12
**Mode:** auto-decided (orchestrator instructed "no clarifying questions")

This phase was discussed in auto mode — the orchestrator scouted the codebase, identified gray areas, and made reasonable calls on each rather than pausing for user input. This log records the gray areas considered, the options weighed, the choice made, and the reasoning. The user can override any decision by editing `02-CONTEXT.md` or re-running `/gsd:discuss-phase 2`.

## Codebase Scout — What Was Found

- The DB JSON already has both `"vpp"` (string, e.g. `"12V"`) and `"vpp_mv"` (int, e.g. `12000`) per entry — written by `build_db.py:255-256`. On-disk schema is dual-keyed; only the wire emission and firmware parsing need to flip.
- `convert_to_programmer` (`database.py:518`) currently emits the wire key as `"vpp": vpp_mv` — the integer value under the legacy name (the v1.0 semantic overload).
- Firmware: `json_parser.c:62` defines `key_vpp[] PROGMEM = "vpp"` and dispatches to `get_vpp_mv` at L74; inside `get_vpp_mv` at L309, `extract_int("vpp", ...)` invokes `extract_num` which compares the literal `"vpp"` against the JSON key via `jsoneq` — **the first arg is the parse key, not a debug label**. Both locations must change together.
- `firestarter_app/CLAUDE.md:46-59` already shows BOTH `"vpp"` AND `"vpp_mv"` in the example JSON — transition artefact, collapses to `vpp_mv` only.
- DB filename `minipro_complete_db.json` is referenced in 8 sites across 6 files (build_db.py:12, database.py:189+:366, check_dispatch.py:2+:27, firestarter_app/CLAUDE.md:19+:36+:69, firestarter/CLAUDE.md:30, meta CLAUDE.md:44).
- Minipro mentions: 2 in firmware CLAUDE.md (drop to 0), 6 in firestarter_app/CLAUDE.md (drop to 1), 3 in app code (.py comments — neutralise wording).
- Phase 1 CONTEXT.md confirmed: "Replacing the v1.0 vpp JSON wire key with vpp_mv is Phase 2 / WIRE-01" — phase boundary locked at milestone start.
- No matching todos for Phase 2 (`todo.match-phase 2` returned empty).

## Gray Areas Considered

### G1 — DB filename

**Options considered:**
1. `chip_database.json` (REQUIREMENTS.md suggestion verbatim).
2. `chip_db.json`.
3. `firestarter_db.json`.
4. `chips.json`.

**Chosen: `chip_database.json`** (D-02). Explicit, self-describing, rhymes with the user-override file `~/.firestarter/database.json`, matches REQUIREMENTS.md suggestion exactly.

### G2 — Wire-key transition: hard vs soft cutover

**Options considered:**
1. Hard cutover both sides: Python emits only `vpp_mv`, firmware parses only `vpp_mv`.
2. Symmetric transitional: Python emits both keys, firmware accepts either.
3. Asymmetric: Python emits only `vpp_mv` (strict), firmware accepts both (legacy fallback).

**Chosen: option 3** (D-01). Rationale: single source of truth (the Python emitter) is strict — no ambiguity at the source. Firmware fallback shields uncontrolled senders: hand-crafted JSON in `firestarter_test.sh` / `write_test.sh` (Phase 4 territory) and any third-party tool. Removing the legacy key from the parser would silently break those senders — too risky for a naming-cleanup phase. The legacy parser entry can be removed in a future cleanup phase once Phase 4 confirms the test scripts are clean.

### G3 — User-override DB schema migration

**Options considered:**
1. New code path to detect+migrate legacy user-override DBs.
2. Use the existing `convert_to_programmer:510` fallback (`vpp_mv or vpp*1000`) — no new code.
3. Document user-side manual migration.

**Chosen: option 2** (D-07). The fallback already handles user-override DBs with the legacy key. Zero new code. The user-override file at `~/.firestarter/database.json` keeps its filename (renaming would break user installs silently).

### G4 — Atomicity / commit shape

**Options considered:**
1. One commit for all of Phase 2 (atomic, one revert).
2. Per-requirement commits (WIRE-01, WIRE-02, CLEAN-01, CLEAN-02) — 4 atomic feature commits.
3. Per-sub-repo commits (firestarter + firestarter_app + meta) — 3 commits.

**Chosen: option 2 with sub-repo split inside** (D-05). 4 requirements → 4 conceptual commits, decomposed naturally across sub-repos (e.g., WIRE-01 → one Python emit commit + one firmware parser commit). Each requirement is independently revertable. Plan-phase finalises the exact decomposition.

### G5 — WIRE-02 test approach

**Options considered:**
1. Augment existing `check_dispatch.py` with end-of-loop wire-key assertion.
2. New dedicated `check_wire_key.py`.
3. Firmware Unity test only.
4. Manual `firestarter info <chip>` smoke.

**Chosen: option 1** (D-06). Single-file change in an existing 743-chip iteration. Two assert lines. Existing exit-code 0/1 contract preserved.

### G6 — Minipro comment scrub wording

**Options considered:**
1. `# Algorithm (upstream protocol_id) → ...`
2. `# Algorithm integer → ...`
3. `# Algorithm integer (upstream protocol_id from infoic.xml) → ...`

**Chosen: option 3 for header comments, option 2 for terse inline comments** (D-04). The expansion preserves attribution where the data flow demands it (table headers); inline comments stay terse. The single load-bearing minipro attribution lives in `tools/build_db.py` (where `MINIPRO_XML_URL` is defined).

### G7 — Firmware parser PROGMEM rename detail

This isn't really a gray area — it's a single technical decision that the planner needed nailed down BEFORE planning, because it's the kind of thing that breaks silently. Captured as D-08:
- Both `key_vpp[] PROGMEM` at L62 AND the macro arg `extract_int("vpp", ...)` at L309 ARE parse keys (the latter is NOT a debug label, contrary to first glance).
- The asymmetric-emit, dual-parse pattern (D-01) requires adding a SECOND PROGMEM key + dispatch row + a manually-inlined `jsoneq || jsoneq` check inside `get_vpp_mv` (the existing `extract_int` macro early-returns and can't be chained twice).

### G8 — Drop the legacy `"vpp"` string-with-unit key from the on-disk DB schema?

Considered: `tools/build_db.py:255` emits `"vpp": "12V"` AND `"vpp_mv": 12000` per entry. The string form was needed when `convert_to_programmer` did the volts→millivolts conversion at emit time; now that emit is `vpp_mv`-only, the string is dead in the package-bundled DB.

**Decision: defer to plan-phase discretion.** Listed in deferred ideas. Small extra change with clear long-term value (less schema clutter), but increases blast radius for the milestone. If plan-phase picks "drop now", the user-override fallback at `convert_to_programmer:510` (`vpp_mv or vpp*1000`) still works for user DBs that haven't been regenerated.

## Deferred Ideas Captured

See `02-CONTEXT.md` <deferred> — 6 items, including the legacy `"vpp"` parser fallback removal (post-Phase-4 cleanup), the on-disk DB schema legacy-string-key removal (plan-phase discretion or v1.2), the `firestarter vpp` CLI subcommand rename (UX phase, may never happen), the `pinouts.json` filename retention (no overload), and the `~/.firestarter/database.json` user-override file retention.

## What Was NOT Asked of the User

Per "no clarifying questions" instruction, no AskUserQuestion calls were made. All gray areas were resolved by the orchestrator based on REQUIREMENTS.md spec, codebase scout, and prior CONTEXT.md (Phase 1) decisions. User can redirect any choice by:

1. Editing `02-CONTEXT.md` directly before `/gsd:plan-phase 2`, OR
2. Re-running `/gsd:discuss-phase 2` with feedback, OR
3. Letting plan-phase decompose and then editing the resulting `02-NN-PLAN.md` files.

---

*Phase: 02-naming-cleanup-wire-key-minipro-references*
*Discussion log: 2026-05-12*

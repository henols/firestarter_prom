# Phase 2: Naming Cleanup (Wire Key + Minipro References) - Context

**Gathered:** 2026-05-12
**Status:** Ready for planning
**Mode:** auto-decided (orchestrator instructed "no clarifying questions" — user can redirect by editing this file or re-running `/gsd:discuss-phase 2`)

<domain>
## Phase Boundary

Mechanical naming cleanup across both sub-repos that removes two long-standing semantic
overloads from the v1.0 wire / data layer:

1. **WIRE-01** — Wire JSON VPP key flips from `"vpp"` (overloaded — historically volts,
   currently millivolts after the silent v1.0 semantic shift) to `"vpp_mv"` end-to-end:
   Python emitter (`firestarter_app/firestarter/database.py::convert_to_programmer`),
   firmware parser (`firestarter/src/json_parser.c` PROGMEM key table + `get_vpp_mv`
   function body), and the wire-JSON example in `firestarter_app/CLAUDE.md`. Closes
   `.planning/MILESTONES.md` WARNING-3.
2. **WIRE-02** — `firestarter_app/tools/check_dispatch.py` regenerates the DB and
   confirms every chip in the regenerated `chip_database.json` still parses end-to-end
   on Uno + Leonardo simulator with no algorithm regressing on the wire after the
   rename. Wire-key assertion folded into the existing dispatch loop (one new check,
   not a new test file).
3. **CLEAN-01** — Generated DB filename flips from `minipro_complete_db.json` (toolchain
   name) to `chip_database.json` (project-neutral). All readers + the writer + docs
   atomically reference the new filename: `tools/build_db.py:12 OUTPUT_FILE`,
   `firestarter/database.py:189 default path + :366 docstring`, `tools/check_dispatch.py:2
   docstring + :27 data-dir glob`, `firestarter_app/CLAUDE.md:19,36,69`, `firestarter/CLAUDE.md:30`,
   meta `CLAUDE.md:44`.
4. **CLEAN-02** — "minipro" comment scrub: firestarter sub-repo drops to **zero** mentions
   (`firestarter/CLAUDE.md:30,69`); firestarter_app keeps **one** load-bearing attribution
   line in `tools/build_db.py` (which owns the `MINIPRO_XML_URL` upstream constant) plus
   **one** attribution line in `firestarter_app/CLAUDE.md`. All other mentions
   (`firestarter_app/firestarter/database.py:45,389`, `firestarter_app/tools/check_dispatch.py:30`,
   the 4 extra `CLAUDE.md` mentions) become neutral wording.

**In scope:**
- Python emitter wire-key rename: `firestarter_app/firestarter/database.py::convert_to_programmer` L518.
- Firmware parser key change: `firestarter/src/json_parser.c:62` PROGMEM literal + L309 inline
  `extract_int(...)` argument (BOTH locations must change together — see <code_context> below).
- DB output filename: `firestarter_app/tools/build_db.py:12 OUTPUT_FILE` and the four reader sites.
- check_dispatch.py augmentation: add an end-of-loop assertion that every emitted wire JSON
  carries `"vpp_mv"` and zero `"vpp"` keys, across all 743 chips. Asserts both Uno + Leonardo
  paths via the existing simulator-buffer fork (no new simulator entry point needed).
- Doc updates: `firestarter_app/CLAUDE.md`, `firestarter/CLAUDE.md`, meta `CLAUDE.md`, including
  the wire-JSON example (drop the dual `"vpp"` / `"vpp_mv"` block to just `"vpp_mv"`).
- Comment scrub on the 4 documented minipro mentions in app code (database.py:45,389;
  check_dispatch.py:30) — replace with neutral wording per D-04 below.

**Out of scope:**
- `build_db.py` robustness — bare-except blocks and missing `raise_for_status()` / `timeout`
  on `requests.get(MINIPRO_XML_URL)` (covered by code-review WR-02/WR-03 from Phase 11; tracked
  as DB-06 in REQUIREMENTS.md "Future Requirements"; deferred past v1.1).
- `verified` field restoration on the regenerated DB (DB-07; deferred past v1.1).
- Test-script fixes for `firestarter_test.sh:31` / `write_test.sh:17` `database_generated.json`
  references — **explicitly owned by Phase 4 / HW-01** (REQUIREMENTS.md:31). They're closely
  related (same WARNING-4 family) but Phase 4 already owns the fix as part of restoring the
  hardware integration test scripts.
- `~/.firestarter/database.json` user-override schema migration — handled organically by the
  retained fallback in `convert_to_programmer:510` (`vpp_mv or vpp*1000`), no new code path.
- Retroactive VERIFICATION.md artifacts for v1.0 phases 01-10 (Phase 3 / VERIF-01..10).
- Hardware validation on the renamed DB (Phase 4 / HW-02..05).
- `firestarter/CLAUDE.md` wire-protocol-section docstring at L51-58 currently lists `vpp` AND
  `vpp_mv` as fields — collapse to `vpp_mv` only (no new section).

</domain>

<decisions>
## Implementation Decisions

### D-01 — Wire-key transition: hard cutover on the emitter, soft retention on the parser

**Python emitter (`convert_to_programmer:518`):** emit **only** `"vpp_mv": vpp_mv`. Drop the legacy `"vpp"` key entirely.

**Firmware parser (`json_parser.c`):** accept **both** `"vpp_mv"` (new primary) and `"vpp"` (legacy fallback). Concretely: keep the existing `key_vpp_mv → get_vpp_mv` row, add a second row `key_vpp_legacy → get_vpp_mv` that re-uses the same handler. Both parse-key string literals inside `get_vpp_mv` (L309) must check both keys via two consecutive `extract_int(...)` calls — the macro returns 0 on key mismatch and 1 on match (see <code_context> below), so two back-to-back invocations naturally form an "or" without changing the dispatch loop.

**Rationale:** asymmetric. The emitter is the single source of truth in this repo — making it strict eliminates ambiguity at the source. The firmware fallback exists for two real-world senders that this phase does NOT control: (a) `firestarter_test.sh` and `write_test.sh` hand-crafted JSON used by Phase 4 / HW-01; (b) any third-party tool that learned to emit `"vpp"` from the v1.0 wire docs. Removing the legacy key entry from the parser would silently break those senders — too risky for a naming-cleanup phase. The legacy key can be removed in a future cleanup phase once Phase 4 hardware scripts are confirmed clean.

### D-02 — DB filename: `chip_database.json`

Verbatim from REQUIREMENTS.md CLEAN-01 suggestion. Rejected alternatives:
- `chip_db.json` — abbreviation, less self-describing.
- `firestarter_db.json` — redundant in a `firestarter/data/` directory.
- `chips.json` — too generic (could collide with future per-family files).
- Keeping `minipro_complete_db.json` — that's what we're fixing.

`chip_database.json` also rhymes with the user-override file `~/.firestarter/database.json` — both are "databases", reinforcing the conceptual symmetry between base + override.

### D-03 — Wire-protocol example in firestarter_app/CLAUDE.md drops the dual-key form

Current `firestarter_app/CLAUDE.md:48-59` example wire JSON shows BOTH `"vpp": 12000` AND `"vpp_mv": 12000`. That's a transition artefact and must collapse to `"vpp_mv": 12000` only after WIRE-01. Same for `firestarter/CLAUDE.md:51-58` field-list block — drop `vpp /` and keep only `vpp_mv`.

### D-04 — Neutral wording for minipro comment scrub

| Current comment site | Current text | New text |
|---|---|---|
| `firestarter_app/firestarter/database.py:45` | `# Algorithm (minipro protocol_id) → firmware mem_type integer.` | `# Algorithm integer (upstream protocol_id from infoic.xml) → firmware mem_type integer.` |
| `firestarter_app/firestarter/database.py:389` | `# Read algorithm integer directly — set by build_db.py as minipro protocol_id` | `# Read algorithm integer directly — set by build_db.py from upstream protocol_id` |
| `firestarter_app/tools/check_dispatch.py:30` | `# Algorithm (minipro protocol_id) → firmware mem_type integer.` | `# Algorithm integer (upstream protocol_id from infoic.xml) → firmware mem_type integer.` |

The single load-bearing attribution stays in `firestarter_app/tools/build_db.py` where `MINIPRO_XML_URL` is defined (the actual constant naming the upstream tool). The single attribution line in `firestarter_app/CLAUDE.md` stays at L19 (`infoic.xml → build_db.py → chip_database.json`) but rephrased: `upstream chip XML → build_db.py → chip_database.json`. **No** minipro reference survives in firmware `firestarter/CLAUDE.md` — the firmware never sees the upstream tool.

### D-05 — Commit shape: 4 atomic feat commits per sub-repo + 1 chore commit per submodule bump in meta

Plan-phase will decompose further, but the intent is:
- `firestarter_app@feat(02-01)` — WIRE-01 Python emitter half (database.py L518 + the wire JSON example in CLAUDE.md)
- `firestarter@feat(02-01)` — WIRE-01 firmware parser half (json_parser.c L62 + L309 + the field list in CLAUDE.md)
- `firestarter_app@chore(02-02)` — WIRE-02 check_dispatch.py wire-key assertion (no behavior change for existing chips — just an extra check)
- `firestarter_app@refactor(02-03)` — CLEAN-01 rename `minipro_complete_db.json` → `chip_database.json` across build_db.py + database.py + check_dispatch.py + CLAUDE.md (`git mv` for the JSON file itself); meta CLAUDE.md updated separately
- `firestarter_app@refactor(02-04)` — CLEAN-02 minipro comment scrub (database.py L45 + L389, check_dispatch.py L30, CLAUDE.md text changes)
- `firestarter@refactor(02-04)` — CLEAN-02 firmware-side minipro scrub (CLAUDE.md L30, L69)
- Meta-repo: one commit per sub-repo submodule bump, plus `docs(02): update meta CLAUDE.md DB filename reference`.

Plan-phase has discretion on whether WIRE-01 spans one plan (both halves together) or two (Python plan + firmware plan). Recommended: one plan, two sub-repo commits — they are conceptually atomic.

### D-06 — Verification approach for WIRE-02 (regression check)

Augment `firestarter_app/tools/check_dispatch.py` with a wire-key assertion that runs over all 743 chips at the end of the existing dispatch-resolution loop:

```python
# Pseudo-code — final shape is plan-phase territory
for chip in chips:
    wire = db.convert_to_programmer(chip)
    assert "vpp_mv" in wire, f"{chip['part_number']}: emitter regressed — missing vpp_mv"
    assert "vpp" not in wire, f"{chip['part_number']}: emitter regressed — legacy vpp still emitted"
```

Single-file change in an already-existing regression-scan script. Uno + Leonardo simulator buffer-size fork already exists in check_dispatch.py; the new assertion runs once per chip regardless of buffer path, so both targets are covered.

Rejected alternatives:
- New `check_wire_key.py` — duplicates iteration logic for one assertion.
- Firmware-side Unity test — overkill; the wire key is a host-side emission concern.
- Manual `firestarter info <chip>` smoke — Phase 4 / HW-01 already covers this empirically.

### D-07 — User-override (`~/.firestarter/database.json`) compatibility

**No new code.** The existing fallback at `convert_to_programmer:510` (`full_eprom_data.get("vpp_mv") or int(full_eprom_data.get("vpp", 0) * 1000)`) already handles user-override DBs that pre-date `vpp_mv` — it reads `vpp_mv` if present, otherwise multiplies legacy `vpp` (volts) by 1000. Leave this fallback in place; it is the migration path for any local user DB. **Do not** rename the user-override file from `database.json` to `chip_database.json` — the user-override file lives under `~/.firestarter/`, not in the package, and renaming would break user installations silently. Only the package-bundled file is in scope.

### D-08 — Firmware parser PROGMEM rename detail

The current code at `firestarter/src/json_parser.c:62` declares `const char key_vpp[] PROGMEM = "vpp";` and the dispatch table at L74 references it as `{key_vpp, get_vpp_mv}`. Inside `get_vpp_mv` (L308-310), the macro `extract_int("vpp", handle->vpp_mv)` is **not** a debug label — it expands to `extract_num("vpp", ...)` which compares the JSON key against `"vpp"` via `jsoneq` (see `extract_num` macro at L268-273 + <code_context> below). So renaming the wire key on the firmware side requires editing **two** locations together:

1. `key_vpp` PROGMEM string at L62 → become `key_vpp_mv` with literal `"vpp_mv"` (primary).
2. Inside `get_vpp_mv` at L309 → first call: `extract_int("vpp_mv", handle->vpp_mv);` (primary). Second back-to-back call: `extract_int("vpp", handle->vpp_mv);` (legacy fallback per D-01). The macro returns 0 if the key doesn't match the current JSON token, so the function will try both in order; first match wins, function returns 1; no match returns 0 and dispatch moves on (matches existing semantics).

Plus a third row in the `key_parsers[]` table at L74 — `{key_vpp_legacy, get_vpp_mv}` with `key_vpp_legacy[] PROGMEM = "vpp";` — so the dispatch table also recognises legacy `"vpp"` keys. The double-extract inside `get_vpp_mv` and the extra dispatch row are belt-and-braces — without the dispatch entry the function would never be invoked for legacy JSON; without the inline-extract second key the function would extract from the wrong token offset. Both are required.

### Claude's Discretion

- Exact PROGMEM constant name (`key_vpp_mv` vs `key_vpp_new` vs `key_vpp_primary`) — pick `key_vpp_mv` for clarity but accept any name that's grep-able.
- Exact phrasing of the `firestarter_app/CLAUDE.md:19` data-flow line beyond removing "minipro" — preserve the arrow-diagram shape.
- Whether the firmware CLAUDE.md wire-protocol field list also documents the legacy `vpp` fallback or just `vpp_mv` (recommend: only `vpp_mv` in user-facing docs; the legacy parser path is implementation detail).
- Whether to add a deprecation logger.warning in `convert_to_programmer` when a user-override entry was read via the legacy `vpp` fallback (recommend: yes — one-line `logger.debug(...)` only, not a noisy warning, since override DBs are user data we don't control).
- Test names for the augmented check_dispatch.py — preserve the existing exit-code 0/1 contract.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements + roadmap
- `.planning/REQUIREMENTS.md` §"Naming Cleanup" — WIRE-01 / WIRE-02 / CLEAN-01 / CLEAN-02 wording (lines 39-42) — names every edit target with line numbers; this is the authoritative spec.
- `.planning/ROADMAP.md` §"Phase 2: Naming Cleanup (Wire Key + Minipro References)" — 5 success criteria, dependency chain (ordered before Phase 4 so hardware tests use final wire key and DB filename).
- `.planning/MILESTONES.md` §"Known Gaps" — WARNING-3 wire-key semantic overload original audit text.
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md` — WARNING-3 full context (volts/millivolts overload introduced in v1.0).

### Codebase entry points — Python host (firestarter_app)
- `firestarter_app/firestarter/database.py:518` — `convert_to_programmer` wire-emit site (`"vpp": vpp_mv` overload); WIRE-01 primary edit.
- `firestarter_app/firestarter/database.py:510` — fallback chain (`vpp_mv or vpp*1000`); per D-07 KEEP this for user-override DBs.
- `firestarter_app/firestarter/database.py:189` — default DB filename (`"minipro_complete_db.json"`); CLEAN-01 edit.
- `firestarter_app/firestarter/database.py:366` — docstring referencing old name; CLEAN-01 edit.
- `firestarter_app/firestarter/database.py:45` — minipro comment in `_ALGO_MEM_TYPE` header; CLEAN-02 edit per D-04.
- `firestarter_app/firestarter/database.py:389` — minipro comment on algorithm read; CLEAN-02 edit per D-04.
- `firestarter_app/tools/build_db.py:12` — `OUTPUT_FILE` constant; CLEAN-01 edit.
- `firestarter_app/tools/build_db.py:9` — `MINIPRO_XML_URL` constant; CLEAN-02 ATTRIBUTION KEEPS minipro mention (this is the load-bearing one).
- `firestarter_app/tools/build_db.py:255-256` — current per-entry emit of both `"vpp"` (string) + `"vpp_mv"` (int); WIRE-01 path: keep `vpp_mv`, drop `vpp` (NOT just the wire emission — also drop from the on-disk DB schema for consistency; plan-phase confirms).
- `firestarter_app/tools/check_dispatch.py:2` — docstring header referencing old DB name; CLEAN-01 edit.
- `firestarter_app/tools/check_dispatch.py:27` — `DB_FILE` default; CLEAN-01 edit.
- `firestarter_app/tools/check_dispatch.py:30` — minipro comment; CLEAN-02 edit per D-04.

### Codebase entry points — firmware (firestarter sub-repo)
- `firestarter/src/json_parser.c:62` — `key_vpp[] PROGMEM = "vpp"`; WIRE-01 edit per D-08 (rename to `key_vpp_mv` with literal `"vpp_mv"`).
- `firestarter/src/json_parser.c:74` — dispatch table `{key_vpp, get_vpp_mv}`; WIRE-01 add second row `{key_vpp_legacy, get_vpp_mv}` per D-01 + D-08.
- `firestarter/src/json_parser.c:308-310` — `get_vpp_mv` function body with `extract_int("vpp", ...)`; WIRE-01 edit per D-08 (two extract_int calls back-to-back).
- `firestarter/src/json_parser.c:268-278` — `extract_num` / `extract_long` / `extract_int` macros (confirm the first arg is the parse key, NOT a debug label — see <code_context>).
- `firestarter/CLAUDE.md:30` — minipro mention in mem_type-fallback paragraph; CLEAN-02 → ZERO mentions.
- `firestarter/CLAUDE.md:69` — minipro mention in JSON wire protocol paragraph; CLEAN-02 → ZERO mentions.
- `firestarter/CLAUDE.md:51-58` — wire-protocol field list with `vpp / vpp_mv`; WIRE-01 → collapse to `vpp_mv`.

### Codebase entry points — docs
- `firestarter_app/CLAUDE.md:19` — data flow diagram (`infoic.xml → build_db.py → minipro_complete_db.json`); CLEAN-01 + CLEAN-02 edit (output filename + neutral "upstream chip XML").
- `firestarter_app/CLAUDE.md:36` — key files list (`minipro_complete_db.json`); CLEAN-01 edit.
- `firestarter_app/CLAUDE.md:42` — build_db.py description ("parses minipro `infoic.xml`"); CLEAN-02 edit (keep one attribution).
- `firestarter_app/CLAUDE.md:46-59` — wire JSON example with dual `"vpp"` + `"vpp_mv"`; WIRE-01 → drop `"vpp"` line.
- `firestarter_app/CLAUDE.md:69` — database pipeline section (`tools/build_db.py parses tools/infoic.xml`); CLEAN-02 + CLEAN-01.
- `firestarter_app/CLAUDE.md:72` — algorithm description with minipro mention; CLEAN-02 edit.
- `CLAUDE.md:44` (meta) — single mention of `minipro_complete_db.json`; CLEAN-01 edit.

### Data file rename target
- `firestarter_app/firestarter/data/minipro_complete_db.json` → rename via `git mv` to `firestarter_app/firestarter/data/chip_database.json`. 743 entries; history preserved.

### Prior context
- `.planning/phases/01-safety-closure-intel-flash-vpp-28c-chip-id/01-CONTEXT.md` §Out of scope — confirms "Replacing the v1.0 vpp JSON wire key with vpp_mv is Phase 2 / WIRE-01" — phase boundary already locked at v1.1 milestone start.
- `.planning/milestones/v1.0-phases/01-database-pipeline-fix/` — phase that established the `convert_to_programmer` emission shape.
- `.planning/milestones/v1.0-phases/02-firmware-json-protocol-extension/` — phase that established `json_parser.c` and the PROGMEM key table.
- `.planning/milestones/v1.0-phases/11-build-db-cleanup/` — phase that consolidated `parse_db_2.py → build_db.py` but deliberately did NOT rename the output JSON (deferred to Phase 2 / CLEAN-01).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`convert_to_programmer` fallback chain (database.py:510):** `vpp_mv or vpp*1000` — already handles user-override DBs that pre-date `vpp_mv`. Keeps Phase 2 from breaking local user installations even though it tightens the wire-emit side. KEEP unchanged.
- **`check_dispatch.py` 743-chip iteration:** already a regression-scan loop. Adding two `assert` lines covers WIRE-02 without a new file. Existing exit-code 0/1 contract preserved.
- **`key_parsers[]` table (json_parser.c:74):** simple `{PROGMEM_key, fn_ptr}` array. Adding a second row for the legacy `"vpp"` key is mechanical and preserves the dispatch-loop shape; no refactor needed.
- **`git mv` for the DB file rename:** mirrors Phase 11's `git mv parse_db_2.py build_db.py` — history-preserving rename pattern is established in this repo.

### Established Patterns
- **Build-time DB emission has BOTH legacy `"vpp"` (string with "V") AND `"vpp_mv"` (int millivolts) at `tools/build_db.py:255-256`** — the on-disk DB schema is dual-keyed. Phase 2 drops the legacy `"vpp"` from BOTH the DB schema (build_db.py) AND the wire emission (database.py:518). Plan-phase verifies that no code path reads the on-disk `"vpp"` key besides the `convert_to_programmer:510` user-override fallback (which then becomes effectively dead for the package-bundled DB, but is retained per D-07 for user-override DBs that haven't been regenerated).
- **Parse keys live in TWO places per field in `json_parser.c`** — once as a `PROGMEM` literal at the top of the file (used by the dispatch table), and once inline inside the `get_*` function body as the macro argument (used by `jsoneq` inside `extract_num`). When renaming, BOTH must change. See D-08.
- **`extract_int` / `extract_long` macros (json_parser.c:268-278) DO NOT use the first arg as a debug label** — they expand to `jsoneq(json, &tokens[pos], element) == 0`, i.e. the first arg IS the parse key. This was confirmed during scout to forestall a likely error class for the planner.
- **Comment scrub leaves project-anchored attribution intact:** the single `MINIPRO_XML_URL` constant in `tools/build_db.py` is where the upstream tool name belongs (the URL contains "minipro"); CLAUDE.md text mentions become neutral.

### Integration Points
- **No wire-protocol change observable to firmware behavior.** The firmware `handle->vpp_mv` field name is already correct (since Phase 1 SAF-04). Phase 2 only renames the JSON key feeding into it.
- **No DB schema observable to runtime.** `chip_database.json` and `minipro_complete_db.json` have identical content; only the filename differs. Phase 12 dispatch tests and Phase 1 Unity tests are unaffected.
- **Cross-sub-repo coordination:** both sub-repos change in Phase 2. The order matters for hand-testing: Python emit change WITHOUT firmware parser change would cause `handle->vpp_mv` to be zero (firmware drops unknown keys silently) → write voltage check would always trip. The firmware fallback (D-01) makes the order independent — firmware accepts both keys, so either sub-repo can ship first. Plan-phase enforces ship-firmware-first to be safe.

</code_context>

<specifics>
## Specific Ideas

### Wire JSON example before/after (firestarter_app/CLAUDE.md:46-59)

**Before:**
```json
{
  "cmd": 2,
  "type": 1,
  "algorithm": 7,
  "memory-size": 65536,
  "vpp": 12000,
  "vpp_mv": 12000,
  "pulse-delay": 0,
  ...
}
```

**After:**
```json
{
  "cmd": 2,
  "type": 1,
  "algorithm": 7,
  "memory-size": 65536,
  "vpp_mv": 12000,
  "pulse-delay": 0,
  ...
}
```

### json_parser.c after-state (sketch — plan-phase finalises)

```c
const char key_vpp_mv[]    PROGMEM = "vpp_mv";   // primary (was: key_vpp = "vpp")
const char key_vpp_legacy[] PROGMEM = "vpp";      // legacy fallback (new row per D-01)
// ...
static const key_parser_t key_parsers[] PROGMEM = {
    // ...
    {key_vpp_mv,    get_vpp_mv},
    {key_vpp_legacy, get_vpp_mv},   // dispatch both keys to same handler
    // ...
};

bool get_vpp_mv(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_int("vpp_mv", handle->vpp_mv);  // primary — returns 1 on match
    extract_int("vpp",    handle->vpp_mv);  // legacy fallback — returns 1 on match
    // (the macro's "return 0" at end of each invocation falls through; both are inline-flat)
}
```

NOTE: the `extract_num` macro at L268 has implicit early returns (`return 1` on match, `return 0` on no-match). Two back-to-back `extract_int` calls cannot work as-is because the first invocation always returns. Plan-phase needs to either (a) inline both `jsoneq` checks manually in `get_vpp_mv` body, or (b) define a new macro `extract_int_alt(elem1, elem2, reg)` that checks both keys before returning. Recommend (a) for clarity:

```c
bool get_vpp_mv(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    if (jsoneq(json, &tokens[pos], "vpp_mv") == 0 || jsoneq(json, &tokens[pos], "vpp") == 0) {
        handle->vpp_mv = simple_strtoul(json + tokens[pos + 1].start);
        return 1;
    }
    return 0;
}
```

### check_dispatch.py augmentation sketch

After the existing per-chip dispatch resolution loop in check_dispatch.py:

```python
# WIRE-02 wire-key regression check
wire = db.convert_to_programmer(chip)
if "vpp_mv" not in wire:
    print(f"WIRE-REGRESSION: {chip.get('part_number')} — missing vpp_mv")
    failures += 1
if "vpp" in wire:
    print(f"WIRE-REGRESSION: {chip.get('part_number')} — legacy vpp key still emitted")
    failures += 1
```

The existing `failures` counter and exit-code logic at the bottom of the file already routes >0 to exit 1.

### Comment scrub table (verbatim diff targets)

| File:Line | Replace this exact string | With this exact string |
|---|---|---|
| `firestarter_app/firestarter/database.py:45` | `# Algorithm (minipro protocol_id) → firmware mem_type integer.` | `# Algorithm integer (upstream protocol_id from infoic.xml) → firmware mem_type integer.` |
| `firestarter_app/firestarter/database.py:389` | `# Read algorithm integer directly — set by build_db.py as minipro protocol_id` | `# Read algorithm integer directly — set by build_db.py from upstream protocol_id` |
| `firestarter_app/tools/check_dispatch.py:30` | `# Algorithm (minipro protocol_id) → firmware mem_type integer.` | `# Algorithm integer (upstream protocol_id from infoic.xml) → firmware mem_type integer.` |

(Plan-phase verifies line numbers haven't drifted at execution time.)

</specifics>

<deferred>
## Deferred Ideas

- **Remove the legacy `"vpp"` parser fallback from firmware** — D-01 keeps it for one milestone as belt-and-braces against hand-crafted JSON in `firestarter_test.sh` / `write_test.sh` and any third-party tool. Once Phase 4 / HW-01 ships the corrected test scripts and the firmware has shipped one full cycle on the new key, the legacy entry can be deleted. Track as v1.2 cleanup or fold into the next firmware-touching phase.
- **Drop the `vpp` (volts string) key from the on-disk DB schema** — `tools/build_db.py:255` currently emits both `"vpp": "12V"` (legacy string-with-unit) AND `"vpp_mv": 12000` (canonical int millivolts). The string form was useful when `convert_to_programmer` did the volts→millivolts conversion at emit time; now that emit is `vpp_mv`-only, the string is dead. Plan-phase decides whether to drop it in Phase 2 (small extra change, helps long-term schema clarity) or defer to v1.2 (lower blast radius for this milestone).
- **`firestarter_app/firestarter/main.py:185,626` `vpp` subcommand** — this is the CLI subcommand name (`firestarter vpp`), NOT the wire key. Naming-overload-y in a different sense. Defer to a future UX-cleanup phase if at all; renaming would break user muscle memory.
- **Replace minipro upstream — out of scope for v1.1.** REQUIREMENTS.md "Out of Scope" explicitly says `infoic.xml` is authoritative; one override is sufficient.
- **`firestarter_app/firestarter/data/pinouts.json` — does it stay named that, or get aligned with `chip_database.json`?** No naming overload there (pinouts ≠ minipro), keep as-is.
- **`~/.firestarter/database.json` → `~/.firestarter/chip_database.json`?** D-07 explicitly says NO — would break user installations silently. Stays as `database.json`.

</deferred>

---

*Phase: 02-naming-cleanup-wire-key-minipro-references*
*Context gathered: 2026-05-12*
*Auto-decided: see header. User can redirect by editing CONTEXT.md or re-running `/gsd:discuss-phase 2`.*

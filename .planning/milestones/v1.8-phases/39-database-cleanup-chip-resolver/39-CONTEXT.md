# Phase 39: Database Cleanup + chip_resolver - Context

**Gathered:** 2026-05-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Clean up the host-side database/chip-resolution layer of `firestarter_app` —
**pure refactor, no wire-protocol or CLI-surface change** (GATE-1.8). Four
deliverables, mapped to DATA-01..04:

- **DATA-01:** New flat `firestarter/chip_resolver.py` with
  `resolve_chip(name) -> programmer-config dict` raising `ChipNotFoundError`,
  eliminating the **9× `get_eprom` → `convert_to_programmer` copy-paste** in
  `main.py` dispatch. New `tests/test_chip_resolver.py`.
- **DATA-02:** Clarify the *apparent* "two sources of truth" for DIP→RURP pin
  mapping with a **docstring** — `pin_conversions` and `pinouts.json` encode
  **different layers**, not duplicates. No code/behavior change.
- **DATA-03:** Replace `from firestarter.constants import *` star-imports with
  **explicit named imports** across all **6** star-importing modules (prereq
  for tightening the mypy gate).
- **DATA-04:** Add `# Firmware sync: firestarter.h` markers to the wire-protocol
  constant blocks in `constants.py`; verify `COMMAND_FW_VERSION` present
  (it is — `0x0D`, already parity-tested). **Mark + verify only.**

Requirements: DATA-01, DATA-02, DATA-03, DATA-04 (full text in
`.planning/REQUIREMENTS.md`). Standing contract: GATE-1.8 (a–e), esp. **(b)**
CLI surface preserved (the 9 sites' `"EPROM '{name}' not found"` log + exit-1
are pinned by Phase 36 snapshots), **(c)** constant contract preserved (parity
test), **(d)** read path ring-fenced (`dev consistency-check` is read-path-
adjacent), **(e)** suite green + entry point runs.

**Depends on:** Phase 38 — `exceptions.py` exists and contains
`ChipNotFoundError` (verified at `firestarter/exceptions.py:55`).
**Unblocks:** Phase 41 (CLI handlers call `resolve_chip()`); Phase 42 (named
imports let mypy be tightened on these modules).

</domain>

<decisions>
## Implementation Decisions

The operator selected all four gray areas to weigh in on, then **accepted all
four recommendations** (2026-05-27). Decisions below are **locked**. Operator's
standing style (Phases 37–38): lean, behavior-preserving, minimize churn,
preserve git blame, document SC deviations with rationale rather than escalate.

### DATA-01 — `resolve_chip()` shape & scope
- **D-01:** `chip_resolver.resolve_chip(name: str) -> dict` returns the
  **converted programmer config** (today's `db.convert_to_programmer(db.get_eprom(name))`
  result) and **raises `ChipNotFoundError`** on a miss (chip absent OR conversion
  yields falsy). Imports `ChipNotFoundError` from `firestarter.exceptions` (Phase
  38 D-01). `chip_resolver.py` is a flat sibling module; stdlib + package imports
  only.
- **D-02:** It replaces **exactly the 9 copy-paste op sites** in `main.py`:
  `read` (`:660`), `write` (`:680`), `verify` (`:699`), `blank` (`:718`),
  `erase` (`:733`), `id` (`:751`), and the 3 `dev` sites — `dev` default
  (`:871`), `dev addr` (`:902`), `dev consistency-check` (`:917`).
  **`info`/`list`/`search` are NOT touched** — they have richer presentation
  needs (`info` also wants the full eprom dict + `get_eprom_config()`'s
  `(config, manufacturer)`; `list`/`search` use `get_eproms`/`search_eprom`).
  Folding those into the resolver would bloat its contract to serve one
  presentation caller — rejected.
- **D-03:** **Observable behavior is byte-identical (GATE-1.8b).** Each of the 9
  sites currently logs `f"EPROM '{args.eprom}' not found in database."` and
  returns exit code **1** on a miss. The planner must preserve that exact log
  line + exit code: catch `ChipNotFoundError` at the dispatch (a small shared
  helper or per-site `try/except` — planner's call) since the CLI is **still
  argparse** in Phase 39 (centralized Click error-mapping is Phase 41). The
  Phase 36 snapshots for the bad-chip path MUST still pass unchanged.
- **D-04 (subtlety — preserve):** `dev consistency-check` (`:917-919`) currently
  calls `convert_to_programmer(...)` and **discards the result** (presence check
  only). `consistency_check` is the v1.6 read-path diagnostic and is read-path-
  adjacent (GATE-1.8d). Using `resolve_chip()` there is behavior-equivalent
  (resolve-or-raise replaces the explicit get-then-check) — keep it that way;
  do not change what the chip data is used for downstream.

### DATA-02 — pin-mapping single source of truth
- **D-05:** **Documentation-only — zero behavior change.** Confirmed during
  scout: `pin_conversions` (`database.py:69`) maps **socket pin number → RURP
  bus line number** (RURP *board wiring*); `pinouts.json` (loaded into
  `self.pin_maps` at `database.py:191`) maps **chip pin function → socket pin
  number** (chip *DIP pinout*). They **compose** in `convert_to_programmer`
  (`pinouts.json` gives function→socket-pin, `pin_conversions` gives
  socket-pin→bus-line) — they are NOT duplicate sources. Per ROADMAP SC#2: add a
  docstring on `pin_conversions` explicitly stating it encodes RURP board-wiring
  distinct from `pinouts.json`'s chip pinout. **Do NOT merge** (the REQUIREMENTS
  DATA-02 "consolidate to one source" wording is superseded by SC#2's finding).

### DATA-03 — star-import → named imports
- **D-06:** Replace `from firestarter.constants import *` with **explicit named
  imports** (`from firestarter.constants import COMMAND_READ, FLAG_FORCE, ...`)
  in **all 6** star-importing modules: `main.py:23`, `serial_comm.py:24`,
  `eprom_operations.py:27`, `database.py:33`, **`firmware.py:28`**, and
  **`hardware.py:14`**. ROADMAP SC#3 names only 4, but its acceptance check is a
  **repo-wide** grep (`grep -r "from firestarter.constants import \*" firestarter/`
  returns no results) → all 6 must be converted. **Documented deviation from
  SC#3's 4-module list** (same pattern as Phase 38's D-01) — flagged so it reads
  as intentional, not a missed requirement.
- **D-07:** **Rejected namespace import** (`from firestarter import constants` +
  `constants.X` prefixing) — it would rewrite every usage site = large diff,
  wrecks git blame. Explicit named imports keep usage sites untouched.
- **D-08:** **Strip the now-obsolete `# noqa: F403`/`# noqa: F405` markers** in
  the same pass (~55 across the 6 modules: `serial_comm.py` 13, `hardware.py` 5,
  `firmware.py` 6, `main.py` 3, `database.py` 2, `eprom_operations.py` 26). Once
  imports are explicit, F403/F405 no longer fire; leaving the noqas would be dead
  lint suppression. Touched modules must stay ruff/ruff-format clean and must not
  raise the mypy watermark (the gate is live on `v1.8-app-cleanup`).

### DATA-04 — wire-protocol constants consolidation
- **D-09:** **Mark + verify only — no relocation.** Add a
  `# Firmware sync: firestarter.h` marker comment to the `COMMAND_*` and
  `FLAG_*` blocks in `constants.py` (`:25-67`). The `CTRL_*` (`:69-81`) and
  `REVISION_*` (`:83-96`) blocks **already** carry v1.7 sync-comment headers
  (pointing at `rurp_pinout.h` / `rurp_shield.h` respectively) — normalize/leave
  them so each wire-protocol block clearly names its firmware-header source.
- **D-10:** `COMMAND_FW_VERSION` is **already present** (`constants.py:37`,
  `= 13` / `0x0D`) and **already parity-tested** (`tests/test_revision_constants_parity.py:116`
  asserts `COMMAND_FW_VERSION == 0x0D`). So SC#4's "added if absent" is a no-op —
  just verify it stays green. **Do NOT relocate the codegenerated `messages.py`**
  message-ID catalog into `constants.py` — it is generated from
  `tools/catalog/messages.toml` and moving it breaks the CI codegen drift gate.
  Other "scattered" literals stay where they are unless trivially wire-protocol
  constants that belong with their block.
- **D-11:** Parity test passes after the marker edits (comments-only → cannot
  change values; GATE-1.8c holds). **SC naming note:** the parity test file is
  `tests/test_revision_constants_parity.py`, NOT `test_firmware_contract_parity.py`
  as SC#4 (and the 36/38 CONTEXT refs) call it — Phase 36 extended it in place.

### Claude's Discretion
- Exact named-import lists per module (enumerate what each module actually
  uses); module/function docstrings; function order in `chip_resolver.py`.
- `chip_resolver` internals: whether `resolve_chip` takes the `EpromDatabase`
  instance as a parameter or constructs one — follow Phase 36's de-singleton
  seam (`skip_local_override` injectable construction) and the testability
  intent of TEST-03; the planner picks the exact signature so
  `tests/test_chip_resolver.py` can run without serial I/O.
- The catch-`ChipNotFoundError` mechanism (shared helper vs per-site try/except)
  as long as D-03's observable behavior is byte-identical.
- `tests/test_chip_resolver.py` coverage shape (hit, miss→`ChipNotFoundError`,
  conversion correctness against real `chip_database.json`).
- Plan/wave decomposition. **Natural ordering** (dependency-safe, each its own
  atomic commit with full suite green before the next): (1) `chip_resolver.py` +
  `test_chip_resolver.py` + repoint the 9 sites (DATA-01) → (2) star-import →
  named imports + noqa sweep (DATA-03) → (3) `pin_conversions` docstring
  (DATA-02) → (4) constants sync markers + parity verify (DATA-04). DATA-02 and
  DATA-04 are tiny and could fold into one wave.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope & locked milestone decisions
- `.planning/ROADMAP.md` — Phase 39 detail (Goal + SC#1–SC#4, lines 138–150) +
  the v1.8 section + GATE-1.8 (a–e) standing gate. **Note the documented
  deviations** above: D-06 (6 star-import modules vs SC#3's 4), D-05 (DATA-02 is
  doc-only, superseding the REQUIREMENTS "consolidate" wording), D-11 (parity
  test filename differs from SC#4).
- `.planning/REQUIREMENTS.md` — DATA-01…DATA-04 (lines 48–51); GATE-1.8 (a–e)
  (lines 12–20); Out-of-Scope table (firmware untouched, no protocol change).
- `.planning/PROJECT.md` — "Current Milestone: v1.8" + "Scope decisions (locked
  2026-05-27)" (lines 32–41): host-only, flat layout (preserve git blame),
  refactor-and-fix-bugs gate.

### Prior-phase context this phase builds on
- `.planning/phases/38-low-risk-extractions/38-CONTEXT.md` — D-01 created the
  empty `ChipNotFoundError` in `exceptions.py` **specifically for this phase to
  wire**; the leaf-module discipline + flat-layout pattern; the "documented SC
  deviation with rationale" precedent (D-06, D-01/D-02 there).
- `.planning/phases/37-tooling-baseline-ci-gate/37-CONTEXT.md` — ruff/ruff-format/
  mypy gate + mypy watermark; **star-import removal was explicitly parked for
  Phase 39 (DATA-03)** with `# noqa: F403/F405` left in place — this phase
  removes them.
- `.planning/phases/36-characterization-test-baseline/36-CONTEXT.md` — the
  characterization safety net (162 passed + 2 xfail + 29 snapshots) that pins the
  9 sites' bad-chip log + exit-1; the `EpromDatabase` de-singleton
  `skip_local_override` seam used to construct the DB without serial I/O;
  `COMMAND_FW_VERSION` confirmed present + folded into the parity test.

### Files this phase edits / creates (firestarter_app sub-repo, branch v1.8-app-cleanup)
- `firestarter_app/firestarter/main.py` — 9 op-site copy-paste blocks (`:660`,
  `:680`, `:699`, `:718`, `:733`, `:751`, `:871`, `:902`, `:917`) → `resolve_chip()`;
  star-import (`:23`) → named; 3 noqas. `info`/`list`/`search` lookups (`:617`,
  `:624`/`:632`/`:633`, `:654`) **untouched**.
- `firestarter_app/firestarter/database.py` — `pin_conversions` (`:69`) docstring
  (DATA-02); star-import (`:33`) → named; 2 noqas. **No behavior change** to
  `get_eprom`/`get_eprom_config`/`convert_to_programmer`/`get_eproms`.
- `firestarter_app/firestarter/constants.py` — `# Firmware sync: firestarter.h`
  markers on `COMMAND_*` (`:25-55`) + `FLAG_*` (`:57-67`); `CTRL_*`/`REVISION_*`
  already marked; `COMMAND_FW_VERSION` (`:37`) verify-only.
- `firestarter_app/firestarter/serial_comm.py` — star-import (`:24`) → named; 13 noqas.
- `firestarter_app/firestarter/eprom_operations.py` — star-import (`:27`) → named; 26 noqas.
- `firestarter_app/firestarter/firmware.py` — star-import (`:28`) → named; 6 noqas.
- `firestarter_app/firestarter/hardware.py` — star-import (`:14`) → named; 5 noqas.
- `firestarter_app/firestarter/exceptions.py` — `ChipNotFoundError` (`:55`) import source (read-only).
- **NEW:** `firestarter_app/firestarter/chip_resolver.py`.
- **NEW test:** `firestarter_app/tests/test_chip_resolver.py` (SC#1's "from Phase 36" is wrong — does not exist yet).
- `firestarter_app/tests/test_revision_constants_parity.py` — MUST stay green (DATA-04); the real parity-test file.

### App architecture (context)
- `firestarter_app/CLAUDE.md` — data flow (`get_eprom` → `_map_data` →
  `convert_to_programmer` → `eprom_operations`) and the `constants.py` ↔
  `firestarter/include/firestarter.h` sync contract (CTRL_* ↔ `rurp_pinout.h`,
  REVISION_* ↔ `rurp_shield.h`).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`ChipNotFoundError`** (`exceptions.py:55`) — created empty in Phase 38
  exactly so `chip_resolver` can raise it. No new exception needed.
- **Phase 36 safety net** (162 passed + 2 xfail + 29 syrupy snapshots) — the
  per-change acceptance signal; the bad-chip snapshots pin the exact
  not-found log + exit-1 the 9 sites must preserve.
- **`EpromDatabase` de-singleton seam** (`skip_local_override` constructor,
  Phase 36 / TEST-03) — lets `test_chip_resolver.py` build a DB against real
  `chip_database.json` without serial I/O.
- **`COMMAND_NAMES`** (`constants.py:41`) — canonical cmd→name map (unrelated
  to this phase but the kind of explicit-name target named imports produce).

### Established Patterns
- The 9 op sites are **literally identical** 4–6 line blocks: `full = get_eprom(name)`
  → `data = convert_to_programmer(full) if full else None` → `if not data: log + return 1`.
  Clean single-function extraction.
- **`info`/`list`/`search` are a different shape** — they consume the full eprom
  dict and/or `(config, manufacturer)` for presentation, not the programmer
  config — which is exactly why D-02 scopes the resolver to the 9 op sites only.
- Flat layout (PROJECT.md): `chip_resolver.py` is a sibling under `firestarter/`;
  no subpackage.
- The v1.7 `CTRL_*`/`REVISION_*` blocks already model the "firmware-header sync
  marker" pattern DATA-04 extends to `COMMAND_*`/`FLAG_*`.

### Integration Points
- `chip_resolver.resolve_chip` becomes the single chokepoint between the CLI
  dispatch and the DB lookup/conversion for the 9 operations — the seam Phase 41
  Click handlers will call.
- `pin_conversions` + `pinouts.json` meet only inside
  `database.convert_to_programmer` (`:262-302`) — DATA-02's docstring documents
  that composition; the code path is left exactly as-is (GATE-1.8d-adjacent).

</code_context>

<specifics>
## Specific Ideas

- Operator chose to weigh in on all four gray areas (vs. Phase 38's blanket
  delegation) and then accepted every recommendation — confirming the lean,
  behavior-preserving, document-the-deviation approach is the intended bar for
  this phase, with the operator wanting visibility into the calls rather than
  blind delegation.
- The three SC inaccuracies (test_chip_resolver.py "from Phase 36" doesn't
  exist; parity test real name is `test_revision_constants_parity.py`;
  DATA-02/DATA-03 wording vs ROADMAP SC) are exactly the kind of "documented
  deviation with rationale" the operator wants surfaced for the plan-checker,
  not silently worked around.

</specifics>

<deferred>
## Deferred Ideas

- **Unifying `FirestarterError` base class** for the exception hierarchy —
  carried from Phase 38; still belongs to **Phase 42** (Error Handling
  Normalization), where the exit-code/exception convention is the explicit
  subject. Not introduced here (would change `isinstance`/`except` semantics).
- **Centralized Click error→exit-code mapping** for `ChipNotFoundError` (and
  friends) — Phase 39 keeps the argparse-era per-dispatch catch; the clean
  boundary mapping is **Phase 41/42** territory.
- **Folding `info`/`list`/`search` lookups into a richer resolver** — considered
  and rejected for Phase 39 (D-02). If a future phase wants a unified DB-facade,
  revisit then; out of scope for this lean cleanup.

### Reviewed Todos (not folded)
Same three pending todos Phases 37/38 reviewed — all hardware/protocol/DB-content,
out of this host-structure cleanup's domain (wire protocol frozen by GATE-1.8a):
- `avrdude-mcu-detection-fallback.md` — blank-chip / wrong-firmware recovery (hardware; v1.9-ish).
- `serial-cobs-resync-data-path.md` — COBS framing on the serial data path (protocol; not host-cleanup).
- `w27c512-eeprom-misclassification.md` — chip-DB *content* classification fix (DB **data**, not the
  resolver **structure** this phase touches; belongs to a database-content milestone). Matched this
  phase on "chip/database" keywords but is orthogonal to the structural cleanup.

</deferred>

---

*Phase: 39-Database Cleanup + chip_resolver*
*Context gathered: 2026-05-27*

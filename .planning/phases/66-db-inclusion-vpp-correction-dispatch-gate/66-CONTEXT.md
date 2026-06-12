# Phase 66: DB Inclusion + VPP Correction + Dispatch Gate - Context

**Gathered:** 2026-06-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Make `firestarter_app/tools/build_db.py` **capability-honest**: stop silently
dropping DIP parallel-memory chips it can't fully support, record **true VPP**
for the authoritatively-known NMOS high-voltage family, tag **every** chip with a
machine-readable `support_status`, and extend the dispatch/correctness gate so
non-`supported` entries are provably **non-dispatchable**. **HOST-ONLY** —
touches only the `firestarter_app` sub-repo (`tools/build_db.py`,
`tools/check_dispatch.py`, baselines, generated `chip_database.json`). Firmware
untouched.

Maps to **DB-01** (inclusion as `protocol-not-implemented`), **DB-03** (true-VPP
correction + status derivation), **DB-05** (gate treats non-supported as
non-dispatchable; gate stays green).

**Capability taxonomy** (locked by REQUIREMENTS): `supported` |
`protocol-not-implemented` | `adapter-required` | `vpp-exceeds-max`.

**In scope:**
- Re-classify the currently-dropped chips; include confirmed DIP-parallel memory.
- `support_status` + `unsupported_reason` on every chip (top-level keys).
- True-VPP correction for the curated NMOS exception list + status-from-ceiling.
- `check_dispatch.py` consistency arm for non-supported entries; regenerate the
  affected baseline(s) as an authorized, reviewed deviation; gate green at 743+.
- **Crossing into the adapter taxonomy this phase** (operator decision A1.2): the
  9 damage-hazard-skipped 24-pin EEPROMs are pulled in as `adapter-required`.

**Out of scope (locked — REQUIREMENTS / sequencing):**
- **No new chips become programmable** — non-`supported` entries are *listed and
  reported honestly*, never made to work. Do NOT route any flagged chip to a
  working handler this milestone.
- Pinout *classification* for unclassifiable chips → **Phase 67 (DB-02)**.
- Host `info`/`write`/`read`/`verify` capability *display & refusal* messages →
  **Phase 68 (DB-04)**. Phase 66 is the **data + gate layer only**; the
  hazard-prevention *guarantee* for non-supported chips lives in the Phase-68
  host-refusal layer, not the dispatch gate.
- Serial / GAL-PLD / MCU / SMD-only chips stay skipped entirely (existing warning).
- No firmware change; no new wire response (reuses existing infra).

</domain>

<decisions>
## Implementation Decisions

### Inclusion discriminator (DB-01)
- **D-01:** **Re-audit per family.** The researcher re-classifies each
  currently-dropped protocol family + form factor against minipro/package ground
  truth and includes **only confirmed DIP-parallel memory** as
  `support_status: protocol-not-implemented` (NOT routed to a handler). Serial
  (`0x04` Atmel DataFlash, `0x11` FWH-LPC), PLCC/SMD-only, and adapter-class
  (`0x0A`) parts **stay skipped** with the existing warning. Do **not** trust the
  coarse DIP filter blindly — it leaks `@SOIC28`/`@PLCC32`-aliased parts that
  passed `package_details` without the SMD/serial bit set.
  - **Concrete tension to resolve:** the v1.11 research table
    (`.planning/research/FEATURES.md`) marks **all** currently-dropped unknown
    protocols INFEASIBLE, but the live `build_db.py` run shows
    `X88C64@DIP24,X88C64S@SOIC24` (proto `0x34` "generic") reaching the drop gate
    — a **genuine Xicor 8K DIP24 parallel EEPROM** the table under-counted. The
    DIP24 variant is a real inclusion candidate; the `@SOIC24` alias is not.
    Per-family re-audit must catch cases like this where the table and the live
    decode disagree.
  - Current drop census (for the researcher): **24 chips** at the unknown-protocol
    gate — `0x04`×18 (DataFlash, skip), `0x11`×4 (FWH, skip), `0x0A`×1
    (`TMS87C257@PLCC32`, skip — PLCC only), `0x34`×1 (`X88C64@DIP24`, **include
    candidate**).

- **D-02:** **Pull the 9 damage-hazard-skipped 24-pin EEPROMs into Phase 66 as
  `support_status: adapter-required`** (operator decision — expands Phase 66 into
  the adapter taxonomy nominally owned by Phase 67/DB-02). These are dropped today
  at the `pin_count==24 AND proto_id in (0x07,0x08,0x0B) AND flags&0x10`
  damage-hazard gate (12V VPP would hit the WE pin; no safe 24-pin EEPROM handler).
  The `unsupported_reason` records the 12V-on-WE hazard + what mapping/adapter
  would be needed.
  - The 9: ATMEL `AT28C04`/`AT28C04E/F`/`AT28C16`/`AT28C16E/F`, MICROCHIP
    `28C04A`/`28C04AF`/`28C16A`/`28C16AF`, NEC `UPD28C04` (DIP24 variants;
    `@SOIC24` aliases excluded).

- **D-03 (HARD CONSTRAINT):** Per the milestone "no new chips become
  programmable", the 9 are **flagged `adapter-required`, NOT unblocked.** Do not
  route them to `configure_eeprom28c` / a working path even if they look
  sibling-identical to already-supported parts.

### VPP correction (DB-03)
- **D-04:** Encode the curated NMOS high-VPP exception list as an **inline
  module-level dict in `build_db.py`** (e.g. `{"M2716": 25000, "M2732": 25000,
  "M2732A": 21000}`), matched against each entry's alias list and applied as a
  post-decode override. Matches the existing inline-override idiom (WARNING-5,
  fm1608) and the project's deliberate removal of the external
  `database_overrides.json`. (Rejected: external data file; chip_id-keyed match.)
- **D-05:** **Key-and-correct, don't split.** When a known NMOS designator appears
  in an entry's aliases, record the true VPP **on that entry as-is** — do not split
  shared NMOS+CMOS aliased entries into separate DB rows. Lowest-risk, smallest
  diff, scoped to the authoritatively-known cases. (Rejected: split into separate
  entries; sole-identity-only correction.)
- **D-06 (locked by ROADMAP/REQUIREMENTS, not re-litigated):** Always record the
  **true** VPP (e.g. `25000`), then **derive** `support_status` from the RURP VPP
  ceiling (~22V): true VPP **>** ceiling → `vpp-exceeds-max` (M2716/M2732 = 25V);
  true VPP **≤** ceiling → `supported` at the corrected voltage (M2732A = 21V).
  The **exact ceiling constant** and **exact curated-list membership** are
  resolved at plan time (REQUIREMENTS explicitly defers these).

### support_status / unsupported_reason schema (DB-01/03/05)
- **D-07:** **Every chip carries an explicit `support_status`** (value
  `"supported"` for the normal majority). `unsupported_reason` is present **only**
  on non-supported entries. Uniform + always-queryable for the gate and Phase 68
  host display. Accepts a one-time uniform `+1-field` diff across all 743 entries
  (reviewable as a single mechanical change). (Rejected: sparse / absence-==-supported.)
- **D-08:** `support_status` + `unsupported_reason` are **top-level keys**, siblings
  of `electrical` / `programming` / `pinout`. (Rejected: nested `capability` object.)
- **D-09:** An included non-supported chip keeps **whatever `resolve_pinout_key`
  currently returns** (its best-effort/fallback). Harmless because non-supported
  chips are non-dispatchable; `unsupported_reason` carries the human story; Phase 67
  refines real pinout keys. (Rejected: `Unknown`/null placeholder.)

### Gate & baseline reconciliation (DB-05)
- **D-10:** **Exclude + consistency-assert.** Non-supported chips are **exempt**
  from the "must dispatch safely" checks (VPP-hazard, SRAM-in-EPROM, valid-handler) —
  they are never sent to firmware (host refuses at Phase 68), and several
  (`adapter-required` 0x07/0x0B, `vpp-exceeds-max` EPROM) would otherwise trip a
  hazard FAIL *for the very reason they're flagged*. Instead `check_dispatch.py`
  **adds assertions**:
  1. every non-supported chip has a non-empty `unsupported_reason`;
  2. a `protocol-not-implemented` chip genuinely has an unimplemented protocol;
  3. **no `supported` chip is non-dispatchable** (the inverse guard).
  The existing `not_implemented` FAIL bucket must be reworked: a chip resolving
  `not_implemented` is a FAIL **only if** `support_status == supported`; for
  `protocol-not-implemented` chips it is **expected → PASS**.
  (Rejected: run safety checks on all chips with expected/FAIL partitioning.)
- **D-11:** **Regenerate the affected baseline(s) as an authorized, reviewed
  deviation** (v1.11 D-01/D-02 precedent) — the new included entries, VPP
  corrections, and `support_status` field are all intentional; review the diff
  explicitly in the plan/commit. Note: the Phase-62 `dispatch_baseline.json` (D-04)
  deliberately **excluded `vpp_mv`**, so it churns only from the **new included
  chips**, not the VPP corrections. (Rejected: append-only / known-new allowlist.)

### Claude's Discretion
- Exact `support_status` enum string values + `unsupported_reason` message
  wording (must be the locked taxonomy strings; phrasing is the planner's).
- Placement/order of the new build_db.py inclusion logic relative to the existing
  drop gates and override blocks (must run after the WARNING-5/fm1608 overrides
  per the existing ordering invariant).
- The precise shape of the new `check_dispatch.py` consistency assertions and
  per-bucket FAIL message format (mirror the existing
  `f"{mfg}/{part} proto=0x{proto:02X} …"` idiom).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone planning
- `.planning/ROADMAP.md` § "Phase 66" — goal + success criteria.
- `.planning/REQUIREMENTS.md` — **DB-01, DB-03, DB-05** (+ the capability taxonomy
  block, the "Out of Scope" / "no new chips programmable" constraints, and the
  plan-time-deferred items: exact ceiling, curated list, alias splitting).
- `.planning/research/SUMMARY.md` — v1.12 reshaped-scope finding (no RURP-feasible
  unimplemented protocols; honest-reporting framing).
- `.planning/research/FEATURES.md` — per-`protocol_id` feasibility table. **Treat
  as a strong prior, NOT ground truth** — it under-counts `0x34` (see D-01); the
  researcher must reconcile it against the live `build_db.py` decode.

### The files this phase modifies
- `firestarter_app/tools/build_db.py` — the inclusion drop gates (unknown-protocol
  skip ~L339-342; 24-pin EEPROM damage-hazard skip ~L359-370), the VPP tables
  (`VPP_VOLTAGES`/`VPP_MV` ~L57-81 + the NMOS-exception comment ~L46-56),
  `KNOWN_PROTOCOLS` (~L83), `resolve_pinout_key`, and `chip_entry` construction
  (~L491-524 — where `support_status`/`unsupported_reason` get added).
- `firestarter_app/tools/check_dispatch.py` — `dispatch()` (~L66-90) +
  `main()` scan loop with per-bucket FAIL lists (~L93-205); the `not_implemented`
  bucket logic to rework + the new consistency assertions.
- `firestarter_app/tools/baseline/dispatch_baseline.json` — Phase-62 dispatch
  baseline (dispatch triples, `vpp_mv` excluded by design); regenerate for new
  included chips.
- `firestarter_app/firestarter/data/chip_database.json` — generated output (do NOT
  hand-edit; regenerate via `python tools/build_db.py`).

### Dispatch + decode source-of-truth
- `firestarter_app/firestarter/doc/protocol-id.md` — authoritative per-`protocol_id`
  classification (v1.11 field dictionary) — the inclusion re-audit's primary source.
- `firestarter_app/CLAUDE.md` § "Database Pipeline" — WARNING-5 / fm1608 override
  rationale + `KNOWN_PROTOCOLS` + the gate's existing guards.
- `firestarter/src/proms/memory.cpp` `configure_memory()` — dispatch source of
  truth `check_dispatch.py::dispatch()` mirrors line-for-line (DB-05 must not break
  the mirror).

### Precedent
- `.planning/phases/62-dispatch-baseline-capture-check-dispatch-update/62-CONTEXT.md`
  — D-04 deferred the `vpp_mv`/wire regression surface to **this** phase; D-03
  defined the two failure buckets the gate mirrors.
- `.planning/phases/59-correctness-gate-per-chip-diff-sram-audit/` — v1.11
  per-chip diff gate + pinned-baseline precedent + the authorized-deviation
  (D-01/D-02) pattern for regenerating baselines.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `build_db.py` already has two clean drop points (unknown-protocol skip; 24-pin
  EEPROM damage-hazard skip) and an established **inline post-decode override**
  idiom (WARNING-5 0x07→0x0D flip; fm1608 type-4 SRAM flip). The VPP exception
  dict + the inclusion logic follow the same idiom — surgical, no new module.
- The NMOS exception list **already exists as a comment** at `build_db.py` ~L46-56
  (M2716/M2732=25V, M2732A=21V) — D-04 promotes it from comment to applied dict.
- `check_dispatch.py::main()` already accumulates per-bucket FAIL lists with a
  uniform print + `sys.exit(1)` idiom and already has a `not_implemented` list +
  arm (added Phase 62) — the rework is reshaping its pass/fail condition by
  `support_status`, plus adding the consistency assertions.

### Established Patterns
- `dispatch()` mirrors `memory.cpp::configure_memory` line-for-line (the core
  invariant — preserve it).
- Generated `chip_database.json` is never hand-edited; regenerate with
  `python tools/build_db.py` (run with the CI-target Python, not devcontainer
  3.12, to avoid the py3.12-masks-py3.11 trap — applies to any codegen-adjacent
  drift gate).

### Integration Points
- `chip_entry` dict (~L491) is the single construction site for the new top-level
  `support_status`/`unsupported_reason` keys.
- `database.py::_map_data` / `EpromDatabase` consume the entry downstream — Phase 68
  reads `support_status` there for host refusal; Phase 66 only needs the field
  written, but should not break the existing consumer contract.

</code_context>

<specifics>
## Specific Ideas

- `X88C64@DIP24` (Xicor 8K parallel EEPROM, proto `0x34`) is the canonical
  worked example of a genuine DIP-parallel chip wrongly dropped — use it to
  validate the DB-01 inclusion path end-to-end.
- New gate FAIL/assert messages should name the offending `mfg/part` +
  `support_status` so a future regression is immediately identifiable, matching
  the existing `f"{mfg}/{part} proto=0x{proto:02X} …"` style.

## Research must-dos (open items the researcher MUST resolve before planning locks)
1. **Locate the v1.11 per-chip diff gate.** ROADMAP says "per-chip diff gate" and
   v1.11 GATE-02 was "`diff_db.py`", but **no `diff_db.py` exists** in
   `firestarter_app/tools/` — only `tools/baseline/dispatch_baseline.json`. Find
   the actual per-chip diff mechanism (could be a test, a check_dispatch arm, or
   in the meta-repo) so D-11 baseline regeneration covers the right artifact(s).
2. **Reconcile the 24-pin EEPROM unblock history.** v1.11 reportedly unblocked
   "9 × 24-pin AT28C04/16 EEPROMs (`DIP24_6116` + `0x0D`)", yet the live build
   still has only **2** `DIP24_6116` entries and **9 still dropped** at the
   hazard gate. Determine why the 9 were skipped by that unblock, and confirm each
   is genuinely flag-only `adapter-required` (D-03) and not trivially unblockable —
   resolving the consistency oddity (`AT28C16@DIP24` adapter-required vs the
   already-supported `AT28C16A`).
3. **Confirm the curated NMOS list + exact RURP VPP ceiling** (D-06) at plan time
   against authoritative datasheet/hardware sources.

</specifics>

<deferred>
## Deferred Ideas

- **Pinout *classification* for unclassifiable DIP chips** → Phase 67 (DB-02).
  Phase 66 only writes best-effort pinouts for the chips it includes (D-09).
- **Host `info`/`write`/`read`/`verify` capability display + refusal messages** →
  Phase 68 (DB-04). Phase 66 writes the data + gates it; the host-side
  status-specific messaging and hardware-operation refusal are Phase 68.
- **Actually making any flagged chip programmable** (per-protocol implementation;
  24-pin EEPROM firmware handler; high-VPP hardware) → future, mostly
  hardware-gated, per-protocol milestones. Explicitly out of scope (D-03).
- **Erase-command firmware support** for 0x07-path EEPROMs → separate firmware
  backlog item, unrelated to this phase.

None — discussion stayed within phase scope (the adapter-required pull-in, D-02,
is an operator-authorized scope decision recorded above, not creep).

</deferred>

---

*Phase: 66-db-inclusion-vpp-correction-dispatch-gate*
*Context gathered: 2026-06-12*

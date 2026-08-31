# Phase 70: v1.11 + v1.12 DB-Pipeline Integration for Beta Merge - Context

**Gathered:** 2026-06-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Re-port v1.12's DB-build **safety** features onto v1.11's principled
`resolve_pinout_key()` pipeline so the `v1.12-protocol-dispatch-hardening` branch
merges into the v1.11-bearing `beta` with **zero decode-correctness regression** and
**zero 12V-to-wrong-pin hazard**.

v1.12 was forked off the **pre-v1.11** beta (`faaa571`). Its `build_db.py` carries its
own `resolve_pinout_key` built **on top of** the resurrected `DIP28_VARIANT_MAP` /
`PIN_MAP_TO_PINOUT` guess tables plus per-chip SRAM override hacks. v1.11's Phase 58
**deleted** those tables and replaced selection with a principled mask-based
`resolve_pinout_key`. This is an **integration / re-port**, NOT a conflict-merge:
re-express v1.12's safety features on v1.11's architecture, keeping v1.11's decode fixes.

**v1.12 safety features to re-port (the WHAT — locked by ROADMAP):**
- `support_status` taxonomy: `protocol-not-implemented` / `adapter-required` / `vpp-exceeds-max`
- true-NMOS-VPP correction (M2716/M2732 = 25V, M2732A = 21V) + `RURP_VPP_CEILING` (~22V) demotion
- `0x34` / X88C64P (XICOR NovRAM) classified `protocol-not-implemented`
- capability-honest inclusion gates (include-but-flag unsupported DIP parallel chips)
- `NON_DISPATCHABLE_ALGO = 0x00` for non-supported chips

**v1.11 decode fixes that MUST be preserved:** no `0x35`/`0x39` protocols (DEC-05);
`voltages & 0xF0` VPP-nibble mask; corrected vcc/vdd bit positions; `interpret_timing`
×100 fix; corrected VCC nibbles.

**Surface:** HOST DB tooling (`firestarter_app/tools/build_db.py`,
`check_dispatch.py`, `diff_db.py`, regenerated `chip_database.json`, their
tests/snapshots/golden). Firmware merge is **staged but not tagged** in this phase
(see D-08). Host runtime (`chip_resolver.py`, `exceptions.py`, `cli_handlers.py`,
`frame_parser.py`) merges clean — only the DB-build pipeline collides.

</domain>

<decisions>
## Implementation Decisions

### Merge mechanics
- **D-01:** Re-port **on the `v1.12-protocol-dispatch-hardening` branch**. Rewrite
  `build_db.py` / `check_dispatch.py` / `diff_db.py` there to sit on beta's
  principled `resolve_pinout_key` architecture, regenerate `chip_database.json`, get
  all gates green — THEN merge v1.12→beta (now near-clean) as the final step. Keeps
  full v1.12 history; the merge is the last action, not the first.
  - **Rationale:** Avoids a conflict-merge against the divergent `build_db.py`;
    the branch becomes architecturally compatible with beta *before* the merge, so
    the merge is mechanical.

### Pinout fixes (re-expressing v1.12's SRAM/per-chip overrides)
- **D-02:** Prefer **extending the mask logic in v1.11's `resolve_pinout_key`
  natively** so the per-chip SRAM override hacks (v1.12 `build_db.py` ~L550-565) are
  not needed. Fix the principled mask logic itself rather than layering overrides.
- **D-03 (guardrail):** The **zero-decode-regression criterion wins** over purity.
  Fallback policy is **decided per-chip during planning/research**: research surfaces
  which chips beta's principled resolve mis-routes (if any) and recommends, per chip,
  whether mask-extension or a documented per-chip override is correct. No blanket
  "block until perfect" stance and no blanket override layer — case-by-case, evidence-driven.
  - **Rationale:** Largest blast radius is on the shared `resolve_pinout_key`; a mask
    change that regresses a v1.11-correct chip would violate SC#2. Per-chip decisions
    keep the 743-chip clean diff intact while preferring the principled path where safe.

### Diff baseline & reconciliation (SC#4)
- **D-04:** Use a **two-stage diff**: (a) **decode/pinout changes** — must be
  near-zero to prove no v1.11 regression (this is the regression-critical gate for
  SC#2); (b) **additive safety-field changes** (`support_status`, VPP demotions,
  `NON_DISPATCHABLE_ALGO`) — expected bulk, each categorized by a documented rule.
- **D-05:** Baseline for stage (a) is the **v1.11 beta `chip_database.json`** (the
  committed DB on beta). v1.11's pinned `chip_database.baseline.json` (GATE-01 anchor)
  remains the existing regression reference and should be reconciled/refreshed as part
  of this work. "0 unexplained" means every chip in BOTH stages maps to a documented rule.

### Firmware lockstep scope
- **D-06:** Firmware **is in scope** for Phase 70, but the phase **STOPS before any
  tag**. Perform the firmware `v1.12→beta` merge, build both envs (uno + leonardo),
  run native dispatch tests, and confirm wire-constant parity with the host
  (`MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` etc.). The lockstep is **proven, not published**.
- **D-07:** The **beta pre-release tag / beta-cut stays operator-gated** — do NOT cut
  any tag in either repo during this phase (standing rule:
  [[feedback_stable_release_operator_gated]]).

### Claude's Discretion
- Exact task breakdown and ordering within the re-port (research + planner decide).
- Whether `diff_db.py` itself needs a `--stage` flag or two invocations to express
  the two-stage diff (D-04) — implementation detail for planning.
- Specific test/snapshot updates required by the regenerated DB.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The collision & integration intent
- `.planning/ROADMAP.md` §"Phase 70" (lines ~877-919) — full goal, scope, v1.12 safety
  feature list, and 6 success criteria. The authoritative scope anchor.
- `.planning/PROJECT.md` — v1.12 milestone goal + branch model (unified beta, dual-repo lockstep).

### v1.11 architecture (the target to re-port ONTO)
- `firestarter_app/tools/build_db.py` (on `beta`) — principled `resolve_pinout_key`
  (L147+), `DIP28_VARIANT_MAP`/`PIN_MAP_TO_PINOUT` DELETED note (L134-135). This is the
  architecture v1.12's features must move onto.
- `.planning/milestones/v1.11-ROADMAP.md`, `.planning/milestones/v1.11-REQUIREMENTS.md`
  — v1.11 decode fixes (DEC-01..05, PIN-01..03), GATE-01..04 definitions.
- `firestarter_app/tools/check_dispatch.py` + `tools/diff_db.py` (on `beta`) — v1.11's
  GATE-02/GATE-03 gates that the integration must keep green.
- `firestarter_app/tools/baseline/` — pinned baseline anchor (GATE-01).

### v1.12 features (the WHAT to carry over)
- `firestarter_app/tools/build_db.py` (on `v1.12-protocol-dispatch-hardening`) —
  `support_status` logic, `RURP_VPP_CEILING_MV` (L93), `NON_DISPATCHABLE_ALGO` (L122),
  true-NMOS VPP correction (~L638), per-chip SRAM overrides (~L550-565) to be re-expressed.
- `firestarter_app/firestarter/exceptions.py` / `chip_resolver.py` / `cli_handlers.py`
  (v1.12) — host runtime support_status guard + `ProtocolNotImplementedError` (merges clean).
- `firestarter_app/tools/catalog/codegen.py` + `catalog/messages.toml` (v1.12) — wire
  message lockstep (Phase 63 WIRE-01).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `resolve_pinout_key()` (beta `build_db.py`) — the principled mask-based pinout
  selector; the single pinout path per SC#1. v1.12's pinout fixes fold into THIS.
- `check_dispatch.py` GATE-03 (beta) — full-class VPP-safety guard (743 chips, 0
  violations on v1.11); re-run after regeneration to satisfy SC#3.
- `diff_db.py` (beta) — per-chip diff gate; extend for the two-stage diff (D-04).
- v1.12 host runtime (`exceptions.py`/`chip_resolver.py`/`cli_handlers.py`) — already
  carries the support_status refusal guard; survives the merge per roadmap.

### Established Patterns
- DB is **regenerated, never hand-merged** (ROADMAP scope note). `chip_database.json`
  is a build artifact of `build_db.py`.
- Both branches define `resolve_pinout_key` with the SAME NAME but divergent bodies —
  the merge must take **beta's** body and graft v1.12's safety logic, NOT a textual merge.
- Dual-repo lockstep wire constants (Python `constants.py` ↔ C++ `firestarter.h`).

### Integration Points
- `build_db.py` is upstream of `chip_database.json` → consumed by host runtime
  (`chip_resolver.py`) → wire dict → firmware dispatch. The integration must keep this
  chain honest end-to-end.
- Firmware wire-response constants must match host expectations (D-06 verification).

</code_context>

<specifics>
## Specific Ideas

- The crux is the divergent `resolve_pinout_key`: beta's principled mask version is the
  keeper; v1.12's guess-table version (with `DIP28_VARIANT_MAP`) is discarded.
- v1.12's per-chip SRAM override hacks (~L550-565) are the concrete artifact to
  eliminate-or-document per D-02/D-03 — research should enumerate exactly which chips
  they touch and how beta's resolve handles each.
- "Zero decode regression" (SC#2) is operationalized as the near-zero stage-(a) diff (D-04).

</specifics>

<deferred>
## Deferred Ideas

- **Beta cut + lockstep pre-release tag** — operator-gated, explicitly out of Phase 70
  (D-07). Happens after this phase on operator authorization.
- **v1.12 milestone close** — blocked on this integration phase; follows the beta merge.
- None of the discussion introduced new capabilities — scope stayed within the re-port.

</deferred>

---

*Phase: 70-v1-11-v1-12-db-pipeline-integration-for-beta-merge*
*Context gathered: 2026-06-15*

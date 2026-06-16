# Phase 63: Catalog Lockstep Wire Change - Context

**Gathered:** 2026-06-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Add a single new wire-protocol message constant — `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB` — to the meta-repo canonical `tools/catalog/messages.toml`, sync it byte-identically into both sub-repos, and regenerate both code-generated outputs (`firestarter/include/messages.h` and `firestarter_app/firestarter/messages.py`). The codegen drift gate must be green in both repos when run with the CI-matching Python version.

**Zero behavior change.** This is a catalog-only commit: the constant is *defined* but referenced by no code anywhere. The firmware emit lands in Phase 64; the host handling lands in Phase 65. This commit must be self-contained and reviewable in isolation.

Satisfies requirement **WIRE-01**.

</domain>

<decisions>
## Implementation Decisions

### Catalog entry shape (the one user-facing decision)
- **D-01:** The new entry mirrors its sibling `MSG_ERR_MEM_TYPE_UNSUPPORTED` (0xAE) exactly — same `params`/`render` style, protocol byte rendered as **hex**. Locked definition:
  ```toml
  [[messages]]
  id          = 0xBB
  name        = "MSG_ERR_PROTOCOL_NOT_IMPLEMENTED"
  severity    = "ERROR"
  format      = "Protocol 0x%02x not implemented"
  params      = [{ type = "u8", render = "hex_byte" }]
  wire_format = "id_frame"
  ```
  Rationale: hex matches how `protocol_id` / `algorithm_id` are referenced everywhere else in this milestone; mirroring 0xAE keeps the ERROR-band entries visually consistent. WIRE-01's "carry the offending protocol byte as a param" is satisfied by the single `u8` param.

### ID placement (determined, not open)
- **D-02:** `0xBB` is the correct slot — verified against the live catalog. ERROR band is `0xA0..0xDF`; the current last ERROR entry is `0xBA` (`MSG_ERR_MEM_SIZE_TOO_SMALL`). `0xBB` is the next free in-band ID, no collision, ERROR band sequence intact (Success Criterion #4). Place the new `[[messages]]` block immediately after the `0xBA` entry — source order is human-readability only (codegen sorts by id ascending), but keeping it adjacent to its band neighbors is the house style.

### Edit + sync workflow (locked by file convention)
- **D-03:** Edit **only** the meta-repo canonical `tools/catalog/messages.toml`, then run `tools/catalog/sync_to_subrepos.sh` to copy it byte-identically into `firestarter/tools/catalog/` and `firestarter_app/tools/catalog/`. Never hand-edit the sub-repo copies. (Enforced by the canonical file's own header comment, lines 6-8.)

### Codegen execution (hard constraint, not a preference)
- **D-04:** Codegen MUST be run with **Python 3.11** (the CI-matching version), NOT the devcontainer's Python 3.12. This project has a documented, repeat-offender "py3.12-masks-py3.11" drift trap: codegen output that looks clean under 3.12 can fail the CI drift gate under 3.11. The drift gate is `codegen + git diff --exit-code`; both sub-repos must report no drift. Prove green locally against 3.11 before claiming Success Criterion #2.

### Cross-repo lockstep
- **D-05:** Both generated outputs change in the same logical change set: `firestarter/include/messages.h` (C++ `#define`/enum) and `firestarter_app/firestarter/messages.py` (Python constant). The meta-repo also tracks the canonical `tools/catalog/messages.toml`. Three edit surfaces, one wire change. Keep the meta `firestarter_app` gitlink behavior consistent with the milestone's pinning rules (do not bump gitlinks per-phase unless the milestone close instructs it).

### Claude's Discretion
- Exact mechanics of how the executor invokes Python 3.11 in this devcontainer (e.g. `/usr/local` python vs a pinned interpreter), and whether the drift gate is verified via the CI workflow command or a direct `codegen.py` + `git diff` — planner/executor decides. The *requirement* (green under 3.11) is fixed; the *invocation* is not.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Catalog source + codegen
- `tools/catalog/messages.toml` — meta-repo canonical message catalog (THE file to edit; header documents the edit-only-here + sync convention). New entry goes after the `0xBA` block.
- `tools/catalog/sync_to_subrepos.sh` — propagates the canonical TOML byte-identically into both sub-repos.
- `tools/catalog/codegen.py` — generates `messages.h` + `messages.py` from the TOML. (Sub-repo copies: `firestarter/tools/catalog/codegen.py`, `firestarter_app/tools/catalog/codegen.py`.)
- `firestarter/include/messages.h` — generated C++ output (Success Criterion #1 target).
- `firestarter_app/firestarter/messages.py` — generated Python output (Success Criterion #1 target).

### CI drift gates (must be green under py3.11)
- `firestarter/.github/workflows/build.yml` + `firestarter/.github/workflows/beta-build.yml` — firmware-side codegen drift gate.
- `firestarter_app/.github/workflows/ci.yml` + `firestarter_app/.github/workflows/beta-release.yml` — host-side codegen drift gate.

### Requirements + roadmap
- `.planning/REQUIREMENTS.md` — WIRE-01 (this phase), WIRE-02 (Phase 64 emit), HOST-01/HOST-02 (Phase 65 handling).
- `.planning/ROADMAP.md` §"Phase 63" — goal + 4 success criteria.

### Sibling for shape reference
- The `0xAE` `MSG_ERR_MEM_TYPE_UNSUPPORTED` entry in `tools/catalog/messages.toml` — the structural template D-01 mirrors.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`MSG_ERR_MEM_TYPE_UNSUPPORTED` (0xAE)**: direct structural template for the new entry — same `u8` + `hex_byte` render param, same `id_frame` wire format, same ERROR severity.
- **`sync_to_subrepos.sh` + `codegen.py`**: the entire propagation pipeline already exists; this phase adds zero tooling, only one TOML stanza + a regen run.

### Established Patterns
- **Single canonical source, generated everywhere**: the catalog is edited in one place (meta-repo TOML) and code-generated into both sub-repos. The drift gate enforces that the committed generated files match a fresh codegen run.
- **DO NOT REORDER**: TOML source order is preserved for diff readability; codegen sorts by id. New entries are appended within their severity band.
- **py3.12-masks-py3.11**: known milestone-cut trap — validate generated output against the CI Python version (3.11), not the devcontainer default.

### Integration Points
- None functional this phase. The constant becomes a *consumable* for Phase 64 (firmware emit in the dispatch fail-closed path) and Phase 65 (host `ProtocolNotImplementedError`). No call site is added here by design (Success Criterion #3).

</code_context>

<specifics>
## Specific Ideas

- Message string: **"Protocol 0x%02x not implemented"** — protocol byte in hex, mirroring the 0xAE sibling. Chosen by the user over a decimal render.

</specifics>

<deferred>
## Deferred Ideas

- **Firmware emit of the new message** (`configure_not_implemented()`, `protocol != 0` guard, named infeasibility arms for 0x11/0x2A/0x2B/0x2C, Unity tests) — Phase 64 (WIRE-02, DISP-01..04, TEST-01/02). Explicitly out of scope here: no call sites in this commit.
- **Host graceful handling** (`ProtocolNotImplementedError` subclass, actionable CLI message) — Phase 65 (HOST-01, HOST-02).

</deferred>

---

*Phase: 63-catalog-lockstep-wire-change*
*Context gathered: 2026-06-10*

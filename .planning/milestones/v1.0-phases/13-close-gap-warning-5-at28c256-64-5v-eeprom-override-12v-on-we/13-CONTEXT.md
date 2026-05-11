# Phase 13: Close gap WARNING-5 — AT28C256/64 5V EEPROM override (12V on /WE on write)

**Gathered:** 2026-05-11
**Status:** Ready for planning
**Source:** Derived from `.planning/v1.0-MILESTONE-AUDIT.md` (re-audit 2026-05-11T11:00) + `.planning/INTEGRATION-CHECK.md` (post-Phase-12).

<domain>
## Phase Boundary

This phase closes the hazardous condition introduced by Phase 12: AT28C-family 5V EEPROMs in the upstream minipro database are tagged `algorithm=0x07` (EPROM_STD) and `electrical.type="Flash/EEPROM"`. Pre-Phase-12 these chips hit BLOCKER-1 and returned a safe ERROR. Phase 12 closed BLOCKER-1, which removed the safe guard — these chips now route through `configure_eprom` and apply 12V `P1_VPP_ENABLE` to socket pin 1 during the write pulse. On the DIP28_2764 pinout that AT28C256/64 use, socket pin 1 = `/WE` (not VPP). Applying 12V to `/WE` during a write is a hardware-damage path.

**In scope:**
- Make AT28C-family 5V EEPROMs (algorithm=0x07 + electrical.type='Flash/EEPROM' in upstream minipro DB) NOT apply 12V to pin 1 on write.
- Preserve correct behavior for W27C512 and other electrically-erasable UV-EPROMs that ARE algorithm=0x07 + 'Flash/EEPROM' AND DO need 12V VPP on pin 1.
- Regenerated `minipro_complete_db.json` reflects the fix; existing chip names that historically worked continue to work.

**Out of scope:**
- Re-classifying every minipro tag (only the AT28C-family hazardous subset).
- Implementing the EEPROM_POLL (0x0D) handler's missing SDP-disable for AT28C256-specific factory-locked variants (separate concern; the 0x0D handler already exists and is correct for the algorithm).
- WARNING-1, WARNING-2, WARNING-3, WARNING-4 (separate closure phases).
- Hardware verification on a real RURP shield (no hardware available; defer to a future hardware-test phase).

</domain>

<decisions>
## Implementation Decisions

### Affected chip set (LOCKED — from audit)
- ~30 chips with `algorithm=0x07` AND `electrical.type="Flash/EEPROM"` in upstream minipro.
- Concrete examples: `AT28C256`, `AT28C64`, `AT28C64B`, `AT28C64E`, `AT28BV64`, `AT28BV64B`, `AT28BV256`, `AT28C17`, `AT28C17E`.
- Must distinguish from `W27C512`, `SST27SF512`, and other electrically-erasable UV-EPROMs that legitimately need 12V VPP on pin 1 — these ALSO have `algorithm=0x07` + `electrical.type="Flash/EEPROM"`.
- The distinguishing signal is **manufacturer + chip name family prefix**, not the raw upstream protocol_id alone (which is wrong for the AT28C family).

### Fix-shape choice (NEEDS RESEARCH)
Three candidate fix shapes from the audit:
- **(A) Override in `build_db.py`** — at chip-emit time, detect the AT28C-family pattern (manufacturer + name prefix), reclassify their `algorithm` to `0x0D` (EEPROM_POLL) AND `electrical.type` to a non-Flash value so the existing 0x0D protocol-prefix dispatch fires.
- **(B) User-override layer in `database.py`** — apply a static override table at load time (similar to user `database.json` overrides but baked in).
- **(C) Firmware protocol-guard in `eprom.cpp` / `eprom_internal_set_control_register`** — refuse to flip `VPE_ENABLE → P1_VPP_ENABLE` when handle indicates a 5V-only EEPROM family (would require a new wire-protocol signal).

Tradeoffs to research:
- (A) is the cleanest data-layer fix and matches the project's "build_db.py is the single source of truth" stance from REQ-DB-05. The reclassification flows naturally into the existing 0x0D protocol-prefix dispatch added in Phase 06.
- (A) has a risk surface: AT28C parts using SDP need the disable sequence before first write; if we route them to `configure_eeprom28c` they hit the existing SDP-disable logic. Need to verify the existing 0x0D handler is correct for AT28C256/64.
- (B) doesn't require regenerating the DB but adds a second source of truth diverging from upstream.
- (C) is defense-in-depth but requires a new wire signal and firmware change; higher cost.

**Preferred direction (to validate via research):** Option (A) — override table in `build_db.py`. Single layer change, leverages existing 0x0D dispatch, keeps "build_db.py is canonical" invariant.

### Override-table location and shape
- A module-level constant in `build_db.py` (e.g. `_PROTOCOL_OVERRIDES`) keyed by `(manufacturer, name_prefix)` → `{new_algorithm, new_electrical_type}`.
- Applied AFTER reading minipro XML but BEFORE writing `chip_entry`.
- Logged at run time so the diff is auditable (regression-friendly).
- Pattern should mirror the existing `DIP28_VARIANT_MAP` / `VPP_MV` / `KNOWN_PROTOCOLS` table idioms at module top.

### Tests / regression coverage
- A new check in `check_dispatch.py` (or sibling script) asserting: every chip whose manufacturer+name matches the AT28C-family pattern routes to `configure_eeprom28c` (not `configure_eprom`).
- The existing `pio test -e native -f "*test_dispatch*"` already covers the 0x0D protocol dispatch; no new firmware tests needed if Option A is chosen.
- Regression scan must confirm W27C512 / SST27SF512 / electrically-erasable UV-EPROMs are UNCHANGED (still route to configure_eprom with 12V VPP on pin 1).

### Documentation
- Update `firestarter_app/CLAUDE.md` to document the override table.
- Update `.planning/REQUIREMENTS.md` if a new sub-requirement is added (e.g., REQ-DB-06: protocol override for upstream-mistagged chips).
- Cross-reference the entry in `.planning/v1.0-MILESTONE-AUDIT.md` so the WARNING-5 closure is traceable.

### Claude's Discretion
- Exact set of `(manufacturer, name_prefix)` pairs to include in the override table (informed by `RESEARCH.md`).
- Logging format for the regenerator (must be parseable for the regression scan but not intrusive).
- Whether to add a new REQ-ID for this override or treat it as closure of WARNING-5 only.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Audit + integration findings
- `.planning/v1.0-MILESTONE-AUDIT.md` — full WARNING-5 context, scope, affected chips
- `.planning/INTEGRATION-CHECK.md` — WARNING-5 section with exact firmware trace

### Phase 12 (predecessor)
- `.planning/phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-CONTEXT.md` — D5 deferral of AT28C256 override
- `.planning/phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-VERIFICATION.md` — 8/8 truths verified; defines the post-Phase-12 dispatch order

### Codebase entry points
- `firestarter_app/tools/build_db.py` — single canonical DB build tool (REQ-DB-05); existing module-top tables: `KNOWN_PROTOCOLS`, `PROTOCOL_MAP`, `VPP_MV`, `DIP28_VARIANT_MAP`. New `_PROTOCOL_OVERRIDES` should live here.
- `firestarter_app/firestarter/database.py` — `_ALGO_MEM_TYPE` table (Phase 12), `_map_data`, `convert_to_programmer`
- `firestarter_app/tools/check_dispatch.py` — regression scan from Phase 12; reusable pattern for the new AT28C-family assertion
- `firestarter/src/proms/memory.cpp:configure_memory` lines 72-116 — current protocol-prefix dispatch chain
- `firestarter/src/proms/eprom.cpp:eprom_internal_set_control_register` — where `VPE_ENABLE → P1_VPP_ENABLE` flip happens for `using_p1_as_vpp(handle)` chips
- `firestarter/src/proms/eeprom_28c.cpp:eeprom28c_write_init` — the 0x0D handler that AT28C256 SHOULD reach after this fix; includes SDP-disable
- `firestarter_app/firestarter/data/minipro_complete_db.json` — regenerated DB (will be regenerated again at end of this phase)
- `firestarter_app/firestarter/data/pinouts.json` — DIP28_2764 pinout assigns VPP to pin 1; AT28C256/64 must NOT use this pinout for write operations

### Requirements
- REQ-FW-03 (EEPROM_POLL DQ7 polling for AT28C256) — currently UNREACHED for AT28C256 because of upstream algorithm=0x07 mistag
- REQ-SAF-01 (VPP voltage ADC check before first write pulse for every chip) — currently compounded by WARNING-5 because the chip routes to a path that applies VPP to /WE

</canonical_refs>

<specifics>
## Specific Ideas

### Confirmed chip families (from audit + minipro upstream)
- AT28C256 / AT28C256E — 5V parallel EEPROM, 32K×8, DIP28, /WE on pin 27, /OE on pin 22 (per Atmel datasheet)
- AT28C64 / AT28C64B / AT28C64E — 5V parallel EEPROM, 8K×8, DIP28
- AT28C17 / AT28C17E — 5V EEPROM, 2K×8, DIP24 (NOT the 28-pin pinout; verify scope)
- AT28BV64 / AT28BV64B / AT28BV256 — 5V (BV = battery-voltage low-power), same family

### Pinout sanity check
For AT28C256 (DIP28):
- pin 1 = A14 (address line, NOT WE — verify against datasheet)
- pin 22 = /OE
- pin 27 = /WE
- pin 20 = /CE
- pin 28 = VCC (5V)

Audit references "DIP28_2764 pinout assigns VPP to pin 1" — confirm that DIP28_2764 pinout assignment for AT28C256 means socket pin 1 receives 12V VPP regulator output, which then connects to AT28C256 pin 1 = A14 (high address line). Either way: 12V on a 5V part's address line is damaging. The exact pin-1 function on AT28C256 is **A14** (not /WE as initially noted in the audit text — research must verify).

### Existing PROTOCOL_MAP entries in build_db.py
- Already maps `proto_id` → tuple. New `_PROTOCOL_OVERRIDES` should sit alongside, named consistently.

### Existing user-override path in database.py
- `~/.firestarter/database.json` loads user overrides via `EpromDatabase._initialize_database_core`. Demonstrates the pattern but is per-user, not project-baked.

</specifics>

<deferred>
## Deferred Ideas

- Full per-chip override mechanism beyond AT28C-family (e.g., other upstream-mistagged chips) — only address AT28C-family in this phase.
- Hardware verification on a real RURP shield — separate hardware-test phase (no hardware in this env).
- Renaming wire JSON key `"vpp"` → `"vpp_mv"` (WARNING-3) — separate phase.
- Adding the missing VPP ADC compare to `flash_intel_write_init` (WARNING-1) — separate phase (recommended Phase 14).
- 28C handler chip_id check (WARNING-2) — separate phase (forward-compat hazard).

</deferred>

---

*Phase: 13-close-gap-warning-5-at28c256-64-5v-eeprom-override-12v-on-we*
*Context derived 2026-05-11 from milestone audit (post-Phase-12 re-audit at 11:00).*

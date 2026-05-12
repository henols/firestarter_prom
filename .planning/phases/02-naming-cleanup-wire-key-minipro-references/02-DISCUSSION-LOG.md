# Phase 2: Naming Cleanup (Wire Key + Minipro References) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-12
**Phase:** 02-naming-cleanup-wire-key-minipro-references
**Areas discussed:** Wire-key transition policy, New DB filename + internal vpp_volts

**Areas NOT selected (Claude made reasonable calls — see CONTEXT.md):**
- User-override DB compat — D-08-compat in CONTEXT.md (loader stays tolerant on
  internal read; wire is atomic).
- Plan granularity — D-13 in CONTEXT.md (3-plan split; planner's discretion to
  merge).

---

## Wire-key transition policy

### Question 1: How should the firmware JSON parser handle the wire-key transition from "vpp" to "vpp_mv"?

| Option | Description | Selected |
|--------|-------------|----------|
| Atomic flip (Recommended) | Firmware accepts ONLY `"vpp_mv"`. Python emits ONLY `"vpp_mv"`. User must flash matching firmware + app together. Cleanest. Matches the audit text "atomic rename". Phase 4 hardware-test scripts will use the new key only — simpler test surface. | ✓ |
| Firmware accepts both (vpp_mv preferred, vpp fallback) | `json_parser.c` registers both keys; vpp_mv takes precedence when both present. Python emits only vpp_mv. Lets users with old firmware keep working until they reflash. Adds one parser line + a comment but no real complexity. | |
| Python emits both (firmware reads only vpp_mv) | Mirror image — firmware atomic, host emits both during transition. Lets new app drive old firmware. Less useful (users typically reflash firmware before upgrading app). | |

**User's choice:** Atomic flip
**Notes:** Locked as D-01 in CONTEXT.md. The const at `json_parser.c:62`, the
dispatch row at `:74`, and the body at `:308-310` are a single atomic-flip unit
— mismatch at any of the three silently breaks the parse (SAF-04 VPP ADC compare
trips on every Intel-flash write because `handle->vpp_mv` would be 0).

### Question 2: Wire-key cleanup scope — should `convert_to_programmer` strip the legacy `"vpp"` from the emitted wire dict entirely?

| Option | Description | Selected |
|--------|-------------|----------|
| Strip vpp from wire dict (Recommended) | `database.py:518` emits ONLY `"vpp_mv": vpp_mv` — the old `"vpp": vpp_mv` line is deleted. Matches the atomic-flip choice. Firmware doesn't see vpp at all. Test scripts updated to grep vpp_mv only. | ✓ |
| Emit both keys for one milestone | Keep `"vpp": vpp_mv` and `"vpp_mv": vpp_mv` both on the wire (current v1.0 behavior is to emit both). Defers the actual `vpp` removal until v1.2. Cleaner upgrade story but extends the semantic-overload WARNING-3 one more milestone. | |

**User's choice:** Strip vpp from wire dict
**Notes:** Locked as D-02 in CONTEXT.md. `convert_to_programmer:518` deletes
the `"vpp": vpp_mv,` line; the wire JSON example in `firestarter_app/CLAUDE.md:46-58`
is also collapsed.

---

## New DB filename + internal vpp_volts

### Question 1: Pick the new neutral filename for `firestarter/data/minipro_complete_db.json`.

| Option | Description | Selected |
|--------|-------------|----------|
| chip_database.json (Recommended) | Most generic, matches REQUIREMENTS.md suggested name. Describes what the file is (a chip database) without overloading the project name. | ✓ |
| firestarter_db.json | Project-branded. Tighter coupling to the project name; matches the pattern of `~/.firestarter/database.json` (user-override). Slight inconsistency with `pinouts.json` (project-neutral file already in the same dir). | |
| chips.json | Shortest. Symmetric with `pinouts.json` already in the same data dir. Minor: less self-describing than `chip_database.json`. | |
| eprom_db.json | Narrower scope name. Slight semantic mismatch — the DB also contains Flash, EEPROM, SRAM — not just UV-EPROMs. | |

**User's choice:** chip_database.json
**Notes:** Locked as D-05 in CONTEXT.md. Rhymes with `~/.firestarter/database.json`
(user override) — reinforces the base + override symmetry.

### Question 2: Internal field `"vpp"` (float volts) at database.py:417 lives next to `"vpp_mv"` (int millivolts) — rename it?

| Option | Description | Selected |
|--------|-------------|----------|
| Rename to `vpp_volts` (Recommended) | Symmetric with `vpp_mv`. Removes the same volts/mV semantic overload internally. Touches `_map_data()` writer and any reader of the `vpp` float-volts internal field (sweep grep: `electrical.get("vpp"`, `data["vpp"]`, etc.). Tiny extra scope, but it's the same WARNING-3 root cause. | ✓ |
| Leave it — wire scope only | Only rename the WIRE key. Internal float-volts field stays as `"vpp"`. Matches the strict reading of WIRE-01 ("wire JSON"). Keeps the file diff smaller but leaves the same name-overload visible to any future reader of `_map_data()`. | |
| Drop the internal float-volts field entirely | Delete `"vpp"` (float) and `vpp_str` parsing at database.py:373-381. `vpp_mv` (int) is the authoritative value from build_db.py. Only callers using float-volts would break — check whether eprom_info.py or ic_layout.py display float volts. More aggressive cleanup. | |

**User's choice:** Rename to `vpp_volts`
**Notes:** Locked as D-04 in CONTEXT.md. Scope distinction documented:
- IN scope: the in-memory dict key `_map_data()` produces (database.py:417 +
  the consumer fallback at :510).
- OUT of scope: the upstream-schema `electrical.vpp = "12V"` string read at
  :373-381 (that field is on-disk DB-owned, not in-memory dict-owned).
Planner must grep callsites reading `["vpp"]` (not `["vpp_mv"]`) in eprom_info.py,
ic_layout.py, etc., and update them.

---

## Claude's Discretion

Areas the user did NOT select for discussion — reasonable calls written
directly into CONTEXT.md:

- **User-override DB compat** (CONTEXT.md D-08-compat) — Loader stays tolerant
  on internal READ; wire is atomic. The existing `_map_data()` fallback at
  `database.py:373-387` (`electrical.get("vpp_mv", 0)` then
  `electrical.get("vpp", "0").replace("V", "")`) is PRESERVED — this handles
  legacy user-override DBs at `~/.firestarter/database.json`. Net effect: users
  with legacy overrides keep working internally; users with old firmware do
  not.
- **Plan granularity** (CONTEXT.md D-13) — Split into 3 plans (planner's
  discretion to merge if friction):
  - Plan 02-01: WIRE-01 atomic flip (Python emitter + firmware parser + wire
    example).
  - Plan 02-02: CLEAN-01 file rename + internal `vpp_volts` rename + reader/
    writer/doc sweep.
  - Plan 02-03: CLEAN-02 attribution scrub + WIRE-02 regression + SC#5 CLI
    smoke.

Other Claude-discretion notes documented in CONTEXT.md "Claude's Discretion"
section.

---

## Deferred Ideas

Captured in CONTEXT.md `<deferred>` section:

- Remove the on-disk `"vpp"` (volts string) field from `build_db.py:255` and
  the DB schema — v1.2 cleanup, would simplify schema but risks user overrides.
- Drop `vpp_volts` field entirely (v1.2+) — compute float volts on demand from
  `vpp_mv / 1000.0`.
- Test-script repair for `firestarter_test.sh` / `write_test.sh` — owned by
  Phase 4 / HW-01.
- Python-side wire-emit unit test (`test_convert_to_programmer.py`) — nice-to-
  have if Python test infra arrives.
- `firestarter vpp` CLI subcommand — separate concept (command name, not wire
  key); user muscle memory.
- Replace minipro upstream — out of scope (REQUIREMENTS.md "Out of Scope").
- `firestarter/data/pinouts.json` rename — no overload, keep as-is.
- `~/.firestarter/database.json` rename — would break user installations;
  explicitly rejected.
- Add `vpp_volts` consumers — v1.2 cleanup in `eprom_info.py` / `ic_layout.py`.

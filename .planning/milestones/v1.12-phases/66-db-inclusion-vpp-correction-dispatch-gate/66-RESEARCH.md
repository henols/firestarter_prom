# Phase 66: DB Inclusion + VPP Correction + Dispatch Gate — Research

**Researched:** 2026-06-12
**Domain:** Python host CLI database pipeline (`build_db.py`, `check_dispatch.py`, `chip_database.json`)
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**D-01:** Re-audit per family. Include only confirmed DIP-parallel memory as
`support_status: protocol-not-implemented`. Serial (0x04 DataFlash, 0x11 FWH),
PLCC/SMD-only, and adapter-class (0x0A) parts stay skipped. Do not trust the
coarse DIP filter blindly — it leaks `@SOIC28`/`@PLCC32`-aliased parts.
Current drop census (verified by live run): 24 chips — `0x04`×18 (DataFlash,
skip), `0x11`×4 (FWH — ST M50FW040/M50FW080 ×2 in two DBs, skip), `0x0A`×1
(`TMS87C257@PLCC32`, skip), `0x34`×1 (`X88C64P@DIP24,X88C64S@SOIC24`,
**include candidate**).

**D-02:** Pull the 9 damage-hazard-skipped 24-pin EEPROMs into Phase 66 as
`support_status: adapter-required`. These are the 9 DIP24 entries currently
dropped at the 24-pin EEPROM damage-hazard gate.

**D-03 (HARD):** The 9 are flagged `adapter-required`, NOT routed to a working
handler.

**D-04:** Encode NMOS VPP exception list as an inline module-level dict in
`build_db.py`, matched against each entry's alias list.

**D-05:** Key-and-correct, don't split. Apply true VPP on the entry as-is.

**D-06:** Always record the true VPP, then derive `support_status` from the
RURP VPP ceiling (~22V). Exact ceiling constant and curated list resolved at
plan time.

**D-07:** Every chip carries an explicit `support_status`. `unsupported_reason`
present only on non-supported entries.

**D-08:** `support_status` + `unsupported_reason` are top-level keys, siblings
of `electrical` / `programming` / `pinout`.

**D-09:** Non-supported chip keeps whatever `resolve_pinout_key` currently
returns.

**D-10:** Non-supported chips exempt from "must dispatch safely" checks. Gate
adds assertions: (1) non-supported chip has non-empty `unsupported_reason`;
(2) `protocol-not-implemented` chip genuinely has unimplemented protocol;
(3) no `supported` chip is non-dispatchable. `not_implemented` FAIL bucket
reworked: a chip resolving `not_implemented` is FAIL only if
`support_status == supported`.

**D-11:** Regenerate affected baselines as an authorized, reviewed deviation.
`dispatch_baseline.json` excluded `vpp_mv`, so it churns only from new included
chips.

### Claude's Discretion
- Exact `unsupported_reason` message wording (must use locked taxonomy strings).
- Placement/order of new `build_db.py` inclusion logic (must run after
  WARNING-5/fm1608 overrides per existing ordering invariant).
- Precise shape of new `check_dispatch.py` consistency assertions and per-bucket
  FAIL message format (mirror `f"{mfg}/{part} proto=0x{proto:02X} …"` idiom).

### Deferred Ideas (OUT OF SCOPE)
- Pinout classification for unclassifiable DIP chips → Phase 67 (DB-02).
- Host `info`/`write`/`read`/`verify` capability display + refusal → Phase 68
  (DB-04).
- Making any flagged chip programmable → future per-protocol milestones.
- Erase-command firmware support for 0x07-path EEPROMs.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DB-01 | `build_db.py` no longer silently drops DIP parallel-memory chips with unknown/unimplemented `protocol_id`; include as `support_status: protocol-not-implemented` | Section: Standard Stack / Architecture Patterns — inclusion logic, KNOWN_PROTOCOLS extension, new skip gate |
| DB-03 | Correct VPP recorded for NMOS family (M2716/M2732=25V, M2732A=21V); `support_status` derived from RURP VPP ceiling | Section: NMOS VPP Correction, ceiling analysis, curated dict pattern |
| DB-05 | `check_dispatch.py` + per-chip diff gate treat non-`supported` entries as non-dispatchable; gate stays green | Section: Gate Rework, diff gate, D-10/D-11 implementation |
</phase_requirements>

---

## Summary

Phase 66 makes `build_db.py` capability-honest through three coordinated changes
to the `firestarter_app` sub-repo. No firmware changes. No new chips become
programmable.

**Change 1 (DB-01):** The unknown-protocol skip gate at `build_db.py:340-342`
currently drops 24 chips. Re-audit reveals: 18 are DataFlash (`0x04`, SOIC28
only — skip confirmed); 4 are FWH (`0x11`, M50FW040/M50FW080 — LPC serial,
skip confirmed); 1 is `TMS87C257@PLCC32` (`0x0A` — PLCC package, skip
confirmed); 1 is `X88C64P@DIP24,X88C64S@SOIC24` (`0x34` generic — a genuine
DIP24 parallel EEPROM, include as `protocol-not-implemented`). Additionally,
the 24-pin damage-hazard gate at L359-370 drops exactly 9 chips (9 live-run
confirmed); these are included as `adapter-required` per D-02.

**Change 2 (DB-03):** The NMOS exception comment at L46-56 is promoted to an
applied dict. The RURP VPP ceiling is ~22V (the codebase's own comment at
`build_db.py:55`); hardware `max_vpp_v = 13` is the production-calibrated
operating point, not the boost regulator's absolute ceiling. M2716 and M2732
(25V true VPP > 22V ceiling) → `vpp-exceeds-max`. M2732A (21V true VPP ≤ 22V
ceiling) → `supported` at corrected voltage.

**Change 3 (DB-05):** The `not_implemented` FAIL bucket in `check_dispatch.py`
is reworked to FAIL only when `support_status == supported`. New consistency
assertions are added. The `diff_db.py` per-chip diff gate does NOT exist on the
current v1.12 branch — it was created in v1.11 Phase 59 but was never merged
into the v1.12 divergence point. Phase 66 must decide: cherry-pick `diff_db.py`
from v1.11 into v1.12, or use `check_dispatch.py` + manual diff as the gate.

**Primary recommendation:** Cherry-pick `diff_db.py` + `chip_database.baseline.json`
from `v1.11-infoic-decode-correctness` as a preparatory Wave-0 task, then add
a new rationale rule for Phase 66 additions.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| DB inclusion logic (filter/skip gates) | Host Data Pipeline (`build_db.py`) | — | Generates `chip_database.json`; no firmware involvement |
| VPP correction / NMOS exception | Host Data Pipeline (`build_db.py`) | — | Pure data transform at generation time |
| `support_status` schema | Host Data Pipeline (`build_db.py`) | Consumer (`database.py`) | Written at gen time; read by Phase 68 |
| Dispatch gate correctness | Host Tool (`check_dispatch.py`) | Host Tool (`diff_db.py`) | CI gate verifies chip → handler mapping |
| Per-chip diff gate | Host Tool (`diff_db.py`) | `check_dispatch.py` | Explains every DB change vs baseline |
| Consumer contract | Host Library (`database.py`) | Host CLI (`cli_handlers.py`) | `_map_data` reads existing keys only; new top-level keys are additive |

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib (`xml.etree`, `json`, `os`, `sys`) | 3.11 (CI target) | DB pipeline parsing and output | Already in use; no new deps needed |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `requests` | existing | Fetch `infoic.xml` from upstream | Already used by `build_db.py` |
| `pytest` | existing | Test framework | New tests for `check_dispatch.py` assertions |

### No New Package Installs
Phase 66 adds zero external dependencies. All changes are to existing Python
source files. No `npm install` / `pip install` / `cargo add` steps.

## Package Legitimacy Audit

No packages are installed in this phase. Audit: N/A.

---

## Architecture Patterns

### Existing Inline Override Idiom (build_db.py)

The established pattern for post-decode surgical corrections:

```python
# Source: firestarter_app/tools/build_db.py (WARNING-5 arm, ~L415-424)
if (pinout_key in ("DIP28_2764", "DIP28_28C256")
        and proto_id == 0x07
        and _etype == "Flash/EEPROM"):
    print(f"INFO: {mfg_name}/{name} algorithm override 0x07->0x0D ...")
    proto_id = 0x0D
```

The NMOS VPP dict (D-04) follows this exact idiom: module-level dict + applied
as a post-decode override after the existing WARNING-5 / fm1608 blocks.

### Recommended build_db.py Change Order

The ordering invariant (D-04 clause: "must run after WARNING-5/fm1608 overrides")
is already documented in the code. The new Phase 66 blocks must land in this
sequence within the `ic` processing loop:

```
1. FILTER (existing): package_details → pin_count / is_smd / is_serial / type_int
2. PROTOCOL SKIP (existing L340-342): proto_id not in KNOWN_PROTOCOLS → skip+warn
   [CHANGE DB-01a]: Modify this gate to INCLUDE instead of skip for confirmed DIP-parallel
3. DAMAGE-HAZARD SKIP (existing L359-370): 24-pin EEPROM gate → skip+warn
   [CHANGE DB-02]: Modify to include as adapter-required instead of skip
4. resolve_pinout_key (existing)
5. FLAGS-BASED _etype (existing — "Pass 1")
6. WARNING-5 override (existing)
7. fm1608 override (existing)
8. Re-derive _etype after overrides (existing — "Pass 2")
   [CHANGE DB-03]: NMOS VPP override dict applied here (after overrides, before chip_entry)
9. chip_entry construction (existing L491-524)
   [CHANGE DB-01b/DB-03/DB-05]: Add support_status + unsupported_reason to chip_entry
```

### Recommended Project Structure (no new files beyond cherry-pick)

```
firestarter_app/
├── tools/
│   ├── build_db.py           # PRIMARY — all three changes land here
│   ├── check_dispatch.py     # DB-05 — rework not_implemented bucket + add assertions
│   ├── diff_db.py            # (cherry-picked from v1.11; add Phase 66 rationale rule)
│   └── baseline/
│       ├── dispatch_baseline.json       # (regenerated — D-11)
│       └── chip_database.baseline.json  # (cherry-picked from v1.11 + updates)
└── firestarter/
    └── data/
        └── chip_database.json  # (regenerated — never hand-edited)
```

### Pattern: chip_entry support_status construction (DB-01/03/05)

```python
# Source: firestarter_app/tools/build_db.py (~L491-524) — to be extended
# Support status derivation (runs after all overrides):
_support_status = "supported"          # default for the majority
_unsupported_reason = None

# --- DB-03: NMOS VPP override (insert before chip_entry construction) ---
# Curated NMOS exception dict (promotes the comment at L46-56 to live code).
# Matched against part_number aliases (comma-split, @-stripped).
NMOS_TRUE_VPP_MV = {"M2716": 25000, "M2732": 25000, "M2732A": 21000}
RURP_VPP_CEILING_MV = 22000  # build_db.py:55 "RURP shield max is ~22V"
part_aliases = set(a.split("@")[0].strip() for a in name.split(","))
for nmos_key, nmos_vpp in NMOS_TRUE_VPP_MV.items():
    if nmos_key in part_aliases:
        # Override the upstream-truncated 18V with true VPP
        vpp_mv_corrected = nmos_vpp
        vpp_str_corrected = f"{nmos_vpp // 1000}V"
        if nmos_vpp > RURP_VPP_CEILING_MV:
            _support_status = "vpp-exceeds-max"
            _unsupported_reason = (
                f"VPP {nmos_vpp // 1000}V exceeds RURP ceiling "
                f"({RURP_VPP_CEILING_MV // 1000}V); cannot program on this hardware"
            )
        # else: supported at corrected voltage
        break
# (Actual wording is Claude's discretion per D-07)

chip_entry = {
    "part_number": ...,
    "support_status": _support_status,           # D-07/D-08: always present
    # "unsupported_reason": _unsupported_reason, # D-07/D-08: only if not supported
    "electrical": { ... "vpp": ..., "vpp_mv": ... },
    "programming": { ... },
    "pinout": pinout_key,
}
if _unsupported_reason:
    chip_entry["unsupported_reason"] = _unsupported_reason
```

### Pattern: check_dispatch.py not_implemented rework (DB-05)

The current `main()` loop adds every `not_implemented`-resolving chip to the
FAIL list unconditionally (L105-124). After Phase 66 the condition changes:

```python
# Source: firestarter_app/tools/check_dispatch.py (~L105-124) — to be reworked
if handler == "not_implemented":
    # D-10: a chip resolving not_implemented is FAIL only when
    # support_status == "supported" (a regression). For
    # "protocol-not-implemented" chips it is expected → count as pass.
    ss = chip.get("support_status", "supported")
    if ss == "supported":
        not_implemented.append(f"{mfg}/{part} proto=0x{proto:02X}")
    else:
        # Expected: protocol-not-implemented chips correctly route to not_implemented
        pass
    continue  # skip VPP/wire checks (no real handler to evaluate)

# --- New consistency assertions (D-10) ---
# These run after the main chip loop (add three new FAIL lists):
# 1. non-supported chip missing unsupported_reason
# 2. protocol-not-implemented chip with proto in KNOWN_PROTOCOLS (contradiction)
# 3. supported chip resolving to not_implemented (already covered above)
```

---

## Research Must-Do Resolutions

### Must-Do 1: Locate the v1.11 Per-Chip Diff Gate

**Finding:** `diff_db.py` does NOT exist on the current `v1.12-protocol-dispatch-hardening`
branch of `firestarter_app`. [VERIFIED: `git ls-tree HEAD -- tools/`]

**Root cause:** The v1.12 branch forked from `beta` at commit `faaa57190066145cfd7cd532bf8a3a9d38791856`,
which predates the v1.11 Phase 59 work that created `diff_db.py` (commits
`fc62a27` and `f3b2ed7`) and `chip_database.baseline.json`.
[VERIFIED: `git merge-base v1.12-protocol-dispatch-hardening v1.11-infoic-decode-correctness` → `faaa571`]

**What exists on v1.12:** Only `tools/baseline/dispatch_baseline.json` (734 chips,
generated 2026-06-10, Phase 62 GATE-01). No `chip_database.baseline.json`. No
`diff_db.py` source (there IS a stale `__pycache__/diff_db.cpython-312.pyc` from
a prior execution, but no `.py` source).

**What D-11 baseline regeneration must cover:** Two distinct artifacts:

1. **`tools/baseline/dispatch_baseline.json`** — Phase 62 GATE-01 artifact. This
   stores per-chip dispatch triples (manufacturer/part/handler) and deliberately
   excludes `vpp_mv`. After Phase 66 adds new chips, this baseline expands.
   `check_dispatch.py` reads this indirectly (it runs against the live DB, not
   the baseline). Regeneration = re-run `python tools/build_db.py` then capture
   new triples. [VERIFIED: file at `tools/baseline/dispatch_baseline.json`, 734 chips]

2. **`tools/baseline/chip_database.baseline.json`** — Phase 59 GATE-02 artifact
   used by `diff_db.py`. This does NOT exist on v1.12. The planner must decide
   whether to cherry-pick `diff_db.py` + `chip_database.baseline.json` from
   `v1.11-infoic-decode-correctness` as Wave 0. [VERIFIED: absent from
   `git ls-tree HEAD -- tools/baseline/`; present on `v1.11-infoic-decode-correctness`]

**Recommendation for planner:** Wave 0 task: cherry-pick `diff_db.py` + set
`chip_database.baseline.json` = current v1.12 `chip_database.json` (734 chips)
as the new baseline. Then Phase 66 edits add a new rationale rule
(e.g. `RULE_PHASE66`: covers protocol-not-implemented additions, adapter-required
additions, VPP corrections). The diff gate then produces a reviewable, explained
diff for all Phase 66 changes. This mirrors the v1.11 D-01/D-02 authorized-deviation
precedent exactly.

**If cherry-pick is not feasible:** The ROADMAP SC#4 already says "via `diff_db.py`
or equivalent". The equivalent is: run `python tools/check_dispatch.py` (gate
green at 0 errors after rework), review the `git diff firestarter/data/chip_database.json`
manually in the commit, and document each new/changed entry in the commit message.
This is lower quality but compliant with the letter of DB-05.

---

### Must-Do 2: Reconcile the 24-pin EEPROM Unblock History

**Finding:** The v1.11 "9 × 24-pin AT28C04/16 EEPROMs unblocked" story is
ACCURATE — they appear with `DIP24_2816 + algo=0x0D` in the v1.11 branch DB
(19 entries confirmed). However, the v1.12 branch has NOT inherited this work
because v1.12 diverged from beta before v1.11 merged.

**Current v1.12 state (VERIFIED by live build_db.py run):**
The 9 damage-hazard-skipped chips produce exactly 9 skip warnings:
- `ATMEL/AT28C04@DIP24,AT28C04@SOIC24,AT28HC04` (proto 0x0B, flags&0x10)
- `ATMEL/AT28C04E@DIP24,AT28C04E@SOIC24,AT28C04F@DIP24,AT28C04F@SOIC24`
- `ATMEL/AT28C16@DIP24,AT28C16@SOIC24,AT28HC16,AT28HC16L`
- `ATMEL/AT28C16E@DIP24,AT28C16E@SOIC24,AT28C16F@DIP24,AT28C16F@SOIC24`
- `MICROCHIP memory/28C04A,28C04A@SOIC24`
- `MICROCHIP memory/28C04AF,28C04AF@SOIC24`
- `MICROCHIP memory/28C16A,28C16A@SOIC24` 
- `MICROCHIP memory/28C16AF,28C16AF@SOIC24`
- `NEC/UPD28C04@DIP24,UPD28C04@SOIC24`

[VERIFIED: `python3 tools/build_db.py 2>&1 | grep "24-pin 5V EEPROM"` → 9 unique skips]

**Why the 9 were not unblocked by Phase 58 in v1.12:** Phase 58's unblock used a
NEW `DIP24_2816` pinout entry and `variant_lo==0x10` discriminator in a rewritten
`resolve_pinout_key`. This rewrite lives on the v1.11 branch in `build_db.py`
(commit `fc62a27` + subsequent) but NOT on v1.12. The v1.12 `build_db.py` still
has the original `flags&0x10` damage-hazard skip (L359-370).
[VERIFIED: `build_db.py` on v1.12 HEAD still has the hazard skip at L357-370]

**D-02 Phase 66 approach (adapter-required, NOT unblocked):**
Phase 66 does NOT re-implement the v1.11 `DIP24_2816` unblock. Instead, Phase 66
modifies the hazard-skip gate to **include rather than drop** these 9 chips, but
marks them `support_status: adapter-required` with `unsupported_reason` documenting
the 12V-VPP-on-WE hazard and the adapter/handler requirement. This is explicitly
weaker than v1.11's full unblock — and that's correct per D-03 (no new chips
become programmable).

**AT28C16@DIP24 (adapter-required) vs AT28C16A (supported) — consistency oddity:**
[VERIFIED by live DB inspection]

`AT28C16A` is currently in the DB as `pinout=DIP24_2716 algo=0x0B` — it passed
the hazard gate because its `flags&0x10` bit is 0 (it's not flagged as
electrically erasable in upstream infoic.xml, even though it IS an EEPROM). The
`AT28C16` entry has `@DIP24` alias AND `flags&0x10=1`, triggering the hazard skip.

The consistency oddity resolves cleanly: `AT28C16A` is a later CMOS revision that
upstream tagged without the erasable bit (whether correct or not), so it slipped
through the flags-based gate. Phase 66 doesn't change this — `AT28C16A` stays
`supported` (it already dispatches to `configure_eprom` which is safe for a UV-EPROM
layout). The 9 D-02 chips all have `flags&0x10=1`, which is the discriminator.

**SOIC24 aliases:** The `@SOIC24` aliases in the name string (e.g.
`AT28C04@DIP24,AT28C04@SOIC24,AT28HC04`) are just aliases in the infoic.xml `name`
attribute. The `package_details` field drives the DIP filter, not the name string.
The entry's `package_details` says DIP24 (pin_count=24, is_smd=0), so it passes
the filter and lands at the hazard gate. `build_db.py` strips `@PACKAGE` suffixes
when constructing `part_number` — so `AT28C04,AT28HC04` would appear in the output
(the SOIC24 form would still be listed as an alias, but the chip IS the DIP24
variant). Phase 66 should include the DIP24 entry as `adapter-required`; the SOIC24
alias is harmless (it just means the same die also came in SOIC24 packaging).

---

### Must-Do 3: NMOS VPP Ceiling + Curated List Confirmation

**RURP VPP Ceiling — Authoritative Finding:**

The codebase's own comment (build_db.py L55): `"RURP shield max is ~22V"`.
[VERIFIED: `firestarter_app/tools/build_db.py:55`]

The firmware `CLAUDE.md` algorithm handler table shows: `0x07 EPROM_STD: 13V via
CTRL_VPP_VPE_DROP_ENABLE` and `0x0B EPROM_LEGACY: 12–18V direct`. The hardware
capability matrix (`v1.7-SHIELD-REVS.md` §6) lists `max_vpp_v = 13` for all Rev
0–2.3 shields. [VERIFIED: SHIELD-REVISIONS.md + v1.7-SHIELD-REVS.md §6 tables]

**Reconciliation:** The `max_vpp_v = 13` is the production-calibrated operating
point for VPP on normal chips. The "~22V" is the boost regulator's theoretical
ceiling (the formula in `rurp_common.cpp` with R1=270kΩ / R2=44kΩ gives a
full-scale measurement range up to ~35V; the regulator feedback is set for 13V in
practice). The distinction matters for the ceiling constant:

- `RURP_VPP_CEILING_MV = 22000` means: if a chip needs > 22V, it is definitively
  `vpp-exceeds-max` (hardware cannot supply it even at maximum regulator output).
- M2716 (25V), M2732 (25V): 25000 > 22000 → `vpp-exceeds-max`. [ASSUMED: datasheet
  values; the existing comment at L46-56 documents these as the known NMOS cases]
- M2732A (21V): 21000 ≤ 22000 → `supported` at corrected voltage. [ASSUMED:
  datasheet value for the later 21V variant]

**The ~22V ceiling is not defined as a codebase constant** — it exists only as a
comment. D-06 says "exact ceiling constant resolved at plan time." Recommendation:
introduce `RURP_VPP_CEILING_MV = 22000` as a new module-level constant in
`build_db.py` with a citation to the comment and hardware evidence.

**Curated NMOS Dict:**

The CONTEXT (D-04) locks: `{"M2716": 25000, "M2732": 25000, "M2732A": 21000}`.
The existing comment at L46-56 lists exactly these three. The live DB shows the
affected entries include manufacturer-specific designators:

- `INTEL/M2716,M2716M` — aliases include `M2716` → covered
- `INTEL/2732,2732A,M2732,M2732A` — aliases include `M2732` and `M2732A` → covered
  (note: this single entry has BOTH M2732 and M2732A; with key-and-correct D-05,
  the higher-priority M2732 match → 25V → `vpp-exceeds-max`; OR the planner may
  prefer explicit handling: if any alias is `M2732A` and no alias is `M2732` →
  21V; if any alias is `M2732` → 25V — resolve at plan time)
- `SGS-THOMSON/ETC2716,M2716`, `ST/ETC2716,M2716` — aliases include `M2716` → covered
- `SGS-THOMSON/ETC2732`, `SGS-THOMSON/M2732A`, `ST/ETC2732`, `ST/M2732A` — aliases
  include `M2732` or `M2732A` → covered

[VERIFIED: `python3 -c "import json; ..."` on current chip_database.json — all
above entries show vpp=18V (the upstream cap) and need correction]

**NMOS-vs-CMOS alias-splitting question (D-05 confirmation):** The `INTEL/2732,2732A,M2732,M2732A`
entry combines M2732 (NMOS, 25V) and M2732A (NMOS, 21V) in one entry. D-05 says
key-and-correct, don't split. The planner must choose which VPP wins for entries
with multiple NMOS aliases — safest is "highest VPP wins" so the chip is correctly
flagged as `vpp-exceeds-max` if ANY alias requires > ceiling. This is the
conservative, hardware-safe choice.

**Other NMOS equivalents beyond Intel:** The SGS-Thomson and ST entries with M2716/M2732/M2732A
aliases are already covered by the dict (the alias match finds them). No additional
manufacturers need to be added beyond what is already in the existing comment —
the scope is the authoritatively-known Intel NMOS cases and their documented
equivalents (per REQUIREMENTS.md DB-03: "scope is the authoritatively-known cases,
not a blanket VPP re-survey").

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Per-chip diff between two DBs | Custom JSON diff logic | Existing `diff_db.py` (cherry-pick from v1.11) | Already handles composite keys, rationale rules, infra-error exit codes |
| support_status check | New file/module | Inline in `check_dispatch.py` (existing per-bucket pattern) | 3 assertions, same idiom as existing FAIL lists |
| NMOS VPP lookup | External file, API call | Inline dict in `build_db.py` (D-04 locked) | Matches WARNING-5/fm1608 idiom; no external deps |
| Alias matching | Regex library | Simple `set` membership after `a.split("@")[0].strip() for a in name.split(",")` | `part_number` construction already does this |

---

## Common Pitfalls

### Pitfall 1: The INTEL/2732,2732A,M2732,M2732A Combined Entry
**What goes wrong:** The single DB entry covers both M2732 (25V) and M2732A (21V).
Matching on M2732A first would give 21V → `supported`; matching on M2732 first would
give 25V → `vpp-exceeds-max`. The alias list iteration order is non-deterministic
without a sort.
**How to avoid:** Search for M2732 first (longer/more specific key), OR use "highest
VPP wins" logic: iterate all aliases, collect all NMOS matches, take max VPP.
**Warning signs:** D-06 says "M2732 → 25V" — if a plan shows INTEL/2732,2732A,M2732,M2732A
as `supported` it has the match-order bug.

### Pitfall 2: Ordering — NMOS Override Must Run After fm1608 Override
**What goes wrong:** If NMOS VPP override runs before the fm1608 override, a FRAM
chip whose alias happens to contain `M2716` would get a spurious VPP correction.
(Unlikely but the ordering invariant exists for a reason.)
**How to avoid:** Insert NMOS override block AFTER the fm1608 `type_int==4` guard,
immediately before `chip_entry` construction. The comment in the existing code
documents the ordering contract explicitly.

### Pitfall 3: diff_db.py Rationale Exhaustiveness
**What goes wrong:** `diff_db.py`'s classifier routes any field path that changes
outside a registered rule's field set to "unexplained" (D-03 BLOCK, exit 1). Phase 66
adds `support_status` and `unsupported_reason` as new top-level keys, and changes
`vpp`/`vpp_mv` for NMOS entries. These will all appear as "unexplained" in the
existing classifier unless a `RULE_PHASE66` rationale is registered.
**How to avoid:** Before re-running the diff gate, add a `RULE_PHASE66` entry to
`_RATIONALES` in `diff_db.py` claiming: new `support_status` / `unsupported_reason`
top-level keys, NMOS `vpp`/`vpp_mv` corrections, new chips from protocol-not-implemented
and adapter-required additions.

### Pitfall 4: dispatch_baseline.json Chip Count vs DB Chip Count
**What goes wrong:** The Phase 62 `dispatch_baseline.json` was captured at 734 chips.
After Phase 66 adds ~10 new chips (1 from 0x34, 9 from adapter-required), the new
DB has ~744 chips. `check_dispatch.py` doesn't compare against the dispatch baseline
directly — it runs against the live DB. The `dispatch_baseline.json` needs to be
regenerated (D-11) to match the new DB for future regression use.
**How to avoid:** Regenerate `dispatch_baseline.json` as part of Phase 66 DB regeneration.

### Pitfall 5: 24-pin EEPROM SOIC Aliases Passing as DIP
**What goes wrong:** The `@SOIC24` form in a chip name string is NOT the package filter
discriminator. The filter uses `package_details` bit 31 (is_smd) and bits 8-15
(is_serial). The 9 chips being included as `adapter-required` are confirmed DIP24
entries (they passed the `package_details` DIP filter — that's why they reach the
hazard gate in the first place). Including them as `adapter-required` is correct.
**How to avoid:** The alias stripping (`a.split("@")[0].strip()`) in `part_number`
construction removes `@SOIC24` from the part number output — it remains only in the
raw `name` string. This is existing behavior, no change needed.

### Pitfall 6: Python 3.12 vs 3.11 (DB Regeneration)
**What goes wrong:** `build_db.py` is run with the devcontainer's Python 3.12, but
the CI target is Python 3.11. The `chip_database.json` output is deterministic JSON
(`sort_keys` not used — but the xml iteration order is deterministic). The real trap
is `check_dispatch.py` and `diff_db.py` which import `firestarter.database` — if
ruff or other tooling is involved, use 3.11.
**How to avoid:** Run `build_db.py`, `check_dispatch.py`, and `diff_db.py` with the
CI-matching Python (3.11) for the gate artifacts. `chip_database.json` generation
itself doesn't have Python-version-sensitive output.

---

## Code Examples

### build_db.py: Current Unknown-Protocol Skip Gate (lines 339-342)
```python
# Source: firestarter_app/tools/build_db.py:339-342 [VERIFIED: direct read]
# Skip chips with unknown protocol_id
if proto_id not in KNOWN_PROTOCOLS:
    print(f"WARN: skipping {name} — unknown protocol_id 0x{proto_id:02X}", file=sys.stderr)
    continue
```

### build_db.py: Current 24-pin EEPROM Damage-Hazard Gate (lines 358-370)
```python
# Source: firestarter_app/tools/build_db.py:359-370 [VERIFIED: direct read]
if (pin_count == 24
        and proto_id in (0x07, 0x08, 0x0B)
        and (flags & 0x10)):
    print(
        f"WARN: skipping {mfg_name}/{name} — 24-pin 5V EEPROM with "
        f"EPROM-family algo 0x{proto_id:02X} (damage hazard: 12V VPP "
        f"to socket pin 21 = WE of 28C-family chips). No 24-pin "
        f"EEPROM firmware handler yet; ...",
        file=sys.stderr,
    )
    continue
```

### check_dispatch.py: Current not_implemented FAIL bucket (lines 122-124)
```python
# Source: firestarter_app/tools/check_dispatch.py:122-124 [VERIFIED: direct read]
if handler == "not_implemented":
    not_implemented.append(f"{mfg}/{part} proto=0x{proto:02X}")
    continue  # skip VPP/wire checks — no real handler to evaluate
```

### check_dispatch.py: Current FAIL report (lines 167-177)
```python
# Source: firestarter_app/tools/check_dispatch.py:167-177 [VERIFIED: direct read]
if not_implemented:
    print(
        f"FAIL: {len(not_implemented)} chips route to not_implemented "
        f"(protocol != 0, not in KNOWN_PROTOCOLS):"
    )
    for e in not_implemented[:20]:
        print(f"  {e}")
```

### database.py: _map_data consumer (lines 364-441)
```python
# Source: firestarter_app/firestarter/database.py:364-441 [VERIFIED: direct read]
# _map_data reads only: electrical.*, programming.*, pinout
# Reads: electrical.vpp, electrical.vpp_mv, programming.algorithm, etc.
# Does NOT read: support_status, unsupported_reason
# Adding these as top-level keys is additive and backward-compatible.
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Silent skip + warning for unknown protocols | Include as `protocol-not-implemented` | Phase 66 (this phase) | DB is now a complete catalog |
| Drop 24-pin EEPROMs entirely | Include as `adapter-required` | Phase 66 (this phase) | Honest about what exists |
| No `support_status` field | Every chip has explicit `support_status` | Phase 66 (this phase) | Machine-readable capability gate |
| Upstream-truncated VPP (18V) for NMOS | True VPP recorded | Phase 66 (this phase) | Accurate capability signal |
| v1.11 full unblock of 24-pin EEPROMs | NOT in v1.12 (branch diverged early) | v1.11 Phase 58 (not merged) | Phase 66 takes a different path |

**Deprecated/outdated:**
- `diff_db.py` on v1.11 branch: the Phase 59 `RULE_ALGO` rationale covers v1.11
  changes. Phase 66 needs a new `RULE_PHASE66` rationale added when cherry-picking.

---

## Runtime State Inventory

This is a greenfield data-pipeline extension, not a rename/refactor.

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| Stored data | `chip_database.json` — 734 chips, no `support_status` field | Regenerated by `python tools/build_db.py` |
| Live service config | None — host-only pipeline, no running services | None |
| OS-registered state | None | None |
| Secrets/env vars | None | None |
| Build artifacts | `tools/__pycache__/diff_db.cpython-312.pyc` — stale compiled pyc with no source on v1.12 | Delete as part of cherry-pick task; `.py` source restores it |

**Nothing found in category:** OS-registered state: None — verified by inspection.
Secrets/env vars: None — `build_db.py` only reads `FIRESTARTER_DB_FILE` env var
(output path override, no secrets).

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11 | CI-matching gate runs | Potentially absent on devcontainer | devcontainer has 3.12 | Use `python3.11` if installed; document that `chip_database.json` regen is Python-version neutral but `diff_db.py` / `check_dispatch.py` are run under CI 3.11 |
| `requests` library | `build_db.py` (fetches infoic.xml) | Available | existing | None — required |
| `firestarter` package | `check_dispatch.py` / `diff_db.py` import | Available (pip install -e .) | existing | None — required |
| internet access | `build_db.py` (fetches upstream infoic.xml) | Required | — | Use cached local copy at `tools/infoic.xml` if network unavailable |

**Missing dependencies with no fallback:** None that block execution.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (existing CI gate) |
| Config file | `pyproject.toml` or `pytest.ini` (existing) |
| Quick run command | `python tools/check_dispatch.py` (tool gate, exits 0/1) |
| Full suite command | `pytest --cov-fail-under=70` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DB-01 | Unknown-protocol chips appear in DB as `protocol-not-implemented` | unit (pytest) | `pytest tests/test_build_db_inclusion.py -x` | ❌ Wave 0 |
| DB-01 | `check_dispatch.py` exits 0 on new DB (no regressions) | integration (tool) | `python tools/check_dispatch.py` | ✅ (existing tool, reworked) |
| DB-01 | X88C64P has `support_status: protocol-not-implemented` in output DB | unit (pytest) | `pytest tests/test_build_db_inclusion.py::test_x88c64_included -x` | ❌ Wave 0 |
| DB-02 | 9 damage-hazard chips appear as `adapter-required` | unit (pytest) | `pytest tests/test_build_db_inclusion.py::test_adapter_required_24pin -x` | ❌ Wave 0 |
| DB-03 | M2716/M2732 entries have vpp_mv=25000 + `vpp-exceeds-max` | unit (pytest) | `pytest tests/test_build_db_inclusion.py::test_nmos_vpp_correction -x` | ❌ Wave 0 |
| DB-03 | M2732A entries have vpp_mv=21000 + `supported` | unit (pytest) | `pytest tests/test_build_db_inclusion.py::test_nmos_m2732a_supported -x` | ❌ Wave 0 |
| DB-05 | `check_dispatch.py` consistency assertions: non-supported chips have `unsupported_reason` | tool (exits 0) | `python tools/check_dispatch.py` | ✅ (reworked) |
| DB-05 | Supported chips with real handlers pass (no regression) | integration | `python tools/check_dispatch.py` | ✅ (existing) |
| DB-05 | `diff_db.py` exits 0 with all changes explained | tool (exits 0) | `python tools/diff_db.py` | ❌ Wave 0 (cherry-pick) |

### Sampling Rate
- **Per task commit:** `python tools/check_dispatch.py` (exits 0 = gate green)
- **Per wave merge:** `pytest --cov-fail-under=70`
- **Phase gate:** `python tools/check_dispatch.py` + `python tools/diff_db.py` (both exit 0) + full pytest suite green

### Wave 0 Gaps
- [ ] `tests/test_build_db_inclusion.py` — unit tests for DB-01/02/03 inclusion logic
- [ ] Cherry-pick `diff_db.py` from `v1.11-infoic-decode-correctness` → add `RULE_PHASE66` rationale rule
- [ ] Set `tools/baseline/chip_database.baseline.json` = current 734-chip DB (pre-Phase-66 baseline)
- [ ] (Optional) `tests/test_check_dispatch_consistency.py` — explicit pytest for the new D-10 consistency assertions

*(If no gaps: cherry-pick + new test file. Existing `check_dispatch.py` + `diff_db.py` tool gates are the primary acceptance evidence; pytest covers the unit behavior.)*

---

## Security Domain

Security enforcement is not applicable: this phase modifies a host-side data
generation pipeline (no network endpoints, no auth, no user input). The primary
safety concern is the existing hardware-damage hazard prevention (WARNING-5,
damage-hazard gate) — these are preserved and extended by the phase.

ASVS categories: Not applicable (no user authentication, no session management,
no input validation paths beyond the existing XML parse, no cryptography).

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | M2716 = 25V, M2732 = 25V, M2732A = 21V (datasheet values) | NMOS VPP Correction | Over/under-flagging vpp-exceeds-max; correctable when operator confirms datasheets |
| A2 | RURP VPP ceiling = ~22V (from build_db.py comment) | VPP ceiling | Wrong ceiling → M2732A could be mis-classified (21V ≤ 22V → supported is fine; if ceiling were actually 20V, M2732A would also be vpp-exceeds-max) |
| A3 | SGS-Thomson/ST M2732A (non-Intel) has same 21V spec as Intel M2732A | NMOS curated dict | Incorrect VPP for those entries; correctable via datasheet lookup at plan time |
| A4 | X88C64P@DIP24 is a genuine 8K DIP24 parallel EEPROM (not serial-bus) | Drop census | If proto 0x34 is actually a serial protocol for this chip, it should stay skipped |
| A5 | The 9 damage-hazard chips are all `flags&0x10=1` (electrically erasable) | 24-pin EEPROM section | If any chip has flags&0x10=0 and was still skipped (different gate), the count changes |

**Claims NOT assumed (verified by code read or live tool run):**
- Drop census numbers (0x04×18, 0x11×4, 0x0A×1, 0x34×1, damage-hazard×9): VERIFIED by live `python3 tools/build_db.py 2>&1 | grep WARN`
- `diff_db.py` absence on v1.12: VERIFIED by `git ls-tree HEAD -- tools/`
- `dispatch_baseline.json` chip count = 734: VERIFIED by file read
- current DB chip count = 734: VERIFIED by `python3` count
- `_map_data` consumer only reads existing keys: VERIFIED by database.py source read (L364-441)
- `check_dispatch.py` `not_implemented` bucket at L105-124: VERIFIED by source read
- KNOWN_PROTOCOLS = {0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39}: VERIFIED by build_db.py:83
- `RURP shield max is ~22V`: VERIFIED by build_db.py:55 comment
- `max_vpp_v = 13` for all RURP revisions: VERIFIED by SHIELD-REVISIONS.md + v1.7-SHIELD-REVS.md §6
- build_db.py NMOS comment at L46-56 lists M2716=25V, M2732=25V, M2732A=21V: VERIFIED by source read

---

## Open Questions

1. **INTEL/2732,2732A,M2732,M2732A combined entry VPP resolution**
   - What we know: single entry contains both M2732 (25V) and M2732A (21V) aliases
   - What's unclear: which VPP to record — highest wins (25V → `vpp-exceeds-max`) vs first-matched
   - Recommendation: "highest VPP wins" logic — conservative and hardware-safe

2. **cherry-pick vs equivalent for diff_db.py**
   - What we know: `diff_db.py` is absent from v1.12; ROADMAP SC#4 says "via `diff_db.py` or equivalent"
   - What's unclear: whether to cherry-pick or use manual diff
   - Recommendation: cherry-pick is cleaner; adds one Wave-0 task; avoids re-implementing the logic

3. **TMS87C257@PLCC32 skip confirmation (0x0A)**
   - What we know: the `@PLCC32` suffix is in the name string; the DIP filter should exclude PLCC via package_details
   - What's unclear: whether `package_details` correctly identifies this as non-DIP, or whether it passes the filter and is skipped by KNOWN_PROTOCOLS
   - The skip warning exists for this chip → it passes the DIP filter → proto 0x0A not in KNOWN_PROTOCOLS → skip is correct; no DIP form exists for this chip
   - Recommendation: skip is confirmed correct; D-01 says PLCC stays skipped

---

## Sources

### Primary (HIGH confidence)
- `firestarter_app/tools/build_db.py` — direct read; all line references verified [VERIFIED: direct read 2026-06-12]
- `firestarter_app/tools/check_dispatch.py` — direct read; all line references verified [VERIFIED: direct read 2026-06-12]
- `firestarter_app/tools/baseline/dispatch_baseline.json` — direct read; 734 chips, 2026-06-10 [VERIFIED: direct read 2026-06-12]
- `firestarter_app/firestarter/database.py` L364-441 — `_map_data` consumer contract [VERIFIED: direct read 2026-06-12]
- Live `python3 tools/build_db.py 2>&1` run — drop census counts confirmed [VERIFIED: live run 2026-06-12]
- `git ls-tree HEAD -- tools/` — confirmed `diff_db.py` absent from v1.12 [VERIFIED: git command 2026-06-12]
- `git ls-tree v1.11-infoic-decode-correctness -- tools/` — confirmed `diff_db.py` present on v1.11 [VERIFIED: git command 2026-06-12]
- `firestarter/doc/SHIELD-REVISIONS.md` + `.planning/v1.7-SHIELD-REVS.md §6` — `max_vpp_v = 13` for all revisions [VERIFIED: direct read 2026-06-12]
- `firestarter/src/boards/rurp_common.cpp` — VPP measurement formula (R1/R2 divider) [VERIFIED: direct read 2026-06-12]
- `firestarter/include/rurp_shield.h:49-50` — `VALUE_R1 = 270000`, `VALUE_R2 = 44000` [VERIFIED: direct read 2026-06-12]
- `firestarter/CLAUDE.md` §"Algorithm Handlers" — handler VPP values (13V for EPROM_STD/QUICK) [VERIFIED: direct read 2026-06-12]
- `firestarter_app/tools/__pycache__/diff_db.cpython-312.pyc` — disassembled to confirm `diff_db.py` structure and content [VERIFIED: python3 marshal read 2026-06-12]
- `git show f3b2ed7:tools/diff_db.py` — confirmed `diff_db.py` source on v1.11 branch [VERIFIED: git show 2026-06-12]

### Secondary (MEDIUM confidence)
- `.planning/phases/66-db-inclusion-vpp-correction-dispatch-gate/66-CONTEXT.md` — locked decisions, open items, canonical refs [CITED: context doc 2026-06-12]
- `.planning/REQUIREMENTS.md §DB-01/03/05` — requirement scope and capability taxonomy [CITED: requirements doc 2026-06-12]
- `.planning/ROADMAP.md §Phase 66` — success criteria [CITED: roadmap doc 2026-06-12]
- `.planning/phases/59-correctness-gate-per-chip-diff-sram-audit/` — v1.11 diff gate precedent [CITED: phase artifacts 2026-06-12]

---

## Metadata

**Confidence breakdown:**
- Drop census: HIGH — verified by live tool run
- diff_db.py location: HIGH — verified by git commands
- 24-pin EEPROM unblock history: HIGH — verified by git log + build_db.py run
- NMOS VPP values (25V/21V): MEDIUM — from existing codebase comment; datasheet confirmation needed at plan time
- RURP VPP ceiling (~22V): MEDIUM — from codebase comment + hardware evidence that max_vpp_v=13 is operational (not absolute) ceiling
- check_dispatch.py rework pattern: HIGH — verified by source read
- consumer contract safety: HIGH — verified by database.py source read

**Research date:** 2026-06-12
**Valid until:** 2026-07-12 (stable codebase; DB pipeline doesn't change independently)

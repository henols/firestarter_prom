# 148-DB-DIFF.md — Phase 148 D-12 review artifact

Per D-12 (148-CONTEXT.md), this is the single reviewable document carrying the phase's `diff_db.py`
run output, the mover list, the D-03 justification, and the explicit non-claim about the untouched
`vcc=5500` group. Later plans in this phase append `## After`, the 56-chip mover list, the
justification, and the non-claim sections below the `## Before` section captured here.

## Before

Measured this session from `/workspaces/firestarter_app`, HEAD `9701209` (pre-Phase-148 content for
`tools/build_db.py`, `firestarter/data/chip_database.json`, `firestarter/database.py`) — same tree
Plan 01 Task 1 captured the wire-dict golden against.

### `python3 tools/diff_db.py ; echo EXIT=$?`

```
========================================================================
GATE-02 Per-chip Diff Report
  Baseline: /workspaces/firestarter_app/tools/baseline/chip_database.baseline.json  (746 chips, 746 diffed)
  Current:  /workspaces/firestarter_app/tools/../firestarter/data/chip_database.json  (746 chips, 746 diffed)
========================================================================

--- CHANGED chips (744 total) ---

[PGSZ_PAGE_SIZE] (2 chips)
  Phase 94 PGSZ-01 / CR-01 — datasheet-sourced per-chip page_size field added.
  Affected part_numbers (2):
    W29C020,W29C020C,W29C022
    W29C040,W29C042

[PROV01_PROTECT_METADATA] (742 chips)
  Phase 136.1 PROV-01 — flags bit 14/15 + raw page_size decode added to the
  programming block: protect_off_before, protect_on_after, infoic_page_size_raw.
  Metadata only — no algorithm / pinout / vpp / electrical.type delta; the
  84/43/41 SDP ALLOW/REFUSE partition (tests/test_sdp_db_invariant.py) is
  unchanged.
  Affected part_numbers (742): [full list measured, omitted here for length —
  reproducible verbatim via the command above]

--- COMPOUND changes (2) — algo+other deltas ---

  W29C020,W29C020C,W29C022 [PGSZ_PAGE_SIZE] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  W29C040,W29C042 [PGSZ_PAGE_SIZE] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after

--- NEW chips (0) — expected Rule 1 unblock (DIP24_2816 + algo=0x0D) ---

--- MISSING chips (0) ---

PASS: all 744 changed chips explained (0 new chips confirmed; 0 chips removed from baseline)
EXIT=0
```

**Why 744 is the correct baseline, not "zero changed chips" (RESEARCH F-2).**
`tools/baseline/chip_database.baseline.json` predates Phase 136.1 — it carries no
`protect_off_before` / `protect_on_after` / `infoic_page_size_raw` and no `page_size`, so 744 of 746
chips already diff against it today, and every one of those 744 is already explained by a named,
cited rule (`PGSZ_PAGE_SIZE`, `PROV01_PROTECT_METADATA`). The baseline is **NOT re-pinned** by this
phase (**D-11**) — `tools/baseline/chip_database.baseline.json` stays as-is, and `diff_db.py`'s
comparator is what normalizes the migration's 56 movers into their own new bucket, not a baseline
regeneration. A criterion phrased "`diff_db.py` reports zero changed chips" would therefore be a
false RED: it is unachievable against this un-re-pinned baseline and was never the correct target —
the achievable, equally strong form is that the changed-chip total and every existing bucket count
stay unchanged after migration, with the 56 movers appearing as their own new, separately-named
bucket.

### `python3 tools/check_dispatch.py ; echo EXIT=$?`

```
PASS: all 746 chips scanned; 736 supported; 10 chips confirmed non-dispatchable (D-12: host guard
covers non-supported chips with real handlers; non-handler outcomes also safe); 0
non_supported_dispatchable (gate GREEN because chip_resolver.resolve_chip refuses, not because sim
pretends mem_type=None); 0 dispatch regressions; 0 consistency violations
EXIT=0
```

Measured summary: 746 scanned, 736 supported, 0 violations (0 dispatch regressions + 0 consistency
violations, the tool's own two named violation counters), `EXIT=0`.

### `python3 -m pytest tests/test_chip_database_field_inventory.py -o addopts="" -q`

```
........                                                                 [100%]
8 passed in 0.09s
```

### `firestarter info AT28C256` (with `FIRESTARTER_CONFIG_DIR` pointed at an empty scratch dir)

```
Eprom Info
Name:               AT28C256,AT28C256E,AT28C256F,AT28HC256,AT28HC256E,AT28HC256F,AT28HC256L
Manufacturer:       ATMEL
Number of pins:     28
Memory size         0x8000
Type:               EEPROM
Can be erased:      yes (electrically erasable)
VCC:                4.0v
VPP:                12.0v
Chip ID:            -
...
Protocol: EEPROM - 5V parallel, SDP + DQ7 poll (ID: 0x0D)
Flags: 0x00000010
  - Electrically erasable
```

`VCC:` reads `4.0v` and `VPP:` reads `12.0v` — the pre-change AT28C256 decode this phase's later
plans will correct.

## Wire equivalence (D-14 / D-06)

Measured this session from `/workspaces/firestarter_app`, on the `gsd/v1.32-at28c-write-path-root-cause-report-provenance`
branch, after Plan 04 Task 1 (`database.py`'s coercion layer deleted, `format_mv` added, direct
indexing on `vcc_mv`/`vpp_mv`/`pulse_duration_us`) and Task 2 (all three display call sites moved
onto `format_mv`) both landed.

### `python3 -m pytest tests/test_wire_dict_equivalence.py -o addopts="" -q`

```
.....                                                                    [100%]
5 passed in 0.55s
```

All 5 tests pass, including the byte-identity leg: the live 746-chip
`EpromDatabase(skip_local_override=True) -> get_eprom -> convert_to_programmer` capture is
**byte-identical** to the Plan 01 pre-change golden (`tests/golden/wire_dict_baseline.json`,
SHA-256 `027a43a0dcef1085afa6a35d2500bd35556140dde4b838dfcd65bfae8cac7dab`). The golden itself was
**not** re-pinned or regenerated by this plan.

### `git diff --stat tests/__snapshots__/test_characterization.ambr`

```
(empty output)
```

The pinned characterization snapshot is **byte-unchanged** — `git diff --quiet` on it succeeds.

### `python3 tools/check_dispatch.py ; echo EXIT=$?`

```
PASS: all 746 chips scanned; 736 supported; 10 chips confirmed non-dispatchable (D-12: host guard
covers non-supported chips with real handlers; non-handler outcomes also safe); 0
non_supported_dispatchable (gate GREEN because chip_resolver.resolve_chip refuses, not because sim
pretends mem_type=None); 0 dispatch regressions; 0 consistency violations
EXIT=0
```

**Claim for the record:** the numeric migration changed no value that reaches the firmware and no
byte that reaches the user. Mechanism: `vcc` and `vpp_volts` are absent from all nine wire keys
`convert_to_programmer` emits (`database.py`'s mapped dict now carries `vcc_mv`/`vpp_mv` only, and
`convert_to_programmer` reads `vpp_mv` directly), so a VCC decode change cannot reach `write` — the
wire never carried `vcc` in the first place (**D-06**). The render contract
`f"{mv / 1000:.1f}v"` (`format_mv`) is byte-exact for all 13 distinct database voltages, so no
rendered byte moved either (**D-15**).

**Correction to the record (RESEARCH F-3):** CONTEXT.md's D-15 supporting prose stated the proof as
"the snapshot diff changes on exactly the AT28C-family lines" — this proof mechanism does **not**
exist. No AT28C VCC line appears in any pinned snapshot; the only info-view snapshot in
`test_characterization.py` runs `firestarter info W27C512`, which is not a mover (its VCC/VPP values
are unaffected by the AT28C-specific decode this phase's later plans address). The criterion this
phase actually holds to, and the one measured above, is the stronger one: the `.ambr` file is
**byte-unchanged** in its entirety. Criterion 1 (AT28C256's `VCC:` line moving to the corrected
value) gets a **new**, dedicated test in Plan 06 — it does not exist yet and was never claimed to
exist in this section.

## Evidence Ceiling

This phase corrects data the generator emits (`tools/build_db.py`'s VCC decode) and makes **no
claim** about AT28C silicon behaviour. `0x0D` stays `UNVERIFIED`, no `support_status` changes as a
result of this phase, and gh#21 / #32 / #11 / #12 stay OPEN.

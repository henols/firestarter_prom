# 149-PAGE-SIZE.md — Phase 149 D-16 review artifact

This is the phase's single reviewable-whole artifact for the firmware page-size seam. It carries
the fork point this phase measures every figure against, the cold pre-edit AVR baseline, the D-01
upstream-provenance table and its citation chain, the three measured non-claims the Evidence
Ceiling requires, and placeholder sections for the evidence later plans in this phase append.
Everything this document records about the page-size change is **software-proven and unvalidated on silicon**.

## The fork point

Branch: `gsd/v1.32-at28c-write-path-root-cause-report-provenance` — byte-identical to the branch
`firestarter_app` was already on, so the milestone's dual-repo pairing is legible by name alone.

Forked with:

```
git -C firestarter fetch origin
git -C firestarter status --porcelain          # empty before switching
git -C firestarter checkout -b gsd/v1.32-at28c-write-path-root-cause-report-provenance origin/beta
```

`origin/beta` resolved, at fork time, to:

```
7f6afc65be2022575989772cc0a5945611741831
```

(Research measured this as `7f6afc6` on 2026-08-19; the full SHA above is what this plan actually
observed and is the fork point every figure in this phase is measured against. It did not move
between research and execution.)

The firmware submodule was previously on `gsd/v1.31-27c-programming-algorithm-fidelity` at
`6992271`. The v1.31 PRs were squash-merged into `beta`, so a `git merge-base --is-ancestor` check
between `6992271` and the new branch returns a false negative. **Ancestry checks were deliberately
not used anywhere in this verification.** The fork was instead verified by five content checks,
each asserting the literal presence of v1.31 deliverables in the new `HEAD`:

```
$ git -C firestarter show HEAD:scripts/check_size_baseline.py | grep -n 'MERGE05'
123:MERGE05_UNO_CLASS_FLASH_BAND = 64
167:MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96
... (8 more references to both constants)

$ git -C firestarter cat-file -e HEAD:scripts/baseline/size_baseline_base01.json ; echo EXIT=$?
EXIT=0

$ git -C firestarter grep -c 'eprom_internal_program_pulse' HEAD -- src/proms/eprom.cpp
HEAD:src/proms/eprom.cpp:4

$ git -C firestarter grep -c 'CAP-02' HEAD -- src/firestarter.cpp
HEAD:src/firestarter.cpp:3

$ git -C firestarter diff --stat 6992271 HEAD -- src/json_parser.c include/json_parser.h \
    include/firestarter.h src/proms/eeprom_28c.cpp scripts/ platformio.ini test/native
(no output — byte-identical)
```

All five checks passed. `eprom_internal_program_pulse` appearing exactly 4 times proves Phase 145's
W27C512 fix landed; `CAP-02` appearing in `src/firestarter.cpp` proves fw#52's CAP-02 conflict is
resolved on `origin/beta`; the empty `diff --stat` proves every file this phase touches is
byte-identical between the old v1.31 tip and the new fork point, so no in-flight change on `beta`
contaminates this phase's baseline. `git -C firestarter status --porcelain` was empty both before
and after the fork.

## Pre-edit cold measurement (D-13)

Procedure, run once per env, in that order, from `/workspaces/firestarter`:

```
rm -rf .pio/build/<env>
pio run -e <env> 2>&1 | tee .../149-baseline-cold-<env>.log
```

Each of the three logs is one uninterrupted invocation (a single `Processing <env>` header), ends
in `[SUCCESS]`, and reports zero `warning:` lines.

| env       | flash_used | flash_total | ram_used | ram_total | warnings |
|-----------|-----------:|------------:|---------:|----------:|---------:|
| uno       | 24920      | 32256       | 1573     | 2048      | 0        |
| uno328pb  | 24970      | 32384       | 1579     | 2048      | 0        |
| leonardo  | 27002      | 28672       | 2014     | 2560      | 0        |

**Delta vs `size_baseline.json`** (the live baseline, uno 24920/1573, uno328pb 24970/1579,
leonardo 27002/2014): **0** on all six figures, on all three envs. Nothing was inherited from the
v1.31→beta merge beyond what `size_baseline.json` already records; the cold capture reproduces it
exactly.

**Delta vs `size_baseline_base01.json`** (BASE-01, MERGE-05's judged reference: leonardo 26906,
uno 24824, uno328pb 24874; RAM 1573/1579/2014 unchanged): **+96 B flash on all three envs, 0 B RAM
on all three envs.** This +96 B is Phase 145's already-adjudicated W27C512 defect fix, funded by
`MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96` — it is not new to this phase and this phase adds nothing
to it at this measurement point.

**Leonardo's MERGE-05 flash headroom is the number 0 bytes.** The leonardo must-not-grow band is
0 B; the only allowance leonardo has ever had is the 96 B defect-fix exemption, and the current
+96 B delta consumes all of it: `0 (band) + 96 (exemption) − 96 (current delta) = 0 bytes`
remaining. Leonardo's physical free flash is **1670 B of 28672 (5.8%)** (28672 − 27002 = 1670),
which is a separate number from the MERGE-05 allowance — plenty of physical flash remains, but the
policy allowance that governs this phase's own growth is exhausted.

**Uno-class MERGE-05 headroom is 64 bytes.** `MERGE05_UNO_CLASS_FLASH_BAND = 64` plus the same 96 B
exemption gives uno/uno328pb a 160 B total allowance; the current +96 B delta leaves
`160 − 96 = 64 bytes` of policy headroom before this phase adds a single byte.

**v1.31's open MERGE-05 band breach, named explicitly:** the leonardo band is 0 B and the current
delta is already +96 B over BASE-01 — entirely consumed by Phase 145's fix, before this phase's own
page-size change adds anything. Any flash growth this phase's firmware seam introduces on leonardo
has zero band left to land in and must be separately funded (D-12), not silently absorbed against
this already-spent allowance.

## Why the reference SHA in size_baseline.json is not usable

`scripts/baseline/size_baseline.json`'s `meta.firmware_tree_sha` field records `3d8ec49…`, the root
tree of commit `6cc4795` — a **Phase 144** commit. That tree does not contain the +96 B Phase 145
later added (the same file's own AVR figures already include Phase 145's fix), so the field and the
figures it sits next to are mutually inconsistent as a reproducibility anchor. This plan therefore
did not reason from `meta.firmware_tree_sha` at all — the fork was verified by content (see above)
and the cold capture was compared directly against the live figures in `size_baseline.json` and
`size_baseline_base01.json`. Plan 07 corrects the stale field; this plan deliberately leaves it
untouched and unused.

## Upstream provenance — which chips get a delivered page size (D-01)

`chip_database.json`'s 84 `algorithm: 13` (`0x0D`) rows are not 84 upstream-`0x0D` records.
`build_db.py`'s `classify()` promotes several DIP families into `0x0D` from whatever protocol they
actually arrived with in the pinned `infoic.xml`. Joining all 84 rows back to the upstream XML
(all 84 matched, zero unmatched):

| upstream `protocol_id` | `page_size` values → counts | row count |
|---|---|---:|
| `0x07` | 1→14 · 16→1 · 32→8 · 64→22 · 128→1 · 256→1 | 47 |
| `0x0B` | 1→17 · 16→2 | 19 |
| **`0x0D`** | **64→3 · 128→15** | 18 |

47 + 19 + 18 = 84. Of the 84, 66 are promoted (47 + 19) and 18 are upstream-native
(64→3, 128→15). `infoic_page_size_raw` is a **faithful** copy of the upstream field — zero fidelity
mismatches across all 84 rows. There is no decode bug anywhere in this pipeline; the question this
phase answers is purely semantic: which of the 84 rows' `page_size` values are evidence about a 28C
page buffer at all.

D-01: deliver a page size only where the upstream `<ic>` record's own `protocol_id` is `0x0D` —
i.e. only the 18 upstream-native rows. `classify()` arm 2 (`build_db.py:371-386`) is the promotion
that makes the other 66 of the 84 non-native, and it is exactly that promotion which disqualifies
them from D-01.

## The 15 movers and the 3 no-change rows

**The 15 movers** (upstream `0x0D`, upstream page 128, growing from today's 64-byte floor):

- ATMEL: `AT28C010,AT28C010E`, `AT28C040,AT28C040E`, `AT28LV010`, `AT28MC020`, `AT28MC040` (5)
- CATALYST (CSI): `CAT28C512`, `CAT28C010`, `CAT28C020`, `CAT28C040` (4)
- MAXWELL: `28C010,28C010T,28C011,28C011T` (1 group, 4 part numbers)
- SGS-THOMSON: `M28010` (1)
- ST: `M28010` (1)
- WED: `WE512K8`, `WME128K8` (2)
- XICOR: `X28C010` (1)

**The 3 no-change rows** (upstream `0x0D`, upstream page 64 — already equal to today's floor):

- ATMEL: `AT28MC010`
- WED: `WE128K8`, `WE256K8`

Note that `AT28MC010` (64) and `AT28C010` (128) are both upstream-native `0x0D` — the
same-density-different-page argument the existing `eeprom_28c.cpp` comment rests on is fully
preserved by D-01's rule, and both chips are in the delivered set.

## Why this condition (D-01, with its citation)

The rule is stated as a claim about **provenance, never about a part**: the `page_size` attribute
is meaningful for the algorithm that consumes it; a record filed under `0x07`/`0x0B` is not
evidence about a 28C page buffer, even when its numeric value happens to be 64 or 128.

Citation: `firestarter_app/doc/infoic-field-dictionary.md:241` — the CONFIRMED `page_size` row:
"Page-write size for EEPROM/Flash. Typically 64 or 128 bytes for 28C-family; `0` or `1` if not
applicable to the device type", itself cited to minipro `database.c#L598` @ `a8efaedc`. Pinned
upstream source: the `infoic.xml` copy at commit `a8efaedc236c1d9718bd28299dfbb99536b010ff`
(md5 `b4548e57c4f6c6c8c4f7387add03fa77`, 17,861,009 bytes; `build_db.py` reads the `INFOIC2PLUS`
section only, of the three `<database>` sections the file contains).

Two rejected directions, and what each would have delivered:

1. **Grow-only, ignoring provenance** — 17 movers. Adds CYPRESS `FM28V020` and FUJITSU
   `MB85R256H`, **both FRAM**, one of them a 3.3 V part — parts with no page buffer at all in the
   sense the AT28C-family floor exists to protect. Rejected because it hands a page size to parts
   for which the concept is meaningless.
2. **All-real-values with sentinels** — 28 movers, 13 of which rest on a `page_size` read directly
   out of a `0x07`/`0x0B` record with no corroboration. Rejected because it reintroduces exactly the
   cross-algorithm reinterpretation D-01 exists to prevent, just with a sentinel fallback bolted on.

## No attribute in infoic.xml corroborates page_size

- `write_buffer_size` looks like the corroborating field one would want, and is not: it is the
  programmer's own transfer buffer. Across the 84 rows it takes `{128×46, 32×33, 64×4, 256×1}`, and
  for AT28C256 (a promoted `0x07` row) it reads 128 while the datasheet page is 64 — the opposite
  number from what this phase's floor uses for that chip.
- `read_buffer_size` is the same *kind* of field (a programmer buffer, not a chip attribute) but
  takes a different value set entirely: `{512, 2048, 128}`.
- `pages_per_block` is 0 on all 84 rows (a NAND-oriented field, inapplicable here).
- `firestarter_app/datasheets/` holds `AT28C256.pdf` and nothing else for any `0x0D` chip, so
  "check it against the datasheet" is unavailable for all 15 movers — and unavailable for the 11
  promoted 16/32-value rows discussed below.

## The three measured non-claims (Evidence Ceiling)

### 1. No silicon claim

No AT28C part exists in operator inventory. `.planning/REQUIREMENTS.md` §Out of Scope excludes
bench validation of the page-size change. ROADMAP criterion 1's "observed to deliver 128" is
satisfied purely as a **native flush-count** assertion on a host compiler (D-09) and must never be
described, here or anywhere else in this phase, as an observation made on real hardware.

### 2. AT28C256 (gh#21) is unchanged

AT28C256 — the part named in gh#21 — is a **promoted** row: its upstream `protocol_id` is `0x07`
and its raw `page_size` is `0x0040` (64). Under D-01 it receives no emitted `page-size` at all,
keeps the existing 64-byte floor, and its wire dictionary entry is **byte-unchanged** by this
phase. This phase cannot alter AT28C256's write behaviour in any way and explains nothing about
gh#21. `0x0D` stays `UNVERIFIED`; no `support_status` value changes anywhere in this phase; and
gh#21, gh#32, gh#11, and gh#12 all stay open.

### 3. The 16/32-value floor rows: unproven, not disproven

For the 11 promoted rows whose raw `page_size` is 16 or 32 (14 upstream-`0x07` at 1, 17
upstream-`0x0B` at 1, plus the 3-at-16 and 8-at-32 groups — see the deferred todo for the full
list), the 64-byte floor's safety is **unproven**, not disproven. Their `page_size` values come
from `0x07`/`0x0B` records whose own algorithm never treats that field as a 28C page-write buffer,
so this phase can assert neither that their real page is 16 or 32, nor that 64 is safe for them.
The correct word is unproven; "overruns today" is too strong a claim and does not appear anywhere
in this phase's artifacts.

## DB-side evidence (plan 03)

*(filled by plan 03)*

## Firmware seam evidence (plan 04)

*(filled by plan 04)*

## Cross-repo parity evidence (plan 05)

*(filled by plan 05)*

## Post-change cold measurement and MERGE-05 funding (plan 06)

*(filled by plan 06)*

## Baseline update and closing record (plans 07-08)

*(filled by plans 07-08)*

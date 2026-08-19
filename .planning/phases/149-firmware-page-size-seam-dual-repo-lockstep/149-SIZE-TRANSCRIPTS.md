# Phase 149 Plan 06 — Size Gate Transcripts

Cold post-change measurement, the MERGE-05 gate seen to FAIL before any exemption existed,
then seen to PASS after it, then the re-armed tripwire seen to FAIL again one byte past the
new allowance. Every command below is pasted verbatim with its literal output.

## Cold post-change measurement (Task 1)

Procedure, identical to plan 01's pre-edit capture: `rm -rf .pio/build/<env>` then one
uninterrupted `pio run -e <env>`, for `uno`, `uno328pb`, `leonardo`. All three ended
`[SUCCESS]` with zero `warning:` lines.

| env | pre-edit cold flash | post-change cold flash | Δ vs pre-edit | BASE-01 flash | Δ vs BASE-01 | pre-edit cold RAM | post-change cold RAM | Δ vs pre-edit | BASE-01 RAM | Δ vs BASE-01 |
|---|---|---|---|---|---|---|---|---|---|---|
| uno | 24920 | 25130 | +210 | 24824 | +306 | 1573 | 1575 | +2 | 1573 | +2 |
| uno328pb | 24970 | 25180 | +210 | 24874 | +306 | 1579 | 1581 | +2 | 1579 | +2 |
| leonardo | 27002 | 27212 | +210 | 26906 | +306 | 2014 | 2016 | +2 | 2014 | +2 |

`flash_total` / `ram_total` are unchanged on all three envs (32256/2048, 32384/2048, 28672/2560)
— the board/framework did not move.

**Seam flash cost `N` (BASE-01 delta minus the already-admitted 96 B defect-fix exemption):
`306 - 96 = 210` B, uniform on all three AVR targets.**

**Seam RAM cost `M` (BASE-01 delta; the pre-edit capture's RAM already equalled BASE-01's on
all three targets, so "vs pre-edit" and "vs BASE-01" are the same number here): `+2` B, uniform
on all three AVR targets — matching the predicted cost of the one `uint16_t page_size` field
added to the single file-scope `firestarter_handle_t` global (AVR aligns scalars to 1 byte, so
there is no padding to absorb it).**

## Cold warning run (Task 1)

Both native build directories plus `native_pinmap_provisional`'s were removed by hand first
(`_rebuild_native` does not clean; the recorded watermarks are cold figures, and the warm
figures read as headroom that does not exist):

```
$ rm -rf .pio/build/native .pio/build/native_nodevtools .pio/build/native_pinmap_provisional
$ python3 scripts/check_build_warnings.py --rebuild ; echo EXIT=$?
...
PASS: uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0), leonardo: macro_redefinition=0 (== 0), native: total warnings=1166 (== watermark 1166), native_nodevtools: total warnings=1166 (== watermark 1166)
EXIT=0
```

AVR macro-redefinition counts are 0/0/0 (the `== 0` rule, not `<= 0`). Both pinned native
watermarks (`native`, `native_nodevtools`) hold at exactly **1166**, measured cold — no
watermark is lowered by this plan. (`--rebuild`'s `NATIVE_ENVS` tuple covers `native` and
`native_nodevtools` only; `native_pinmap_provisional` is not part of that rebuild set and was
not re-measured here — its build directory was still removed for cleanliness before the run,
and its recorded baseline watermark of 138 is untouched.)

## RED — MERGE-05 before the page-size-seam exemption

```
$ python3 scripts/check_size_baseline.py --policy merge05 \
  --baseline scripts/baseline/size_baseline_base01.json \
  --avr-log uno=/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-postchange-cold-uno.log \
  --avr-log uno328pb=/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-postchange-cold-uno328pb.log \
  --avr-log leonardo=/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-postchange-cold-leonardo.log ; echo EXIT=$?
FAIL:
  uno: flash_used baseline=24824 observed=25130 delta=+306 exceeds MERGE-05 uno-class allowance of 160 B (band 64 B + defect-fix exemption 96 B)
  uno: ram_used baseline=1573 observed=1575 delta=+2 (MERGE-05 requires ram_used unchanged)
  uno328pb: flash_used baseline=24874 observed=25180 delta=+306 exceeds MERGE-05 uno-class allowance of 160 B (band 64 B + defect-fix exemption 96 B)
  uno328pb: ram_used baseline=1579 observed=1581 delta=+2 (MERGE-05 requires ram_used unchanged)
  leonardo: flash_used baseline=26906 observed=27212 delta=+306 exceeds MERGE-05 leonardo allowance of 96 B (band 0 B + defect-fix exemption 96 B)
  leonardo: ram_used baseline=2014 observed=2016 delta=+2 (MERGE-05 requires ram_used unchanged)
EXIT=1
```

This confirms the exemption is necessary, not convenient — both a flash exemption (the
leonardo line names `allowance of 96 B`, the pre-existing figure) and a RAM exemption (every
env's `ram_used` line fires, `M=2` moved on all three targets) are required before this gate
can pass. Recorded before any constant was authored.

## The named exemptions (Task 2)

`MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES = 210` (flash) and
`MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES = 2` (RAM) added to
`firestarter/scripts/check_size_baseline.py`, funding exactly `N=210` and `M=2` as measured
above. `MERGE05_UNO_CLASS_FLASH_BAND` stays 64, `MERGE05_DEFECT_FIX_EXEMPTION_BYTES` stays 96,
and `scripts/baseline/size_baseline_base01.json` is byte-unchanged. `_merge05_flash_allowance`
is now a 5-tuple `(band, defect_exemption, seam_exemption, allowance, band_label)`; a new
`_merge05_ram_allowance(env)` resolves the RAM tolerance. New effective allowances:
leonardo `0 + 96 + 210 = 306` B, uno-class `64 + 96 + 210 = 370` B; RAM tolerance `2` B on all
three targets.

## GREEN — MERGE-05 with the page-size-seam exemption

```
$ python3 scripts/check_size_baseline.py --policy merge05 \
  --baseline scripts/baseline/size_baseline_base01.json \
  --avr-log uno=/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-postchange-cold-uno.log \
  --avr-log uno328pb=/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-postchange-cold-uno328pb.log \
  --avr-log leonardo=/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-postchange-cold-leonardo.log ; echo EXIT=$?
PASS: uno(flash=25130/32256[+306<=370=band64+exempt96+seam210],ram=1575/2048[+2<=2=seam2]), uno328pb(flash=25180/32384[+306<=370=band64+exempt96+seam210],ram=1581/2048[+2<=2=seam2]), leonardo(flash=27212/28672[+306<=306=band0+exempt96+seam210],ram=2016/2560[+2<=2=seam2])
EXIT=0
```

Every env's PASS text names the full three-term flash decomposition (`band` + `exempt` +
`seam`) and the RAM decomposition (`seam2`), on the real cold post-change logs. Leonardo's
delta (`+306`) exactly equals its allowance (`306`) — its MERGE-05 headroom after this
exemption is exactly **0 bytes**, same shape as the Phase 145 admission it sits alongside: the
exemption funds exactly what was measured, with no spare margin.

## The tripwire is still ARMED

Full suite, with the three fixtures re-planted at exactly one byte past the new allowances:

```
$ python3 -m pytest tests/test_check_size_baseline.py -q
..............
14 passed in 0.70s
```

Direct gate runs against each re-planted fixture, showing the tripwire fires one byte past the
new allowance in all three dimensions (leonardo flash, uno-class flash, RAM):

```
$ python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json \
  --avr-log leonardo=tests/fixtures/planted_size_baseline_policy_leonardo_growth.log ; echo EXIT=$?
FAIL:
  leonardo: flash_used baseline=26906 observed=27213 delta=+307 exceeds MERGE-05 leonardo allowance of 306 B (band 0 B + defect-fix exemption 96 B + page-size-seam exemption 210 B)
EXIT=1

$ python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json \
  --avr-log uno=tests/fixtures/planted_size_baseline_policy_uno_over_band.log ; echo EXIT=$?
FAIL:
  uno: flash_used baseline=24824 observed=25195 delta=+371 exceeds MERGE-05 uno-class allowance of 370 B (band 64 B + defect-fix exemption 96 B + page-size-seam exemption 210 B)
EXIT=1

$ python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json \
  --avr-log uno=tests/fixtures/planted_size_baseline_policy_ram_moved.log ; echo EXIT=$?
FAIL:
  uno: ram_used baseline=1573 observed=1576 delta=+3 exceeds MERGE-05 ram allowance of 2 B (page-size-seam exemption 2 B) (MERGE-05 requires ram_used within the admitted allowance)
EXIT=1
```

Each fixture was re-derived from `allowance + 1` using the new allowances above (leonardo
`306+1=307` → flash `26906+307=27213`; uno-class `370+1=371` → flash `24824+371=25195`; RAM
`2+1=3` → RAM `1573+3=1576`) and observed to fail, not merely asserted to fail — the tripwire
is a machine-checked negative control at the new floor, not a claim.

## Firmware repo pytest and native suites (Task 2, run after committing)

```
$ python3 -m pytest tests/ -o addopts="" -q
........................................................................ [ 22%]
........................................................................ [ 45%]
........................................................................ [ 68%]
........................................................................ [ 91%]
...........................                                              [100%]
315 passed in 9.75s
```

314 (Phase 149 pre-existing count, per plan 04's SUMMARY) + 1 new leg
(`test_base01_is_not_re_anchored_by_the_new_exemption`) = 315. This plan added zero new native
cases.

```
$ pio test -e native
================ 151 test cases: 151 succeeded in 00:00:20.434 ================
$ pio test -e native_nodevtools
================ 151 test cases: 151 succeeded in 00:00:22.194 ================
```

Both pinned native envs agree at 151/151 cases, 17 suites, unmoved from plan 04's landing
(baseline 141 + 10 new native cases added by plan 04).

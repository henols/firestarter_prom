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

<!-- gsd:write-continue -->

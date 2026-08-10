# 141-LOOP-RECORD: Phase 141 Per-Byte Program Loop — Close Record

**Owner requirements:** LOOP-01, LOOP-02, LOOP-03, LOOP-04, LOOP-05, LOOP-06, LOOP-07, LOOP-08 — all
eight discharged **here**, by this plan (141-09), citing the evidence the eight prior plans
(141-01 through 141-08) produced. **Status:** the cold measurement this document reconciles was taken
strictly after `141-PREDICTIONS.md` was committed, exactly as that document requires. **The MERGE-05
flash-band policy is RED and stays RED** — an explicit operator decision, recorded in §1 and not
softened anywhere in this document. Every other gate this phase touches is green. LOOP-01 through
LOOP-08 are marked complete in `.planning/REQUIREMENTS.md` by this same plan's Task 3, after every
piece of evidence below exists.

This document follows `140-PARAM-TABLE-RECORD.md`'s house shape (numbered sections, a findings
register with owners, an explicit "what this is and is not" framing, a hand-off table), adapted to
the sections this plan's own Task 2/Task 3 action text specifies.

---

## 1. MERGE-05 verdict — RED, and it stays RED (operator decision)

**Operator decision, recorded before this plan (141-09) began — 2026-08-10, during `/gsd-execute-phase
141`, before Wave 3 was dispatched.** The operator was presented three options for the flash-band
overage below (continue-and-record / halt-and-shrink / re-baseline) and chose: **"Continue; 141-09
records it."** This document's job is to record the RED faithfully, not to fix it and not to soften
it. Per that instruction, this plan did **not** run the plan's own action-text reduction ladder
(payload-size shrink / `verify_mode` call collapse / dead-function deletion) — attempting it would
re-litigate a decision the operator already closed before this plan was dispatched. No baseline JSON
was edited; `git status --porcelain scripts/baseline/` is empty in `/workspaces/firestarter`.

### 1.1 Cold measurement (this plan's own, re-derived — matches the pre-dispatch figures exactly)

Each target was measured via `pio run -t clean -e <env>` followed by a single uninterrupted
`pio run -e <env>`, one target at a time, logs captured:

```
uno:      RAM 1573 B / Flash 24424 B  (75.7% of 32256)
uno328pb: RAM 1579 B / Flash 24474 B  (75.6% of 32384)
leonardo: RAM 2014 B / Flash 26400 B  (92.1% of 28672 — 2272 B headroom)
```

### 1.2 `check_size_baseline.py --policy merge05` — verdict, verbatim

```
$ cd /workspaces/firestarter && python3 scripts/check_size_baseline.py --policy merge05 \
    --baseline scripts/baseline/size_baseline_base01.json \
    --avr-log uno=<log> --avr-log uno328pb=<log> --avr-log leonardo=<log>
FAIL:
  uno: flash_used baseline=23932 observed=24424 delta=+492 exceeds MERGE-05 uno-class band of 64 B
  uno328pb: flash_used baseline=23976 observed=24474 delta=+498 exceeds MERGE-05 uno-class band of 64 B
  leonardo: flash_used baseline=26072 observed=26400 delta=+328 exceeds MERGE-05 leonardo band of 0 B
$ echo $?
1
```

**RAM passes exactly** on all three targets (0 delta vs BASE-01: 1573/1579/2014, identical) — the
script prints no RAM `FAIL:` line, and the equality enforcement (`check_size_baseline.py:224-227`)
is satisfied. The removed `uint8_t mismatch_bitmask[DATA_BUFFER_SIZE / 8]` stack array (64 B on
Uno-class, 128 B on Leonardo, `eprom.cpp:155` pre-141-04) is a genuine peak-stack improvement that
deliberately does **not** appear in this figure — a stack array is neither `.data` nor `.bss`, so
`avr-size`'s static `ram_used` cannot see it move, exactly as `141-PREDICTIONS.md` P2 stated before
any code moved.

### 1.3 `check_build_warnings.py --rebuild` — passes, watermark holds with zero headroom

```
PASS: uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0),
      leonardo: macro_redefinition=0 (== 0), native: total warnings=1166 (== watermark 1166),
      native_nodevtools: total warnings=1166 (== watermark 1166)
```
Exit 0. The three AVR targets stay at exact-zero macro-redefinition warnings; both pinned native
envs sit exactly **at** the 1166 watermark — **zero headroom**, unchanged since before this phase
started. Neither `native_loop_v131`, `native_trace_v131`, nor `native_params_v131` was ever passed
to this script or to `check_size_baseline.py` (an unrecognized env name raises an uncaught `KeyError`
in the latter, exit 1 — F-138-05, inherited, accepted, not fixed by this phase).

### 1.4 Measured-versus-predicted table

`141-PREDICTIONS.md` was committed at `4c5d9172` (meta repo, branch
`gsd/v1.31-27c-programming-algorithm-fidelity`), **before** plan 141-04 (or any later plan) moved a
byte of `src/proms/eprom.cpp` or `src/proms/memory.cpp` — the ordering this document's own reconciliation
section requires.

| Target | BASE-01 | 141-PREDICTIONS.md P1 (Phase-141-only delta) | Predicted absolute | **Measured absolute (this plan, cold)** | **Measured total delta vs BASE-01** | Band | Remaining headroom |
|---|---|---|---|---|---|---|---|
| `uno` | 23932 | +30 B | 23984 (+52 vs BASE-01) | **24424** | **+492** | 64 B (uno-class) | **−428 B (over budget)** |
| `uno328pb` | 23976 | +30 B | 24034 (+58 vs BASE-01) | **24474** | **+498** | 64 B (uno-class) | **−434 B (over budget)** |
| `leonardo` | 26072 | +18 B | 26034 (−38 vs BASE-01, i.e. under ceiling) | **26400** | **+328** | 0 B (must not grow) | **−328 B (over budget)** |

RAM (P2, all three): predicted exact-0 delta — **measured exact-0 delta, confirmed** (1573/1579/2014,
byte-identical to BASE-01).

**The overrun is roughly 14x P1's point estimate**, and beyond even `141-PREDICTIONS.md`'s own
acknowledged worst case (that document's own ingredient ledger, recomputed from its high-adds/
low-removes extremes, reaches approximately +274 B — still well short of the measured +422/+422/
+336 B this phase's own rewrite contributed on top of the pre-141-04 tip).

### 1.5 Attribution of the overrun

Of `uno`'s measured **+492 B** total delta vs BASE-01:

- **+22 B** — pre-existing Phase 140 tip (already spent before Phase 141 began; unrelated to this
  phase's own work).
- **+48 B** — plan 141-02's `mem_util_delay_us` / `mem_util_split_delay` safe-delay helper.
- **+422 B** — plan 141-04's rewrite itself, decomposed via `avr-nm --print-size` (LTO is active,
  confirmed by `__gnu_lto_slim`/`__gnu_lto_v1` markers in every `.o`, which is why `eprom_overprogram_us`,
  `eprom_params_for`, and `configure_eprom` do not appear as separate linked symbols in either build):
  - **+108 B** — `eprom_write_execute` itself (898 → 1006 B): the actual per-byte pulse→verify loop,
    the two skip checks, the dual budget tracking, the DIP32 branch, the `overprogram` gate, and the
    `VERIFY_PER_PULSE_PLUS_FINAL` final-pass loop.
  - **+110 B** — `eprom_internal_report_budget_failure` (new, kept out-of-line by LTO because it has
    two call sites).
  - **+156 B** — `configure_memory` (864 → 1020 B): `configure_eprom`'s two new D-03/D-05 refusals
    land here once inlined, **and** this is the first place `eprom_params_for()`'s own linear-scan
    accessor body becomes genuinely linked at all — the two costs are inseparable in this one number.
  - **+48 B** — `EPROM_PARAMS[]` (36 B) + `EPROM_PARAM_KEYS[]` (3 B) PROGMEM data becoming linked for
    the first time, plus alignment/padding.

**Key framing for the record: roughly +204 B of the +422 B is Phase 140's parameter table finally
being paid for**, not new Phase 141 logic. Before this phase, nothing in `src/` called
`eprom_params_for()`, so `-Wl,--gc-sections` collected the whole table and its accessor wholesale
(Phase 140 F-140-02, `140-PARAM-TABLE-RECORD.md` §6). `configure_memory`'s own +156 B delta is where
that first-live-reference cost lands, combined with `configure_eprom`'s two refusals — the two are
not separable by this measurement, but the accessor-body-plus-hoisted-reads component of that number
is itself larger than the entirety of what `141-PREDICTIONS.md` budgeted for it. **Only roughly
+218 B is attributable to this phase's own loop and reporter logic** (`eprom_write_execute` +108 B,
`eprom_internal_report_budget_failure` +110 B). The **64 B `MERGE05_UNO_CLASS_FLASH_BAND`** was set
in Phase 123/124, before Phase 140's parameter table existed to be paid for — the band's own
provenance predates the cost this phase is now the first to pay.

### 1.6 The prediction miss — which ingredient was under-budgeted

`141-PREDICTIONS.md`'s own ingredient ledger budgeted roughly **70-80 B combined** for "the accessor
body" (`eprom_params_for()`'s ≤3-iteration linear scan) plus "six hoisted `pgm_read_*` reads" (one
per `eprom_params_t` column, at the loop's setup). The measured first-live-reference cost — captured
in the `configure_memory` delta above, **+156 B**, which is *at minimum* that same accessor-body cost
(it also carries `configure_eprom`'s two refusals) — is **at least double** the entire budgeted
figure, on its own, before the per-byte loop's own growth or the new reporter are even counted. This
is the single largest source of the miss: **the first-live-reference cost of the Phase 140 table was
under-budgeted by roughly 2x**, not merely imprecisely estimated. The retry-loop-removal's reclaim
(the *removes* half of the ledger) also plausibly landed toward the low end of its own acknowledged
range — 141-04-SUMMARY names the named uncertainty explicitly: AVR has no hardware 32-bit multiply/
divide, and if `libgcc`'s `__mulsi3`/division-helper routines were already linked elsewhere in the
binary for an unrelated reason, removing the one retry-loop call site reclaims only the call-site
overhead, not the shared routine body.

This is not reconciled by editing the implementation to force agreement with the prediction — no
task in this plan alters `src/proms/eprom.cpp` or `src/proms/memory.cpp`, and no baseline JSON was
edited. The number is recorded as measured; Phase 144 / TEST-08 owns the full 138-143 cross-phase
flash/RAM delta reconciliation, and inherits this attribution rather than re-deriving it.


# 143-HOST-RECORD: Phase 143 Host Timeout, Progress & Pulse Override — Close Record

**Owner requirements:** HOST-01, HOST-02, HOST-03, HOST-04, HOST-05 — all five discharged **here**, by
this plan (143-10), citing the evidence the nine prior plans (143-01 through 143-09) produced. This
document follows `142-VPP-RECORD.md`'s house shape (numbered sections, a findings register with owners,
an explicit "what this is and is not" framing, a hand-off table).

*Sections 1-6 and 8-11 are written by this plan's Task 3, after every piece of evidence below exists.
Section 7 (this plan's Task 2) is measured and recorded first, so the requirement evidence table and the
non-claims section that follow can cite real numbers rather than predictions.*

---

## 7. Measured size and gate verdicts

All AVR figures below were measured **cold**: `pio run -t clean -e <env>` followed by a single
uninterrupted `pio run -e <env>`, one target at a time, in this plan's own Task 2 session. The native
warning figures were measured cold too — `.pio/build/native` and `.pio/build/native_nodevtools` were
removed before invoking `check_build_warnings.py --rebuild`, so the recorded native totals are the COLD
figure `size_baseline.json`'s own `meta.warm_vs_cold_correction` distinguishes from a WARM re-run (COLD
1166 vs WARM 998 for both pinned native envs) — this measurement reproduced **1166**, confirming it is
the cold figure, not an accidentally-warm one.

### 7.1 Cold flash/RAM, all three AVR targets

```
--- uno ---
RAM:   [========  ]  76.8% (used 1573 bytes from 2048 bytes)
Flash: [========  ]  77.0% (used 24824 bytes from 32256 bytes)
--- uno328pb ---
RAM:   [========  ]  77.1% (used 1579 bytes from 2048 bytes)
Flash: [========  ]  76.8% (used 24874 bytes from 32384 bytes)
--- leonardo ---
RAM:   [========  ]  78.7% (used 2014 bytes from 2560 bytes)
Flash: [========= ]  93.8% (used 26906 bytes from 28672 bytes)
```

These figures are **byte-identical** to the post-143-08 tip (143-08 touched no firmware source; this
plan's own Task 1 is a docs-only `CLAUDE.md` commit) — cold and the prior incremental measurements agree
exactly, so no incremental-build artifact was hiding anything.

| Target | `size_baseline.json` baseline (Phase 124) | Measured (this plan, cold) | Delta vs. Phase-124 baseline |
|---|---|---|---|
| `uno` flash | 23954 B | 24824 B | **+870 B** |
| `uno328pb` flash | 24004 B | 24874 B | **+870 B** |
| `leonardo` flash | 26016 B | 26906 B | **+890 B** |
| `uno` / `uno328pb` / `leonardo` RAM | 1573 / 1579 / 2014 B | 1573 / 1579 / 2014 B | **+0 / +0 / +0 (exact)** |

RAM is unmoved on all three targets. `leonardo` headroom: **28672 − 26906 = 1766 B** remaining against the
hard build-failure ceiling, and **2130 − 1766 = 364 B** of F-142-08's hand-off headroom consumed this
phase. **`leonardo` still fits — D-22's whole bar is satisfied.**

**This phase's own contribution, isolated from the pre-existing (Phase 140-142) drift:**

| Target | Phase-142 tip (cold, `142-VPP-RECORD.md` §1.1) | This phase's own delta | Attributed to |
|---|---|---|---|
| `uno` flash | 24568 B | **+256 B** | 143-03 (CAP-02 port + CAP-03 wire-up, one pack block) |
| `uno328pb` flash | 24618 B | **+256 B** | 143-03, identical to `uno` |
| `leonardo` flash | 26542 B | **+256 B** (143-03) **+108 B** (143-05) = **+364 B** | 143-03 (CAP-02+CAP-03) and 143-05 (the guarded progress emission) |
| every target, 143-01/143-08/143-10 Task 1 | — | **+0 B** | 143-01 (arithmetic added but uncalled, `--gc-sections`-eliminated), 143-08 (Python-only gate, no firmware source), 143-10 Task 1 (docs-only) |

143-03's own SUMMARY records this identically: "this plan spent 256 B of F-142-08's 2130 B hand-off on
all three AVR targets (uno/uno328pb/leonardo all +256 B identically)." 143-05's own SUMMARY records the
`leonardo`-only +108 B, with `uno`/`uno328pb` confirmed byte-identical (proving the `#ifndef SERIAL_ON_IO`
guard genuinely excludes the code there, not merely an assertion about source text).

**RESEARCH's `[ASSUMED]` estimates, verdict:**

- **A2 (CAP-02 ~+34 B):** does **not** hold as a standalone prediction of the measured total, and
  cannot be cleanly isolated from it. BF-1's recommended disposition — and 143-03's own design decision
  — packed CAP-02 and CAP-03 into **one** `_ready[]` buffer and **one** `LOG_OK_ID_BYTES` emit, landed in
  one commit, specifically so the ack's shape is a single length-discriminated blob rather than two
  independent emits. The measured **+256 B** on every target is therefore CAP-02 **plus** CAP-03 **plus**
  the previously dead-code-eliminated `eprom_budget.cpp` functions becoming referenced (143-01 added them
  uncalled, at +0 B, precisely because nothing referenced them yet) — not CAP-02 alone. A2's ~34 B figure,
  cited from the upstream `13eb350` commit message, describes a narrower change than what this branch
  actually shipped, and the record states this rather than implying A2 was falsified by a like-for-like
  comparison that was never possible once BF-1's port-in-one-block disposition was chosen.
- **A3 (the emission 40-120 B on `leonardo`):** **held.** The measured `leonardo`-only contribution from
  143-05's guarded `MSG_DATA_PROGRESS` emission is **+108 B** — inside the stated 40-120 B range, and the
  `uno`/`uno328pb` zero-delta measurement is the direct, measured proof (not merely an assertion) that the
  `#ifndef SERIAL_ON_IO` guard costs nothing on those targets.

### 7.2 Warnings, cold

```
$ rm -rf .pio/build/native .pio/build/native_nodevtools
$ python3 scripts/check_build_warnings.py --rebuild
PASS: uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0), leonardo: macro_redefinition=0 (== 0), native: total warnings=1166 (== watermark 1166), native_nodevtools: total warnings=1166 (== watermark 1166)
$ echo $?
0
```

All three AVR targets: `macro_redefinition=0`, satisfying the stricter `avr_rule: "== 0"`. Both pinned
native envs: **1166**, exactly at the watermark with **zero headroom**, unmoved from the post-143-08 tip
(143-01 through 143-08 never moved this figure either — the phase's native-side additions are all pure,
Arduino-free C, contributing no new `pgmspace.h`-vs-`ArduinoFake` redefinition). No new warning of any
kind was introduced by this phase, on any target.

### 7.3 Native envs

| Env | Measured this plan | Baseline / prior tip | Gate coverage |
|---|---|---|---|
| `native` | **141 test cases: 141 succeeded**, 17 suites | unmoved since `size_baseline.json` (Phase 124) and every intervening phase | `check_size_baseline.py` (default byte-identity mode), CI (`build.yml`/`beta-build.yml`) |
| `native_nodevtools` | **141 test cases: 141 succeeded**, 17 suites | unmoved, identical to `native` | same |
| `native_loop_v131` | **79 test cases: 79 succeeded**, 2 suites (`test_loop_eprom_v131` 47 + `test_vpp_eprom_v131` 32) | unmoved since the post-143-08 tip | **No gate asserts these counts and no CI leg of either repository runs this env** (D-14 of `142-CONTEXT.md`, carried). This record is the only place a later reader finds them. |
| `native_params_v131` | **9 test cases: 9 succeeded**, 1 suite | unmoved since Phase 140 | **No gate, no CI leg** — same caveat as `native_loop_v131`. |
| `native_trace_v131` | **6 test cases: 3 failed, 2 succeeded** (`ERRORED` overall) | unmoved since the post-142-04 tip | **RED by design (D-24).** No gate asserts it; no CI leg runs it. **Not re-frozen here.** |

**`native_trace_v131`, verbatim, both sides recorded:**

```
$ pio test -e native_trace_v131
test_smoke_setup_leaves_both_recorders_clean	[PASSED]
test_smoke_timing_hook_fires_for_delay_and_delaymicroseconds	[PASSED]
test_protocol_0x07_am27c512_capture_is_sound_and_deterministic: Expected 198 Was 91. 0x07 AM27C512 DIP28_27512	[FAILED]
test_protocol_0x08_am27c020_capture_is_sound_and_deterministic: Expected 221 Was 115. 0x08 AM27C020 DIP32_27C020	[FAILED]
test_protocol_0x0B_am2716_capture_is_sound_and_deterministic: Expected 201 Was 59. 0x0B AM2716 DIP24_2716	[FAILED]
Program received signal SIGQUIT (Quit)
6 test cases: 3 failed, 2 succeeded
```

Every `Was` value (91/115/59) is **byte-identical** to the value recorded at the post-143-03 and
post-143-05 tips — **this phase added zero frames to the frozen trace**, exactly as D-24 requires:
`native_trace_v131`'s harness pins `millis()` to `AlwaysReturn(0)`, so 143-05's time-gated emission (whose
predicate is `(millis() - last_emit_ms) >= EPROM_PROGRESS_EMIT_INTERVAL_MS`) can never fire there — a
frozen clock never advances past the interval. Phase 144 / TEST-06, which owns the eventual freeze and the
attributable diff, will therefore find **zero** D-02-attributable strobes when it re-derives this fixture.

**Never passed to either baseline script this session:** `native_loop_v131`, `native_params_v131`, or
`native_trace_v131` — confirmed by inspection of every command run in this task. An unrecognized native
env raises an uncaught `KeyError` in `check_size_baseline.py` (F-138-05, inherited, not fixed) and exits 2
from `check_build_warnings.py`. Neither was risked.

### 7.4 Baseline gate (`check_size_baseline.py`)

**The bare, no-argument invocation** (the literal form this plan's own `<verify>` block names) does not
compare anything and is not the substantive verdict:

```
$ python3 scripts/check_size_baseline.py
FAIL: no envs compared -- supply --avr-log/--native-log or --rebuild (never-vacuous guard: a comparator that compares nothing must not pass)
$ echo $?
1
```

This is the script's own documented "never-vacuous guard" (its own module docstring: "zero envs were
compared... not bypassed by `--policy`") — a tool-usage condition, not a flash-regression finding. It is
recorded here for completeness because the plan's own shorthand verify block names exactly this
invocation, but it is **not** one of the three permitted RED reasons (MERGE-05, the OD-2 CAP-02 drift, or
this phase's own measured growth) and is not treated as a fourth, unattributed reason — it simply supplies
no data to attribute. The substantive verdict is the `--rebuild` invocation below, matching the
established convention every firmware plan in this phase (143-01, 143-03, 143-05, 143-08) already used:

```
$ python3 scripts/check_size_baseline.py --rebuild
FAIL:
  uno: flash_used baseline=23954 observed=24824
  uno328pb: flash_used baseline=24004 observed=24874
  leonardo: flash_used baseline=26016 observed=26906
$ echo $?
1
```

**Every RED reason enumerated and attributed:**

| Target | `flash_used` delta | Attribution |
|---|---|---|
| `uno` | +870 B | +614 B — MERGE-05/OD-2 drift already RED and operator-accepted through the Phase-142 tip (`142-VPP-RECORD.md` §1.5, the script's own default-baseline invocation), unmoved by this phase's own measurement, **plus** +256 B — this phase's own measured growth (143-03's CAP-02 port + CAP-03 wire-up), against a baseline deliberately left un-updated (D-22) |
| `uno328pb` | +870 B | identical composition to `uno`: +614 B pre-existing + 256 B this phase |
| `leonardo` | +890 B | +526 B — MERGE-05/OD-2 drift through the Phase-142 tip, **plus** +256 B (143-03) **plus** +108 B (143-05's guarded progress emission) = +364 B this phase's own growth |

**No RAM mismatch and no native mismatch appear anywhere in this output** — only `flash_used` lines, on
all three AVR targets, confirming RAM and both pinned native envs' case/suite/status facts still match
`size_baseline.json` exactly. **No reason outside the three permitted categories appeared.**
`git diff --exit-code -- scripts/baseline/size_baseline.json` is clean — the baseline was not edited, per
D-22.

### 7.5 Firmware pytest

```
$ python3 -m pytest tests/ -o addopts="" -q
292 passed in 12.70s
```

**292 passed** — the post-143-08 count, unchanged by this plan's own docs-only Task 1 commit (confirmed:
this run was made immediately after committing `CLAUDE.md` alone, satisfying L-1). Reconciled against the
phase's own running total: 272 (post-142-07) → 282 (143-03, `+10`: `test_ack_layout_source_contract_v143.py`)
→ 292 (143-08, `+10`: `test_progress_emission_is_leonardo_only.py`) → **292** (143-01/143-05/143-09/this
plan's Task 1 add zero Python-pytest-collected tests — their additions are native Unity C++ cases, or, for
143-09, a `firestarter_app`-only change).

Both new gate modules are confirmed included and green, alongside every other "must stay green" module
named by this plan:

```
$ python3 -m pytest tests/test_ack_layout_source_contract_v143.py tests/test_progress_emission_is_leonardo_only.py tests/test_protocol_branch_inventory.py tests/test_hv_routing_source_contract_v142.py tests/test_write_path_source_contract_v131.py tests/test_golden_trace_identity.py tests/test_golden_trace_identity_eprom_v131.py tests/test_flash_path_record_sync.py -o addopts="" -q
108 passed in 1.70s
```

### 7.6 Host (`firestarter_app`, read-only this phase)

From `/workspaces/firestarter_app`, `.venv/ci-replica/bin/python` (verified `Python 3.11.15`, L-3):

```
$ .venv/ci-replica/bin/python -m pytest tests/ --cov=firestarter --cov-fail-under=70 -o addopts=""
1578 passed, 1 warning in 229.49s (0:03:49)
Required test coverage of 70% reached. Total coverage: 82.92%
30 snapshots passed.
```

**1578 passed**, coverage **82.92%** (≥ 70% floor). Reconciled against the **1547** phase-start baseline
(`138-04-HOST-BASELINE.md`), every added test attributed to its plan:

| Plan | Host tests added | Running total |
|---|---|---|
| phase start (`138-04-HOST-BASELINE.md`) | — | 1547 |
| 143-01 | 0 (firmware-only plan) | 1547 |
| 143-02 | +5 (`test_hw_revision_gate.py`'s CAP-03 decode cases) | 1552 |
| 143-03 | 0 (firmware-only plan) | 1552 |
| 143-04 | +10 (`test_write_response_budget.py` 6 + `test_pulse_us_override.py` 4) | 1562 |
| 143-05 | 0 (firmware-only plan) | 1562 |
| 143-06 | +6 (`test_write_progress.py`; Test 5's negative split into two functions, plan-permitted) | 1568 |
| 143-07 | +6 (`test_pulse_us_override.py` extended in place, 4→10) | 1574 |
| 143-08 | 0 (firmware-only plan) | 1574 |
| 143-09 | +4 (`test_budget_failure_render.py`) | 1578 |
| **Total** | **+31** | **1578** |

`1547 + 5 + 10 + 6 + 6 + 4 = 1578` — the measured figure, exactly. No discrepancy.

```
$ ruff check firestarter/ tests/
All checks passed!
$ ruff format --check firestarter/ tests/
134 files already formatted
$ .venv/ci-replica/bin/python tools/check_mypy_watermark.py
checked 136 source files
mypy errors: 33 (watermark: 35)
$ echo $?
0
```

`ruff check` and `ruff format --check` both clean. The mypy watermark gate **exits 0** — 33 errors, 2
below the 35 watermark, unmoved from the 143-04/143-06/143-07/143-09 baseline (this phase's own new code
is fully typed; the 33 pre-existing errors are untouched). **Exit 0 is a genuine pass, not the exit-2
"cannot be trusted" condition.**

`git -C /workspaces/firestarter status --porcelain` was confirmed clean both immediately before this sweep
and immediately after — no L-6/L-1b deselection was needed, and `firestarter_app`'s own
`git status --porcelain` shows only the same eight pre-existing untracked files present at session start
(`.coverage`, `.planning/config.json`, `SECURITY.md`, four datasheets, `write_test_port.sh`) — **nothing
was written or committed in `firestarter_app` by this plan**, matching its read-only role in
`commits_land_in`.

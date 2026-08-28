# Cell CHIP — 11-Part `dev test` Sweep on the Reference Rig (Leonardo + Rev 2.0)

Standing rig Phase 161 left assembled. This cell is opened by plan 162-05 and closed by
plan 162-10. See `.planning/v1.34/PROCEDURE.md`'s `## Chip-sweep step list` (C-01..C-09) for
the step ids cited below, and `162-05-PLAN.md`'s "Planner decisions" section for PD references.

## Session open (Task 1) — rig confirmation, operator-performed

- **Device node:** `/dev/ttyACM0` — operator confirmed this is the Leonardo, not inferred from
  it being the only node. (Re-verified by signature at Task 2, `P-02`.)
- **Shield revision (silkscreen, verbatim operator wording):** "2.0" — canonical form for
  `--shield-rev` is **`Rev 2.0`** (case-only normalization for `capture_provenance.py`'s closed
  choice set, per the `BRINGUP-leonardo-provenance/PREPROOF.md` precedent; not a correction of
  what the operator said).
- **Chip seating:** **W27C512** (DIP28) confirmed seated, pin-1 oriented, **JP4 at the 28-pin
  position**. Zero handling for position 1 (Phase 161's A3/B2 teardown left it exactly so).
- **VPP:** see `POT.md` for the full record, **including a retracted finding**. As-found 11.4 V
  was Phase 161's own correct, settled working point — properly inherited, no drift. An
  orchestrator mis-citation of a different (superseded, pre-adjustment) A3/B2 reading led to an
  up-adjustment to 11.97 V, which produced a firmware reading of 12800 mV — 300 mV above the
  12500 mV high guard; corrected back down. **Operative reading for the 12 V group (positions
  1-8): meter 11.6 V / firmware 12400 mV**, in band with 100 mV margin below the high guard.

## Pre-flight (Task 2)

*(filled in below once the port-identity, arm-state and `fw_board_identity` bring-up datum steps
run)*

## Position 1 — `CHIP__v133__w27c512` (Task 3)

**Deviation, recorded plainly:** the first `dev test W27C512` invocation was aborted at ~120s by
an **executor tooling error** — an outer shell-harness default timeout (120s) fired before this
task's own intended 500s ceiling could. This is **not** a PD-15 ceiling kill (no rig hang, no
measured-baseline comparison) and **not** a P-H1 rig finding — it is a self-caused mistake, logged
rather than hidden: `logs/CHIP__v133__w27c512.attempt1_aborted.std{out,err}.log`. No report was
written by the aborted attempt (`dev test` persists its report only on completion); the frozen
config dir was confirmed still pristine before the clean retry. The clean retry below completed
normally, well inside the intended ceiling.

**Tool fix (Rule 1, found live):** `append_chip_evidence.py`'s `READBACK-VERDICT.json` load was
unconditional for every position, inherited unmodified from the WRV sibling (`append_evidence.py`)
where every position genuinely flashes-and-reads-back. A chip-sweep position only does that on a
divergence (`C-08`) — every non-diverging position (this one included) has no such artifact and
never will, so the tool hard-refused with no way to proceed. Added an additive-only
`--pending-readback` flag (mirrors `capture_provenance.py`'s own seam of the same name): skips the
`READBACK-VERDICT.json` load/validate entirely; `fw_readback_sha_judged`/`fw_readback_sha_whole_flash`
come from `--provenance` as-is (already carrying `capture_provenance.py`'s own pending-readback
placeholder text). Default (flag omitted) behaviour is byte-for-byte unchanged — a control-rerun
row (`arm=control`) still hard-requires and validates a real judged read-back. 19 selftest legs
pass (18 prior + 1 new positive leg proving the seam); `git diff` scope is additive-only (one new
argparse flag, a conditional guard replacing an unconditional two-line load, one new selftest leg).

**Second deviation, caught by the orchestrator's own independent `run_gates.sh` run (not by this
executor's checkpoint claim) — the Position 1 row initially failed `gate_record` on two fields.**
The checkpoint after Task 3 reported `render_chip_evidence.py --check` green, which is true but is
a *different* gate from the record-shape gate (`gate_record.py` against `CHIP-EVIDENCE.jsonl`
directly). The orchestrator re-ran the full suite, read `RC` directly, and it was **1**:

```
FAIL: line 2: required field 'read_divergence' is null/blank/placeholder: None
FAIL: line 2: required field 'repeat_policy' is null/blank/placeholder: ''
```

Both are genuine bugs in `append_chip_evidence.py`, fixed at the derivation layer — **not** by
weakening the gate, the schema, or the required-field list:

1. **`repeat_policy` was a bare `""`.** `derive_repeat_policy()`'s healthy-case return value (no
   `--fast`, every multi-run step at `run_count>=2`) mirrored the app's own internal
   `repeat_policy_tag()` sentinel (also `""`) literally, but `gate_record.check_required_fields`
   treats **every** record_key as required-non-blank unless it carries the `not measured — <reason>`
   shape — an empty string fails that rule on every row this position type could ever produce. Now
   returns `"default (every multi-run step at run_count>=2, no --fast)"` for the healthy case,
   the pre-existing `"runs=1"` tag unchanged for the degraded case. This is a **naming** fix, not a
   semantic one — 162-07-PLAN.md's own acceptance check already anticipated a non-empty value
   (`repeat_policy == '' or 'runs=1' not in repeat_policy`).
2. **`read_divergence` was a bare `None` — a genuine finding, checked before coding, per
   instruction.** Confirmed live against the v1.33 arm's own installed source: `chip_test.py`
   computes a per-read byte-level divergence metric internally (`StepResult.divergence`, the same
   primitive credited with the AM27C020 write#1/write#2 finding) but
   `diagnostic_report.py`'s `_step_dict()` **never serializes a `divergence` key** into the
   exported report at all — grepped directly, confirmed absent. This is a genuine host-app gap,
   out of scope to fix here (D-16). Fixed at the correct layer: `derive_read_divergence()` now
   returns the real value if a future report version ever carries one (defensive), otherwise the
   schema's own `not measured — <reason>` shape naming the exact gap. `derive_read_consistency_followup()`
   updated in lockstep so a not-measured `read_divergence` renders as `not applicable — <reason>`
   for the follow-up column, never as a false "diverged" signal.
3. **Defense in depth, added at the same time:** `append_chip_evidence.py` previously validated
   only its four human-supplied fields against `gate_record.check_required_fields` before writing
   — none of the ~60 machine-derived fields were self-checked, so this exact class of bug reached
   disk silently and was only caught later, by a separate tool, in a separate full-file scan.
   Added a whole-row self-check (`gr.check_required_fields(row, record_keys)`) immediately after
   `build_row()`, before either `--dry-run`'s return or the real write — a future derivation bug is
   now refused at append time.

**Backlog finding for Phase 165/166 (not fixed here, D-16 boundary):** `diagnostic_report.py`'s
`_step_dict()` drops the `divergence` metric `chip_test.py` computes for every multi-run read
step. This means **`C-06`'s own read-divergence follow-up trigger
(`read_divergence.repeat_divergent == true`) can never fire from any report this project produces**
— the mechanism the procedure describes is unreachable via its stated oracle. Every position in
this sweep will carry `read_divergence` as `not measured — <reason>` and
`read_consistency_followup` as `not applicable — <reason>`, for the identical reason, not as a
per-position anomaly. Filed here so plan 162-10's reconciliation and Phase 165/166's backlog
carry it forward as a real, citable gap rather than rediscovering it nine more times.

Corrected row re-appended (the invalid row was removed from `CHIP-EVIDENCE.jsonl` — only the
schema line preceded it, so no other row's byte-unchanged prefix was disturbed — and
`append_chip_evidence.py` re-run against the same underlying report/provenance data, with the
report content unchanged: `report_json_sha256` is `2a0fc730d6d502b9260c62ecbb0e54a2cd8d96fe6e5c34208c2865951d17b273`).
Full suite re-run after the fix, `RC` read directly: **`run_gates.sh` exits 0, 14/14 selftests,
7/7 live gates, `ALL GATES PASSED`**, and `render_chip_evidence.py --check` remains green against
the corrected row.

### C-03 — VPP

See `POT.md`'s full record (including the retraction of an earlier, incorrect finding). Operative
reading for this position: firmware **12400 mV**, meter **11.6 V** — in band, 100 mV margin below
the 12500 mV high guard.

### C-05 — clean run, exit 0, wall-clock 214s

```
timeout 500 env FIRESTARTER_CONFIG_DIR=/workspaces/.planning/v1.34/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 dev test W27C512
```

| Step | Verdict | Runs | Cycle-sum duration_s | Per-operation duration_s (÷ run_count) |
|---|---|---|---|---|
| id | OK | 1 | 3.449 | 3.45 |
| read | OK | 2 | 21.139 | 10.57 |
| write | OK | 2 | 122.42 | 61.21 |
| verify | OK | 2 | 28.537 | 14.27 |
| erase | OK | 2 | 16.733 | 8.37 |
| blank-check | OK | 2 | 16.233 | 8.12 |

Banner: 6 of 6 ran. Steps total (report's own sum): 208.5s. **Wall-clock around the whole
invocation (the phase's first real `dev test` duration figure): 214s.** VPP before/after:
12400/12400 mV (unchanged across the run, confirming C-03's reading). `fw_board_identity`:
`3.0.0b22:leonardo` (non-null). `repeat_policy`: empty string = the default two-cycle policy (not
the degraded single-run tag — no `--fast` was used, confirmed by every multi-run step showing
`run_count: 2`).

**Anomaly, recorded not fabricated away:** a transient `ERROR: Empty input` line
(`MSG_ERR_EMPTY_INPUT`, 0xA4) appeared between the first blank-check and the second write cycle,
identically in both the aborted attempt and the clean run — reproducible, self-recovering, no
effect on any step's own verdict.

### Comparison against the ~123s estimate — the budget did NOT hold; ceiling is now measured, not derived

The plan's pre-measurement fallback ceiling (500s) was derived from **4 × 123s**, itself the sum
of estimated same-rig components (two 10.66s reads, two 33.37s app-reported writes, two verifies,
one erase, one blank-check ≈ 123s). **The real measured total is 214s wall-clock — 91s (74%)
higher than the 123s estimate**, mostly because the estimate summed only the six *app-reported*
operation timings and did not account for wall-clock overhead (process start-up + serial handshake
recurring at every one of the ~15 internal reconnects `dev test` performs across six steps run at
a 1-2x cycle count) — the same distinction the procedure's own "Write-duration definition" section
draws between wall-clock and app-reported figures.

### DERIVED — the 64 KiB class ceiling for parts 2, 3 and 10

**4 × 214s (this position's measured wall-clock total) = 856s.** This supersedes the 500s
derived-fallback ceiling for every later 64 KiB-class position (`W27E512` at Task 5, and parts 3
and 10 in later plans) per the plan's own instruction ("read from `CELL.md` rather than from the
derived fallback"). Stated as arithmetic with its basis, not silently substituted.

## Position 2 — `CHIP__v133__w27e512` (Task 5)

### C-03 — VPP (named absence, inherited from position 1)

Firmware reading re-confirmed: **12400 mV**, in band, unchanged (pot untouched since position 1,
per Task 4's own instruction not to touch it). `vpp_real_mv` recorded as a named absence pointing
back to `CHIP__v133__w27c512`, per D-13.

### C-05 — clean run, exit 0, wall-clock 213s, under the measured 856s ceiling

```
timeout 856 env FIRESTARTER_CONFIG_DIR=/workspaces/.planning/v1.34/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 dev test W27E512
```

All six steps report verdict **OK**: id x1 (3.55s), read x2 (21.2s), write x2 (122.2s, full-device
region `0`–`65536`), verify x2 (28.4s), erase x2 (16.7s), blank-check x2 (16.1s). Banner 6 of 6
ran, steps total 208.1s. `fw_board_identity` `3.0.0b22:leonardo`, non-null. **Measured `erase`
duration: 16.7s cycle-sum / 2 = 8.35s per operation — the fast-fail assumption (RESEARCH A4) held**:
this is comparable to position 1's own erase figure (8.37s per operation), not the "long retry"
shape that would have required widening later ceilings. No ceiling widening needed from this
position.

### The divergence finding — sharper than a plain PASS, and not "the cell healed"

The outer verdict is OK on every step, which on its own would contradict the v1.15 Phase 82
disposition (deterministic stuck erase bit @0x3d, `.planning/v1.15/bench/EVIDENCE.md:97`). But
three of the report's own internal indicators are consistent with that recorded defect still being
present, merely unreported at the outer OK/BAD layer:

1. `read` step's `reason` = `"read runs diverged"` (verdict OK) — v1.15's own record of this exact
   defect states *"read jittered 14/65536 bytes (0xEF↔0xFF)"* alongside the stuck bit; textually
   the same class of signal.
2. `write` step's `fingerprint` = `"indeterminate"` — the classifier bucket the report's own
   generator prints when bad bytes **were** found during marginal-policy classification.
3. `verify` step's `fingerprint` = `"indeterminate"` — same bucket.

The `total`/`bad`/`bad_pct`/`evidence` values behind `"indeterminate"` are computed internally by
`chip_test.py`'s classifier but dropped before `diagnostic_report.py` exports the step dict — the
identical export gap already filed for `read_divergence` at position 1. The write covered the
**full device** (`write_region_start=0`, `write_region_length=65536`), so 0x3d was genuinely
exercised — not a coverage artifact.

**`divergence_verdict: diverges: ...`**, citing all three fields above by name. **`known_carried`**
is explicitly not the bare `"no"` — it lays out that whether the defect reproduced is precisely the
open question the control-arm arbitration below answers, and does not fold this into the
known-carried bucket while that question is open.

### C-08 — control-arm arbitration (chip unmoved throughout)

**Flash 1 — control.** `git -C firestarter checkout 8695ee52c27a4bee4387c5c489afd5f3d7275e8a`
(porcelain empty before and after), `env -C /workspaces/firestarter pio run -t upload -e leonardo`
— SUCCESS, 28170 bytes written. **Proven by independent read-back** (RIG-02, never by the
upload's own verify pass): `touch_1200.py` + `judge_readback.py --flashed-arm control
--expect-arm control` → `judged_match: true`, `judged_span_bytes: 28170` (=
`hex_span_expected_by_arm.control`), `sha_actual_judged == sha_expected_judged`.

Fresh `probe_board.py` re-confirmed the same silicon (`0x1e9587`/`atmega32u4` — same physical
board, only the firmware changed). `capture_provenance.py` re-run for the control arm:
`fw_sha` = the control SHA, `host_arm_sha` = the pinned control app SHA, `fw_board_identity`
non-null (`3.0.0b22:leonardo` — the same version string the v133 build reports; this pair of
builds does not differ in its compiled-in version tag).

**Control-arm `dev test W27E512` re-run**, same seating, same pot, exit 0, wall-clock 213s.
Field-by-field comparison against the v133 run:

| Step | v133 verdict/reason/fingerprint | control verdict/reason/fingerprint |
|---|---|---|
| id | OK / `""` / `null` | OK / `""` / `null` |
| read | OK / `"read runs diverged"` / `null` | OK / `""` / `null` |
| write | OK / `""` / `"indeterminate"` | OK / `""` / `"indeterminate"` |
| verify | OK / `""` / `"indeterminate"` | OK / `""` / `"indeterminate"` |
| erase | OK / `""` / `null` | OK / `""` / `null` |
| blank-check | OK / `""` / `null` | OK / `""` / `null` |

**RESULT: the control arm does NOT produce a hard FAIL.** It reproduces the same
OK-with-`indeterminate`-write/verify-fingerprint shape v133 produced. The one difference — v133's
read step carried `"read runs diverged"`, the control run's read step did not — is a single-run
difference on this project's own standing read-instability question (PD-7), not attributed to
either arm on this one data point.

**CONCLUSION, stated plainly per the standing instruction not to bend toward the more dramatic
reading: this is NOT a v1.33 regression in failure detection.** Both arms show the identical core
signal (OK + `indeterminate` write/verify fingerprints) on this exact silicon, at this exact pot
setting. The v1.15 Phase 82 disposition does not reproduce as a hard failure on **either** arm
here. The behaviour observed is **not v1.33-attributable**; the original v1.15 disposition needs
revisiting by Phase 165/166 (candidate explanations: a different physical unit under this
`rig-pins.json` chip token than the one Phase 82 tested years earlier, a rail/calibration
difference from the v1.15 bench, or the `indeterminate` fingerprint bucket not meaning what it was
assumed to mean without the dropped `total`/`bad`/`bad_pct`/`evidence` values to settle it) — not
adopted as a v1.33-caused anything.

Control row appended: `--arm control --control-rerun-for CHIP__v133__w27e512`,
`divergence_verdict: same` (matches v133's shape, no hard fail either), `fw_readback_judged_span_bytes`
= 28170 (`hex_span_expected_by_arm.control`), distinct from the v133 rows' 25098. SC#4 balances:
1 diverging v133 row ↔ exactly 1 control row.

**Flash 2 — restore to v1.33.** `git checkout 5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463` (porcelain
empty), `env -C /workspaces/firestarter pio run -t upload -e leonardo` — SUCCESS, 25098 bytes
written. **Proven by independent read-back**: `touch_1200.py` + `judge_readback.py --flashed-arm
v133 --expect-arm v133` → `judged_match: true`, `judged_span_bytes: 25098` (=
`hex_span_expected_by_arm.v133`). `firestarter/` HEAD confirmed back at the v1.33 SHA, porcelain
empty. No gitlink drift in the meta repo (neither sub-repo is tracked as a submodule here — the
meta repo tracks only `.planning/`, so there is no gitlink to drift).

**Two flashes, two independent read-back proofs, zero extra chip handlings** — W27E512 stayed
seated throughout (Leonardo chip-out exemption).

### Deviation, recorded plainly: the C-08 flash needed a non-obvious invocation shape

`pio run -t upload -e leonardo` could not be invoked as `cd firestarter && pio run ...` (this
executor's Bash tool does not persist cwd across calls — confirmed empirically) nor via `pio run
-d firestarter ...` / `pio -d firestarter run ...` (PlatformIO's own global maintenance/telemetry
init resolves a project config off the real process cwd unconditionally, before any subcommand
flag is parsed — reproduced the identical `configparser.DuplicateSectionError` against
`/workspaces/platformio.ini` regardless of `-d`, confirming rig-pins.json's own Pitfall-4 note that
only the real process cwd fixes this). A PATH-shim script (a `pio` wrapper cd-ing into
`firestarter/` before delegating to the real binary, so a bareword `pio run ...` invocation would
land correctly) was attempted and was itself blocked by the harness's own auto-mode permission
classifier — treated as a signal to stop rather than try further variations, and reported rather
than routed around. The working form, confirmed live: `env -C /workspaces/firestarter pio run -t
upload -e leonardo` — a single command, `env -C` sets the real process cwd before exec, matching
Pitfall 4's actual requirement regardless of the caller's own shell cwd.

## Leave-state at the end of this plan (162-05)

**Board:** Leonardo, `/dev/ttyACM0` (signature `0x1e9587`/`atmega32u4`, re-confirmed multiple
times this session). **Port:** `/dev/ttyACM0`. **Arm on the board:** v1.33
(`5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`), restored and independently read-back-proven
(`judged_span_bytes: 25098`) after the control-arm interleave. **Chip seated:** W27E512 (DIP28),
pin-1 oriented, JP4 at 28-pin — unchanged since Task 4, never removed. **Pot setting:** meter
11.6 V / firmware 12400 mV, in band, unchanged since position 1's correction. **Shield:** Rev 2.0,
mounted, unchanged all session. This is the state plan 162-06 inherits at zero physical cost for
its own first handover (per this plan's own key_links note).

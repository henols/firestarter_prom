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
- **VPP:** see `POT.md` for the full record — as-found 11.4 V (in band, 0 mV margin), a ~600 mV
  drift finding against Phase 161's A3/B2 12.0 V reading on this same rig/pot setting, and the
  pot re-adjusted to **11.97 V** (operative reading for the 12 V group, positions 1-8).

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

*(measured erase duration and fast-fail assumption check filled in after C-05/C-07)*

## Leave-state at the end of this plan (162-05)

*(filled in at the end of Task 5 — board, port, arm, chip seated, pot setting, shield state)*

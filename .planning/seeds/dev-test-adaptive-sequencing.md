---
title: dev test — adaptive, evidence-gated test sequencing
trigger_condition: Next milestone that touches `dev test` / chip_test.py. Explicitly NOT v1.35 (documentation-only). Natural carriers, whichever activates first: a `dev test` throughput milestone in its own right, or folded into the next chip-validation milestone that already has the engine open.
planted_date: 2026-08-30
status: dormant
---

# `dev test` — adaptive, evidence-gated sequencing

Make `dev test` **31% faster across the chip classes modelled, and 55–60% faster
on UV parts, while losing no diagnostic fidelity on any failing run.**

The engine today pays **worst-case diagnostic cost on every run**. It performs
the expensive diagnostics — full-device read-backs — unconditionally, whether or
not there is anything to diagnose. The fix is not to delete diagnostics; it is to
make each one *conditional on a cheap oracle failing*.

Measured evidence, primitive costs, the validated connect model and the four
waste patterns are in
[`../notes/dev-test-sequence-cost-model.md`](../notes/dev-test-sequence-cost-model.md),
with the executable model beside it as `dev-test-sequence-cost-model.py`. This
seed carries only the design.

## The four rules

### R1 — Never read what you can verify

`verify_eprom` streams host→device and the firmware compares
([`memory.cpp:377-396`](../../firestarter/src/proms/memory.cpp#L377-L396)).
Same byte coverage as a read-back, **24% cheaper**, no host file I/O, and it
early-returns on the first mismatch — so failing runs get *faster*, not slower.

Any place the engine reads the whole device back to compare it against a buffer
it already holds is a verify. This applies to the fingerprint read-backs; it does
**not** apply to the SDP leg, whose `_read_region` read-back *is* the verdict and
must stay a real read.

### R2 — Diagnose on failure only

Gate the fingerprint read-back at
[`chip_test.py:3100`](../../firestarter_app/firestarter/chip_test.py#L3100) on
`not all(outcomes)`.

- Passing run: **zero** read-backs.
- Failing run: **byte-identical** fidelity to today.

The `ff_ratio` false-PASS check that motivated the unconditional form is
preserved for free — a write that reports OK without driving the bus is caught by
the verify step immediately following it in the same cycle. **This dependency
must be asserted structurally**, not assumed: if a future plan ever emits a write
without a verify behind it, that plan needs the unconditional read-back back.

Note the pleasing asymmetry: because verify early-returns on first mismatch, the
runs that now pay for a read-back are exactly the runs whose verify was cheapest.

### R3 — Sample for a rate, sweep for a map

Read-repeatability is a **statistical** property, and so is `ff_ratio`. Both are
currently established by full-device sweeps.

Replace the read step's second full run with a **bit-structured sample**: one
256 B block at each `1 << k` boundary for `k` in `8..log2(size)`, plus block 0
and the top block. For a 64 KiB part that is 10 blocks / 2560 B, and it toggles
**every address line in both polarities** — which is precisely the structure
`classify_fingerprint` looks for when it clusters mismatch offsets by high
address bit. A contiguous sample would not do this; the bit-structure is the
whole point.

Escalate to the full second read only when the sample diverges, so exact
divergence counts (`cmp_len`, `bad`, `pct`, `first_offset`) survive intact on
every run where they mean anything.

**Cost, stated:** on a passing run the divergence metric becomes an *estimate*
over a sampled subset rather than an exact whole-device count. A scattered
transport fault — the uno328pb signature, and the only fault class this metric
was built to catch — is caught with high probability by any sample of this size,
because scatter is what makes it detectable. A fault confined entirely to
unsampled bytes would be missed on the first pass; the bit-structured stride is
chosen to make that region small and address-line-aligned rather than arbitrary.

### R4 — One session per plan, not one per call

`run_plan` is the natural connection boundary; `EpromOperator.comm` is currently
torn down after every operator call. Counts are 22 for sst27sf512 and **32 for
at28c256**, whose six-op SDP leg alone costs 12 connects for ~3 KB of traffic.

Cheaper, strictly-additive sub-step available independently: fold `sample_vpp_mv`
and `sample_vpe_mv` into one monitor read (−2 connects per write step).

**Per-connect cost is unmeasured** — the counts are validated, the seconds are
not. Anyone planning this should measure a connect first and let that decide how
much R4 is worth relative to R1–R3.

## Projected effect

From the model (`dev-test-sequence-cost-model.py`), `runs=2`:

| Chip | Class | Now | Proposed | Saved |
| --- | --- | --- | --- | --- |
| sst27sf512 | EEPROM full-device | 121.8s | 92.7s | **23.9%** |
| w27c512 | EEPROM full-device | 121.8s | 92.7s | **23.9%** |
| at28c256 | EEPROM + SDP leg | 61.3s | 47.3s | **23.0%** |
| m27c512 | UV, 256 B slot | 25.4s | 11.2s | **55.8%** |
| am27c020 | UV, 256 B slot | 99.6s | 40.4s | **59.5%** |
| w29c040 | flash4, 480 KiB | 769.3s | 537.5s | **30.1%** |

UV parts gain most because their write is 256 bytes — the run is almost entirely
preflight overhead. W29C040 saves nearly four minutes per run.

These figures exclude connection overhead entirely (unmeasured), so R4's
contribution is **not** in the table. They also assume the sampled preflight;
R1+R2 alone deliver roughly two thirds of each row.

## Per-class characteristics that must survive

The whole point of `dev test` is that the plan is derived per chip. Nothing here
may flatten that:

- **UV-EPROM** — keeps its full-device blank-check (blankness is an
  operator-actionable finding, and blank-check is the *cheapest* primitive per
  byte, so there is no reason to sample it), its top-down slot probe, and its
  tranche staging across cycles.
- **SRAM/FRAM** — keeps `CYCLE_PAYLOAD_ALTERNATE`; a volatile part has no blank
  state and needs the 0→1 transition the alternating payload forces.
- **flash4 / W29C040** — keeps the boot-block carve-out and its NA erase and
  blank-check.
- **AT28C256 / SDP leg** — untouched by R1 and R2. Its `_read_region` read-back
  is a verdict, not decoration, and its length gate and degeneracy gate depend on
  getting real bytes back. R4 is the only rule that helps here, and it helps a
  lot.
- **`--fast`** — unchanged in meaning. It stays the weaker single-run mode and
  must keep re-keying `dedup_fingerprint` through `repeat_policy_tag`.

## Sequencing note

R2 is small, self-contained and worth ~24% on its own — it is filed separately as
todo `2026-08-30-gate-fingerprint-readback-on-step-failure.md` so it can land
without waiting for the rest. R1 and R3 are engine changes with real test
surface. R4 is the largest structural change and the only one whose payoff is
currently unquantified.

## Explicitly out of scope

The write path's 2.2 KB/s — 65% of a full-device run — is the per-byte VPE settle
behaviour and is a firmware concern. No rule here touches it, and no figure above
claims it improves.

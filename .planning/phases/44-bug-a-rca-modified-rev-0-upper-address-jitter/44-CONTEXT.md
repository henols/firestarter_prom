# Phase 44: Bug A RCA — Modified Rev 0 Upper-Address Jitter - Context

**Gathered:** 2026-05-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Prove the Modified Rev 0 `A15=1` upper-address read jitter to a **specific, controllable mechanism** — going beyond the Phase 29 v2 symptom characterization (1.86× A15 skew, 1.31% byte disagreement, 63% bit-raise, +8.89 mean delta). Deliver a controlled pre-fix baseline on Modified Rev 0 and start the per-rev failure-mode map.

**In scope:** Modified Rev 0 board only. Static circuit inspection of its mods; host-tunable firmware instrumentation (settling + strobe knobs); causal sweep + `dev consistency-check` baseline; documented root-cause evidence; per-rev map *started* (Modified Rev 0 → Bug A; Rev 2.2 entry recorded).

**Out of scope (other phases):** Bug B / Rev 2.0 RCA (Phase 45); the actual fix (Phase 46); Rev 2.2 *physical bench test* (Phase 45); acceptance gate re-run (Phase 47); COBS/TYPE cleanup (Phase 48).
</domain>

<decisions>
## Implementation Decisions

### Investigation sequence
- **D-01:** **Static circuit first.** Before any sweep, inspect the Modified Rev 0 modifications with multimeter + v1.7 schematic — checking for missing series termination on A15, data-bus pull-down resistor values, and supply sag — to form a *specific* hypothesis. The sweep then confirms it causally.
- **D-02:** The Modified Rev 0 mods are treated as the prime suspect (it is a hand-modified board) and are **documented in the v1.7 shield-revisions docs**; the static check verifies the physical board matches that documented mod record.

### Primary evidence path
- **D-03:** **Firmware sweep = the causal lead.** Root cause is proven by *manipulation*: vary the timing knob(s), re-run the diagnostic, and show the jitter rate moves. LA / scope / multimeter captures are corroborating evidence, not the headline.
- **D-04:** The sweep varies **both** (a) address-settling delay (NOPs/µs after address set, before data latch — the lever parked at `4f205e58` in Plan 28-04) **and** (b) read-strobe (`/OE` or `/CE`) pulse width. 2D sweep space.
- **D-05:** Both knobs are exposed as **host-tunable dev parameters** (serial param / dev command), swept from the host **with the chip seated** — NO re-flash and NO chip reseat between data points. This is mandatory: reseating per point would inject the very signal-integrity variance being measured, and violates the chip-out-before-sideload rule on every point.

### Proven bar (governs RCA-01 closure + verification)
- **D-06:** **Causal-only bar.** RCA-01 closes when a timing knob drives the upper-address jitter to ~zero (a controllable cause = an actionable Phase 46 fix target). Localization of the effect to the A15=1 / upper-24KB population and an operator-witnessed LA/scope capture are **corroborating, not gating**.
- **D-07:** D-06 **governs over** the ROADMAP Phase 44 success-criterion-1 wording ("identifies the *specific electrical cause* … not merely the symptom"). The verifier should treat "a demonstrated knob that controls the jitter" as sufficient, with mechanism-naming a stretch goal. *(Flagged tension — recorded intentionally so the verifier does not over-block.)*

### Instrumentation reality
- **D-08:** Bench instruments available: a **simple (low-bandwidth) scope**, an **8-channel logic analyzer**, and a **multimeter**. No high-bandwidth analog scope. The LA is the strongest *witness* tool here — it can capture A15/A14/A13 + the read strobe (`/OE`, `/CE`) + a couple of data lines simultaneously to see whether A15 is still settling/glitching when the strobe latches. The simple scope covers gross analog ringing/levels on the single worst line; the multimeter covers static DC (termination, pull-down values, VPP, supply sag).
- **D-09:** Physical probing (scope/LA/multimeter/photos/chip-handling) is **operator-only**; Claude drives firmware sideload, host reads, serial, and the sweep automation. Per-port `controller:` identity is verified at each bench task; operator confirms the silkscreen rev when the board goes on the bench.

### Per-rev map scope
- **D-10:** **Rev 2.2 deferred to Phase 45.** Phase 44 records the Rev 2.2 map entry as "untested — predicted clean per v1.7 capability matrix"; the real Rev 2.2 bench run happens in Phase 45 when that shield is already on the bench for the full per-rev map.

### Baseline-repro rigor (Claude's discretion — defaults)
- **D-11:** Controlled pre-fix baseline = re-run `dev consistency-check` at **N=5** on the **same Leonardo board / W27C512 / port** as the Phase 29 v2 substrate, and **byte-compare against the 15 captured binaries** to confirm bench continuity (WORST ≥ 1% zeros, A15 skew reproduced) before any knob change. Operator may raise N if tighter stats are wanted.

### Claude's Discretion
- Baseline-repro rigor (D-11) — defaulted, open to operator override.
- Where RCA evidence/docs are written (meta `.planning/` vs `firestarter/doc/`), and whether the sweep knobs ship as a dev-command vs build-flag — left to planning/research, subject to the chip-seated/host-tunable constraint (D-05).
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Bug A characterization + baseline substrate
- `.planning/v1.6-EVIDENCE.md` — Phase 29 v2 block: full Bug A characterization (1.86× A15 skew, 1.31% disagreement, 63% bit-raise, +8.89 mean delta, upper-24KB concentration) + SHA-256s of the 15 baseline binaries. **The richest empirical evidence for this RCA.**
- `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` — the 15 captured N=5 W27C512 binaries to byte-compare the new baseline against (D-11).

### Shield mod record (static-check reference — D-01/D-02)
- `.planning/v1.7-SHIELD-REVS.md` — investigation-canonical mod record (full 9 sections), incl. §8/§9 per-rev capability matrix + Detect-HW schematic delta. **⚠ NOT on the current working checkout** — its commits live on an unmerged branch; recover via git before the static inspection.
- `firestarter/doc/SHIELD-REVISIONS.md` — operator-canonical subset (on firestarter `beta` @ `59a5e58`). **⚠ submodule currently at `efd203a`** (predates this doc). The two are kept in lockstep.

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — RCA-01 (Bug A root cause proven), RCA-03 (per-rev map, Modified Rev 0 portion).
- `.planning/ROADMAP.md` — Phase 44 goal + 4 success criteria (note D-07 relaxes criterion 1).

### Prior-art / parked lever
- Firmware commit `4f205e58` (Plan 28-04, parked) — the `_NOP()` address-settling lever; insufficient alone but the seed for the D-04 settling knob.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `firestarter_app/firestarter/eprom_operations.py` + `serial_comm.py` + `cli_handlers.py` — the host side of `dev consistency-check` (WORST/zeros jitter metric). Reuse as-is for baseline (D-11) and per-sweep-point runs; the sweep harness drives it once per knob setting.
- `firestarter/src/dev_tools.cpp` — firmware dev-command surface; likely host of the new host-tunable settling + strobe knobs (D-05).
- `firestarter/src/eprom_operations.cpp` — firmware read path where address-settling and the read strobe live (the knobs instrument this path).

### Established Patterns
- Constants/flag bits are duplicated `constants.py` ↔ `firestarter.h`; serial protocol is duplicated `serial_comm.py` ↔ `firestarter.cpp` — any new dev param/flag for the knobs must be changed in BOTH (per CLAUDE.md).
- v1.8 GATE-1.8d ring-fenced the read path; baselines remain valid. TYPE-01 (lift `eprom_operations.py` mypy overrides) is explicitly Phase 48, not here.

### Integration Points
- The sweep knobs cross the serial protocol boundary (host sets param → firmware applies in read path). Leonardo (1024-byte buffer) is the baseline board.
- v1.9 firmware/host work expects v1.9-slug branches forked **off beta** in both sub-repos (vs v1.8's host-only scope) — see flagged prerequisite below.
</code_context>

<specifics>
## Specific Ideas

- The 8-channel LA capture should be set up to trigger on (or align with) A15=1 read accesses so the A15-vs-strobe timing relationship is directly visible — the single most informative witness given no high-bandwidth scope.
- The "weak data-bus pull-down on tristate glitch" sub-hypothesis (from the 63% bit-raise) was *not* dropped — but under D-01 (static-first) it is checked via multimeter on the data-bus pull-downs during the static pass rather than chased as a separate dynamic track. If the static pass finds the smoking gun there, it may short-circuit the sweep.
</specifics>

<deferred>
## Deferred Ideas

- **Rev 2.2 physical bench test** (`dev consistency-check` run) → Phase 45, as part of completing the per-rev failure-mode map.
- **Naming the single dominant electrical mechanism** + ruling out alternatives (ringing vs settling vs crosstalk vs supply sag) → stretch goal beyond the D-06 causal-only bar; pursue only if cheap once causality is shown.

### Prerequisite (not a deferral — must resolve before bench/firmware work)
- The v1.9 firmware branch must be **forked off `beta`** in `firestarter/` (and `firestarter_app/`) so the v1.7 shield docs + firmware substrate are present on the working tree. The submodule is currently at `efd203a`, predating both the v1.7 `doc/SHIELD-REVISIONS.md` and the firmware substrate the static check (D-01/D-02) verifies against.
</deferred>

---

*Phase: 44-bug-a-rca-modified-rev-0-upper-address-jitter*
*Context gathered: 2026-05-29*

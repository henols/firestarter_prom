---
phase: 160
slug: rig-dual-arm-build-flash-provenance-the-shared-cell-procedur
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-26
---

# Phase 160 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `160-RESEARCH.md` § "Validation Architecture". Every figure below was
> measured in the devcontainer during research unless the row says otherwise.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | **None.** The meta repo has no `pyproject.toml`, no `pytest.ini`, no `tests/`, and `pytest` is not importable from `python3`. Do not introduce one — this phase adds no package. |
| **Established convention** | Standalone `python3` gate scripts: `def main() -> int` + `raise SystemExit(main())`, asserted by **exit code**. Precedents: `.planning/v1.18/bench/check_{verdict,graduation,signature,pre01,diff07}.py`, `.planning/phases/145-bench-validation/tools/extract_frames.py`, `.planning/phases/145-bench-validation/images/gen_addr_image.py`. |
| **Config file** | none — each gate is invoked explicitly by path |
| **Quick run command** | `python3 .planning/v1.34/tools/<gate>.py [args] ; echo rc=$?` |
| **Full suite command** | `bash .planning/v1.34/tools/run_gates.sh` — runs every gate, fails on the first non-zero. **Does not exist yet; Wave 0 creates it.** |
| **Bin-level oracles** | `sha256sum` + `cmp` + `stat -c%s`, exactly as the `SHA256SUMS.txt` precedent does |
| **Estimated runtime** | Host-side gates: seconds. On-device legs: bounded by the bench, not by the suite — measure and record during bring-up. |

---

## Sampling Rate

- **Per task commit:** the gate(s) that task touches, exit code asserted.
- **Per wave merge:** `run_gates.sh` — every gate green.
- **Phase gate, before `/gsd-verify-work`:** `run_gates.sh` green **and** both falsification tests **observed**, not merely authored —
  - D-03: the deliberate wrong-arm cross-flash MISMATCH recorded on **all three** targets, plus the corrected match;
  - D-17: reconstruction of the bring-up run from the record alone, diffed against the prescription.
- **Max feedback latency:** host-side gates must stay under ~10 s each; no three consecutive implementation tasks may lack an automated check.
- **Gate birth rule (standing project discipline):** every gate above is observed **red** against a deliberately broken input — a truncated read-back, a null provenance field, a hand-edited `EVIDENCE.md`, an `outcome: inconclusive` — before it is trusted green. A gate written but never seen to fail proves nothing in this repo (`reference_gate_authored_before_content_can_be_unreachable`, and `check_permitted_claims.py` which scanned nothing and exited 0).

---

## Per-Task Verification Map

*Filled by the planner — one row per task, referencing the requirement → test map below.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 160-01-01 | 01 | 1 | RIG-01 | — | — | integration | *(planner fills)* | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

### Requirement → test map (research-measured)

| Req | Behavior | Test type | Automated command | Exists? |
|-----|----------|-----------|-------------------|---------|
| RIG-01 SC#1 | six images build from named SHAs; each has a recorded hash | integration | `cd /workspaces/firestarter && rm -rf .pio/build/$E && pio run -e $E` then `sha256sum -c SHA256SUMS.txt` | ✅ mechanism verified (`uno`, byte-identical, 2.04 s) |
| RIG-01 SC#1 | rebuild reproduces the hash, or the divergence is recorded with a measured cause | integration | `python3 tools/check_rebuild.py --images … --expect SHA256SUMS.txt` | ❌ Wave 0 |
| RIG-01 SC#2 | read-back over the hex extent equals the flashed image | integration, on-device | `python3 tools/judge_readback.py --hex … --readback … --objcopy …` | ❌ Wave 0 |
| RIG-01 SC#2 | the check is **proven able to fail** | falsification, on-device | the D-03 cross-flash: same `judge_readback.py`, **observed** non-zero, artifact committed | ❌ Wave 0 — must be observed red, not authored |
| RIG-03 SC#3 | the two arms' step lists diff empty | unit | `diff <(render_steps.py --arm control) <(render_steps.py --arm v133)` must be empty | ❌ Wave 0 |
| RIG-03 | the two arms' CLI surfaces are identical | unit | AST / `--help` diff across all 25 commands | ✅ AST diff already measured empty both directions; the `--help` variant is Wave 0 |
| RIG-04 | full-device SHA equality vs the written image, never an exit code | integration, on-device | `python3 tools/judge_wrv.py --written … --reads … --expect-size 65536\|262144` | ❌ Wave 0 |
| RIG-04 | N=3 resolving to one SHA; a disagreement recorded as a disagreement | integration, on-device | same tool; counts `run_*.bin` (fewer than N on a hw error) and emits `disagreement` rather than retrying | ❌ Wave 0 |
| RIG-02 / RIG-05 | every required provenance field present and non-null | unit | `python3 tools/gate_record.py <cell>/provenance.json` | ❌ Wave 0 |
| RIG-05 | every recorded command line re-parses into the prescribed set | unit | same gate: assert `argv[0]` ∈ {the two absolute arm binaries}; reject bare `firestarter` | ❌ Wave 0 |
| RIG-05 | reconstruction from the record alone matches the prescription | manual, once | fresh context given only the bring-up record + PROCEDURE.md; output diffed against the prescription (D-17) | ❌ Wave 0 — manual by design; automating it defeats its purpose |
| D-18 | no cell outcome is ever `inconclusive` | unit | `gate_record.py` asserts `outcome ∈ {validated, skipped-with-reason}` | ❌ Wave 0 |
| D-15 | `EVIDENCE.md` is byte-identical to a fresh render of `EVIDENCE.jsonl` | unit | `render_evidence.py --check` | ❌ Wave 0 — this is what makes "never hand-edited" enforceable rather than aspirational |
| D-07 | the shared config dir is unchanged after each cell | unit | recompute the tree SHA, compare against the recorded value | ❌ Wave 0 |
| Pitfall 8 | the two arm venvs resolve identical dependency versions | unit | `diff` of the two `pip freeze` outputs must be empty | ❌ Wave 0 |

---

## Wave 0 Requirements

- [ ] `.planning/v1.34/tools/run_gates.sh` — the "full suite" runner; does not exist
- [ ] `tools/judge_readback.py` — RIG-01 SC#2 (`-A` read, `avr-objcopy` normalize, span compare, whole-flash datum recorded unjudged per D-02)
- [ ] `tools/judge_wrv.py` — RIG-04 (full-device SHA, file-count guard, app-verdict disagreement flag)
- [ ] `tools/capture_provenance.py` — RIG-02 / RIG-05 (`--shield-rev` required-or-refuse; `python -P` on the `__file__` probe per Pitfall 1)
- [ ] `tools/gate_record.py` — D-17 script gate (field presence + command re-parse + `outcome` domain)
- [ ] `tools/render_evidence.py` — D-15, with a `--check` mode so "never hand-edited" is enforced
- [ ] `tools/probe_board.py` — D-14 signature probe, both parse routes, plus `-xshowvector` on `uno328pb` (Pitfall 3)
- [ ] `tools/touch_1200.py` — Leonardo bootloader entry (pyserial)
- [ ] `tools/gen_addr_image.py` — copied from Phase 145 with its D-16 boundary comment intact; stamp-width decision made before generating images (16-bit stamp repeats every 64 KiB on the 256 KiB W29C020)
- [ ] `tools/check_rebuild.py` — SC#1's reproduce-or-record-the-cause clause

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Reconstruction of a cell run from the record alone | RIG-05 SC#5 (D-17) | Automating it would let the record's author also be its reader — the whole point is that a party with no session memory can rebuild the run | Give a fresh context only the bring-up record + `PROCEDURE.md`; have it emit the command set and physical setup; diff against what the procedure prescribes; **zero fields may come from session memory** |
| Chip insertion / removal, photography, multimeter readings, pot adjustment | RIG-02, RIG-03 | Standing bench rule — operator-only | `PROCEDURE.md` names the operator step and the single reading; Claude drives serial/CLI only (Phase 145 D-19) |
| Shield revision declaration | RIG-05 | `hw_revision` cannot distinguish Rev 2.2 / Rev 2.0 / modified Rev 0; the A3 ADC check collides on 10 kΩ | Operator declares it; `capture_provenance.py` requires `--shield-rev` and refuses to infer |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Every gate observed **red** once against a deliberately broken input
- [ ] Both falsification tests (D-03 cross-flash, D-17 reconstruction) observed, not authored
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

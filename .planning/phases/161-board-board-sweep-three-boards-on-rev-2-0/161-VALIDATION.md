---
phase: 161
slug: board-board-sweep-three-boards-on-rev-2-0
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-27
---

# Phase 161 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `161-RESEARCH.md` § Validation Architecture (line 1230).

This is a **hardware evidence phase**, not a software-feature phase. It ships no product code —
both submodules stay byte-unchanged. There is no unit-test framework in the ordinary sense: the
"tests" are the rig's own gates plus the 12 evidence positions.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `bash .planning/v1.34/tools/run_gates.sh` — 11 Python `--selftest` suites + 5 live gates |
| **Config file** | `.planning/v1.34/rig-pins.json` (constants) + `bench/EVIDENCE.jsonl` line 1 (`_schema`) |
| **Quick run command** | `bash .planning/v1.34/tools/run_gates.sh --quick` (skips `check_rebuild` / `check_arms` only) |
| **Full suite command** | `bash .planning/v1.34/tools/run_gates.sh` |
| **Estimated runtime** | quick ~seconds; full suite ~1 min (dominated by the two rebuild/arm gates) |

**Exit-code discipline (binding):** measure `run_gates.sh`'s exit code **directly, never through a
pipe**. Baseline measured green during research: 11/11 selftests, 5/5 live gates, `EXIT=0`.

**Wave 0 will add a 12th tool** (`append_evidence.py`, D-05). `run_gates.sh` discovers every `*.py`
under `tools/` and **fails the suite** if one does not advertise `--selftest` — so the new tool's
selftest is not optional, and the suite becomes 12/12 the moment the file lands.

---

## Sampling Rate

- **Per position** (12x): `judge_wrv.py` (the oracle) → `append_evidence.py` → `render_evidence.py`.
  Records are written as each position completes (D-03), so a kill mid-cell leaves a consistent,
  resumable state.
- **Per cell / per wave** (3x — D-01 makes a wave equal a cell, D-04 designates the gate):
  full `bash .planning/v1.34/tools/run_gates.sh`, exit code measured directly.
- **Before `/gsd-verify-work`:** full suite green **and** all 12 rows present in `EVIDENCE.jsonl`.
- **Max feedback latency:** one position (~5–20 min, chip-dependent). This is bench-bound, not
  compute-bound; the ceiling is set by D-08's stall kill, not by the gate.

---

## Per-Task Verification Map

Per-task rows are populated by the planner — this phase's tasks do not exist until `*-PLAN.md`
files are written. The requirement-level map below is the contract those rows must satisfy.

| Req | Behaviour that must be TRUE | Type | Automated command | Infra exists? | Status |
|-----|-----------------------------|------|-------------------|---------------|--------|
| BOARD-01 | A1's 4 positions each hold a verdict or a **named** absence | evidence | `gate_record.py --jsonl bench/EVIDENCE.jsonl` + row-count assertion over `cell_id == "A1"` | ✅ (row filter is new, trivial) | ⬜ pending |
| BOARD-02 | A2's 4 positions; the failure **observed** on both arms, not asserted from Backlog 999.2 | evidence + human | same, plus each A2 row's `verdict` naming the observed stop point and exact host output | ✅ / prose is human by D-05 | ⬜ pending |
| BOARD-03 | A3/B2's 4 positions | evidence | same, filtered on `cell_id == "A3/B2"` | ✅ | ⬜ pending |
| BOARD-04 | A measured write duration on every position | evidence | assert `write_duration_wallclock_s` non-null on all 12 rows (a real float **or** the `"not measured — <reason>"` shape) | ✅ via `gate_record.py` field presence | ⬜ pending |
| SC#2 | Provenance captured **before** the cell's first test step; arm confirmed by on-device read-back | mechanism | `captured_at_step == 2` on all 12 `provenance_*.json`; `READBACK-VERDICT.judged_match == true` per flash | ✅ | ⬜ pending |
| SC#5 | A3/B2 executed exactly once in the milestone | arithmetic | exactly 4 rows with `cell_id == "A3/B2"`, one per (arm x chip); `render_evidence.append_row_to_file` structurally refuses a duplicate `position_id` | ✅ | ⬜ pending |
| D-05 | Zero machine-readable fields transcribed by hand | mechanism | `append_evidence.py --selftest` — negative legs must **refuse** a field taken from the wrong position's provenance | ❌ **Wave 0** | ⬜ pending |
| Amendment 3 | The procedure stays arm-agnostic after the edit | gate | `render_steps.py --arm control` vs `--arm v133` diff empty (3rd live leg of `run_gates.sh`) | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `.planning/v1.34/tools/append_evidence.py` — the tool itself (D-05). Derives every
      machine-readable field from `provenance_<position>.json`, `WRV-VERDICT.json` and
      `READBACK-VERDICT.json`; only 5 of the 40 schema columns are human-supplied.
- [ ] Its `--selftest`, with **named negative legs**, not just a happy path:
      missing `WRV-VERDICT.json`; `position_id` disagreeing across the three artifacts;
      `image_sha` != `written_sha`; a bare `not measured` in `blank_state`; an empty `verdict`;
      `outcome` derived as `validated` while `sha_verdict_judged != "match"`.
- [ ] `PROCEDURE.md` **Amendment 3** (research recommends four clauses: D-06 per-position append,
      D-12 leave-state, per-position artifact paths, `~/.firestarter` baseline restatement) plus a
      `run_gates.sh` re-confirmation that the `render_steps` arm diff stays empty.
- [ ] `bench/.gitignore` extension **if** per-position `written.bin` moves out from under
      `cells/*/written.bin` (measured with `git check-ignore`; not needed if `written.bin` stays
      under `reads/<pos>/`).

---

## Manual-Only Verifications

The operator-physical steps. Per CONTEXT D-02 — *"I dont want any handover until a real physical
action is needed"* — `human-verify` checkpoints belong at these steps and **nowhere else**.

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Shield mounted on the correct board; silkscreen revision declared | SC#2 | `hw_revision` cannot distinguish Rev 2.2 / Rev 2.0 / modified Rev 0 — the operator reads the silkscreen | `P-01`; `capture_provenance.py` refuses to run without an operator-declared shield revision |
| Chip OUT before an Uno-class sideload / signature probe | safety | Physical socket action; Uno-class chip-out rule (Leonardo exempt) | `P-03` — and, per research Pitfall 6, also **before `P-02`** on A1/A2, because `probe_board.py` is an avrdude signature probe |
| Chip 1 seated (W27C512, DIP28) | BOARD-01…03 | Physical socket action, pin-1 orientation | `P-05` |
| VPP pot set to 12.0 V | BOARD-01…03 | Operator adjusts the pot solo — state the target, wait, take ONE read | `P-06` (single confirming `vpp` read; never a monitor loop) |
| Chip 2 swapped in (W29C020, DIP32) | BOARD-01…03 | Physical socket action, different package width | `P-08` |
| The above repeated across the arm switch | SC#1 | Same physical actions, second arm | `P-10` |
| A2's observed failure symptom — where the program stops, what the host printed | BOARD-02 / SC#3 | Prose observation; D-05 leaves `verdict` and `anomalies` human by design | Recorded into the position's row as the human fields |

---

## Claims This Phase CANNOT Validate — record as non-claims

1. **Any electrical claim.** Program-window VPP/VCC *under load* stays unmeasured (DTR-reset-on-close
   tooling gap). v1.34 makes no electrical claim.
2. **8 bytes on uno328pb.** Under `vector-exclusion`, `[0,4)` and `[100,104)` — 8 of 26074 judged
   bytes — are excluded from every comparison. A fault confined to those 8 bytes is invisible on A2.
   *(Disclosed §6 limit — carry it, do not re-raise it.)*
3. **A duration-to-spread comparison against v1.31.** v1.31's 0.37 s is a *spread* (max−min across
   three app-reported figures), not a duration. Also: v1.34's ~3x faster W27C512 figures are PR #55's
   VPE-settle amortisation, present in **both** arms — not a v1.33 effect.
4. **Python 3.11.** Both arms run devcontainer 3.12.14, not the app-CI floor. *(Disclosed §6.)*
5. **Stable-channel reachability.** `dev consistency-check` is in `BETA_ONLY_DEV_COMMANDS`; the
   judged SHA is unaffected, but the read-set command is a dev-channel-only surface. *(Disclosed §6.)*
6. **Byte-level re-check of a clean position.** A clean-match read set is re-checkable by SHA only —
   the bytes stay local unless the position failed, in which case they are committed with `git add -f`.
7. **Cause.** This phase *records*. Phase 165 classifies and fixes, on the v1.33 PR branch.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify legs or a Wave 0 dependency
- [ ] Every `<automated>` leg's constants are **arm-aware** — `hex_span_expected_by_arm`, never the
      legacy scalar `hex_span_expected` (Phase 160 recorded this defect recurring 4x; 12 positions
      means one wrong constant is twelve false results)
- [ ] Sampling continuity: no 3 consecutive tasks without an automated verify
- [ ] Wave 0 covers all MISSING references (`append_evidence.py` + its selftest, Amendment 3)
- [ ] No watch-mode flags; no `run_gates.sh` exit code read through a pipe
- [ ] `human-verify` appears at P-01 / P-03 / P-05 / P-06 / P-08 and their P-10 repeats — nowhere else
- [ ] This phase must **not** run under `--auto` / `--chain` / any auto-advance mode (Standing bench
      rule 7): those auto-approve the very checkpoints every physical step depends on, and
      `autonomous: false` on a plan is not self-protecting against that
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

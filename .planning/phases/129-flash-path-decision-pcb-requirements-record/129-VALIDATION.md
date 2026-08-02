---
phase: 129
slug: flash-path-decision-pcb-requirements-record
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-02
---

# Phase 129 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `129-RESEARCH.md` §"Validation Architecture".

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` — firmware repo, `firestarter/tests/` (stdlib + pytest only) |
| **Config file** | **none** — no `conftest.py`, `pytest.ini`, `pyproject.toml`, `setup.cfg` or `tox.ini` anywhere in the firmware repo. Per-module path resolution is the house convention (see `tests/test_vpp_seam_manual_on_every_board.py` docstring). |
| **Quick run command** | `python -m pytest tests/test_flash_path_record_sync.py -v` |
| **Full suite command** | `python -m pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds (quick) / ~30 seconds (full, 21 existing modules + 1 new) |

**CI status — must be stated in the new module's docstring.** This module will run in **NO CI leg on this branch**. `pytest tests/ -v` exists only in `build.yml` (main) and `beta-build.yml` (beta); `py32f071.yml` — the only workflow that fires here — has no pytest step. **The local run is the evidence.** Same disposition as Phase 126's `test_config_storage_design_vendored.py`.

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/test_flash_path_record_sync.py -v`
- **After every plan wave:** Run `python -m pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite green **plus** the D-13 byte-identity sequence re-run on the final tree, both recorded in `129-NONREGRESSION.md`
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

Task IDs are assigned by the planner; rows below are the requirement-level contract each task must land against.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | 0 | D-03 | T-129-03 | A parse returning empty must fail, never compare-equal | unit | `pytest tests/test_flash_path_record_sync.py::test_shared_sections_match -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 0 | D-03 | T-129-03 | Planted mutation is detected (RED demonstration) | unit | `…::test_planted_mutation_is_detected -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 0 | D-03 | T-129-03 | Gate cannot pass vacuously or skip silently (5 F-14 modes) | unit | `…::test_*_non_vacuous`, `…::test_absent_meta_is_not_a_silent_skip`, `…::test_missing_target_raises` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | PCB-01 | — | Both copies name all three tiers + the non-retirement sentence | content gate | `…::test_three_tiers_and_non_retirement -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | PCB-02 | T-129-06 | Every checklist row is `- [ ]` + rationale line + breaks-if line (D-16); all named items present incl. F-10's package row | structural gate | `…::test_pcb_checklist_rows_are_wellformed -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | PCB-03 | — | Record contains literal reserved addresses (`0x08000000`, `0x0801E000`, `120K`, `8K`, `256`, `8192`) | content gate | `…::test_flash_budget_cites_reserved_map -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | PCB-03 | T-129-05 | Bootloader figure never appears without its migration cost within N lines | proximity gate | `…::test_bootloader_figure_carries_its_cost -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | PCB-03 | T-129-05 | Linker comment names the record's filename (D-11) **and no longer says "no VTOR"** (C-1) | cross-file gate | `…::test_linker_comment_cross_references_record -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | PCB-03 | — | The linker-comment edit changes no emitted byte (D-13) | build delta | `sha256sum` before/after sequence (RESEARCH §Pattern 3) | ✅ proven in C-3 | ⬜ pending |
| TBD | TBD | — | PCB-04 | T-129-01 | Record names `0x1209` + interim `1209:0001`, the ship gate, and cites `0x36B7`'s Puya provenance | content gate | `…::test_vid_pid_decision_and_ship_gate -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | PCB-05 | — | Socket-empty instruction present in the firmware copy, states the provisional-pin-map reason | content gate | `…::test_socket_empty_instruction_present -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | D-17 | — | Seed frontmatter `status:` no longer `dormant`, points at the record | content gate | grep assertion — meta-side, or firmware-side via the meta-presence helper | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter/tests/test_flash_path_record_sync.py` — the D-03 sync gate, covering PCB-01…PCB-05 content assertions and the five F-14 fail-open modes
- [ ] `firestarter/tests/meta_presence.py` — meta-repo presence helper mirroring `firestarter_app/tests/fw_presence.py` (unrenameable marker, `FIRESTARTER_META_ROOT` seam, `MissingScanTargetError`)
- [ ] Toolchain install for D-13's evidence, if executors run in a fresh container:
      `sudo apt-get install -y --no-install-recommends gcc-arm-none-eabi libnewlib-arm-none-eabi libstdc++-arm-none-eabi-newlib && pip install cmake ninja`
- [ ] No framework install needed — pytest is already used by 21 modules

---

## Manual-Only Verifications

No gate can judge these. They belong in UAT; Phase 130's CLOSE-02 honesty ledger consumes them.

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The rationale lines are useful to a schematic author | PCB-02 | Usefulness is a judgement, not a string match | Read the checklist as if starting a schematic; can each row be acted on without further research? |
| The rejected-route table is fair | PCB-01 | Fairness of a comparison is not machine-checkable | Check each rejected route states a real cost, not a strawman |
| The record's stated edges are the *right* edges | PCB-02 | Requires domain judgement about what was omitted | Confirm connector choice, socket/ZIF and power budget are named as undecided rather than silently absent |
| The corrected C-1 framing reads as an honest correction, not a retcon | PCB-03 | Tone and provenance judgement | Confirm the record says what was previously believed, what is true, and how it was established |
| Any behavioural claim about PY32F071 silicon | all | **No board exists** — the milestone ceiling | Every such claim must carry `[UNVERIFIED-UNTIL-SILICON]` |

---

## Security Domain

`security_enforcement` is not disabled in `.planning/config.json`. The phase adds no runtime code, no network surface, no parser, and no data path.

| Pattern | STRIDE | Mitigation |
|---|---|---|
| Shipping another company's USB vendor identity (`0x36B7` = Puya) | Spoofing | C-2 + D-09's ship gate; `1209:0001` as the interim identity |
| USB PID collision with every unmodified Puya CDC example | Spoofing / DoS | Same |
| A gate that passes without observing anything | Tampering (undetected) | Planted-violation fixture + per-parse non-vacuity (F-14) |
| An agent performing an outward-facing publish action | Elevation of Privilege | **Structural** separation — no `git push`, no `gh workflow run`, no PR filing. Not a checkpoint: `--auto`/`--chain` auto-approve checkpoints. |
| A future reader trusting a false silicon claim in a durable record | Repudiation / Information Disclosure | Per-claim tags + `[UNVERIFIED-UNTIL-SILICON]` + a `## Claim ceiling` section |
| Bricking a board via option bytes with no SWD | DoS (physical) | PCB-02's SWD-pads row, justified by Open Question 1 |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

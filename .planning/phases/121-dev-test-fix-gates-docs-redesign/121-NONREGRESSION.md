# Phase 121 Non-Regression Sweep — `dev test` FIX + GATES + DOCS + REDESIGN, closed at GATE-03

**Written:** 2026-07-29 (Plan 121-14)
**Firmware phase base:** `0048b3d` (Phase 119's own sweep HEAD) · **Host phase base:** `96e0622` (confirmed by `121-RESEARCH.md`) · **Meta phase base:** the commit preceding `121-01`'s golden regen
**Firmware HEAD at this sweep:** `48c36e569c8ddfd3daa8aea7e55c5bbc79b48b08` · **Host HEAD at this sweep:** `c3c9424f7a299c6ff3498a15620e5235cf72a782`

This is the single artifact a later reader should open to answer "what did Phase 121 change, and
what did it prove unchanged, at the phase's actual final commit". Per the mandatory discipline
inherited from `119-NONREGRESSION.md` §CORRECTION-4 and restated by `120-NONREGRESSION.md`, every
row below was **re-executed in this session** — nothing here is copied from a prior plan's
SUMMARY. Where a prior plan's SUMMARY made a claim this document re-checks it against the live
tree and says so.

---

## 1. The claim, as precise statements

Each statement below is individually checkable against the artifacts named in §2-§4, not merely
asserted:

1. **An unmapped `dev test` op string cannot reach a chip-mutating operator method.** The
   fail-closed arm added ahead of `OP_WRITE_PARTIAL` (Plan 121-02) means `_dispatch_step` /
   `_dispatch_multi_run` never fall through to `erase_eprom` for an op they do not recognise —
   verified structurally present in `_DESTRUCTIVE_OPS`/dispatch and by the still-green
   `test_chip_test.py` suite (§4, row-adjacent host pytest count).
2. **UV-ness is decided once, from the exact `electrical-type` axis, and only read downstream.**
   `chip_test.is_uv_eprom(full)` measures **301/301** against the live 746-entry DB (re-derived
   live this session, §"Requirement Row Re-Verification" below); `_is_uv_eprom` in
   `cli_handlers.py` reads it from `app.db.get_eprom(chip)` — never `resolve_chip`'s programmer
   dict.
3. **The partial write is inside the chip-ID destructive gate.** `OP_WRITE_PARTIAL` is a live
   member of `_DESTRUCTIVE_OPS` (confirmed: `frozenset({'erase', 'write-partial', 'write'})`),
   so a chip-ID mismatch gates it exactly like a full write.
4. **The erase step is `NA` on `0x0D` with an actionable, family-fact reason.** Confirmed live
   this session: `derive_plan('AT28C256', db, write_scope='full')`'s erase step reads
   `supported=False`, `reason="protocol 0x0D (28C family) has no erase operation; each page write
   auto-erases internally"` — the string contains `0x0D`, not `FLAG_CAN_ERASE`.
5. **`dev test <chip>` takes no options and always writes.** Confirmed live: the handler's
   callback signature is `(app, chip)`; each of the five removed flag spellings
   (`--destructive`, `--output-dir`, `-y`, `--yes`, `--submit`) errors `No such option` at exit
   code 2 when passed.
6. **Every run runs the dedup check, then asks.** `submit_report`'s Step 3
   (`find_prior_report_fn`) is called unconditionally, before the Step 5 ask, on every reached
   path including off-TTY — confirmed by reading the live source and by the green
   `test_submit.py` dedup/ordering legs (§ Requirement Row Re-Verification).
7. **The docs say so.** All eight GATE-02-named docs across both sub-repos carry the no-erase
   statement (firmware-side four) and the always-writes statement with zero residual
   "non-destructive" wording (host tester-facing three) — grepped live, not trusted from
   `121-13-SUMMARY.md`'s own assertion (§ Requirement Row Re-Verification).

Everything else this phase touched — the catalog string (D-15), the SDP-capability gate
(GATE-01), the audit-matrix golden (D-18) — is covered in its own section below.

---

## 2. The command-by-gate matrix

Every command below was executed in this session at the phase's final commit
(`firestarter@48c36e5`, `firestarter_app@c3c9424`). "Baseline" is `121-RESEARCH.md` §F-8's
measured figures (this phase's own start-of-phase baseline) unless noted otherwise.

| # | Gate | Exact command | Result this sweep | vs. baseline |
|---|---|---|---|---|
| 1 | Firmware native suite | `cd firestarter && pio test -e native` | **141/141 PASSED**, 17 groups | Unchanged (F-8 row 1) |
| 2 | Firmware native, no `DEV_TOOLS` | `pio test -e native_nodevtools` | **141/141 PASSED**, identical to row 1 | Unchanged (F-8 row 1b) |
| 3 | AVR builds | `pio run` (uno, uno328pb, leonardo) | **3/3 SUCCESS** — Leonardo 26072/28672, Uno 23932/32256, uno328pb 23976/32384 | **Unchanged from Phase 119's final measurement** — confirms `121-12`'s finding that the messages.toml edit produced a byte-identical `messages.h` |
| 4 | Host pytest, devcontainer interpreter | `python3 -m pytest tests/` (Python 3.12.13) | **1134 passed, 0 failed** in 51.83s; "29 snapshots passed" | **CHANGED BY DESIGN** — up from baseline 1051/1052 (F-8 row 2/3); this phase added ~83 new tests across 121-01..13. Matches `121-13-SUMMARY.md`'s own recorded 1134, independently reproduced |
| 5 | Host pytest, CI-parity Python 3.11 | `uv`-provisioned `/tmp/venv311/bin/python -m pytest tests/` (Python 3.11.15) | **1134 passed, 0 failed** in 52.39s — identical failure set (none) to row 4 | Confirms parity holds across the devcontainer/CI-target interpreter split |
| 6 | Coverage gate | `/tmp/venv311/bin/python -m pytest tests/ --cov=firestarter --cov-fail-under=70` | **81.86%** — passes with 11.9 pts headroom | Baseline was 82.47%/81.91%/81.86% across 121-08/09/11's own runs — consistent, no regression |
| 7 | `ruff check` | `/tmp/venv311/bin/ruff check firestarter/ tests/ tools/` (ruff **0.16.0**, the CI-resolved version) | **4 errors, 3 files** (`tools/audit_coverage_matrix.py` I001, `tools/catalog/codegen.py` I001, `tools/catalog/codegen_vectors.py` I001+UP031) | **CHANGED BY DESIGN, but not this phase's diff** — `git -C firestarter_app diff --stat 96e0622..HEAD -- <these 4 files + .github/scripts/update_version.py>` is **empty**: none of these files were touched by any Phase 121 plan. Pre-existing findings, same class as F-8 row 5's baseline. **The devcontainer's own globally-installed `ruff` has since drifted to 0.16.0 as well** (confirmed: `ruff --version` on `PATH` → 0.16.0) — RESEARCH's Pitfall 2 divergence (0.15.20 vs 0.16.0) is **no longer reproducible in this environment**; both now agree. The CI-resolved version is still the one reported here per the plan's mandate. |
| 8 | `ruff format --check` | `/tmp/venv311/bin/ruff format --check firestarter/ tests/ tools/` (ruff 0.16.0) | **3 files would be reformatted** (same 3 files as row 7, plus `tools/check_mypy_watermark.py`) | Same empty-diff proof as row 7 — pre-existing, not in this phase's diff. `tests/golden/` and `tests/fixtures/` stay excluded via `pyproject.toml`'s `extend-exclude` (Plan 121-01, D-18's collision-prevention edit) — confirmed present and unchanged |
| 9 | mypy watermark | `/tmp/venv311/bin/python tools/check_mypy_watermark.py` | `mypy errors: 1 (watermark: 35)` — 34 below | Unchanged from F-8 row 7 |
| 10 | `check_dispatch.py` | `python3 tools/check_dispatch.py` | **PASS** — 746 scanned, 736 supported, 10 non-dispatchable, 0 regressions, 0 consistency violations | Unchanged |
| 11 | `check_devtest_orchestrator.py` | `python3 tools/check_devtest_orchestrator.py` | **PASS** — scanned `chip_test.py`, `cli_handlers.py`, `submit.py`; 0 VPP-set, 0 raw-wire-dict, 0 `--force`; firmware untouched (host-only, asserted) | **Allow-list grew this phase** (Plan 121-09 added `_is_uv_eprom`/`_resolve_write_scope`; RESEARCH C-4's mandatory fix) — confirmed the gate still passes non-vacuously with the extended list |
| 12 | `check_sdp_capability_invariants.py` (**NEW this phase, GATE-01**) | `python3 tools/check_sdp_capability_invariants.py` | **PASS** — `0 permit-by-default, 0 widenable-allow-set`, `SDP_CAPABLE_TOKENS` bound exactly 1 time | New row — did not exist before Plan 121-03 |
| 13 | `check_no_community_support_status_write.py` | `python3 tools/check_no_community_support_status_write.py` | **PASS** — scanned `diagnostic_report.py`, `parse_devtest_issue.py`; 0 support_status writes | Unchanged (pre-existing gate) |
| 14 | `check_no_log_in_sdp_window.py` | `python3 tools/check_no_log_in_sdp_window.py` | **PASS** — resolved target `.../firestarter/src/proms/eeprom_28c.cpp`, emitter lines 298-314, poll lines 348-361 | Unchanged; resolved path confirmed to **exist** (both-directions rename check, §4) |
| 15 | `check_is_memory_cmd_no_ifdef.py` | `python3 tools/check_is_memory_cmd_no_ifdef.py` | **PASS** — resolved target `.../firestarter/include/firestarter.h`, predicate body lines 109-123, exactly 8 commands | Unchanged; resolved path confirmed to **exist** |
| 16 | `diff_db.py` identity | `python3 tools/diff_db.py` | **`PASS: all 2 changed chips explained (0 new chips confirmed; 0 chips removed from baseline)`** | **Identity here means "still exactly 2 explained `PGSZ_PAGE_SIZE` changes" — NOT zero.** The two changes are the pre-existing Phase 94 `W29C020,W29C020C,W29C022` / `W29C040,W29C042` page-size entries. A verifier expecting a zero-diff misreads this gate. |
| 17 | Catalog validity, both sub-repos | `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` (run from both `firestarter/` and `firestarter_app/`) | **`OK: catalog valid (73 messages, version 1)`**, both exit 0 | Unchanged in message count; `0x5F`'s format string changed (D-15), version stayed 1 |
| 18 | Codegen drift, firmware header | regenerate `firestarter/include/messages.h`, `git diff --exit-code` | **NO DRIFT** | Confirms Plan 121-12's own finding: the C++ header carries only numeric id `#define`s, so the `0x5F` format-string edit is invisible there — zero reflow risk realised |
| 19 | Codegen drift, host module | regenerate `firestarter_app/firestarter/messages.py`, `git diff --exit-code` | **NO DRIFT** | Unchanged |
| 20 | Three-way catalog identity | `md5sum` on all three `messages.toml` copies | **Identical** — `8c9f79af841537310e2db197decc62b2` | Matches Plan 121-12's recorded md5 exactly |
| 21 | Remaining nine-row named pytest modules | `pytest tests/test_check_no_log_in_sdp_window.py tests/test_sdp_table_parity.py tests/test_check_is_memory_cmd_no_ifdef.py tests/test_sdp_bus_config_drift.py tests/test_revision_constants_parity.py tests/test_dispatch_mirror.py tests/test_check_devtest_orchestrator.py tests/test_check_sdp_capability.py` | **62 passed** in 1.89s | Includes GATE-01's new 9-leg module (`test_check_sdp_capability.py`, row 12's companion) |
| 22 | `gen_sdp_bus_config.py` | `python3 tools/gen_sdp_bus_config.py` | **`OK: wrote .../_shared/sdp_bus_config.h`**; `git -C firestarter status --porcelain` on that path empty afterward | Idempotent, no drift |
| 23 | Second audit-matrix regeneration (D-18/C-2) | see §3 | **Byte-identical to golden** (`cmp` exit 0, both 186034 bytes) | **Proven no-op**, per C-2's prediction (§3) |

**No row is marked from memory or from a prior plan's SUMMARY.** Every command above was executed
in this session; where a figure matched a prior SUMMARY's own claim, that match was itself
verified by re-running the command, not by reading the SUMMARY.

---

## 3. Golden and generated-artifact identity

**The coverage-matrix golden's one intentional refresh (Plan 121-01) and the proven no-op second
regeneration (this plan).** Plan 121-01 regenerated `tests/golden/v1.3-COVERAGE-MATRIX.md` as its
own first commit, alone, with zero DEVTEST code in the tree — closing a pre-existing 1403-byte
drift traced to Phase 98's pinout split (`362bfa0`), unrelated to this phase's own work (RESEARCH
C-2). This sweep re-ran the generator a **second** time against the same committed ledger
(`.planning/v1.3-defect-coverage-ids.json`) and diffed the output against the now-committed
golden:

```
$ python3 -c "from tools.audit_coverage_matrix import generate_matrix; \
    generate_matrix(output='/tmp/regen_matrix.md', ledger_path='.../.planning/v1.3-defect-coverage-ids.json')"
$ cmp /tmp/regen_matrix.md tests/golden/v1.3-COVERAGE-MATRIX.md && echo BYTE-IDENTICAL
BYTE-IDENTICAL
$ wc -c /tmp/regen_matrix.md tests/golden/v1.3-COVERAGE-MATRIX.md
186034 /tmp/regen_matrix.md
186034 tests/golden/v1.3-COVERAGE-MATRIX.md
$ git -C firestarter_app status --porcelain tests/golden/
(empty)
```

**This confirms RESEARCH C-2's prediction exactly**: `tools/audit_coverage_matrix.py` reads only
`chip_database.json` and the `.planning` ledger, and has no `dev test`/`OP_*`/`chip_test`
vocabulary at all — so this phase's `OP_WRITE_PARTIAL` addition, UV-axis redesign, and every other
DEVTEST change genuinely could not move the matrix, and did not. Had this second regeneration
produced a non-empty diff, the correct response would have been to **stop and investigate**, not
to silently regenerate the golden a second time — D-18's entire purpose is to make that scenario
visible rather than mask it. No such investigation was needed.

**The three-way catalog identity and both codegen drift gates** are recorded in full in §2 rows
17-20. **No firmware `.cpp` or `.h` file other than the generated `messages.h` was touched by this
phase** — confirmed by the phase-scoped firmware diff:

```
$ git -C firestarter diff --stat 0048b3d..HEAD
CLAUDE.md                   | 13 ++++++++++++-
README.md                   |  7 +++++++
doc/PROTOCOLS.md            |  4 ++--
tools/catalog/messages.toml |  8 +++++++-
4 files changed, 28 insertions(+), 4 deletions(-)
```

Three of those four are documentation (`CLAUDE.md`, `README.md`, `doc/PROTOCOLS.md` — GATE-02).
**The one non-doc file is `tools/catalog/messages.toml`** (D-15's catalog edit) — confirming
`121-12-SUMMARY.md`'s own framing: **this phase's firmware footprint is not docs-only**, but it is
narrower than 121-12's own must-have language predicted ("a generated firmware header changes").
Independently re-verified in this sweep (§2 row 18): `firestarter/include/messages.h` regenerates
to a **zero diff** — the C++ header carries only numeric id `#define`s; the changed format string
lives entirely in the host-side `messages.py` (§2 row 19, which does show the expected
one-field diff, already committed). The compiled firmware is therefore unchanged even though a
tracked firmware **source** file (the catalog mirror) is not byte-identical to phase base — the
catalog-sync CI red-until-milestone-merge expectation (§7) still holds on that basis alone.

---

## 4. The nine-row cross-repo gate table (from `119-NONREGRESSION.md` §CORRECTION-4)

Re-run and re-recorded at this phase's final commit, per Phases 120 and 121's mandatory
inheritance of this checklist. Row identifiers follow `119-NONREGRESSION.md`'s own numbering.

| # | Gate | Command | Verdict this sweep |
|---|---|---|---|
| 1 | `check_no_log_in_sdp_window.py` (HIGH-risk — firmware source scan) | `python3 tools/check_no_log_in_sdp_window.py` | **PASS**, resolved path `.../firestarter/src/proms/eeprom_28c.cpp` **confirmed to exist** (`ls -la` in this sweep). D-15's catalog edit does not touch this file — the emitter/poll line numbers (298-314/348-361) are unchanged. |
| 2 | `test_check_no_log_in_sdp_window.py` | (in §2 row 21's combined run) | **PASS** |
| 3 | `test_sdp_table_parity.py` (MEDIUM-risk) | (in §2 row 21's combined run) | **PASS** |
| 4 | `check_is_memory_cmd_no_ifdef.py` (firmware source scan) | `python3 tools/check_is_memory_cmd_no_ifdef.py` | **PASS**, resolved path `.../firestarter/include/firestarter.h` **confirmed to exist**, predicate body lines 109-123, exactly 8 commands |
| 5 | `gen_sdp_bus_config.py` (generator) | `python3 tools/gen_sdp_bus_config.py` | **PASS**, `git -C firestarter status --porcelain` on that path empty afterward — idempotent, no drift |
| 6 | `test_sdp_bus_config_drift.py` | (in §2 row 21's combined run) | **PASS** |
| 7 | `test_revision_constants_parity.py` | (in §2 row 21's combined run) | **PASS** — unchanged test count/shape this phase (no `CMD_*`/`FLAG_*` value added by Phase 121) |
| 8 | `test_dispatch_mirror.py` | (in §2 row 21's combined run) | **PASS** |
| 9 | `check_dispatch.py` + `check_devtest_orchestrator.py` | `python3 tools/check_dispatch.py` then `python3 tools/check_devtest_orchestrator.py` | **PASS** both — `check_dispatch.py` unchanged (746/736/10/0/0); `check_devtest_orchestrator.py`'s allow-list **grew** this phase (Plan 121-09's `_is_uv_eprom`/`_resolve_write_scope`) and the gate confirmed non-vacuous against the extended list |

**Cross-repo rename check, both directions, explicitly.** This phase touched firmware (D-15's
catalog edit, landing in Plan 121-12). For each host gate that scans firmware source text (rows
1 and 4 above), the resolved target path was confirmed to **exist** on disk in this sweep, not
merely assumed from the PASS line. **The reverse direction — a firmware-side gate scanning host
source text — does not exist as an architecture in this project**: a repo-wide grep of
`firestarter/tools/` for `firestarter_app` returns only prose comments in the catalog files
(`messages.toml`, `codegen_vectors.py`, `frame-vectors.toml`) documenting the sync-script
relationship, never a source-scanning gate. So the "both directions" obligation resolves to: the
one real direction (host-scans-firmware) is proven non-vacuous by path, and the other direction is
confirmed **not to exist** rather than silently assumed absent.

**Every row PASS.** No row was accepted on the strength of an earlier plan's SUMMARY alone — each
command above was re-run in this sweep, at the phase's final commit.

---

## Requirement Row Re-Verification (row by row, against the live tree)

Every one of the phase's nine requirement ids was independently re-checked against the live tree
in this sweep — not against any SUMMARY's own assertion. Each row below states the command or
assertion used.

| Requirement | Independent check performed this sweep | Result |
|---|---|---|
| **DEVTEST-01** | `derive_plan('AT28C256', db, write_scope='full')` — read the erase `Step`'s `supported`/`reason` fields directly; ran `pytest tests/test_chip_test.py -k devtest01` | `supported=False`, `reason` names `0x0D`/`28C family`, never `FLAG_CAN_ERASE`; 2/2 tests pass |
| **DEVTEST-02** | Read `inspect.signature(cli_handlers.dev_test.callback)`; invoked `dev test AT28C256 <flag>` via `CliRunner` for each of `--destructive`/`--output-dir`/`-y`/`--yes`/`--submit` | signature is `(app, chip)`; every flag → `No such option`, exit 2 |
| **DEVTEST-03** | Computed `is_uv_eprom` coverage against the live 746-entry `chip_database.json` via `EpromDatabase.get_eproms()` | 301/301 UV-EPROM entries covered; old `algorithm==0x0B` proxy covers only 32/301 (0 false positives either way) |
| **DEVTEST-04** | Read the live `_DESTRUCTIVE_OPS` frozenset; ran `pytest tests/test_dev_test_cmd.py -k TestUVOnlyStopAndAsk` | `OP_WRITE_PARTIAL` present in `_DESTRUCTIVE_OPS`; 4/4 branch legs (non-UV/UV-yes/UV-no/UV-off-TTY) pass |
| **DEVTEST-05** | Read `submit_report`'s live source for step ordering; ran `pytest tests/test_submit.py -k "dedup or argv or deny"` | Step 3 (dedup) confirmed unconditional and before Step 5 (ask) in source; 27/27 tests pass |
| **DEVTEST-06** | Ran `pytest tests/test_submit.py -k "negative or permission_gated or mutating"` | 16/16 deny-set legs pass (both `gh issue create` and `gh issue comment` paths, long and short flag forms) |
| **GATE-01** | Ran `tools/check_sdp_capability_invariants.py` against real source, then against each of the two planted-violation fixtures via `FIRESTARTER_SDP_CAPABILITY_SRC` | Real source: exit 0, PASS. Each planted fixture: exit 1, named violation reported |
| **GATE-02** | `grep -ci` for the required statements across all eight named docs in both sub-repos | No-erase statement present in all 4 firmware/protocol docs; always-writes statement present and "non-destructive" absent from all 3 tester-facing docs; `doc/lockable-proms.md` confirmed tracked |
| **GATE-03** | The full sweep in §2/§4 above | Green at every row, both interpreters, both ruff/format checks recorded with version, `diff_db.py` identity confirmed as "2, not 0" |

**All nine rows verify.** None required a report of a non-holding claim.

---
<!-- gsd:write-continue -->

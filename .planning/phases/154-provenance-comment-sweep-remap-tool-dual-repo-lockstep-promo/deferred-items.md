# Deferred items — Phase 154

Out-of-scope discoveries found during execution. Logged, not fixed.

## D1 — Malformed stray `/workspaces/platformio.ini` breaks any meta-root `pio` invocation

**Found during:** Plan 01, Task 3 (capturing tool versions).

`/workspaces/platformio.ini` exists as an untracked, gitignored 21 KB file
(`.gitignore:20` ignores `platformio.ini`, so it is invisible to `git status`). It is
malformed — duplicate `[platformio]` section at line 26 — so **any** `pio` invocation
whose cwd is `/workspaces` dies:

```
platformio.project.exception.InvalidProjectConfError: Invalid '/workspaces/platformio.ini'
(project configuration file): 'While reading from '/workspaces/platformio.ini' [line 26]:
section 'platformio' already exists'
```

Even a bare `pio --version` crashes (it prints the version, then dies in the atexit
telemetry hook when it tries to resolve `core_dir` from the project config).

**Impact on this phase:** none, provided every oracle invocation in plans 06-11 does
`cd /workspaces/firestarter` first. Recorded in
`.planning/v1.33/baseline-pre-sweep.md` §6 as a TRAP.

**Why deferred:** the file is not tracked by any of the three repos, is not this phase's
work, and Phase 154's scope is comment text only. Fixing or deleting it is a devcontainer
hygiene change with no requirement behind it.

**Suggested disposition:** delete it, or repair the duplicate section, in a separate
housekeeping task. Verify with `pio --version` exiting 0.

## D2 — Research finding F7's module count is 9; measured is 7

**Found during:** Plan 01, Task 2 (verifying the porcelain-assertion constraint).

F7 states "9 modules assert git porcelain". Grep of both repos this session finds **7**
modules: 4 in `firestarter_app/tests/` (`test_cap03_ack_layout_parity.py`,
`test_py32_flash_map_host.py`, `test_json_key_parity.py`, `test_py32_asset_name_host.py`)
and 3 in `firestarter/tests/` (`test_requirement_case_mapping_v131.py`,
`test_trace_segment_exhaustiveness_v131.py`, `test_flash_path_record_sync.py`).

**The load-bearing half of F7 is confirmed:** every one of the 7 asserts on the
**firmware** repo, so `firestarter_app`'s untracked files are harmless to all gates.

**Why deferred:** the count does not change any decision. F7's conclusion stands. The
delta is recorded rather than corrected in either direction, per this phase's
measure-both-sides rule.

## D3 — The manifest's `source_text` side is the WORKING TREE, not `pre_sweep_shas`

**Found during:** Plan 05, Task 2 (dry-running the finished tool against the real
13,692-record manifest as a scale check).

`build_citation_manifest.py` reads every `source_text` from the file **on disk**, while the
header records `pre_sweep_shas` = each sub-repo's `git rev-parse HEAD` at generation time.
For the 169 clean candidate files those coincide. For the **two** files plan 03 had already
modified in `firestarter_app`'s working tree — `tests/test_dispatch_mirror.py` and
`tests/test_sdp_table_parity.py` — they do not: measured, `6bfa645:./tests/test_dispatch_mirror.py`
is 222 lines and the working tree is 362, so old lines ≥ 23 shift by **+5**.

**Measured consequence:** the 7 manifest records targeting `test_dispatch_mirror.py` are all
recognised as **fixed points** and the tool is a correct no-op on them, because their recorded
`source_text` is the post-plan-03 text that already sits at the recorded line. The
fixed-point-first ordering is what turned a stale anchor into a safe no-op instead of a wrong
rewrite — the exact property SWEEP-11 asks for.

**What Phase 159 must do about it:** the app-side "old" anchor for the composite map is the
**plan 12 commit** (which contains plan 03's edits), not `6bfa6453d1bac232eb81ab35fa7f14b50b0b291a`.
This is precisely why `--pre-sweep-sha` is an argv argument that beats the header. Nothing needs
fixing in the manifest.

**Why deferred:** correcting it would mean regenerating plan 04's committed manifest, and D-11
reserves `firestarter_app`'s single commit for plan 12. Recorded, not corrected.

## D4 — 15 manifest records against `.planning/STATE.md` no longer bind

**Found during:** Plan 05, Task 2 (the same real-manifest dry run).

All 15 "binding is ambiguous" residues in the real dry run are in `.planning/STATE.md`, whose
line numbers have drifted since plan 04 generated the manifest — every plan's `state_updates`
step rewrites it. The tool **refuses** rather than guessing, which is the intended fail-closed
behaviour, and it names each one.

**Why deferred:** STATE.md is machine-maintained bookkeeping, not source provenance. The honest
options are to re-generate the manifest immediately before Phase 159's remap, or to exclude
`.planning/STATE.md` from the citation corpus. Either is a Phase 159 / SWEEP-12 decision, not a
plan 05 one.

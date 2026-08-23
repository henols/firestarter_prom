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

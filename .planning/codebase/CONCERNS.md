# Codebase Concerns

**Analysis Date:** 2026-05-08

## Tech Debt

**Database override system is disabled:**
- Issue: `override_proms = None` is hardcoded on line 170 of `database.py`, disabling the `database_overrides.json` file entirely. A comment shows it was replaced with the new `minipro_complete_db.json` format but the override mechanism was never re-enabled or ported to the new format.
- Files: `firestarter_app/firestarter/database.py`
- Impact: Users cannot override EPROM definitions via the documented `~/.firestarter/database.json` override file path; the code path to merge overrides calls `_merge_databases`, which has a known comment noting "This might not merge correctly if format differs."
- Fix approach: Port the override merge logic to the new `minipro_complete_db.json` format and re-enable loading from `database_overrides.json`.

**Commented-out `get_eprom` pruning logic:**
- Issue: Lines 406–425 of `database.py` contain a large block of commented-out code that was responsible for trimming fields on non-full data fetches. The `get_eprom` function now always returns full data, and the comment explains nothing about whether this is intentional or a regression.
- Files: `firestarter_app/firestarter/database.py`
- Impact: Callers always receive the full dict; `convert_to_programmer` re-filters, so there is no runtime breakage, but the code is confusing and misleading.
- Fix approach: Remove the dead commented-out code block once it is confirmed the current behavior is correct.

**`globals()` introspection to derive command names:**
- Issue: Two places in `eprom_operations.py` (lines 163 and 217) resolve command names by scanning `globals()` for constants matching a numeric command code. This is fragile, slow, and hard to reason about.
- Files: `firestarter_app/firestarter/eprom_operations.py`
- Impact: If a constant is renamed, or two constants share the same value, the lookup silently returns the wrong name or raises `IndexError`.
- Fix approach: Use a reverse-lookup dict keyed by command integer, e.g. `COMMAND_NAMES = {COMMAND_READ: "READ", ...}`.

**`LEONARDO_BUFFER_SIZE` constant is unused:**
- Issue: `constants.py` defines `LEONARDO_BUFFER_SIZE = 1024`, but `_calculate_buffer_size()` in `eprom_operations.py` always returns `BUFFER_SIZE = 512` and ignores the Leonardo variant. The comment says it "matches the firmware's internal buffer size" without board-specific branching.
- Files: `firestarter_app/firestarter/constants.py`, `firestarter_app/firestarter/eprom_operations.py`
- Impact: Leonardo boards may be sending sub-optimal (half-sized) chunks, but more importantly, a defined constant that is never used signals unfinished work.
- Fix approach: Either wire up board detection (the board name is returned from `check_current_firmware`) to select the correct buffer size, or remove the unused constant.

**Duplicate/stale `build/` directory in repo:**
- Issue: `firestarter_app/build/lib/firestarter/` contains a copy of most source files. The `ic_layout.py` build copy is 301 lines (vs 626 in source), indicating it is significantly outdated.
- Files: `firestarter_app/build/`
- Impact: The stale build artifacts can cause confusion about which files are authoritative and may accidentally be imported.
- Fix approach: Add `build/` to `.gitignore` and remove the checked-in build artefacts.

**Inconsistent command dict key (`"cmd"` vs `"state"`):**
- Issue: EPROM operations send `{"cmd": ...}` while hardware/firmware commands send `{"state": ...}`. The serial communicator works around this in `_probe_port` with `command_to_send.get("state") or command_to_send.get("cmd")`.
- Files: `firestarter_app/firestarter/eprom_operations.py`, `firestarter_app/firestarter/hardware.py`, `firestarter_app/firestarter/firmware.py`, `firestarter_app/firestarter/serial_comm.py`
- Impact: Adding new command types requires remembering which key to use, and the dual-lookup is error-prone.
- Fix approach: Standardize on a single key (e.g., `"cmd"`) across all command dicts and update the firmware protocol documentation accordingly.

**`pulse-delay` is always zero:**
- Issue: `_map_data` in `database.py` (line 346) sets `"pulse-delay": 0` with a comment "Not directly available in new format, may need parsing from string." It is never populated with a real value.
- Files: `firestarter_app/firestarter/database.py`
- Impact: EPROMs that require a specific programming pulse delay will use the wrong (zero) value, potentially causing write failures or data errors.
- Fix approach: Parse the pulse delay from the new database format string field, or add the field explicitly to the EPROM database entries.

**`_verbose` global in `utils.py` is set but never read:**
- Issue: `utils.py` declares a module-level `_verbose = False` but nothing in the module reads it; verbosity is handled via the standard `logging` framework everywhere else.
- Files: `firestarter_app/firestarter/utils.py`
- Impact: Dead code, minor confusion.
- Fix approach: Remove the unused global.

## Known Bugs

**`can_erase_str` uses wrong flag key:**
- Symptoms: The "Can be erased" field in `info` output is always `false` for Flash/EEPROM chips even when they support electrical erase.
- Files: `firestarter_app/firestarter/ic_layout.py` (line 510)
- Trigger: Run `firestarter info <flash-eprom>`.
- Workaround: None.
- Root cause: Line 510 reads `eprom_data.get("flags", 0) & 0x00000010` but the erasability bit is stored in `"info-flags"`, not `"flags"`. The `"flags"` key holds the simple programmer-facing flags (e.g., `FLAG_CAN_ERASE = 0x02`), not the detailed info-flags. The correct read would be `eprom_data.get("info-flags", 0) & 0x00000010`.

**`get_eproms(verified=False)` returns all EPROMs instead of unverified only:**
- Symptoms: Calling `get_eproms(verified=False)` returns all chips, not just unverified ones.
- Files: `firestarter_app/firestarter/database.py` (lines 380–383)
- Trigger: Call `db.get_eproms(verified=False)`.
- Workaround: None.
- Root cause: The condition `or (not verified)` is True whenever `verified=False`, so the filter never restricts results when `verified` is `False`.

**Typo in SIGINT handler message:**
- Symptoms: When the user presses Ctrl+C, the message "Prosess interrupted." is printed instead of "Process interrupted."
- Files: `firestarter_app/firestarter/main.py` (line 698)
- Trigger: Press Ctrl+C during any operation.
- Workaround: Cosmetic only.

## Security Considerations

**Firmware downloaded over HTTPS but not verified:**
- Risk: The firmware `.hex` file is downloaded from GitHub Releases over HTTPS, but there is no checksum or signature verification before flashing it to the Arduino.
- Files: `firestarter_app/firestarter/firmware.py`
- Current mitigation: HTTPS provides transport-level protection, and the URL is the official GitHub API endpoint.
- Recommendations: Verify a SHA-256 checksum published alongside the release asset, or verify a GPG signature, before passing the file to avrdude.

**Config file written without directory permission check:**
- Risk: If `~/.firestarter/` is world-writable (e.g., misconfigured system), a local attacker could pre-populate the config with a malicious `avrdude-path`, causing arbitrary code execution the next time `firestarter fw --install` is run.
- Files: `firestarter_app/firestarter/config.py`, `firestarter_app/firestarter/firmware.py`
- Current mitigation: Default `~` directory permissions restrict this on standard systems.
- Recommendations: Validate `avrdude-path` from config is a real executable in a trusted location before invoking it.

## Performance Bottlenecks

**Serial port probing adds 2-second stabilization delay per port:**
- Problem: Each candidate serial port connection adds a `time.sleep(2.0)` (`CONNECTION_STABILIZE_DELAY`) to allow the Arduino to reset. If multiple ports are tried, this multiplies linearly.
- Files: `firestarter_app/firestarter/serial_comm.py` (line 106)
- Cause: Arduino boards with auto-reset on DTR/RTS require time to leave the bootloader and enter application mode.
- Improvement path: Cache the last successful port in config (already done) so the preferred port is tried first and the delay is only paid once on first connection. Consider reducing delay or using a readiness handshake to detect when the board is ready earlier.

**O(n) linear scan of entire EPROM database on every lookup:**
- Problem: `get_eprom`, `get_eprom_config`, and `search_eprom` iterate over all manufacturers and all ICs on every call. With thousands of entries in `minipro_complete_db.json`, this is noticeable.
- Files: `firestarter_app/firestarter/database.py`
- Cause: The database is stored as a nested dict of lists (`{manufacturer: [ic, ic, ...]}`), not indexed by part number.
- Improvement path: Build an inverted index `{part_number.lower(): ic_data}` during `_initialize_database_core` for O(1) name lookups.

## Fragile Areas

**`expect_ack` loops forever on unexpected response types:**
- Files: `firestarter_app/firestarter/serial_comm.py` (lines 234–246)
- Why fragile: The `expect_ack` loop only breaks on `"OK"` or `"ERROR"` responses. Any other response type (e.g., `"WARN"`, `"DATA"`) causes the loop to call `get_response` again. A firmware bug that sends only `"WARN"` responses will spin until `get_response` itself times out, which takes `DEFAULT_RESPONSE_TIMEOUT = 10` seconds per call, potentially looping for a very long time.
- Safe modification: Add a counter or dedicate a maximum retry limit; log and raise on unexpected types after N attempts.
- Test coverage: No unit tests; only tested via physical hardware integration tests in `.sh` scripts.

**State machine in `_run_state_machine` assumes INIT always succeeds:**
- Files: `firestarter_app/firestarter/eprom_operations.py` (line 242)
- Why fragile: `_ = self._execute_phase("INIT", progress)` discards the return value. If INIT fails with a programmer error, `_execute_phase` raises `EpromOperationError`, which is caught by the outer try/except — but the MAIN ACK (`self.comm.send_ack()`) on line 245 is sent unconditionally before checking anything, potentially desynchronizing the protocol.
- Safe modification: Validate the INIT return value before sending the MAIN start ACK.
- Test coverage: No unit tests.

**Database merge (`_merge_databases`) uses shallow `.update()`:**
- Files: `firestarter_app/firestarter/database.py` (line 208)
- Why fragile: When merging user overrides, `existing_names[manual_item["name"]].update(manual_item)` performs a shallow dict update. Nested dicts (e.g., `programming`, `electrical`) in the override will replace, not merge, the base entry's nested fields.
- Safe modification: Use a deep-merge utility instead of `.update()`.
- Test coverage: No automated tests.

**`_read_voltage_loop` uses tuple unpacking on `get_response` return:**
- Files: `firestarter_app/firestarter/hardware.py` (line 204)
- Why fragile: Line 204 calls `response_type, message = comm.get_response()`, but `get_response` returns a `Response` namedtuple, not a plain tuple. While namedtuple unpacking works, if `get_response`'s return type changes this will break silently.
- Safe modification: Use `response.type` and `response.message` directly (as done everywhere else).
- Test coverage: None.

## Dependencies at Risk

**`requests` used for GitHub API without retry or rate-limit handling:**
- Risk: GitHub API rate-limits unauthenticated requests to 60/hour. If the rate limit is hit, `fetch_latest_release_info` fails silently and returns `(None, None)`, which prevents firmware installation even when `--install` is passed.
- Impact: Firmware update check fails; user gets a confusing error about "latest firmware URL not available."
- Migration plan: Add `Retry` adapter to the `requests.Session`, or cache the latest-release response locally with a TTL.

**`argcomplete>=3.6.2` is a recent pinned minimum:**
- Risk: `argcomplete` 3.6.2 was released recently; older system Python environments may not satisfy this constraint, breaking installation.
- Impact: `pip install firestarter` fails on systems with older package caches.
- Migration plan: Evaluate whether any 3.6.2-specific features are actually used; if not, relax to `>=2.0`.

## Missing Critical Features

**No partial-write recovery:**
- Problem: If a write operation is interrupted mid-way (power loss, USB disconnect), there is no way to resume from the last written address. The user must restart the write from the beginning.
- Blocks: Reliable operation on large (1 MB+) Flash chips where write time is significant.

**No automated unit tests:**
- Problem: The test suite consists entirely of bash integration scripts (`firestarter_test.sh`, `write_test.sh`) that require physical hardware. There are no Python unit tests, no mocks for serial communication, and no CI configuration.
- Blocks: Confident refactoring, contributor onboarding, CI/CD pipelines.

**Board type not persisted after firmware check:**
- Problem: `check_current_firmware` returns the board name from the programmer, but this is never stored in config. On the next run, `_install_with_avrdude` falls back to the CLI `--board` argument default (`"uno"`), which may be wrong for Leonardo users.
- Blocks: Correct firmware installation on Leonardo boards without always passing `--board leonardo`.

## Test Coverage Gaps

**Serial communication layer (`serial_comm.py`):**
- What's not tested: Response parsing, timeout handling, checksum verification in `read_data_block`, port probing logic, firmware version comparison.
- Files: `firestarter_app/firestarter/serial_comm.py`
- Risk: Protocol bugs or regressions in checksum, timeout, or version-check logic will only be caught at hardware integration time.
- Priority: High

**Database loading and lookup (`database.py`):**
- What's not tested: Singleton initialization, JSON loading failure paths, `_merge_databases` correctness, `get_bus_config` pin conversion, `search_chip_id`.
- Files: `firestarter_app/firestarter/database.py`
- Risk: Silent data corruption in pin mappings or incorrect EPROM definitions sent to hardware.
- Priority: High

**EPROM operations state machine (`eprom_operations.py`):**
- What's not tested: State machine phase transitions, write chunking protocol, progress reporting, error recovery, checksum generation.
- Files: `firestarter_app/firestarter/eprom_operations.py`
- Risk: Protocol desynchronization bugs are hard to diagnose without hardware.
- Priority: High

**Firmware manager (`firmware.py`):**
- What's not tested: Version comparison edge cases (e.g., `x` wildcard replacement), download failure paths, avrdude subprocess invocation, port selection logic.
- Files: `firestarter_app/firestarter/firmware.py`
- Risk: Incorrect version comparison could prevent update or force unnecessary re-flash.
- Priority: Medium

---

*Concerns audit: 2026-05-08*

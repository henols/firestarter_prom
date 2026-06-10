# Pitfalls Research

**Domain:** Firmware dispatch hardening + lockstep wire-protocol extension + skeleton handlers (v1.12)
**Researched:** 2026-06-10
**Confidence:** HIGH — all findings grounded in actual source files read above, v1.2/v1.10/v1.11 retrospectives, and the live flash-budget measurements from the current branch.

---

## Critical Pitfalls

### Pitfall 1: Deleting the mem_type fallback before establishing a regression baseline — unmasking a WARNING-5-class hazard

**What goes wrong:**

The `mem_type == TYPE_EPROM (1)` fallback at `memory.cpp:104` is the last stop before the existing `MSG_ERR_MEM_TYPE_UNSUPPORTED` error. It is currently only reachable when `handle->protocol == 0` (or some unknown non-zero value). Every chip in `chip_database.json` that the regenerated pipeline emits carries an explicit `algorithm` integer, so for those 743 chips the protocol-prefix chain always fires first and the fallback is never exercised. However, the fallback still provides safety for two real populations:

1. **Hand-crafted JSON commands** — a developer or operator sending raw JSON with `"type": 1` and no `"algorithm"` key (or `"algorithm": 0`) will silently route to `configure_eprom`, which enables the 12V VPP boost regulator (`CTRL_VPP_REGULATOR_ENABLE`). If the chip seated in the socket is anything other than a UV-EPROM, that is a hardware-damage path. This population exists today and is explicitly called out in `firestarter/CLAUDE.md` as the backward-compatibility rationale for the fallback.

2. **User-override database entries** — entries in `~/.firestarter/database.json` that predate the v1.0 `algorithm` field will arrive with `protocol == 0` and `mem_type == 1`. These also silently route to `configure_eprom`.

Removing the fallback without auditing these populations first turns a latent hazard into a silent regression: any chip that was accidentally working through the fallback (even correctly) now gets `MSG_ERR_MEM_TYPE_UNSUPPORTED` at runtime with no warning that a fallback was removed.

The v1.0 retrospective documents exactly this pattern: "Closing a blocker can unmask a deeper hazard. Phase 12 closed BLOCKER-1's 'Memory type not supported' safe-exit, which had been silently protecting 23 AT28C-family 5V EEPROMs from receiving 12V." Removing the fallback here is the same structural move — the net you are removing may be load-bearing for some edge case you have not yet enumerated.

**Why it happens:**

The fallback looks vestigial once the protocol-prefix chain covers all 743 DB chips. The temptation is to delete it as part of the "fail-closed" cleanup without asking what would have fallen through it in practice.

**How to avoid:**

Before deleting or neutering the fallback, run a concrete audit:

1. **Grep the codebase and test fixtures** for any JSON command that omits `algorithm` or sets `algorithm: 0`. Collect the set. For each, determine whether the current behavior (routes to `configure_eprom`) is correct or coincidentally safe.
2. **Build a dispatch-baseline test** (a native Unity test or a host-side pytest) that asserts the expected handler for every `(protocol, mem_type)` pair in the current DB — including the `(0, 1)` case — *before* changing anything. This baseline is the regression surface the fallback-removal can be diffed against.
3. **Update `check_dispatch.py`'s `dispatch()` function** to mirror the new fail-closed logic before the firmware changes land — so the gate is testing the new behavior against the old DB, surfacing any chip that would newly route to ERROR.
4. Only after the baseline is green and any fallback-dependent chips are explicitly handled (or documented as unsupported) should the fallback be replaced with the fail-closed not-implemented response.

**Warning signs:**

- Any chip whose `algorithm` resolves to 0 in the DB pipeline (e.g. a chip with `protocol_id` absent in `infoic.xml` that build_db.py silently drops to 0).
- User-override DB entries in `~/.firestarter/database.json` that predate the v1.0 `algorithm` field.
- Native dispatch tests that only cover the protocol-prefix chain, with no test for `(protocol=0, mem_type=1)`.
- `check_dispatch.py` exit 0 even after the firmware fallback is removed — because `check_dispatch.py`'s `dispatch()` still has the mem_type fallback chain (lines 89-95 of the current file), so it would NOT catch a chip that the firmware now rejects.

**Phase to address:**

The phase that removes/guards the mem_type fallback must begin with a "capture pre-removal baseline" plan step. The baseline (native test + `check_dispatch.py` scan on the fallback-present state) must be pinned before the fallback is touched. This is a Phase 1 / foundational-dispatch phase concern.

---

### Pitfall 2: Lockstep wire-protocol desync — firmware emits the new "not implemented" message ID before the host catalog knows about it

**What goes wrong:**

v1.12 introduces a new response code / message ID (e.g. `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`) to distinguish "protocol unimplemented" from the existing `MSG_ERR_MEM_TYPE_UNSUPPORTED` (0xAE). The message must be added to three places in lockstep:

1. `firestarter/tools/catalog/messages.toml` (canonical source, meta-repo)
2. `firestarter/include/messages.h` (generated C++ header — firmware side)
3. `firestarter_app/firestarter/messages.py` (generated Python module — host side)

The codegen drift gate (`python3 tools/catalog/codegen.py --catalog ... --check && git diff --exit-code`) catches drift between the TOML and the generated files *within each repo*. However it does NOT catch the case where the two repos' `messages.toml` files diverge from each other. The canonical copy lives in the meta-repo; it is sync'd to both sub-repos via `tools/catalog/sync_to_subrepos.sh`. If someone edits the firmware sub-repo's `messages.toml` directly (bypassing the sync script) the host's catalog will not have the new ID, and any frame carrying that ID will be decoded as an unknown message. Depending on `serial_comm.py`'s error handling, this produces a cryptic `EpromOperationError` or a silent hang rather than "protocol not implemented."

The v1.10 retrospective confirms: "dual-repo lockstep pinned by codegen + golden vectors … byte-compatibility was provable in CI before the bench, so the hardware session verified transport, not contract."

**Why it happens:**

The firmware dev makes the catalog change in the firmware sub-repo directly (it is faster than going through the meta-repo sync path). The host CI only checks its own catalog drift; it does not cross-check the firmware sub-repo's catalog. The desync is invisible until a real device is connected.

**How to avoid:**

1. **Edit `messages.toml` ONLY in the meta-repo** and run `sync_to_subrepos.sh` to push the identical copy to both sub-repos. The sync script is the contract.
2. **Add a cross-repo parity test** — a script (or a CI job in the meta-repo) that diffs `firestarter/tools/catalog/messages.toml` against `firestarter_app/tools/catalog/messages.toml` and fails on any difference. This is not currently in CI.
3. **Assign consecutive IDs by appending to the catalog**, not by inserting in the middle — the drift gate is byte-identity, so any insertion shifts existing IDs and breaks every device running old firmware.
4. **The new message ID must be in the 0xA0-0xBF ERROR band** (per the existing catalog layout) and must not collide with any existing `MSG_ERR_*` value. The current highest error ID is `MSG_ERR_MEM_SIZE_TOO_SMALL = 0xBA`. The next available slot is `0xBB`.

**Warning signs:**

- `serial_comm.py` logs an "unknown message id" warning during a `write` or `read` of an unimplemented-protocol chip.
- The host prints a generic `EpromOperationError` or timeout instead of "protocol not implemented."
- The codegen drift gate passes in both sub-repos individually but the two `messages.toml` files differ (no cross-repo gate today).
- The host-side `messages.py` does not contain a constant for the new message ID but the firmware `messages.h` does (or vice versa).

**Phase to address:**

The phase that adds the new message ID to the catalog must include both: (a) editing and syncing the meta-repo `messages.toml`, and (b) regenerating + committing both sub-repo generated files in the same commit pair, with the codegen drift gate green in both repos. This lockstep-wire phase must come before any firmware dispatch logic uses the new ID.

---

### Pitfall 3: Codegen-drift CI gate masked by Python version skew (py3.12-on-devcontainer vs py3.11-in-CI)

**What goes wrong:**

The codegen drift gate in both sub-repo CI workflows runs on Python 3.11 (`python-version: '3.11'` in `.github/workflows/ci.yml` and `build.yml`). The devcontainer runs Python 3.12. In v1.10 and v1.11 this caused the `ruff` formatter to produce different output on 3.12 (f-string backslash handling) and the codegen script to emit slightly different formatting. The developer runs `python3 tools/catalog/codegen.py --catalog ... --output messages.py` locally on 3.12 and commits the result; CI on 3.11 re-runs codegen and sees a diff, failing the drift gate at cut time.

From the project memory: "py3.12-masks-py3.11 ruff/codegen issue seen at prior cuts" and "validate ruff check + ruff format --check against the target before claiming CI green."

**Why it happens:**

The drift gate is designed to be deterministic, but `ruff format` and the codegen script itself can produce different output across Python minor versions for edge cases (f-strings, string quoting, trailing comma rules). The developer only discovers this at beta-cut time because that is when CI runs against the pinned Python version. By then the commit is already made and the fix requires a follow-up commit.

**How to avoid:**

1. **Run codegen + drift gate using the CI Python version**, not the devcontainer default. In the devcontainer: `python3.11 tools/catalog/codegen.py ...` (or activate a venv pinned to 3.11 for codegen work).
2. **After editing `messages.toml` and running codegen**, always run `ruff format --check` and `ruff check` against the generated output with the 3.11-compatible ruff version before committing.
3. **Add a note to the catalog-sync plan step**: "regenerate using `python3.11`; if py3.11 is not installed in the devcontainer, install it with `apt-get install python3.11` or use the CI-equivalent environment."
4. **At beta-cut time**, run the CI workflow on a draft PR first and watch the codegen drift step before pushing to `beta`. This has caught drift at both prior milestone cuts.

**Warning signs:**

- The devcontainer's `python3 --version` reports 3.12 while CI runs 3.11.
- A newly generated `messages.py` or `messages.h` passes local `git diff --exit-code` but fails the drift gate in CI.
- Ruff reports no issues locally but fails in CI — the py3.12-vs-3.11 f-string backslash issue presents exactly this way.

**Phase to address:**

Any phase that modifies `messages.toml` or its generated artifacts must include a "verify codegen with py3.11" plan step before the commit is pushed. The beta-cut phase must include this check as a blocking pre-cut gate.

---

### Pitfall 4: Skeleton handlers that accidentally touch hardware before returning not-implemented

**What goes wrong:**

A skeleton handler for an unimplemented protocol is written as a stub that sets `handle->response_code = RESPONSE_CODE_ERROR` and emits `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`, but the developer copies the structure from an existing handler (e.g. `configure_eprom`) and forgets to remove the hardware-setup calls that appear before the error return in the real handler. Specifically:

- `configure_eprom` calls `eprom_check_vpp()` early in its body, which enables the VPP boost regulator (`CTRL_VPP_REGULATOR_ENABLE`) and samples the ADC.
- Any skeleton that inherits this structure and calls `eprom_check_vpp()` before the not-implemented guard will enable 12V on the VPP regulator — exactly the hazard v1.12 is designed to close.
- Similarly, calling `rurp_chip_enable()` or setting address-bus lines before returning not-implemented drives the socket bus with arbitrary state, which can latch data into a seated chip or stress address lines.

The `configure_memory()` dispatch currently assigns `handle->firestarter_operation_main`, `_init`, and `_end` as function pointers via NULL initialization before calling `configure_X`. A skeleton that sets `firestarter_operation_init` to a function that enables the regulator as part of its "init" phase will trigger regulator enable even if the skeleton's configure function itself does not — because the state machine calls `firestarter_operation_init` later.

**Why it happens:**

Copy-paste from working handlers is the fastest way to create a skeleton. The hardware-touching calls are deep inside the handler body or the init/end callbacks, not at the top, making them easy to miss in a quick review.

**How to avoid:**

1. **Write skeleton handlers from a zero-hardware template**, not by copying existing handlers. The template: (a) do NOT assign `firestarter_operation_init`, `firestarter_operation_main`, or `firestarter_operation_end` — leave the NULL assignments from `configure_memory` in place; (b) immediately set `handle->response_code = RESPONSE_CODE_ERROR` and emit the not-implemented message with the protocol value; (c) return. The state machine will not call NULL operation callbacks.
2. **Add a native Unity test** for each skeleton protocol that asserts: `handle->response_code == RESPONSE_CODE_ERROR` AND `handle->firestarter_operation_init == NULL` AND `handle->firestarter_operation_main == NULL` after `configure_memory()` is called with that protocol. This detects hardware-touching regressions in the host-side test suite without any hardware.
3. **Code review checklist for each skeleton**: no VPP regulator enable, no chip enable, no address bus writes, all three operation pointers remain NULL.
4. The existing `host_stubs.cpp` in `test/native/avr/test_dispatch/` provides no-op `rurp_*` stubs. The dispatch tests assert on `handle->firestarter_operation_main` and `handle->response_code` only — so a skeleton that incorrectly hooks in a hardware-touching init callback will cause the test to fail because `firestarter_operation_init != NULL`.

**Warning signs:**

- A skeleton handler file that `#include`s `eprom.h`, `flash_intel.h`, or similar and calls any `*_check_vpp*`, `rurp_chip_enable`, or `rurp_write_to_register` function.
- A native dispatch test for a skeleton that passes but does NOT assert `firestarter_operation_init == NULL`.
- Flash measurement after adding skeletons shows unexpected increase caused by PROGMEM strings or function bodies from hardware-touching paths being compiled in.

**Phase to address:**

The skeleton-handler scaffolding phase must include a zero-hardware-template requirement and a native Unity test asserting both the not-implemented response code and the NULL operation pointers for every skeleton. This phase should not begin until the not-implemented message ID is defined and the catalog is synchronized.

---

### Pitfall 5: `check_dispatch.py` drift — the guard does not model the new fail-closed outcome and gives false assurance

**What goes wrong:**

`check_dispatch.py`'s `dispatch()` function (lines 75-95) currently models the firmware dispatch including the `mem_type` fallback chain (lines 89-95). After v1.12 removes the fallback and adds the fail-closed not-implemented path, `dispatch()` must be updated to match. If it is not updated:

1. Any chip whose `algorithm` is not in the currently-handled protocol set will still "resolve" to a `mem_type`-based handler in the simulation, masking the fact that the firmware now returns an error for that chip.
2. The `errors` list (filled when `handler == "ERROR"`) will only fire for chips with `mem_type` outside {1, 3, 4, 5} — the same behavior as today — even though the firmware now returns not-implemented for every unknown protocol regardless of `mem_type`.
3. The BLOCKER-2 SRAM safety guard (`sram_in_eprom` list) is correct only if `dispatch()` accurately models the firmware path. With a stale `dispatch()` the guard can give a false PASS.

Additionally, `check_dispatch.py` has a pre-existing gap: it handles `0x05` explicitly but NOT `0x35` or `0x39` (the full `configure_flash4` set that the firmware dispatches together at `memory.cpp` line 88-89). For `0x35` chips, `dispatch()` falls through to the mem_type fallback (`mem_type=5 → configure_flash4`), which happens to give the correct answer coincidentally — not structurally. If the fallback is removed, `0x35` chips will route to `"ERROR"` in `check_dispatch.py` because the `dispatch()` function has no explicit case for them.

**Why it happens:**

`check_dispatch.py` was written to mirror the firmware dispatch at the time of Phase 12. The firmware has been extended since (0x35/0x39 added), but `dispatch()` was not updated. The v1.12 fail-closed change is a second opportunity for the same pattern. Because the CI gate only runs `check_dispatch.py` (not a diff of `check_dispatch.py` against `memory.cpp`), the drift is invisible until someone audits the two files side-by-side.

**How to avoid:**

1. **Update `check_dispatch.py`'s `dispatch()` to match the new `configure_memory` dispatch order** as the first step of the fail-closed dispatch phase — before any firmware changes. The updated `dispatch()` must: add explicit cases for `0x35` and `0x39`; replace the mem_type fallback with `"NOT_IMPLEMENTED"` (or a similar string); treat `"NOT_IMPLEMENTED"` as a distinct non-error outcome (not the same as `"ERROR"`) in the scan loop.
2. **Add a new `not_implemented` list** in the main scan loop alongside `errors`, `sram_in_eprom`, etc., that collects chips resolving to `"NOT_IMPLEMENTED"`. The gate should print a summary (e.g. "N chips resolve to not-implemented") but NOT fail on it — that is the expected, safe outcome of the new dispatch.
3. **Write a unit test for `dispatch()`** that exhaustively covers every protocol value in `KNOWN_PROTOCOLS` plus the new fail-closed case and the `0x35`/`0x39` protocols.
4. **Review `check_dispatch.py` against `memory.cpp` as a paired artifact** at every phase that modifies dispatch logic. The CLAUDE.md note "Dispatch order in memory.cpp:configure_memory (source-of-truth — must match check_dispatch.py line-for-line)" must be enforced as a phase-close gate, not just documentation.

**Warning signs:**

- `check_dispatch.py` exit 0 after the firmware fallback is removed, even though some chips now get not-implemented responses.
- `0x35`-protocol chips routing to `configure_flash4` via the mem_type fallback in `dispatch()` rather than an explicit protocol branch.
- The PASS message says "0 chips have no valid dispatch path" but does not mention the number of chips routing to not-implemented.

**Phase to address:**

The `check_dispatch.py` update is a prerequisite for the fail-closed dispatch phase and must be its own plan step or sub-phase. It should be committed before the firmware `memory.cpp` changes so that the updated gate is already in place when the firmware change is reviewed.

---

### Pitfall 6: "recognized-but-not-implemented" and "totally-unknown" conflated into one error code

**What goes wrong:**

If the fail-closed dispatch emits a single `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` for both (a) a protocol the firmware has explicitly enumerated as "skeleton — not yet implemented" and (b) a completely unknown protocol value that has never been seen before, the host cannot distinguish between them. This matters because:

- For case (a), the host should surface: "This chip's programming protocol (0x3C) is recognized but not yet implemented in the firmware. A future firmware update will add support." This is actionable for the user.
- For case (b), the host should surface: "This chip's programming protocol (0x99) is unknown and may not be supported on this hardware." This signals a database or firmware mismatch.

If both cases emit the same message ID with the same protocol-byte parameter, the host's error rendering falls back to a generic string and the operator loses diagnostic information. This is especially relevant for the v1.12 "protocol-gap enumeration" deliverable: the goal is to classify every protocol as implemented / skeleton / infeasible, and that classification should be reflected in the wire response.

**Why it happens:**

The simplest implementation is a single `else { emit NOT_IMPLEMENTED; }` at the bottom of `configure_memory()`. It handles both cases with one code path and one message ID. The distinction only becomes visible when a user encounters a chip with an unexpected protocol value and the error message gives no hint whether it is a known gap or something completely off the map.

**How to avoid:**

1. **Use the protocol-byte parameter** on the not-implemented message to carry the `protocol` value. The host can then look up the value in its own catalog (the v1.11 `protocol_id.md` classification) and render the distinction itself, without needing two separate message IDs from the firmware.
2. **Alternatively, define two message IDs**: `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` (for explicitly-registered skeletons) and `MSG_ERR_PROTOCOL_UNKNOWN` (for unrecognized values). The firmware emits the former for protocols in the known-skeleton set and the latter for everything else. This is cleaner but costs one additional catalog entry.
3. **The recommended approach for v1.12**: single `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` with the protocol value as a u8/u32 param; the host renders "Protocol 0xXX is recognized but not yet implemented" for protocols in the known-skeleton set (a Python-side lookup against the v1.11 classification), and "Protocol 0xXX is unrecognized" for values outside that set. This minimizes firmware flash cost (one message, not two) while preserving diagnostic quality.
4. **Update `exceptions.py`** to carry a `protocol_id` field on whatever exception class surfaces the not-implemented response, so the CLI handler can render the appropriate message.

**Warning signs:**

- The host prints "Memory type 0x01 not supported" (the old `MSG_ERR_MEM_TYPE_UNSUPPORTED` wording) for an unimplemented protocol — indicates the host is not decoding the new message ID.
- The host prints a generic "operation failed" without any protocol value — indicates the new message ID is being decoded but the protocol-byte param is not being extracted.
- `serial_comm.py`'s error path uses `str(message)` or a default format that does not include the param bytes.

**Phase to address:**

This distinction must be designed in the catalog-and-wire-protocol phase (before any firmware dispatch logic is written) and validated in the host-graceful-handling phase (the phase that adds the "protocol not implemented" user-facing error message to `exceptions.py` and `cli_handlers.py`).

---

### Pitfall 7: Flash budget regression — new strings and handlers push Leonardo over the ceiling

**What goes wrong:**

Current flash usage as of 2026-06-10 (measured from live build on `v1.11-infoic-decode-correctness`):

- **Leonardo**: 88.4% (25,354 B of 28,672 B) — 3,318 B remaining
- **Uno**: 72.0% (23,216 B of 32,256 B) — 9,040 B remaining

Leonardo is the constrained board. The v1.12 changes add: (a) skeleton handler function bodies (small but non-zero); (b) at minimum one new `MSG_ERR_*` emit site in `configure_memory()` (costs the `rurp_log_id` call site plus the ID byte param); (c) additional dispatch branches in `configure_memory()`.

The v1.2 retrospective established that helper-function refactors targeting flash savings often wash out on AVR-gcc with `-Os`: "AVR-gcc was already inlining the pack bodies efficiently — the CALL/RET overhead ate most of the dedup savings." The same caveat applies in reverse: what looks like "just a return statement" in a skeleton handler may be larger than expected after linking, because each new function introduces a function prologue/epilogue even if the body is trivial.

At 88.4% on Leonardo, adding roughly 3% (approximately 860 B) of new code would put the board at ~91.4%. Still below the 98.7% danger level from before v1.2, but the margin is much tighter than Uno. The risk is real if the skeleton set is large (the v1.11 protocol-gap enumeration found multiple protocols without handlers) and each skeleton contributes even a 50-100 B function body.

**Why it happens:**

Flash cost is invisible during code writing and only surfaces at `pio run --target=size`. Developers writing skeletons focus on correctness, not binary size. Leonardo's 28KB ceiling is 13% smaller than Uno's 32KB, making it the binding constraint for every firmware change.

**How to avoid:**

1. **Measure flash after each skeleton is added**, not at the end. Run `pio run -e leonardo` after the first skeleton to establish the per-skeleton cost, then project whether the full set fits.
2. **Prefer a single shared `configure_not_implemented()` function** called from all skeleton dispatch branches, rather than N separate stub functions. One function body; N if/return call sites (each ~4-8 B on AVR) rather than N full function bodies.
3. **Use a single inlined response call in `configure_memory()` itself** for the fail-closed path — the not-implemented case does not need a per-protocol function at all if the only behavior is "emit message + set error code." The protocol value is already in `handle->protocol`. This is the most flash-efficient approach.
4. **Set a flash-budget gate** in the phase acceptance criteria: `pio run -e leonardo` must report <= 90% after all skeletons are added. This is a hard go/no-go, not a suggestion.

**Warning signs:**

- `pio run -e leonardo` after adding the first few skeletons shows the percentage growing faster than 0.1% per skeleton.
- The skeleton function body inadvertently calls `rurp_shield.h` helpers (which pull in their dependency chain) rather than being truly minimal.
- The `configure_memory()` if-chain grows significantly — each if/return is small but not free.

**Phase to address:**

The skeleton-handler phase must include a post-skeleton flash measurement plan step with a leonardo gate. The measurement should be done on a branch off the final dispatch-logic state (not mid-refactor) so the number is stable. If the gate is at risk, a "consolidate not-implemented path" sub-task must be included before close.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|---|---|---|---|
| Leaving `check_dispatch.py`'s `dispatch()` stale after firmware dispatch change | Saves one file edit | Gate gives false PASS; SRAM safety check may not cover new protocols | Never — update `dispatch()` in the same commit or PR that changes `configure_memory()` |
| Emitting `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` without the protocol value as a param | Simpler catalog entry | Host cannot render a useful message; debugging requires serial capture | Never for v1.12 — the protocol value must be included |
| Reusing `MSG_ERR_NOT_SUPPORTED (0xA5)` instead of defining a new message ID | No catalog change needed | Conflates "command not supported" with "protocol not implemented"; host cannot distinguish | Never — separate semantics deserve separate IDs |
| Copying an existing handler as the skeleton template | Fast to write | Hardware-touching calls may be inherited silently | Never — use the zero-hardware template |
| Not syncing `messages.toml` via `sync_to_subrepos.sh` | Faster dev loop | Both repos' catalogs drift; codegen drift gate only detects intra-repo drift | Never — the sync script is the contract |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|---|---|---|
| meta-repo `messages.toml` to sub-repo sync | Edit firmware sub-repo `messages.toml` directly | Edit only the meta-repo copy; run `sync_to_subrepos.sh`; regenerate in both sub-repos |
| Codegen drift gate with Python version | Run codegen locally on py3.12, commit, fail CI on py3.11 | Explicitly invoke `python3.11` (or a 3.11 venv) for codegen and drift gate before committing |
| `check_dispatch.py` vs `memory.cpp` | Update `memory.cpp` dispatch without updating `dispatch()` in `check_dispatch.py` | Treat the two as a paired artifact; update `check_dispatch.py` first, verify gate, then change firmware |
| Deferred v1.11 host work on `firestarter_app/beta` | Begin v1.12 host changes before the deferred v1.11 work is reconciled into `beta` | Confirm `firestarter_app/beta` tip is clean and post-v1.11 before branching `v1.12-*` off it |

## "Looks Done But Isn't" Checklist

- [ ] **Fail-closed dispatch**: `check_dispatch.py` updated to match new `configure_memory()` order, including removal of mem_type fallback — verify `python tools/check_dispatch.py` exit 0 with the updated `dispatch()` function.
- [ ] **New message ID**: appears in meta-repo `messages.toml`, synced to both sub-repos, both generated files (`messages.h`, `messages.py`) regenerated and committed, codegen drift gate green in both repos.
- [ ] **Skeleton handlers**: each skeleton's native Unity test asserts `handle->response_code == RESPONSE_CODE_ERROR` AND all three operation pointers remain NULL.
- [ ] **`check_dispatch.py` updated**: `0x35` and `0x39` have explicit cases (not relying on mem_type fallback), and a `"NOT_IMPLEMENTED"` outcome is distinct from `"ERROR"` in the scan logic.
- [ ] **Flash budget**: `pio run -e leonardo` reports <= 90% after all skeletons are added.
- [ ] **Host graceful handling**: `firestarter write <unimplemented-chip>` prints a message that includes the protocol value and distinguishes "not yet implemented" from "unrecognized protocol."
- [ ] **Deferred v1.11 host work**: `firestarter_app/beta` is at the correct post-v1.11 state before any v1.12 host changes are committed.
- [ ] **Regression baseline**: pre-removal dispatch baseline test exists and is pinned before the mem_type fallback is deleted.

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---|---|---|
| 1 — mem_type fallback removal unmasks hazard | Phase that establishes pre-removal baseline (Phase 1 of v1.12 roadmap) | Native Unity test covering `(protocol=0, mem_type=1)` exits PASS before the baseline commit; `check_dispatch.py` scan with updated `dispatch()` shows 0 chips newly routing to ERROR that were previously routed to a real handler |
| 2 — lockstep wire desync | Phase that adds the new message ID to the catalog (lockstep-wire phase) | Codegen drift gate green in both sub-repos; cross-repo `diff messages.toml` returns empty |
| 3 — py3.12-vs-py3.11 codegen drift | Same lockstep-wire phase, plus every phase touching catalog artifacts | Explicitly run codegen with `python3.11` in the plan step; CI green on PR before push to beta |
| 4 — skeleton hardware accidental access | Skeleton-handler scaffolding phase | Native Unity test asserts NULL operation pointers and error response code for every skeleton; code review against zero-hardware template checklist |
| 5 — `check_dispatch.py` drift | `check_dispatch.py` update phase (must precede firmware dispatch changes) | `dispatch()` explicitly handles `0x35`/`0x39` and the new fail-closed path; unit test for `dispatch()` covers all known protocols |
| 6 — recognized vs unknown conflated | Catalog-and-wire-protocol design phase + host-graceful-handling phase | Host test: chip with skeleton protocol prints "not yet implemented" including protocol value; chip with unknown protocol value prints "unrecognized protocol" |
| 7 — flash budget regression | Skeleton-handler phase (measure after each batch) | `pio run -e leonardo` <= 90% gate in phase acceptance criteria |

## Sources

- `firestarter/src/proms/memory.cpp` — live dispatch chain and mem_type fallback (lines 73-118), read 2026-06-10
- `firestarter/CLAUDE.md` — dispatch order documentation and backward-compatibility rationale for the fallback
- `firestarter_app/tools/check_dispatch.py` — `dispatch()` function (lines 75-95); gap: no explicit 0x35/0x39 cases, read 2026-06-10
- `firestarter/include/messages.h` + `firestarter_app/firestarter/messages.py` — generated catalog; current highest error ID 0xBA (`MSG_ERR_MEM_SIZE_TOO_SMALL`)
- `firestarter/include/firestarter.h` — `firestarter_handle_t` struct; operation pointer fields
- `firestarter/include/logging_id.h` — `LOG_ERROR_ID_U8` macro chain
- `.planning/RETROSPECTIVE.md` §v1.2 — codegen drift gate; "measure before refactoring for size"; "read the host's expect_ack / probe path before changing the firmware ack shape"
- `.planning/RETROSPECTIVE.md` §v1.10 — dual-repo lockstep pinned by codegen + golden vectors; cross-repo catalog sync pattern
- `.planning/RETROSPECTIVE.md` §v1.0 — "closing a blocker can unmask a deeper hazard"; three-layer fix; audit-then-close
- `.planning/PROJECT.md` §v1.12 — milestone goal statement; mem_type fallback as explicit safety hazard; dual-repo lockstep requirement
- Live `pio run -e uno/leonardo` builds on `v1.11-infoic-decode-correctness` (2026-06-10): Uno 72.0% / Leonardo 88.4%

---
*Pitfalls research for: v1.12 — Firmware Protocol Dispatch Hardening + Skeletons*
*Researched: 2026-06-10*

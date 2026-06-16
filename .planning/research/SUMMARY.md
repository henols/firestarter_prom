# Project Research Summary

**Project:** Firestarter v1.12 — Firmware Protocol Dispatch Hardening + Skeletons
**Domain:** Arduino C++ firmware safety hardening + dual-repo wire-protocol lockstep extension
**Researched:** 2026-06-10
**Confidence:** HIGH

## Executive Summary

v1.12's headline finding reshapes the milestone's framing: the SKELETON-NEEDED bucket is empty. Every RURP-feasible DIP-parallel-memory protocol_id is already implemented in firmware; all 743 chips in `chip_database.json` map to the 13 handled protocols. There are no missing-but-feasible protocols requiring new stub handlers. The milestone's real value is the **fail-closed safety framework and honest not-implemented reporting** — not new protocol coverage.

The primary hazard this milestone addresses is the silent `mem_type` fallback at the bottom of `configure_memory()` in `memory.cpp`. Any chip command that carries an unimplemented non-zero protocol but `mem_type=1 (TYPE_EPROM)` currently routes silently to `configure_eprom`, which enables the 12V VPP boost regulator — a hardware-damage path for chips that don't expect VPP on pin 1. The fix is a `protocol != 0` guard that short-circuits to `configure_not_implemented()` before the `mem_type` chain is reached, while the `protocol == 0` path preserves the fallback for legitimate backward-compat use (hand-crafted JSON, older host versions, user-override DB entries).

The mechanism is minimal: one new catalog message ID (`MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB`) carrying the protocol byte, lockstep codegen across both sub-repos, a shared `configure_not_implemented()` catch-all, and a native dispatch test proving the hazard is closed. The host requires `check_dispatch.py` to gain a `not_implemented` arm and a pre-existing gap (`0x35`/`0x39` explicit dispatch) to be reconciled. Flash cost is under 300 bytes; both boards have 7+ KB headroom. The "skeletons" reframe: a single shared catch-all rather than N dead per-protocol stubs, with optional explicit infeasibility markers for `0x11` (FWH) and `0x2A/0x2B/0x2C` (GAL/PLD) only if the roadmap warrants them.

## Key Findings

### Recommended Stack

The v1.12 change surface is narrow and well-contained within the established codebase. No new dependencies or frameworks are required. The existing response-code infrastructure (`RESPONSE_CODE_ERROR`), catalog codegen pipeline (`messages.toml` -> `messages.h` / `messages.py`), native Unity test harness, and `check_dispatch.py` regression gate are all reused without modification to their contracts.

**Core technologies:**
- `memory.cpp` dispatch chain: the sole firmware change site; `protocol != 0` guard inserted between the protocol-prefix chain and the `mem_type` fallback block
- `messages.toml` + `codegen.py`: canonical catalog in meta-repo; synced to both sub-repos manually (no `sync_to_subrepos.sh` exists — confirmed 2026-06-10); drift gate enforces byte-identity within each repo
- `configure_not_implemented()`: new shared catch-all function in `src/proms/not_implemented.cpp`; calls `LOG_ERROR_ID_U8(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, handle->protocol)` + sets `RESPONSE_CODE_ERROR`; no operation pointers touched
- Native Unity test suite (`test_configure_memory.cpp`): extended with fail-closed assertions; existing `make_handle(0, mem_type, cmd)` tests must remain green
- `check_dispatch.py`: host-side dispatch mirror and VPP-safety gate; requires updating `dispatch()` to model the new fail-closed path before firmware changes land

**Critical version constraint:** Codegen must be run with Python 3.11 (CI target), not the devcontainer's Python 3.12 — the py3.12/3.11 drift trap has caused CI failures at every prior milestone cut that touched the catalog.

### Expected Features

**Must have (table stakes):**
- Fail-closed dispatch: `protocol != 0` guard in `configure_memory()` eliminating the silent VPP-hazard path
- `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB`: new catalog entry with protocol-byte param; codegen lockstep across both sub-repos
- `configure_not_implemented()` catch-all: zero-hardware-effect; emits the new message ID; sets `RESPONSE_CODE_ERROR`; leaves all operation pointers NULL
- `check_dispatch.py` update: `dispatch()` gains `protocol != 0 -> "not_implemented"` arm; `0x35` and `0x39` gain explicit cases; `not_implemented` list + FAIL guard added
- Pre-removal dispatch baseline: native test capturing `(protocol=0, mem_type=1)` behavior before the guard is added; committed before any `memory.cpp` changes
- Native tests: fail-closed path (unknown non-zero protocol must error), legacy path (protocol=0 + mem_type=1 still routes to `configure_eprom`)

**Should have (differentiators):**
- `ProtocolNotImplementedError(EpromOperationError)`: host exception subclass in `exceptions.py`; detection in `_run_state_machine` via `"not implemented" in response.message`; `map_typed_errors` catch in `cli_handlers.py` before `EpromOperationError`
- Explicit infeasibility markers for `0x11` (FWH), `0x2A/0x2B/0x2C` (GAL/PLD): registered dispatch arms calling `configure_not_implemented()` directly; documents the hardware reason; scope decision for planning

**Defer (v2+):**
- Actual programming logic for any new protocol family: no RURP-feasible protocol is unimplemented; defer to hardware-gated per-protocol milestones
- Stubbing all 43 infeasible protocol IDs: only stub IDs a user could plausibly hand-craft (0x11, 0x2A-0x2C at most)
- `ProtocolNotImplementedError` carrying a typed `protocol_id` field: message text is sufficient for v1.12

### Architecture Approach

Three tightly-coupled change sets must land in lockstep: (1) catalog + codegen in both sub-repos establishing the new message ID, (2) firmware `memory.cpp` fail-closed guard + `configure_not_implemented()` + native tests, and (3) host `check_dispatch.py` update + `ProtocolNotImplementedError` + CLI wiring. The catalog step has no observable behavior change and can be reviewed in isolation; it is the prerequisite for every other step.

**Major components:**
1. `memory.cpp` `configure_memory()`: dispatch entry point; receives the `protocol != 0` guard; the mem_type fallback block is preserved intact behind the guard
2. `not_implemented.cpp` / `not_implemented.h`: new file(s) housing `configure_not_implemented()` (catch-all) and any named skeleton dispatch arms; keeps `memory.cpp` clean
3. `messages.toml` (meta-repo canonical) + codegen outputs: the contract between firmware and host; adding `0xBB` here and regenerating both sub-repos is the sole wire-change
4. `check_dispatch.py`: host-side dispatch mirror; must be updated before firmware changes; GATE-03 VPP-safety check depends on it
5. `exceptions.py` + `eprom_operations.py` + `cli_handlers.py`: host error-surface chain; `ProtocolNotImplementedError` threads from firmware frame through to CLI message

### Critical Pitfalls

1. **Deleting the mem_type fallback without a pre-removal baseline** — capture a dispatch baseline (native test + `check_dispatch.py` scan on fallback-present state) before touching any fallback code. Guard with `protocol != 0`; do not delete outright. The fallback serves hand-crafted JSON and pre-algorithm user-override DB entries.

2. **Catalog lockstep desync** — `messages.toml` must be edited in the meta-repo and the identical block manually copied to both sub-repos (no sync script exists); the codegen drift gate only catches intra-repo drift. Edit meta-repo first, copy to both, regenerate with Python 3.11, verify drift gate green in both repos.

3. **py3.12-masks-py3.11 codegen drift** — devcontainer runs Python 3.12; CI pins 3.11; ruff formatter and codegen produce different output across minor versions. Always invoke `python3.11` for codegen and drift gate; validate before pushing. This has caught failures at every prior milestone cut that touched the catalog.

4. **`check_dispatch.py` drift / false assurance** — `dispatch()` currently has no explicit case for `0x35`/`0x39` (they coincidentally route correctly via the mem_type fallback that the firmware change will guard away). Update `check_dispatch.py` BEFORE the firmware changes so the gate is testing the new behavior against the live DB.

5. **Skeleton handlers that accidentally touch hardware** — copy-paste from a working handler inherits hardware-touching calls. Write skeletons from the zero-hardware template only: emit error, set `RESPONSE_CODE_ERROR`, return; leave all three operation pointers NULL. Assert NULL pointers in native tests.

## Implications for Roadmap

Based on research, suggested phase structure (4 phases):

### Phase 1: Baseline Capture + `check_dispatch.py` Update
**Rationale:** All subsequent phases depend on a known-good baseline and an accurate regression gate. Update `check_dispatch.py` first, before any firmware changes, so the gate is probing the new behavior against the old DB.
**Delivers:** Updated `dispatch()` with explicit `0x35`/`0x39` cases + `"not_implemented"` arm + `not_implemented` FAIL guard; a native test asserting the current `(protocol=0, mem_type=1)` behavior; CI green with 0 newly-broken chips.
**Addresses:** Fail-closed dispatch prerequisite; check_dispatch.py drift pitfall; pre-removal baseline requirement.
**Avoids:** Pitfall 1 (mem_type removal without baseline), Pitfall 5 (check_dispatch.py false assurance).

### Phase 2: Catalog Lockstep Wire Change
**Rationale:** The new message ID must exist in both sub-repos' generated files before any firmware or host code references it. This step has no observable behavior change and can be reviewed in isolation.
**Delivers:** `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB` in meta-repo `messages.toml`; identical block in both sub-repo `messages.toml` copies; regenerated `messages.h` + `messages.py` committed; CI drift gate green in both repos using Python 3.11.
**Addresses:** New message ID prerequisite for all other phases.
**Avoids:** Pitfall 2 (lockstep desync), Pitfall 3 (py3.12/3.11 drift trap).

### Phase 3: Firmware Fail-Closed Dispatch + Native Tests
**Rationale:** With the baseline captured and the catalog synced, the firmware change is safe to make. This is the primary safety fix. `configure_not_implemented()` is the shared skeleton catch-all.
**Delivers:** `configure_not_implemented()` in `not_implemented.cpp`; `protocol != 0` guard in `configure_memory()`; optional named stubs for `0x11`/`0x2A`/`0x2B`/`0x2C` (scope decision for planning); native Unity tests; `pio run -e leonardo` flash gate (must stay <= 90%).
**Addresses:** Fail-closed dispatch, skeleton handler scaffolding, flash budget.
**Avoids:** Pitfall 4 (skeleton hardware accidental access), Pitfall 7 (flash budget regression).

### Phase 4: Host Graceful Handling + Integration
**Rationale:** With firmware emitting the new error ID, the host needs to surface it cleanly. The exception subclass, detection logic, and CLI message are straightforward given the established error-flow path.
**Delivers:** `ProtocolNotImplementedError(EpromOperationError)` in `exceptions.py`; detection in `_run_state_machine`; `map_typed_errors` catch in `cli_handlers.py` before `EpromOperationError`; pytest tests using mocked ERROR response; CI green.
**Addresses:** Host graceful handling; user-facing message clarity.
**Avoids:** Anti-pattern of string-matching inside ring-fenced `_read_and_parse_lines` (GATE-1.8d); anti-pattern of reusing `MSG_ERR_NOT_SUPPORTED`.

### Phase Ordering Rationale

- Phase 1 must precede Phase 3: `check_dispatch.py` must be committed and CI-green before any `memory.cpp` change lands
- Phase 2 must precede Phase 3: firmware cannot call `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` until the constant is in `messages.h`
- Phase 2 must precede Phase 4: host cannot import the constant from `messages.py` until codegen has run
- Phases 1 and 2 can be ordered either way or combined; no dependency between them
- Phase 4 can be partially developed in parallel with Phase 3 (mock tests don't require live firmware) but must not merge until Phase 3 is committed

### Open Design Questions for Planning

1. **Single `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` vs two IDs** — one ID carrying the protocol byte as a param (host lookup determines "recognized infeasible" vs "totally unknown") vs two IDs. Researchers lean toward single ID; resolve at planning based on CLI UX requirements.

2. **Named infeasibility stubs vs catch-all only** — whether to register explicit dispatch arms for `0x11`/`0x2A/0x2B/0x2C` (documenting infeasibility reason in-code) or rely on the single catch-all. Flash cost is trivial; the question is documentation value vs dispatch-chain noise.

3. **`messages.toml` sync mechanism** — no `sync_to_subrepos.sh` script exists. Planning must either add a sync script or document the manual-copy procedure explicitly to prevent the lockstep desync pitfall.

4. **In-the-wild user-override entries** — user `~/.firestarter/database.json` entries that omit `algorithm` rely on the `mem_type=1` fallback. Cannot be statically audited. The `protocol == 0` backward-compat path handles this; document the behavior change in release notes.

### Research Flags

Phases with standard patterns (skip research-phase):
- **Phase 1:** `check_dispatch.py` update — mechanical mirror of `memory.cpp` dispatch order; well-understood
- **Phase 2:** Catalog codegen lockstep — exact pattern from v1.10/v1.11; no new discovery needed
- **Phase 3:** Firmware dispatch guard — pattern established in `memory.cpp`; native test harness well-understood
- **Phase 4:** Host error-flow — exception hierarchy + `_run_state_machine` + `cli_handlers` pattern established in v1.8

No phases need `/gsd-plan-phase --research-phase` — all architectural patterns are verified from source.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All mechanism findings from direct source read of `memory.cpp`, `messages.toml`, `codegen.py`, `messages.h/py`, test harness; flash budget measured live |
| Features | HIGH | Protocol-ID classification exhaustive against minipro `database.h` at confirmed commit; SKELETON-NEEDED bucket confirmed empty by cross-checking KNOWN_PROTOCOLS, filter logic, and v1.11 docs |
| Architecture | HIGH | Component boundaries, build order, and anti-patterns verified from direct source inspection of all 6 relevant files; no inference |
| Pitfalls | HIGH | All 7 pitfalls sourced from actual prior-milestone retrospectives (v1.0, v1.2, v1.10, v1.11) + live code gaps found by reading `check_dispatch.py` against `memory.cpp` |

**Overall confidence:** HIGH

### Gaps to Address

- **No `sync_to_subrepos.sh`** — confirmed absent 2026-06-10. Planning must either add the script or establish an explicit manual-copy procedure as a phase plan step.
- **`check_dispatch.py` 0x35/0x39 gap** — pre-existing; not broken today because the mem_type fallback coincidentally returns the right answer. Must be fixed in Phase 1 before the fallback is guarded away.
- **User-override DB entry population** — cannot be statically audited. The `protocol == 0` backward-compat path handles this, but release notes must document the behavior change.
- **`u8` vs `u32` param type for new message** — STACK.md recommends `u8` (protocol always fits, smaller flash); ARCHITECTURE.md recommends `u32` (future-proofs `firestarter_handle_t.protocol` which is declared `uint32_t`). Resolve at planning; lean toward `u8` to match the existing `MSG_ERR_MEM_TYPE_UNSUPPORTED` convention.
- **`ProtocolNotImplementedError` scope** — STACK.md says not required for v1.12; ARCHITECTURE.md includes it. Recommend including it in Phase 4 (~10 lines, improves host testability).

## Sources

### Primary (HIGH confidence)

- `firestarter/src/proms/memory.cpp` — dispatch chain, lines 73-118 (direct read 2026-06-10)
- `firestarter/include/firestarter.h` — response codes, `firestarter_handle_t` (direct read)
- `firestarter/tools/catalog/messages.toml` + `firestarter/include/messages.h` + `firestarter_app/firestarter/messages.py` — catalog; ERROR band confirmed ending at `0xBA`; `0xBB` confirmed free
- `firestarter_app/tools/check_dispatch.py` — `dispatch()` function; 0x35/0x39 gap confirmed (direct read)
- `firestarter_app/firestarter/serial_comm.py`, `exceptions.py`, `eprom_operations.py`, `cli_handlers.py` — host error-flow chain (direct read)
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — native test harness pattern (direct read)
- minipro `database.h` IC2_ALG_* constants @ `a8efaedc236c1d9718bd28299dfbb99536b010ff` — exhaustive protocol-ID classification source
- `firestarter_app/tools/build_db.py` — KNOWN_PROTOCOLS (11 IDs), filter logic, PROTOCOL_MAP (direct read)
- Live `pio run -e uno/leonardo` flash measurements on `v1.11-infoic-decode-correctness` (2026-06-10): Uno 70.8% / 23,216 B; Leonardo 77.4% / 25,354 B

### Secondary (MEDIUM confidence)

- `.planning/RETROSPECTIVE.md` sections v1.0, v1.2, v1.10 — pitfall pattern sources (retrospective notes, not primary code)
- `firestarter/CLAUDE.md` — dispatch order documentation; backward-compat rationale for mem_type fallback
- `.planning/PROJECT.md` section v1.12 — milestone scope and key decisions record

---
*Research completed: 2026-06-10*
*Ready for roadmap: yes*

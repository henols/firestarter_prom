# Requirements: v1.12 — Firmware Protocol Dispatch Hardening + Skeletons

**Milestone goal:** Make the **whole stack honest about what it can and cannot program** — (a) firmware fail-closed dispatch with an explicit "not implemented" response the host surfaces cleanly + skeleton (infeasibility-rejection) handlers, and (b) a capability-honest database that *lists* the DIP parallel-memory chips RURP can't fully support (instead of silently dropping them) with a `supported: false` flag the host reports clearly. **Framework + honest reporting only; no new per-protocol programming logic and no new chips become programmable.** Dual-repo lockstep wire change.

**Research finding (reshapes scope):** There are **no RURP-feasible unimplemented protocols** — every DIP parallel-memory protocol_id already has a handler (all 743 DB chips covered). The unimplemented protocol_ids are all infeasible on RURP (serial/LPC/3.3V, GAL/PLD, MCU, SMD-only). So the milestone's value is the **fail-closed safety framework + honest reporting**, and "skeletons" are explicit infeasibility-rejection markers, not future-fill stubs. See `.planning/research/SUMMARY.md`.

---

## v1.12 Requirements

### DISP — Fail-Closed Dispatch (firmware)

- [ ] **DISP-01**: An unknown/unimplemented **non-zero** `protocol` no longer routes to a programming handler — `configure_memory` returns an explicit not-implemented response instead of falling through to the `mem_type` chain, closing the hazard where `protocol`=unknown + `mem_type=1` reaches `configure_eprom` (12V VPP on a 5V part).
- [ ] **DISP-02**: The legacy `mem_type` fallback is preserved ONLY for `protocol == 0` (hand-crafted / pre-`algorithm` legacy JSON), behind an explicit, auditable guard — no dispatch change for any chip the current `chip_database.json` emits.
- [ ] **DISP-03**: A shared `configure_not_implemented()` handler reports not-implemented with **zero hardware side effects** (no VPP regulator enable, no chip-enable, no address/data drive) and sets no operation function pointers.
- [ ] **DISP-04**: The protocols a user might plausibly hand-craft but that are infeasible on RURP (`0x11` FWH, `0x2A`/`0x2B`/`0x2C` GAL/PLD) are explicitly recognized and routed to the not-implemented response (distinct from "totally unknown", but same wire message + protocol param).

### WIRE — Not-Implemented Wire Response (lockstep, dual-repo)

- [x] **WIRE-01**: A new catalog message `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` (carrying the offending `protocol` byte as a param) is added to the canonical `messages.toml` and code-generated into BOTH sub-repos (`messages.h` + host `messages.py`); the codegen drift gate is green in both repos (generated with the CI-matching Python to avoid the py3.12-masks-py3.11 trap).
- [ ] **WIRE-02**: The firmware emits `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` with the protocol value for every not-implemented dispatch outcome, reusing `RESPONSE_CODE_ERROR` (no new response code added).

### HOST — Host Graceful Handling (firestarter_app)

- [ ] **HOST-01**: The host detects the not-implemented response and raises a typed `ProtocolNotImplementedError` (subclass of `EpromOperationError`), distinguishable from generic operation failures.
- [ ] **HOST-02**: `firestarter write` / `read` / `verify` against a chip whose protocol is unimplemented prints a clear, actionable message (decoding recognized-but-infeasible vs totally-unknown via the v1.11 protocol classification) instead of a cryptic error or hang.

### GATE — Dispatch-Mirror Safety Gate (host)

- [x] **GATE-01**: A pre-removal dispatch baseline is captured (every DB chip's resolved handler + representative `protocol==0`/legacy and unknown-protocol cases) and committed BEFORE the fallback is guarded, providing regression evidence that no current chip changes dispatch.
- [x] **GATE-02**: `check_dispatch.py` gains a `not_implemented` arm mirroring the firmware `protocol != 0` guard, plus a FAIL assertion that no DB chip resolves to not-implemented; the pre-existing `0x35`/`0x39` dispatch-mirror gap is reconciled. Exits clean across all 743 chips.

### TEST — Native Dispatch Coverage (firmware)

- [ ] **TEST-01**: Native (host, no-hardware) Unity dispatch tests cover the new paths — unknown non-zero protocol → not-implemented; `protocol==0` + `mem_type` → legacy fallback still works; named infeasibility markers (`0x11`/`0x2A`/`0x2B`/`0x2C`) → not-implemented; `configure_not_implemented` sets no operation pointers and ERROR response. All pre-existing dispatch tests stay green.
- [ ] **TEST-02**: Flash-budget regression check — the v1.12 addition keeps both Uno and Leonardo builds under their flash ceilings (Leonardo is the binding constraint).

### DB — Capability-Honest Database Inclusion (host)

**Capability taxonomy** (machine-readable `support_status` + `unsupported_reason` per chip): `supported` | `protocol-not-implemented` | `adapter-required` | `vpp-exceeds-max`. Only genuinely-irrelevant serial / GAL-PLD / MCU / SMD-only parts stay skipped entirely.

- [ ] **DB-01**: `build_db.py` no longer silently drops DIP parallel-memory chips (24/28/32-pin, Memory/SRAM type). Chips with an **unknown/unimplemented `protocol_id`** are INCLUDED in `chip_database.json` marked `support_status: protocol-not-implemented` (NOT routed to a handler) — so they are visible and "can maybe be resolved later" when/if the protocol is implemented. Serial/GAL/MCU/SMD parts remain skipped (existing warning).
- [ ] **DB-02**: **Pinouts are classified, not skipped.** For DIP parallel chips whose pinout `build_db.py` currently can't classify, make a best-effort principled classification to a RURP pinout (extending the Phase-58 `resolve_pinout_key` rules). Only if a chip genuinely cannot be mapped correctly to RURP's bus is it INCLUDED marked `support_status: adapter-required` with a note on what adapter/mapping would be needed (tie to the existing `firestarter info --adapter` concept). No DIP-parallel chip is dropped for pinout reasons.
- [ ] **DB-03**: **Correct VPP is recorded, not the truncated cap.** For DIP parallel chips authoritatively known to need a VPP above the upstream 18V `infoic.xml` cap (the documented NMOS family — Intel `M2716`/`M2732` = 25V, `M2732A` = 21V, and equivalents), the DB records the **true VPP**. `support_status` is then derived from the RURP hardware VPP ceiling (~22V): true VPP > ceiling → `vpp-exceeds-max`; true VPP within range → `supported` at the corrected voltage. (The exact ceiling, the curated known-exception list, and NMOS-vs-CMOS alias splitting are resolved at plan time — scope is the authoritatively-known cases, not a blanket VPP re-survey.)
- [ ] **DB-04**: The host reports capability honestly — `firestarter info <chip>` shows the `support_status` + reason; `firestarter write` / `read` / `verify` on a non-`supported` chip prints a clear, status-specific message ("protocol not implemented" / "adapter required: <note>" / "VPP <x>V exceeds programmer max") and does NOT attempt the hardware operation (rather than silently failing, mis-programming at a wrong voltage, or "chip not found").
- [ ] **DB-05**: The correctness/dispatch gate accounts for non-`supported` entries — `check_dispatch.py` (and the per-chip diff) treat them as non-dispatchable (they must NOT resolve to a programming handler) and the gate stays green across the regenerated DB.

---

## Future Requirements (deferred)

- **Per-protocol implementation** of any genuinely-feasible protocol that a future minipro/infoic update or a new RURP shield revision makes drivable — each is its own (likely hardware-gated) milestone, filling in a skeleton.
- **Erase-command firmware support** for the 0x07-path electrically-erasable EEPROMs surfaced in v1.11 (`firestarter erase W27C512` etc.) — a separate firmware backlog item, not protocol-dispatch.

## Out of Scope

- **Implementing any infeasible protocol** (serial/LPC/3.3V `0x11`; GAL/PLD `0x2A`/`0x2B`/`0x2C`; MCU; SMD-only) — RURP cannot physically drive these (fixed 5V VCC, ≤18V VPP, DIP parallel only). They get not-implemented markers, never handlers.
- **New response codes** — the not-implemented outcome reuses `RESPONSE_CODE_ERROR`; discrimination is via the message ID + protocol param.
- **Deleting the `mem_type` fallback outright** — it is guarded (`protocol==0` only), not removed, to preserve hand-crafted/legacy JSON.
- **Hardware/bench validation** — this milestone is provable on the native dispatch harness + host pytest; no bench session required to close.
- **Making any new chip programmable** — `supported: false` entries are *listed and reported honestly*, NOT made to work; no chip gains real programming support this milestone (that's the deferred per-protocol / hardware work).
- **Serial / GAL-PLD / MCU / SMD-only chips** — remain skipped from the DB entirely; only DIP parallel memory is included-but-flagged.

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| GATE-01 | Phase 62 | Complete |
| GATE-02 | Phase 62 | Complete |
| WIRE-01 | Phase 63 | Complete |
| WIRE-02 | Phase 64 | Pending |
| DISP-01 | Phase 64 | Pending |
| DISP-02 | Phase 64 | Pending |
| DISP-03 | Phase 64 | Pending |
| DISP-04 | Phase 64 | Pending |
| TEST-01 | Phase 64 | Pending |
| TEST-02 | Phase 64 | Pending |
| HOST-01 | Phase 65 | Pending |
| HOST-02 | Phase 65 | Pending |
| DB-01 | Phase 66 | Pending |
| DB-02 | Phase 67 | Pending |
| DB-03 | Phase 66 | Pending |
| DB-04 | Phase 68 | Pending |
| DB-05 | Phase 66 | Pending |

**Mapped: 17/17 requirements ✓** — no orphans, no duplicates.

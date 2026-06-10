# Requirements: v1.12 — Firmware Protocol Dispatch Hardening + Skeletons

**Milestone goal:** Make the firmware honestly report unimplemented programming protocols — fail-closed dispatch with an explicit "not implemented" response the host surfaces cleanly — and scaffold skeleton (infeasibility-rejection) handlers for the protocols a user might plausibly attempt. **Framework + skeletons only; no new per-protocol programming logic.** Dual-repo lockstep wire change.

**Research finding (reshapes scope):** There are **no RURP-feasible unimplemented protocols** — every DIP parallel-memory protocol_id already has a handler (all 743 DB chips covered). The unimplemented protocol_ids are all infeasible on RURP (serial/LPC/3.3V, GAL/PLD, MCU, SMD-only). So the milestone's value is the **fail-closed safety framework + honest reporting**, and "skeletons" are explicit infeasibility-rejection markers, not future-fill stubs. See `.planning/research/SUMMARY.md`.

---

## v1.12 Requirements

### DISP — Fail-Closed Dispatch (firmware)

- [ ] **DISP-01**: An unknown/unimplemented **non-zero** `protocol` no longer routes to a programming handler — `configure_memory` returns an explicit not-implemented response instead of falling through to the `mem_type` chain, closing the hazard where `protocol`=unknown + `mem_type=1` reaches `configure_eprom` (12V VPP on a 5V part).
- [ ] **DISP-02**: The legacy `mem_type` fallback is preserved ONLY for `protocol == 0` (hand-crafted / pre-`algorithm` legacy JSON), behind an explicit, auditable guard — no dispatch change for any chip the current `chip_database.json` emits.
- [ ] **DISP-03**: A shared `configure_not_implemented()` handler reports not-implemented with **zero hardware side effects** (no VPP regulator enable, no chip-enable, no address/data drive) and sets no operation function pointers.
- [ ] **DISP-04**: The protocols a user might plausibly hand-craft but that are infeasible on RURP (`0x11` FWH, `0x2A`/`0x2B`/`0x2C` GAL/PLD) are explicitly recognized and routed to the not-implemented response (distinct from "totally unknown", but same wire message + protocol param).

### WIRE — Not-Implemented Wire Response (lockstep, dual-repo)

- [ ] **WIRE-01**: A new catalog message `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` (carrying the offending `protocol` byte as a param) is added to the canonical `messages.toml` and code-generated into BOTH sub-repos (`messages.h` + host `messages.py`); the codegen drift gate is green in both repos (generated with the CI-matching Python to avoid the py3.12-masks-py3.11 trap).
- [ ] **WIRE-02**: The firmware emits `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` with the protocol value for every not-implemented dispatch outcome, reusing `RESPONSE_CODE_ERROR` (no new response code added).

### HOST — Host Graceful Handling (firestarter_app)

- [ ] **HOST-01**: The host detects the not-implemented response and raises a typed `ProtocolNotImplementedError` (subclass of `EpromOperationError`), distinguishable from generic operation failures.
- [ ] **HOST-02**: `firestarter write` / `read` / `verify` against a chip whose protocol is unimplemented prints a clear, actionable message (decoding recognized-but-infeasible vs totally-unknown via the v1.11 protocol classification) instead of a cryptic error or hang.

### GATE — Dispatch-Mirror Safety Gate (host)

- [ ] **GATE-01**: A pre-removal dispatch baseline is captured (every DB chip's resolved handler + representative `protocol==0`/legacy and unknown-protocol cases) and committed BEFORE the fallback is guarded, providing regression evidence that no current chip changes dispatch.
- [ ] **GATE-02**: `check_dispatch.py` gains a `not_implemented` arm mirroring the firmware `protocol != 0` guard, plus a FAIL assertion that no DB chip resolves to not-implemented; the pre-existing `0x35`/`0x39` dispatch-mirror gap is reconciled. Exits clean across all 743 chips.

### TEST — Native Dispatch Coverage (firmware)

- [ ] **TEST-01**: Native (host, no-hardware) Unity dispatch tests cover the new paths — unknown non-zero protocol → not-implemented; `protocol==0` + `mem_type` → legacy fallback still works; named infeasibility markers (`0x11`/`0x2A`/`0x2B`/`0x2C`) → not-implemented; `configure_not_implemented` sets no operation pointers and ERROR response. All pre-existing dispatch tests stay green.
- [ ] **TEST-02**: Flash-budget regression check — the v1.12 addition keeps both Uno and Leonardo builds under their flash ceilings (Leonardo is the binding constraint).

---

## Future Requirements (deferred)

- **Per-protocol implementation** of any genuinely-feasible protocol that a future minipro/infoic update or a new RURP shield revision makes drivable — each is its own (likely hardware-gated) milestone, filling in a skeleton.
- **Erase-command firmware support** for the 0x07-path electrically-erasable EEPROMs surfaced in v1.11 (`firestarter erase W27C512` etc.) — a separate firmware backlog item, not protocol-dispatch.

## Out of Scope

- **Implementing any infeasible protocol** (serial/LPC/3.3V `0x11`; GAL/PLD `0x2A`/`0x2B`/`0x2C`; MCU; SMD-only) — RURP cannot physically drive these (fixed 5V VCC, ≤18V VPP, DIP parallel only). They get not-implemented markers, never handlers.
- **New response codes** — the not-implemented outcome reuses `RESPONSE_CODE_ERROR`; discrimination is via the message ID + protocol param.
- **Deleting the `mem_type` fallback outright** — it is guarded (`protocol==0` only), not removed, to preserve hand-crafted/legacy JSON.
- **Hardware/bench validation** — this milestone is provable on the native dispatch harness + host pytest; no bench session required to close.
- **Host DB changes** — `chip_database.json` is unchanged; no chip gains or loses support.

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| GATE-01 | TBD | Pending |
| GATE-02 | TBD | Pending |
| WIRE-01 | TBD | Pending |
| WIRE-02 | TBD | Pending |
| DISP-01 | TBD | Pending |
| DISP-02 | TBD | Pending |
| DISP-03 | TBD | Pending |
| DISP-04 | TBD | Pending |
| TEST-01 | TBD | Pending |
| TEST-02 | TBD | Pending |
| HOST-01 | TBD | Pending |
| HOST-02 | TBD | Pending |

_(Phase column filled by the roadmapper.)_

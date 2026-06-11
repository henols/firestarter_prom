# Phase 63: Catalog Lockstep Wire Change - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-10
**Phase:** 63-catalog-lockstep-wire-change
**Areas discussed:** Catalog entry shape (message definition)

---

## Catalog entry shape (MSG_ERR_PROTOCOL_NOT_IMPLEMENTED definition)

| Option | Description | Selected |
|--------|-------------|----------|
| Mirror 0xAE, hex byte | Match existing `MSG_ERR_MEM_TYPE_UNSUPPORTED` (0xAE) exactly — `format = "Protocol 0x%02x not implemented"`, `params = [{ type = "u8", render = "hex_byte" }]`. Hex matches how protocol_id/algorithm_id are discussed everywhere. | ✓ |
| Decimal protocol value | Render protocol byte as plain decimal — `format = "Protocol %u not implemented"`, `params = [{ type = "u8" }]`. | |
| Different wording | Same shape, tweaked human-readable string. | |

**User's choice:** Mirror 0xAE, hex byte
**Notes:** This was the only genuine gray area in the phase. ID placement (0xBB), edit/sync workflow, and the py3.11 codegen constraint were all presented as already-locked by roadmap/requirements/file-convention and not put to a vote.

---

## Claude's Discretion

- Exact mechanics of invoking Python 3.11 in the devcontainer for codegen, and whether the drift gate is verified via the CI workflow command or a direct `codegen.py` + `git diff --exit-code`. The requirement (green under 3.11) is fixed; the invocation is the executor's call.

## Deferred Ideas

- Firmware emit of the new message (Phase 64 — WIRE-02, DISP-01..04, TEST-01/02). No call sites added this phase by design.
- Host `ProtocolNotImplementedError` + actionable CLI message (Phase 65 — HOST-01, HOST-02).

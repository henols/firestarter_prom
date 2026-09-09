# GSD Debug Knowledge Base

Resolved debug sessions. Used by `gsd-debugger` to surface known-pattern hypotheses at the start
of new investigations.

---

## beta-probe-empty-input — Uno-class probe self-sustaining failure via spurious ack interleave
- **Date:** 2026-09-09
- **Error patterns:** Empty input, ERROR: Empty input, responded but not with OK, No compatible
  programmer found, Bad JSON, Buf val: 0x7b, self-sustaining probe failure, Uno DTR reset,
  MSG_ERR_EMPTY_INPUT
- **Root cause(s):** Firmware reuses `MSG_ERR_EMPTY_INPUT` ("Empty input") as a generic catch-all
  for every CMD_IDLE COBS-decode failure (empty read, CRC mismatch, COBS violation, or
  read/inter-byte underrun), so the host cannot distinguish a real command rejection from an
  unrelated, self-recovering framing glitch; `SerialCommunicator.expect_ack()`/`_probe_port`
  treat the FIRST post-send OK/ERROR response as final, with no check for whether the genuine ack
  is already queued immediately behind it. Both conditions were required (AND-gate): the ambiguous
  error text alone is cosmetic, and the host's read-first-response behavior alone would be
  harmless if firmware never emitted an unsolicited frame between a sent command and its ack.
  No firmware code regression was found or is implicated — a full source-diff bisect proved
  `firestarter_uno.hex` is compiled-byte-identical across 3.0.0b23/b24/b25 (one version-string
  line differs) and that the b22->b23 code delta never touches the CMD_IDLE decode path.
- **Fix:** `SerialCommunicator._probe_port` (`firestarter_app/firestarter/serial_comm.py`) gives
  the setup ack one bounded extra read (2s) when the first response is exactly the generic
  frame-decode-failure text, before giving up — scoped to this one ambiguous error and to this one
  hazard-free call site (CMD_FW_VERSION never engages VPP/VPE), so a genuine rejection elsewhere
  still fails immediately.
- **Files changed:** firestarter_app/firestarter/serial_comm.py,
  firestarter_app/tests/test_probe_spurious_setup_ack.py
- **Why not caught:** no gate existed for this class. The existing test suite exercised
  `_probe_port`/`expect_ack()` only with clean, well-ordered response streams (see
  `test_fwguard.py`, `test_hw_revision_gate.py`); nothing modeled an interleaved unsolicited
  response between a sent command and its ack, so a host-side "return on first response" gap had
  no test surface to fail against. The bug is also structurally invisible to this project's CI:
  every native/host test runs against a Leonardo-shaped or hardware-free fixture; the Uno-specific
  PORTD/UART pin-sharing hazard class this bug's spurious frame most plausibly originates from
  (already documented twice elsewhere in this codebase — `PREFIX_REGEX`'s rightmost-match design
  and `rurp_set_communication_mode()`'s boot-transition drain) has no native/CI equivalent at all.
- **Recurrence guard:** regression test
  `firestarter_app/tests/test_probe_spurious_setup_ack.py::test_probe_port_recovers_from_spurious_empty_input_ahead_of_real_ack`
  (RED against the unmodified code, GREEN after the fix) plus its negative-control sibling
  `test_probe_port_still_fails_on_a_genuine_unrecoverable_error`, which pins that the fix does not
  broaden `_probe_port`'s tolerance beyond the one ambiguous error text. If a future firmware
  change ever splits `MSG_ERR_EMPTY_INPUT` into distinct message IDs per failure cause (noted as a
  reasonable future enhancement, not done this session), this KB entry and the retry's text-match
  scoping should be revisited together.
---

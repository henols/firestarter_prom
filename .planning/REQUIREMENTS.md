# Requirements: Firestarter v1.10 — Serial Transport Hardening (COBS)

**Defined:** 2026-06-01
**Milestone goal:** Implement a custom serial framing + automatic-resync layer on the Arduino↔host data path — covering **both** the binary data-block path (host↔fw payload transfers) **and** the host→firmware JSON command channel — so the transport is **provably byte-exact** end to end: delivering exactly the bytes the firmware read off the parallel bus, and exactly the commands the host issued, with any line corruption bounded to a single frame. This rules serial corruption out as a confounding variable before the per-shield read-bug RCA resumes (v1.9 Phase 45+).

**Scope locked:** 2026-06-01 via `/gsd-new-milestone`, inserted ahead of the paused v1.9 RCA. Phase numbering continues at **Phase 49** (45–48 reserved for deferred v1.9 phases).

**Binding inputs (from `.planning/v1.9-COBS-DECISION.md`):** ADOPT a custom framing layer; REJECT all off-the-shelf libraries (§4); KEEP CRC8-CCITT poly 0x07 (D-05); Uno-fit filter (D-04 — streaming encode only, no second ~512 B buffer, ~545 B free-RAM ceiling). The framing **mechanism** (streaming COBS `0x00` per §4.3 vs SLIP/RFC-1055 `0xC0` per §4.2) is deferred to plan-phase research.

**Hardware-gated:** byte-exact transport verification (Uno / Leonardo / uno328pb) is operator-authorized. Per `feedback_chip_out_before_sideload`, the chip leaves the socket before any firmware sideload; per `feedback_verify_port_identity_each_task`, controller identity is verified per port at each bench task; per `user_shield_revisions`, the operator is asked which silkscreen rev is on the bench.

**Lockstep mandate:** root `CLAUDE.md` requires `rurp_serial_utils.cpp` ↔ `serial_comm.py`/`frame_parser.py` to change together; this is a coordinated dual-repo milestone.

## v1.10 Requirements

### 1. Framing Layer (FRAME)

- [ ] **FRAME-01**: A custom delimiter-based framing layer is implemented on the host↔firmware data-block path (streaming COBS `0x00` or SLIP `0xC0`, mechanism chosen in plan research), replacing the desync-prone bare `[len_u16][xor][payload]` frame boundary.
- [ ] **FRAME-02**: Automatic resync — after any framing or integrity error, the receiver discards bytes up to the next frame delimiter and recovers within a single packet; the 2-second `len_u16`-corruption timeout-desync cascade is eliminated.
- [ ] **FRAME-03**: The firmware encoder/decoder is streaming — no second ~512 B encode buffer is materialized; the change fits the Uno ~545 B free-RAM ceiling, proven by a post-change `pio run -e uno` RAM report (D-04).
- [ ] **FRAME-04**: Full board-buffer payloads are framed without operator-visible re-chunking — 512 B (Uno) and 1024 B (Leonardo) transfers complete through the new framing transparently to the eprom read/write loop.
- [ ] **FRAME-05**: The host→firmware JSON command channel is migrated to the same framing layer — the firmware decodes a frame, verifies its CRC8, then hands the payload to the JSON parser; the legacy "`{`-peek and discard non-`{` bytes" path is replaced (or retained only as an explicit fallback). This is a breaking wire-protocol change: firmware and host upgrade lockstep, no mixed-version interop (cf. v1.2 lockstep upgrade).

### 2. Integrity (CRC)

- [ ] **CRC-01**: CRC8-CCITT (poly 0x07, seed 0x00, no reflection, no final XOR) is retained unchanged on every framed payload — including the newly-framed command channel (FRAME-05), which previously had no checksum; the existing byte-level CRC contract in `rurp_serial_utils.cpp` and `frame_parser.py` is preserved (D-05 — framing layers on top, no polynomial swap).

### 3. Dual-Repo Lockstep (LOCK)

- [ ] **LOCK-01**: The firmware (`rurp_serial_utils.cpp`) and host (`serial_comm.py` + `frame_parser.py`) framing implementations are byte-compatible — a round-trip test proves host-encode → firmware-decode and firmware-encode → host-decode for representative payloads (data blocks **and** JSON command frames), including payloads that contain the delimiter byte and the pathological all-delimiter case.
- [ ] **LOCK-02**: The `test_messages` Unity suite and host-side parser tests are updated to pin the new frame contract; firmware/host constant parity is preserved and CI stays green across both repos.

### 4. Bus-Aliasing Safety (SAFE)

- [x] **SAFE-01**: The SERIAL_ON_IO `0x00` bus-aliasing risk (COBS-DECISION Open Q2) is resolved and documented — either a code/bench proof that the host cannot deliver a `0x00` frame-boundary byte during the programmer↔communication mode transition window (COBS path), or adoption of SLIP's `0xC0` delimiter, which sidesteps the concern entirely (Q3). Note: framing the command channel (FRAME-05) means the host now actively emits delimiter bytes on the host→fw direction, so this host-side timing guarantee is load-bearing, not theoretical. **SATISFIED: static proof conclusive (Phase 49 Plan 01 — `.planning/v1.10-FRAMING-DECISION.md`)**

### 5. Byte-Exact Verification (XACT)

- [ ] **XACT-01**: Transport proven byte-exact on a clean board — N consecutive framed read **and** write transfers are byte-identical on Uno (512 B) and Leonardo (1024 B); the hardened path reproduces the GATE-1.8d W27C512 N=5 baselines.
- [ ] **XACT-02**: Resync proven under fault injection — a deliberately corrupted byte (or length field) recovers within one packet via the delimiter, not a 2-second timeout cascade, demonstrated by a host-side or bench fault-injection harness.
- [ ] **XACT-03**: uno328pb re-test recorded — the consistency-check read is re-run on the uno328pb (where the timeout + ~99% 0xff-drift instability appears) and the result documents whether the hardened transport changes the failure shape, stating explicitly what it does and does not conclude per COBS-DECISION §2.0 (transport-exoneration, not a hardware fix).

## Out of Scope (v1.10)

- **Re-framing the fw→host log/telemetry channel** (#4: `[0xAA55AA55][len_u16][id][params][crc8][0x0A]`) — it already self-delimits via the magic preamble + CRC8 + `0x0A` terminator and is gated behind `com_mode`, so it is outside the data-corruption blast zone. (The host→fw JSON command channel #1, by contrast, IS now in scope per FRAME-05.)
- **Adopting any off-the-shelf framing library** — PacketSerial, nanocobs, cobs-c/cobs-python, SerialTransfer, MIN are all rejected/eliminated in COBS-DECISION §4 (Uno-RAM, CRC-poly, or Python-version filters). v1.10 builds the custom layer only.
- **CRC polynomial change / CRC32** — D-05 keeps CRC8-CCITT; candidates requiring a poly swap are eliminated.
- **Fixing the read-bug itself** — v1.10 only rules transport out as a confounder; Bug A was localized by Phase 44 to the parallel read path (downstream of serial). The actual per-shield RCA/fix is v1.9 (Phases 45–47).
- **Stable `3.0.1` release** — deferred until a real read-bug fix lands and is bench-verified (D-17v2 carry-forward). v1.10 may cut a new beta; stable promotion is a separate operator gate.

## Future Requirements (deferred)

- Re-framing the fw→host log/telemetry channel (#4), if a corruption case there is ever observed (it already self-delimits today).
- Resync telemetry/metrics (counting recovered desyncs) if field instrumentation becomes useful for the v1.9 RCA.
- Applying the framing layer to any future higher-throughput transport (e.g. a faster baud or a binary command channel).

## Traceability

| REQ-ID | Phase | Status |
|--------|-------|--------|
| FRAME-01 | Phase 50 | Pending |
| FRAME-02 | Phase 50 | Pending |
| FRAME-03 | Phase 50 | Pending |
| FRAME-04 | Phase 50 | Pending |
| FRAME-05 | Phase 51 | Pending |
| CRC-01 | Phase 50 | Pending |
| LOCK-01 | Phase 52 | Pending |
| LOCK-02 | Phase 52 | Pending |
| SAFE-01 | Phase 49 | ✅ Complete (2026-06-01) |
| XACT-01 | Phase 53 | Pending |
| XACT-02 | Phase 53 | Pending |
| XACT-03 | Phase 53 | Pending |

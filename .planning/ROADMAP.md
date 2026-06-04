# Roadmap: Firestarter — Protocol-Aware Programming Architecture

## Milestones

- ✅ **v1.0 Protocol-Aware Programming Architecture** — Phases 1-13 (shipped 2026-05-11)
- ⏸ **v1.1 Safety Closure & Hardware Validation** — Phases 1-3 done, Phase 4 hardware-validation parked (FM1608 byte-0 bug); Phase 5 milestone-close deferred. Original artifacts preserved at `.planning/milestones/v1.1-paused/`.
- ✅ **v1.2 Message-ID Logging Rework** — Phases 6-10 (shipped 2026-05-19); Phase 10 closed by `/gsd-complete-milestone` (DOC-02)
- ⏸ **v1.3 CMOS EPROM Family Hardware Validation** — Phases 11-14 (PAUSED 2026-05-20, hardware-gated). Phase 11 shipped + Phase 12 Wave 0 scaffold committed; Plans 12-01/02/03 + Phases 13/14 await operator bench hardware.
- ✅ **v1.4 Beta & Pre-release Deployment Pipeline** — Phases 15-20 (shipped 2026-05-20; ship tag `3.0.0b3` in both sub-repos; hardware-flash validated on Uno + Leonardo). Parallel beta channel for both sub-repos without disrupting the stable main → release pipeline.
- ✅ **v1.5 Arduino Uno (ATmega328PB) Board Support** — Phases 21-25 (shipped 2026-05-21; ship tag `3.0.0b4`; bench-validated on operator's 328PB-Uno via `urclock` bootloader). `uno328pb` as a third first-class firmware target alongside `uno` + `leonardo`. Full detail in `.planning/milestones/v1.5-ROADMAP.md`; bench evidence in `.planning/v1.5-BENCH-RESULTS.md`.
- ⏸ **v1.6 Fix the Read Bug** — Phases 26-30 (SHIPPED 2026-05-26 as "diagnostic + revert" per D-17v2). Read-bug carries to v1.9 as Bug A + Bug B RCA seed.
- ✅ **v1.7 RURP Shield Hardware Investigation & Version Detection** — Phases 31-35 (SHIPPED 2026-05-26). Per-rev capability table + labeled schematics + shield-version-detect firmware plumbing.
- ✅ **v1.8 Host CLI Structural Cleanup (firestarter_app)** — Phases 36-43 (SHIPPED 2026-05-29; ship tag `3.0.0b7` beta-only). 27 requirements DELIVERED + 3 VERIFIED-at-close; argparse→Click, mypy strict on 8 modules, 70% coverage floor. Full detail in `.planning/MILESTONES.md` §v1.8.
- 🚧 **v1.10 Serial Transport Hardening (COBS)** — Phases 49-53 (STARTED 2026-06-01). Hardware-gated; coordinated dual-repo firmware + host lockstep. Inserted ahead of the paused v1.9 RCA: a custom delimiter-based framing + automatic-resync layer (streaming COBS `0x00` vs SLIP `0xC0` — mechanism chosen in plan research) on the data-block path AND the host→fw JSON command channel, making the transport provably byte-exact so serial corruption is ruled out as a read-bug confounder. CRC8-CCITT poly 0x07 retained (D-05); Uno-fit streaming-encode-only constraint (D-04). Stacked off the v1.9 branch tip.
- ⏸ **v1.9 Read-Bug RCA + Fix** — Phases 44-48 (PAUSED 2026-06-01 at Phase 44 — v1.10 inserted ahead; resumes at Phase 45). Hardware-gated; firmware sub-repo work expected. Root-cause and fix Bug A (Modified Rev 0 upper-address jitter) + Bug B (Rev 2.0 /CE-/OE timing + VPP mismatch); N≥5 byte-identical acceptance gate across shield fleet.

## v1.10 — Serial Transport Hardening (COBS) (STARTED 2026-06-01)

**Milestone goal:** Implement a custom delimiter-based serial framing + automatic-resync layer on the Arduino↔host data path — covering **both** the binary data-block path and the host→firmware JSON command channel — so the transport is **provably byte-exact** end to end: delivering exactly the bytes the firmware read off the parallel bus, and exactly the commands the host issued, with any line corruption bounded to a single frame. This rules serial corruption out as a confounding variable before the paused per-shield read-bug RCA resumes (v1.9 Phase 45+). Per `.planning/v1.9-COBS-DECISION.md` §2: ADOPT a custom framing layer; REJECT all off-the-shelf libraries (§4); KEEP CRC8-CCITT poly 0x07 (D-05); honor the Uno-fit filter (D-04 — streaming encode only, no second ~512 B buffer, ~545 B free-RAM ceiling).

**Interleaved milestone:** v1.10 was inserted *ahead* of the paused v1.9 RCA (operator pivot 2026-06-01). Phase numbering continues at **Phase 49** — Phases 45–48 are RESERVED for the deferred v1.9 phases and are not reused here. Branch model: `v1.10-serial-transport-hardening` stacked off the `v1.9-read-bug-rca` tip in all 3 repos (NOT off `main`/`beta`, which are stale at the v1.8 close and lack both the COBS ADOPT decision and Phase 44's read-timing knobs that v1.10 depends on).

**Hardware-gated:** byte-exact transport verification (Uno 512 B / Leonardo 1024 B / uno328pb) is operator-authorized bench work. Per `feedback_chip_out_before_sideload`: the chip leaves the socket before any firmware sideload. Per `feedback_verify_port_identity_each_task`: controller identity is verified per port at each bench task. Per `user_shield_revisions`: the operator is asked which silkscreen rev is on the bench.

**Lockstep mandate:** root `CLAUDE.md` requires `rurp_serial_utils.cpp` ↔ `serial_comm.py`/`frame_parser.py` to change together; the `test_messages` Unity contract pins the byte-level frame shape. This is a coordinated dual-repo (firmware + host) milestone, like the v1.2 Message-ID rework.

**Granularity:** Comprehensive (decision → data-path framing → command-channel migration → lockstep contract → hardware verification — five distinct delivery boundaries; the breaking command-channel change and the operator-gated bench verification each warrant their own phase).

### Phases

- [x] **Phase 49: Framing Mechanism Decision (COBS `0x00` vs SLIP `0xC0`)** — Resolve the deferred mechanism choice and the `0x00` bus-aliasing safety question (COBS-DECISION §2.0 / Open Q2/Q3) before any implementation commits to a delimiter. **COMPLETE 2026-06-01: COBS `0x00` selected; SAFE-01 proof conclusive; D-06 frame contract frozen at `.planning/v1.10-FRAMING-DECISION.md`.**
- [x] **Phase 50: Data-Path Framing Layer + Automatic Resync (dual-repo lockstep)** — Implement the chosen streaming framing on the host↔fw data-block path with CRC8 retained; receiver auto-resyncs to the next delimiter, killing the 2 s `len_u16`-corruption timeout cascade; fits the Uno free-RAM ceiling. (completed 2026-06-01)
- [x] **Phase 51: Command-Channel Framing Migration (breaking wire change)** — Migrate the host→fw JSON command channel into the same framing (CRC8-verified before the JSON parser sees the payload); firmware + host upgrade lockstep, no mixed-version interop. **COMPLETE 2026-06-02: all 4 plans shipped (COBS decode+CRC8, host framing, breaking-change docs, CR-01/CR-02 gap closure); 36/36 native tests green.**
- [x] **Phase 52: Lockstep Contract + Round-Trip Tests** — Prove host-encode↔firmware-decode byte-compatibility (data blocks AND command frames, incl. delimiter-laden + all-delimiter payloads); pin the new frame contract in the `test_messages` Unity suite + host parser tests; CI green across both repos. (completed 2026-06-02)
- [ ] **Phase 53: Byte-Exact Bench Verification (hardware-gated)** — Operator-authorized bench proof: N consecutive framed read+write transfers byte-identical on Uno + Leonardo (reproducing the GATE-1.8d W27C512 N=5 baselines); fault-injection resync proven within one packet; uno328pb re-test recorded (transport-exoneration, not a hardware fix).
- [ ] **Phase 54: Even-Block Data Transfers (full-buffer-aligned host→fw chunks)** — Make host→fw write/verify data blocks a full even buffer (512/1024) like the fw→host read path already is, instead of buffer−2 (510/1022), so a chip-sized transfer divides into whole blocks with no odd-sized final remainder chunk — saving one write round. Decouple the on-wire data-block size from the COBS decode-buffer cap (decode buffer holds a full block + CRC8 + NUL) while keeping the Phase 52 lockstep contract green.

### Phase Details

#### Phase 49: Framing Mechanism Decision (COBS `0x00` vs SLIP `0xC0`)

**Goal**: The framing mechanism is chosen with a binding, evidence-backed decision — streaming COBS (`0x00` delimiter) vs SLIP/RFC-1055 (`0xC0` delimiter) — and the SERIAL_ON_IO `0x00` bus-aliasing risk (COBS-DECISION Open Q2) is resolved before any implementation phase commits to a delimiter byte. The decision is load-bearing because framing the command channel (Phase 51) means the host now actively emits delimiter bytes on the host→fw direction.
**Depends on**: Nothing (first v1.10 phase). Inputs: `.planning/v1.9-COBS-DECISION.md` §2.0/§4.2/§4.3/§5, the verified `com_mode` gate analysis in `uno_rurp_shield.cpp`, and the current four-framing serial-path map (§1.1).
**Requirements**: SAFE-01
**Success Criteria** (what must be TRUE):

  1. A written decision record names the chosen mechanism (COBS `0x00` or SLIP `0xC0`) with rationale referencing the Uno-fit constraint (D-04), the CRC8 coexistence requirement (D-05), and the bus-aliasing analysis — not merely "we picked one".
  2. The SERIAL_ON_IO `0x00` bus-aliasing risk is resolved and documented: EITHER a code/bench proof that the host cannot deliver a `0x00` frame-boundary byte during the programmer↔communication mode transition window (COBS path), OR an explicit adoption of SLIP's `0xC0` delimiter that sidesteps the concern (Q3) — the chosen resolution is the one the implementation phases build on.
  3. The decision explicitly confirms the mechanism is streaming-encodable with no second ~512 B encode buffer (fits the ~545 B Uno free-RAM ceiling) and layers on top of the unchanged CRC8-CCITT poly 0x07 integrity byte.
  4. The decision identifies what changes in each repo file (`rurp_serial_utils.cpp`, `serial_comm.py`, `frame_parser.py`, `test_messages`) so Phases 50–52 inherit a concrete contract, not an open question.

**Plans**: 1 plan
Plans:

- [x] 49-01-PLAN.md — Wave 1: SAFE-01 static proof → scored neutral COBS-vs-SLIP matrix → ADR + frozen frame contract at `.planning/v1.10-FRAMING-DECISION.md` (handles both decision branches; CRC8-before-parse V5 mandate recorded; supersedes v1.9-COBS-DECISION.md DEFER line) ✅ 2026-06-01

#### Phase 50: Data-Path Framing Layer + Automatic Resync (dual-repo lockstep)

**Goal**: The host↔firmware data-block path uses the Phase-49 framing layer end to end — full board-buffer payloads (512 B Uno / 1024 B Leonardo) frame transparently to the eprom read/write loop, the firmware encoder/decoder streams with no second encode buffer (proven by a post-change Uno RAM report), CRC8 is retained on every framed payload, and the receiver automatically resyncs to the next delimiter after any framing or integrity error — eliminating the 2 s `len_u16`-corruption timeout-desync cascade.
**Depends on**: Phase 49 (mechanism + delimiter + bus-aliasing resolution chosen). Coordinated dual-repo work: `rurp_serial_utils.cpp` (firmware) + `serial_comm.py`/`frame_parser.py` (host) change in lockstep.
**Requirements**: FRAME-01, FRAME-02, FRAME-03, FRAME-04, CRC-01
**Success Criteria** (what must be TRUE):

  1. The bare `[len_u16][xor][payload]` data-block frame boundary is replaced by the chosen delimiter-based framing on both directions of the data-block path; a corrupted byte no longer causes a wrong-length read that cascades to the 2 s timeout.
  2. After a deliberately injected framing or integrity error in a unit/host-level test, the receiver discards bytes up to the next delimiter and recovers within a single packet — the desync is bounded to one frame, not the rest of the transfer.
  3. A post-change `pio run -e uno` RAM report shows the encoder/decoder is streaming — no second ~512 B encode buffer is materialized and the build stays under the ~545 B free-RAM ceiling (D-04); 512 B (Uno) and 1024 B (Leonardo) full-buffer payloads frame without operator-visible re-chunking.
  4. CRC8-CCITT (poly 0x07, seed 0x00, no reflection, no final XOR) is computed and verified on every framed data-block payload, byte-compatible with the existing `rurp_serial_utils.cpp` table and `frame_parser.py` `_build_crc8_table` — no polynomial swap (D-05).

**Plans**: 4 plans
Plans:
**Wave 1**

- [x] 50-01-PLAN.md — Wave 0 failing-test scaffold (both repos): host `test_cobs.py` + firmware COBS decode/resync Unity suite + `Serial.read`/`available` mock + scripted Uno RAM gate (D-02; D-05/D-06)

**Wave 2** *(parallel — firmware vs host, zero file overlap; both depend on 50-01)*

- [x] 50-02-PLAN.md — firmware: rewrite `rurp_communication_read_data` (COBS decode-in-place + CRC8 + drain-to-`0x00`, removes 2 s loop) + `rurp_communication_write` COBS encode mirror; `case '#'` surface preserved (D-01/D-04/D-05/D-06)
- [x] 50-03-PLAN.md — host: add `cobs_encode`/`cobs_decode` to `frame_parser.py` (CRC8 reused) + COBS frame contents in `_main_phase_send_data` (atomic write); read RX path untouched (D-05/D-06)

**Wave 3** *(integration gate — depends on 50-02 + 50-03)*

- [x] 50-04-PLAN.md — post-change Uno RAM proof (FRAME-03) + dual-repo full-suite green gate + Leonardo `DATA_BUFFER_SIZE` A/B-pin operator decision (D-03)

#### Phase 51: Command-Channel Framing Migration (breaking wire change)

**Goal**: The host→firmware JSON command channel is migrated into the same framing layer — the firmware decodes a frame, verifies its CRC8, then hands the payload to the JSON parser; the legacy "`{`-peek and discard non-`{` bytes" path is replaced (or retained only as an explicit fallback). This is a breaking wire-protocol change: firmware and host upgrade lockstep with no mixed-version interop, exactly like the v1.2 Message-ID rework.
**Depends on**: Phase 50 (the framing layer + CRC8-on-payload contract exists on the data path and is reused for the command channel). Coordinated dual-repo lockstep.
**Requirements**: FRAME-05
**Success Criteria** (what must be TRUE):

  1. The host→fw JSON command channel emits framed commands using the Phase-49/50 framing; the firmware decodes a frame and verifies its CRC8 BEFORE the JSON parser sees the payload — the command channel, which previously had no checksum, now gains end-to-end integrity (closing the CRC-01 command-channel obligation).
  2. The legacy `{`-peek / discard-non-`{` command-ingest path is replaced (or demoted to an explicit, documented fallback) — the firmware no longer relies on byte-peeking to find command boundaries on the framed path.
  3. The change is enforced as a breaking lockstep upgrade: a version/handshake guard (or equivalent) prevents a framed host from silently mis-driving unframed firmware and vice-versa; the breaking nature is documented for the beta cut.
  4. A representative set of host commands (read/write/info/etc.) round-trips through the framed command channel and is parsed identically to the pre-migration JSON behavior — no command-surface regression.

**Plans**: 4 plans (3 + 1 gap-closure)
Plans:
**Wave 1** *(parallel — firmware vs host, zero file overlap)*

- [x] 51-01-PLAN.md — firmware: new `test_cobs_cmd_frame` Unity suite (Wave-0 scaffold) + `CMD_FRAME_MAX` + delete `{`-peek `CMD_IDLE` loop → `rurp_communication_read_data()` COBS-decode + CRC8-before-parse + drain-to-`0x00`; `init_programmer_framed` surgery (FRAME-05/CRC-01; D-05/D-06; V5 §4.4)
- [x] 51-02-PLAN.md — host: framed `send_json_command()` (COBS+CRC8, single atomic `send_bytes()`) + `CMD_FRAME_MAX` parity in constants.py + framed/atomic/version-probe tests; probe framed automatically (FRAME-05/CRC-01; D-04; SAFE-01 sub-claim B)

**Wave 2** *(merge gate — depends on 51-01 + 51-02)*

- [x] 51-03-PLAN.md — breaking-change README notes in both sub-repos (D-02 documentation-as-SC3-guard) + dual-repo full-suite green gate + firmware/host `CMD_FRAME_MAX` parity check (FRAME-05 SC3)

**Wave 1 (gap closure — firmware BLOCKER defects from 51-VERIFICATION.md)**

- [x] 51-04-PLAN.md — firmware gap closure: close CR-01 (off-by-one OOB NUL-write at the 512-byte boundary → cap decode at `DATA_BUFFER_SIZE-1`) + CR-02 (unbounded busy-wait hang on a truncated frame → bounded mid-frame inter-byte deadline on both `rurp_serial_utils.cpp` spin sites) + exact-boundary & truncated-frame Unity cases + finite-stream mock mode (FRAME-05/CRC-01; D-06 reconciled; SC1 win preserved) ✅ 2026-06-02

#### Phase 52: Lockstep Contract + Round-Trip Tests

**Goal**: The firmware and host framing implementations are proven byte-compatible and pinned by tests in both repos, so the dual-repo contract cannot silently drift — host-encode→firmware-decode and firmware-encode→host-decode both round-trip for representative payloads (data blocks AND JSON command frames), including the pathological delimiter-laden and all-delimiter cases, and CI stays green across both repos with firmware/host constant parity preserved.
**Depends on**: Phase 50 (data-path framing) + Phase 51 (command-channel framing) — both framed paths must exist to pin the full contract.
**Requirements**: LOCK-01, LOCK-02
**Success Criteria** (what must be TRUE):

  1. A round-trip test proves host-encode → firmware-decode AND firmware-encode → host-decode for representative payloads — data blocks and JSON command frames — including a payload that contains the delimiter byte and the pathological all-delimiter payload; encode/decode are byte-exact inverses.
  2. The `test_messages` Unity suite (firmware) and the host-side parser tests are updated to pin the new frame contract (delimiter, escaping/run-length, CRC8 placement) so any future drift fails a test rather than silently breaking the link.
  3. Firmware/host constant parity is preserved (the constants duplicated between `firestarter/include/firestarter.h` and `firestarter_app/firestarter/constants.py` stay in sync, guarded by the parity tests) and CI is green in both the `firestarter` and `firestarter_app` repos.
  4. The CRC8-CCITT byte-level contract (poly 0x07) is asserted byte-for-byte in the updated suites — confirming framing layered on top without a polynomial change (D-05).

**Plans**: 4 plans
Plans:
**Wave 1**

- [x] 52-01-PLAN.md — author canonical `frame-vectors.toml` (D-05 corpus incl. 253/254/255-run boundary) + `codegen_vectors.py` (v1.2 determinism contract + `--check`), vendor byte-identical into both repos, generate `frame_vectors.h` / `frame_vectors.py`, add per-repo codegen drift-gate CI steps (D-01/D-04/D-08)

**Wave 2** *(parallel — firmware vs host, zero file overlap; both depend on 52-01)*

- [x] 52-02-PLAN.md — firmware: new `test_frame_vectors/` Unity suite (both-legs vector assertions, decode leg capped at 511 B per CR-01, CRC8 KAT `CRC8([0x01])==0x07`) + platformio.ini allowlist registration (D-02/D-06)
- [x] 52-03-PLAN.md — host: new `test_frame_vectors.py` (both-legs assertions + CRC8 KAT) + extend `test_revision_constants_parity.py` with `CMD_FRAME_MAX==512` parity (D-02/D-06/D-07)

**Wave 3** *(merge gate — depends on 52-01 + 52-02 + 52-03)*

- [x] 52-04-PLAN.md — cross-repo byte-identity assert (`diff` empty for catalog + codegen, D-09) + both codegen drift gates clean + dual-repo full-suite green (LOCK-01 + LOCK-02 close)

#### Phase 53: Byte-Exact Bench Verification (hardware-gated)

**Goal**: The hardened transport is proven byte-exact on real hardware and its resync behavior is demonstrated under fault injection — closing the milestone's central claim that serial corruption is ruled out as a read-bug confounder. The uno328pb (where the timeout + ~99% 0xff-drift instability bites hardest) is re-tested with the result documenting explicitly what the hardened transport does and does not conclude (transport-exoneration per COBS-DECISION §2.0, NOT a hardware fix).
**Depends on**: Phase 50 + Phase 51 (both framed paths implemented) + Phase 52 (lockstep contract proven green) — bench verification runs against the merged hardened firmware + host. Bench hardware: Uno (512 B) + Leonardo (1024 B) + uno328pb + RURP shield + operator authorization. Operator is asked which silkscreen rev is on the bench; controller identity verified per port; chip out of socket before any sideload.
**Requirements**: XACT-01, XACT-02, XACT-03
**Success Criteria** (what must be TRUE):

  1. Transport proven byte-exact on a clean board: N consecutive framed read AND write transfers return byte-identical results on Uno (512 B) and Leonardo (1024 B) — operator-witnessed — and the hardened read path reproduces the GATE-1.8d W27C512 N=5 baselines (`.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`).
  2. Resync proven under fault injection: a deliberately corrupted byte (or length field) recovers within one packet via the delimiter — demonstrated by a host-side or bench fault-injection harness — NOT a 2-second timeout cascade.
  3. uno328pb re-test recorded: the `firestarter dev consistency-check` read is re-run on the uno328pb and the result documents whether the hardened transport changes the failure shape (timeout / ~99% 0xff-drift), stating explicitly that this is transport-exoneration and NOT a per-shield hardware fix (the actual RCA is deferred v1.9 Phase 45+).
  4. The bench evidence is captured in a milestone artifact (hashes, fault-injection log, uno328pb before/after shape) sufficient for the resumed v1.9 RCA to treat the transport as a settled, byte-exact variable.

**Plans**: 6 plans
Plans:
**Wave 1**

- [x] 53-01-PLAN.md — Wave 0 failing-test scaffold: RED tests for write_cycle_eprom 3-way verdict, outgoing fault-inject hook + FaultInjectingSerialCommunicator, dev write-cycle/dev fault-inject smoke tests, plus a GREEN _read_and_parse_lines ring-fence compliance assertion (XACT-01/02)

**Wave 2** *(depends on 53-01)*

- [x] 53-02-PLAN.md — software harness: write_cycle_eprom() (erase->write->read-back->host SHA compare, D-06), getattr-guarded outgoing fault hook in send_json_command(), FaultInjectingSerialCommunicator + fault_inject_cycle(), dev write-cycle/dev fault-inject subcommands (3-way verdict); transport production path byte-identical; ring-fence intact (XACT-01/02)

**Wave 3** *(parallel — operator-witnessed bench, distinct artifact subdirs; all depend on 53-02)*

- [ ] 53-03-PLAN.md — clean-board bench (autonomous: false): N=5 byte-identical reads + N=5 write->read-back cycles on clean Uno (512 B) + Leonardo (1024 B), Rev 2.0 target (D-07), GATE-1.8d hash-match strong-form-or-self-consistency (D-04/D-05/D-06) (XACT-01)
- [ ] 53-04-PLAN.md — fault-injection bench (autonomous: false): host->fw + fw->host, both fault forms (corrupt-crc8, drop-delimiter); sub-second clean error (no 2 s cascade) + byte-exact next transfer (D-01/D-02/D-03) (XACT-02)
- [ ] 53-05-PLAN.md — uno328pb re-test (autonomous: false): N=5 with timeout-retry logging (D-08), hardened-firmware-only (D-09), structured transport-exoneration verdict per v1.9-COBS-DECISION §2.0 (D-10) (XACT-03)

**Wave 4** *(milestone artifact — depends on 53-03 + 53-04 + 53-05)*

- [ ] 53-06-PLAN.md — milestone evidence artifact (autonomous: false): assemble .planning/v1.10/bench-verification/SUMMARY.md (operator attestation, full SHA table, fault-injection log, uno328pb before/after + exoneration verdict, settled-variable claim) (D-11; SC4)

#### Phase 54: Even-Block Data Transfers (full-buffer-aligned host→fw chunks)

**Goal**: Host→fw data blocks (write/verify) transfer in full, even, buffer-sized blocks — 512 on Uno/uno328pb, 1024 on Leonardo — exactly like the fw→host read path already does, so a chip-sized transfer divides into whole blocks with NO odd-sized final remainder chunk. Today the host→fw chunk is `buffer − 2` (510 / 1022): the firmware COBS decoder commits at most `DATA_BUFFER_SIZE − 1` (CR-01 NUL-slot reservation) and the payload also carries a trailing CRC8 byte, so usable data = buffer − 2. On a 65536-byte chip that 510-byte chunk leaves a 256-byte partial last write (128×510 + 256) — one extra round trip. Make the on-wire DATA payload equal the full buffer in BOTH directions by decoupling the data-block size from the decode-buffer cap (e.g. size the firmware decode buffer to hold a full block + CRC8 + NUL, or carry the CRC/length out-of-band), so the even-block transfer saves a write round and the two directions are symmetric.

**Depends on**: Phase 50 (data-path framing), Phase 51 (the CR-01 decode cap this loosens), Phase 52 (lockstep contract — must stay green at the new block size), Phase 53 (bench-verified transport baseline + the per-board buffer negotiation: firmware advertises `DATA_BUFFER_SIZE`, host sizes chunks). This phase changes the chunk-size-vs-decode-cap relationship on that substrate.

**Requirements**: EVEN-01

**Success Criteria** (what must be TRUE):

  1. Host→fw write/verify data blocks are full buffer-sized (512 / 1024) — no `buffer − 2` reduction — verified on the wire (frame sizes) on Uno + Leonardo.
  2. A full-chip (65536 B) write/verify divides into whole blocks with no odd-sized final remainder chunk — one fewer round trip than the 510/1022 chunking.
  3. The firmware COBS decoder accepts a full-buffer data block + CRC8 without overflow (no `Data error: -2`); RAM-fit confirmed on the Uno (2 KB) and uno328pb.
  4. The Phase 52 lockstep contract + round-trip tests stay green (host-encode ↔ firmware-decode byte-compatible at the new block size); a regression test pins the full-buffer block round-trip.

**Plans**: 3 plans
Plans:
**Wave 1** *(parallel — firmware vs host, zero file overlap)*

- [x] 54-01-PLAN.md — firmware: parameterize `rurp_communication_read_data(char*, size_t cap)` (MAIN cap=DATA_BUFFER_SIZE, CMD_IDLE cap=DATA_BUFFER_SIZE−1 per CR-01) + 4th `:<maxchunk>` identity field + update all 4 native Unity suites + new MAIN-path/CMD_IDLE-overflow/no-remainder tests (EVEN-01; D-01 Candidate A/D-04)
- [x] 54-02-PLAN.md — host: parse `fw_fields[3]`→`firmware_max_chunk` (isdigit/V5) + rewrite `_calculate_buffer_size()` to return it (no −2, raise `FirmwareOutdatedError` if absent per D-05) + new `test_even_block.py` + fix the 2 breaking `test_frame_vectors.py` classes (EVEN-01; D-03/D-04/D-05/D-06/D-07)

**Wave 2** *(integration gate — depends on 54-01 + 54-02)*

- [x] 54-03-PLAN.md — Uno + uno328pb RAM gate under ~545 B free-RAM ceiling (D-08 hard close) + dual-repo full-suite green + frame-vectors drift gate clean (EVEN-01 SC3/SC4)

### v1.10 Coverage

| REQ-ID | Phase |
|--------|-------|
| SAFE-01 | Phase 49 |
| FRAME-01 | Phase 50 |
| FRAME-02 | Phase 50 |
| FRAME-03 | Phase 50 |
| FRAME-04 | Phase 50 |
| CRC-01 | Phase 50 |
| FRAME-05 | Phase 51 |
| LOCK-01 | Phase 52 |
| LOCK-02 | Phase 52 |
| XACT-01 | Phase 53 |
| XACT-02 | Phase 53 |
| XACT-03 | Phase 53 |
| EVEN-01 | Phase 54 |

**Mapped: 13/13 requirements ✓** — no orphans, no duplicates.

## v1.9 — Read-Bug RCA + Fix (STARTED 2026-05-29)

**Milestone goal:** Root-cause and fix the EPROM read-bug deferred since v1.6, restoring N≥5 byte-identical reads across the shield fleet (Modified Rev 0, Rev 2.0, Rev 2.2). Inherits the v1.6 `dev consistency-check` diagnostic, the 15-binary N=5 W27C512 bench substrate at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`, the Phase 29 v2 Bug A/Bug B characterization in `.planning/v1.6-EVIDENCE.md`, the v1.7 schematics + shield-version-detect plumbing, and the v1.8 cleaned-up host read path (GATE-1.8d ring-fence intact — baselines still valid).

**Hardware-gated:** All bench operations are operator-authorized (shield swaps, scope traces, A/B fix trials). Per `feedback_chip_out_before_sideload`: chip leaves socket before any firmware sideload. Per `feedback_verify_port_identity_each_task`: controller identity verified per port at each bench task. Per `user_shield_revisions`: operator asked which silkscreen rev is on bench (EEPROM hw_revision byte cannot distinguish revs).

**Phase numbering:** Continues from v1.8 last phase 43 → v1.9 starts at **Phase 44**.

### Phases

- [x] **Phase 44: Bug A RCA — Modified Rev 0 Upper-Address Jitter** *(complete 2026-06-01; re-grounded)* — RCA achieved: Bug A is a **Rev 0-shield read-path fault** (broad read jitter, causally controlled by read-strobe timing — the governing D-07 causal bar), NOT the hypothesized A15 upper-address effect. Per-rev map started.
- [ ] **Phase 45: Bug B RCA — Rev 2.0 Timing & Voltage** — Instrument the Rev 2.0 /CE-or-/OE timing + VPP=13.1V failure to a definitive root cause; complete the per-rev failure-mode map.
- [ ] **Phase 46: Fix Design & A/B Bench Trials** — Design firmware fix candidates for Bug A and Bug B; A/B-test on the affected boards; regression-check across the shield fleet.
- [ ] **Phase 47: Acceptance Gate + Backlog Closures** — Re-run the Phase 29 acceptance gate (N≥5 byte-identical W27C512 reads across boards with fix applied); close VERIFY-01/03/04 backlog.
- [ ] **Phase 48: COBS Evaluation + Post-RCA Cleanup + Milestone Close** — Evaluate COBS framing on the serial data path (adopt/defer/reject decision); lift `eprom_operations.py` mypy strict overrides; close milestone with documentation and branch promotion.

## Phase Details

### Phase 44: Bug A RCA — Modified Rev 0 Upper-Address Jitter

> **★ RE-GROUNDED 2026-06-01 (RCA achieved).** The 2026-06-01 bench session
> **disproved the upper-address premise** and proved a stronger result: Bug A is a
> **Rev 0 (Modified Rev 0) shield read-path fault** — broad, ~uniform read jitter
> (not A15-specific), **causally controlled by the read-strobe knob** (longer
> strobe → ~6.5× worse; mechanism = charge-leakage / weak data-bus pulldown; fix
> direction = shorter strobe, handed to Phase 46). Isolated to the shield via a 2×2
> controller×shield crossover (chips + controllers exonerated). This **meets the
> governing D-07 causal-only success bar** (a knob that controls the jitter).
> Plans 04/05 as-written (Modified-Rev-0-on-Leonardo baseline + upper-address 2D/LA
> sweep) are **superseded**. Canonical RCA: `evidence/44-RCA-FINDINGS.md`.
> Adjacent findings (out of scope, logged): VPP hardware healthy (Uno R1 miscal
> fixed); **write/program stalls on both controllers** (`evidence/.../WRITE-STALL.md`
> — recommend a separate `/gsd-debug`).

**Goal**: The Modified Rev 0 A15=1 upper-address jitter is proven to a specific signal-integrity mechanism (ringing, crosstalk, settling-time violation, or other), with scope traces and/or circuit analysis as evidence — going beyond the Phase 29 v2 symptom characterization (1.86× skew, 63% bit-raise). *(Re-grounded: mechanism proven is a Rev 0-shield read-path fault, causally controlled by read-strobe timing — see re-grounding note above.)*
**Depends on**: Phase 29 v2 evidence substrate (`.planning/v1.6-EVIDENCE.md` H3 block), v1.7 shield-version-detect plumbing, v1.8 cleaned-up host read path. Bench hardware: Modified Rev 0 shield + scope + operator authorization.
**Requirements**: RCA-01, RCA-03 (partial — Modified Rev 0 failure mode confirmed)
**Success Criteria** (what must be TRUE):

  1. Operator-witnessed scope trace (or equivalent circuit measurement) identifies the specific electrical cause of A15=1 address line jitter on Modified Rev 0, not merely the symptom — e.g. "ringing on A15 due to missing series termination" or "settling time violation at current read-pulse width". *(Per CONTEXT D-07, the causal-only bar — a knob that controls the jitter — governs over this wording; mechanism-naming is a stretch goal.)*
  2. The root-cause mechanism is documented with supporting evidence (scope screenshot or measurement values) sufficient to inform a targeted fix strategy — not just "the signal is slow".
  3. `firestarter dev consistency-check` run on Modified Rev 0 reproduces the Phase 29 v2 pattern (jitter present, WORST ≥ 1% zeros) as a controlled baseline before any fix is applied, confirming bench continuity with v1.6 substrate.
  4. Per-rev failure-mode map is started: Modified Rev 0 → Bug A confirmed; Rev 2.2 entry recorded (confirm whether Rev 2.2 shows Bug A or is clean).

**Plans**: 5 plans
Plans:
**Wave 1**

- [x] 44-01-PLAN.md — Wave 1: fork v1.9-read-bug-rca off beta in both sub-repos + recover v1.7-SHIELD-REVS.md (git/working-tree prereq)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 44-02-PLAN.md — Wave 2: firmware read-timing knobs (read_settling_us / read_strobe_us) + bounds cap + Wave 0 native Unity tests
- [x] 44-03-PLAN.md — Wave 2: host knob params + CLI options + Wave 0 pytest + 2D sweep harness

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 44-04-PLAN.md — Wave 3 (bench): *superseded* — static check done (readings uncaptured); baseline misattributed to a Rev 2.0 board & relocated. Goal served by the isolation experiment (Bug A reproduced + isolated to Rev 0 shield). See 44-04-SUMMARY.md.

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 44-05-PLAN.md — Wave 4 (bench): *goal achieved, method changed* — knob check proved causal coupling (D-06; longer strobe → 6.5× worse), 2×2 crossover isolated the fault to the Rev 0 shield, RCA findings written, per-rev map started (RCA-03 partial). Full 2D grid + LA capture deferred (not needed for the mechanism). See 44-05-SUMMARY.md.

### Phase 45: Bug B RCA — Rev 2.0 Timing & Voltage

**Goal**: The Rev 2.0 read-failure mechanism (/CE-or-/OE timing mismatch + voltage-divider mismatch + VPP=13.1V interaction) is proven to a definitive root cause, with bench evidence identifying which factor(s) are causal vs incidental.
**Depends on**: Phase 44 (per-rev map started; bench protocol established). Bench hardware: Rev 2.0 shield + scope + operator authorization.
**Requirements**: RCA-02, RCA-03 (completion — Rev 2.0 failure mode confirmed; full per-rev map finalized)
**Success Criteria** (what must be TRUE):

  1. Operator-witnessed bench measurement on Rev 2.0 isolates the dominant failure factor: timing margin (/CE or /OE pulse width relative to chip t_ACC), voltage-divider mismatch (VPP at chip pin vs. expected), or VPP=13.1V overstress — with evidence distinguishing causal from coincidental.
  2. The Rev 2.0 failure reproduces with `firestarter dev consistency-check` as a controlled baseline (jitter present, WORST ≥ 1% zeros, or the specific failure mode observed in Phase 29 v2).
  3. Per-rev failure-mode map is complete and documented: Modified Rev 0 → Bug A (upper-address jitter); Rev 2.0 → Bug B (timing/voltage); Rev 2.2 → confirmed clean or categorized; each entry cites the evidence from Phase 44 / Phase 45.
  4. RCA-02 root cause is documented with enough detail that a firmware-side or host-side fix candidate can be designed without further scope work (i.e., the mechanism is fully understood, not just observed).

**Plans**: TBD

### Phase 46: Fix Design & A/B Bench Trials

**Goal**: Firmware (and/or host-side) fix candidates for Bug A and Bug B are designed based on the Phase 44/45 root causes, A/B-tested on the affected boards, and verified not to regress the unaffected boards — leaving a committed fix in both sub-repos ready for acceptance gating.
**Depends on**: Phase 44 (Bug A root cause proven), Phase 45 (Bug B root cause proven). Bench hardware: all three shields (Modified Rev 0, Rev 2.0, Rev 2.2) + operator authorization. Firmware sub-repo `firestarter/` work expected.
**Requirements**: FIX-01, FIX-02, FIX-03
**Success Criteria** (what must be TRUE):

  1. A/B comparison on Modified Rev 0: `firestarter dev consistency-check` with fix applied shows WORST < 0.1% zeros (or byte-identical N=5 reads), vs. pre-fix baseline showing the Bug A pattern — operator-witnessed, result recorded.
  2. A/B comparison on Rev 2.0: `firestarter dev consistency-check` with fix applied shows WORST < 0.1% zeros (or byte-identical N=5 reads), vs. pre-fix baseline showing the Bug B pattern — operator-witnessed, result recorded.
  3. Rev 2.2 regression check: `firestarter dev consistency-check` on Rev 2.2 with the fix applied returns the same clean baseline as pre-fix (WORST stays ≤ 0.1% zeros or equivalent); no fix for one rev breaks reads on another.
  4. The fix is committed to the firmware sub-repo (and/or host sub-repo) with atomic commits citing the RCA findings from Phases 44/45; unit tests (Unity or pytest) covering the changed code path are committed alongside the fix.

**Plans**: TBD
**UI hint**: no

### Phase 47: Acceptance Gate + Backlog Closures

**Goal**: The headline Phase 29 acceptance gate is re-run with the fix applied and passes on all boards; the three v1.6 backlog closures (VERIFY-01/03/04) are completed, retiring the open items that have been carried since v1.6.
**Depends on**: Phase 46 (fix committed and A/B-tested on both bug families). Bench hardware: all three shields + uno328pb board + operator authorization.
**Requirements**: VERIFY-A, VERIFY-01, VERIFY-03, VERIFY-04
**Success Criteria** (what must be TRUE):

  1. N≥5 consecutive `firestarter read W27C512` invocations return byte-identical SHA-256 hashes on Modified Rev 0, Rev 2.0, AND Rev 2.2 shields — operator-witnessed, hashes recorded in bench artifact.
  2. uno328pb byte-identity confirmed (VERIFY-01): N≥5 `firestarter read` on the 328PB-Uno + RURP shield returns byte-identical results, closing the v1.6 carry-forward backlog item.
  3. 1KB low-rate jitter resolved (VERIFY-03): `firestarter dev read -s 1024` returns consistent results without the jitter pattern observed in v1.5/v1.6 bench sessions.
  4. Phase 24 BENCH-02 closure (VERIFY-04): the 328PB-Uno bench cycle item carried from v1.5 Phase 24 is formally closed with a recorded bench result or documented disposition.

**Plans**: TBD

### Phase 48: COBS Evaluation + Post-RCA Cleanup + Milestone Close

**Goal**: The COBS framing evaluation yields a documented adopt/defer/reject decision with rationale; the `eprom_operations.py` mypy strict overrides are lifted now that the read path is fixed and free to touch; the milestone is documented and branches promoted.
**Depends on**: Phase 46 (read path is fixed — TYPE-01 is gated on this). Phase 47 (acceptance gate passed — milestone close follows). COBS-01 is independent of the hardware RCA and can proceed in parallel or after Phase 46.
**Requirements**: COBS-01, TYPE-01
**Success Criteria** (what must be TRUE):

  1. A written COBS-01 decision document (or section in a planning artifact) records: PacketSerial re-assessed, custom COBS layer option evaluated, and a clear adopt/defer/reject verdict with rationale referencing the current serial data-path shape post-v1.8 cleanup — not just "we looked at it".
  2. `eprom_operations.py` mypy strict overrides are removed (or reduced to the minimum justifiable residual); `mypy` on `eprom_operations.py` exits without the deferred-per-D-07 suppressions; the change is covered by the existing test suite.
  3. MILESTONES.md gains a complete v1.9 entry covering the RCA findings, fix summary, acceptance gate result, and COBS decision.
  4. Sub-repo branches for v1.9 are promoted per the branching convention; a new beta pre-release tag is cut (at minimum); the stable `3.0.1` promotion checklist is either executed or explicitly deferred with rationale.

**Plans**: 3 plans
Plans:
**Wave 1** *(parallel — no file overlap)*

- [x] 48-01-PLAN.md — COBS-01: from-scratch lightweight-framing survey -> `.planning/v1.9-COBS-DECISION.md` (ADR, REJECT-libraries/DEFER-concept). UNGATED — decidable now.
- [ ] 48-02-PLAN.md — TYPE-01: lift `eprom_operations.py` mypy strict ring-fence (strict-island move + ~53 behavior-preserving fixes + watermark). HARD-GATED on Phase 46.

**Wave 2** *(milestone close — depends on 48-01 + 48-02; gated on Phases 46/47)*

- [ ] 48-03-PLAN.md — MILESTONES.md v1.9 entry + coordinated lockstep `3.0.0b8` beta tag (sub-repos->beta, meta->main; no stable 3.0.1). Operator-gated promotion checkpoint.

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1-13 (v1.0) | v1.0 | 22/22 | ✅ Shipped | 2026-05-11 |
| 1-3 (v1.1) | v1.1 | done | ✅ Complete | 2026-05-12..18 |
| 4 (v1.1) | v1.1 | partial | ⏸ Parked | — (FM1608 blocked) |
| 5 (v1.1) | v1.1 | 0/0 | ⏸ Deferred | — |
| 6-10 (v1.2) | v1.2 | 32/32 | ✅ Shipped | 2026-05-19 |
| 11 | v1.3 | 6/6 | ✅ Complete | 2026-05-19 |
| 12 | v1.3 | 1/4 | ⏸ Paused | — (hardware-gated) |
| 13 | v1.3 | 0/0 | ⏸ Paused | — (hardware-gated) |
| 14 (close) | v1.3 | 0/0 | ⏸ Paused | — (hardware-gated) |
| 15-20 (v1.4) | v1.4 | 10/10 | ✅ Shipped | 2026-05-20 |
| 21-25 (v1.5) | v1.5 | 6/6 | ✅ Shipped | 2026-05-21 |
| 26 | v1.6 | 2/2 | ✅ Complete | 2026-05-21 |
| 27 | v1.6 | 3/2 | ✅ Complete | 2026-05-26 |
| 28 | v1.6 | 4/4 | ✅ Complete | 2026-05-26 |
| 29 | v1.6 | 4/4 | ✅ Complete | 2026-05-26 |
| 30 (close) | v1.6 | 3/3 | ✅ Shipped | 2026-05-26 |
| 31-35 (v1.7) | v1.7 | — | ✅ Shipped | 2026-05-26 |
| 36-43 (v1.8) | v1.8 | 26/26 | ✅ Shipped | 2026-05-29 |
| 49 | v1.10 | 1/1 | Complete    | 2026-06-01 |
| 50 | v1.10 | 4/4 | Complete    | 2026-06-01 |
| 51 | v1.10 | 4/4 | Complete    | 2026-06-02 |
| 52 | v1.10 | 4/4 | Complete    | 2026-06-02 |
| 53 | v1.10 | 2/6 | In Progress|  |
| 44 | v1.9 | 3/5 | In Progress|  |
| 45 | v1.9 | 0/TBD | Not started | — |
| 46 | v1.9 | 0/TBD | Not started | — |
| 47 | v1.9 | 0/TBD | Not started | — |
| 48 (close) | v1.9 | 1/3 | In Progress|  |

## v1.8 — Host CLI Structural Cleanup (firestarter_app) (SHIPPED 2026-05-29)

<details>
<summary>✓ v1.8 shipped — Host CLI structural cleanup (firestarter_app); 8 phases, 27 requirements DELIVERED + 3 VERIFIED-AT-CLOSE; ship tag 3.0.0b7 beta-only. Full detail in `.planning/MILESTONES.md` §v1.8.</summary>

- **Ship tag:** `3.0.0b7` (beta-only; stable `3.0.1` deferred to v1.9 read-bug fix per D-17v2 carry-forward)
- **Phases:**
  - [x] Phase 36: Characterization Test Baseline (TEST-01..05)
  - [x] Phase 37: Tooling Baseline + CI Gate (TOOL-01..03)
  - [x] Phase 38: Low-risk Extractions (STRUCT-01..05)
  - [x] Phase 39: Database Cleanup + Chip Resolver (DATA-01..04)
  - [x] Phase 40: Serial Transport Restructure (SERIAL-01..03)
  - [x] Phase 41: CLI Migration argparse → Click (CLI-01..04; BUG-1 INTENTIONAL BEHAVIOR CHANGE)
  - [x] Phase 42: Error Handling Normalization + Quality Sweep (ERR-01..03; BUG-2 INTENTIONAL BEHAVIOR CHANGE; mypy strict on 8 modules; coverage 70.12%)
  - [x] Phase 43: Documentation + Milestone Close (DOC-01..02, MS-01)
- **Branch model:** sub-repo `v1.8-app-cleanup` off `beta@3.0.0b6` (firestarter_app only); meta-repo `v1.8-app-cleanup` off `main`; firmware sub-repo untouched at `beta@0bbe017` from v1.6 close.
- **v1.9 hand-off:** read-bug (Bug A + Bug B) carries forward with GATE-1.8d ring-fence intact; 15 N=5 W27C512 baseline binaries at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` remain valid because `_read_and_parse_lines` body is byte-identical pre/post v1.8; `eprom_operations.py` mypy strict + `ProtocolStateMachine` extraction also carry to v1.9.
- See full archive: `.planning/MILESTONES.md` §v1.8, `.planning/milestones/v1.8-REQUIREMENTS.md`, `.planning/milestones/v1.8-phases/`.

</details>

## v1.7 — RURP Shield Hardware Investigation & Version Detection (SHIPPED 2026-05-26)

<details>
<summary>✅ v1.7 shipped — per-rev capability table + labeled schematics + shield-version-detect firmware plumbing (5 phases). Full detail in `.planning/MILESTONES.md` §v1.7.</summary>

- **Phases:**
  - [x] Phase 31: Upstream Shield Archaeology (HW-INV-01, HW-INV-02, HW-INV-03, SILK-01)
  - [x] Phase 32: Inter-Rev Difference + Capability Matrix (DIFF-01, DIFF-02, CAPS-01, CAPS-02)
  - [x] Phase 33: Silkscreen Label → Code Alias Migration (ALIAS-01, ALIAS-02, ALIAS-03)
  - [x] Phase 34: Shield-Version-Detect Design + Firmware Plumbing (DETECT-HW-01, DETECT-HW-02, DETECT-FW-01, DETECT-FW-02)
  - [x] Phase 35: Documentation + Milestone Close (DOC-01, MS-01)
- **Canonical reference:** `.planning/v1.7-SHIELD-REVS.md` (9 sections: inventory, difference matrix, capability matrix, alias table, detect-hw schematic delta, per-rev ADC band table, labeled schematics, operator-board annotations, v1.8 hand-off).
- See full archive: `.planning/MILESTONES.md` §v1.7.

</details>

## v1.6 — Fix the Read Bug (SHIPPED 2026-05-26 — diagnostic + revert)

<details>
<summary>✅ v1.6 shipped — ships as "diagnostic + revert" per D-17v2 (5 phases, 13 plans). Read-bug carries to v1.9 with Bug A + Bug B pattern findings as RCA seed. Full detail in `.planning/MILESTONES.md` §v1.6.</summary>

- **Ship tag:** `3.0.0b6` (beta-only; both sub-repos lockstep)
- **Phases:**
  - [x] Phase 26: Cross-board Reproduction & Diagnostic Tooling (2 plans; REPRO-01..03)
  - [x] Phase 27: Root Cause Analysis (3 plans incl. re-open Plan 27-05; RCA-01..03)
  - [x] Phase 28: Fix Implementation + Unit Test Coverage (4 plans incl. revert Plan 28-03 + parked Plan 28-04; FIX-01..03 as diagnostic + revert)
  - [x] Phase 29: Multi-Board Bench Verification (4 plans incl. v2 re-iteration Plans 29-03/04; VERIFY-02 PASS via structured_data shape; VERIFY-01/03/04 DEFERRED to v1.9)
  - [x] Phase 30: Documentation + Milestone Close (3 plans; DOC-01/02 + MS-01)
- **Re-scope (D-17v2):** Phase 29 v1 Wave B FAIL → Plan 27-05 re-open confirmed dual-cause (Outcome A Leonardo firmware-induced + Outcome B-independent uno328pb hardware) → Plan 28-03 reverted `437339b6` via `ea25174`; `4f205e58` `_NOP()` settling preserved (Plan 28-04 parks) → Phase 29 v2 PASS_PARKED (Leonardo Modified Rev 0 returns to Phase 26 baseline; WORST 0.047% zeros vs 83.8% pre-revert).
- **v1.9 hand-off:** 15 N=5 W27C512 binaries at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`; Bug A (Modified Rev 0 upper-address jitter, A15=1 → 1.86× skew) + Bug B (Rev 2.0 /CE-or-/OE timing + VPP=13.1V) characterized in `.planning/v1.6-EVIDENCE.md` Phase 29 v2 H3 block + `.planning/milestones/v1.6-phases/29-multi-board-bench-verification/29-04-SUMMARY.md`.
- See full archive: `.planning/MILESTONES.md` §v1.6, `.planning/milestones/v1.6-REQUIREMENTS.md`, `.planning/v1.6-EVIDENCE.md`.

</details>

## v1.5 — Arduino Uno (ATmega328PB) Board Support (SHIPPED 2026-05-21)

<details>
<summary>✅ v1.5 shipped — `uno328pb` as third first-class firmware target (5 phases, 6 plans). Full detail in `.planning/milestones/v1.5-ROADMAP.md`.</summary>

- **Ship tag:** `3.0.0b4` (both sub-repos, GitHub Pre-release on each).
- **Phases:**
  - [x] Phase 21: Firmware Target — `uno328pb` (2 plans; FW-01..FW-04)
  - [x] Phase 22: Release Pipeline Artifacts (1 plan; REL-01, REL-02)
  - [x] Phase 23: Host CLI Installer Integration (2 plans; INST-01..03, GATE-01)
  - [x] Phase 24: Bench Validation on 328PB-Uno (operator-on-bench; BENCH-01, BENCH-02)
  - [x] Phase 25: Documentation + Milestone Close (1 plan; DOC-01, DOC-02, MS-01)
- **Bench-validated** on operator's 328PB-Uno via `firestarter fw -i --pre` end-to-end on `/dev/ttyUSB0` with `urclock` bootloader. Post-flash handshake reports `v3.0.0b4 / uno328pb`.
- **Open v1.9 backlog** carried forward (3 todos): `large-read-data-jitter-uno328pb` (HIGH, pre-existing, affects all controllers — now in scope for v1.9), `w27c512-eeprom-misclassification` (HIGH, operator-tagged asap), `avrdude-mcu-detection-fallback` (low).
- See full archive: `.planning/milestones/v1.5-ROADMAP.md`, `.planning/milestones/v1.5-REQUIREMENTS.md`, `.planning/v1.5-BENCH-RESULTS.md`.

</details>

## v1.3 — CMOS EPROM Family Hardware Validation (PAUSED 2026-05-20)

**Milestone goal:** Bench-validate, on real silicon and on both Arduino Uno + Leonardo, that the algorithm-0x07 (28-pin DIP CMOS UV-EPROM, 212 chips in DB) and algorithm-0x08 (32-pin DIP CMOS UV-EPROM, 127 chips in DB) dispatch logic shipped in v1.0–v1.2 actually programs, reads back, and verifies cleanly across the full 32K → 512K density span. This is **validation, not new features** — architecture is locked.

**Status:** ⏸ Paused 2026-05-20 — hardware-gated. Phase 11 shipped clean; Phase 12 Wave 0 desk-side scaffold committed; Plans 12-01/02/03 (BENCH-01/02/05 — W27C512, SST27SF512, W27C257) + entire Phase 13 + Phase 14 await operator bench hardware (Uno + Leonardo + RURP shield + DIP-28 socket + scope + bench chips). Resume command: `/gsd-execute-phase 12 --wave 1 --interactive` once hardware is available.

**Granularity:** Comprehensive (compressed — focused validation milestone, not a build milestone).
**Phase numbering:** Phases 11-14 (continues from v1.2 close).

### Structural Notes

- **Bench-gated vs. desk-side split.** Phase 11 (coverage matrix + DB inconsistency report) is fully desk-side and can land without hardware. Phases 12 and 13 are operator-on-bench (Uno + Leonardo + chip socket + scope). Phase 14 is paperwork only.
- **PROTO-01/02 are observation protocols, not standalone phases.** Chip-ID read at the start of every BENCH cycle (PROTO-01) and scope-measured VPP at the chip socket during write (PROTO-02) are practiced in Phase 12 where the protocol is established, then carried forward into Phase 13. They map formally to Phase 12 (where the observation protocol is set up + first applied) but the success-criteria coverage runs across both bench phases.
- **Density coverage strategy.** Phase 12 covers the 28-pin / algo-0x07 family at both the marquee 64K size (W27C512, SST27SF512) and the 32K low end (BENCH-05). Phase 13 mirrors this for 32-pin / algo-0x08 at 256K + 512K (W27C020, W27E040) and the 128K low end (BENCH-06). Together this exercises the full address-bus span end-to-end.
- **Deferred v1.2 items.** BENCH-01 (W27C512 bench cycle) naturally closes the four v1.2 hardware-pending UAT items (Phase 08 SC#2/SC#3, Phase 08 HUMAN-UAT.md, Phase 09 Plan-05 Task 3 chip-seated W27C512 UAT). Phase 12 detail flags this closure.
- **Flash budget floor.** v1.2 ship state (Leonardo 24,482 B / 85.4%, Uno 22,262 B / 69.0%, firmware 3.0.0-dev) is a non-regress floor. v1.3 is read-only against firmware semantics; only defect-driven changes are in scope.

### Phases

- [x] **Phase 11: Coverage Matrix & DB Inconsistency Audit** — Desk-side enumeration of all 339 algo-0x07/0x08 DB rows + flag intra-algorithm inconsistencies. ✅ 2026-05-19
- [ ] **Phase 12: 28-Pin / Algo-0x07 Bench Validation** — End-to-end bench cycle on Uno + Leonardo for W27C512, SST27SF512, and the 32K density-low representative; establish chip-ID + VPP scope observation protocols. ⏸ Paused (Wave 0 shipped; Waves 1-3 await hardware)
- [ ] **Phase 13: 32-Pin / Algo-0x08 Bench Validation** — End-to-end bench cycle on Uno + Leonardo for W27C020, W27E040, and the 128K density-low representative; same observation protocols carried forward. ⏸ Paused
- [ ] **Phase 14: Milestone Close & Artifacts** — Publish BENCH-RESULTS, update MILESTONES, archive v1.3 phase directories. ⏸ Paused

### Phase Details

#### Phase 11: Coverage Matrix & DB Inconsistency Audit

**Goal:** Operator has a complete, single-source coverage map of every algo-0x07 + algo-0x08 chip in `chip_database.json`, with intra-algorithm DB inconsistencies surfaced as defect candidates for follow-up milestones.
**Depends on:** Nothing (desk-side; can land before any bench session).
**Requirements:** COV-01, COV-02
**Success Criteria** (what must be TRUE):

  1. A coverage matrix file exists at `.planning/v1.3-COVERAGE-MATRIX.md` (or equivalent) enumerating every algo-0x07 + algo-0x08 row in `chip_database.json` with: manufacturer, part_number(s), pin_count, size_bytes, pulse_duration, chip_id_check, chip_id_value, pinout class. Total row count matches DB histogram (212 + 127 = 339 chips).
  2. The same file (or a companion file) lists every intra-algorithm DB inconsistency — chips that share `pin_count` + `algorithm` but differ in `pulse_duration`, `chip_id_check`, or `pinout` — with each inconsistency labeled as a defect candidate for v1.4 or a sub-repo PR (no auto-fixes applied in v1.3).
  3. Operator can use the matrix to confirm that the six BENCH chips (BENCH-01..06) span the pinout classes and pulse-duration profiles actually represented in the DB, so bench results generalize to the rest of the 339 rows.

**Plans:** 4/4 plans complete

- [x] 11-01-PLAN.md — Wave 0 failing-test scaffold for tests/test_audit_coverage_matrix.py (10 tests) ✅ 2026-05-19
- [x] 11-02-PLAN.md — Wave 1 tool skeleton + CLI + §1 Summary + §2 DB Count Reconciliation ✅ 2026-05-19
- [x] 11-03-PLAN.md — Wave 2 §3 Full Enumeration (339 rows, per-algorithm sub-tables, D-06 sort) ✅ 2026-05-19
- [x] 11-04-PLAN.md — Wave 3 §4 Defect Candidates + DEFECT-COV-NN ledger + --check semantics
- [x] 11-05-PLAN.md — Wave 4 §5 BENCH Coverage Proof + golden-file fixture
- [x] 11-06-PLAN.md — Wave 5 D-07 planning-doc count reconciliation (PROJECT.md, ROADMAP.md, REQUIREMENTS.md, STATE.md) ✅ 2026-05-19

#### Phase 12: 28-Pin / Algo-0x07 Bench Validation

**Goal:** On both Uno and Leonardo, operator can run a full write → read-back → verify cycle on every named 28-pin CMOS UV-EPROM (W27C512, SST27SF512) and on a 32K density-low representative, with chip-ID and VPP observation protocols established and captured.
**Depends on:** Phase 11 (coverage matrix informs which density-low representative is in scope and which pinout classes are exercised). Bench hardware: Uno + Leonardo + RURP shield + DIP-28 socket + scope.
**Requirements:** BENCH-01, BENCH-02, BENCH-05, PROTO-01, PROTO-02
**Plans:** 4 plans (Wave 0 shipped; Waves 1-3 paused on bench hardware)

#### Phase 13: 32-Pin / Algo-0x08 Bench Validation

**Goal:** On both Uno and Leonardo, operator can run a full write → read-back → verify cycle on every named 32-pin CMOS UV-EPROM (W27C020, W27E040) and on a 128K density-low representative, completing the algo-0x08 family coverage at the high (512K) and low (128K) ends of the address-bus span.
**Depends on:** Phase 12 (chip-ID + VPP observation protocols established; bench harness validated against algo-0x07 first).
**Requirements:** BENCH-03, BENCH-04, BENCH-06
**Plans:** TBD (paused on bench hardware)

#### Phase 14: Milestone Close & Artifacts

**Goal:** v1.3 ships with a per-chip, per-board green/red/quirks artifact covering all six BENCH chips and both PROTO observation protocols, plus a clean milestone close (MILESTONES.md updated, phase directories archived).
**Depends on:** Phases 11, 12, 13.
**Requirements:** DOC-01, DOC-02
**Plans:** TBD (paused on bench hardware)

### v1.3 Coverage

| REQ-ID | Phase |
|--------|-------|
| BENCH-01 | Phase 12 |
| BENCH-02 | Phase 12 |
| BENCH-03 | Phase 13 |
| BENCH-04 | Phase 13 |
| BENCH-05 | Phase 12 |
| BENCH-06 | Phase 13 |
| PROTO-01 | Phase 12 (observation protocol carried forward into Phase 13) |
| PROTO-02 | Phase 12 (observation protocol carried forward into Phase 13) |
| COV-01 | Phase 11 |
| COV-02 | Phase 11 |
| DOC-01 | Phase 14 |
| DOC-02 | Phase 14 |

**Mapped: 12/12 requirements ✓** — no orphans, no duplicates.

## Prior Milestones (archived)

<details>
<summary>✅ v1.4 Beta & Pre-release Deployment Pipeline (Phases 15-20) — SHIPPED 2026-05-20</summary>

- [x] **Phase 15**: Versioning & Locked-Step Coordination (foundation) — 4/4 plans
- [x] **Phase 16**: App Beta Release Pipeline — 1/1 plan
- [x] **Phase 17**: Firmware Beta Release Pipeline — 1/1 plan
- [x] **Phase 18**: Beta-Aware Firmware Downloader (`--pre`, `--firmware-version`, `firmware list`) — 2/2 plans
- [x] **Phase 19**: Documentation (READMEs + `v1.4-RELEASE-PROCEDURES.md`) — 1/1 plan
- [x] **Phase 20**: End-to-End Smoke Test + Milestone Close — 1/1 plan

Ship tag: `3.0.0b3` (auto-incremented from `b1` → `b2` → `b3` during live E2E; six substrate defects E2E-01..06 surfaced and fixed in-place during the cut).
Hardware-flash validated: Uno + Leonardo at `3.0.0b3` via `firestarter fw -i --pre`.

Full milestone archive: [`.planning/milestones/v1.4-ROADMAP.md`](milestones/v1.4-ROADMAP.md).
Requirements archive: [`.planning/milestones/v1.4-REQUIREMENTS.md`](milestones/v1.4-REQUIREMENTS.md) (16/16 complete).
Summary: [`.planning/MILESTONES.md`](MILESTONES.md) §v1.4.
Phase archive: [`.planning/milestones/v1.4-phases/`](milestones/v1.4-phases/).

</details>

<details>
<summary>✅ v1.2 Message-ID Logging Rework (Phases 6-9) — SHIPPED 2026-05-19</summary>

- [x] **Phase 6**: Logging Infrastructure (catalog + codegen + helper + decoder) — 6/6 plans
- [x] **Phase 7**: Convert ERROR + WARN + INFO Call-Sites — 13/13 plans
- [x] **Phase 8**: Convert State-Machine Prefix Call-Sites (OK/INIT/MAIN/END) — 8/8 plans
- [x] **Phase 9**: Delete Old Log Macros + Measure Flash Savings — 5/5 plans
- [x] **Phase 10**: Milestone Close (v1.2) — closed by `/gsd-complete-milestone` (DOC-02)

Full milestone archive: [`.planning/milestones/v1.2-ROADMAP.md`](milestones/v1.2-ROADMAP.md) (frozen snapshot of full phase details + coverage map + dependency graph).

Requirements archive: [`.planning/milestones/v1.2-REQUIREMENTS.md`](milestones/v1.2-REQUIREMENTS.md) (23/23 complete).

Summary: [`.planning/MILESTONES.md`](MILESTONES.md) §v1.2.

</details>

<details>
<summary>⏸ v1.1 Safety Closure & Hardware Validation (Phases 1-5) — PAUSED 2026-05-18</summary>

- [x] **Phase 1**: Safety Closure (Intel-flash VPP, 28C chip-id) — complete
- [x] **Phase 2**: Wire-key rename + minipro attribution scrub — complete
- [x] **Phase 3**: Retroactive VERIFICATION.md for v1.0 phases — complete
- [ ] **Phase 4**: Hardware validation across chip families — Plan 2 of 3 in progress; **FM1608 byte-0 read bug** parked (needs different Uno R3 to unblock; see [`.planning/debug/fm1608-fresh-chip-baseline.md`](debug/fm1608-fresh-chip-baseline.md))
- [ ] **Phase 5**: Milestone close (DOC-01) — deferred until after v1.2 ships or fm1608 unblocks

Original artifacts: [`.planning/milestones/v1.1-paused/`](milestones/v1.1-paused/).

Also carrying: WARNING-4 (`firestarter_test.sh` / `write_test.sh` references to deleted `database_generated.json`).

</details>

<details>
<summary>✅ v1.0 Protocol-Aware Programming Architecture (Phases 1-13) — SHIPPED 2026-05-11</summary>

- [x] Phases 1-13 covering the algorithm-first dispatch architecture (13 phases, 22 plans, 4-day timeline)
- Key deliverables: protocol-prefix dispatch in `memory.cpp`, 743-chip database with explicit `algorithm` integer, five firmware handlers (`configure_eprom`, `configure_flash3`, `configure_flash_intel`, `configure_eeprom28c`, `configure_sram`), pre-write safety stack (VPP ADC compare, chip-ID validation, blank check), static-pin and address-bus correctness

Full archive: [`.planning/milestones/v1.0-ROADMAP.md`](milestones/v1.0-ROADMAP.md) | [`.planning/milestones/v1.0-REQUIREMENTS.md`](milestones/v1.0-REQUIREMENTS.md) | [`.planning/milestones/v1.0-MILESTONE-AUDIT.md`](milestones/v1.0-MILESTONE-AUDIT.md) | [`.planning/milestones/v1.0-INTEGRATION-CHECK.md`](milestones/v1.0-INTEGRATION-CHECK.md) | [`.planning/milestones/v1.0-phases/`](milestones/v1.0-phases/).

</details>

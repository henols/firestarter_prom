# Pitfalls Research

**Domain:** EPROM Programmer — Bench Validation of Operator Chip Inventory (v1.15)
**Researched:** 2026-06-23
**Confidence:** HIGH (grounded in project history, source-code traces, bench session records, planning artifacts, and firmware source)

---

## Critical Pitfalls

### Pitfall 1: Irreversible Write to a UV-EPROM Without an Eraser Available

**What goes wrong:**
The operator writes data to a genuine UV-EPROM (ST M27C512, AM27C020, or 2516) — chips that require ultraviolet light to erase. Because the operator has no UV eraser, any write is permanent. Once a bit is programmed from 1→0 it cannot be restored without a UV eraser. If the wrong image is written, or even a partial write is attempted, the chip is permanently altered. Using the EEPROM AND-mask strategy (writing all-0x00 forces all bits 0→0 or 1→0, never 0→1) still consumes the chip as a 0x00-only specimen. Writing a random test pattern wastes a chip the operator may have wanted to keep in pristine state.

**Why it happens:**
UV-EPROM chips look electrically identical to EEPROMs in the DB entry. The write command does not warn "this chip cannot be erased without UV." A read-first protocol is obvious in retrospect but is easily skipped when the operator is focused on proving the algorithm works. The 2516 is the sole graduation candidate in the inventory; spending it on a failed write test means there is no chip left to prove graduation.

**How to avoid:**
Each UV-EPROM phase plan must sequence as:
1. **Read + blank-check FIRST** (non-destructive; validates the read path, VPP-for-read, and DB decode with zero chip risk). If blank-check fails (chip already has data), the chip cannot be used for a pristine write test.
2. **Per-chip spend decision at the bench** — operator decides live: is the chip blank (write test possible), or does it have data (AND-mask/read-only test only)?
3. If blank: proceed with write→read→verify using a known image.
4. If not blank: perform the AND-mask write proof (all-0x00 image, which only requires 1→0 transitions) followed by read→verify. Never attempt to overwrite non-0xFF bytes with non-0x00 data on a UV-EPROM — that sets bits to 1 which cannot be done without an eraser.

For the 2516, explicitly decide before touching the chip: use a generated 0x000-sized partial image or the AND-mask path if the chip is not blank, not the full program cycle.

**Warning signs:**
- A bench plan that starts with `firestarter write` on a UV-EPROM without a preceding blank-check step.
- A plan that calls `firestarter write` on M27C512 or AM27C020 with `-b` (force-overwrite) when the chip's state is unknown.
- The `electrical.type` field in `firestarter info` reads "UV-EPROM" but the plan does not include a blank-check sub-step.

**Phase to address:**
The UV-EPROM validation phase (whichever phase covers M27C512, AM27C020, and 2516). The phase plan must make the blank-check/spend-decision gate the mandatory first action for each UV-EPROM chip, before any write sub-plan is unlocked.

---

### Pitfall 2: False-PASS Oracle — Reading on the Wrong Board or Shield

**What goes wrong:**
A bench session uses any board other than Leonardo, or uses a shield other than Rev 2.0, to read back a written chip. The result appears to pass but the read path is corrupted. The v1.9 read-bug RCA identified two independent failure modes: Bug A (Modified Rev 0 shield — upper-address jitter, A15=1 → 1.86× skew, causally controlled by read-strobe timing) and Bug B (Rev 2.0 timing/voltage issues that were present before v1.10 transport hardening but now exonerated at the transport layer — the RCA for Bug B is still deferred). The uno328pb board additionally has persistent bench instability during W27C512 reads (timeouts, 99%-0xFF drift) independent of the shield — documented as pre-existing, not fixed by COBS transport hardening.

A false-PASS is the worst outcome because it marks a chip as validated when the actual read is garbage. The SHA recorded in the VERIFICATION.md is meaningless if it came from a corrupted read path.

**Why it happens:**
With multiple boards on the USB hub, `/dev/ttyACM*` numbers shuffle after any unplug, replug, or power cycle. The board that was Leonardo at session start may be uno328pb after a shield swap. The COBS transport hardening in v1.10 made serial byte-exact — but byte-exact transport on a board with a hardware read-path fault still produces consistent garbage (the data is self-consistent noise, not the chip's actual content).

**How to avoid:**
The v1.13 standing bench precondition carries forward unchanged:
- **Leonardo + Rev 2.0 is the ONLY valid write/verify board-shield combination** for any operation that produces an authoritative PASS verdict.
- **uno328pb is N/A** for any program, write, or verify cell (brownout at 999.2; read instability documented as pre-existing, NOT fixed by v1.10).
- **Verify `controller:` port identity per task** at every bench task — run `firestarter info <chip>` or equivalent to confirm the Leonardo identity string before any write or read. If `/dev/ttyACM*` numbers have changed since session start, re-verify all port assignments.
- **ASK which silkscreen shield rev is mounted** before every task. The EEPROM `hw_revision` byte cannot distinguish Rev 2.0 from Rev 2.2 or Rev 0. Port identity alone does not confirm shield rev.
- **N≥5 reads with SHA hash comparison** — a single read is insufficient as an oracle. N≥5 reads that produce identical SHA hashes on Leonardo/Rev 2.0 establishes a credible PASS. A single divergent SHA in N reads is a FAIL (hardware fault, contact fault, or read-path bug).

**Warning signs:**
- A bench result that does not specify board and shield revision in its VERIFICATION entry.
- A SHA hash recorded without the board/port identity confirmed at the time of the read.
- A `firestarter read` result that shows large blocks of 0xFF or 0x00 (characteristic of uno328pb instability and Rev 0 address jitter respectively).
- Any plan that re-uses port assignments from a previous task without re-verifying `controller:` identity.

**Phase to address:**
Every bench phase and every bench sub-plan in the milestone. The success-criteria template for every bench plan must cite: board = Leonardo, port identity confirmed via `controller:` string, shield rev stated explicitly (operator confirms), R1 value recorded.

---

### Pitfall 3: NMOS Under-Voltage Programming — Best-Effort vs. Chip Destruction

**What goes wrong:**
The 2516 (and the four graduated NMOS chips: INTEL M2716, M2732/M2732A, SGS-THOMSON ETC2716, ST ETC2716) are programmed on the 0x0B `configure_eprom` path using the VPE rail directly (no dropping resistor). The bench VPE rail measures 22.4V DMM / 23.9V firmware readback. This is approximately 90% of the 25V datasheet specification for the 2516 and M2716 family. The firmware warns-and-proceeds on under-voltage (the warn threshold is 95% of `vpp_mv`, which is 23.75V for a 25V chip; the 22.4V DMM reading falls below this threshold). Programming at 90% of the spec voltage can result in:
- Partial programming: some bits do not toggle reliably, producing intermittent verify failures.
- Unreliable data retention: the threshold margin is reduced; programmed bits may flip back over years.
- For the 2516 specifically: the 500µs default pulse delay (0x0B protocol) may be too short at 90% of spec voltage. The firmware widens the pulse delay on retries (up to 20×), but the retry ceiling may not compensate for the voltage deficit.

**Why it happens:**
Phase 79 raised the VPP ceiling 22000→25000 under operator override D-07 (best-effort graduation, no hardware change ever). The firmware warns but proceeds. The bench tops out at ~22.4V VPE at the socket pin. This is a known and accepted risk for the four previously graduated NMOS chips — but for the 2516 (the one chip that has never been bench-proven on this hardware), the under-voltage risk is entirely uncharacterized. The 2516 is also a genuine UV-EPROM: a partial write cannot be corrected without an eraser.

**How to avoid:**
The 2516 programming plan must:
1. Record the live VPE rail reading at task start (`firestarter vpe` with live board) and capture the firmware under-voltage warning explicitly.
2. Use the full retry sequence — never abort early on the first warning.
3. Perform N≥3 read-backs immediately after programming; compare SHAs. If any read-back SHA diverges from the written image, treat it as a partial-program failure.
4. Accept that a PASS at 22.4V is a best-effort result: the chip should be expected to work but long-term data retention at 90% of spec is not guaranteed.
5. Treat any verify failure as a possible under-voltage programming failure, not as a software bug, before escalating to firmware investigation.

For the 2516 specifically, if the chip fails to program reliably at 22.4V, the honest verdict is "NMOS under-voltage partial-program" — not a chip defect and not a firmware bug.

**Warning signs:**
- Firmware emits `MSG_WARN_VPP_LOW` during the 0x0B write — this is expected at 22.4V for a 25V chip but must be explicitly noted in the bench record, not treated as a transient warning.
- The write appears to succeed (firmware returns OK) but the verify step fails — this is the signature of partial programming at marginal voltage.
- N=1 verify matching the written image is not sufficient; always do N≥3 reads before declaring a PASS.

**Phase to address:**
The 2516 investigation and graduation phase. The bench plan must include the VPE rail readback as the first step, explicitly document the under-voltage warning as expected, require N≥3 read-backs, and record a SHA-match table rather than a single verify result.

---

### Pitfall 4: UV-EPROM AND-Mask Misunderstanding — Trying to Set Bits 0→1

**What goes wrong:**
An operator writes a non-blank UV-EPROM with a data image that tries to set some bits from 0→1. On a UV-EPROM, bits can only be programmed from 1→0 (photons erase 0→1; VPP programs 1→0). The firmware's `configure_eprom` / `eprom_write_execute` does a per-chunk verify-after-program with retries. If the target byte has a 1-bit where the chip already has a 0-bit, the firmware retries the write pulse up to 20 times, then emits `MSG_ERR_WRITE_FAILED` with the mismatch count and address. This is not a firmware bug — it is the physical constraint of UV-EPROMs.

For the non-blank UV-EPROMs in the inventory, the AND-mask write strategy (using a 0x00 image) avoids this: writing 0x00 to any address forces all bits 0, which only requires 1→0 transitions and is always physically achievable. The mistake is writing any image that has 0xFF bytes or partial-non-zero bytes to a non-blank UV-EPROM.

**Why it happens:**
A bench operator may try to write a "real" data image to a non-blank UV-EPROM, expecting the firmware to handle it. The `firestarter write` command does not reject this upfront — it passes the image to the firmware, which discovers the physical constraint byte-by-byte and fails with cryptic mismatch errors late in the write cycle.

**How to avoid:**
- Run `firestarter blank-check` before any write to a UV-EPROM. If the chip is not blank (blank-check fails), only AND-mask writes (all-0x00 images or images that are bitwise-subsets of the current chip state) are valid.
- Generate the 0x00 test image in advance: `dd if=/dev/zero of=zeros.bin bs=1 count=<chip_size>`.
- Never use `-b` (force, skip blank check) on a UV-EPROM without knowing the chip state — the firmware will silently attempt impossible writes and spend the chip's write-cycle life for nothing.

**Warning signs:**
- `MSG_ERR_WRITE_FAILED` with mismatch counts immediately after the blank-check fails — this is the AND-mask failure mode.
- The verify step after a failed write shows the expected-vs-actual image differs at positions where the chip already had 0-bits.
- A write to a UV-EPROM that does not start with a blank-check confirmation.

**Phase to address:**
Every UV-EPROM phase. The phase plans must explicitly state the AND-mask strategy as the fallback path when a chip is found non-blank during the mandatory blank-check sub-step.

---

### Pitfall 5: The 0xA4 Empty-Input Write Desync Regression

**What goes wrong:**
`firestarter write` on a chip with `FLAG_CAN_ERASE` (W27C512, W27E512, SST27SF512, W27E040, W29C020, W29C040, SST39SF040, FM1608) runs the default write path (no `-b` flag). During the INIT phase, the firmware performs a blank-check which emits per-chunk `MSG_DATA_PROGRESS` frames as it scans the chip. If the host incorrectly ACKs each DATA frame during INIT, the firmware RX buffer accumulates N-1 spurious ACKs. When the firmware transitions to the MAIN phase and waits for the first host ACK to start data transfer, it finds the buffer already full of spurious ACKs — it dequeues them immediately, producing `MSG_ERR_EMPTY_INPUT` (0xA4) because the data chunks are not yet available.

This regression was fixed in Phase 77 (commit `fcf7974`): `_execute_phase` now passes `ack_data=False` for DATA frames during INIT and END phases. A regression test pins this invariant. However, if the test is removed or if a future refactor changes `_execute_phase` to ack DATA frames unconditionally, the regression resurfaces on every default write path that involves a blank-check sub-step.

**Why it happens:**
The INIT and MAIN phases use the same `_handle_progress_response` helper, but with different semantics: MAIN-phase DATA frames are flow-control (must be ACKed); INIT-phase DATA frames are progress notifications (must NOT be ACKed, because the firmware only consumes one ACK at the phase boundary, not one per chunk). The `ack_data=False` invariant is easy to break if `_handle_progress_response` is called with the wrong default.

**How to avoid:**
- Confirm the regression test in `test_eprom_operations.py` (`test_init_phase_data_frames_not_acked`) is present and green before any v1.15 bench session. This test was added in Phase 77 and pins the `ack_data=False` invariant.
- Any future refactor of `_execute_phase` or `_handle_progress_response` must preserve the INIT/END `ack_data=False` contract.
- If a write on an EEPROM/Flash chip produces `MSG_ERR_EMPTY_INPUT` (0xA4) at the start of the MAIN phase, suspect this regression immediately before looking at chip-state or DB issues.

**Warning signs:**
- `MSG_ERR_EMPTY_INPUT` (0xA4) error at the transition from INIT to MAIN during a `firestarter write` (no `-b`).
- The error occurs only on chips with `FLAG_CAN_ERASE` (blank-check in INIT emits progress DATA frames); a write with `-b` (which skips the blank-check) succeeds.
- A refactor diff that changes `_handle_progress_response` call sites in `_execute_phase`.

**Phase to address:**
The pre-bench software validation phase (first phase of v1.15, before any hardware session). Run the full host test suite including the regression test, and confirm it is green. Additionally, the first bench task on any EEPROM chip should run a default (no `-b`) write as the canonical test of the 0xA4 guard.

---

### Pitfall 6: FLAG_CAN_ERASE Auto-Erase Path — SRAM/FRAM Exempt, but Verify the Boundary

**What goes wrong:**
`FLAG_CAN_ERASE` is now derived from `electrical.type in ("EEPROM", "Flash/EEPROM")` in `convert_to_programmer`. The FM1608 FRAM (algorithm 0x40, `configure_sram` path) has `electrical.type = "SRAM"` — it does NOT get FLAG_CAN_ERASE and does NOT auto-erase. This is correct: `configure_sram` does not read `FLAG_CAN_ERASE`, and attempting `firestarter erase FM1608` returns "Not supported" (the standalone erase path exits 1 on SRAM/FRAM). The FM1608 write path uses `write -b` (force, skip blank-check) as the only viable path.

The potential confusion: an operator who runs `firestarter write FM1608` without `-b` will get a blank-check failure (FRAM is never blank after first use), followed by a misleading error that looks like an erase failure. The FM1608 does NOT auto-erase even though it is physically rewritable — it is a FRAM with byte-level rewrite capability, not a bulk-erase part.

**Why it happens:**
FRAM behaves like SRAM at the electrical level (byte-rewritable, no erase needed) but is classified as persistent storage. The terminology "write -b" is counterintuitive — it means "force write, skip blank-check" rather than "write in binary mode." An operator expecting auto-erase to handle the non-blank chip will be confused when it does not.

**How to avoid:**
- FM1608 bench plans must always use `firestarter write -b FM1608` (force-write, bypass blank-check). Document this explicitly in the phase plan.
- The blank-check step (which would fail for non-blank FRAM) must not be performed before FM1608 write attempts.
- Confirm that `firestarter info FM1608` shows `electrical.type = SRAM` (or equivalent) and no erase support — this is the correct classification.

**Warning signs:**
- A `firestarter write FM1608` without `-b` that fails with a blank-check error — the chip is not blank and SRAM types do not auto-erase.
- `MSG_WARN_ERASE_NOT_SUPPORTED` or an equivalent error on the FM1608 erase path.

**Phase to address:**
The FM1608 / SRAM validation phase. The success criteria must state explicitly that FM1608 write requires `-b`, and the negative-control test must confirm that `firestarter erase FM1608` returns a non-zero exit code (erase not supported on SRAM path).

---

### Pitfall 7: Flash/EEPROM Auto-Erase on W29C020/W29C040 — Blank-Check After Erase Required

**What goes wrong:**
W29C020 and W29C040 (algorithm 0x05, `configure_flash4`, `Flash/EEPROM` type) have `FLAG_CAN_ERASE` set and auto-erase before write. However, Phase 73 bench work showed that the original flash4 implementation had a defect: after the erase command, the chip was not actually erased to 0xFF — the blank-check that follows erase would fail. The Phase 74 fix (W29C040 SDP-unlock + data-driven page-write) was shipped and bench-proven, but the bench proof at Phase 74 Wave-1 was software-only; Phase 74 Wave-2 (hardware re-bench on Leonardo + Rev 2.0 with a real W29C040) was deferred to v1.14 and then closed as best-effort (deferred from Phase 74 state). The v1.13 algorithm fix is in production code, but silicon-level proof (write→read→SHA) on a real W29C040 is not yet in VERIFICATION.md.

For the v1.15 inventory (W29C020 and W29C040 are both listed), this means:
- The algorithm fix is in the firmware and host code.
- The auto-erase path (via `FLAG_CAN_ERASE`) fires before write.
- A failed erase would show up as a write verify failure where the output contains the OR of old and new bits.

**Why it happens:**
The flash4 chip family uses SDP (Software Data Protection) — writing must be preceded by an unlock sequence (0xAA at 0x5555, 0x55 at 0x2AAA, data at target). The erase command similarly requires an unlock sequence. If the erase does not complete before the blank-check runs, the blank-check fails. The Phase 74 fix addresses the SDP unlock, but a silicon-level confirmation is the definitive proof.

**How to avoid:**
- Run `firestarter blank-check W29C020` before any write attempt to confirm whether the chip is genuinely blank.
- After a write, perform an independent `firestarter read` and compare SHA to the written image (not just the firmware's verify step).
- If the write verify fails with data that looks like OR of old and new bits (bits that should have been cleared are still set), treat it as an erase failure and investigate the SDP unlock sequence.
- The Phase 74 fix in `flash_type_4.cpp` includes `CMD_CHECK_CHIP_ID` dispatch — confirm the chip ID is recognized before write (`firestarter id W29C040`).

**Warning signs:**
- Write verify failure where the readback data has unexpected set bits (0-bits that should have been erased to 1).
- `MSG_ERR_WRITE_FAILED` after the blank-check succeeds but before the data transfer.
- `CMD_CHECK_CHIP_ID` returning a mismatch for W29C040 (chip not recognized → wrong algorithm dispatched).

**Phase to address:**
The flash4 family bench validation phase (covering W29C020 and W29C040). The phase plan must include a chip-ID check as the first step, followed by a blank-check, write, and independent read-SHA comparison.

---

### Pitfall 8: 2516 User-Override Entry Bypasses Safety Gates

**What goes wrong:**
The 2516 is absent from `infoic.xml` (the 28 "2516" entries in minipro are all 25160 SPI serial parts, not the 2516 parallel UV-EPROM). The 2516 DB entry must be hand-authored in `~/.firestarter/database.json` (the user override file). This entry bypasses `build_db.py` entirely — it is not subject to:
- `check_dispatch.py` VPP-safety invariants (the gate runs only on `chip_database.json`, not the local override).
- `diff_db.py` per-chip diff tracking.
- The `resolve_pinout_key` logic that assigns canonical bus config from DIP pin numbers.

An incorrectly authored entry can set wrong VPP (e.g., 12V instead of 25V), wrong algorithm (e.g., 0x07 instead of 0x0B), wrong pin-count, or wrong pinout key — all of which can reach the hardware with zero software-layer protection.

**Why it happens:**
The local override path in `EpromDatabase` is intentionally designed to let operators add chips without a build_db.py run. The `skip_local_override=True` seam (used in tests) bypasses this file for hermeticity. But production resolves the override first. If the entry is malformed, `chip_resolver.resolve_chip` only checks `support_status` — not the correctness of VPP, algorithm, or pinout.

The highest-risk field is `vpp_mv`: if the 2516 entry specifies 12000 (12V, typical for 0x07 EEPROM) instead of 25000 (25V, correct for NMOS), the firmware issues the write sequence at 12V — far below the programming threshold for a 2516, producing no programming effect and no error. Conversely, if VPP is overstated (e.g., 28000), the firmware's `eprom_check_vpp` over-voltage check (measured VPP > `vpp_mv + 500 mV`) would block the write — but only on the 0x0B path where `eprom_check_vpp` actually runs.

**How to avoid:**
Before any bench session with the 2516 user-override entry:
1. Run `firestarter info 2516` and confirm: `algorithm` = 0x0B, `vpp_mv` = 25000, `pin-count` = 24, `electrical.type` = UV-EPROM, `support_status` = supported.
2. Manually review the `~/.firestarter/database.json` entry against the datasheet: verify VPP pin is pin 21 (DIP24 pinout — same as M2716 family, `DIP24_2716`), Vcc = 5V, CE#/OE#/PGM# pin assignments, and chip size (256 bytes for 2516).
3. Cross-check that the pinout key maps correctly: the 2516 is a 24-pin DIP NMOS UV-EPROM, same package as the M2716 family — use `DIP24_2716` as the pinout reference.
4. Run a dry-run VPE measurement (`firestarter vpe` or `dev reg`) with no chip seated to confirm the rail voltage before the first seated operation.

**Warning signs:**
- `firestarter info 2516` shows algorithm other than 0x0B or vpp_mv other than 25000.
- The NMOS write attempt returns no `MSG_WARN_VPP_LOW` (expected given 22.4V < 23.75V threshold) — absence of this warning when it is expected suggests the VPP value in the entry is wrong (e.g., set to 12000, so 22.4V does not trigger the under-voltage threshold).
- The write completes with OK but verify shows all-0xFF (chip never programmed — typical of VPP too low for NMOS).

**Phase to address:**
The 2516 investigation and graduation phase. The first plan must be the DB entry review and `firestarter info 2516` confirmation, before any write attempt.

---

### Pitfall 9: DB Decode Mismatch — VPP, Type, Size, or Pinout Disagreeing with Real Silicon

**What goes wrong:**
For chips that have never been bench-proven before (most of the 11-chip inventory), the DB entry may have an incorrect field that only surfaces when the chip is exercised on real hardware:
- **Wrong VPP**: the DB specifies 12V but the chip needs 14V (W27E512 erase) or vice versa.
- **Wrong size**: DB says 64KB but the chip is 32KB — the read pads with 0xFF at addresses beyond the chip's actual range, producing a SHA that never matches.
- **Wrong pinout**: DB maps VPP to the wrong physical pin — the chip gets VCC on the VPP pin and never programs.
- **Wrong algorithm**: a chip may be 0x07 in the DB but actually need 0x08 (EPROM_QUICK, 100µs pulse) to program reliably.

The v1.11 decode-correctness work fixed the major systematic decode bugs, but individual chip entries may still disagree with the specific silicon variant in the operator's inventory.

**How to avoid:**
For each chip exercised in the bench session:
1. Run `firestarter info <chip>` before the first operation and record: algorithm, vpp_mv, size, pin-count, electrical.type.
2. Cross-check against the chip's datasheet (or the markings on the physical chip) before applying VPP.
3. If size is uncertain, start with a short read (`dev read <chip> --size 256`) to confirm the data bus returns coherent data before a full read.
4. For VPP mismatches: live R1/R2 readback (`firestarter config --r1`) confirms the calibration. A R1 value other than ~270000 indicates a stale calibration that must be corrected before any VPP-dependent operation.

**Warning signs:**
- `firestarter id <chip>` returns a mismatch (chip ID from silicon does not match DB chip-id field) — this is the strongest early indicator of a wrong DB entry.
- A full read that produces all-0xFF (chip may not be enabled at the right address range, or VPP is not applied correctly for chip-ID reads).
- A write that appears to succeed but verify fails at every byte — wrong pinout or wrong algorithm.

**Phase to address:**
Every chip validation phase. The phase plan template must include `firestarter info <chip>` and `firestarter id <chip>` as the first two steps, before any write or erase.

---

### Pitfall 10: Stale R1 Calibration Producing Wrong VPP

**What goes wrong:**
The RURP shield's VPP boost regulator output is set by R1/R2 resistor values stored in Arduino EEPROM. The R1 value for the operator's uno328pb was incorrectly set (default 1000Ω) until Phase 54 corrected it to 270000Ω. If a board is swapped, the Arduino EEPROM has been reset, or a new firmware sideload cleared the calibration, the R1 value reverts to the default. An incorrect R1 causes the VPP regulator to produce the wrong voltage: with R1=1000 (instead of 270000), VPP reads approximately 13V ADC-value but the actual regulator setpoint is wrong — the chip may receive a VPP that is over-voltage (triggering `MSG_ERR_VPP_HIGH`) or under-voltage.

For the Leonardo (the only valid bench board), the calibration should be stable, but any firmware sideload to the Leonardo resets the Arduino EEPROM. After any sideload, R1/R2 must be re-confirmed via live readback before any VPP-dependent operation.

**How to avoid:**
- **At the start of every bench task**: run `firestarter config` (or the equivalent `r1` readback command) and confirm R1 ≈ 270000. If R1 reads as 1000 (default) or any other unexpected value, recalibrate with `firestarter config -r1 270000` before any chip operation.
- **After any firmware sideload to Leonardo**: recalibrate immediately. The sideload erases the Arduino EEPROM, resetting R1 to 1000.
- **Do not trust a session-start calibration across a sideload** — the sideload invalidates it.

**Warning signs:**
- `firestarter config` shows R1 = 1000 (the default, not calibrated).
- `MSG_ERR_VPP_HIGH` on a chip that previously programmed fine — indicates the regulator is running above the expected setpoint.
- `MSG_WARN_VPP_LOW` at a voltage that should be within range — indicates the regulator is running below setpoint.
- A VPP measurement (`firestarter vpp`) that disagrees significantly with previous sessions.

**Phase to address:**
Every bench phase. The standing bench precondition "live R1/R2 readback (r1 ≈ 270000) each task" must be the first documented step in every bench plan that involves VPP.

---

### Pitfall 11: Chip Seating and Contact Faults Misread as Chip Failures

**What goes wrong:**
A chip that is not fully seated in the ZIF socket, or that has oxidized or bent leads, produces read data that is all-0xFF (open data bus) or repeating patterns (address lines floating). The operator or bench plan interprets this as a chip defect, DB error, or algorithm bug, and spends time diagnosing a software issue that is actually a mechanical one.

For the 2516 (24-pin DIP), the chip is narrower than the 28-pin default ZIF socket width — it must be aligned to the correct end of the socket (pin 1 of the chip to the marked pin 1 of the socket). Misalignment by even one position can route VPP to VCC or float the address bus.

**How to avoid:**
- Before any read, visually confirm chip alignment in the socket with the ZIF lever closed.
- After a suspicious all-0xFF or repeating-pattern read, open the ZIF, reseat the chip, and retry before diagnosing a software issue.
- For 24-pin chips in a 28-pin socket: confirm the chip is positioned with pin 1 of the chip at the pin-1 end of the socket (chips in wider sockets must be aligned to one end — check the socket silkscreen).
- Confirm the ZIF lever is fully closed (firm resistance, not partially engaged).

**Warning signs:**
- All-0xFF read on a chip that is expected to have data (strongly suggests open address or data bus, not a blank chip).
- Repeating 64-byte or 256-byte patterns in a 64KB read (suggests floating address lines — the chip reads as if only the lower address bits are active).
- A read that varies run-to-run on N≥2 reads (a properly-seated chip produces identical reads; a floating pin produces noise).

**Phase to address:**
Every bench phase. The bench plan must include "confirm chip seated + ZIF fully closed" as a precondition before any read or write.

---

### Pitfall 12: Port-Identity Drift Across USB Replug in Multi-Board Sessions

**What goes wrong:**
The operator connects Leonardo and begins a bench task. A USB unplug-replug or shield swap causes the `/dev/ttyACM*` numbers to shuffle. The port that was `/dev/ttyACM0` (Leonardo) becomes `/dev/ttyACM1` after the replug, and `/dev/ttyACM0` is now an unrelated board. The subsequent `firestarter write -p /dev/ttyACM0 <chip>` targets the wrong board — possibly the uno328pb (which cannot complete a program without brownout). The result is either an error (brownout on uno328pb) or a false read/write on the wrong hardware.

**Why it happens:**
Linux assigns `/dev/ttyACM*` numbers dynamically at plug time. With multiple boards, the numbering is not stable across reconnects. The only stable identifier is the board's `controller:` identity string from the firmware handshake.

**How to avoid:**
Per `feedback_verify_port_identity_each_task` (operator memory): verify `controller:` port identity at every task, not just session start. After any USB event (unplug, replug, shield swap, board power cycle), re-verify all port assignments before the next operation. The simplest method is `firestarter info <any-chip> -p /dev/ttyACMX` — the response includes the `controller:` string which identifies the board.

**Warning signs:**
- A command that completes faster than expected (uno328pb is N/A for program, fails immediately with brownout — faster than a Leonardo write).
- A verify result that disagrees with a previous write on the same chip — suggest the read came from a different board than the write.

**Phase to address:**
Every bench phase. The bench plan must require re-verification of `controller:` identity at the start of each task, and after any USB event.

---

### Pitfall 13: Chip-OUT Before Sideload — Uno-Class Boards Only, Leonardo Exempt

**What goes wrong:**
The operator or a bench plan sideloads firmware to a Uno-class board (Uno or uno328pb) while a chip is seated in the ZIF socket. During firmware upload, the Uno-class boards drive the shield bus with AVR AVRD signals. This can assert high-voltage signals on chip address/data pins unexpectedly — particularly on VPP pins — potentially damaging the chip in the socket.

Leonardo is EXEMPT from this rule. The Leonardo's USB hardware handles firmware upload separately from the shield bus, so a chip in the socket is not at risk during a Leonardo sideload.

**Why it happens:**
The sideload mechanism is different between board families. Uno-class boards use the AVR AVRD protocol which repurposes the same GPIO pins the shield uses for bus communication. Leonardo uses the ATmega32U4's built-in USB DFU bootloader which does not drive the shield bus.

**How to avoid:**
- Before sideloading firmware to any Uno-class board: remove the chip from the ZIF socket.
- For Leonardo: no chip removal is necessary before sideload.
- After any sideload (to any board): recalibrate R1 before any VPP-dependent operation (sideload resets Arduino EEPROM — see Pitfall 10).

**Warning signs:**
- A plan that includes a firmware sideload to an Uno-class board without a preceding "remove chip from socket" step.

**Phase to address:**
Any phase that involves a firmware sideload to a Uno-class board. v1.15 is expected to be host-only (no firmware changes unless a defect forces a fix), so this pitfall is primarily relevant if a lockstep firmware fix is triggered by bench findings.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| N=1 read for verify instead of N≥5 SHA | Faster bench session | A single read on Leonardo/Rev 2.0 is not sufficient to rule out contact faults or residual instability; a false-PASS is permanently recorded | Never for an authoritative PASS verdict on a chip graduation |
| Skip blank-check on UV-EPROM before write | Saves one command round-trip | Wastes the chip on an impossible 0→1 bit write attempt; permanent damage | Never — blank-check must precede every UV-EPROM write |
| Use session-start port assignment after a shield swap | Saves the port re-verification step | Write goes to wrong board; result is invalid or board is damaged | Never — re-verify after any USB event |
| Trust `firestarter info` without a live R1 readback | Skips the calibration step | VPP setpoint may be wrong; chip programs at wrong voltage | Never for any VPP-dependent operation |
| Skip `firestarter id <chip>` before write | Saves 5 seconds | Wrong chip seated (or wrong chip name) → wrong algorithm → wrong VPP → chip damage | Never when validating a previously unbenched chip |
| Write 2516 without documenting VPE rail reading and firmware under-voltage warning | Cleaner PASS record | Obscures the best-effort nature of the result; if the chip fails later, the evidence trail is incomplete | Never — under-voltage programming requires explicit documentation |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| User-override `~/.firestarter/database.json` for 2516 | Copying a 0x07 EEPROM entry and changing the name, leaving `vpp_mv=12000` | Author from the 0x0B NMOS template: `algorithm=0x0B`, `vpp_mv=25000`, `pin-count=24`, `electrical.type=UV-EPROM`, `support_status=supported`, pinout = DIP24_2716 |
| `firestarter write` default path on EEPROM (no `-b`) | Assuming erase-before-write is silent; not checking for 0xA4 | Confirm the regression test `test_init_phase_data_frames_not_acked` is green before bench; if 0xA4 appears, suspect the `ack_data=False` invariant |
| FM1608 write | Running `firestarter write FM1608` without `-b` expecting auto-erase | FRAM is SRAM-typed; there is no auto-erase; always use `write -b` for FM1608 |
| Shield revision identification | Using `hw_revision` EEPROM byte to infer shield rev | Always ASK the operator which silkscreen rev is mounted — EEPROM byte cannot distinguish Rev 2.0, Rev 2.2, or Rev 0 |
| W29C040 write | Using `firestarter write W29C040` without verifying `firestarter id` first | Run `firestarter id W29C040` first; the flash4 path requires `CMD_CHECK_CHIP_ID` dispatch to be correct; a mismatch indicates a DB or chip identification issue |
| NMOS 0x0B write (2516, M2716, M2732) | Using `firestarter write` path expecting 25V at socket | The 0x0B path uses the VPE rail (~22.4V DMM), not the full VPP boost; `MSG_WARN_VPP_LOW` is expected and normal — record it, do not treat it as an error |

---

## "Looks Done But Isn't" Checklist

- [ ] **UV-EPROM write test:** blank-check confirmed FIRST — verify `firestarter blank-check <chip>` returned success before any write attempt is unlocked.
- [ ] **UV-EPROM non-blank write:** AND-mask strategy confirmed — verify the write image is all-0x00 (or a bitwise subset of current chip state) before `firestarter write` is run.
- [ ] **NMOS 2516 write:** `firestarter vpe` rail reading documented AND `MSG_WARN_VPP_LOW` firmware warning explicitly noted in bench record — verify both are present.
- [ ] **2516 user-override entry:** `firestarter info 2516` shows algorithm=0x0B, vpp_mv=25000, pin-count=24 — verify before any write attempt.
- [ ] **FM1608 write:** `-b` flag confirmed — verify the write command includes `--force`/`-b`; a write without `-b` will fail the blank-check.
- [ ] **W29C020/W29C040 write:** `firestarter id <chip>` returns a chip-ID match — verify before write; ID mismatch means wrong algorithm or wrong chip.
- [ ] **Every bench read:** N≥5 read count confirmed with SHA match table — verify VERIFICATION.md cites N, distinct SHA count, and board/port/shield identity.
- [ ] **Every bench task:** R1 ≈ 270000 confirmed via live readback at task start — verify the calibration readback is the first documented step.
- [ ] **Every bench task:** `controller:` port identity verified — verify the board identity string is confirmed at the start of each task, not just session start.
- [ ] **After any sideload:** R1 recalibrated — verify that sideload is followed by R1 re-confirmation before any VPP-dependent operation.
- [ ] **0xA4 regression guard:** `test_init_phase_data_frames_not_acked` is green — verify the regression test passes in the host test suite before any bench session.
- [ ] **Negative control for verify oracle:** wrong-file verify exits non-zero — verify this is tested at least once per chip family (the oracle is not valid if wrong-file verify silently passes).

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| UV-EPROM chip written with wrong image (no eraser) | HIGH — chip permanently consumed | Document the permanent state; if chip had data, it now has data AND-ed with the wrong image; the chip may still be useful for reading/probing; order a replacement if graduation proof requires a blank chip |
| UV-EPROM non-blank write attempt that fails with mismatch | LOW — no additional damage | Chip state is unchanged (bits cannot go 0→1); switch to AND-mask (0x00 image) strategy; the failed write did not alter bits that were already 0 |
| False-PASS recorded from wrong board or shield | MEDIUM — invalid VERIFICATION entry | Discard the bench result; re-verify port identity; re-run the bench session on Leonardo + Rev 2.0 only; update VERIFICATION.md with a corrected result and an explicit note that the previous result was invalid |
| 0xA4 desync during write | LOW — no hardware damage | Abort the write; confirm test_init_phase_data_frames_not_acked is green; if the regression has surfaced, revert the offending change to eprom_operations.py and re-run |
| Stale R1 calibration (R1=1000 default) on Leonardo | LOW | Run `firestarter config -r1 270000` to recalibrate; re-run the bench task |
| Chip contact fault misread as chip failure | LOW | Reseat chip in ZIF; confirm ZIF lever closed; re-run read; N≥2 reads with matching SHA confirms correct seating |
| Port-identity drift (write sent to wrong board) | LOW to MEDIUM | Re-verify all port assignments via `controller:` string; if the write went to uno328pb, the write likely failed with brownout error — no chip damage; retry on confirmed Leonardo |
| 2516 user-override entry with wrong VPP | MEDIUM — chip may have been programmed at wrong voltage | Correct the entry; re-run `firestarter info 2516` to confirm; if the chip was programmed at 12V (too low for NMOS), the chip is likely unmodified (12V is below programming threshold for 2516) — retry at the correct VPE rail voltage |
| W29C040 erase failure (blank-check fails after write attempt) | LOW | Run `firestarter erase W29C040` explicitly; confirm all-0xFF blank-check after; if erase fails, investigate the SDP unlock sequence in `flash_type_4.cpp` |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| UV-EPROM irreversible write without eraser | UV-EPROM validation phase (every UV-EPROM chip) | Blank-check sub-plan must precede every write sub-plan; phase plan explicitly locks the write sub-plan behind blank-check result |
| AND-mask misunderstanding (0→1 bit writes) | UV-EPROM validation phase | Phase plan documents AND-mask as the fallback path for non-blank chips; no arbitrary image is used on non-blank UV-EPROMs |
| False-PASS oracle (wrong board/shield) | Every bench phase | VERIFICATION.md entry cites board=Leonardo, shield=Rev 2.0, controller: string, port, R1; negative-control test (wrong-file verify exits non-zero) is documented |
| NMOS under-voltage 2516 programming | 2516 graduation phase | VPE rail reading documented; MSG_WARN_VPP_LOW noted; N≥3 read-backs with SHA table recorded |
| 0xA4 write desync regression | Pre-bench software validation phase | test_init_phase_data_frames_not_acked green in host test suite before any bench session begins |
| FLAG_CAN_ERASE / FM1608 SRAM boundary | FM1608 validation phase | firestarter info FM1608 shows no erase support; write -b used; erase returns non-zero exit code |
| W29C040 flash4 auto-erase correctness | Flash4 family bench phase | firestarter id W29C040 matches; blank-check confirms 0xFF after erase; SHA match on N≥5 reads |
| 2516 user-override bypasses safety gates | 2516 graduation phase (first plan) | firestarter info 2516 confirms algorithm=0x0B, vpp_mv=25000; dry-run VPE measurement before write |
| DB decode mismatch (VPP/type/size/pinout) | Every chip validation phase | firestarter info <chip> and firestarter id <chip> as first two steps in every bench plan |
| Stale R1 calibration | Every bench phase | live R1 readback (r1 ≈ 270000) is first documented step in every bench plan |
| Chip seating and contact faults | Every bench phase | visual confirmation before read; reseat on all-0xFF or pattern reads before diagnosing software |
| Port-identity drift | Every bench phase | controller: string verified per task; re-verified after any USB event |
| Chip-OUT before Uno-class sideload | Any phase with a firmware sideload | Chip-OUT confirmed before sideload; not applicable to Leonardo sideload |

---

## Sources

- `.planning/PROJECT.md` — v1.15 milestone framing, v1.14 NMOS best-effort D-07, Phase 77 erase graduation, 0xA4 regression fix
- `.planning/STATE.md` — bench preconditions, deferred items (FUT-01/03/04), standing board/calibration discipline
- `.planning/MILESTONES.md` — v1.14 Phase 77 (ack_data=False invariant, FLAG_CAN_ERASE from electrical.type), v1.13 false-PASS oracle design, v1.10 0xA4 transport context
- `firestarter_app/firestarter/eprom_operations.py` — `_execute_phase` ack_data=False invariant (lines 366-373), `write_cycle_eprom` SHA oracle (lines 793-873), 0xA4 regression comment (lines 367-372)
- `firestarter_app/firestarter/database.py` — `convert_to_programmer` FLAG_CAN_ERASE from electrical.type (lines 592-607)
- `firestarter_app/firestarter/chip_resolver.py` — support_status guard fires before any wire dict (lines 16-63)
- `firestarter/src/proms/eprom.cpp` — `eprom_write_init` FLAG_CAN_ERASE check (lines 100-107), `eprom_internal_erase` VPP routing (lines 274-288), `eprom_check_vpp` under-voltage warning logic (lines 252-270), 0x0B EPROM_LEGACY direct-VPE path (lines 144-147)
- `.planning/phases/77-erase-write-path-graduation-0x07-ee-eproms/77-PATTERNS.md` — ack_data=False regression test design, FLAG_CAN_ERASE derivation pattern
- `.planning/research/_archive-pre-v1.15/PITFALLS.md` — v1.14 hazard model (Pitfalls 2/7/8 directly carried forward for false-PASS oracle, constant drift, and wrong-board discipline)
- Memory: `project_write_path_empty_input_regression.md` — 0xA4 root cause (N-1 spurious acks from DATA frames during INIT, fixed via ack_data=False)
- Memory: `project_phase79_gate_reexamined.md` — VPE=22.4V DMM (authoritative), VPP~15-19V (dropped path), NMOS under-voltage warn-and-proceed, D-07 best-effort
- Memory: `reference_w27c512_bench_write_erase_gotcha.md` — erase unsupported on 0x07 path as standalone; write -b for non-blank chip
- Memory: `feedback_chip_out_before_sideload.md` — Uno-class chip-OUT rule; Leonardo EXEMPT
- Memory: `feedback_verify_port_identity_each_task.md` — port identity re-verification requirement after any USB event
- Memory: `user_shield_revisions.md` — EEPROM hw_revision cannot distinguish shield revs; always ASK
- Memory: `project_uno328pb_vpp_recal_and_program_brownout.md` — uno328pb N/A for program/write, R1 recalibration to 270000
- Memory: `reference_vpp_vpe_no_socket_routing.md` — vpp/vpe monitor commands enable regulator + measure only; no routing to socket

---
*Pitfalls research for: EPROM programmer bench validation of operator chip inventory (v1.15)*
*Researched: 2026-06-23*

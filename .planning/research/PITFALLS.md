# Pitfalls Research

**Domain:** EPROM Programmer — Chip Graduation (removing host-guard refusals for 4 chip families)
**Milestone:** v1.14 Feasible-Gap Implementation
**Researched:** 2026-06-18
**Confidence:** HIGH (grounded in project history, source-code traces, bench session records, and planning artifacts)

---

## Critical Pitfalls

### Pitfall 1: Removing a Host-Guard Refusal Without a Pre-Graduation Safety Checklist

**What goes wrong:**
A chip's `support_status` is flipped from `adapter-required` or `vpp-exceeds-max` to `supported` in `chip_database.json` (or the host guard in `chip_resolver.resolve_chip` is removed) before the complete stack has been validated. The refusal was the only thing preventing a wrong VPP voltage, wrong pin assignment, or wrong handler from reaching real hardware. Once the refusal is gone, the next `firestarter write` against that chip dispatches live hardware signals — possibly the wrong ones.

**Why it happens:**
The database classification change and the code change feel like one operation ("mark it supported"), but they are three distinct safety layers that must be proven independently before the guard drops:
1. The firmware handler produces the correct electrical sequence (proven by native Tier-1 recording-stub tests).
2. The host sends the correct parameters (proven by Tier-2 wire round-trip tests).
3. Real hardware produces the expected result without chip or shield damage (proven by Tier-3 Leonardo bench with chip-OUT VPP dry-run preceding the first seated operation).

Skipping step 3 before removing the guard is the failure mode. The v1.12 milestone deliberately installed these guards (`chip_resolver.resolve_chip` raises `ChipNotImplementedError` before any serial byte) precisely because the consequence of a wrong dispatch is hardware damage, not just a bad read.

**How to avoid:**
Each chip graduation phase must define an explicit pre-graduation checklist that must be completed in order:
1. Native Tier-1 tests prove the handler does NOT enable VPP on a 5V-only part (recording-stub register sequence).
2. Tier-2 host wire round-trip confirms the correct algorithm ID and parameters are transmitted.
3. A chip-OUT VPP multimeter dry-run confirms the VPP rail at the socket pin before any chip is seated.
4. A Tier-3 write+read-back SHA match on Leonardo is recorded as the golden baseline.
5. Only after all four: flip `support_status` to `supported` and remove the host guard.

`check_dispatch.py` must be run after each graduation to confirm no chip violates the `_FAMILY_VPP_INVARIANTS` invariants.

**Warning signs:**
- A graduation phase plan that changes `support_status` in the same commit wave as the handler code, before any bench result exists.
- A phase that removes the `chip_resolver.py` guard without a VERIFICATION.md entry citing bench evidence.
- `check_dispatch.py` failures after a database regeneration.

**Phase to address:**
Every graduation phase (999.4 erase-path, 999.5 X88C64, 999.7 25V NMOS, 999.6 adapter). The graduation gate must be the final plan in each phase, locked behind the bench evidence plan.

---

### Pitfall 2: Raising `RURP_VPP_CEILING_MV` to 25000 When the Shield Cannot Physically Produce 25V

**What goes wrong:**
`RURP_VPP_CEILING_MV` is changed from 22000 to 25000 in `firestarter_app/tools/build_db.py`. The database is regenerated: the 4 `vpp-exceeds-max` chips (INTEL M2716, M2732; SGS-THOMSON ETC2716; ST M2716) flip to `supported`. The host guard is removed. A `firestarter write M2716` command is now dispatched. But if the shield's VPP boost regulator tops out below 25V — or if the 25V regulator setting routes 25V through the wrong CTRL_ bit to the wrong socket pin — the chip sees the wrong voltage on the wrong pin and is destroyed. The shield may also be damaged if 25V exceeds the regulator's design ceiling.

**Why it happens:**
The constant `RURP_VPP_CEILING_MV = 22000` in `build_db.py` is not a software preference — it reflects the physical maximum the RURP VPP boost regulator was designed and tested to produce. The v1.13 protocol enumeration states this explicitly: "Any Phase 75 work on the W27C512 erase rail (14V for erase vs. 12V for write) is within the 22V ceiling. No ceiling relaxation is proposed or needed." The v1.14 25V NMOS work relaxes that ceiling.

The danger is treating the ceiling as a software configuration rather than a hardware characteristic. Changing the number does not change what the regulator can produce. The operator decided on 2026-06-18 to "implement 25V NMOS assuming hardware can produce 25V" — the word "assuming" is load-bearing. The assumption must be verified, not assumed.

**How to avoid:**
Before changing `RURP_VPP_CEILING_MV`:

1. Operator multimeter measurement — chip OUT, no chip seated. Enable the VPP regulator via a dry-run command (or directly drive the CTRL_VPP_REGULATOR_ENABLE bit) and measure the resulting voltage at the DIP32 socket's VPP pin (pin 1 for the UV-EPROM pinout). Record the measured value. If it is below 25V, the ceiling cannot be raised without a hardware change; stop here.

2. Confirm which shield revision is on the bench. The EEPROM `hw_revision` byte cannot distinguish Rev 2.0 from Rev 2.2. Ask the operator which silkscreen rev is mounted (per `user_shield_revisions`). Rev 2.2 R41 = 10kΩ (confirmed at v1.7 close). Rev 2.0 R41 may differ. Regulator output depends on the R1/R2 resistor network — calibrated values must match the bench rev.

3. Confirm the CTRL_VPP_P1_ENABLE routing. 25V UV-EPROM chips (M2716 family) use VPP on socket pin 1 (P1 path, not the A9/VPE path used by EPROM_QUICK). Verify the CTRL_VPP_P1_ENABLE bit routes to pin 1 for the DIP32 UV-EPROM pinout and does not inadvertently route 25V to a data pin.

4. Only after measured confirmation: raise the ceiling, regenerate the DB, run `check_dispatch.py`, and proceed to Tier-3 bench with a chip seated.

**Warning signs:**
- A plan that changes `RURP_VPP_CEILING_MV` without a preceding bench measurement plan.
- A `check_dispatch.py` run using the new ceiling value before the operator has measured the rail.
- Any bench plan that seats a 25V chip before a chip-OUT dry-run has been documented.
- The note in `v1.13-PROTOCOL-ENUMERATION.md`: "No runtime firmware enforcement — the firmware trusts the host has pre-screened chips." At 25V, that trust becomes irreversible if wrong.

**Phase to address:**
The 25V NMOS phase (999.7). The very first plan of that phase must be the chip-OUT VPP multimeter dry-run, gated as `autonomous: false` (operator-only). The ceiling constant must not change until that plan's result is recorded.

---

### Pitfall 3: Flash-Budget Exhaustion Bricking the Leonardo Build

**What goes wrong:**
A new firmware handler (X88C64 `configure_eeprom_x88c64` or a 25V VPP-path extension) pushes the Leonardo flash usage above 100%. The `pio run -e leonardo` build fails. The milestone is blocked because no firmware can be uploaded to the only trustworthy verify board.

**Why it happens:**
The Leonardo flash ceiling has been the binding constraint since v1.12. At v1.13 close, the ceiling sat at 89.5% after the Phase 74 flash4 fixes (a shared AMD chip-ID utility was explicitly created to stay within budget). Each new firmware handler costs 1–3 KB. The X88C64 handler (`configure_eeprom_x88c64`) implementing the full ALE/WR/RD multiplexed-bus sequence plus toggle-bit polling plus WC control is likely 1.5–3 KB. Adding it on top of the already-used 89.5% risks an overflow — 10.5% headroom = approximately 3 KB at the Leonardo's 28,672-byte total.

The v1.13 flash4 fix specifically introduced a shared `flash_check_chip_id_execute` utility to avoid duplicating the chip-ID logic. That pattern must be repeated for v1.14 handlers.

**How to avoid:**
- Every firmware-touching phase plan must include `pio run -e leonardo` as a success criterion with the flash percentage recorded.
- Implement handlers in order of flash cost: lower-cost changes first (erase path 999.4 is mostly host-side and adds minimal firmware flash; 25V NMOS 999.7 may only require a constant change and a new CTRL_VPP_P1_ENABLE path; X88C64 999.5 is the heaviest).
- Before committing the X88C64 handler, build a size estimate: count the number of new functions and compare against the known cost of `flash_type_4.cpp` additions from v1.13.
- If the build goes over ceiling: look for shared utilities (e.g., the I/O6 toggle-bit polling may share structure with the DQ7 polling in `configure_eeprom28c`).
- Never defer the flash check to "after I'm done" — verify at each plan boundary.

**Warning signs:**
- Phase 74 Wave-2 (74-03) is still deferred from v1.13. That plan carries a flash percentage from Phase 74's software work (89.5%). Any v1.14 firmware additions must be measured against that baseline, not a stale pre-v1.13 figure.
- A plan that says "implement the handler" without a flash-percentage success criterion.
- A plan ordering that puts the X88C64 handler before the lighter 25V NMOS change.

**Phase to address:**
All firmware-touching phases. The build order in PROJECT.md (999.4 → 999.5 → 999.7 → 999.6) places the X88C64 handler (999.5) second. Consider moving 999.7 before 999.5 since 25V NMOS may require only a ceiling constant change and a routing-bit confirmation — minimal flash cost — leaving maximum headroom for the X88C64 handler.

---

### Pitfall 4: ALE Routing Infeasibility Discovered Only After Implementation Work Begins

**What goes wrong:**
Work on the X88C64 `configure_eeprom_x88c64` handler begins — the write-sequence logic is implemented, tests are written — and then the ALE routing investigation reveals that no free RURP control-register bit exists to toggle ALE. The chip requires ALE to latch the multiplexed address/data bus. Without ALE, the handler cannot write. The work is wasted and the chip cannot be graduated without a PCB change.

**Why it happens:**
The X88C64 feasibility document explicitly flags ALE routing as an open question with LOW confidence: "ALE routing is available via an existing RURP control-register bit — LOW confidence — Not yet investigated." The document says the ALE/WR/RD investigation must happen first (§5, item 1). But implementation pressure can lead to deferring the blocker investigation until after the handler code is done.

**How to avoid:**
Make the ALE routing investigation the mandatory first plan of the X88C64 phase, before any handler code is written:

1. Read `firestarter/include/rurp_pinout.h` and map every `CTRL_*` bit to its current use.
2. Identify any unused bit that can drive a GPIO to the DIP24 socket position for ALE (pin 22 on the X88C64P).
3. If a free bit exists: document the routing, write a Tier-1 native test that confirms the ALE toggle sequence via the recording stub, then implement the handler.
4. If no free bit exists: document the constraint (handler requires a new shield PCB pad or a bodge wire); escalate the feasibility verdict from MEDIUM to BLOCKED-HARDWARE; defer graduation to a future milestone that includes hardware changes.

Committing to handler code before this investigation is complete is premature implementation.

**Warning signs:**
- A phase plan that starts with `configure_eeprom_x88c64.cpp` implementation before any `rurp_pinout.h` ALE-bit analysis.
- The feasibility document's Assumption A6 (LOW confidence) is not resolved in the phase's first plan.
- An X88C64 phase that does not include a `pio run -e leonardo` flash-% check after the ALE investigation concludes.

**Phase to address:**
The X88C64 handler phase (999.5). Plan 1 of that phase must resolve Assumption A6 from `X88C64-FEASIBILITY.md` before any handler code is written.

---

### Pitfall 5: DIP24 to DIP32 Adapter Mis-Wiring Routing a Signal to the Wrong Pin

**What goes wrong:**
A physical DIP24-to-DIP32 adapter is built with a wiring error. The most consequential error is the /WE reroute: the AT28C04/16's chip pin 21 (/WE) must go to DIP32 socket pin 30. If it instead connects to DIP32 socket pin 21 (the default direct-passthrough position), the firmware cannot assert write-enable — the chip is readable but not writable. A less obvious error is connecting unused NC (No Connect) DIP32 pins to power or ground, which could corrupt the address decode.

The adapter is 5V-only (no VPP), so the damage risk from a mis-wire is low (per `AT28C04-ADAPTER.md` §3: "The worst case for a wiring error is a non-functioning read or write — not chip destruction"). However, a mis-wired adapter produces incorrect results that are indistinguishable from a firmware bug, wasting bench time.

**Why it happens:**
DIP24-to-DIP32 adapters have two sub-classes of wiring errors:
- Signal routing errors: pin numbers on the chip do not match socket positions because the chip is smaller than the socket (the chip's GND on pin 12 must land at socket pin 16, not pin 12).
- NC confusion: DIP32 socket pins 3, 4, 25, 28, 29 are NC in the `DIP32_28C512_EEPROM` layout and must be left floating. Bridging any of these to VCC or GND will incorrectly assert an address bit on the AT28C16 or cause erratic behavior.

**How to avoid:**
The adapter spec in `firestarter/doc/AT28C04-ADAPTER.md` is the authoritative pin-table. Before any bench session with the adapter:

1. Use a continuity tester (DMM in continuity mode) to verify each of the 24 connected pairs from the pin table, with no chip inserted.
2. Confirm no continuity between the 7 NC DIP32 socket pins (1, 3, 4, 25, 28, 29, 31) and any signal, VCC, or GND.
3. Verify the critical /WE reroute: chip pin 21 to socket pin 30 (not 21).
4. Only then insert the AT28C04 or AT28C16 chip.

The graduation gate for this chip family should require a documented DMM continuity check result in the bench plan, not just a "built the adapter" assertion.

**Warning signs:**
- A bench plan that proceeds directly from "adapter is built" to "write test" without a continuity verification step.
- A write test that returns errors or all-zeros on readback, with no accompanying VPP measurement (since VPP is absent here, a bad read/write is purely a /WE routing or address bus fault).
- A firmware error response rather than a data mismatch — this would indicate a control signal (like /CE or /OE) is floating or shorted.

**Phase to address:**
The adapter graduation phase (999.6). The bench validation plan must include an explicit DMM continuity check of the adapter wiring before any chip is inserted.

---

### Pitfall 6: Erase-Rail (14V) Not Confirmed Before Flagging FLAG_CAN_ERASE

**What goes wrong:**
`FLAG_CAN_ERASE` is wired into `convert_to_programmer` based on `electrical.type == "EEPROM"`. The firmware's `eprom_write_init` now auto-erases before programming W27C512-class chips. The erase electricals in `eprom_internal_erase` drive `CTRL_VPP_REGULATOR_ENABLE`, `CTRL_VPP_A9_ENABLE`, and `CTRL_VPE_ENABLE`. The W27C512 datasheet specifies erase mode at OE/VPP=14V and A9=14V — but the RURP's VPP regulator is calibrated for the write mode setpoint (typically 12V for 0x07 protocol, confirmed at ~13V bench measurement). If the erase needs 14V and the regulator is producing 12V, the erase cycle completes without actually erasing the chip, then the write proceeds on an un-erased chip, causing the write to silently fail (data ORed with existing bits).

**Why it happens:**
The v1.13 protocol enumeration noted: "The 14V rail question (W27C512 datasheet: erase mode OE/VPP=14V, A9=14V vs. 12V for write) remains a Phase 75 bench verification item." This question was explicitly left open at v1.13 close. The firmware's `eprom_internal_erase` simply enables the VPP regulator and the existing VPP pins — it does not dynamically change the regulator setpoint. Whether the regulator's current setpoint produces 14V for erase or stays at 12V (the write setpoint) is unknown without measurement.

**How to avoid:**
The erase-path phase (999.4) must include, as its first bench plan:

1. Chip-OUT VPP meter dry-run at the erase-mode setpoint. Trigger the erase sequence with no chip seated. Measure the actual voltage at the VPP pin (A9) during the erase window. Record the value.
2. If measured VPP is in the 12–14V range: confirm whether the W27C512 can tolerate erase at the measured value (datasheets often specify minimum erase voltage; some chips erase successfully at 12V even though the spec says 14V).
3. If measured VPP is below the datasheet minimum: the regulator must be re-calibrated or a separate setpoint path must be used. Do NOT proceed to seated erase until VPP is confirmed within specification.
4. After erase, perform a full blank-read (all-0xFF check) to confirm the erase actually cleared the chip. A vacuous success (erase command returns OK but chip is not blank) is the silent failure mode.

The live R1/R2 calibration readback (`r1 ≈ 270000`) must be captured at the start of this bench session, per the v1.13 standing precondition.

**Warning signs:**
- An erase plan that doesn't include a VPP measurement step.
- An erase result that returns "success" but a subsequent read shows non-0xFF bytes — this is the silent failure mode.
- An erase bench session run on anything other than Leonardo + Rev 2.0 (the only bench-verified clean read path).

**Phase to address:**
Erase write-path phase (999.4). The chip-OUT VPP dry-run is the mandatory first bench sub-plan, before any seated erase is attempted.

---

### Pitfall 7: `constants.py` / `firestarter.h` Constant Drift Between Host and Firmware

**What goes wrong:**
A constant that must be identical in both repos gets updated in one and not the other. For v1.14, the two highest-risk constants are:

- `FLAG_CAN_ERASE` (0x02) — defined in `firestarter/include/firestarter.h` (C++) and used in `firestarter_app/firestarter/database.py` (Python). If the host sets bit 0x02 but the firmware reads a different bit position as `FLAG_CAN_ERASE`, the erase is silently never triggered (or the wrong operation is triggered).
- `RURP_VPP_CEILING_MV` — defined only in `firestarter_app/tools/build_db.py`. No firmware-side enforcement exists. If someone adds a firmware-side ceiling check with a different constant value, the two can diverge, gating different chips on each side.

**Why it happens:**
The constants are duplicated by design (C++ and Python cannot share a header) and the CI gates that check for drift (messages.toml codegen drift gate, `check_dispatch.py` VPP invariants) cover the wire protocol and VPP safety but do not cover flag-bit assignments. The `FLAG_*` constants in `firestarter.h` are not covered by any automated parity gate.

**How to avoid:**
- Any phase that touches a `FLAG_*` constant must explicitly verify both files in the same commit or commit pair.
- Add a parity test for `FLAG_CAN_ERASE` in the host test suite (analogous to the existing constants parity tests for other values) as part of the erase-path phase.
- After the `RURP_VPP_CEILING_MV` change (if it happens in 999.7), run `check_dispatch.py` and confirm the VPP invariant assertions still match the new ceiling.
- The existing CI codegen drift gate (messages.toml → messages.h + messages.py) covers only wire-protocol message IDs. It does not cover `FLAG_*` bits or the ceiling constant. Do not assume it catches everything.

**Warning signs:**
- An erase bench session where `firestarter write -e W27C512` does not auto-erase despite `FLAG_CAN_ERASE` being set in `database.py` — the most likely cause is the flag bit was not changed in `firestarter.h`.
- A CI run that is green but a bench session shows unexpected behavior on VPP-dependent chips.

**Phase to address:**
The erase-path phase (999.4, which modifies `database.py`). A parity test should be added in the same phase. The 25V ceiling phase (999.7) must update `check_dispatch.py`'s `_FAMILY_VPP_INVARIANTS` to match the new ceiling before any chip is flipped to `supported`.

---

### Pitfall 8: Wrong Board Used for Bench Verification Producing a False PASS

**What goes wrong:**
A bench session uses the uno328pb or the Uno (Rev 0 shield) for a write+read-back verification. The result appears to pass but the read path is corrupted: uno328pb has persistent read instability (intermittent timeouts, run-to-run divergence — documented as pre-existing, not fixed by COBS transport hardening). The Modified Rev 0 shield has Bug A (read-path fault, causally controlled by read-strobe timing). A verification run on either of these returns garbage data that happens to match a corrupted expectation, and the phase is falsely marked PASS.

**Why it happens:**
With multiple boards and shields in the bench fleet, it is easy to connect to the first available `/dev/ttyACM*` port after a USB reconnect without verifying which board is at which port. The v1.9 read-bug RCA is still open and explicitly deferred; the only confirmed-clean verify path for write operations is Leonardo + Rev 2.0 (the v1.13 standing bench precondition, verified at Phase 73 close).

**How to avoid:**
The v1.13 standing bench precondition is carried forward to v1.14 unchanged:
- Leonardo is the only board whose verify read is a valid PASS for any program/write operation.
- uno328pb is N/A for any program/write cell (brownout at 999.2, read instability).
- Check `controller:` port identity per task at every bench session — `/dev/ttyACM*` numbers shuffle after any USB unplug/replug.
- Ask the operator which silkscreen shield rev is mounted before every session.
- Record live R1/R2 readback (`r1 ≈ 270000`) at the start of every VPP-dependent bench task.

For the chip-OUT VPP dry-runs (all four graduation phases), the board is irrelevant since no chip operation occurs — but port identity must still be confirmed so the correct board receives the firmware sideload.

**Warning signs:**
- A bench result that does not specify which board and shield revision was used.
- A `firestarter read` result on a chip that was written with uno328pb.
- Port assignments established at session start not re-verified after any USB reconnect or shield swap.

**Phase to address:**
Every bench plan in every v1.14 phase. The success-criteria template for every bench plan must include: board = Leonardo, shield = Rev 2.0 (or explicitly stated rev), controller: identity verified, R1 recorded.

---

### Pitfall 9: Graduating a Chip Before the v1.13 Beta Cut Lands

**What goes wrong:**
v1.14 branches off `beta`. If the v1.13 lockstep beta cut (`3.0.0b10`) has not yet been made (it was operator-gated as of 2026-06-18), then `beta` may not yet carry the v1.13 changes. Branching v1.14 off the wrong tip includes v1.14 changes on top of a stale base, and the eventual merge back to `beta` will be a collision (the v1.12-to-v1.13 beta merge collision pattern, documented in `project_v112_beta_merge_architecture_collision.md`, required a full Phase 70 re-port).

**Why it happens:**
The branch model requires: operator cuts the v1.13 beta tag and pushes `beta` to the remote, then v1.14 branches off the new `beta` tip. If a v1.14 phase starts before the operator has done this, any firmware or host commits that land on the premature v1.14 branch will need to be re-ported onto the correct beta base, exactly as v1.12 required.

**How to avoid:**
Before any v1.14 work begins, confirm that:
1. `3.0.0b10` beta tag exists in both sub-repos.
2. Both sub-repos' `beta` branches carry the v1.13 merge (fw `a1953c2`, app `98b3a92` per `project_v113_milestone_closed.md`).
3. The v1.14 working branches are cut from the confirmed `beta` tip.

This is the pre-milestone branch setup plan and must be the first plan of the first v1.14 phase.

**Warning signs:**
- Sub-repo `git log beta..HEAD` shows v1.13 commits that are not in `beta`.
- The meta-repo gitlinks in `beta` do not match fw `a1953c2` / app `98b3a92`.

**Phase to address:**
Phase 77 (first phase of v1.14). The branch setup plan is mandatory and blocking all subsequent work.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Flip `support_status` to `supported` before Tier-3 bench evidence | Unblocks DB regeneration, CI goes green | A live hardware dispatch with unverified electrical behavior; potential chip/shield damage | Never for VPP-asserting chips; only for 5V-only operations with a strong prior (e.g., the AT28C04 adapter, VPP-free) — but even then, bench evidence is required before graduation |
| Change `RURP_VPP_CEILING_MV` without a VPP measurement | Unblocks the 25V NMOS classification | Routes 25V to a pin the hardware cannot produce or that is mis-routed — chip or regulator damage | Never |
| Defer the ALE routing investigation to a later plan | Allows handler code to be written optimistically | Wasted implementation effort if ALE is infeasible without PCB changes | Acceptable only if handler code is clearly labeled experimental and no graduation gate is triggered |
| Skip the `pio run -e leonardo` flash check for "one small addition" | Saves one build step | Accumulates undetected overflow until the first attempt to flash the board fails | Never; the check is a 30-second `pio run` command |
| Re-use an existing bench port mapping without re-verifying port identity | Saves time at session start | False PASS on wrong board (uno328pb instability, Rev 0 Bug A) invalidates the bench result | Never for any session that follows a USB reconnect, shield swap, or board power cycle |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| `build_db.py` ceiling constant to `chip_database.json` | Raising `RURP_VPP_CEILING_MV` without updating `check_dispatch.py` `_FAMILY_VPP_INVARIANTS` | Change the constant, regenerate the DB, update the invariant assertion to the new ceiling, run `check_dispatch.py` 0-violation |
| `messages.toml` codegen to `messages.h` + `messages.py` | Editing `messages.h` or `messages.py` directly instead of editing `messages.toml` and running codegen | Always edit `messages.toml` only; run codegen; commit both generated files; confirm drift gate is green in both sub-repos |
| `database.py` `convert_to_programmer` to `firestarter.h` `FLAG_*` | Changing a flag bit in Python without updating the C++ header | Any `FLAG_*` change requires a paired commit in both repos; add a parity test that reads the constant value from both files |
| DIP24-to-DIP32 adapter wiring to `pinouts.json` ground truth | Building the adapter from memory or from the chip datasheet alone | Use `firestarter/doc/AT28C04-ADAPTER.md` pin table as the sole authoritative source; verify against `pinouts.json` DIP24_2816 + DIP32_28C512_EEPROM entries |
| `firestarter_app` sub-repo `beta` branch to meta-repo gitlink | Bumping sub-repo commits during a phase and forgetting to update the meta-repo gitlink at milestone close | Pin the gitlink to the final beta merge commit at milestone close, not per-phase |

---

## "Looks Done But Isn't" Checklist

- [ ] **Erase path:** `FLAG_CAN_ERASE` set in `convert_to_programmer` — verify the bit value matches `FLAG_CAN_ERASE` in `firestarter.h`, not a stale or wrong value.
- [ ] **Erase path:** `firestarter write W27C512` auto-erases — verify by writing a chip with known content, then overwriting with different content without manual erase; confirm the second write produces the correct data (not the OR of old and new bits).
- [ ] **25V NMOS:** `RURP_VPP_CEILING_MV` changed to 25000 — verify the VPP rail actually measures at or above 24V (within tolerance) at the socket pin with no chip seated, on the specific shield revision the operator is using.
- [ ] **25V NMOS:** 4 chips flipped to `supported` — verify `check_dispatch.py` exits 0 violations on the full regenerated DB.
- [ ] **X88C64:** ALE routing confirmed — verify a free `CTRL_*` bit exists in `rurp_pinout.h` for ALE before any handler code is written.
- [ ] **X88C64:** Handler implemented — verify `pio run -e leonardo` stays under the ~88% flash ceiling (record the percentage).
- [ ] **AT28C04/16 adapter:** Adapter built — verify DMM continuity on chip pin 21 (/WE) to socket pin 30, and confirm no continuity between any NC socket pin and VCC/GND.
- [ ] **Any graduation:** `chip_resolver.resolve_chip` host guard removed — verify the chip no longer raises `ChipNotImplementedError` at the CLI, and that `firestarter info <chip>` shows `support_status: supported`.
- [ ] **Any graduation:** Tier-3 bench complete — verify a write+read-back SHA match is recorded in the phase VERIFICATION.md, on Leonardo, with the shield rev and R1 value documented.
- [ ] **Branch setup:** v1.14 branches off the correct `beta` tip — verify `git log --oneline beta..HEAD` in both sub-repos shows only v1.14 commits, not v1.13 commits that were supposed to be in beta.

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Host guard removed prematurely (chip dispatches to live hardware before bench validation) | MEDIUM | Re-add the `ChipNotImplementedError` guard in `chip_resolver.resolve_chip`; revert `support_status` in DB; document as a gap-closure item; add the missing bench plan |
| RURP_VPP_CEILING_MV raised but shield cannot produce 25V | HIGH | Revert the constant and DB regeneration; document the hardware limitation; the 4 chips stay `vpp-exceeds-max` until a shield revision can produce 25V; log as v1.15 backlog |
| ALE routing infeasible (no free CTRL_ bit) | MEDIUM | Document the constraint in `X88C64-FEASIBILITY.md`; update verdict from MEDIUM to BLOCKED-HARDWARE; chip stays `protocol-not-implemented`; propose a PCB bodge or new shield revision in the next hardware milestone |
| DIP24-to-DIP32 adapter miswired (chip not writable or bad data) | LOW | Re-inspect the adapter wiring against the pin table; re-wire the incorrect connections; re-run the DMM continuity check; repeat the bench validation |
| Flash budget exhausted (Leonardo build fails) | MEDIUM | Identify the largest handler; look for shared utility functions (toggle-bit polling, chip-ID) that can be factored out; or defer the heaviest handler to a later phase; never disable optimizations or strip test code to recover flash |
| False PASS on wrong board (uno328pb or Rev 0 shield) | MEDIUM | Discard the bench result; re-verify port identity; repeat the bench session on Leonardo + Rev 2.0 only; update the VERIFICATION.md with the corrected result |
| Constant drift between `database.py` and `firestarter.h` | LOW | Compare the flag bit values in both files; update the lagging file; add a parity test; re-run the full test suite in both repos |
| v1.14 branched off wrong beta tip (missing v1.13 changes) | HIGH | Stop v1.14 work; wait for operator to cut `3.0.0b10` and push the correct `beta`; rebase or cherry-pick v1.14 commits onto the correct beta tip; verify gitlinks in meta-repo match |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Host guard removed before bench evidence | Every graduation phase (999.4/5/6/7) | Graduation gate is the final plan; VERIFICATION.md cites the bench SHA match result |
| 25V ceiling raised without hardware measurement | 25V NMOS phase (999.7), Plan 1 | Chip-OUT dry-run result is documented with measured VPP value and shield rev |
| Flash budget exhausted | Every firmware-touching phase | `pio run -e leonardo` flash % is a success criterion in every firmware plan |
| ALE routing infeasibility discovered late | X88C64 phase (999.5), Plan 1 | `rurp_pinout.h` CTRL_* bit mapping is documented before handler code begins |
| Adapter mis-wiring | AT28C04/16 adapter phase (999.6) bench plan | DMM continuity check of all 24 pairs is documented in the bench plan |
| Erase rail (14V) not confirmed | Erase write-path phase (999.4) bench plan | Chip-OUT VPP measurement at erase setpoint is recorded before seated erase |
| FLAG_CAN_ERASE constant drift | Erase write-path phase (999.4), parity test plan | Parity test asserting FLAG_CAN_ERASE value matches across Python and C++ files |
| Wrong board used for bench verification | Every bench plan in all phases | Success criteria specify board = Leonardo, shield = Rev 2.0, controller: identity verified |
| v1.14 branched off wrong beta tip | Phase 77 (first phase), branch setup plan | `git log --oneline beta..HEAD` shows only v1.14 commits in both sub-repos |

---

## Sources

- `.planning/PROJECT.md` — v1.14 milestone framing, operator decision 2026-06-18, 25V NMOS assumption
- `.planning/ROADMAP.md` — v1.13 Phase 74/75/76, standing bench precondition, flash-ceiling constraints
- `.planning/v1.13-PROTOCOL-ENUMERATION.md` — 22V ceiling rationale, GAP index, anti-feature block, no runtime firmware enforcement
- `.planning/X88C64-FEASIBILITY.md` — ALE routing open question (Assumption A6, LOW confidence), MEDIUM verdict, handler pre-requisites
- `.planning/MILESTONES.md` — v1.12 host-guard safety layer, v1.13 close, accepted tech debt
- `firestarter/doc/AT28C04-ADAPTER.md` — /WE critical reroute, VPP-free safety characterization, NC pin risks
- Memory: `project_phase74_wave1_shipped_wave2_deferred.md` — flash at 89.5% after Phase 74 firmware
- Memory: `project_uno328pb_vpp_recal_and_program_brownout.md` — uno328pb N/A for program/write
- Memory: `feedback_chip_out_before_sideload.md` — chip-OUT rule (Uno-class only, Leonardo exempt)
- Memory: `feedback_verify_port_identity_each_task.md` — port-identity verification requirement
- Memory: `user_shield_revisions.md` — EEPROM hw_revision cannot distinguish shield revs; always ask
- Memory: `project_v112_beta_merge_architecture_collision.md` — beta branching collision precedent
- Memory: `project_v113_milestone_closed.md` — 3.0.0b10 operator-gated, fw a1953c2 / app 98b3a92

---
*Pitfalls research for: EPROM programmer chip graduation (v1.14 Feasible-Gap Implementation)*
*Researched: 2026-06-18*

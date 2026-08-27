# Cell A2 — uno328pb (ATmega328PB) on Rev 2.0 shield — the expected-failure cell

Runs `P-01`..`P-11` per `.planning/v1.34/PROCEDURE.md` (Amendment 3), control arm then v1.33,
W27C512 then W29C020, four evidence positions. This is the milestone's expected-failure cell
(Backlog 999.2): the requirement is that the failure be **observed**, not assumed.

## P-01 — Mount and declare (2026-08-27)

**Precondition, inherited from cell A1's own recorded teardown leave-state** (Task 15,
`161-03-SUMMARY.md` / `bench/cells/A1/CELL.md`): A1's Uno-class chip socket was confirmed
**EMPTY** at A1's own teardown (both chips pulled, no chip re-seated afterward). The Rev 2.0
shield carries its socket with it when moved, so that empty state travels with the shield.

**Orchestrator-measured bus state** (sysfs USB descriptors, read-only, 2026-08-27T14:25:33Z):

| Node | Descriptor | State |
|---|---|---|
| `/dev/ttyUSB0` | `1a86:7523` "USB Serial" (CH340) | LIVE — the uno328pb, THE ONLY LIVE NODE |
| `/dev/ttyACM0` | — | ABSENT (Leonardo removed by operator) |
| `/dev/ttyACM1` | — | ABSENT (A1 Uno removed by operator) |

**Independently re-confirmed by Claude** (2026-08-27T14:27:53Z, this task): `ls /dev/ttyACM*` ->
no such file (both absent); `/dev/ttyUSB0` present, `1a86:7523`, mtime `2026-08-27 14:24:30 UTC`
(`readlink -f /sys/class/tty/ttyUSB0/device` walked to the `idVendor`/`idProduct` files directly,
not merely quoted from the orchestrator's figure) — matches the orchestrator's measurement
exactly. **Only one node is live this cell**, but every avrdude/probe/tool invocation below still
passes an explicit `--port`/`-P`/`-p` `/dev/ttyUSB0` — never autodetected, per Standing bench rule
1 and this phase's own prior finding (nodes have shuffled multiple times already).

**Operator statement, recorded verbatim:** "uno328pb is connected and rev 2.0 shiled is on"
(operator's own spelling; the intended word is "shield"). This confirms: the board is connected,
and the Rev 2.0 shield is now mounted on the uno328pb — i.e. the shield has been moved from the
A1 Uno onto this board.

**Declared shield revision** (`shield_rev_declared`, becomes this value on all four A2
positions): **`Rev 2.0`** — normalized from the operator's "rev 2.0" to the canonical
capitalization used everywhere else in this project's record; no other normalization applied.
Silkscreen is authoritative per Standing bench rule 6; the operator's statement is the silkscreen
declaration for this cell.

**Socket-empty confirmation for the Uno-class chip-out precondition (`P-03`, control-arm
pass):** established by the conjunction of (a) A1's own teardown-confirmed empty-socket
leave-state (the state that traveled with the shield) and (b) the operator's statement above,
which reports the shield as mounted with no chip-seating action described. No chip has been
seated on this board at any point in this cell's history to date. `P-03` is therefore satisfied
as a **one-line no-op re-confirmation**, not a second gate — Task 3 (`161-04-PLAN.md`) explicitly
prescribes this shape, mirroring A1's own `P-01`-satisfies-`P-03` precedent.

**`$PORT` for this cell:** `/dev/ttyUSB0`
**`$SHIELD_REV` for this cell:** `Rev 2.0`
**`$TARGET` for this cell:** `uno328pb`

**Pre-cell arm integrity capture** (log `00_check_arms_pre_cell`): `check_arms.py` exit 0, both
arms verified (SHA+porcelain+file-probe+dep-freeze+interpreter+config-sha+cli-surface). `control`
HEAD `6bfa6453d1bac232eb81ab35fa7f14b50b0b291a`, `v133` HEAD
`cb189a9b001e9e34fb7651535de339761301d061`, `config_dir_sha`
`77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0` — matches the frozen pinned
value. `surface_diff_ab`/`surface_diff_ba` both empty; 25/25 CLI surface parity both arms. See
`check_arms_pre_cell.json`.

**Standing carve-out restated (D-07 safety):** this cell is expected to fail its W27C512 write on
both arms — that is the point of running it. The operator was informed at this checkpoint that
the 32-pin part swap later in this cell is conditioned on their own safety judgement of the board
after the W27C512 attempt (Task 6/Task 12's `P-08` gates carry this explicitly).

## P-02 — Board identity + pending provenance, all four positions (2026-08-27)

**Signature probe** (log `01_probe_board`): `board_probe.json` — `connected_part=atmega328pb`,
`board_signature=0x1e9516`, `mcu_matches=true`, `signature_route=route1`. Matches the expected
constants exactly and matches the operator's declaration.

**Control-arm `hw` probe** (log `02_hw_probe_pre_flash`, config dir inline): rc=0,
`Hardware revision: Rev 2.0-class` — the non-authoritative controller-string datum, recorded
alongside the authoritative signature probe. It agrees with the operator's silkscreen
declaration ("Rev 2.0"), a useful (non-authoritative) cross-check.

**Provenance captured for all four positions**, each with `--pending-readback` and its own
`--arm`/`--chip`/`--out`, `--cell-id A2`, `--target uno328pb`, `--port /dev/ttyUSB0`,
`--shield-rev "Rev 2.0"`:

| `position_id` | file | rc | `captured_at_step` |
|---|---|---|---|
| `A2__control__w27c512` | `provenance_A2__control__w27c512.json` | 0 | 2 |
| `A2__control__w29c020` | `provenance_A2__control__w29c020.json` | 0 | 2 |
| `A2__v133__w27c512` | `provenance_A2__v133__w27c512.json` | 0 | 2 |
| `A2__v133__w29c020` | `provenance_A2__v133__w29c020.json` | 0 | 2 |

Verified: `board_signature` matches `rig-pins.json`'s `targets.uno328pb.mcu`; exactly four
`provenance_A2__*.json` files exist with no default `provenance.json` collision; each record's
`captured_at_step==2`, `cell_id=="A2"`, `target_env=="uno328pb"`; each record's `arm`/`chip`
match its own `position_id`; each record's `image_mask`/`image_stamp_width`/`image_sha` equal
`IMAGE-PLAN.json`'s row (masks 20/21/22/23); each record's `fw_sha`/`host_arm_sha` equal
`rig-pins.json`'s pinned values for its own arm.

## P-03 (control pass) — satisfied by P-01, no second gate

Already recorded above: the socket-empty confirmation established at `P-01` covers this pass.

## P-04 (control) — flash + independent read-back judge (2026-08-27)

**Firmware checkout** (log `07_pio_upload_control` covers steps 2-3): `git -C
/workspaces/firestarter checkout 8695ee52c27a4bee4387c5c489afd5f3d7275e8a` — pre-checkout HEAD was
`5759dc8d...` (v133, A1's leave-state); post-checkout HEAD `8695ee52c27a4bee4387c5c489afd5f3d7275e8a`,
equal to `arms.control.fw_sha`; porcelain empty both before and after.

**Flash** (`pio run -t upload -e uno328pb --upload-port /dev/ttyUSB0`, cwd
`/workspaces/firestarter`): rc=0, "1 succeeded in 00:00:09.288". Build report: `Flash: 79.6% (used
26074 bytes from 32768 bytes)` — matches the control arm's expected hex span (26074) exactly.
PlatformIO resolved `urclock`/avrdude 8.1 and supplied its own flags; the host app's own
firmware-install path was never used.

**Independent read-back judge** (`judge_readback.py --target uno328pb --port /dev/ttyUSB0
--flashed-arm control --expect-arm control --out-dir $CELL_DIR --pins rig-pins.json`, log
`08_judge_readback_control`): rc=0.

- `judged_match`: **true**
- `judged_span_bytes`: **26074**, read at assertion time from `hex_span_expected_by_arm.control`
  — **not** the legacy scalar 23000 (`targets.uno328pb.hex_span_expected`)
- `vector_exclusions_applied`: both entries present (offset 0 length 4 — reset vector; offset 100
  length 4 — SPM_Ready/vector 25), unchanged from the control-arm-derived `-xshowvector`
  interrogation recorded in `rig-pins.json`
- `readback_size_bytes`: 32768; `flash_readback.bin` on disk: 32768 bytes — matches
- `sha_actual_judged` (`43dcb663...`) and `sha_expected_judged` (`b18a7151...`): recorded, **never
  compared** — this target's 8 excluded bytes (`[0,4)`, `[100,104)`, both in the vector table) make
  the two raw-span SHAs unequal on a *correct* flash; comparing them would be the exact false-RED
  Pitfall 4 names, and this task did not do it.

**Standing disclosed non-claim (carried, not raised as a new A2 finding):** the 8-byte
vector-exclusion blind spot (`[0,4)` + `[100,104)`, 8 of 26074 judged bytes on this arm) means a
fault confined entirely to those 8 bytes is invisible to A2's judged verdict. This is a Phase 160
§6 disclosed limit, proven live already on this exact silicon (`BRINGUP-uno328pb-v133/PREPROOF.md`,
plan 161-02) — carried here unchanged, not re-raised.

**Provenance patched, control positions only:** `A2__control__w27c512` and `A2__control__w29c020`
now carry `fw_readback_sha_judged == 43dcb663...` (the control verdict's `sha_actual_judged`),
`captured_at_step` still `2`. The two v1.33 positions' provenance are **untouched** — both still
carry the `--pending-readback` placeholder, confirmed above.

## P-05 / P-06 — Seat W27C512, pot confirmed against the firmware guard window (2026-08-27)

Operator (via coordinator relay): "seated and set, 12.0V" — W27C512 (DIP28) seated in the Rev
2.0 socket on the uno328pb at `/dev/ttyUSB0`; pot reported set and reading 12.0 V.

Claude's single confirming `vpp` read: **11.9 V** (first reported reading; band 11.8-11.9V across
the brief capture, no monitor loop). Judged against the firmware-derived accepted window
`[11.4, 12.5]` V for a 12000 mV target (`firestarter/src/proms/eprom.cpp:713` HIGH guard
`target+500mV`, `:736` LOW guard `target*95/100`), **not** string-equality to the target —
**in band**. Full detail, including a corrected first determination recorded honestly rather than
silently rewritten, in `POT.md`. `--force used? No.`

**Avrdude window now closed:** the W27C512 is seated. From this point no avrdude operation of any
kind (upload, read-back, or signature probe) may run on this board until the chip comes out again
at Task 6's swap (`P-08`).

## P-07 (control x W27C512) — position 1 of 4: observed, not asserted (2026-08-27)

Full detail in `WRITE.md` ("Position 5 (1 of 4)"). Summary: the write's INIT phase completed
(65536/65536 B queued), but the MAIN (chip-program) phase stopped at the exact first-block
boundary (0x0200/512 B) and the app's own internal serial-response timeout fired — wall-clock
**15.813 s**, wrapper exit code **1** (not 124 — the D-08 165 s ceiling was never approached). A
subsequent read succeeded (rc=0) and shows exactly 431/512 bytes of the first block were actually
programmed before the stall, everything from the second block onward reading fully erased.

**Matches Backlog 999.2's block-position prediction** (stops on the first program block) while
being materially more precise (bounded by the app's own ~15.8 s internal timeout, not an
unbounded hang; measured at 431/512 bytes into that block, not just "the block").

`judge_wrv.py`: `sha_verdict_judged=mismatch` (expected), `verdict_disagreement=true` (the read
command's own exit code 0 disagrees with the judged mismatch — recorded as a finding, not
resolved). `EVIDENCE.jsonl` row appended, `outcome=skipped-with-reason` (computed, not hand-set).
`render_evidence.py --check`: green.

## P-08 — Swap to W29C020 (2026-08-27, operator)

Operator, verbatim: "W29C020 seated". W27C512 (DIP28) removed, W29C020 (DIP32) seated on the
uno328pb at `/dev/ttyUSB0`. **D-07 safety judgement: the operator inspected the board before the
swap and affirmatively raised no concern** — this is an operator clearance actively given at this
gate, not a silent absence of objection. **Pot not touched** — Task 4's single confirming read
(11.9 V, in band against the firmware guard window) stands for the whole cell; no second `vpp`
invocation was run for this swap.

## P-09 (control x W29C020) — position 2 of 4: the first algorithm-0x05 attempt, a different failure mode (2026-08-27)

Full detail in `WRITE.md` ("Position 6 (2 of 4)"). Summary: **not predictable from position 1** —
a genuinely different failure mechanism. The **firmware itself** reported a verify-timeout error
(`ERROR: Timeout verifying 0x15 at 0x00007f (got 0x13)`), not a bare host communication timeout.
Wall-clock **4.019 s**, wrapper exit code **1** (the derived 391.748 s ceiling was never
approached). The subsequent read **also failed** (rc=1, partial 113152/262144 B) — contradicting
position 1's "the READ path works" observation, not re-asserting it. Byte 0x7f in the partial
read-back independently confirms the firmware's own quoted stop value (`0x13`). The bulk of the
partial read correlates ~65% with a freshly-generated copy of `A1__v133__w29c020`'s own image
(mask `0x13`, matching the stop-point byte) — flagged as an unconfirmed observation for Phase
165's RCA (possible residual chip content from A1's earlier use of this physical part), not
asserted as a proven cause.

`judge_wrv.py`: `sha_verdict_judged=mismatch`, `size_violations` **non-empty** (113152 bytes, not
262144) — this diverges from the plan's own stated acceptance-criteria assumption of an empty
`size_violations` list, which did not anticipate a partial (truncated) read as a real outcome;
recorded honestly rather than forced to match the template. `app_verdict_unjudged=1` **agrees**
with the judged mismatch this time (`verdict_disagreement=false`), unlike position 1's
disagreement. `EVIDENCE.jsonl` row appended, `outcome=skipped-with-reason`. `render_evidence.py
--check`: green.

**Both of cell A2's control-arm positions have now failed, by two distinct mechanisms** — a host
serial-response timeout (W27C512) and a firmware-reported verify timeout (W29C020) — neither a
clean electrical brownout with zero response, both bounded well under their respective D-08
ceilings.

## P-10/P-04 (v1.33) — arm switch, preserve control read-back, flash v1.33, judge (2026-08-27)

**Control read-back set preserved** into `readback_control/` (all six cell-root artifacts,
copied — not moved — before the v133 flash overwrites them), mirroring cell A1's own precedent.

**Firmware checkout:** `git -C /workspaces/firestarter checkout 5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`
— pre-checkout HEAD `8695ee52...` (control); post-checkout HEAD `5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`,
equal to `arms.v133.fw_sha`; porcelain empty both before and after.

**Flash** (`pio run -t upload -e uno328pb --upload-port /dev/ttyUSB0`, cwd
`/workspaces/firestarter`, log `22_pio_upload_v133`): rc=0, "1 succeeded in 00:00:08.124". Build
report: `Flash: 70.2% (used 23000 bytes from 32768 bytes)` — matches the v133 arm's expected hex
span (23000) exactly.

**Independent read-back judge** (`judge_readback.py --target uno328pb --port /dev/ttyUSB0
--flashed-arm v133 --expect-arm v133 --out-dir $CELL_DIR --pins rig-pins.json`, log
`23_judge_readback_v133`): rc=0.

- `judged_match`: **true**
- `judged_span_bytes`: **23000**, read at assertion time from `hex_span_expected_by_arm.v133` —
  **not** the legacy scalar `hex_span_expected` (which for this target numerically **equals**
  23000, the specific trap this target carries — using it would have silently passed a
  wrong-arm judgement on the control side; it was not used)
- `vector_exclusions_applied`: both entries present, unchanged
- `sha_actual_judged` (`bbf7aa68...`): **exact match** to plan 161-02's D-10 pre-proof
  (`BRINGUP-uno328pb-v133/PREPROOF.md`, same value) — an independent consistency confirmation
  that this cell's v133 flash reproduces the already-proven pre-proof result byte-for-byte.
  `sha_expected_judged` (`75382672...`): recorded, **never compared** to `sha_actual_judged` (this
  target's expected inequality on a correct flash, per Pitfall 4)
- **D-10 is closed** (plan 161-02): a v1.33 flash on an ATmega328PB judging a match at span 23000
  is already proven. This flash **reproduces** that result exactly — consistent with a correct
  flash, not merely an untested tool passing by chance.

**Provenance patched, v1.33 positions only:** `A2__v133__w27c512` and `A2__v133__w29c020` now
carry `fw_readback_sha_judged == bbf7aa68...`, `captured_at_step` still `2`. The two control
positions' provenance remain patched to the **control** verdict's SHA (`43dcb663...`) —
confirmed distinct and unaltered by this step.

## P-07 (v1.33 x W27C512) — position 3 of 4: the A/B half, a rule-8 re-seat, and a different mechanism (2026-08-27)

Full detail in `WRITE.md` ("Position 7 (3 of 4)"). Summary: **attempt 1** failed at INIT with a
firmware-reported chip-ID mismatch (`0x303` vs expected `0xda08`) — matching this project's own
standing contact-fault signature. **One clean re-seat performed** under Standing bench rule 8
(operator reported "reseated," no specific physical defect identified — recorded honestly as
"suspected," not "confirmed"). This chip's fifth insertion across A1 and A2 by this point.

**Attempt 2 (the one permitted re-run)** got past INIT and the full transfer, then failed with a
**firmware-diagnosed** program-convergence error at address `0x000179` ("failed to program within
25 pulses... usually means insufficient program voltage or a worn or failing cell, not a timing
problem") — wall-clock **10.245 s**. **This is a genuinely different failure mechanism from the
control-arm baseline** (position 1: host-side comms timeout, no firmware diagnosis, 15.813 s) —
recorded as different, not softened, with chip/contact wear named honestly as an undismissed
alternative to a genuine v1.33 firmware-behavior difference; neither is asserted as proven from
one data point.

**Read set:** three-run `dev consistency-check` **FAILED** — 3 distinct SHAs, no two reads agreed
(first divergence at offset `0x001A`, 23/65536 bytes divergent run1-vs-run2). `judge_wrv.py`:
`sha_verdict_judged=disagreement`, `n3_disagreement=true`, `app_verdict_unjudged=1` agreeing.

**N=3 escalation scheduled, not yet run:** because `distinct_read_shas > 1`, a retroactive
three-run read on the control arm's matching position (`A2__control__w27c512`) is scheduled for
`P-11`/Task 15, per 161-03-PLAN's shared-conventions escalation rule. `EVIDENCE.jsonl` row
appended, `outcome=skipped-with-reason`. `render_evidence.py --check`: green.

## P-08 (second arm) — Swap to W29C020 (2026-08-27, operator)

Operator, verbatim: "W29C020 seated". W27C512 removed, W29C020 (DIP32) seated on the uno328pb at
`/dev/ttyUSB0`. **D-07 safety judgement: operator inspected and proceeded, raising no concern —
an affirmative clearance given at this gate.** The operator was also asked directly about the
W27C512's physical condition after its five insertions (including the rule-8 re-seat) and did not
report on it — **recorded as NOT assessed**, not as "found sound." This matters directly for
plan 161-05 (cell A3/B2), which reuses this same physical part.

**Pot not touched** — Task 4's single confirming read (11.9 V) stands for the whole cell; no
second `vpp` invocation for this swap.

**VPP note carried into position 4, stated explicitly rather than left implicit:** position 3's
re-run failed with the firmware's own diagnosis naming "insufficient program voltage or a worn or
failing cell" as the likely cause — nominating low VPP as a candidate. The pot is **not**
adjusted for position 4 regardless: `P-06` sets VPP once per cell (comparability across all four
positions would break if changed mid-cell, and adjusting now would be chasing a success rather
than measuring one). Task 4's "in band" ruling (11.9 V inside the firmware guard window
`[11.4, 12.5]` V) is **not** the same claim as "VPP is optimal" — the guard not firing only means
the firmware's own init check did not trip; it says nothing about whether 11.9 V is sufficient
for reliable programming margin. This distinction is recorded explicitly so the earlier in-band
ruling is never read as a clearance that VPP is fine.

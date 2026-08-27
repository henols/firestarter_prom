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

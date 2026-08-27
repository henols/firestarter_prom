# Cell A3/B2 — Leonardo (ATmega32U4) on Rev 2.0 shield — v1.31's own reference rig

Runs `P-01`..`P-11` per `.planning/v1.34/PROCEDURE.md` (Amendment 3), control arm then v1.33,
W27C512 then W29C020, four evidence positions — the last four of the phase's twelve. This is the
**intersection cell**: it belongs to both the board sweep and the shield sweep, it is the exact
rig v1.31 used, and it is executed **exactly once** in this milestone. Phase 163 cites its rows;
it must not re-run them.

`cell_slug`: `A3-B2` (directory name, `position_id` prefix). `--cell-id` value passed to every
tool: `A3/B2` (with the slash).

## P-01 — Mount and declare (2026-08-27)

**Precondition, inherited from cell A2's own recorded teardown leave-state**
(`161-04-SUMMARY.md` / `bench/cells/A2/CELL.md`): A2's socket was left **empty** at teardown
(both chips pulled, no chip re-seated afterward). The Rev 2.0 shield carries its socket with it
when moved, so that empty state travels with the shield.

**Orchestrator-measured bus state before the gate** (sysfs USB descriptors, read-only,
2026-08-27T17:22:57Z): `/dev/ttyUSB0` `1a86:7523` "USB Serial" (CH340) — LIVE, the uno328pb,
socket empty; `/dev/ttyACM0`/`/dev/ttyACM1` ABSENT — the Leonardo not yet attached.

**Independently re-confirmed by Claude, pre-gate** (2026-08-27T17:24:34Z): `ls /dev/ttyACM*` ->
no such file (both absent); `/dev/ttyUSB0` present, mtime `2026-08-27 17:14:08 UTC` — matches the
orchestrator's measurement exactly.

**Operator declaration, verbatim:** "ttyACM0, Rev 2.0, messured vpp to be exactly 12v" (operator's
own spelling; "messured" = "measured"). This one statement carries three separate facts, each
recorded on its own below: the device node, the shield silkscreen, and a pre-flash multimeter VPP
reading volunteered ahead of any firmware `vpp` query (its ordering is part of its value — see the
P-06 section below for the paired comparison this enables).

**Orchestrator-measured bus state at resume** (sysfs USB descriptors, read-only, no port opened,
2026-08-27T17:41:11Z): `/dev/ttyACM0` `2341:8036` "Arduino Leonardo" — LIVE, freshly attached,
mtime `17:40`; `/dev/ttyACM1` ABSENT; `/dev/ttyUSB0` ABSENT (uno328pb disconnected by operator).

**Independently re-confirmed by Claude, post-resume** (2026-08-27T17:42:02Z): `/dev/ttyACM0`
present, `vid:pid=2341:8036`, mtime `2026-08-27 17:40:00 UTC` — matches the orchestrator's
measurement exactly. `/dev/ttyACM1` and `/dev/ttyUSB0` both absent. Only one live node this cell,
but per Standing bench rule 1 every avrdude/probe/tool invocation below still passes an explicit
`--port /dev/ttyACM0` — never autodetected.

**Declared shield revision** (`shield_rev_declared`, becomes this value on all four A3/B2
positions): **`Rev 2.0`** — the operator's own statement was already in canonical form; no
normalization applied (contrast the `BRINGUP-leonardo-provenance` pre-proof, where "rev 2.2" did
need case normalization to "Rev 2.2" — that record's own transcription note, not repeated here
because it does not apply).

**VPP multimeter pre-read** (operator-volunteered, recorded verbatim then normalized):
"messured vpp to be exactly 12v" -> **12.0 V, operator-measured**, taken **before** any firmware
`vpp` query on this board — no firmware read has yet been taken at the point this reading was
given. This pre-ordering is itself part of the record's value: it makes the `P-06` firmware
confirming-read a genuine, properly-ordered paired measurement (meter first, firmware second),
unlike A2's retrospective pairing. The confirming firmware read is deferred to Task 4/`P-06` per
the plan's own step ordering (this task only records the operator's declaration); the calibration
finding itself is written up there and in the SUMMARY.

**Socket state:** not yet re-confirmed post-mount (no chip seating action has occurred yet this
cell); A2's teardown-confirmed empty state is the only claim made at this point.

**`$PORT` for this cell:** `/dev/ttyACM0`
**`$SHIELD_REV` for this cell:** `Rev 2.0`
**`$TARGET` for this cell:** `leonardo`

**Chip-out rule note:** this board is **exempt** from the Uno-class chip-out-before-sideload rule
(standing bench rule 2) — it is flashed and read back with the chip seated. No `P-03` gate exists
in this cell for either arm's flash; the absent gate is explained here rather than left
unexplained, and again at each flash task where the exemption applies.

**Pre-cell arm integrity capture** (log `00_check_arms_pre_cell`): `check_arms.py` exit 0, both
arms verified (SHA+porcelain+file-probe+dep-freeze+interpreter+config-sha+cli-surface). `control`
HEAD `6bfa6453d1bac232eb81ab35fa7f14b50b0b291a`, `v133` HEAD
`cb189a9b001e9e34fb7651535de339761301d061`, `config_dir_sha`
`77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0` — matches the frozen pinned
value. `surface_diff_ab`/`surface_diff_ba` both empty; 25/25 CLI surface parity both arms. See
`check_arms_pre_cell.json`.

**Inherited chip-condition caveat, carried forward, not cleared:** the W27C512 this cell needs
has been handled eight times across A1 and A2, was never physically assessed by the operator when
asked, and threw a 0x303 contact fault in A2 requiring a rule-8 re-seat. This cell inherits that as
standing **uncertainty**, never as clearance. If a 0x303-class contact fault appears here, one
clean re-seat and one re-run are permitted per position, with both the discarded attempt and the
re-run recorded.

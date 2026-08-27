# Cell A1 — Arduino Uno (ATmega328P) on Rev 2.0 shield

Runs `P-01`..`P-11` per `.planning/v1.34/PROCEDURE.md` (Amendment 3), control arm then v1.33,
W27C512 then W29C020, four evidence positions. This cell inherits an occupied socket (the only
inherited-state cell in the milestone) and is the milestone's first 262144 B write/read on
silicon.

## P-01 — Mount and declare (2026-08-27T13:16:22Z)

**Enumeration before presenting the gate** (2026-08-27T13:14:06Z, Claude, sysfs mtimes):
- `/dev/ttyACM0` — Leonardo, mtime 13:02:11Z
- `/dev/ttyUSB0` — uno328pb (CH340), mtime 12:48:34Z
- No `ttyACM1` — the A1 Uno was off the bus, as expected.

**Enumeration on resume** (2026-08-27T13:16:22Z orchestrator sysfs descriptors, re-confirmed
independently by Claude at the same timestamp):
- `/dev/ttyACM0` — `2341:8036` "Arduino Leonardo", serial (empty), mtime 13:02
- `/dev/ttyACM1` — `2341:0043`, product (empty), serial `55736303739351B040E1`, mtime 13:15:37Z
  — **this is A1's Uno**, identity confirmed by serial descriptor, not by node number. The
  recorded serial `55736303739351B040E1` is byte-identical to the descriptor recorded before
  this board was set aside at the end of Phase 161 Plan 02, and the node's mtime advanced
  (12:48 area -> 13:15), consistent with a fresh re-enumeration of the same physical unit.
- `/dev/ttyUSB0` — CH340 "USB Serial" (uno328pb), serial (empty), mtime 12:48

Reported node matched the post-resume enumeration; no stop condition.

**THREE live nodes for the whole of this cell.** `/dev/ttyACM0` (Leonardo) and `/dev/ttyUSB0`
(uno328pb) are two stationary boards that will appear in every before/after enumeration this cell
runs — they are not a re-enumeration of the board under test. Every avrdude / `probe_board.py` /
`capture_provenance.py` / `firestarter` invocation in this cell carries an explicit
`--port /dev/ttyACM1` (or `-p`), never autodetected.

**Operator declaration, recorded verbatim:**
- Board: Uno, on `/dev/ttyACM1`
- Shield silkscreen: **"Rev 2.0"** (`shield_rev_declared`) — already the canonical value, no
  normalization applied. Silkscreen is authoritative; the A3 ADC band cannot distinguish
  Rev 2.0 / Rev 2.2 / Modified Rev 0.
- Socket: **EMPTY**, W27C512 removed — operator-confirmed in words: "socket empty"

**`$PORT` for this cell:** `/dev/ttyACM1`
**`$SHIELD_REV` for this cell:** `Rev 2.0`

`P-03` (Uno-class chip-out, control-arm pass) is satisfied by this same confirmation — the
socket was emptied here at `P-01`, so Task 3's `P-03` reference is a one-line no-op
re-confirmation, not a second gate (D-02: no artificial park prompt).

**Pre-cell arm integrity capture** (log `00_check_arms_pre_cell`, before the board was
reconnected — this tool never touches the device): `check_arms.py` exit 0, both arms verified
(SHA+porcelain+file-probe+dep-freeze+interpreter+config-sha+cli-surface). `control` HEAD
`6bfa6453d1bac232eb81ab35fa7f14b50b0b291a`, `v133` HEAD `cb189a9b001e9e34fb7651535de339761301d06`,
`config_dir_sha` `77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0` — matches the
frozen pinned value. See `check_arms_pre_cell.json`.

**Uno-class chip-out precondition satisfied:** the signature probe (`P-02`, Task 2) may now run.
From the moment the W27C512 is seated again (Task 4, `P-05`/`P-06`) no avrdude operation of any
kind may run on this board until the chip comes out again (`P-03`/`P-10` window for the second
arm).

## P-05 / P-06 — Seat W27C512, pot confirmed by measurement (2026-08-27)

Operator: "Uno on /dev/ttyACM1, rev 2.0 shield and W27C512 seated" — W27C512 (DIP28) seated,
board/shield re-confirmed. Pot not separately declared by the operator; `P-06` settled instead by
Claude's single confirming `vpp` read: `VPP: 12.0V, Internal VCC: 5.1V`, matching the 12.0 V
target to the precision this project records it at. Full detail in `POT.md`.

**Avrdude window now closed:** the W27C512 is seated. From this point no avrdude operation of any
kind (upload, read-back, or signature probe) may run on this board until the chip comes out again
at Task 6's swap (`P-08`).

## P-08 — Swap to W29C020 (2026-08-27, operator)

Operator: "W29C020 seated". W27C512 (DIP28) removed, W29C020 (DIP32) seated on the Uno at
`/dev/ttyACM1`. **Pot not touched** — `P-06`'s single confirming read (12.0 V) stands for the
whole cell; no second `vpp` invocation was run for this swap.

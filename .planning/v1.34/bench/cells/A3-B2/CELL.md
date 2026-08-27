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

## P-02 — Board identity + four pending provenance records (2026-08-27)

**Followed `bench/cells/BRINGUP-leonardo-provenance/PREPROOF.md`'s final working sequence
verbatim** — external `touch_1200.py` (bare, settle-only) + external `probe_board.py`, a 2 s
settle for the post-avr109-exit USB re-enumeration, then `capture_provenance.py` with
`--board-probe-json` pointing at the external probe's own `--out` file. This is deliberately
**not** a copy of A1's `P-02` (which relies on `capture_provenance.py`'s own internal
`probe_board.py` subprocess call, refuted on this board) — per delta 2, an A3/B2 `P-02` shaped
like A1's is the documented warning sign.

**Touch** (log `01_touch`, `--settle-s 2.0`, no `--wait-new-port` token anywhere in the recorded
argv): rc=0, `touch.json` records `changed: false`,
`devices_before == devices_after == ["/dev/ttyACM0"]` — the Leonardo's node does not change.

**Board probe — one genuine transient race, then success on immediate retry (Rule 3, blocking
issue auto-fixed):** the first `probe_board.py` attempt immediately after the touch (log
`02_probe_board`, first run) failed, rc=1: avrdude's stderr read `OS error: cannot open port
/dev/ttyACM0: Input/output error` / `No such file or directory` — the port was mid-re-enumeration,
consistent with the Caterina-entry transition PREPROOF documents for the post-avr109-exit case,
here evidently also possible on the touch-to-bootloader-entry side. `ls /dev/ttyACM0` immediately
after confirmed the node was present again with an advanced mtime. Re-ran the identical
touch+probe pair (log `01_touch` / `02_probe_board`, final, overwriting the failed attempt's
logs): touch rc=0 at `17:43:46Z`, probe rc=0 at `17:43:49Z` — **3 s elapsed**, inside the measured
3.487 s touch-to-responsive-programmer window. `board_probe.json`: `connected_part=atmega32u4`,
`board_signature=0x1e9587`, `mcu_matches=true`, `signature_route=route1` — matches the known-good
Leonardo signature and the operator's declaration exactly. This retry is a hardware-timing race,
not a defect in the command sequence or its ordering; the *first* attempt's failed log pair was
overwritten by the retry's successful pair, and this paragraph is the record of that discarded
attempt, per the same discipline the plan requires for a chip contact-fault re-seat.

**2 s settle** applied after the probe and before the first `capture_provenance.py` call, per the
seam PREPROOF establishes (avr109 session exit resets the MCU back into the application; the
tool's own next live-port action — the `hw` probe inside `capture_provenance.py` — needs that
re-enumeration to have settled first).

**Provenance captured for all four positions**, each with `--pending-readback`,
`--board-probe-json $CELL_DIR/board_probe.json` (Seam 1 — skips the tool's own internal
`probe_board.py` call entirely, consuming the already-obtained result above instead), its own
`--arm`/`--chip`/`--out`, `--cell-id A3/B2` (with the slash — the tool derives the `A3-B2` slug
itself), `--target leonardo`, `--port /dev/ttyACM0`, `--shield-rev "Rev 2.0"`. `--no-image-plan`
was **not** passed — every real sweep position resolves a genuine `IMAGE-PLAN.json` row, per the
plan's own prohibition; that flag is bring-up-only.

| `position_id` | file | rc | `captured_at_step` | log |
|---|---|---|---|---|
| `A3-B2__control__w27c512` | `provenance_A3-B2__control__w27c512.json` | 0 | 2 | `03_capture_provenance_A3-B2__control__w27c512` |
| `A3-B2__control__w29c020` | `provenance_A3-B2__control__w29c020.json` | 0 | 2 | `04_capture_provenance_A3-B2__control__w29c020` |
| `A3-B2__v133__w27c512` | `provenance_A3-B2__v133__w27c512.json` | 0 | 2 | `05_capture_provenance_A3-B2__v133__w27c512` |
| `A3-B2__v133__w29c020` | `provenance_A3-B2__v133__w29c020.json` | 0 | 2 | `06_capture_provenance_A3-B2__v133__w29c020` |

Verified by script: `board_probe.json`'s `connected_part`/`board_signature` match
`rig-pins.json`'s `targets.leonardo` values exactly; exactly four
`provenance_A3-B2__*.json` files exist with no default `provenance.json` collision; each record's
`captured_at_step==2`, `cell_id=="A3/B2"`, `cell_slug=="A3-B2"`, `target_env=="leonardo"`; each
record's `arm`/`chip` match its own `position_id`; each record's `image_mask`/`image_stamp_width`/
`image_sha` equal `IMAGE-PLAN.json`'s row (masks 24/25/26/27); each record's `fw_sha`/
`host_arm_sha` equal `rig-pins.json`'s pinned values for its own arm; `touch.json`'s recorded argv
carries no `--wait-new-port` token.

## P-03 / P-04 (control) — no chip-out gate, flash + independent read-back proof (2026-08-27)

**No `P-03` gate.** Standing bench rule 2 exempts the Leonardo: it is flashed and read back with
the chip **seated**. The socket was also still empty at this point regardless (no chip has been
seated in this cell yet), but the absent gate is explained by the rule, not by the empty socket
being a coincidence.

**Flash — executed by a PRIOR agent instance, before a user interrupt (2026-08-27T17:45:54Z).**
`git -C /workspaces/firestarter checkout 8695ee52c27a4bee4387c5c489afd5f3d7275e8a` (empty
porcelain, `rev-parse HEAD` confirmed equal to `arms.control.fw_sha`), then
`pio run -t upload -e leonardo`, cwd `/workspaces/firestarter`
(log `07_pio_upload_control.std{out,err}.log`, both untracked at the point this executor resumed
and committed with this task). PlatformIO report: `Flash: 86.0% (used 28170 bytes from 32768
bytes)`, `[SUCCESS] Took 8.08 seconds`. avrdude (Caterina, `CATERIN` programmer, device signature
`0x1e9587`): `28170 bytes of flash written`, `28170 bytes of flash verified`. **This
upload-time avrdude verify is explicitly NOT the project's proof oracle (D-01)** — it establishes
only that the flash step itself completed and self-reported clean before the interrupt landed;
the independent read-back below is the actual proof.

**This executor resumed after the interrupt, verified the flash's own logs first, and did NOT
re-run `pio run -t upload`.** `git -C firestarter status --porcelain` was empty and
`rev-parse HEAD` still equalled `arms.control.fw_sha` at resume, confirming the gitlink is still
sitting exactly where the flash left it — no intervening state change. Proceeded straight to the
independent read-back proof this task actually needed.

**Independent read-back proof (`judge_readback.py`, never the uploader's own verify):**
```
python3 .planning/v1.34/tools/touch_1200.py --port /dev/ttyACM0 --settle-s 2.0 \
  --out $CELL_DIR/touch_for_read_control.json
python3 .planning/v1.34/tools/judge_readback.py --target leonardo --port /dev/ttyACM0 \
  --flashed-arm control --expect-arm control \
  --out-dir $CELL_DIR --pins .planning/v1.34/rig-pins.json
```
**First attempt (log `08_touch_for_read_control` / `09_judge_readback_control`, discarded,
overwritten by the retry below):** touch rc=0; `judge_readback.py` rc=1,
`FAIL: avrdude read failed (rc=1): OS error: cannot open port /dev/ttyACM0: Input/output error`
— the identical transient post-touch USB re-enumeration race `BRINGUP-leonardo-provenance/
PREPROOF.md` already documented for this exact board (a `probe_board.py` attempt landing while
the port is mid-re-enumeration). **Rule 1/Rule 3 auto-fix — a genuine hardware-timing race, not a
defect in the command sequence:** re-ran the identical touch-then-judge pair immediately
(`/dev/ttyACM0` confirmed still present, advanced mtime). **Retry (final, kept):** touch rc=0;
`judge_readback.py` rc=0, `judged_match=True`, `judged_span_bytes=28170`. This discarded first
attempt is recorded here per the same discipline this cell applies to a chip contact-fault
re-seat — not papered over.

`READBACK-VERDICT.json`: `target=leonardo`, `flashed_arm=expect_arm=control`,
`judged_match=true`, `judged_span_bytes=28170` — read at assertion time from
`rig-pins.json`'s `hex_span_expected_by_arm.control`, **never** the legacy scalar (25098).
`sha_actual_judged == sha_expected_judged` = `d734ad49...` (exact match, `hex-extent` policy, no
vector exclusions). `readback_size_bytes=32768` (`flash_readback.bin`, whole-flash SHA
`334f9144...` recorded as the unjudged datum, D-02). Both control positions' provenance were
patched with `--patch-readback`; the v133 records are untouched.

**The control arm is on the Leonardo and proven by an independent avr109 read-back**, judged
against its own 28170-byte span — the flash (run before the interrupt) and its proof (run after)
are two separate events, both now on the record, with no re-flash performed.

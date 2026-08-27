# Cell A3/B2 — P-05 / P-06: chip seating and pot confirmation, calibration cross-check

## P-05 — Seat the W27C512 (2026-08-27, operator)

Operator reply, verbatim (via coordinator relay), in two parts (same class of ambiguity cell A2
recorded — the first reply answered a different, separately-asked question and was not treated as
a state confirmation on its own):
1. "nothing looks of" (i.e. "nothing looks off") — answer to the chip-condition inspection
   question, not a seat/pot state confirmation.
2. "seated and set" — the state confirmation, sought separately and explicitly after (1).

**W27C512 (DIP28) SEATED** in the Rev 2.0 socket on the Leonardo at `/dev/ttyACM0`.

### Inherited chip-condition caveat — CLOSED at this handling (ninth), by inspection

The W27C512 was handled eight times across A1 and A2 with its physical condition never assessed —
the operator was asked twice and did not answer, and it threw a `0x303` contact fault in A2
requiring a Standing bench rule 8 re-seat. Both A2's `CELL.md` and this cell's own `CELL.md` (P-01
section) carried that as explicit, unresolved **uncertainty**.

At this, the part's **ninth** handling, the operator inspected it and reported **"nothing looks
of[f]"** — the first assessment of its physical condition anywhere in the phase. Recorded
precisely, not overstated: this is **an operator visual inspection reporting nothing anomalous at
handling nine**, not a clean bill of health from any measurement, and it is **not** retroactive
clearance for A2's contact fault, which remains a real, separately-recorded observed event (its
own discarded attempt is preserved in `A2/CELL.md`, unchanged by this note). The standing caveat
is closed as of this handling; A2's fault stands as history.

## P-06 — Single confirming `vpp` read (log `10_vpp_confirm`) — a direct calibration cross-check

**Target:** 12.0 V, sourced from `rig-pins.json`'s `chips.w27c512.vpp_mv` /
`chips.w29c020.vpp_mv` (both `12000`) — the single pot setting for the whole cell.

**Operator's multimeter reading, already on record from `P-01`** (`CELL.md`): "messured vpp to be
exactly 12v" -> **12.0 V**, taken **before** any firmware `vpp` query on this board — a properly
ordered paired measurement (meter first, firmware second), unlike A2's retrospective pairing.

**Command:** `timeout --signal=INT 6 env FIRESTARTER_CONFIG_DIR=/workspaces/.planning/v1.34/config
/workspaces/.v1.34-arms/control/.venv/bin/firestarter -p /dev/ttyACM0 vpp` — exactly one
confirming read, no monitor loop (Standing bench rule 4). `firestarter vpp` has no single-shot
flag (continuous monitor, "Press Ctrl+C to stop."); interrupted via SIGINT (`timeout
--signal=INT`) after the first readings appeared, rc=124 (SIGINT-terminated as expected, not a
tool failure).

**Measured (first reported reading, the confirming value): `VPP: 12.9V, Internal VCC: 5.3V`.**
Subsequent readings in the same brief capture before interrupt: 13.0V / 13.0V / 13.0V / 12.9V.

**`--force used? No`** — no write was attempted; this is a monitor-only read.

### Result: FIRMWARE MATERIALLY OFF THE OPERATOR-MEASURED RAIL — STOPPING PER INSTRUCTION

Firmware-reported VPP (**~12.9-13.0 V**) versus the operator's multimeter reading on this exact
rig (**12.0 V**, taken before this read) differ by **~0.9-1.0 V** — materially off target, and
**above the firmware's own HIGH guard threshold**:

- `firestarter/src/proms/eprom.cpp:713` — HIGH guard fires above `target_mv + 500` = **12.5 V**
  for a 12000 mV target. The measured 12.9-13.0 V reading is **above this threshold**, meaning an
  actual write attempt at this pot setting would very likely trip `MSG_ERR_VPP_HIGH` (a hard
  error, since `FLAG_FORCE` is never set in this project).
- `firestarter/src/proms/eprom.cpp:736` — LOW guard fires below `target_mv * 95%` = 11.4 V; not
  the relevant side here.
- Accepted window for a 12000 mV target: **11.4-12.5 V**. The measured reading is **outside** this
  window, on the high side.

Per the coordinator's explicit instruction for this branch: **no pot adjustment was performed.**
Task 5 (`P-07`, the W27C512 write) was **not** started — proceeding to a write at a VPP reading
already above the guard's own HIGH threshold would risk exactly the failure mode A2's escalation
step 4 recorded ("VPP guard now fires HIGH, unexpectedly"), and the instruction was explicit not
to chase the ADC by re-adjusting the pot (on A2 that drove the real rail to ~11.2 V).

**This is a second, independent VPP ADC finding, same direction as A2's:** A2's uno328pb read
~0.8 V high (firmware 12.5 V vs meter 11.7 V); this Leonardo reads ~0.9-1.0 V high (firmware
12.9-13.0 V vs meter 12.0 V, taken first). Two boards, two ADC chains, both reading high by a
comparable margin, against two independently meter-verified real rails. **Escalated to the
coordinator for a ruling before this cell proceeds** — see the plan-level checkpoint note.

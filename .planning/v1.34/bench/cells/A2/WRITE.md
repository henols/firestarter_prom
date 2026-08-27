# Cell A2 — WRITE.md

Per-position write observations, control arm first then v1.33 — the record Backlog 999.2's
prediction is judged against, not asserted from.

## Position 5 (1 of 4): `A2__control__w27c512`

**Command:** `timeout --signal=INT 165 env FIRESTARTER_CONFIG_DIR=/workspaces/.planning/v1.34/config
/workspaces/.v1.34-arms/control/.venv/bin/firestarter -p /dev/ttyUSB0 write w27c512
reads/A2__control__w27c512/written.bin` (log `12_write_control_w27c512`).

**Ceiling:** 165 s (4x the measured healthy 41.010 s baseline). **Basis: not needed** — the write
did not run anywhere near the ceiling; the app's own internal per-response communication timeout
fired first, at 15.813 s wall-clock. Wrapper exit code: **1** (the process exited on its own with
an error; the external `timeout` wrapper's SIGINT never had to fire — **124 was NOT the exit
code**, so the D-08 ceiling itself was not what ended this attempt, the app's own internal
serial-response timeout was).

**Wall-clock:** 15.813 s (measured by `date +%s.%N` either side of the write command).
**App-reported figure:** `not measured — the write failed before any success line
("Write to {CHIP} successful ({t:.2f}s)") was emitted; the host printed a failure line instead
(quoted below)`.

**The stop point, precisely.** The host prints two separate `tqdm` progress bars for this
operation — one for the protocol's INIT phase, one for MAIN (per `eprom_operations.py`'s
`_execute_phase()`/`_main_phase_simple()` structure, three-phase INIT/MAIN/END protocol per
project `CLAUDE.md`). The **first** bar (INIT) reached **100% (`0x10000/0x10000 bytes`)** — the
full 65536 B image was queued/transferred to the host-side protocol layer without incident. The
**second** bar (MAIN — the actual chip-programming phase) restarted at **0%** and reached only
**`1%|  | 0x0200/0x10000 bytes`** (512 bytes — exactly one Uno-class buffer block,
`_write_block_timeout()`'s own 512 B floor) before the host's serial layer raised a timeout. **The
last progress frame, verbatim:** `1%|          | 0x0200/0x10000 bytes` (appeared twice in
succession in the captured stderr, then no further frames).

**Backlog 999.2 predicted a hang "deterministically on the FIRST program block."** What was
**observed** here: the MAIN phase's progress stopped at exactly the first block boundary
(0x0200 = 512 B), matching that prediction's block-position claim precisely. It is **not** a
hang without termination, though — the app's own internal per-response read timeout
(`serial_comm.py get_response()`, `DEFAULT_RESPONSE_TIMEOUT`/the firmware-advertised MAIN-phase
budget) fired and the process exited cleanly with an error, well before the external 165 s
D-08 ceiling was ever approached. This is a faster, more precisely bounded failure than the
raw "it hung" description — a real difference worth recording, not softened into "the same
thing happened."

**Exactly what the host printed** (stdout, in full):
```
Connecting...Connecting... OK      
Writing /workspaces/.planning/v1.34/bench/cells/A2/reads/A2__control__w27c512/written.bin to W27C512
Timeout waiting for a response from /dev/ttyUSB0.
Communication error during WRITE: Timeout waiting for a significant response from /dev/ttyUSB0.
Write to W27C512 failed.
```
(stderr held only the two `tqdm` progress bars quoted above; no separate error text on stderr.)

**Read attempted anyway** (the READ path is predicted to work on this board even after a failed
write): `firestarter -p /dev/ttyUSB0 read w27c512 reads/A2__control__w27c512/run_01.bin` (log
`13_read_control_w27c512`), rc=0, "Read complete (14.60s)". The READ path **did** work, confirming
that half of the 999.2 prediction too.

**What the read-back actually shows (a measurement, not an inference):** of the 65536 B read, 431
bytes are non-`0xFF`, and every one of them is **contiguous from offset 0x0000 through 0x01AE**
(431 bytes, entirely inside the first 512 B block) — the remaining 65105 bytes, including all of
the second block onward, read back fully erased (`0xFF`). This is a precise, on-chip measurement
of exactly how far the MAIN phase got before the timeout: partway through programming the first
block (431 of 512 bytes, ~84%), never reaching the second block. This is a stronger, more exact
statement than "stopped on the first block" alone.

**Judged verdict** (`judge_wrv.py`, `WRV-VERDICT_A2__control__w27c512.json`): `sha_verdict_judged
== "mismatch"` (expected — the write never completed); `read_count == 1`; `distinct_read_shas ==
1`; `size_violations == []`; `app_verdict_unjudged == 0` (the **read** command's own exit code —
the read mechanically succeeded even though the bytes it returned don't match the intended
image); `verdict_disagreement == true` — the app's read-exit-code (0, success) disagrees with the
judged SHA verdict (mismatch), exactly the kind of disagreement D-11/the Recording discipline says
is itself a finding, never resolved by preferring one field over the other. **Outcome:
`skipped-with-reason`** (computed by `append_evidence.py`, never hand-set).

**Comparison basis:** 15.813 s elapsed against the measured healthy 41.010 s W27C512 baseline —
the failure is roughly 2.6x **faster** than a healthy write, not slower; it never got close to
using its 165 s ceiling.

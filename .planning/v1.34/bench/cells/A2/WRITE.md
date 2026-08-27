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

## Position 6 (2 of 4): `A2__control__w29c020`

**The first algorithm-`0x05` (5V page-write) program ever attempted on this board.** Explicitly
NOT predictable from position 1's result — a materially different electrical/firmware path
(page-write with polled verify, not the 27C-family program-pulse path) — and it was not
pre-judged either way before running.

**Command:** `timeout --signal=INT 392 env FIRESTARTER_CONFIG_DIR=/workspaces/.planning/v1.34/config
/workspaces/.v1.34-arms/control/.venv/bin/firestarter -p /dev/ttyUSB0 write w29c020
reads/A2__control__w29c020/written.bin` (log `17_write_control_w29c020`).

**Ceiling:** **391.748 s (derived: 4x A1's measured control-arm W29C020 wall-clock, 97.937 s** —
`161-03-SUMMARY.md`). Not the 165 s W27C512 ceiling, not the 600 s absolute fallback (A1's own
control-arm W29C020 completed, so a derivation exists and is used). **Not needed** — the write
did not run anywhere near this ceiling either; wall-clock **4.019 s**, wrapper exit code **1**
(never 124 — the ceiling never fired here, same fact-pattern as position 1 but a much shorter
elapsed time).

**Wall-clock:** 4.019 s. **App-reported figure:** `not measured — the write failed before any
success line was emitted`.

**A DIFFERENT failure mechanism from position 1 — record which, do not conflate.** Position 1
ended in the *host's* own serial-response timeout (no reply from the firmware at all). This
position ended in a **firmware-reported error**, relayed by the host: the firmware's own verify
(data-poll) loop timed out and reported the last value it actually read. **Exactly what the host
printed** (stdout, in full):
```
Connecting...Connecting... OK      
Writing /workspaces/.planning/v1.34/bench/cells/A2/reads/A2__control__w29c020/written.bin to W29C020
ERROR: Timeout verifying 0x15 at 0x00007f (got 0x13)
Programmer error during WRITE: Timeout verifying 0x15 at 0x00007f (got 0x13)
Write to W29C020 failed.
```
(stderr held only the `tqdm` byte-progress frames; **last progress frame, verbatim:**
`0%|          | 0x0200/0x40000 bytes` — 512 bytes into the 262144 B device, appeared twice
before the error. `0x40000` = 262144.)

**Stop point, precisely:** the firmware reports the verify failure at device offset **0x00007f**
(127 decimal), expecting to see `0x15` (this position's mask byte) written, and instead still
reading `0x13` after its own internal poll gave up. `0x13` (19 decimal) is **A1__v133__w29c020`'s
own mask** — this is the same physical W29C020 chip previously used in cell A1, and byte 0x7f had
not actually been reprogrammed to this position's value at the point the verify gave up.

**Read attempted anyway.** Unlike position 1, the READ path did **NOT** work cleanly here:
`firestarter -p /dev/ttyUSB0 read w29c020 reads/A2__control__w29c020/run_01.bin` (log
`18_read_control_w29c020`), rc=**1**, wall-clock 43.945 s, host printed `Timeout waiting for a
response from /dev/ttyUSB0. Communication error during READ: Timeout waiting for a significant
response from /dev/ttyUSB0.` — a genuinely different observation from position 1's "the READ path
works on this board" statement; it is **not** re-asserted here, it is contradicted by this
position's own measurement. The read produced a **partial** file: **113152 of 262144 bytes**
before it, too, timed out.

**What the partial read-back shows (a measurement):** of the 113152 bytes actually returned, only
292 are `0xFF` (blank) — the overwhelming majority (112860 bytes) are non-blank, i.e. this is
**not** simply an erased chip. Byte at offset **0x7f reads `0x13`** in this read-back — an exact
match to the firmware's own quoted "got 0x13," an independent on-chip confirmation of the same
fact the error message reported. Diffing the partial read against a freshly-generated copy of
**`A1__v133__w29c020`'s own image** (mask `0x13`/19, the value the stop-point byte matches)
shows a partial correlation (~65%, 74117/113152 bytes identical) — consistent with, but not
conclusively proving, that this physical chip still carries substantial residual content from
its earlier use in cell A1, since this position's own write essentially never got past its first
page and the read itself was also cut short by a communication timeout (which could itself
corrupt the transferred bytes independent of the chip's actual content). **Recorded as an
observation for Phase 165, not asserted as a proven root cause.**

**Judged verdict** (`judge_wrv.py`, `WRV-VERDICT_A2__control__w29c020.json`): `sha_verdict_judged
== "mismatch"`; `size_violations` non-empty (`run_01.bin` is 113152 bytes, not 262144);
`app_verdict_unjudged == 1` (the read command's own exit code, a failure) — **agrees** with the
judged mismatch this time (`verdict_disagreement == false`), unlike position 1 where the two
disagreed.

**Comparison basis:** neither this write's 4.019 s nor this read's 43.945 s (partial, failed) is
compared against A1's healthy 97.937 s write / 73.344 s read baselines as if they were the same
kind of measurement — both of A2's figures here are failures, not completions, and are recorded
as such rather than forced into a like-for-like comparison with a completed baseline.

# Phase 145 — W27C512 `0x07` Bench Validation Log

> Nothing in this record is fabricated. A tooling-blocked reading is recorded as `not measured`
> with its blocking reason stated on the same line. This record recognizes exactly two outcome
> states: **validated**, or **skipped-with-reason**. Anything that is not a clean pass is a
> **fail**; anything not attempted is a skip. There is no third state — the word `inconclusive`
> is not a valid outcome in this document, and the only place it appears at all is this sentence,
> denying that it exists. This taxonomy (D-14) is fixed here, before any run, precisely so that a
> partial result cannot later be argued into the friendlier bucket.

**Session start:** NOT YET RUN
**Operator:** Henrik (henrik@predictly.se)
**Driver:** Claude Code (GSD executor; operator authorizes every spend; drives the serial/CLI side
per D-19, the operator owns the physical side)
**Dispatch mode:** This phase was dispatched via `/gsd-execute-phase 145` with **no** `--auto` flag
and **no** `--chain` flag, and `check auto-mode` resolved `false`. Per D-20, auto-modes
**auto-approve** `human-verify` gates, and `autonomous: false` on a plan's frontmatter is **not**
self-protecting by itself — every operator gate in this phase is real, and this line is the
record's own standing assertion of that.

---

## Verification map bindings

`145-VALIDATION.md`'s "Task ID" / "Plan" columns are a pre-planning guess and are **superseded**
by this table. Rows below are in the same order as `145-VALIDATION.md`'s per-task verification
map, each bound to a concrete plan-and-task id (17 distinct `145-0N Task M` bindings across the 27
rows; several rows bind to more than one task where the same check recurs across cycles).

| # | Gate | Requirement | Secure behavior | Test type | Bound to |
|---|------|-------------|------------------|-----------|----------|
| 1 | Gate 0 | BENCH-03 | no `support_status` mutation across v1.31 | automated | 145-02 Task 1 |
| 2 | Gate 0 | BENCH-03 | generator inputs unchanged | automated | 145-02 Task 1 |
| 3 | Gate 0 | BENCH-03 | write-locus lock still holds | automated | 145-02 Task 1 |
| 4 | Gate 0 | BENCH-03 | histogram unchanged (736 supported / 9 adapter-required / 1 protocol-not-implemented / 746 total) | automated | 145-02 Task 1 |
| 5 | Gate 0 | BENCH-02 | `0x08` skip names part + 60/64 → 0/64 + FUT-08 + the "NOT inferred" sentence | source assertion | 145-02 Task 2 |
| 6 | Gate 0 | BENCH-02 | `0x0B` skip names part + 22.4 V DMM / 23.9 V firmware + parked graduation + the "NOT inferred" sentence | source assertion | 145-02 Task 3 |
| 7 | Gate 0 | BENCH-01 | three distinct address-attributable 64 KiB images + one 4 KiB pulse image | automated | 145-01 Task 2 |
| 8 | Gate 1 | BENCH-01 | image under test identified by commit, not version string | hardware | 145-03 Task 2 |
| 9 | Gate 1 | BENCH-01 | zero flash growth vs `size_baseline.json` | automated | 145-03 Task 2 |
| 10 | Gate 1 | BENCH-01 | controller/port identity verified this session, not assumed | hardware | 145-03 Task 2 |
| 11 | Gate 1 | BENCH-01 | seated part is Winbond `0xda08`, not ST `0x203d` | hardware | 145-03 Task 3 |
| 12 | Gate 1 | BENCH-01 | VPP in band; `--force` not used (D-17) | human-verify + hardware | 145-04 Task 1, 145-04 Task 2 |
| 13 | Gate 1 | BENCH-01 | pre-write content preserved before first erase | hardware | 145-04 Task 1 |
| 14 | Gate 1 | BENCH-01 | D-03 settled on the bench, not assumed | hardware | 145-04 Task 3 |
| 15 | Gate 2 ×3 | BENCH-01 | 64 KiB write completes, firmware verify passes | hardware | 145-05 Task 2 (cycle 1); 145-06 Task 1, 145-06 Task 2 (cycles 2, 3) |
| 16 | Gate 2 ×3 | BENCH-01 | oracle 1 — second firmware-side compare | hardware | 145-05 Task 2 (cycle 1); 145-06 Task 1, 145-06 Task 2 (cycles 2, 3) |
| 17 | Gate 2 ×3 | BENCH-01 | oracle 2 — independent SHA compare (D-06), recorded on its own line | automated | 145-05 Task 2 (cycle 1); 145-06 Task 1, 145-06 Task 2 (cycles 2, 3) |
| 18 | Gate 2 ×3 | BENCH-01 | read stability per cycle (D-07) | hardware | 145-05 Task 2 (cycle 1); 145-06 Task 1, 145-06 Task 2 (cycles 2, 3) |
| 19 | Gate 2 | BENCH-01 | erase actually fired (D-03 corroboration) | derived | 145-06 Task 3 |
| 20 | Gate 2 | BENCH-01 | 3/3 byte-exact on both oracles (D-09); any re-seat recorded twice | derived | 145-06 Task 3 |
| 21 | Gate 2 | BENCH-01 | no `--force`, anywhere (D-17) | source assertion | 145-06 Task 3 |
| 22 | Gate 2 | D-11 / 143 H4 | long write survives the advertised budget (free evidence) | derived | 145-05 Task 3 |
| 23 | Gate 2 | D-10 Claim A | ≥1 bar frame at a non-multiple-of-1024 position | automated | 145-05 Task 3 |
| 24 | Gate 3 | D-10 Claim B | ≥2 distinct positions inside the same `n // 1024` bucket | automated | 145-07 Task 2 |
| 25 | Gate 3 | D-12 | `--pulse-us` exercised on silicon above the 4687 µs residual-gap threshold | hardware | 145-07 Task 2 |
| 26 | Gate 3 | D-12 | A1 per-pulse overhead measured | derived | 145-07 Task 3 |
| 27 | Gate 3 | D-10 eyes-on | operator confirms a smoothly moving bar, not an end-burst | human-verify | 145-08 Task 1 |

---

## Gate 0 — Off-bench evidence (no hardware)

Everything in this gate is reachable with zero hardware attached. Per Pattern 1 (RESEARCH), it is
finished — including BENCH-02's two skip records and the BENCH-03 re-measurement — before the
board is even connected, so a D-13 halt on the first genuine `0x07` failure still leaves two whole
requirements discharged.

### Instrument inventory and tripwire baseline
NOT YET RUN — filled by `145-01` Task 3 (the `extract_frames.py` self-test outcomes and the
pre-bench firmware/host tripwire pass counts).

### Write images

Four images, generated in the meta repo only:

| File | Size | Mask | SHA-256 |
|---|---|---|---|
| `images/img1.bin` | 65536 B | `0x00` | `f72489604bfe917db7ee505e4d674576b2905a418e8dc55372b78dcab3e34e3a` |
| `images/img2.bin` | 65536 B | `0xFF` | `b566c7a0319cc37051ec9c92bc1faef81f75e3740c7c6c8864778a549624fd96` |
| `images/img3.bin` | 65536 B | `0x5A` | `74c359c8d8668fdc5778270d61cc3fbef55a1027999f20c5798a54bf0f6aea01` |
| `images/img_4k_pulse.bin` | 4096 B | `0x3C` | `6db951cca6af4c56524f3ad01bbcd5658c44ea6b73eb0dca9469b9e787ca448a` |

(Digests recomputed from disk with `sha256sum`, not copied from the generator's own printed
output; the full manifest is `SHA256SUMS.txt` — see the SHA manifest section below.)

**Generator:** `.planning/phases/145-bench-validation/images/gen_addr_image.py` — meta-repo bench
tooling authored under this phase directory, explicitly NOT inside `firestarter/` or
`firestarter_app/` (D-16). It implements the word-stamped address recipe: the byte at offset `N`
is the low byte of `N` when `N` is even, the high byte of `N` when `N` is odd, XORed with a
per-image mask, so each aligned 2-byte word literally stamps its own 16-bit address.

**Pairwise distinctness (measured):** all three 64 KiB pairs — img1/img2, img1/img3, img2/img3 —
differ in **65536 of 65536 bytes**. D-05's "different image each cycle" requirement is maximally
satisfied; rewriting the same bytes over an unerased chip could never pass any of these cycles
trivially.

**Erase-oracle figures (measured):** bytes needing at least one `0 → 1` bit transition are
**65408 of 65536 (99.8 %)** going from cycle 1 (img1) to cycle 2 (img2), and **59392 of 65536
(90.6 %)** going from cycle 2 (img2) to cycle 3 (img3). A clean cycle-2 (or cycle-3) PASS is
therefore **positive proof the erase actually fired**: a silently no-op erase would leave those
bytes unprogrammable (a program pass cannot clear a bit already at `0`) and the write would fail
with `MSG_ERR_MAX_PULSES` rather than report success.

**`0xFF` byte counts (measured):** img1 = 128, img2 = 384, img3 = 128. Firmware
(`eprom.cpp:407`, `if (expected == 0xFF) continue;`) skips a byte whose expected value is `0xFF`
without issuing a pulse — this record does not claim all 65536 bytes were individually pulsed.
Those bytes remain covered by `VERIFY_PER_PULSE_PLUS_FINAL`'s final full-block read pass, so there
is no verification coverage hole, only a pulse-count honesty note.

**Address-attributability, worked example (simulated A8-stuck-low, img1/mask `0x00`):** simulating
address line A8 (bit 8 of the 16-bit address) stuck low over the full 65536-byte space produces
16384 mismatches; the first is at offset `0x0101`, observed byte `0x00`. Un-masking (mask `0x00`
for img1) leaves `0x00`; the offset is odd, so the stamp is the *high* address byte, meaning the
byte read back belongs to an address whose high byte is `0x00` — i.e. address `0x0001` — naming
**A8** as the aliased line. This is the property `gen_test_image.py`'s pseudo-random bytes do not
have: a mismatch's *value*, not just its offset, decodes to a source address (the same distinction
that root-caused Phase 97's pin-31 defect).

### BENCH-03 `support_status` invariance
NOT YET RUN — filled by `145-02` Task 1 (chip-database diff, generator-inputs diff, write-locus
lock, histogram recount).

### BENCH-02 `0x08` (AM27C020) disposition
NOT YET RUN — filled by `145-02` Task 2 (skipped-with-reason record citing Phase 99's 60/64 → 0/64
and FUT-08, with the explicit "NOT inferred from the `0x07` result" sentence).

### BENCH-02 `0x0B` (M2716/M2732) disposition
NOT YET RUN — filled by `145-02` Task 3 (skipped-with-reason record citing Phase 79's 22.4 V DMM /
23.9 V firmware VPE reading and the parked graduation, with the same "NOT inferred" sentence).

**Gate 0 verdict:** NOT YET RUN

---

## Gate 1 — Identity, image under test, VPP, D-03 pre-flight

| Field | Value | Source |
|---|---|---|
| Controller identity | NOT YET RUN | `firestarter fw` |
| Port | NOT YET RUN | `firestarter fw` |
| Hardware revision (reported) | NOT YET RUN | `firestarter hw` |
| Shield silkscreen (operator eyes-on) | NOT YET RUN | operator |
| Seated chip (operator confirmed) | NOT YET RUN | operator |
| Part expendable (operator confirmed) | NOT YET RUN | operator |
| R1 readback | NOT YET RUN | `firestarter config` |
| R2 readback | NOT YET RUN | `firestarter config` |
| Firmware version string | NOT YET RUN | `firestarter fw` |
| Firmware commit under test | NOT YET RUN | `git -C /workspaces/firestarter rev-parse HEAD` |
| Firmware working tree clean | NOT YET RUN | `git -C /workspaces/firestarter status --porcelain` |
| Flash bytes measured | NOT YET RUN | `pio run -e leonardo --target size` |
| avrdude verified byte count | NOT YET RUN | upload log |
| VPP target | NOT YET RUN | plan (D-17) |
| VPP confirmation read | NOT YET RUN | `timeout -s INT N firestarter vpp` (single sample) |
| `--force used?` | NOT YET RUN | source assertion |
| Dispatch mode | No `--auto`, no `--chain` (see header block; D-20) | this record |

**D-18 version-string caveat** (next to the Firmware version string row): a correctly reflashed
v1.31 image is expected to report `3.0.0b17`, which is byte-identical to the v1.31 branch's own
fork point `3085084` and reads *older* than `origin/beta`'s `3.0.0b18` — so the version string
identifies nothing. The firmware commit under test plus the avrdude-verified byte count are the
only discriminators; this row's `NOT YET RUN` becomes a fact only once actually read from a
flashed board, never inferred from the version string.

### Reflash proof
NOT YET RUN — `pio run -t upload -e leonardo` from a clean, named commit; expect avrdude to report
26906 bytes written and verified (144 H7's zero-growth band, 1766 B headroom, 0 B band).

### VPP
NOT YET RUN — the operator states the target, waits, and takes **one** confirming
`timeout -s INT N firestarter vpp` read; never a live monitor loop (D-17, operator preference).

### Pre-write chip preservation
NOT YET RUN — `firestarter read W27C512 prewrite.bin`, digest recorded into `SHA256SUMS.txt`.

### D-03 erase-capability pre-flight
NOT YET RUN — determine, on this bench, whether plain `write` erases the seated W27C512 before any
Gate 2 cycle is spent. If it does not, the fallback is a pure 1→0 program proof; `-b`/`--skip-erase`
is never used as a workaround (D-03).

**Gate 1 verdict:** NOT YET RUN

---

## Gate 2 — Three 64 KiB cycles (authorized spend)

**Operator authorization:** NOT YET RUN — verbatim quote recorded here before the first cycle 1
byte is spent.

### Cycle 1
NOT YET RUN — this subsection is re-titled with the exact command line
(`firestarter -v write W27C512 img1.bin`) once run, per the command-line-as-heading convention.

### Cycle 2
NOT YET RUN — re-titled with the exact command line (`firestarter -v write W27C512 img2.bin`)
once run.

### Cycle 3
NOT YET RUN — re-titled with the exact command line (`firestarter -v write W27C512 img3.bin`)
once run.

### Progress-frame evidence (D-10 Claim A)
NOT YET RUN — frame extraction over the three cycles' raw stderr captures, counting only frames
after the last bar restart (Pitfall 6): at least one frame at a position that is not a multiple of
1024.

### D-09 re-seat ledger
At most one re-seat is allowed across the whole Gate 2 spend, and it must be attributable to a
named physical cause (re-seat, chip-id mismatch, VPP out of band). If it happens, both the
discarded failure and its one re-run are recorded here — never a quiet retry. NOT YET RUN.

**Gate 2 verdict:** NOT YET RUN

---

## Gate 3 — `--pulse-us 4688` (D-10 Claim B, D-12)

Gate 3 is **required conditional on Gate 2 passing**. If Gate 2 fails, Gate 3 is recorded here as
**not-reached**, with the reason, rather than silently omitted.

**Operator authorization:** NOT YET RUN — verbatim quote recorded here before this run.

### Run
NOT YET RUN — `firestarter write W27C512 img_4k_pulse.bin --pulse-us 4688`, expected to cross the
4687 µs residual-gap threshold and print the mandatory pulse-override provenance line.

### Claim B
NOT YET RUN — ≥2 distinct positions inside the same `n // 1024` bucket (D-10 as literally worded).

### A1 per-pulse overhead
NOT YET RUN — `(t2 - t1)/N` vs `P2 - P1` across two pulses over the same byte count; error bars
recorded honestly rather than rounded away.

### Operator eyes-on
NOT YET RUN — operator statement, recorded verbatim, on whether the bar moved smoothly rather than
arriving in an end-burst.

**Gate 3 verdict:** NOT YET RUN

---

## SHA manifest

Every digest for this phase — every generated image and every hardware read-back — lives in one
place: `.planning/phases/145-bench-validation/SHA256SUMS.txt`. No hash is written inline anywhere
in this narrative; a reader runs `sha256sum -c SHA256SUMS.txt` from the phase directory to verify
everything at once.

## Not measured

(Empty at this point. Populated only if a reading turns out to be genuinely tooling-blocked, each
entry naming the reading and its blocking reason — see Phase 99's Program-window VPP-under-load
row for the house precedent.)

## Carry-forward hand-offs with no v1.31 owner

(Empty at this point.) Phase 146 is docs-and-claims only and cannot run a bench. Anything this
phase does not discharge — most plausibly D-12's `--pulse-us`-on-silicon item or the A1 overhead
measurement, if Gate 2 does not clear cleanly enough to reach Gate 3 — has no v1.31 owner and is
recorded here rather than silently dropped.

---

## VERDICT: NOT YET RUN

**Session end:** NOT YET RUN

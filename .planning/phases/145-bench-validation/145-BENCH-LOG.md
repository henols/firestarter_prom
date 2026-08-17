# Phase 145 — W27C512 `0x07` Bench Validation Log

> Nothing in this record is fabricated. A tooling-blocked reading is recorded as `not measured`
> with its blocking reason stated on the same line. This record recognizes exactly two outcome
> states: **validated**, or **skipped-with-reason**. Anything that is not a clean pass is a
> **fail**; anything not attempted is a skip. There is no third state — the word `inconclusive`
> is not a valid outcome in this document, and the only place it appears at all is this sentence,
> denying that it exists. This taxonomy (D-14) is fixed here, before any run, precisely so that a
> partial result cannot later be argued into the friendlier bucket.

> **READ THIS FIRST — THIS RECORD HAS TWO SESSIONS.** Session 1 (2026-08-16) ran Gates 0 and 1,
> then HALTED at Gate 2 cycle 1. Session 2 (2026-08-17) resumed after a debug session found and
> fixed a **firmware defect**, and therefore runs against a **DIFFERENT firmware image**. Session
> 1's text below is left exactly as written — including its `VERDICT: HALTED` — because rewriting
> it would launder the phase's history. Everything session 2 supersedes is marked with an explicit
> pointer to **"## Resumed session (2026-08-17)"** at the bottom of this file, which is where the
> superseding facts live. Session 1's Gate 1 firmware-identity rows in particular **no longer
> describe the image any session-2 result was produced by.**

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

This phase adds **no automated test**. D-16 forbids source changes and BENCH-01/BENCH-02 are
irreducibly hardware- and operator-gated, so the two suites below are run as **regression
tripwires** — evidence that nothing this phase touches has broken either repo's existing test
suite — never as requirement evidence. Requirement evidence is this record and its artifacts.

**Frame-extraction instrument:** `.planning/phases/145-bench-validation/tools/extract_frames.py`
— meta-repo bench tooling authored under this phase directory, explicitly NOT inside
`firestarter/` or `firestarter_app/` (D-16). It parses a raw tqdm stderr capture
(`logs/write_cycleN.stderr.raw`), keeps only the last bar segment (the write bar, discarding
INIT-phase blank-check frames per Pitfall 6), and reports per-block frame positions.

**Self-test — both outcomes observed (command: `python3 tools/extract_frames.py --selftest`,
exit 0):**

| Leg | Fixture | `segments` | `selected_segment` | `positions` | `intra_block_frames` | `blocks_with_multiple_updates` | `block_updates` | Verdict |
|---|---|---|---|---|---|---|---|---|
| POSITIVE | 2-segment, write bar has one intra-block frame at 1280 | 2 | 2 | `[0, 1024, 1280, 2048]` (4096 confirmed absent) | 1 | 1 | `{1: 2}` (`block 1 has 2 updates`) | `SELFTEST: POSITIVE PASS` |
| NEGATIVE | 2-segment, write bar has only boundary frames | 2 | 2 | `[0, 1024, 2048, 3072]` | 0 | 0 | `{}` | `SELFTEST: NEGATIVE PASS` |

All expected-versus-observed fields matched on both legs (no diff lines emitted); the script
exited 0. `grep -c "PASS"` on the self-test output is 2.

**Pre-bench tripwire baseline:**

| Check | Command | Result | RESEARCH baseline | Match |
|---|---|---|---|---|
| Firmware porcelain (precondition, RQ-9) | `git -C /workspaces/firestarter status --porcelain` | empty (0 lines), both immediately before and immediately after the suite run below | empty | yes |
| Firmware suite | `cd /workspaces/firestarter && python3 -m pytest tests/ -q -o addopts=` | **312 passed** in 19.61s, 0 failed | 312 passed | yes |
| Host sibling-porcelain subset | `cd /workspaces/firestarter_app && python3 -m pytest tests/test_py32_flash_map_host.py tests/test_cap03_ack_layout_parity.py tests/test_py32_asset_name_host.py -q -o addopts=` | **38 passed**, 0 failed | 38 passed | yes |

Both commands were issued with `-o addopts=` cleared (the repos' own `addopts` is `-ra -q`, and
doubling `-q` suppresses the summary count line — Pitfall 10); the count line was visible in both
captured outputs. `firestarter_app`'s own working tree carries 8 pre-existing untracked entries
(no porcelain assertion exists on that repo directly; the subset above asserts the *sibling*
firestarter checkout's porcelain instead), unrelated to this phase and unchanged by it.

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

Re-measured at the tip, all four legs run this session from `/workspaces/firestarter_app`. Nothing
was regenerated and `tools/build_db.py` was not invoked — the requirement is that nothing changed,
and regenerating would be the change. This is a re-measurement, not a first discovery: D-15 already
established the diff was empty at discussion time; this record re-confirms it at execution time.

**Leg 1 — D-15's mandated whole-milestone diff, base confirmed rather than assumed.**
```
$ git merge-base HEAD origin/beta
4d18b645ab18a2d2465f0f623062e9249eb24132
```
The confirmed merge-base matches D-15's recorded base exactly — measured, not assumed.
```
$ git diff 4d18b645..HEAD -- firestarter/data/chip_database.json | wc -c
0

$ git diff --stat 4d18b645..HEAD -- firestarter/data/chip_database.json
(no output — zero rows)
```
Zero bytes of diff and zero stat rows across the **whole** v1.31 range from the app's branch base to
HEAD — not merely across this phase's own commits (per D-15's explicit instruction).

**Leg 2 — the generator inputs are also unchanged.**
```
$ git diff --stat 4d18b645..HEAD -- tools/build_db.py tools/extra_chips.json tools/infoic.xml | wc -c
0
```
This matters because `chip_database.json` is **generated**: an unchanged database sitting on top of
drifted generator inputs would be a latent change waiting for the next regeneration. This leg closes
that gap — the inputs are exactly as unchanged as the output they produce.

**Leg 3 — the mechanism lock.**
```
$ python3 tools/check_no_community_support_status_write.py; echo "exit=$?"
PASS: scanned ../firestarter/diagnostic_report.py, parse_devtest_issue.py; 0 support_status writes (sole write locus stays tools/build_db.py)
exit=0
```
This is an AST gate that denies any `support_status` **assignment target**
(`ast.Assign`/`ast.AnnAssign`/`ast.AugAssign`, attribute form or dict-subscript form) in its two scan
targets, `firestarter/diagnostic_report.py` and `tools/parse_devtest_issue.py`, and fails closed if
either scan target is missing from disk. The sole sanctioned write locus is `tools/build_db.py`.
D-15's proof **composes with** this lock rather than duplicating it: the lock already runs
automatically under `pytest tests/` via `tests/test_check_no_community_support_status_write.py` on
every suite invocation; this leg is a direct, standalone re-run of that same gate at the tip.

**Leg 4 — the value histogram, a positive statement rather than an absence.**
```
$ sha256sum firestarter/data/chip_database.json
3befbaad7bbb88307abd94db0447ad78e847c40f3c96be7751f5b87a1e913479  firestarter/data/chip_database.json

$ python3 -c "import json,collections; d=json.load(open('firestarter/data/chip_database.json')); c=collections.Counter(ic.get('support_status') for ics in d.values() for ic in ics); print('total', sum(c.values())); [print(k, v) for k,v in c.most_common()]"
total 746
supported 736
adapter-required 9
protocol-not-implemented 1
```
All four figures and the digest match the value expected from discussion time exactly.

**Caveat — three benign textual mentions in the range, each verified by grepping the actual diff
rather than restated from RESEARCH.** `git diff 4d18b645..HEAD` contains exactly three lines
mentioning the string `support_status`, none a value change:
```
$ git diff 4d18b645..HEAD -- tests/golden/chip_database_field_inventory.json | grep -n support_status
31:+      "support_status": 746,
82:+    "support_status",

$ git diff 4d18b645..HEAD -- tests/test_write_response_budget.py | grep -n support_status
12:+EPROM_STD, ``support_status: supported``). Already the shared "non-0x0D"
```
Two are in `tests/golden/chip_database_field_inventory.json` — a per-key **occurrence count** of
`746` (matching Leg 4's total chip count, not a support-status value) and the key's appearance in a
key list — and one is in `tests/test_write_response_budget.py`, a docstring quoting
`` support_status: supported ``. A full unscoped `git diff 4d18b645..HEAD | grep -c support_status`
returns exactly `3`, confirming no fourth mention exists anywhere in the range.

**Scope statement — single-repo by construction.**
```
$ cd /workspaces/firestarter && grep -rc "support_status" src/ include/ scripts/ 2>/dev/null | grep -v ":0$"
(no output — zero hits)
```
Run read-only from `/workspaces/firestarter`. The firmware repo carries no `support_status`
anywhere across `src/`, `include/` or `scripts/`, so BENCH-03 is single-repo by construction: only
`firestarter_app` can possibly move this value, and Leg 1 already proves it did not.

**BENCH-03 verdict: validated** — four independent legs (the whole-range diff, the generator-inputs
diff, the mechanism-lock re-run, and the value histogram), all re-measured at the tip this session,
none discovered for the first time here.

### BENCH-02 `0x08` (AM27C020) disposition

**Missing part, stated as the reason for the skip:** AM27C020, protocol `0x08`. No AM27C020 is on
the bench this session (operator, this phase) — that is the entire and sufficient reason this
protocol is skipped rather than validated. No measurement is taken here and no hardware is touched;
every number below is cited from Phase 99, not re-derived.

**Last known bench state, with its numbers and its source — Phase 99, 2026-07-01, Leonardo + RURP
Rev 2.0, firmware commit `35706c2`**
(`.planning/phases/99-bench-ledger-graduation-gate-evidence-ledger-update/99-03-BENCH-LOG.md`):

- **Write #1** — `firestarter write AM27C020 writeA.bin -a 0x1da00 -b` → RC **1**,
  `Failed to write memory, 0x01da00, retries: 20, bad bytes: 4`. Read-back of the region
  `0x1da00..+64`: **60 of 64 bytes byte-exact**. The failing bytes were the **first four**, at
  `0x1da00` through `0x1da03`, which stayed `0xFF` (unprogrammed).
- **Read stability between the two writes** — `dev consistency-check AM27C020 --runs 3` →
  **PASS at N=3, one distinct SHA** (`4b192bba…a418`) — the partial-program state was real and
  stable, not a read glitch.
- **Write #2** (confirmatory, different region) — `firestarter write AM27C020 writeA.bin -a
  0x16600 -b` → RC **1**, `Failed to write memory, 0x016600, retries: 20, bad bytes: 64`. Read-back
  of the region `0x16600..+64`: **0 of 64** — the entire region stayed `0xFF` (total program
  failure).
- **Idle VPP**, both before write #1 and after write #2: **12.9 to 13.0 V**, Internal VCC 5.5 V —
  inside the 12.75 V ± 0.25 V band.
- **NOT MEASURED** — program-window VPP at socket pin 1. Blocked because the held-rail DMM proxy is
  defeated by DTR-reset-on-close (the Phase-97 tooling gap, standing across this project). Program-
  window droop under load is the leading hypothesis for the marginal/unreliable programming shape
  above, and it was never instrumented.
- **Carry-forward id: `FUT-08`.**

**D-14's judgement, stated plainly.** Under this phase's two-state taxonomy the Phase-99 shape —
60 of 64 byte-exact, then 0 of 64 — is a **fail**, not a qualified pass. The taxonomy was fixed
before any run in this phase precisely so that a partial result of exactly this shape cannot be
argued into the friendlier bucket after the fact.

**D-02's denial.** This disposition is **NOT inferred from the `0x07` result**. No `0x08`
measurement was taken this phase; the numbers above are Phase 99's, cited, not re-derived.

**BENCH-02 `0x08` verdict: skipped-with-reason** — missing part: AM27C020.

### BENCH-02 `0x0B` (M2716/M2732) disposition

**Missing parts, stated as the reason for the skip:** M2716 and M2732, protocol `0x0B`. Neither
part is on the bench this session (operator, this phase) — that is the entire and sufficient
reason this protocol is skipped rather than validated. No measurement is taken here and no
hardware is touched; every number below is cited from Phase 79, not re-derived.

**Last known bench state, with its numbers and its source — Phase 79, rail-corrected
2026-06-23, Leonardo + RURP Rev 2.0, firmware `3.0.0b8`, chip OUT, pot at maximum, R1/R2 at
`270000`/`44000`** (`.planning/phases/79-25v-nmos-ceiling-raise/79-01-SUMMARY.md`,
`.planning/phases/79-25v-nmos-ceiling-raise/79-02-SUMMARY.md`):

- **VPE = 22.4 V by operator DMM** (treated as authoritative) **against 23.9 V reported by
  `firestarter vpe`** — both at max pot, roughly 90 % of the rated 25 V.
- **VPP on the same run:** roughly 15 to 19 V by operator DMM against **18.7 V** reported by the
  firmware on the dropped path.
- The strict **≥ 25 V bar was NOT CLEARED** at this reading, and was then **retired by operator
  override** (79-CONTEXT D-07). After the override, the four NMOS chips (INTEL M2716/M2716M,
  INTEL 2732/2732A/M2732/M2732A, SGS-THOMSON ETC2716/M2716, ST ETC2716/M2716) graduate to
  `supported` **best-effort**: the firmware warns under-voltage (22.4 V against a 23.75 V
  threshold, 95 % of the rated 25 V) and proceeds; over-voltage stays blocked as the damage
  boundary.
- **Caveat:** the firmware ADC measures the regulator **rail** at 23.9 V, not the
  socket-delivered **pin voltage** at 22.4 V — the two figures are measuring different things,
  and neither supersedes the other.
- **Definitive proof** — a real write plus an independent read-back SHA — is Phase 79's plan
  `79-03`, **deferred until a physical chip is on hand**. The graduation is **parked** exactly
  there.

**D-02's denial.** This disposition is **NOT inferred from the `0x07` result**. No `0x0B`
measurement was taken this phase; the numbers above are Phase 79's, cited, not re-derived.

**BENCH-02 `0x0B` verdict: skipped-with-reason** — missing parts: M2716, M2732.

**Gate 0 verdict:** Cleared, zero hardware touched. Four items complete: the instrument inventory
and tripwire baseline (`145-01` Task 3 — the frame-extraction self-test passed both outcomes, the
firmware suite ran 312 passed, and the host sibling-porcelain subset ran 38 passed); the four
address-attributable write images plus their digest manifest (`145-01` Task 2 —
`img1.bin`/`img2.bin`/`img3.bin`/`img_4k_pulse.bin` and `SHA256SUMS.txt`); **BENCH-03** validated on
four independent legs (this plan's Task 1); and both **BENCH-02** dispositions — `0x08` and `0x0B` —
recorded `skipped-with-reason` with their explicit not-inferred sentences (this plan's Tasks 2 and
3). Because Gate 0 completed with zero hardware touched, a D-13 halt at any later gate still leaves
BENCH-02 and BENCH-03 complete — neither requirement needed the bench to finish.

---

## Gate 1 — Identity, image under test, VPP, D-03 pre-flight

> ⚠ **PARTIALLY SUPERSEDED BY SESSION 2.** Four rows in the table below — *Firmware commit under
> test*, *Flash bytes measured*, *avrdude verified byte count*, and the flash-headroom figure
> quoted inside the *Flash bytes measured* row — describe firmware commit `a594173d`, which is
> **not** the image any session-2 (2026-08-17) result was produced by. The superseding values are
> in **"Firmware-image supersession"** under "## Resumed session (2026-08-17)" at the bottom of
> this file. The rows are deliberately left legible rather than edited into silence. Every other
> Gate 1 row (board, part, shield revision, R1/R2, VPP, D-03 erase) is unaffected and still holds:
> nothing physical changed between the two sessions.

| Field | Value | Source |
|---|---|---|
| Controller identity | `leonardo` | `firestarter -p /dev/ttyACM0 fw` |
| Port | `/dev/ttyACM0` (CLI-reported; same port before and after the upload's 1200-baud touch reset re-enumeration) | `firestarter -p /dev/ttyACM0 fw` |
| Hardware revision (reported) | `Rev 2.0-class, Override HW: Rev 2.0-class` — **NOT authoritative for distinguishing Rev 2.0 from Rev 2.2 from the modified Rev 0**; the EEPROM `hw_revision` byte cannot make that distinction. The operator's silkscreen reading (row below) is the authority. | `firestarter -p /dev/ttyACM0 hw` |
| Shield silkscreen (operator eyes-on) | **Rev 2.0** — operator's verbatim answer: "Leonardo,  Rev 2.0, w27c512 seated" | operator |
| Seated chip (operator confirmed) | **W27C512** (operator wrote lowercase `w27c512`) — operator's verbatim answer: "Leonardo,  Rev 2.0, w27c512 seated" | operator |
| Part expendable (operator confirmed) | **NOT separately confirmed.** The operator's exact words were "Leonardo,  Rev 2.0, w27c512 seated" — the word "expendable" does not appear and expendability was not separately stated. This is recorded as answered-by-implication only: the prompt they responded to stated the part's contents will be bulk-erased, and the operator seated the part and replied "continue". **Carry-forward status (updated in 145-04): the standalone confirmation was asked for again at 145-04's Gate 1 checkpoint and again not given** — the operator answered "you are authorized" without using the word. Adjudicated there as informed consent for the erase specifically (the operator was shown exactly what `erase W27C512 -b` does before answering, the prior content was already captured and hashed, and a bulk erase is a designed EEPROM operation rather than a wear event); see the "Expendability — recorded truthfully, not overstated" note under Gate 1's authorization. **The carry-forward is NOT discharged and now targets 145-05's Gate 2 authorization**, where the three write cycles put actual wear on the part. | operator (implied only — see note) |
| R1 readback | `270000` | `firestarter -p /dev/ttyACM0 config` |
| R2 readback | `44000` | `firestarter -p /dev/ttyACM0 config` |
| Firmware version string | `3.0.0b17` — see the D-18 caveat immediately below; the version string identifies nothing on its own | `firestarter -p /dev/ttyACM0 fw` |
| Firmware commit under test | `a594173d2bbbabe74e6a470b4751528435246326`, branch `gsd/v1.31-27c-programming-algorithm-fidelity` | `git -C /workspaces/firestarter rev-parse HEAD` / `--abbrev-ref HEAD` |
| Firmware working tree clean | Empty (0 lines), asserted both immediately before `pio run -e leonardo --target size` and immediately after the upload | `git -C /workspaces/firestarter status --porcelain` |
| Flash bytes measured | **26906 bytes program (82.1 % Full against the 32768 B part)**, **2014 bytes data (78.7 % Full)** — equal to `size_baseline.json`'s leonardo record (`flash_used 26906`, `ram_used 2014`). Delta vs baseline: **0 B** against the 0 B leonardo must-not-grow band. Reason: a phase that compiles nothing new cannot move flash (D-16). Against `flash_total` 28672 B (bootloader excluded), the baseline's own figure gives **93.8 %** and **1766 B** of headroom — this is the figure PlatformIO's own `pio run` output (not `--target size`) reported directly: `Flash: [========= ]  93.8% (used 26906 bytes from 28672 bytes)`. Both the 82.1 % (against the 32768 B part) and the 93.8 % (against `flash_total` 28672 B, bootloader excluded) figures are correct; this record names the 93.8 % / 1766 B figure as the one it is quoting for the H7 headroom hand-off. | `pio run -e leonardo --target size` (log: `/tmp/gsd-145/size_leonardo.log`) and `pio run -t upload -e leonardo`'s own pre-upload size banner |
| avrdude verified byte count | **26906** — matches expectation exactly. avrdude tool version actually invoked this session: **`tool-avrdude @ 1.60300.200527 (6.3.0)`** (the PlatformIO package line printed at the top of the upload log) — **not** 8.1; RQ-5's assumption A3 about 8.x wording did not apply this session, but the log was still captured whole and read rather than grepped with a hard-coded pattern, per the plan's prohibition. Verbatim lines read from `/tmp/gsd-145/upload_leonardo.log`: `avrdude: 26906 bytes of flash written` and `avrdude: 26906 bytes of flash verified`. | `/tmp/gsd-145/upload_leonardo.log` (not committed; byte count quoted here per plan) |
| VPP target | **11.9 to 12.4 V** (firmware band 11400 to 12500 mV; hard-abort above 12500 mV, under-voltage warning below 11400 mV) | plan (D-17) |
| VPP confirmation read | **12.0 V (12000 mV)**, single sample, `firestarter -p /dev/ttyACM0 vpp -t 5`, stable across all ten frames of the 5 s window; **no pot adjustment was made** — the operator did not report an adjustment, so this Task 1 reading stands as the confirmation read (see "VPP" subsection below) | `firestarter -p /dev/ttyACM0 vpp -t 5` (single sample) |
| `--force used?` | **No** | source assertion |
| Dispatch mode | **Attested by the orchestrator, not restated by the operator.** The run was invoked as `/gsd-execute-phase 145 --wave 3`; neither `--auto` nor `--chain` was present in the arguments; the orchestrator's `check auto-mode --pick active` query returned `false` before dispatch; and Task 1's `checkpoint:human-action` gate was in fact presented and waited on — the operator's answer arrived only after the gate was posted, which is the behavioural proof no auto-approval occurred. The operator did not separately restate this; the attestation is the orchestrator's (D-20). | orchestrator attestation, see header block |

**D-18 version-string caveat** (next to the Firmware version string row): a correctly reflashed
v1.31 image is expected to report `3.0.0b17`, which is byte-identical to the v1.31 branch's own
fork point `3085084` and reads *older* than `origin/beta`'s `3.0.0b18` — so the version string
identifies nothing. The firmware commit under test plus the avrdude-verified byte count are the
only discriminators; this row's `NOT YET RUN` becomes a fact only once actually read from a
flashed board, never inferred from the version string.

### Reflash proof

`pio run -t upload -e leonardo` from `/workspaces/firestarter` at commit `a594173d` (clean tree,
verified before and after). `firestarter fw --install` was **not used anywhere in this session** —
it resolves a GitHub release asset and the v1.31 branch has none, so it would have flashed `beta`.
Only one `/dev/ttyACM*` device was present before the upload (`/dev/ttyACM0`), so no
`--upload-port` override was needed; the same port was re-detected by PlatformIO's own
"Auto-detected: /dev/ttyACM0" line after the 1200-baud touch reset and re-enumeration, and
confirmed independently afterward by `ls /dev/ttyACM*` and by the subsequent `firestarter fw`
invocation both reporting `/dev/ttyACM0`.

avrdude wrote and verified **26906 bytes**, matching the pre-upload size measurement exactly
(144 H7's zero-growth band, 1766 B headroom, 0 B band, both discharged for free — see the Flash
bytes measured row above).

**MERGE-05 clause, quoted verbatim from `firestarter/scripts/baseline/size_baseline.json`
`meta.deltas_vs_base01.leonardo.merge05_clause`** (NOT paraphrased as compliance):

> "Delta vs BASE-01 is now exactly zero -- Phase 144 / D-11 re-anchored BASE-01 to this file's own
> v1.31-tip figure (26906 B). A zero delta here means the anchor moved to the v1.31 tip, NOT that
> flash growth stayed inside v1.24's original 0 B must-not-grow band (D-14) -- see meta.supersedes
> for the full disclosure."

**Anchor disclosure, stated plainly:** the 0 B delta measured this session is real and matches the
baseline exactly, but per the clause above it is green *because the baseline's own anchor point
was moved to the v1.31 tip by Phase 144*, not because flash growth across the whole v1.24→v1.31
range stayed inside the original v1.24 0 B band. This record states that distinction rather than
reporting the 0 B delta as unqualified MERGE-05 compliance.

### Chip-id confirmation (145-03 Task 3)

**`firestarter info W27C512`** — zero-hardware corroboration, recorded verbatim:
```
Name:               W27C512,W27E512
Manufacturer:       WINBOND
Type:               EEPROM
Can be erased:      yes (electrically erasable)
VCC:                5.0v
VPP:                12.0v
Chip ID:            0xda08
Pulse delay:        100µS
```
Full output in `/tmp/gsd-145/info_w27c512.log`.

**`firestarter -p /dev/ttyACM0 id W27C512`** — run against the seated part. Exit status captured
directly from the command (redirected to a file, `$?` read immediately, never through a pipe to
`tail`), per the plan's explicit anti-false-green instruction:
```
$ firestarter -p /dev/ttyACM0 id W27C512 > /tmp/gsd-145/id_w27c512.log 2>&1
$ echo "exit=$?"
exit=0
```
Verbatim log contents (`/tmp/gsd-145/id_w27c512.log`):
```
Connecting...Connecting... OK
Checking chip ID for W27C512
Chip ID check passed for W27C512: (main done) (0.28s)
```
A `-v` (verbose) re-run against the same seated part additionally shows, at the DEBUG level, the
expected chip-id value the host sent for the firmware to check against: `'chip-id': 55816` in the
EPROM data dict (`EpromOperator: 498`). **55816 decimal = 0xda08** — the Winbond W27C512's chip-id,
matching `firestarter info W27C512`'s printed `Chip ID: 0xda08` exactly. The command passed
(`Chip ID check passed`, exit 0) with no mismatch reported, confirming the seated part **is** the
Winbond W27C512 at chip-id `0xda08`, not the ST M27C512 (`0x203d`) or the TI TMS27C512 (`0x9785`).

**The two wrong-part ids, named for the record:** `0x203d` — ST M27C512, 13 V, non-erasable — and
`0x9785` — TI TMS27C512, also 13 V and non-erasable. D-01 explicitly forbids spending the TMS27C512.
Either id being reported instead of `0xda08` would mean the wrong part is seated. That is **not** a
D-09 re-seat allowance; it is a phase-halting mismatch, and no `--force` may be used to proceed past
it. No mismatch occurred this session — the reported/confirmed id is `0xda08` throughout.

**Fail-safe subsection.** A plain `write` aborts on a chip-id mismatch with no `--force` available
to bypass it. This is the exact mechanism that caught the v1.18 Phase-97 wrong-part mix-up before
any silicon was spent: seating the wrong "512" part triggers this same id-check path and halts the
run rather than damaging the part or producing a false-green result. `--force` is banned for this
entire phase (D-17) — it is not used anywhere in the commands recorded in this session, and none of
the commands actually run in this plan pass `--force`. (`firestarter fw`'s own printed hint, "Use
--force to reinstall", is `fw --install`'s reinstall-even-if-current force — a different flag from
the operation `--force` D-17 bans — and it was never invoked either way.)

**Port identity, re-verified this task (D-19).** A fresh `firestarter -p /dev/ttyACM0 fw`
invocation, run independently in this task rather than carrying Task 2's reading forward, reports
`controller: leonardo on port /dev/ttyACM0` — identical to Task 2's recorded values. No
re-enumeration occurred between Task 2 and Task 3; both values are unchanged and are recorded here
as a fresh, independent confirmation rather than an assumption.

### VPP

Port re-verified fresh for this task (D-19): `firestarter -p /dev/ttyACM0 fw` → `controller:
leonardo on port /dev/ttyACM0` (`/tmp/gsd-145/fw_task1.log`), identical to `145-03`'s recorded
value — no re-enumeration occurred since.

**`firestarter -p /dev/ttyACM0 vpp -t 5`** (single invocation, piped through `tr '\r' '\n'`
per RQ-7's sampling form; the frames are written with carriage returns to stdout, so without the
translation the capture reads as one line). Full transcript in `logs/vpp_confirm.log`:

```
Reading VPP voltage...
Reading will stop after 5 seconds.
Connecting...
Connecting... OK
VPP: 12.0V, Internal VCC: 5.5V   (x10 identical frames over the 5 s window)
VPP reading timed out after 5s.
```

**Reading: 12.0 V (12000 mV), stable across all ten frames of the 5-second sample.**
Classification against the firmware's `eprom_check_vpp` band for W27C512 (`vpp_mv 12000`): the
hard-abort ceiling is above **12500 mV**, the under-voltage warning floor is below **11400 mV**, so
in-band is **11400 through 12500 mV** — 12000 mV is comfortably in-band. Against the concrete pot
target of **11.9 to 12.4 V**, 12.0 V is inside that target window as well, near its low edge. The
reading is neither blank nor `0x303`, so no contact fault is indicated. No pot adjustment appears
necessary on this reading, but per D-20 the operator's explicit authorization for the erase
(Task 2) is still required regardless — this reading alone does not authorize the destructive act.

Exactly one `vpp` invocation was run in this task; no loop, no second call, no monitor left running.

**Task 2 resolution — no adjustment was needed.** The operator was presented with the 12.0 V
reading above, told no adjustment appeared necessary, and asked to either confirm it as-is or
report that the pot had been adjusted. The operator did **not** report any adjustment. Per the
plan's own branch (Task 2's "On resume" instruction), a further `vpp` reading is taken only if the
operator reports an adjustment; since none was reported, no second `vpp` invocation was run in this
continuation. **This Task 1 reading is therefore the confirmation read** — stated explicitly here
rather than left implicit, per the plan's requirement that "if it was not adjusted, the record says
so explicitly." `logs/vpp_confirm.log` is unchanged from Task 1 and contains exactly one `vpp`
invocation for this whole gate.

**Operator authorization (Gate 1, the erase pre-flight):** "you are authorized" (2026-08-16),
recorded verbatim. The operator was shown the VPP reading and classification above and was told the
next command would be `firestarter erase W27C512 -b`, which bulk-erases the whole 64 KiB part and
then blank-checks it, before answering.

**Expendability — recorded truthfully, not overstated.** `145-03`'s carry-forward asked for an
explicit confirmation that the part is expendable; the operator's answer above, "you are
authorized", does not use the word "expendable" and no standalone expendability confirmation was
given. This authorization is read as informed consent for **the erase specifically**: the operator
was shown exactly what `erase W27C512 -b` does before answering, the part's full prior content is
already captured and hashed (see "Pre-write chip preservation" below), and a bulk erase is a
designed EEPROM operation rather than a wear event. This record does **not** claim the operator
confirmed the part is expendable. The standalone expendability confirmation is carried forward to
`145-05`'s Gate 2 authorization, where the three write cycles actually spend wear on the part.

### Pre-write chip preservation

**`firestarter -p /dev/ttyACM0 read W27C512 .planning/phases/145-bench-validation/readbacks/prewrite.bin`**
— exit `0` (console tee'd to `logs/prewrite_read.log`; verbatim completion line: `Read complete
(7.40s). Data saved to .planning/phases/145-bench-validation/readbacks/prewrite.bin`).
`readbacks/prewrite.bin` is exactly **65536 bytes** (`stat -c "%n %s"` confirmed). Its SHA-256
digest is recorded in `SHA256SUMS.txt` (row `readbacks/prewrite.bin`) — no hash inline here;
`sha256sum -c SHA256SUMS.txt` from the phase directory exits 0 over all five rows, including this
one. This is Phase 99's `prewrite.bin` pattern exactly: cheap insurance taken before the first
erase, which also removes assumption A6's risk that the part's prior content mattered — it is now
captured and hashed regardless.

### D-03 erase-capability pre-flight

Port re-verified fresh for this task (D-19), not carried forward from Task 1: `firestarter -p
/dev/ttyACM0 fw` → `Current firmware version: 3.0.0b17, for controller: leonardo on port
/dev/ttyACM0` — identical to Task 1's and 145-03's recorded values; no re-enumeration occurred.

#### `firestarter -p /dev/ttyACM0 erase W27C512 -b`

Run only after the operator's Task-2 authorization above. `-b` here is `--blank-check`, which
**adds** a post-erase blank check (the inverse polarity to `write -b`, which removes the pre-write
blank check and is forbidden this phase — Pitfall 7 / D-03). Exit status captured directly from the
command via `PIPESTATUS[0]`, not through `tail`'s exit code:

```
$ firestarter -p /dev/ttyACM0 erase W27C512 -b | tee logs/erase_preflight.log
Connecting... OK
Erasing EPROM W27C512
  0%|          | 0x0000/0x10000 bytes  ...  100%|██████████| 0x10000/0x10000 bytes
Erase for W27C512 successful (5.05s). (main done)
$ echo "PIPE_EXIT=${PIPESTATUS[0]}"
PIPE_EXIT=0
```

**Exit 0.** `grep -ci "not supported" logs/erase_preflight.log` returns 0 — the historical
`ERROR: Not supported` op-layer gate (`eprom_operations.py:33-40`) did not fire. Exit 0 with the
`-b` blank check attached proves two things at once, per RQ-1: (a) the op-layer `FLAG_CAN_ERASE`
gate let the command through, and (b) the erase physically worked — a non-blank result after erase
would have failed the attached blank check rather than reported `successful`. Full transcript in
`logs/erase_preflight.log`.

**Second confirmation — `firestarter -p /dev/ttyACM0 blank W27C512`.** Exit status read from the
command itself: redirected to a file, `$?` read immediately, then the file tailed — never through a
pipe to `tail`, which would report `tail`'s own exit status instead of the command's:

```
$ firestarter -p /dev/ttyACM0 blank W27C512 > /tmp/gsd-145/blank_w27c512.log 2>&1
$ echo "exit=$?"
exit=0
$ tail -1 /tmp/gsd-145/blank_w27c512.log
Blank check for W27C512 successful (4.85s). (main done)
```

**D-03's contingency branch was NOT taken.** The erase succeeded cleanly on the first pre-flight
attempt; the pure 1→0 program-proof fallback (verify a region reads all-`0xFF`, write a distinctive
pattern, read back byte-exact) was never needed and was not run.

**Dated supersession chain, resolving the record's apparent conflict chronologically:**
- **2026-05-21** — Phase 24 bench: `firestarter erase W27C512` → `ERROR: Not supported`. At the
  time, `build_db.py` decoded W27C512 as a UV-EPROM, so `FLAG_CAN_ERASE` was never set.
- **v1.11 `cca7d62`** — fixes the infoic decode so `electrical.type = EEPROM` for W27C512. The todo
  closed with *"NOT yet bench-verified: whether `firestarter erase W27C512` succeeds end-to-end is
  firmware-gated … needs an operator bench test"* — this is D-03's "operator-bench-pending" caveat.
- **v1.14 Phase 77** — first hardware graduation: the full write→auto-erase→program→verify cycle
  bench-proven on a real non-blank W27C512 on the Leonardo.
- **v1.16 Phase 91** — RCA established that `write -b` (skip-erase) was the earlier test-method
  error, not a firmware defect; W27C512 graduated to PASS with erase confirmed on the bench.
- **v1.16 Phase 92** — `-b` decoupled from skip-erase into its present, inverse-polarity form on
  `write`; bench-confirmed on the seated W27C512.

This session's `erase W27C512 -b` result is a fresh, independent re-confirmation on this exact
board and this exact v1.31 build, settling D-03 on silicon rather than by inference from those prior
sessions.

**Measured wire facts** (host-side, `EpromDatabase().convert_to_programmer()` against the shipped
v1.31 DB, corroborated by RESEARCH §RQ-1): W27C512 sends `flags` **`0x02`** with **`FLAG_CAN_ERASE`
set**, `vpp_mv` **12000**, `pulse-delay` **100**, `chip-id` **`0xDA08`**, `memory-size` **65536**.

**The `-b` polarity, stated once more for this record's own closure:** `erase -b`/`--blank-check`
**adds** a post-erase blank check; `write -b`/`--no-blank-check` **removes** the pre-write blank
check — opposite polarities on the same short flag, both preserved verbatim from the argparse era.
Neither `write -b` nor `--skip-erase` was used anywhere in this plan or in this phase.

**Gate 1 identity-half verdict (145-03, Tasks 1–3):** Five conditions cleared that plan —
(1) right board, by the operator's own silkscreen reading, `Rev 2.0`; (2) right part, by chip-id
`0xda08`, confirmed via `firestarter id W27C512` (exit 0) and corroborated by `firestarter info
W27C512`; (3) right build, by firmware commit `a594173d` plus the avrdude-verified byte count
`26906`, never by the `3.0.0b17` version string alone; (4) clean tree, `git status --porcelain`
empty both before and after the build and upload; (5) zero flash growth, `26906`/`2014` matching
`size_baseline.json` exactly, with the MERGE-05 anchor-move disclosure stated rather than an
unqualified compliance claim.

**Gate 1 verdict: cleared.** All seven conditions are now discharged: (1) right board by operator
silkscreen (`Rev 2.0`); (2) right part by chip-id `0xda08`; (3) right build by commit `a594173d`
plus the avrdude-verified byte count `26906` against a clean tree; (4) zero flash growth against the
Leonardo baseline (`26906`/`2014`, MERGE-05 anchor-move disclosed); (5) VPP in band by a single
confirming read (12.0 V / 12000 mV, no adjustment needed, `--force used? No`); (6) the D-03
erase-capability question settled on silicon — `erase W27C512 -b` exited 0 with its post-erase
blank check passing, corroborated by a standalone `blank W27C512` also exiting 0, and the
historical `ERROR: Not supported` contradiction is explained by the dated supersession chain above;
(7) the chip is left blank and ready for Gate 2's cycle 1. **Gate 2's three-cycle spend is a
separate authorization, given in `145-05`, and has not been given here** — nothing in this plan
writes to the part beyond the erase itself.

---

## Gate 2 — Three 64 KiB cycles (authorized spend)

**Operator authorization:** "you can erase or do anything its a test ic for you" (2026-08-16),
recorded verbatim exactly as given — spelling and phrasing preserved, not cleaned up, not
corrected, not paraphrased.

**Carry-forward adjudication (145-04's standalone expendability confirmation).** This
authorization discharges both halves of what this gate needed:
1. The three-cycle 64 KiB spend itself is authorized ("you can erase or do anything").
2. The 145-04 carry-forward — a standalone confirmation that the part is expendable, distinct
   from consent for the erase alone — is discharged here by the phrase "its a test ic for you":
   the operator states the seated part is a test IC held for this purpose, which is unambiguous
   informed consent that it may be consumed or damaged by this spend. This record states the
   reason the adjudication holds (the "test ic" phrasing naming the part's purpose) rather than
   asserting the discharge without support, so a later reader can audit the adjudication rather
   than trust it on faith.

### Cycle 1

> ⚠ **SESSION 1's cycle 1. SUPERSEDED BY SESSION 2 — see "## Resumed session (2026-08-17)".**
> The failure recorded below was subsequently root-caused to a **firmware defect** (debug session
> `w27c512-program-fail-byte0`), not to the part, the shield or the bench. It is left here verbatim
> because it is real evidence and because the defect it exposed is the most valuable thing this
> phase produced. Session 2 re-ran cycle 1 on a **different, fixed firmware build**; that run is
> recorded separately below and does **not** overwrite this one.

**Cycle 1 verdict (session 1): FAILED.** One attempt was made and it failed on the very first byte of the
very first block. Per D-14's two-state taxonomy this is a fail, not a partial and not an
inconclusive. Cycles 2 and 3 were never attempted — the pass rule is 3/3 byte-exact on both
oracles, and a fail on cycle 1 forecloses that regardless of what a later cycle might have shown.

#### Attempt 1 (GENUINE FAILURE — not discarded; D-09's re-seat allowance was never consumed)

Port re-verified fresh for this task (D-19): `firestarter -p /dev/ttyACM0 fw` →
`Current firmware version: 3.0.0b17, for controller: leonardo on port /dev/ttyACM0` — identical
to `145-04`'s recorded value; no re-enumeration occurred.

`firestarter -v -p /dev/ttyACM0 write W27C512 .planning/phases/145-bench-validation/images/img1.bin`
(stdout preserved at `logs/write_cycle1_attempt1.stdout.log`, stderr at
`logs/write_cycle1_attempt1.stderr.raw` — copied off the canonical `write_cycle1.stdout.log` /
`write_cycle1.stderr.raw` names before any re-run, so a re-run does not overwrite this evidence)
— **exit 1**, elapsed 9.4s (`time`). Verbatim failure line:

```
ERROR  :RURP         : 342: ERROR: Byte at 0x000000 failed to program within 25 pulses
ERROR  :EpromOperator: 622: Programmer error during WRITE: Byte at 0x000000 failed to program
within 25 pulses -- the write aborted at this address: bytes before this block were already
programmed, this block is only partially programmed, and no later block was attempted. The
firmware stops accepting blocks for this write and its address counter does not advance, so
re-running the write repeats the whole file from the start. A byte that will not converge like
this usually means insufficient program voltage or a worn or failing cell, not a timing problem.
ERROR  :EpromOperator:1986: Write to W27C512 failed.
```

The failure occurred on the very first byte of block 1 (offset `0x000000`), on the first pulse
attempt of the entire cycle — before any block completed.

**What still worked, bounding the failure to the program step specifically:**
- Port identity: `firestarter -p /dev/ttyACM0 fw` → `controller: leonardo on port /dev/ttyACM0`,
  identical to `145-04`'s recorded value; the right board was addressed.
- `firestarter -p /dev/ttyACM0 id W27C512` → exit 0, `Chip ID check passed for W27C512` — the
  seated part still identifies correctly as the Winbond W27C512 (`0xda08`); this rules out a
  chip-id mismatch as the cause.
- The INIT-phase blank-check streamed cleanly through the **entire** 65536-byte space before the
  failure (`DATA: 2048/65536` through `DATA: 65536/65536`, then `INIT: (init done)`) — the whole
  part read as blank going in, consistent with `145-04`'s `erase W27C512 -b` having passed its own
  post-erase blank check. The chip was blank and readable; only the program step failed.
- `firestarter -p /dev/ttyACM0 vpp -t 5` (post-failure) → **12.0V, Internal VCC 5.5V**, stable
  across all ten frames of the 5s window — unchanged from Gate 1's confirming read, still in-band
  (11400–12500 mV).

**What failed:** bit-programming under load, on the very first byte, on the very first pulse
attempt of the entire cycle — `MAIN` phase, not `INIT`.

**The idle VPP reading does NOT rule out program-window droop.** 12.0V/5.5V is an *idle* sample,
taken with no pulse in flight. The program-window voltage at the socket, under load, was **not
measured** — the held-rail DMM proxy that would take that reading is defeated by
DTR-reset-on-close (the standing Phase-97 tooling gap), so an idle-in-band reading and a
droop-under-load failure are not in tension with each other; the tooling on hand cannot
distinguish the two.

**D-09 adjudication — the allowance was NOT consumed.** The operator physically inspected the
bench and reported that **no physical cause is apparent** — the setup looks correct — and selected
the D-13 halt path over consuming D-09's re-seat allowance. Per D-09 the allowance requires
attribution to a *named physical cause*; none was found, so **this attempt stands as a genuine
failure, not a discardable one, and D-09's single re-seat allowance was never spent — it remains
available, unconsumed, if this phase is ever resumed after a debug session.** No re-seat occurred.
No Attempt 2 was run.

**Operator's decision, recorded honestly as a selection, not a quote.** The operator answered by
selecting a presented option, not by typing prose. This record does not manufacture a verbatim
quote for that selection: the operator inspected the bench and reported no physical cause
apparent; they selected the D-13 halt path over consuming D-09's re-seat allowance. (Contrast:
Gate 2's own authorization above was typed verbatim by the operator and stays quoted as-is —
that is a different answer, recorded by a different method, and this record does not blur the
two together.)

**A HYPOTHESIS FOR DEBUG ONLY, not a claimed cause.** The `vpp -t 5` reading also reports
`Internal VCC: 5.5V`. This project's v1.31 milestone carries a known **6.25V program-VCC evidence
ceiling** (unreachable on this shield) as standing context. Naming the two figures side by side is
useful for whoever picks up the debug session, but this record makes **no claim either way**: no
measurement here distinguishes a program-VCC-related explanation from a marginal/worn part or from
an unmeasured VPP droop under load, and this is explicitly **not** a datasheet-conformance claim in
either direction. This sentence exists to hand the observation to debug, not to adjudicate it.

### Cycle 2
**NOT ATTEMPTED — Gate 2 halted on cycle 1's failure.** Per D-14 cycle 1's fail forecloses the
3/3 pass rule regardless of what cycle 2 might have shown; running it would not change the
verdict. Not run.

### Cycle 3
**NOT ATTEMPTED — Gate 2 halted on cycle 1's failure.** Same reason as Cycle 2. Not run.

### Progress-frame evidence (D-10 Claim A)

> ⚠ **SUPERSEDED BY SESSION 2** — measured in "## Resumed session (2026-08-17)".

**NOT MEASURED (session 1).** Frame extraction requires a completed (or at least far-progressed) write's raw
stderr capture; cycle 1 failed on the first byte of the first block, so there is no meaningful
progress-bar segment to extract frames from. No v1.31 owner (see "Carry-forward hand-offs" below).

### D-09 re-seat ledger
At most one re-seat is allowed across the whole Gate 2 spend, and it must be attributable to a
named physical cause (re-seat, chip-id mismatch, VPP out of band). **The allowance was OFFERED
but NOT SPENT.** The operator physically inspected the bench after cycle 1's Attempt 1 failure and
reported no physical cause apparent; they selected the D-13 halt path instead of a re-seat. No
re-seat occurred. No Attempt 2 was run. **The allowance remains unconsumed** and is available if
this phase is resumed after a debug session determines and fixes (or rules out) a cause.

**Gate 2 verdict (session 1): FAIL.** Cycle 1's single attempt failed on the first byte of the
first block (`Byte at 0x000000 failed to program within 25 pulses`, exit 1). Cycles 2 and 3 were
never attempted. Per D-14 there is no partial and no inconclusive state — this is a fail.

> ⚠ **This verdict is session 1's and is not the phase's final Gate 2 verdict.** Session 2 resumed
> Gate 2 on a corrected firmware build. Gate 2's overall verdict is closed by `145-06` Task 3 after
> cycles 2 and 3, not here and not by session 1's fail. See "## Resumed session (2026-08-17)".

---

## Gate 3 — `--pulse-us 4688` (D-10 Claim B, D-12)

Gate 3 is **required conditional on Gate 2 passing**. If Gate 2 fails, Gate 3 is recorded here as
**not-reached**, with the reason, rather than silently omitted.

**Gate 3: NOT REACHED.** Gate 2 did not validate — cycle 1 failed and cycles 2/3 were never
attempted (D-14: fail, not partial). Per this gate's own opening sentence, a Gate-2 fail records
Gate 3 as not-reached with the reason, rather than silently omitting it. Nothing below this line
was run.

**Operator authorization:** NOT REACHED — Gate 2 did not clear, so this authorization was never
sought.

### Run
**NOT REACHED** — `firestarter write W27C512 img_4k_pulse.bin --pulse-us 4688` was never run.

### Claim B
**NOT REACHED** — no `--pulse-us` run occurred, so no Claim B measurement is possible.

### A1 per-pulse overhead
**NOT REACHED** — requires two pulse-width runs on silicon; neither was attempted.

### Operator eyes-on
**NOT REACHED** — no run occurred for the operator to watch.

**Gate 3 verdict: NOT REACHED — Gate 2 failed to clear.**

---

## SHA manifest

Every digest for this phase — every generated image and every hardware read-back — lives in one
place: `.planning/phases/145-bench-validation/SHA256SUMS.txt`. No hash is written inline anywhere
in this narrative; a reader runs `sha256sum -c SHA256SUMS.txt` from the phase directory to verify
everything at once.

## Not measured

| Reading | Blocking reason |
|---|---|
| Program-window VPP (and program-window internal VCC) at the socket, under load, during cycle 1's failed write | The held-rail DMM proxy that would take this reading is defeated by DTR-reset-on-close (the standing Phase-97 tooling gap). Only an *idle* `vpp -t 5` sample (12.0V / Internal VCC 5.5V) was available, before and after the failed write; whether the program-window figure droops under load was never instrumented, exactly as `0x08`'s FUT-08 was never instrumented for the same reason. |

## Carry-forward hand-offs with no v1.31 owner

> ⚠ **PARTIALLY SUPERSEDED BY SESSION 2.** Three of the items below have since been discharged and
> no longer lack an owner: **D-10 Claim A** (measured, HOLDS — 64 intra-block frames),
> **D-11's CAP-03 free evidence** (claimed, with its non-claim stated), and **BENCH-01's cycle 1**
> (byte-exact on all three oracles). BENCH-01 as a whole is still undischarged — Gate 2 needs 3/3
> and `145-06` owns cycles 2 and 3. The remaining items are genuinely still open. See
> "## Resumed session (2026-08-17)".

Phase 146 is docs-and-claims only and cannot run a bench. This phase halted at Gate 2's first
cycle failure; everything below did not run and has **no v1.31 owner**:

- **BENCH-01 itself — no v1.31 owner.** The full 64 KiB write→read→verify on W27C512, three cycles
  deep, did not clear cycle 1. The requirement is undischarged pending a debug session's root
  cause and, if fixed, a resumed bench run.
- **D-10 Claim A (machine-counted intra-block frames) — no v1.31 owner.** No progress-frame
  extraction was possible; cycle 1 failed before any meaningful bar segment existed.
- **D-10 Claim B (`--pulse-us` bucket collision) — no v1.31 owner.** Gate 3 was not reached.
- **D-10 operator eyes-on (smooth bar vs end-burst) — no v1.31 owner.** No run occurred for the
  operator to watch.
- **D-11's CAP-03 advertised-budget free evidence — no v1.31 owner.** The write did not complete;
  there is no completed-run evidence to claim.
- **D-12's `--pulse-us`-on-silicon item — no v1.31 owner.** Stretch item, never attempted; Gate 3
  was not reached.
- **D-12's A1 per-pulse-overhead measurement — no v1.31 owner.** Same reason; never attempted.
- **The program-window VPP-under-load measurement** (see "Not measured" above) — carried forward
  as the leading diagnostic a debug session would want, alongside the `Internal VCC: 5.5V`
  hypothesis-for-debug-only note recorded in Cycle 1's Attempt 1 subsection.

---

## VERDICT: HALTED (session 1, 2026-08-16 — SUPERSEDED, see the resumed session below)

> ⚠ **This halt was lifted on 2026-08-17.** The debug session it handed off to
> (`.planning/debug/w27c512-program-fail-byte0.md`) found the cause in **firmware**, fixed it, and
> resolved. The phase resumed. This verdict block is preserved verbatim as the record of what
> session 1 concluded with the evidence session 1 had; it is **not** the phase's current state.
> Read "## Resumed session (2026-08-17)" below for what is true now.

**Reason:** Gate 2 failed on cycle 1's first write attempt — `Byte at 0x000000 failed to program
within 25 pulses`, exit 1, on the very first byte of the very first block, before any block
completed. The operator physically inspected the bench and found no physical cause apparent,
so D-09's one allowed re-seat was not spendable and was not spent (it remains unconsumed for a
resumed run). Per D-13 this phase does not absorb a fix and does not retry; it hands off to a
debug session. Cycles 2 and 3 of Gate 2, and all of Gate 3, were never attempted (D-14: this is a
fail, not a partial). BENCH-02 and BENCH-03 (Gate 0) remain independently validated/skipped-with-
reason — they required no bench and are unaffected by this halt.

**Session end:** 2026-08-16, halted at 145-05 Task 2 (cycle 1, Attempt 1) — see the "Carry-forward
hand-offs with no v1.31 owner" section above for everything this phase did not discharge.

---

# Resumed session (2026-08-17)

**Session start:** 2026-08-17
**Operator:** Henrik (henrik@predictly.se)
**Driver:** Claude Code (GSD executor), same D-19 split as session 1 — Claude drives serial/CLI,
the operator owns the physical side.
**Resumed at:** `145-05` Task 2, Gate 2 cycle 1. Tasks before it were already discharged in
session 1 and were not re-run.
**Dispatch mode:** resumed by explicit operator instruction with no `--auto` and no `--chain`;
`autonomous: false` on `145-05` still holds and no operator gate was self-approved in this session
(D-20). No `AskUserQuestion` capability was available to this executor, so any gate reached would
have been handed back rather than answered — none other than the already-discharged Gate 2 spend
authorization was reached.

## Why the phase resumed

Session 1's Gate 2 cycle 1 failure was handed to `/gsd-debug` per D-13. Debug session
`.planning/debug/w27c512-program-fail-byte0.md` (status: **resolved**) root-caused it to a
**firmware defect**, not to the part, the shield, the pot or the seating:

> v1.31 Phase 141 rewrote `eprom_write_execute` into a per-byte pulse-to-verify loop and deleted
> `program_mismatched_bytes()`, which was the **only** place the EPROM write path ever asserted
> `CTRL_VPE_ENABLE`. From Phase 141 until the fix, every program pulse on protocols `0x07`, `0x08`
> and `0x0B` was emitted with the 12 V rail generated and dropped but **never routed onto the
> socket's VPP node**. No cell could change, so byte `0x000000` — which needs a pulse, since
> `img1.bin` byte 0 is `0x00` and escapes the `expected == 0xFF` skip — exhausted `max_pulses` 25.

Fixed in `firestarter` commits `eb563d2` (restore the per-pulse program-voltage assert) and
`ebe9cb3` (raise `EPROM_VPP_SETUP_US`/`EPROM_VPP_HOLD_US` to 1000 µs/100 µs on bench evidence).

This vindicates session 1's own refusal to consume D-09's re-seat allowance: the operator inspected
the bench, found no physical cause, and there was none to find.

## Firmware-image supersession — Gate 1's identity record is STALE for this session

Gate 1 (`145-03`) deliberately identified the image under test by **commit plus avrdude-verified
byte count, never by version string** (D-18). That discipline is exactly what makes this
supersession statable: the version string is unchanged and would have hidden the swap entirely.

`145-04-SUMMARY.md` wrote that "firmware remains at commit `a594173d` — no further reflash should be
needed for `145-05` **unless the tree changes**." **The tree changed.** So the board was reflashed
before any session-2 silicon was spent, and these four Gate 1 rows are superseded:

| Gate 1 row | Session 1 value (still true of `a594173d`) | **Session 2 value — the image every result below was produced by** |
|---|---|---|
| Firmware commit under test | `a594173d2bbbabe74e6a470b4751528435246326` | **`ebe9cb353f134d6c56a8295490142de1a43fdf8f`**, branch `gsd/v1.31-27c-programming-algorithm-fidelity` |
| Flash bytes measured | 26906 program / 2014 data | **27002 program (82.4 % Full against the 32768 B part) / 2014 data (78.7 % Full)** |
| Flash headroom | 93.8 %, **1766 B** free | **94.2 %, 1670 B free** against `flash_total` 28672 B (bootloader excluded) |
| avrdude verified byte count | 26906 | **27002** |
| Firmware version string | `3.0.0b17` | **`3.0.0b17` — UNCHANGED, and therefore useless as a discriminator.** This is D-18's caveat proving itself: the fix moved 96 bytes of flash and did not move the version string by one character. |

**Corrected flash-delta line — session 1's "0 B delta" is FALSE for this build and is NOT carried
forward.** Gate 1 recorded: *"Delta vs baseline: 0 B against the 0 B leonardo must-not-grow band.
Reason: a phase that compiles nothing new cannot move flash (D-16)."* For the session-2 image the
delta is **+96 B** (26906 → 27002) against the 0 B leonardo must-not-grow band, and **the reason
clause no longer applies** — code *was* compiled that this phase did not compile, by a debug
session, so "a phase that compiles nothing new cannot move flash" is true of the phase and
irrelevant to the image.

### Reflash proof (session 2)

Commands run from `/workspaces/firestarter` at `ebe9cb3`, with
`git -C /workspaces/firestarter status --porcelain` asserted **empty (0 lines) both immediately
before and immediately after** the build and the upload:

```
$ pio run -e leonardo --target size          # exit 0
Program:   27002 bytes (82.4% Full)
Data:       2014 bytes (78.7% Full)

$ pio run -t upload -e leonardo              # exit 0
```

`firestarter fw --install` was **not used anywhere in this session either** — it resolves a GitHub
release asset and the v1.31 branch has none, so it would have flashed `beta`. The upload log was
captured whole and read in full rather than grepped with a hard-coded pattern; verbatim lines from
`/tmp/gsd-145/upload_leonardo_145_05.log`:

```
RAM:   [========  ]  78.7% (used 2014 bytes from 2560 bytes)
Flash: [========= ]  94.2% (used 27002 bytes from 28672 bytes)
Auto-detected: /dev/ttyACM0
avrdude: 27002 bytes of flash written
avrdude: 27002 bytes of flash verified
```

avrdude tool version actually invoked: `tool-avrdude @ 1.60300.200527 (6.3.0)` — same as session 1.
Only one `/dev/ttyACM*` device was present before and after; no `--upload-port` override was needed.

## D-16 — stated plainly rather than left to read as untouched

D-16 says *"No file under `firestarter/` or `firestarter_app/` is created, edited or deleted by any
plan."* **That invariant is intact on its own terms: no plan in this phase edited a source file,
and this plan did not either.** But the record must not let D-16 read as though the firmware were
untouched across the whole phase. It was not. A **debug session** — which is not a plan — changed
eleven files under `firestarter/`, and the phase's second session therefore measures a *different
built image* than its first. That is the honest shape of it: D-16 not violated, firmware not
unchanged.

## MERGE-05 — this build carries a known, un-adjudicated band breach

The session-2 image is **+96 B of flash** against MERGE-05's **0 B leonardo** must-not-grow band
(the uno-class band is 64 B, also exceeded). The debug session **deliberately did not launder it**:
BASE-01 was **not** re-anchored, because Phase 144 / D-11 moved that anchor once already and moving
it again from a debug session would hide a breach behind the same mechanism twice. The breach is
recorded as a live assertion, `test_policy_merge05_fires_on_the_current_tree`, so it cannot rot.

**This is not this plan's to adjudicate, and this plan did not adjudicate it.** Nothing here
re-anchors a baseline, widens a band or edits a gate. The operator has seen the breach and chose to
resume with it open. It is stated here for one reason only: **every measurement recorded in this
resumed session was produced by a build carrying an open MERGE-05 band breach**, and a later reader
must not discover that from somewhere else. Whether a defect fix is admitted through the band is a
milestone requirements judgement.

## D-09 re-seat ledger — adjudicated, still UNCONSUMED

Stated explicitly rather than assumed:

- Session 1's cycle-1 failure was a defect in the **firmware build**, now proven by root cause and
  by the fix flipping a 100 %-reproducible failure into a byte-exact write on the same board, the
  same shield and the **same seated part**. It had no physical cause, which is precisely why the
  operator could not name one.
- **No re-seat occurred.** No chip was touched between session 1 and session 2. D-09's allowance is
  therefore **untouched and still available** — it was never spent, and nothing in this session
  spends it.
- The run below is **Gate 2 cycle 1 on a different firmware build**, not "Attempt 2" under D-09's
  ledger. D-09 governs discarding a failure attributable to a *named physical cause* and re-running
  the same configuration; that is not what happened. Session 1's failure is **not discarded** — it
  stands in the record above as a genuine failure of a genuinely defective build.

## Operator authorization — already given, not re-sought

Gate 2's three-cycle spend authorization stands as recorded above: **"you can erase or do anything
its a test ic for you"** (2026-08-16), verbatim. It was given for this exact spend and is not
re-sought here. It also already discharged `145-04`'s standalone-expendability carry-forward, for
the reason recorded under Gate 2's heading.

**Additional wear disclosure, for honesty about what the part has actually absorbed.** The debug
session ran **13 further full 64 KiB erase-and-program cycles** on this same part while
root-causing and validating the fix (12 byte-exact, 1 failure at the pre-shipping settle values).
Those cycles were run under the operator's live debug-session authorization ("you can erase or do
anything its a test ic for you", plus the session's explicit *"part is expendable; erases and write
attempts on it are authorized"* constraint block) — but they were **not** part of Gate 2's
three-cycle budget and are named here so the record does not imply this part has seen only three
program cycles. Cycle counting for Gate 2's pass rule starts fresh below.

## Gate 2 (resumed) — Cycle 1

**Port identity, re-verified fresh for this task (D-19), not carried forward from `145-04` and not
carried forward from session 1.** Two independent invocations, one before the reflash and one after:

```
$ firestarter -p /dev/ttyACM0 fw                       # exit 0, BEFORE the reflash
Current firmware version: 3.0.0b17, for controller: leonardo on port /dev/ttyACM0

$ firestarter -p /dev/ttyACM0 fw                       # exit 0, AFTER the reflash
Current firmware version: 3.0.0b17, for controller: leonardo on port /dev/ttyACM0
```

`ls /dev/ttyACM*` reported exactly one device, `/dev/ttyACM0`, before and after; no re-enumeration
shuffled the numbering. **Note what these two readings prove and what they do not:** they prove the
right *controller* on the right *port*, and they prove **nothing** about which image is on it — the
version string is byte-identical across a 96-byte firmware change (D-18). The image is identified by
commit `ebe9cb3` plus the avrdude-verified **27002** bytes, recorded under "Firmware-image
supersession" above.

**Seated part re-confirmed after the reflash:**
```
$ firestarter -p /dev/ttyACM0 id W27C512                # exit 0
Chip ID check passed for W27C512: (main done) (0.28s)
```

---

#### `firestarter -v -p /dev/ttyACM0 write W27C512 .planning/phases/145-bench-validation/images/img1.bin`

Run from `/workspaces`, stdout redirected to `logs/write_cycle1.stdout.log` and stderr to
`logs/write_cycle1.stderr.raw`. **No `-b`, no `--no-blank-check`, no `--skip-erase`, no `--force`,
no `-a` and no `-s`** — the full 65536 bytes, 64 blocks of 1024 B (D-04). `-v` and `-p` are group
options and precede the subcommand. The canonical stderr path was asserted **absent** immediately
before the run, so session 1's preserved failure evidence
(`logs/write_cycle1_attempt1.stdout.log` / `.stderr.raw`) could not be overwritten; it was not.

**Exit 0.** Wall clock 110 s (`date` delta around the invocation).

##### The three oracle verdicts — recorded separately, never merged

**Oracle 1a — the write's own verdict (firmware-side, first pass).** Verbatim from
`logs/write_cycle1.stdout.log`:
```
INFO   :EpromOperator:1982: Write to W27C512 successful (106.06s).
```
`grep -ci "bad bytes" logs/write_cycle1.stdout.log` → **0**.

**The 106.06 s figure is a first-class measurement, not a timing footnote.** No v1.31 figure for a
64 KiB W27C512 write existed before this run; the only prior recorded figure is a **22.84 s**
pre-v1.31 run. The gap is **not** a v1.31 regression in the loop: **58.9 s of it is the
`EPROM_VPP_SETUP_US` 100 → 1000 µs settle increase** shipped by the debug session
(65408 pulsed bytes × 900 µs = 58.9 s), and the debug session independently cross-checked that the
added time is settle rather than extra pulses (it matches the arithmetic almost exactly, which it
could not if bytes were needing more pulses). Recorded as measured with its cause named, not
explained away.

**Oracle 1b — the verify's own verdict (firmware-side, SECOND pass).** Verbatim from
`logs/verify_cycle1.log`, exit **0**:
```
Verify for W27C512 successful (5.68s).
```

**D-06's independence boundary, stated rather than implied.** `verify` uses the **same
`_main_phase_send_data` handler as `write`** and the **firmware** performs the compare, so oracle 1b
is a **second firmware-side pass, not an independent oracle**. The genuinely independent oracle is
oracle 2 below: `read` to a file (firmware `CMD_READ` merely streams bytes; no comparison happens on
the board) followed by a **host-side** `sha256sum` compare against the source image.

**Oracle 2 — the independent host-side SHA compare.** `firestarter -p /dev/ttyACM0 read W27C512
.planning/phases/145-bench-validation/readbacks/readback1.bin` → exit **0**, `Read complete (7.40s)`
(`logs/read_cycle1.log`). `readbacks/readback1.bin` is exactly **65536 bytes**.

```
$ cmp images/img1.bin readbacks/readback1.bin        # exit 0, no output
$ sha256sum images/img1.bin readbacks/readback1.bin
f72489604bfe917db7ee505e4d674576b2905a418e8dc55372b78dcab3e34e3a  images/img1.bin
f72489604bfe917db7ee505e4d674576b2905a418e8dc55372b78dcab3e34e3a  readbacks/readback1.bin
```
**Digests identical — 65536 of 65536 bytes byte-exact.** `readbacks/readback1.bin`'s digest is
appended to `SHA256SUMS.txt`; `img1.bin`'s row was already in the manifest from `145-01` and is
**unchanged**, which is itself a small extra fact — the source image on disk is bit-for-bit the one
whose digest was published before any hardware was touched. `sha256sum -c SHA256SUMS.txt` from the
phase directory exits **0** over all six rows. No duplicate `img1.bin` row was appended; the
manifest stays one-row-per-artifact.

**The three verdicts agree. They are recorded on three separate lines anyway**, because D-06's point
is that a *disagreement* must be visible, and a format that only works when everything agrees would
not have shown one.

##### Read stability for this cycle (D-07)

```
$ firestarter -p /dev/ttyACM0 dev consistency-check W27C512 --runs 3 \
      --output-dir .planning/phases/145-bench-validation/runs/cycle1
```
**Exit 0.** The exit code here is a three-way value, not a boolean — **0 = PASS, 1 = FAIL on
divergent SHAs, 2 = hardware or serial error** — so `0` specifically means the runs agreed, not
merely that the command ran. Verdict block verbatim from `logs/consistency_cycle1.log`:
```
Consistency check: PASS
Chip: W27C512  Board: unknown-board  Port: /dev/ttyACM0
Runs: N=3
Distinct SHAs: 1
Output dir: .planning/phases/145-bench-validation/runs/cycle1/
```
`run_01.bin`, `run_02.bin` and `run_03.bin` all exist at exactly **65536 bytes** each.
`git check-ignore` on `runs/cycle1` reports **not ignored** — the evidence is committable, and the
default `firestarter-runs/consistency-check-*/` path (matched by two meta `.gitignore` rules) was
deliberately not used.

**A free extra fact worth naming:** all three runs reported SHA-256
`f72489604bfe917db7ee505e4d674576b2905a418e8dc55372b78dcab3e34e3a` — the **same digest as the source
image**. `dev consistency-check` only asserts the runs agree *with each other*; that they also agree
with `img1.bin` makes this three further independent confirmations of oracle 2, on top of the one
oracle 2 required. Read stability and program correctness are different failure modes (D-07) and
this cycle passes both.

##### `--force used?` **No**

No `--force` was passed to any command in this cycle. Neither was `write -b`, `--no-blank-check`,
`--skip-erase`, `-a`/`--address` nor `-s`/`--size`. Every command line above appears verbatim as its
own heading or fenced block so the flags are auditable without trusting this sentence (D-17).

##### Cycle 1 verdict (resumed session): **PASS — byte-exact on all three oracles**

Write exit 0 with 0 bad bytes, verify exit 0, independent host-side SHA compare byte-exact over all
65536 bytes, read stability PASS at N=3 with 1 distinct SHA.

**This does NOT close Gate 2.** Gate 2's rule is **3/3** byte-exact cycles on both oracles; cycles 2
and 3 are `145-06`'s, and Gate 2's overall verdict is `145-06` Task 3's to record. One cycle is one
cycle.

### Cycle 2 (resumed) — `145-06` Task 1

**Port identity, re-verified fresh for this task (D-19), not carried forward from `145-05`.**

```
$ ls /dev/ttyACM*                                      # exactly one device
/dev/ttyACM0
$ firestarter -p /dev/ttyACM0 fw                       # exit 0
Current firmware version: 3.0.0b17, for controller: leonardo on port /dev/ttyACM0
```

**What this proves and what it does not.** It proves the right *controller* on the right *port*. It
proves **nothing** about which image is on the board — `3.0.0b17` did not move across a 96-byte
firmware change (D-18), so the version string is useless as a discriminator. The image under test is
identified by commit and byte count only: `/workspaces/firestarter` was asserted still at
`ebe9cb353f134d6c56a8295490142de1a43fdf8f` with **empty** `git status --porcelain` before this task
began, so the avrdude-verified **27002**-byte image flashed in `145-05` is unchanged and **no
reflash was performed or needed in this plan**.

**Seated part re-confirmed:**
```
$ firestarter -p /dev/ttyACM0 id W27C512                # exit 0
Chip ID check passed for W27C512: (main done) (0.28s)
```

---

#### `firestarter -v -p /dev/ttyACM0 write W27C512 .planning/phases/145-bench-validation/images/img2.bin`

Run from `/workspaces`, stdout redirected to `logs/write_cycle2.stdout.log` and stderr to
`logs/write_cycle2.stderr.raw`. **No `-b`, no `--no-blank-check`, no `--skip-erase`, no `--force`,
no `-a` and no `-s`** — the full 65536 bytes, 64 blocks of 1024 B (D-04). `-v` and `-p` are group
options and precede the subcommand. The canonical cycle-2 stderr and stdout paths were asserted
**absent** immediately before the run.

**Exit 0.** Wall clock 109 s (`date` delta around the invocation).

##### The three oracle verdicts — recorded separately, never merged

**Oracle 1a — the write's own verdict (firmware-side, first pass).** Verbatim from
`logs/write_cycle2.stdout.log`:
```
INFO   :EpromOperator:1982: Write to W27C512 successful (105.69s).
```
`grep -ciE "bad bytes|MAX_PULSES" logs/write_cycle2.stdout.log` → **0**.

**Oracle 1b — the verify's own verdict (firmware-side, SECOND pass).** Verbatim from
`logs/verify_cycle2.log`, exit **0**:
```
Verify for W27C512 successful (5.69s).
```

**D-06's independence boundary, restated rather than assumed carried.** `verify` uses the **same
`_main_phase_send_data` handler as `write`** and the **firmware** performs the compare, so oracle 1b
is a **second firmware-side pass, not an independent oracle**. The genuinely independent oracle is
oracle 2.

**Oracle 2 — the independent host-side SHA compare.** `firestarter -p /dev/ttyACM0 read W27C512
.planning/phases/145-bench-validation/readbacks/readback2.bin` → exit **0**, `Read complete (7.40s)`
(`logs/read_cycle2.log`). `readbacks/readback2.bin` is exactly **65536 bytes**.

```
$ cmp images/img2.bin readbacks/readback2.bin        # exit 0, no output
$ sha256sum images/img2.bin readbacks/readback2.bin
b566c7a0319cc37051ec9c92bc1faef81f75e3740c7c6c8864778a549624fd96  images/img2.bin
b566c7a0319cc37051ec9c92bc1faef81f75e3740c7c6c8864778a549624fd96  readbacks/readback2.bin
```
**Digests identical — 65536 of 65536 bytes byte-exact.** `readbacks/readback2.bin`'s digest is
appended to `SHA256SUMS.txt`; `img2.bin`'s row was already in the manifest from `145-01` and is
**unchanged**, so no duplicate row was appended (same handling as cycle 1). `sha256sum -c
SHA256SUMS.txt` from the phase directory exits **0** over all seven rows.

**The three verdicts agree. They are recorded on three separate lines anyway** (D-06).

##### The consecutive-read-back difference — asserted, not assumed

```
$ cmp -s readbacks/readback1.bin readbacks/readback2.bin ; echo $?
1
$ cmp -l readbacks/readback1.bin readbacks/readback2.bin | wc -l
65536
```
`cmp` exit **1** means *differ* (2 would mean error, and both files were `stat`-confirmed present at
65536 bytes before the compare, so a missing-file 2 cannot be misread as a pass here — an earlier
invocation of this compare in the wrong working directory produced exactly that false green and was
discarded and re-run). **All 65536 bytes changed.** The chip's contents genuinely changed between
cycle 1 and cycle 2, so a real erase-and-reprogram occurred rather than a no-op rewrite.

##### Read stability for this cycle (D-07) — measured for cycle 2 in its own right

```
$ firestarter -p /dev/ttyACM0 dev consistency-check W27C512 --runs 3 \
      --output-dir .planning/phases/145-bench-validation/runs/cycle2
```
**Exit 0.** The exit code is a three-way value — **0 = PASS, 1 = FAIL on divergent SHAs, 2 = hardware
or serial error** — so `0` specifically means the runs agreed. Verdict block verbatim from
`logs/consistency_cycle2.log`:
```
Consistency check: PASS
Chip: W27C512  Board: unknown-board  Port: /dev/ttyACM0
Runs: N=3
Distinct SHAs: 1
Output dir: .planning/phases/145-bench-validation/runs/cycle2/
```
`run_01.bin`, `run_02.bin` and `run_03.bin` all exist at exactly **65536 bytes** each.
`git check-ignore` on `runs/cycle2` reports **not ignored**. This is cycle 2's own measurement in its
own output directory — **nothing was inferred from cycle 1** (D-07). All three runs reported
`b566c7a0…`, the **same digest as `img2.bin`**, which is three further confirmations of oracle 2.

##### Frame summary for this cycle (D-10 Claim A)

Extractor self-test re-run immediately before the measurement: `SELFTEST: POSITIVE PASS`,
`SELFTEST: NEGATIVE PASS`, exit 0. The six summary values, verbatim from `logs/frames_cycle2.txt`:
```
segments=2
selected_segment=2
frames=267
intra_block_frames=64
blocks_with_multiple_updates=2
step_histogram=204:1,692:1,820:1,1023:18,1024:27,1025:17
```
**Claim A HOLDS for this cycle too, as measured, not as predicted** — 64 intra-block positions, one
per block. Corroborated independently of the extractor by 96 `DATA:` lines in the `-v` stdout capture
(32 INIT blank-check frames stepping by 2048, then 64 MAIN-phase write frames). This is the
**measured truth for cycle 2**; no predicted count was asserted. **`145-05`'s standing correction
applies: RQ-4's frames-per-block table row `100 µs (DB) → 0 frames` is stale for the shipped
firmware** — the settle increase pushed block time past the 1000 ms emission cadence.
`blocks_with_multiple_updates=2` is again **not** banked as Claim B, for `145-05`'s stated reason
(bar-latch-transition artifacts, not two firmware emissions in one block). Claim B remains `145-07`'s.

##### D-03 erase-fired corroboration — derived, not a second independent measurement

Going from `img1.bin` to `img2.bin`, **65408 of 65536 bytes — 99.8 %** — require at least one
`0`-to-`1` bit transition, which on this part only a real erase can deliver. **Re-derived on the
actual image bytes this session** rather than quoted from research: a per-byte `(~img1 & img2)`
population count over the two files on disk returns exactly 65408. A silently no-op erase would
leave those bytes unable to reach their target values and the write would have failed with
`MSG_ERR_MAX_PULSES`; it exited 0 with 0 bad bytes and the independent read-back is byte-exact.
Cycle 2's clean pass therefore **could not have been produced without a real erase**.

**Stated plainly: this is a derived corroboration of the D-03 pre-flight, not a second independent
measurement.** It reasons from the image sequence and the observed pass; it does not observe the
erase itself.

##### `--force used?` **No**

No `--force` was passed to any command in this cycle. Neither was `write -b`, `--no-blank-check`,
`--skip-erase`, `-a`/`--address` nor `-s`/`--size`.

##### Cycle 2 verdict: **PASS — byte-exact on all three oracles**

Write exit 0 with 0 bad bytes at 105.69 s, verify exit 0, independent host-side SHA compare
byte-exact over all 65536 bytes, read stability PASS at N=3 with 1 distinct SHA, consecutive
read-backs asserted to differ in all 65536 bytes. **Cycle 2 of 3. Gate 2 is not closed here.**

---

### Cycle 3 (resumed) — `145-06` Task 2

**Port identity, re-verified fresh for this task (D-19), not carried forward from cycle 2.**

```
$ ls /dev/ttyACM*                                      # exactly one device
/dev/ttyACM0
$ firestarter -p /dev/ttyACM0 fw                       # exit 0
Current firmware version: 3.0.0b17, for controller: leonardo on port /dev/ttyACM0
```
Same caveat as cycle 2: this identifies the controller and the port, never the image. The firmware
tree was re-asserted at `ebe9cb353f134d6c56a8295490142de1a43fdf8f` with **empty**
`git status --porcelain` immediately before this task; no reflash occurred in this plan.

**Seated part re-confirmed:**
```
$ firestarter -p /dev/ttyACM0 id W27C512                # exit 0
Chip ID check passed for W27C512: (main done) (0.28s)
```

---

#### `firestarter -v -p /dev/ttyACM0 write W27C512 .planning/phases/145-bench-validation/images/img3.bin`

Run from `/workspaces`, stdout to `logs/write_cycle3.stdout.log`, stderr to
`logs/write_cycle3.stderr.raw`. **No `-b`, no `--no-blank-check`, no `--skip-erase`, no `--force`,
no `-a` and no `-s`** — the full 65536 bytes, 64 blocks of 1024 B (D-04). `-v` and `-p` are group
options and precede the subcommand. Canonical cycle-3 log paths asserted absent before the run.

**Exit 0.** Wall clock 110 s (`date` delta around the invocation).

##### The three oracle verdicts — recorded separately, never merged

**Oracle 1a — the write's own verdict (firmware-side, first pass).** Verbatim from
`logs/write_cycle3.stdout.log`:
```
INFO   :EpromOperator:1982: Write to W27C512 successful (106.06s).
```
`grep -ciE "bad bytes|MAX_PULSES" logs/write_cycle3.stdout.log` → **0**.

**Oracle 1b — the verify's own verdict (firmware-side, SECOND pass).** Verbatim from
`logs/verify_cycle3.log`, exit **0**:
```
Verify for W27C512 successful (5.69s).
```
Again: `verify` shares `write`'s `_main_phase_send_data` handler and the compare happens **on the
firmware**, so this is a second firmware-side pass and **not** an independent oracle (D-06).

**Oracle 2 — the independent host-side SHA compare.** `firestarter -p /dev/ttyACM0 read W27C512
.planning/phases/145-bench-validation/readbacks/readback3.bin` → exit **0**, `Read complete (7.40s)`
(`logs/read_cycle3.log`). `readbacks/readback3.bin` is exactly **65536 bytes**.

```
$ cmp images/img3.bin readbacks/readback3.bin        # exit 0, no output
$ sha256sum images/img3.bin readbacks/readback3.bin
74c359c8d8668fdc5778270d61cc3fbef55a1027999f20c5798a54bf0f6aea01  images/img3.bin
74c359c8d8668fdc5778270d61cc3fbef55a1027999f20c5798a54bf0f6aea01  readbacks/readback3.bin
```
**Digests identical — 65536 of 65536 bytes byte-exact.** `readbacks/readback3.bin`'s digest is
appended to `SHA256SUMS.txt`; `img3.bin`'s row already existed from `145-01` and is unchanged.
`sha256sum -c SHA256SUMS.txt` exits **0** over all eight rows.

##### The consecutive-read-back difference — asserted, not assumed

```
$ cmp -s readbacks/readback2.bin readbacks/readback3.bin ; echo $?
1
$ cmp -l readbacks/readback2.bin readbacks/readback3.bin | wc -l
65536
```
Both files `stat`-confirmed present at 65536 bytes before the compare, so exit **1** is *differ* and
not a missing-file error. **All 65536 bytes changed** between cycle 2 and cycle 3.

##### Read stability for this cycle (D-07) — measured for cycle 3 in its own right

```
$ firestarter -p /dev/ttyACM0 dev consistency-check W27C512 --runs 3 \
      --output-dir .planning/phases/145-bench-validation/runs/cycle3
```
**Exit 0** — on the three-way scale (0 = PASS, 1 = FAIL on divergent SHAs, 2 = hardware or serial
error), so the runs agreed. Verdict block verbatim from `logs/consistency_cycle3.log`:
```
Consistency check: PASS
Chip: W27C512  Board: unknown-board  Port: /dev/ttyACM0
Runs: N=3
Distinct SHAs: 1
Output dir: .planning/phases/145-bench-validation/runs/cycle3/
```
`run_01.bin` through `run_03.bin` each exactly **65536 bytes**; `runs/cycle3` is **not gitignored**.
This is cycle 3's own measurement in its own directory — **not inferred from cycle 1 or cycle 2**
(D-07). All three runs reported `74c359c8…`, the same digest as `img3.bin`.

##### Frame summary for this cycle (D-10 Claim A)

Extractor self-test re-run immediately before the measurement: `SELFTEST: POSITIVE PASS`,
`SELFTEST: NEGATIVE PASS`. The six summary values, verbatim from `logs/frames_cycle3.txt`:
```
segments=2
selected_segment=2
frames=267
intra_block_frames=64
blocks_with_multiple_updates=2
step_histogram=336:1,688:1,689:1,896:1,1023:11,1024:38,1025:11,1151:1
```
**Claim A HOLDS for this cycle as measured** — 64 intra-block positions, corroborated by 96 `DATA:`
lines in the `-v` stdout. No predicted count was asserted; `145-05`'s standing correction to RQ-4's
frames-per-block table still applies. `blocks_with_multiple_updates=2` is again **not** banked as
Claim B (bar-latch-transition artifacts); Claim B remains `145-07`'s on the Gate 3 run.

##### Cycle-2-to-3 transition density

Going from `img2.bin` to `img3.bin`, **59392 of 65536 bytes — 90.6 %** — require at least one
`0`-to-`1` bit transition, re-derived on the actual image bytes this session by a per-byte
`(~img2 & img3)` population count rather than quoted from research. So cycle 3 also required a real
erase rather than a no-op rewrite. Lower than cycle 1-to-2's 99.8 %, and stated as such rather than
rounded together with it.

##### `--force used?` **No**

No `--force`, no `write -b`, no `--no-blank-check`, no `--skip-erase`, no `-a`/`--address` and no
`-s`/`--size` in this cycle.

##### Cycle 3 verdict: **PASS — byte-exact on all three oracles**

Write exit 0 with 0 bad bytes at 106.06 s, verify exit 0, independent host-side SHA compare
byte-exact over all 65536 bytes, read stability PASS at N=3 with 1 distinct SHA, consecutive
read-backs asserted to differ in all 65536 bytes.

---

### v1.31 write timing — the three measured figures, with no comparative claim

| Cycle | Image | Measured write elapsed |
|---|---|---|
| 1 | `img1.bin` | **106.06 s** |
| 2 | `img2.bin` | **105.69 s** |
| 3 | `img3.bin` | **106.06 s** |

Three full 64 KiB W27C512 writes on Leonardo at firmware `ebe9cb3`, spread **0.37 s** — this phase's
first v1.31 timing data for this operation, and the tightest thing here is the *consistency*, which
is worth more than any single figure.

**No comparative claim is made against any earlier firmware (D-08).** D-08 rejected a pre-v1.31
control run, and this milestone claims **fidelity, not improvement**. The 22.84 s pre-v1.31 figure
that appears in cycle 1's record is a *recorded historical number, not a control measurement*: it was
not taken on this part, in this session, under these conditions. **These figures are therefore not
evidence that v1.31 programs better or worse than what preceded it**, and 58.9 s of the difference is
already accounted for as the `EPROM_VPP_SETUP_US` 100 → 1000 µs settle increase shipped by a debug
session outside this phase. No datasheet-conformance claim is made in either direction.

---

---

## Progress-frame evidence (D-10 Claim A) — resumed session, MEASURED

Instrument: `.planning/phases/145-bench-validation/tools/extract_frames.py`, meta-repo bench tooling
under this phase directory and explicitly not inside either sub-repo (D-16). Its self-test was
re-run in **this** session, immediately before the measurement below, and both legs were observed:
`SELFTEST: POSITIVE PASS`, `SELFTEST: NEGATIVE PASS`, exit 0. That matters more here than it did in
Gate 0, because this session's result is a **positive** one — an instrument that can only fail to
find things is no use when it does find them.

```
$ python3 .planning/phases/145-bench-validation/tools/extract_frames.py \
      .planning/phases/145-bench-validation/logs/write_cycle1.stderr.raw \
      | tee .planning/phases/145-bench-validation/logs/frames_cycle1.txt
```

**The six summary values, verbatim from `logs/frames_cycle1.txt`:**
```
segments=2
selected_segment=2
frames=267
intra_block_frames=64
blocks_with_multiple_updates=2
step_histogram=336:1,688:2,1023:11,1024:40,1025:11
```

**D-10 Claim A, in its literal form:** *at least one bar frame reported a position that is not a
multiple of 1024.*

### Claim A verdict: **HOLDS**

`intra_block_frames=64`. Only a firmware `MSG_DATA_PROGRESS` (`0xE0`) frame can produce a
non-multiple-of-1024 position, because every host chunk hand-off lands exactly on a 1024 boundary
for a 65536-byte file on a 1024-byte-buffer board.

**The offending positions, named.** 64 of the 66 distinct positions are intra-block, one per block,
at a constant ≈688-byte offset into each block:
```
688, 1712, 2736, 3760, 4785, 5809, 6832, 7857, 8880, 9904, 10928, 11952, 12976, 14001,
15025, 16049, 17072, 18096, 19120, 20145, 21169, 22193, 23216, 24240, 25264, 26288, 27313,
28337, 29360, 30385, 31408, 32432, 33456, 34480, 35505, 36529, 37553, 38576, 39600, 40624,
41648, 42673, 43697, 44720, 45745, 46769, 47792, 48816, 49840, 50865, 51889, 52913, 53936,
54960, 55984, 57008, 58032, 59056, 60080, 61104, 62129, 63152, 64176, 65200
```
The only two boundary positions in the write bar are `0` (tqdm's initial draw) and `1024`.

**Corroborated independently of the extractor, from the `-v` stdout log.** The capture contains
**96** `DATA: n/65536` lines: the first **32** step by 2048 (`2048 … 65536`) — that is the INIT-phase
blank check, `BLANK_CHECK_CHUNK_SIZE = 2048` — and the remaining **64** are the MAIN-phase write,
beginning `688, 1712, 2736, 3760, 4785, 5809, …`. Two different artifacts of the same run, produced
by two different mechanisms (a tqdm stderr bar and a verbose stdout debug line), agree on the same
64 positions. The extractor's segment selection is confirmed correct rather than merely trusted:
`segments=2`, `selected_segment=2` discarded exactly the 32 INIT frames, so no 2048-step blank-check
frame was miscounted as intra-block write motion (Pitfall 6, T-145-28).

### RQ-4 predicted ZERO. It measured 64. Why the prediction was falsified — honestly

RQ-4's arithmetic predicted **no intra-block frame at all** at the database's 100 µs pulse:
emission is time-keyed at `EPROM_PROGRESS_EMIT_INTERVAL_MS` = **1000 ms**, `last_emit_ms` is a
function-local **re-initialised at the top of every block**, and a 1024-byte block was estimated at
**400–700 ms** — comfortably under the cadence, so the timer could never expire inside a block.

**That reasoning was correct, and it was correct about a firmware that no longer exists.** The
debug session's fix raised `EPROM_VPP_SETUP_US` from 100 µs to 1000 µs, adding ~900 µs per pulsed
byte. Measured block time is now **106.06 s / 64 = 1.657 s**, which **crosses the 1000 ms cadence**.
`floor(1657 / 1000) = 1` — exactly one emission per block, which is exactly what was measured: 64
frames across 64 blocks. The predicted offset within a block, `1024 × 1000/1657 ≈ 618` bytes, lands
close to the observed ≈688 (the residual is that a block's wall time is not purely the pulse loop —
the final full-block verify pass runs after it, so the pulse loop's own bytes-per-ms is slightly
higher than the block average).

So the null result the plan pre-authorised did not occur, and this is **not** a case of the
measurement being massaged toward the interesting answer: **the prediction was falsified by a
firmware change made outside this phase, for an unrelated reason, and the mechanism RQ-4 named is
exactly the mechanism that produced the frames.** The 1000 ms cadence and the per-block
`last_emit_ms` reset are not overturned — they are what makes it *one* frame per block rather than
several. Had the settle not been raised, RQ-4's zero would have stood.

**Standing correction for anything downstream:** RQ-4's frames-per-block table (`100 µs (DB) → 0
frames`) is **stale for the shipped firmware**. At the database pulse on `ebe9cb3` the true figure is
**1 frame per block**.

### About `blocks_with_multiple_updates=2` — stated precisely, NOT claimed as Claim B

Two blocks carry more than one distinct position: block 0 (`0`, `688`) and block 1 (`1024`, `1712`).
**These are latch-transition artifacts, not two firmware emissions inside one block.** In each pair
the lower position is a host-side draw (tqdm's initial render at `0`; the chunk hand-off boundary at
`1024`) and the upper is the firmware frame. Once `firmware_drives_bar` latched, the chunk hand-off
`progress.update()` stopped, which is why no boundary position appears after `1024` at all.

Claim B is worded as *"≥ 2 distinct positions inside the same `n // 1024` bucket"*, and read with
maximum literalism this measurement satisfies it for two blocks. **This record does not claim Claim
B on that basis.** Claim B exists to demonstrate *multiple firmware emissions within a single
block*, and mixed-provenance pairs at the moment the bar changes hands are not that. Claim B and its
verification-map row 24 remain **`145-07` Task 2's to measure** on the Gate 3 `--pulse-us 4688` run,
where ~5 firmware emissions per block are expected on all four blocks. Recording the literal
satisfaction here and declining to bank it is the honest form.

### The constraint that makes any of this reachable

The `MSG_DATA_PROGRESS` emission is guarded by `#ifndef SERIAL_ON_IO` (`eprom.cpp:398,403`) — it is
**`leonardo`-only** (plus `native`) and is **compiled out on `SERIAL_ON_IO` targets**, i.e. `uno` and
`uno328pb`. This measurement exists because this phase runs on a Leonardo; on an Uno-class board it
would be **structurally unavailable**, not merely absent. Nothing here generalises to Uno-class
hardware.

No source file was edited to make a frame appear (D-16); `git -C /workspaces/firestarter status
--porcelain` is empty. No cycle was retried, and nothing was re-run to obtain a more agreeable
number — the extractor was run **once**, over the capture of the **first and only** write in this
session.

---

## D-11 — CAP-03 advertised-budget survival, claimed as free evidence

**The claim:** a 64 KiB write either completes or the host times out. **It completed** — exit 0,
`Write to W27C512 successful (106.06s).` — so the CAP-03 advertised-budget path held on real
hardware. This costs no extra bench time; it is the same run recorded above, read for a second
purpose.

| Figure | Value |
|---|---|
| Measured elapsed (host's own success line) | **106.06 s** for 65536 bytes / 64 blocks |
| Measured per-block time | **1.657 s** |
| CAP-03 advertised budget, W27C512 @ 100 µs, 1024-byte block | **8 s** (per block) |
| Legacy fallback the advertised budget replaces | **120 s** |
| Margin actually used | ~21 % of the 8 s advertised budget |

**The non-claim, stated plainly: nothing logs the advertised budget.** The host decodes it silently
from the `MSG_OK_READY` capability blob; no line in `logs/write_cycle1.stdout.log` prints `8`,
prints a budget, or names CAP-03 at all — the `-v` capture was read for one and there is none.
**The evidence is the completion itself, and no attempt was made to observe the number in the logs**
(Pitfall 9 explicitly warns against chasing it there). This record therefore claims *the budget path
held*, and does **not** claim *the budget was observed to be 8 s* — the 8 s is computed, cited from
RQ-4's table, not measured.

**An honest qualifier on how sharp this evidence is.** 1.657 s per block sits inside **both** the 8 s
advertised budget and the 120 s legacy fallback, so this run does not discriminate between them: it
would have completed even if the advertised budget had never been implemented. It is real evidence
that the path does not *break* a long write, and it is **not** evidence that the advertised budget is
what carried it. The sharp discriminating case is a run whose budget exceeds 120 s, which is exactly
what Gate 3's `--pulse-us 4688` (244 s advertised) is for — `145-07`'s, not this plan's. The settle
increase did make this figure meaningfully longer than the ~40 s the pre-settle fix produced, which
narrows the margin without crossing anything.

**143 H4's long-write half: DISCHARGED by this run**, with the qualifier above attached. Phase 146
no longer carries it as unproven. H4's `--pulse-us`-above-4687 µs half remains open and is Gate 3's.

**Verification-map rows discharged by this section and the one above:** row 22 (D-11 long-write free
evidence) and row 23 (D-10 Claim A). Rows 24–27 remain Gate 3's and `145-08`'s.

---

# GATE 2 CLOSURE — `145-06` Task 3

## The per-cycle oracle table (D-06) — nine cells, never merged

| Cycle | Image | **Oracle 1a** — write's own verdict (firmware-side, 1st pass) | **Oracle 1b** — verify's own verdict (firmware-side, 2nd pass) | **Oracle 2** — independent host-side SHA compare |
|---|---|---|---|---|
| **1** | `img1.bin` | exit **0** — `Write to W27C512 successful (106.06s).`, 0 bad bytes | exit **0** — `Verify for W27C512 successful (5.68s).` | exit **0** — `f72489604bfe…` == `f72489604bfe…`, **65536/65536** |
| **2** | `img2.bin` | exit **0** — `Write to W27C512 successful (105.69s).`, 0 bad bytes | exit **0** — `Verify for W27C512 successful (5.69s).` | exit **0** — `b566c7a0319c…` == `b566c7a0319c…`, **65536/65536** |
| **3** | `img3.bin` | exit **0** — `Write to W27C512 successful (106.06s).`, 0 bad bytes | exit **0** — `Verify for W27C512 successful (5.69s).` | exit **0** — `74c359c8d866…` == `74c359c8d866…`, **65536/65536** |

All **nine** cells are clean. The columns stay separate because D-06's point is that a *disagreement*
must be visible; **oracle 1b is not independent** — `verify` shares `write`'s `_main_phase_send_data`
handler and the firmware performs the compare — so the independence in this table lives entirely in
the oracle-2 column.

## The D-09 verdict

**The pass rule: 3/3 byte-exact on BOTH oracles, with exactly one clean re-seat allowed across the
whole of Gate 2.**

**Result: 3/3 on both oracles.** Three cycles, three distinct images, each byte-exact on the
firmware-side pair and on the independent host-side compare. In D-14's vocabulary Gate 2 is
**`validated`**. D-14 admits only `validated`, `skipped-with-reason` or `fail` — no `partial` and no
`inconclusive` — and nothing here needed softening, which is the only circumstance in which that
taxonomy costs nothing to honour.

## The D-09 re-seat ledger — stated explicitly, either way

**The allowance was NOT used. It remains UNCONSUMED at Gate 2's close.**

Said in as many words: **no re-seat was required at any point in Gate 2, no re-seat occurred, and
D-09's single allowance was never spent.** The chip was seated once and not touched again.

The ledger's full history, so the "unconsumed" claim is auditable rather than asserted:

| Event | Re-seat? | Allowance state |
|---|---|---|
| Session 1, cycle 1 attempt 1 — `Byte at 0x000000 failed to program within 25 pulses`, exit 1 | **No** | The allowance was **offered and declined**. D-09 requires attribution to a *named physical cause*; the operator inspected the bench and reported none apparent, and selected the D-13 halt path. Debug session `w27c512-program-fail-byte0` later proved the cause was a **firmware defect** (Phase 141 deleted the only `CTRL_VPE_ENABLE` assert in the EPROM write path), vindicating the refusal. **Unconsumed.** |
| Session 2, cycle 1 (`145-05`) | **No** | Ran clean first time on the fixed build. **Unconsumed.** |
| Session 2, cycle 2 (`145-06` Task 1) | **No** | Ran clean first time. **Unconsumed.** |
| Session 2, cycle 3 (`145-06` Task 2) | **No** | Ran clean first time. **Unconsumed.** |

**Each of the three counted cycles was written exactly once.** There was no retry, silent or
documented, and no source file was edited to make any result appear. Session 1's failure is **not
discarded** — it stands in this record as a genuine failure with a genuine cause, and it is *not*
one of Gate 2's three cycles.

## The no-`--force` source assertion (D-17) — over a counted denominator

This is a claim about the artifact, so it is stated with the count it covers rather than as an
unbounded "all".

**Denominator: 17 recorded silicon-touching `firestarter` invocations across Gates 0, 1 and 2** —
**4** appearing as their own command-line subsection heading, and **13** appearing as `$ firestarter …`
lines inside fenced blocks.

The four command-line headings, verbatim (all at `####` depth):

```
  [h1] line  535 — firestarter -p /dev/ttyACM0 erase W27C512 -b               (D-03 erase pre-flight)
  [h2] line 1032 — firestarter -v -p /dev/ttyACM0 write W27C512 .../img1.bin  (cycle 1)
  [h3] line 1164 — firestarter -v -p /dev/ttyACM0 write W27C512 .../img2.bin  (cycle 2)
  [h4] line 1316 — firestarter -v -p /dev/ttyACM0 write W27C512 .../img3.bin  (cycle 3)
```

Each is a `####`-depth heading at the line given. They are transcribed here **indented and without
their leading hashes on purpose**: quoting them at column 0 with their `####` intact would make the
counting grep below match its own evidence block and report 8 where the truth is 4. That is not a
cosmetic detail — it is the difference between an assertion that measures the record and one that
measures itself.

**The checks, and their results:**

```
$ grep -E "^#{2,6} .*firestarter " 145-BENCH-LOG.md | wc -l                                  → 4
$ grep -E "^#{2,6} .*firestarter " 145-BENCH-LOG.md | grep -cE -- "--force|--skip-erase|--no-blank-check"  → 0
$ grep -E "^#{2,6} .*firestarter .*write " 145-BENCH-LOG.md | grep -cE -- " -b| -a | -s "     → 0
$ grep -cE "^\$ firestarter " 145-BENCH-LOG.md                                                → 13
$ grep -E "^\$ firestarter " 145-BENCH-LOG.md | grep -cE -- "--force|--skip-erase|--no-blank-check"        → 0
```

**None of the 17 contains `--force`, `--skip-erase` or `--no-blank-check`; no `write` carries `-b`,
`-a` or `-s`.** Every `--force` string anywhere in this record was checked individually and every one
is a *negation or a declaration* (`--force used? No`, "no `--force` was passed", the verification-map
rows), never an executed command line.

**Two `-b` uses exist and both are legitimate, named here so the zero-count is not read as sleight of
hand:** `erase W27C512 -b` and `blank W27C512`. On `erase`, `-b` is the *blank-check-after* flag —
the opposite polarity to `write -b`, which sets `FLAG_SKIP_ERASE`. **No `write` in this phase carried
`-b`.** That distinction is load-bearing: `write -b` skips the erase, not merely the blank check, and
still reports "successful" over a corrupted part — the exact false-green this milestone exists not to
commit.

**What the ban protects — the two mechanisms, named:**

1. **`eprom_check_vpp` (`firestarter/src/proms/eprom.cpp:525-586`) hard-aborts when the measured rail
   exceeds `handle->vpp_mv + 500` — 12500 mV for this part** — returning `MSG_ERR_VPP_HIGH` and
   ending the run. **`--force` converts that abort into a `MSG_WARN_VPP_HIGH` warning and proceeds**,
   which on this specific board matters more than usual: the W27C512's `VPP is high: 13.1V > 12.0V`
   guard has historically been force-bypassed here, and the operator's standing "use force and ignore
   vpp" permission was **withdrawn for this phase** by D-17.
2. **The chip-id check likewise aborts without `--force`.** That abort is what caught the v1.18
   Phase-97 wrong-part mix-up; bypassing it risks driving one part's algorithm and VPP into another's
   silicon.

**Scope limit, stated rather than glossed:** this assertion covers **Gates 0, 1 and 2 only**. **Gate 3
has not been run**, so no Gate-3 command line exists to assert over. `145-07` must extend this
assertion over its own runs; it is not covered here.

**A divergence from this plan's own acceptance grep, recorded rather than silently satisfied.**
`145-06` Task 3 specifies `grep -cE "^### .*firestarter .* (write|verify|read|erase|id|dev
consistency-check) "`. That expression returns **0** against this record, and would have done so
however the work went: every command-line heading in this log is at `####` depth, not `###`, a
convention set in Gate 1 long before this plan was written. The plan's regex is **broken as a
gate — it cannot distinguish a compliant record from an empty one**. It was not "made to pass"; the
heading depths were left as they are and the assertion is made with the corrected `^#{2,6} `
expression above, with the original stated here so the substitution is visible.

**A second limit worth being straight about:** not every silicon-touching invocation in this phase is
a *heading* — 13 of the 17 are fenced-block lines, and cycle 1–3's `verify` and `read` commands are
quoted inline in prose as well. The claim honoured here is that **every one of them is recorded
verbatim somewhere in this log and all 17 were checked**, which is weaker than "every one is its own
heading" but is what the record actually supports.

## D-07 summary — three measurements, none inferred

Read stability was measured **per cycle, three times, each in its own output directory**, and **not
inferred from any single measurement**:

| Cycle | Output dir | Verdict | Runs | Distinct SHAs | Digest |
|---|---|---|---|---|---|
| 1 | `runs/cycle1/` | **PASS** (exit 0) | N=3 | **1** | `f72489604bfe…` = `img1.bin` |
| 2 | `runs/cycle2/` | **PASS** (exit 0) | N=3 | **1** | `b566c7a0319c…` = `img2.bin` |
| 3 | `runs/cycle3/` | **PASS** (exit 0) | N=3 | **1** | `74c359c8d866…` = `img3.bin` |

Nine read-back files, all 65536 bytes, all committed. In every cycle the three runs agreed **with the
source image** as well as with each other — `dev consistency-check` only asserts the latter, so the
former is a free extra confirmation of oracle 2 each time.

**Why the per-cycle separation matters and is not ceremony:** program repeatability and read
repeatability are **different failure modes**, and this project has a worked example — `0x08`
(AM27C020) is precisely a part that **reads stably and programs unreliably** (Phase 99: write#1
60/64, write#2 0/64, at stable idle VPP). A single end-of-gate stability check would have passed on
that part too. Three separate measurements can catch a part that degrades across cycles; one cannot.

## Gate 2 verdict: **VALIDATED**

**Gate 2 verdict:** Three full 64 KiB cycles were written on three distinct images (`img1.bin`,
`img2.bin`, `img3.bin`), all **3/3 byte-exact on both oracles** — the firmware-side write/verify pair
and the independent host-side SHA compare, nine clean cells in total; per-cycle read stability
**PASS at N=3 with 1 distinct SHA** in all three cycles; **no `--force`** in any of the 17 recorded
invocations; **D-09's single re-seat allowance UNCONSUMED**, no re-seat performed and each cycle
written exactly once; and **the erase demonstrably fired**, corroborated by the transition densities
(**65408/65536, 99.8 %** of cycle-1→2 bytes and **59392/65536, 90.6 %** of cycle-2→3 bytes require at
least one `0`→`1` transition, which no silent no-op erase can deliver) together with consecutive
read-backs asserted to differ in **all 65536 bytes** both times. **Gate 3 (`--pulse-us 4688`) is next
and is separately authorized** — it is `145-07`'s, it is not covered by Gate 2's spend authorization,
and it has not been run.

### What this verdict does NOT cover — stated at the point of closure

- **The build under test carries a known, un-adjudicated band breach.** `ebe9cb3` is **+96 B** against
  the 0 B leonardo must-not-grow band (MERGE-05). Nothing in this plan re-anchored a baseline, widened
  a band or touched `test_policy_merge05_fires_on_the_current_tree`. **Gate 2's result was obtained on
  a build with an open breach**, and a reader must not discover that elsewhere.
- **The intermittent single-byte margin failure is mitigated, not explained.** The debug session's
  1000/100 µs settle values stopped it recurring; Gate 2's three cycles make 15 consecutive clean
  cycles on this part. **Fifteen clean cycles is not a root cause.** Nobody knows whether the original
  cause was an under-settled route, a marginal cell, or program-window VPP droop.
- **Program-window VPP under load was never measured** — the standing Phase-97 DTR-reset tooling gap.
  Every VPP figure in this record is an *idle* sample.
- **No comparative claim against any earlier firmware** (D-08), and **no datasheet-conformance claim**
  in either direction.
- **Nothing about `0x08` or `0x0B`**, which remain skipped-with-reason, and **nothing about Uno-class
  boards** — the progress emission is compiled out on `SERIAL_ON_IO` targets.
- **Claim B is not claimed**, in any of the three cycles, despite `blocks_with_multiple_updates=2`
  appearing in all three. It is `145-07`'s on the Gate 3 run.
- **No requirement checkbox was flipped by this plan.** `BENCH-01` is multi-plan; ticking is
  centralised in `145-09` behind its own blocking operator gate.



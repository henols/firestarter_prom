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

| Field | Value | Source |
|---|---|---|
| Controller identity | `leonardo` | `firestarter -p /dev/ttyACM0 fw` |
| Port | `/dev/ttyACM0` (CLI-reported; same port before and after the upload's 1200-baud touch reset re-enumeration) | `firestarter -p /dev/ttyACM0 fw` |
| Hardware revision (reported) | `Rev 2.0-class, Override HW: Rev 2.0-class` — **NOT authoritative for distinguishing Rev 2.0 from Rev 2.2 from the modified Rev 0**; the EEPROM `hw_revision` byte cannot make that distinction. The operator's silkscreen reading (row below) is the authority. | `firestarter -p /dev/ttyACM0 hw` |
| Shield silkscreen (operator eyes-on) | **Rev 2.0** — operator's verbatim answer: "Leonardo,  Rev 2.0, w27c512 seated" | operator |
| Seated chip (operator confirmed) | **W27C512** (operator wrote lowercase `w27c512`) — operator's verbatim answer: "Leonardo,  Rev 2.0, w27c512 seated" | operator |
| Part expendable (operator confirmed) | **NOT separately confirmed.** The operator's exact words were "Leonardo,  Rev 2.0, w27c512 seated" — the word "expendable" does not appear and expendability was not separately stated. This is recorded as answered-by-implication only: the prompt they responded to stated the part's contents will be bulk-erased, and the operator seated the part and replied "continue". **Carry-forward: explicit expendability confirmation is REQUIRED before 145-04's D-03 erase pre-flight** (the first destructive act; this Gate 1 identity check spends nothing). | operator (implied only — see note) |
| R1 readback | `270000` | `firestarter -p /dev/ttyACM0 config` |
| R2 readback | `44000` | `firestarter -p /dev/ttyACM0 config` |
| Firmware version string | `3.0.0b17` — see the D-18 caveat immediately below; the version string identifies nothing on its own | `firestarter -p /dev/ttyACM0 fw` |
| Firmware commit under test | `a594173d2bbbabe74e6a470b4751528435246326`, branch `gsd/v1.31-27c-programming-algorithm-fidelity` | `git -C /workspaces/firestarter rev-parse HEAD` / `--abbrev-ref HEAD` |
| Firmware working tree clean | Empty (0 lines), asserted both immediately before `pio run -e leonardo --target size` and immediately after the upload | `git -C /workspaces/firestarter status --porcelain` |
| Flash bytes measured | **26906 bytes program (82.1 % Full against the 32768 B part)**, **2014 bytes data (78.7 % Full)** — equal to `size_baseline.json`'s leonardo record (`flash_used 26906`, `ram_used 2014`). Delta vs baseline: **0 B** against the 0 B leonardo must-not-grow band. Reason: a phase that compiles nothing new cannot move flash (D-16). Against `flash_total` 28672 B (bootloader excluded), the baseline's own figure gives **93.8 %** and **1766 B** of headroom — this is the figure PlatformIO's own `pio run` output (not `--target size`) reported directly: `Flash: [========= ]  93.8% (used 26906 bytes from 28672 bytes)`. Both the 82.1 % (against the 32768 B part) and the 93.8 % (against `flash_total` 28672 B, bootloader excluded) figures are correct; this record names the 93.8 % / 1766 B figure as the one it is quoting for the H7 headroom hand-off. | `pio run -e leonardo --target size` (log: `/tmp/gsd-145/size_leonardo.log`) and `pio run -t upload -e leonardo`'s own pre-upload size banner |
| avrdude verified byte count | **26906** — matches expectation exactly. avrdude tool version actually invoked this session: **`tool-avrdude @ 1.60300.200527 (6.3.0)`** (the PlatformIO package line printed at the top of the upload log) — **not** 8.1; RQ-5's assumption A3 about 8.x wording did not apply this session, but the log was still captured whole and read rather than grepped with a hard-coded pattern, per the plan's prohibition. Verbatim lines read from `/tmp/gsd-145/upload_leonardo.log`: `avrdude: 26906 bytes of flash written` and `avrdude: 26906 bytes of flash verified`. | `/tmp/gsd-145/upload_leonardo.log` (not committed; byte count quoted here per plan) |
| VPP target | NOT YET RUN | plan (D-17) |
| VPP confirmation read | NOT YET RUN | `timeout -s INT N firestarter vpp` (single sample) |
| `--force used?` | NOT YET RUN | source assertion |
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
NOT YET RUN — determine, on this bench, whether plain `write` erases the seated W27C512 before any
Gate 2 cycle is spent. If it does not, the fallback is a pure 1→0 program proof; `-b`/`--skip-erase`
is never used as a workaround (D-03).

**Gate 1 identity-half verdict (145-03, Tasks 1–3):** Five conditions cleared this plan —
(1) right board, by the operator's own silkscreen reading, `Rev 2.0`; (2) right part, by chip-id
`0xda08`, confirmed via `firestarter id W27C512` (exit 0) and corroborated by `firestarter info
W27C512`; (3) right build, by firmware commit `a594173d` plus the avrdude-verified byte count
`26906`, never by the `3.0.0b17` version string alone; (4) clean tree, `git status --porcelain`
empty both before and after the build and upload; (5) zero flash growth, `26906`/`2014` matching
`size_baseline.json` exactly, with the MERGE-05 anchor-move disclosure stated rather than an
unqualified compliance claim. **VPP and the D-03 erase-capability pre-flight are explicitly
`NOT YET RUN` and belong to `145-04`** — this plan does not close them and does not write a full
`Gate 1 verdict:` line; that line is `145-04 Task 3`'s to write once VPP and the pre-flight are
done. Also outstanding for `145-04`: the explicit, separately-stated expendability confirmation
carried forward from Task 1 (see the Part-expendable identity row above) — required before the
D-03 pre-flight, the phase's first destructive act.

**Gate 1 verdict:** NOT YET RUN — VPP and the D-03 pre-flight remain outstanding; see the
identity-half verdict immediately above for what this plan (145-03) did clear.

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

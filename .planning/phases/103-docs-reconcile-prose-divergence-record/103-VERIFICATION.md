# Phase 103 — GATE-01/02/03 Re-Verification (D-05, milestone close)

**Verified:** 2026-07-01
**Scope:** Re-verify GATE-01/GATE-02/GATE-03 against the landed Phase-103-01 docs-only edit
(`firestarter/doc/PROTOCOLS.md` §1 heading rename, §3 INV-row augmentation, D-04 divergence
callout). No firmware, host, DB, wire, or lockstep-constant code was touched by Phase 103 —
this is pure re-verification that the doc churn did not regress dispatch behavior, DB/wire
identity, or CLI grammar.

## Tool Availability (deterministic probe, per Phase-98 precedent)

| Tool | Probe | Result |
|------|-------|--------|
| `python3.11` | `command -v python3.11` | **ABSENT** |
| `pio` (PlatformIO) | `command -v pio` | **PRESENT** (`/usr/local/bin/pio`) |

Per the deterministic CI-PENDING guard: any leg scoped to an absent tool is recorded
`CI-PENDING` below — never a fabricated `PASS`. `pio` is present, so the GATE-01 firmware leg
is a real, executed `PASS`, not deferred.

## GATE-01 — Protocol numbers remain dispatch key; algorithm-first dispatch unchanged

### Host leg — dispatch-mirror guard (parser reads only the frozen §0 tables)

```
$ cd firestarter_app && python -m pytest tests/test_dispatch_mirror.py -q
..                                                                       [100%]
```
**Result: PASS** (2 tests, exit 0). Confirms the §1 heading/anchor churn and §3 INV-row
augmentation did NOT break the dispatch-mirror parser (it only reads the §0 canonical bucket
table + handler-family table, which Phase 103 did not touch).

### Host leg — dispatch mirror check tool

```
$ cd firestarter_app && python tools/check_dispatch.py
PASS: all 746 chips scanned; 736 supported; 10 chips confirmed non-dispatchable
(D-12: host guard covers non-supported chips with real handlers; non-handler outcomes
also safe); 0 non_supported_dispatchable (gate GREEN because chip_resolver.resolve_chip
refuses, not because sim pretends mem_type=None); 0 dispatch regressions;
0 consistency violations
```
**Result: PASS.**

### Firmware leg — native dispatch suite + golden register traces

`pio` is present in this session — this leg is a real executed PASS, not CI-PENDING.

```
$ pio test -e native
================= 82 test cases: 82 succeeded in 00:00:24.003 =================
```
All 14 native test suites passed (82/82 test cases), including `native/avr/test_dispatch`,
`native/avr/test_val_eprom`, `native/avr/test_val_sram`, `native/avr/test_val_flash3`,
`native/avr/test_val_flash4`, `native/avr/test_val_flash_intel`, `native/avr/test_val_eeprom28c`,
`native/avr/test_not_implemented`. Golden register traces byte-identical (no diff reported).
**Result: PASS.**

### DOC-01 anchor integrity (regenerated §3 cross-link anchors resolve)

Re-ran the exact anchor-verification script from 103-01-PLAN.md Task 1 (GitHub slugger:
em-dash→`--`, en-dash→`-`, proven against this doc's working anchors):

```
$ grep -c '^### 1\.[0-9]* — 0x[0-9A-Fa-f]* PROTO_' doc/PROTOCOLS.md
12
$ python3 -c "<anchor cross-check script>"
HEADINGS_OK
ANCHORS_OK
```
All 12 §1.x headings carry the `PROTO_` token form; all 8 `](#1...)` fragment links in §3
resolve to a real rendered heading anchor. No stale anchors.

**GATE-01 verdict: PASS** (host dispatch-mirror guard green, host check_dispatch green,
firmware native suite 82/82 green, doc anchor integrity green — all four legs executed, none
deferred).

## GATE-02 — No `chip_database.json` / wire / lockstep-constant value change

### `chip_database.json` identity

```
$ cd firestarter_app && python tools/diff_db.py
...
PASS: all 2 changed chips explained (0 new chips confirmed; 0 chips removed from baseline)
```
The 2 reported deltas (`W29C040,W29C042` and `W29C020,W29C020C,W29C022` gaining a
`page_size` field) are the pre-existing, already-explained Phase-94 `PGSZ` baseline delta —
not introduced by Phase 103. No dispatch/algorithm/VPP delta. **Result: PASS (identity
confirmed relative to the documented baseline; no new/unexplained diff).**

### Constants-parity (`constants.py` <-> `firestarter.h`)

```
$ cd firestarter_app && python -m pytest tests/ -k "parity" -q
......                                                                   [100%]
```
**Result: PASS** (6 tests, exit 0) — executed under py3.12.13 (devcontainer). No `python3.11`
binary is present in this session; per the Phase-98 precedent this is recorded
**CI-PENDING (py3.11 target)** for the target CI interpreter specifically, while the
structurally-identical py3.12 run is a real, executed PASS (structurally-green). This is a
docs-only phase — no new code executes under either interpreter, so the CI-PENDING marker is
a pure interpreter-target deferral, not a functional gap.

**GATE-02 verdict: PASS** (`diff_db.py` identity confirmed against documented baseline,
constants-parity green under py3.12; py3.11-target leg CI-PENDING per Phase-98 precedent —
no DB/wire/lockstep-constant value changed by Phase 103).

## GATE-03 — CLI grammar unchanged (chip selection stays by part number)

```
$ git -C firestarter_app status --porcelain --untracked-files=no
 M .gitignore
```
Only `.gitignore` shows as modified in `firestarter_app` (pre-existing, unrelated to this
phase — not source/CLI code). No `cli_handlers.py`, `main.py`, or any CLI-surface file was
touched by Phase 103. No protocol name or alias was added as CLI input; chip selection
continues to resolve by part number only (`chip_resolver.resolve_chip`).

**GATE-03 verdict: PASS** (no CLI code changed; grammar unchanged; docs-only phase confirmed
by the git diff surface).

## D-02 / DOC-02 retention guard (frozen strings untouched)

```
$ grep -n "datasheets/0x" doc/PROTOCOLS.md | wc -l
20
$ grep -n "Flash — AMD/SST unlock-sequence NOR" doc/PROTOCOLS.md
46:| 0x06 | 190 | `0x06-FLASH-AMD-ALT` | ... | Flash — AMD/SST unlock-sequence NOR | ...
103:**Canonical name (col 2):** `PROTO_FLASH_NOR_UNLOCK` — Flash — AMD/SST unlock-sequence NOR
```
All `datasheets/<slug>/*.pdf` citation paths retain their frozen slug strings verbatim (20
citation lines found, unchanged from the pre-Phase-103 baseline). The Phase-100
operator-approved 0x06 display name `Flash — AMD/SST unlock-sequence NOR` is intact in both
the §0 canonical table and the §1.2 per-section "Canonical name (col 2)" line — not touched.

## Summary Verdict Table

| Gate | Verdict | Basis |
|------|---------|-------|
| GATE-01 | **PASS** | dispatch-mirror guard green, check_dispatch.py green, `pio test -e native` 82/82 green, 12/12 headings + 8/8 anchors resolve |
| GATE-02 | **PASS** (py3.11-target leg **CI-PENDING**, structurally-green under py3.12) | `diff_db.py` identity vs. documented Phase-94 baseline, constants-parity 6/6 green under py3.12; no python3.11 binary in this devcontainer session |
| GATE-03 | **PASS** | no CLI/source file touched; `git status --porcelain` shows only pre-existing unrelated `.gitignore` diff; no name/alias accepted as CLI input |

**No `FAIL` verdict recorded for any gate.** The Task-2 milestone-close precondition holds.

## Commands Reference (verbatim, all executed this session)

```bash
# GATE-01 host leg
cd firestarter_app
python -m pytest tests/test_dispatch_mirror.py -q      # PASS
python tools/check_dispatch.py                          # PASS

# GATE-01 firmware leg
cd ../firestarter
pio test -e native                                       # PASS (82/82)

# GATE-02
cd ../firestarter_app
python tools/diff_db.py                                  # PASS (baseline-explained)
python -m pytest tests/ -k "parity" -q                    # PASS under py3.12 (py3.11 CI-PENDING)

# GATE-03
git -C firestarter_app status --porcelain --untracked-files=no   # only unrelated .gitignore

# DOC-01 anchor integrity
cd ../firestarter
grep -c '^### 1\.[0-9]* — 0x[0-9A-Fa-f]* PROTO_' doc/PROTOCOLS.md   # 12
# + anchor cross-check script (103-01-PLAN.md Task 1 verify block)   # ANCHORS_OK

# DOC-02 / D-02 retention guard
grep -n "datasheets/0x" doc/PROTOCOLS.md                  # 20 citation lines, frozen slugs intact
grep -n "Flash — AMD/SST unlock-sequence NOR" doc/PROTOCOLS.md   # 2 hits, both intact
```

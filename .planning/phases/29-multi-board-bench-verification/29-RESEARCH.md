# Phase 29: Multi-Board Bench Verification - Research

**Researched:** 2026-05-22
**Domain:** Operator-on-bench EPROM-read verification; local-sideload firmware deployment; evidence-accretion documentation
**Confidence:** HIGH

## Summary

Phase 29 is the **local-sideload operator-on-bench acceptance gate** for the v1.6 read-bug fix. There is no source-of-truth code to write — the firmware fix already landed in Phase 28 on `firestarter/v1.6-read-bug` (tip `4f205e58`, LOCAL only) and the host CLI diagnostic shipped in Phase 26 on `firestarter_app/v1.6-read-bug` (tip `c057fe2`). The phase has two waves: (1) a desk-side scaffold + local build wave (`autonomous: true`) that produces three `.hex` artifacts via `pio run -e <env>` and appends empty scaffold sections to `.planning/v1.6-EVIDENCE.md` + `.planning/v1.5-BENCH-RESULTS.md`; and (2) an operator-on-bench wave (`autonomous: false`) that sideloads firmware per board and runs three verification axes (full-chip consistency-check N=5, 1KB shell-loop N=5, BENCH-02 write→read→verify).

The research surfaces five high-value facts the planner needs:

1. **PIO upload protocols differ per env** — `arduino` for Uno (115200), `avr109` for Leonardo (57600, with `use_1200bps_touch: true` handled automatically), `urclock` for uno328pb (115200). The Leonardo's 1200-baud touch reset is fully PIO-managed; no operator intervention.
2. **EVIDENCE.md line 186 is already the canonical anchor** — verified verbatim as `<!-- Phase 29 inverts here: ## Phase 29 — Post-fix Consistency-Check Verification (YYYY-MM-DD). Same 9-column row schema; Verdict cells flip from FAIL to PASS, SHAs distinct cells go from N to 1. -->`. Wave A inserts immediately after this comment (line 187+).
3. **The `firestarter write` subparser has NO `-e` (erase-first) flag** — CONTEXT.md D-06 is incorrect on this point. The actual flags are `-b/--no-blank-check` (skip blank check AND erase) and `-f/--force`. By default, `firestarter write SST27SF512 <bin>` attempts blank-check + erase; the erase step is where v1.5 BENCH-02 saw `ERROR: Not supported` per the SST27SF512 misclassification.
4. **`update_version.py` does NOT run automatically on `pio run`** — only `name_firmware.py` runs as a pre-script. Local builds emit `version 3.0.0b4, controller <board>` (stale tag, no `+local` / `+phase29` suffix). The commit SHA `4f205e58` + the `.hex` SHA-256 are the unambiguous local-build identifiers; the version string is informational only.
5. **All three local `.hex` artifacts already exist on disk** at `firestarter/.pio/build/<env>/firestarter_<env>.hex` (built 2026-05-21 from tip `4f205e58`). Sizes match Phase 28 D-07 table exactly: uno=62,617 B, leonardo=68,917 B, uno328pb=62,854 B. Wave A's `pio run` invocations will be no-op rebuilds (or re-link only) unless the operator touched sources between phases.

**Primary recommendation:** Plan Wave A as four serial tasks (build×3 + host-install + scaffold-append + SHA-256 capture); plan Wave B as one task per board×axis (3 boards × 3 axes = 9 verification cells, plus 1 pre-flight hardware-metadata snapshot task and 1 verifier hand-off task). Treat CONTEXT.md D-06's `-e` reference as a verbal shorthand — the actual command is `firestarter write SST27SF512 <image>.bin` (no `-e`); operator falls back to `-b` (skip blank-check/erase) if the default erase path fails with `ERROR: Not supported`.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**D-01: Local-sideload reflash-then-test; fall back to code-equivalence DEFERRAL if sideload confirms misidentification (uno328pb row).**
- Procedure: sideload locally-built `firestarter_uno328pb.hex` via `pio run -e uno328pb -t upload --upload-port /dev/ttyUSB0 -d firestarter/` from meta-repo root. Fallback: `avrdude -p atmega328pb -c urclock -b 115200 -P /dev/ttyUSB0 -U flash:w:firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex:i`.
- Post-flash, run `firestarter -p /dev/ttyUSB0 fw`. Case A (reports `uno328pb`): full verification. Case B (reports `uno` OR avrdude signature mismatch on 328PB): mark row DEFERRED with code-equivalence rationale per Phase 28 hex-size table (uno328pb Δ=0).

**D-02: Local PIO build + `pio -t upload` (or `avrdude -c urclock`) sideload from `firestarter/v1.6-read-bug` LOCAL branch. NO beta merge in Phase 29.**
- Wave A builds: `pio run -e uno | leonardo | uno328pb` (3 separate invocations). Produces `.pio/build/<env>/firestarter_<env>.hex` for each board.
- Host CLI: `cd firestarter_app && pip install -e .` from `v1.6-read-bug` checkout.
- Wave B sideload commands (per board):
  ```bash
  cd firestarter && pio run -e uno -t upload --upload-port /dev/ttyACM0
  pio run -e leonardo -t upload --upload-port /dev/ttyACM1
  avrdude -p atmega328pb -c urclock -b 115200 -P /dev/ttyUSB0 \
    -U flash:w:.pio/build/uno328pb/firestarter_uno328pb.hex:i
  ```
- Verify each board post-flash: `firestarter -p /dev/ttyXXX fw`.
- No update_version.py invocation; no version bump.

**D-03: Uniform N=5 on every participating board.** Every verification axis (full-chip consistency-check, 1KB shell-loop) uses `--runs 5` / `seq 5`. EVIDENCE.md "N" column = 5 in every Phase 29 row.

**D-04: Two-plan structure — 29-01 (desk-side local build + scaffold, `autonomous: true`) + 29-02 (operator-on-bench, `autonomous: false`). NO merge/promotion in either plan; Phase 30 owns that.**
- 29-01: ~5 min. Three `pio run` + `pip install -e .` + EVIDENCE.md + BENCH-RESULTS scaffold + pre-flight checklist + per-board build hash record (SHA-256 of each .hex).
- 29-02: ~60-90 min. Operator-on-bench session: sideload per board + hardware metadata snapshot + 3-axis verification + scaffold fill + Case A/B branch for uno328pb + green-verdict hand-off to Phase 30.
- Plan dependency: 29-01 → 29-02.

**D-05: Operator shell-loop with `sha256sum` for VERIFY-03 — reuses existing `dev read -s 1024` path; no new code.**
- Per-board: `for i in $(seq 5); do firestarter -p /dev/ttyXXX dev read W27C512 -s 1024 -a 0 /tmp/r1k_<board>_$i.bin; done; sha256sum /tmp/r1k_<board>_*.bin`
- Expected: 5 identical SHA-256s.

**D-06: SST27SF512 on Leonardo for the BENCH-02 cycle. Single chip, single board, single row in `.planning/v1.5-BENCH-RESULTS.md`.**
- Procedure: `firestarter -p /dev/ttyACM1 write -e SST27SF512 <image>.bin` → fallback to `-b` (small-window write per v1.5 BENCH-02) if `-e` fails → `firestarter dev read SST27SF512 -s <size> /tmp/readback.bin` → `cmp <image>.bin /tmp/readback.bin`. Exit 0 = PASS.
- Note: this RESEARCH.md documents that the actual `write` flag is `-b/--no-blank-check` (not `-e`); the default `firestarter write` path attempts erase. See Pitfall 2 below.

**D-07: Any FAIL row in the Phase 29 EVIDENCE table triggers milestone-reopens — Wave B verifier MUST NOT auto-close VERIFY-NN cells.**
- On any FAIL: capture binaries + sha256s + offset distributions; mark VERIFY-NN as FAIL with linked run output; append Wave B post-mortem prose to EVIDENCE.md; halt session; do NOT promote; update STATE.md to "v1.6 milestone re-opened — Phase 28 fix masked vs fixed root cause; further RCA needed".
- No auto-retry. Halt and surface.

**D-08: Mirror Phase 26's 9-column row schema; append three sub-sections inside `## Phase 29 — Post-fix Consistency-Check Verification (YYYY-MM-DD)`.**
- Sub-sections: Pre-flight checklist (operator) | Per-board build hash record | Hardware metadata snapshot | VERIFY-01+02 full-chip table (9 cols) | VERIFY-03 1KB table | VERIFY-04 BENCH-02 cross-ref | Verdict block | Hand-off to Phase 30.
- See CONTEXT.md D-08 for the exact section template (Wave A scaffolds verbatim).

**D-09: W27C512 for VERIFY-01/02/03; SST27SF512 for VERIFY-04. Single physical W27C512 chip rotated through all 3 boards.**
- W27C512 is read-only (UV-erasable) — no re-writing between runs.
- SST27SF512 is electrically erasable in theory; seated only when BENCH-02 cycle runs on Leonardo.
- Leonardo's W27C512 reports chip ID `0xda01` vs Uno's `0xda08` — known cosmetic variant; operator records in hardware metadata snapshot.

**D-10: Operator confirms shield rev at session start; rev recorded in EVIDENCE.md hardware metadata snapshot table. Plan does NOT lock a specific shield rev.**
- Phase 26 baseline used: Uno + Rev 2.0 shield; Leonardo + modified Rev 0 + voltage-divider mod. Same shield rev per board preferred for direct A/B (but bug is shield-invariant per 3-shield triage).

**D-11: Single post-hoc row addendum in `.planning/v1.5-BENCH-RESULTS.md`; cross-reference the Phase 29 EVIDENCE.md section.**
- Append at end of file (current EOF is line 45). Format per CONTEXT.md D-11.
- Cites Phase 28 fix commits (`437339b6` + `4f205e58`) — these are LOCAL SHAs at Phase 29 time; Phase 30 may amend after merge.

### Claude's Discretion

- Whether to run BENCH-02 on Uno in addition to Leonardo. Default: NO (Leonardo is the maximally-informative single closure). Bonus row only if operator volunteers.
- Whether `pio run -e leonardo -t upload` handles the 32U4's USB-CDC reset dance vs needing operator-side intervention. Default: trust PIO's bundled `avr109` upload protocol with `use_1200bps_touch: true` (handles reset automatically). Manual reset fallback recorded in EVIDENCE.md only if PIO fails.
- How to handle a partial PASS (e.g., 4 / 5 SHAs identical) — default: strict binary PASS/FAIL per D-07. Any non-1 `SHAs distinct` is FAIL.
- Whether to capture pre-flash binary baselines for uno328pb sideload test. Default: NOT captured.
- Whether `update_version.py` should run in Wave A. Default: NO — adds diff churn; commit SHA + hex SHA-256 are unambiguous.

### Deferred Ideas (OUT OF SCOPE)

- Cutting a one-off `3.0.0-rcaN` tag for Phase 29 (mirror of Phase 27 RCA tag option). Phase 30 owns all public artifacts.
- Cutting the public pre-release in Phase 29. Phase 30 owns the merge per ROADMAP Phase 30 SC#5.
- Adding `--size N` flag to `dev consistency-check`. Post-v1.6.
- Auto-orchestrating cross-board verification (`--all-boards` flag). Post-v1.6.
- Bench-validating Uno's `df5fb44` 2026-05-13 fix via parallel Unity test. Post-v1.6 quality-debt.
- Reverting Leonardo `DATA_BUFFER_SIZE` from 512 → 1024 in `firestarter/platformio.ini:64-65`. Phase 30 polish or post-v1.6.
- Documentation drift correction (5 "Leonardo 1024-B" locations). Phase 30 paperwork.
- `firestarter info <chip>` TypeError crash; `0xda01` W27C512 chip-ID alias gap; cosmetic `Board: unknown-board` in consistency-check stdout. Out of v1.6 scope.
- `--keep-files=False` cleanup for Phase 29 post-fix run binaries. Default keep.
- `dev consistency-check` FAIL-without-divergence edge case (Phase 26 REVIEW WR-01). Phase 30 paperwork or post-v1.6.
- Folded todos: NONE folded. `large-read-data-jitter-uno328pb.md` (Phase 30 DOC-01 moves it); `w27c512-eeprom-misclassification.md` (separate milestone); `avrdude-mcu-detection-fallback.md` (unrelated).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| **VERIFY-01** | Post-fix `firestarter read <chip> file.bin` invoked **N≥5 consecutive times** against the same physically-static chip returns byte-identical SHA-256 hashes on `uno328pb` | D-01 reflash test (Case A real-row OR Case B code-equivalence DEFERRAL via Phase 28 hex Δ=0); `dev consistency-check W27C512 --runs 5` invocation; D-08 9-column EVIDENCE row |
| **VERIFY-02** | Same N≥5 consecutive-read consistency check passes on `uno` and `leonardo` | D-03 N=5 uniform; W27C512 chip; `dev consistency-check W27C512 --runs 5 --output-dir .planning/v1.6/post-fix-runs/W27C512-<board>-<TS>` per D-08; expected verdict regex `Consistency check: PASS` + `Distinct SHAs: 1` |
| **VERIFY-03** | `firestarter dev read <chip> -s 1024` byte-identical across N≥5 consecutive calls on all 3 boards (the low-rate jitter must also resolve — if it doesn't, the root cause isn't truly fixed) | D-05 shell-loop snippet `for i in $(seq 5); do firestarter -p /dev/ttyXXX dev read W27C512 -s 1024 -a 0 /tmp/r1k_<board>_$i.bin; done; sha256sum /tmp/r1k_<board>_*.bin`; D-07 milestone-reopens on FAIL even if VERIFY-01/02 PASS |
| **VERIFY-04** | Phase 24 BENCH-02 acceptance criterion ("write→read→verify on a representative EPROM") closes as a side effect — recorded in `.planning/v1.5-BENCH-RESULTS.md` (post-hoc row addendum) | D-06 SST27SF512 on Leonardo; `write SST27SF512 <image>.bin` (default erase) with `-b` fallback if erase fails; `dev read SST27SF512 -s <size> /tmp/readback.bin`; `cmp` exit 0 = PASS; D-11 post-hoc addendum format appended at end of v1.5-BENCH-RESULTS.md (currently line 45) |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

**`/workspaces/CLAUDE.md` (meta-repo) — applicable:**
- Repo is meta-repo / planning repo; tracks only `.planning/` + `.claude/`. Sub-repos (`firestarter/`, `firestarter_app/`) are not committed here. Phase 29 file writes target `.planning/` only.
- Serial protocol changes must be kept in sync between `firestarter_app/firestarter/serial_comm.py` and `firestarter/src/firestarter.cpp`. Phase 29 does NOT touch either (no code edits).
- Constants/flag bits duplicated between `firestarter_app/firestarter/constants.py` and `firestarter/include/firestarter.h`. Phase 29 does NOT touch either.
- Uno has 512-B buffer; Leonardo has 1024 (NOTE: outdated — `platformio.ini:64-65` confirms both run at `DATA_BUFFER_SIZE=512` per Phase 27 H6 refutation; Phase 30 DOC-01 paperwork corrects this).

**`/workspaces/firestarter/CLAUDE.md` (firmware sub-repo) — applicable:**
- Canonical build commands: `pio run -e <env>` and `pio run -t upload -e <env>`. Phase 29 D-02 follows these verbatim.
- Native test environment: `pio test -e native`. Phase 29 does NOT run pio test (Phase 28 already green).

**`/workspaces/firestarter_app/CLAUDE.md` (host CLI sub-repo) — applicable:**
- Dev install: `pip install -e .`. Phase 29 D-02 follows this.
- Wire protocol at 250000 baud; firmware responses are prefix-tagged `OK:`, `DATA:`, `MAIN:`, `END:`, `ERROR:`. Phase 29 does NOT touch protocol; relies on stable contract.

**Auto Mode:** `/gsd-discuss-phase 29` ran in Auto Mode. CONTEXT.md captured all 11 decisions auto-resolved. Phase 29 may proceed without operator interruption; gray areas are encoded under `Claude's Discretion`.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Firmware build | Build toolchain (PlatformIO) | — | `pio run -e <env>` emits `.hex` artifacts. No runtime tier involvement. |
| Local sideload (Uno) | Build toolchain (PIO) | — | `pio run -t upload --upload-port /dev/ttyACM0` invokes `avrdude -c arduino -b 115200`. |
| Local sideload (Leonardo) | Build toolchain (PIO) | — | `pio run -t upload --upload-port /dev/ttyACM1` invokes `avrdude -c avr109 -b 57600` with `use_1200bps_touch` reset handled by PIO. |
| Local sideload (uno328pb) | Build toolchain (PIO) OR direct avrdude (operator) | — | PIO uses `urclock` protocol by default; D-01 fallback uses `avrdude -c urclock` directly. |
| Host CLI install | Python toolchain (pip) | — | `pip install -e .` from `firestarter_app/v1.6-read-bug` (editable install; auto-tracks file changes). |
| Firmware handshake | Arduino firmware (`firestarter.cpp` MSG_OK_FW_HANDSHAKE emit) | Host CLI (`firmware.py:check_current_firmware` parse) | Wire protocol: firmware emits `OK: FW: <version>:<board>` → host prints `Current firmware version: <ver>, for controller: <board> on port <port>`. |
| Consistency-check N=5 | Host CLI (`eprom_operations.py:consistency_check_eprom`) | Firmware (state-machine + `rurp_read_data_buffer`) | Host orchestrates N reads via `_run_state_machine` + `_main_phase_read_data`; firmware executes per-chunk read with the Phase 28 fix in `leonardo_rurp_shield.cpp`. |
| 1KB low-rate read (VERIFY-03) | Host CLI (`dev read -s 1024` via `dev_read_eprom`) | Firmware (same state machine) | Operator shell-loop wraps 5 invocations; same code path as full-chip read. |
| BENCH-02 write→read→verify | Host CLI (`write` + `dev read` + shell `cmp`) | Firmware (write path + read path) | Write commits bits; read returns them; OS `cmp` compares files. Phase 28 fix is read-path only — write semantics unaffected. |
| Evidence capture | Meta-repo (`.planning/v1.6-EVIDENCE.md` + `.planning/v1.5-BENCH-RESULTS.md` + `.planning/v1.6/post-fix-runs/`) | — | Append-only; commits to meta-repo `main` per standing convention. |
| Branch flow | Sub-repos LOCAL (`firestarter/v1.6-read-bug`, `firestarter_app/v1.6-read-bug`) | Meta-repo `main` (planning artifacts pushed) | NO sub-repo pushes / merges / tags in Phase 29. Phase 30 owns all public-channel work. |

## Standard Stack

### Core (verified in-tree; no installs needed)

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| PlatformIO Core | 6.1.19 | Firmware build + upload | [VERIFIED: `pio --version`] Standard for Arduino-platform projects; canonical per `firestarter/CLAUDE.md`. |
| avrdude | 7.1 | Direct AVR flash (uno328pb fallback) | [VERIFIED: `avrdude -v`] Standard AVR uploader; v1.5 BENCH-01 proved `-c urclock` works on the misidentified board. |
| Python pip (editable install) | system | Host CLI dev install | [VERIFIED: `pyproject.toml` declares `firestarter = "firestarter.main:main"` entry point] |
| pyserial | >=3.5 | Serial transport (host CLI dep) | [VERIFIED: `pyproject.toml` line 47] Auto-pulled by `pip install -e .`. |
| requests | >=2.20 | GitHub releases enumeration | [VERIFIED: `pyproject.toml` line 48] Not exercised in Phase 29 (no `fw -i`). |
| tqdm | >=4.60 | Progress bars in consistency-check | [VERIFIED: `pyproject.toml` line 49] Suppressed by `-q` flag if desired. |

### Supporting (verified in-tree)

| Component | Location | Purpose | When to Use |
|-----------|----------|---------|-------------|
| `firestarter dev consistency-check` | `firestarter_app/firestarter/main.py:432-481` + `eprom_operations.py:431-603` | N-run SHA-256 divergence verdict | Wave B per-board full-chip verification (VERIFY-01/02) |
| `firestarter dev read -s N` | `firestarter_app/firestarter/main.py:373-388` + `eprom_operations.py:dev_read_eprom` | Single-shot read with `-s` size + `-a` address | Wave B per-board 1KB shell-loop (VERIFY-03) |
| `firestarter write <chip> <file>` | `firestarter_app/firestarter/main.py:93-116` + `eprom_operations.py:write_eprom` | Write binary file to EPROM | Wave B BENCH-02 cycle (VERIFY-04) |
| `firestarter fw` (no args) | `firestarter_app/firestarter/main.py:790-839` + `firmware.py:check_current_firmware` | Read FW version + board handshake | Post-flash verification per board |
| `name_firmware.py` | `firestarter/name_firmware.py` | PIO pre-script: derive `PROGNAME=firestarter_<board>` from `RURP_BOARD_NAME` flag | Runs automatically per `pio run`; emits `firestarter_<board>.hex`. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `pio run -t upload --upload-port /dev/ttyACM<N>` for Uno/Leonardo | `avrdude -c arduino`/`-c avr109` directly | More verbose; loses PIO's auto-reset handling for Leonardo (1200-baud touch). PIO is canonical per CLAUDE.md. |
| `avrdude -c urclock` for uno328pb sideload | `pio run -e uno328pb -t upload --upload-port /dev/ttyUSB0` | PIO's `urclock` protocol path may differ from v1.5's proven avrdude invocation. CONTEXT.md D-01 names avrdude fallback as primary if PIO upload fails. PIO attempt first is fine; avrdude is the safety net. |
| `firestarter write -b SST27SF512` (skip erase) | `firestarter write SST27SF512` (default erase) | Default path attempts erase first; v1.5 BENCH-02 saw `ERROR: Not supported` from SST27SF512 misclassification (DB routes as UV-EPROM). D-06 specifies fallback to `-b` if `-e` (which doesn't exist as a flag — see Pitfall 2) fails. |

**Installation:** All tools verified pre-installed on this dev container. No installs required.

**Version verification:** Phase 29 is offline / bench-only — no npm registry or pip registry calls. The "Standard Stack" versions are pinned to what's already present in-tree.

## Architecture Patterns

### System Architecture Diagram

```
Wave A (autonomous: true, desk-side):
┌─────────────────────────────────────────────────────────────────────┐
│ /workspaces/firestarter (on v1.6-read-bug @ 4f205e58)               │
│                                                                       │
│  pio run -e uno      ─┐                                              │
│  pio run -e leonardo ─┼──→ name_firmware.py (pre-script)            │
│  pio run -e uno328pb ─┘     ↓                                        │
│                              .pio/build/<env>/firestarter_<env>.hex  │
│                              [ALREADY EXISTS on disk; rebuild no-op] │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ shasum -a 256 .pio/build/*/firestarter_*.hex                         │
│  ──→ 3 SHA-256 strings (build hash record)                          │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ /workspaces/firestarter_app (on v1.6-read-bug @ c057fe2)            │
│  pip install -e .                                                    │
│  ──→ entry_point `firestarter` installed in active venv             │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ /workspaces/.planning/v1.6-EVIDENCE.md                              │
│  Append at line 187 (after Phase 29 anchor at line 186):            │
│   ## Phase 29 — Post-fix Consistency-Check Verification (TBD)       │
│   + pre-flight checklist + build hash table + scaffold sub-tables   │
│                                                                       │
│ /workspaces/.planning/v1.5-BENCH-RESULTS.md                         │
│  Append at line 46 (after current EOF at line 45):                  │
│   ## Phase 24 BENCH-02 post-hoc closure (placeholder)               │
└─────────────────────────────────────────────────────────────────────┘

Wave B (autonomous: false, operator-on-bench):
┌─────────────────────────────────────────────────────────────────────┐
│ Per board (Uno on /dev/ttyACM0, Leonardo on /dev/ttyACM1,            │
│   uno328pb on /dev/ttyUSB0):                                         │
│                                                                       │
│  Sideload:                                                            │
│   pio run -e <env> -t upload --upload-port /dev/ttyXXX               │
│   (uno328pb: avrdude -p atmega328pb -c urclock -b 115200             │
│              -P /dev/ttyUSB0 -U flash:w:.../firestarter_uno328pb.hex)│
│                                                                       │
│  Handshake check:                                                     │
│   firestarter -p /dev/ttyXXX fw                                       │
│   → "Current firmware version: 3.0.0b4, for controller: <board>"     │
│   (uno328pb: branch Case A vs Case B per D-01)                       │
│                                                                       │
│  Axis 1 (VERIFY-01/02 full-chip):                                    │
│   firestarter -p /dev/ttyXXX dev consistency-check W27C512           │
│     --runs 5 --output-dir .planning/v1.6/post-fix-runs/<dir>         │
│   → exit 0 + "Consistency check: PASS" + "Distinct SHAs: 1"          │
│                                                                       │
│  Axis 2 (VERIFY-03 1KB):                                             │
│   for i in $(seq 5); do                                               │
│     firestarter -p /dev/ttyXXX dev read W27C512 -s 1024 -a 0         │
│       /tmp/r1k_<board>_$i.bin                                         │
│   done; sha256sum /tmp/r1k_<board>_*.bin                              │
│   → 5 identical SHA-256 lines                                         │
│                                                                       │
│  Axis 3 (VERIFY-04 BENCH-02 — Leonardo only):                        │
│   firestarter -p /dev/ttyACM1 write SST27SF512 <image>.bin           │
│     (default = blank-check + erase + write; fallback `-b` if erase   │
│      throws ERROR: Not supported)                                     │
│   firestarter -p /dev/ttyACM1 dev read SST27SF512 -s <size>          │
│     /tmp/readback.bin                                                 │
│   cmp <image>.bin /tmp/readback.bin                                   │
│   → exit 0 = PASS                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ Operator fills EVIDENCE.md scaffold:                                 │
│  - VERIFY-01+02 9-column rows (3 boards × {SHAs distinct, divergent │
│    bytes, first-diverge offset, verdict, log dir})                   │
│  - VERIFY-03 sub-table (3 boards × {N=5, SHAs distinct, verdict})    │
│  - VERIFY-04 cross-ref to v1.5-BENCH-RESULTS.md addendum             │
│  - Hardware metadata snapshot (3 boards × {hw_rev, shield, FW build, │
│    chip ID seen})                                                     │
│  - Verdict block (VERIFY-01..04 each CLOSED ✓ or FAIL per D-07)      │
│  - Hand-off to Phase 30 block (green → Phase 30 may proceed)         │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
                    No merge / push / tag.
                    Phase 30 owns all of that.
```

### Recommended Project Structure (no code changes — file paths Phase 29 touches)

```
/workspaces/                                          # meta-repo
├── .planning/
│   ├── v1.6-EVIDENCE.md                             # APPEND at line 187 (after Phase 29 anchor)
│   ├── v1.5-BENCH-RESULTS.md                         # APPEND at line 46 (after current EOF)
│   ├── v1.6/
│   │   ├── consistency-check-runs/                  # Phase 26 baseline binaries (PRESERVE)
│   │   │   ├── W27C512-uno-20260521-133418/run_0[1-3].bin
│   │   │   └── W27C512-leonardo-20260521-134210/run_0[1-3].bin
│   │   ├── post-fix-runs/                           # NEW — Wave B writes here
│   │   │   ├── W27C512-uno-<TS>/run_0[1-5].bin
│   │   │   ├── W27C512-leonardo-<TS>/run_0[1-5].bin
│   │   │   └── W27C512-uno328pb-<TS>/run_0[1-5].bin  # Case A only
│   │   └── bench-logs/                              # tee'd stdout per board
│   │       ├── W27C512-uno-<TS>.log
│   │       ├── W27C512-leonardo-<TS>.log
│   │       └── W27C512-uno328pb-<TS>.log
│   └── phases/29-multi-board-bench-verification/
│       ├── 29-CONTEXT.md                            # exists
│       ├── 29-DISCUSSION-LOG.md                     # exists
│       ├── 29-RESEARCH.md                           # THIS FILE
│       ├── 29-01-PLAN.md                            # planner will create (Wave A)
│       └── 29-02-PLAN.md                            # planner will create (Wave B)
├── firestarter/                                     # sub-repo (LOCAL only)
│   ├── .pio/build/<env>/firestarter_<env>.hex        # local artifacts (already built)
│   └── platformio.ini                                # READ ONLY in Phase 29
└── firestarter_app/                                 # sub-repo (LOCAL only)
    ├── firestarter/main.py                           # READ ONLY in Phase 29
    ├── firestarter/eprom_operations.py               # READ ONLY in Phase 29
    └── pyproject.toml                                # READ ONLY (pip install -e . consumes)
```

### Pattern 1: Two-wave structure (desk-side + operator-on-bench)
**What:** Phase 29 mirrors Phase 26's pattern exactly — Wave A `autonomous: true` (scaffold + build), Wave B `autonomous: false` (operator session).
**When to use:** Any phase with desk-side prep + a bench session. Build artifacts must be ready BEFORE the bench session so operator never waits on `pio run` mid-session.
**Example:** Phase 26 Plan 26-01 (desk-side tool ship) + Plan 26-02 (operator-on-bench session). See `.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-02-SUMMARY.md` for the canonical pre-flight + post-flight narrative.

### Pattern 2: 9-column EVIDENCE.md row schema
**What:** `| Board | Port | Chip | N | SHAs distinct | Divergent bytes (run1 vs run2) | First-diverge offset | Verdict | Log |` — locked across all v1.6 phases per Phase 26 D-08.
**When to use:** Any Phase 29 evidence row in the VERIFY-01+02 table. VERIFY-03 uses a simpler 7-column variant; VERIFY-04 uses a free-form 3-column addendum.
**Example:** `.planning/v1.6-EVIDENCE.md:14-18` (Phase 26 baseline) — pattern Phase 29 inverts cell-for-cell.

### Pattern 3: Cross-phase append-only with HTML anchors
**What:** EVIDENCE.md grows via `<!-- Phase N ... -->` HTML-comment anchors. Each phase appends exactly one section at its anchor; downstream phases insert anchors for their successor.
**When to use:** Wave A scaffold task. Locate the Phase 29 anchor at line 186; insert the new section immediately after (line 187+).
**Example:** Lines 20, 110, 186 of EVIDENCE.md each carry a forward-annotation HTML comment for the next phase.

### Pattern 4: Local-sideload before public commit
**What:** Build firmware locally via `pio run -e <env>`; sideload via `pio run -t upload`; bench-test; ONLY THEN merge to `beta` (which triggers public pre-release cut).
**When to use:** Any phase that validates a fix before merging to `beta`. Keeps failed verdicts private (no public-channel pollution).
**Example:** Phase 29 entire scope. Phase 30 owns the public-channel merge.

### Anti-Patterns to Avoid

- **Using `firestarter fw -i --pre --force` for Phase 29 install:** That path requires a public GitHub Pre-release tag, which doesn't exist yet (Phase 30 creates it). Trying to use it in Phase 29 would either fail (no pre-release fetchable) or — worse — install a stale `3.0.0b4` from v1.5 lacking the Phase 28 fix. Use `pio run -t upload` (or `avrdude` for uno328pb fallback) instead.
- **Cutting a `3.0.0b5` pre-release tag in Phase 29:** Phase 30 SC#5 explicitly owns this. A failed Phase 29 verdict against a publicly-tagged `3.0.0b5` would force a cleanup `3.0.0b6` retract-or-yank. Local sideload preserves the option of clean re-open.
- **Auto-closing VERIFY-NN cells on FAIL:** D-07 mandates milestone-reopens, NOT auto-close. Wave B verifier MUST halt and surface on any FAIL, even if other axes PASS.
- **Skipping the hardware metadata snapshot table:** Per memory `[[user_shield_revisions]]`, the EEPROM `hw_revision` byte cannot distinguish Rev 2.2 / Rev 2.0 / modified Rev 0. The snapshot table is the only audit trail for which shield was actually in use. In Auto Mode, operator must self-record the shield rev at session start.
- **Treating `$?` after a piped command as the firestarter exit code:** Phase 26 SUMMARY documented this trap. Use `${PIPESTATUS[0]}` when tee'ing stdout (e.g., `firestarter ... | tee log.txt; ec=${PIPESTATUS[0]}`).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| N-run consistency check | Custom shell loop with `firestarter read` + `sha256sum` | `firestarter dev consistency-check <chip> --runs 5` | The tool already exists (Phase 26 commit `999c3cc`), uses the SAME `_run_state_machine` + `_main_phase_read_data` code path the bug lives in, emits the canonical stdout verdict block, and writes per-run binaries to a structured `--output-dir`. Phase 26 D-03 reuse-not-duplicate is the lock. |
| 32U4 USB-CDC 1200-baud touch reset | Manual operator reset-press dance | PIO's bundled `avr109` upload protocol (`use_1200bps_touch: true` in `~/.platformio/platforms/atmelavr/boards/leonardo.json`) | PIO handles the touch automatically; `wait_for_upload_port: true` waits for the bootloader CDC port to reappear. Tested via avr109/Caterina-Leonardo bootloader. |
| 328PB sideload | Hand-rolled `avrdude` command line | `pio run -e uno328pb -t upload --upload-port /dev/ttyUSB0` (primary) OR `avrdude -p atmega328pb -c urclock -b 115200 -P /dev/ttyUSB0 -U flash:w:.pio/build/uno328pb/firestarter_uno328pb.hex:i` (D-01 fallback) | PIO uses `urclock` protocol natively per the bundled `boards/ATmega328PB.json`. avrdude direct invocation matches v1.5 BENCH-01's proven path verbatim. |
| Firmware version stamping | `update_version.py --beta` manually in Wave A | DO NOTHING (D-02 default) | Local builds intentionally retain the stale `3.0.0b4` version string; commit SHA `4f205e58` + `.hex` SHA-256 are the unambiguous identifiers. update_version.py is for Phase 30's CI-driven beta cut, not local bench runs. |
| Per-board name in EVIDENCE.md | Custom board-detection shell script | Read it from `firestarter -p /dev/ttyXXX fw` stdout (`for controller: <board>`) | Host CLI already parses the firmware handshake response in `firmware.py:check_current_firmware`. The `<board>` token in `Current firmware version: <ver>, for controller: <board> on port <port>` IS the board name. |
| Cross-checking divergence count post-fix | New tool / new test | Re-run the Phase 27 5-line Python snippet (EVIDENCE.md lines 99-108) against the post-fix binaries | Cross-check is optional Wave B sanity gate. Expected output post-fix: `Total divergences: 0; single-bit-flip fraction: 0.0%`. See "Code Examples" below. |

**Key insight:** Phase 29 is a *consumer* of every tool built in Phases 26-28. Wave A's local build + Wave B's three verification axes can ALL be expressed as invocations of existing CLI surface plus shell pipelines. There is no new code in either wave.

## Runtime State Inventory

> Phase 29 is a verification phase — not a rename, refactor, or migration. The Runtime State Inventory question ("after every file in the repo is updated, what runtime systems still have the old string cached?") does not apply because nothing is being renamed.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — Phase 29 does not modify any database, datastore, or persistent record. Phase 26 baseline run binaries at `.planning/v1.6/consistency-check-runs/W27C512-{uno,leonardo}-20260521-*/` are PRESERVED (do NOT delete). | none |
| Live service config | None — no external services involved. PlatformIO's bundled board JSONs (`~/.platformio/platforms/atmelavr/boards/{uno,leonardo,ATmega328PB}.json`) are read-only consumption. | none |
| OS-registered state | None — no OS-level registrations created or modified. The Arduino bootloaders pre-installed on each board (optiboot for Uno, Caterina for Leonardo, urclock for uno328pb) are pre-existing and unchanged. | none |
| Secrets/env vars | None — Phase 29 does not consume or set any secret keys / env vars. The optional `BETA_VERSION` env var documented in update_version.py is for Phase 30 only. | none |
| Build artifacts | `firestarter/.pio/build/{uno,leonardo,uno328pb}/firestarter_*.hex` already exist on disk from 2026-05-21 builds at tip `4f205e58`. Wave A's `pio run` will be a no-op rebuild unless sources changed. The pre-existing `.elf` companions are unchanged. | Wave A captures SHA-256 of each `.hex` for the EVIDENCE.md build hash record; no rebuild required unless `pio` detects source drift. |

**Nothing else found.** Phase 29 is purely additive evidence + read-only consumption of Phase 26-28 artifacts.

## Common Pitfalls

### Pitfall 1: Treating `firestarter write -e <chip>` as a valid invocation
**What goes wrong:** CONTEXT.md D-06 reads `firestarter -p /dev/ttyACM1 write -e SST27SF512 <test-image>.bin` — but the actual `write` subparser (`firestarter_app/firestarter/main.py:93-116`) has NO `-e` flag. The flags are `-b/--no-blank-check` (skip blank check AND erase per the help text), `-f/--force`, `-a/--address`, `--vpe-as-vpp`.
**Why it happens:** Verbal shorthand in the CONTEXT discussion ("`-e` = erase-first") got encoded literally. The actual default-erase behavior is on by default — there's no flag to enable it.
**How to avoid:** Plan Wave B BENCH-02 step as: `firestarter -p /dev/ttyACM1 write SST27SF512 <image>.bin` (default = blank-check + erase + write). If the erase step fails with `ERROR: Not supported` per the v1.5 BENCH-02 SST27SF512 misclassification, fallback is `firestarter -p /dev/ttyACM1 write SST27SF512 <image>.bin -b` (skip blank check + skip erase; small-window write at `-a 0` covers the address space).
**Warning signs:** `firestarter write -e ...` returns `unrecognized arguments: -e`. Operator sees this in <1s; obvious failure mode.

### Pitfall 2: `$?` after a piped command masking firestarter's exit code
**What goes wrong:** Pipeline `firestarter ... | tee log.txt` exits with tee's exit code (always 0 unless tee itself fails). `$?` shows 0 even when firestarter returned 1 (FAIL) or 2 (hardware error).
**Why it happens:** Bash pipe semantics — `$?` captures the last command in the pipeline.
**How to avoid:** Use `${PIPESTATUS[0]}` to capture firestarter's exit code: `firestarter ... | tee log.txt; ec=${PIPESTATUS[0]}; echo "EXIT: $ec"`. Documented in Phase 26 26-02-SUMMARY.md `patterns-established` (the first Leonardo bench run hit this and masked a chip-ID-fail).
**Warning signs:** Operator sees `EXIT: 0` after a clearly-failed consistency-check run. Always cross-check with the printed `Consistency check: FAIL` / `Consistency check: PASS` line.

### Pitfall 3: Forgetting that uno328pb path branches Case A vs Case B
**What goes wrong:** Plan Wave B as a single 3-board loop and you'll either fabricate a uno328pb verdict (against a Plain-Uno-with-wrong-FW board) or skip the uno328pb verification entirely (leaving VERIFY-01 unclosed).
**Why it happens:** The misidentification was only discovered mid-Phase-26 bench session; pre-existing CONTEXT files predate the correction.
**How to avoid:** Plan Wave B's uno328pb task with explicit Case A / Case B branches per D-01:
- Case A: post-flash handshake reports `uno328pb` → run full verification → fill row normally.
- Case B: handshake reports `uno` (or avrdude returns `signature mismatch` on the 328PB signature `0x1E 0x95 0x16` vs 328P's `0x1E 0x95 0x0F`) → mark row `DEFERRED — board confirmed misidentified per [[project_uno328pb_correction]]; VERIFY-01 closes via code-equivalence with Uno row (Phase 28 hex Δ=0)`.
Both branches close VERIFY-01 in the EVIDENCE Verdict block — Case A directly, Case B by code-equivalence.
**Warning signs:** Wave B plan task says "run consistency-check on uno328pb" without the branch logic. Verifier must read CONTEXT.md D-01 verbatim before writing the task.

### Pitfall 4: Expecting `firestarter fw` to print a `+local` / `+phase29` version suffix
**What goes wrong:** EVIDENCE.md FW build column gets a literal `3.0.0b4+local` value but the actual handshake emits `3.0.0b4` (no suffix). Then the build hash record cross-check fails because the version string doesn't match what was predicted.
**Why it happens:** `update_version.py` does NOT run automatically on `pio run`. The only PIO pre-script is `name_firmware.py` (which only derives `PROGNAME`, not VERSION). VERSION stays at whatever `firestarter/include/version.h:11` says (`"3.0.0b4"` at tip `4f205e58`).
**How to avoid:** EVIDENCE.md FW build column records the verbatim handshake output (`3.0.0b4`) plus the local commit SHA `4f205e58`. The combination is unambiguous. Do NOT predict a version-string format with a suffix; record what the firmware emits.
**Warning signs:** Plan task says "verify FW build = `3.0.0b4+local`" — incorrect prediction. Replace with "record the verbatim version string from `firestarter -p /dev/ttyXXX fw` stdout".

### Pitfall 5: Leonardo upload requires PIO's auto-reset; operator-side intervention if PIO fails
**What goes wrong:** `pio run -e leonardo -t upload --upload-port /dev/ttyACM1` either silently waits for a port that never reappears (if the 32U4 USB-CDC isn't enumerating properly) OR fails with `port not found` if the auto-reset 1200-baud touch races the upload command.
**Why it happens:** Leonardo's bootloader (Caterina) requires a 1200-baud serial touch to enter bootloader mode, then re-enumerates the USB device. PIO's `avr109` upload protocol handles this via `use_1200bps_touch: true` + `wait_for_upload_port: true` (verified in `/home/vscode/.platformio/platforms/atmelavr/boards/leonardo.json`). If the host USB stack is slow to re-enumerate or the kernel `cdc_acm` driver hangs, the upload waits indefinitely.
**How to avoid:** Default plan task uses `pio run -e leonardo -t upload --upload-port /dev/ttyACM1`. If it hangs >30s, operator falls back to manual reset (double-tap the Leonardo reset button to force bootloader mode) then re-runs `pio run -t upload`. Record in EVIDENCE.md "Deviations" section if manual reset was needed.
**Warning signs:** `pio` blocks at `Looking for upload port` or `Waiting for the new upload port` for >30s.

### Pitfall 6: EVIDENCE.md line 186 anchor shifts if upstream edits land between Wave A and bench
**What goes wrong:** Wave A patches at line 186-187 today, but if any Phase 28 SUMMARY amendment lands between Wave A research and Wave A execution, the line number drifts.
**Why it happens:** Markdown line numbers are not stable across edits.
**How to avoid:** Wave A scaffold task locates the anchor by **substring grep**, not line number: `grep -n '<!-- Phase 29 inverts here:' .planning/v1.6-EVIDENCE.md` returns the current line. Insert immediately after that match. The HTML comment substring `<!-- Phase 29 inverts here:` is unique to that single anchor in the file (verified `grep` returns exactly one match at line 186).
**Warning signs:** Wave A task says "insert at line 186" without a grep fallback. Replace with "locate via grep, insert after match".

### Pitfall 7: Conflating local-build artifacts with public-release artifacts
**What goes wrong:** Operator (or Phase 30) assumes the Phase 29 `.hex` SHA-256s in EVIDENCE.md must match the Phase 30 post-merge `.hex` SHA-256s. They don't, by default: Phase 30 runs `update_version.py --beta` which rewrites `firestarter/include/version.h` to (e.g.) `3.0.0b5`, changing the `.rodata`/`.data` version-string region in the `.hex` (Phase 21 21-02-SUMMARY.md documented this exact effect for the AVR build).
**Why it happens:** Both Phase 29 and Phase 30 emit "the same firmware", but Phase 30's version-bump invalidates byte-identity.
**How to avoid:** EVIDENCE.md per-board build hash record SHOULD note "LOCAL build, no version bump — Phase 30 post-merge artifacts will differ by version-string region only". The build hash record is for *Phase 29 reproducibility*, not for Phase 30 cross-verification.
**Warning signs:** Plan / CONTEXT says "Phase 30 verifies post-merge SHA-256 matches Phase 29's record". This is wrong; they will differ by ~10-20 bytes due to version-string change.

## Code Examples

Verified patterns from in-tree source:

### Wave A: Build all three firmware envs locally

```bash
# From meta-repo root, OR cd firestarter && pio run -e ...
cd /workspaces/firestarter
git log -1 --oneline   # expect: 4f205e5 fix(leonardo): add _NOP settling delay...

pio run -e uno
pio run -e leonardo
pio run -e uno328pb

# Capture SHA-256 of each .hex for EVIDENCE.md build hash record
shasum -a 256 \
  .pio/build/uno/firestarter_uno.hex \
  .pio/build/leonardo/firestarter_leonardo.hex \
  .pio/build/uno328pb/firestarter_uno328pb.hex
```
Expected sizes (verified on disk 2026-05-22):
- `firestarter_uno.hex` = 62,617 B
- `firestarter_leonardo.hex` = 68,917 B
- `firestarter_uno328pb.hex` = 62,854 B
(Per Phase 28 D-07 table.)

### Wave A: Install host CLI locally
```bash
cd /workspaces/firestarter_app
git log -1 --oneline   # expect: 999c3cc feat(26-01): implement dev consistency-check (REPRO-03)
pip install -e .
firestarter dev consistency-check --help   # smoke test — should print help
```
Note: `firestarter_app/v1.6-read-bug` HEAD shows `modified: firestarter/config.py` in working tree (uncommitted). Wave A should check whether this needs `git stash` or commit before `pip install -e .` (editable installs track file content, so the modification is consumed live).

### Wave B: Leonardo sideload + handshake verification
```bash
cd /workspaces/firestarter
pio run -e leonardo -t upload --upload-port /dev/ttyACM1
# Source: firestarter/CLAUDE.md §"Build Commands" + PIO board JSON
# (avr109 upload protocol, 1200-baud touch handled automatically)

firestarter -p /dev/ttyACM1 fw
# Expected stdout fragment (from firestarter_app/firestarter/firmware.py:115):
#   Current firmware version: 3.0.0b4, for controller: leonardo on port /dev/ttyACM1
```

### Wave B: uno328pb sideload (PIO primary, avrdude fallback)
```bash
# Primary path (PIO uses urclock protocol natively per boards/ATmega328PB.json)
cd /workspaces/firestarter
pio run -e uno328pb -t upload --upload-port /dev/ttyUSB0

# Fallback path (D-01) — proven from v1.5 BENCH-01
avrdude -p atmega328pb -c urclock -b 115200 -P /dev/ttyUSB0 \
  -U flash:w:.pio/build/uno328pb/firestarter_uno328pb.hex:i

# Handshake — branches per D-01
firestarter -p /dev/ttyUSB0 fw
# Case A: "for controller: uno328pb" → run full verification
# Case B: "for controller: uno"      → DEFERRED row + code-equivalence rationale
# Case B': avrdude exits 1 with "device signature = 0x1e950f / expected 0x1e9516" → DEFERRED
```

### Wave B: Per-board full-chip consistency-check (VERIFY-01/02)
```bash
# Per board (Uno on /dev/ttyACM0, Leonardo on /dev/ttyACM1, uno328pb on /dev/ttyUSB0)
TS=$(date +%Y-%m-%d-%H%M%S)
BOARD=leonardo  # or uno, uno328pb
PORT=/dev/ttyACM1  # or /dev/ttyACM0, /dev/ttyUSB0
OUTDIR=.planning/v1.6/post-fix-runs/W27C512-${BOARD}-${TS}

firestarter -p ${PORT} dev consistency-check W27C512 \
  --runs 5 \
  --output-dir ${OUTDIR} \
  --force \
  2>&1 | tee .planning/v1.6/bench-logs/W27C512-${BOARD}-${TS}.log
ec=${PIPESTATUS[0]}  # CRITICAL: $? would be tee's exit code (0), masking firestarter's exit
echo "EXIT: ${ec}"
# Expected: EXIT: 0 + last stdout line "First 10 divergent offsets:" ABSENT (PASS path)
# Source: firestarter_app/firestarter/eprom_operations.py:557-563 + main.py:914-923
```

Expected stdout block (verbatim regex from `test_consistency_check.py:352-415` Phase 29 forward-compat pin):
```
Consistency check: PASS
Chip: W27C512  Board: unknown-board  Port: /dev/ttyACM1
Runs: N=5
Distinct SHAs: 1
Output dir: .planning/v1.6/post-fix-runs/W27C512-leonardo-<TS>/
```
(`Board: unknown-board` is a known cosmetic issue per Phase 26 REVIEW WR-02; not blocking. Phase 29 ignores this column.)

### Wave B: VERIFY-03 1KB shell-loop
```bash
BOARD=leonardo
PORT=/dev/ttyACM1
for i in $(seq 5); do
  firestarter -p ${PORT} dev read W27C512 -s 1024 -a 0 \
    /tmp/r1k_${BOARD}_$i.bin
done
sha256sum /tmp/r1k_${BOARD}_*.bin
# Expected: 5 lines with IDENTICAL SHA-256 prefix
```
Source: `firestarter_app/firestarter/main.py:373-388` (`dev read` subparser); arg shape `firestarter -p <port> dev read <chip> -s <size> -a <addr> <outfile>`.

### Wave B: VERIFY-04 BENCH-02 cycle (Leonardo only)
```bash
PORT=/dev/ttyACM1

# Generate test image (simplest reproducible source — pseudo-random for deterministic compare)
python3 -c "import os; open('/tmp/sst_test.bin','wb').write(os.urandom(65536))"
# Or all-0xAA for visual inspection: 
# python3 -c "open('/tmp/sst_test.bin','wb').write(b'\xAA'*65536)"

# Write with default erase (D-06 primary path)
firestarter -p ${PORT} write SST27SF512 /tmp/sst_test.bin
# If above fails with ERROR: Not supported on the erase step, fallback:
# firestarter -p ${PORT} write SST27SF512 /tmp/sst_test.bin -b -a 0
# (the -b skips blank-check AND erase per main.py:99-103)

# Read back
firestarter -p ${PORT} dev read SST27SF512 -s 65536 -a 0 /tmp/sst_readback.bin

# Compare
cmp /tmp/sst_test.bin /tmp/sst_readback.bin
echo "cmp exit: $?"
# Expected: exit 0, no stdout (byte-identical)
```

### Phase 27 cross-check 5-liner (optional Wave B sanity gate)

Quote verbatim from `.planning/v1.6-EVIDENCE.md:99-108`:
```python
# Re-verify H2 in <1 second against the committed Phase 26 binaries
r1 = open('.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/run_01.bin','rb').read()
r2 = open('.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/run_02.bin','rb').read()
diffs = [(i, r1[i], r2[i], r1[i]^r2[i]) for i in range(65536) if r1[i] != r2[i]]
from collections import Counter; xor_dist = Counter(x[3] for x in diffs)
single_bit_xors = sum(n for v,n in xor_dist.items() if bin(v).count('1') == 1)
print(f"Total divergences: {len(diffs)}; single-bit-flip fraction: {100*single_bit_xors/len(diffs):.1f}%")
# expected output: Total divergences: 1349; single-bit-flip fraction: 78.6%
```

Phase 29 sanity-check variant — re-run against the post-fix Leonardo binaries:
```python
# Repoint the paths at the Phase 29 post-fix outputs
import glob, sys
runs = sorted(glob.glob('.planning/v1.6/post-fix-runs/W27C512-leonardo-*/run_*.bin'))
if len(runs) < 2:
    print("ERROR: expected at least 2 post-fix run binaries"); sys.exit(1)
r1 = open(runs[0],'rb').read()
r2 = open(runs[1],'rb').read()
diffs = [(i, r1[i], r2[i], r1[i]^r2[i]) for i in range(len(r1)) if r1[i] != r2[i]]
print(f"Total divergences: {len(diffs)}; (expected: 0 post-fix)")
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Public pre-release tag for bench validation | Local sideload via `pio run -t upload` | Phase 29 CONTEXT correction 2026-05-22 | Failed verdicts stay private; no GitHub Pre-release / PyPI cleanup required on FAIL. |
| Phase 26 N=3 baseline | Phase 29 N=5 verification | Phase 29 D-03 (matches REQUIREMENTS VERIFY-01/02 floor) | Symmetric A/B vs Phase 26 with more samples; ~6s extra per board (trivial). |
| Auto-mark uno328pb DEFERRED in v1.6 | Reflash-then-test with Case A / Case B branches | Phase 29 D-01 | Resolves the carry-over VERIFY-01 mismatch explicitly; closes via real verification OR code-equivalence. |

**Deprecated/outdated:**
- "Leonardo has 1024-B buffer" claim in `/workspaces/CLAUDE.md` + `firestarter/CLAUDE.md` + 3 other locations — refuted by `platformio.ini:64-65` (`-D DATA_BUFFER_SIZE=512`); Phase 30 DOC paperwork corrects.
- `firestarter fw -i --pre --force` install-pipeline regression check — Phase 30 territory (after public pre-release exists). Phase 29 uses `pio -t upload` exclusively.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Operator's bench port mapping is `/dev/ttyACM0` (Uno), `/dev/ttyACM1` (Leonardo), `/dev/ttyUSB0` (uno328pb) per Phase 26 baseline + memory `[[project_bench_findings_v15]]` | Architecture Patterns; Code Examples | Wrong port → upload fails; operator reads the right port from `dmesg` / `ls /dev/tty*` at session start. Low risk — operator confirms at Wave B start. |
| A2 | The `cdc_acm` kernel driver on the operator's machine handles Leonardo's USB re-enumeration without intervention (Pitfall 5) | Pitfall 5 | If the host kernel hangs on Leonardo re-enumeration, operator needs manual double-tap reset. Mitigation documented in Pitfall 5. Medium risk; benign workaround. |
| A3 | The pre-existing local `.hex` artifacts (built 2026-05-21 with sizes matching Phase 28 D-07 table) are still valid; `pio run -e <env>` will produce byte-identical output if re-run | Wave A; Code Examples | If sources were touched between phases, `pio run` rebuilds. Build hash record captures the actual SHA-256s — no integrity risk; just informational diff. |
| A4 | `firestarter_app` working-tree modification of `firestarter/config.py` is benign / unrelated to Phase 29 | Code Examples (Wave A pip install -e .) | Wave A may need to `git stash` or commit the modification before `pip install -e .` to get a deterministic install state. Operator should inspect the diff at session start. |
| A5 | SST27SF512 socket-swap for VERIFY-04 cycle is uncontentious (operator-confirmed available in chip kit per memory `[[v1.5_bench_findings]]`) | VERIFY-04 (Pattern 1 Code Example) | If SST27SF512 is not at hand, operator can substitute another writable chip (e.g., another SST27 variant) — record the substitution in BENCH-RESULTS addendum. Low risk. |
| A6 | Phase 30 will use either a merge-commit OR squash-merge for `v1.6-read-bug → beta`; if squash, only the squashed commit SHA appears on `beta` (the LOCAL `437339b6` / `4f205e58` SHAs become unreachable on `beta` but stay reachable in `git log --all`) | D-11 BENCH-RESULTS addendum | Low risk — D-11 note documents both cases. Phase 30 may amend the addendum row with post-merge SHAs. |

**If this table looks long for a verification phase:** Most items are auto-mode-stand-ins for operator clarifications that would normally be live-asked. Wave B is `autonomous: false` so the operator can confirm/correct each at session start.

## Open Questions (RESOLVED)

1. **Working-tree modification in `firestarter_app/firestarter/config.py`** — Should Wave A commit, stash, or proceed with the uncommitted change for the `pip install -e .`?
   - What we know: `git status` on the sub-repo shows one file modified, not staged.
   - What's unclear: whether the modification is intentional Phase 29 prep or stale leftovers from Phase 26.
   - RESOLVED: Recommendation: Wave A first task should `git diff firestarter/config.py` and surface the diff. Operator decides: commit (if intentional), stash (if accidental), or proceed (if it's a no-op change with no functional effect on Phase 29).

2. **PIO `urclock` upload protocol for uno328pb — works first-try or needs avrdude fallback?**
   - What we know: `~/.platformio/platforms/atmelavr/boards/ATmega328PB.json` declares `protocol: urclock` natively. PIO 6.1.19 supports urclock.
   - What's unclear: whether PIO's urclock invocation matches v1.5 BENCH-01's avrdude command verbatim (same baud, same `-c urclock`).
   - RESOLVED: Recommendation: Wave B uno328pb task tries `pio run -e uno328pb -t upload --upload-port /dev/ttyUSB0` FIRST; falls back to verbatim avrdude command on failure (per D-01 fallback). Either path satisfies D-01.

3. **Test image source for VERIFY-04** — operator-supplied or generated on-the-fly?
   - What we know: Wave B BENCH-02 task needs a binary to write to SST27SF512.
   - What's unclear: whether operator has a canonical "test image" they want to use OR is fine with a fresh pseudo-random one.
   - RESOLVED: Recommendation: Default to generating via `python3 -c "import os; open('/tmp/sst_test.bin','wb').write(os.urandom(65536))"`. Pseudo-random is best for compare integrity (any single-bit error visible); all-0xAA is best for visual inspection. Plan offers both as options; operator picks at session.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO Core | Wave A firmware build + Wave B PIO sideload | ✓ | 6.1.19 | — |
| `pio run -e uno`, `-e leonardo`, `-e uno328pb` (platform-bundled) | Firmware builds | ✓ | atmelavr@5.2.0 | — |
| avrdude | uno328pb fallback sideload (D-01); also bundled with PIO for Uno/Leonardo upload internally | ✓ | 7.1 | — |
| Python 3.9+ | Host CLI (`pip install -e .` consumer; pyproject.toml requires-python ≥3.9) | ✓ | (system) | — |
| pip / setuptools | Host CLI editable install | ✓ | setuptools 45+ | — |
| pyserial >=3.5, requests >=2.20, tqdm >=4.60, argcomplete, rich, packaging | Host CLI runtime deps | ✓ | auto-pulled by `pip install -e .` | — |
| pytest >=7.0 | (NOT required for Phase 29 — host-side test suite already green in Phase 26/28) | ✓ | (dev extra) | — |
| `firestarter` CLI entry point | Wave B per-board invocations | ✓ post-Wave-A | (3.0.0b4) | — |
| Operator's 3 boards + RURP shield(s) + W27C512 chip + SST27SF512 chip | Wave B bench session | operator-owned | — | If SST27SF512 unavailable, substitute another writable chip (A5) |
| `cmp(1)` | VERIFY-04 byte-identity check | ✓ | (coreutils) | — |
| `sha256sum(1)` | VERIFY-03 1KB shell-loop SHA capture | ✓ | (coreutils) | — |
| `shasum(1)` | Wave A `.hex` SHA-256 capture | ✓ | (Perl) | sha256sum alternative |
| `tee(1)` | Wave B per-board log capture | ✓ | (coreutils) | — |
| `seq(1)` | VERIFY-03 1KB shell-loop counter | ✓ | (coreutils) | `for i in 1 2 3 4 5` equivalent |

**Missing dependencies with no fallback:** None — all toolchain is in-place.

**Missing dependencies with fallback:** None.

## Validation Architecture

> **Phase 29 has no source-of-truth code edits.** Traditional unit-test validation does not apply directly. The bench evidence IS the validation.

### Test Framework

| Property | Value |
|----------|-------|
| Framework (host) | pytest 7.0+ (firestarter_app sub-repo; for re-running existing tests if regression suspected) |
| Framework (firmware) | Unity via PlatformIO (firestarter sub-repo; for re-running Phase 28 `test_data_input` if regression suspected) |
| Quick run command (host) | `cd firestarter_app && pytest tests/test_consistency_check.py -x` |
| Quick run command (firmware) | `cd firestarter && pio test -e native -f "*test_data_input*"` |
| Full suite command (host) | `cd firestarter_app && pytest -ra -q` |
| Full suite command (firmware) | `cd firestarter && pio test -e native` |

These suites are NOT in Phase 29's gating path — Phase 26 (host) and Phase 28 (firmware) already shipped them green. They are diagnostic gates if a Phase 29 bench result smells like a host-side or firmware-side regression rather than a true read-bug masking.

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| VERIFY-01 | uno328pb N=5 consecutive read byte-identity | Manual/bench (hardware-gated) | `firestarter -p /dev/ttyUSB0 dev consistency-check W27C512 --runs 5 --output-dir <path>` | ✓ tool exists (Phase 26 commit `999c3cc`) |
| VERIFY-02 | uno + leonardo N=5 byte-identity | Manual/bench (hardware-gated) | Same tool, per board (3 invocations total per axis) | ✓ |
| VERIFY-03 | All 3 boards 1KB N=5 byte-identity | Manual/bench (hardware-gated shell loop) | `for i in $(seq 5); do firestarter dev read W27C512 -s 1024 -a 0 /tmp/r1k_<board>_$i.bin; done; sha256sum /tmp/r1k_<board>_*.bin` | ✓ |
| VERIFY-04 | BENCH-02 write→read→verify cycle | Manual/bench (hardware-gated) | `firestarter write SST27SF512 ...; firestarter dev read SST27SF512 ...; cmp` | ✓ |

### Sampling Rate

- **Per task commit (Wave A):** `cd firestarter && pio run -e <env>` (build smoke). Existing artifacts on disk mean these are no-op rebuilds — fast.
- **Per wave merge:** Wave A — `shasum -a 256 *.hex` + `firestarter dev consistency-check --help` smoke. Wave B — operator-driven; no automated sampling.
- **Phase gate:** All 4 VERIFY-NN cells in EVIDENCE.md show CLOSED ✓ in the Verdict block; D-07 milestone-reopens if any FAIL.

### Wave 0 Gaps

- **None — existing test infrastructure covers all phase requirements.** Phase 26 already shipped the consistency-check pytest contract (`test_consistency_check.py`, 8 tests including the stdout regex pin Phase 29 relies on). Phase 28 already shipped the Unity `test_data_input` suite green. Phase 29's validation is the bench evidence itself, not a Wave 0 scaffold.

### Validation Architecture observations (suggested tasks for the planner)

The orchestrator scans for this header to decide whether to generate VALIDATION.md. Suggested validation activities Phase 29 plans should encode:

1. **EVIDENCE.md row-fill acceptance criterion (VERIFY-01 + VERIFY-02):**
   - Per row: `SHAs distinct == 1` AND `Verdict == PASS` (case A) OR `Verdict == DEFERRED` (case B for uno328pb).
   - Verifier check (substring grep): `grep -c "SHAs distinct | 1" <path>/29-RESEARCH-or-EVIDENCE.md` returns ≥2 (Uno + Leonardo; uno328pb may be DEFERRED).
2. **VERIFY-03 sub-table acceptance:** `Distinct SHAs: 1` line in the 1KB sub-table for each non-DEFERRED board.
3. **VERIFY-04 acceptance:** `cmp` exit 0 confirmed in BENCH-RESULTS addendum; addendum row contains `✓ PASS` literal.
4. **Optional Wave B sanity gate (the Phase 27 5-line Python cross-check rerun):** Expected output `Total divergences: 0; (expected: 0 post-fix)`. If divergences > 0 alongside a `PASS` verdict, something is internally inconsistent — halt and surface (paranoia check; not a replacement for the consistency-check tool).
5. **Build hash record acceptance:** SHA-256 captured for each of the 3 `.hex` artifacts in EVIDENCE.md Wave A scaffold table; commit SHA recorded as `4f205e58` for all three rows.

## Security Domain

> Required when `security_enforcement` is enabled (absent = enabled).

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Phase 29 is local-only; no authentication surface. |
| V3 Session Management | no | No sessions. |
| V4 Access Control | no | Operator-local hardware access only; no multi-tenant boundary. |
| V5 Input Validation | partial | `name_firmware.py:49` already validates `RURP_BOARD_NAME` against `^[a-zA-Z0-9_-]+$` regex; Phase 29 inherits that contract, doesn't change it. `firestarter dev consistency-check` validates `--runs >= 2` per D-10 Test 6. |
| V6 Cryptography | partial | SHA-256 used for byte-identity verification via `hashlib.sha256` (Python stdlib) + `shasum -a 256` (Perl) + `sha256sum` (coreutils). All standard, never hand-rolled. Phase 29 is consuming pre-built crypto; no implementation. |

### Known Threat Patterns for {stack}

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Operator runs Phase 29 sideload against wrong physical board | Spoofing (board identity) | Post-flash handshake check via `firestarter fw` confirms board identity matches expected per port. D-01 Case A/B branch encodes this explicitly for uno328pb. |
| Operator commits the post-fix run binaries with sensitive content | Information Disclosure (not real risk here — EPROM content is operator-owned hardware data) | Run binaries land in `.planning/v1.6/post-fix-runs/` which is tracked git; W27C512 content is operator's own ROM data, not secrets. No mitigation needed. |
| Phase 29 EVIDENCE.md commits accidentally include credentials | Information Disclosure | Standard meta-repo convention: only commit `.planning/*.md` text files. No `.env` / `.secret` files in scope. |
| Wave A `pip install -e .` pulls a compromised dependency | Tampering | All deps (`pyserial`, `requests`, `tqdm`, `argcomplete`, `rich`, `packaging`) are pre-existing in operator's venv from Phase 26 install. `pip install -e .` re-resolves only the local package; deps already satisfied. Low risk. |

**Phase 29 has no novel security surface.** All inherits from Phase 26 (host CLI install) + Phase 28 (firmware build). The bench session is operator-local; no network exposure introduced.

## Sources

### Primary (HIGH confidence)
- `.planning/phases/29-multi-board-bench-verification/29-CONTEXT.md` — [VERIFIED: cat] 11 locked decisions D-01..D-11; section schema; sub-repo branch state; line-186 anchor confirmation.
- `.planning/v1.6-EVIDENCE.md` (entire file, 219 lines) — [VERIFIED: cat] Confirmed line-186 anchor is the Phase 29 insertion point; Phase 28 section terminates at line 185; Verdict block at lines 188-204.
- `.planning/v1.5-BENCH-RESULTS.md` — [VERIFIED: wc -l = 45] EOF is line 45 (the final Verdict block ends without trailing blank lines); Phase 29 D-11 addendum appends at line 46+.
- `firestarter/platformio.ini` — [VERIFIED: cat] Three envs `[env:uno]` / `[env:leonardo]` / `[env:uno328pb]`; pre-script `extra_scripts = pre:name_firmware.py` confirmed.
- `~/.platformio/platforms/atmelavr/boards/{uno,leonardo,ATmega328PB}.json` — [VERIFIED: python json parse] Upload protocols: arduino@115200 (uno), avr109@57600 with `use_1200bps_touch: true` (leonardo), urclock@115200 (ATmega328PB).
- `firestarter/.pio/build/{uno,leonardo,uno328pb}/firestarter_*.hex` — [VERIFIED: ls -la] Already built 2026-05-21 with sizes 62617 / 68917 / 62854 matching Phase 28 D-07.
- `firestarter/name_firmware.py` — [VERIFIED: cat] Only pre-script wired; derives PROGNAME from RURP_BOARD_NAME; does NOT invoke update_version.py.
- `firestarter/.github/scripts/update_version.py` — [VERIFIED: cat] Standalone script, NOT a PIO pre-script; invoked manually with `--beta` or in CI via GITHUB_REF. Local `pio run` does NOT call it.
- `firestarter/include/version.h` — [VERIFIED: grep] `#define VERSION "3.0.0b4"` at line 11.
- `firestarter_app/firestarter/main.py:90-481, 790-924` — [VERIFIED: Read] `fw` subparser invocation flow; `dev consistency-check` subparser (`--runs`, `--output-dir`, `--keep-files`, `--max-diffs`, `-q`, `-f`); `dev read` subparser (`-a`, `-s`, `-f`); `write` subparser (`-b/--no-blank-check`, `-f/--force`, `-a/--address`, `--vpe-as-vpp`; NO `-e`).
- `firestarter_app/firestarter/eprom_operations.py:431-603` — [VERIFIED: Read] `consistency_check_eprom` returns int 0/1/2 (PASS/FAIL/hw-error); stdout block format: `Consistency check: <verdict>`, `Chip: ...  Board: unknown-board  Port: ...`, `Runs: N=<int>`, `Distinct SHAs: <int>`, `Output dir: ...`, `First divergence: offset 0x<HHHH>  (run_1=0xHH, run_2=0xHH)` (FAIL only), `Total divergent bytes (run_1 vs run_2): <n> / <m> (<pct>%)`, `First <N> divergent offsets: ...`.
- `firestarter_app/firestarter/firmware.py:80-127` — [VERIFIED: Read] `check_current_firmware` handshake parse — emits `Current firmware version: <version>, for controller: <board_name> on port <port>` (line 115). Wire payload: `OK: FW: <ver>:<board>`.
- `firestarter_app/pyproject.toml` — [VERIFIED: cat] Entry point `firestarter = "firestarter.main:main"`; deps list; `requires-python = ">=3.9"`.
- `firestarter_app/tests/test_consistency_check.py:1-50, 352-415` — [VERIFIED: Read] Stdout regex pin (Phase 29 forward-compat contract); 8 test cases; monkeypatch-of-operator-internals pattern.
- `pio --version` → `PlatformIO Core, version 6.1.19` — [VERIFIED: Bash]
- `avrdude -v` → `Version 7.1` — [VERIFIED: Bash]
- `git log -1` on both sub-repos confirmed at `4f205e58` (firestarter) and `999c3cc` (firestarter_app, with uncommitted `firestarter/config.py` change) — [VERIFIED: Bash]
- `.planning/phases/28-fix-implementation-unit-test-coverage/28-CONTEXT.md` §D-07 — [VERIFIED: grep] Per-board hex size table: uno=62,617 B (Δ=0), leonardo=68,917 B (Δ=+41 B), uno328pb=62,854 B (Δ=0).
- `.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-02-SUMMARY.md` — [VERIFIED: cat] Canonical pre-flight + post-flight narrative; `${PIPESTATUS[0]}` shell pitfall; uno328pb identity correction; 9-column schema lock.

### Secondary (MEDIUM confidence)
- Memory `[[project_bench_findings_v15]]` — [CITED: ~/.claude memory] Port mapping `/dev/ttyUSB0` for misidentified board; `programmer_id="urclock"` for v1.5 BENCH-01.
- Memory `[[project_uno328pb_correction]]` — [CITED: ~/.claude memory] The board labeled `uno328pb` in v1.5 bench notes was actually a Plain Uno + wrong FW; skip for v1.6 read-bug repro.
- Memory `[[user_shield_revisions]]` — [CITED: ~/.claude memory] Operator owns Rev 2.2, Rev 2.0, modified Rev 0; EEPROM `hw_revision` byte cannot distinguish them; always ASK which rev (in auto mode → record explicitly).
- Memory `[[v1.5_bench_findings]]` — [CITED: ~/.claude memory] SST27SF512 in operator's kit; worked end-to-end for v1.5 BENCH-01.

### Tertiary (LOW confidence)
- None — all critical claims verified against in-tree source or local environment.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — every tool version verified via Bash; no remote registry calls needed.
- Architecture: HIGH — file paths verified via `ls` / `grep`; line-186 anchor verified verbatim; per-board upload protocol verified via PIO board JSON parse.
- Pitfalls: HIGH — Pitfall 1 (no `-e` flag) verified by reading `create_write_args` in main.py; Pitfalls 2-6 carried over from Phase 26-28 closed phases with documented evidence in SUMMARY files; Pitfall 7 cross-referenced with Phase 21 21-02-SUMMARY.md.
- Code examples: HIGH — every command line traceable to in-tree source line numbers; `python3 -c "import os; ..."` verified to be a standard cross-platform pseudo-random generator; `shasum -a 256` / `sha256sum` interchangeable.
- Open questions: MEDIUM — all three resolvable at Wave B session start by operator inspection (`git diff`, PIO output, chip kit availability).

**Research date:** 2026-05-22
**Valid until:** 2026-06-22 (30 days — stable verification phase; the only freshness risk is sub-repo working-tree drift between research and execution, mitigated by Wave A's git-status checks).

---

*Phase: 29-multi-board-bench-verification*
*Research gathered: 2026-05-22*

---
phase: 29
slug: multi-board-bench-verification
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-22
---

# Phase 29 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> **Phase 29 has NO source-of-truth code edits.** The bench evidence (post-fix run binaries + EVIDENCE.md row fills) IS the validation. Existing pytest / Unity suites stay green by hypothesis (Phase 26 + Phase 28 shipped them); they are diagnostic gates if a bench result smells like a host-side or firmware-side regression rather than the read-bug actually being fixed.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (host)** | pytest 7.0+ (firestarter_app sub-repo) |
| **Framework (firmware)** | Unity via PlatformIO (firestarter sub-repo) |
| **Config file (host)** | firestarter_app/pyproject.toml + firestarter_app/tests/ |
| **Config file (firmware)** | firestarter/platformio.ini |
| **Quick run command (host)** | `cd firestarter_app && pytest tests/test_consistency_check.py -x` |
| **Quick run command (firmware)** | `cd firestarter && pio test -e native -f "*test_data_input*"` |
| **Full suite command (host)** | `cd firestarter_app && pytest -ra -q` |
| **Full suite command (firmware)** | `cd firestarter && pio test -e native` |
| **Estimated runtime (host quick)** | ~3 seconds (8 tests in test_consistency_check.py) |
| **Estimated runtime (firmware native)** | ~8 seconds |
| **Bench evidence runtime** | ~60–90 minutes (operator-on-bench session, Wave B) |

---

## Sampling Rate

- **After every Wave A task commit (`autonomous: true`):** No automated test pass — Wave A is build + scaffold only. Smoke gate is `pio run -e <env>` exit 0 + `shasum -a 256 .pio/build/<env>/firestarter_<env>.hex` produces a hash + `firestarter dev consistency-check --help` prints usage.
- **After every Wave B task commit (`autonomous: false`):** Each bench task atomically commits EVIDENCE.md row fill + post-fix run binaries; no automated test command runs (hardware-gated).
- **Before `/gsd-verify-work`:**
  - Host pytest suite: `cd firestarter_app && pytest -ra -q` must be green (sanity — confirms `pip install -e .` did not break the install).
  - EVIDENCE.md Verdict block: all 4 VERIFY-NN cells show CLOSED ✓ (or DEFERRED with rationale for VERIFY-01 Case B per D-01).
- **Max feedback latency:** Wave A smoke = ~5 s per `pio run`; Wave B per-task = operator's pace (3-axis verification ≈ 5 min per board).

---

## Per-Task Verification Map

> The acceptance criteria below are bench-evidence assertions, not unit-test outcomes. "Automated command" = the shell command whose stdout/exit-code/file-state confirms the requirement was met.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 29-01-NN | 29-01 | A | scaffold | — | EVIDENCE.md schema appended at line-186 anchor | manual+grep | `grep -c '## Phase 29 — Post-fix Consistency-Check Verification' .planning/v1.6-EVIDENCE.md` → 1 | ✅ EVIDENCE.md exists | ⬜ pending |
| 29-01-NN | 29-01 | A | local build (uno) | — | hex artifact byte-identical to Phase 28 D-07 size table | shell | `[ -f firestarter/.pio/build/uno/firestarter_uno.hex ] && stat -c %s firestarter/.pio/build/uno/firestarter_uno.hex` → 62617 (±tolerance for Phase 28 commit baseline) | ✅ artifact pre-existing | ⬜ pending |
| 29-01-NN | 29-01 | A | local build (leonardo) | — | hex artifact within ±100 B of Phase 28 D-07 leonardo size | shell | `stat -c %s firestarter/.pio/build/leonardo/firestarter_leonardo.hex` → ~68917 | ✅ artifact pre-existing | ⬜ pending |
| 29-01-NN | 29-01 | A | local build (uno328pb) | — | hex artifact within ±100 B of Phase 28 D-07 uno328pb size | shell | `stat -c %s firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex` → ~62854 | ✅ artifact pre-existing | ⬜ pending |
| 29-01-NN | 29-01 | A | host CLI install | — | `dev consistency-check` subcommand surface present | shell | `firestarter dev consistency-check --help` exit 0 + prints `--runs` | ✅ Phase 26 commit `999c3cc` shipped | ⬜ pending |
| 29-01-NN | 29-01 | A | host CLI test gate | — | host pytest suite green (regression sanity) | pytest | `cd firestarter_app && pytest tests/test_consistency_check.py -x` exit 0 | ✅ test file from Phase 26 | ⬜ pending |
| 29-02-NN | 29-02 | B | VERIFY-01 | — | uno328pb sideload + handshake reports `uno328pb` (Case A) OR DEFERRED (Case B) per D-01 | manual+stdout | `firestarter -p /dev/ttyUSB0 fw` stdout contains `controller uno328pb` (Case A) OR `controller uno` (Case B) | ✅ tool exists | ⬜ pending |
| 29-02-NN | 29-02 | B | VERIFY-02 (uno) | — | N=5 byte-identical consistency-check | manual+stdout | `firestarter -p /dev/ttyACM0 dev consistency-check W27C512 --runs 5 --output-dir <path>` exit 0 + stdout `Distinct SHAs: 1` | ✅ tool exists | ⬜ pending |
| 29-02-NN | 29-02 | B | VERIFY-02 (leonardo) | — | N=5 byte-identical consistency-check (FIX CONFIRMED — inverts Phase 26 FAIL) | manual+stdout | `firestarter -p /dev/ttyACM1 dev consistency-check W27C512 --runs 5 --output-dir <path>` exit 0 + stdout `Distinct SHAs: 1` | ✅ tool exists | ⬜ pending |
| 29-02-NN | 29-02 | B | VERIFY-03 | — | 1KB shell-loop byte-identity per board | shell | `for i in $(seq 5); do firestarter -p /dev/ttyXXX dev read W27C512 -s 1024 -a 0 /tmp/r1k_<board>_$i.bin; done; sha256sum /tmp/r1k_<board>_*.bin \| awk '{print $1}' \| sort -u \| wc -l` → 1 | ✅ tool exists | ⬜ pending |
| 29-02-NN | 29-02 | B | VERIFY-04 | — | BENCH-02 write→read→verify cycle on Leonardo+SST27SF512 | shell | `cmp <test-image>.bin /tmp/readback.bin` exit 0 | ✅ tool exists | ⬜ pending |
| 29-02-NN | 29-02 | B | EVIDENCE.md fill | — | All 4 VERIFY-NN cells CLOSED ✓ in Verdict block | grep | `grep -E 'VERIFY-0[1-4].*(CLOSED|DEFERRED)' .planning/v1.6-EVIDENCE.md \| wc -l` → 4 | ✅ EVIDENCE.md exists | ⬜ pending |
| 29-02-NN | 29-02 | B | v1.5-BENCH addendum | — | Post-hoc closure section appended per D-11 | grep | `grep -c '## Phase 24 BENCH-02 post-hoc closure' .planning/v1.5-BENCH-RESULTS.md` → 1 | ✅ file exists | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `firestarter_app/tests/test_consistency_check.py` — exists (Phase 26 commit `999c3cc`, 8 tests, pins stdout regex contract)
- [x] `firestarter/test/native/test_data_input.cpp` — exists (Phase 28 Unity scaffold)
- [x] PlatformIO toolchain installed (verified by researcher via `pio --version`)
- [x] `avrdude` available as fallback (verified locally; v7.x supports `-c urclock`)
- [x] Pre-built `.hex` artifacts already on disk at expected sizes from Phase 28 D-07
- [x] EVIDENCE.md line-186 anchor confirmed present (verified by researcher)
- [x] v1.5-BENCH-RESULTS.md line-45 EOF confirmed (D-11 append point = line 46+)

*Existing infrastructure covers all phase requirements. No Wave 0 scaffold needed.*

---

## Manual-Only Verifications

> Phase 29 is overwhelmingly manual-by-design — the bench is the test rig.

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| uno328pb identity resolution (D-01 Case A/B branch) | VERIFY-01 | Requires physical board reflash + post-flash handshake observation | Operator runs `pio run -e uno328pb -t upload --upload-port /dev/ttyUSB0` (or avrdude fallback per D-01). Then `firestarter -p /dev/ttyUSB0 fw`. Case A if handshake reports `controller uno328pb` → run full Phase 29 verification on this board. Case B if handshake reports `controller uno` → mark row DEFERRED with code-equivalence rationale (Phase 28 D-07 hex size Δ=0). |
| N=5 byte-identity (full-chip) | VERIFY-01, VERIFY-02 | Requires physical board + W27C512 chip in socket | Operator runs `firestarter -p /dev/ttyXXX dev consistency-check W27C512 --runs 5 --output-dir .planning/v1.6/post-fix-runs/W27C512-<board>-<timestamp>/` per board. Acceptance: tool exit code 0 + stdout contains `Distinct SHAs: 1`. Verbatim SHA-256s captured to EVIDENCE.md 9-column row. |
| N=5 byte-identity (1KB) | VERIFY-03 | Requires physical board; tool has no built-in `--size` mode (Phase 26 D-06 deferred) | Operator runs the per-board shell-loop verbatim from CONTEXT.md D-05: `for i in $(seq 5); do firestarter -p /dev/ttyXXX dev read W27C512 -s 1024 -a 0 /tmp/r1k_<board>_$i.bin; done; sha256sum /tmp/r1k_<board>_*.bin`. Acceptance: 5 identical SHA-256 hashes (1 distinct). |
| BENCH-02 write→read→verify | VERIFY-04 | Requires physical SST27SF512 chip + write capability | Operator runs `firestarter -p /dev/ttyACM1 write SST27SF512 <test-image>.bin` (default erase-first; fall back to `firestarter -p /dev/ttyACM1 write SST27SF512 -b <test-image>.bin` if "ERROR: Not supported" surfaces per v1.5 BENCH-02 caveat). Then `firestarter -p /dev/ttyACM1 dev read SST27SF512 -s <full-chip-or-window> /tmp/readback.bin`. Then `cmp <test-image>.bin /tmp/readback.bin`. Acceptance: `cmp` exit code 0. Recommended test image: `python3 -c "import os; open('/tmp/sst_test.bin','wb').write(os.urandom(65536))"`. |
| Hardware metadata snapshot (D-10) | All VERIFY-NN (audit) | Memory `[[user_shield_revisions]]` says ASK which shield rev is in use; EEPROM `hw_revision` byte cannot distinguish Rev 2.2 / 2.0 / mod-Rev 0 | Operator declares per-board: effective `hw_rev`, physical shield revision, native auto-detect rev, FW build (local commit + handshake version string), chip ID. Fills row in EVIDENCE.md hardware metadata snapshot table verbatim. |
| FAIL-handling halt (D-07) | All VERIFY-NN | ROADMAP SC#3 mandates milestone-reopens on any FAIL; no auto-close on FAIL | If any axis FAILs on any board: capture failing-run binaries + sha256s + offset distribution to EVIDENCE.md; mark cell `FAIL`; append post-mortem prose; update STATE.md to "v1.6 milestone re-opened — Phase 28 fix masked vs fixed root cause"; halt bench session; do NOT promote to Phase 30. |

*Every phase behavior except the host-CLI install regression sanity (pytest) is hardware-gated and manual.*

---

## Optional Sanity Gates

| Gate | When | Command | Pass Condition |
|------|------|---------|----------------|
| Phase 27 5-line Python cross-check rerun on post-fix binaries | Wave B end (paranoia gate; not blocking) | `python3 -c "import hashlib,glob; ...` (the 5-line snippet from EVIDENCE.md lines 99-108, re-targeted at the post-fix-runs/ dir) | Stdout reports `Total divergences: 0; single-bit-flip fraction: 0.0%`. If divergences > 0 alongside a `PASS` verdict from the consistency-check tool, something is internally inconsistent — surface as anomaly. |
| Build-hash byte-equivalence check (Phase 30 forward-looking) | Wave A end | `shasum -a 256 firestarter/.pio/build/{uno,leonardo,uno328pb}/firestarter_*.hex` → recorded in EVIDENCE.md per-board build hash record | Phase 30 will rebuild from the merge commit and compare hashes; Phase 29 just captures the LOCAL hashes. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` (shell/grep) or `<manual>` (bench) verification commands listed
- [x] Sampling continuity: every Wave B task has a stdout-or-grep acceptance criterion; no 3 consecutive tasks without an automated check
- [x] Wave 0 covers all MISSING references — none MISSING; existing infrastructure suffices
- [x] No watch-mode flags (pytest runs `-x`/`-ra -q`; Unity runs single-shot)
- [x] Feedback latency: Wave A < 5 s per smoke; Wave B paced by operator (no software-induced latency)
- [ ] `nyquist_compliant: true` — pending plan-checker review (flips to `true` when 29-01-PLAN.md and 29-02-PLAN.md both lock acceptance_criteria to assertions matching this table)

**Approval:** pending plan-phase verification

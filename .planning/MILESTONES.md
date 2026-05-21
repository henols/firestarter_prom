# Milestones

## v1.5 — Arduino Uno (ATmega328PB) Board Support (Shipped: 2026-05-21)

**Phases:** 5 (numbered 21-25) | **Plans:** 6 (Phase 21 = 2, Phase 22 = 1, Phase 23 = 2, Phase 24 = bench-only / 0 plans, Phase 25 = 1) | **Timeline:** 2026-05-20 (planning) → 2026-05-21 (execution + bench validation + close — single-day operator-on-bench cut) | **Ship tag:** 3.0.0b4 (auto-incremented from v1.4's 3.0.0b3 via the v1.4 lockstep mechanism on push to `beta`) | **Commits:** meta-repo ~30, firestarter sub-repo 3 (`da607d4` + `ab7c2a9` + merge `62df517`), firestarter_app sub-repo 4 (`67c8357` + `d13d9b1` + `c184910` urclock fix + merge `75db46e`)

**Delivered:** Added `uno328pb` as a third first-class firmware target alongside `uno` and `leonardo`. Three-board release matrix flows end-to-end: `pio run` emits three `.hex` files per cut → CI workflows' existing `files: .pio/build/**/firestarter_*.hex` glob picks up the new artifact with zero workflow YAML changes → `firestarter fw -i --pre` resolves and flashes the matching artifact for `uno328pb`-reporting devices. Bench-validated on operator's 328PB-Uno (/dev/ttyUSB0): full install path proven on real silicon, post-flash handshake reports `v3.0.0b4, controller: uno328pb`. Existing `uno` + `leonardo` artifacts remain byte-identical (GATE-1.5 preserved via `cmp -s` against baselines captured at firestarter/beta @ 5fd751e).

### Key Accomplishments

1. **Firmware build target (Phase 21 — FW-01..FW-04).** New `[env:uno328pb]` in `firestarter/platformio.ini` between `[env:uno]` and `[env:leonardo]` (`platform = atmelavr`, `board = ATmega328PB`, `-D RURP_BOARD_NAME=\"uno328pb\"`). MiniCore-the-core is bundled inside `platformio/atmelavr@5.2.0` via the stock `ATmega328PB` board file's `build.core` field — no custom board JSON needed (CONTEXT D-05 Path B). Atomic 4-site macro-guard widening (`ARDUINO_AVR_UNO` → `defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)`) in `uno_rurp_shield.cpp`, `rurp_common.cpp` (×2 lines), `rurp_register_utils.h` — no umbrella macro per CONTEXT D-02. `name_firmware.py` reworked to derive PROGNAME from `-D RURP_BOARD_NAME` via `env.ParseFlags()` so the board-id triple (board-id = artifact-name = handshake-string) has a single source of truth.

2. **Release pipeline (Phase 22 — REL-01, REL-02).** `platformio.ini` `default_envs` widened to `uno, uno328pb, leonardo` (Phase 21 D-08 section order); ROADMAP SC#1 literal realigned to match (Phase 21 D-12 hand-off). Zero `.github/workflows/*.yml` edits — both `build.yml:105` and `beta-build.yml:92` already used the `firestarter_*.hex` glob. Verified by `softprops/action-gh-release@v2` attaching the third asset on the first real beta cut.

3. **Host CLI installer (Phase 23 — INST-01, INST-02, INST-03, GATE-01).** Two-file edit in `firestarter_app/`: `firmware.py:_install_with_avrdude` gained `uno328pb` elif branch with `("atmega328pb", "urclock", 115200)` profile (bench-validated; initial guess of `arduino` programmer_id was incorrect — operator's MiniCore-flashed 328PB-Uno ships with Urclock bootloader); `main.py` argparse `-b/--board` `choices=` widened to `["uno", "uno328pb", "leonardo"]`. TDD shape (RED tests landed first; 5 new test methods in `test_firmware_install.py` plus a `_FakeAvrdude` module-local mock helper). Full pytest 82/82 PASS; GATE-01 `pytest -k "not uno328pb"` = 77 PASS byte-identical to pre-Phase-23.

4. **Bench validation (Phase 24 — BENCH-01, BENCH-02).** Merge `v1.5-uno328pb` → `firestarter/beta` triggered CI → GitHub Pre-release `3.0.0b4` with three `.hex` artifacts. `firestarter fw -i --pre --force` on `/dev/ttyUSB0` against the 328PB-Uno + RURP shield: downloaded `firestarter_uno328pb.hex` (22,340 bytes in 0.51s), flashed via avrdude+urclock (5.94s), post-flash handshake reports `version: 3.0.0b4, controller: uno328pb`. VPP 12.4–12.5V stable, VPE 14.4V stable, hardware rev EEPROM-read works. Write path bench-validated for small (16B) and medium (256B) writes via SST27SF512 in socket — every committed bit matches expected `pre AND target` pattern byte-for-byte. Full evidence in `.planning/v1.5-BENCH-RESULTS.md`.

5. **Documentation + milestone close (Phase 25 — DOC-01, DOC-02, MS-01).** Both READMEs (firmware + host CLI) gained three-board references and a per-board PlatformIO env table; ROADMAP Phase 21–24 closed with shipped dates; REQUIREMENTS FW-01..04 + REL-01..02 + INST-01..03 + GATE-01 + BENCH-01..02 all flipped to `[x]`. PROJECT.md updated to "v1.5 shipped 2026-05-21".

### Branch Strategy

Per operator standing instruction (memory `feedback-branching-firestarter-milestones`): all milestone work landed on `v1.5-uno328pb` branches in all 3 repos (meta + firestarter + firestarter_app). Sub-repos merged `v1.5-uno328pb` → `beta` during Phase 24 to trigger the beta CI cut. Meta-repo `v1.5-uno328pb` retains the full planning trail and gets merged to `main` at milestone-close (this file).

### Open backlog from v1.5 bench session (carried to v1.6)

The Phase 24 bench rigor surfaced three pre-existing bugs that do NOT block v1.5 ship but warrant near-term attention:

- **`large-read-data-jitter-uno328pb.md`** (HIGH, **affects all controllers**) — full 64KB streaming reads return ~57% different bytes across consecutive reads. 3-shield A/B/C triage proves the bug is hardware-independent and existed in v1.4 unnoticed (no one byte-compared 64KB round-trip reads before).
- **`w27c512-eeprom-misclassification.md`** (HIGH, operator-tagged "asap") — chip database routes 8 electrically-erasable EEPROMs (W27C512, W27E512, W27C257, W27E257, SST27SF512, SST27VF512, SST27SF256, SST27VF256) to the UV-only EPROM dispatch path. `firestarter erase <chip>` returns `ERROR: Not supported`. Fix requires new firmware dispatch for "12V VPP write + electrical erase" chips, not a one-line override.
- **`avrdude-mcu-detection-fallback.md`** (low) — host CLI enhancement for blank-chip recovery; empirical basis bench-validated (avrdude reveals MCU type via stderr on signature mismatch).

### Key Decisions (locked)

- **Path B for FW-02** (CONTEXT D-05): drop `boards/uno328pb.json`; use stock `platform = atmelavr` + `board = ATmega328PB`; rework `name_firmware.py` to derive PROGNAME from `RURP_BOARD_NAME`. Preserves the locked board-id-triple invariant.
- **`platform = atmelavr`** (RESEARCH Open Q1 resolution): `MCUdude/MiniCore` is not a registered PlatformIO platform; the MiniCore core ships bundled inside atmelavr@5.2.0.
- **`programmer_id="urclock"`** for uno328pb (bench-validated): MiniCore's stock bootloader on the operator's 328PB-Uno is Urclock, not optiboot. Phase 23 CONTEXT D-02 documented this as a known contingency; bench confirmed it 2026-05-21.
- **GATE-1.5 byte-identity** (CONTEXT D-04): `firestarter_uno.hex` + `firestarter_leonardo.hex` from v1.5 cuts byte-identical to pre-v1.5 (modulo `update_version.py` drift). Baselines captured at `firestarter/beta` tip `5fd751e` (SHA-256 `0dd5c01a…` uno, `f49e2a57…` leonardo); verified via `cmp -s` during Phase 22.
- **Local milestone branches, beta-cut only on operator authorization** (memory `feedback-branching-firestarter-milestones`): work stays on `v1.5-uno328pb` until the operator explicitly authorizes a merge to `beta`. The "merge in to beta and test that we can install via the app to the pb" instruction on 2026-05-21 was the explicit auth point.

---

## v1.4 — Beta & Pre-release Deployment Pipeline (Shipped: 2026-05-20)

**Phases:** 6 (numbered 15-20) | **Plans:** 10 (Phase 15 = 4, Phase 16 = 1, Phase 17 = 1, Phase 18 = 2, Phase 19 = 1, Phase 20 = 1) | **Timeline:** 2026-05-20 (single-day cut: planning + execution + live verification including real-hardware flash) | **Ship tag:** 3.0.0b3 (auto-incremented from b1/b2 during E2E iteration; .pyc hygiene fix triggered b3) | **Commits:** meta-repo 56, firestarter sub-repo 13, firestarter_app sub-repo 17

**Delivered:** Added a parallel beta / pre-release deployment channel across both Firestarter sub-repos without touching the existing main → stable pipelines. Branch-driven trigger (`beta` branch in each sub-repo) wired to new beta workflows that emit PEP 440 / matching pre-release version strings, publish PyPI pre-release wheels (installable via `pip install --pre`), and create GitHub Pre-releases with `make_latest: false` carrying per-board `firestarter_*.hex` artifacts. App and firmware ship locked-step on a single `BETA_VERSION` operator input. Beta-installed app grows three new CLI flags (`--pre`, `--firmware-version`, `firmware list`) plus a PEP 440-safe version comparator; stable-installed app's `firestarter --install` defaults remain byte-identical to pre-v1.4. Documentation: both READMEs grew a Beta channel section; meta-repo `v1.4-RELEASE-PROCEDURES.md` documents the release-engineer cutting workflow.

### Key Accomplishments

1. **Versioning + lockstep foundation (Phase 15 — VER-01/02/03).** Extended both
   sub-repos' `.github/scripts/update_version.py` to recognize beta-branch context
   and emit PEP 440 pre-release identifiers (`X.Y.ZbN`, `X.Y.ZrcN`) on `BETA_VERSION`
   input, preserving stable-branch patch-bump behavior verbatim. Shared validation
   regex `^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$` between both scripts (string-equality
   lockstep check). Lockstep mechanism finalized as **manually-paired beta-branch
   push with explicit `BETA_VERSION` input** (rejected: shared meta-repo VERSION file,
   cross-repo `repository_dispatch`). Documented in `15-LOCKSTEP-PROCEDURE.md` and
   proven via `lockstep-dryrun-fixture.sh` cross-script byte-identity check.

2. **App beta release pipeline (Phase 16 — REL-01, GATE-01).** New
   `firestarter_app/.github/workflows/beta-release.yml` — single-file deliverable
   covering push:beta + workflow_dispatch triggers, inline CI gates (pytest),
   Phase 15 version-bump call, GitHub Pre-release creation, and PyPI publish via
   the existing `publish.yml`. GATE-01 preserved: stable `main`-push behavior
   byte-identical to pre-v1.4.

3. **Firmware beta release pipeline (Phase 17 — REL-02, GATE-02).** New
   `firestarter/.github/workflows/beta-build.yml` — single-file deliverable
   covering push:beta + workflow_dispatch triggers, inline catalog/codegen/Unity/
   PlatformIO gates, Phase 15 version-bump auto-commit, `pio run` build, and
   GitHub Pre-release with `firestarter_*.hex` artifacts per board (Uno +
   Leonardo). GATE-02 preserved: stable `main`-push behavior + existing
   `build.yml` artifacts byte-identical to pre-v1.4.

4. **Beta-aware firmware downloader (Phase 18 — INST-01/02/03/04).** Scope
   amendment 2026-05-20 added a narrow CLI carve-out to make the published beta
   firmware actually installable. `firestarter --install` (no flags) preserves
   byte-identical stable behavior; `--pre` fetches highest PEP 440 pre-release;
   `--firmware-version X.Y.ZbN` pins exact tag via `/releases/tags/{tag}`;
   `firestarter firmware list [--all|--pre|--stable]` enumerates releases.
   `_compare_versions` refactored to PEP 440-safe via `packaging.version.Version`.

5. **Documentation (Phase 19 — DOC-01/02/03).** App + firmware READMEs grew
   Beta channel sections (install via `pip install --pre` + `firestarter --install
   --pre/--firmware-version`/`firmware list`; stability guarantee; issue-reporting
   guidance). Meta-repo `.planning/v1.4-RELEASE-PROCEDURES.md` documents the
   release-engineer cutting workflow end-to-end, consuming `15-LOCKSTEP-PROCEDURE.md`
   verbatim with corrected workflow filenames.

6. **End-to-end acceptance gate (Phase 20 — E2E-01, MS-01).** Real beta cut in
   both repos following the documented procedure; PyPI shows `<BETA_VERSION>`,
   `pip install --pre` works cleanly, firmware GitHub Pre-release page carries
   the expected per-board `.hex` artifacts, both repos' tags string-equal per
   VER-03, beta-installed app's `firestarter fw -i --pre` fetches the matching
   firmware, and stable-installed app's `firestarter fw -i` (no flags) still
   pulls stable firmware (INST-01 non-regression). Verified via the automated
   `.planning/v1.4-e2e-verify.sh` (PyPI + GitHub Releases API checks) and the
   6-test operator checklist `20-HUMAN-UAT.md`.

### Stats

| Metric | Value |
|--------|-------|
| Phases | 6 (numbered 15-20) |
| Plans | 10 (Phase 15 = 4, Phase 16 = 1, Phase 17 = 1, Phase 18 = 2, Phase 19 = 1, Phase 20 = 1) |
| Requirements | 16/16 mapped, 16/16 shipped (E2E-01 + MS-01 close on operator green) |
| Meta-repo commits | 56 (`git log --oneline 261a430^..HEAD | wc -l` — from `docs(15): capture phase context` to ship) |
| Firmware sub-repo commits | 13 (`git log --oneline 6c66b29^..origin/beta | wc -l` — from `test(15-01): wave 0 scaffold` to 3.0.0b3 cut) |
| Host sub-repo commits | 17 (`git log --oneline a7390cc^..origin/beta | wc -l` — from `test(15-01): wave 0 scaffold (app)` to 3.0.0b3 cut) |
| Live cut iterations | 3 (`3.0.0b1` → `3.0.0b2` → `3.0.0b3`; b1 cut surfaced 5 substrate fixes E2E-01..05, b2 added firmware.py parser fix E2E-06, b3 added .pyc hygiene) |
| Hardware flash validated | Uno (`/dev/ttyACM0`) + Leonardo (`/dev/ttyACM1`) at `3.0.0b3` via `firestarter fw -i --pre` end-to-end |
| New workflow files | 2 (`firestarter_app/.github/workflows/beta-release.yml`, `firestarter/.github/workflows/beta-build.yml`) |
| Existing workflow files modified | 0 (additive only — GATE-01/GATE-02 preserve stable verbatim) |
| New CLI flags on `firestarter` | 3 (`--pre`, `--firmware-version`, `firmware list`) |
| New planning docs | `.planning/v1.4-RELEASE-PROCEDURES.md`, `.planning/v1.4-e2e-verify.sh`, `.planning/v1.4-archive.sh`, `15-LOCKSTEP-PROCEDURE.md`, `lockstep-dryrun-fixture.sh` |
| Hardware impact | None (software-only milestone; no firmware behavior change, no chip support change) |

### Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Branch-driven beta (push to `beta` branch) | Mirrors current `main` -> stable trigger shape; one mental model | Good (single trigger pattern across both pipelines; operator picks the branch, not a tag) |
| PEP 440 pre-release identifiers (`X.Y.ZbN`/`X.Y.ZrcN`) on same PyPI index | TestPyPI adds operator friction; `pip install --pre` is the cleaner opt-in | Good (single source of truth; stable users unaffected) |
| Lockstep mechanism = manually-paired beta-branch push with explicit `BETA_VERSION` input | Rejected alternatives: shared meta-repo VERSION file (cross-repo write coupling), cross-repo `repository_dispatch` (requires cross-repo PAT with `repo` scope) | Good (no new cross-repo trust surface; operator-readable; `lockstep-dryrun-fixture.sh` proves byte-identity) |
| Firmware GitHub Pre-release with `make_latest: false` | `/releases/latest` API automatically filters pre-releases out -- protects stable-installed `firestarter --install` without code changes | Good (INST-01 non-regression preserved via API filtering, not via brittle client-side logic) |
| Stable pipeline preservation (GATE-01 + GATE-02) | v1.4 is additive plumbing; main -> stable behavior byte-identical to pre-v1.4 | Good (zero regressions; verified by independent main-push smoke during Phase 16/17 development) |
| Scope amendment 2026-05-20: add Phase 18 Beta-Aware Firmware Downloader | Without `--pre`/`--firmware-version`/`firmware list`, published beta firmware was uninstallable via `firestarter` CLI -- half a feature | Good (full operator round-trip: cut beta -> install beta app -> install beta firmware via app) |
| Auto-promotion beta -> stable workflow DEFERRED to v1.5+ | Manual fast-forward merge `beta` -> `main` is sufficient for the milestone's first beta cuts; auto-promotion needs real-world usage data before designing | Revisit (when beta channel sees real use) |

### Known Gaps (deferred — pointers to REQUIREMENTS.md Future Requirements)

Per D-15, the following are explicit pointers to existing entries in `.planning/REQUIREMENTS.md`
section "Future Requirements (deferred past v1.4)":

- **Auto-promotion beta -> stable workflow** — `promote.yml` (or equivalent) that fast-forwards
  `beta` -> `main` and bumps to stable in one CI run. Deferred until beta channel sees real use
  and the promotion pattern stabilizes. See REQUIREMENTS.md Future Requirements.

- **Branch-protection rules on `beta` branch** — accidental force-pushes possible today. Add
  post-v1.4 if accidental-push problems surface. See REQUIREMENTS.md Future Requirements.

- **Signed release artifacts** (sigstore / GPG) — both stable and beta ship unsigned today;
  signing is a dedicated milestone covering both at once. See REQUIREMENTS.md Future Requirements.

- **TestPyPI publishing channel** — explicitly rejected for v1.4 (operator friction); could
  revisit if beta operators report needing isolated install testing. See REQUIREMENTS.md
  Future Requirements.

- **Beta installation metrics / telemetry** — not in scope; future release-ops milestone.
  See REQUIREMENTS.md Future Requirements.

- **Per-board `--pre` fallback** — if Uno has a beta but Leonardo doesn't, INST-02's fallback
  policy is unspecified. Add explicit policy in a later milestone if it surfaces. See
  REQUIREMENTS.md Future Requirements.

- **Cached firmware download / offline install** — app always hits GitHub today; cache layer
  is a separate feature. See REQUIREMENTS.md Future Requirements.

### Carry-forward technical debt

Items surfaced during v1.4 development but explicitly NOT cleaned up here (preserves
v1.4's "additive plumbing only" discipline). Each is documented at the listed
phase-local artifact and may be addressed in a follow-on milestone:

- **Phase 17 WR-01** — pre-existing `build.yml` technical debt (vestigial `setup-python@v4` step, `.editorconfig/**` glob).
- **Phase 18 CR-01..CR-03** — pre-existing `update_version.py` code-review findings (atomic file write, none-return crash, rc-series tag fallback).
- **Phase 15 D-25** — `_dev` / `-dev` suffix conventions in version files (e.g. `2.0.7_dev`, `3.0.0-dev`); silently truncated by the version-file parse regex today.

### Hardware impact

None — v1.4 is CI/CD plumbing + consumer-side CLI + docs only. Firmware semantics
stay at v1.2's 3.0.0-dev baseline. No new chip support, no flash budget movement,
no bench session required for milestone close.

---

## v1.2 — Message-ID Logging Rework (Shipped: 2026-05-19)

**Phases:** 4 (numbered 6-9; Phase 10 closed by this milestone-close workflow) | **Plans:** 32 | **Timeline:** 2026-05-08 → 2026-05-19 (~11 days, 108 meta-repo commits, 104 firmware + 64 host sub-repo commits)

**Delivered:** Replaced every firmware text-prefix log emit (`OK:` / `INIT:` / `MAIN:` / `END:` / `INFO:` / `WARN:` / `ERROR:` / `DEBUG:`) with a 1-byte message-ID + raw-byte-param wire protocol driven by a canonical catalog in the meta-repo. The catalog is the single source of truth; codegen emits a C++ header for firmware and a Python module for the host, both regenerated and byte-identity-checked in CI. Old log helpers (`rurp_log`, `rurp_log_P`, `LOG_*_MSG` PROGMEM strings, `log_info_const` / `log_error_format` / `log_warn`) deleted. Leonardo flash 98.7% → **85.4%** (−13.3 pp / −3,792 B of headroom); firmware major bumps to 3.0.0 to enforce lockstep upgrade.

### Flash-Savings Comparison (LMIG-04 acceptance — DOC-02 anchor)

| Snapshot | Leonardo Flash | Uno Flash | SRAM (Uno) | Notes |
|----------|---------------|-----------|------------|-------|
| v1.1 close (baseline) | 28,292 / 28,672 B = **98.7%** | n/a | n/a | Carried v1.1 risk: < 400 B Leonardo headroom |
| v1.2 Phase 6 close | 28,292 B = 98.7% | 26,178 / 32,256 B = 81.1% | 1,593 B | Catalog + helpers landed; no call-sites converted yet (LMIG-01 coexistence proven) |
| v1.2 Phase 7 close | 27,952 B = 97.5% | 25,818 B = 80.0% | 1,593 B | ERROR + WARN + INFO converted (LMIG-02) |
| v1.2 Phase 8 close | 26,096 B = 91.0% | 23,718 B = 73.5% | 1,497 B | State-machine prefix converted (LMIG-03); MSG_DATA_CHUNK streaming (W-04) |
| v1.2 Phase 9 close | 24,500 B = **85.4%** | 22,282 B = 69.1% | 1,497 B | Legacy infra deleted; 3.0.0-dev bump (LFW-03/04, LMIG-04) |
| v1.2 ship | 24,482 B = **85.4%** | 22,262 B = **69.0%** | 1,497 B | Post-ship polish: drop MSG_OK_FW_HANDSHAKE, INFO echo, helper refactor |

### Key Accomplishments

1. **Canonical message catalog + codegen pipeline** (LCAT-01..05, Phase 6 Plan 01)
   — `tools/catalog/messages.toml` is the single source of truth for every log
   message in the system. `tools/catalog/codegen.py` (stdlib-only, deterministic,
   byte-identical re-runs) emits both `firestarter/include/messages.h` (C++) and
   `firestarter_app/firestarter/messages.py` (Python) from the same TOML.
   `sync_to_subrepos.sh` distributes the canonical copy to both sub-repos with
   `diff -q` byte-identity guarantees. CI workflow (`.github/workflows/catalog-
   sync-check.yml` in meta-repo + matching gates in both sub-repos) fails any
   PR that introduces drift.

2. **ID-encoded wire protocol** (LFW-01/02, LHOST-01/02, Phase 6 Plans 02-03)
   — `rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count)`
   replaces the legacy `rurp_log(LOG_*_MSG, char*)` family. Wire frame is
   `MAGIC_PREAMBLE | len_u16 | id | params | crc8 | 0x0A` (W-04 wide len
   added in Phase 8 for MSG_DATA_CHUNK > 255 B). Host decoder in
   `serial_comm.py::_decode_id_frame` handles the same shape with WR-03
   guard for text-format catalog entries.

3. **All firmware log call-sites migrated** (LMIG-02, LMIG-03, LFW-03, Phases 7-9)
   — Every text-prefix emit converted across 13 sub-systems
   (`eprom_operations`, `eeprom_28c`, `flash_intel`, `flash_type_3/4`,
   `hardware_operations`, `memory`, `firestarter` main loop, `dev_tools`,
   `json_parser`, plus catalog/helpers). Composite shapes added for
   `MSG_OK_REV` (P-02 [u8, u8]), `MSG_OK_CFG` (P-03 [u32, u32, u8]),
   `MSG_DATA_CHUNK` (W-04 wide bytes), and the host's sentinel-aware
   `_format_message` renderer.

4. **Legacy log infrastructure deletion** (LFW-03/04, Phase 9 Plan 02)
   — Atomic deletion across 23 files: `logging.h` + `logging.c` outright;
   `rurp_log`, `rurp_log_P`, `_firestarter_log_ram`, `_firestarter_log_progmem`,
   `LOG_OK_MSG`, `send_ack`, `send_ack_const`, `debug_setup`, `log_debug`,
   plus all four `#ifdef SERIAL_DEBUG` SoftwareSerial blocks + RX_DEBUG/TX_DEBUG
   defines. `#include "logging.h"` swept from 20 sites. Firmware version
   bumped to `3.0.0-dev` (LFW-05) so the host's `major < 3` guard refuses
   pre-v1.2 firmware cleanly.

5. **Phase 9 flash measurement** (LMIG-04, Phase 9 Plan 05 Task 1)
   — Cold-cache PlatformIO measurement on Leonardo + Uno, two delta tables
   in `09-MEASUREMENT.md`: incremental Phase 8 → Phase 9 attribution and the
   milestone-close v1.1 → v1.2 comparison. SC#1 PROGMEM exemption audit
   landed (12 named-symbol declarations: MAGIC_PREAMBLE + CRC8_TABLE +
   json_parser keys + key_parsers[]; 1 inline `F(...)` literal at LFW-05
   bootstrap; zero uncategorized log-purposed PROGMEM hits).

6. **Post-ship polish: protocol simplification + verbose diagnostics**
   (post-Phase-9 cleanup, ~9 commits) — Dropped per-command `MSG_OK_FW_HANDSHAKE`
   composite (P-04) in favour of a plain `MSG_OK_READY` setup-complete ack;
   added 4 single-purpose INFO emits (`MSG_INFO_FW` / `_HW` / `_PHYSICAL_HW` /
   `_CMD` at 0x5A-0x5D) that mirror the dropped handshake content under the
   `FLAG_VERBOSE` runtime gate. Migrated the EXTRA_INFO_LOGGING build-flag
   block (BUF_VAL, TOKEN_COUNT, FLAG_*, BUFFER_SIZE, MEM_SIZE, ADDR_MASK,
   MATCH_LINES) to SERIAL_DEBUG-gated `DBG_*` sub_ids (0x29-0x35) so the
   diagnostics ride the existing DEBUG channel — zero production wire bytes,
   full breadcrumb chain available in `-D SERIAL_DEBUG` builds.

7. **Host probe path + symbolic command names** — Refactored `_probe_port`
   to send a dedicated `CMD_FW_VERSION` pre-probe with two-ack pattern
   handling (skip setup-complete "Ready", parse "OK: FW: ..." for version
   validation) so the host correctly recognizes 3.0.0-dev firmware without
   the dropped FW_HANDSHAKE in every ack. `COMMAND_NAMES` lookup in
   `constants.py` + a `_format_message` branch renders `MSG_INFO_CMD` as
   "Cmd: 0x0f (HW_VERSION)" and the same annotation applies to `DBG_CMD`
   via the new MSG_DEBUG sub_id decoder path.

8. **Helper-function refactor of macro internals** — Factored
   `LOG_ID_U{8,16,24,32}` byte-pack bodies into `rurp_log_id_u{8,16,24,32}`
   helpers in `rurp_serial_utils.cpp`. The macros collapse to one-liners;
   each call site emits a single CALL instead of inlining the byte-array
   build. Net Flash impact small (−20 B Uno / −18 B Leonardo) since
   AVR-gcc was already inlining well — main value is code cleanliness.

### Stats

| Metric | Value |
|--------|-------|
| Phases | 4 active phases (6-9) + Phase 10 milestone-close (this workflow) |
| Plans | 32 (Phase 6 = 6, Phase 7 = 13, Phase 8 = 8, Phase 9 = 5) |
| Meta-repo commits | 108 |
| Firmware sub-repo commits | 104 |
| Host sub-repo commits | 64 |
| Files changed (meta-repo + planning) | 101 files / +26,173 / −63 |
| Firmware LOC | 4,932 (src + include, C++) |
| Host LOC | 5,200 (firestarter/, Python) |
| Catalog LOC | 1,743 (messages.toml + codegen.py) |
| Native tests | 20/20 PASS (test_dispatch + test_messages) |
| Host pytest | 29/29 PASS (test_decoder + test_fwguard + others) |
| Hardware-bench verified | Uno + Leonardo at 3.0.0-dev, verbose + SERIAL_DEBUG modes |

### Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| ID width = 1 byte | < 100 distinct strings; generous headroom for future growth | ✓ Good (60 catalog entries + 41 DBG sub_ids = 101 total; comfortable) |
| Raw byte params, no type tags on wire | Catalog declares each ID's shape; type tags would waste bytes | ✓ Good (Phase 8 W-04 added `bytes` variable-length shape without protocol break) |
| Codegen output committed to both sub-repos | Operators can build without running codegen first; CI drift gate catches changes | ✓ Good (zero drift incidents; tags ship reproducibly) |
| Phased migration (infra → batched convert → delete last) | Allows both old + new paths to coexist during migration; safer than big-bang | ✓ Good (each phase shipped a working build; LMIG-01 coexistence proven Phase 6) |
| Lockstep upgrade (no backwards compat) | Wire format change too invasive to support both; FW major bump enforces | ✓ Good (3.0.0-dev gate works; host pre-v1.2 refusal clean) |
| MSG_OK_FW_HANDSHAKE → plain MSG_OK_READY (post-ship polish) | Per-command FW echo over-specified; INFO emits handle verbose case better | ✓ Good (saved ~5 wire bytes per command; INFO echo restored visibility) |
| EXTRA_INFO_LOGGING → SERIAL_DEBUG | Build-flag gate is coarser than macro-level; DBG channel already SERIAL_DEBUG-gated | ✓ Good (10 fewer INFO catalog entries; debug breadcrumbs richer) |
| Helper functions for byte-pack | Deduplicate ~10-line macro bodies | ⚠️ Revisit (Flash savings ~20 B — AVR-gcc was already optimizing well; kept for code cleanliness) |

### Known Gaps / Hardware-Pending UAT

Recorded in [STATE.md `## Deferred Items`](.planning/STATE.md). All four items bundle on a single chip-seated W27C512 bench session:

- **Phase 09 Plan 05 Task 3** — chip-seated W27C512 write + readback on both boards (Plan 09-05 hardware UAT)
- **Phase 08 SC#2 / SC#3** — chip-seated UAT carried forward from Phase 8 close (same scope)
- **Phase 08 HUMAN-UAT.md** — 2 pending scenarios (same scope, different artifact)
- **v1.1 debug session `fm1608-fresh-chip-baseline`** — parked since 2026-05-18; unrelated to v1.2 scope (needs different Uno R3 to unblock)

Known deferred items at close: **4** (see STATE.md Deferred Items).

### v1.1 Items Carried Forward (still open after v1.2)

- v1.1 Phase 4 — FM1608 byte-0 read bug (parked, needs different Uno R3)
- WARNING-4 — `firestarter_test.sh` / `write_test.sh` reference deleted `database_generated.json`
- v1.1 DOC-01 — v1.1 milestone close (Phase 5 of v1.1 deferred)

---

## v1.0 — Protocol-Aware Programming Architecture (Shipped: 2026-05-11)

**Phases:** 13 | **Plans:** 22 | **Timeline:** 2026-05-08 → 2026-05-11 (4 days, 66 commits)

**Delivered:** Replaced the guessing-based chip-type pipeline with an explicit
algorithm-first architecture where minipro `protocol_id` flows authoritatively
from upstream XML through the database, wire protocol, and firmware dispatch —
and the firmware executes exactly that algorithm for every chip in the 743-entry
DB. Two safety-critical hazards closed (BLOCKER-1, BLOCKER-2, WARNING-5).

### Key Accomplishments

1. **Algorithm-first wire protocol** (REQ-SER-01, REQ-FW-01) — `firestarter_handle_t`
   carries an explicit `algorithm` integer; `memory.cpp::configure_memory`
   protocol-prefix dispatch covers all 13 KNOWN_PROTOCOLS (0x05/0x06/0x07/0x08/
   0x0B/0x0D/0x0E/0x10/0x27/0x28/0x29/0x35/0x39); legacy `type` enum retained
   as fallback only. Verified by 15/15 Unity dispatch tests on `[env:native]`
   plus `check_dispatch.py` PASS across all 743 chips.

2. **Database pipeline canonicalized** (REQ-DB-01..05, Phases 01 + 11) — Single
   `build_db.py` fetches `infoic.xml` from upstream minipro at runtime,
   parses deterministically to `minipro_complete_db.json` with explicit
   `algorithm` integer, decoded-millivolt `vpp`, correct DIP28 variant splitting
   (`DIP28_27512` / `DIP28_27256` / `DIP28_2764`), unknown-protocol chips
   skipped with WARN. Legacy `parse_db.py`, `infoic.xml`, `verified.txt`,
   `database_generated.json`, `pin-maps.json` all removed.

3. **Five new firmware handlers** — `configure_eprom` (UV-EPROM STD/QUICK/LEGACY,
   Phase 03), `configure_flash3` (AMD-style sector erase, Phase 04),
   `configure_flash_intel` (Intel command-register flash, Phase 05),
   `configure_eeprom28c` (AT28C SDP-disable + DQ7-polling page write, Phase 06),
   `configure_sram` (5V SRAM safe no-op, Phase 12).

4. **Pre-write safety stack** (REQ-SAF-01/02/03, Phases 03 + 07) — VPP ADC
   compare before first write pulse on UV-EPROM and 28C-EEPROM paths;
   chip-ID validation for Intel + AMD + UV-EPROM (`A9_VPP_ENABLE` sequence
   for 27Cxxx); blank check across Flash/EEPROM write inits gated by
   `!FLAG_SKIP_BLANK_CHECK`.

5. **Static-pin and address-bus correctness** (REQ-FW-05/06, Phase 10) —
   `static_high_mask` end-to-end (`pinouts.json` static-high-pins → wire JSON
   static-high → `bus_config_t.static_high_mask` → `mem_util_remap_address_bus`
   unconditional OR); replaces hardcoded `pins == 24` heuristic for tied-high
   CE2/NC pins. Dead `READ_WRITE == WRITE_FLAG` condition replaced with the
   physical-reality `if (handle->pins < 32)` plus VPE_TO_VPP/A16-sharing comment.

6. **CLI hardware-compatibility surface** (REQ-UX-01/02, Phase 09) —
   `firestarter search` flags chips with no valid pinout via `[!]` marker;
   `firestarter info --adapter` prints a DIP-mirrored two-column physical-pin →
   RURP-signal table derived entirely from `pinouts.json`, enabling adapter
   wiring without source-code reference.

7. **Three safety-critical close-out phases** —
   - **Phase 11** consolidated the build pipeline to `build_db.py` and removed
     all legacy artifacts (REQ-DB-05; byte-identical regeneration verified).

   - **Phase 12** closed BLOCKER-1 (277 chips fell through to "Memory type
     0x%02x not supported" before the protocol-prefix dispatch) + BLOCKER-2
     (52 SRAM chips routed to `configure_eprom` with 12V VPP regulator on 5V
     parts). Fixed at three layers: firmware dispatch + Python `_ALGO_MEM_TYPE`
     table + `build_db.py` SRAM tagging.

   - **Phase 13** closed WARNING-5 (23 DIP28_2764 5V EEPROMs mistagged in
     upstream minipro as `algorithm=0x07` would have applied 12V to socket
     pin 1 = A14 address line on write). Data-layer-only fix via inline
     3-predicate override in `build_db.py` flipping these chips to `0x0D`
     (`EEPROM_POLL` → `configure_eeprom28c`, pure 5V path with zero VPP
     regulator engagement). Permanent regression guard `_28C_EEPROM_HAZARD_PINOUT`
     in `check_dispatch.py`.

### Stats

- **Files modified:** firmware (Arduino C++) + Python CLI submodules; meta-repo
  tracks `.planning/` only

- **Verification:** Phase 11 (4/4), Phase 12 (8/8), Phase 13 (8/8) formally
  verified end-to-end. Phases 01-10 verified by independent
  `INTEGRATION-CHECK.md` + Phase 12 `check_dispatch.py` regression on the full
  743-chip DB.

- **E2E flows shipped:** `write -e W27C512`, `write -e AM29F040`,
  `write -e SST39SF040`, `erase -s 0x10000 -e SST39SF040`, `write -e 6116`
  (SRAM safe), `write -e AT28C256` (now safe via Phase 13), `write -e AM28F010`
  (Intel — see Known Gaps), `info <chip> --adapter`, `python tools/build_db.py`.

### Key Decisions

- **Database source:** minipro `infoic.xml` via `build_db.py` (not hand-curated
  JSON). Outcome: ✓ — 743 chips covered without per-chip curation overhead.

- **Wire protocol:** New explicit `algorithm` integer field (minipro
  `protocol_id`); `type` retained as legacy fallback. Outcome: ✓ — all 13
  KNOWN_PROTOCOLS dispatched correctly; no regressions.

- **Firmware dispatch:** Protocol-prefix `if-return` block per KNOWN_PROTOCOLS
  entry in `configure_memory`, mem_type chain retained only for legacy
  user-override DB entries. Outcome: ✓ — verified by Phase 12 `check_dispatch.py`.

- **Packages in scope:** DIP 24, 28, 32 only. Outcome: ✓ — SMD/PLCC/serial
  filtered cleanly by `build_db.py`.

- **WARNING-5 fix:** Data-layer override in `build_db.py` rather than
  per-chip firmware switch. Outcome: ✓ — preserves the "algorithm is
  authoritative" contract while routing around the upstream minipro
  classification error for 23 5V EEPROMs.

### Known Gaps (accepted as tech debt for v1.1)

Captured from `.planning/milestones/v1.0-MILESTONE-AUDIT.md` (status:
`gaps_found`). Audit-time score: 4/18 SATISFIED, 13 PARTIAL (verification-gap
only), 1 UNSATISFIED.

- **REQ-SAF-01 partial — Intel-flash write path** (WARNING-1): `flash_intel_write_init`
  (`firestarter/src/proms/flash_intel.cpp:47-62`) enables `REGULATOR |
  P1_VPP_ENABLE` and delays 500ms before the first write pulse, but never calls
  `rurp_read_voltage_mv()` ADC compare. The UV-EPROM and 28C-EEPROM paths
  satisfy REQ-SAF-01; the Intel-flash family (39 chips, algo=0x10, highest VPP
  in firmware) does not. **Severity: WARNING.** Fix scope: 1-2 lines in
  `flash_intel.cpp`; pattern mirrors `eprom_check_vpp`.

- **Phases 01-10 lack formal VERIFICATION.md files** (verification-gap on 13
  requirements). Wiring is independently verified by `.planning/INTEGRATION-CHECK.md`

  + Phase 12 `check_dispatch.py` (743/743 chips PASS) + Phase 13 hazard guard
  (0 violations) + 15/15 Unity dispatch tests. By the workflow rule "missing
  VERIFICATION.md = unverified phase", 10 of 13 phases remain structurally
  unverified. Optional retroactive `/gsd-validate-phase` runs would close.

- **WARNING-2 — 28C chip-ID forward-compat hazard**:
  `eeprom_28c.cpp::eeprom28c_write_init` ignores `handle->chip_id`. Vacuous
  today (zero 0x0D chips in regenerated DB carry `chip_id_value`) but breaks
  REQ-SAF-02 the moment a user-override or upstream DB change populates
  chip_id for an AT28C-family chip.

- **WARNING-3 — wire-protocol key naming**: JSON `"vpp"` key now carries
  millivolts (was volts) — semantic overload. Recommend renaming wire key to
  `"vpp_mv"`. `firestarter_app/CLAUDE.md` example currently shows a phantom
  `"vpp_mv"` key that is not emitted.

- **WARNING-4 — test-script drift**: `firestarter_test.sh:31` and
  `write_test.sh:17` reference the deleted `database_generated.json`. Breaks
  the documented hardware-integration E2E flow.

- **`build_db.py` robustness**: Bare `except:` at lines ~138-186 (silent chip
  drops + KeyboardInterrupt swallow). `requests.get` lacks `raise_for_status()`
  and `timeout` (non-200 upstream silently overwrites DB). Pre-existing,
  out-of-scope of Phase 11 lock.

- **Lost `verified` field**: `minipro_complete_db.json` no longer carries the
  `verified` field; `database.py::get_eproms(verified=True)` silently returns
  empty. Carried in `11-VERIFICATION.md` follow_ups.

- **DIP24/DIP28/DIP32 `static-high-pins` coverage**: Only DIP24 variants
  populated in `pinouts.json` today. DIP28/DIP32 quirk pins (CE2, JEDEC-tied
  NC) could be added in a future phase (INFO-3).

- **`DIP24_2732` pinout** never appears in regenerated DB (no 24-pin
  variant=0x01 chips survive the DIP/memory-type filter on current
  `infoic.xml`). May be intentional; flag for review.

### Hardware Verification

Not performed in this milestone — no RURP shield available in the dev
environment. All verification was structural (code/DB/dispatch tests). The
documented hardware integration tests (`firestarter_test.sh`, `write_test.sh`)
should be re-run against a physical board before declaring the four
chip-family canon (W27C512, 29F040, SST39SF040, AT28C256) hardware-validated.

---

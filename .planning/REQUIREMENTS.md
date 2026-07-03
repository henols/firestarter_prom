# Requirements: Firestarter — v1.21 Community Chip-Validation Command

**Defined:** 2026-07-02
**Core Value:** Algorithm-first dispatch is authoritative; v1.21 extends the project's reach by letting the *community* prove chip support on hardware the maintainer doesn't own — turning "can't verify, don't have that chip" deferrals into actionable, structured evidence.

Source: `/gsd-explore` 2026-07-02 seed `community-chip-validation-command.md` + design note `dev-test-design-decisions.md`; research `.planning/research/SUMMARY.md` (HIGH confidence, 4-stream convergent). Phase numbering continues from v1.20's Phase 107 → v1.21 starts at **Phase 108**.

## v1 Requirements

Requirements for milestone v1.21. Each maps to a roadmap phase.

### Sweep Engine (SWEEP)

- [x] **SWEEP-01**: `firestarter dev test <chip>` derives a per-chip test plan from the chip's DB fields (`protocol`/`electrical-type`/`FLAG_CAN_ERASE`), running only the operations that chip supports — without re-invoking build-time `classify()`, and bypassing the `resolve_chip` support-status guard for plan derivation only.
- [x] **SWEEP-02**: Each operation (id, read, write, verify, erase, blank-check) runs as an independent, non-fatal step with an explicit per-op verdict (`OK`/`BAD`/`NA`/`SKIPPED`); a failure in one step never aborts the remaining steps.
- [x] **SWEEP-03**: The sweep runs id-check first; a chip-ID mismatch hard-gates the destructive steps (fail-safe — chip left pristine) while still recording the read/id findings.
- [x] **SWEEP-04**: Destructive/verify steps run N≥2 times; disagreement across runs is reported as `marginal` rather than PASS or FAIL.
- [x] **SWEEP-05**: Non-destructive by default (id + read + blank-check only); the run prints a loud "only N of M tests ran — pass `--destructive` on a scrap chip for the rest" banner whenever N < M.

### Pattern & Diagnosis (PATT)

- [x] **PATT-01**: The write/verify step uses an **address-derived** data pattern (byte = f(address), folding high address bits in), preceded by a cheap all-0x00/all-0xFF pre-pass — never a fixed pattern that is blind to stuck/shorted address lines.
- [x] **PATT-02**: A byte-mismatch fingerprint classifier categorizes verify failures (blank/contact fault vs address-line fault vs transport fault) from the mismatch distribution; it is coupled to the address-derived pattern in the same phase.
- [x] **PATT-03**: UV EPROMs use a small-region write variant (high-address contiguous window for upper-address-line coverage) so an eraser-less tester can retry; the region is capped by the engine, not by any DB field.

### Safety & Destructiveness (SAFE)

- [x] **SAFE-01**: The `--destructive` flag gates write/erase at plan-construction time (a non-destructive plan literally lacks those steps); it is per-invocation only and is never read from config or env.
- [x] **SAFE-02**: `dev test` is a pure orchestrator of existing commands — it routes every operation through `chip_resolver.resolve_chip`/the existing serial path, sets no VPP, builds no raw protocol commands, and passes no `--force`; the firmware VPP guard's refusals are recorded as findings.
- [x] **SAFE-03**: A CI gate asserts `dev test` adds zero new firmware dispatch entries and zero new VPP-set call sites (the orchestrator-only contract is machine-enforced).
- [ ] **SAFE-04**: `dev test <chip>` hard-fails (exit 1, bare `Error: <chip>: not found in database`, no "did you mean") when the chip name is **absent from the DB** (`db.get_eprom` empty), short-circuiting **before** any hardware is energized or report rendered — while a chip that is present-but-unsupported (support-status refusal, case B) STILL runs the full sweep (SWEEP-01). The guard keys off `get_eprom` emptiness, never a `resolve_chip` refusal, so it cannot swallow case B. Added post-roadmap via `/gsd-explore` 2026-07-03 as Phase-112-handler hardening.

### Diagnostic Report (RPT)

- [x] **RPT-01**: One run produces a single self-contained report rendered two ways from one source object — a human-readable `rich` results table and a compact fenced JSON block — carrying a `schema_version` key.
- [x] **RPT-02**: The report auto-captures the full diagnostic field set the host/firmware already know: FW+board+host version (MSG_OK identity), chip-ID expected-vs-actual, protocol path, per-op exact firmware error code, and the byte-mismatch fingerprint.
- [x] **RPT-03**: `EpromOperationError` preserves the firmware `response.id` byte via a backward-compatible `error_code` seam (currently discarded) so per-step results carry the exact error code.
- [x] **RPT-04**: Superseded by Phase 112 Plan 04 descope (operator-approved per `112-UAT.md`): the interactive provenance-prompt model (shield revision / chip origin / pot adjustments, collected before the sweep) is removed outright, not deprecated. The report instead auto-captures the identity the firmware/DB can supply — `hw_revision` via `HardwareManager`, host version, protocol path — and is honest (`None`/"not measured") about what it cannot. Zero interactive provenance prompts are issued anywhere in `dev test`. Submittability (`is_submittable`) is derived from auto-capture completeness only (`chip` + `protocol` + `host_version`), never from a human-supplied provenance field.
- [x] **RPT-05**: The report embeds a DB-diff (chip's `support_status` at test time + the proposed change) to support flag-only triage.

### Measured Voltage Capture (VOLT)

- [x] **VOLT-01**: A value-returning VPP/VPE mV sampler in `hardware.py` (parsing the `MSG_DATA_VPP/VPE_VOLTAGE` frames the current monitor only prints) captures the tester's actual rail voltage during the write step into the report.

### Transport Health (XPORT)

- [x] **XPORT-01**: The sweep captures transport-health counters (COBS/CRC/retry/timeout) and flags a run `transport-suspect` when they are elevated, so transport instability is not mis-read as a chip fault; degrades to "not measured" if unavailable.

### Submission (SUB)

- [ ] **SUB-01**: `--submit` files the report via a tiered flow: `gh issue create --body-file -` (stdin, auto-labeled `gsd-inbox`) when `gh` is present and authed, else a prefilled `issues/new` browser URL guarded to stay under the ~8 KB server cap (escalate/omit the JSON past ~7.5 KB encoded); a gist/attachment path is reserved for verbose failure logs.
- [ ] **SUB-02**: Before submitting, the report is sanitized (field whitelist, local paths/PII scrubbed, byte dumps hex/base64-encoded) and shown to the tester for preview-before-submit; submission is explicit/interactive only, never on a bare run.
- [x] **SUB-03**: Submission carries a dedup fingerprint so repeat reports for the same chip are recognizable in triage.

### Disposition & Graduation (DISP / GRAD / INBOX)

- [ ] **DISP-01**: No code path writes a chip's `support_status` from a parsed community report — graduation is flag-only and human-gated (locked anti-feature: no auto-graduation).
- [ ] **GRAD-01**: The `support_status` taxonomy gains community graduation-ladder states (`community-reported` / `community-confirmed` / `community-fail`); transitions to a `confirmed`/`supported` state require a human step keyed on N≥2 consistency.
- [ ] **INBOX-01**: `gsd-inbox` triage can auto-parse the report's fenced JSON on issue arrival and surface its DB-diff against the current database for maintainer review.

### Community Onboarding (ONBOARD)

Validation + docs for the beta-channel install/flash chain a community tester must traverse before they can run `dev test`. The install/flash/channel-select feature already exists (`firmware.py`, `cli_handlers.py` `fw`, `avr_tool.py`) — these requirements PROVE it on hardware and document it; they do not build it.

- [ ] **ONBOARD-01**: On a fresh machine/venv, `pip install --pre firestarter` installs the current `3.0.0bN` prerelease from PyPI and `firestarter --version` reports it — verified per bench board (Uno, Leonardo, uno328pb). Step 0 first confirms the prerelease is actually published to PyPI (operator-gated `gh` dispatch) or halts on a publish-first blocker.
- [ ] **ONBOARD-02**: A bare `firestarter fw -i` from the prerelease-installed app auto-routes to the `--pre` channel (D-23/D-24), downloads the board-matching `firestarter_<board>.hex` from the GitHub prerelease, and avrdude flashes + verifies it — verified per bench board. Step 0 first confirms the GitHub prerelease exposes a `.hex` asset for each board.
- [ ] **ONBOARD-03**: After flashing, a smoke test passes per board — `firestarter fw` reports the expected beta version + correct board and one minimal live protocol op (e.g. `hw`/identify) succeeds. Explicitly NOT a full chip write/verify (that is `dev test`'s job).
- [ ] **ONBOARD-04**: A community-facing "install the beta & flash beta firmware to help test PROMs" doc exists in the `firestarter_app` sub-repo (operator-canonical, per the two-layer doc pattern), written for a stranger on a fresh machine: per-board commands, the avrdude prerequisite, the per-port controller-identity gotcha, the correct `.hex` per board, and the hand-off into `dev test <chip>`.

## v2 / Future Requirements

Deferred beyond v1.21. Tracked, not in the current roadmap.

### Pattern (PATT-future)

- **PATT-F1**: Dedicated walking-1s/walking-0s extra address-bus pass (beyond the address-derived pattern's coverage).

### Submission (SUB-future)

- **SUB-F1**: Gist/attachment tier fully wired for verbose failure logs (v1.21 reserves it but only escalates off the URL tier).
- **SUB-F2**: Auto-merge/PR of community-confirmed DB entries (still human-gated review).

### Local staging (STAGE-future)

- **STAGE-F1**: Formalized `~/.firestarter/database.json` staging of unconfirmed community entries as local overrides.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Auto-graduation of `support_status` on a community PASS | Anti-feature — the project's own false-PASS history (Rev-0 shield, ST-vs-Winbond, AM27C020 write#1 60/64 vs write#2 0/64) proves a naive grader mis-promotes; graduation stays human-gated |
| Full March C- / galloping memory-test suite | RAM-oriented; destructive/slow on limited-endurance EPROM/Flash; address-derived pattern + fingerprint gives the needed coverage |
| Checkerboard/fixed pattern as the health proof | Fixed patterns are blind to the address-line faults this tool exists to catch |
| Fail-fast sweep | Contradicts the independent-non-fatal-steps design (the W29C040 locked-boot-block lesson) |
| Silent / automatic issue submission | Submission is explicit, previewed, interactive-only |
| New Python third-party dependencies | Reuse-first — `click`/`rich`/`requests` + stdlib cover everything; `gh` is an optional runtime tool, not a pip dep |
| Firmware protocol/dispatch changes | `dev test` is host-side orchestration; the only near-firmware touch is parsing an existing VPP/VPE frame (VOLT-01) |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SWEEP-01 | Phase 108 | Complete |
| SWEEP-02 | Phase 108 | Complete |
| SWEEP-03 | Phase 108 | Complete |
| SWEEP-04 | Phase 108 | Complete |
| SWEEP-05 | Phase 109 | Complete |
| PATT-01 | Phase 108 | Complete |
| PATT-02 | Phase 108 | Complete |
| PATT-03 | Phase 109 | Complete |
| SAFE-01 | Phase 109 | Complete |
| SAFE-02 | Phase 109 | Complete |
| SAFE-03 | Phase 109 | Complete |
| SAFE-04 | Phase 114 | Pending |
| RPT-01 | Phase 110 | Complete |
| RPT-02 | Phase 110 | Complete |
| RPT-03 | Phase 108 | Complete |
| RPT-04 | Phase 110 | Complete |
| RPT-05 | Phase 110 | Complete |
| VOLT-01 | Phase 111 | Complete |
| XPORT-01 | Phase 110 | Complete |
| SUB-01 | Phase 113 | Pending |
| SUB-02 | Phase 113 | Pending |
| SUB-03 | Phase 113 | Complete |
| DISP-01 | Phase 114 | Pending |
| GRAD-01 | Phase 114 | Pending |
| INBOX-01 | Phase 114 | Pending |
| ONBOARD-01 | Phase 115 | Pending |
| ONBOARD-02 | Phase 115 | Pending |
| ONBOARD-03 | Phase 115 | Pending |
| ONBOARD-04 | Phase 115 | Pending |

**Coverage:**

- v1 requirements: 29 total (SWEEP×5, PATT×3, SAFE×4, RPT×5, VOLT×1, XPORT×1, SUB×3, DISP×1, GRAD×1, INBOX×1, ONBOARD×4 — the initial definition's stated count of 20 undercounted the original REQ-IDs; Phase 115 added ONBOARD×4; SAFE-04 added mid-milestone via `/gsd-explore` 2026-07-03)
- Mapped to phases: 29/29 ✓
- Unmapped: 0

**Phase spine:** Phase 108 (test-plan engine + address-derived pattern + fingerprint) → Phase 109 (destructiveness gate + safety) → Phase 110 (diagnostic report + provenance) → Phase 111 (measured-voltage sampler, hardware-gated) → Phase 112 (`dev test` CLI wiring — integration only, no new v1 REQ-ID) → Phase 113 (submission flow) → Phase 114 (disposition / no-auto-graduate lock, feature close) → Phase 115 (beta install + firmware-flash bench validation & community-onboarding doc, hardware-gated close).

---
*Requirements defined: 2026-07-02*
*Last updated: 2026-07-03 — Phase 115 (beta install & firmware-flash bench validation, community onboarding) appended via `/gsd-explore`; ONBOARD×4 added → 28/28 requirements mapped across Phases 108–115.*
*Last updated: 2026-07-03 — SAFE-04 (`dev test` hard-fails on absent chip before energizing hardware) added via `/gsd-explore`; mapped to Phase 114 → 29/29.*

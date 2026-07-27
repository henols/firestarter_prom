# Project Research Summary

**Project:** Firestarter — `firestarter dev test <chip>` community chip-validation command
**Domain:** Community-run, partially-destructive hardware test + GitHub-submission CLI feature (integrated into an existing Click-based Python programmer app + Arduino firmware)
**Researched:** 2026-07-02
**Confidence:** HIGH

## Executive Summary

Firestarter v1.21 adds `firestarter dev test <chip>`: a community-distributed command that runs a per-chip capability sweep, produces a structured diagnostic report, and optionally files it to GitHub for maintainer triage. All four research streams converged on the same shape — this is **not** a greenfield feature but an **orchestration layer** sitting above the existing per-op service methods (`EpromOperator.{check_eprom_id, read_eprom, write_eprom, verify_eprom, erase_eprom, check_eprom_blank}`), architecturally a sibling of the shipped `dev validate-family`. It requires **zero new third-party dependencies** — every capability is satisfied by existing deps (`click`, `rich`, `requests`) plus stdlib (`json`, `subprocess`, `shutil.which`, `webbrowser`, `urllib.parse`). Prior art (flashrom's per-operation `.tested` struct with mandatory-logs, human-committed graduation; minipro's freeform, hard-to-triage issue flow) directly validates the locked design decisions and identifies the concrete differentiator: a *structured* two-tier report contract where minipro has only prose.

The recommended approach is **software-first, hardware-gated last**. Derive the test plan from DB fields `classify()` already baked into `chip_database.json` (never call `classify()` at runtime — it is a build-time function over `infoic.xml` ints); run each op as an independent, non-fatal step (the W29C040 locked-boot-block lesson made structural); assemble one dual-output artifact (human `rich` table + fenced compact JSON); prompt for firmware-unknowable provenance (shield rev, chip origin, pot) *before* the sweep; submit via a tiered flow (`gh issue create --body-file -` when `gh` is present/authed → prefilled `issues/new` URL under an ~8 KB cap → gist reserved for verbose logs). Nearly every auto-captured field already crosses the wire today, so **no firmware change is required**; the only genuinely new intra-host components are a value-returning VPP/VPE sampler (current `read_vpp_voltage` only *prints* the mV) and transport-health counters (resync is only logged today), plus a small backward-compatible `EpromOperationError.error_code` seam to preserve the firmware `response.id` byte currently discarded.

The dominant risk is that this command is **partially destructive, run on unknown hardware by an unknown operator, on a chip the maintainer cannot inspect, feeding a triage pipeline** — the exact conditions under which this project's own history produced false signals (Rev-0 shield Bug A, ST-vs-Winbond chip-ID mixup, AM27C020 write#1 60/64 then write#2 0/64, uno328pb transport instability). Safety is therefore a **hard requirement, not a feature**: `dev test` must route every op through the existing `chip_resolver.resolve_chip` → serial path, set no VPP, build no raw protocol commands, and pass no `--force` — enforced by a CI gate asserting zero new dispatch entries and zero new VPP-set call sites. Two open questions are resolved with cited evidence: the write pattern must be **address-derived** (a fixed pattern is blind to the address-line faults this tool exists to catch, coupled in the same phase with the byte-mismatch fingerprint classifier), and community PASS must be **FLAG-only, human-gated** (never auto-graduate `support_status`; flashrom precedent + this project's false-PASS museum make auto-graduation an anti-feature).

## Key Findings

### Recommended Stack

**Add zero new third-party dependencies.** Every capability `dev test` needs is already present or in stdlib; no `pyproject.toml` change. The reuse-first rule is not merely honored but fully achievable. See `.planning/research/STACK.md`.

**Core technologies (all already present — reuse):**
- `click >=8.1` — register `@dev.command("test")` as a drop-in sibling of `dev_validate_family`; provides `--destructive`/`--submit`/`--output-dir` flags — already the framework for all `dev` subcommands.
- `rich >=14.0` — human results table (`rich.table.Table`) + interactive provenance prompts (`rich.prompt`) — already imported in-repo (`firmware.py` uses `Confirm`).
- stdlib `json` — build/serialize the machine report dict (compact for URL, indented for human) — self-produced output needs no schema library.
- stdlib `subprocess` + `shutil.which` — Tier-1 `gh issue create --body-file -` (stdin, no length limit, no shell-quoting hazard) with `--label gsd-inbox`; `gh` is an optional *runtime* tool, never a pip dep.
- stdlib `webbrowser` + `urllib.parse` — Tier-2 prefilled `issues/new?...` URL, correctly percent-encoded.

**Rejected:** `PyGithub` (dep + token burden, duplicates `gh`), `jsonschema`/`pydantic` (validating self-authored output buys nothing), `--body` argv string for `gh` (ARG_MAX/quoting), prefilled URL for verbose logs (~8 KB cap; ~3× percent-encoding inflation → ~2.5–3 KB source budget → HTTP 414 on overflow).

### Expected Features

See `.planning/research/FEATURES.md`. flashrom is the closest analogue and validates the locked decisions; minipro's prose-only reports are the incumbent to beat with structure.

**Must have (table stakes, P1):**
- Per-chip test-plan engine derived from `classify()`/protocol — run only the ops the chip supports.
- Independent, non-fatal steps with per-op `OK/BAD/NA/SKIPPED` verdicts (flashrom-grade contract).
- Non-destructive default (id + read + blank-check) + loud `--destructive` gate + "only N of M tests ran" banner.
- Address-derived write/verify pattern (+ cheap all-0/all-FF pre-pass) + UV small-region variant.
- Byte-mismatch fingerprint classifier (blank/contact vs address-line vs transport) — coupled to the pattern.
- Dual-output self-contained report (human table + fenced JSON) with full auto-captured field set.
- Prompted provenance (shield rev / chip origin / pot) **before** the sweep.
- Tiered `--submit` (gh issue → prefilled URL) auto-labeled to `gsd-inbox`.
- DB-diff (status-at-test-time + proposed change) embedded in the report.

**Should have (competitive, P2):** VPP/VPE mid-write capture, transport-health capture, graduation-ladder states (`community-reported`/`-confirmed`/`-fail`), `gsd-inbox` reconciliation automation.

**Defer (v1.x / v2+):** walking-1s/0s extra address-bus pass, gist/attachment tier for verbose logs, formalized local user-override staging, auto-merge/PR of confirmed entries (still human-gated).

**Anti-feature (do NOT build):** auto-graduation of `support_status` on a community PASS; full March C-/galloping suite (RAM-oriented, destructive/slow on limited-endurance EPROM/Flash); checkerboard as the health proof (fixed → address-fault-blind); fail-fast sweep; silent auto-submit.

### Architecture Approach

See `.planning/research/ARCHITECTURE.md`. `dev test` is a NEW orchestration layer that composes existing service methods verbatim (the `validate-family` compose-don't-reimplement precedent), derives its op list from DB fields `classify()` froze into `chip_database.json`, and emits a two-tier artifact. It bypasses the `resolve_chip` support-status guard *for plan derivation only* (via `get_eprom()` + `convert_to_programmer()`) because the target population is exactly the non-`supported` chips the guard would refuse — while keeping that guard authoritative for every real op.

**Major components:**
1. `@dev.command("test")` handler in `cli_handlers.py` — args, provenance prompts, invoke engine, exit code (sibling of `dev_validate_family`).
2. NEW `firestarter/chip_test.py` — `derive_plan()` (protocol→ops), non-fatal `run_step()`, `DiagnosticReport` dataclass + dual-output renderer; reuses `consistency_check_eprom`'s divergence math for the fingerprint.
3. NEW `firestarter/submit.py` — tiered `gh`/browser-URL submission (`shutil.which` + `subprocess` + `webbrowser`).
4. Modified (small, backward-compatible): `eprom_operations.py` gains `EpromOperationError.error_code` (preserve `response.id`); `hardware.py` gains a value-returning mV VPP/VPE sampler.

### Critical Pitfalls

See `.planning/research/PITFALLS.md` (13 domain-specific pitfalls + a "looks done but isn't" checklist).

1. **VPP-guard bypass / over-voltage footgun** — a "thorough" plan that sets VPP or builds raw commands reintroduces the hazard v1.12/v1.20 removed. Avoid: orchestrate existing commands only; CI gate for zero new dispatch entries + zero VPP-set call sites; refusals become findings.
2. **`--destructive` bypass / silent partial-PASS** — gate destructiveness at plan-construction time (non-destructive plan literally lacks write/erase steps); per-invocation only (never config/env); report always carries `destructive` + `tests_run/tests_total`; banner when N < M.
3. **Auto-graduation poisons the DB** — a community PASS NEVER writes `support_status`; it creates a `gsd-inbox` triage artifact a human confirms (lock this).
4. **Shield-revision provenance gap** — never auto-derive shield rev from the ambiguous `hw_revision` byte; prompt before the sweep with an explicit "not sure"; not submittable if blank.
5. **Fixed pattern hides address-line faults** — use an address-derived pattern so a mis-wired line produces a *detectable* mismatch; wire the fingerprint classifier's address-line bucket.
6. **Wrong chip / false PASS** — id-first ordering; chip-ID mismatch is a hard gate for destructive steps (fail-safe, chip pristine); capture DB entry + measured VPP.
7. **UV full/wrong-region write bricks an eraser-less chip** — engine-capped small region (a DB misconfig must not widen it), no erase step in the UV plan.
8. **Transport instability mis-read as chip fault** + **N=1 flukes** — capture transport-health counters, flag `transport-suspect`; run destructive/verify N≥2, disagreement → `marginal` (not PASS/FAIL).
9. **PII/path leak + URL truncation + binary-encoding/injection** (submission) — whitelist report fields, sanitize paths, preview-before-submit; measure encoded length and escalate off the URL tier past ~7.5 KB; hex/base64 all byte data; `--body-file -` stdin, never `shell=True`.

## Implications for Roadmap

Phase numbering continues from v1.20's 107 → **v1.21 starts at Phase 108**. The dependency spine is: **address-derived pattern ⇄ fingerprint are coupled (same phase)**; **provenance must precede the sweep**; **graduation depends only on the DB-diff, not on any auto-promotion code**; **hardware-gated pieces land last**. The suggested nine-phase structure below refines the four-agent-convergent order.

### Phase 108: Test-plan engine + pattern + fingerprint
**Rationale:** the core; everything else consumes its per-op verdicts. The address-derived pattern and byte-mismatch fingerprint are coupled and must ship together (a fixed pattern makes "high-address clustering → address-line" impossible to produce).
**Delivers:** `chip_test.py` `derive_plan()` (protocol/`electrical-type`/`FLAG_CAN_ERASE` → op list, bypassing the `resolve_chip` guard for derivation), address-derived pattern generator + fingerprint classifier, id-first ordering with chip-ID mismatch gating destructive steps, N≥2 execution with per-run capture, bounded retry.
**Addresses:** per-chip plan, address-derived pattern, fingerprint classifier, non-fatal steps.
**Avoids:** Pitfalls 6 (wrong-chip gate), 7 (correct family classification), 8 (retry), 9 (N≥2).
**Foundational sub-step:** the `EpromOperationError.error_code` seam in `eprom_operations.py` (smallest change, biggest leverage — every step result depends on it).

### Phase 109: Destructiveness gate + safety
**Rationale:** the single most consequential bug class; must be locked before any write path is exposed.
**Delivers:** plan-construction-time destructiveness gate, per-invocation `--destructive` (never persisted), UV small-region hard cap enforced in the engine, loud "N of M ran" banner, CI gate (zero new dispatch entries + zero VPP-set call sites; all ops via resolver).
**Avoids:** Pitfalls 1 (VPP-guard authority), 2 (gate placement), 3 (UV small-region).

### Phase 110: Diagnostic report model + dual output + provenance prompts
**Rationale:** the report is the deliverable and the submission dependency; provenance must be captured pre-sweep or the report is un-actionable.
**Delivers:** two-tier `DiagnosticReport` dataclass (auto-capture + prompted), `rich` table + fenced-JSON renderer from one source object, `schema_version` key, DB-diff (status-at-test-time + proposed change), transport-health field, provenance prompts (`click.prompt`) run before the sweep with "not sure" options.
**Uses:** stdlib `json`, `rich`.
**Avoids:** Pitfalls 4 (DB-diff enables FLAG-only), 5 (provenance gap), 8 (transport-health field).

### Phase 111: Measured-voltage sampler (hardware-gated)
**Rationale:** the only genuinely-new hardware-touching component; isolate it so the software MVP is unblocked.
**Delivers:** value-returning `sample_vpp_mv`/`sample_vpe_mv` in `hardware.py` parsing `MSG_DATA_VPP/VPE_VOLTAGE` frames (current monitors only print), wired into the write step to capture the tester's actual rail.
**Implements:** the VPP/VPE mid-write auto-capture field.
**Avoids:** Pitfall 6 (off-nominal rail surfaces bench/calibration faults).

### Phase 112: `dev test` handler wiring
**Rationale:** integrates 108–111 into the CLI once the pieces exist.
**Delivers:** `@dev.command("test")` in `cli_handlers.py`, `--destructive`/`--output-dir` flags, non-destructive default, exit-code semantics; unit-testable via `EpromDatabase(skip_local_override=True)` + mock operator (the `validate-family` test seam).

### Phase 113: Submission flow
**Rationale:** depends on the report existing; pure host/tooling, no hardware.
**Delivers:** `submit.py` tiered `--submit` (gh `--body-file -` stdin → prefilled URL with encoded-length measure + ~7.5 KB escalation → gist reserved), auto-label `gsd-inbox`, PII whitelist + path sanitizer, hex/base64 byte encoding, preview-before-submit, dedup fingerprint, explicit/interactive-only (never on a bare run).
**Avoids:** Pitfalls 10–13 (PII, URL truncation, binary/injection, submission spam).

### Phase 114: Disposition / no-auto-graduate lock
**Rationale:** resolves the graduation open question and closes the trust loop.
**Delivers:** locked "FLAG-only, human-gated" disposition; `suggested_status` is advisory only; no code path writes `support_status` from a parsed report; triage keys off consistency (N≥2 agreement) not a single result; optional graduation-ladder states formalized.
**Avoids:** Pitfalls 4 (auto-graduation) and 9/13 (N=1/spam feeding triage).

### Phase Ordering Rationale
- **Pattern + fingerprint first (108)** because they are coupled and are the diagnostic differentiator; the error-code seam is the foundational sub-step everything depends on.
- **Safety before any exposed write path (109)** — destructive-by-accident is the top bug class; the gate lives at plan construction, not per-step.
- **Report + provenance (110) before submission (113)** — submission needs the body; provenance must precede the sweep.
- **Measured-voltage (111) isolated as the only hardware-gated piece** — mirrors the project's standing software-first, hardware-last discipline; the rest is fully unit-testable without a bench.
- **Graduation last (114)** — it depends only on the DB-diff (110), deliberately not on any auto-promotion code.

### Research Flags

Phases likely needing deeper research during planning (`/gsd-plan-phase --research-phase <N>`):
- **Phase 108:** address-derived pattern math for the UV small-region variant (upper-address coverage from a small window) and precise fingerprint thresholds — some parameter tuning is bench-informed.
- **Phase 111:** the mV sampler is the one true new hardware component (frame parsing of `MSG_DATA_VPP/VPE_VOLTAGE`, sampling count) and is hardware-gated for validation.

Phases with standard patterns (skip research-phase):
- **Phase 109, 110, 112:** well-grounded in existing source (`validate-family` sibling, `consistency_check_eprom` divergence math, `AppContext` DI) with locked decisions.
- **Phase 113:** stack research fully quantified the submission tiers, URL cap, and encoding; standard stdlib patterns.
- **Phase 114:** disposition is a documented, cited decision (flashrom precedent + project history); it is a lock, not an exploration.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | `gh` flags verified locally (2.95.0); GitHub URL cap corroborated by multiple community/docs sources; deps read directly from `pyproject.toml`. |
| Features | HIGH | flashrom official docs + source; minipro tracker; address-fault detection backed by patents (US4876684, US7532526) + fault-model literature; both open questions resolved with cited evidence. |
| Architecture | HIGH | Every recommendation names the real file/function; grounded in actual `firestarter_app/firestarter/*.py` + firmware headers. Auto-capture gaps (voltage, transport) called out explicitly rather than assumed. |
| Pitfalls | HIGH | Grounded in this project's first-party RCA history (Bug A, ST-vs-Winbond, AM27C020, uno328pb, W29C040, `write -b`) + web-verified external facts (URL cap, `--body-file -`). |

**Overall confidence:** HIGH

### Gaps to Address

- **Transport-health capture is a real gap** — no persistent COBS/CRC/retry/timeout counters exist today; resync is only `logger.debug`-logged. v1 recommendation: attach a `logging.Handler` during the sweep and count resync/timeout records (zero-risk to transport), report "not measured" if absent. Decide handler-vs-counter approach during Phase 110 planning.
- **Measured VPP/VPE requires a new sampler** — `read_vpp_voltage`/`read_vpe_voltage` return `bool` and only print; the mV value is not returned. Confirm the `MSG_DATA_VPP/VPE_VOLTAGE` (0xE4/0xE5) frame parse and sampling count during Phase 111 planning; this is the one hardware-gated validation.
- **`resolve_chip` guard bypass mechanism** — Option (a) (bypass via `get_eprom()`+`convert_to_programmer()` for the diagnostic sweep only, no shared-code change) is recommended over adding a `require_supported=False` seam; confirm at Phase 108.
- **UV small-region window choice** — a high-address contiguous window maximizes upper-address-line coverage from a small write; validate the exact size/placement against real UV parts (bench-informed, Phase 108/111).

## Sources

### Primary (HIGH confidence)
- `firestarter_app/firestarter/{cli_handlers,eprom_operations,database,chip_resolver,serial_comm,hardware,messages}.py` + `tools/build_db.py` + firmware `include/firestarter.h` — grounded architecture, service-method contracts, `classify()` build-time semantics, error-code table.
- `firestarter_app/pyproject.toml` — existing dependency set; `gh version 2.95.0` verified locally (`--body-file -`, `--label`).
- [flashrom — Board Testing HOWTO](https://www.flashrom.org/Board_Testing_HOWTO), [How to mark chip as tested](https://www.flashrom.org/contrib_howtos/how_to_mark_chip_tested.html), [flashchips.c `.tested`](https://github.com/flashrom/flashrom/blob/main/flashchips.c) — per-op status + human-gated graduation precedent.
- [github/docs #5136 — ~8191-byte URL cap](https://github.com/github/docs/issues/5136), [cli/cli #6355 — `--body-file -` stdin](https://github.com/cli/cli/discussions/6355).
- [US4876684 — address-in-data stuck-line detection for ROM](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4876684), [US7532526 — per-address-bit stuck-at method](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7532526).
- Project RCA history (`.planning/` + auto-memory): Bug A / Rev-0 read-path, ST-vs-Winbond chip-ID mixup, AM27C020 VPP droop, uno328pb transport instability, W29C040 locked boot block, `write -b` skip-erase footgun, v1.12 12V-hazard removal + v1.16 SAFE-01..06.
- Seed + design note: `.planning/seeds/community-chip-validation-command.md`, `.planning/notes/dev-test-design-decisions.md` (locked decisions).

### Secondary (MEDIUM confidence)
- [minipro issue #109 (DB re-reverse-engineering)](https://github.com/vdudouyt/minipro/issues/109), [#90 (user-defined chip configs)](https://github.com/vdudouyt/minipro/issues/90), [DavidGriffith/minipro GitLab issues](https://gitlab.com/DavidGriffith/minipro/-/issues) — incumbent triage flow.
- [Fault Models for Memories (Sontakke)](https://medium.com/@vijay.n.sontakke/fault-models-for-memories-fe883b022380), [Walking/marching/galloping patterns (Auburn)](https://www.eng.auburn.edu/~agrawvd/COURSE/E7250_05/REPORTS_TERM/Raghuraman_Mem.doc), [Address-decoder faults (Embedded.com)](https://www.embedded.com/targeting-soc-address-decoder-faults-using-functional-patterns/) — pattern coverage/rationale.

### Tertiary (LOW confidence)
- [sindresorhus/new-github-issue-url](https://github.com/sindresorhus/new-github-issue-url) — illustrative encoding reference (Node-only, not adopted).

---
*Research completed: 2026-07-02*
*Ready for roadmap: yes*

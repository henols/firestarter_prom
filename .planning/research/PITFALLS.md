# Pitfalls Research

**Domain:** Community-run, partially-destructive hardware test + GitHub-reporting command (`firestarter dev test <chip>`)
**Researched:** 2026-07-02
**Confidence:** HIGH (grounded in this project's own documented RCA history: Bug A / Rev 0 read-path, ST-vs-Winbond 512 chip-ID mixup, AM27C020 VPP droop, uno328pb timeouts, W29C040 locked boot block, `write -b` skip-erase footgun; external facts — GitHub 8191-byte URL cap and `gh --body-file -` — web-verified)

This file catalogs the mistakes that will bite when *building* the community chip-validation command. It is deliberately domain-specific: generic "validate CLI input" advice is omitted in favor of the failure modes this exact feature creates — a destructive operation, run on unknown hardware by an unknown operator, on a chip the maintainer can't inspect, feeding an auto-graduation/triage pipeline. Every pitfall names the phase that must prevent it.

Suggested v1.21 phase skeleton referenced below (Phase numbering continues from v1.20's 107 → **v1.21 starts at Phase 108**):
- **Phase 108 — Test-plan engine** (per-chip plan from `classify()`, independent non-fatal steps)
- **Phase 109 — Destructiveness gate + safety** (`--destructive` default-off, UV small-region, VPP-guard-authoritative)
- **Phase 110 — Diagnostic report contract** (auto-capture + provenance prompts, fingerprinting, portability)
- **Phase 111 — Submission flow** (`gh` / prefilled-URL / gist tiers, encoding, PII scrub)
- **Phase 112 — Auto-graduation / triage disposition** (community PASS → confirmation, N=1 discipline)

(Phase boundaries are a recommendation for the roadmap author; the pitfall-to-phase mapping table at the end is the load-bearing artifact.)

---

## Critical Pitfalls

### Pitfall 1: The command becomes a new over-voltage footgun by re-deriving VPP instead of deferring to the firmware guard

**What goes wrong:**
`dev test` builds a "technology-aware" plan and, wanting to be thorough, computes or overrides VPP/VPE targets, passes a `--force`, or routes an unimplemented protocol into a working handler to "at least try the write." A 12V (or 21–25V NMOS) VPP rail then lands on a chip/pin combination the existing safety stack would have refused. On a community bench with an unknown shield, that is silicon damage or worse — and it happened *because the new command took a path around the guard*.

**Why it happens:**
The existing over-voltage protection is layered and non-obvious: the **host guard `chip_resolver.resolve_chip` refuses before any serial byte** (authoritative layer, per v1.12), and the **firmware VPP check blocks over-voltage at the rail** (per v1.16 SAFE-01..06, every primitive keys on `handle->protocol`, never on `electrical.type`). v1.12 specifically removed the silent `mem_type → configure_eprom` 12V fallback because it was a hardware-damage path; v1.20 finished removing that axis. A new command author who doesn't know this history can trivially reintroduce the hazard by constructing commands the guard never sees, or by treating "the chip refused" as a bug to work around.

**How to avoid:**
- **Non-negotiable requirement: `dev test` MUST route every operation through the exact same `chip_resolver.resolve_chip` → serial path that `read`/`write`/`verify`/`erase` use. It must NOT construct raw protocol commands, MUST NOT set VPP, and MUST NOT pass `--force` on the tester's behalf.** The command is an *orchestrator of existing commands*, not a new low-level path.
- The firmware VPP guard and the host refusal stay authoritative; `dev test` inherits their verdicts as *findings* ("write refused: vpp-exceeds-max"), never overrides them.
- A protocol-not-implemented (`0xBB`) or host refusal is a **recorded finding**, exactly like the W29C040 locked-boot-block: the surprise is the value.
- Add a `check_dispatch.py`-style CI assertion that `dev test` introduces **zero** new dispatch entries and **zero** new VPP-setting call sites.

**Warning signs:**
- Any new code in the test-plan engine that reads `vpp_mv`, calls a monitor to *set* (not measure) voltage, or branches on `electrical.type` to choose a handler.
- A `--force` or `--yes-really` flag on `dev test` that is passed down to the write/erase primitive.
- Native tests for `dev test` that don't go through the resolver.

**Phase to address:** Phase 109 (destructiveness gate + safety) — with a hard SAFE-* requirement and a CI dispatch/VPP-callsite gate carried from v1.12/v1.16.

---

### Pitfall 2: `--destructive` default-off is bypassed, ambiguous, or under-communicated — a tester nukes a keeper chip

**What goes wrong:**
Three sub-failures: (a) the default run silently includes a write/erase step because the gate check is in the wrong place or a family was mis-classified as "safe"; (b) `--destructive` is a persistent config/env that "sticks" across invocations so a later bare run is unexpectedly destructive; (c) the non-destructive run *looks* like a full PASS because it doesn't loudly say "only N of M tests ran," so a maintainer reads a partial sweep as a clean bill of health.

**Why it happens:**
Destructive-by-accident is the single most consequential bug class for this feature, and it's easy to get subtly wrong. The seed is explicit that bare run = id + read + blank-check only, and that non-destructive runs must **loudly** report `"only N of M tests ran"`. But "loudly" is a UX property that's trivially lost, and gate placement is exactly the kind of thing that regresses silently (see the v1.16 `write -b` skip-erase footgun: a flag with non-obvious destructive semantics silently corrupted non-blank chips and *reported success*).

**How to avoid:**
- Gate destructiveness at **plan-construction time**, not per-step: the non-destructive plan literally does not contain write/erase steps (can't run what isn't in the list). `--destructive` is the only thing that adds them.
- `--destructive` is **per-invocation only** — never read from config/env/a saved profile. No "remember this."
- The report itself carries a machine field `destructive: true|false` and `tests_run: N, tests_total: M`, and the human summary leads with a banner when `N < M`. A report consumer (and the auto-graduation logic) must be able to distinguish "3/3 non-destructive passed" from "8/8 full sweep passed."
- Mirror the v1.16 HARD-01 lesson: decouple flag names from destructive semantics and make the destructive path *explicitly* opt-in, never a side effect of another flag (e.g., don't let `--force` imply `--destructive`).

**Warning signs:**
- A bare `dev test <chip>` that emits a `MAIN:`/write frame on the wire (assert in a native/wire test that it never does).
- A report with `destructive:false` that contains write or erase results.
- A human summary that prints "PASS" with no coverage denominator.

**Phase to address:** Phase 109. Verification: a wire-level test asserting the default plan produces no destructive frames, plus a report-schema test asserting `tests_run/tests_total` are always present.

---

### Pitfall 3: UV EPROM written full-image (or wrong region) turns an eraser-less tester's chip into a one-way brick with no retry

**What goes wrong:**
The tester runs `--destructive` on a UV EPROM without a UV lamp. The command writes the full image (or a large/random region), the bits go one-way (1→0), and the chip is now permanently dirty — they can't retry, can't blank-check clean, and their only "keeper" of that part number is consumed. Worse: the report may still say PASS, so the maintainer never learns the tester is now stuck.

**Why it happens:**
UV EPROMs are irreversible without a UV lamp; this project has repeatedly designed around it (v1.15 UV no-eraser protocol; operator owns no eraser). The seed's mitigation is a **small-region write** so an eraser-less tester can retry (a small dirty region still leaves most of the chip usable and the test repeatable in a fresh region). But "small region" is a design intent that's easy to drop, and the classify-to-family mapping that decides "this is UV, use small-region, skip electrical erase" is exactly the kind of table that gets a chip mis-bucketed (see the ST M27C512 vs Winbond W27C512 confusion below — one is UV, one is electrically erasable).

**How to avoid:**
- UV-family write path is **hard-capped to a small region** (e.g. a fixed small byte count / single page), enforced in the engine, not the DB — a DB misconfig must not be able to widen it.
- Electrical-erase and repeatable-round-trip steps are **structurally absent** from the UV plan (the seed's family table: UV = write small region only, skip erase).
- The provenance prompt (Pitfall 8) asks the UV tester "do you own an eraser?" *before* the sweep; if no, the report records "UV, no eraser — chip now partially spent" so the maintainer knows a retry needs a fresh region/chip.
- Family classification for the destructive plan must be driven by `classify()` / `electrical.type` **ground truth** (EEPROM vs UV-EPROM), the same source v1.11/v1.16 corrected — and a chip-ID mismatch must abort the destructive step before any 1→0 write (Pitfall 6).

**Warning signs:**
- A UV chip's plan containing an `erase` step or a full-size `write`.
- Small-region size sourced from a DB field a user-override could change.
- A destructive UV run proceeding despite a chip-ID mismatch.

**Phase to address:** Phase 109 (small-region cap + UV plan shape) + Phase 108 (correct family classification into the plan).

---

### Pitfall 4: A community PASS auto-graduates `support_status` — the maintainer's ground truth gets poisoned by one unverified bench

**What goes wrong:**
The pipeline treats "community reported PASS" as authority and flips a chip's `support_status` to `supported` (or opens an auto-merge). Then it turns out the tester had a bad bench config, a mis-wired address line that a fixed pattern didn't catch (Pitfall 7), an N=1 fluke on unstable transport (Pitfall 9), or the wrong physical chip (Pitfall 6). Now the DB — which every user's firmware trusts for VPP and pinout — claims a chip works when it doesn't, and the regression is invisible until someone's silicon is at risk.

**Why it happens:**
This is one of the two explicitly-open research questions in the seed ("does a community PASS graduate a chip, or only flag it for maintainer confirmation?"). The whole project's discipline is *evidence-driven, Leonardo-only-trustworthy, never-N=1, honest-UNVERIFIED* (v1.13 non-vacuous PASS oracle; v1.15/v1.16 "no chip graduated without bench proof"; "never trust N=1" from the uno328pb memory). Auto-graduation from remote, unverifiable, N=1 data is the exact opposite of that discipline and would undo years of careful `UNVERIFIED` honesty.

**How to avoid:**
- **Decision for the roadmap (recommend LOCKING it): a community PASS NEVER auto-graduates `support_status`. It creates a triage artifact — an auto-labeled `gsd-inbox` issue — that a maintainer confirms.** The report can carry a `suggested_status` field, but the DB value is maintainer-gated, exactly like every graduation to date.
- Introduce a distinct provenance tier in the DB if desired — e.g. `community-reported` vs `supported` — so a community result is *visible* without being *trusted as bench-proven*. This preserves the honest-gap culture.
- The submission label routes to the existing `gsd-inbox` triage flow (already in the seed), which is the human gate.

**Warning signs:**
- Any code path where a parsed report writes to `chip_database.json` / `support_status` without a human step.
- A `suggested_status` field being consumed as authoritative by another tool.
- Graduation happening from a single report (no N≥2, no independent bench).

**Phase to address:** Phase 112 (auto-graduation / triage disposition) — resolve the open research question by locking "flag, never auto-graduate."

---

### Pitfall 5: The shield-revision provenance gap makes reports un-actionable — the one field that cracked Bug A is blank or guessed

**What goes wrong:**
A report lands with everything auto-captured beautifully but the shield revision blank or auto-guessed from the EEPROM `hw_revision` byte. The maintainer can't reproduce or reason about it — because the read-path fault Bug A was **Rev-0-shield-specific** and revision was *decisive* to the RCA, yet the `hw_revision` EEPROM byte **cannot distinguish Rev 2.2 / Rev 2.0 / modified Rev 0**. A report that auto-fills revision from that byte is not just incomplete — it's *actively misleading*, asserting a revision the hardware can't actually prove.

**Why it happens:**
It is enormously tempting to auto-fill every field (it's "in the EEPROM, right there"). But this project's memory is explicit: the `hw_revision` byte can't tell the three revisions apart, and the operator owns Rev 2.2 / Rev 2.0 / modified Rev 0 and must *always be asked* which is seated. The design note calls this out directly: shield revision, chip provenance, and pot adjustments are the fields firmware genuinely can't self-report, and the command must collect them as **prompts before the sweep** so no report lands with them blank.

**How to avoid:**
- **Never auto-derive shield revision from `hw_revision`.** Prompt the tester interactively *before* the sweep, offer an explicit "not sure" option, and record the answer verbatim plus a `hw_revision_byte` (raw) so the maintainer sees both the human claim and the raw byte.
- Same for chip provenance (new/blank vs pulled/used; owns-a-UV-eraser) and pot adjustments (did they touch the voltage trim).
- Make the provenance block a **required, pre-sweep, interactive step** — a report is not submittable without it (or with an explicit "declined"). The design consequence in the note: prompt-before-sweep so a "beautiful auto-report" is never un-actionable due to an unknown shield.
- If run non-interactively (`--yes`/CI), refuse to submit, or stamp the report `provenance: unattended — shield UNKNOWN` so it's visibly downgraded.

**Warning signs:**
- A `shield_revision` field populated from a byte read rather than a prompt.
- Reports where shield revision equals a decoded `hw_revision` value.
- A submission path reachable with the provenance prompts skipped.

**Phase to address:** Phase 110 (diagnostic report contract — provenance prompts as a required pre-sweep step).

---

### Pitfall 6: Wrong physical chip / bad bench config produces a confident false PASS (or false FAIL)

**What goes wrong:**
The tester seats a chip whose markings say one thing but silicon says another (the classic ST M27C512 UV/13V/`0x203d` vs Winbond W27C512 EEPROM/12V/`0xda08` mixup — same "512" label, different technology, different VPP). Or the bench has a stale saved config, a live-board-plus-saved-config port mismatch, or an R1/R2 miscalibration. The sweep runs the *wrong* algorithm/VPP for the actual silicon and reports PASS or FAIL that describes neither the chip nor the firmware honestly.

**Why it happens:**
Chip markings lie or get misread; two physically different parts share a name; and a community tester won't have the operator's standing discipline (verify `controller:` identity per task, live R1/R2 readback). The chip-ID expected-vs-actual check is the fastest wrong-chip signal (design note) — but only if it's run first and treated as gating for destructive steps.

**How to avoid:**
- **Run id-check first and make expected-vs-actual chip-ID a hard gate for any destructive step.** A mismatch (like ST-vs-Winbond) must fail-safe: skip write/erase, record the mismatch as the headline finding, leave the chip pristine (this project's chip-ID mismatch already "fails safe, chip pristine" without `--force` — inherit that, don't override it).
- Auto-capture the DB entry actually used (`support_status`, `protocol_id`, pin config, assumed voltages) so a wrong-entry is visible in the report.
- Prompt for chip provenance (Pitfall 5) so "pulled/used, markings faint" context travels with the report.
- Auto-capture measured VPP/VPE during the write step (design note) so a bench-config/calibration problem shows up as an off-nominal rail, not as a silent "chip fault."

**Warning signs:**
- A destructive step proceeding after a chip-ID mismatch.
- Reports with no `chip_id_expected`/`chip_id_actual` pair.
- PASS reports with a measured VPP far off the DB-assumed value.

**Phase to address:** Phase 108 (id-first plan ordering + mismatch gate) + Phase 110 (capture DB entry + measured VPP into the report).

---

### Pitfall 7: A fixed test pattern passes while address lines are mis-wired — false confidence baked into the report

**What goes wrong:**
The write/verify step uses a simple fixed pattern (all-`0x55`, all-`0xFF`, a constant). Because every address holds the *same* byte, a swapped/shorted/stuck address line still verifies "correct" — the chip returns the expected value from the wrong cell. The sweep reports a clean write PASS on hardware that is actually mis-wired, and that false PASS then feeds graduation/triage.

**Why it happens:**
This is the other explicitly-open research question in the seed ("what write/verify pattern proves chip health — fixed vs address-derived?"). A fixed pattern is the obvious first implementation and it's *wrong* for exactly this hardware-validation use case: the entire point is to catch bad benches, and address-line faults are a top failure mode for socketed parallel memory (see Bug A's "high-address clustering" fingerprint).

**How to avoid:**
- **Use an address-derived pattern** (each cell's value is a function of its address — e.g. a low/high address-byte mix, an LFSR seeded by address, or address ⊕ constant) so a mis-wired address line produces a *detectable* mismatch. Resolve the open research question toward address-derived, and document why.
- Feed the byte-mismatch fingerprint classifier the address context so it can distinguish the three signatures the design note already names: all-`0xFF` → blank/contact fault; **high-address clustering → address-line fault**; scattered → transport.
- On UV (small-region only), an address-derived pattern over even a small region still catches low-order address-line faults; note the reduced coverage in the report.

**Warning signs:**
- A constant/fixed write buffer in the write-test step.
- A verify that compares against a single repeated byte.
- No address-line signature in the fingerprint classifier's output vocabulary.

**Phase to address:** Phase 108 (test-plan engine — pattern selection) + Phase 110 (fingerprint classifier consumes address context). Resolve the open research question here.

---

### Pitfall 8: Transport instability (uno328pb timeouts, COBS/CRC errors) is misread as a chip fault — mis-RCA'd reports

**What goes wrong:**
The tester's board is transport-unstable (the documented uno328pb signature: read timeouts + drifting 0xff, marginal even after COBS hardening). The sweep sees corrupted reads and records "chip verify FAILED / 40% bad bytes" — a **chip** finding — when the real cause is the **transport/board**. A maintainer chasing that report RCAs a nonexistent silicon bug.

**Why it happens:**
Corruption at the byte level looks identical whether it originated in the cells or the serial link. This project learned it the hard way: v1.10 proved the transport byte-exact yet uno328pb instability *persisted* (recorded as transport-exoneration, not a hardware fix); the standing rule is "retry on timeout and never trust N=1." A naive sweep attributes all mismatches to the chip.

**How to avoid:**
- **Auto-capture transport health as a first-class report field** (COBS/CRC error count, retries, timeouts) — the design note already lists this as the uno328pb signature. A report with high transport-error counts is flagged `transport-suspect` and its chip findings are downgraded.
- The fingerprint classifier's "scattered → transport" bucket must be wired so scattered mismatches on a high-error link are labeled transport, not chip.
- **Retry-on-timeout with a bounded count**, and record retries; a step that only passed after N retries is a *finding*, not a clean PASS.
- Feed the board type (`version:board`, auto-captured) into the classifier so known-unstable board classes (Uno-class 328PB) get an automatic `transport-suspect` caveat.

**Warning signs:**
- Reports attributing failures to the chip while transport-error counts are non-zero.
- No retry accounting in the report.
- A verify-fail finding with a scattered fingerprint on a 328PB board and no transport caveat.

**Phase to address:** Phase 110 (transport-health capture + classifier wiring) + Phase 108 (bounded retry in step execution).

---

### Pitfall 9: N=1 results treated as authoritative — a fluke ships as a finding

**What goes wrong:**
The sweep runs each operation once and the report presents the single result as fact. On marginal hardware (VPP droop, transport instability), a single run is a coin flip: the AM27C020 wrote 60/64 bytes on write #1 and 0/64 on write #2 in the *same session* on the *same bench*. An N=1 report of either would be misleading.

**Why it happens:**
Single-shot is the simple implementation and "it passed" feels conclusive. But this project's memory is emphatic — "never trust N=1," AM27C020 marginal/unreliable across repeats, uno328pb needs retries. Marginal silicon/rails are exactly what community testers will surface, so N=1 is structurally dangerous here.

**How to avoid:**
- For destructive write/verify (and reads on suspect transport), **run N≥2 (recommend N=3) and record every result + agreement**. Report a PASS only if runs agree; disagreement is a `marginal/unreliable` finding, not a FAIL and not a PASS (the honest AM27C020 disposition).
- The report schema carries per-run results and a `consistency: consistent|marginal` verdict; auto-graduation/triage (Pitfall 4) keys off consistency.
- Capture SHA per read (this project's evidence pattern) so "3 distinct SHAs" (the 2516 instability signature) is machine-detectable.

**Warning signs:**
- A report with a single result per operation and a bare PASS/FAIL.
- No inter-run agreement field.
- Marginal chips reported as clean PASS.

**Phase to address:** Phase 108 (N≥2 step execution + per-run capture) + Phase 112 (triage keys off consistency, not single result).

---

### Pitfall 10: Local paths / PII / hostnames leak into a public GitHub issue

**What goes wrong:**
The auto-generated issue body includes the tester's home directory path (`/home/alice/roms/secret_project.bin`), a serial device path that encodes a username, the config dir, environment details, an absolute path to a proprietary ROM image, or a git email — filed into a *public* repo issue, indexed forever.

**Why it happens:**
Diagnostic dumps are grabbed wholesale ("include everything that helps RCA"), and paths/usernames ride along invisibly. This is a real project surface: the firmware/host know the port (`/dev/tty…`), the config dir (`FIRESTARTER_CONFIG_DIR`, `~/.firestarter/`), and the input image path — all of which can contain PII, and the tester's git identity (the operator's is `henrik@predictly.se`) is one `gh` call away.

**How to avoid:**
- **Whitelist, don't blacklist, the report fields.** The report is built from an explicit field contract (the two-tier list in the design note) — only listed fields are emitted. No "dump the whole context."
- Sanitize the few path-bearing fields: report the *basename* or a placeholder for input files, the port *class* (`ttyUSB`/`ttyACM`) not the full node if it embeds a name, and never the config dir contents or absolute home paths.
- Show the tester the exact issue body and require confirmation before `--submit` (they see what goes public).
- Never auto-attach the ROM image or raw config; the verbose-log/gist tier (Pitfall 11) gets the same scrub.

**Warning signs:**
- Any `str(path)` / `os.getcwd()` / `os.environ` / `~` expansion in report construction.
- A field carrying an absolute filesystem path.
- `--submit` reachable without a preview/confirm step.

**Phase to address:** Phase 111 (submission flow — whitelist contract + sanitizer + preview-before-submit).

---

### Pitfall 11: Prefilled-URL truncation silently drops report data past ~8 KB

**What goes wrong:**
The non-`gh` submission tier opens `github.com/…/issues/new?title=…&body=…`. GitHub enforces a **server-side ~8191-byte URL limit**; a body past that is silently truncated (or the request rejected), so the maintainer receives a *partial* JSON block — often cut mid-structure so it won't even parse, or missing the exact failure detail that made the report worth filing.

**Why it happens:**
URL length limits are invisible until exceeded, and byte dumps / raw serial traces blow past 8 KB fast. The seed already anticipates this (gist/attachment tier "reserved for the rare verbose failure log that overflows URL limits") — the pitfall is *not detecting the overflow* and silently truncating instead of escalating tiers.

**How to avoid:**
- **Measure the encoded body length before choosing a tier.** If the URL-encoded `issues/new` URL would exceed a safe budget (recommend ≤7500 bytes to leave headroom under 8191 for title + framing + percent-encoding expansion), do **not** use the prefilled-URL tier.
- Tier escalation on overflow: `gh issue create --body-file -` (no URL limit — reads body from stdin, also the injection-safe path, see Pitfall 12) when `gh` is present; else write the full report to a local file and open a *short* prefilled URL that references the attached/gist content, telling the tester to paste/attach it.
- Keep the normal single-chip report compact (design note: a few KB) so the common path fits; only verbose failure logs (byte dumps, raw traces) escalate.
- Round-trip test: encode a known-large report and assert the chosen tier preserves every byte (parse the JSON back out).

**Warning signs:**
- A prefilled URL constructed with no length check.
- Reports whose JSON block fails to re-parse after submission.
- Byte dumps embedded in a URL-tier body.

**Phase to address:** Phase 111 (submission tiering + overflow detection + preservation round-trip test).

*(External: GitHub's URL cap is ~8191 bytes — [github/docs #5136](https://github.com/github/docs/issues/5136).)*

---

### Pitfall 12: Binary/byte-dump encoding corrupts the report or enables command/markdown injection

**What goes wrong:**
Two related failures: (a) raw binary bytes (a byte-mismatch dump, a chip-ID blob) are stuffed into JSON/markdown as-is — non-UTF-8 bytes break JSON encoding, or a backtick sequence closes the fenced ```json block and mangles the issue; (b) the body is passed to `gh issue create --body "<string>"` or an `os.system`/shell string, so a byte sequence or a chip name with shell metacharacters injects into the shell or the markdown.

**Why it happens:**
Byte dumps are the whole point of the verbose tier, and binary → text is a known trap. The design note's fingerprint/byte-mismatch fields are inherently binary. And `--body` takes a literal string that's easy to build by naive concatenation; the safe stdin form (`--body-file -`) is less obvious.

**How to avoid:**
- **Encode binary explicitly**: hex or base64 for any byte dump, never raw bytes into JSON/markdown. The machine report is JSON with only string/number fields; byte data is hex-encoded strings.
- **Escape for the fenced block**: ensure no user/chip-derived content can contain a triple-backtick sequence that closes the JSON fence (the report generator controls the fence; content is hex/escaped).
- **Never shell-interpolate the body.** Use `gh issue create --title <t> --body-file -` reading the body from **stdin** (the injection-safe, no-length-limit path) rather than `--body "<concatenated string>"`; pass args via a list (no `shell=True`).
- Validate the emitted JSON re-parses (Pitfall 11's round-trip test doubles as this check).

**Warning signs:**
- Raw `bytes` written into the report without hex/base64.
- `--body "…"` built by string concatenation, or `subprocess` with `shell=True`.
- A chip name / DB string interpolated into a `gh`/URL command unescaped.

**Phase to address:** Phase 111 (encoding + `--body-file -` + no-shell submission).

*(External: `gh` safe stdin form is `--body-file -` — [cli/cli #6355](https://github.com/cli/cli/discussions/6355).)*

---

### Pitfall 13: Auto-graduation / submission spam — noise floods `gsd-inbox`

**What goes wrong:**
Every run offers `--submit`; enthusiastic testers file dozens of near-duplicate PASS reports for the same chip, or a CI/loop fires reports automatically. `gsd-inbox` triage drowns, and the signal (a genuine new-chip PASS or a real FAIL) is buried.

**Why it happens:**
A frictionless submit button plus a community equals volume. Combined with auto-graduation (Pitfall 4) it compounds: noise + auto-trust = bad DB writes at scale.

**How to avoid:**
- `--submit` is **explicit and interactive** (never default, never on a bare run), with the preview/confirm step from Pitfall 10.
- Deduplicate at triage: the report carries a stable fingerprint (chip + protocol + result + fw/board) so `gsd-inbox` (or an issue-template dedup) can collapse repeats; a repeat PASS *strengthens* an existing report (raising N) rather than filing a new issue.
- Auto-labeling routes to `gsd-inbox` (seed) — lean on that human gate; do not auto-close or auto-graduate (Pitfall 4).
- Rate-limit / discourage automated/looped submission; a non-interactive run refuses to auto-submit.

**Warning signs:**
- `--submit` reachable non-interactively or as a default.
- Multiple identical open issues for one chip.
- No dedup fingerprint in the report.

**Phase to address:** Phase 111 (submit is explicit + dedup fingerprint) + Phase 112 (triage dedup / N-strengthening).

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Fixed write pattern (all-0x55) instead of address-derived | Trivial to implement/verify | False PASS on mis-wired address lines → poisons graduation | **Never** for a validation tool — this is the tool's core job |
| Auto-fill shield revision from `hw_revision` byte | "Complete" report, no prompt | Misleading revision → mis-RCA (Bug A was rev-specific) | **Never** — byte can't distinguish the 3 revs; must prompt |
| N=1 per operation | Fast sweeps | Fluke ships as fact (AM27C020 60/64 then 0/64) | Only for the non-destructive read on known-stable transport; never for destructive/marginal |
| Auto-graduate `support_status` on community PASS | Zero maintainer effort | One bad bench poisons DB every user trusts for VPP/pinout | **Never** — flag for confirmation only |
| Prefilled-URL for all submissions | No `gh` dependency | Silent truncation past ~8 KB drops the failure detail | Only when the encoded body is measured < ~7.5 KB |
| `dev test` builds raw protocol commands to be "thorough" | Can test paths `read`/`write` don't expose | Bypasses the authoritative VPP guard → over-voltage footgun | **Never** — orchestrate existing commands only |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| `gh issue create` | `--body "<concatenated string>"` (shell-interpolated, length-limited by argv, injectable) | `--title <t> --body-file -` reading body from **stdin**; args as a list, no `shell=True` |
| `issues/new?body=…` prefilled URL | Build unconditionally; silent ~8191-byte truncation | Measure URL-encoded length; escalate to `gh`/gist tier past a ~7.5 KB budget |
| Firmware VPP/dispatch | New command sets VPP or routes protocols to "try harder" | Route only through `chip_resolver.resolve_chip` + existing commands; guard stays authoritative |
| Voltage monitor (`vpp`/`vpe`) | Call it to *set* voltage, or confuse measure-only rails | It is **measure-only** (doesn't route to socket); auto-run mid-sweep to *capture*, never to set |
| `gsd-inbox` triage | Auto-graduate / auto-close from parsed report | Auto-label → human confirms; dedup repeats into N-strengthening |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Wholesale context dump into public issue | PII/path/hostname/git-email leak, indexed forever | Whitelist report fields; sanitize paths to basenames/placeholders; preview-before-submit |
| Raw bytes → JSON/markdown | Broken JSON, fence-escape, garbled report | Hex/base64-encode all byte data; generator controls the ```json fence |
| Shell-interpolated submit command | Command injection via chip name / byte content | `--body-file -` stdin; subprocess arg list; never `shell=True` |
| Attaching ROM image / config to report | Proprietary/private data leak | Never auto-attach; verbose tier scrubbed identically |
| `--destructive` persisted in config/env | Later bare run unexpectedly destructive | Per-invocation only; never read from saved state |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Non-destructive run prints "PASS" with no denominator | Maintainer reads partial sweep as clean bill of health | Lead with "only N of M tests ran — pass `--destructive` on a scrap chip" banner + `tests_run/tests_total` in report |
| Provenance asked *after* the sweep (or not at all) | Report lands with shield/provenance blank → un-actionable | Prompt provenance **before** the sweep; not submittable without it (or explicit "declined") |
| Destructive run gives no clear "this will consume your chip" warning | Tester bricks a keeper | Loud confirmation on `--destructive`, especially UV (one-way) |
| Silent retry hides marginal hardware | Marginal chip looks clean | Surface retry count + `marginal` verdict in summary |

## "Looks Done But Isn't" Checklist

- [ ] **Destructiveness gate:** Verify a *bare* run emits **zero** write/erase frames on the wire (wire-level assert), and `--destructive` is per-invocation only (not config/env).
- [ ] **VPP-guard authority:** Verify `dev test` adds **zero** new dispatch entries and **zero** new VPP-setting call sites (`check_dispatch.py`-style CI gate); all ops go through `chip_resolver.resolve_chip`.
- [ ] **UV small-region cap:** Verify a UV chip's destructive plan writes only a small, engine-capped region and contains **no** erase step — even with a hostile DB entry.
- [ ] **Chip-ID mismatch gate:** Verify a chip-ID mismatch aborts destructive steps and leaves the chip pristine (ST-vs-Winbond case), recorded as the headline finding.
- [ ] **Address-derived pattern:** Verify a simulated swapped address line produces a *detectable* mismatch (fixed pattern would hide it).
- [ ] **Provenance required:** Verify no report can be submitted with shield revision blank; auto-derive-from-`hw_revision` is absent.
- [ ] **N≥2 discipline:** Verify destructive/verify ops run ≥2× and disagreement yields `marginal`, not PASS.
- [ ] **URL overflow escalation:** Verify a >8 KB report escalates off the prefilled-URL tier (round-trip: re-parse the submitted JSON).
- [ ] **PII scrub:** Verify no absolute path / config dir / env / git-email appears in an emitted report.
- [ ] **Binary encoding:** Verify byte dumps are hex/base64 and the ```json fence can't be closed by content.
- [ ] **No auto-graduation:** Verify no code path writes `support_status` from a parsed report without a human step.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Over-voltage on a community chip (Pitfall 1) | HIGH (silicon damaged remotely, trust damaged) | Cannot un-damage silicon; audit for the bypass path, add the CI VPP-callsite gate, notify. This is why the guard must be authoritative *before* ship. |
| DB poisoned by false auto-graduation (Pitfall 4) | MEDIUM–HIGH | Revert the `support_status` change, mark `community-reported`/`UNVERIFIED`, require maintainer re-confirmation; add the human gate. |
| PII leaked into public issue (Pitfall 10) | MEDIUM (GitHub caches/indexes) | Edit/delete the issue fast, request cache purge; add the whitelist+preview retroactively. Prevention >> recovery. |
| UV chip bricked with no retry room (Pitfall 3) | LOW–MEDIUM (per tester) | Tester needs a fresh chip/region; report records "UV spent"; small-region cap limits damage to one region. |
| Truncated report filed (Pitfall 11) | LOW | Re-file via `gh`/gist tier; add the length-measure + escalation. |
| Transport-fault mis-RCA'd as chip fault (Pitfall 8) | LOW–MEDIUM (wasted maintainer time) | Re-read report's transport-health field; downgrade finding; add the `transport-suspect` auto-caveat. |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| 1. Over-voltage footgun (VPP guard bypass) | Phase 109 | CI: zero new dispatch entries + zero VPP-set call sites; all ops via resolver |
| 2. `--destructive` gate bypass / silent partial-PASS | Phase 109 | Wire test: bare run emits no destructive frame; report always carries `tests_run/tests_total` |
| 3. UV full/wrong-region write | Phase 109 (+108 classify) | Engine test: UV plan is small-region-capped, no erase step, DB can't widen it |
| 4. Auto-graduation poisons DB | Phase 112 | No code path writes `support_status` without a human step; N≥2 required |
| 5. Shield-revision provenance gap | Phase 110 | Provenance prompted pre-sweep; `hw_revision` auto-derive absent; not submittable if blank |
| 6. Wrong chip / bad bench false PASS | Phase 108 (+110 capture) | id-first ordering; chip-ID mismatch gates destructive steps; DB entry + measured VPP in report |
| 7. Fixed-pattern hides address-line fault | Phase 108 (+110 classifier) | Simulated swapped address line yields detectable mismatch; classifier has address-line bucket |
| 8. Transport instability mis-read as chip fault | Phase 110 (+108 retry) | Transport-health field present; scattered-on-328PB gets `transport-suspect`; retries recorded |
| 9. N=1 fluke as fact | Phase 108 (+112 triage) | Destructive/verify run N≥2; disagreement → `marginal`; per-run SHAs captured |
| 10. PII/path leak into public issue | Phase 111 | No abs path/env/email in report; whitelist contract; preview-before-submit |
| 11. Prefilled-URL truncation | Phase 111 | >8 KB report escalates tier; submitted JSON re-parses |
| 12. Binary encoding / injection | Phase 111 | Byte data hex/base64; `--body-file -` stdin; no `shell=True` |
| 13. Submission spam / triage flood | Phase 111 (+112 dedup) | `--submit` explicit+interactive only; dedup fingerprint present |

## Sources

- Project RCA history (HIGH — first-party, this repo's `.planning/` + auto-memory):
  - Bug A / Rev 0 shield read-path fault (rev-specific; `hw_revision` can't distinguish Rev 2.2/2.0/mod-0)
  - ST M27C512 vs Winbond W27C512 chip-ID mixup (fails safe, chip pristine without `--force`)
  - AM27C020 VPP droop — write#1 60/64 then write#2 0/64 same bench (marginal/unreliable → DEFER)
  - uno328pb transport instability persisting post-COBS (retry, never trust N=1; transport-exoneration)
  - W29C040 permanently-locked §6.6 boot block (surprise = the value; independent non-fatal steps)
  - `write -b` skip-erase footgun (flag with non-obvious destructive semantics reported success) — v1.16 HARD-01
  - v1.12 silent `mem_type → configure_eprom` 12V hazard removal; host guard authoritative; v1.16 SAFE-01..06 (primitives key on `handle->protocol`, over-voltage blocked at firmware VPP check)
  - `vpp`/`vpe` monitors are measure-only (don't route voltage to socket)
- [github/docs #5136 — server-side URL length limit (~8191 bytes)](https://github.com/github/docs/issues/5136) (HIGH)
- [cli/cli discussion #6355 — `gh ... --body-file -` reads body from stdin (injection-safe, no URL limit)](https://github.com/cli/cli/discussions/6355) (HIGH)
- Seed + design note: `.planning/seeds/community-chip-validation-command.md`, `.planning/notes/dev-test-design-decisions.md` (HIGH — first-party locked decisions)

---
*Pitfalls research for: community-run partially-destructive hardware test + GitHub-reporting command (Firestarter v1.21 `dev test <chip>`)*
*Researched: 2026-07-02*

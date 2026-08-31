# Feature Research

**Domain:** Community-distributed device-test / capability-sweep command for a hobbyist EPROM/Flash/SRAM programmer (`firestarter dev test <chip>`)
**Researched:** 2026-07-02
**Confidence:** HIGH (prior art cited from flashrom docs + minipro issue tracker; memory-test patterns from published fault-model literature; both open questions resolved with cited evidence)

> Scope note: this file is authored for **v1.21 — Community Chip-Validation Command**. It supersedes the v1.16 protocol-vocabulary FEATURES content (archived in `.planning/milestones/`). Prior architecture (protocol-first `classify()`→dispatch, `support_status` taxonomy, `PROTOCOL-LEDGER`/`EVIDENCE.{md,json}`, `dev validate-family`, MSG_OK `version:board`, protocol error codes, VPP/VPE monitor) is treated as SHIPPED and is NOT re-proposed here.

---

## Prior Art Survey (concrete)

### 1. flashrom — "board status" / device-support reporting flow

flashrom is the closest analogue: a community-maintained tool whose device coverage grows by users testing real silicon and reporting back. Concrete mechanics worth copying or avoiding:

- **A per-chip `.tested` field, per-operation, not a single boolean.** In `flashchips.c` each chip carries a `.tested` struct with independent qualifiers for `probe / read / erase / write / wp`, each `OK` / `BAD` / `NA` / `UNTESTED` (`enum test_state`, `include/flash.h`). A chip introduced from datasheet values only is `TEST_UNTESTED`; partial testing is first-class — you can mark `probe`+`read` OK while leaving `erase`/`write` untested. **This directly validates Firestarter's "independent, non-fatal steps" decision** and argues the report must carry a *per-operation* verdict, not one PASS/FAIL.
- **Evidence is mandatory to change status.** The "How to mark chip as tested" HOWTO requires *full logs of a successful run* attached (via `paste.flashrom.org` or the mailing list) before a chip's `.tested` state is upgraded. No log, no graduation.
- **Human-in-the-loop graduation.** The status change is a *patch/commit* (`"flashchips: Mark <chip> as tested for <operations>"`) that goes through maintainer code review — it is NOT auto-applied from a submitted result. This is the decisive precedent for the graduation question (Q2 below).
- **Submission is tiered and low-friction.** Direct patch if you can; otherwise send logs + exact board manufacturer/model + observations to the mailing list. The pattern is: *structured evidence to a triage channel*, then a human commits.

Sources: [Board Testing HOWTO](https://www.flashrom.org/Board_Testing_HOWTO), [How to mark chip as tested](https://www.flashrom.org/contrib_howtos/how_to_mark_chip_tested.html), [flashchips.c](https://github.com/flashrom/flashrom/blob/main/flashchips.c).

### 2. minipro / TL866 — community device-verification practice

minipro's device database (`infoic.xml`, the same source Firestarter's `build_db.py` consumes) was reverse-engineered from vendor Windows software and is **not systematically bench-verified** — coverage/correctness questions are litigated in the issue tracker ad hoc:

- New-chip / correction requests arrive as GitHub/GitLab **issues and PRs** ("add support for X", "value Y is wrong"), triaged by a maintainer (David Griffith's GitLab fork is the active one). A `check_db.py` diffs database dumps and once reported ~3145 new parts / ~390 changed values — i.e. the DB drifts and needs human reconciliation.
- There is a standing RFE for **user-defined chip configs** (issue #90) — the community repeatedly asks for a way to describe a chip locally before it's upstreamed. Firestarter already has this (`~/.firestarter/database.json` overrides) and it is the natural *staging* place for a community-tested-but-not-yet-graduated entry.
- The lesson: minipro has **no diagnostic-report contract** — reports are freeform prose, so triage is expensive and reproduction is guesswork. Firestarter's two-tier structured contract (auto-captured fields + prompted provenance) is the concrete differentiator over the incumbent.

Sources: [minipro issue #109 (re-reverse-engineering the DB)](https://github.com/vdudouyt/minipro/issues/109), [issue #90 (user-defined chip configs)](https://github.com/vdudouyt/minipro/issues/90), [DavidGriffith/minipro GitLab issues](https://gitlab.com/DavidGriffith/minipro/-/issues).

### 3. Hardware-CI / self-test command conventions

- **Non-fatal, per-step result collection** is the norm in HIL/self-test runners (POST-style: run every check, aggregate a report, never abort on first fail). Matches the locked decision.
- **Machine-readable + human output from one run** (JUnit XML / JSON sidecar + console summary) is the standard hardware-CI convention. Firestarter's "human table on top, fenced JSON below, one markdown doc" is the idiomatic single-artifact form of this.
- **Explicit destructive-op gating** (a `--force`/`--destructive` flag before anything that mutates the device) is universal in flashing tooling. flashrom itself refuses risky board operations without opt-in and warns about recovery. Matches the `--destructive` decision.
- **Environment fingerprinting** (tool version, adapter/board identity, transport health) is standard in HIL reports because "works on my bench" is the default failure mode. Firestarter's auto-capture list (FW `version:board`, host version, protocol path, error codes, VPP/VPE, COBS/CRC health) is exactly this.

---

## Design Question 1 — Health-proving write/verify PATTERN

**RECOMMENDATION: address-derived pattern as the primary write test, with a cheap fixed all-cells pre-pass. Specifically:**

1. **Fixed uniform pre-pass (cheap, catches gross faults):** write `0x00`, verify; write `0xFF`, verify. Catches stuck-*data*-bits and gross contact/power faults instantly.
2. **Address-in-data pass (the real health proof):** write each byte as a deterministic function of its address — e.g. `data[a] = (a ^ (a >> 8)) & 0xFF` (folds high address bits into the byte so A8..A18 participate), optionally alternating with its complement on odd addresses. This is the standard **"address-in-data"** memory test.

**Why address-derived, not fixed:** A fixed pattern (`0xAA`/`0x55` checkerboard, all-`0x00`, all-`0xFF`) writes the *same* byte to many addresses, so it is **blind to address-line faults**. If A14 is stuck, or A9/A14 are shorted, the chip mis-addresses but every location still holds the expected constant — verify passes on a broken chip. This is precisely Firestarter's historical **Bug A "upper-address jitter"** failure class: an address-derived pattern would surface it directly, because a stuck/shorted address line makes two locations that differ only in that bit read back *different* expected values. Published fault-model literature agrees: stuck-at address-decoder faults "can only be caught when memories are accessed with addresses that are hamming distance apart," and the address-in-data technique detects a stuck address bit because otherwise "locations with the address and the location with that bit complemented have the same value."

**Named standard patterns and what each catches (cite in requirements):**

| Pattern | Catches | Misses | Fit for `dev test` |
|---|---|---|---|
| All-`0x00` / all-`0xFF` | stuck data bits, gross contact/power, blank-vs-programmed | address faults, coupling | cheap pre-pass |
| Checkerboard `0xAA`/`0x55` | adjacent-cell data coupling, stuck data bits | **address-line faults** | low value here; skip |
| **Address-in-data** (byte = f(address)) | **stuck/shorted address lines, decoder faults**, data-path errors | dynamic/coupling faults needing read-after-read | **PRIMARY recommendation** |
| Walking-1s / walking-0s (over addresses) | address-bus integrity, decoder-selects-wrong-cell | full data-cell coverage | good cheap address-bus check; complements address-in-data |
| March C- / full March | comprehensive (stuck-at, transition, coupling, address) | — (gold standard) | **anti-feature here** — built for RAM with unlimited fast rewrites; destructive + slow on limited-endurance, slow-program EPROM/Flash |

**Verdict:** the byte-mismatch *fingerprint* the design already wants (all-`0xFF` → blank/contact; high-address clustering → address-line; scattered → transport) is only *diagnostically meaningful if the written pattern encodes address*. A fixed pattern cannot produce "high-address clustering" as a distinguishing signal. **The address-derived pattern is what makes the fingerprint field earn its place** — the two decisions are coupled and must be planned together.

**UV-EPROM small-region variant:** UV chips can only 1→0 without a lamp, and the locked decision is "write only a small region." Recommendation: pick a **small contiguous window high in the address space** (e.g. the last N bytes) and write the **address-in-data** value there, so even the small-region UV test still probes upper-address-line health rather than just proving a handful of bytes flip. Verify only that window; leave the rest for an eraser-equipped retry.

Sources: [Fault Models for Memories (Sontakke)](https://medium.com/@vijay.n.sontakke/fault-models-for-memories-fe883b022380), [Walking/marching/galloping patterns (Auburn)](https://www.eng.auburn.edu/~agrawvd/COURSE/E7250_05/REPORTS_TERM/Raghuraman_Mem.doc), [Targeting address-decoder faults (Embedded.com)](https://www.embedded.com/targeting-soc-address-decoder-faults-using-functional-patterns/), [Diagnosing failures in ROM systems — US4876684](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4876684), [Testing address lines — US7532526](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7532526).

---

## Design Question 2 — Community PASS → `support_status` graduation

**RECOMMENDATION: FLAG-only. A community-submitted PASS must NOT auto-graduate `support_status`; it produces a maintainer-review item that a human confirms before the canonical DB entry changes. Auto-graduation is an anti-feature.**

**Why (evidence-backed):**

- **flashrom precedent is unambiguous:** even with mandatory full logs, a `.tested` upgrade is a reviewed *patch/commit*, never auto-applied from a submitted result. The most successful community hardware-verification project in this exact domain chose flag-then-human-commit. Firestarter should not adopt a weaker trust model.
- **The threat is a bad bench falsely promoting a chip.** Firestarter's own history is a museum of environment-specific false signals a naive auto-grader would mis-promote: Rev-0-shield read-path fault (Bug A), ST-M27C512-vs-Winbond-W27C512 chip-ID mixup, AM27C020 VPP droop (write#1 60/64 "looked good", write#2 0/64), uno328pb timeout instability. A PASS on an unknown shield/provenance/pot-state is *exactly* the input auto-graduation cannot safely trust — which is why the diagnostic contract *prompts* for shield revision, provenance, and pot adjustments.
- **The maintainer is the authoritative safety layer** — the same architectural stance already chosen elsewhere in the project (host guard authoritative over hollow GATE-03; "nothing is stable until I say so"). Auto-graduation contradicts an established project value.
- **Triage load is the accepted cost, and it's bounded** because the structured report makes confirmation cheap: `gsd-inbox` receives an issue that already diffs the submitted result against the current DB entry.

**How the report reconciles/diffs against the DB inside `gsd-inbox`:**

- The JSON block should carry the **`support_status` the tester's DB entry had at test time** plus the full DB entry used (protocol_id, pinout, voltages) — so triage can compute a diff: *"submitter ran `spec-only` W29C040 on Rev 2.0, all destructive steps PASS byte-exact; proposed graduation `spec-only → supported`."*
- Graduation reuses the **existing evidence machinery**: the confirmed result becomes a `PROTOCOL-LEDGER` / per-chip `EVIDENCE.{md,json}` entry (v1.15/v1.16 pattern) with a **provenance tag = community + submitter + shield rev**, distinct from operator-bench evidence, and composes with (does not replace) the maintainer's own bench ledger.
- Intermediate state: a community-PASS-but-unconfirmed chip can live as a **user-override DB entry** (minipro issue #90 pattern; `~/.firestarter/database.json` already exists) so the submitter gets local use immediately without touching the canonical DB.

**A graduation LADDER makes both sides honest** (matches flashrom's partial `.tested` and the project's existing taxonomy):

`spec-only` → `community-reported` (auto-set on submission; the flag) → `community-confirmed` / `supported` (maintainer promotes after review) — plus a `community-fail` state so a *negative* result is captured, not discarded.

Sources: [How to mark chip as tested](https://www.flashrom.org/contrib_howtos/how_to_mark_chip_tested.html), [Board Testing HOWTO](https://www.flashrom.org/Board_Testing_HOWTO), [minipro issue #90 (user configs)](https://github.com/vdudouyt/minipro/issues/90).

---

## Feature Landscape

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Per-chip test-plan derived from `classify()`/protocol | Must run only the ops the chip supports; erasing a UV EPROM is nonsense | MEDIUM | Reuses existing `classify()` + DB entry; no new firmware |
| Independent, non-fatal steps (per-op verdict) | flashrom's per-op `.tested` is the domain norm; W29C040 locked-boot-block lesson | MEDIUM | Each of id/read/write/verify/erase/blank-check → `OK/BAD/NA/SKIPPED` |
| Non-destructive default (id + read + blank-check) | Users will run it on a chip they care about; must not silently mutate | LOW | Reuses existing read/blank-check paths |
| Loud `--destructive` gate for write/erase | Universal flashing-tool convention; protects real chips | LOW | Must state "only N of M tests ran — pass `--destructive` on a scrap chip" |
| Dual output: human table + machine JSON, one artifact | Hardware-CI convention (console + JUnit/JSON); triage needs structure | MEDIUM | Single markdown: results table + fenced ```json block |
| Auto-captured environment fingerprint | "works on my bench" default failure; flashrom requires board id + logs | MEDIUM | FW `version:board`, host version, protocol path, error codes, DB entry used, transport health (SHIPPED sources) |
| Chip-ID expected-vs-actual in the report | Fastest wrong-chip/wrong-entry signal (ST-vs-Winbond 512 precedent) | LOW | Already have chip-ID read |
| Tiered `--submit` (gh issue → else prefilled URL) | Low-friction reporting is why coverage grows; flashrom paste/mailing precedent | MEDIUM | `gh issue create` auto-labeled → `gsd-inbox`; else `issues/new?title=&body=` |
| Prompted human-only provenance before sweep | Report un-actionable if shield unknown (Bug A was shield-decisive); firmware can't self-report | LOW | Prompt shield rev / chip origin / pot up front; offer "not sure" |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Address-derived write/verify pattern + fingerprint** | Catches stuck/shorted address lines a fixed pattern hides — the exact Bug-A class; makes the fingerprint meaningful | MEDIUM | See Q1; the reason this beats minipro's ad-hoc reports |
| Byte-mismatch pattern classifier (blank/contact vs address-line vs transport) | Turns raw failures into an RCA hypothesis in the report itself | MEDIUM | Only meaningful *with* the address-derived pattern (coupled) |
| Auto-run VPP/VPE monitor mid-write step | Captures the tester's actual rail voltage — many project bugs were droop (AM27C020) | MEDIUM | Reuses existing vpp/vpe monitor; capture during the write op |
| Transport-health capture (COBS/CRC errors, retries, timeouts) | uno328pb instability signature; distinguishes chip fault from link fault | LOW | Reuses COBS transport counters |
| DB-diff in the submitted report (status-at-test-time + proposed change) | Makes maintainer triage cheap; the graduation ladder's mechanism | MEDIUM | Feeds `gsd-inbox` reconciliation (Q2) |
| Graduation ladder w/ `community-reported`/`-confirmed`/`-fail` + provenance tag | Honest trust model; captures negatives too; composes with EVIDENCE ledger | MEDIUM | Extends existing `support_status` taxonomy |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Auto-graduate `support_status` on a community PASS** | "Faster coverage, less maintainer work" | A bad bench (wrong shield, VPP droop, wrong chip-ID, wear) silently promotes falsely; contradicts flashrom precedent + the project's authoritative-maintainer value | **FLAG-only**: auto-set `community-reported`, maintainer confirms → `supported` (Q2) |
| Full March C- / galloping suite | "Most thorough memory test" | Built for RAM with unlimited fast rewrites; destructive + slow on limited-endurance, slow-program EPROM/Flash; wildly over-scoped for a coverage-reporting tool | address-in-data pass + cheap all-0/all-FF pre-pass (Q1) |
| Checkerboard `0xAA`/`0x55` as the health proof | "Classic RAM test pattern" | Fixed pattern → blind to address-line faults, the exact class this tool exists to surface | address-derived pattern |
| Fail-fast sweep (abort on first failure) | "Stop wasting time on a broken chip" | Hides the *surprise* that is the valuable output (W29C040 locked boot block found because the sweep continued) | independent non-fatal steps (locked decision) |
| Auto-attach huge raw serial dumps to every issue | "More data is better" | Overflows URL/issue limits; buries the signal; makes triage worse | compact self-contained body normally; gist/attachment tier **only** for the rare verbose-failure case (locked) |
| Destructive-by-default (always write to prove health) | "A read-only test proves little" | Destroys chips the user cares about; UV EPROMs are one-way without a lamp | non-destructive default + `--destructive` gate + UV small-region variant |
| Silent telemetry / auto-submit without consent | "Grow the DB passively" | Privacy + trust violation; submits unreviewed benches | explicit opt-in `--submit`; human-readable body the tester sees before filing |

---

## Feature Dependencies

```
[Per-chip test-plan engine (classify())]
    └──requires──> [existing classify() + DB entry + protocol dispatch]   (SHIPPED)

[Independent non-fatal steps]
    └──requires──> [Per-chip test-plan engine]

[Address-derived write/verify pattern]
    └──enables──> [Byte-mismatch fingerprint classifier]   (fingerprint is meaningless without it)

[Diagnostic report (dual output)]
    ├──requires──> [Independent non-fatal steps]        (per-op verdicts to tabulate)
    ├──requires──> [Auto-captured fingerprint]          (FW version:board, protocol path, error codes — SHIPPED)
    ├──requires──> [Prompted provenance]                (must run BEFORE the sweep)
    └──requires──> [VPP/VPE monitor + transport counters] (SHIPPED)

[Tiered --submit]
    └──requires──> [Diagnostic report]                  (needs the body to submit)

[Graduation (FLAG-only)]
    ├──requires──> [DB-diff in report]
    └──feeds──> [gsd-inbox triage → EVIDENCE/PROTOCOL-LEDGER]   (SHIPPED machinery)

[--destructive gate] ──guards──> [write/erase/round-trip steps]
[UV small-region variant] ──specializes──> [Address-derived write pattern]  for one-way EPROM
```

### Dependency Notes

- **Address-derived pattern ⇄ fingerprint classifier are coupled** — plan them in the same phase; a fixed pattern makes the "high-address clustering → address-line" fingerprint impossible to produce.
- **Provenance prompts must precede the sweep** — otherwise a completed auto-report lands with shield unknown and is un-actionable (the whole point of the two-tier contract).
- **Graduation depends only on the DB-diff + gsd-inbox**, not on any auto-promotion code — deliberately, per Q2.
- Nearly every *auto-captured* field already has a SHIPPED source (v1.16 protocol path, MSG_OK `version:board`, protocol error codes, VPP/VPE monitor, COBS counters). The new build is the *test-plan engine + report schema + submission + provenance prompts + pattern*, not new firmware capability.

---

## MVP Definition

### Launch With (v1.21)

- [ ] Per-chip test-plan engine from `classify()` — the command's core
- [ ] Independent non-fatal per-op steps with `OK/BAD/NA/SKIPPED` verdicts — the flashrom-grade contract
- [ ] Non-destructive default + `--destructive` gate + loud "N of M ran" — essential safety
- [ ] Address-derived write/verify pattern (+ cheap all-0/all-FF pre-pass) + UV small-region variant — the diagnostic differentiator (Q1)
- [ ] Byte-mismatch fingerprint classifier — coupled to the pattern
- [ ] Dual-output self-contained report (human table + fenced JSON) with the full auto-captured field set
- [ ] Prompted provenance (shield rev / chip origin / pot) before the sweep — report is noise without it
- [ ] Tiered `--submit` (gh issue → prefilled URL) with auto-label to `gsd-inbox`
- [ ] DB-diff (status-at-test-time + proposed change) embedded in the report — enables FLAG-only graduation

### Add After Validation (v1.x)

- [ ] Graduation ladder states (`community-reported`/`-confirmed`/`-fail`) formalized in the taxonomy — trigger: first real community submissions need a status
- [ ] `gsd-inbox` reconciliation automation (auto-diff submitted JSON vs canonical DB) — trigger: triage volume justifies it
- [ ] Walking-1s/0s address-bus quick check as an extra cheap pass — trigger: address-in-data proves valuable and users want a faster subset
- [ ] gist/attachment tier for verbose failure logs (byte dumps, raw serial traces) — trigger: a real failure overflows URL limits

### Future Consideration (v2+)

- [ ] Auto-merge/PR of a confirmed community entry into `chip_database.json` — defer: needs a mature, trusted flow; still human-gated
- [ ] Formalized local user-override staging of a community-tested entry — defer: `~/.firestarter/database.json` already exists; formalize only if demanded

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Per-chip test-plan engine | HIGH | MEDIUM | P1 |
| Independent non-fatal steps | HIGH | MEDIUM | P1 |
| Non-destructive default + `--destructive` gate | HIGH | LOW | P1 |
| Address-derived pattern + UV variant | HIGH | MEDIUM | P1 |
| Byte-mismatch fingerprint classifier | HIGH | MEDIUM | P1 |
| Dual-output report + auto-captured fields | HIGH | MEDIUM | P1 |
| Prompted provenance before sweep | HIGH | LOW | P1 |
| Tiered `--submit` | HIGH | MEDIUM | P1 |
| DB-diff in report | MEDIUM | MEDIUM | P1 |
| VPP/VPE mid-write capture | MEDIUM | MEDIUM | P2 |
| Transport-health capture | MEDIUM | LOW | P2 |
| Graduation ladder states | MEDIUM | MEDIUM | P2 |
| gsd-inbox reconciliation automation | MEDIUM | MEDIUM | P2 |
| Walking-1s/0s extra pass | LOW | LOW | P3 |
| gist/attachment verbose tier | LOW | LOW | P3 |
| Auto-graduation | (negative) | — | ANTI-FEATURE — do not build |

**Priority key:** P1 = must have for v1.21 launch · P2 = should have, add when possible · P3 = nice to have / future.

---

## Competitor Feature Analysis

| Feature | flashrom | minipro/TL866 | Our Approach (Firestarter) |
|---------|----------|---------------|----------------------------|
| Per-op test status | `.tested` struct (probe/read/erase/write/wp) | none (freeform) | per-op `OK/BAD/NA/SKIPPED` in report + ladder |
| Structured report | logs via paste, freeform prose | freeform issue prose | dual human+JSON, one self-contained artifact |
| Submission flow | patch or mailing-list logs | GitHub/GitLab issue | tiered `--submit`: gh issue → prefilled URL → gist |
| Graduation model | maintainer commits after full logs | maintainer triages issue/PR | **FLAG-only, maintainer confirms** (matches flashrom) |
| Address-fault-aware pattern | write/verify (user-run) | write/verify (user-run) | **address-derived pattern + fingerprint** (explicit differentiator) |
| Environment fingerprint | board mfr/model + logs (manual) | manual | **auto-captured** FW `version:board`, protocol path, VPP, transport |
| Human-only provenance | manual prose | manual prose | **prompted up front** (shield rev, provenance, pot) |

---

## Sources

- [flashrom — Board Testing HOWTO](https://www.flashrom.org/Board_Testing_HOWTO) — HIGH (official docs)
- [flashrom — How to mark chip as tested](https://www.flashrom.org/contrib_howtos/how_to_mark_chip_tested.html) — HIGH (official docs; graduation precedent)
- [flashrom — flashchips.c (`.tested` / `enum test_state`)](https://github.com/flashrom/flashrom/blob/main/flashchips.c) — HIGH (source)
- [minipro issue #109 — re-reverse-engineering the device DB](https://github.com/vdudouyt/minipro/issues/109) — MEDIUM (community tracker)
- [minipro issue #90 — user-defined chip configs](https://github.com/vdudouyt/minipro/issues/90) — MEDIUM (community tracker)
- [DavidGriffith/minipro — GitLab issues](https://gitlab.com/DavidGriffith/minipro/-/issues) — MEDIUM (active fork tracker)
- [Fault Models for Memories — V. Sontakke](https://medium.com/@vijay.n.sontakke/fault-models-for-memories-fe883b022380) — MEDIUM (secondary summary of standard fault models)
- [Walking/marching/galloping patterns for memory tests — Auburn Univ.](https://www.eng.auburn.edu/~agrawvd/COURSE/E7250_05/REPORTS_TERM/Raghuraman_Mem.doc) — MEDIUM (academic course material)
- [Targeting address-decoder faults using functional patterns — Embedded.com](https://www.embedded.com/targeting-soc-address-decoder-faults-using-functional-patterns/) — MEDIUM (industry article)
- [Method of diagnosing failures in ROM systems — US4876684](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4876684) — HIGH (patent; address-in-data stuck-line detection for ROM)
- [Method and system for testing address lines — US7532526](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7532526) — HIGH (patent; per-address-bit stuck-at method)

---
*Feature research for: community-distributed EPROM/Flash/SRAM device-test & reporting command*
*Researched: 2026-07-02*

---
created: 2026-08-05T08:38:31Z
title: "Skill: triage `dev test` issues — diagnose against the datasheet, comment, close passes into a tested-good IC list"
area: tooling
status: complete
completed: 2026-08-09
files:
  - firestarter_app/tools/parse_devtest_issue.py
  - firestarter_app/firestarter/diagnostic_report.py
  - firestarter_app/firestarter/submit.py
  - firestarter_app/datasheets/
  - .planning/v1.16/ledger/PROTOCOL-LEDGER.json
  - .claude/gsd-core/workflows/inbox.md
---

## Problem

Community `dev test` reports arrive as GitHub issues in `henols/firestarter_prom`
(`firestarter/submit.py` files them; see [issue tracking is centralized](../../MILESTONES.md)
— note b11 and earlier misfiled some into the app repo). Today a maintainer must open each
one, read the fenced JSON report by eye, decide whether the chip actually passed, judge
whether a failure is a chip fault / a shield fault / a real firmware protocol defect, and
then hand-write a reply. Nothing accumulates: a chip that three people have proven good
leaves no machine-readable trace, and the same diagnosis gets re-derived per issue.

Wanted: a skill that

1. **Fetches** the open `[dev test]` issues (read-only `gh` — see the caveat below).
2. **Parses + analyses** every report's data, not just its exit code.
3. **Compares against the EPROM's datasheet** to name the actual fault.
4. **Comments the diagnosis** on the issue.
5. **Closes** issues that are a clean pass, and **records the chip in a list of
   tested-good ICs**.

### What already exists (build on it, don't re-invent)

- `firestarter_app/tools/parse_devtest_issue.py` — the INBOX-01 triage parser from v1.21
  Phase 114. Already does detection (requires BOTH the `[dev test]` title marker AND a
  fenced ```json block carrying a `schema_version` key, by PRESENCE not value), bounded
  hostile-input parsing (never `eval`/`exec`/shell, every extractor fails SOFT), and
  `count_agreeing` — cross-report N≥2 grouping by the report's already-embedded
  `dedup_fingerprint` (never re-hashed). The skill is the layer ABOVE this; the parser
  should not be rewritten.
- `firestarter_app/firestarter/diagnostic_report.py` — the report schema (currently
  `SCHEMA_VERSION = "1.3"`, eleven `to_dict()` keys: `schema_version`, `generated`,
  `auto_capture`, `transport_health`, `steps`, `banner`, `voltage`, `is_submittable`,
  `dedup_fingerprint`, `db_diff`, `sdp_hold_state`). The analysis inputs are here:
  per-step `StepResult`s, `BannerCounts`, `voltage`, `auto_capture.{hw_revision,
  fw_board_identity, host_version, protocol}`, and `db_diff.{current_support_status,
  proposed_disposition, ladder_state}`.
- `.planning/v1.16/ledger/PROTOCOL-LEDGER.{md,json}` — the existing per-protocol
  verified / explicit-UNVERIFIED record. Closest thing to a tested-good list today, but
  it is protocol-scoped and milestone-frozen, not per-IC and not community-fed.
- The `gsd-inbox` skill already fetches/labels issues. Phase 114's D-04 deliberately kept
  the parser OUT of `inbox.md`; decide whether this new skill extends `gsd-inbox` or sits
  beside it, and keep that separation intact either way.

### Hard constraints that shape the design

- **The datasheet corpus is three PDFs.** `firestarter_app/datasheets/` holds only
  `AT28C256.pdf`, `SST39SF0x0A.pdf`, `W27C020.pdf`. "Compare with the prom's datasheet"
  cannot be the primary oracle for an arbitrary reported chip. The realistic oracle stack
  is: `chip_database.json` entry (timings, VPP/VPE, protocol, pin map) → `PROTOCOLS.md`
  bucket semantics → `PROTOCOL-LEDGER` verified/unverified status → datasheet PDF *when
  one is on hand*. Either accept a graceful "no datasheet for this part" degradation, or
  scope the phase to also solve datasheet acquisition — don't let the skill silently claim
  a datasheet-backed conclusion it did not have.
- **"Passed" is not `exit == 0`.** `dev test`'s exit precedence is `max(MARGINAL=2,
  BAD=1)` — MARGINAL beats BAD, and its own comment and docstring both claim the opposite.
  A pass must be decided from the report's banner/step data, never from a remembered exit
  rule.
- **Never auto-write `support_status`.** `diagnostic_report.py` is explicit (RPT-05/D-07):
  `db_diff.proposed_disposition` is ADVISORY text, `ladder_state` never becomes a concrete
  `support_status`, and the actual DB write stays a manual `build_db.py` edit. The
  tested-good list must therefore be a NEW artifact (its own JSON + human-readable
  rendering, fed by `dedup_fingerprint` and N≥2 agreement), feeding the graduation ladder
  rather than short-circuiting it.
- **Commenting and closing are outward-facing.** Both write to a stranger's issue under
  the maintainer's name. Default must be dry-run / propose-then-confirm, with the operator
  approving the comment text and the close. Note the standing hazard: GSD `--auto`/`--chain`
  AUTO-APPROVES human-verify gates, so `autonomous: false` alone is not self-protecting —
  the gate has to be structural.
- `gh` write operations (`issue comment`, `issue close`, `--label`) need write access and,
  for labels, a pre-existing label. Read-only `gh issue view/list` works in this
  environment; `gh workflow run` is blocked by the auto-mode classifier, so assume any
  write path may need the operator to run it.

## Solution

TBD — needs `/gsd-discuss-phase` before planning. Sketch of the shape:

1. **Ingest** — `gh issue list --repo henols/firestarter_prom --state open --json ...`,
   filter with the existing two-marker detection, extract each fenced report via
   `parse_devtest_issue.py`.
2. **Group** — bucket by `dedup_fingerprint` so N≥2 agreement is visible before any
   verdict; a lone N=1 report is a hypothesis, not a finding.
3. **Classify** — per group, decide PASS / chip-fault / board-or-contact-fault /
   host-or-firmware-defect from the step results + banner + voltage + `hw_revision` +
   `sdp_hold_state`, cross-checked against the DB entry and (when present) the datasheet.
   Each verdict must carry the evidence fields it rests on and say what it could not check.
4. **PASS path** — append to the tested-good list (chip name, protocol, fingerprint,
   fw/host versions, board revision, issue numbers, agreement count), propose the closing
   comment, close on operator approval.
5. **FAIL path** — post the diagnosis comment with the named probable cause and the next
   diagnostic step for the reporter; label; leave open. Where the diagnosis implicates
   firmware/host, emit a pointer suitable for a backlog/todo capture rather than silently
   ending at a comment.
6. **Guards** — dry-run default, no `support_status` write, explicit "datasheet not
   available" honesty, and a regression test over frozen issue-body fixtures (the existing
   `tests/test_parse_devtest_issue.py` already pins a `"1.1"`-era body — extend that
   pattern rather than replacing it).

Open question for discuss-phase: does the tested-good list live in the meta repo
(`.planning/`, maintainer-facing planning artifact) or in `firestarter_app`
(shippable, user-visible "known-good chips" data)? That choice decides whether it can be
committed by the skill at all, given the app is a submodule.

---

## COMPLETE — 2026-08-09

Shipped as **two** skills rather than one, splitting triage from root-cause:

- `.claude/skills/devtest-triage/` — SKILL.md + scripts. Triages community `dev test`
  issues in `henols/firestarter_prom` against the chip's datasheet: closes PASS issues and
  logs the chip, or posts a datasheet-grounded findings comment on FAIL/marginal ones.
- `.claude/skills/devtest-rootcause/` — SKILL.md + scripts. Takes a triaged failure into
  the code: a decode bug in the database generator, or a genuine host/firmware defect.
  Knows `chip_database.json` is generated and must never be hand-edited.

Both are registered and discoverable. The "nothing accumulates" complaint is addressed by
the tested-good chip log (`.planning/VALIDATED-EPROMS.md`) plus per-issue datasheet
findings comments.

# 152-CLAIM-GATE-TRANSCRIPTS.md — RED/GREEN evidence for `152-check-claims.py`

**This file deliberately contains forbidden vocabulary, quoted verbatim as evidence of what the
gate rejected. It is NOT a claim about the outward-facing close, and it is deliberately NOT a gate
target — it is absent from `152-check-claims.py`'s `_DEFAULT_TARGETS` by design (see the module's
own docstring and `test_the_transcript_file_is_not_a_gate_target` in `test_check_claims_152.py`).**
A future reader must not "fix" this file by rewording the RED blocks below to remove the forbidden
phrases — doing so would destroy the evidence the transcript exists to preserve. If this file were
ever added to `_DEFAULT_TARGETS`, every RED block below would make the gate permanently fail against
its own proof of itself working.

All commands below were run from
`.planning/phases/152-outward-facing-close-operator-gated/` with `python3` (3.12.13). Every `###`
heading pastes the literal command line, followed by the gate's literal stdout and its literal
`EXIT=` value — nothing paraphrased.

---

## RED — one block per forbidden-pattern label this phase added or modified

Each planted fixture carries all three required caveats and exactly one planted violation, so each
failure below is attributable to its own forbidden pattern and to nothing else about the document
(proven by `test_every_forbidden_pattern_has_a_planted_fixture` and the dedicated new legs, which
assert leg isolation programmatically; the transcripts below are the same runs, pasted for human
review).

### 1. `sdp-relock-as-shipped` — ADDED (plant = the roadmap's pre-amendment criterion-1 wording)

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_sdp_relock_as_shipped.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_sdp_relock_as_shipped.md:12: forbidden phrase match [sdp-relock-as-shipped]: 'write --sdp-relock'
EXIT=1
```

The plant's line 12 reads, in full: "The planted sentence, taken verbatim from ROADMAP.md's
pre-amendment criterion 1: `enable` returns as `write --sdp-relock`." — the command name is not
followed by a withdrawal predicate, so the negative lookahead does not permit it.

### 2. `sdp-relock-flag-as-shipped` — ADDED (the bare-flag companion)

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_sdp_relock_bare_flag.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_sdp_relock_bare_flag.md:11: forbidden phrase match [sdp-relock-flag-as-shipped]: '--sdp-relock'
EXIT=1
```

The plant's line 11 reads: "The planted sentence: the `--sdp-relock` option is available for
re-protecting a part." — no `write` precedes the flag (so the row-1 lookbehind does not suppress
it) and no withdrawal predicate follows it. Note this fires the bare-flag row alone, not the
command-first row — leg isolation, proven again by
`test_planted_sdp_relock_bare_flag_is_rejected`.

### 3. `issue-closed` — MODIFIED (32 dropped), with the three still-fires controls

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_issue_closed_gh21.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_issue_closed_gh21.md:11: forbidden phrase match [issue-closed]: 'gh#21 was closed'
EXIT=1
```

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_issue_closed_gh11.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_issue_closed_gh11.md:11: forbidden phrase match [issue-closed]: 'gh#11 was resolved'
EXIT=1
```

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_issue_closed_gh12.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_issue_closed_gh12.md:11: forbidden phrase match [issue-closed]: 'gh#12 was fixed'
EXIT=1
```

The row's alternation dropped `32` from `gh#(?:21|32|11|12)\b...` to `gh#(?:21|11|12)\b...`
(`152-RESEARCH.md` §C-5, D-05), so D-05's own required statement about gh#32 is expressible (see
the ALLOW section below) while gh#21, gh#11 and gh#12 all still fire — the narrowing did not become
a general loosening of the row.

---

## RED — donor-carried rows, for completeness

### 4. `proven-unqualified` — carried VERBATIM from the donor, narrowed to `(?<!software-)\bproven\b`

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_proven_unqualified.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 3 forbidden phrase match(es):
  fixtures/planted_proven_unqualified.md:2: forbidden phrase match [proven-unqualified]: 'proven'
  fixtures/planted_proven_unqualified.md:2: forbidden phrase match [proven-unqualified]: 'proven'
  fixtures/planted_proven_unqualified.md:16: forbidden phrase match [proven-unqualified]: 'proven'
EXIT=1
```

The plant's line 16 reads, in full: "The planted sentence: the write path is bench-proven on one
part, one controller, one shield revision." — a bare `bench-proven` compound, which is NOT the
`software-proven` compound the negative lookbehind permits. The two line-2 hits come from this
file's own HTML-comment header describing the plant, which independently uses the word twice. The
gate still exits non-zero and still names `proven-unqualified` — the narrowing did not disarm the
pattern.

### 5. `graduation` — donor-carried, unmodified

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_graduation.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_graduation.md:11: forbidden phrase match [graduation]: 'promoting protocol 13'
EXIT=1
```

### 6. `support-status-change` — donor-carried, unmodified

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_support_status_change.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_support_status_change.md:11: forbidden phrase match [support-status-change]: 'support_status:'
EXIT=1
```

### 7. `at28c256-fixed` — donor-carried, unmodified

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_at28c256_fixed.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_at28c256_fixed.md:11: forbidden phrase match [at28c256-fixed]: 'AT28C256 write path is finally fixed'
EXIT=1
```

### 8. `page-size-proven` — donor-carried, unmodified

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_page_size_proven.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_page_size_proven.md:11: forbidden phrase match [page-size-proven]: 'page size is validated'
EXIT=1
```

### 9. Missing required caveat — the `software-proven-unvalidated` row

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_missing_caveat_software_proven.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 file(s) missing a required caveat:
  fixtures/planted_missing_caveat_software_proven.md: missing required caveat [software-proven-unvalidated]: expected a phrase matching 'the software-proven / unvalidated-on-silicon qualifier'
EXIT=1
```

### 10. Missing required caveat — the `no-at28c-part-tested` row

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_missing_caveat_no_at28c.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 file(s) missing a required caveat:
  fixtures/planted_missing_caveat_no_at28c.md: missing required caveat [no-at28c-part-tested]: expected a phrase matching 'the "no AT28C part was tested" qualifier'
EXIT=1
```

### 11. Missing required caveat — the `zero-d-stays-unverified` row

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_missing_caveat_unverified.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 file(s) missing a required caveat:
  fixtures/planted_missing_caveat_unverified.md: missing required caveat [zero-d-stays-unverified]: expected a phrase matching 'the "0x0D stays UNVERIFIED in PROTOCOL-LEDGER" qualifier'
EXIT=1
```

---

## ALLOW — the two clean controls

```
$ python3 152-check-claims.py fixtures/clean_control.md ; echo EXIT=$?
PASS: scanned fixtures/clean_control.md; 1 of 1 caveat-required file(s) carry every caveat their own rule demands; 0 file(s) carry no caveat requirement (this PASS is compliance with the forbidden-phrase table and the per-file caveat rule only -- see the module docstring's explicit non-claim, and note that a green run alone does not discharge D-03's per-artifact blocking operator wording review)
EXIT=0
```

```
$ python3 152-check-claims.py fixtures/clean_control_second.md ; echo EXIT=$?
PASS: scanned fixtures/clean_control_second.md; 1 of 1 caveat-required file(s) carry every caveat their own rule demands; 0 file(s) carry no caveat requirement (this PASS is compliance with the forbidden-phrase table and the per-file caveat rule only -- see the module docstring's explicit non-claim, and note that a green run alone does not discharge D-03's per-artifact blocking operator wording review)
EXIT=0
```

`clean_control.md` carries the mandated `write --sdp-relock` withdrawal word order ("is
withdrawn -- tracked as Backlog 999.28") and D-05's gh#32 statement in the natural past-tense
phrasing ("gh#32 was closed on 2026-08-08 as a duplicate fold into gh#21") — this control proves
that the mandated withdrawal word order survives class (e), and that D-05's gh#32 statement
survives the narrowed `issue-closed` row.

`clean_control_second.md` carries a second, differently-worded withdrawal predicate ("remains
withdrawn, for a second release"), the parenthetical gh#32 form ("gh#32 (closed 2026-08-08, folded
into gh#21)"), and D-11's two exempted statements of shipped command behaviour ("Standalone erase
is now available on this protocol, and write no longer performs a blank check on it") — this
control proves that a second withdrawal phrasing and D-11's exempted statements of current,
user-visible command behaviour both survive the same forbidden-class table.

---

## GREEN — the real default targets, no argv, no seam

```
$ python3 152-check-claims.py ; echo EXIT=$?
PASS: scanned 152-CLAIM-CLASSES.md; 1 of 1 caveat-required file(s) carry every caveat their own rule demands; 0 file(s) carry no caveat requirement (this PASS is compliance with the forbidden-phrase table and the per-file caveat rule only -- see the module docstring's explicit non-claim, and note that a green run alone does not discharge D-03's per-artifact blocking operator wording review)
EXIT=0
```

This is the literal mechanical discharge of "armed against the real files" for this plan's scope:
the gate is armed against `152-CLAIM-CLASSES.md`, the one artifact Plan 152-01 already wrote,
while every other `152-*` artifact this phase will publish is still being written. A later plan
extends `_DEFAULT_TARGETS` and re-runs this transcript (see the "Extended target list" section
below).

---

## Paired suite — `python3 -m pytest test_check_claims_152.py -q -o addopts=""`

```
$ python3 -m pytest test_check_claims_152.py -q -o addopts=""
..............................                                           [100%]
30 passed in 1.13s
```

All 30 legs pass: the 20 donor legs (renamed to this phase's own module, env seam, and adapted to
this phase's committed fixtures where the donor's own generic fixtures do not exist here) plus the
six phase-specific legs — the two `sdp-relock` isolation legs, the mandated-withdrawal-sentence
leg, the three-fixture `issue-closed` still-fires leg, the gh#32-permitted leg, and the
three-fixture required-caveat-independence leg.

---

## What this transcript does and does not prove

**Does prove:** every forbidden-pattern label this phase added or modified (`sdp-relock-as-shipped`,
`sdp-relock-flag-as-shipped`, the narrowed `issue-closed`) fires on a real planted document via a
real subprocess invocation of the real gate script, attributable to that label alone; every
donor-carried row this phase did not modify still fires; each of the three required-caveat rows
fails independently on its own dedicated missing-caveat plant; the mandated `write --sdp-relock`
withdrawal word order and D-05's gh#32 closure statement both survive the same table that rejects
their shipped-framing and closed-issue counterparts; the gate is armed against the real
`152-CLAIM-CLASSES.md` artifact and passes.

**Does not prove (the gate's own explicit non-claim, from its module docstring):** that any scanned
document's prose is honest in every implication, omission or tone — only that it is free of this
specific forbidden-phrase table and carries the caveats its own per-file rule demands. A green gate
is not a wording review. D-03's per-artifact blocking operator checkpoint is the separate control
that reviews wording, and this transcript does not discharge it and must not be cited as
discharging it.

---

## Extended target list (Plan 152-13)

This section is filled in by Plan 152-13, which extends `_DEFAULT_TARGETS` beyond the single
`152-CLAIM-CLASSES.md` entry armed above. Not yet written as of this plan.

---

## Final target list (close-out, Plan 152-20 — the last SUMMARY added via argv)

This section is filled in by Plan 152-20, this phase's close-out plan, which scans the phase's
final `152-20-SUMMARY.md` via positional argv (it cannot be a `_DEFAULT_TARGETS` member while that
plan is still writing it) and records the last extended-list re-run. Not yet written as of this
plan.

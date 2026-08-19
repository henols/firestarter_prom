# 149-CLAIM-GATE-TRANSCRIPTS.md — RED/GREEN evidence for `149-check-claims.py`

**This file deliberately contains forbidden vocabulary, quoted verbatim as evidence of what the
gate rejected. It is NOT a claim about the page-size change, and it is deliberately NOT a gate
target — it is absent from `149-check-claims.py`'s `_DEFAULT_TARGETS` by design (see the module's
own docstring and `test_the_transcript_file_is_not_a_gate_target` in
`test_check_claims_v132.py`).** A future reader must not "fix" this file by rewording the RED
blocks below to remove the forbidden phrases — doing so would destroy the evidence the transcript
exists to preserve. If this file were ever added to `_DEFAULT_TARGETS`, every RED block below would
make the gate permanently fail against its own proof of itself working.

All commands below were run from
`.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/` with `python3` (3.12.13). Every
`###` heading pastes the literal command line, followed by the gate's literal stdout and its
literal `EXIT=` value — nothing paraphrased.

---

## RED — one block per forbidden-pattern label this phase added or modified

Each planted fixture carries the required `software-proven-unvalidated` caveat and exactly one
planted violation, so each failure below is attributable to its own forbidden pattern and to
nothing else about the document (proven by `test_every_forbidden_pattern_has_a_planted_fixture`,
which asserts leg isolation programmatically; the transcripts below are the same runs, pasted for
human review).

### 1. `proven-unqualified` — the MODIFIED pattern (`149-RESEARCH.md` §X-2), narrowed to `(?<!software-)\bproven\b`

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_149=fixtures/planted_proven_unqualified.md python3 149-check-claims.py ; echo EXIT=$?
FAIL: 3 forbidden phrase match(es):
  fixtures/planted_proven_unqualified.md:2: forbidden phrase match [proven-unqualified]: 'proven'
  fixtures/planted_proven_unqualified.md:2: forbidden phrase match [proven-unqualified]: 'proven'
  fixtures/planted_proven_unqualified.md:11: forbidden phrase match [proven-unqualified]: 'proven'
EXIT=1
```

The plant's line 11 reads (in full, in `fixtures/planted_proven_unqualified.md`): "0x07 is
bench-proven on one part, one controller, one shield revision." — a bare `bench-proven` compound,
which is NOT the `software-proven` compound the negative lookbehind permits. The two line-2 hits
come from this file's own HTML-comment header describing the plant, which independently uses the
word twice. The gate still exits non-zero and still names `proven-unqualified` — the narrowing did
not disarm the pattern.

### 2. `page-size-proven` — ADDED

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_149=fixtures/planted_page_size_proven.md python3 149-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_page_size_proven.md:7: forbidden phrase match [page-size-proven]: 'page size is validated'
EXIT=1
```

### 3. `graduation` — ADDED

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_149=fixtures/planted_graduation.md python3 149-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_graduation.md:7: forbidden phrase match [graduation]: 'promoting protocol 13'
EXIT=1
```

### 4. `support-status-change` — ADDED

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_149=fixtures/planted_support_status_change.md python3 149-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_support_status_change.md:7: forbidden phrase match [support-status-change]: 'support_status:'
EXIT=1
```

### 5. `issue-closed` — ADDED

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_149=fixtures/planted_issue_closed.md python3 149-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_issue_closed.md:7: forbidden phrase match [issue-closed]: 'gh#21 is now considered closed'
EXIT=1
```

### 6. `at28c256-fixed` — ADDED

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_149=fixtures/planted_at28c256_fixed.md python3 149-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_at28c256_fixed.md:7: forbidden phrase match [at28c256-fixed]: 'AT28C256 write path is finally fixed'
EXIT=1
```

## RED — the two donor-carried rows, for completeness

### 7. `confirmed-working` — carried unchanged from the donor table

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_149=fixtures/planted_forbidden_claim.md python3 149-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_forbidden_claim.md:10: forbidden phrase match [confirmed-working]: 'confirmed working'
EXIT=1
```

### 8. Missing required caveat — the `software-proven-unvalidated` row

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_149=fixtures/planted_missing_caveat.md python3 149-check-claims.py ; echo EXIT=$?
FAIL: 1 file(s) missing a required software-proven-unvalidated caveat:
  fixtures/planted_missing_caveat.md: missing required caveat [software-proven-unvalidated]: expected a phrase matching 'the software-proven / unvalidated-on-silicon qualifier'
EXIT=1
```

---

## GREEN — the real default target, no argv, no seam

```
$ python3 149-check-claims.py ; echo EXIT=$?
PASS: scanned 149-PAGE-SIZE.md; 1 of 1 caveat-required file(s) carry every caveat their own rule demands; 0 file(s) carry no caveat requirement (this PASS is compliance with the forbidden-phrase table and the per-file caveat rule only -- see the module docstring's explicit non-claim, and note that a green run alone does not discharge plan 08's human wording review)
EXIT=0
```

This is the literal mechanical discharge of "armed against the real files" for this plan's scope
(`149-RESEARCH.md` §R9e option 1 — the gate is armed against `149-PAGE-SIZE.md` while every other
`149-*-SUMMARY.md` is still being written; plan 08 extends the target list and re-runs this
transcript).

---

## Paired suite — `python3 -m pytest test_check_claims_v132.py -q -o addopts=""`

```
$ python3 -m pytest test_check_claims_v132.py -q -o addopts=""
....................                                                     [100%]
20 passed in 0.59s
```

All 20 legs pass: the 15 donor legs (renamed to this phase's own module and env seam) plus the
five phase-specific legs — the X-2 forward and negative-control pair, the transcript/upstream
exclusion pair, and the every-added-pattern-has-a-fixture leg.

---

## What this transcript does and does not prove

**Does prove:** every forbidden-pattern label this phase added or modified fires on a real
planted document via a real subprocess invocation of the real gate script, attributable to that
label alone; the gate is armed against the real `149-PAGE-SIZE.md` artifact and passes; the
narrowed `proven-unqualified` pattern still fires on a bare, unqualified `proven` after the
negative-lookbehind narrowing that PGSZ-05's own required phrase forced.

**Does not prove (the gate's own explicit non-claim, from its module docstring):** that
`149-PAGE-SIZE.md`'s prose is honest in every implication, omission or tone — only that it is free
of this specific forbidden-phrase table and carries the one required caveat. That is plan 08's
human wording review, which this transcript does not discharge and must not be cited as
discharging.

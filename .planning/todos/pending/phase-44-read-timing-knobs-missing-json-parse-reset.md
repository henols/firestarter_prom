---
created: 2026-08-19T00:00:00Z
title: "Phase 44 read-timing knobs (read_settling_us, read_strobe_us) are missing from json_parse's optional-key reset block"
area: firmware
resolves_phase: unassigned
files:
  - firestarter/src/json_parser.c
  - firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp
---

## Problem

Research Open Question 5 (149-RESEARCH.md). `firestarter_handle_t handle` is a single
file-scope global (`firestarter/src/firestarter.cpp:33`) with **no per-command `memset`** --
`json_parse` resets only its *optional* keys at the top of each parse, because the mandatory
keys are always overwritten by the current command. Phase 149 / D-05 added exactly this reset
for the new `page_size` field, on the reasoning that without it, a 128 parsed for one chip would
persist into the next command's chip if that command omitted `page-size` -- turning "absent means
64" false in practice.

**Measured (`firestarter/src/json_parser.c:83-100`):** the two Phase 44 read-timing knobs,
`read_settling_us` and `read_strobe_us`, are **not** in that reset block. This is the exact same
category of latent defect one field over -- it predates Phase 149 and Phase 149 does not
introduce it, but Phase 149's own D-05 fix makes its absence for these two fields conspicuous by
contrast (the reset block's own comment now says so explicitly, filed as this todo).

## Why this is not simply a page overrun

Both knobs treat `0` as "use the firmware default" (`read_settling_us == 0` -> no settling
delay; `read_strobe_us == 0` -> use the default 3µs), per
`firestarter/src/json_parser.c:358-359`. So the symptom of the missing reset is a **stale
non-zero knob value persisting into a later command** that did not specify one -- e.g. a read
issued with `read-settling-delay: 500` followed by a plain read for a different chip would
silently keep applying a 500µs settling delay -- rather than any buffer or address overrun. Lower
severity than the page-size case, but the same shape of bug.

## Deliberately not fixed in this phase

Adding the reset here would perturb
`firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp`'s
`test_read_timing_fields_default_zero_when_absent` test, which characterizes the current
(pre-fix) behaviour. A defect in this neighbouring field is its own change, with its own test
update, not a page-size phase's business.

## What would close it

Add `handle->read_settling_us = 0;` and `handle->read_strobe_us = 0;` to `json_parse`'s
optional-key reset block (`firestarter/src/json_parser.c:83-100`, immediately alongside the
existing `chip_id`/`page_size` resets), and update
`test_read_timing_fields_default_zero_when_absent` (and any sibling test asserting persistence
across commands) to match the corrected behaviour.

## Filed by

Phase 149 (dual-repo lockstep), research Open Question 5, Plan 07.

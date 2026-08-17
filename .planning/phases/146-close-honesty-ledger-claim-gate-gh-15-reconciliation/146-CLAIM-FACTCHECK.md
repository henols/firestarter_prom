# 146-CLAIM-FACTCHECK — the outward-facing quantitative claims, re-derived from source

> **Status of this document.** Not the output of any `146-*-PLAN.md`. The orchestrator produced it
> while plan `146-12` was parked at its blocking operator wording review, to make that review faster
> by settling the *checkable* half of it in advance.
>
> It **approves nothing**. The claim gate establishes that forbidden vocabulary is absent; this
> document establishes that the numbers resolve to live sources. Neither is the wording verdict, which
> is judgement about whether the prose claims more than the evidence supports — still the operator's,
> still outstanding. Nothing here was written into any frozen artifact; all three remain byte-identical
> to `146-12`'s recorded freeze.

## Why bother

The three artifacts about to be reviewed carry numbers. A number in a public comment that traces to a
stale record rather than to the shipped tree is exactly the failure this milestone is closing out — and
it is the one part of a wording review that can be settled mechanically instead of by reading. So each
was re-derived from the live source, not read back from the record that asserted it.

**Result: 6 of 6 verified, 0 discrepancies.** Two apparent problems turned out to be defects in the
checking, not in the text; both are recorded below rather than quietly dropped, because a check that
cried wolf twice is worth knowing about.

## The checks

### 1. `146-GH15-RECONCILIATION.md:46` — "the modal value in 113 of 170 `0x07` chips at `100` us"

**VERIFIED EXACT** against the shipped `firestarter_app/firestarter/data/chip_database.json`:

| algorithm | n | modal pulse | distribution |
|---|---|---|---|
| `7` (`0x07`) | **170** | **`"100 us"` ×113** | 200×27, 1000×22, 500×4, 50×4 |
| `8` (`0x08`) | 127 | `"100 us"` ×104 | 50×11, 10×7, 200×2, 1000×2 |
| `11` (`0x0B`) | 32 | `"500 us"` ×21 | 1000×6, 200×5 |

All three rows match `PROJECT.md`'s C2 correction figure-for-figure. This is the strongest quantitative
claim in the text that would be posted, and it is live-accurate rather than inherited.

**Checking defect #1 (mine, not the text's).** The first two queries returned **zero rows** and looked
like the claim was fabricated. The cause was the query: the database nests `vendor -> [chip]` and the
fields are `programming.algorithm` (an **int**, so `0x0B` is `11`) and `programming.pulse_duration` (a
**string**, `"100 us"`). `protocol_id` / `pulse_delay` — the names `PROJECT.md` and the issue text both
use — do not exist in the shipped schema; v1.19/v1.20 renamed them. A zero-row answer from the wrong
field name is indistinguishable from a false claim, which is worth remembering next time.

### 2. `146-RELEASE-NOTES-fw.md:80` — the `+96 B` flash-band exemption

**VERIFIED.** `+96 B` appears 11 times across `145-BENCH-LOG.md` and the Phase 144 records, with the
attribution the release note gives it: a defect fix, admitted rather than laundered, and not
remediated. The note's phrasing "not remediated" matches the record's own standing status.

### 3. `146-RELEASE-NOTES-app.md:80` — "roughly 4687 microseconds ... `leonardo` ... roughly 9375 ... `uno`"

**VERIFIED EXACT** against `143-HOST-RECORD.md:164`, which derives both:

    120 / (25 x 1024) = 4687 us   (leonardo)
    120 / (25 x  512) = 9375 us   (uno)

The two numbers differ because the data buffer differs — 1024 B on Leonardo, 512 B on Uno — which is
precisely what the note's "board-specific, not universal" clause asserts. The derivation is per-board
by construction, so the claim is not merely true but true *for the stated reason*.

**Checking defect #2 (mine again).** `9375` does not appear anywhere in `145-BENCH-LOG.md`, which
briefly read as an unsourced figure. It is a **host** timeout derivation from Phase 143, not a bench
measurement, so the bench log is simply the wrong place to look.

Worth flagging for the reviewer, because the two are one digit apart and mean different things:

- **4687 us** — the derived timeout *gap* above which a pulse can time out. What the release note uses.
- **4688 us** — the `--pulse-us 4688` value Phase 145's Gate 3 passed as an override.

The note uses **4687**, which is the correct one for the sentence it appears in. A future editor
"correcting" it to 4688 would introduce an error.

### 4. The program-VCC ceiling — consistency across every document that states it

**VERIFIED CONSISTENT.** The roughly 6.25 V figure and a silicon-margin phrase appear together in all
eight documents that touch the subject — the four gate targets and the four shipped CLOSE-03 docs:

| document | `6.25` | silicon-margin phrase |
|---|---|---|
| `146-LEDGER.md` | 5 | 2 |
| `146-GH15-RECONCILIATION.md` | 2 | 2 |
| `146-RELEASE-NOTES-fw.md` | 1 | 1 |
| `146-RELEASE-NOTES-app.md` | 1 | 1 |
| `firestarter/doc/PROTOCOLS.md` | 3 | 3 |
| `firestarter/CLAUDE.md` | 1 | 1 |
| `firestarter/README.md` | 1 | 1 |
| `firestarter_app/README.md` | 1 | 1 |

No document states a competing ceiling figure. A first pass appeared to find `3.9 V` and `2.4 V` in the
artifacts; both were an over-loose regex clipping **23.9 V** and **22.4 V** out of the Phase 79 rail
readings (`146-LEDGER.md:176`, `:225`) — a different rail and a different quantity entirely.

### 5. `--pulse-us` is bounded only by the host

**VERIFIED** in shipped source at `firestarter_app/firestarter/cli_handlers.py:576-578`:
`type=click.IntRange(1, 65535)`, with `default=None` and an in-source comment explaining why `0` would
make every `firestarter write` exit 2. This supports the records' standing note that the firmware-side
`MSG_ERR_PULSE_TOO_WIDE` guard is unreachable while the `0x07`/`0x08` rows ship an energy cap of zero,
leaving the host range as the only live bound.

### 6. Caveat compliance is content-matched, not label-matched

**VERIFIED, with a negative control.** `_CAVEAT_RULES` maps four of the five gate targets to
`ceiling-voltage` and `ceiling-narrowing`, but those are the gate's internal *label names* — the
patterns actually matched are `6\.25\s*V` and `silicon[-\s]margin` (case-insensitive). Searching the
artifacts for the label strings returns nothing and proves nothing.

To confirm the check is not vacuous, both phrases were stripped from a scratch copy of
`146-LEDGER.md`; the gate then exited 1 naming **both** missing labels. So the passes recorded
elsewhere are real passes.

## What this does not cover

- **The wording verdict itself.** Every claim checked here is one with a number in it. The judgements
  that matter most — whether a narrowing is placed where a skimming reader will meet it, whether the
  public correction reads as a correction rather than a defence, whether a partial progress bar could
  still be misread as a partial write — are not mechanically checkable and are exactly what `146-12`'s
  gate asks the operator for.
- **Prose claims with no figure**, such as the characterisation of the bench coverage as asymmetric.
- **Anything about the firmware image on the attached board.** A version string identifies neither the
  image nor its commit.
- **The two protocols validated in the golden trace only.** Their status is unchanged by this document.

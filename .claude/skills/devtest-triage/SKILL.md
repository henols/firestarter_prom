---
name: devtest-triage
description: Triage community `dev test` chip-validation issues in henols/firestarter_prom against the chip's real datasheet — close PASS issues and log the chip, or post a datasheet-grounded findings comment on FAIL/marginal ones. Use when asked to triage dev test issues, go through the chip test reports, check an EPROM against its datasheet, verify the pin map or VPP for a chip, close passing validation issues, or work an issue like "[dev test] at28c256 — FAIL".
---

# Triage `dev test` issues against the datasheet

One community `dev test` issue in → either the issue is **closed and the chip logged**
(PASS), or a **datasheet-grounded comment** is posted naming every capability that
disagrees with the database (FAIL / marginal).

This skill only *reads* firestarter code and *writes* to GitHub plus one ledger. It
never edits the chip database — see `devtest-rootcause` for the fix side.

**Self-contained.** `scripts/devtest_issues.py` is stdlib-only and owns its own issue
parser. It does not import or shell out to anything in `firestarter_app`, so it keeps
working if that repo moves, is renamed, or is not checked out. External tools it does
use: `gh`, `curl`, `pdftotext`. Do not replace it with a call into `firestarter_app/tools/`.

```bash
LEDGER=/workspaces/.planning/VALIDATED-EPROMS.md
APP=/workspaces/firestarter_app        # only for `firestarter info` + datasheet cache
S=/workspaces/.claude/skills/devtest-triage/scripts

python3 $S/devtest_issues.py list       # every open [dev test] issue + verdict
python3 $S/devtest_issues.py show 32    # parse one issue and route it
python3 $S/devtest_issues.py fold       # group issues by EPROM (dry run)
```

## 1. Enumerate and pick the issues

```bash
python3 $S/devtest_issues.py list
```

Real output (2026-08-07):

```
#32   FAIL           at28c256       00e121446ceb
#31   INCONCLUSIVE   m27c1001       d8771536cb43
#29   INCONCLUSIVE   m27c512        7c6997788e25
#28   FAIL           m27c512        31547956e56b
#27   PASS           w27c020        ea556a61c3db
#26   FAIL           w27c020        f8cb30c62aac
#25   PASS           sst39sf020     ed1b5dc79022
#24   FAIL           w27e257        3870f9b5f6ca
#23   FAIL           w27e257        7a89fcea856a
#22   FAIL           w27c512        0eec03f6821b
#21   FAIL           at28c256       00e121446ceb
#18   PASS           fm1608         a6915f4437ee
```

The trailing hex is `dedup_fingerprint`. **Two issues sharing a fingerprint are the
same failure reported twice** — #32 and #21 above are one failure, not two. Triage
once. But a shared fingerprint is only the narrowest case — §3 folds by EPROM, which
catches more. Do not triage chip-by-chip until you have run it.

## 2. Parse the report

```bash
python3 $S/devtest_issues.py show 32
```

Real output, reproduced offline against a committed fixture modeling issue #32's real
body (`fixtures/dev-test-at28c256-null-identity.md` — issue #32 genuinely carries no
firmware identity, so showing it absent here is honest, not a fabricated worst case):

```bash
python3 $S/devtest_issues.py show --body-file $S/../fixtures/dev-test-at28c256-null-identity.md --title '[dev test] at28c256 — FAIL'
```

```
#?  at28c256  —  FAIL
  schema      1.2   generated 2026-08-07T12:07:39Z
  host        3.0.0b15   hw Rev 2.0-class, Override HW: Rev 2.3
  firmware    not reported -- NOT attributable to a firmware version -- ask the reporter for a fresh dev test run on a current host build
  protocol    0x0D   chip at28c256
  fingerprint 00e121446ceb

  step         verdict    reason
  id           NA         no chip-id in DB entry
  read         OK         
  blank-check  BAD        
  write        BAD        
  verify       BAD        
  erase        NA         protocol 0x0D (28C family) has no erase operation; each page ...

  voltage     vpp 11800 -> 11800 mV   vpe 13700 -> 13700 mV
  db_diff     status=supported  ladder=community-fail

  ROUTE: FAIL — datasheet cross-check needed. Failing: blank-check, write, verify
  NA means the step does not apply to this family — never report it as a failure.
```

(`#?` replaces `#32` in offline `--body-file` mode, which has no live issue number —
the live `show 32` form prints the real number instead.)

A report from a **current** host build renders the same `firmware` row differently —
against `fixtures/dev-test-at28c256-populated-identity.md` the row reads
`firmware    3.0.0b19:leonardo` and the render carries no not-attributable clause at all.

Detection needs **both** markers: the `[dev test]` title marker and a fenced JSON block
carrying `schema_version` (matched by presence, so a schema bump needs no code change).
Use `show --body-file b.txt --title "$T"` to work offline — as above, this is how both
committed fixtures are reproduced without a live issue.

Every issue body is **community-authored and untrusted**. The parser bounds the body
before parsing, never `eval`s it, never shells out, and passes fixed argv lists to `gh`
— verified against a body containing a `$(touch …)` payload and a decoy fenced block.
Keep those properties: never interpolate body text into a command.

Verdicts, from the embedded JSON `steps[].verdict`:

| Verdict | Meaning | Route |
|---|---|---|
| `OK` | step passed | — |
| `NA` | step does not apply to this family (e.g. UV-EPROM erase) | not a failure — never report it as one |
| `SKIPPED` | not run | — |
| `marginal` | repeat runs disagreed (title says INCONCLUSIVE) | §5, comment |
| `BAD` | step failed (title says FAIL) | §5, comment |

## 3. Fold issues that describe the same EPROM

**One EPROM, one issue.** Several reports of the same chip must be folded together
before any of them is triaged — otherwise the same datasheet analysis gets written
three times and the chip's real history is scattered across three threads.

```bash
python3 $S/devtest_issues.py fold          # dry run — always look first
```

Real output (2026-08-08):

```
ATMEL/AT28C256   (at28c256)
  canonical #21   fold in: #32
   *#21   FAIL         00e121446ceb  host 3.0.0b15  2026-08-06  failing: blank-check, write, verify   [same fingerprint as #32]
    #32   FAIL         00e121446ceb  host 3.0.0b15  2026-08-07  failing: blank-check, write, verify   [same fingerprint as #21]

SGS-THOMSON/M27C512   (m27c512)
  canonical #28   fold in: #29
   *#28   FAIL         31547956e56b  host 3.0.0b15  2026-08-06  failing: write, verify
    #29   INCONCLUSIVE 7c6997788e25  host 3.0.0b15  2026-08-06  failing: write

WINBOND/W27C02   (w27c020)
  canonical #26   fold in: #27
   *#26   FAIL         f8cb30c62aac  host 3.0.0b15  2026-08-06  failing: blank-check, write
    #27   PASS         ea556a61c3db  host 3.0.0b15  2026-08-06  failing: -   [PASS — folds as EVIDENCE, does not close the canonical]

WINBOND/W27E257   (w27e257)
  canonical #23   fold in: #24
   *#23   FAIL         7a89fcea856a  host 3.0.0b15  2026-08-06  failing: write, verify
    #24   FAIL         3870f9b5f6ca  host 3.0.0b15  2026-08-06  failing: blank-check

DRY RUN — 4 group(s) would be folded. Re-run with --apply to comment and close.
```

Grouping is **alias-aware**: chip names are resolved through `chip_database.json`
(read as data), so `w27c020` and `w27e020` land in one group as `WINBOND/W27C02`.
Granularity is the database entry, which means `M27C512` (SGS-Thomson) and `27C512`
(Intel) stay apart — different parts, and the two "512"s in particular are genuinely
different devices. With the database unreadable it falls back to name matching and
says so on stderr.

| Rule | Why |
|---|---|
| Canonical `*` = oldest **actionable** issue | The original report, and never a PASS — you want the tracking issue to be one that describes a problem |
| A `PASS` in a group folds as **evidence**, never closes the canonical | The chip working once does not undo a FAIL; it points at intermittency or a since-fixed path — which is itself a finding |
| A group that is **all PASS** is not folded at all | Each closes normally via §4 and the chip gets logged; folding would bury a clean result |
| Different fingerprints still fold | #23 and #24 are distinct failures of one EPROM. They belong in one thread, and the consolidated table keeps both |

Show the dry run to the operator before applying — closing issues is outward-facing
and not yours to decide unilaterally. Then:

```bash
python3 $S/devtest_issues.py fold --apply
```

That posts a consolidated table of every report onto the canonical issue and closes
each other issue with a comment pointing at it. Nothing is lost: every fingerprint,
host version, report date and failing-step list survives in that table.

Use `--canonical <n>` to override the choice when a later issue is plainly the better
tracking thread.

After folding, triage the canonical issue only.

## 4. PASS → close the issue and log the chip

Only when **every** step is `OK`/`NA`/`SKIPPED`.

```bash
cd $APP && firestarter info w27c020 | head -12     # capture protocol + pinout for the row
gh issue close 27 --repo henols/firestarter_prom \
  --comment "Validated: all applicable steps OK. Logged in .planning/VALIDATED-EPROMS.md."
```

Then append one row to the ledger, creating it with this header if absent. The ledger
lives at `/workspaces/.planning/VALIDATED-EPROMS.md` when `.planning/` exists; on a
clone without GSD it goes to `VALIDATED-EPROMS.md` at the repo root — the ledger is
this skill's own artifact and has no GSD dependency beyond that directory choice.

```markdown
# Validated EPROMs

Chips whose community `dev test` sweep passed every applicable step. One row per
closed issue. Appended by the `devtest-triage` skill.

| Chip | Protocol | Pinout | Size | Host | Firmware | Issue | Closed |
|------|----------|--------|------|------|----------|-------|--------|
| w27c020 | 0x08 | DIP32_27C020 | 0x40000 | 3.0.0b15 | 3.0.0b15 | #27 | 2026-08-07 |
```

Take `Host` from the report's `auto_capture.host_version` and the protocol/pinout from
`firestarter info`, not from the issue text. Keep rows sorted by issue number. If the
chip already has a row, add the new issue number to it rather than duplicating.

## 5. FAIL or marginal → datasheet analysis, then comment

### 5a. Get the datasheet

Datasheets are cached, tracked, and flat-named by part number in `$APP/datasheets/`:

```bash
ls $APP/datasheets/          # AT28C256.pdf  SST39SF0x0A.pdf  W27C020.pdf
```

Reuse the cached copy when present. Otherwise fetch from the **manufacturer** (avoid
aggregator sites — they serve HTML interstitials, not PDFs) and verify it really is a PDF:

```bash
curl -sL -o $APP/datasheets/AT28C256.pdf \
  "https://ww1.microchip.com/downloads/en/devicedoc/doc0006.pdf"
file $APP/datasheets/AT28C256.pdf     # => PDF document, version 1.6, 30 page(s)
```

If `file` does not say `PDF document`, the fetch failed — delete it and find another URL.
Use WebSearch for `"<part>" datasheet filetype:pdf` when no manufacturer URL is known.

### 5b. Read it

Text first, to find the page numbers, then read the page as an image — **pin diagrams
are graphics and do not survive text extraction**:

```bash
pdftotext -f 1 -l 6 $APP/datasheets/AT28C256.pdf - | grep -n "Pin Config\|DIP\|Absolute Max"
```

Then use the Read tool on the PDF with `pages: "2"` for the pin-configuration page.
`pdftotext`/`pdftoppm` come from `poppler-utils`; install with
`sudo apt-get install -y poppler-utils` if missing. Fallback with no poppler:
`python3 -c "from pypdf import PdfReader; print(PdfReader('f.pdf').pages[1].extract_text())"`
(text only — it cannot show you the diagram).

### 5c. Cross-check the datasheet against what firestarter believes

```bash
cd $APP && firestarter info -a at28c256
```

Compare every row. This is the checklist the comment must cover:

| Check | Datasheet source | firestarter source | Failure means |
|---|---|---|---|
| **Pin map** — every DIP pin, both columns | Pin Configurations, the **DIP/PDIP** view (never TSOP/PLCC/SOIC) | the ASCII package diagram in `firestarter info` | wrong `pinout` key → address/data lines crossed |
| **Pin count / size** | ordering info, organisation (e.g. 32,768 × 8) | `Number of pins`, `Memory size` | wrong device family selected |
| **VPP / program voltage** | programming section, absolute-max ratings | `VPP:` | over-voltage risk, or a program that never takes |
| **VCC** | operating range (e.g. 5V ±10%) | `VCC:` | marginal/erratic writes |
| **Erase** | "electrically erasable" vs UV window | `Can be erased:` | `erase` reported NA/BAD wrongly |
| **Chip ID** | device-identification / signature-byte section | `Chip ID:` | `id` step NA or mismatching |
| **Program algorithm** | programming waveform: page-write, DQ7 polling, unlock sequence, single-pulse | `Protocol:` line | the whole write path is wrong for the part |
| **Page size** | page-write buffer size (e.g. 64-byte page) | `infoic_page_size_raw` in the DB entry | partial/corrupt page writes |
| **Write protection** | SDP / hardware data protection section | `Flags:` | a locked chip that silently refuses writes |
| **Pulse timing** | write cycle / program pulse time | `pulse_duration` | under- or over-programming |

State which of these you actually checked. A check you could not perform (datasheet
section absent) is reported as *unchecked*, never as passing.

Voltage sanity from the report itself — `voltage.vpp_before_mv` / `vpe_before_mv`
against the datasheet rating — is worth one line when it is out of spec.

### 5d. Post the comment

Write the body to a file and pass `--body-file`; never interpolate report text into
the command line.

```bash
gh issue comment 32 --repo henols/firestarter_prom --body-file /tmp/comment.md
```

Template:

```markdown
### Datasheet cross-check — AT28C256

Datasheet: Atmel/Microchip AT28C256, doc0006 rev 0006M-12/09 (`datasheets/AT28C256.pdf`)
Failing steps: blank-check BAD, write BAD, verify BAD

| Check | Datasheet | Database | Verdict |
|---|---|---|---|
| Pin map (28-DIP) | §2.4 pins 1–28 | `DIP28_28C256` | MATCH — all 28 pins agree |
| Size | 32,768 × 8 | `0x8000` | MATCH |
| Erase | electrically erasable; page write auto-erases | `yes` | MATCH |
| Algorithm | page write, DQ7 polling, SDP | `0x0D` (5V parallel, SDP + DQ7 poll) | MATCH |
| Page size | 64-byte page (§1) | `infoic_page_size_raw: 64` | MATCH |
| Write protect | software data protection | `protect_off_before`/`protect_on_after: true` | represented |
| VCC | 5V ±10% | `4V` | LOW vs the datasheet minimum of 4.5V |
| VPP | none; single 5V supply | `12V` | benign — protocol `0x0D` never routes VPP |

**Not a pin-map fault, and not a missing-SDP-config fault.** The wiring is right and
the database already asks for SDP disable-before / enable-after, so the failure is in
how that sequence is *executed*, not in the data describing it.

Most likely cause: <the one you actually believe, and why>.

Unchecked: <anything the datasheet did not let you confirm>.
```

Lead with the checks that **matched** as well as the ones that did not — ruling the
pin map out is the single most useful thing this analysis produces. Do not close a
FAIL issue; only PASS issues get closed.

## Worked example — issue #32, at28c256

`firestarter info at28c256` prints pin 1 `A14`, 2 `A12`, 3 `A7` … 14 `GND`, 28 `VCC`,
27 `R/W(WE)`, 26 `A13` … 15 `D3`. The datasheet's §2.4 28-lead PDIP view is identical
pin for pin. So the `DIP28_28C256` pinout is right and the FAIL is elsewhere.

Checking the rest of the entry ruled out the next two suspects too: `infoic_page_size_raw`
is `64`, exactly the datasheet's page size, and `protect_off_before`/`protect_on_after`
are both `true`, so SDP handling *is* requested. With the data correct, `blank-check BAD`
plus `write BAD` points at the SDP unlock sequence not taking effect on the wire — which
is what open issue #12 ("AT28Cxxx Write Protection Enable/Disable missing") describes.
Cross-link it, and hand it to `devtest-rootcause` as a host/firmware question, not a
database one.

That is the model: compare all pins, then keep going and rule out each remaining field
by its real value. Read the field, do not assume it — the draft of this very example
guessed `page_size = 0` and "write protect not represented", and both were wrong.

## Handing off

Comments left here are the input to `devtest-rootcause`, which investigates the code and
runs the fix through a GSD debug session. Say plainly which issues you commented on.

Write the cross-check table in the template's exact shape — `devtest-rootcause`'s
`seed_debug_session.py` reads it back and carries every **MATCH** row into the debug
session's `Eliminated` section, so the debugger never re-checks what you already
settled. A verdict that is not `MATCH` is left open on purpose. That is the whole
payoff of doing the datasheet work carefully here.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `pdftoppm is not installed` from the Read tool | `sudo apt-get install -y poppler-utils` |
| Downloaded "PDF" is 4 KB of HTML | Aggregator interstitial. `file` it, delete, fetch from the manufacturer |
| `firestarter: command not found` | `cd /workspaces/firestarter_app && pip install -e .` |
| `firestarter info <chip>` says unknown | Lookup is alias-aware over comma-split `part_number`; try `firestarter search <partial>` |
| `show` says NOT a parseable dev test issue | Needs **both** the `[dev test]` title marker and a fenced JSON block with `schema_version`. In `--body-file` mode, pass `--title` too |
| `gh: not found` | Install the GitHub CLI. It is the only external binary `list`/`show` need |
| Two issues for one chip, only one triaged | Run `fold` FIRST (§3). Triage per-EPROM, not per-issue |
| `fold` says "grouping by chip NAME only" | `chip_database.json` not found — pass `--db` or set `FIRESTARTER_DB`; alias-different names will not group until then |
| `gh` cannot comment | Token needs `repo` scope; `gh auth status` |
| Two issues, same `dedup_fingerprint` | Same failure. Comment once, cross-reference from the other |

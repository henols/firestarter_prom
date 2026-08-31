# Phase 168 Honesty Ledger

Phase 168's own purpose is preventing a false claim from surviving a relocation. This ledger is
not a summary of what shipped — thirteen `168-NN-SUMMARY.md` files already say that. It is the
list of things a reader might otherwise *assume* from those summaries, paired against what is
actually true. Each entry names its own evidence rather than asking to be taken on faith.

## 1. Claim / non-claim pairs

**1. Relocation is not verification.**
- **Claim:** Twelve `doc/` files are now reachable on the wiki (MIGRATE-01, WIKI-05).
- **Non-claim:** Reachability says nothing about whether their *content* is correct. `wiki.py
  links` proves a page can be found; it does not read a single word of what the page says.
  Correctness of content is a separate, narrower claim — see entries 3 and 4 below for exactly
  how much of it this phase actually checked.
- **Evidence:** `evidence/wiki05-live-GREEN.txt`, `evidence/phase-gates.txt` criterion 8.

**2. HONEST-01 is a one-shot proof, and the source side is now frozen forever.**
- **Claim:** HONEST-01 proved the wiki carries the same claim force as the pre-deletion `doc/`
  sources, and it passed (0 dropped, 0 added, 6 vacuous).
- **Non-claim:** That proof ran exactly once, by design (D-03). Both `doc/` directories are now
  deleted, so `MIGRATION-TABLE.md`'s recorded SHAs are the *only* surviving oracle for the
  pre-migration text, permanently. Nothing after this phase stops a later wiki edit from quietly
  softening a claim the 2026-08-31 documents made — HONEST-02 is the standing gate for *future*
  drift against the database, but it has no memory of what the source documents originally said.
  This is an accepted cost of the model, not an oversight.
- **Evidence:** `tools/wiki/honest01_claims.py`, `168-11-SUMMARY.md` "Next Phase Readiness".

**3. Half of the HONEST-01 requirement was vacuous from the corpus side, not the checker side.**
- **Claim:** "Every `support_status` value and every `PROTOCOL-LEDGER` `UNVERIFIED` bucket is
  present on the wiki with the same force" — ROADMAP criterion 4 — passed.
- **Non-claim:** The `PROTOCOL-LEDGER` / `UNVERIFIED` half of that sentence was never testable
  against this corpus, because none of the 12 migrating documents ever cited it. Measured:
  `vpp-exceeds-max`, `UNVERIFIED` and `PROTOCOL-LEDGER` all occur **0 times** in the pre-deletion
  source. `PROTOCOL-LEDGER.json` itself exists (at `.planning/v1.16/ledger/PROTOCOL-LEDGER.json`,
  not the path CONTEXT.md/REQUIREMENTS.md state) and does carry 7 `UNVERIFIED` entries — but
  nothing in this phase's corpus ever pointed at it. The checker prints this as an explicit
  `0 of 0 -- VACUOUS, not checked` line on every run, never folded into the pass line.
- **Evidence:** `tools/wiki/claim-vocabulary.json`'s `expected_zero`; `evidence/honest01-live-GREEN.txt`
  ("6 vacuous"); `168-RESEARCH.md` § "The Claim Vocabulary".

**4. The truth check's resolve leg is scoped to three delimited regions; eight pages are unchecked.**
- **Claim:** HONEST-02 checks that per-chip/per-protocol claims on the wiki resolve against
  `chip_database.json` (ROADMAP criterion 5).
- **Non-claim:** Leg 2's resolve check only reads inside an explicit
  `firestarter-claims-begin`/`-end` region, and only three pages have one: Programming-Protocols,
  AT28C04-Adapter, Protocol-ID. The other eight claim-bearing pages carry a freshness *stamp*
  (Leg 1 + Leg 3 confirm it is present and current) but their prose is never resolved
  token-by-token against the database. Named explicitly by the checker as
  `UNCHECKED (stamp only)`, never silently passed: **Community-Validation, Infoic-Field-Dictionary,
  Lockable-PROMs, Package-Details, Pinout-Safety-Review, Protocol-Flags, SRAM-and-NVRAM-Behavior,
  Shield-Revisions.** This scoping was a deliberate, measured correction — a free-text scrape of
  the whole corpus was falsified in `168-RESEARCH.md` (3% resolve rate on Lockable-PROMs' 209
  bold tokens; 11 of 20 `0xNN` tokens on the zero-part-number Shield-Revisions page "resolve" by
  pure numeric coincidence).
- **Evidence:** local run this plan, Task 1: `LEG 2 -- claims resolve: 3 regions found, 60 claims
  checked, 8 pages stamp-only unchecked`; `168-12-SUMMARY.md`.

**5. The packaging change is a measured no-op; the "three files shipped" premise was false.**
- **Claim:** MIGRATE-03 required observing the packaging effect of deleting `doc/`.
- **Non-claim:** No `doc/` file was ever inside the published `firestarter` package. A clean
  build of the pre-phase tree (doc/ still on disk, 10 files) already produced **0** `doc/`
  entries; the current tree also produces 0; the two most recently published PyPI releases
  (`3.0.0b33`, `3.0.0b34`) independently confirm 0. The belief that three files shipped traced to
  a stale, gitignored `firestarter.egg-info/SOURCES.txt` — never to `pyproject.toml` or
  `MANIFEST.in`, neither of which ever mentioned `doc/`. Stating that packaging improved would be
  a false claim inside the milestone whose purpose is preventing exactly that.
- **Evidence:** `evidence/migrate03-sdist-doc-delta.txt`.

**6. Seventeen test legs were deleted; the flash-map/pyusb-floor parity loss is the sharpest.**
- **Claim:** MIGRATE-02/03 removed both `doc/` directories with the app suite staying green.
- **Non-claim:** Staying green required deleting 17 test legs across 5 modules whose oracle was a
  `doc/` file — 12 documentation-claim legs plus 5 install-doc packaging legs — none of which is
  replaced by anything this phase built. HONEST-02 is a coarser, per-chip/per-protocol stamp
  mechanism; it does not cover figure-level or citation-level parity the deleted legs asserted.
  The sharpest of the seventeen: `test_install_doc_app_region_end_matches_host_constant` and
  `test_install_doc_flash_base_matches_host_constant` were the *only* external cross-check this
  project ever had between `py32_dfu.APP_REGION_END`/`py32_dfu.FLASH_BASE` and any written
  description of them — and `test_install_doc_pyusb_floor_matches_pyproject`, the only check that
  `pyproject.toml`'s `[py32]` pyusb floor and the install guide's own stated floor still agreed.
  All three parity gates are gone until the deferred PY32F071 install guide is republished; that
  restoration is owed to whichever phase does so, not delivered here. 33 code-side legs across
  the same 5 modules (26 + 7) still run, unchanged.
- **Evidence:** `168-09-SUMMARY.md` "What Each Deleted Leg's Coverage Cost, and Whether It Is
  Checked Elsewhere" (the full 17-row table).

**7. One file was deleted without ever being published, recoverable only from a recorded commit.**
- **Claim:** `firestarter_app/doc/` no longer exists (MIGRATE-02).
- **Non-claim:** That directory held 10 files, not the 9 that were migrated —
  `PY32F071-FIRMWARE-INSTALL.md` was deleted along with it, by operator decision (2026-08-30):
  the PY32F071 work is planning-stage and its code a proof-of-concept, so publishing an install
  guide would promise a capability the project cannot back. It joins the FUT-W deferral family.
  Deferred did not become *lost*: its pre-deletion SHA
  (`d56424e1979edf7245cffb9ec3111c0469f5b23f`) is recorded in `MIGRATION-TABLE.md`'s "Deferred,
  not migrating" section, readable today via `git -C firestarter_app show <sha>:doc/PY32F071-FIRMWARE-INSTALL.md`.
- **Evidence:** `tools/wiki/MIGRATION-TABLE.md`.

**8. Four historical records were deliberately not repaired.**
- **Claim:** MIGRATE-04 requires no file in either sub-repo to link to a dead `doc/` path.
- **Non-claim:** Four files still do, by name, deliberately excluded rather than missed:
  | File | Why excluded |
  |---|---|
  | `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md` | Records a RED-baseline file listing — what was true when it was written. Repairing it falsifies a historical test record. |
  | `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md` | A scope statement about the deferred `PY32F071-FIRMWARE-INSTALL.md` being out of scope for its own, unrelated phase. |
  | `firestarter/tests/golden/eprom_params_citations.json` | Contains a sentence *about* `doc/PROTOCOLS.md` citing paths that did not resolve — repairing it destroys the evidence it exists to hold. |
  | `firestarter_app/tools/baseline/chip_database.baseline.json` | See entry 9. |
  This is the *only* surviving surface the strict repair-sweep grep finds (plus the meta repo's
  own by-design matches — `MIGRATION-TABLE.md`'s source-path column and a synthetic fixture
  string in `selftest.sh`, neither a dangling reference to a real deleted path).
- **Evidence:** `evidence/phase-gates.txt` GATE 2.

**9. The pinned diff baseline was deliberately not re-anchored.**
- **Claim:** `firestarter_app/tools/build_db.py`'s emitted reason string was repointed at the wiki
  and `chip_database.json` regenerated (D-14, MIGRATE-04).
- **Non-claim:** The historical baseline snapshot consumed by the diff-against-baseline
  regression gate, `tools/baseline/chip_database.baseline.json` (pinned Phase-98, `362bfa0`,
  2026-06-30), still carries 9 stale `firestarter/doc/AT28C04-ADAPTER.md` references and was
  deliberately left that way. Justification, measured: `tools/diff_db.py` returns `RC=0` against
  the mutated reason text (the gate is indifferent to it), no test asserts the literal path, and
  re-anchoring a frozen baseline has previously reddened unrelated legs elsewhere in this
  project's history.
- **Evidence:** `168-09-SUMMARY.md` "The `chip_database.baseline.json` Stale-Reference Decision".

**10. No publishing-integrity check exists any more, and nothing replaces it.**
- **Claim:** The wiki's content is guarded by HONEST-02 (truth) and `wiki.py links` (reachability),
  both scheduled.
- **Non-claim:** Neither one is a publishing-integrity check. Phase 167's WIKI-04
  (source-vs-published drift detection) was withdrawn at the model reversal — there is no longer
  an in-repo source tree for a wiki edit to drift *from*. A person with write access to
  `firestarter_prom.wiki.git` can edit any page directly, and nothing in this project's tooling
  distinguishes a good edit from a bad one except HONEST-02's narrow, three-region resolve check
  and the reachability check. This is not a gap this phase closes.
- **Evidence:** `168-RESEARCH.md` § "Retiring `tools/wiki/`"; ROADMAP.md Phase 168 criterion 5's
  own text ("Phase 167's publishing-integrity check (WIKI-04) is withdrawn").

**11. A wiki edit still needs no review — an accepted cost, not an oversight.**
- **Claim:** The wiki is now the single home for this content, with real checkers behind it.
- **Non-claim:** GitHub wikis have no pull-request mechanism; every edit lands on `master`
  immediately, reviewed only after the fact by whatever runs against the live clone on the next
  scheduled tick (weekly) or manual dispatch. Between an edit and the next check run, a false
  claim can be live and public. This is the same shape of exposure D-19 accepted when it chose
  "no tooling" for publishing, and it is restated here rather than left implicit.
- **Evidence:** `168-RESEARCH.md` § "Wiki Push and Clone Mechanics"; this plan's own
  `.github/workflows/wiki-check.yml` trigger (`schedule` + `workflow_dispatch`, no PR gate is
  possible on a wiki).

**12. D-08's "generated from DB vN" requirement is unsatisfiable as literally written.**
- **Claim:** ROADMAP criterion 5 requires "an explicit 'generated from DB vN, verified &lt;date&gt;'
  stamp."
- **Non-claim:** `chip_database.json` has no version field — there is no `vN` to name. The
  implemented substitute is a truncated sha256 content hash plus a verification date
  (`<!-- firestarter-claim-stamp: db-sha256-16=<16hex> verified=<YYYY-MM-DD> -->`), which is
  strictly *more* precise than a version number would have been (a hash changes on every content
  edit; a hand-incremented version number would not), but it is not literally what the roadmap
  text describes, and that gap is recorded here rather than glossed over.
- **Evidence:** `168-RESEARCH.md` D-08; `tools/wiki/honest02_truth.py`'s stamp regex.

## 2. The HONEST-01 live finding — the phase's strongest non-vacuity evidence

On its first real run against the live wiki (`master` `9d7e9bc`), `honest01_claims.py` did not
come back clean — it caught a genuine dropped claim token, not a designed test case. Plan
168-05's own bounded edit removing the unopenable `.planning/v1.7-SHIELD-REVS.md` reference from
`Shield-Revisions.md` incidentally pluralized "operator does not need these" into "operators do
not need it," dropping one `does not` occurrence while adding an unrelated `do not` occurrence —
a purely grammatical drift, but a real drop under the multiset's literal accounting. The response
was to fix the content, not loosen the check: the live wiki was corrected (`master` `9d7e9bc` →
`aa4a5c7`, restoring "the operator does not need these"), and the checker was re-run clean. This
is recorded here as a first-class result, not a footnote, because it is direct proof the gate is
not vacuous — it found something real, on real published content, before the source side ever
froze. See entry 2 above for what "frozen" now means going forward.

**Evidence:** `evidence/honest01-weakened-claim-RED.txt`, `evidence/honest01-live-GREEN.txt`,
`168-11-SUMMARY.md` "The HONEST-01 finding, as a first-class result".

## 3. Human visual verification of the live wiki pages — still outstanding

Two checkpoints in this phase (168-05, 168-08) pushed content live and captured every automated
proxy available (curl status codes, `wiki.py links` against a fresh clone, byte-for-byte diffs
against the pre-deletion source) — but neither substitutes for a human actually looking at the
rendered pages at `https://github.com/henols/firestarter_prom/wiki`. Both plans' own summaries
recorded this as outstanding rather than done, and it is restated here at phase close, not
silently dropped: tables render as tables, the hyphen-hazard titles (`AT28C04-Adapter`,
`SRAM-and-NVRAM-Behavior`) display correctly, no stamp/sentinel HTML comment is visible to a
reader, `Pinout-Safety-Review` and `SRAM-and-NVRAM-Behavior` read without needing to know what a
GSD phase is, and the sidebar appears and lists all 14 pages on every page. **This is not marked
done. It requires the operator to look.**

**Evidence:** `168-05-SUMMARY.md` "Next Phase Readiness"; `168-08-SUMMARY.md` "Next Phase Readiness".

## 4. Final selftest count

`bash tools/wiki/selftest.sh` → **`OK: selftest complete (11 cases)`**, all green, 0 failures, as
of this plan. (168-12's own action text and the earlier plan-authored artifact list both project
a smaller number — 9 — a stale-arithmetic pattern already documented in `168-11-SUMMARY.md` and
`168-12-SUMMARY.md` for the same reason: each plan's case count was projected before the next
plan's case was added. Eleven is the real, observed, final count.)

**Evidence:** `evidence/phase-gates.txt` § "Selftest driver — final count".

## 5. Every ROADMAP criterion, cross-referenced

See `evidence/phase-gates.txt` for the full command-and-result mapping of all eight Phase 168
success criteria; this ledger's twelve entries above are the non-claims that sit beside those
eight passing criteria, not a contradiction of them.

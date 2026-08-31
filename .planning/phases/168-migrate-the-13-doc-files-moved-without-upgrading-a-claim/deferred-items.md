# Phase 168 — Deferred Items

Out-of-scope discoveries logged during execution, not fixed per the executor's
scope-boundary discipline (fix only what the current task's changes directly
caused to break).

## Plan 168-04, Task 1 — two orphaned C++ fixture files

Deleting `firestarter_app/tests/test_dispatch_mirror.py` (its sole consumer)
leaves two committed fixture files unreferenced by any Python code in the
repository:

- `firestarter_app/tests/fixtures/planted_dispatch_missing_hex.cpp`
- `firestarter_app/tests/fixtures/planted_dispatch_comment_only_hex.cpp`

Both were SWEEP-07 planted-violation controls consumed exclusively by
`test_dispatch_mirror.py`'s `test_planted_missing_hex_is_detected` and
`test_planted_comment_only_hex_is_NOT_detected`. No test currently fails as a
result of their being orphaned (nothing scans `tests/fixtures/` for unused
files), so this is tidiness, not a defect: leaving them does not violate any
of plan 168-04's acceptance criteria, and 168-04's `files_modified` does not
name them.

Recommended follow-up: delete both files in whichever later 168 plan next
touches `tests/fixtures/` (e.g. a plan doing broader test-tree cleanup), or
in a dedicated hygiene pass after the phase closes.

## Plan 168-05, Task 2 — `wiki.py links` false-positives on `Lockable-PROMs.md`'s external reference-style links

`Lockable-PROMs.md` (migrated byte-for-byte from `lockable-proms.md` except for
the title insertion and stamp) carries 8 standard Markdown reference-style
citations to external datasheet URLs — `([Infineon][1])`, `([macronix.com][4])`,
`([Microchip][6])`, etc., each resolved by a `[N]: https://...` definition
further down the same file (lines 51, 106, 119, 130, 248, 273, 304; definitions
at 392–399). `wiki.py`'s `extract_internal_links` (`tools/wiki/wiki.py:69-90`)
treats **any** `[text][ref]` bracket pair as an attempted internal link — it has
no way to distinguish a reference-style external citation from a malformed
internal link attempt — so `check_link_forms` reports all 8 as
`illegal internal link form`, even though every one resolves to a real external
URL and none was ever intended as a wiki-internal link.

This is a pre-existing property of the source document surfaced for the first
time by migration (the checker never ran against this content before, since it
lived in the app repo, not the wiki). It was not introduced by this plan's
edits (title + stamp only), does not affect this plan's own acceptance criteria
(Task 2's `<verify>` only counts `orphan` occurrences; the top-level plan
`<verification>` only requires the `links` run to exit 1 with 12 orphan lines,
both satisfied regardless), and fixing it would mean rewriting the 8 citations
into inline-link form — content-shape editing beyond this plan's bounded edit
set (title / unopenable planning paths / stamp / the three named cross-file
links). Left as-is; not fixed here.

Recommended follow-up: whichever later plan owns the "clean" (post-Home-rewrite)
`wiki.py links` run against the live clone (168-13's workflow repoint, or a
dedicated hygiene pass) should either convert `Lockable-PROMs.md`'s 8
reference-style external citations to inline `[text](url)` form, or teach
`extract_internal_links` to recognize a `[N]: <url>` reference-definition block
and skip reference-style links whose `ref` resolves to one — whichever the
610-line `wiki.py` checker's owning plan judges cheaper.

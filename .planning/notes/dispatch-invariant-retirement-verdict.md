---
title: Dispatch invariant retirement verdict — the three-way dispatch invariant is RETIRED OUTRIGHT, no successor
date: 2026-09-11
context: v1.37 Phase 184, CLAIM-03 — measured in this session against live source (all three repos)
  and git history, plus the two orphaned `planted_dispatch_*.cpp` fixtures, read in full before
  `184-04` deletes them.
---

# Dispatch invariant retirement verdict (CLAIM-03)

## THE VERDICT

**The three-way dispatch invariant — dispatch table (`PROTOCOLS.md`), host tool
(`KNOWN_PROTOCOLS`), and firmware (`kAllProtocolFamilies`) all agreeing — is RETIRED
OUTRIGHT. No successor guard. No backlog item. A future need re-opens the question from
scratch.** This was the operator's own call, taken against the orchestrator's
recommendation, which was to retire the three-way and backlog the narrower two-way
`KNOWN_PROTOCOLS` ↔ `kAllProtocolFamilies` successor instead.

**Two limits on this verdict, stated before any detail.** First, the verdict rests on
what the three legs were measured to do — not on a claim that the underlying protocol
lists actually agree; the divergence table below is on the record as measured and
explicitly unjudged. Second, retirement is reversible in principle, but nothing will be
watching after this note is committed — re-opening depends on someone noticing unaided,
which is precisely the condition this milestone exists to correct. That is the operator's
own caveat, stated in the operator's terms, and it is not softened here into a
reassurance: nothing currently planned will surface this question again.

## THE GROUNDS

Three grounds, checked against source in this session before being written. The first
ground below **corrects** the framing carried in `184-CONTEXT.md` (D-08 item 1) — the
correction and the evidence for it are given in place, because the original framing does
not survive verification and this document is not permitted to carry a citation that
does not.

**(a) Nothing machine-reads `firestarter/PROTOCOLS.md` today, in any of the three
repositories — but not because the file lacks a claims-region delimiter.** It has one.
`184-CONTEXT.md`'s D-08 item 1 states the document leg "carries no claims-region
delimiter at all"; that is false, and this session's own read of `PROTOCOLS.md` finds it
false on inspection:

```
$ cd /workspaces/firestarter && /usr/bin/grep -n 'firestarter-claims-begin\|firestarter-claims-end' PROTOCOLS.md
53:<!-- firestarter-claims-begin -->
82:<!-- firestarter-claims-end -->
```

These markers have been in the file since it was first committed (`bbcdc39`, "docs: add
the firmware protocol and pinout references") — they did not arrive or leave with any
edit this phase makes. The now-deleted meta-repo checker
(`tools/wiki/dispatch_mirror.py`, deleted 2026-09-02 by `5426d7ef`) parsed exactly this
delimiter pair structurally, recoverable from git history even though no live checkout
carries the file:

```
$ git show 5426d7ef^:tools/wiki/dispatch_mirror.py | head -35
...
CLAIMS_BEGIN = "<!-- firestarter-claims-begin -->"
CLAIMS_END = "<!-- firestarter-claims-end -->"
...
def parse_claims_region(text: str) -> str | None:
    begin = text.find(CLAIMS_BEGIN)
    if begin == -1:
        return None
    ...
```

So the document leg was not unparseable, and the "keep its table shape intact"
instruction the old `PROTOCOLS.md` paragraph carried was real advice for a real (if
never-exercised) parser, not a warning about an empty gesture. What actually makes the
document leg bound nothing is narrower and more damning than "no marker exists": every
consumer of that marker is gone — the app repo's original `tests/test_dispatch_mirror.py`
(module-scope `fw_path("doc", "PROTOCOLS.md")`, deleted 2026-08-31 by `39ea3e8`) and its
meta-repo successor `tools/wiki/dispatch_mirror.py` (deleted 2026-09-02 by `5426d7ef`) —
and, per `5426d7ef`'s own commit message (quoted in full under Leg B below), the CI
workflow that would have run the meta-repo checker, `wiki-check.yml`, **had run ZERO
times** before its own retirement. A parser that exists in source but is wired to a
workflow that never once executed bounds nothing in practice, whether or not it carries a
delimiter. Confirmed today, across all three repositories:

```
$ /usr/bin/grep -rn 'firestarter-claims-begin\|firestarter-claims-end\|PROTOCOLS.md' \
    --include='*.py' --include='*.sh' --include='*.yml' /workspaces 2>/dev/null | /usr/bin/grep -v '/.planning/'
(no output — no live script in any of the three repositories references PROTOCOLS.md or its delimiter)
```

(The only hits inside `.planning/` are frozen `.v1.34-arms/` bench-rig control snapshots
from the closed v1.34 milestone — archived comparison artefacts, not live scripts, and
excluded from the count above.)

**(b) The firmware leg was fail-open by construction.** The deleted checker's firmware-leg
check extracted every `0x[0-9A-Fa-f]+` token from the whole file text of
`test/native/avr/test_dispatch/test_configure_memory.cpp` via a bare regex with no
comment-awareness:

```
$ git show 5426d7ef^:tools/wiki/dispatch_mirror.py | /usr/bin/grep -n '_FW_HEX_TOKEN_RE\|fw_hex_tokens ='
41:_FW_HEX_TOKEN_RE = re.compile(r"0x([0-9A-Fa-f]+)")
132:    fw_hex_tokens = {int(tok, 16) for tok in _FW_HEX_TOKEN_RE.findall(fw_text)}
```

So a comment-only mention of a protocol's hex identifier satisfied this leg exactly as
well as a real dispatch case would. The two orphaned `planted_dispatch_*.cpp` fixtures
prove this directly and are the subject of their own section below (D-08 item 3), because
that finding must survive their deletion in `184-04`.

**(c) Of the three legs, only the host leg — `KNOWN_PROTOCOLS`, a plain Python set
literal in `firestarter_app/tools/build_db.py` — was checked by native language semantics
rather than by regex-scraping raw file text.** The document leg required a markdown-table
regex parse (`_BUCKET_ROW_RE`/`_FAMILY_ROW_RE`, shown in Leg A below) and the firmware leg
required the comment-blind hex-token regex in ground (b); only the host leg was `import`ed
and read as an actual Python object (`set(dispatch_module.KNOWN_PROTOCOLS)`). That
asymmetry does not by itself retire the invariant — the document leg's structural parse
was real, when it ran — but combined with (a)'s "ran zero times" fact and (b)'s fail-open
firmware leg, the practical result is the same: nothing in this project's actual history
exercised a three-way check that would have caught a real divergence before it happened.

## THE EVIDENCE CHAIN

Two lettered legs, the two-deletion history that nobody intended.

**Leg A — `39ea3e8`, 2026-08-31, app repo, `fix(168-04): sever the module-scope fw_path
collection hazard`.** It deleted `tests/test_dispatch_mirror.py` because that module's
module-scope `fw_path("doc", "PROTOCOLS.md")` raised `MissingScanTargetError` and aborted
the WHOLE app suite at collection once `firestarter/doc/` was deleted — a collection-time
abort, not a test failure. In the same commit it deliberately re-pointed the surviving
`ScanPathEntry` at `tools/wiki/dispatch_mirror.py (meta repo; relocated by 168-10)`,
naming where the mirror-check logic had already moved by that point (Phase 168 Plan 10).

```
$ cd /workspaces/firestarter_app && git log -1 --format='%H %ad %s' --date=short 39ea3e8
39ea3e8f9819603a999f13027deaaddc1f459492 2026-08-31 fix(168-04): sever the module-scope fw_path collection hazard

$ git show 39ea3e8 --stat
 tests/scan_paths.py            |   6 +-
 tests/test_dispatch_mirror.py  | 366 -----------------------------------------
 tools/check_no_exists_proxy.py |   1 -
 3 files changed, 1 insertion(+), 372 deletions(-)

$ git show 39ea3e8 -- tests/scan_paths.py
--- a/tests/scan_paths.py
+++ b/tests/scan_paths.py
@@ -109,13 +109,9 @@ CROSS_REPO_TEST_PATHS: tuple[ScanPathEntry, ...] = (
             "test_sdp_table_parity.py",
         ),
     ),
-    ScanPathEntry(
-        "doc/PROTOCOLS.md",
-        ("test_dispatch_mirror.py",),
-    ),
     ScanPathEntry(
         "test/native/avr/test_dispatch/test_configure_memory.cpp",
-        ("test_dispatch_mirror.py",),
+        ("tools/wiki/dispatch_mirror.py (meta repo; relocated by 168-10)",),
     ),
```

**Leg B — `5426d7ef`, 2026-09-02, meta repo, `chore: retire wiki-check.yml and the
tools/wiki checkers`.** Two days later it retired every `tools/wiki/` checker,
demolishing the receiving end of a handoff that had just been written.

```
$ git log -1 --format='%H %ad %s' --date=short 5426d7ef
5426d7ef6b32cf83680ae056baa4e65d591a2ab6 2026-09-02 chore: retire wiki-check.yml and the tools/wiki checkers

$ git show 5426d7ef --stat | head -12
 .planning/CLOSE-RECORD.md               | ...
 .planning/REQUIREMENTS.md                | ...
 .planning/ROADMAP.md                     | ...
 .github/workflows/wiki-check.yml         | deleted
 tools/wiki/wiki.py                       | deleted
 tools/wiki/honest01_claims.py            | deleted
 tools/wiki/honest02_truth.py             | deleted
 tools/wiki/dispatch_mirror.py            | deleted
 tools/wiki/provenance_footers.py         | deleted
 tools/wiki/selftest.sh                   | deleted
 tools/wiki/claim-allowlist.json          | deleted
 tools/wiki/claim-vocabulary.json         | deleted
```

The commit's own message states the measured reason, quoted in full because it is the
strongest evidence in this whole record for "bounded nothing":

```
Measured 2026-09-02, and the reason:
  2,558 lines of checkers (selftest.sh alone 653)
  guarding 12 wiki pages, 28 commits old, one human author
  the Wiki check workflow had run ZERO times
  HONEST-02's leg 2 resolved claims on exactly 1 page of 12
  honest01_claims.py, 308 lines, was invoked by nothing
  dispatch_mirror.py never read the wiki, despite its leg's message
```

**Neither commit intended to retire the invariant.** Each was a correct local fix — sever
a collection-time abort, retire disproportionate machinery that had never run — and the
invariant died in the eleven-day gap between them, unnoticed until this phase's own CLAIM-01/CLAIM-02 sweep found it.

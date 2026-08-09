# Phase 139 — Citation Register

**Owner requirement:** ISSUE-01 (every C1/C2/C3 claim citable by `file:line` or commit SHA) and
ISSUE-02 (the 6.25 V program-VCC ceiling statement and the acceptance-criteria amendment it requires)
— this register supplies the evidence floor both requirements stand on.

**Measured:** 2026-08-09, this session, live and read-only.

Per the plan's own instruction, nothing below is copied from `139-RESEARCH.md` — every command in
this register was re-run fresh this session, and any divergence from research's recorded figures is
stated explicitly rather than reconciled by editing `139-CONTEXT.md` or `139-RESEARCH.md`. In practice
every figure below matched RESEARCH's recorded value exactly, with one unit-precision clarification
noted in §0 and one strengthening noted in §2 (minipro's GitLab citations, unreachable in RESEARCH's
own session, resolved live in this one).

---

## 0. gh#15 before-state

| Field | Command (as run) | Result |
|---|---|---|
| state | `gh issue view 15 --repo henols/firestarter_prom --json state -q .state` | `OPEN` |
| comment count | `gh issue view 15 --repo henols/firestarter_prom --json comments -q '.comments \| length'` | `0` |
| labels | `gh issue view 15 --repo henols/firestarter_prom --json labels -q .labels` | `[]` |
| updatedAt | `gh issue view 15 --repo henols/firestarter_prom --json updatedAt -q .updatedAt` | `2026-07-12T09:15:27Z` |
| createdAt | `gh issue view 15 --repo henols/firestarter_prom --json createdAt -q .createdAt` | `2026-07-12T09:15:27Z` |
| body byte length | `gh issue view 15 --repo henols/firestarter_prom --json body -q .body \| wc -c` | `5964` bytes |

All six fields match `139-RESEARCH.md` §"gh#15 Live State" exactly — no divergence.
`updatedAt == createdAt` still holds: the body has not been edited at any point between research and
this plan's execution. This measurement is also independent of Task 1's own before-count check earlier
in this same plan (which asserted comment count `0` via a separate, differently-shaped query) — both
land on `0`, a second free corroboration.

**One measurement precision note, not a divergence.** `gh issue view ... --json body -q .body | wc -c`
gives **5964** (raw byte count — matches RESEARCH exactly and is the figure recorded above). Piping the
same body through `jq`'s `.body | length` directly gives **5950** — that function counts Unicode
*codepoints*, not bytes, and the body contains multi-byte UTF-8 characters (`µ` in "500 µs" etc., each
1 codepoint but 2 bytes). `wc -c` is the correct byte-length oracle and the one used above and by
RESEARCH; the 14-byte gap is arithmetic, not a body change.

---

## 1. Pinning strategy

Citations pin to commit SHAs, never branch names (D-07).

| Repo | Pin SHA (re-derived this session) | Command (as run) |
|---|---|---|
| `henols/firestarter_prom` (meta) | `b6aa1dcb23ef9931105752ed6dd6badccf6719de` — pushed tip of this milestone branch | `git ls-remote --heads origin \| grep v1.31` |
| `henols/firestarter` (fw) | `6fab4eafdcd0981d24fddc3ff177abc5c74e313c` (`origin/beta`) | `git -C /workspaces/firestarter rev-parse origin/beta` |
| `henols/firestarter_app` (host) | `4d18b645ab18a2d2465f0f623062e9249eb24132` (`origin/beta` **and** branch tip — same commit) | `git -C /workspaces/firestarter_app rev-parse origin/beta` and `git -C /workspaces/firestarter_app rev-parse HEAD` |

All three re-derived fresh this session; all three match `139-RESEARCH.md`'s recorded values exactly —
no divergence. (Firmware branch tip, for reference, is `fb7949c0bdd575177262a76af506cec3b73ea28b` — not
used as a pin, since `origin/beta` is what a stranger reads, but confirmed reachable, see below.)

**Blob identity, re-confirmed, not assumed** — the two firmware anchor files are byte-identical at
`HEAD` (`fb7949c0`) and `origin/beta` (`6fab4eaf`):

```
$ for r in HEAD origin/beta; do git -C /workspaces/firestarter rev-parse $r:src/proms/eprom.cpp; done
8dfa4cced460416fc1b0f73cf3f0e6f77965f962
8dfa4cced460416fc1b0f73cf3f0e6f77965f962
$ for r in HEAD origin/beta; do git -C /workspaces/firestarter rev-parse $r:src/proms/memory.cpp; done
478fa1d35fed2abbefb27d4d2c54dcec02086687
478fa1d35fed2abbefb27d4d2c54dcec02086687
```

The host repo's `HEAD` and `origin/beta` are the *same commit* (`4d18b645`), so every cited host file
(`infoic-field-dictionary.md`, `database.py`) is trivially identical between them — no separate check
needed.

**Visibility, measured this session:**

```
$ gh repo view henols/firestarter_prom --json visibility -q .visibility   → PUBLIC
$ gh repo view henols/firestarter        --json visibility -q .visibility  → PUBLIC
$ gh repo view henols/firestarter_app    --json visibility -q .visibility  → PUBLIC
```

All three repos PUBLIC — no citation into any of them requires special access, and planning artifacts
in the meta repo are legitimately citable by a stranger.

### Two deliberate divergences from `139-CONTEXT.md` §canonical_refs

**`138-BASELINE.md` is DROPPED from the citation set.** Re-confirmed this session:

```
$ curl -s -o /dev/null -w "%{http_code}\n" \
  https://raw.githubusercontent.com/henols/firestarter_prom/b6aa1dcb23ef9931105752ed6dd6badccf6719de/.planning/phases/138-preconditions-baseline/138-BASELINE.md
404
```

It 404s at the pushed tip (it landed in the unpushed `baa131a3`), it appears **nowhere** in D-06's
binding citation list — only in `139-CONTEXT.md`'s looser §canonical_refs "Evidence being cited" list
— and everything it would prove is already inside `138-02-PULSE-DISTRIBUTION.md`, which resolves (see
anchor 8 below). Dropping it means this phase needs **no `git push`** at all: the phase's only outward
act stays the post itself (owned by plan 139-05), matching D-08's shape exactly.

**`.planning/PROJECT.md` is NOT cited publicly.** Its C1/C2/C3 table sits at different line numbers
depending on which ref is read — re-confirmed this session, not assumed from RESEARCH:

```
$ grep -n '\*\*C1\*\*' /workspaces/.planning/PROJECT.md
71:| **C1** | ...
$ curl -s https://raw.githubusercontent.com/henols/firestarter_prom/b6aa1dcb23ef9931105752ed6dd6badccf6719de/.planning/PROJECT.md \
    | grep -n '\*\*C1\*\*'
61:| **C1** | ...
```

Line 71 locally, line 61 at the pushed tip — a ten-line shift. A permalink written from local line
numbers would return HTTP 200 and point at the wrong ten lines (exactly Pitfall 2's failure mode).
`PROJECT.md` is the *source* of the comment's substance — the design it renders for a public reader —
not one of its citations, and D-06's binding citation list never names it.

---

## 2. Anchor verification table

Every anchor is verified by CONTENT: fetch the raw file at the pinned SHA, slice to the pinned line
range with `awk`, `grep -qF` for an expected substring. An HTTP 200 alone is never recorded as
verification. All nine raw-file anchors below were run through the identical `verify_anchor` shell
function reproduced verbatim from `139-RESEARCH.md` §"Code Examples":

```bash
verify_anchor() {  # $1=raw-url  $2=first  $3=last  $4=expected substring
  local out; out=$(curl -sf "$1") || { echo "FAIL(fetch) $1"; return 1; }
  printf '%s\n' "$out" | awk -v a="$2" -v b="$3" 'NR>=a && NR<=b' | grep -qF -- "$4" \
    && echo "OK   $1#L$2-L$3" || { echo "FAIL(anchor) $1#L$2-L$3"; return 1; }
}
```

**Transcript, this session, all nine raw anchors.** The first seven lines are the plan's own literal
`<verify><automated>` block, run verbatim, exiting `OK-T2-ANCHORS`. That literal block's argv list
covers seven of the nine anchors named in this task's `<action>` text; the remaining two — the
erase-pulse anchor and the pulse-distribution script — were run immediately after through the *same*
function, with the same fail-closed discipline, so all nine carry an independent `OK` line:

```
OK   https://raw.githubusercontent.com/henols/firestarter_app/4d18b645ab18a2d2465f0f623062e9249eb24132/doc/infoic-field-dictionary.md#L210-L217
OK   https://raw.githubusercontent.com/henols/firestarter_app/4d18b645ab18a2d2465f0f623062e9249eb24132/firestarter/database.py#L128-L128
OK   https://raw.githubusercontent.com/henols/firestarter/6fab4eafdcd0981d24fddc3ff177abc5c74e313c/src/proms/eprom.cpp#L20-L20
OK   https://raw.githubusercontent.com/henols/firestarter/6fab4eafdcd0981d24fddc3ff177abc5c74e313c/src/proms/eprom.cpp#L69-L77
OK   https://raw.githubusercontent.com/henols/firestarter/6fab4eafdcd0981d24fddc3ff177abc5c74e313c/src/proms/eprom.cpp#L177-L177
OK   https://raw.githubusercontent.com/henols/firestarter/6fab4eafdcd0981d24fddc3ff177abc5c74e313c/src/proms/memory.cpp#L249-L258
OK   https://raw.githubusercontent.com/henols/firestarter_prom/b6aa1dcb23ef9931105752ed6dd6badccf6719de/.planning/phases/138-preconditions-baseline/138-02-PULSE-DISTRIBUTION.md#L237-L249
OK-T2-ANCHORS
OK   https://raw.githubusercontent.com/henols/firestarter/6fab4eafdcd0981d24fddc3ff177abc5c74e313c/src/proms/eprom.cpp#L274-L283
OK   https://raw.githubusercontent.com/henols/firestarter_prom/b6aa1dcb23ef9931105752ed6dd6badccf6719de/.planning/phases/138-preconditions-baseline/138-pulse-distribution.py#L120-L120
```

Nine `OK` lines, zero `FAIL` lines. Per-anchor detail follows, four columns each: numbered anchor · the
literal command as run · the sliced text actually returned · the enclosing function or section.

| # | Anchor | Command (as run) | Sliced text actually returned | Enclosing function / section |
|---|---|---|---|---|
| 1 | `firestarter_app/doc/infoic-field-dictionary.md:210-217` | `verify_anchor "$APP/doc/infoic-field-dictionary.md" 210 217 '50000 µs (×100 wrong)'` | Table row: `AM2716 \| 0x0B \| 0x1F4 \| 500 µs \| 50000 µs (×100 wrong)`.<br>L217: "**BUG-2 (DEC-03):** Correct is: raw `pulse_delay` value = microseconds for ALL protocols; current `build_db.py` `interpret_timing()` applies `val * 100` for `protocol_id` `0x07` and `0x0B` (`database.c#L866`) — this ×100 multiplier is wrong; 252 chips across those two protocols currently have inflated `pulse_duration` values in `chip_database.json`; fix deferred to Phase 57." | The raw-hex→µs adjudication table inside `doc/infoic-field-dictionary.md` (a markdown reference table, not a function) — **C1's adjudication**. |
| 2 | `firestarter_app/firestarter/database.py:128` | `verify_anchor "$APP/firestarter/database.py" 128 128 'def _parse_pulse_duration'` | `def _parse_pulse_duration(pulse_str: str) -> int:` — docstring: "Parse a pulse_duration string from chip_database.json into microseconds. Accepts values like \"100 us\", \"1000 us\", \"Algorithm Controlled\", or \"\". Returns the integer microsecond value, or 0 for unknown / algorithm-controlled." | The function itself, `_parse_pulse_duration()` — the `pulse_duration` string → `pulse_delay` int-µs layer (Phase 138 D-11: imported, never reimplemented). |
| 3 | `firestarter/src/proms/eprom.cpp:20` | `verify_anchor "$FW/src/proms/eprom.cpp" 20 20 '#define NUMBER_OF_RETRIES 20'` | `#define NUMBER_OF_RETRIES 20` | Top-level file-scope macro (before any function). Used as the divisor in the adaptive-growth formula (anchor 5) and as the retry-loop bound inside `eprom_write_execute()`. |
| 4 | `firestarter/src/proms/eprom.cpp:69-77` | `verify_anchor "$FW/src/proms/eprom.cpp" 69 77 'case 0x0B: handle->pulse_delay = 500;'` | `if (handle->pulse_delay == 0) { switch (handle->protocol) {`<br>`case 0x08: handle->pulse_delay = 100;  break;  // EPROM_QUICK: 100µs`<br>`case 0x0B: handle->pulse_delay = 500;  break;  // EPROM_LEGACY: 500µs`<br>`default:   handle->pulse_delay = 1000; break;  // EPROM_STD: 1ms } }` | `configure_eprom()`, opens at eprom.cpp:41. This range shows the firmware **already** defaults `0x0B` to 500 µs — independent corroboration of C1 straight out of the code gh#15 asks to change. |
| 5 | `firestarter/src/proms/eprom.cpp:177` | `verify_anchor "$FW/src/proms/eprom.cpp" 177 177 'org_delay * retries / NUMBER_OF_RETRIES'` | `handle->pulse_delay = org_delay + (org_delay * retries / NUMBER_OF_RETRIES);` | `eprom_write_execute()`, opens at eprom.cpp:143 — the adaptive pulse-growth formula, inside the block-mismatch retry loop gh#15 asks to remove. |
| 6 | **`firestarter/src/proms/memory.cpp:249-258`** ← corrected C3 anchor | `verify_anchor "$FW/src/proms/memory.cpp" 249 258 'delayMicroseconds(handle->pulse_delay);'` | `rurp_chip_enable();`<br>`delayMicroseconds(handle->pulse_delay);`<br>`rurp_chip_disable();` (lines 256-258, inside the fetched 249-258 range) | **`memory_set_data()`** — this is **the PROGRAM pulse**. `memory.cpp:86` binds `firestarter_set_data` to `memory_set_data`; `eprom.cpp`'s `program_mismatched_bytes()` (lines 114-126) has no delay of its own — the per-byte program pulse happens inside this function via the function pointer. |
| 7 | `firestarter/src/proms/eprom.cpp:274-283` — kept, relabelled | `verify_anchor "$FW/src/proms/eprom.cpp" 274 283 'delayMicroseconds(handle->pulse_delay);'` | `void eprom_internal_erase(firestarter_handle_t* handle) {`<br>`... rurp_chip_input(); ... delay(100); ... firestarter_set_address(handle, 0x0000); ...`<br>`rurp_chip_enable();`<br>`delayMicroseconds(handle->pulse_delay);` | **`eprom_internal_erase()`**, opens exactly at line 274 — this is **the ERASE pulse**, the only other `delayMicroseconds()` call in `eprom.cpp`. **Correction recorded here:** `139-CONTEXT.md` D-06 lists `eprom.cpp:283` as C3's "the pulse" anchor with no qualifier — that citation resolves but is checkably the erase pulse, not the program pulse, and a reader following it would land in the wrong function. Anchor 6 above (`memory.cpp:249-258`) is the corrected program-pulse citation; this row is kept and explicitly relabelled rather than dropped, because `handle->pulse_delay` doing double duty as both program and erase pulse is itself a real design observation worth citing. |
| 8 | `.planning/phases/138-preconditions-baseline/138-02-PULSE-DISTRIBUTION.md:237-249` | `verify_anchor "$META/.../138-02-PULSE-DISTRIBUTION.md" 237 249 'n = 170'` | Three histogram lines: `0x07: n = 170, histogram 100 us ×113, 200×27, 1000×22, 500×4, 50×4` · `0x08: n = 127, histogram 100 us ×104, 50×11, 10×7, 200×2, 1000×2, 20×1` · `0x0B: n = 32, histogram 500 us ×21, 1000×6, 200×5` — each line's own text states "zero divergence" against both the seed and `138-RESEARCH.md`. | §"the live pulse-width distribution" measurement section. `n = 170`, `n = 127` and `n = 32` **all three** confirmed inside the fetched 237-249 slice by direct inspection — the plan's "separately confirm" instruction is satisfied by the same fetch, no second request needed. |
| 9 | `.planning/phases/138-preconditions-baseline/138-pulse-distribution.py` | existence: `curl -sf -o /dev/null -w "%{http_code}" "$META/.../138-pulse-distribution.py"` → `200`; content: `verify_anchor "$META/.../138-pulse-distribution.py" 120 120 'from firestarter.database import _parse_pulse_duration'` | `from firestarter.database import _parse_pulse_duration  # noqa: E402 -- the production parser, D-11, never reimplemented` | Import section of the runnable script. Confirms the script imports Phase 138's own D-11 rule (never reimplement the parser) rather than re-deriving pulse-duration parsing — the "runnable, a stranger can re-run" property C2 depends on. |

### Commit-level citations (C1)

| # | Citation | Command (as run) | Result |
|---|---|---|---|
| 10 | commit `8de307f` (`firestarter_app`) | `gh api repos/henols/firestarter_app/commits/8de307f278370c07bfd3328aa9020248e66d0649 --jq '.sha[0:7] + " \| " + (.commit.message \| split("\n")[0])'` | `8de307f \| feat(57-01): remove interpret_timing x100 multiplier and fix bare excepts (DEC-03)` — full SHA `8de307f278370c07bfd3328aa9020248e66d0649` |
| | reachability | `git -C /workspaces/firestarter_app branch -r --contains 8de307f278370c07bfd3328aa9020248e66d0649` | Lists 12 remote branches including **`origin/beta`** and `origin/gsd/v1.31-27c-programming-algorithm-fidelity` |
| 11 | commit `12286df` (`firestarter_app`) | `gh api repos/henols/firestarter_app/commits/12286df86abaf02be1d8e719818b7ca76a4c00e9 --jq '.sha[0:7] + " \| " + (.commit.message \| split("\n")[0])'` | `12286df \| feat(57-03): regenerate chip_database.json from corrected build_db.py` — full SHA `12286df86abaf02be1d8e719818b7ca76a4c00e9` |
| | reachability | `git -C /workspaces/firestarter_app branch -r --contains 12286df86abaf02be1d8e719818b7ca76a4c00e9` | Lists the identical 12-branch set including **`origin/beta`** |

Both commit subjects match `139-RESEARCH.md`'s D-06/citation-register expectations exactly. Both are
reachable from `origin/beta` — the ×100 BUG-2 fingerprint is cited by commit, not by assertion.

### minipro — GitLab, not GitHub

Upstream is `https://gitlab.com/DavidGriffith/minipro`, pinned at
`cae74c0607077d6260b24995f5e4c0d0b66a6a2e`. **gitlab.com was reachable from this session** (confirmed
`curl -sf` returned HTTP 200) — this is a live, executed re-verification, not the `[CITED, not
re-verified this session]` fallback the plan's `<action>` text authorizes for the case where GitLab is
unreachable. RESEARCH's own session found minipro "not local" (present only in a different, now-gone
scratchpad) and could not re-verify against the live GitLab remote; this session could, and did.

| # | Anchor | Command (as run) | Sliced text actually returned | Enclosing function / section |
|---|---|---|---|---|
| 12 | `src/t48.c:246` | `curl -sf "$MP/src/t48.c" \| awk 'NR==246'` | `int t48_begin_transaction(minipro_handle_t *handle)` | Function signature — `t48_begin_transaction()` itself opens here. |
| 13 | `src/t48.c:255` | `curl -sf "$MP/src/t48.c" \| awk 'NR==255'` | `msg[1] = device->protocol_id;` | Inside `t48_begin_transaction()` — `protocol_id` packed into the `BEGIN_TRANS` wire message. |
| 14 | `src/t48.c:266-267` | `curl -sf "$MP/src/t48.c" \| awk 'NR>=266 && NR<=267'` | `format_int(&(msg[12]), device->pulse_delay, 2,`<br>`format_int(..., MP_LITTLE_ENDIAN);` | Inside `t48_begin_transaction()` — `pulse_delay` packed into the same message, as a **sibling, orthogonal** field to `protocol_id` (anchor 13). This is the "two orthogonal wire fields" claim's whole evidentiary basis. |
| 15 | `src/main.c:698` | `curl -sf "$MP/src/main.c" \| awk 'NR==698'` | `"Default write pulse: %u us\nAvailable write pulse[us]: 1-65535\n",` | The CLI help-string table for the `-o pulse=N` option — the source of the **65535 µs ceiling** claim, corroborating the 2-byte (`format_int(..., 2, ...)`) wire width used at anchor 14. |

**Scope note:** RESEARCH additionally cross-checked four sibling files (`tl866a.c:257`,
`tl866iiplus.c:238`, `t56.c:193`, `t76.c:529`) for the identical `format_int(..., pulse_delay, 2, ...)`
pattern. This task's `<action>` text names only `t48.c` and `main.c` as the anchors to verify for this
register; the four siblings are not re-verified here and are cited by reference to RESEARCH's own
resolution, not re-derived — no claim in this register depends on them.

---

## 3. D-10 baseline — the correction precedes implementation

The "before implementation" claim is recorded as **three-ref blob equality**, not a `git status`
inference, for both `eprom.cpp` and `memory.cpp`.

```
$ for r in HEAD origin/beta 3085084; do git -C /workspaces/firestarter rev-parse $r:src/proms/eprom.cpp; done
8dfa4cced460416fc1b0f73cf3f0e6f77965f962
8dfa4cced460416fc1b0f73cf3f0e6f77965f962
8dfa4cced460416fc1b0f73cf3f0e6f77965f962
$ for r in HEAD origin/beta 3085084; do git -C /workspaces/firestarter rev-parse $r:src/proms/eprom.cpp; done | sort -u | wc -l
1
```

```
$ for r in HEAD origin/beta 3085084; do git -C /workspaces/firestarter rev-parse $r:src/proms/memory.cpp; done
478fa1d35fed2abbefb27d4d2c54dcec02086687
478fa1d35fed2abbefb27d4d2c54dcec02086687
478fa1d35fed2abbefb27d4d2c54dcec02086687
$ for r in HEAD origin/beta 3085084; do git -C /workspaces/firestarter rev-parse $r:src/proms/memory.cpp; done | sort -u | wc -l
1
```

Both files: **exactly one** unique blob SHA across `HEAD`, `origin/beta`, and `3085084` (the Phase 138
frozen firmware base named in `PROJECT.md`). `3085084` is confirmed an ancestor of `HEAD`:

```
$ git -C /workspaces/firestarter merge-base --is-ancestor 3085084 HEAD && echo "3085084 IS an ancestor of HEAD"
3085084 IS an ancestor of HEAD
```

`eprom.cpp` = `8dfa4cced460416fc1b0f73cf3f0e6f77965f962` at all three refs — exactly matching
`139-RESEARCH.md` F-09's recorded value; no divergence. `memory.cpp` = `478fa1d35fed2abbefb27d4d2c54dcec02086687`
at all three refs — RESEARCH's own F-09 measured only `HEAD` and `origin/beta` for `memory.cpp` and
suggested extending the check to `3085084` ("Consider extending the same three-ref blob check to
`memory.cpp`"); this plan carried out that suggestion, and `3085084` agrees with the other two refs.

**Why the meta repo's ` M firestarter` line is a stale gitlink pointer, not an edit.** The meta repo's
own tree records:

```
$ git ls-tree HEAD firestarter firestarter_app
160000 commit 0933bd7d602efb30e4a666e8231ecf724e90ab09	firestarter
160000 commit cc036e8dc3cd77bbdfc7ec5190d79cdb172153c7	firestarter_app
```

...while the actual checkouts are `fb7949c0bdd575177262a76af506cec3b73ea28b` (firestarter) and
`4d18b645ab18a2d2465f0f623062e9249eb24132` (firestarter_app). `git status` reports ` M firestarter` /
` M firestarter_app` purely because the meta repo's *tracked gitlink SHA* is behind the *checked-out*
commit in each submodule — a bookkeeping drift in what the meta repo points at, not a source edit
inside either submodule's working tree. Neither `eprom.cpp` nor `memory.cpp` is touched by this drift;
the three-ref blob-equality check above is what actually proves "untouched," and it is immune to this
drift by construction, since it reads each submodule's own commit history directly rather than
trusting the meta repo's gitlink pointer.

**`git submodule status` is never used in this phase's verification, by design.** It fails
unconditionally in this repo, for a reason unrelated to either submodule cited here:

```
$ git submodule status
fatal: no submodule mapping found in .gitmodules for path '.planning/v1.7/upstream-rurp'
```

This is a pre-existing `.gitmodules` mapping gap on an unrelated path
(`.planning/v1.7/upstream-rurp`); any script using this command as a blanket precondition check would
exit non-zero for a reason that has nothing to do with the D-10 claim it was meant to verify. This
register uses the three-ref blob-equality form exclusively.

---

*Phase: 139-gh-15-correction-outward*
*Plan: 139-01*
*Pinned SHAs this register cites against — meta `b6aa1dcb23ef9931105752ed6dd6badccf6719de` ·
firmware (`origin/beta`) `6fab4eafdcd0981d24fddc3ff177abc5c74e313c` · host (`origin/beta`)
`4d18b645ab18a2d2465f0f623062e9249eb24132` · minipro (GitLab) `cae74c0607077d6260b24995f5e4c0d0b66a6a2e`.*

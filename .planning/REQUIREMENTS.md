# Requirements — Milestone v1.33: Source Hygiene & Firmware Size Reduction

**Status:** **ACTIVE — activated 2026-08-22** by `/gsd-new-milestone`. Scoped 2026-08-22 by `/gsd-explore` routing after the v1.32 close (`REQUIREMENTS.md` was `git rm`'d at that close, per `.planning/milestones/v1.32-*`). **Hand-authored and pointed at, never regenerated** — the GSD requirements verbs normalise the whole file and would reformat all 31 requirements. Activation added this line and the Traceability table below — the file carried no Traceability section, though the phase mapping was already unambiguous from each category heading, so the table records that mapping rather than deciding it. Research was skipped at activation: these requirements derive from measured `uno` / `uno328pb` / `leonardo` builds, not from a domain survey.

**Milestone goal (verbatim from ROADMAP.md):** Make the source shorter without changing what it does. Two halves. First, promoted Backlog **999.34**: sweep the ~646 GSD provenance comments that ~150 phases stamped into shipped source across 167 files, condensing the minority that carry real rationale, and repair the 6,939 `.planning/` `file:LINE` citations that shift as a result. Second, four **measured** firmware size reductions worth **−2938 B flash / −13 B RAM** on all three AVR targets for a **net −2 lines of source**. Six phases, 154–159.

**Evidence base — read before planning any of Phases 155–158:** [`.planning/notes/firmware-size-reduction-survey.md`](notes/firmware-size-reduction-survey.md), plus the applyable [`firmware-size-reduction-measured.patch`](notes/firmware-size-reduction-measured.patch). Phases 155–158 are **review, decomposition and landing** phases — the work is already implemented on firmware branch `size-reduction-survey` (forked off `8695ee5`) and validated at 172/172 native across seven runs.

---

## 1. Provenance Comment Sweep (SWEEP) — Phase 154, promoted Backlog 999.34

**Requirements SETTLED 2026-08-23 at `/gsd-discuss-phase 154`.** They were deliberately UNSET at activation because the triage policy — which of the ~646 comments are deleted outright, which are condensed into ordinary comments, and what "load-bearing rationale" means operationally — is the substance of this phase and had to be fixed against measurement rather than guessed here. The 13 requirements below are the resolution of the `SWEEP-01…NN` placeholder, transcribed from [`phases/154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo/154-CONTEXT.md`](phases/154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo/154-CONTEXT.md) §`<requirements>`, where each carries the measurement or precedent that settled it (D-01…D-12). The full writeup is [`todos/pending/2026-08-22-sweep-gsd-provenance-comments-from-firmware-and-host-source.md`](todos/pending/2026-08-22-sweep-gsd-provenance-comments-from-firmware-and-host-source.md); Backlog 999.34's roadmap entry is the handle only. Three of the writeup's figures are corrected by the discuss-step re-survey: the gate count (~20 → **8** paths, D-05), the corpus split (52% is test files, not shipped source, D-04), and `CAP-0` being a survey false positive (D-02).

- [ ] **SWEEP-01**: The triage runs as D-01's single mechanical procedure — strip the provenance token(s) and enclosing punctuation, then judge what remains (sentence describing code that exists → keep, reflowed; connective punctuation only → delete; sentence describing code that is NOT there → delete) — stated in the plan and applied per hit, with the step-3 guard named: never delete the only statement of a non-obvious invariant, trap, or fail-closed rationale. All five keep-examples the writeup names (`eprom_params.cpp:61`, `uno_rurp_shield.cpp:109`, `database.py:580-630`, `flash_5v_page.cpp:101`, `json_parser.c:92`) are shown to land on "keep, reflowed".
- [x] **SWEEP-02**: `CAP-0N` is exempt as live cross-repo wire-protocol vocabulary (shipped host source: `serial_comm.py:67-156`, `hardware.py:39,153`, `firmware.py:180`; 13 host test modules reference it), and the generalised both-repos exemption test is applied to every token not on D-01's list. `firestarter/src/firestarter.cpp:182-200` is untouched, and `test_cap03_ack_layout_parity.py` is green **and** shown still able to fail. **Discharged 2026-08-23 by plan 154-07**: `grep -c 'CAP-0'` is **6 / 1** in `src/firestarter.cpp` / `include/firestarter.h` before **and** after the sweep, so the exemption held everywhere, not only inside the no-touch region. The no-touch region is proven untouched by **content search** rather than line range — necessary, because the sweep shifted it by −5: the pre-sweep 182-200 text (sha256 `233ecb44…d97c9`) is present VERBATIM at its new line 177, and `git diff -U0 -- src/firestarter.cpp | grep -c 'buffer_size u16 BE'` is **0**, so the pinned string appears on no added or removed line. `test_cap03_ack_layout_parity.py` runs **12/12** against a clean clone carrying the swept blobs committed — *including* both planted legs, which are themselves the still-able-to-fail proof; against the D-11-mandated dirty tree it is 10/2 with both failures verbatim `the firmware repo's working tree is no longer clean after the planted-copy test`. **Boundary correction recorded:** the contiguous comment block runs 182–232, not 182–200, so the whole block was left alone and one mid-comment `(D-09)` at old line 209 is a deliberate named residual rather than a surgical edit beside a gate fixture. **Standing obligation this tick carries:** plans 154-09…154-11 sweep host source where `CAP-0N` lives and must retain it — a restatement of the now-recorded rule, not an undischarged half.
- [ ] **SWEEP-03**: Requirement/decision IDs are stripped from shipped source and **retained** in test files where the ID is the case's traceability key. The rule is stated so the asymmetry does not read as an inconsistency.
- [x] **SWEEP-04**: Test files receive the **narrow** treatment only — tombstone deletion and label-only-comment deletion, no reflowing of substantive test commentary. The 331-of-636 measurement (`firestarter/test/native` 216, `firestarter_app/tests` 115) and the fact that **no oracle covers any of them** are both recorded.
- [ ] **SWEEP-05**: The `uno` build is byte-identical before and after, stated as a **measured pair of numbers**, not asserted. Any delta is reverted, not explained.
- [x] **SWEEP-06**: All 8 paths in `firestarter_app/tests/scan_paths.py::ALL_CROSS_REPO_PATHS` are classified and disposed of per D-05's table. The two generated headers (`sdp_bus_config.h`, `validation_matrix.h`) are fixed at their generators or shown to need no fix; their output is never edited.
- [ ] **SWEEP-07**: `test_sdp_table_parity.py` and `test_dispatch_mirror.py`'s C++ leg each get a planted-violation control proving they go **RED before** the sweep and **RED again after**. The live `_PAIR_RE` collision at `eeprom_28c.cpp:199-201` and the comment-blind brace slice at `test_sdp_table_parity.py:141-158` are both named as the reason.
- [x] **SWEEP-08**: `eeprom_28c.cpp` is swept as its own plan, not batched — 33 hits, both comment-blind gate mechanisms, and the AT28C datasheet citation of record (Atmel doc0270 rev 0270L-PEEPR-2/09 §19 note 2, corroborated by Microchip DS20006432B §6.18 note 2) all land in one file.
- [x] **SWEEP-09**: The pre-sweep citation manifest is committed at `.planning/v1.33/sweep-citation-manifest.jsonl`, covering all **10,054** citations that target a swept file (not only the 6,939 predicted to shift), with both endpoints and both source texts for every range citation. **Discharged 2026-08-23 by plan 154-04**: 13,692 records over 2,947 planning documents and a 171-file candidate set; **10,445** records (10,169 occurrence-equivalent) target a candidate swept file and **7,249** (7,076) are shifting. Per Ruling G the recorded 10,054 is **not** rewritten and the produced count is **not** quietly asserted in its place — both stand, reconciled at +115 (+1.1%) with the cause measured, in [`sweep-citation-manifest-report.md`](v1.33/sweep-citation-manifest-report.md). Every range record carries `target_line_end` **and** `source_text_end`, asserted by the generator's own serialize-then-scan self-check and re-asserted over the written artifact; all 10,190 readable rows verified byte-for-byte against the on-disk source, 0 mismatch.
- [ ] **SWEEP-10**: Citations targeting a comment line the sweep deletes are recorded `retarget: true` with the original cited text preserved and a hand-chosen new target. None is silently dropped, and the subset's **count is reported** — it is a deliverable, not a prediction. **HALF discharged 2026-08-23 by plan 154-04, deliberately left unticked.** The pre-sweep half is done: every one of the 13,692 records exists with a `resolution` and `retarget: false`, so nothing is silently dropped and the field is present to be flipped rather than added (a schema change to a committed 7 MB pre-sweep artifact is the risk that removes). The retarget subset **cannot exist until the sweep's diff exists**; plan **154-12** settles it against the real diff and reports its count — D-08's only manual work in the whole repair.
- [x] **SWEEP-11**: `remap_citations.py` + `test_remap_citations.py` are committed under `.planning/v1.33/tools/`, proven **idempotent** (run twice = no-op) and proven to **shrink** a range spanning a deleted block rather than translate it by a constant offset, against synthetic diffs. The tool takes the repo root as an **explicit argument** (never derived from `_HERE`), exits non-zero on an empty input set, and is **not applied** in this phase.
- [ ] **SWEEP-12**: The staleness marker is planted, naming the swept files, stating that `.planning/` citations into them are knowingly stale, and pointing at Phase 159 / REMAP-04 as the close-blocking closer.
- [ ] **SWEEP-13**: One commit per sub-repo plus one meta commit; both sub-repo commits land **before** the host suite runs (`test_flash_path_record_sync` asserts whole-repo porcelain). Whether editing archived `milestones/` records tripped the known "milestone close breaks its own record gates" behaviour is recorded either way — the collision or its absence, with cause.

**Scope was narrowed on 2026-08-22 (D-01): this phase sweeps source and BUILDS the remap tool; it does NOT apply the remap.** Application moves to Phase 159 / REMAP-01…05, so the remap runs exactly once over a composite diff instead of once per source-shifting phase. Measured justification: **723** citations sit at or below an edit Phases 155–158 make and would otherwise be remapped twice — `json_parser.c` **198 of 198**, `flash_utils.cpp` **97 of 97**, `memory.cpp` 199, `flash_intel.cpp` 147, `eeprom_28c.cpp` 71 — and **41% of that rework traces to four added `#include` lines**.

Four things are already decided and must survive the discuss step:

- **Decided 2026-08-22 (operator):** repair the `.planning/` `file:LINE` citations, archives included — "the only sensible way". Not "accept staleness for closed milestones". 6,939 of 12,753 citations shift. **This requirement is honoured by Phase 159, not by this phase** — see D-05 and REMAP-04 for why that is safe rather than a loophole.
- **The `uno` build must come out byte-identical.** Comments cost zero flash, so this is the sweep's strongest oracle and it is free.
- **The pre-sweep citation manifest is a deliverable of THIS phase**, not Phase 159's. It is Phase 159's oracle input and cannot be reconstructed after the sweep lands.
- **The remap tool must be idempotent and re-runnable**, not one-shot — proven by running it twice, not asserted. This caps the downside if the split is ever reverted to the naive shape.

## 2. Dead-Weight Removal (DEAD) — Phase 155, measured −1364 B flash / −8 B RAM

- [ ] **DEAD-01**: The image contains no `malloc`, `free`, `realloc`, `calloc` or `__brkval` symbol. `mem_util_blank_check` allocated `sizeof(blank_check_progress_data_t)` — a struct holding **one `uint32_t`** — and was the allocator's only caller anywhere in the firmware; the saved address moves to a file-scope static. Measured: **−650 B flash, −8 B RAM**.
- [ ] **DEAD-02**: The unchecked dereference that allocation carried is closed and **recorded as a latent defect**, not as incidental cleanup. The prior code ran `progress_data->address = handle->address` immediately after the `malloc` with no NULL test, on a part with roughly **470 B** of free RAM once `handle` (1115 B) and the jsmn token array (512 B) are accounted for.
- [ ] **DEAD-03**: The image contains no 64-bit runtime helper — `__muldi3`, `__udivmod64`, `__lshrdi3`, `__udivdi3`, `__umoddi3`, `__adddi3`, `__muldi3_6`, `__udivdi3_umoddi3` — totalling **438 B**, all of which `rurp_read_voltage_mv` alone pulled in. That function's own body also drops 434 → ~232 B. Measured total: **−714 B flash**.
- [ ] **DEAD-04**: The 32-bit voltage reformulation is proven equivalent by a **committed oracle over a stated input grid**, not by a comment. Required readings: bit-identical at the shipped calibration (`VALUE_R1` 270000 / `VALUE_R2` 44000 → `k = 7850` exactly, ADC 1023 / bandgap 225 → 35691 mV both ways), and **5 mV** worst deviation across R2 39k–47k × bandgap 200–250 × the full ADC range, against the ±5 % VPP validation windows (±600 mV at 12 V) that consume the value. Both uint32 overflow guards (`R1+R2 <= 3900000`, `k <= 4194303`) are exercised, and an implausible calibration returns 0 exactly as `r2 == 0` already did.
- [ ] **DEAD-05**: The coverage ceiling is **stated, not implied**: `src/boards/rurp_common.cpp` compiles in no native environment (`[env:native]`'s `src_filter = +<proms/>`), so DEAD-04's oracle is the only mechanical check on this arithmetic. No phase artifact may imply native or bench coverage of it.
- [ ] **DEAD-06**: The two native suites asserting `h.progress_data == NULL` — `test_eeprom28c_sdp.cpp` (Case 30 / ERASE-01) and `test_val_5v_page.cpp` (ERASE-02) — are updated together with their assertion comments and the third stale comment at `test_val_5v_page.cpp:238`. The behaviour each tested stays pinned by the surviving `is_operation_in_progress` assertion, which the **same statement** sets. This is the only requirement in Phases 155–158 that touches a test file; the alternative (retaining a dead `void* progress_data` field for 2 B of RAM) is recorded as considered and rejected, with its cost.

## 3. Duplicated-Report Extraction (DEDUP) — Phase 156, measured −426 B flash

- [ ] **DEDUP-01**: One `mem_util_report_voltage()` replaces four byte-identical VPP packing blocks (`eprom.cpp` ×2 inside `eprom_check_vpp`, `flash_intel.cpp` ×2 inside `flash_intel_write_init`). The emitted 8-byte payload is unchanged and the arithmetic preserved exactly — including the existing `uint16 + 50` promotion — so this is de-duplication, never a behaviour change. `__udivmodhi4` call sites fall **30 → 13**; those four blocks held 24 of them. `eprom_check_vpp` 524 → 280 B, `flash_intel_write_init` 562 → 348 B, helper 190 B. Measured: **−268 B**.
- [ ] **DEDUP-02**: One `mem_util_report_chip_id()` replaces four chip-ID blocks (`flash_utils.cpp`, `flash_intel.cpp`, `eprom.cpp`, `eeprom_28c.cpp`). The copies **had already drifted** — three tested `is_flag_set(FLAG_FORCE)` inline while `eprom.cpp` took an `error_code` parameter, and `eeprom_28c.cpp` carried redundant casts — and the resolved single semantic is stated, not silently chosen. Measured: **−158 B**.
- [ ] **DEDUP-03**: The WARNING/ERROR fork is proven preserved **by a test that can see it**. Every `LOG_{WARN,ERROR}_ID_BYTES` macro is the *same alias* of `LOG_ID_BYTES` (`logging_id.h:105-119`), so severity rides entirely in the message id — which means a golden trace matching on id alone **cannot** detect a swapped `response_code`. A mismatch test is required; a green golden trace does not satisfy this requirement.
- [ ] **DEDUP-04**: The nine `return !op_execute_*_operation(...)` inversions in `eprom_operations.cpp` are removed, or declined **with the measurement cited**. Flipping the convention was measured **byte-for-byte zero** on both targets — all nine wrappers inline into `main` and the switch collapses to a single shared call to `op_execute_stateful_operation.constprop.44`. So this is a pure readability decision with no size argument either way; today it costs a ten-line comment at `eprom_operations.cpp:57-67` to explain why a `!` is load-bearing.

## 4. Command-Decode Table & Type Narrowing (DECODE) — Phase 157, measured −1148 B flash / −5 B RAM

- [ ] **DECODE-01**: `key_parsers[]` and the eleven `get_*` stubs it dispatched through are replaced by one data table of `{key, offset, width, clamp}`. The stubs cost **1012 B** — 86–110 B each for one `strtoul` and one store — because a PROGMEM function pointer stopped gcc inlining them; five *identical* siblings called directly with a literal key (`get_r1`, `get_r2`, `get_rev`, `get_rw_pin`, `get_vpp_pin`) cost **zero**, which is the proof that the opacity and not the logic was the cost. Measured: **−976 B**.
- [ ] **DECODE-02**: Every wire key appears **once** in flash. Ten of eleven were stored twice — once for the table, once as a `PSTR` inside the stub that re-matched the key the table had just matched. `get_flags` remains a real function because `json_parse_config` calls it directly at two sites; that is documented as a deliberate exception, not left as an inconsistency.
- [ ] **DECODE-03**: `width` is derived from the member itself (`sizeof(((firestarter_handle_t*)0)->member)`) so it cannot drift from the field it writes, and a **compile-time assertion** prevents a future struct reorder from silently truncating an offset. All eleven fields currently sit at offsets 3–37, below `data_buffer` at 38; a `uint8_t` offset is only safe while that holds.
- [ ] **DECODE-04**: `handle->protocol` is `uint8_t` and `handle->ctrl_flags` is `uint16_t` (largest values in use `0x39` and `FLAG_SKIP_SDP_UNLOCK` `0x100`), removing a 4-byte compare from 19 protocol comparisons and 45 `is_flag_set` call sites.
- [ ] **DECODE-05**: **An out-of-range wire `algorithm` fail-closes rather than truncating into a valid protocol, proven by a NEW test.** This is the milestone's safety requirement. `json_parser.c` applies no range check, so a narrowed `protocol` would truncate `0x105` to `0x05` and dispatch into `configure_flash_5v_page` where it previously reached `configure_memory`'s fail-closed tail — and **all 172 existing tests passed against the broken version**, so the suite is blind to it. The fix saturates in `store_field`, covering `pins`, `chip_id`, `vpp_mv` and `page_size` too, which the per-stub form could not.
- [ ] **DECODE-06**: The Phase-44 `READ_TIMING_MAX_US` clamp (T-44-01) on `read-settling-delay` and `read-strobe-us` survives the deletion of `get_read_settling` / `get_read_strobe`, proven by a test rather than by inspection. The clamp moves to the table's `clamp` column and its `#define` must be hoisted above the table.
- [ ] **DECODE-07**: The rejected alternative is recorded with its measurement: converting `configure_memory`'s protocol if-chain to a `switch` on the narrowed field is **+18 B worse** (`uno` 25696 vs 25678), because the values are sparsely spread over 0x05–0x39 and gcc emits comparisons either way. The if-chain stays.

## 5. Residual Optimizations & Landing (LAND) — Phase 158, close

- [ ] **LAND-01**: `scripts/baseline/size_baseline.json` is re-recorded from **cold** builds (`rm -rf .pio/build/<env>` then exactly one `pio run -e <env>` per env) for all three AVR targets plus the native blocks, per that file's own documented convention. **BASE-01 is NOT re-anchored** — doing so would erase the reduction the same way it would erase a growth.
- [ ] **LAND-02**: The MERGE-05 policy run is green **and its one-sidedness is recorded**. `check_size_baseline.py:697` compares `flash_delta > allowance` and `:709` compares `ram_delta > ram_tolerance` — growth-only — so a reduction passes with **no named exemption**, unlike the four growth exemptions v1.31–v1.32 stacked up. Recorded explicitly so a future reader cannot mistake the green run for "nothing moved". If re-anchoring reddens the known four legs, fixtures are severed onto a **new** fixture family rather than the criterion being softened.
- [ ] **LAND-03**: The pre-existing BASE-01 native case-count mismatch — `cases baseline=141 observed=172`, which makes the canonical `--policy merge05 --baseline scripts/baseline/size_baseline_base01.json` invocation exit 1 on `beta` **before it ever reports flash** — is fixed or recorded as knowingly carried, with its cause named (BASE-01 frozen at Phase 124's count). It is **not** caused by this milestone: the size-reduction diff touches zero files under `test/`.
- [ ] **LAND-04**: It is recorded that **`check_size_baseline.py` runs in no CI workflow at all** (`grep` over `.github/` returns nothing), so every gate this milestone leans on is a local-run obligation. Stated plainly; never implied to be automated.
- [ ] **LAND-05**: The `jsmntok_t` 8 → 6 B narrowing is re-tested on an idle machine and either landed (**−128 B RAM** for +30 B flash, no protocol change) or rejected **with the failure named**. Its earlier "breaks the suite" reading was **retracted during scoping** as probable load-flakiness, so the result is genuinely **unknown**. `start` and `end` must stay signed — `jsmn.c` uses `-1` sentinels in twelve places.
- [ ] **LAND-06**: The `flash_5v_page_write_execute` per-byte modulo is replaced with a mask or declined, **with the measurement cited either way**. `flash_5v_page_page_size()` returns 64/128/256 — always a power of two — yet the loop calls `__udivmodsi4` **twice per byte**. Masking costs **+22 B flash** (measured), so this is a size-for-speed trade and the runtime half is unquantified. If taken, it is labelled as affecting the **algorithm-5 flash-page path only** and explicitly **not** connected to the w27c512-write-slow-3x work, which is a different protocol path.
- [ ] **LAND-07**: `NUMBER_JSNM_TOKENS` is recorded as **not reducible**, with the arithmetic, so the lead is closed rather than re-investigated. The maximal real command is **57 tokens** (from `pinouts.json`'s largest `address-bus-pins` = 19 and `static-high-pins` = 1, plus every optional wire key) against the current 64 — **7 tokens of headroom**. The 512 B token array can therefore only shrink via LAND-05 or via v1.28 / Backlog 999.35.
- [ ] **LAND-08**: The native suite's load-flakiness is recorded with its evidence — 172/172 at ~35 s (×5), 171/172 once at 1:13, 158-cases-with-2-ERRORED once at 1:44; failure correlates with run duration, not tree content — so the next reader does not re-derive it from a single confusing failure.

## 6. Citation Remap & Close (REMAP) — Phase 159, milestone close

- [ ] **REMAP-01**: The remap runs **exactly once**, over the composite diff from Phase 154's pre-sweep manifest to the post-Phase-158 tree — not once per phase. Input: the sweep's 6,939 shifting citations plus the **723** that Phases 155–158 shift.
- [ ] **REMAP-02**: The oracle holds mechanically — the source text recorded in the Phase 154 manifest at each cited line equals the text at the remapped line after the pass. This is the only check on the remap; **no global citation gate exists in this project today**, so nothing else would catch a bad mapping.
- [ ] **REMAP-03**: Every range citation has **both** endpoints mapped, and a range spanning a deleted block is **shrunk**, not translated by a constant offset. Proven on a real case from this milestone's own diff — Phase 157 deletes ten functions from `json_parser.c`, which guarantees at least one such case exists — not only on Phase 154's synthetic fixtures.
- [ ] **REMAP-04**: Phase 154's staleness marker is **removed, and its removal is close-blocking** — the milestone cannot close while the marker exists. This is the structural guarantee that makes D-05's temporary staleness safe rather than a promise, and it is the mechanism by which the operator's "never accept stale citations" ruling is honoured despite the split.
- [ ] **REMAP-05**: The tool is proven **idempotent** on the real corpus, not just on fixtures: a second run is a no-op. Without this, a partially-applied remap cannot be safely resumed.

---

## Traceability

Which phase covers which requirement. Authored with the requirements, tabulated at activation (2026-08-22) — this table records the mapping the category headings already state; it does not decide it.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SWEEP-01 | Phase 154 | Pending |
| SWEEP-02 | Phase 154 | Complete (154-07) |
| SWEEP-03 | Phase 154 | Pending |
| SWEEP-04 | Phase 154 | Complete |
| SWEEP-05 | Phase 154 | Pending |
| SWEEP-06 | Phase 154 | Complete (154-02) |
| SWEEP-07 | Phase 154 | Pending |
| SWEEP-08 | Phase 154 | Complete |
| SWEEP-09 | Phase 154 | Complete (154-04) |
| SWEEP-10 | Phase 154 | Partial (154-04 pre-sweep half; 154-12 settles the retarget subset) |
| SWEEP-11 | Phase 154 | Complete |
| SWEEP-12 | Phase 154 | Pending |
| SWEEP-13 | Phase 154 | Pending |
| DEAD-01 | Phase 155 | Pending |
| DEAD-02 | Phase 155 | Pending |
| DEAD-03 | Phase 155 | Pending |
| DEAD-04 | Phase 155 | Pending |
| DEAD-05 | Phase 155 | Pending |
| DEAD-06 | Phase 155 | Pending |
| DEDUP-01 | Phase 156 | Pending |
| DEDUP-02 | Phase 156 | Pending |
| DEDUP-03 | Phase 156 | Pending |
| DEDUP-04 | Phase 156 | Pending |
| DECODE-01 | Phase 157 | Pending |
| DECODE-02 | Phase 157 | Pending |
| DECODE-03 | Phase 157 | Pending |
| DECODE-04 | Phase 157 | Pending |
| DECODE-05 | Phase 157 | Pending |
| DECODE-06 | Phase 157 | Pending |
| DECODE-07 | Phase 157 | Pending |
| LAND-01 | Phase 158 | Pending |
| LAND-02 | Phase 158 | Pending |
| LAND-03 | Phase 158 | Pending |
| LAND-04 | Phase 158 | Pending |
| LAND-05 | Phase 158 | Pending |
| LAND-06 | Phase 158 | Pending |
| LAND-07 | Phase 158 | Pending |
| LAND-08 | Phase 158 | Pending |
| REMAP-01 | Phase 159 | Pending |
| REMAP-02 | Phase 159 | Pending |
| REMAP-03 | Phase 159 | Pending |
| REMAP-04 | Phase 159 | Pending |
| REMAP-05 | Phase 159 | Pending |

**Coverage:**
- v1 requirements: **43** total (30 specified at activation + the **13** SWEEP requirements settled 2026-08-23 at `/gsd-discuss-phase 154`)
- Mapped to phases: **43**
- Unmapped: **0** ✓

The activation count was **31** — 30 fully specified plus one `SWEEP-01…NN` placeholder of unknown cardinality. That placeholder resolved to **13**, so the total moved 31 → 43. This is the expansion activation predicted, not drift.

---

## Out of Scope

**Replacing JSON with a binary command protocol.** Operator decision, 2026-08-22. Measured at **−3728 B flash / −512 B RAM** on `leonardo` — the largest single saving the survey found, and deliberately not taken here because it is a breaking cross-repo wire change rather than a refactor. It stays queued as **v1.28 Binary Command Protocol** and is filed as Backlog **999.35** carrying the measurement. Two consequences that must not be lost:

- It **corrects v1.28's own estimate**: that entry's ~512 B RAM figure is confirmed exactly, but its "~1–1.5 KB net flash" is wrong by roughly 2.5×.
- It **overlaps DECODE-01**. If 999.35 ever lands, Phase 157's field table is superseded, so the two figures are **not additive** and 999.35 must be re-measured from the post-v1.33 position before anyone quotes a combined saving.

**Any criterion requiring a physical board.** Two changes here have runtime consequences a bench could measure (DEAD-04's voltage reformulation, LAND-06's modulo), but neither needs silicon to be *correct*, and DEAD-04's numerical oracle bounds the voltage change at 5 mV against ±600 mV windows. Adding a bench phase would create a hardware-gated criterion for a milestone whose entire premise is byte-level equivalence.

**Host-side changes in Phases 155–158.** Those four phases are firmware-only: no host file moves, no wire change, no `chip_database.json` change, no protocol-parity constant moves. The asymmetry is deliberate — it keeps every measured delta attributable to firmware edits alone. Phase 154 is the only dual-repo phase.

**Restructuring `eprom_write_execute`.** At 1570 B it is still the largest single handler, but it was rewritten for speed in the w27c512-write-slow-3x debug session (pass-batched program loop) and is heavily documented. Touching it would trade a delivered speed win for bytes. Lead closed during scoping.

**A shared skeleton across the five write paths.** Inspected during scoping: `flash_5v_page_write_execute` is page-buffered with boundary detection while `flash_nor_unlock_write_execute` is per-byte-with-verify. Genuinely different shapes; forcing a common helper would cost readability for little size. Lead closed.

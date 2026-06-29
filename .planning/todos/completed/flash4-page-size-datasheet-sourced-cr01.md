---
id: flash4-page-size-datasheet-sourced-cr01
title: flash4 page size should be datasheet-sourced per chip, not a capacity heuristic (CR-01)
captured: 2026-06-18
status: pending
type: bug
target_milestone: v1.13+
priority: medium
related_phase: 74
resolves_phase: 94
source: .planning/phases/74-per-family-correctness-fixes-flash-gated/74-REVIEW.md (CR-01 + WR-04)
---

# flash4 page size: replace capacity heuristic with a datasheet-sourced per-chip value (CR-01)

## The finding

Phase 74 (74-02 / FIX-02B) fixed the W29C040 mid-page-poll write bug by replacing a fixed
64-byte page `#define` with `flash4_page_size(mem_size)` in
`firestarter/src/proms/flash_type_4.cpp:27-31`:

```cpp
static uint32_t flash4_page_size(uint32_t mem_size) {
    if (mem_size <= 65536)  return 64;
    if (mem_size <= 262144) return 128;
    return 256;
}
```

Page size is a **per-chip datasheet constant** that does NOT track capacity. The bands
under-size by half for the two non-512KB flash4 families:

| Family (size_bytes) | Example chips | Real page | Heuristic | Verdict |
|---------------------|---------------|-----------|-----------|---------|
| 64KB (65536)  | AT29C512, W29C512, SST29EE512 | 128 | 64  | under-sized |
| 256KB (262144)| AT29C020, W29C020, SST29EE020 | 256 | 128 | under-sized |
| 512KB (524288)| **W29C040** (phase target)    | 256 | 256 | **correct** |

~10 of 27 flash4 (`algorithm:5`) chips get an under-sized page, which makes
`flash4_wait_for_page_write` poll mid-page — the exact failure mode this phase fixed for
the W29C040, just on different chips.

## Why this is NOT a regression (and why it was deferred, not fixed in 74)

- Before 74-02 the code used a **fixed 64-byte page for ALL flash4 chips**. Relative to that:
  W29C040 is now **fixed**, the 256KB family is **improved** (64→128, still short of 256),
  and the 64KB family is **unchanged** (still 64). No chip is worse off.
- Phase 74's scope (and the 74-02 plan text) was W29C040-specific — "the W29C040's 256-byte
  page." The executor generalized the fix into the capacity heuristic; the extra bands are
  the questionable part. W29C040, the only bench-validated flash4 representative (Phase 73),
  is correct.
- A *correct* fix has no firmware-only form: `chip_database.json` has **no page-size field**
  today (only `size_bytes` + `programming.algorithm`). The firmware can only guess from
  capacity unless we add the datum.

## Proper fix (for whoever picks this up)

1. Add a datasheet-sourced `page_size` (a.k.a. page-write-buffer size) to the flash4 chip
   entries in the chip DB build pipeline (`firestarter_app` build_db.py / source) — per chip,
   not derived.
2. Plumb it through host codegen → the wire/`configure_flash4` handle so the firmware reads
   page size from the handle instead of `flash4_page_size(mem_size)`.
3. Delete `flash4_page_size()` (and its capacity bands) once the handle carries the real value.
4. **Flash budget:** Leonardo is at ~89.5% (3018 bytes headroom after 74-02's Option B
   mitigation). Adding a handle field is cheap; confirm `-e leonardo` stays under the ceiling.

## WR-04 (paired test gap)

`firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp` hard-codes
`mem_size = 524288` everywhere — the one capacity where the heuristic is correct — so the
suite greenlights while CR-01 is live. When fixing CR-01 (or as a standalone RED guard),
add `mem_size`-parameterized cases (32768 / 65536 / 131072 / 262144 / 524288) asserting the
page-end poll fires at the correct datasheet page boundary (`flash4_wait_for_page_write`
invoked at `address == page-1`, not earlier). These fail today and would guard the fix.

## Related review warnings (same REVIEW.md, lower severity — fold in if convenient)

- **WR-02:** `const byte_flip_t FLASH_*[]` arrays defined in a header → duplicated into 4 TUs;
  works against the flash budget. Make `extern` + define once.
- **WR-03 / IN-01:** `FLASH_ENABLE_WRITE_PROTECTION` / `FLASH_DISABLE_WRITE_PROTECTION` are
  dead constants (the former byte-identical to `FLASH_ENABLE_WRITE`).
- **WR-01:** the page loop assumes a page-aligned `handle->address`; non-aligned starts
  misalign page grouping (chip tolerates it, untested).

## Cross-references

- `.planning/phases/74-per-family-correctness-fixes-flash-gated/74-REVIEW.md` — full findings (CR-01, WR-01..04, IN-01..03)
- `firestarter/src/proms/flash_type_4.cpp` — the heuristic + write loop
- Phase 73 W29C040 FAIL (the only bench-validated flash4 cell); 74-03 re-bench is the PASS proof
- Memory `reference_infoic_xml_field_decode` — DB field semantics for build_db.py

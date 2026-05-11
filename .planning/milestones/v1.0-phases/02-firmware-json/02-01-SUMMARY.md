---
phase: 02-firmware-json
plan: 01
status: complete
files_modified:
  - firestarter/src/json_parser.c
---

# Phase 02 Plan 01: Firmware JSON Protocol Extension — Summary

## What was changed

Two changes were made to `firestarter/src/json_parser.c`:

1. **Added "algorithm" key parser**: Added `const char key_algorithm[] PROGMEM = "algorithm"` alongside the other PROGMEM key constants, added `{key_algorithm, get_algorithm}` as the final entry in the `key_parsers[]` array, added a forward declaration for `get_algorithm()`, and implemented `get_algorithm()` using the `extract_long` macro to store the integer value in `handle->protocol`.

2. **Silently skip unknown JSON fields**: Replaced the else-branch in `json_parse()` that called `firestarter_error_response_format("Unknown field: %s", ...)` and returned -1 with a simple `token_idx += 2` to skip the unknown key and its scalar value token. This makes the firmware forward-compatible with new fields added by the Python CLI.

## Build results

```
========================= [SUCCESS] Took 0.48 seconds =========================  (uno)
========================= [SUCCESS] Took 0.40 seconds =========================  (leonardo)
```

## Deviations

None — plan executed exactly as written.

---
id: remove-dead-json-init-sizeof-pointer-bug
title: Remove/fix dead json_init() — sizeof(pointer) makes num_tokens compute to 0
captured: 2026-07-02
status: pending
type: bug
priority: low
source: /gsd-explore 2026-07-02 (binary-protocol-savings-analysis.md)
---

# Remove/fix dead `json_init()` — `sizeof(pointer)` bug

`firestarter/src/json_parser.c:50`

```c
int json_init(const char* json, int len, jsmntok_t* tokens) {
    jsmn_parser parser;
    jsmn_init(&parser);
    return jsmn_parse(&parser, json, len, tokens, sizeof(tokens) / sizeof(tokens[0]));
}
```

`tokens` is a **pointer** parameter, so `sizeof(tokens)` = 2 (AVR pointer) and
`sizeof(tokens[0])` = `sizeof(jsmntok_t)` = 8 → `num_tokens` computes to **0**.
`jsmn_parse` with `num_tokens=0` returns `JSMN_ERROR_NOMEM`, so this function
would never parse anything.

## Why it hasn't bitten

Appears to be **dead code**. The live parse path (`firestarter.cpp:59`) calls
`jsmn_parse` directly with the correct `NUMBER_JSNM_TOKENS` (64). No caller of
`json_init` was found in `src/` or `include/`.

## Action

- Confirm no caller (grep `json_init` across both repos incl. tests).
- If dead: delete `json_init` and its decl in `include/json_parser.h`.
- If a caller exists: pass an explicit `token_count` param — never `sizeof` on a
  pointer.

## Note

Likely mooted entirely if the binary-command-protocol seed is executed (deletes
`json_parser.c`). Fix or delete independently if that seed stays dormant.

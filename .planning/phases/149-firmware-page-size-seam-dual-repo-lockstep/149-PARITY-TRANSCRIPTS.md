# 149-PARITY-TRANSCRIPTS.md — Phase 149 Plan 05 (PGSZ-03, D-18) transcripts

Transcripts for `tests/test_json_key_parity.py`'s two undecorated planted-fixture legs, and (below,
added by this plan's Task 3) the empty-`FIRESTARTER_FW_ROOT` skip-leg transcript. All commands run
from `/workspaces/firestarter_app`.

## Plant 1 — key-string drift (`planted_json_parser_key_string_drift.c`)

The page-size PROGMEM string is spelled with an underscore (`page_size`) instead of the wire's
hyphen (`page-size`) — Pitfall 10's exact shape.

### pytest invocation (the wrapper test, which asserts the helper raises — expected exit 0)

```
$ python3 -m pytest tests/test_json_key_parity.py::test_planted_key_string_drift_is_detected -o addopts="" -q ; echo EXIT=$?
.                                                                        [100%]
1 passed in 0.04s
EXIT=0
```

### Direct helper invocation — the seen-to-fail evidence (outside pytest, no wrapper)

```
$ python3 -c "
import tests.test_json_key_parity as m
m.FIRMWARE_PARSER_SOURCE = m._FIXTURE_KEY_STRING_DRIFT
try:
    m._check_page_size_key_present_and_dispatched()
    print('UNEXPECTED: did not raise')
except AssertionError as e:
    print('RAISED:', e)
"
RAISED: no PROGMEM key string equal to JSON_KEY_PAGE_SIZE ('page-size') was found in /workspaces/firestarter_app/tests/fixtures/planted_json_parser_key_string_drift.c -- extracted key strings: ['address', 'algorithm', 'chip-id', 'flags', 'memory-size', 'page_size', 'pin-count', 'pulse-delay', 'read-settling-delay', 'read-strobe-us', 'vpp_mv']
```

The raised message names `page_size` (the fixture's mis-spelling) among the extracted keys and
never `page-size` — the gate's own shared helper (`_check_page_size_key_present_and_dispatched`,
the same one `test_page_size_key_string_matches_constants_py` calls) is what fired, not a
parallel reimplementation.

## Plant 2 — undispatched key (`planted_json_parser_undispatched_key.c`)

The page-size PROGMEM string is spelled correctly (`page-size`), but its `key_parsers[]` row is
absent — the declared-but-unwired hole.

### pytest invocation (expected exit 0)

```
$ python3 -m pytest tests/test_json_key_parity.py::test_planted_undispatched_key_is_detected -o addopts="" -q ; echo EXIT=$?
.                                                                        [100%]
1 passed in 0.03s
EXIT=0
```

### Direct helper invocation — the seen-to-fail evidence

```
$ python3 -c "
import tests.test_json_key_parity as m
m.FIRMWARE_PARSER_SOURCE = m._FIXTURE_UNDISPATCHED_KEY
try:
    m._check_page_size_key_present_and_dispatched()
    print('UNEXPECTED: did not raise')
except AssertionError as e:
    print('RAISED:', e)
"
RAISED: the page-size key string 'page-size' is declared as 'key_page_size' but that identifier does not appear inside the key_parsers[] dispatch body -- a PROGMEM string that is declared but never dispatched exists on the wire and never matches anything a host sends.
```

Leg isolation, confirmed by the test module's own assertions and visible above: plant 1's message
never contains the phrase "does not appear inside the key_parsers"; plant 2's message never contains
"no PROGMEM key string equal to JSON_KEY_PAGE_SIZE" — the two failure modes are distinguishable from
their raised text alone.

### Real firmware source untouched

Both plants inject via `monkeypatch.setattr` on the module-scope `FIRMWARE_PARSER_SOURCE` constant,
never an edit to the real file. Confirmed after both runs above:

```
$ git -C /workspaces/firestarter status --porcelain
(empty)
$ test "$(git -C /workspaces/firestarter hash-object src/json_parser.c)" = "$(git -C /workspaces/firestarter rev-parse HEAD:src/json_parser.c)" && echo MATCH
MATCH
```

Both planted legs also assert this same before/after blob-hash equality and the empty-porcelain
condition internally, every time they run (the V12 ceremony), not just in this manual transcript.

# Cell A1 — write/read/judge narrative, one section per position

## Position 1 — `A1__control__w27c512`

- **Image:** `gen_addr_image.py --stamp-width 16 65536 16` -> `reads/A1__control__w27c512/written.bin`,
  65536 B, sha256 `8ee568689ae9ab14ac5e34179542fecbe44373c7ef8b4400a1b6f3e3f0d563a4`, matches
  `IMAGE-PLAN.json`'s row for this position by runtime lookup.
- **Write:** `control` arm, `firestarter -p /dev/ttyACM1 write w27c512 written.bin`, under
  `timeout --signal=INT 165` (the W27C512 ceiling — 4x the measured healthy 41.010 s from
  `BRINGUP-wrv`). Wrapper exit code **0** — the ceiling did **not** fire.
  - **Wall-clock (judged measure):** **41.305 s**
  - **App-reported (unjudged datum):** **37.48 s** (`Write to W27C512 successful (37.48s).`,
    grepped by string, not line number)
- **Read:** control arm, single read (normal case, no v133 disagreement to escalate against yet):
  `firestarter -p /dev/ttyACM1 read w27c512 run_01.bin`, exit code **0** (`--app-verdict`).
  App-reported read duration: 14.48 s (informational only; not the judged quantity).
- **Judge:** `judge_wrv.py --expect-size 65536 --app-verdict 0` ->
  `sha_verdict_judged=match`, `read_count=1`, `distinct_read_shas=1`, `size_violations=[]`,
  `app_verdict_unjudged=0`, `verdict_disagreement=false`.
- **Blank state:** not measured — the W27C512's pre-write blank check runs internally inside the
  write path (never skipped; no forbidden flag used); no standalone blank observation was taken
  for this position (the standalone `blank` command is reserved for the W29C020 smoke check,
  D-09, Task 7).
- **Outcome:** `validated`. Appended to `EVIDENCE.jsonl`, `render_evidence.py --check` green.
- No re-seat was needed.

## Position 2 — `A1__control__w29c020` — the milestone's first 262144 B write/read on silicon

- **D-09 smoke check** (outside the `P-01`..`P-11` step list; full detail in `SMOKE-W29C020.md`):
  `id w29c020` exit 0 (chip-id matched); standalone `blank w29c020` exit 1, `Not blank, at
  0x000000, v: 0x00` — a valid, expected addressability proof, **not** a failure. No forbidden
  flag used.
- **Image:** `gen_addr_image.py --stamp-width 32 262144 17` -> `reads/A1__control__w29c020/written.bin`,
  262144 B, sha256 `46e0fe13b11c46d3a86039c6812ddf6a809746ab33c945104e6753d0eb877dfb`, matches
  `IMAGE-PLAN.json`'s row by runtime lookup.
- **Write:** `control` arm, under `timeout --signal=INT 600` — **the 600 s absolute fallback,
  named as a fallback, not a derivation**, because this position is the one that creates the
  derived figure. Wrapper exit code **0** — did not fire.
  - **Wall-clock (judged measure):** **97.937 s**
  - **App-reported (unjudged datum):** **94.47 s** (`Write to W29C020 successful (94.47s).`)
  - **Derived D-08 W29C020 ceiling for every later W29C020 position: 4x97.937 = 391.748 s.**
    This number is carried into Task 11 (position 4, v133 x w29c020) and into plans 161-04
    (A2) and 161-05 (A3/B2) via this plan's SUMMARY.
- **First 262144 B read wall-clock:** **73.344 s** (app-reported 69.86 s). This is the read-set
  budget baseline A2/A3-B2 inherit — **a baseline to compare against, not a portable constant**:
  the Uno moves 512 B chunks per transfer where the Leonardo moves 1024 B.
- **Read:** control arm, single read: `firestarter -p /dev/ttyACM1 read w29c020 run_01.bin`,
  exit code **0** (`--app-verdict`).
- **Judge:** `judge_wrv.py --expect-size 262144 --app-verdict 0` -> `sha_verdict_judged=match`,
  `read_count=1`, `distinct_read_shas=1`, `size_violations=[]`, `app_verdict_unjudged=0`,
  `verdict_disagreement=false`.
- **Blank state:** not blank at `0x000000`, `v: 0x00` (D-09's standalone `blank` check) — the
  only blank observation the whole milestone will have for W29C020; since Phase 153,
  `-b`/`--no-blank-check` is unread on algorithm `0x05`, so the write itself performs no
  pre-write blank check on this part at all.
- **Outcome:** `validated`. Appended to `EVIDENCE.jsonl`, `render_evidence.py --check` green.
- No re-seat was needed.

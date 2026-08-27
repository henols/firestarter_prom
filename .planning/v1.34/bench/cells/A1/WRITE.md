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

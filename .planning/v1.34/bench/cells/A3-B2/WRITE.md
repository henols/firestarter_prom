# Cell A3/B2 — write/read/judge narrative, one section per position

## Position 1 — `A3-B2__control__w27c512`

- **Image:** `gen_addr_image.py --stamp-width 16 65536 24` -> `reads/A3-B2__control__w27c512/written.bin`,
  65536 B, sha256 `a094e902a30b4fa3369ee493338351e11a8b6667f7539460b63f78dce896ae43`, matches
  `IMAGE-PLAN.json`'s row for this position by runtime lookup (mask 24, stamp 16).
- **Write:** `control` arm, `firestarter -p /dev/ttyACM0 write w27c512 written.bin`, under
  `timeout --signal=INT 165` (the W27C512 ceiling). Wrapper exit code **0** — the ceiling did
  **not** fire (log `11_write_control_w27c512.std{out,err}.log`).
  - **Wall-clock (judged measure):** **37.172 s**
  - **App-reported (unjudged datum):** **33.37 s** (`Write to W27C512 successful (33.37s).`,
    grepped by string — `grep -o "Write to W27C512 successful ([0-9.]*s)"` — never by line
    number: the identical success string sits at `eprom_operations.py:2045` on the control arm
    and `:1934` on v133, an arm-dependent line offset).
  - **Cross-board reference:** A1's control-arm W27C512 figure (Uno, `161-03-SUMMARY.md`) was
    **41.305 s wall / 37.48 s app**. This cell's figures (37.172 s / 33.37 s) are close to but
    somewhat below A1's — consistent with, not proof of, the **Leonardo moving 1024-byte chunks
    where the Uno moves 512** (a comparison note, not a portable per-byte budget; the board
    identity, not the firmware, is the variable named here).
- **Read:** control arm, single read (normal case, no v133 disagreement to escalate against yet):
  `firestarter -p /dev/ttyACM0 read w27c512 run_01.bin`, exit code **0** (`--app-verdict`), log
  `12_read_control_w27c512.std{out,err}.log`. App-reported read duration: 7.40 s (informational
  only, not the judged quantity).
- **Judge:** `judge_wrv.py --expect-size 65536 --app-verdict 0` ->
  `sha_verdict_judged=match`, `read_count=1`, `distinct_read_shas=1`, `size_violations=[]`,
  `app_verdict_unjudged=0`, `verdict_disagreement=false`.
- **Blank state:** not measured — the W27C512's pre-write blank check runs internally inside the
  write path (never skipped; no forbidden flag used); no standalone blank observation was taken
  for this position.
- **Real VPP context for this write (P-06):** firmware-reported 12.3 V, operator meter 11.44 V —
  in band (guard window [11.4, 12.5] V, `eprom.cpp:713`/`:736`), the best achievable real rail on
  this shield. Full ratiometric-ADC finding in `POT.md`.
- **Chip-condition context:** this is the W27C512's ninth handling; the caveat carried from A1/A2
  was closed at `P-05` by operator inspection ("nothing looks of[f]") — not a measurement-based
  clearance. No `0x303`-class fault occurred on this write; no re-seat was needed.
- **Outcome:** `validated`. Appended to `EVIDENCE.jsonl` as position 9 of 12,
  `render_evidence.py --check` green.

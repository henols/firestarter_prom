# Pitfalls Research

**Domain:** Validating + extending write/program/verify algorithm families on an Arduino-based EPROM/Flash/EEPROM programmer (RURP shield), hardware-in-the-loop, dual-repo lockstep (firmware C++ + Python host CLI)
**Researched:** 2026-06-16
**Confidence:** HIGH (project-internal evidence: firmware source `eprom.cpp`/`flash_intel.cpp`/`eeprom_28c.cpp`, the `firmware-vpp-misread.md` + `write-verify-datapath-overflow.md` debug records, v1.9 Phase 44 RCA, v1.12 dispatch-hardening, and operator bench-protocol memory)

> This milestone is **test-first validation of already-implemented algorithm families on real chips, then evidence-driven gap implementation**. The dominant hazards are (A) **false pass/fail** — believing a write succeeded (or failed) when the verify itself is untrustworthy — and (B) **chip destruction** — driving the wrong VPP / wrong algorithm / a brown-out program onto a physical part. Both are unforgiving: a false pass ships a corrupt image; a chip-destruction event burns the operator's silicon. Everything below is prioritized accordingly.

---

## Critical Pitfalls

### Pitfall 1: False-PASS from an untrustworthy verify read board (verify is meaningless on Rev 0 / Rev 2.0 / uno328pb)

**What goes wrong:**
A `write`/`program` is declared correct because the post-write `verify` matched — but the verify ran on a board whose **read path is the v1.9-deferred read bug**. On Modified Rev 0 the read path has broad read-strobe-causal jitter (Phase 44 RCA); Rev 2.0 has the Bug B /CE-or-/OE timing + voltage-divider failure; uno328pb drifts (timeouts + up-to-99% `0xff`/`0x00` zero-drift during W27C512 reads). A verify built on any of those compares the file against **noise**, so it can both falsely pass (jitter happens to land on matching bytes, or a re-read returns the expected value by luck) and falsely fail (jitter on an actually-correct write). The firmware's own in-program verify loop (`eprom_write_execute` → `verify_and_update_mask`, `eprom.cpp:129`) reads the chip back through the **same** suspect read path, so even the firmware-internal "did it stick?" decision is corrupted on a bad board.

**Why it happens:**
The read bug is *deferred*, not fixed — it is easy to forget that "deferred" means "still present on 2 of 3 shields + the 328PB board". Verify *looks* like an independent oracle, but on this hardware the read oracle shares the exact fault the milestone is designing around.

**How to avoid:**
- **Pin the verify oracle to Leonardo + a clean shield and treat every other board's verify as advisory only.** Leonardo's write+verify is proven clean (EVEN-01; `write-verify-datapath-overflow.md` end-to-end: "Verify for W27C512 successful", full 64 KB host↔fw compare PASSED).
- Build the validation matrix so each family's **PASS criterion is a Leonardo verify**, and explicitly mark uno328pb / Rev-0 / Rev-2.0 results as "read-unreliable — not a pass".
- For any board other than the clean verify board, **require N≥5 byte-identical reads (SHA-256) of the just-written image before trusting a single verify** — a single read is never authoritative (operator rule: "never trust N=1").
- Cross-check write success against a **second, read-independent signal** where the algorithm provides one: Intel-flash status-register polling (`flash_intel_poll_sr`) and AT28C DQ7/data-poll (`eeprom28c_wait_for_write`) are programming-completion signals that do NOT depend on the bulk read path.

**Warning signs:**
- A family "passes" on uno328pb but the read SHA changes between two consecutive reads of the same chip.
- WORST-case zero-byte percentage > 0.1% in a `dev consistency-check` on the verify board.
- Verify flips PASS↔FAIL on re-run — that is read noise, not write state.

**Phase to address:**
Harness/matrix phase (first phase) — bake "Leonardo is the verify oracle; other boards advisory" into the matrix schema and the PASS definition. Re-asserted in every bench-validation phase.

---

### Pitfall 2: Chip destruction by wrong VPP / wrong algorithm routed to a physical part

**What goes wrong:**
A chip is driven with a programming voltage or sequence its silicon cannot survive: 12–13 V VPP onto a 5 V-only EEPROM/SRAM pin, 25 V NMOS VPP onto a 21 V part, or a UV-EPROM 1 ms VPE pulse onto a part that expects a 5 V page write. This is exactly the hazard v1.12's fail-closed dispatch + host `resolve_chip` guard exists to prevent (the silent `mem_type=1 → configure_eprom → 12 V VPP` fallback). During *validation* the danger re-enters through the back door: writing a chip whose DB classification is wrong, hand-crafting JSON to test a family (bypassing the host guard), or implementing a new per-family algorithm that asserts the wrong control-register bits (`CTRL_VPP_REGULATOR_ENABLE`, `CTRL_VPP_VPE_DROP_ENABLE`, `CTRL_VPP_P1_ENABLE`, `CTRL_VPP_A9_ENABLE`).

**Why it happens:**
- Bench testing tempts shortcuts (`--force`, hand-built JSON, user-override DB entries) that route around the v1.12 in-host refusal.
- A new/corrected handler is one wrong `set_control_register` line from energizing VPP on the wrong pin; the dispatch tests assert on operation pointers, **not** register side effects (firmware CLAUDE.md native-test note), so a wrong-VPP bug compiles, passes native tests, and manifests only as a fried chip on the bench.
- `FLAG_VPE_AS_VPP` / `protocol==0x0B` selects a **direct VPE path with no dropping resistor** (`eprom_write_execute`, `eprom.cpp:145`); the wrong flag on the wrong chip puts undropped VPE on the part.

**How to avoid:**
- **Never bypass the host `resolve_chip` / `support_status` guard during validation.** Test only DB-classified chips through the normal path; if a hand-crafted JSON test is unavoidable, do it with **no chip in the socket** (the v1.12 fail-closed + VPP-check paths can be exercised chip-out).
- For any new/corrected handler, **dry-run the VPP electrically with the chip OUT first**: assert the regulator, measure the socket VPP pin with a multimeter, confirm it matches `handle->vpp_mv` and is routed to the intended pin **before** ever seating a chip. The `vpp`/`vpe` monitors enable the regulator + measure only (no A9/VPE/P1 socket routing) — safe with or without a chip seated.
- Lean on the existing pre-pulse VPP ADC compare (`eprom_check_vpp`, `flash_intel_check_vpp`): it errors-closed (`RESPONSE_CODE_ERROR`, regulator cleared) when measured VPP exceeds `vpp_mv + 500` — **but see Pitfall 3: that check is only as trustworthy as the calibration**.
- Keep host `check_dispatch.py` / GATE-03 class guard green for any DB change a validation/gap phase makes; never re-promote an `adapter-required` / `vpp-exceeds-max` chip to a real handler without a fresh safety review.
- For corrected handlers, add a **native test asserting the control-register bit sequence** (extend `host_stubs.cpp` to record register writes) so wrong-VPP routing is caught off-bench.

**Warning signs:**
- A test plan that says "force-write to see what happens" on a seated chip.
- A `diff_db.py` diff that moves a chip's `algorithm`/`vpp_mv`/`pinout` without a documented rationale.
- A new handler calling `set_control_register(... CTRL_VPP_* ...)` without a matching chip-out VPP bench measurement.

**Phase to address:**
Per-family validation phases (chip-out VPP dry-run as a precondition gate) **and** per-family-fix / adapter-required-implementation phases (register-bit native tests + GATE-03 re-green). Harness phase encodes "chip-out VPP measurement precedes first seated write".

---

### Pitfall 3: Calibration confounder — stale-EEPROM R1 makes the VPP safety check (and program path) lie (backlog 999.1)

**What goes wrong:**
Firmware computes VPP as `Vin = Vadc * 1100 * (r1+r2) / (bandgap * r2)` with `r1/r2` read from **EEPROM**, not the code defaults. A board calibrated under `CONFIG_VERSION="VER06"` keeps its stale `r1` because `rurp_validate_config` re-applies defaults only when `version != CONFIG_VERSION` — and the Phase 44 fix (`VALUE_R1` 1000→270000) **did not bump CONFIG_VERSION**. On the affected uno328pb unit a true 12.2 V reads as ~1.8 V (≈6.8× under-read). Two downstream failures: (a) the program path stalls at the first chunk because `eprom_check_vpp` sees "VPP low" and errors; (b) more dangerously, a different miscalibration could under-read a genuinely-too-high VPP and let the safety check **pass a destructive voltage**. A validation run on a miscalibrated board produces VPP-dependent results that are pure measurement artifact — you "discover a bug" that is actually stale EEPROM.

**Why it happens:**
EEPROM is authoritative and persistent; the code-default fix is invisible to an already-calibrated board, and nothing in the normal flow surfaces the live `r1`.

**How to avoid:**
- **At the start of every VPP-dependent bench task, read back the live calibration** (`firestarter config` / `hw_get_config` renders `R1: {r1}, R2: {r2}`) and confirm `r1 ≈ 270000`. A board showing `r1 ≈ 1000` is miscalibrated — recalibrate before trusting any VPP/program/verify result.
- Independently confirm socket VPP with a **multimeter** the first time a given board+shield programs in this milestone; a persistent fixed-ratio divergence = stale divider constants.
- Consider closing 999.1 properly (bump `CONFIG_VERSION` so the default propagates, or add a host recalibrate step) — but treat that as a firmware change subject to the flash-budget pitfall.
- Prefer **Leonardo** for program/verify validation: its calibration is the known-good EVEN-01 baseline, sidestepping the stale-R1 unit entirely.

**Warning signs:**
- "VPP is low: 1.8V < 12.0V" while a meter reads ~12 V at the socket.
- Program stalls at the very first chunk (`0x0200`) — classic 999.1/999.2 signature.
- VPP "bugs" that appear on one board and never reproduce on Leonardo.

**Phase to address:**
Harness phase (encode "read-back live R1/R2 + meter-reconcile VPP" as a per-board precondition). If testing elevates 999.1 to a committed gap, a dedicated firmware-fix phase (`CONFIG_VERSION` bump) — gated by the flash-budget check.

---

### Pitfall 4: uno328pb program-current brown-out hang (backlog 999.2) — never trust uno328pb for program/write tests

**What goes wrong:**
When uno328pb drives programming current (chip PROGRAM phase), the board brown-outs and the firmware stalls (backlog 999.2; "uno328pb can't complete a program"; Phase 54 UAT). A validation run treats the resulting timeout/stall as an *algorithm* failure and chases a phantom firmware bug, or records the family as "fails on hardware" when the real cause is the board's power delivery.

**Why it happens:**
The 999.2 brownout and the 999.1 stale-R1 misread present *similarly* (program stalls at first chunk), so they get conflated; uno328pb is a tempting test board because it is often on the bench.

**How to avoid:**
- **Exclude uno328pb from program/write validation entirely.** Use it (at most) for read-only/dispatch observation. Leonardo is the program/verify board of record (PROJECT.md key context).
- Mark uno328pb cells for write/program families **N/A — board power-delivery limitation (999.2)**, not failures.
- Distinguish 999.1 (stale R1, fixable, reads ~1.8 V) from 999.2 (brownout, board limitation) via the live-R1 readback (Pitfall 3): correct R1 + still stalls under program current ⇒ 999.2.

**Warning signs:**
- Program completes on Leonardo but stalls on uno328pb at the same chip/algorithm.
- The stall correlates with program/erase current draw, not with a specific data pattern.

**Phase to address:**
Harness phase (board-eligibility column: uno328pb = no program/write). Every bench-validation phase honors it.

---

### Pitfall 5: False-PASS from a stale/cached host-side buffer (verify reads what you wrote, not what the chip holds)

**What goes wrong:**
The host `verify` compares the file image against bytes it *believes* came from the chip — but a code path returns a cached/echoed buffer, compares the just-sent write buffer to itself, or the read-back never actually round-trips to silicon. The compare passes vacuously. (Adjacent precedent: the v1.10 `write-verify-datapath-overflow.md` showed the host→fw data path was *unexercised* on hardware for a whole milestone because bench focus was the read path — a full class of write/verify behavior was never run end-to-end.)

**Why it happens:**
Verify-during-write reuses `handle->data_buffer` (`eprom_write_execute`); on the host side an optimization or a test stub can short-circuit the chip round-trip. It is invisible because the happy-path output looks identical to a real pass.

**How to avoid:**
- **Independent-read verify:** the authoritative validation is *write image A → power-cycle / re-handshake → fresh full read → compare SHA-256(read) to SHA-256(A)*, using a separately-loaded file, not the in-memory write buffer.
- **Negative control on every family:** prove verify *fails* when it should — verify the written chip against a *different* file (must report a mismatch at a specific address), and verify a chip-out/blank read (the `write-verify-datapath-overflow.md` error leg "0xff != 0x03 at 0x000000" is exactly this control). A verify that can't fail isn't a verify.
- Confirm the read genuinely traverses the firmware data path (COBS-framed, CRC8) — transport is proven byte-exact (v1.10), so a true read-back is trustworthy *on a clean board*; combine with Pitfall 1's board constraint.

**Warning signs:**
- Verify passes against a deliberately-wrong file.
- Verify of a blank/absent chip "passes".
- Verify time implausibly short for the chip size (no real per-byte read traffic).

**Phase to address:**
Harness phase — the matrix PASS definition must require independent-read-then-SHA-compare **plus** a passing negative control per family.

---

### Pitfall 6: A clean read masks a bad write (verify-during-write declared success via read jitter / retry convergence)

**What goes wrong:**
`eprom_write_execute` retries mismatched bytes up to `NUMBER_OF_RETRIES` (20) with escalating `pulse_delay`, then returns success when `verify_and_update_mask` reports zero mismatches. But that mask is computed from **chip reads on a possibly-jittery board** (Pitfall 1): a read that flickers to the *expected* value clears the mismatch bit, so the loop "converges" without the byte being correctly programmed. The chip is under-programmed (marginal cell charge) yet reported PASS; a later fresh read shows corruption.

**Why it happens:**
The in-loop verify and the success decision share the read path; escalating retries + read noise can manufacture false convergence. Marginal programming is invisible to a single immediate read-back.

**How to avoid:**
- Require the **independent post-write full read** (Pitfall 5) as the PASS oracle, not the firmware's internal retry-convergence.
- Watch the retry count: the firmware emits `MSG_INFO_RETRIES`. A family that "passes" only after many retries is a marginal-programming warning, not a clean pass — record retries in the matrix.
- For UV-EPROM/Flash, use a clean verify board + N≥5 byte-identical reads so a single lucky read can't mask under-programming.

**Warning signs:**
- High retry counts before success.
- Verify passes immediately after write but a re-read minutes later differs.
- `MSG_ERR_WRITE_FAILED` with a small mismatch count that disappears on the next run (read noise, not a stable write).

**Phase to address:**
Harness phase (capture retry counts; PASS = independent read) + per-family validation phases.

---

### Pitfall 7: Leonardo flash-budget overflow when adding/correcting firmware (≈88% TIGHT)

**What goes wrong:**
This is a firmware-touching milestone. Leonardo flash sat at **88.4% (25,354 / 28,672 B, ~3,318 B free)** at v1.12 start and is likely similar/tighter now. A corrected algorithm path, a new adapter-required handler, a `CONFIG_VERSION`-bump recalibration path, or extra log strings can push Leonardo over 100% — the build fails (or links but corrupts). Uno has more headroom (~72%), so a change can pass on Uno and overflow only on Leonardo.

**Why it happens:**
Per-family fixes feel small; PROGMEM log strings + new dispatch arms accrete; the tightest board (Leonardo) is not always built first.

**How to avoid:**
- **Build `pio run -e leonardo` (not just `-e uno`) and check the flash % on every firmware change**; set a hard ceiling (v1.12 used ≤90% post-change) as a phase success criterion.
- Prefer host-side fixes where the gap allows (v1.11/v1.8 were host-only); push DB/classification corrections to `build_db.py` rather than firmware when possible.
- Reuse existing message IDs / `DBG_*` sub-IDs instead of minting new PROGMEM strings; the v1.2 message-ID rework exists precisely to conserve Leonardo flash.

**Warning signs:**
- Leonardo build flash % creeping toward 90%+.
- A change built only on Uno.
- New `LOG_*` / `MSG_*` strings added casually.

**Phase to address:**
Any firmware-touching phase (per-family fix, adapter-required impl, 999.1 fix) — flash-% ceiling as an explicit success criterion. Re-check at milestone close.

---

### Pitfall 8: Lockstep / codegen drift — py3.12-masks-CI-py3.11 + dual-repo wire changes

**What goes wrong:**
Two recurring traps from prior firmware-touching milestones:
1. The devcontainer runs **Python 3.12** but CI targets **3.9/3.11**; `ruff check` / `ruff format --check` and the codegen drift gate pass locally on 3.12 yet fail in CI. F-string backslashes + non-ruff-clean codegen output are the classic offenders.
2. Any wire change (new message ID, changed command field) must be **edited in the meta-repo catalog only** and synced to both sub-repos (`sync_to_subrepos.sh` / `messages.toml`); editing one sub-repo directly desyncs firmware↔host and the codegen drift gate (`<regen> && git diff --exit-code`) fails — or worse, a silent host/fw mismatch ships.

**Why it happens:**
The local toolchain masks the CI toolchain; lockstep is a manual discipline; the codegen emitter is now ruff-clean (Phase 63) so hand-normalizing reintroduces drift.

**How to avoid:**
- **Validate `ruff check` + `ruff format --check` against the CI Python (3.11), not the devcontainer 3.12,** before claiming green (use the source-built 3.11.13 per the v1.12 D-04 pattern).
- Edit wire/catalog definitions in the **meta-repo only**; regenerate; commit generated files; let the drift gate confirm byte-identity in both repos. Do **not** hand-normalize codegen output.
- Bump the firmware version and cut a real firmware pre-release tag this milestone (firmware changed) — don't reuse a skipped-lockstep tag.
- Two pre-existing `test_*` I001 ruff-debt errors are unrelated — don't chase them as new regressions.

**Warning signs:**
- Local CI-equivalent checks green but GitHub CI red on ruff/codegen.
- A `messages.py` / generated-header diff in only one repo.
- Host raises/handles a message ID the firmware never emits (or vice versa).

**Phase to address:**
Any wire-touching phase (catalog/codegen first, before firmware emits the new value — the v1.12 ordering: GATE → WIRE → FIRMWARE → HOST). Milestone-close/beta-cut phase for the lockstep tag + CI green.

---

### Pitfall 9: Bench-protocol safety — sideload-with-chip-seated, wrong shield rev, wrong port

**What goes wrong:**
Three operator-bench hazards that corrupt results or damage hardware:
1. **Sideloading firmware to a Uno-class board (Uno or uno328pb) with a chip seated** drives the shield bus during upload and can damage the chip. (Leonardo is EXEMPT — its upload does not drive the shield bus.)
2. **Assuming the shield revision** — Rev 2.2 / Rev 2.0 / modified Rev 0 are operator-owned and **indistinguishable by the EEPROM `hw_revision` byte**; the wrong-rev assumption silently attributes a Rev-0 read fault (or a Rev-2.0 Bug B) to the algorithm under test.
3. **Trusting a stale port→board mapping** — `/dev/ttyACM*` / `ttyUSB*` numbers shuffle across every USB replug / board cycle / chip re-seat; a result gets recorded against the wrong board.

**Why it happens:**
These are physical-world facts the firmware/host cannot enforce; they rely on operator discipline and are easy to skip under time pressure.

**How to avoid:**
- **Chip OUT of the socket before any Uno-class sideload** (Uno + uno328pb only; Leonardo exempt). Codified as `feedback_chip_out_before_sideload`.
- **ASK the operator which silkscreen rev is on the bench** at the start of any bench task; never infer it from EEPROM. Codified as `user_shield_revisions`.
- **Verify `controller:` identity per port at every bench task start** (re-handshake; confirm board name on the port you're about to drive). Codified as `feedback_verify_port_identity_each_task`.
- Record board + rev + port + chip state in every matrix row so a mis-attribution is auditable after the fact.

**Warning signs:**
- A bench plan that sideloads without an explicit chip-out step.
- Results recorded with a board name but no per-task identity re-verification.
- A read fault that "moves" between boards across a session (almost always a port-shuffle mis-attribution).

**Phase to address:**
Every bench-gated phase — encode chip-out, ask-rev, and verify-port as standing preconditions in the harness/matrix and in each bench plan's checklist.

---

### Pitfall 10: Over-claiming the gap set — re-deriving "feasible-but-unimplemented" without grounding

**What goes wrong:**
The milestone re-researches the protocol landscape to surface genuine gaps (revisiting v1.12's "the feasible set is already complete" finding). Risk: a phase commits to "implementing" a protocol that is in fact infeasible on RURP (e.g. `0x11` FWH = LPC-serial/3.3 V; `0x2A/0x2B/0x2C` = GAL/PLD/MCU with zero DIP memory chips) — wasting a firmware-touching phase (flash budget!) on a non-deliverable, or scaffolding a handler that becomes a future wrong-VPP hazard.

**Why it happens:**
"Unimplemented" reads as "missing feature" rather than "deliberately excluded as infeasible". The v1.11/v1.12 source-grounded findings are easy to re-litigate without re-citing them.

**How to avoid:**
- Ground any "new gap" claim in the **v1.11 field dictionary + minipro source**, not the bare `protocol_id` list; re-use the v1.12 classification (implemented / infeasible-on-RURP). The named-infeasibility arms (`configure_not_implemented` for 0x11/0x2A/0x2B/0x2C) already document the hardware reason in-code.
- Treat the **deferred erase path (`firestarter erase` 0x07)** as the most credible real gap candidate, but confirm it against the firmware's existing `eprom_internal_erase` (which drives VPE+A9 — a VPP hazard surface) before committing.
- For `adapter-required` chips, the gap is **physical (build/obtain the adapter)**; don't implement firmware for a chip the operator can't physically seat — keep it hardware-gated and deferrable (hybrid bench gating).

**Warning signs:**
- A proposed phase to "add support for protocol 0x11/0x2A/..." (infeasible).
- A new handler with no corresponding seated-chip test path.
- Re-opening the "feasible set" question without citing the v1.11/v1.12 source artifacts.

**Phase to address:**
The re-research / protocol-landscape phase (must reaffirm or overturn the v1.12 finding with citations before any gap-implementation phase is committed).

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Validate a family on uno328pb because it's on the bench | No board swap | Brownout (999.2) / stale-R1 (999.1) confounds → phantom bugs or false fails | Read-only/dispatch observation only; **never** for program/write |
| Trust a single post-write verify read | Fast | A jittery board manufactures a false PASS or FAIL | Only on the clean Leonardo verify board, and even then a negative control is mandatory |
| Hand-craft JSON to exercise a family bypassing the host guard | Tests firmware path directly | Re-opens the v1.12 wrong-VPP hazard (no `resolve_chip` refusal) | Only with the chip OUT of the socket |
| Add a new PROGMEM log string for diagnostics | Easier debugging | Pushes Leonardo flash toward overflow | Reuse `DBG_*` sub-IDs; add new strings only after checking Leonardo flash % |
| Hand-normalize codegen output to satisfy local ruff | Local green | Reintroduces py3.12↔3.11 drift; CI red | Never — the emitter is already ruff-clean (Phase 63) |
| Mark a family "validated" without a negative-control verify | Faster matrix fill | Vacuous PASS ships a verify that can't fail | Never |
| Skip live R1/R2 readback at bench-task start | One fewer step | VPP results become measurement artifacts (999.1) | Never on a VPP-dependent (UV-EPROM / Intel-flash) task |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Firmware ↔ host wire (messages.toml) | Editing a sub-repo catalog directly | Edit meta-repo only; sync to both; let codegen drift gate confirm byte-identity |
| Host↔fw data path (write/verify) | Assuming read-path bench coverage implies write/verify coverage | Exercise the **host→fw** chunk path on hardware explicitly (the v1.10 overflow bug hid here for a milestone) |
| Chip ↔ programmer VPP | Trusting firmware-reported VPP | Reconcile against a multimeter at the socket the first time per board; confirm live R1/R2 |
| Verify oracle ↔ read path | Using the same suspect board to read-verify a write | Pin verify to Leonardo + clean shield; advisory-only elsewhere |
| DB classification ↔ firmware dispatch | Re-promoting an `adapter-required` / `vpp-exceeds-max` chip to a real handler | Keep GATE-03 / `check_dispatch.py` green; safety-review any re-promotion |

## Performance Traps

(Not a scale-of-users domain; "scale" here = chip size, retry counts, per-byte serial traffic.)

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| In-program retry convergence masks marginal programming | High `MSG_INFO_RETRIES` count, PASS that won't reproduce on re-read | Use independent N≥5 read as the oracle; record retry counts | Marginal cells / jittery read board |
| Full-buffer chunk exceeds firmware decode cap | `Data error: -2` at first chunk | Host `MAX_DATA_CHUNK = BUFFER_SIZE-2` (fixed v1.10) — keep the lockstep test pinning the MAX on-wire chunk | If a future change re-touches chunk sizing without re-running the MAX-chunk test |
| Intel-flash / EEPROM poll timeout vs slow chip | `MSG_ERR_INTEL_SR_TIMEOUT` / `MSG_ERR_EEPROM_TIMEOUT` on a healthy chip | Validate poll timeouts against datasheet t_prog before calling it an algorithm bug | Slow/old silicon at the edge of the hardcoded timeout |

## Security Mistakes

(Physical-safety analog — "what could destroy hardware or corrupt an image".)

| Mistake | Risk | Prevention |
|---------|------|------------|
| `--force` to push past a VPP / chip-ID warning on a seated chip | Drives unsafe VPP / wrong-chip program → dead chip | Never `--force` a seated chip in validation; investigate the warning first |
| Bypassing host `resolve_chip` refusal via raw JSON | Re-opens silent wrong-VPP fallback | Only chip-out for raw-JSON firmware-path tests |
| Assuming the safety VPP check is reliable | A miscalibrated divider can pass a destructive voltage | Verify calibration (R1/R2) + meter before trusting the check |
| Wrong control-register bits in a new handler | VPP on the wrong socket pin | Native test asserting register sequence + chip-out meter dry-run |

## "Looks Done But Isn't" Checklist

- [ ] **Family "validated":** Often missing the negative control — verify a deliberately-wrong file mismatches at a specific address, and a blank/chip-out read fails.
- [ ] **Write PASS:** Often missing the independent post-write full read (SHA-256) — confirm verify isn't reading the in-memory write buffer.
- [ ] **VPP-dependent result:** Often missing the live R1/R2 readback + meter reconcile — confirm it's not a 999.1 artifact.
- [ ] **Firmware change:** Often missing the `-e leonardo` build + flash-% check — Uno-only builds hide Leonardo overflow.
- [ ] **Wire change:** Often missing the CI-Python (3.11) ruff/codegen check + both-repo sync — devcontainer 3.12 masks it.
- [ ] **Bench result:** Often missing per-task port-identity re-verification + recorded shield rev — port shuffle / wrong-rev mis-attribution.
- [ ] **"New gap" to implement:** Often missing the v1.11/v1.12 source-grounded feasibility citation — may be an infeasible protocol.
- [ ] **uno328pb cell in the matrix:** Often mislabeled "fail" when it's N/A (999.2 brownout / read-unreliable).

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| False PASS shipped (corrupt image believed good) | HIGH | Re-validate the family on Leonardo with independent read + negative control; invalidate prior matrix rows from the suspect board |
| Chip destroyed by wrong VPP/algorithm | HIGH (physical) | Stop bench; root-cause the routing (register bits / DB classification / calibration); add the missing chip-out VPP dry-run gate before resuming |
| 999.1 stale-R1 misattributed as algorithm bug | LOW | Read-back R1; recalibrate; re-run on corrected board (or switch to Leonardo) |
| 999.2 brownout misrecorded as failure | LOW | Re-label matrix cell N/A; re-run on Leonardo |
| Leonardo flash overflow | MEDIUM | Revert/trim PROGMEM strings; move fix host-side if possible; reuse DBG sub-IDs |
| Lockstep wire desync | MEDIUM | Re-sync from meta-repo catalog; regenerate; re-run drift gate in both repos |
| Wrong-rev / wrong-port mis-attribution | LOW–MEDIUM | Re-verify identity + rev with operator; re-run the affected matrix rows |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| 1. Untrustworthy verify board | Harness/matrix phase (PASS = Leonardo verify) | Matrix schema pins verify oracle; advisory-only flag on other boards |
| 2. Wrong VPP / wrong algorithm | Per-family validation + per-family-fix / adapter-impl phases | Chip-out VPP meter dry-run precedes seated write; register-bit native test; GATE-03 green |
| 3. Stale-R1 calibration (999.1) | Harness phase precondition (+ optional 999.1 firmware-fix phase) | Live R1/R2 readback + meter reconcile recorded per board |
| 4. uno328pb brownout (999.2) | Harness phase (board-eligibility column) | uno328pb = N/A for program/write in matrix |
| 5. Stale/cached verify buffer | Harness phase (PASS definition) | Independent read-then-SHA + passing negative control per family |
| 6. Clean read masks bad write | Harness + per-family validation | Retry-count captured; PASS = independent N≥5 read |
| 7. Leonardo flash overflow | Every firmware-touching phase | `pio run -e leonardo` flash % ≤ ceiling as success criterion |
| 8. Lockstep / codegen drift | Wire-touching phase (catalog→fw→host order) + close phase | CI-3.11 ruff/codegen green; both-repo byte-identity; real fw tag at cut |
| 9. Bench-protocol safety | Every bench-gated phase | Chip-out + ask-rev + verify-port preconditions in each bench plan |
| 10. Over-claiming the gap set | Re-research / protocol-landscape phase | Feasibility claims cite v1.11 field dictionary + minipro source |

## Sources

- Firmware program/verify source: `firestarter/src/proms/eprom.cpp` (in-program verify loop `verify_and_update_mask`, `eprom_check_vpp` VPP safety gate, `eprom_internal_erase` VPE/A9 hazard), `flash_intel.cpp` (SR polling, VPP P1 routing), `eeprom_28c.cpp` (DQ7/data-poll, A9-12V chip-ID, `mem_size<64` underflow guard) — HIGH
- `.planning/debug/firmware-vpp-misread.md` — 999.1 stale-EEPROM-R1 / CONFIG_VERSION-not-bumped diagnosis (6.8× under-read, program stall) — HIGH
- `.planning/debug/write-verify-datapath-overflow.md` — host→fw data-path coverage gap; verify negative-control ("0xff != 0x03") precedent — HIGH
- `.planning/PROJECT.md` v1.13 scope + v1.12 fail-closed dispatch archive + Known Gaps; `.planning/STATE.md` flash budget, lockstep pitfalls, deferred items — HIGH
- v1.9 Phase 44 RCA (Rev 0 read-strobe-causal read fault) + Bug B (Rev 2.0) characterization; uno328pb bench-instability + brownout records (project memory) — HIGH
- `firestarter/CLAUDE.md` dispatch table + native-test "asserts pointers, not register side effects" note; v1.12 STATE pitfalls (py3.12-masks-3.11, messages.toml meta-only, ≤90% Leonardo flash) — HIGH
- Operator bench protocol memory: `feedback_chip_out_before_sideload`, `user_shield_revisions`, `feedback_verify_port_identity_each_task`, `reference_vpp_vpe_no_socket_routing` — HIGH

---
*Pitfalls research for: write/program/verify validation + gap implementation on the Firestarter RURP programmer*
*Researched: 2026-06-16*

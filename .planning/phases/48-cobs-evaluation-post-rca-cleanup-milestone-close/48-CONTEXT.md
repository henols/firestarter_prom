# Phase 48: COBS Evaluation + Post-RCA Cleanup + Milestone Close - Context

**Gathered:** 2026-06-01
**Status:** Ready for planning

<domain>
## Phase Boundary

The v1.9 close phase. Three independent workstreams:

1. **COBS-01** — a serial-data-path robustness *evaluation*, ending in a written adopt/defer/reject decision. **Evaluation only — adopting any framing layer is an explicit non-goal** (future milestone).
2. **TYPE-01** — lift the `eprom_operations.py` mypy strict-mode overrides deferred in v1.8 (Phase 42 D-07, GATE-1.8d read-path ring-fence), now that the read path is fixed and free to touch. **Hard-gated on Phase 46.**
3. **Milestone close** — MILESTONES.md v1.9 entry + branch promotion + coordinated beta tag.

Sequencing caveat captured during discussion: this phase was discussed ahead of Phases 45→46→47 (we are at Phase 44 complete). COBS-01 is fully decidable now and independent of the hardware RCA. TYPE-01 cannot start until Phase 46 ships (read path fixed). Milestone-close specifics are conditional on the Phase 46/47 fix + acceptance outcome.
</domain>

<decisions>
## Implementation Decisions

### COBS-01 — Serial Robustness Evaluation
- **D-01: Verdict on PacketSerial-the-library = REJECT (locked, not re-openable).** RAM-blocked on Uno (current baseline ~553 B free; PacketSerial's `send()` builds a full ~516 B COBS copy → buffer collision), requires a coordinated dual-repo rewrite of `rurp_serial_utils.cpp` + `serial_comm.py` + the `test_messages` frame contract, and risks `0x00`-delimiter collisions with bus-driven `0x00` under `SERIAL_ON_IO` bus-aliasing. Do **not** re-litigate PacketSerial.
- **D-02: Re-open the robustness investigation FROM SCRATCH — survey lightweight alternatives.** Do **not** merely formalize the 2026-05-27 todo. The deliverable is a fresh comparative survey of *lightweight* serial-framing/automatic-resync mechanisms (PacketSerial **excluded**). The genuine win being chased is automatic resync (a garbled byte corrupts only one packet and re-syncs on the next delimiter instead of desyncing until the 2 s timeout).
- **D-03: No preset candidate list — researcher surveys the field.** User has no specific packages in mind ("there are so many"). Researcher enumerates and compares lightweight options (e.g. SLIP/RFC-1055 byte-stuffing, a hand-rolled streaming/in-place COBS encoder with no library, `min`, `SerialTransfer`, and any others found) on a level playing field.
- **D-04: BINDING FILTER = must fit the Uno.** Any candidate that could plausibly be adopted (in a future milestone) MUST fit the Uno RAM budget — no second ~512 B encode buffer; must stream or encode in-place. The `0x00`-vs-bus-aliasing concern under `SERIAL_ON_IO` is a secondary correctness filter. Anything that fails the Uno fit is filtered out, however attractive on a Leonardo.
- **D-05: Expected outcome = reject-library / defer-the-resync-concept, but genuinely re-derivable.** The from-scratch survey is expected to confirm "no lightweight option is worth adopting now; keep the resync concept as a future-milestone candidate," but the evidence drives the verdict — if a lightweight Uno-fitting mechanism surfaces, the adopt/defer line may move. Keep the existing CRC8-CCITT integrity layer regardless (any candidate must coexist with it; PacketSerial has no checksum).
- **D-06: Decision doc home = standalone `.planning/v1.9-COBS-DECISION.md`** (ADR-style), cross-referenced from the v1.9 MILESTONES entry. Records the survey, the per-candidate Uno-fit analysis, and the adopt/defer/reject verdict + rationale against the *post-v1.8* serial-path shape. *(Default chosen by Claude — user picked "re-open" over the doc-home options; standalone doc best fits a from-scratch comparative survey.)*

### TYPE-01 — Lift the eprom_operations.py mypy ring-fence
- **D-07: Target = FULL strict parity.** Move `firestarter.eprom_operations` out of the non-strict-silenced override block (`pyproject.toml` ~L151) into the Phase-42 strict-island block (~L131), alongside the other 8 v1.8 modules. Fix all surfaced type errors; aim for zero residual ignores. `tools/check_mypy_watermark.py` tracks the count.
- **D-08: Strictly behavior-preserving.** Type fixes must NOT change any runtime semantics — annotations/casts/guards only. The existing characterization + pytest suite must stay green with zero output changes, and the read-path bytes (`_read_and_parse_lines`, GATE-1.8d) must remain identical. **Escape hatch / reconciliation with D-07:** if a strict fix would require changing behavior, prefer a single documented, individually-justified `# type: ignore[code]` over altering logic. So the order of preference is: (1) behavior-preserving annotation, else (2) documented residual ignore — never (3) logic change.
- **D-09: Hard-gated on Phase 46.** Do NOT start TYPE-01 until the read path is fixed (Phase 46 ships). This is the original reason for the GATE-1.8d ring-fence.

### Branch Promotion & Milestone Close
- **D-10: Coordinated lockstep beta tag.** Cut a single coordinated beta tag (e.g. `3.0.0b8`) on BOTH sub-repos together, restoring lockstep after v1.8's host-only `3.0.0b7`. Both firmware (P44 read-timing knobs + P46 fix) and host (P44 knob params, TYPE-01, fix) changed in v1.9, so both ship.
- **D-11: Beta-only promotion — stable is operator-gated.** "Nothing is stable until I say so." Promotion target is the **beta channel only**: sub-repos merge to `beta`; meta merges to `main` (where `.planning/` lives). **No stable `3.0.1` promotion this milestone** — stable is a manual operator decision, never automatic at close. (This resolves the skipped "Stable 3.0.1 vs beta" area: defer stable.) See `[[stable-release-operator-gated]]`.
- **D-12: Beta promotion is NOT hard-gated on a perfect acceptance pass.** Cut the beta tag at close with caveats noted in MILESTONES even if the Phase 47 N≥5 gate isn't fully green on every shield — beta is the right channel for "fix landed, not fully gate-proven." Reserve the acceptance gate for the eventual operator-authorized stable cut.

### Claude's Discretion
- COBS decision doc internal structure / ADR format (D-06 sets the file; format is open).
- Exact beta tag number (`3.0.0b8` assumed as the next in sequence; confirm against actual prior tags at cut).
- MILESTONES.md v1.9 entry structure (must cover RCA findings, fix summary, acceptance result, COBS decision per success criterion #3).
- Execution order of the three workstreams (COBS-01 can run anytime; TYPE-01 after P46; close last).

### Folded Todos
- **`serial-cobs-resync-data-path.md`** (medium, COBS-01, resolves_phase: 48) — folded as the *input substrate* for D-02's from-scratch survey, NOT as the answer. Its on-the-wire framing map (4 framings on one 250000-baud line), Uno RAM/flash baselines, and `SERIAL_ON_IO` aliasing analysis are starting evidence to re-verify against the current codebase; its PacketSerial conclusion is promoted to the locked D-01 reject.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & Roadmap
- `.planning/REQUIREMENTS.md` — COBS-01 + TYPE-01 definitions and the explicit non-goals (no COBS adoption; no protocol migration this milestone).
- `.planning/ROADMAP.md` — Phase 48 success criteria (4 criteria); dependency on Phases 46/47.

### COBS-01 substrate
- `.planning/todos/pending/serial-cobs-resync-data-path.md` — the 2026-05-27 investigation: wire-framing map, Uno RAM/flash baselines, PacketSerial cost analysis, `SERIAL_ON_IO` aliasing risk. Re-verify every load-bearing claim against current code.
- `firestarter/src/boards/rurp_serial_utils.cpp` — data-block framing (`[len_u16][xor][payload]`, 2 s timeout) + log/telemetry framing (`[0xAA55AA55][len_u16][id][params][crc8][0x0A]`).
- `firestarter/src/firestarter.cpp` — host→fw command intake (ASCII JSON, peek for `{`).
- `firestarter_app/firestarter/serial_comm.py` + `firestarter_app/firestarter/frame_parser.py` — host-side demux of all framings; CRC8 table; must stay byte-synced with firmware (lockstep mandate in root CLAUDE.md).
- Uno RAM/flash watermark — re-measure via `pio run -e uno` (todo recorded RAM 73.0% = 1495/2048, ~553 B free; Flash 68.6%, ~10 KB free).

### TYPE-01 substrate
- `firestarter_app/pyproject.toml` — mypy override blocks: strict-island (~L117/L131) and non-strict-silenced (~L147/L151, where `firestarter.eprom_operations` currently lives).
- `firestarter_app/firestarter/eprom_operations.py` — the module to lift; contains the GATE-1.8d read path.
- `firestarter_app/tools/check_mypy_watermark.py` — the full-gate watermark tracker.
- `firestarter_app/CLAUDE.md` — host conventions; lockstep rule for serial files.

### Milestone close & branching
- `.planning/MILESTONES.md` — v1.9 entry target (success criterion #3); §v1.8 / §v1.6 as close-format precedents.
- `[[feedback_branching]]` / `[[stable-release-operator-gated]]` — branch model (sub-repos→beta off beta tips, meta→main) and the operator-gated stable rule.
- `.planning/STATE.md` — Accumulated Context (GATE-1.8d ring-fence, baseline binaries, branch model).
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- The 4-framing serial stack + CRC8-CCITT integrity layer is the baseline any COBS candidate must coexist with (CRC8 stays).
- The 8-module Phase-42 strict-island in `pyproject.toml` is the exact template TYPE-01 extends — same override block, one more module name.
- v1.8 §MILESTONES and v1.6's "diagnostic + revert" close are format precedents for the v1.9 entry.

### Established Patterns
- Serial framing changes are dual-repo lockstep (`rurp_serial_utils.cpp` ↔ `serial_comm.py`/`frame_parser.py`), pinned by the `test_messages` native suite — relevant to scoping any COBS adoption cost (and why adoption is out of scope here).
- Uno is the binding RAM constraint for all firmware-side serial work (512 B data buffer; ~553 B free).

### Integration Points
- TYPE-01 touches only `pyproject.toml` + `eprom_operations.py` (+ possibly watermark count); must not perturb the read-path bytes.
- COBS-01 produces a doc only — no code change this milestone.
</code_context>

<specifics>
## Specific Ideas

- COBS-01 reframed by the user mid-discussion: "start from the beginning, but exclude PacketSerial and investigate some more lightweight packages" — and "it must fit the UNO." This is the defining constraint pair: fresh survey, PacketSerial out, Uno-fit mandatory.
- "Nothing is stable until I say so" — stable promotion is operator-only; beta is the default channel.
</specifics>

<deferred>
## Deferred Ideas

- **Adopting any COBS/lightweight-framing layer** — explicit non-goal of v1.9 (REQUIREMENTS.md). If D-05 lands "defer," it becomes a candidate for a future protocol-quality milestone (borrow automatic-resync into the existing length-prefixed path, keep CRC8).
- **Stable `3.0.1` promotion** — deferred to operator authorization (D-11); not cut at this milestone close.

### Reviewed Todos (not folded)
- `avrdude-mcu-detection-fallback.md` (low) — out of v1.9 scope; carry forward.
- `w27c512-eeprom-misclassification.md` (HIGH) — DB content fix, out of v1.9 scope; separate track.
</deferred>

---

*Phase: 48-cobs-evaluation-post-rca-cleanup-milestone-close*
*Context gathered: 2026-06-01*

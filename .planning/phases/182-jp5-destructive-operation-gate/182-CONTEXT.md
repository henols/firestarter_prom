# Phase 182: JP5 Destructive-Operation Gate - Context

**Gathered:** 2026-09-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Stop the host tool from routing VPP onto socket pin 1 of a part whose pin 1 is A19, by
**correcting the chip→pin-map assignment at the generator** rather than by building a warning on
top of a database that is wrong. Then let the shield schematic decide whether a residual
operator-facing warning is still owed for the part the tool cannot see — the JP5 solder jumper.

**In scope:** `firestarter_app/tools/build_db.py` (`resolve_pinout_key` 32-pin arm),
`firestarter_app/firestarter/data/pinouts.json` (one new layout), the regenerated
`chip_database.json`, retirement of `MAX_27C020_SIZE` and its self-comparing parity test, the
SAFE-03 schematic/VPP-path trace, deletion of the dead JP5 renderer (SAFE-05), and — **only if the
trace requires it** — a damage-scoped confirmation gate.

**Out of scope:** detecting JP5's physical state (impossible — it is a solder jumper); the shield
photographs, per-revision jumper tables and the `firestarter info` jumper-block rewrite (their own
phase, decided D-06); any firmware change; the wider pin-map audit (D-07).

</domain>

<decisions>
## Implementation Decisions

### The affected-part predicate — corrected at the source, not invented

- **D-01:** SAFE-01's literal wording ("the pin map puts A19 on socket pin 1") is **not
  satisfiable against the database as it stands** — measured 2026-09-10: no pin map in
  `pinouts.json` declares A19 at all, and all eight 1 MB (8 Mbit) rows sit on `DIP32_STD`, which
  declares 19 address lines (A0–A18) and `vpp-pin: [1]`. The phase does **not** work around this
  with a synthetic predicate (address-line shortfall, size threshold, or the 291-row
  VPP-on-pin-1 set were all considered and rejected). It **fixes the pin map so SAFE-01 becomes
  literally true**, and the gate predicate is then the requirement's own words.
  — **Reversibility:** costly — the new pinout key enters both `pinouts.json` and the generated
  `chip_database.json`; reverting means another full regeneration, and any user override in
  `~/.firestarter/database.json` written against the new key is stranded.

- **D-02:** The fix is **rule-shaped, with no per-part special case**. `resolve_pinout_key`
  already dispatches on infoic's `variant_lo` for `pin_count == 24` and `pin_count == 28`; it
  abandons the field only at `pin_count == 32`, substituting a hand-tuned size threshold. The
  32-pin arm dispatches on `variant_lo` like the other two widths:

  | infoic `variant` | `code_memory_size` | family | pin 1 | pinout key |
  |---|---|---|---|---|
  | `0x01` | 256 KB | 27C020 class | VPP | `DIP32_27C020` (pin 31 = PGM) |
  | `0x02` | 512 KB | 27C040 class | VPP | `DIP32_STD` (pin 31 = A18) |
  | `0x03` | **1 MB** | 27C080 / M27C801 | **A19** | **new layout — to be authored** |

  All three sit at `pin_map=0x000c`, `protocol_id=0x08`. A future 8 Mbit part added upstream
  carries `variant=0x03` and is classified correctly with **no generator edit** — which is the
  standing requirement on this generator.
  — **Reversibility:** costly — same regeneration cost as D-01.

- **D-03:** `MAX_27C020_SIZE` and `tests/test_revision_constants_parity.py`'s
  `MAX_27C020_SIZE` arm are **retired**. Verified 2026-09-10: the constant exists only in
  `firestarter_app`; the test's docstring cites
  `firestarter/include/firestarter.h #define MAX_27C020_SIZE 262144`, which **does not exist** —
  the assertion compares the host constant to a literal copy of itself. Retiring it is host-only,
  so the milestone's "firmware at the edges only" constraint holds.
  — **Reversibility:** reversible.

- **D-04:** The `chip_database.json` diff is **the output of a `build_db.py` re-run**, never a
  hand edit — the standing rule (milestone D-6), which applies here for the same reason: a hand
  edit is silently reverted by the next regeneration and does not fix the other parts sharing the
  decode path.
  — **Reversibility:** reversible.

### The gate — evidence-gated, damage-scoped

- **D-05:** Whether a warning gate ships **at all** is decided by the SAFE-03 trace that this
  phase produces, not before it. The operator's expected outcome is that **the map fix supersedes
  the gate** — once the tool stops asking for VPP on pin 1, our contribution to the hazard is
  gone. If the trace confirms that JP5-bridged with VPP unasserted cannot damage the part,
  **SAFE-02 and SAFE-04 are formally retired in `REQUIREMENTS.md` with the trace as the recorded
  reason**, and the phase ships the map fix plus SAFE-05 only. If the trace shows otherwise, a
  gate ships under D-06 and D-07 below.
  — **Reversibility:** reversible.

- **D-06:** **If** a gate ships, it fires **only on operations that can physically damage the
  part**. Operations that merely return or write wrong data are explicitly **not** gated —
  correctness is the map fix's job, not the gate's. The damage-capable set is defined by the
  SAFE-03 trace, not by inference.
  — **Reversibility:** reversible.

- **D-07:** **If** a gate ships, its escape hatch is: an interactive **question to continue**;
  `-f`/`--force` **does not** satisfy or bypass it; and — since no substitute flag was authorised
  — SAFE-04's only remaining branch applies, so a **non-interactive invocation refuses** (no TTY,
  piped stdin, `dev test`, `--auto`/`--chain`). Never a default-yes. Reusing `--force` was
  rejected explicitly: gh#62 is a reporter reaching for `--force` to get past a refusal, and
  overloading it here rebuilds that trap.
  — **Reversibility:** costly — a non-interactive refusal is a CLI behaviour change that any
  existing script driving these parts would hit.

### Scope split

- **D-08:** SAFE-05 stays in this phase — `_get_rev2_2_jumper_settings_data`
  ([ic_layout.py:186-201](../../../firestarter_app/firestarter/ic_layout.py#L186-L201)) and its
  commented-out call site ([ic_layout.py:656](../../../firestarter_app/firestarter/ic_layout.py#L656))
  are deleted. It is a named requirement of Phase 182.
  — **Reversibility:** reversible.

- **D-09:** The shield photographs, the per-revision jumper configuration tables, and the
  `firestarter info` jumper-block rewrite (per-pin-map derivation replacing the pin-count
  heuristic, corrected JP4 labels, and an explicit "this jumper does not matter for this chip"
  line) are a **separate phase**, published to the `firestarter_prom` wiki plus the `info` output.
  Not Phase 182.
  — **Reversibility:** reversible.

### Claude's Discretion

- The name of the new 32-pin layout key. `DIP32_27C801` follows the established
  `DIP32_27C020` / `DIP32_SST39SF040` convention (exemplar part number); the planner may settle it.
- Whether the SAFE-03 trace is written as a standalone note under `.planning/notes/` or inline in
  the phase `SUMMARY.md`. It must be citable by Phase 187's gh#60 reply either way.
- How the retired `MAX_27C020_SIZE` parity arm is disposed — deleted outright, or replaced by a
  test that asserts something real about the 32-pin dispatch.

### Folded Todos

Both todos carrying `resolves_phase: 182` were folded, one of them **split**:

- **`delete-jp5-dead-renderer`**
  (`.planning/todos/pending/delete-jp5-dead-renderer.md`) — folded whole. It *is* SAFE-05: delete
  `_get_rev2_2_jumper_settings_data` and the commented call, which present the `A19_CUT` solder
  jumper as an operator-settable Rev 2.2 config header.
- **`fix-jp4-labels-and-rev2-revision-block`**
  (`.planning/todos/pending/fix-jp4-labels-and-rev2-revision-block.md`) — **split**. Its item 3
  (delete the dead renderer) is SAFE-05 and lands here. Its items 1 and 2 (JP4's meaningless
  `"28pin"`/`"32pin"` labels; relabelling the Rev-2 block from `"2.0 & 2.1"` to cover 2.0–2.3)
  move to the Phase D-09 `info` rewrite, because the photographs now show JP4's own silkscreen
  already states the condition the rewrite must reproduce — *"Only for ROMs with VPP on P1."*
  **The todo's `resolves_phase: 182` tag needs re-pointing once the D-09 phase has a number.**

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Hardware ground truth — settles SAFE-03's hardware half

- `.planning/phases/182-jp5-destructive-operation-gate/evidence/shield-rev2-jp4-jp5.jpg` —
  **Rev 2 board, operator-photographed 2026-09-10.** Silkscreen, verbatim: *"JP4: Open for 32 pin
  ROMs, Closed for 28 pin ROMs (Only for ROMs with VPP on P1)"* and *"JP5: Cut for ROMs with A19
  on P1"*. This is the authoritative statement of the affected class and it is printed on the
  hardware. Note the JP5 instruction is **unconditional** — it does not say "cut if VPP is
  asserted".
- `.planning/phases/182-jp5-destructive-operation-gate/evidence/shield-rev2.2-jp4-jp5-jp6-jp9.jpg` —
  **Rev 2.2 board.** Same JP4/JP5 silkscreen, plus JP6/JP7 (`5V`/`5V_REG`), JP8 (`VPE`), JP9 and
  TP1 — jumpers absent from the current `info` renderer entirely.
- `.planning/phases/182-jp5-destructive-operation-gate/evidence/shield-rev0-modified-jp1-jp2-jp3.jpg` —
  **Modified Rev 0 board.** Carries the JP1/JP2/JP3 table: `24pin → B to 5V` · `28pin → A to 5V, B
  to A13` · `32pin → B to A13, A to A17*` · `VPP alt → Pin1 VPP to C* or D*` · `* = If needed`.
  Cut-and-jumper rework visible. **This board had never been physically photographed** in the
  project record before now — it closes a standing evidence gap, and it is the only board whose
  identity `hw_revision` cannot distinguish.
- `.planning/v1.7/upstream-rurp/hardware/RelativelyUniversalROMProgrammer.kicad_sch:26840` — JP5's
  KiCad record: value `A19_CUT`, footprint `Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm`
  — **bridged by default**. The photographs do not establish either board's *current* JP5 state,
  which is precisely why the tool cannot read it.
- `.planning/notes/jumper-display-ground-truth.md` — schematic-verified JP1–JP5 routing per
  revision, and the five confirmed defects in the current `ic_layout.py` derivation. §"What each
  jumper actually routes" and §"Chip-population impact".
- `.planning/v1.7-SHIELD-REVS.md` — per-revision electrical deltas. Note **JP4/JP5 do not exist on
  a Rev 0 board** and must not be searched for there.

### Generator and database

- `firestarter_app/tools/build_db.py` — `resolve_pinout_key` (the 32-pin arm is the defect;
  `MAX_27C020_SIZE` is imported at line 8 and used at line 271), `classify`, and `MINIPRO_XML_URL`
  (infoic pinned at commit `a8efaedc`).
- `firestarter_app/tools/DECODE-NOTES.md` — the decode rationale the generator's rules answer to.
- `firestarter_app/firestarter/data/pinouts.json` — the 15 layout definitions; `VALID_PINOUT_KEYS`
  is sourced from here. **`address-bus-pins` is an ordered A0..An list** — index *is* the address
  bit, which is how "A19 on pin 1" becomes expressible.
- `firestarter_app/firestarter/data/chip_database.json` — generated; 746 rows. Never hand-edit.
- `firestarter_app/firestarter/constants.py:49-51` — `MAX_27C020_SIZE`, to be retired.
- `firestarter_app/tests/test_revision_constants_parity.py:688-710` — the parity arm that compares
  the host constant to a literal copy of itself.

### Host surfaces

- `firestarter_app/firestarter/ic_layout.py:169-201` — `_get_rev2_jumper_settings_data` and the
  dead `_get_rev2_2_jumper_settings_data`; `:618-656` — the pin-count-keyed jumper derivation that
  currently prints **JP4 = Closed** for the 8 Mbit parts.
- `firestarter_app/firestarter/cli_handlers.py:512-913` — the six chip operations
  (`read`, `write`, `verify`, `blank`, `erase`, `id`) and `:2363` — `dev test`. `-f/--force`
  currently means "ignore a VPP or chip-id mismatch" on `blank`, `erase` and `id`.
- `firestarter_app/firestarter/cli_handlers.py:2299-2306` — `_is_interactive`. **Cross-phase
  hazard:** CLAIM-07 (Phase 185) removes it. If D-05 resolves to "gate ships", Phase 182 becomes
  its first live consumer and CLAIM-07 must be revisited; if D-05 resolves to "no gate", CLAIM-07
  is unaffected. The planner must not silently revive it.
- `firestarter_app/firestarter/submit.py:695-780` and `firestarter/firmware.py` — the established
  `rich.prompt.Confirm` + injectable `confirm_fn`/`isatty_fn` pattern, if a prompt is needed.

### Requirements and milestone

- `.planning/REQUIREMENTS.md` § SAFE — SAFE-01…05, and D-1…D-7 taken at activation.
- `.planning/PROJECT.md` § Current Milestone — the through-line and the five "does NOT do" bounds.
- `.planning/ROADMAP.md` §"Phase 182" and §"Phase 999.51" — the promoted backlog stub carrying the
  reporter's own words.
- [`henols/firestarter_prom#60`](https://github.com/henols/firestarter_prom/issues/60) — the
  originating report. Its two open questions are this phase's to answer.

### Standing project rules that bind this phase

- `/workspaces/CLAUDE.md` § "Source code comments — hard rule" — **no comments in product
  source, at all**, not overridable by a plan, task or skill. This binds the generator edit and
  any new pin-map entry.
- `firestarter_app/tools/` sits outside every CI gate — no mypy, no ruff check, no ruff format.
  A `build_db.py` change is not caught by CI.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`resolve_pinout_key`'s own 24- and 28-pin arms** are the pattern the 32-pin fix should copy —
  they already dispatch on `variant_lo` with a documented `# CRITICAL` note about not swapping
  `0x10`→27512 (VPP pin 22) and `0x11`→27256 (VPP pin 1), which is the same class of hazard.
- **`rich.prompt.Confirm` with an injectable `confirm_fn`/`isatty_fn`** (`submit.py:641,701`) is
  the established, test-friendly prompt pattern — no new mechanism needed if a gate ships.
- **The `WARN: resolved pinout key ... not in pinouts.json` guard** (`build_db.py:287`) already
  fails loudly on an unregistered key, so adding the new layout is self-checking.

### Established Patterns

- **The generator is a pure function of decoded minipro fields** — its own docstring: *"no per-IC
  names, no per-family tables"*. The `mem_size <= MAX_27C020_SIZE` threshold is the one place it
  breaks its own contract, which is exactly why it produced this defect.
- **`chip_database.json` is generated; `pinouts.json` is authored.** infoic's `<maps>` section was
  checked (lines 16717–17202, 121 records) and carries **only a GND pin and a masked-pin list —
  connectivity, no signal function**. It therefore *cannot* generate a layout definition. The
  chip→layout **assignment** is fully rule-derivable; the layout **definition** must still be
  authored once from the JEDEC pinout. Do not send a researcher looking for a pinout oracle in
  infoic — it is not there.
- **`support_status` and `programming.*` are generated fields.** Whether the eight 8 Mbit rows'
  `support_status` should change on regeneration was raised and not decided; treat any change as
  an output of the rules, not a target.

### Integration Points

- `resolve_pinout_key` → `pinouts.json` key registration → regenerated `chip_database.json` →
  `EpromDatabase.get_pin_map` → `ic_layout.py`'s jumper derivation **and** the RURP bus config the
  host sends to firmware. A new layout key propagates to all three.
- The eight affected rows: `AM27C080`, `AM27LV080`, `AT27C080`, `MX27C8000`, `MX27C8000A`,
  `UPD27C8001`, and `M27C801` (present **twice** — a duplicate worth noting to the planner).

</code_context>

<specifics>
## Specific Ideas

- **The hardware says it better than we do.** JP4's silkscreen already carries the "say when it
  does not matter" principle the operator asked for — *"Only for ROMs with VPP on P1."* Any
  operator-facing jumper text this project writes should be checkable against that sentence.
- **The open question research must settle before anything is buildable:** if pin 1 on an 8 Mbit
  part is A19, **where is VPP, and can the RURP shield reach it?** The Rev 2 pin labels break out
  A15, A16 (`P2 / A16`), A17 and A18 but **no A19**, and the shield exposes `"Pin 1" VPE Enable`,
  `VPE Enable (P24)`, `A9 VPE Enable` and `VPE_TO_VPP`. If the shield cannot deliver VPP to
  wherever the 27C801 wants it, these parts may be **read-only on this hardware** — which is
  itself the honest answer gh#60 deserves, and it changes what the new layout can claim.
- **The evidence photographs are 900×1600 / ~250 KB each**, downscaled from ~15 MB originals
  (44 MB total, too large for the meta repo). Silkscreen legibility was verified after
  downscaling. Originals remain outside `.planning/` at `/workspaces/tmp/` and are **not
  preserved by any commit** — the D-09 wiki phase will want them re-exported at publication
  resolution before that directory is cleared.

</specifics>

<deferred>
## Deferred Ideas

- **The wider pin-map audit** — offered and declined for Phase 182. Two further classes of the
  same defect were measured 2026-09-10 and are real:
  - `AT27C011`, `D27011`, `D27C011` — 128 KB parts on `DIP28_2764`, which supplies **14** address
    lines. Not a damage path (their pin 1 genuinely is VPP) but they can address only 16 KB.
  - 18 rows on `DIP32_28C512_EEPROM` (`AT28C010`, `AT28C040`, `AT28MC040`, `CAT28C040`, `WE512K8`
    and others) — up to 512 KB against **16** address lines.
  Worth a backlog item: a fail-closed generator assertion that every row's `size_bytes` fits the
  address lines its layout declares. That check would have caught the 8 Mbit defect at build time.
- **Silently-wrong 8 Mbit reads with JP5 bridged.** If the SAFE-03 trace concludes "no damage",
  the correctness failure remains: an 8 Mbit read would alias or return garbage above 512 KB, and
  a `verify` against it would pass for the wrong reason. Explicitly **not** gated per D-06.
  Capture as its own item if the trace confirms it.
- **The D-09 phase itself does not exist yet.** Shield photographs + per-revision jumper tables on
  the `firestarter_prom` wiki, and the `info` jumper-block rewrite. It needs inserting into
  `.planning/ROADMAP.md` — noting Phase 187 (Answered Reports) must stay last, so the new phase
  slots **before** it.
- **`REQUIREMENTS.md` needs two edits from this discussion** (not made here — discuss-phase does
  not mutate requirements): SAFE-01's wording should reflect that the predicate is achieved by
  correcting the pin map rather than by deriving around it, and SAFE-02/SAFE-04 should be marked
  **conditional on the SAFE-03 trace** per D-05.

### Reviewed Todos (not folded)

The `todo.match-phase` scan surfaced six further pending todos on keyword overlap alone
(`skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads`,
`2026-08-27-safe-state-outputs-on-powerup-and-fault`,
`config-version-not-bumped-strands-stale-eeprom-calibration`,
`phase-44-read-timing-knobs-missing-json-parse-reset`, `prove-pio-dev-flag-fails-closed`,
`runtime-info-log-naming-the-effective-page-size`). **All are firmware-area items** and none
bears on this phase; the milestone touches firmware only at the edges. Not folded.

</deferred>

---

*Phase: 182-JP5 Destructive-Operation Gate*
*Context gathered: 2026-09-10*

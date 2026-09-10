# Phase 182: JP5 Destructive-Operation Gate - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-10
**Phase:** 182-jp5-destructive-operation-gate
**Areas discussed:** Affected-part predicate, Operation coverage, Escape hatch & non-interactive, Jumper-display cleanup scope

---

## Pre-discussion finding that reframed the phase

Before the first question, a measurement against the live database showed SAFE-01's literal
wording could not be implemented:

- No pin map in `pinouts.json` declares A19 at all (15 maps checked).
- All eight 1 MB (8 Mbit) rows — `AM27C080`, `AM27LV080`, `AT27C080`, `MX27C8000`, `MX27C8000A`,
  `UPD27C8001`, `M27C801` ×2 — sit on `DIP32_STD`, which declares 19 address lines (A0–A18) and
  `vpp-pin: [1]`.
- `ic_layout.py` consequently renders **JP4 = Closed** for those parts — actively instructing the
  operator to route VPP to socket pin 1.

This was presented to the operator before any option was offered.

---

## Affected-part predicate

| Option | Description | Selected |
|--------|-------------|----------|
| Shortfall + 32-pin | Address-line shortfall AND `vpp-pin == [1]` AND `pin_count == 32`. Exactly 8 rows; self-corrects if the map is later fixed. Was the recommendation. | |
| Shortfall, unscoped | Same without the pin-count scope. 11 rows — 3 of them (`AT27C011`, `D27011`, `D27C011`) would get a "cut JP5" message that is wrong for them. | |
| Size threshold + VPP-pin-1 | `size_bytes >= 0x100000` AND `vpp-pin == [1]`. Exactly 8 rows, but `0x100000` is a magic constant standing in for "needs A19". | |
| All VPP-on-pin-1 parts | 291 chips. Cannot under-warn, but fires across the whole 27C010/020/040 population where closing JP4 is correct. | |

**User's choice:** *"Other"* — none of the above. Free-text: *"If the pin maps are wrong that must
be created and solved from the infoic.xml. The database must be generated from the infoic.xml
without any special cases or workarounds, we have to consider that new types of EPROMs get
inserted in the infoic and they must apply to the rules without to have to update the db
generator."*

**Notes:** The operator supplied three photographs of their shields (Rev 0 modified, Rev 2,
Rev 2.2) alongside the answer. Follow-up measurement confirmed the operator's position is
implementable: infoic's `variant` field already discriminates the three 32-pin families
(`0x01` = 256 KB, `0x02` = 512 KB, `0x03` = 1 MB) at `pin_map=0x000c` / `protocol_id=0x08`, and
`resolve_pinout_key` already uses `variant_lo` for 24- and 28-pin parts — it abandons the field
only at `pin_count == 32`, substituting a hand-tuned `MAX_27C020_SIZE` threshold.

One correction was put back to the operator rather than accepted: infoic's `<maps>` section
(121 records, lines 16717–17202) carries only a GND pin and a masked-pin list — connectivity with
no signal function — so pin-map **definitions** cannot be generated from it. The chip→layout
**assignment** can be, and that is where the special case lives.

---

## Generator fix scope

| Option | Description | Selected |
|--------|-------------|----------|
| Full fix in 182 | Dispatch 32-pin on `variant_lo`, retire `MAX_27C020_SIZE` and its parity arm, author the new layout, regenerate. Was the recommendation. | ✓ |
| Fix + audit all widths | As above, plus sweep every arm for thresholds standing in for rules — including 3 rows on a 14-line `DIP28_2764` and 18 `DIP32_28C512_EEPROM` rows with 16 lines for up to 512 KB. | |
| Gate only in 182; fix in its own phase | Ship the warning against the current database; correct the generator separately. | |

**User's choice:** Full fix in 182.
**Notes:** The declined audit was captured as a deferred idea, together with a suggested
fail-closed generator assertion (every row's `size_bytes` must fit the address lines its layout
declares) that would have caught the 8 Mbit defect at build time.

---

## Operation coverage

### Round 1 — does the gate survive the map fix?

| Option | Description | Selected |
|--------|-------------|----------|
| Both — gate still required | Silkscreen says "Cut for ROMs with A19 on P1" unconditionally; JP5 is unreadable, so the gate covers what the map fix cannot. Was the recommendation. | |
| Map fix supersedes the gate | Treat the hazard as closed once the tool stops asking for VPP on pin 1; strike SAFE-02 and SAFE-04. | ✓ (round 1) |

**User's choice (round 1):** Map fix supersedes the gate.

**Notes:** This voided two of the phase's five requirements on a circuit fact not yet established,
so the concern was raised once, specifically: the silkscreen instruction is unconditional; A19 is
not broken out anywhere on the Rev 2 pin labels, so the JP5 path may be *how* A19 reaches pin 1
rather than merely a VPP disconnect; and either way an 8 Mbit read with JP5 bridged returns wrong
data silently.

### Round 2 — drop now, or gate on the evidence?

| Option | Description | Selected |
|--------|-------------|----------|
| Evidence-gated | Map fix and SAFE-03 trace first; the trace decides whether SAFE-02/04 retire (with the trace as the recorded reason) or a warning ships. Was the recommendation. | ✓ |
| Drop the gate now | Strike SAFE-02/04 at discuss time; the trace is recorded but gates nothing. | |
| Drop the refusal, keep a notice | No prompt or refusal, but an unconditional informational line. | |

**User's choice (round 2):** Evidence-gated. The operator's expected outcome — that the map fix
supersedes the gate — is retained as the expectation, with the trace required underneath it.

### Round 3 — if a warning does ship, what does it cover?

| Option | Description | Selected |
|--------|-------------|----------|
| Every operation | read, write, verify, blank, erase, id, dev test — because no operation on an 8 Mbit part is correct if pin 1 cannot carry A19. Was the recommendation. | |
| Writes and erases only | Gate only VPP-asserting or modifying operations. | |
| Whatever the trace proves energizes pin 1 | Let the evidence define the set exactly. | |

**User's choice:** *"Other"* — *"Only when its a dangerus operation that can damage an EPROM."*

**Notes:** Narrower than the recommendation and coherent with the round-2 split: the gate is about
**damage**, the map fix is about **correctness**. Silently-wrong reads are explicitly not gated;
they were recorded as a deferred item instead.

---

## Escape hatch & non-interactive

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated flag, `--force` excluded | Interactive prompt; non-interactive refuses unless a purpose-built flag (e.g. `--jp5-cut`) is given. Was the recommendation. | |
| Hard refuse, no escape at all | No flag, no override; `dev test` skips with a stated reason. | |
| `--force` satisfies it | Reuse the existing `-f/--force`. | |

**User's choice:** *"Other"* — *"force excluded and when it is dangerus a question to continue."*

**Notes:** `-f/--force` is excluded as an escape hatch, and no substitute flag was authorised.
Since SAFE-04 permits only "refuse" or "an explicit, separate acknowledgement flag — never a
default-yes", the remaining branch is refusal, so non-interactive invocations (no TTY, piped
stdin, `dev test`, `--auto`/`--chain`) refuse. This reading was stated back to the operator
before being recorded. Rejecting `--force` reuse was reinforced by gh#62, where a reporter reached
for `--force` to get past a refusal.

---

## Jumper-display cleanup scope

| Option | Description | Selected |
|--------|-------------|----------|
| Own phase, wiki + info output | Photographs and per-revision tables to the prom wiki; `info` prints only the rows that matter and says when a jumper is irrelevant. New capability, so its own phase. | ✓ |
| Fold the info-output half into 182 | Phase 182 also rewrites the `info` jumper block; photographs still separate. | |
| All of it in 182 | Gate, generator fix, info rewrite, photographs and wiki tables together. | |

**User's choice:** Own phase, wiki + info output.
**Notes:** Decided without asking (precedent settled it): SAFE-05 is a named requirement of
Phase 182, so deleting `_get_rev2_2_jumper_settings_data` stays here. The
`fix-jp4-labels-and-rev2-revision-block` todo therefore splits — its dead-renderer item is SAFE-05
here; its JP4-label and Rev-2-block items move to the new phase, whose number does not exist yet.

---

## Claude's Discretion

- Name of the new 32-pin layout key (`DIP32_27C801` suggested, following the existing
  exemplar-part convention).
- Whether the SAFE-03 trace is a standalone `.planning/notes/` file or lives in the phase
  `SUMMARY.md` — it must be citable by Phase 187's gh#60 reply either way.
- Disposal of the retired `MAX_27C020_SIZE` parity arm — deleted, or replaced with a test that
  asserts something real about the 32-pin dispatch.
- Preservation of the operator's photographs: downscaled to 900×1600 / ~250 KB each (from 44 MB
  of originals) and placed under the phase `evidence/` directory, with silkscreen legibility
  verified after downscaling.

## Deferred Ideas

- The wider pin-map audit the operator declined for 182 — `AT27C011`/`D27011`/`D27C011` on a
  14-address-line `DIP28_2764`, and 18 `DIP32_28C512_EEPROM` rows with 16 lines for up to 512 KB —
  plus a suggested fail-closed generator assertion that every row's size fits its layout's address
  lines.
- Silently-wrong 8 Mbit reads if the SAFE-03 trace concludes "no damage".
- The new shield-documentation phase (wiki photographs, per-revision jumper tables, `info`
  rewrite) — needs inserting into `ROADMAP.md` before Phase 187, which must stay last.
- Two `REQUIREMENTS.md` edits arising from this discussion: SAFE-01's wording, and marking
  SAFE-02/SAFE-04 conditional on the SAFE-03 trace.

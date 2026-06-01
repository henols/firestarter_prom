# Modified Rev 0 — Hardware Modification Record

> Operator's third RURP shield: a stock upstream Rev 0 board
> (`parent = upstream-486f3d1`, schematic blob `d2a7f691`) carrying
> hardware-bug-A/B rework (cuts + jumpers). This file was a long-standing TBD
> stub (Phase 32 deferred it; Phase 35 follow-up #4 never landed because operator
> photos were blocked). Created in Phase 44 (Plan 04, bench session 1).
>
> **Provenance discipline:** every row below is tagged either **[attested]**
> (sourced from prior operator statements / `.planning/v1.7-SHIELD-REVS.md` with a
> citation) or **[uncaptured]** (the Phase 44 static inspection did not yield a
> quantitative reading — left blank, never fabricated).

## Board identity

| Field | Value | Source |
|-------|-------|--------|
| Silkscreen rev | Modified Rev 0 | Phase 44 operator confirmation ("rev 0"), 2026-06-01 |
| Parent | upstream Rev 0 — `upstream-486f3d1`, schematic blob `d2a7f691` (`UniversalProgrammerRev0b0.zip`) | v1.7-SHIELD-REVS.md §1/§4 |
| EEPROM `hw_revision` | cannot distinguish this board from the other two shields — silkscreen is authoritative | memory [[user_shield_revisions]] |

## Known / attested modifications

| Mod | Description | Status | Source |
|-----|-------------|--------|--------|
| A3 pull-up | External 10 kΩ pull-up on A3 → +5 V. Lands the board in the ADC mid-band (220–600) → detected as `REVISION_2_3`. | **[attested]** | v1.7-SHIELD-REVS.md §"Modified Rev 0" (line 209); bench-evidence-35.md |
| Bug-A/B rework | Hardware-bug-A/B rework consists of **cuts + jumpers** (count/locations not yet inventoried). | **[attested, untraced]** | v1.7-SHIELD-REVS.md §4/§5; memory [[user_shield_revisions]] |

## Signal-integrity trace vs upstream Rev 0 schematic (Phase 44 Task 1 target)

| Net | Measurement | Reading | Status |
|-----|-------------|---------|--------|
| A15 | Series termination, RURP driver → A15 chip pin (expect ~33–100 Ω) | — | **[uncaptured]** Phase 44 session: no quantitative reading dictated |
| D0–D7 | Pull-down to GND, per data line | — | **[uncaptured]** |
| VPP | Voltage at chip pin during read (expect ~0 V) | — | **[uncaptured]** board not connected this session |
| VCC | Rail sag during rapid A15-toggling reads | — | **[uncaptured]** board not connected this session |

## Outstanding

- Full rework inventory (cuts + jumpers, photographed and traced against blob
  `d2a7f691`) — carried forward from Phase 35 follow-up #4; **still open**.
- A15 series-termination + D0–D7 pull-down DC readings — the evidence that would
  down-select Bug A to a single signal-integrity mechanism. Recommend capturing
  during the Plan 05 bench session. See
  `.planning/phases/44-bug-a-rca-modified-rev-0-upper-address-jitter/evidence/static-check-notes.md`.

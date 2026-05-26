# Phase 35: Documentation + Milestone Close — Pattern Map

**Mapped:** 2026-05-25
**Files analyzed:** 19 (4 firmware/host code fixes; 3 sub-repo operator-facing docs; 7 meta-repo planning files; 2 todos; 3 wave-2 evidence artifacts)
**Analogs found:** 19 / 19 — every file has a closest existing analog or an immediately-prior in-place template.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter/include/rurp_hw_rev_utils.h` | firmware fix (CR-01 + CR-02) | event-driven (boot ADC + dispatcher) | itself @ Phase 34 baseline | in-place edit (Phase 34 baseline = canonical) |
| `firestarter/include/rurp_pinout.h` | firmware fix (CR-02 threshold widening) | config (compile-time `#define`) | itself @ Phase 34 baseline | in-place edit |
| `firestarter/CLAUDE.md` (optional D-10 extension) | doc / sync-rule | n/a | `firestarter_app/CLAUDE.md:100` constants-sync rule line | role-match (sync-rule prose pattern) |
| `firestarter_app/firestarter/serial_comm.py` | host fix (WR-01 + WR-02) | request-response (decoded ID frame → string) | `serial_comm.py:351-357` MSG_OK_REV branch | exact (same function, same dict) |
| `firestarter_app/tests/test_decoder.py` | test (D-03 + D-04 new tests) | request-response | `test_decoder.py:381-394` `test_ok_rev_p02_no_override_decodes` | exact (same shape — feed frame, assert message) |
| `firestarter_app/CLAUDE.md` (optional D-10 extension) | doc / sync-rule | n/a | itself @ line 100 (Phase 34 added REVISION_* sync clause) | in-place extension |
| `firestarter/doc/SHIELD-REVISIONS.md` | new sub-repo operator-facing doc | n/a | `.planning/v1.7-SHIELD-REVS.md` §1+§6+§7+§9 (subset copy) | exact source-of-truth (subset clone) |
| `firestarter/README.md` (Shield Revision Support section) | sub-repo doc | n/a | `firestarter/README.md` "Beta / Pre-release Channel" section | role-match (new top-level README section) |
| `firestarter_app/README.md` (Shield Revision Detection section) | sub-repo doc | n/a | `firestarter_app/README.md` ToC + Beta section | role-match (new top-level README section with cross-link) |
| `.planning/v1.7-SHIELD-REVS.md` (§3/§8/§9 row updates + §1 state flip) | state update | n/a | itself @ Phase 34 close | in-place edit |
| `.planning/PROJECT.md` (v1.7 block + Validated section) | state update | n/a | `PROJECT.md` v1.5 + v1.6 archive blocks | exact template (mirror v1.5 Archive structure) |
| `.planning/MILESTONES.md` (new v1.7 entry at top) | state update / archive | n/a | `MILESTONES.md:3-40` v1.5 entry | exact template |
| `.planning/STATE.md` (Operator Next Steps + frontmatter) | state update | n/a | `STATE.md` v1.6 PAUSE block + v1.5 close block | role-match (frontmatter + Operator Next Steps rewrite) |
| `.planning/v1.7-archive.sh` | new archive script | batch / file-I/O | `.planning/v1.4-archive.sh` | exact (4-line edit: phase number array) |
| `.planning/ROADMAP.md` (v1.7 → `<details>`) | state update | n/a | MILESTONES.md commit `8eff40e` (v1.5 ROADMAP collapse) | exact template (git-citable) |
| `.planning/REQUIREMENTS.md` → `.planning/milestones/v1.7-REQUIREMENTS.md` | archive move | n/a | `.planning/milestones/v1.5-REQUIREMENTS.md` | exact template (archive-header pattern) |
| `.planning/todos/pending/photograph-modified-rev-0.md` | new todo | n/a | `.planning/todos/pending/large-read-data-jitter-uno328pb.md` | exact (frontmatter + sections layout) |
| `.planning/todos/pending/write-modifications-md-rework-trace.md` | new todo | n/a | same | exact |
| `35-HUMAN-UAT.md` | wave-2 evidence | n/a | `34-HUMAN-UAT.md` | exact (frontmatter + test-row schema) |
| `.planning/v1.7/photos/rev-2-0/{top,bottom,silkscreen}.jpg` + `rev-2-2/...` | wave-2 evidence | file-I/O | `.planning/v1.7/photos/rev-2-0/README.md` landing slot | in-place fill (slot already exists) |

---

## Pattern Assignments

### Cluster 1: Firmware CR-01/CR-02 fixes (`rurp_hw_rev_utils.h` + `rurp_pinout.h`)

**Analog:** Phase 34 baseline of both files (in-place edit; lines cited below).

**Imports / file structure pattern** (`rurp_hw_rev_utils.h:1-12`):
```cpp
#ifndef __RURP_HW_REV_UTILS_H__
#define __RURP_HW_REV_UTILS_H__

#ifdef HARDWARE_REVISION

#include "rurp_shield.h"
#include "rurp_pinout.h"
#include <Arduino.h>
#include <stdint.h>
#include <string.h>

uint8_t revision = 0xFF;
```

**Auth pattern (compile-time guard)** — all detect-rev code under `#ifdef HARDWARE_REVISION` (`rurp_hw_rev_utils.h:4`, `:99` closing, mirrored in `rurp_pinout.h:45-47, :58-62`). Phase 35 CR-01/CR-02 edits stay inside this guard verbatim. Native-test env (`[env:native]`) excludes this TU via `src_filter = +<proms/>` — no native test impact.

**CR-01 fix pattern — replace `INPUT_PULLUP` with `INPUT`** (target: `rurp_hw_rev_utils.h:60-62`):

Current Phase 34 baseline:
```cpp
void rurp_detect_hardware_revision() {
    pinMode(PIN_HW_REVISION_DETECT_ADC, INPUT_PULLUP);
    pinMode(PIN_VPP_VOLTAGE_ADC, INPUT_PULLUP);
```

Phase 35 fix (per D-01):
```cpp
void rurp_detect_hardware_revision() {
    pinMode(PIN_HW_REVISION_DETECT_ADC, INPUT);  // high-Z; R41 + R_top divider drives the pin
    pinMode(PIN_VPP_VOLTAGE_ADC, INPUT);          // symmetric per CR-01b — both ADC reads see same input mode
```

Symmetric `pinMode(PIN_VPP_VOLTAGE_ADC, INPUT)` already at `rurp_hw_rev_utils.h:88` post-disambig — Phase 35 may consolidate or leave per planner's atomic-vs-bundled call (D-Discretion).

**CR-02 fix pattern — explicit `case REVISION_UNKNOWN:` arm in dispatcher** (target: `rurp_hw_rev_utils.h:14-40`):

Current Phase 34 baseline:
```cpp
uint8_t rurp_map_ctrl_reg_for_hardware_revision(rurp_register_t data) {
    uint8_t ctrl_reg = 0;
    uint8_t hw = rurp_get_hardware_revision();
    switch (hw) {
    case REVISION_2_0:
    case REVISION_2_1:
    case REVISION_2_2:
    case REVISION_2_3:
        ctrl_reg = data & (CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE | ...);
        ...
        break;
    case REVISION_0:
    case REVISION_1:
        ctrl_reg = data;
        ...
        break;
    default:
        // REVISION_UNKNOWN + any unrecognized byte fall through to ctrl_reg = 0
        break;
    }
    return ctrl_reg;
}
```

Phase 35 fix (per D-02 hard-fail-loud) — pattern: add explicit `case REVISION_UNKNOWN:` arm that emits a `LOG_ERROR_ID(...)` or `LOG_WARN_ID(...)` per the LOG-channel pattern already used in `firestarter/src/proms/*.cpp`. Planner picks: (a) error+refuse-dispatch (return 0 with explicit error emit), or (b) one-shot startup warn from `rurp_detect_hardware_revision()` when result is `REVISION_UNKNOWN` AND no EEPROM override at `rurp_hw_rev_utils.h:91-97`. Use existing `LOG_ERROR_ID` macro family (search `firestarter/src/proms/eprom.cpp` for analog call sites).

**Threshold-widening pattern (D-02 first part)** — `rurp_pinout.h:58-62`:

Current Phase 34 baseline:
```c
#ifdef HARDWARE_REVISION
#define ADC_BAND_R41_4K7_HIGH 200  // upper edge of 4k7 bucket
#define ADC_BAND_R41_10K_LOW  220  // lower edge of 10k bucket
#define ADC_BAND_R41_10K_HIGH 600  // upper edge of 10k bucket
#endif
```

Phase 35 widening pattern: Wave 2 captures real-silicon raw ADC values under `INPUT` mode (post-CR-01 fix). Wave 3 re-derives constants from bench data with ≥ 50-count guard gap (2-3× the 8-sample-averaged AVR ADC noise floor of ~5-10 counts). Same `#define` (NOT `constexpr`) per Phase 33 D-07 — preprocessor constants resolve at compile time, 0 B `.hex` contribution until referenced.

**Backward-compat invariant preserved** (`rurp_hw_rev_utils.h:91-97`):
```cpp
uint8_t rurp_get_hardware_revision() {
    rurp_configuration_t* rurp_config = rurp_get_config();
    if (rurp_config->hardware_revision < 0xFF) {
        return rurp_config->hardware_revision;
    }
    return rurp_get_physical_hardware_revision();
}
```
EEPROM override beats detection UNCHANGED. CR-02 hard-fail-loud fires only when there's no EEPROM override AND ADC lands in guard gap.

---

### Cluster 2: Host fixes WR-01 + WR-02 (`serial_comm.py`)

**Analog:** `firestarter_app/firestarter/serial_comm.py:334-398` `_format_message` (Phase 34 added MSG_OK_REV branch at lines 351-357; D-03/D-04 extend the same surface).

**Existing branch pattern** (`serial_comm.py:351-357` — MSG_OK_REV silkscreen renderer):
```python
if msg_id == MSG_OK_REV and len(params) == 2:
    physical, effective = params[0], params[1]
    phys_str = _REVISION_SILKSCREEN.get(physical, f"Rev{physical}")
    if effective == 0xFF:
        return phys_str
    eff_str = _REVISION_SILKSCREEN.get(effective, f"Rev{effective}")
    return f"{eff_str}, Override HW: {phys_str}"
```

**D-03 pattern — MSG_INFO_HW + MSG_INFO_PHYSICAL_HW silkscreen rendering** (NEW branches at `serial_comm.py:~340` insertion site):

```python
if msg_id == MSG_INFO_HW and len(params) == 1:
    byte = params[0]
    return _REVISION_SILKSCREEN.get(byte, f"Rev{byte}")

if msg_id == MSG_INFO_PHYSICAL_HW and len(params) == 1:
    byte = params[0]
    return _REVISION_SILKSCREEN.get(byte, f"Rev{byte}")
```

Catalog IDs: MSG_INFO_HW = 0x5B, MSG_INFO_PHYSICAL_HW = 0x5C (from `firestarter_app/firestarter/messages.py`). Single-byte u8 payload — single-param tuple.

**D-04 pattern — MSG_OK_CFG Override clause silkscreen rendering** (target: `serial_comm.py:359-363`):

Current baseline:
```python
if msg_id == MSG_OK_CFG and len(params) == 3:
    r1, r2, override = params[0], params[1], params[2]
    if override == 0xFF:
        return f"R1: {r1}, R2: {r2}"
    return f"R1: {r1}, R2: {r2}, Override HW: Rev{override}"
```

Phase 35 fix:
```python
if msg_id == MSG_OK_CFG and len(params) == 3:
    r1, r2, override = params[0], params[1], params[2]
    if override == 0xFF:
        return f"R1: {r1}, R2: {r2}"
    override_str = _REVISION_SILKSCREEN.get(override, f"Rev{override}")
    return f"R1: {r1}, R2: {r2}, Override HW: {override_str}"
```

Last-line literal `Rev{override}` (no space) becomes silkscreen-lookup result; fallback preserves the no-space `Rev{n}` shape so unknown bytes degrade gracefully.

**`_REVISION_SILKSCREEN` dict — DO NOT TOUCH** (`serial_comm.py:171-179` Phase 34 substrate):
```python
_REVISION_SILKSCREEN = {
    REVISION_0:       "Rev 0",
    REVISION_1:       "Rev 1",
    REVISION_2_0:     "Rev 2.0-class",   # broad bucket per Phase 34 D-04
    REVISION_2_1:     "Rev 2.1 (override)",
    REVISION_2_2:     "Rev 2.2 (override)",
    REVISION_2_3:     "Rev 2.3",
    REVISION_UNKNOWN: "rev_unknown",
}
```
All 7 entries already populated per Phase 34 D-05; D-03/D-04 are pure consumer-side wiring.

**Test pattern (D-03 + D-04 new tests)** — `firestarter_app/tests/test_decoder.py:381-394`:

```python
def test_ok_rev_p02_no_override_decodes(self, fake_serial, make_comm):
    """P-02: MSG_OK_REV with physical=0x01, effective=0xFF sentinel renders
    'Rev 1' per Phase 34 D-05 Path A silkscreen-string mapping."""
    comm = make_comm()
    params = bytes([0x01, 0xFF])
    frame = build_frame(MSG_OK_REV, params)
    fake_serial.feed(frame)
    response = _drive_one_response(comm)
    assert response is not None
    assert response.type == "OK"
    assert response.message == "Rev 1"
```

Phase 35 new tests (mirror shape — one per branch added):
- `test_info_hw_silkscreen_decodes` — feed MSG_INFO_HW frame with byte=0x01, assert message == `"Rev 1"`; second test for byte=0xFE (REVISION_UNKNOWN), assert `"rev_unknown"`.
- `test_info_physical_hw_silkscreen_decodes` — same shape for MSG_INFO_PHYSICAL_HW.
- Update `test_ok_cfg_p03_with_override_decodes` at line 400-412 — change assertion from `"R1: 10000, R2: 4700, Override HW: Rev2"` to `"R1: 10000, R2: 4700, Override HW: Rev 2.0-class"` (since 0x02 == REVISION_2_0 in `_REVISION_SILKSCREEN`).

---

### Cluster 3: Sub-repo operator-facing doc (D-10) — `firestarter/doc/SHIELD-REVISIONS.md`

**Analog:** `.planning/v1.7-SHIELD-REVS.md` §1 + §6 + §7 + §9 — subset copy with operator preamble + investigation-pointer footer.

**Structure pattern** (NEW file, ~5 sections):

1. **Preamble (3-5 sentences)** — "What this is" (canonical per-rev reference for RURP shield hardware revisions) + "How to use it" (look up your board's silkscreen, find its capability matrix, use the alias table when reading firmware) + brief mention of EEPROM `hw_revision` override escape hatch.
2. **§1 Inventory** — copied verbatim from `.planning/v1.7-SHIELD-REVS.md:12-26` (9-column inventory schema). Photo column updated from `—` to per-rev paths under the sub-repo (or kept upstream pointer; planner's choice).
3. **§6 Per-Rev Capability Matrix** — copied verbatim from `.planning/v1.7-SHIELD-REVS.md` §6.
4. **§7 Silkscreen → Code Alias Table** (17 rows per D-11) — copied verbatim from `.planning/v1.7-SHIELD-REVS.md` §7.
5. **§9 Per-Rev ADC Band Table** — copied verbatim from `.planning/v1.7-SHIELD-REVS.md` §9 (post-Wave-2-bench-update values).
6. **Footer pointer** — "Full investigation history: see `.planning/v1.7-SHIELD-REVS.md` in the meta-repo at https://github.com/henols/firestarter-meta/... (§§ 2-5, 8 — git archaeology, electrical/mechanical deltas, detect-HW narrative)."

**Path:** `firestarter/doc/SHIELD-REVISIONS.md` (new `doc/` directory in firmware sub-repo — `ls firestarter/doc/` confirms it does not exist; `mkdir` first).

**Drift policy** — Wave 4 close adds a `firestarter/CLAUDE.md` sync rule extension (parallel to `firestarter_app/CLAUDE.md:100` REVISION_* sync clause): "if `.planning/v1.7-SHIELD-REVS.md` §1/§6/§7/§9 changes, also update `firestarter/doc/SHIELD-REVISIONS.md` in lockstep." Land in Wave 3 (post-bench) — copying mid-investigation would mean re-copying after bench data updates §9 row values.

---

### Cluster 4: Sub-repo README sections (D-10) — `firestarter/README.md` + `firestarter_app/README.md`

**Analog:** `firestarter/README.md` "Beta / Pre-release Channel" section (added in v1.4 Phase 19) — same top-level README addition pattern.

**Firmware README addition pattern** (`firestarter/README.md`, insert after "Beta / Pre-release Channel" or near "Supported boards"):

```markdown
## Shield Revision Support

The firmware detects the connected RURP shield's silkscreen revision at boot
via the ADC voltage-band lookup on pin A3 (Rev 2.3+ boards carry the R41 detect
divider; pre-detect-resistor boards Rev 0 / Rev 1 / Rev 2.0 / Rev 2.2 fall
through to `rev_unknown` + EEPROM `hw_revision` byte override). The detected
silkscreen string surfaces on the firmware handshake (`MSG_OK_REV`).

For per-revision capability matrix, electrical differences, and the canonical
silkscreen → code alias table, see [`doc/SHIELD-REVISIONS.md`](./doc/SHIELD-REVISIONS.md).

If detection lands in the guard gap (`rev_unknown`), set the EEPROM override
byte via the host CLI: `firestarter rev <N>` (see firestarter_app README).
```

**Host README addition pattern** (`firestarter_app/README.md`, insert into ToC + new section):

```markdown
## Shield Revision Detection

The Firestarter firmware reports the detected RURP shield silkscreen revision
on every handshake (`MSG_OK_REV`). For per-revision capability matrix and the
silkscreen → code alias reference, see the firmware sub-repo doc:
https://github.com/henols/firestarter/blob/main/doc/SHIELD-REVISIONS.md

If detection reports `rev_unknown` (pre-detect-resistor boards or guard-gap
land), set the EEPROM override byte: `firestarter rev <N>` where `<N>` is the
silkscreen-rev byte (e.g. `0x00` Rev 0, `0x02` Rev 2.0, `0x23` Rev 2.3,
`0xFE` rev_unknown sentinel).
```

3-5 sentences + GitHub-URL link + EEPROM-override escape hatch per D-10.

---

### Cluster 5: `firestarter/CLAUDE.md` + `firestarter_app/CLAUDE.md` (D-10 sync-rule extensions — optional Discretion)

**Analog:** `firestarter_app/CLAUDE.md:100` — Phase 34 added the REVISION_* sync clause to the existing constants-parity rule. Same in-place prose extension pattern.

**Existing prose pattern** (`firestarter_app/CLAUDE.md:100`):
```
... Additionally, the `RURP_HARDWARE_REVISIONS` block in `constants.py`
(REVISION_* names) mirrors the hardware-revision enum declarations in
`firestarter/include/rurp_shield.h` (Phase 34 / v1.7 — shield-version-detect
design + firmware plumbing). Keep REVISION_* names + byte values in sync with
the firmware enum; `0xFF` is reserved as the EEPROM-override-absent sentinel
and `0xFE` (`REVISION_UNKNOWN`) is reserved for the ADC-band-gap fall-through.
```

**Phase 35 extension pattern** — add one sentence to the same paragraph:
```
... Additionally, the sub-repo `firestarter/doc/SHIELD-REVISIONS.md` operator-
facing doc is a subset clone of meta-repo `.planning/v1.7-SHIELD-REVS.md`
sections §1/§6/§7/§9 (Phase 35 / v1.7 — close); if any of those four sections
change in the meta-repo, update the sub-repo doc in lockstep.
```

Mirror in `firestarter/CLAUDE.md` — search for the existing "What's load-bearing" / constants-sync block and extend similarly. Small DOC-01 footprint.

---

### Cluster 6: Meta-repo planning surface updates (D-11..D-13)

#### `.planning/v1.7-SHIELD-REVS.md` (in-place row updates from Wave 2 bench evidence)

**Analog:** itself @ Phase 34 close.

**Update targets:**
- **§1 row 2 (Rev 2.2) `state` column** — flip `upstream-only` → `operator-photographed`
- **§1 row 5 (Rev 2.0 working) `state` column** — flip `upstream-only` → `operator-photographed`
- **§1 row 2 + row 5 `photo_dir` column** — fill `.planning/v1.7/photos/rev-2-2/` + `.planning/v1.7/photos/rev-2-0/`
- **§3 row 3 (Rev 2.2 R41 value)** — replace `4k7 (4.7kΩ) per schematic; NOTE: Anders stated "10k"…discrepancy` with the bench-measured value (UAT-2 resolves §8 OPEN flag)
- **§4 row 5 (Rev 2.1 → Rev 2.2) `voltage_divider_delta`** — replace `DISCREPANCY` annotation with resolution per Wave 2 bench
- **§8** — flip the R41-value OPEN flag to RESOLVED (cite UAT-2 result)
- **§9 per-rev ADC band table** — replace placeholder/Phase 34 design-time values with empirically-characterized Wave 2 raw ADC values (mean ± stddev across the 3 boards × N boots)

**Pattern:** mechanical row edits; no schema change. Wave 3 commit boundary — likely all in one commit (the row-set is tightly coupled; planner finalizes per D-Discretion).

#### `.planning/PROJECT.md` (D-11 — Validated section + v1.7 block)

**Analog:** `PROJECT.md` v1.5 Archive block (`PROJECT.md:68+`) — already-shipped milestone template.

**Pattern — v1.7 block rewrite at top:**
- Change `**v1.7 status:** STARTED 2026-05-22 — …` → `**v1.7 shipped:** 2026-05-XX (Y phases, Z requirements; ship tag `3.0.0b5` both sub-repos; bench-validated on operator's Rev 2.0 + Rev 2.2 boards). …`
- Migrate the existing v1.7 "Current Milestone" + "Target features" + "Locked decisions" block under a new `## v1.7 Archive: RURP Shield Hardware Investigation & Version Detection — Shipped 2026-05-XX` header (mirror of `## v1.5 Archive:`/`## v1.6 Archive:` pattern).

**Pattern — Validated section insertion** (search PROJECT.md for existing "Validated" bullet list of prior milestones — insert at top before v1.5):
```
- **Silkscreen → code alias migration (v1.7)** — 4-namespace lock
  (CTRL_ / PIN_ / RES_ / JMP_) applied across firmware
  (`firestarter/include/rurp_pinout.h`) + host
  (`firestarter_app/firestarter/constants.py`); 17 rows in §7 canonical alias
  table; GATE-1.7 Δ = 0 B across all 3 AVR envs.
- **Shield-version-detect plumbing (v1.7)** — ADC band lookup on A3 (high-Z)
  + EEPROM override fall-through + handshake report; `REVISION_2_3` /
  `REVISION_UNKNOWN` enum on firmware + Python parity; pre-detect-resistor
  boards (Rev 0 / 2.0 / 2.2) handshake byte-identical to v1.6 baseline modulo
  the additive `MSG_OK_REV` physical-u8 value.
```

#### `.planning/MILESTONES.md` (D-12 — new v1.7 entry at top)

**Analog:** `MILESTONES.md:3-40` v1.5 entry — closest template-of-record; also `MILESTONES.md:43-174` v1.4 entry for the longer-form structure.

**Header-line pattern** (mirror of `MILESTONES.md:3`):
```
## v1.7 — RURP Shield Hardware Investigation & Version Detection (Shipped: 2026-05-XX)

**Phases:** 5 (numbered 31-35) | **Plans:** N (TBD at close — sum across phases 31-35) | **Timeline:** 2026-05-22 (planning) → 2026-05-25 (execution close) | **Ship tag:** 3.0.0b5 (both sub-repos via the v1.4 lockstep mechanism) | **Commits:** meta-repo ~N, firestarter sub-repo M, firestarter_app sub-repo P
```

**Section order** (verbatim mirror of v1.5 entry):
1. Header + metrics line
2. **Delivered** narrative (3-5 sentences) — see `MILESTONES.md:5` for v1.5 example
3. **### Key Accomplishments** — one bulleted item per phase (31 archaeology / 32 difference matrix / 33 alias migration / 34 detect plumbing / 35 fix+bench+close), each 2-4 sentences citing specific artifacts. Mirror `MILESTONES.md:9-19` structure.
4. **### Branch Strategy** — `v1.7-shield-investigation` branches in all 3 repos; sub-repos branched off post-v1.5 `beta`; meta off `main`; `beta` → `main` cut at Wave 4 with `3.0.0b5`. Mirror `MILESTONES.md:21-23`.
5. **### Open backlog from v1.7 bench session (carried to post-v1.7)** — pattern mirrors `MILESTONES.md:25-31`. Items: Modified Rev 0 photo (D-07); MODIFICATIONS.md rework trace (D-07); any CR-02 follow-ups if bench data forces band collapse of Rev 2.0/2.3.
6. **### Key Decisions (locked)** — D-01, D-02, D-08, D-09, D-07 per D-12. Mirror `MILESTONES.md:33-39`.
7. **### Known Gaps** — runtime capability guards (CAPS-02); REVISION_UNKNOWN hard-fail policy mechanism; R41 stock-part 5% tolerance worst-case. Mirror v1.5 + v1.4 "Known Gaps" patterns.

**Closing-commit-ref placeholder pattern** (v1.5 example):
```
*Closed via commit `<MILESTONE_CLOSE_COMMIT>` on 2026-05-XX*
```
Filled at Wave 4 final close commit.

#### `.planning/STATE.md` (D-13 — Operator Next Steps + frontmatter)

**Analog:** `STATE.md:1-14` frontmatter + `STATE.md` "Open Blockers" / "Operator Next Steps" section.

**Frontmatter update pattern** (`STATE.md:1-14`):
```yaml
---
gsd_state_version: 1.0
milestone: v1.6                       # was: v1.7
milestone_name: — Fix the Read Bug    # was: v1.7 RURP Shield ...
status: paused_resume_v1.6            # was: planning
last_updated: "2026-05-XX...Z"
last_activity: 2026-05-XX
progress:
  total_phases: 5                     # v1.6 paused 5 phases
  completed_phases: 3                 # v1.6 had 3 phases shipped at pause
  ...
---
```

**Operator Next Steps rewrite pattern** (4 bullet points per D-13):
1. v1.7 closed — mark Shipped 2026-05-XX at top.
2. v1.6 resume: `/gsd-plan-phase 27 --gaps`
3. Cite v1.7 substrate artifacts the Phase 27 RCA re-open consumes:
   - Labeled schematic: `.planning/v1.7-SHIELD-REVS.md` §1 + §3 + §4
   - Per-rev capability table: `.planning/v1.7-SHIELD-REVS.md` §6
   - Detect-fw substrate: `REVISION_2_3` / `REVISION_UNKNOWN` enum + ADC band lookup (post-CR-01/CR-02 fix)
4. First disambiguation experiment per Phase 29-02 SUMMARY hand-off: pre-Phase-28-firmware A/B test on `firestarter/v1.6-read-bug~2`, sideload to Leonardo, re-probe.

---

### Cluster 7: Archive script (D-14) — `.planning/v1.7-archive.sh`

**Analog:** `.planning/v1.4-archive.sh` — proven pattern (used at v1.4 close; v1.5 archive at `.planning/milestones/v1.5-phases/` exists, indicating a v1.5-archive.sh or manual move was used).

**Edit pattern — 4-line change to the `PHASE_GLOBS` array** (`v1.4-archive.sh:74-81`):

Current (v1.4):
```bash
PHASE_GLOBS=(
    "$PHASES_DIR/15-"*
    "$PHASES_DIR/16-"*
    "$PHASES_DIR/17-"*
    "$PHASES_DIR/18-"*
    "$PHASES_DIR/19-"*
    "$PHASES_DIR/20-"*
)
```

v1.7 version:
```bash
PHASE_GLOBS=(
    "$PHASES_DIR/31-"*
    "$PHASES_DIR/32-"*
    "$PHASES_DIR/33-"*
    "$PHASES_DIR/34-"*
    "$PHASES_DIR/35-"*
)
```

**Other edits** (find/replace throughout):
- `v1.4` → `v1.7` (header comment, usage line, error messages, destination path, commit-instruction echo)
- `15-* through 20-*` → `31-* through 35-*` (5 globs not 6)
- `.planning/milestones/v1.4-phases/` → `.planning/milestones/v1.7-phases/`
- Update next-steps echo (`v1.4-archive.sh:140-145`):
  - `git commit -m 'refactor: archive v1.7 phase directories to milestones/v1.7-phases/'`
- Preserve verbatim: `set -euo pipefail`, `--dry-run` argparse, pre-flight checks (dest non-empty + at least one source exists), explicit-glob-not-wildcard safety, idempotence message. Per D-14: "Explicit per-phase glob enumeration; pre-flight; `--dry-run` flag; safety against accidental capture of paused phases."

**Critical safety guarantee:** the explicit per-phase array (NOT `31-*` single wildcard) prevents accidental capture of v1.6 paused phases (`26-*` through `29-*`) — they live alongside v1.7 phases in `.planning/phases/` because v1.6 is paused, not archived (see `STATE.md` Paused Milestones). Test with `--dry-run` first.

---

### Cluster 8: ROADMAP collapse + REQUIREMENTS archive (D-15)

#### `.planning/ROADMAP.md` (v1.7 section → `<details>`)

**Analog:** Git-citable: `git show 8eff40e` reveals v1.5 ROADMAP collapse pattern (per CONTEXT.md canonical refs).

**Pattern:**
- Wrap the entire v1.7 section (currently `ROADMAP.md:14-` through end of v1.7 phase details — likely ~30-100 lines) in a `<details>` block.
- Top bullet (`ROADMAP.md:12`) flips: `🚧 **v1.7 ... STARTED 2026-05-22** ...` → `✅ **v1.7 ... shipped 2026-05-XX** ...` with a one-sentence summary; the full milestone block goes inside `<details><summary>v1.7 details (archived)</summary>...</details>`.

Mirror of v1.5 ROADMAP archive pattern (live `.planning/milestones/v1.5-ROADMAP.md` carries the full historical version; the active `.planning/ROADMAP.md` references it via the collapsed `<details>` shape).

#### `.planning/REQUIREMENTS.md` → `.planning/milestones/v1.7-REQUIREMENTS.md`

**Analog:** `.planning/milestones/v1.5-REQUIREMENTS.md:1-8` archive header — exact template.

**Archive header pattern** (mirror of `v1.5-REQUIREMENTS.md:1-8`):
```markdown
# Requirements Archive: v1.7 RURP Shield Hardware Investigation & Version Detection

**Archived:** 2026-05-XX
**Status:** SHIPPED

For current requirements, see `.planning/REQUIREMENTS.md`.

---

# Milestone v1.7 — RURP Shield Hardware Investigation & Version Detection
[... full body of current REQUIREMENTS.md preserved verbatim ...]
```

**Operations:**
1. `git mv .planning/REQUIREMENTS.md .planning/milestones/v1.7-REQUIREMENTS.md`
2. Prepend the 8-line archive header block above.
3. The active `.planning/REQUIREMENTS.md` file is **removed from the live planning surface** per D-15 (no replacement — v1.6 resume reads its REQUIREMENTS from `.planning/milestones/v1.6-paused/v1.6-REQUIREMENTS.md`, which the planner may need to create as part of v1.6 resume — out of Phase 35 scope).

---

### Cluster 9: New post-v1.7 todos (D-07)

**Analog:** `.planning/todos/pending/large-read-data-jitter-uno328pb.md` — exact template (frontmatter + 4-5 section layout).

**Frontmatter pattern** (verbatim mirror of `large-read-data-jitter-uno328pb.md:1-9`):
```yaml
---
id: photograph-modified-rev-0
title: Photograph operator's Modified Rev 0 board (Phase 31 follow-up #3)
captured: 2026-05-25
status: pending
type: documentation
target_milestone: post-v1.7
priority: MEDIUM
related_phase: 31
resolves_phase: 35 (deferred per D-07)
---
```

**Body section pattern:**
1. **# Title** — restate concisely
2. **## The deferral** — D-07 rationale: rework trace independent of v1.7 detect-fw; operator's Modified Rev 0 uses EEPROM override path regardless of rework
3. **## What's needed** — top.jpg + bottom.jpg + silkscreen.jpg + per-region close-ups per the `.planning/v1.7/photos/<rev>/README.md` landing-slot schema
4. **## Sentinel cross-references** — v1.7-SHIELD-REVS.md §1 row 4 + §4 row 8 + §5 row 7 + §6 row 91 (the "as-modified — pending Phase 35" sentinels — preserve verbatim per D-Discretion recommendation)
5. **## When to triage** — at next milestone-start sweep; grep for `pending Phase 35` to pick up

**Second todo (`write-modifications-md-rework-trace.md`):**
- Same frontmatter shape; `id: write-modifications-md-rework-trace`; `type: documentation`; `priority: MEDIUM`
- Body covers: depend on photograph-modified-rev-0; trace each cut/jumper against `UniversalProgrammerRev0b0.zip::W27C512Programmer.kicad_sch` (blob d2a7f691 on `origin/rev2.0`); upgrade §1 row 4 / §4 row 8 / §5 row 7 / §6 row 91 TBD sentinels.

---

### Cluster 10: Wave 2 bench evidence files

#### `35-HUMAN-UAT.md` (D-05)

**Analog:** `.planning/phases/34-shield-version-detect-design-firmware-plumbing/34-HUMAN-UAT.md:1-40` — exact frontmatter + test-row schema.

**Frontmatter pattern** (mirror of `34-HUMAN-UAT.md:1-7`):
```yaml
---
status: partial
phase: 35-documentation-milestone-close
source: [.planning/phases/35-documentation-milestone-close/35-VERIFICATION.md]
started: 2026-05-XXTHH:MM:00Z
updated: 2026-05-XXTHH:MM:00Z
---
```

**Per-test row pattern** (mirror of `34-HUMAN-UAT.md:15-28`):
```markdown
### N. <Test title>
expected: <expected outcome>
why_human: <why physical hardware required>
result: [pending]
```

3 test rows per D-05:
1. UAT-1 — sideload Phase 35 firmware to Rev 2.0 board; confirm MSG_OK_REV report
2. UAT-2 — sideload Phase 35 firmware to Rev 2.2 board; capture MSG_OK_REV report (resolves §8 OPEN flag)
3. UAT-3 — CR-01 misclassification cross-check across multiple boots (verify Wave 1 fix landed correctly)

**Summary block pattern** (mirror of `34-HUMAN-UAT.md:30-37`):
```markdown
## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0
```

#### `.planning/v1.7/photos/rev-2-0/` + `rev-2-2/` (D-06)

**Analog:** `.planning/v1.7/photos/rev-2-0/README.md` (existing — landing slot already created in Phase 31 Plan 03).

**Slot already exists** — operator drops JPGs into these existing dirs. README schema:
- `top.jpg` — full top view, silkscreen-version string visible
- `bottom.jpg` — full bottom view
- `silkscreen.jpg` — macro of silkscreen-version region
- Optional: `socket-detail.jpg`, `jp4-detail.jpg`

**Gitignored** per Phase 31 substrate decision (operator's local-only photos; only README.md tracked).

**No new directory needed** for rev-2-0 / rev-2-2 (already created). **Do NOT create** `.planning/v1.7/photos/rev-0-modified/` populated content per D-07 — that exists empty; populating is the deferred post-v1.7 todo.

---

## Shared Patterns

### Pattern A: Atomic per-CR/WR commit vs bundled fix-up commit (D-Discretion)

**Source:** v1.5 Phase 23 fix-up cluster + v1.4 E2E-01..06 substrate fixes (bundled approach in single day).
**Apply to:** Wave 1 (CR-01 + CR-02 + WR-01 + WR-02 fixes).
**Pattern:** Planner picks atomic-per-finding vs bundled. v1.5 Phase 23 + v1.4 E2E both show bundled "Phase X BLOCKER fixes" commit works for tightly-related findings. v1.7 has 4 findings, all in same milestone close — bundled is reasonable; atomic is cleaner for git-bisect.

### Pattern B: Phase 33 `#define`-not-`constexpr` for thresholds

**Source:** Phase 33 D-07 (cited in CONTEXT §code_context).
**Apply to:** `rurp_pinout.h:58-62` ADC band threshold widening.
**Pattern:** Preprocessor `#define` constants resolve at compile time, contribute 0 B to the `.hex` until referenced. Maintains GATE-1.7 Δ = 0 B invariant when values change but nothing else does.

### Pattern C: `#ifdef HARDWARE_REVISION` compile-flag gating

**Source:** Phase 34 substrate (`platformio.ini:23` for all 3 AVR envs; native env excludes).
**Apply to:** All firmware fix work in `rurp_hw_rev_utils.h` + `rurp_pinout.h`.
**Pattern:** All detect-rev code paths under this ifdef. Phase 35 CR-01/CR-02 edits stay inside the existing ifdef boundary. Native tests at `[env:native]` bypass detect-rev (src_filter = +<proms/>` excludes `rurp_hw_rev_utils.h`).

### Pattern D: EEPROM override sentinel = `0xFF`, REVISION_UNKNOWN = `0xFE`

**Source:** `rurp_hw_rev_utils.h:91-97` precedence chain + `serial_comm.py:171-179` _REVISION_SILKSCREEN.
**Apply to:** All Phase 35 firmware + host fixes.
**Pattern:** `0xFF` = "no EEPROM override set"; `0xFE` = `REVISION_UNKNOWN` (ADC band-gap fall-through). Both are first-class values; never collapse. CR-02 hard-fail-loud fires only on REVISION_UNKNOWN WITHOUT EEPROM override (defensive — operator escape via EEPROM preserved).

### Pattern E: Sentinel preservation across milestone boundaries (D-Discretion recommended)

**Source:** Phase 32 §6 row 91 "as-modified — pending Phase 35" sentinel pattern.
**Apply to:** D-07 post-v1.7 todos (Modified Rev 0 photo + MODIFICATIONS.md trace).
**Pattern:** New todos preserve the `pending Phase 35` sentinel verbatim in cross-references. Future RCA / milestone-start sweeps can grep for the sentinel and pick up deferred work cleanly.

### Pattern F: v1.4 lockstep mechanism for sub-repo `3.0.0b5` cut

**Source:** `.planning/milestones/v1.4-phases/15-versioning-locked-step-coordination-foundation/15-LOCKSTEP-PROCEDURE.md`.
**Apply to:** D-08 + D-09 Wave 2 beta cut + Wave 4 stable promotion.
**Pattern:** Manually-paired beta-branch push with explicit `BETA_VERSION=3.0.0b5` input. `firestarter_app/.github/workflows/beta-release.yml` + `firestarter/.github/workflows/beta-build.yml` both accept the explicit input and emit matching PEP 440 / GitHub Pre-release version strings. No new CI/CD work.

### Pattern G: Operator-bench protocol (memory-recall)

**Source:** memory `[[feedback_chip_out_before_sideload]]` + `[[feedback_verify_port_identity_each_task]]` + `[[v1.5-bench-findings]]`.
**Apply to:** Wave 2 operator-on-bench sideload + UAT execution.
**Pattern:** Chip OUT of socket before any firmware sideload (drives data/address/control bus). Verify `controller:` identity per port at every task start (`/dev/ttyACM*` numbers shuffle across replug). Operator's 328PB-Uno uses `programmer_id="urclock"` (bench-validated v1.5 Phase 24).

---

## No Analog Found

None. Every Phase 35 file has a strong in-codebase analog or in-place template.

---

## Metadata

**Analog search scope:**
- `/workspaces/.planning/` (MILESTONES.md, PROJECT.md, STATE.md, ROADMAP.md, v1.7-SHIELD-REVS.md, v1.4-archive.sh, milestones/v1.5-REQUIREMENTS.md, todos/pending/)
- `/workspaces/firestarter/` (include/rurp_hw_rev_utils.h, include/rurp_pinout.h, CLAUDE.md, README.md, doc/)
- `/workspaces/firestarter_app/` (firestarter/serial_comm.py, tests/test_decoder.py, CLAUDE.md, README.md)
- `/workspaces/.planning/phases/34-shield-version-detect-design-firmware-plumbing/` (34-CONTEXT.md, 34-REVIEW.md, 34-HUMAN-UAT.md)
- `/workspaces/.planning/v1.7/photos/` (rev-2-0/README.md, rev-2-2/README.md, MODIFICATIONS.md)

**Files scanned:** ~25.
**Pattern extraction date:** 2026-05-25.
**Closest-template-of-record:** v1.5 Phase 25 close (single-day execution; same shape modulo Wave 1 fix-up).

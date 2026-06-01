# Phase 48: COBS Evaluation + Post-RCA Cleanup + Milestone Close — Pattern Map

**Mapped:** 2026-06-01
**Files analyzed:** 5 (2 new, 3 modified)
**Analogs found:** 5 / 5

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `.planning/v1.9-COBS-DECISION.md` | planning doc (ADR) | doc-only | `.planning/v1.7-SHIELD-REVS.md` + RESEARCH.md §"v1.9-COBS-DECISION.md structure" | structural match |
| `firestarter_app/pyproject.toml` | config | transform | `firestarter_app/pyproject.toml` lines 131-145 (strict-island block itself) | exact — same file, existing block is the target shape |
| `firestarter_app/firestarter/eprom_operations.py` | service | CRUD / request-response | `firestarter_app/firestarter/serial_comm.py` (strict-island sibling) | role-match (same strict-island tier, same `Optional` narrowing problem) |
| `firestarter_app/tools/check_mypy_watermark.py` | utility | transform | self (read-only; watermark comment update only) | exact |
| `.planning/MILESTONES.md` | planning doc | doc-only | `.planning/MILESTONES.md` lines 1-80 (v1.8 entry) | exact format precedent |

---

## Pattern Assignments

### `.planning/v1.9-COBS-DECISION.md` (planning doc, ADR-style, NEW)

**Analog:** `.planning/v1.7-SHIELD-REVS.md` (section-header structure) + RESEARCH.md §"v1.9-COBS-DECISION.md structure" (ADR sections)

**Section skeleton** (from RESEARCH.md §COBS-01 Decision + v1.7-SHIELD-REVS.md heading style):

```markdown
# v1.9 COBS Decision — Serial Robustness Framing Evaluation

**Milestone:** v1.9 Read-Bug RCA + Cleanup
**Decided:** [date]
**Status:** FINAL — REJECT libraries / DEFER concept

## 1. Context

[4-framing wire map, resync motivation, Uno RAM baseline 2026-06-01:
73.4% used (1503/2048 bytes), 545 B free; Flash 69.7% (22492/32256)]

## 2. Decision

REJECT all off-the-shelf libraries (D-01 + filter below).
DEFER the auto-resync concept to a future protocol-quality milestone.
Keep existing framing + CRC8-CCITT intact.

## 3. Consequences

[No wire change this milestone; future milestone path = hand-rolled
streaming COBS (~70 lines); SLIP is simpler alternative if 0x00
delimiter concern ever proves architectural]

## 4. Candidate Survey

### 4.1 PacketSerial — LOCKED REJECT (D-01)
...
### 4.2 SLIP / RFC-1055
...
### 4.3 Hand-Rolled Streaming COBS
...
### 4.4 nanocobs (charlesnicholson/nanocobs)
...
### 4.5 cobs-c + cobs-python (cmcqueen)
...
### 4.6 SerialTransfer + pySerialTransfer (PowerBroker2)
...
### 4.7 MIN Protocol (min-protocol/min)
...

### Comparative Verdict Table

| Candidate | Fits Uno RAM? | Frame ≤512 B? | Resync? | CRC8 coexists? | Cost | Verdict |
|-----------|...

## 5. Open Questions for Future Milestone

[Field evidence threshold for resync win; streaming COBS 0x00 bus-aliasing
host-side timing guarantee; SLIP vs COBS if adopted]
```

**Key structural rules from v1.7-SHIELD-REVS.md precedent:**
- Top-level H1 = `v1.9 COBS Decision — [topic]`
- H2 = numbered sections (## 1. Context, ## 2. Decision, …)
- H3 = sub-items within a section (### 4.1 PacketSerial, …)
- Include a "Source evidence" or "Verified:" provenance note per claim
- Tables use pipe-style markdown; all columns filled or use `—` sentinel
- "RESOLVED" / "VERIFIED" / "ASSUMED" tags on individual claims (v1.7 pattern)

---

### `firestarter_app/pyproject.toml` (config, TYPE-01 — MODIFY)

**Analog:** `firestarter_app/pyproject.toml` lines 131-163 (existing strict-island + silent blocks)

**Current strict-island block** (lines 131-145 — this is the TARGET SHAPE the planner must extend):

```toml
[[tool.mypy.overrides]]
# Phase 42 D-06: strict-island for the 8 modules touched in v1.8.
# eprom_operations.py DELIBERATELY EXCLUDED per D-07 (GATE-1.8d read-path ring-fence; deferred to v1.9 post-RCA).
module = [
    "firestarter.main",
    "firestarter.cli_handlers",
    "firestarter.chip_resolver",
    "firestarter.frame_parser",
    "firestarter.codec",
    "firestarter.address_parser",
    "firestarter.exceptions",
    "firestarter.serial_comm",
]
disallow_untyped_defs = true
check_untyped_defs = true
```

**Current non-strict-silenced block** (lines 147-163 — `firestarter.eprom_operations` must be REMOVED from here):

```toml
[[tool.mypy.overrides]]
# Phase 42 D-06 / D-07: non-strict modules — silence transitively-imported
# errors so `mypy <strict-list>` exits 0. The full mypy gate
# (tools/check_mypy_watermark.py) still tracks these via the watermark count.
module = [
    "firestarter.eprom_operations",   # <-- REMOVE THIS LINE (TYPE-01)
    "firestarter.firmware",
    "firestarter.hardware",
    "firestarter.database",
    "firestarter.config",
    "firestarter.ic_layout",
    "firestarter.eprom_info",
    "firestarter.utils",
    "firestarter.logging_utils",
    "firestarter.avr_tool",
]
follow_imports = "silent"
```

**Watermark comment** (line 115 — update after TYPE-01 fixes applied):

```toml
# mypy_error_watermark = 26   # Updated Phase 42 D-08 post-strict-overrides addition. Old floor: 44 (Phase 37 tip).
```

After TYPE-01 fixes, update to the measured post-fix count. Keep the same comment format exactly — `check_mypy_watermark.py` uses regex `r"^\s*#\s*mypy_error_watermark\s*=\s*(\d+)"`.

**The two-step atomic change:**
1. Add `"firestarter.eprom_operations"` to the `module = [...]` list in the strict-island block (lines 131-145), between `"firestarter.exceptions"` and `"firestarter.serial_comm"` (alphabetical order is conventional but not enforced).
2. Remove `"firestarter.eprom_operations"` from the `module = [...]` list in the silent block (lines 151-162).
3. Update the watermark comment to the new measured count.

**Critical pitfall:** mypy applies the last matching `[[tool.mypy.overrides]]` block. The silent block (L147) appears AFTER the strict-island block (L131). If `firestarter.eprom_operations` is left in BOTH blocks, the silent block wins and the strict-island override is defeated. Remove from silent block in the same commit that adds to strict block.

---

### `firestarter_app/firestarter/eprom_operations.py` (service, CRUD, MODIFY — TYPE-01)

**Analog:** `firestarter_app/firestarter/serial_comm.py` (strict-island sibling — same `Optional` narrowing pattern)

**Imports pattern** (lines 1-20 of serial_comm.py — follow same `# noqa: UP035` for typing imports):

```python
from typing import Callable, Dict, Optional, Tuple  # noqa: UP035
```

The `# noqa: UP035` suppresses ruff UP035 ("use `dict` / `tuple` etc. instead of `typing.Dict` / `typing.Tuple`") — required because `pyproject.toml` `target-version = py39` is set but `from __future__ import annotations` is not used. Keep existing import style; add missing type imports from `typing` as needed (e.g., `List`, `Any`).

**assert-narrowing pattern for `Optional` members** (serial_comm.py lines 134-138):

```python
def send_bytes(self, data_bytes: bytes) -> int:
    """Write raw bytes to the serial port and return the byte count written."""
    if not self.is_connected():
        raise SerialError("Not connected.")
    assert self.connection is not None  # narrow for mypy strict (D-06)
    try:
        written_bytes = self.connection.write(data_bytes)
```

Apply the same pattern for `self.comm: SerialCommunicator | None` accesses in `eprom_operations.py`. At the top of each method that directly accesses `self.comm` (e.g., `_execute_phase`, `_main_phase_simple`, `_main_phase_send_data`, `_main_phase_read_data`):

```python
def _execute_phase(
    self, phase_name: str, progress: ClassProgressHandler
) -> Optional[str]:
    """Executes a single phase (INIT or END) of the state machine."""
    assert self.comm is not None  # narrowing: method only reachable after _setup_operation sets comm
    self.comm.send_ack()
    # ... rest of body unchanged
```

**ClassProgressHandler annotation pattern** — add return type annotations to all 4 methods. The existing unannotated signatures (lines 111-146 of eprom_operations.py) become:

```python
class ClassProgressHandler:
    def __init__(self, progress_callback: Optional[Callable[..., None]] = None) -> None:
        ...

    def start(self, total_steps: int) -> None:
        ...

    def update(self, completed_steps: int) -> None:
        ...

    def set_progress(self, current: int, total: int) -> None:
        ...

    def close(self) -> None:
        ...
```

**Documented residual ignore pattern** (D-08 escape hatch — for cross-module untyped calls where the callee module is not in the strict island this phase):

```python
result = extract_hex_to_decimal(value)  # type: ignore[no-untyped-call]  # utils.py not yet in strict island; lift when utils moves to strict
```

**The one runtime bug fix** (line 381 — not annotation-only, but behavior-preserving):

```python
# Before (Python 3.11+ only; TypeError on Python 3.9):
header = b"#" + len(data_chunk).to_bytes(2, "big") + checksum.to_bytes(1)

# After (Python 3.9 compatible; single byte, endianness has no effect):
header = b"#" + len(data_chunk).to_bytes(2, "big") + checksum.to_bytes(1, "big")
```

**bare `dict`/`Callable` fix pattern** — for the 15 `[type-arg]` errors, add type parameters:

```python
# Before:
def some_method(self, config: Dict) -> Callable:
# After:
def some_method(self, config: Dict[str, Any]) -> Callable[..., None]:
```

**Validation sequence** (run after each fix batch):
```bash
cd /workspaces/firestarter_app && python -m mypy firestarter/eprom_operations.py --strict --no-error-summary
cd /workspaces/firestarter_app && python tools/check_mypy_watermark.py
cd /workspaces/firestarter_app && python -m pytest tests/test_serial_characterization.py tests/test_decoder.py -v -q
```

---

### `firestarter_app/tools/check_mypy_watermark.py` (utility, READ-ONLY for patterns)

**Role:** This file is not modified in TYPE-01 — it reads the watermark from `pyproject.toml` and compares against the live mypy error count. The planner should instruct the executor to update the `pyproject.toml` watermark comment; this tool validates the result.

**Watermark regex** (line 31-34 of check_mypy_watermark.py — DO NOT CHANGE FORMAT):

```python
m = re.search(
    r"^\s*#\s*mypy_error_watermark\s*=\s*(\d+)", text, flags=re.MULTILINE
)
```

Any deviation from `# mypy_error_watermark = N` comment format causes exit code 2 (configuration error) which blocks CI.

---

### `.planning/MILESTONES.md` (planning doc, MODIFY — add v1.9 entry)

**Analog:** `.planning/MILESTONES.md` lines 1-80 (v1.8 entry — exact format precedent)

**v1.8 heading line format** (line 3 — follow exactly):

```markdown
## v1.8 — Host CLI Structural Cleanup (firestarter_app) — Shipped 2026-05-29
```

**v1.9 heading line shape** (fill in at milestone close):

```markdown
## v1.9 — Read-Bug RCA + Cleanup (firestarter + firestarter_app) — Shipped [date]
```

**Top-matter paragraph format** (v1.8 line 5 — single dense paragraph):

```markdown
**Phases:** [N] (numbered 44-48) | **Plans:** [N] (Phase 44 = N, ...) | **Timeline:** [start date] → [end date] | **Ship tag:** `3.0.0b8` (beta-only — stable `3.0.1` deferred to operator authorization per D-11) | **Commits:** meta-repo [N], firestarter sub-repo [N] (notable: [...]), firestarter_app sub-repo [N] (notable: [...])
```

**Delivered paragraph format** (v1.8 line 7 — single dense paragraph summarizing the milestone deliverables):

```markdown
**Delivered:** v1.9 is the **Read-Bug RCA + Post-RCA Cleanup** milestone. [RCA findings: Bug A = Rev 0 shield read-path fault, read-strobe-causal — Phase 44. Bug B = [Phase 45 outcome]. Fix = [Phase 46 short-strobe or equivalent]. Acceptance gate = [Phase 47 N≥5 result]]. TYPE-01 lifts GATE-1.8d: `eprom_operations.py` moved to mypy strict island (9th module). COBS-01 delivers `v1.9-COBS-DECISION.md`: libraries REJECT, auto-resync concept DEFER. [...requirements closed...]
```

**Key Accomplishments section** (v1.8 lines 9-25 — numbered list, one item per phase):

```markdown
### Key Accomplishments

1. **Phase 44 — Bug A RCA (read-strobe causal).** [summary]
2. **Phase 45 — Bug B RCA ([TBD from Phase 45 SUMMARY.md]).** [summary]
3. **Phase 46 — Read-Path Fix ([TBD from Phase 46 SUMMARY.md]).** [summary]
4. **Phase 47 — Acceptance Gate (N≥5 reads, [TBD result]).** [summary]
5. **Phase 48 — COBS Evaluation + TYPE-01 + Milestone Close.** COBS-01: fresh survey of 7 candidates → libraries REJECT, concept DEFER (`v1.9-COBS-DECISION.md`). TYPE-01: `eprom_operations.py` joins 8-module strict island; 53 strict errors resolved (behavior-preserving annotations + assert guards + one `to_bytes(1, "big")` Python 3.9 bug fix). Watermark updated. Milestone closed per D-10/D-11/D-12.
```

**Branch Strategy section** (v1.8 lines 27-29):

```markdown
### Branch Strategy

Per operator standing instruction (memory `feedback_branching`): all v1.9 work landed on `v1.9-read-bug-rca` branches. `firestarter` sub-repo `v1.9-read-bug-rca` off `beta@3.0.0b6` (v1.7 close tip); `firestarter_app` sub-repo `v1.9-read-bug-rca` off `beta@3.0.0b7` (v1.8 close tip); meta-repo `v1.9-read-bug-rca` off `main`. Both sub-repos merge to `beta`; meta merges to `main`. Ship tag `3.0.0b8` is **LOCKED beta-only** per D-11 — stable `3.0.1` bump DEFERRED to explicit operator authorization. No stable promotion at this milestone close.
```

**Stats table format** (v1.8 lines 46-65 — markdown table, one row per metric):

```markdown
### Stats

| Metric | Value |
|--------|-------|
| Phases | [N] (numbered 44-48) |
| Plans | [N] total (...) |
| Requirements (v1.9 scope) | [N] total; [N] DELIVERED (...) + [N] VERIFIED-at-close (...) |
| Meta-repo commits | [N] |
| Firestarter sub-repo commits | [N] (notable: [...]) |
| Firestarter_app sub-repo commits | [N] (notable: [...]) |
| mypy strict module list | main, cli_handlers, chip_resolver, frame_parser, codec, address_parser, exceptions, serial_comm, **eprom_operations** |
| mypy strict errors resolved (TYPE-01) | 53 (16 no-untyped-def + 15 type-arg + 9 union-attr + 9 no-untyped-call + 2 no-any-return + 1 call-arg + residual ignores) |
| Test count at v1.9 close | [N] (was 387 at phase start) |
| Coverage at v1.9 close | [N]% (≥ 70% floor) |
| Firmware RAM (Uno) | [N]% ([N]/2048 bytes, [N] B free) |
| Bug A | Rev 0 shield read-path fault, read-strobe-causal (Phase 44 RCA) |
| Bug B | [Phase 45 outcome] |
| Ship tag | `3.0.0b8` (beta-only) |
| Hardware impact | Firmware: read-timing knobs (Phase 44) + read-path fix (Phase 46) |
```

**Conditional content note for planner:** The Phase 45/46/47 outcome fields in the Delivered paragraph and Key Accomplishments items 2/3/4 CANNOT be filled at planning time. The milestone-close plan must include an explicit task: "Populate Phase 45-47 fields from their SUMMARY.md and evidence files at Phase 48 execution time, after Phase 47 completes."

---

## Shared Patterns

### mypy `Optional` narrowing via `assert x is not None`
**Source:** `firestarter_app/firestarter/serial_comm.py` line 138
**Apply to:** All `eprom_operations.py` methods that access `self.comm` directly
```python
assert self.connection is not None  # narrow for mypy strict (D-06)
```

### Documented residual ignore (D-08 escape hatch)
**Source:** RESEARCH.md §TYPE-01 + CONTEXT.md D-08
**Apply to:** Cross-module untyped calls in `eprom_operations.py` where the callee module is not yet in the strict island
```python
result = fn()  # type: ignore[no-untyped-call]  # <callee>.py not yet in strict island; lift when it moves to strict
```

### pyproject.toml `[[tool.mypy.overrides]]` block shape
**Source:** `firestarter_app/pyproject.toml` lines 131-145
**Apply to:** The TYPE-01 strict-island extension
```toml
[[tool.mypy.overrides]]
module = [
    "firestarter.main",
    ...
    "firestarter.eprom_operations",  # TYPE-01 addition
]
disallow_untyped_defs = true
check_untyped_defs = true
```

### Watermark comment format (must not deviate)
**Source:** `firestarter_app/pyproject.toml` line 115 + `tools/check_mypy_watermark.py` lines 31-34
**Apply to:** pyproject.toml watermark update in TYPE-01
```toml
# mypy_error_watermark = N   # Updated Phase 48 TYPE-01 post-eprom_operations strict addition. Old floor: 26 (Phase 42 tip).
```

### MILESTONES.md entry — heading + top-matter + body
**Source:** `.planning/MILESTONES.md` lines 1-80 (v1.8 entry)
**Apply to:** v1.9 entry appended at the top (above v1.8 entry)
Format: H2 heading → bold top-matter pipe-separated paragraph → `**Delivered:**` paragraph → `### Key Accomplishments` numbered list → `### Branch Strategy` → open backlog → `### Stats` table → `### Key Decisions` table (optional)

---

## No Analog Found

No files in this phase are entirely without precedent — all have structural analogs in the existing codebase or planning artifacts.

| File | Role | Data Flow | Note |
|------|------|-----------|------|
| `.planning/v1.9-COBS-DECISION.md` | planning doc (ADR) | doc-only | No prior ADR-style doc exists; closest structural analog is v1.7-SHIELD-REVS.md (numbered sections, evidence-tagged claims). RESEARCH.md provides the full candidate survey content directly. |

---

## Metadata

**Analog search scope:** `firestarter_app/pyproject.toml`, `firestarter_app/firestarter/serial_comm.py`, `firestarter_app/firestarter/frame_parser.py`, `firestarter_app/firestarter/eprom_operations.py`, `firestarter_app/tools/check_mypy_watermark.py`, `.planning/MILESTONES.md`, `.planning/v1.7-SHIELD-REVS.md`
**Files scanned:** 7
**Pattern extraction date:** 2026-06-01

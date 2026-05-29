# Phase 44: Bug A RCA — Modified Rev 0 Upper-Address Jitter - Research

**Researched:** 2026-05-29
**Domain:** Embedded firmware signal-integrity RCA, serial-protocol dev-param extension, bench automation
**Confidence:** HIGH (codebase inspected directly; empirical evidence substrate read verbatim from planning artifacts)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Static circuit first. Before any sweep, inspect the Modified Rev 0 modifications with multimeter + v1.7 schematic — checking for missing series termination on A15, data-bus pull-down resistor values, and supply sag — to form a specific hypothesis. The sweep then confirms it causally.
- **D-02:** The Modified Rev 0 mods are treated as the prime suspect and are documented in the v1.7 shield-revisions docs; the static check verifies the physical board matches that documented mod record.
- **D-03:** Firmware sweep = the causal lead. Root cause is proven by manipulation: vary the timing knob(s), re-run the diagnostic, and show the jitter rate moves. LA / scope / multimeter captures are corroborating evidence, not the headline.
- **D-04:** The sweep varies both (a) address-settling delay (NOPs/µs after address set, before data latch) and (b) read-strobe (`/OE` or `/CE`) pulse width. 2D sweep space.
- **D-05:** Both knobs are exposed as host-tunable dev parameters (serial param / dev command), swept from the host with the chip seated — NO re-flash and NO chip reseat between data points.
- **D-06:** Causal-only bar. RCA-01 closes when a timing knob drives the upper-address jitter to ~zero. Localization and LA/scope capture are corroborating, not gating.
- **D-07:** D-06 governs over the ROADMAP Phase 44 success-criterion-1 wording. "A demonstrated knob that controls the jitter" is sufficient; mechanism-naming is a stretch goal.
- **D-08:** Bench instruments: simple (low-bandwidth) scope, 8-channel LA, multimeter. No high-bandwidth analog scope. LA is the strongest witness tool.
- **D-09:** Physical probing (scope/LA/multimeter/photos/chip-handling) is operator-only; Claude drives firmware sideload, host reads, serial, and sweep automation.
- **D-10:** Rev 2.2 deferred to Phase 45. Phase 44 records the Rev 2.2 map entry as "untested — predicted clean per v1.7 capability matrix".
- **D-11:** Controlled pre-fix baseline = re-run `dev consistency-check` at N=5 on the same Leonardo board / W27C512 / port as Phase 29 v2 substrate, and byte-compare against the 15 captured binaries.

### Claude's Discretion
- Baseline-repro rigor (D-11) — defaulted, open to operator override.
- Where RCA evidence/docs are written (meta `.planning/` vs `firestarter/doc/`), and whether the sweep knobs ship as a dev-command vs build-flag.

### Deferred Ideas (OUT OF SCOPE)
- Rev 2.2 physical bench test → Phase 45.
- Naming the single dominant electrical mechanism (ringing vs settling vs crosstalk vs supply sag) → stretch goal beyond D-06 causal-only bar.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| RCA-01 | Bug A root cause proven — Modified Rev 0 upper-address (A15=1) jitter instrumented to a definitive signal-integrity mechanism, beyond Phase 29 v2 characterized symptom (1.86× skew, 63% bit-raise) | D-03 firmware sweep: add host-tunable settling + strobe knobs; show knob drives jitter to ~zero = causal proof. Code path: `memory_get_data()` in `memory.cpp` (address settle delay at line 189: `delayMicroseconds(3)`; chip-enable strobe width governs /CE pulse). |
| RCA-03 (partial) | Per-rev failure-mode map confirmed — Modified Rev 0 → Bug A confirmed; Rev 2.2 entry recorded | D-10 defers Rev 2.2 bench. Phase 44 writes "Modified Rev 0 → Bug A (upper-address jitter)" + "Rev 2.2 → untested, predicted clean per v1.7 capability matrix". |
</phase_requirements>

---

## Summary

Phase 44 is an embedded signal-integrity RCA phase. The empirical substrate (15 × N=5 W27C512 binaries from Phase 29 v2, characterized as Bug A: 1.86× A15=1 jitter rate, 63% bit-raise, upper-24KB concentration) is on disk and verified. The phase proves Bug A by manipulation, not just by observation: two firmware timing knobs (address-settling delay and /CE or /OE read-strobe pulse width) are exposed as host-tunable dev parameters and swept 2D from the host, chip seated throughout. If either knob drives the WORST jitter rate to ~zero, Bug A is causally proven and RCA-01 closes. LA and scope observations are corroborating witnesses, not the headline proof.

The read path in firmware (`memory_get_data()` in `memory.cpp`) has a hardcoded `delayMicroseconds(3)` between `rurp_chip_enable()` and `rurp_read_data_buffer()` — this is the settling knob's instrument point. The `_NOP()` settling already added at commit `4f205e58` (parked Plan 28-04) sits in `rurp_read_data_buffer()` between PIND/PINC/PINE reads on the Leonardo and is the secondary mechanism. The existing `pulse_delay` field in `firestarter_handle_t` and its JSON wire key `"pulse-delay"` demonstrate the pattern for adding new host-tunable numeric fields: (1) add field to `firestarter_handle_t`, (2) add PROGMEM key + parser entry in `json_parser.c`, (3) mirror the constant in `constants.py` (sync rule per CLAUDE.md), (4) emit the field from the host in the JSON command sent by `dev consistency-check`. No re-flash is required between sweep points; the JSON command carries the knob value on each run.

The primary prerequisite: fork `v1.9-read-bug-rca` branches off `beta` in both sub-repos. The firmware submodule is currently detached at `efd203a` (pre-v1.7, no `doc/SHIELD-REVISIONS.md`). The v1.7 shield docs needed for the static check (D-01/D-02) live on the `v1.7-shield-investigation` branch in the meta-repo and on the `beta` branch of the firmware sub-repo (commit `59a5e58`). The v1.9 firmware branch must be cut from `beta` (not from `efd203a`) so that the v1.7 shield-detect plumbing and `doc/SHIELD-REVISIONS.md` are present on the working tree.

**Primary recommendation:** Add two host-tunable dev params (`"read-settling-delay"` and `"read-strobe-us"`) to the JSON wire protocol, implement them in `memory_get_data()`, run a 2D sweep of (settling, strobe) × `dev consistency-check --runs 5 -q`, and show the WORST zero-byte ratio tracks the knobs. That's the causal proof. All other work (static check, LA capture, per-rev map) is supporting.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Host-tunable sweep param delivery | Host CLI (Python) | Serial protocol (JSON) | The host builds the JSON command; firmware parses it. The knob value travels as a JSON field per the established `"pulse-delay"` pattern. |
| Settling delay enforcement | Firmware (AVR C++) | — | `delayMicroseconds()` / `_NOP()` calls in `memory.cpp::memory_get_data()` and `leonardo_rurp_shield.cpp::rurp_read_data_buffer()` run on the MCU; the host cannot insert delays in the read path. |
| Read-strobe (/CE) pulse width control | Firmware (AVR C++) | — | `rurp_chip_enable()` / `delayMicroseconds()` / `rurp_chip_disable()` sequence in `memory_get_data()`. The `"pulse-delay"` field already controls the write-strobe; a parallel `"read-strobe-us"` field controls the read-strobe. |
| Sweep harness / data collection | Host CLI (Python) | — | Shell loop or Python script calls `firestarter dev consistency-check --runs 5 -q` per (settling, strobe) point, reads WORST metric from exit code + stdout. |
| LA / scope triggering and capture | Operator (bench) | — | Physical probing is operator-only (D-09). Claude provides the target signal labels (A15, A14, /CE, D0-D7) and trigger conditions; operator attaches probes. |
| Baseline repro validation | Host CLI + firmware | — | `dev consistency-check --runs 5` byte-compared against the 15 Phase 29 v2 binaries confirms bench continuity before any knob change. |
| Per-rev failure-mode map | Meta-repo docs (`.planning/`) | Firmware sub-repo (`doc/`) | Map is a planning artifact; physical bench result annotated in `.planning/v1.6-EVIDENCE.md` or a new Phase 44 evidence file. |

---

## Standard Stack

This phase uses only existing in-repo tooling. No new external libraries are introduced.

### Core (existing, no install needed)

| Tool | Version | Purpose | Status |
|------|---------|---------|--------|
| PlatformIO CLI | 6.1.19 | Firmware build (`pio run -e leonardo`) and native test (`pio test -e native`) | Available [VERIFIED: environment check] |
| firestarter host CLI | 3.0.0b5 (editable install from `/workspaces/firestarter_app`) | `dev consistency-check`, serial commands | Available [VERIFIED: environment check] |
| AVR-GCC (via PlatformIO) | bundled with pio | Compiles `memory.cpp` + `leonardo_rurp_shield.cpp` | Available [VERIFIED: pio 6.1.19 in path] |
| Unity (via PlatformIO native) | bundled | Native host-side unit tests for new dispatch cases | Available [VERIFIED: existing test suite runs] |
| Python 3.12 | 3.12.13 | Sweep harness scripting, baseline byte-comparison | Available [VERIFIED: environment check] |

### Supporting (for sweep and forensics)

| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| `hashlib.sha256` (stdlib) | stdlib | Byte-compare sweep runs against Phase 29 v2 binaries | Sweep harness and baseline validation |
| `tqdm` (installed) | installed | Progress bars for multi-run sweep | Already a host CLI dep |

### No External Packages Added

This phase installs zero new Python or C packages. The sweep harness is written in-repo (plain Python script or shell loop). The firmware param extension follows the established `"pulse-delay"` pattern — no new libraries.

---

## Package Legitimacy Audit

No new external packages are installed in this phase. All tooling is existing in-repo or standard-library.

| Package | Registry | Disposition |
|---------|----------|-------------|
| (none) | — | No new installs — N/A |

---

## Architecture Patterns

### System Architecture Diagram

```
Host (Python)                       Firmware (AVR/Leonardo)
─────────────────────────────────   ─────────────────────────────────────
sweep_harness.py                    memory.cpp :: memory_get_data()
  for settling in [0..N]:
    for strobe in [0..M]:              firestarter_handle_t.read_settling_us
      build JSON cmd with               → delayMicroseconds(read_settling_us)
        "read-settling-delay": s        after set_address() / before chip_enable()
        "read-strobe-us": w       ──► 
      → serial send JSON          
                                       firestarter_handle_t.read_strobe_us
      dev consistency-check            → delayMicroseconds(read_strobe_us)
        runs N=5 reads                  in chip_enable()→read→chip_disable()
        each read: COMMAND_READ         sequence
        with knob params in JSON
      ← stdout: WORST ratio      ◄──
      collect metric grid

json_parser.c (parse keys)
  "read-settling-delay" → handle->read_settling_us
  "read-strobe-us"      → handle->read_strobe_us
constants.py (host mirror)
  JSON_KEY_READ_SETTLING = "read-settling-delay"
  JSON_KEY_READ_STROBE   = "read-strobe-us"
```

### Recommended Project Structure (phase 44 artifacts)

```
.planning/phases/44-bug-a-rca-modified-rev-0-upper-address-jitter/
├── 44-RESEARCH.md                  # this file
├── 44-PLAN.md                      # planner output
└── evidence/
    ├── static-check-notes.md       # D-01 multimeter readings
    ├── sweep-grid.csv              # (settling, strobe) → WORST metric
    └── la-capture-notes.md         # LA trigger config + operator notes

firestarter/include/firestarter.h   # add read_settling_us + read_strobe_us fields
firestarter/src/json_parser.c       # add PROGMEM keys + parser entries
firestarter/src/proms/memory.cpp    # instrument memory_get_data() with knobs
firestarter_app/firestarter/constants.py  # mirror new JSON key names
firestarter_app/firestarter/eprom_operations.py  # emit knob params in read commands
```

### Pattern 1: Host-Tunable Dev Param (the `pulse-delay` model)

**What:** A numeric field is added to `firestarter_handle_t`, parsed from the JSON command by `json_parser.c`, and consumed in the firmware read/write path. The host emits the field in the JSON dict built by `eprom_operations.py`.

**When to use:** Any time a firmware timing parameter must be varied from the host without re-flashing.

**Implementation pattern** (from `json_parser.c` — the `"pulse-delay"` precedent): [CITED: `/workspaces/firestarter/src/json_parser.c` lines 55-73, 303-305]

```c
// In json_parser.c:
const char key_read_settling[] PROGMEM = "read-settling-delay";
const char key_read_strobe[]   PROGMEM = "read-strobe-us";

// Add to key_parsers[] array:
{key_read_settling, get_read_settling},
{key_read_strobe,   get_read_strobe},

// Parser functions (same pattern as get_delay):
bool get_read_settling(const char* json, jsmntok_t* tokens, int pos,
                       firestarter_handle_t* handle) {
    extract_long("read-settling-delay", handle->read_settling_us);
}
bool get_read_strobe(const char* json, jsmntok_t* tokens, int pos,
                     firestarter_handle_t* handle) {
    extract_long("read-strobe-us", handle->read_strobe_us);
}
```

**In `firestarter_handle_t` (firestarter.h)** — add alongside `pulse_delay`:
```c
uint32_t read_settling_us;   // address-settling delay before data latch (0 = default 3µs)
uint32_t read_strobe_us;     // /CE read-strobe pulse width in µs (0 = default 3µs)
```

**In `memory_get_data()` (memory.cpp)** — instrument with knobs: [CITED: `/workspaces/firestarter/src/proms/memory.cpp` lines 182-194]

```c
uint8_t memory_get_data(firestarter_handle_t* handle, uint32_t address) {
    rurp_chip_output();
    address = mem_util_remap_address_bus(handle, address, READ_FLAG);

    handle->firestarter_set_address(handle, address);
    rurp_set_data_input();

    // Address-settling delay: time from address-set to chip-enable
    // Default = 3µs (current hardcoded). Knob: "read-settling-delay" JSON field.
    uint32_t settling = handle->read_settling_us ? handle->read_settling_us : 3;
    delayMicroseconds(settling);

    rurp_chip_enable();

    // Read-strobe pulse width: time /CE is asserted
    // Default = 0 (current: immediate read). Knob: "read-strobe-us" JSON field.
    uint32_t strobe = handle->read_strobe_us;
    if (strobe) delayMicroseconds(strobe);

    uint8_t data = rurp_read_data_buffer();
    rurp_chip_disable();

    return data;
}
```

**In `constants.py` (host)** — SYNC RULE: add JSON key names alongside existing keys:
```python
# Dev sweep knobs — Firmware sync: json_parser.c (key_read_settling, key_read_strobe)
JSON_KEY_READ_SETTLING_DELAY = "read-settling-delay"
JSON_KEY_READ_STROBE_US = "read-strobe-us"
```

**In `eprom_operations.py`** — the `_operation_context` or JSON command builder emits these fields when non-zero:
```python
if read_settling_us:
    cmd["read-settling-delay"] = read_settling_us
if read_strobe_us:
    cmd["read-strobe-us"] = read_strobe_us
```

### Pattern 2: 2D Sweep Harness (host script)

**What:** A Python script (or shell loop) iterates over a grid of (settling, strobe) values, calls `firestarter dev consistency-check --runs 5 -q` once per point with the sweep params, collects the exit code (0=PASS, 1=FAIL) plus WORST metric from stdout, and writes a CSV.

**When to use:** When proving causality — the jitter rate must track the knob.

**Example sweep structure** (to be implemented by executor):
```python
# sweep_bug_a.py — Phase 44 sweep harness
import subprocess, csv

SETTLING_VALUES = [0, 3, 10, 25, 50, 100]   # µs
STROBE_VALUES   = [0, 3, 10, 25, 50]         # µs
RUNS = 5
CHIP = "W27C512"
PORT = "/dev/ttyACM1"  # operator confirms at session start

with open("sweep-grid.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["settling_us", "strobe_us", "exit_code", "worst_note"])
    for s in SETTLING_VALUES:
        for t in STROBE_VALUES:
            # Hypothetical: dev consistency-check will accept --settling and --strobe
            # options (or env vars) once the firmware + host params land.
            result = subprocess.run(
                ["firestarter", "-p", PORT, "dev", "consistency-check",
                 CHIP, "--runs", str(RUNS), "-q",
                 "--read-settling", str(s), "--read-strobe", str(t)],
                capture_output=True, text=True
            )
            w.writerow([s, t, result.returncode, result.stdout.strip()[-200:]])
```

**Key constraint (D-05):** chip must remain seated throughout the sweep. The JSON command delivers the knob value per read; no re-flash occurs.

### Pattern 3: Baseline Byte-Compare (D-11)

**What:** After bench setup, before any knob change, run N=5 `dev consistency-check` on the same Leonardo/W27C512/port as Phase 29 v2, then byte-compare run_01.bin against the 15 Phase 29 v2 binaries.

**Reference binaries:** [CITED: `.planning/milestones/v1.6-phases/29-multi-board-bench-verification/29-04-SUMMARY.md`]
- `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-155021-v2/run_0[1-5].bin` (canonical first session)
- `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-160035-v2-rep/run_0[1-5].bin` (replication)
- `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-155617-v2-rev20/run_0[1-5].bin` (Rev 2.0 bonus, for comparison)

**Expected result:** 5 distinct SHAs (jitter present), WORST zero-byte ratio ≥ 0.04% (matches Phase 29 v2's 0.046%/0.047%), A15=1 jitter rate ≈ 1.70% vs A15=0 ≈ 0.92%.

**5-line byte-compare (re-runnable):** [CITED: `.planning/v1.6-EVIDENCE.md` Phase 27 cross-check pattern]
```python
import glob, hashlib
ref_dir = ".planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-155021-v2/"
new_dir = "<new-baseline-dir>/"
for i in range(1, 6):
    ref = open(f"{ref_dir}run_{i:02d}.bin", "rb").read()
    new = open(f"{new_dir}run_{i:02d}.bin", "rb").read()
    diffs = sum(a != b for a, b in zip(ref, new))
    print(f"run_{i:02d}: {diffs}/65536 byte differences vs Phase 29 v2 ref")
```

### Pattern 4: LA Trigger Setup for A15=1 Read Accesses

**What:** Configure the 8-channel LA to trigger on the A15 line going HIGH (or on the combination A15=1 + /CE falling edge). This aligns captures to the moments when the upper-address population (the Bug A-affected region) is being read, making A15-vs-/CE timing directly visible.

**Channel assignment (suggested):**
- Ch0: A15 (the primary jitter line; 1.86× skew signal)
- Ch1: A14 (secondary; 1.46× skew)
- Ch2: A13 (reference — low jitter expected)
- Ch3: /CE (chip-enable, active-low)
- Ch4: /OE (output-enable, if wired separately)
- Ch5-Ch7: D0, D1, D7 (sample data bus for tristate detection)

**Trigger condition:** A15 rising edge (LOW→HIGH transition). Sample rate: maximum available on the 8-ch LA. Capture depth: enough for several address cycles (~1 µs per read cycle at 3µs settle + chip-enable).

**What to look for:** A15 still settling (ringing or slow slew) when /CE asserts. If A15 is still bouncing when /CE falls, the chip latches an indeterminate address and may read from the wrong location (or from a cell whose drive is marginal).

**Multimeter measurements (D-01 static check):**
- A15 series resistance to the RURP address driver: measure between RURP bus pin and A15 chip pin. Missing or absent series termination (should be 33–100Ω for signal integrity) is the "ringing" hypothesis.
- Data bus pull-down resistors (D0-D7): measure each pull-down to ground. Weak pull-downs (high resistance) support the "63% bit-raise" observation (chip's weak output drives the bus high vs pull-down).
- VPP at chip pin with chip seated, during a read: measure (should be ~0V during read, not elevated).
- VCC rail sag: scope or multimeter on VCC during rapid address transitions (upper-24KB reads toggle many bits simultaneously — worst-case ground bounce).

### Anti-Patterns to Avoid

- **Re-flashing between sweep points (D-05 violation):** The chip-out-before-sideload rule means every re-flash also means a chip reseat, injecting pin-contact variance into the measurement. The knob MUST be a runtime serial parameter, not a build-time define.
- **Treating the `_NOP()` settling at commit `4f205e58` as the sole knob:** The existing NOPs in `rurp_read_data_buffer()` address the between-PINx-read race (secondary mechanism). The primary address-settling knob lives in `memory_get_data()` — time from `firestarter_set_address()` to `rurp_chip_enable()`. Both knobs should be independently sweepable.
- **Using `pulse_delay` as the settling knob:** `pulse_delay` controls write-strobe width in `memory_set_data()`. It is NOT in the read path. Adding read timing to write timing would corrupt the write path's programming pulse intervals.
- **Performing the sweep before the baseline repro (D-11):** The sweep is only meaningful if bench continuity with Phase 29 v2 is first confirmed. If the baseline repro fails (different jitter signature), the phase is blocked until the cause is understood.
- **Leaving `read_settling_us == 0` as the zero-settling test point:** The current default `delayMicroseconds(3)` in `memory_get_data()` runs when the field is 0 (unset). The sweep must distinguish "0 = default (3µs)" from "0 = actual zero delay". Either use a sentinel (e.g., 0xFF = default, 0 = actual zero) or initialize the field to 3 in `json_init`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Per-byte progress display during sweep | Custom tqdm wrapper | `firestarter dev consistency-check -q` (quiet flag suppresses inner tqdm per-run bars) | `-q` flag exists; wrapping again adds complexity |
| JSON serialization for the host command | Custom string builder | `json.dumps()` (already used throughout `serial_comm.py` and `eprom_operations.py`) | Established pattern |
| AVR delay in firmware | Bit-banged loop | `delayMicroseconds()` / `_NOP()` (Arduino framework) | AVR interrupt jitter makes hand-rolled loops unreliable; `delayMicroseconds()` uses timer compare |
| Signal integrity measurement | Custom scope software | Operator's 8-ch LA + multimeter (D-08) | Phase constraint; no high-bw scope available |
| Baseline binary comparison | Custom diff tool | `hashlib.sha256` + zip-compare Python 5-liner (established in-project pattern) | Phase 27/29 both used this exact pattern; results reproducible |

**Key insight:** Every new mechanism needed by Phase 44 has a direct precedent already in this codebase. The `"pulse-delay"` / `get_delay()` pattern in `json_parser.c` is the exact template for the two new read-timing knobs. Zero hand-rolling required.

---

## Runtime State Inventory

> Not a rename/refactor phase — this section is omitted per instructions.

---

## Common Pitfalls

### Pitfall 1: Forking the v1.9 Branch from `efd203a` Instead of `beta`

**What goes wrong:** If the v1.9 firmware branch is cut from `efd203a` (the current submodule detach point), it will be missing the entire v1.7 shield-detect plumbing (`rurp_hw_rev_utils.h`, `rurp_pinout.h` ADC band table, `doc/SHIELD-REVISIONS.md`). The static check (D-01/D-02) requires comparing the Modified Rev 0 physical board against the schematic in `doc/SHIELD-REVISIONS.md`. The ADC-detect firmware is also required by D-09 for per-port controller identity verification.

**Why it happens:** The submodule pointer in the meta-repo is stuck at `efd203a` (end of v1.6 work). The `beta` branch tip is `0bbe017` (v1.6-read-bug merge), which has the v1.7 plumbing because v1.7 was merged into `beta` at `59a5e58` → `c923e2b` → `0bbe017`.

**How to avoid:** `cd /workspaces/firestarter && git checkout beta && git checkout -b v1.9-read-bug-rca` — then verify `doc/SHIELD-REVISIONS.md` exists.

**Warning signs:** `ls /workspaces/firestarter/doc/SHIELD-REVISIONS.md` returns "no such file" — means the branch predates v1.7.

### Pitfall 2: Constants Drift — Adding Firmware Fields Without Updating `constants.py`

**What goes wrong:** `json_parser.c` accepts the new `"read-settling-delay"` JSON key, but `constants.py` doesn't define the key name. The host may use a string literal that diverges from the firmware's PROGMEM key string, causing the firmware to silently ignore the param (JSON unknown-field behavior = silently skipped per CLAUDE.md).

**Why it happens:** The CLAUDE.md sync rule ("change both together") is easy to miss for new fields.

**How to avoid:** Any new PROGMEM key in `json_parser.c` MUST have a corresponding `JSON_KEY_*` constant in `constants.py`. Add both in the same commit. Per CLAUDE.md: "Constants/flag bits are duplicated `constants.py` ↔ `firestarter.h`; serial protocol is duplicated `serial_comm.py` ↔ `firestarter.cpp` — any new dev param/flag for the knobs must be changed in BOTH."

**Warning signs:** `firestarter dev consistency-check ... --read-settling 50` has no effect on WORST — firmware is ignoring the param because the JSON key name doesn't match.

### Pitfall 3: Sweep With Zero-Settling Indistinguishable From Default

**What goes wrong:** `handle->read_settling_us = 0` is ambiguous: it could mean "host didn't set the param (use default 3µs)" or "host explicitly requested 0µs settling". If the firmware defaults to 3µs when the field is 0, the sweep cannot test the actual zero-settling point — a potentially important data point for proving the causal relationship.

**Why it happens:** The existing `pulse_delay` field uses 0 as "use protocol default" (see `eprom.cpp` lines 68-75). If `read_settling_us` is initialized to 0 in `json_parse()`, zero-param absence and zero-explicit-setting are indistinguishable.

**How to avoid:** Either (a) initialize `read_settling_us` to a sentinel value like `UINT32_MAX` meaning "use default", and only treat 0 as an explicit zero-delay request; or (b) define 0 to mean "use default (3µs)" and add a separate `--read-settling 0` vs unset distinction at the host. The simplest safe approach: treat 0 as "current default (3µs)" and add a `--raw-settling-zero` flag for the explicit-zero test. Document the convention in the code.

**Warning signs:** The sweep grid shows no difference between settling=0 and settling=3 — likely because both use the firmware default.

### Pitfall 4: Chip-Out During Sweep Point Transition (D-05 Violation)

**What goes wrong:** The chip is removed from the socket between sweep points (e.g., the operator reseats it "to check contact"). This injects pin-contact resistance variance that can dominate the jitter signal, invalidating the causal attribution.

**Why it happens:** D-05 is clear but the temptation to reseat is natural if the jitter looks strange.

**How to avoid:** The sweep harness must be framed to the operator as "do not touch the chip; the board; or the shield between sweep points". The chip-out rule applies ONLY before firmware sideload (chip-out-before-sideload per MEMORY.md), NOT during runtime parameter sweeps.

**Warning signs:** WORST metric jumps discontinuously between adjacent sweep points in a pattern inconsistent with the knob values — likely a reseat.

### Pitfall 5: `delayMicroseconds()` Granularity on AVR at 16 MHz

**What goes wrong:** `delayMicroseconds(1)` on AVR at 16 MHz has a practical minimum of ~1µs (16 cycles), but the overhead of the function call itself adds ~0.5–1µs of non-determinism at very short values. The sweep at values < 3µs may not produce clean step responses.

**Why it happens:** AVR `delayMicroseconds()` documentation notes that values below 3µs become inaccurate.

**How to avoid:** Set sweep minimum at 3µs (the current default). Use `_NOP()` counts for sub-3µs experiments (2 NOPs = ~125ns total). The firmware can implement a combined strategy: if `read_settling_us < 3`, use NOP counts; if `>= 3`, use `delayMicroseconds()`.

**Warning signs:** Sweep shows no improvement at 1µs and 2µs even though 3µs and above show a clear trend — likely `delayMicroseconds()` granularity floor.

### Pitfall 6: `memory_get_data()` vs `eprom_read_chip_byte()` — Wrong Instrument Point

**What goes wrong:** Bug A jitter is in the EPROM read path. The firmware has TWO mechanisms for reads: `memory_get_data()` (the generic path used by all chip families via `firestarter_get_data` function pointer) and board-specific `rurp_read_data_buffer()` (the `_NOP()` settling at `4f205e58`). The address-settling knob must be in `memory_get_data()`, NOT only in `rurp_read_data_buffer()`.

**Why it happens:** The Phase 27 RCA named BOTH `memory_get_data()` (address-settle gap, hardcoded `delayMicroseconds(3)`) and `rurp_read_data_buffer()` (between-PINx-read race, fixed by `4f205e58` NOPs) as mechanisms. The D-04 sweep targets BOTH — but they are at different levels of the call chain.

**How to avoid:** Map the full call chain: `memory_read_execute()` → `handle->firestarter_get_data()` → `memory_get_data()` → `handle->firestarter_set_address()` → `rurp_set_data_input()` → `rurp_chip_enable()` → `delayMicroseconds(3)` → `rurp_read_data_buffer()` → `rurp_chip_disable()`. The settling knob sits between `set_address` and `chip_enable`; the between-PINx NOP knob could be parameterized as a count but is harder to expose via JSON without adding a dedicated field. Start with the `delayMicroseconds(3)` knob (cleaner, larger effect expected) and the chip-enable strobe width knob.

**Warning signs:** Changing the settling delay has no effect on WORST — the wrong delay point was instrumented.

---

## Code Examples

Verified patterns from codebase inspection:

### The existing `delayMicroseconds(3)` in the read path
[CITED: `/workspaces/firestarter/src/proms/memory.cpp` lines 182-194 — direct inspection]

```c
// CURRENT read path — the 3µs delay is the settling knob's instrument point
uint8_t memory_get_data(firestarter_handle_t* handle, uint32_t address) {
    rurp_chip_output();
    address = mem_util_remap_address_bus(handle, address, READ_FLAG);
    handle->firestarter_set_address(handle, address);
    rurp_set_data_input();
    rurp_chip_enable();
    delayMicroseconds(3);          // ← address settling + chip-enable strobe combined
    uint8_t data = rurp_read_data_buffer();
    rurp_chip_disable();
    return data;
}
```

Note: The existing `delayMicroseconds(3)` occurs AFTER `rurp_chip_enable()`, meaning it is currently acting as the /CE read-strobe pulse width, NOT a pre-/CE address-settling delay. To separate the two knobs, the settling delay needs to be inserted BETWEEN `set_address()` and `chip_enable()`. This is an important pre-implementation detail for the planner.

### The parked `_NOP()` settling commit (4f205e58) in `rurp_read_data_buffer()`
[CITED: `/workspaces/firestarter/src/boards/leonardo_rurp_shield.cpp` lines 112-138 — direct inspection]

```c
// Current state of rurp_read_data_buffer() on the v1.6-read-bug branch (efd203a)
uint8_t rurp_read_data_buffer() {
    // _NOP() between each PINx read: 0.5-1.5 cycle latch latency per 32U4 datasheet §10.2.4
    // W27C512 tACC = 90 ns; 2× NOP @ 16 MHz = ~125 ns > tACC
    uint8_t pind_val = PIND;
    _NOP();
    uint8_t pinc_val = PINC;
    _NOP();
    uint8_t pine_val = PINE;
    // ... bit-map reassembly ...
    return data;
}
```

### The `pulse_delay` JSON field pattern (precedent for new knobs)
[CITED: `/workspaces/firestarter/src/json_parser.c` lines 55-73, 299-305; `/workspaces/firestarter/include/firestarter.h` line 84 — direct inspection]

```c
// firestarter.h — existing:
uint32_t pulse_delay;           // write-strobe width µs

// json_parser.c — existing PROGMEM key:
const char key_pulse_delay[] PROGMEM = "pulse-delay";
// Registered in key_parsers[]:
{key_pulse_delay, get_delay},
// Parser:
bool get_delay(...) { extract_long("pulse-delay", handle->pulse_delay); }
```

### `consistency_check_eprom()` call surface (host entry point for sweep)
[CITED: `/workspaces/firestarter_app/firestarter/eprom_operations.py` lines 497-510; `/workspaces/firestarter_app/firestarter/cli_handlers.py` lines 1030-1099 — direct inspection]

```python
# Current signature — new knob params need to be added here
def consistency_check_eprom(
    self,
    eprom_name: str,
    eprom_data_dict: dict,
    runs: int = 3,
    output_dir: Optional[str] = None,
    keep_files: bool = True,
    max_diffs: int = 10,
    quiet: bool = False,
    operation_flags: int = 0,
    read_settling_us: int = 0,    # NEW: address-settling delay in µs
    read_strobe_us: int = 0,      # NEW: /CE read-strobe pulse width in µs
) -> int:
    ...
```

### `dev consistency-check` CLI surface (host entry point for sweep)
[CITED: `/workspaces/firestarter_app/firestarter/cli_handlers.py` lines 1030-1099 — direct inspection]

```python
@dev.command(name="consistency-check")
# ... existing options ...
@click.option("--read-settling", "read_settling_us", type=int, default=0,
              help="Address-settling delay before /CE assert (µs; 0=firmware default)")
@click.option("--read-strobe", "read_strobe_us", type=int, default=0,
              help="/CE read-strobe pulse width (µs; 0=firmware default)")
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| "Bug is in Leonardo firmware" (Phase 27 RCA conclusion) | "Bug A is hardware-originated signal integrity on Modified Rev 0, NOT firmware-only" | Phase 29 v2 (2026-05-26) | Phase 28's pullup-clear fix (`437339b6`) was reverted because it improved Leonardo Phase 26 baseline but did NOT fix the residual upper-address jitter on Modified Rev 0. The jitter signature (A15=1 → 1.86× rate) persists post-revert. |
| `pulse_delay` = only host-tunable timing param | Add `read_settling_us` + `read_strobe_us` as parallel dev-only read-timing params | Phase 44 (new) | Enables 2D sweep without re-flash per D-04/D-05. |
| `delayMicroseconds(3)` hardcoded in read path | Make settling + strobe configurable at runtime | Phase 44 | Separates the pre-/CE settling window from the /CE pulse width (currently conflated in the hardcoded 3µs). |

**Key state-of-the-art insight:** The hardcoded `delayMicroseconds(3)` in `memory_get_data()` currently appears AFTER `rurp_chip_enable()`, not between `set_address` and chip-enable. This means the current code has a zero-settling window between address-set and /CE assertion, followed by a 3µs /CE pulse. The "settling knob" needs to inject a delay BEFORE `chip_enable()`, not extend the existing one. This is a non-obvious implementation detail that distinguishes "address-settling delay" from "read-strobe pulse width" in the current code.

**Deprecated:**
- `FLAG_VERBOSE (0x80)`: still present in `firestarter.h` but not used in the current read path for timing purposes.
- The Phase 27 hypothesis that `rurp_set_data_input()` pullup bias was the sole mechanism for Modified Rev 0 jitter: refuted by Phase 29 v2 results (revert of `437339b6` still shows 1.31% jitter on Modified Rev 0).

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The `delayMicroseconds(3)` in `memory_get_data()` (after `rurp_chip_enable()`) is the read-strobe width, not a pre-/CE settling delay | Code Examples | If the addressing and chip-enable are slower than assumed, the 3µs may already be sufficient settling and the knob location needs to be between `set_address` and chip-enable only | [ASSUMED — inspected code directly but no oscilloscope trace to confirm current wiring behavior on Modified Rev 0] |
| A2 | The 8-channel LA has sufficient time resolution to show A15 settling relative to /CE at 16 MHz / 62.5 ns clock | Architecture Patterns §LA Trigger | If LA sample rate is < 20 MHz, A15 settling glitches shorter than 50 ns will be missed; the sweep would still work causally even if the LA misses the glitch | [ASSUMED — operator's LA spec not confirmed in research materials] |
| A3 | The Modified Rev 0 modifications are visible / measurable with a multimeter (missing series termination, pull-down values) | Pitfalls §Pitfall 1 | If the mods are not electrically distinguishable by multimeter (e.g. no R41-equivalent path), the static check may not surface the specific mechanism | [ASSUMED — the v1.7 SHIELD-REVS.md §4 row "Modified Rev 0" is all TBD/pending Phase 35; no confirmed mod inventory available] |
| A4 | `delayMicroseconds()` calls in the firmware translate to µs-accurate delays at 16 MHz for values ≥ 3µs | Pitfalls §Pitfall 5 | If the MCU runs at a different clock or if interrupts fire, sweep data points may not reflect true delay values | [ASSUMED — established Arduino AVR behavior, but not verified against actual board clock config] |

**If this table is empty:** All claims in this research were verified or cited — no user confirmation needed.

---

## Open Questions (RESOLVED)

1. **Are the Modified Rev 0 hardware modifications documented anywhere beyond the v1.7 TBD stubs?**
   - **RESOLVED:** Documentation gap is the point — 44-04 Task 1 static inspection (D-01) physically traces and documents the mods (filling `.planning/v1.7/MODIFICATIONS.md`). Planning proceeds knowing the mods exist and will be characterized on the bench; no further documentation is a prerequisite to plan.
   - What we know: v1.7-SHIELD-REVS.md §4 row "Rev 0 → Modified Rev 0" is entirely "TBD pending Phase 35" — the operator's rework trace (cuts + jumpers) was never photographed or documented. Phase 35 follow-up #3 + #4 are recorded as outstanding actions.
   - What's unclear: What specifically was modified? Which lines were cut or jumpered? Does the rework affect the address bus (A15 path) or only the voltage divider / R41 detect circuit?
   - Recommendation: The static check (D-01) must be performed by the operator with the board in hand. The Phase 44 plan should include a task where the operator photographs the board's rework regions and documents what they see against the upstream Rev 0 schematic (`UniversalProgrammerRev0b0.zip`, blob `d2a7f691`). The MODIFICATIONS.md stub at `.planning/v1.7/MODIFICATIONS.md` should be filled out. This is the prerequisite for a meaningful static-check hypothesis.

2. **Does the sweep need to parameterize the `_NOP()` count in `rurp_read_data_buffer()` as well?**
   - **RESOLVED:** Start with the two primary knobs (address-settling + /CE strobe per D-04). The `_NOP()`-count is an optional Phase 44 extension only if residual jitter persists at maximum settling.
   - What we know: The existing 2 × `_NOP()` at commit `4f205e58` (part of shipped v1.6 beta) address the between-PINx-read race. This is a Leonardo-specific fix on `beta`. The primary D-04 knobs are the address-settling delay and the /CE strobe width, both in `memory_get_data()`.
   - What's unclear: Whether a separate NOP-count knob (e.g., `"read-nop-count"`) adds meaningful data, or whether the settling delay in `memory_get_data()` is sufficient to capture the dominant mechanism.
   - Recommendation: Start with the two primary knobs (settling + strobe). Add the NOP-count knob as a Phase 44 optional extension if the first sweep shows residual jitter at maximum settling that correlates with the between-PINx race. This keeps the firmware change minimal for the first iteration.

3. **Git prerequisite: is the `firestarter_app` v1.9 branch also needed before Phase 44 firmware work?**
   - **RESOLVED:** Yes — 44-01 forks BOTH sub-repos (`firestarter` AND `firestarter_app`) off `beta` before any host-side change, so the host-side knob work in 44-03 lands on the v1.9 branch.
   - What we know: Phase 44 requires adding the read-timing knobs to `eprom_operations.py` and `constants.py` in `firestarter_app`. The firestarter_app is currently installed as editable from `/workspaces/firestarter_app` at commit `efd203a` (which is actually the firmware sub-repo point — the firestarter_app's current installed version is 3.0.0b5 from the editable install).
   - What's unclear: Whether the firestarter_app submodule is on a v1.8-app-cleanup branch or beta. The v1.8 shipped as `3.0.0b7` on beta; the editable install shows `3.0.0b5` which may be from an older install.
   - Recommendation: Before any host-side code changes, confirm `cd /workspaces/firestarter_app && git branch` shows the correct starting point (should be `beta` tip at `3.0.0b7` or the v1.9 branch). Cut `v1.9-read-bug-rca` off `beta` before any commits.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO CLI | Firmware build + native tests | ✓ | 6.1.19 | — |
| Python 3 | Host CLI + sweep harness | ✓ | 3.12.13 | — |
| firestarter host CLI | Baseline repro, sweep | ✓ | 3.0.0b5 (editable) | — |
| Serial ports (/dev/ttyACM1) | Bench reads | ✗ (not visible, hardware not connected) | — | Hardware must be connected by operator at bench session start |
| Arduino Leonardo + Modified Rev 0 shield | Baseline repro + sweep | ✗ (not connected) | — | Operator bench session required |
| 8-channel LA | A15/CE corroborating capture | ✗ (operator-owned) | — | Operator provides; D-09 confirms operator-only physical probing |
| Low-bw scope | Analog ringing observation | ✗ (operator-owned) | — | Operator provides; corroborating only (D-06/D-08) |
| Multimeter | Static check (D-01) | ✗ (operator-owned) | — | Operator provides |

**Missing dependencies with no fallback:** Serial ports + hardware require operator bench session. All bench tasks are operator-gated (D-09).

**Missing dependencies with fallback:** None — scope and LA are corroborating, not gating (D-06).

---

## Validation Architecture

> `workflow.nyquist_validation` is absent from `.planning/config.json` — treated as enabled.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Unity (PlatformIO native) + pytest (host) |
| Config file | `firestarter/platformio.ini` ([env:native]) + `firestarter_app/pyproject.toml` |
| Quick run (firmware native) | `pio test -e native -f "*test_data_input*"` |
| Full native suite | `pio test -e native` |
| Host quick run | `pytest tests/ -x -q` |
| Host full suite | `pytest tests/ --cov-fail-under=70` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RCA-01 (causal proof) | `read_settling_us` + `read_strobe_us` parsed from JSON and stored in handle | unit (native) | `pio test -e native -f "*test_read_timing*"` | ❌ Wave 0 — new test file needed |
| RCA-01 (sweep mechanics) | `consistency_check_eprom` accepts `read_settling_us` / `read_strobe_us` params | unit (pytest) | `pytest tests/test_eprom_operations.py -x -q -k "read_timing"` | ❌ Wave 0 — new test cases needed |
| D-11 baseline repro | Byte-compare of new N=5 run against Phase 29 v2 binaries passes (jitter present) | manual / bench | Operator-run + 5-line Python cross-check script | ✓ (script pattern established in EVIDENCE.md) |
| D-04 sweep validity | Firmware applies `read_settling_us` delay at correct call site in `memory_get_data()` | unit (native) | `pio test -e native -f "*test_read_timing*"` | ❌ Wave 0 |
| D-05 no-reflash constraint | Host sends knob params per-read in JSON command without triggering sideload | integration / manual | Operator verifies during sweep session | manual-only |

### Sampling Rate

- **Per task commit:** `pio test -e native` (for firmware changes) or `pytest tests/ -x -q` (for host changes)
- **Per wave merge:** Both suites green + `pio run -e leonardo` succeeds (flash budget check)
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp` — Unity tests verifying `read_settling_us` and `read_strobe_us` are parsed from JSON and stored in the handle; pattern: include `json_parser.c` as source, call `json_parse()` with a JSON string containing the new keys, assert `handle.read_settling_us == expected`.
- [ ] `firestarter/test/native/avr/test_read_timing/host_stubs.cpp` — stubs for `rurp_*` symbols (same pattern as `test/native/avr/test_data_input/host_stubs.cpp`).
- [ ] `tests/test_eprom_operations.py` — pytest cases for new `read_settling_us` / `read_strobe_us` params in `consistency_check_eprom()` signature and JSON command emission.

*(The existing `test/native/avr/test_data_input/` suite provides the copy-paste template for the new native test.)*

---

## Security Domain

> `security_enforcement` is absent from config — treated as enabled. However, this phase involves no user-facing authentication, session management, data persistence, or external network calls. The two new JSON fields (`read-settling-delay`, `read-strobe-us`) are integer values parsed from a locally-trusted serial stream (operator bench hardware). ASVS categories V2/V3/V4/V6 do not apply.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | N/A — local serial communication |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | Yes (minimal) | Integer bounds check on new JSON fields; `delayMicroseconds()` saturates at `uint32_t` max; no buffer overflow path in `extract_long()` macro |
| V6 Cryptography | No | N/A |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Integer overflow in `read_settling_us` → very long delay (hangs firmware) | Tampering | Cap at reasonable max (e.g., 1000µs) in firmware parser or at chip-enable; document the cap |
| Malformed JSON with `"read-settling-delay": "abc"` | Tampering | Existing `extract_long()` / `simple_strtoul()` silently produces 0 on non-numeric input (existing behavior — acceptable for dev-only tool) |

---

## Sources

### Primary (HIGH confidence)
- Direct codebase inspection: `/workspaces/firestarter/src/proms/memory.cpp` — `memory_get_data()`, `memory_read_execute()`, `mem_util_set_address()`
- Direct codebase inspection: `/workspaces/firestarter/src/boards/leonardo_rurp_shield.cpp` — `rurp_read_data_buffer()`, `rurp_set_data_input()`
- Direct codebase inspection: `/workspaces/firestarter/src/json_parser.c` — parser pattern, PROGMEM key registration
- Direct codebase inspection: `/workspaces/firestarter/include/firestarter.h` — `firestarter_handle_t` struct
- Direct codebase inspection: `/workspaces/firestarter_app/firestarter/constants.py` — sync rule constants
- Direct codebase inspection: `/workspaces/firestarter_app/firestarter/eprom_operations.py` — `consistency_check_eprom()`, `_operation_context()`
- Direct codebase inspection: `/workspaces/firestarter_app/firestarter/cli_handlers.py` — `dev_consistency_check` Click command
- `.planning/milestones/v1.6-phases/29-multi-board-bench-verification/29-04-SUMMARY.md` — Bug A characterization, Phase 29 v2 bench evidence, 15-binary registry
- `.planning/v1.6-EVIDENCE.md` (Phase 29 v2 H3 block, read lines 1-255) — WORST ratio, A15 jitter correlation, 63% bit-raise
- `.planning/phases/44-bug-a-rca-modified-rev-0-upper-address-jitter/44-CONTEXT.md` — locked decisions D-01..D-11
- `git show v1.7-shield-investigation:.planning/v1.7-SHIELD-REVS.md` — §3 ADC detect, §8 band-math, §9 per-rev ADC table, Modified Rev 0 mid-band empirical result
- `git log` on `/workspaces/firestarter` and meta-repo — branch topology, commit SHAs

### Secondary (MEDIUM confidence)
- `/workspaces/firestarter/CLAUDE.md` — constants sync rule, chip-out-before-sideload, buffer size note
- `/workspaces/firestarter_app/CLAUDE.md` — serial protocol wire format, constants sync rule
- `/workspaces/CLAUDE.md` — repo structure, sub-repo layout

### Tertiary (LOW confidence)
- None. All claims were verified by direct codebase inspection or from the project's own planning artifacts.

---

## Metadata

**Confidence breakdown:**
- Standard stack / tooling: HIGH — directly verified via `pio --version`, `firestarter --version`, `pip show`
- Architecture and code patterns: HIGH — read actual source files, not training knowledge
- Bug A characterization (empirical substrate): HIGH — read Phase 29 v2 SUMMARY + EVIDENCE.md directly
- Modified Rev 0 modifications detail: LOW — v1.7 §4 row is all TBD; the static check (D-01) is the mechanism for resolving this at bench time
- LA sample rate and scope bandwidth specifics: LOW — instrument specs not recorded in planning artifacts; operator-known

**Research date:** 2026-05-29
**Valid until:** Stable — firmware architecture changes slowly; re-verify if `memory.cpp` or `json_parser.c` changes substantially before planning is complete.

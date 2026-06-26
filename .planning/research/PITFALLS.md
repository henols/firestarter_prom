# Pitfalls Research

**Domain:** Internal refactor of a silicon-driving protocol layer (Arduino C++ firmware + Python host) — renaming minipro hex-ID protocol buckets, extracting shared firmware primitives, and standing up a per-protocol bench-verification ledger.
**Researched:** 2026-06-25
**Confidence:** HIGH (grounded in the actual fix history in `.planning/STATE.md`, the live gate scripts `tools/check_dispatch.py` + `tools/diff_db.py`, the lockstep surface `constants.py` ↔ `include/firestarter.h`, the firmware handler source `src/proms/eprom.cpp` + `flash_utils.cpp`, and the v1.13/v1.15 verification artifacts).

> **Danger profile (read first).** This is not an ordinary refactor. A regression here can *physically destroy silicon* (wrong VPP rail / wrong algorithm on an irreplaceable UV-EPROM), and the only trustworthy read/write oracle is **Leonardo + RURP Rev 2.0** (the v1.9 read bug corrupts reads on every other board/shield). The firmware sits at **~89.5% flash against a ~90% gate** — a refactor that *adds* flash can wedge the build before the reuse savings land. Every pitfall below is keyed to a real one-off fix that must survive the recompose.

---

## Critical Pitfalls

### Pitfall 1: Re-tangling the algorithm axis (`protocol_id`) with the UV-vs-EEPROM electrical axis during primitive extraction

**What goes wrong:**
A "VPP primitive" gets factored to switch on `electrical.type` (`UV-EPROM` / `EEPROM` / `Flash/EEPROM` / `FRAM`) instead of on `handle->protocol`. The two axes are orthogonal: `protocol_id` is the *algorithm* (how to write/erase/gate VPP); `electrical.type` is a *display/classification + erase-capability* field. They were tangled repeatedly in v1.11 (infoic decode), v1.12 (dispatch hardening), and the v1.15 DECODE-AUDIT, and untangling them is half the point of v1.16. A primitive that keys VPP on the electrical axis re-introduces exactly the bug class the project keeps paying down — e.g. an `EEPROM`-typed `0x07` chip (W27C512) legitimately needs 12–13V VPP on a real vpp-pin, while a same-typed `0x07` chip on `DIP28_2764` (an AT28C 5V part) was deliberately flipped to `0x0D` so it routes to `configure_eeprom28c` and never asserts VPP.

**Why it happens:**
The electrical type "feels" more human-readable than a hex ID, so a naming/refactor pass naturally reaches for it. But `electrical.type` is a *derived* field (`build_db.py` Pass-2 recomputes it from algorithm/pinout — see `diff_db.py` `_RULE_FIELD_PATHS` comment), and `FLAG_CAN_ERASE` is *already* derived from `electrical.type == "EEPROM" | "Flash/EEPROM"` (Phase 77). Layering VPP routing onto the same axis double-couples it.

**How to avoid:**
- Keep **dispatch and VPP gating keyed on `handle->protocol`** exactly as `memory.cpp::configure_memory` and `check_dispatch.py::dispatch()` do today (protocol prefix fires *before* the `mem_type` fallback). The extracted VPP primitive must take `handle->protocol` (or an explicit "VPP profile" enum derived once from protocol), never `electrical.type`.
- Preserve the documented one-to-one in `eprom.cpp`: `0x0B` → direct VPE rail (`CTRL_VPP_REGULATOR_ENABLE` only, no `CTRL_VPP_VPE_DROP_ENABLE`); `0x07`/`0x08` → regulator + dropping resistor (`CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE`). A primitive that collapses these two is a silicon hazard.
- Document the two axes explicitly in the naming pass so the refactor can't conflate them.

**Warning signs:**
- A new primitive signature takes `electrical.type` / a type-string as input.
- `diff_db.py` reports a chip whose `electrical.type` changed with **no** co-occurring `algorithm`/`pinout` change (the script treats this as unexplained — it's the tangle leaking into data).
- `check_dispatch.py` `novpp_in_eprom` or `eeprom28c_in_eprom` buckets become non-empty.

**Phase to address:**
Naming + documentation pass (own the axis vocabulary). Enforced through every recompose phase by the unchanged `check_dispatch.py` gate.

---

### Pitfall 2: Silently dropping one of the accreted per-protocol one-off fixes during recompose

**What goes wrong:**
The handlers carry a string of correct-but-undocumented point fixes. Recomposing from primitives drops one because its *why* lived in a commit message / STATE decision, not the code. The known load-bearing fixes that MUST survive byte-for-byte behavior:

| Fix | Where | What it does | Drop = |
|-----|-------|-------------|--------|
| `0x0B` direct-VPE rail | `eprom.cpp:145,218` | `0x0B` (EPROM_LEGACY, NMOS ~25V) uses regulator-only (no dropping resistor); 0x07/0x08 use the dropping path | wrong VPP on NMOS UV parts |
| `0x0B` shared OE/VPP pin read | `eprom.cpp` read path + VPP-skip | the 2516's read VPP must be skipped on `CMD_READ`/`CMD_BLANK_CHECK` (fw `cb947c7`) | re-introduces the 18.8V boot-refusal |
| `0x08` large-EPROM P1-as-VPP | `eprom.cpp` 0x08 branch | 32-pin DIP large-EPROM VPP routing (still buggy → FUT-06, but must not silently change) | regress an already-fragile path |
| flash4 256B page boundary | `flash_type_4.cpp` | per-page write/poll at the 256B page boundary (Phase 74 SDP fix) | flash4 page-0 timeout |
| VPP-skip on reads | `eprom.cpp` / dispatch | reads/blank-checks assert no programming VPP | non-destructive reads become destructive |
| pulse-delay defaults | `eprom.cpp:71-74` | 0x08=100µs, 0x0B=500µs, default(0x07)=1000µs when host sends 0 | wrong write timing |
| FM1608 SRAM→FRAM relabel | `build_db.py` codegen + display | label-only; `FRAM ∉ {EEPROM,Flash/EEPROM}` so `FLAG_CAN_ERASE` stays off | spurious erase attempt on FRAM |
| WARNING-5 `0x07`→`0x0D` override | `build_db.py` `_PROTOCOL_OVERRIDES` | DIP28_2764 5V-EEPROMs flip to `0x0D` (12V would hit A14) | 12V on A14 hazard |
| `SST39SF040` KEEP Flash/EEPROM (D-40) | `build_db.py` | NOT relabeled to "Flash" — relabel would flip `FLAG_CAN_ERASE` off and break Phase-77/82 auto-erase | break proven auto-erase |

**Why it happens:**
No documented per-protocol model exists yet (that's the v1.16 deliverable). The fixes are spread across firmware C++, `build_db.py` Python, and the DB data, and several look like incidental branches rather than deliberate corrections.

**How to avoid:**
- Make the **naming + documentation pass produce a per-protocol "behavior contract"** (the protocol_id → name → datasheet-verified behavior map from `questions.md` Q4) that *explicitly enumerates each one-off fix as a named invariant* before any code moves. The recompose then has a checklist.
- Sequence per the seed: **document first (structure stable, near-zero flash delta), recompose second** — never recompose a family before its behavior contract is written.
- For each family, write/confirm a **Tier-1 native register-level test** (recording-bus stub, `pio test -e native`) that asserts the exact control-register sequence (`CTRL_VPP_REGULATOR_ENABLE` with/without `CTRL_VPP_VPE_DROP_ENABLE`, pulse width, VPP-skip on read) *before* extracting the primitive, so the recompose is a refactor-under-test.

**Warning signs:**
- A native suite assertion (`vpp_regulator_enabled_on_write`, `vpp_regulator_disabled_on_read`, etc. from `validation_matrix_spec.json`) flips.
- A family's flash *drops more than the shared-code estimate* (a fix's bytes vanished, not just duplication).
- The behavior-contract checklist for a family has an unchecked invariant after recompose.

**Phase to address:**
Naming + documentation pass (enumerate the invariants); each per-family recompose phase (assert them under native test). Bench validation phase confirms on silicon.

---

### Pitfall 3: A "cleanup" that *adds* Leonardo flash and wedges the ~90% gate

**What goes wrong:**
The driver for v1.16 is *shrinking* the ~89.5% Leonardo flash via shared primitives. But the intermediate steps can *grow* flash: a generic primitive with a runtime dispatch table, function-pointer indirection, or a `switch` over all protocols can compile *larger* than the inlined per-handler code it replaces (AVR-GCC inlines small static handlers aggressively). A naming/doc pass that adds PROGMEM strings (handler-name strings, log messages) also costs flash. If a recompose step pushes past ~90% before the savings from a *later* family land, the build fails and the milestone stalls mid-refactor.

**Why it happens:**
Refactoring intuition from desktop ("abstraction is free") doesn't hold on a 28–32KB AVR with the build already at 89.5%. The savings are non-monotonic across families: extracting the first primitive may cost (the primitive + one call site) before the 2nd/3rd call sites pay it back.

**How to avoid:**
- **Measure flash per step.** Run `pio run -e leonardo` after every recompose and record the flash % delta in the family's recompose plan (this is `questions.md` Q3 — per-handler flash breakdown — operationalized). Treat any net increase as a STOP-and-explain.
- **Add a CI/plan flash-ceiling gate** (`pio run -e leonardo` parse + assert ≤ ~90%, mirroring the v1.14 Phase-78 `≤~90% flash` gate that already exists as precedent). Wire it as a per-phase exit gate.
- **Order families by reuse payback**, not alphabetically: extract the primitive with the most call sites first so the curve trends down. `flash_utils.cpp` (chip-id, DQ7 poll) is already a shared primitive — use it as the template and as the proof the pattern shrinks flash.
- Keep handler-name/doc strings **out of firmware flash** — put the protocol vocabulary in host-side docs / the ledger, not PROGMEM.

**Warning signs:**
- `pio run -e leonardo` flash % ticks *up* after a recompose.
- AVR map file shows the generic primitive + thunks larger than the removed handlers.
- The naming pass introduces new PROGMEM string literals.

**Phase to address:**
Primitive decomposition / recompose phases (per-step flash measurement + ceiling gate). Naming pass must prove near-zero flash delta (its stated success criterion).

---

### Pitfall 4: Dual-repo lockstep drift — `constants.py` ↔ `firestarter.h` (and the CTRL_*/REVISION_* mirrors)

**What goes wrong:**
The refactor renames a flag, command code, control-register bit, or response code on one side of the wire and forgets the other. The host `constants.py` and firmware `include/firestarter.h` independently `#define`/assign the *same* values (`FLAG_CAN_ERASE=0x02`, `CMD_*`, `RESPONSE_CODE_*`); `constants.py` *also* mirrors `rurp_pinout.h` (`CTRL_VPP_REGULATOR_ENABLE=0x080`, `CTRL_VPP_VPE_DROP_ENABLE=0x100`, `CTRL_VPP_P1_ENABLE=0x008`, …) and `rurp_shield.h` (`REVISION_*`). A protocol-vocabulary rename is *especially* tempting to apply asymmetrically because "it's just a name." If only one repo changes, the wire desyncs silently (no compile error — the integers still match by accident, or a handler reads the wrong bit).

**Why it happens:**
The two repos are separate git submodules with separate CI; nothing structurally forces the edit to be atomic. A rename touching `CTRL_*` names but not their hex values reads as cosmetic but is part of the parity contract per both CLAUDE.md files.

**How to avoid:**
- Treat **any wire-touching change as a dual-repo lockstep commit pair** (standing policy, restated in the v1.16 seed). The protocol naming pass is *intended* to be near-wire-neutral — keep the actual integers on the wire (`algorithm`/`protocol` values) unchanged; rename only in code/docs/ledger, not the wire field values.
- Keep the **constants-parity test green** (`8/8` parity per v1.14 close). If the refactor renames a constant, rename it in *both* `constants.py` and the matching firmware header in the same change, and update the parity test.
- The `CTRL_*` block in `constants.py` is *documentary only* (Python never writes the register) — but it is still part of the parity contract. Do not let a firmware `rurp_pinout.h` bit-value change (e.g. a new control bit for a primitive) land without mirroring it.

**Warning signs:**
- Constants-parity test fails, or worse, *passes* because only names (not values) drifted.
- A bench read/write that worked pre-refactor returns garbage with no error (silent wire desync).
- `git log` shows a firmware-header commit with no paired host commit (or vice versa).

**Phase to address:**
Every wire-touching recompose phase (lockstep commit discipline + parity test as exit gate). Naming pass should explicitly assert "wire field values unchanged."

---

### Pitfall 5: The py3.12-masks-CI-3.11 ruff / codegen-drift trap

**What goes wrong:**
The devcontainer runs Python 3.12 but `firestarter_app` CI gates on py3.9/3.11. Code that is ruff-clean and ruff-format-stable under 3.12 can fail the CI's `ruff check` + `ruff format --check` on the target version, and **codegen output drift** (`tools/catalog/codegen.py` → `messages.py`) can contradict the ruff baseline. A refactor that regenerates `messages.py` or touches the gated modules looks green locally and red in CI.

**Why it happens:**
Different interpreter + different ruff resolution; the codegen emitter and the ruff formatter historically disagreed (fixed at the emitter in v1.12 Phase 63 — `codegen.py` now emits ruff-clean, format-stable output; do **not** hand-normalize it). f-string backslashes and non-ruff-clean codegen are the recurring traps.

**How to avoid:**
- Before claiming CI green, run `ruff check firestarter/ tests/` + `ruff format --check` **scoped exactly as `ci.yml` gates** (the CI gates `firestarter/ tests/`, not the whole tree — broad `ruff check .` findings under `tools/` are out-of-CI-scope and must not be "fixed" into noise, but also must not mask real failures).
- If `messages.py` is regenerated, **let `codegen.py` emit it; never hand-edit/normalize** the output (v1.12 lesson). Keep the codegen drift gate green.
- mypy is strict on 8 named modules — but the hardened gate *prints OK even when mypy is MISSING*; verify mypy actually ran, don't trust the OK line.
- Validate against the CI target interpreter, not the 3.12 devcontainer default.

**Warning signs:**
- Local `ruff`/`pytest` green but CI red on formatting/lint.
- A `messages.py` diff appears in a refactor that "didn't touch messages."
- mypy "OK" with no error count printed.

**Phase to address:**
Any phase touching host modules / codegen (CI-parity preflight as a success criterion). Recurs in every recompose that changes host code.

---

### Pitfall 6: Breaking the `check_dispatch.py` / `diff_db.py` safety+diff gates (or hollowing them)

**What goes wrong:**
The refactor changes how a chip's handler is resolved, or regenerates the DB, and the two gates either (a) start failing for the wrong reason, or (b) get "fixed" by loosening the assertion until they're hollow. Both gates are load-bearing safety:
- `check_dispatch.py` is the **full-class VPP-safety guard**: `novpp_in_eprom` (structural — no chip routes to `configure_eprom` on a pinout with no vpp-pin), `eeprom28c_in_eprom` (WARNING-5 12V-on-A14), `sram_in_eprom` (BLOCKER-2), per-family VPP invariants, and the `non_supported_dispatchable` inverse guard. Its `dispatch()` function is a **hand-maintained mirror of `memory.cpp::configure_memory`** dispatch order.
- `diff_db.py` is the **per-chip diff vs `chip_database.baseline.json`**: every changed chip must be explained by a cited root-cause rule; any unexplained diff or missing chip = exit 1.

If the refactor renames protocols or restructures dispatch, `check_dispatch.py::dispatch()` and the firmware `configure_memory` order **silently diverge** — the gate then validates a fiction. v1.12 already shipped a *hollow* `non_supported_dispatchable` detector as accepted debt (host guard authoritative); re-hollowing more of the gate erodes the safety net further.

**Why it happens:**
`check_dispatch.py::dispatch()` is a *copy* of the firmware dispatch order, not a derivation from it. Nothing forces them to stay in sync; a firmware dispatch refactor won't fail any test unless someone also edits the Python mirror. The DB baseline is pinned — a legitimate refactor that re-derives the DB will produce diffs that need *new cited rules*, and the temptation is to re-pin the baseline instead of explaining the diff.

**How to avoid:**
- When the recompose changes firmware dispatch order, update `check_dispatch.py::dispatch()` **in the same change** and keep the documented mirror in `firestarter/CLAUDE.md` (the line-for-line dispatch table) authoritative. Add a test that the mirror matches the documented order.
- If the refactor is *behavior-preserving* (the v1.16 intent), the DB should **not** change — `diff_db.py` should report **zero diffs**. A clean recompose is the easiest `diff_db.py` PASS. Treat any DB diff from a "pure refactor" as a red flag, not something to explain away with a new rule.
- Do **not re-pin `chip_database.baseline.json`** to silence a diff during a behavior-preserving refactor. Re-pinning is only legitimate when the DB *intentionally* changes (and then with a cited rule + operator authorization, per the GATE-01 precedent).
- Preserve the structural, type-string-*independent* `novpp_in_eprom` guard — it auto-covers any future `electrical.type` label, which is exactly the safety property the axis-untangling (Pitfall 1) needs.

**Warning signs:**
- `check_dispatch.py` PASS while the firmware dispatch order has changed (mirror drift — the dangerous silent case).
- `diff_db.py` exit 1 with "unexplained diff" on a refactor that claimed to be behavior-preserving.
- A PR loosens a gate assertion or re-pins the baseline without an operator-authorized cited rule.

**Phase to address:**
Every recompose phase (gates as mandatory exit criteria — both must exit 0). A dedicated early plan to add the dispatch-mirror-matches-doc test before any dispatch restructuring.

---

### Pitfall 7: Trusting a non-Leonardo / non-Rev-2.0 bench read as the verification oracle

**What goes wrong:**
A recomposed family is "verified" using a read on a Uno/uno328pb or a different shield rev. The v1.9 read bug corrupts reads on Rev-0/Rev-2.0-elsewhere and uno328pb is N/A for program/write — so the SHA "match" or "mismatch" is meaningless, producing either a false PASS (ships a silicon-destroying regression) or a false FAIL (wastes an irreplaceable UV chip chasing a phantom).

**Why it happens:**
Port numbers shuffle across USB replug; "a board is connected" is not "the trustworthy board on the trustworthy shield." The bench has multiple boards and the operator owns multiple shield revs (Rev 2.2 / 2.0 / modified Rev 0) that the EEPROM `hw_revision` byte *cannot distinguish*.

**How to avoid:**
- **Leonardo + RURP Rev 2.0 is the ONLY authoritative combo** for any program/write/verify ledger row. Anything else is recorded `UNVERIFIED`, never PASS.
- Every bench task re-checks the SAFE-01 discipline already codified in v1.15: `controller:` port identity per task, live `r1 ≈ 270000`/`r2 ≈ 44000` readback, operator-stated silkscreen shield rev (ASK — the EEPROM byte can't tell Rev 2.0/2.1/2.2 apart), host suite + `test_init_phase_data_frames_not_acked` 0xA4 guard green before the session.
- Reuse `dev consistency-check` (N≥3 reads, distinct-SHA count) as the read oracle and a wrong-file `verify` as the negative control — both already proven non-vacuous in v1.13/v1.15.

**Warning signs:**
- A ledger row says PASS with board ≠ leonardo or shield ≠ Rev 2.0.
- `controller:`/port identity not recorded for a bench row.
- N=1 read used as proof (must be N≥3 with distinct-SHA = 1).

**Phase to address:**
Per-protocol bench validation phase (SAFE-discipline preconditions on every row). The ledger schema (below) makes board/shield/oracle mandatory columns so a non-authoritative PASS is structurally impossible.

---

### Pitfall 8: Bypassing the host VPP guard or writing an irreplaceable UV part on an unstable read path

**What goes wrong:**
A recompose or a "convenience" test path writes a chip whose protocol the host guard would refuse, or spends an irreplaceable UV-EPROM (operator has no eraser) before its read path is proven stable. The 2516 (0x0B, shared OE/VPP) read is *still unstable* after the VPP-skip fix (3 distinct SHAs, 1.9% jitter, N=3) — writing/dumping it on that untrusted oracle would consume it for a vacuous result.

**Why it happens:**
The host guard (`chip_resolver.resolve_chip` → `ChipNotImplementedError`, refuses any `support_status != "supported"` before any serial byte) is the *authoritative* safety layer (the firmware `check_dispatch` GATE-03 inverse detector is hollow by accepted debt). A refactor that reroutes resolution could bypass it. And the "just write a few bytes to test" instinct ignores that UV writes are irreversible.

**How to avoid:**
- **Never route around `chip_resolver.resolve_chip`.** Any new resolution path must still call the host guard before emitting wire bytes. Keep the guard the single chokepoint.
- **No UV-part write before a blank-check + stable read + explicit per-chip spend decision** (the v1.15 SAFE-02/03 + D-21 discipline). If the read path is unstable (2516), the chip stays `UNVERIFIED` — record it, don't spend it.
- Over-voltage stays blocked at the firmware VPP check (`eprom_check_vpp`); under-voltage is warn-and-proceed (best-effort, operator opt-in per D-07). The refactor must not relax the over-voltage block.
- Guard-removal (flipping `support_status`→`supported` / dropping a host refusal) is always the **last** step of a graduation, after bench proof (SAFE-01/02/03 "guard-removal-last" discipline from v1.14 Phase 77).

**Warning signs:**
- A code path builds a wire dict / emits serial without going through `resolve_chip`.
- A bench plan writes a UV chip whose Phase-equivalent read sweep showed instability.
- The firmware over-voltage block is loosened "to let a chip through."

**Phase to address:**
Bench validation phase (spend-vs-preserve discipline, host-guard chokepoint preserved). Recompose phases must not alter the resolution chokepoint without re-proving the guard fires.

---

## The Verification Ledger (PRIMARY deliverable)

### Goal

A **per-protocol** bench-verification ledger that says, for each protocol bucket, whether it is silicon-proven on Leonardo+Rev2.0, `UNVERIFIED` (no chip on hand), or chip-needed — and that **composes with** (does not replace) the two existing layers:

1. **v1.13 per-family validation matrix** — `tools/validation_matrix_spec.json` (declarative spec: family → handler → protocols → rep_chip → tier1/2/3) + per-family `val-results/<family>/validation-matrix.{json,md}` (per-cell Tier-3 verdicts).
2. **v1.15 per-chip EVIDENCE** — `.planning/v1.15/bench/EVIDENCE.{md,json}` (per-chip write→read→verify cells with `sha256`, `blank_state`, `verdict`, `anomalies`, SAFE-01 metadata).

### Where it lives

`.planning/v1.16/ledger/PROTOCOL-LEDGER.{md,json}` — a **new artifact** (one per milestone, like v1.15's EVIDENCE), NOT an edit to the v1.13 spec or the v1.15 evidence. The markdown is the human view; the JSON is the machine-checkable source (mirrors the EVIDENCE.{md,json} dual-format convention). It **references** the other two layers by key rather than copying their data.

### Composition model (the key design constraint from `questions.md` Q5)

```
PROTOCOL-LEDGER.json  (v1.16 — NEW; the "did this protocol survive the rebuild" layer)
   │  one row per protocol_id bucket
   │  ├─ family_id          ──► joins to validation_matrix_spec.json families[].id  (v1.13)
   │  └─ evidence_refs[]    ──► joins to EVIDENCE.json cells[].chip + sha256        (v1.15)
   │
   ├── v1.13 matrix answers: "does the family's handler pass tier1/2/3?"  (algorithm-family granularity)
   └── v1.15 EVIDENCE answers: "did THIS physical chip write→read→verify clean?" (per-chip silicon granularity)
```

The ledger adds the **protocol-rebuild dimension** the other two lack: for each protocol it records (a) the human name + datasheet citation produced by the naming pass, (b) the shared primitives the recomposed handler is built from, (c) the flash delta vs the pre-refactor handler, and (d) the bench verification status — **linking** to the family matrix cell and the EVIDENCE chip cells that substantiate it rather than re-deriving them.

### Proposed schema (`PROTOCOL-LEDGER.json`)

```json
{
  "schema_version": 1,
  "milestone": "v1.16",
  "generated": "<ISO8601>",
  "board": "leonardo",
  "shield": "Rev 2.0",
  "composes_with": {
    "family_matrix": "firestarter_app/tools/validation_matrix_spec.json",
    "per_chip_evidence": ".planning/v1.15/bench/EVIDENCE.json"
  },
  "protocols": [
    {
      "protocol_id": "0x07",
      "name": "EPROM_STD",                         // naming-pass vocabulary
      "datasheet_ref": "datasheets/W27C512.pdf#programming",
      "handler": "configure_eprom",
      "family_id": "eprom",                         // → v1.13 matrix families[].id
      "behavior_contract": {                        // the enumerated one-off invariants (Pitfall 2)
        "vpp_rail": "regulator + VPE_DROP (dropping resistor)",
        "pulse_default_us": 1000,
        "vpp_skip_on_read": true,
        "notes": "0x07 distinct from 0x0B direct-VPE rail; survives recompose"
      },
      "primitives": ["addr_setup", "data_strobe", "vpp_gate", "dq7_poll"],
      "flash_delta_bytes": -312,                    // measured pio run -e leonardo (Pitfall 3)
      "verification": {
        "status": "PASS",                           // PASS | UNVERIFIED | CHIP-NEEDED | FAIL
        "oracle": "leonardo+Rev2.0",
        "evidence_refs": [                           // → v1.15 EVIDENCE cells (chip + sha)
          {"chip": "W27C512", "sha256": "e16b2a5b…", "source": "v1.15 EVIDENCE.json"},
          {"chip": "SST27SF512", "sha256": "e16b2a5b…", "source": "v1.15 EVIDENCE.json"}
        ],
        "matrix_ref": {"family": "eprom", "tier": 3, "verdict": "PASS"},
        "negative_control": "wrong-file verify RC=1",
        "note": "Recomposed 0x07 path bench-confirmed; behavior_contract invariants asserted in test_val_eprom (native)."
      }
    },
    {
      "protocol_id": "0x10",
      "name": "FLASH_INTEL",
      "handler": "configure_flash_intel",
      "family_id": "flash_intel",
      "verification": {
        "status": "UNVERIFIED",                     // honest gap — no chip on hand
        "oracle": "leonardo+Rev2.0",
        "evidence_refs": [],
        "matrix_ref": {"family": "flash_intel", "tier": 1, "verdict": "PASS"},
        "note": "No Intel 28F chip on hand. Tier-1 native + Tier-2 wire pass; Tier-3 silicon UNVERIFIED. Datasheet AM28F010 sourced for primitive verification."
      }
    }
  ]
}
```

### Markdown view columns (`PROTOCOL-LEDGER.md`)

| protocol_id | name | handler | family_id | primitives | flash Δ | status | oracle | evidence (chip · sha) | matrix cell |
|-------------|------|---------|-----------|-----------|---------|--------|--------|----------------------|-------------|

- `status` taxonomy reuses the v1.15 verdict vocabulary so the three layers read consistently: `PASS` (silicon-proven on the authoritative oracle), `UNVERIFIED` (no chip on hand — explicit honest gap), `CHIP-NEEDED` (chip identified but not yet on hand), `FAIL` (bench-proven defect, links to a FUT/CR tracker), and may carry `ANOMALY` for flaky reads (2516-class).
- Rows whose `status=PASS` MUST carry a non-empty `evidence_refs` *and* `oracle: leonardo+Rev2.0` — structurally enforcing Pitfall 7 (no non-authoritative PASS).
- A small validator (reuse the `tools/audit_coverage_matrix.py` + `test_matrix_schema.py` pattern — no new dependency) asserts: every `family_id` exists in `validation_matrix_spec.json`; every `evidence_refs[].chip` exists in `EVIDENCE.json`; every PASS row's oracle is the authoritative combo.

### What the ledger explicitly does NOT do

- It does not duplicate per-chip SHAs (it references them).
- It does not re-run or replace the family matrix tiers.
- It does not become a new test harness (reuse `dev validate-family`, `dev consistency-check`, `write_test.sh`, `gen_test_image.py` — EVID-02 reuse-first).

---

## Incremental-Refactor Safety (keeping each recompose bench-honest + reversible)

| Discipline | How | Why (codebase-specific) |
|-----------|-----|--------------------------|
| **Document-before-recompose** | Naming pass writes each family's behavior contract (the one-off-fix invariants) before its handler is touched | The fixes' *why* is in commits/STATE, not code (Pitfall 2) |
| **Native register-level test first** | For each family, a `pio test -e native` Unity suite asserts the exact control-register sequence (VPP rail bits, pulse width, VPP-skip-on-read) using the recording-bus stub, *before* extracting the primitive | Makes recompose a refactor-under-test; catches silicon-hazard regressions with zero chips (the v1.13 Tier-1 pattern) |
| **One family per phase, behavior-preserving** | Recompose a single protocol family per phase; the DB must not change → `diff_db.py` exit 0 with zero diffs | A clean refactor produces no DB diff; any diff is a red flag (Pitfall 6) |
| **Flash measured per step** | `pio run -e leonardo` flash % recorded in the plan; net increase = STOP | The ~90% ceiling can wedge mid-refactor (Pitfall 3) |
| **Gates as exit criteria** | `check_dispatch.py` exit 0 + `diff_db.py` exit 0 + constants-parity + host suite + native suite green before the phase closes | The full-class VPP guard + per-chip diff are the safety net (Pitfall 6) |
| **Negative controls on every bench row** | wrong-file `verify` must exit non-zero; N≥3 `consistency-check` distinct-SHA = 1 | Proven non-vacuous oracle (v1.13/v1.15); guards false PASS |
| **Host VPP guard never bypassed** | All resolution stays through `chip_resolver.resolve_chip`; over-voltage block intact; guard-removal-last | Host guard is the authoritative safety layer (Pitfall 8) |
| **Reversibility** | Each family recompose is an isolated, behavior-preserving commit pair (host+fw) on the milestone branch; revert = drop the pair. No DB re-pin, so baseline stays the rollback anchor | A bad recompose reverts cleanly without touching the DB ground truth |

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hand-maintaining `check_dispatch.py::dispatch()` as a copy of firmware `configure_memory` | No build-system coupling between repos | Silent drift = the gate validates a fiction (Pitfall 6) | Acceptable now (precedent) IF paired with a dispatch-mirror-matches-doc test |
| Keeping the `non_supported_dispatchable` inverse detector partly hollow | Host guard is authoritative anyway | Erodes the firmware-side safety net; relies entirely on host | Accepted v1.12 debt; never *expand* the hollowness |
| Re-pinning `chip_database.baseline.json` to clear a `diff_db.py` diff | Gate goes green fast | Hides an unintended DB change from a "pure" refactor | **Never** during a behavior-preserving recompose; only with operator-authorized cited rule |
| Keying a VPP/erase primitive on `electrical.type` instead of `protocol` | Reads more human-friendly | Re-tangles the two axes (Pitfall 1) | **Never** |
| Hand-normalizing generated `messages.py` to pass ruff | Local green | Contradicts the codegen emitter; CI red (Pitfall 5) | **Never** (fix at `codegen.py`) |
| Skipping per-step flash measurement | Faster iteration | Build wedges past ~90% mid-refactor (Pitfall 3) | Never on Leonardo target |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Host ↔ firmware wire (`algorithm`/`protocol`) | Renaming the protocol vocabulary changes wire field *values* | Rename in code/docs/ledger only; keep wire integers identical (parity test green) |
| `constants.py` ↔ `firestarter.h`/`rurp_pinout.h`/`rurp_shield.h` | Edit one repo's constant, forget the mirror | Lockstep commit pair + constants-parity test (8/8) |
| `build_db.py` → `chip_database.json` → `diff_db.py` baseline | Regenerate DB during a refactor, get unexpected diffs | Behavior-preserving refactor → zero DB diff; don't re-pin |
| Devcontainer py3.12 → CI py3.9/3.11 | Trust local ruff/format/mypy green | Run CI-scoped `ruff check firestarter/ tests/` + `ruff format --check` on the target; verify mypy actually ran |
| `flash_utils.cpp` shared primitive (chip-id, DQ7 poll) | Re-implementing the same logic per family | Reuse it as the extraction template — it already proves the shrink pattern |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Generic primitive compiles larger than inlined handlers | `pio run -e leonardo` flash % rises after recompose | Measure per step; prefer static inlinable primitives over function-pointer tables | Leonardo build at ≥90% flash |
| PROGMEM doc/name strings in firmware | Flash creep during the naming pass | Keep protocol vocabulary host-side (docs/ledger), not firmware PROGMEM | When naming pass should be near-zero-flash |
| Uno (512B buffer) vs Leonardo (1024B) chunking assumptions | A primitive hardcodes a buffer size | Read `DATA_BUFFER_SIZE` / firmware-advertised `MSG_OK_READY` chunk (Phase 55), never hardcode | Cross-board after a buffer-coupled refactor |

## Security / Hardware-Safety Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| VPP primitive keyed on electrical type | 12V on a 5V pin / wrong rail → silicon damage | Key VPP gating on `handle->protocol`; preserve `novpp_in_eprom` + WARNING-5 guards |
| Bypassing `chip_resolver.resolve_chip` | A refused chip reaches the wire and asserts VPP | Single host-guard chokepoint; guard-removal-last |
| Relaxing the firmware over-voltage block | Over-VPP write destroys chip | Over-voltage stays blocked; only under-voltage is warn-and-proceed (D-07) |
| Writing an irreplaceable UV part on an unstable read oracle | Consumes the only chip for a vacuous result | Blank-check + stable N≥3 read + explicit spend decision first (2516 lesson) |
| Trusting a non-Leonardo/Rev-2.0 read | False PASS ships a silicon-destroying regression | Authoritative-oracle-only PASS rows in the ledger |

## "Looks Done But Isn't" Checklist

- [ ] **Recomposed family:** Often missing one of the enumerated one-off-fix invariants — verify the behavior contract checklist is fully checked + native suite asserts each register sequence.
- [ ] **Naming pass:** Often missing the *wire-values-unchanged* guarantee — verify `diff_db.py` exit 0 and constants-parity 8/8.
- [ ] **Flash shrink claim:** Often measured only at milestone end — verify per-step `pio run -e leonardo` deltas recorded and net ≤ pre-refactor.
- [ ] **`check_dispatch.py` PASS:** Often stale mirror — verify `dispatch()` matches the current `memory.cpp::configure_memory` order (dispatch-mirror test).
- [ ] **Ledger PASS row:** Often missing oracle/evidence linkage — verify `oracle: leonardo+Rev2.0` + non-empty `evidence_refs` pointing at real EVIDENCE.json cells.
- [ ] **CI green:** Often only local — verify CI-scoped ruff/format on the target interpreter and that mypy actually executed (not the MISSING-prints-OK trap).
- [ ] **UNVERIFIED rows:** Often silently omitted — verify every protocol bucket has a ledger row (honest gap, not absence).

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Dropped one-off fix in recompose | LOW (if caught by native test) / HIGH (if caught on silicon) | Revert the family's commit pair; restore the invariant from the behavior contract; re-assert in native suite before re-recomposing |
| Flash past ~90% mid-refactor | MEDIUM | Revert the offending recompose; reorder families by reuse payback; extract the highest-call-site primitive first |
| `check_dispatch.py` mirror drift | LOW | Re-sync `dispatch()` to the documented `memory.cpp` order; add the mirror-matches-doc test |
| Lockstep wire desync | MEDIUM (silent — may reach bench) | Diff `constants.py` vs `firestarter.h` values; restore the missing mirror; re-run parity test + a bench round-trip |
| Spent an irreplaceable UV chip on a bad oracle | HIGH (irreversible) | Cannot recover the chip; record as `UNVERIFIED`/`FAIL` with the lesson; tighten the spend-gate |
| Axis re-tangle shipped | HIGH | Revert; re-key the primitive on `protocol`; re-run `check_dispatch.py` full-class guard |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| 1. Axis re-tangle | Naming + documentation pass | `check_dispatch.py` `novpp_in_eprom`/`eeprom28c_in_eprom` empty; primitive signature takes `protocol` |
| 2. Dropped one-off fix | Naming pass (enumerate) + each recompose phase | Behavior-contract checklist + native suite assertions green |
| 3. Flash creep | Each recompose phase | Per-step `pio run -e leonardo` ≤ ~90%, net delta recorded |
| 4. Lockstep drift | Each wire-touching recompose phase | Constants-parity 8/8; lockstep commit pair; wire values unchanged |
| 5. py3.12/CI ruff-codegen trap | Any host/codegen-touching phase | CI-scoped ruff/format on target; codegen un-normalized; mypy ran |
| 6. Gate breakage/hollowing | Early dispatch-mirror plan + every recompose phase | `check_dispatch.py` + `diff_db.py` exit 0; dispatch-mirror test |
| 7. Non-authoritative oracle | Per-protocol bench validation phase | Ledger PASS rows carry `leonardo+Rev2.0` + evidence_refs |
| 8. Guard bypass / UV spend | Bench validation phase + recompose phases | Resolution stays through `resolve_chip`; over-voltage blocked; spend-after-stable-read |

## Sources

- `.planning/STATE.md` — Decisions/Accumulated Context: the actual one-off fix history (0x0B direct-VPE, 0x08 P1-as-VPP/FUT-06, flash4 256B page/CR-01, VPP-skip `cb947c7`, FM1608 SRAM→FRAM D-30, SST39SF040 D-40 keep, WARNING-5 0x07→0x0D, 25V ceiling D-07) — HIGH
- `firestarter_app/tools/check_dispatch.py` — full-class VPP-safety guard, `dispatch()` firmware mirror, family VPP invariants, hollow `non_supported_dispatchable` debt — HIGH
- `firestarter_app/tools/diff_db.py` — per-chip baseline diff, cited root-cause rules, derived-field coupling notes — HIGH
- `firestarter_app/firestarter/constants.py` + `firestarter/include/firestarter.h` + `include/rurp_pinout.h` + `include/rurp_shield.h` — the lockstep parity surface — HIGH
- `firestarter/src/proms/eprom.cpp` + `flash_utils.cpp` + `memory.cpp` — the actual VPP rail branching (0x0B vs 0x07/0x08), pulse defaults, and an already-extracted shared primitive — HIGH
- `firestarter_app/tools/validation_matrix_spec.json` + `val-results/<family>/validation-matrix.{json,md}` — the v1.13 family matrix the ledger composes with — HIGH
- `.planning/v1.15/bench/EVIDENCE.{md,json}` — the v1.15 per-chip evidence (columns, verdict taxonomy, SAFE-01 metadata) the ledger references — HIGH
- `firestarter/CLAUDE.md` + `firestarter_app/CLAUDE.md` — dispatch order documentation, constants-parity rule, py3.12/CI ruff-codegen trap, mypy-MISSING-prints-OK — HIGH
- `.planning/seeds/protocol-first-architecture-rebuild.md` + `.planning/notes/protocol-rebuild-rationale.md` + `.planning/research/questions.md` (Q5) — locked decisions, axis-confusion pain, ledger composition requirement — HIGH

---
*Pitfalls research for: Firestarter v1.16 protocol-first architecture rebuild (refactor-regression + verification-ledger design)*
*Researched: 2026-06-25*

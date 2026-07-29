# Requirements: Firestarter v1.22 — AT28C Software Data Protection Lifecycle

**Defined:** 2026-07-27
**Core Value:** Algorithm-first dispatch — the minipro `protocol_id` (`algorithm`) is the single authoritative dispatch key end to end. v1.22 completes the write-protection lifecycle on protocol `0x0D` without adding a second dispatch axis.

**Research:** `.planning/research/SUMMARY.md` (4 streams + adjudicated synthesis, 2026-07-27). Confidence HIGH on all in-tree code claims and AT28C datasheet semantics; MEDIUM on cross-manufacturer `tBLC`; silicon-state claims explicitly UNPROVABLE this milestone.

---

## Framing — this milestone opens with a FIX, not a feature

The promoting backlog note (999.19/999.18) asserted protocol `0x0D` "has no SDP path today." Reading the tree disproved that: a 6-write SDP-disable sequence has shipped since v1.0-era Phase 06-01 and is in `3.0.0b11`. Research then falsified the *second* framing too — that sequence is true of the **source** and almost certainly false of the **silicon**:

- `flash_util_byte_flipping` → `fu_flash_fast_address` (`flash_utils.cpp:61-66`) **bypasses `mem_util_remap_address_bus`** (`memory.cpp:259-282`), so no pin remap, no `rw_line` polarity, no `static_high_mask`.
- The four `0x0D` pinouts carry `rw` bus lines **11/14/14/20** (DIP pins 21/27/27/30) versus **22** for the `DIP32_SST39SF040` this shared helper was authored for. **At least one command write is emitted with `/WE` HIGH — a documented Write Inhibit — on all 84 `0x0D` chips.**
- The success check `eeprom28c_wait_for_write(handle, 0x5555, 0x20)` is **inverted, not weak**: both datasheets state the command-sequence data *"is not written to the device"* (DS20006432B §6.6.2 p.10; DS20006386B p.10), so it can only pass when the sequence was **not** recognised.

**Highest-value PREDICTED claim, assigned to Phase 116:** `firestarter write at28c256` currently aborts at INIT on `3.0.0b11` with an EEPROM timeout. If true, gh#11/gh#12 are **live defects, not stale 2024 reports**, and there is no working behaviour to preserve.

## Locked decisions (operator, 2026-07-27)

| Decision | Choice |
|---|---|
| Core scope | Full SDP lifecycle — lock, unlock, observability, and the fix that makes them reach silicon |
| Auto-unlock policy | **(d)** default-on, **reported**, with a `--skip-sdp-unlock` opt-out |
| CLI surface | `firestarter dev sdp <chip> <enable\|disable>` — datasheet term, family-honest, leaves `lock-status` free |
| gh#11 polling defect | **In scope** — the 1-byte-in-64 page poll is folded into this milestone |
| `dev test` phantom-erase | **In scope** — load-bearing for the closeout's evidence value |
| AT28C silicon | **None on the bench** → software-only validation; no requirement depends on a community reply |
| `--sdp-relock` | **Deferred to v1.23+** |
| Three-field SDP report shape | **Deferred** — a minimal honesty floor is retained (HOST-05) |
| `lock-status` + protection table | **Out of scope** — stays planted as a seed |

---

## v1 Requirements

### Trace Harness (the oracle — no production code changes)

- [x] **TRACE-01**: Native register-trace recording captures data bytes and `/CE`//`/OE` edges in the **same ordered stream** as register writes, behind a new opt-in flag so every existing suite stays byte-exact
- [x] **TRACE-02**: A `0x0D` SDP trace suite pins the exact ordered `(LSB, MSB, data, CE-pulse)` stream `eeprom28c_write_init` emits for **each of the four `0x0D` pinouts**, and is **RED against today's tree**
- [x] **TRACE-03**: First-class negative traces go RED — unlock table mutated to `0x10`, lock table swapped for the write prefix, a planted `LOG_` inside the timing window, and `protocol != 0x0D` reaching `configure_not_implemented()`/`0xBB`
- [x] **TRACE-04**: The call-ordered scripted mock is replaced by an **address-keyed** `mock_get_data`, retiring the fixture that cements the inverted success check as expected behaviour (`test_eeprom28c_chip_id.cpp:104`)
- [x] **TRACE-05**: A DB-invariant host test pins `chip_id_check: false` across all **84** `algorithm == 13` entries, making the dead identity gate a machine-checked fact
- [x] **TRACE-06**: A written premise-verification artifact settles whether `write at28c256` aborts at INIT on `3.0.0b11`, and records every PROJECT.md correction the finding implies

### Emitter Fix (make the sequences reach silicon)

- [x] **FIX-01**: A `0x0D`-local, remap-aware command emitter built on `handle->firestarter_set_data` replaces `flash_execute_command(EEPROM_SDP_DISABLE)`, so command writes are emitted with `/WE` asserted on all four pinouts
- [x] **FIX-02**: The inverted `(0x5555, 0x20)` read-back is **deleted, not salvaged**, and replaced by a `t_WC` wait and/or toggle-bit poll — a success condition that is not anti-correlated with success
- [x] **FIX-03**: Upper-address staleness (A16–A18 retaining whatever the previous operation left) is closed for the **18 chips ≥64 KB**, as a by-product of routing through the full remap
- [x] **FIX-04**: `flash_utils.{h,cpp}`, `flash_5v_page.cpp` and `flash_nor_unlock.cpp` are **byte-untouched**, and the `0x05`/`0x06`/`0x07`/`0x10`/SRAM traces stay byte-identical
- [x] **FIX-05**: Terminal-byte constant guards pin each table's last byte and assert SDP-disable (`…0x20`) and `FLASH_ERASE` (`…0x10`) are not the same object — the one-nibble chip-erase hazard
- [x] **FIX-06**: Per-page write polling is corrected so a **partial write cannot report success** — today `eeprom28c_write_execute` polls 1 byte in 64, the more likely root cause of gh#11's symptom than SDP

### Observability (make the unlock visible and declinable)

- [x] **OBS-01**: The auto-unlock is reported — one line before and one after the sequence, **never inside it**
- [x] **OBS-02**: `FLAG_SKIP_SDP_UNLOCK` (`0x100`) is honoured in firmware, so the user can decline the unlock
- [x] **OBS-03**: A named `AT28C_TBLC_MAX_US = 100` constant is cited at every call site, and a source-scan test with a planted `LOG_` fixture proves no logging occurs inside the timing window
- [x] **OBS-04**: The emitted sequence's host-side duration is **measured** per board via `micros()` and logged after the sequence — one of the few v1.22 claims provable without an AT28C (measured on a real Leonardo: 572 µs, budget 600 µs; full provenance in `118-MEASUREMENT.md`)
- [x] **OBS-05**: With no new flag set, `write` behaviour is **byte-identical to `3.0.0b11`** apart from the corrected emitter and the added report lines

### SDP Lock (the genuinely new capability)

- [x] **LOCK-01**: SDP-enable is emitted as **3 loads + `t_WC` with no data payload** (`AA→0x5555`, `55→0x2AAA`, `A0→0x5555`), per Atmel doc0270 `0270L–PEEPR–2/09` §19 note 2 (Plan 119-05: four dump-authored `SDP_FIXED_LOCK_*` goldens pin the production `CMD_SDP_LOCK` stream on all four `0x0D` pinouts, `delay(AT28C_TWC_MAX_MS)` follows, and the no-payload termination is asserted positionally — Case 17)
- [x] **LOCK-02**: `CMD_SDP_UNLOCK` and `CMD_SDP_LOCK` are invocable **in their own right** — no data payload, no host `DONE` round-trip, `init`/`end` left NULL so those phases are skipped (Plan 119-04 wired the standalone entry points and dispatch arms; Plan 119-07 closes the dispatch proof — case group 3 in `test_configure_memory.cpp` machine-checks non-NULL `main` and NULL `init`/`end` for both commands on `0x0D`, with RESEARCH F-T's correction recorded in-source: NULL `init`/`end` does not skip the INIT/END frame pairs, only the `DONE` round-trip and any `#` data frame are absent; cases 24/25 in `test_eeprom28c_sdp.cpp` prove the op-layer refusal end to end, including `CMD_ERASE`'s DEVTEST-01 firmware-half fix)
- [x] **LOCK-03**: The ordinal `cmd < CMD_DEV_ADDRESS` admission guard (`firestarter.cpp:79`) is replaced by an explicit predicate enumerating the memory commands, proven **identical with and without `-D DEV_TOOLS`** — a prerequisite for LOCK-02, since no free command slot exists below the guard (D-04's two oracles: the two-env truth table over all 256 `cmd` values, Plan 119-02; and `check_is_memory_cmd_no_ifdef.py`'s brace-matched source-scan gate + planted-violation fixture proving no build-configuration conditional in the predicate's body, Plan 119-03)
- [x] **LOCK-04**: `configure_eeprom28c` gains a `default:` → `MSG_ERR_NOT_SUPPORTED` arm, and lock/unlock are fail-closed for any `protocol != 0x0D` (mechanism-corrected, intent-satisfied — D-05 disproved the literal `default:` arm against live source: `configure_memory` pre-sets the generic `main` for `CMD_READ`/`CMD_WRITE`/`CMD_VERIFY` before `configure_eeprom28c` runs, so that arm would have refused read and verify on all 84 `0x0D` chips, and `configure_eeprom28c` only ever runs for `0x0D` so it could never refuse another protocol either. D-06's single generic NULL-`main` refusal at `operation_utils.cpp` satisfies the intent instead — Plan 119-07: the refusal reuses the existing `MSG_ERR_NOT_SUPPORTED` id, no `default:` arm was added to `configure_eeprom28c` or any other `configure_*` handler, and case groups 1/2 in `test_configure_memory.cpp` machine-check that read/write/verify stay non-NULL for every protocol while `CMD_SDP_UNLOCK`/`CMD_SDP_LOCK` are NULL-main for every protocol other than `0x0D`)
- [x] **LOCK-05**: `FLASH_ENABLE_WRITE_PROTECTION` is **preserved, not deduped** — it is byte-identical to `FLASH_ENABLE_WRITE` because `AA-55-A0` is genuinely dual-purpose, so the name is the only discriminator (Plan 119-06: `test_lock05_three_way_enable_table_identity` machine-checks the three-way byte-identity against the production objects, `test_lock05_enable_table_objects_distinct` machine-checks the three-way pairwise distinctness, Plan 119-05's Case 17 pins the no-payload stream absence, and `test_sdp_table_parity.py`'s `test_eeprom_sdp_enable_matches_flash_enable_write_and_write_protection` gives a second, independent source-text oracle)
- [x] **LOCK-06**: A `pio run -e leonardo` flash delta is reported and stays within the measured 3348 B headroom (Plan 119-10: the `3348 B` figure is **superseded** — it predates Phase 117's `+204 B` and Phase 118's `+152 B`, already spent. Judged instead against the live phase-base headroom: `28672 − 25680 = 2992 B` (phase base commit `1880054`). Full-phase Leonardo delta measured **+392 B** (per-plan: 119-01 +0, 119-02 +12, 119-04 +262, 119-05 +0, 119-06 +0, 119-07 +18, 119-08 +100), landing at `26072/28672` = **2600 B free — fits**, no threshold claim beyond that. Reported against the `-D DEV_TOOLS` build, the tighter and therefore binding configuration, since the flag alone costs 1292 B (a release-config Leonardo build measured `24388/28672` at phase base). Uno measured `+390 B` (`23542→23932/32256`), uno328pb `+384 B` (`23592→23976/32384`); Uno and uno328pb capacities differ by bootloader reservation, so only deltas are compared across boards, never free-space figures or percentages.)

### Host Surface (lands strictly after firmware)

- [x] **HOST-01**: `firestarter dev sdp <chip> <enable|disable>` exists, behind the v1.21 destructiveness confirm + `-y` + the SAFE-04 absent-chip hard-fail (Plan 120-08: the locked surface `firestarter dev sdp <chip> <enable|disable>` — chip first, mode second, `click.Choice` argument, no mode flag — lands behind D-08's four-gate order (absent → capability → support-status → confirm → serial), with the three deliberate inversions from `dev test`'s analog named and applied: gate order reversed (confirm no longer precedes the absent-chip hard-fail), the `--destructive`-style mode flag dropped per D-05, and off-TTY refuses without `-y` per D-06 rather than proceeding. Refusal is proven by "no confirm shown" + "no port opened" + reason text on every leg — including all nine `adapter-required` `0x0D` parts, parametrised individually — never by exit code alone.)
- [x] **HOST-02**: `write --skip-sdp-unlock` emits the `0x100` flag, following the in-tree rule that `--skip-X` skips a chip-state-modifying operation (Plan 120-09: `write --skip-sdp-unlock` emits `FLAG_SKIP_SDP_UNLOCK 0x100`, mapped by a keyword-only `build_flags` parameter (plan 120-06, D-19) and threaded through `_build_op_flags`; exposed on `write` only because firmware auto-unlocks in `eeprom28c_write_init` and nowhere else (D-17); a non-`0x0D` chip warns and proceeds with the bit still emitted (D-18); and the BUG-1 characterization contract was re-verified unmodified. There is **no** `0x200` flag despite the ROADMAP wording (F-120-05) — this text is a note, not an edit to that wording.)
- [x] **HOST-03**: New `CMD_*`/`FLAG_*` values land in the same commit pair across `firestarter.h` ↔ `constants.py`, **with mandatory `COMMAND_NAMES` entries**, and the constants-parity test is extended (`COMMAND_SDP_UNLOCK 9` / `COMMAND_SDP_LOCK 10` / `FLAG_SKIP_SDP_UNLOCK 0x100` plus two mandatory `COMMAND_NAMES` entries landed in Plan 120-02; the parity test itself was **rebuilt** in Plan 120-07 from hardcoded literals into a real two-way header-parsing gate with three planted-violation fixtures, a `COMMAND_NAMES`-coverage leg, a fail-closed path, and a machine-checked conditional-compilation assertion. Honest reading of "same commit pair": firmware landed the defines in **Phase 119** and the host lands them here, deliberately, since HOST-06 forbids the reverse order — what the requirement demands and what is now proven is that the pair *agrees*, machine-checked in both directions.)
- [x] **HOST-04**: A pre-wire capability refusal keeps SDP commands away from non-SDP parts inside the `0x0D` bucket — the 2 FRAM parts and the pre-SDP `2804`/`2816`/`2817` class — resolved in code, with **zero DB change** (Plan 120-09, plus Plan 120-08's `dev sdp`: the pre-wire refusal is a **fail-closed allow-list** in `firestarter/sdp_capability.py` rather than HOST-04's literal five-part deny-list, because on a part with no SDP command decoder the sequence is not inert; the partition is **43 ALLOW / 41 REFUSE** derived from `infoic.xml` `INFOIC2PLUS` `flags` bit 15 at minipro commit `a8efaedc236c1d9718bd28299dfbb99536b010ff` (see `120-SDP-PARTITION.md`), machine-checked total and stable by `tests/test_sdp_capability.py`; the refusal covers **both** `dev sdp` (plan 120-08) and `write`'s automatic unlock (D-04, this plan), with a mandatory report line; and **zero `chip_database.json` change** — nothing reads `infoic.xml` at runtime or in CI and it is not committed to either sub-repo.)
- [x] **HOST-05**: The SDP outcome is reported honestly and **never as a fabricated state boolean** — where state is unreadable, the report says so (Plan 120-08: the honesty floor is met by D-09's INFO promotion (Plan 120-03), which is what makes the firmware report lines visible at default verbosity at all, plus D-10's symmetric host summary line — carrying the unreadable-state caveat on both `enable` and `disable`, and no duration figure (mechanically enforced by `get_response()`'s INFO-band filtering, not merely by discipline) — plus D-11's plain 0/1 exit code, with a `0x87` `MSG_WARN_SDP_TBLC_EXCEEDED` frame staying in the text and never changing the code. The deferred three-field SDP report shape (SDP-F2) is unchanged; this is the retained minimal floor.)
- [x] **HOST-06**: The host half never lands before the firmware half; a host emitting `0x100` against `3.0.0b11` would be silently ignored and would run the unlock the user declined (Plan 120-10: the invariant is upheld **in practice at runtime**, by exploiting the asymmetry between the two halves of the wire surface — an unknown **command** produces `MSG_ERR_UNKNOWN_CMD`, mapped in plan 120-08 to a firmware-too-old refusal naming `firestarter fw --install` (D-14); an unknown **flag bit** produces **silence**, so the flag half requires firmware's `MSG_WARN_SDP_UNLOCK_SKIPPED` (`0x86`) ack and fails loudly when it is absent (D-15, this plan), scoped to protocol `0x0D` since firmware only reads the flag bit — and only ever emits `0x86` — on `0x0D` writes. The honest limitation: D-15 **detects after the fact**, it does not prevent — on old firmware the unlock has already been emitted by the time the user is told. **No version floor was introduced** (D-16): the host structurally cannot distinguish `3.0.0b11` from a later pre-release because `_probe_port`'s capture regex truncates the suffix; widening it touches the ring-fenced transport version-capture path and is deferred. A numeric minor bump was rejected because it would make HOST-06's correctness depend on a release-versioning decision belonging to Phase 122's CLOSE-03. The **landing-order fact with commit provenance**: the firmware half landed first, in Phase 119, final commit `0048b3d` on branch `v1.22-at28c-software-data-protection-lifecycle`, tree clean; the host half lands in Phase 120; `firestarter/include/version.h` still reads `3.0.0b11` and was not bumped. `0x86` shipped in Phase 118 for a different purpose and is repurposed here with **zero firmware change**.)

### `dev test` Correctness (unblocks usable community evidence)

- [ ] **DEVTEST-01**: `OP_ERASE` is marked `NA` for protocol `0x0D` with a named reason, and firmware fail-closes on `CMD_ERASE` for `0x0D` — today the sweep reports OK having done nothing and auto-tags `ladder_state = "community-fail"` even when write and verify pass (**split by phase, Plan 119-09:** the firmware half — fail-closed on `CMD_ERASE` for `0x0D`, via a generic op-layer NULL-`main` refusal, not a `0x0D`-local arm — landed in **Phase 119** under D-06/D-07/D-08; the host half — `OP_ERASE` marked `NA` for `0x0D` with a named reason in the `dev test` sweep — remains **Phase 121**. Checkbox stays unticked pending the host half.)

### Gates & Documentation

- [ ] **GATE-01**: An AST capability gate is paired with a planted-violation pytest proving the gate actually fails — the anti-hollow discipline that closed this project's v1.12 hollow-GATE-03 debt
- [ ] **GATE-02**: Docs are corrected where they describe behaviour that does not reach silicon — `doc/PROTOCOLS.md` §1.6, `doc/lockable-proms.md`, `doc/protocol-id.md`, `firestarter/CLAUDE.md`, both READMEs — including an explicit note that `0x0D` has **no erase**, so `-b` is required for a non-blank AT28C and skips nothing else on this family
- [ ] **GATE-03**: The full non-regression set is green — native suite, `check_dispatch.py`, host pytest, ruff/format against the **py3.9/3.11 CI targets** (not the devcontainer's 3.12), and `diff_db.py` identity proving the DB is untouched

### Close (honesty ledger)

- [ ] **CLOSE-01**: `0x0D` stays `UNVERIFIED` in `PROTOCOL-LEDGER`, **zero** chips change `support_status`, and the 84-chip count is unchanged
- [ ] **CLOSE-02**: gh#12 is answered with the decided auto-unlock policy (its reporter's own 2024 question) and gh#11 is followed up — both framed as *"here is what changed and why we believe it addresses your report; please re-test"*, **never as a verified fix**
- [ ] **CLOSE-03**: The accept/avoid/cleanup decision for the `beta` push is made and recorded **before** any push — v1.21's close auto-cut a stray `3.0.0b12`

---

## Future Requirements (deferred, tracked)

### Deferred by operator decision this milestone

- **SDP-F1**: `--sdp-relock` opt-in post-write re-lock, gated on verify success. Deselected for v1.22. Note the constraint if it returns: an unconditional step in a conditional pipeline is the Phase-112 `if destructive:` lesson repeating, and a re-lock after a failed verify strands the user with a locked chip they cannot retry on.
- **SDP-F2**: The full three-field SDP report shape (`sdp_command_issued` / `sdp_sequence_ack` / `sdp_state_after`). Deselected; HOST-05 retains the honesty floor.

### Deferred on research grounds

- **SDP-F3**: A `dev test` SDP step. Perturbs `dedup_fingerprint` for all 84 `0x0D` chips and pulls the locked D-03/D-04 ladder taxonomy plus the orchestrator-only AST gate into a milestone with no silicon — triples the blast radius.
- **SDP-F4**: Write-probe SDP *inference* — the only real state observation available, but destructive and an honest-labelling design problem.
- **SDP-F5**: The datasheet 6-byte software chip-erase for `0x0D`. A real gap, but an *erase* feature riding an *SDP* milestone, and it needs `OE = V_H = 12 V` — the T-93-CANERASE hazard class.
- **SDP-F6**: SDP handling for the AT29C / SST39SF / W29EE families — multiplies the no-silicon problem across settled bench evidence.
- **SDP-F7**: Datasheet verification of SDP magic addresses for AT28C040 / AT28C16 / AT28C04. Low risk given truncation is structural, but recorded UNVERIFIED rather than assumed.
- **SDP-F8**: The `DIP24_2816` missing `static-high-pins` finding — 19 chips have `static_high_mask == 0` so VCC (bus line 13) is not force-driven, unlike `DIP24_2716`/`DIP24_2732`. The remap fix does **not** address it. Confirm against the shield schematic before acting.

---

## Out of Scope

| Feature | Reason |
|---------|--------|
| `firestarter lock-status <chip>` + hand-curated protection table | Operator decision — stays planted as a seed. Its DB axis plus AMD Autoselect / Winbond product-ID query sequences are a different shape of work. |
| Auto-relock by default | Unverifiable on this family, and it manufactures the gh#12 bug for the next user. |
| "Leave the chip as you found it" as a default | **Physically unimplementable** — SDP state is unreadable, so restoring it is a guess wearing a promise. |
| Populating `chip_id_value` for AT28C | Anti-feature — those 64 bytes are *user*-writable and read `0xFF` virgin, so an ID check would fail on a blank part. |
| A generic `locked` DB boolean | `infoic.xml` cannot supply it (pinned negative result: `W29C020C` and `W29EE011` carry identical flags), it resurrects the override stack v1.16 deleted, and it competes with `support_status`. |
| Fail-loud-by-default on a locked chip | Rejected with the auto-unlock policy — makes every AT28C write a two-step for all 84 chips' users. |
| Deleting `FLASH_ENABLE_WRITE_PROTECTION` | The duplication is datasheet-**correct**; the dedup destroys real semantics. Abandoned commit `0052c42` stays abandoned. |
| A `--force` path that widens which chips a lock can reach | `--force` keeps its one existing meaning (ERROR→WARNING on ID mismatch). For *lock*, prefer refuse-over-warn. |
| Promoting SDP into shared `flash_utils` code | The shared implementation **is** the broken one; extending it would change the emitted stream for the bench-proven `0x05`/`0x06` families. Worth ≤48 B against 3348 B headroom. |
| Any claim that SDP works on real AT28C silicon | No AT28C part on the bench. See the validation ceiling below. |

---

## Validation Ceiling (stated before work begins)

**Provable in software:** the emitted address/data/strobe byte-stream is correct per pinout and per size band; the sequence contains no logging and its host-side duration is measured; lock/unlock is `0x0D`-scoped and fail-closed elsewhere; the admission guard is `DEV_TOOLS`-invariant; the other protocol families' traces are byte-identical; the host refuses before opening a port.

**NOT provable without an AT28C part:** that silicon actually enters or leaves the protected state; that `tBLC` is met *as accepted by the die*; that gh#11's symptom is gone; that the curated capability partition is correct per family.

**Permitted claim at close:** *"The SDP lock and unlock sequences are emitted exactly as specified, verified byte-exact by golden register trace across all four `0x0D` pinouts, with a documented and measured host-side timing assumption."*

**Forbidden claim:** *"SDP lock/unlock works on an AT28C256."*

---

## Traceability

Filled during roadmap creation (`/gsd-new-project` → roadmapper, 2026-07-27). Every v1 requirement maps to exactly one phase.

| Requirement | Phase | Status |
|-------------|-------|--------|
| TRACE-01 | Phase 116 | Complete |
| TRACE-02 | Phase 116 | Complete |
| TRACE-03 | Phase 116 | Complete |
| TRACE-04 | Phase 116 | Complete |
| TRACE-05 | Phase 116 | Complete |
| TRACE-06 | Phase 116 | Complete |
| FIX-01 | Phase 117 | Complete |
| FIX-02 | Phase 117 | Complete |
| FIX-03 | Phase 117 | Complete |
| FIX-04 | Phase 117 | Complete |
| FIX-05 | Phase 117 | Complete |
| FIX-06 | Phase 117 | Complete |
| OBS-01 | Phase 118 | Complete |
| OBS-02 | Phase 118 | Complete |
| OBS-03 | Phase 118 | Complete |
| OBS-04 | Phase 118 | Complete |
| OBS-05 | Phase 118 | Complete |
| LOCK-01 | Phase 119 | Complete |
| LOCK-02 | Phase 119 | Complete |
| LOCK-03 | Phase 119 | Complete |
| LOCK-04 | Phase 119 | Complete (mechanism-corrected, intent-satisfied) |
| LOCK-05 | Phase 119 | Complete |
| LOCK-06 | Phase 119 | Complete |
| HOST-01 | Phase 120 | Complete |
| HOST-02 | Phase 120 | Complete |
| HOST-03 | Phase 120 | Complete |
| HOST-04 | Phase 120 | Complete |
| HOST-05 | Phase 120 | Complete |
| HOST-06 | Phase 120 | Complete |
| DEVTEST-01 | Phase 119 (firmware half, landed) + Phase 121 (host half) | Pending |
| GATE-01 | Phase 121 | Pending |
| GATE-02 | Phase 121 | Pending |
| GATE-03 | Phase 121 | Pending |
| CLOSE-01 | Phase 122 | Pending |
| CLOSE-02 | Phase 122 | Pending |
| CLOSE-03 | Phase 122 | Pending |

**Coverage:**

- v1 requirements: **36** total (TRACE 6 · FIX 6 · OBS 5 · LOCK 6 · HOST 6 · DEVTEST 1 · GATE 3 · CLOSE 3)
- Mapped to phases: **36/36** (Phase 116: TRACE ×6 · Phase 117: FIX ×6 · Phase 118: OBS ×5 · Phase 119: LOCK ×6 + DEVTEST's firmware half (Plan 119-09 amendment, D-08) · Phase 120: HOST ×6 · Phase 121: DEVTEST ×1 (host half only) + GATE ×3 · Phase 122: CLOSE ×3). DEVTEST-01 itself is still counted once, mapped to both phases by split — the 36/36 total and the 0-unmapped count are unaffected by the split.
- Unmapped: **0** ✓

---
*Requirements defined: 2026-07-27*
*Last updated: 2026-07-27 after roadmap creation — 36/36 requirements mapped to Phases 116-122, 0 unmapped*

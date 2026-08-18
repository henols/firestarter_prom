# Requirements: Firestarter v1.32 — AT28C Write-Path Root Cause & Report Provenance

**Defined:** 2026-08-18
**Core Value:** Algorithm-first dispatch — the `protocol_id` (`algorithm`) is the single authoritative
dispatch key end to end. v1.32 turns that key on the project's own diagnostics: a community `dev test`
report must be attributable to the firmware that produced it before any protocol-`0x0D` write-path
claim can be made about it.

---

## Evidence Ceiling — read before scoping any phase

**There is still no AT28C part in operator inventory** (recorded 2026-08-04 in
`.planning/todos/pending/at28c256-write-path-failure-gh20.md`, re-confirmed by the operator at this
milestone's kickoff). This is not a caveat appended at the close; it is a constraint on what any
requirement below is allowed to assert:

- **`0x0D` stays `UNVERIFIED`** in `PROTOCOL-LEDGER`. No phase may graduate it, and no
  `support_status` may change on that basis.

- **gh#21, gh#32, gh#11 and gh#12 stay OPEN.** A code fix is not a validation. Only a fresh passing
  `dev test` on real silicon closes them, and per the project's own rule only `devtest-triage` closes
  a `dev test` issue, and only on a PASS report.

- **No phase may claim silicon proof.** The firmware page-size change (PGSZ) ships software-proven
  and must say so in those words.

- The honest outward outcome of this milestone is a corrected code path plus a request to the
  reporter for a fresh run — which is only worth asking for *because* PROV makes that run
  self-identifying.

This is the same ceiling v1.22 and v1.30 operated under, and it held in both. It holds here.

---

## v1 Requirements

### Report Provenance (PROV)

The dependency spine. `cli_handlers.py:2503` hardcodes `fw_board_identity=None`, so **every `dev test`
report ever filed carries a null firmware identity** — gh#21 and gh#32 report host `3.0.0b15` against
an unknown firmware and cannot be distinguished from a board lacking the entire Phase-117–120 `0x0D`
fix stack. Host-only; needs no AT28C part.

- [x] **PROV-01**: A `dev test` report records the firmware version and board identity of the
      programmer that produced it, in place of today's unconditional `null`.

- [x] **PROV-02**: That capture happens without violating the SAFE-02 orchestrator-only contract —
      it does not open an extraneous connection outside the orchestrator, and `EpromOperator.comm`
      remains a transient per-operation connection.

- [x] **PROV-03**: The recorded firmware string preserves the **prerelease suffix**, so a board
      running `3.0.0b19` is distinguishable in the report from one running `3.0.0b11` — exactly the
      discrimination this requirement exists to enable. *(Corrected 2026-08-18, Phase 147 D-05/D-06:
      this requirement was originally written asserting that `_probe_port`'s `[\d.x]+` pattern
      truncates the identity to `3.0.0`. That premise is **false**. The regex at `serial_comm.py:866`
      builds a separate local that feeds only `_validate_firmware_version`; `comm.firmware_identity`
      (`serial_comm.py:412`) holds the raw, untruncated `"<version>:<board>"` decoded from the CAP-02
      ack tail. Suffix preservation therefore comes **for free** from recording that field. The
      version-capture path is GATE-1.8d ring-fenced and MUST NOT be edited to satisfy this
      requirement.)*

- [ ] **PROV-04**: The report schema version is bumped, and reports written by earlier versions
      (carrying `fw_board_identity: null`) still parse without error.

- [ ] **PROV-05**: A null or unobtainable firmware identity renders as an **explicit unknown** in
      the human-readable report surfaces and in the issue parser — never as a blank, and never as the
      bare rendering of `None` that reads like a captured value. *(Tightened 2026-08-18, Phase 147
      D-10: the fenced report JSON deliberately keeps typed `null` so machine consumers can test
      `is None` and so PROV-04's backward-compatibility story stays one case. "Both report outputs"
      as originally worded read as requiring a string sentinel in the JSON; it does not.)*

- [ ] **PROV-06**: The `[dev test]` issue parser surfaces the firmware identity, so a triager can
      attribute a report without asking the reporter.

### Database Decode & Numeric Values (DATA)

Two findings plus the `db-numeric-values-simplification` seed. `electrical.vcc: "4V"` is a genuine
decode defect against the AT28C256 datasheet's 4.5–5.5 V; it is inert on the wire (no VCC field is
sent and the firmware has no VCC control register), so it cannot explain `write BAD`, but it is wrong
data the generator emits. The seed touches the same field, so both land together — numericalising
`vcc` turns the correction into a value change rather than a string edit.

- [ ] **DATA-01**: `electrical.vcc` for the AT28C family decodes to the datasheet's 4.5 V minimum
      rather than `4V`, fixed in `build_db.py`'s decode function — never in the generated JSON.

- [ ] **DATA-02**: Voltages are stored as millivolt integers and timing as microsecond integers,
      ending the half-done state where every chip carries both `vpp: "12V"` and `vpp_mv: 12000` while
      `vcc`/`vdd` exist only as unit-suffixed strings.

- [ ] **DATA-03**: `database.py`'s string-coercion layer (`_map_data`'s `.replace("V","")` → `float()`
      and `_parse_pulse_duration`) is deleted, not merely bypassed.

- [ ] **DATA-04**: No generator field is emitted that cannot be proven from `infoic.xml`. No per-chip
      lookup table keyed on part number, and no sibling to the pre-existing `_PAGE_SIZE_BY_PART`
      exception.

- [ ] **DATA-05**: `diff_db.py` is the review artifact for every decode change, and the blast radius
      is justified: a one-chip fix that moves hundreds of chips means the condition was too broad.
      `check_dispatch.py` (GATE-03) stays green and is never weakened to make a change pass.

- [ ] **DATA-06**: `protect_on_after` stops being dead data. It is either given a consumer by RELOCK
      or documented explicitly as an advisory upstream hint with no runtime effect — the database no
      longer states an intent the system silently ignores.

### Firmware Page-Size Seam (PGSZ)

`eeprom_28c.cpp` hardcodes `PAGE_SIZE 64` while `infoic_page_size_raw` already ships in the database.
The handler's own comment records the per-chip delivery path as deferred and "not yet inserted into
ROADMAP.md". The floor is deliberate and safe (a smaller flush granularity issues two legal write
cycles into one physical page and can never overrun), but AT28C010 needs 128. **The only
firmware-touching workstream — dual-repo lockstep.**

- [ ] **PGSZ-01**: The per-chip page size travels from `chip_database.json` over the wire to the
      firmware handler, through the existing JSON command path.

- [ ] **PGSZ-02**: The `0x0D` handler uses the delivered page size, falling back to the conservative
      64-byte floor when the field is absent — so an older host against newer firmware still writes
      correctly rather than overrunning a page.

- [ ] **PGSZ-03**: Constants and flag bits stay in lockstep between `firestarter/include/firestarter.h`
      and `firestarter_app/firestarter/constants.py`, changed together in one milestone branch.

- [ ] **PGSZ-04**: The flash and RAM delta is measured against a pre-change baseline for all three AVR
      targets. The `leonardo` warning watermark has near-zero headroom and v1.31 closed with MERGE-05's
      band breach open — this phase must not silently consume what is left.

- [ ] **PGSZ-05**: The change is stated as **software-proven and unvalidated on silicon**, in those
      terms. No page-size claim is made about any physical AT28C part.

### Deliberate Protection — `write --sdp-relock` (RELOCK)

Promoted from Backlog **999.28**, deferred out of v1.30 as Phase 135. Text carried forward **verbatim**
from `.planning/milestones/v1.30-REQUIREMENTS.md` §RELOCK with checkboxes restored from `⏸` to `[ ]`;
nothing was re-authored. v1.30 shipped the deletion of `dev sdp enable|disable` without this half, so
since 2026-08-05 there has been **no supported way to deliberately protect an SDP part**. RELOCK-07
already shipped in v1.30 Phase 137 and is not repeated here.

**Polarity is already decided — do not re-litigate:** verify failure ⇒ skip the relock and report it
loudly, leaving the recoverable state. Relocking a part whose write did not verify would protect a bad
image behind a lock that cannot be read back and can only be cleared by another write.

- [ ] **RELOCK-01**: `firestarter write --sdp-relock` deliberately protects a part after a write,
      as the single user-facing way to do so.

- [ ] **RELOCK-02**: An explicit verify pass runs on the `--sdp-relock` path; the default `write` path
      stays byte-identical to today. (`write` has no verify pass at all today — this is the added scope
      the decided polarity requires.)

- [ ] **RELOCK-03**: On verify failure the relock is **skipped** and `sdp_lock` is provably not called.
- [ ] **RELOCK-04**: A skipped relock is reported **loudly** — a mandatory final `WARNING:` line or a
      non-zero exit, asserted by test. Because protection state cannot be read back, an `INFO`-level
      skip leaves the user with **no way to ever discover the part is unprotected**.

- [ ] **RELOCK-05**: `--sdp-relock` on a non-`0x0D` chip **refuses loudly** rather than
      warning-and-proceeding, because the lock sequence's magic-address bytes would land as data.

- [ ] **RELOCK-06**: `--sdp-relock` on a capability-REFUSED chip refuses **before any hardware is
      energized** — this is where the deleted command's capability gate is repurposed, not discarded.

- [ ] **RELOCK-08**: Any `write --help` output pinned by v1.30 Phase 136's channel-gating tests is
      updated **deliberately** as part of this work, never silently re-baselined.

### Protection Readability — `lock-status` (LOCK)

Consumes the `lock-status-command-hand-curated-protection-table` seed. This is the half RELOCK cannot
supply: after a relock the user still cannot observe the resulting state, and the gh#12 reply is
obliged to admit that. The 2026-07-10 research settled the sourcing question — `infoic.xml` **cannot**
supply protection readability, because W29C020C (readable permanent boot block) is flag-identical to
W29EE011 (SDP-only, unreadable), and the entire AMD Autoselect readable-sector-protect group carries
zero protection bits. A hand-curated family-level table is therefore not a violation of DATA-04's
proof rule; it is what that rule leaves when upstream genuinely lacks the field.

- [ ] **LOCK-01**: A hand-curated, family-level protection table records mechanism, readability and
      permanence, sourced from `firestarter_app/doc/lockable-proms.md` with per-family citations.

- [ ] **LOCK-02**: `firestarter lock-status <chip>` reports the protection state of a chip on families
      where it is documented as readable.

- [ ] **LOCK-03**: On families where protection state is **not** readable — `0x0D`/SDP among them — the
      command refuses gracefully and says why, rather than guessing or returning a fabricated value.

- [ ] **LOCK-04**: The command never over-promises: it distinguishes "unprotected" from "readability
      not supported on this family", and its output cannot be read as a lock-state guarantee where
      none exists.

### Outward-Facing Close (OUT)

Every item here is **operator-reviewed before posting** and must be gated separately from automated
approval — `--auto`/`--chain` auto-approves human-verify checkpoints, so an outward-facing gate that
relies on `autonomous: false` alone is not self-protecting.

- [ ] **OUT-01**: The owed gh#12 reply is posted — v1.30's CLOSE-06, held open by design. It must state
      both halves plainly: `disable`'s behaviour survives as `write`'s automatic auto-unlock, `enable`
      returns as `write --sdp-relock`, and it must not describe the v1.30 gap as if the original ask
      had been satisfied all along.

- [ ] **OUT-02**: gh#21 (with #32 folded) receives a comment stating what changed in code, what remains
      unproven, and a request for a fresh `dev test` run — now attributable because of PROV.

- [ ] **OUT-03**: gh#11's 2024 report is answered in light of the FIX-06 conflation finding, which is
      its actual shape, rather than left silently superseded.

- [ ] **OUT-04**: The release notes announce `write --sdp-relock` and `lock-status` as shipped in the
      version that actually contains them, and correct the forward-looking wording v1.30 left behind.

- [ ] **OUT-05**: No outward artifact claims AT28C silicon validation. Every claim about `0x0D`
      behaviour is paired with its explicit non-claim, per the honesty-ledger discipline v1.22, v1.23
      and v1.31 all closed under.

---

## Out of Scope

| Feature | Reason |
|---------|--------|
| Graduating `0x0D` to `supported` / any `support_status` change | No AT28C part in inventory. The Evidence Ceiling forbids it, and v1.22 and v1.30 both held this line. |
| Closing gh#21 / #32 / #11 / #12 | A code fix is not a validation. Only `devtest-triage` closes a `dev test` issue, and only on a PASS report from real silicon. |
| Reading protection state on `0x0D` / SDP parts | Physically unreadable on the family — LOCK-03 refuses rather than guessing. This is the gap OUT-01 must admit to, not one this milestone can close. |
| Bench validation of the page-size change | PGSZ-05 states it ships software-proven. Adding a bench phase would create a hardware-gated criterion nothing can satisfy. |
| Extending `_PAGE_SIZE_BY_PART` or adding per-chip guess tables | DATA-04. Three such tables were deliberately deleted in Phase 70; the pattern is not reintroduced under a new name. |
| Weakening `check_dispatch.py` (GATE-03) | It stops 12 V reaching a 5 V part's WE/address pin. A hardware-damage guard, not a lint. |
| Re-litigating RELOCK's verify-failure polarity | Decided in v1.22 auto-unlock policy (d), recorded at `PROJECT.md:823`. Skip-and-report-loudly stands. |
| Meta PR #34 | A stale leftover targeting `main` (its title is a v1.23 phase artifact) whose head branch is v1.31's. Superseded by PR #35's merge to `beta`. Operator's call to close; not v1.32 work. |

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PROV-01 | Phase 147 | Complete |
| PROV-02 | Phase 147 | Complete |
| PROV-03 | Phase 147 | Complete |
| PROV-04 | Phase 147 | Pending |
| PROV-05 | Phase 147 | Pending |
| PROV-06 | Phase 147 | Pending |
| DATA-01 | Phase 148 | Pending |
| DATA-02 | Phase 148 | Pending |
| DATA-03 | Phase 148 | Pending |
| DATA-04 | Phase 148 | Pending |
| DATA-05 | Phase 148 | Pending |
| DATA-06 | Phase 150 | Pending |
| PGSZ-01 | Phase 149 | Pending |
| PGSZ-02 | Phase 149 | Pending |
| PGSZ-03 | Phase 149 | Pending |
| PGSZ-04 | Phase 149 | Pending |
| PGSZ-05 | Phase 149 | Pending |
| RELOCK-01 | Phase 150 | Pending |
| RELOCK-02 | Phase 150 | Pending |
| RELOCK-03 | Phase 150 | Pending |
| RELOCK-04 | Phase 150 | Pending |
| RELOCK-05 | Phase 150 | Pending |
| RELOCK-06 | Phase 150 | Pending |
| RELOCK-08 | Phase 150 | Pending |
| LOCK-01 | Phase 151 | Pending |
| LOCK-02 | Phase 151 | Pending |
| LOCK-03 | Phase 151 | Pending |
| LOCK-04 | Phase 151 | Pending |
| OUT-01 | Phase 152 | Pending |
| OUT-02 | Phase 152 | Pending |
| OUT-03 | Phase 152 | Pending |
| OUT-04 | Phase 152 | Pending |
| OUT-05 | Phase 152 | Pending |

**Coverage:**

- v1 requirements: 33 total
- Mapped to phases: 33 ✓
- Unmapped: 0

**Phase map** (numbering continues at 147; v1.31 ran 138–146):

| Phase | Name | Requirements |
|-------|------|--------------|
| 147 | Report Provenance — every `dev test` report names its firmware | PROV-01…06 |
| 148 | Numeric Database Values & the AT28C VCC Decode | DATA-01…05 |
| 149 | Firmware Page-Size Seam (dual-repo lockstep) | PGSZ-01…05 |
| 150 | Deliberate Protection — `write --sdp-relock` | RELOCK-01…06, RELOCK-08, DATA-06 |
| 151 | Protection Readability — `lock-status` | LOCK-01…04 |
| 152 | Outward-Facing Close (operator-gated) | OUT-01…05 |

**RELOCK-07 is deliberately absent** — it shipped in v1.30 Phase 137. The ID gap between RELOCK-06
and RELOCK-08 is intentional and must not be filled by an invented requirement.

**DATA-06 is mapped to Phase 150, not Phase 148** — `protect_on_after` stops being dead data where
its consumer is created (D-03), so the choice between "give it a consumer" and "document it as
advisory" is made once rather than twice.

---
*Requirements defined: 2026-08-18*
*Last updated: 2026-08-18 — traceability populated at roadmap creation (Phases 147–152, 33/33 mapped)*

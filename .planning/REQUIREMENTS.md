# Requirements: Firestarter — v1.37 Operator Safety, Answered Reports & Claim Hygiene

**Defined:** 2026-09-10
**Milestone:** v1.37 — "Say the thing you already know"
**Core Value (this milestone):** The project stops withholding what it already knows — from the operator
about to destroy a chip, from the reporter waiting for an answer, and from the maintainer reading a guard
that no longer exists.

**Scope:** `firestarter_app` (host) and `firestarter_prom` (replies, CI) primarily. Firmware is touched only
at the edges: one `.md`, one baseline JSON plus its test fixtures, and — only if D-3 resolves that way — one
generated message id. No protocol change, no dual-repo behavioural lockstep, no golden register traces.

---

## Decisions taken at activation (operator, 2026-09-10)

Settled here so no phase re-litigates them. Full text and rationale in `PROJECT.md` § Current Milestone.

| ID | Decision |
|---|---|
| **D-1** | **999.43 R4 (session reuse) is OUT**, against a measured 50–80 s/run payoff, because a leased link poisoned by one `SerialError` would silently corrupt every later step. Stays shortlisted for v1.38. |
| **D-2** | The FLOOR strand is in because **Python 3.10 EOLs 2026-10-31**, inside this milestone's window — not because it is thematically related. |
| **D-3** | Whether the flash4 erase refusal takes a **new message id** is a plan-time decision priced against firmware flash on boards at 0 B headroom, not a default. |
| **D-4** | The SAFE gate's part predicate is **derived from the database**, never a hand-kept part list. |
| **D-5** | Every outward-facing reply stays behind **operator wording review**. `--auto`/`--chain` auto-approve human-verify gates, so the REPLY phase must not run in those modes. |
| **D-6** | If AE29F2008 proves misclassified, the fix goes in **`build_db.py`'s decode** — `chip_database.json` is generated. |
| **D-7** | `size_baseline.json`'s re-record uses the **fixture-severance pattern**. No acceptance criterion may say "tests byte-unchanged" — it is unsatisfiable by construction. |

---

## v1 Requirements

### SAFE — refusals and warnings that teach

- [x] **SAFE-01**: The set of parts at risk from an intact JP5 — those whose pin map puts A19 on socket pin 1
      where the shield may still route VPP — is achieved by CORRECTING the pin map so this requirement's own
      words are literally true, not by deriving a synthetic predicate around a database that was wrong.
      Measured 2026-09-10: no pin map in `pinouts.json` declared A19 at all, and all eight 1 MB rows sat on
      `DIP32_STD` (19 address lines, `vpp-pin: [1]`). An address-line-shortfall test, a size threshold, and the
      291-row VPP-on-pin-1 set were considered and rejected (D-01; `182-01-SUMMARY.md`, `182-02-SUMMARY.md`).
      The set is derived from the chip database and its pin maps, not a hand-written list — proved by
      `test_jp5_gate.py::test_synthetic_pin_map_with_pin1_at_index19_appears_in_the_affected_set` — so adding a
      new part to the database cannot silently omit it from the gate.
- [x] **SAFE-02** — **CONFIRMED REQUIRED 2026-09-10 (D-05 resolved)**: Before an affected operation on an
      affected part, the operator is told, in the terminal, that JP5 must be cut on Rev 2.x shields for this
      part and why (`JP5 = A19_CUT`; JP5 routes VPP to socket pin 1), and the operation does not proceed
      without explicit confirmation. D-05 resolution: the operator's stated expectation was that the pin-map
      fix would supersede this requirement; the SAFE-03 trace found the opposite — the outcome is against that
      expectation. On
      Rev 2.x, control bit `0x08` is both `CTRL_VPP_P1_ENABLE` and `CTRL_ADDRESS_LINE_18`, and socket pin 1 is
      bus line 21, inside the address mask a write/erase drives on every byte. The fix moves VPP off pin 1 and
      onto pin 24, but puts A19 on the same physical line pin 1 already was — it relocates the hazard, it does
      not remove it, so the retirement branch of D-05 does not fire. Trace: `182-05-SUMMARY.md`,
      `.planning/notes/jumper-display-ground-truth.md` § "Which operations energize socket pin 1".
- [x] **SAFE-03** — **CONFIRMED 2026-09-10 (182-06 bench probe)**: Which operations the gate covers is settled
      from the shield schematics and the protocol's VPP path — not inferred — and the answer is recorded with
      its evidence. The reporter's own open question ("just writing, or reading too?") is answered in the
      artifact: writing and erasing, not reading, verifying or blank-checking. The one inferred link in that
      trace — assumption A1, the VPE rail level with the boost regulator disabled — was measured at 4.9 V
      (decisively below the ~6 V logic-level threshold), confirming rather than widening the scope. Trace:
      `182-05-SUMMARY.md`, `182-06-SUMMARY.md`, `.planning/notes/jumper-display-ground-truth.md`.
- [x] **SAFE-04** — **CONFIRMED REQUIRED 2026-09-10 (D-05 resolved)**: The gate cannot be auto-answered. A
      non-interactive invocation, a piped stdin, `dev test`, and `--auto`/`--chain` each either refuse the
      affected operation or require an explicit, separate acknowledgement flag — never a default-yes. Same
      D-05 trace and reasoning as SAFE-02, against the same stated operator expectation. `--auto`/`--chain` have no
      firestarter CLI counterpart (measured: no match in `firestarter_app/firestarter/`) — they are GSD
      execution-mode flags, and a GSD run in those modes invokes the CLI non-interactively, so the non-TTY
      refusal satisfies this clause for them, not any flag handling. **Option B taken on `_is_interactive`:**
      the gate (`jp5_gate.py`) carries its own injectable `isatty_fn`, per the `submit.py` pattern, and never
      calls or imports `cli_handlers._is_interactive` — CLAIM-07 needs no amendment and Phase 185 removes that
      symbol as planned.
- [x] **SAFE-05**: `_get_rev2_2_jumper_settings_data` and its commented-out call site are deleted, so no code
      path can render JP5 as an operator-settable config header. (`todos/pending/delete-jp5-dead-renderer.md`)
- [x] **SAFE-06**: A refusal to erase a flash4 (`0x05`) part names the part — instead of a bare `Not
      supported` — and does not carry a cause or an alternative in the CLI text. **AMENDED by Phase 183
      under D-07/D-08:** the operator chose this one-line shape knowingly, with the conflict against this
      requirement's original wording — which had promised the refusal state its cause and its alternative —
      stated on the record before the choice was made. The cause and the alternative are not dropped; they
      move to Phase 187's REPLY-03 (D-09), which answers gh#62 directly instead of printing the answer into
      a tool every operator sees. Trace: `183-03-SUMMARY.md`; shipped
      `firestarter_app/firestarter/flash4_erase_gate.py` and `firestarter_app/tests/test_flash4_erase_gate.py`
      (22 tests).
- [x] **SAFE-07**: The firmware-flash cost of SAFE-06 is measured before the mechanism is chosen, and the
      zero-firmware-byte alternative (host-side text against the existing `MSG_ERR_NOT_SUPPORTED`) is priced
      against a new `messages.toml` id. The decision and both figures are recorded. (D-3) Trace:
      `183-01-SUMMARY.md`'s three-row M1/M2/M3 pricing table — M1 measured +12 B flash / +0 B RAM on all three
      AVR targets, M2 and M3 recorded as structural zeros with their reasons; M3 (host pre-flight policy gate)
      chosen on D-02 grounds, not the flash figures.
- [x] **SAFE-08**: `configure_flash_5v_page`'s `CMD_ERASE` arm — unreachable while the host clears
      `FLAG_CAN_ERASE` for every `0x05` part — is adjudicated explicitly: removed as dead weight, or kept with
      the reason it is kept recorded. It is not left undecided. Trace: `183-04-SUMMARY.md` (deletion at all
      four sites, RED-then-GREEN native proof) and `183-05-SUMMARY.md` (documentation blast-radius repair and
      the measured shrink).
- [x] **SAFE-09**: Whether AE29F2008 is correctly classified `algorithm 5` is investigated against its
      datasheet and the reporter's evidence (die answers `0xDA45`; accepts an `algorithm 6` chip-erase and
      blank-checks clean over `0x40000`). The conclusion is recorded either way; any correction lands in
      `build_db.py`, never in `chip_database.json`. (D-6) Trace: `.planning/notes/ae29f2008-classification-verdict.md`
      and `183-02-SUMMARY.md` — classification CORRECT, equivalence-based verdict; the gh#62 reporter is ALSO
      correct.

### REPLY — answer the reporters

- [ ] **REPLY-01**: gh#23 receives a reply naming what v1.36's fault-attribution work changed and what a
      fresh run would now show, and acknowledging that the reporter's diagnosis — a rig fault reported as a
      chip verdict — was correct.
- [ ] **REPLY-02**: gh#28 and gh#31 each receive a reply naming the v1.36 changes that bear on them and
      requesting an attributable re-run.
- [ ] **REPLY-03**: gh#62 receives the answer this milestone produces: why the refusal exists, what changed,
      and — explicitly — that re-running under another chip's identity with `--force` is not a safe
      workaround.
- [ ] **REPLY-04**: gh#60 receives a reply confirming the hazard from the project's own schematic record and
      stating what the gate does and does not do (it warns; it cannot detect the jumper).
- [ ] **REPLY-05**: Every reply that asks for a re-run states that reports are now `schema_version` 2.0 and
      that v1.36 deliberately re-keyed `dedup_fingerprint`, so a fresh run will not group with the old one.
      A reporter must not read an intended re-key as a new defect.
- [ ] **REPLY-06**: No issue is closed on our own reading. gh#23, #28 and #31 stay open pending the
      reporters' response; a close requires their confirmation or a superseding PASS.
- [ ] **REPLY-07**: gh#9 (`Repository Structure and Contribution Guide`) receives a closing reply or a
      close-as-done — the end-state it describes has been configured since v1.35 Phase 172.

### CLAIM — things the repo says that are not true

- [x] **CLAIM-01**: No file in any of the three repositories names `tools/wiki/dispatch_mirror.py` as a live
      guard. `firestarter/PROTOCOLS.md:11` and `firestarter_app/tests/scan_paths.py:114` both stop claiming a
      checker that was deleted on 2026-09-02.
- [x] **CLAIM-02**: The two orphaned controls `tests/fixtures/planted_dispatch_comment_only_hex.cpp` and
      `planted_dispatch_missing_hex.cpp` are disposed — deleted, or re-pointed at a consumer that exists.
- [x] **CLAIM-03**: Whether the three-way dispatch invariant (dispatch table / host tool / firmware agree) is
      worth re-guarding is decided and recorded. Retiring it is a valid outcome; leaving the question
      unanswered is not.
- [x] **CLAIM-04**: `firestarter/scripts/baseline/size_baseline.json` records the current cold-build figures
      (uno 22968, uno328pb 23016, leonardo 25114 — to be re-measured, not transcribed from this line), and
      the default byte-identity gate is green again.
- [x] **CLAIM-05**: CLAIM-04 is achieved by fixture severance: a new version-named fixture family at the
      post-change figures, with the existing frozen `captured_build_v158_*` family left byte-unchanged —
      proven by an empty `git diff` over those paths. No new MERGE-05 exemption is authored. (D-7)
- [x] **CLAIM-06**: `tests/test_numeric_schema_source_scan.py`'s docstring stops citing `build_db.py:594` for
      a symbol that lives at 545, and cites the symbol and its enclosing scope instead of a line number, so
      the next comment sweep cannot stale it a third time.
- [x] **CLAIM-07**: `_is_interactive` is removed, and the two tests named `..._on_a_tty` either gate real TTY
      behaviour or are renamed and rewritten to assert what they actually cover. No test claims coverage that
      does not exist.
- [x] **CLAIM-08**: Originally demanded that `Catalog sync check` complete with conclusion `success` on
      `firestarter_prom`'s `main`, and that the cause of the failure that has stood since 2026-08-31 be
      recorded rather than merely cleared. Unsatisfiable as written, for two independent reasons: (1) Phase
      185 deletes the workflow on the operator's own decision (D-01), and once it is deleted no run on `main`
      can exist at all; (2) `main` is protected in all three repositories and nothing this phase does lands
      there. AMENDED (D-02) to: the check is retired, and the cause of its standing failure is recorded in
      `.planning/notes/catalog-sync-check-retirement.md`. Precedent for amending in the same phase as the
      work: Phase 183's D-08 (SAFE-06 amended alongside the code) and Phase 184's D-03 (criterion 1 amended).
- [x] **CLAIM-09**: A fail-closed check asserts that every guard file a `ScanPathEntry` names actually exists.
      The CLAIM strand exists because nothing detected any of the above; this is what stops it recurring.

### FLOOR — the one item with an external clock

- [ ] **FLOOR-01**: The advertised Python floor and the type-checker agree. Either mypy enforces the
      advertised `>=3.9` floor, or the floor is raised deliberately and `requires-python`, `target-version`
      and `python_version` all move together.
- [ ] **FLOOR-02**: The choice is made and applied **before 2026-10-31**, when Python 3.10 reaches
      end-of-life, and the milestone does not close with the pair still divergent.
- [ ] **FLOOR-03**: The reasoning — which floor, and why — is recorded where the next person to face this
      finds it, not only in a commit message. The treadmill recurs; the decision should not be re-derived.

---

## Future Requirements

Deferred, tracked, not in this roadmap.

| ID | Requirement | Where it lives |
|---|---|---|
| **REUSE-01** | `EpromOperator` leases one validated link per plan rather than reconnecting per call (measured 50–80 s/run). Deferred by D-1; the lease must be invalidated on any `SerialError`. | Backlog 999.43, shortlisted for v1.38 |
| **BLANK-01** | Region-scope the firmware write-init blank check so `firestarter write -a` stops refusing a partial write to a non-erasable part holding data elsewhere. | Backlog 999.44 (host half shipped v1.36) |
| **DOCS-01** | The wiki's compatibility matrix, family pages and tutorials — content v1.35 relocated but never authored. | Backlog 999.12, gh#5 |

## Out of Scope

| Feature | Reason |
|---|---|
| Detecting JP5's physical state | Not readable by the tool — the reporter says so and the schematics agree. The deliverable is a warning and a refusal, never a detection. |
| Closing gh#23 / #28 / #31 | The reporters' disputes are the open question. A unilateral close is the failure mode this milestone exists to correct. (REPLY-06) |
| Re-guarding the three-way dispatch invariant | CLAIM-03 decides *whether* it is worth doing. Building the guard is a separate milestone's work if the answer is yes. |
| Any firmware protocol or behaviour change | Keeps this milestone off dual-repo lockstep, golden register traces and the flash budget. Leonardo has 0 B flash and 0 B RAM headroom. |
| `dev test` throughput work | D-1. Explicitly deferred with its measurement intact. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SAFE-01 | Phase 182 | Complete |
| SAFE-02 | Phase 182 | Complete |
| SAFE-03 | Phase 182 | Complete — trace recorded (182-05), assumption A1 measured CONFIRMED at 4.9V (182-06) |
| SAFE-04 | Phase 182 | Complete |
| SAFE-05 | Phase 182 | Complete |
| SAFE-06 | Phase 183 | Complete — amended to D-07's one-line refusal (183-06); trace 183-03 |
| SAFE-07 | Phase 183 | Complete — M3 chosen on D-02 grounds (183-01) |
| SAFE-08 | Phase 183 | Complete — deletion landed (183-04), docs/shrink repaired (183-05) |
| SAFE-09 | Phase 183 | Complete — equivalence-based verdict recorded (183-02) |
| CLAIM-01 | Phase 184 | Complete — repaired in all three repos; criterion 1 amended by D-03 (184-05), three D-02 citations kept and re-dated (184-04) |
| CLAIM-02 | Phase 184 | Complete — both fixtures deleted (184-04); their fail-open finding preserved in notes/dispatch-invariant-retirement-verdict.md first (184-03) |
| CLAIM-03 | Phase 184 | Complete — retired outright per D-05; verdict recorded in notes/dispatch-invariant-retirement-verdict.md; zero backlog items filed, deliberately (D-06) |
| CLAIM-09 | Phase 184 | Complete — fail-closed check landed (184-01), proven RED on the real rotted entry before the entry was removed, then on three planted controls |
| CLAIM-04 | Phase 185 | Complete |
| CLAIM-05 | Phase 185 | Complete |
| CLAIM-06 | Phase 185 | Complete |
| CLAIM-07 | Phase 185 | Complete |
| CLAIM-08 | Phase 185 | Complete |
| FLOOR-01 | Phase 186 | Pending |
| FLOOR-02 | Phase 186 | Pending |
| FLOOR-03 | Phase 186 | Pending |
| REPLY-01 | Phase 187 | Pending |
| REPLY-02 | Phase 187 | Pending |
| REPLY-03 | Phase 187 | Pending |
| REPLY-04 | Phase 187 | Pending |
| REPLY-05 | Phase 187 | Pending |
| REPLY-06 | Phase 187 | Pending |
| REPLY-07 | Phase 187 | Pending |

**Coverage:**

- v1 requirements: 28 total
- Mapped to phases: 28
- Unmapped: 0 ✓

---
*Requirements defined: 2026-09-10*
*Last updated: 2026-09-10 after milestone activation*

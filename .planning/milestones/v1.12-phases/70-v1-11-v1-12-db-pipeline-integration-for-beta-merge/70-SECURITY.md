# SECURITY.md — Phase 70: v1.11/v1.12 DB-Pipeline Integration for Beta Merge

**Audited:** 2026-06-16
**Auditor:** gsd-security-auditor (adversarial verification)
**ASVS Level:** 1
**block_on:** high
**Hardware risk guarded:** driving 12V VPP onto a wrong physical pin (chip/shield destruction)

**Result:** SECURED — 13/13 threats closed (12 mitigate verified in code, 1 accept logged). `threats_open: 0`.

Both submodules confirmed on branch `beta` with the `v1.12-protocol-dispatch-hardening`
work merged (app HEAD `6b5480f`, fw HEAD `b71c6fd`). All verification commands run live
against the merged beta state.

---

## Threat Verification

| Threat ID | Category | Disposition | Status | Evidence (verified live) |
|-----------|----------|-------------|--------|--------------------------|
| T-70-01 | Tampering | mitigate | CLOSED | `tools/build_db.py:416-424` — sole `resolve_pinout_key(` call site passes `type_int=type_int, mem_size=mem_size`; signature at `:173-175` carries both params. No other call sites (grep). 14 SRAM chips not mis-routed. |
| T-70-02 | Information Disclosure | mitigate | CLOSED | Live: `interpret_timing('64',0x07)=='100 us'` (not 10000); `VCC_VOLTAGES[0x02]=='4V'`, `[0x03]=='4.5V'`; `tools/build_db.py:657,662` use `voltages & 0xF0` (BUG-B); vcc/vdd bit positions `(voltages>>8)&0x0F` / `(voltages>>12)&0x0F` at `:668,671` (BUG-3). DB: SST27VF512 `vpp_mv=12000`. |
| T-70-03 | Elevation of Privilege | mitigate | CLOSED (defense on host layer; gate-layer hollowness = accepted tech debt) | Authoritative control: `firestarter/chip_resolver.py:55-57` raises `ChipNotImplementedError` for any `support_status != "supported"` BEFORE `convert_to_programmer` (`:60`) builds any wire dict. Live test: all 14 non-supported chips (9 adapter-required/algo=0x0D, 4 vpp-exceeds-max/algo=0x00, 1 protocol-not-implemented/algo=0x34) refused, 0 leaked. Site B/C set the sentinel in `build_db.py`, but Step 4 (`:468-476`) re-promotes the 9 adapter-required chips to 0x0D — see Accepted Risk AR-1. |
| T-70-04 | Elevation of Privilege | mitigate | CLOSED | `python tools/check_dispatch.py` exits 0: "PASS: 744 chips; 730 supported; 14 non-dispatchable; 0 non_supported_dispatchable; 0 dispatch regressions". The runtime authority is the host guard (above), confirmed live for all 14 chips. GATE-03 `non_supported_dispatchable` detector is hollow (never appended — `check_dispatch.py:237-243` comments admit it) — see AR-1. |
| T-70-05 | Tampering | mitigate | CLOSED | Structural no-vpp-pin guard restored from beta and live: `_build_no_vpp_pin_set` (`check_dispatch.py:122`), `PINOUTS_FILE` (`:30`), `no_vpp_pin_pinouts` (`:143`), `novpp_in_eprom` bucket (`:155`), per-chip guard `if handler=="configure_eprom" and pinout in no_vpp_pin_pinouts` (`:290`), FAIL block (`:353`). GATE-03 reports `0 novpp_in_eprom`. This bucket IS genuinely populated (unlike `non_supported_dispatchable`). |
| T-70-06 | Tampering | mitigate | CLOSED | Stage-a diff vs pre-merge v1.11 beta DB (parent `e910e5e`, 743 chips): `FIRESTARTER_BASELINE_FILE=... python tools/diff_db.py` exits 0, "all 743 changed chips explained; 0 UNEXPLAINED". SST27VF512 `vpp_mv=12000` confirmed in DB. |
| T-70-07 | Repudiation | mitigate | CLOSED | `tools/diff_db.py` carries `BUG_A_ETYPE` (`:89,203,320`), `BUG_B_VPP` (`:98,206,328`), `RULE_PHASE66` (`:109,215,339`) placed LAST per Pitfall 7 (`:213-214`). Stage-a 0 UNEXPLAINED; stage-b identity diff vs refreshed 744-chip baseline = 0 changes, exit 0. |
| T-70-08 | Tampering | mitigate | CLOSED | `tests/test_audit_coverage_matrix.py:389,413` assert chip count 744; `tests/golden/v1.3-COVERAGE-MATRIX.md:13,100` cite 744. `pytest tests/`: 29 snapshots pass. The stage-a diff (T-70-06) independently proves every changed field is rule-attributed (no hidden decode regression masked by the snapshot). |
| T-70-09 | Repudiation | mitigate | CLOSED | mypy watermark `29` in `pyproject.toml:115` (not regressed below 29); `python tools/check_mypy_watermark.py` → "29 errors / 29 watermark — OK", exit 0. CI-scoped `ruff check firestarter/ tests/` → "All checks passed!"; `ruff format --check firestarter/ tests/` → "59 files already formatted". Coverage 76.27% >= 70% floor. No blanket ignores / skips / config relaxation. |
| T-70-10 | Spoofing | mitigate | CLOSED | `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED == 0xBB` in firmware `firestarter/include/messages.h:96` AND host `firestarter_app/firestarter/messages.py:111`. `MSG_ERR_NOT_SUPPORTED == 0xA5` matches both sides (`messages.h:74` / `messages.py:89`). FW handler `src/proms/not_implemented.cpp:17` emits the constant. |
| T-70-11 | Tampering | mitigate | CLOSED | On beta HEAD post-merge: `check_dispatch.py` exits 0 (GATE-03 green); full CI gate (ruff/format/watermark/pytest+cov) green; DB has 744 chips; guess tables absent (`grep -v '^#' build_db.py` for DIP28_VARIANT_MAP/PIN_MAP_* → none). DB regenerated, not hand-merged. |
| T-70-12 | Elevation of Privilege | mitigate | CLOSED | No tag at HEAD in either repo: app `git describe` = `3.0.0b8-78-g6b5480f` (78 commits past last tag); fw = `3.0.0b7-32-gb71c6fd` (32 past last tag); `git tag --points-at HEAD` empty both repos. No version bump / release. Operator beta-cut gate intact (D-07). |
| T-70-SC | Tampering | accept | CLOSED | No new packages introduced this phase (pure code re-port + DB regen). See Accepted Risks AR-2. |

---

## Accepted Risks Log

### AR-1 — GATE-03 inverse-guard (`non_supported_dispatchable`) is hollow; Site B sentinel re-promoted by Step 4 (CR-01 / WR-01)

**Disposition:** ACCEPTED AS TECH DEBT by operator (2026-06-16, recorded in 70-VERIFICATION.md
`human_disposition` and 70-HUMAN-UAT.md).

**Finding (confirmed live by this audit):**
- `check_dispatch.py` declares `non_supported_dispatchable = []` (`:167`) but never appends to it;
  the comments at `:237-243` explicitly state it "remains empty under the current DB". The
  gate-failure branch (`:387`) and assertions (`:411,422`) can therefore never fire — the
  GATE-03 "D-03 HARD inverse guard" is non-functional as a future-regression detector.
- `build_db.py` Site B (`:409-411`) demotes the 9 adapter-required 24-pin EEPROMs to
  `NON_DISPATCHABLE_ALGO` (0x00), but Step 4 (`:468-476`) re-promotes every `DIP24_2816` chip
  to `0x0D` (`configure_eeprom28c`). Verified live: all 9 adapter-required chips ship
  `algorithm=13` (0x0D), contradicting the in-code invariant comment.

**Why accepted (not a live hazard):** The authoritative safety control is the host guard
`chip_resolver.resolve_chip` (`:55-57`), which refuses every `support_status != "supported"`
chip BEFORE any wire dict is built. This audit independently confirmed all 14 non-supported
chips raise `ChipNotImplementedError` with zero leakage. Additionally `0x0D` is the 5V no-VPP
handler (`configure_eeprom28c`), so even the re-promoted algorithm is not a 12V path; and the
structural `novpp_in_eprom` guard (genuinely populated) reports 0. Defense rests on the host
layer; the gate-layer enforcement is hollow but redundant.

**Residual risk:** False assurance — a *future* regression where a chip gains a real handler
while losing its non-supported tag would not be caught by GATE-03. Suggested closure (deferred):
populate `non_supported_dispatchable` by cross-checking `resolve_chip` per non-supported chip,
and re-assert the sentinel after Step 4 for non-supported chips.

### AR-2 — T-70-SC: no new package dependencies this phase

Pure code re-port and DB regeneration. `pip install -e '.[test]'` only restores the existing
pinned toolchain; firmware build uses pinned PlatformIO. No npm/pip/cargo additions. No new
trust boundary introduced (RESEARCH Package Legitimacy Audit).

---

## Related (non-blocking) review findings outside the threat register

These are documented in 70-REVIEW.md as warnings/info, are NOT declared threats, and do not
constitute a 12V-to-wrong-pin hazard given the host guard. Logged here for traceability only:

- **WR-02** — unguarded `int(None,16)` in `build_db.py:329-333` (build-time crash surface on
  malformed upstream XML; availability, not a wire-hazard).
- **WR-03** — `diff_db.py` does not fail on unexpected NEW chips (only WARN); the X88C64P new
  chip surfaces as a WARN line. Latent given pinned baseline.
- **WR-04** — `vpp-exceeds-max` chips still publish `vpp_mv=25000` in the DB; refused by host
  guard before serialization, so latent only.
- **WR-05** — combined INTEL `2732,2732A,M2732,M2732A` entry blocks the programmable 21V M2732A
  via highest-VPP-wins (known upstream-data trade-off).

---

## Unregistered Flags

None. No SUMMARY contains a `## Threat Flags` section; all four `## Threat Surface Scan`
sections report "no new security-relevant surface introduced" and map every change to an
existing T-70-xx threat ID. No new attack surface appeared during implementation without a
threat mapping.

---

## Verdict

All 13 declared threats resolve to CLOSED. The phase's central safety claim — zero
12V-to-wrong-pin hazard — is upheld by a real, present, enforced control (the host guard in
`chip_resolver.resolve_chip`), verified live against all 14 non-supported chips. The gate-layer
weakness (CR-01/WR-01) is a documented, operator-accepted false-assurance defect with no live
hardware hazard, recorded as AR-1. **threats_open: 0. Phase may ship.**

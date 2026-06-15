# SECURITY.md — Phase 66: db-inclusion-vpp-correction-dispatch-gate

**Audit date:** 2026-06-15
**ASVS Level:** L1
**block_on:** high
**Result:** SECURED — all declared threats CLOSED (18/18 across 5 plans)
**Scope:** `firestarter_app/` submodule (host CLI + build tooling). Firmware untouched.

This phase closes a real physical/electrical hazard: a non-supported chip whose
`algorithm` resolved to a real firmware handler would engage the 12V VPP boost
regulator and drive ~12V onto a pin of a 5V part (e.g. the WE pin of a 24-pin 5V
EEPROM, or a 25V NMOS UV-EPROM exceeding the RURP ceiling) → hardware/chip damage.
The host-side defense-in-depth is verified present below.

Note: threat IDs T-66-01/02/03 are REUSED across Plan 01 and Plan 05 with different
meanings; they are disambiguated by plan suffix.

---

## Threat Verification

| Threat ID | Plan | Category | Disposition | Status | Evidence |
|-----------|------|----------|-------------|--------|----------|
| T-66-01 | 01 | Tampering | mitigate | CLOSED | Baseline byte-exact to committed DB at pin commit `a70d098` (734 chips). Verified: `git show a70d098:tools/baseline/chip_database.baseline.json == git show a70d098~1:firestarter/data/chip_database.json` → True. |
| T-66-02 | 01 | Repudiation | mitigate | CLOSED | `tools/diff_db.py:89-99` RULE_PHASE66 rationale embeds `[VERIFIED: ...66-CONTEXT.md D-04/D-06/D-07]`; diff_db.py run attributes all 730 Phase-66 chips + 4 RULE_ALGO compound to a rule (exit 0). |
| T-66-SC | 01 | Tampering (installs) | mitigate | CLOSED | `git log` over phase-66 commits: zero changes to pyproject/setup/requirements; baseline pin via cherry-pick `a70d098` (git-internal restore). |
| T-66-03 | 02 | Tampering | mitigate | CLOSED | `tools/check_dispatch.py:223-238` — both `errors.append` and `not_implemented.append` guarded by `chip_ss == "supported"`; both in `sys.exit(1)` condition (L269-348). A `supported` chip with no handler still FAILs loudly; non-supported chips are the only relaxation (safe direction). |
| T-66-04 | 02 | Information Disclosure | ACCEPT | CLOSED | Host-only build tooling; no PII/secrets/network. Accepted-risk entry logged below. |
| T-66-05 | 02 | Tampering (mirror drift) | mitigate | CLOSED | `tools/check_dispatch.py:67-72` source-of-truth comment cites build_db.py; assertion 2 (`pni_with_known_proto`, L186-189) catches a protocol-not-implemented chip whose proto drifts into KNOWN_PROTOCOLS. |
| T-66-06 | 03 | Tampering (untrusted infoic.xml) | mitigate | CLOSED | `tools/build_db.py:563-586` Site C "highest-VPP-wins" + `RURP_VPP_CEILING_MV=22000` (L93): true VPP > ceiling → `vpp-exceeds-max` + proto demoted to 0x00. No new parsing surface; ambiguous high-VPP refused, never silently programmable. |
| T-66-07 | 03 | Elevation of Privilege | mitigate | CLOSED | Live DB: 9 adapter-required chips; **0** route to `configure_eeprom28c` (or any real handler) — verified via dispatch() one-liner. D-03 HARD honored. |
| T-66-08 | 03 | Tampering (false-green baseline) | mitigate | CLOSED | `tools/diff_db.py` exit 0: every change attributed (RULE_ALGO ×4 compound, RULE_PHASE66 ×730, 10 new WARN-only); 0 unexplained, 0 D-03 BLOCK; independent re-derivation vs pinned baseline. |
| T-66-09 | 03 | Tampering (py3.12 masks py3.11) | mitigate | CLOSED | DB regen + gates produce version-neutral JSON; gate tools functionally equivalent; documented decision (py3.11 binary absent after devcontainer reset). See note below. |
| T-66-SC | 03 | Tampering (installs) | mitigate | CLOSED | No dependency-file changes in any phase-66 commit. |
| T-66-10 | 04 | Elevation of Privilege | mitigate | CLOSED | `tools/build_db.py:122` `NON_DISPATCHABLE_ALGO=0x00`; demotion at Site B (L442) + Site C (L584). Live DB: 14 non-supported chips → 13×algo=0x00 (dispatch ERROR) + 1×0x34 (dispatch not_implemented); **0** resolve to a real handler. |
| T-66-11 | 04 | Tampering (false-PASS) | mitigate | CLOSED | `tools/check_dispatch.py:143,277,336-347` non_supported_dispatchable bucket in sys.exit(1) condition + FAIL block; truthful PASS line (L365-375) prints live count + WR-02/WR-03 asserts (L354-363). Gate exits 0. |
| T-66-12 | 04 | Tampering (future regression) | mitigate | CLOSED | `tests/test_build_db_inclusion.py:329` TestNonSupportedNonDispatchable models real `_map_data` mem_type derivation + D-12 host-guard exemption. Test passes. (See finding INFO-1.) |
| T-66-13 | 04 | Tampering (false-green baseline) | mitigate | CLOSED | dispatch_baseline.json regenerated (D-11 authorized); diff_db.py re-derives proto_id→0 as RULE_ALGO+RULE_PHASE66; exit 0. |
| T-66-SC | 04 | Tampering (installs) | mitigate | CLOSED | No dependency-file changes. |
| T-66-01 | 05 | Tampering (electrical/physical) | mitigate | CLOSED | **Load-bearing.** `firestarter/chip_resolver.py:54-57` raises ChipNotImplementedError when `support_status != "supported"`, BEFORE `convert_to_programmer`. Proven by `tests/test_chip_resolver.py:105-115`: M2716 (vpp-exceeds-max, 25V) raises and `convert_to_programmer.assert_not_called()` — no wire dict, no serial byte. AT28C04 (adapter-required) also raises (L77-85). |
| T-66-02 | 05 | Repudiation/false assurance | mitigate | CLOSED | `tools/check_dispatch.py:163-173` mirrors `_map_data` real mem_type derivation (etype fallback for proto==0); PASS prints live non_supported_dispatchable count + `assert non_dispatchable_count == non_supported_count` (L354). |
| T-66-03 | 05 | Elevation (future regression) | mitigate | CLOSED | Realigned gate + 8th CI test model the real production path with host-guard exemption (check_dispatch.py:190-221; test L329-384). chip_resolver guard is the authoritative refuse-point; test_chip_resolver runtime-boundary tests pin it. |
| T-66-SC | 05 | Tampering (installs) | ACCEPT | CLOSED | No installs. Accepted-risk entry logged below. |

---

## Accepted Risks Log

- **T-66-04 (Plan 02) — Information Disclosure [ACCEPT]:** `build_db.py` /
  `check_dispatch.py` / `diff_db.py` are host-only build tooling. No PII, no
  secrets, no network I/O, no credential handling. Input is the bundled
  `infoic.xml` (public minipro chip database). Accepted: out-of-band data
  exposure is not in scope for offline DB-build tooling.
- **T-66-SC (Plan 05) — Tampering via installs [ACCEPT]:** No package installs in
  any phase-66 commit (verified across all 13 commits). The diff_db.py
  introduction (Plan 01) is a git-internal cherry-pick, not an external dependency.

---

## Notes

- **T-66-09 (py3.12-masks-py3.11):** The DB was regenerated under Python 3.12
  because the py3.11 binary was unavailable after a devcontainer reset (built from
  source in Phase 63, lost on reset). `chip_database.json` output is version-neutral
  JSON; all gate tools run identically under 3.12; ruff/format checks were clean.
  This is a tooling-environment deviation documented at plan time, not an unmitigated
  threat. Recommendation: when py3.11 is restored, re-run `check_dispatch.py` +
  `diff_db.py` + the inclusion test suite on the CI-target interpreter to fully
  retire the residual drift concern.

- **INFO-1 (non-blocking, internal-consistency observation on T-66-12):** The 8th
  CI test (`test_non_supported_chips_are_non_dispatchable`,
  `tests/test_build_db_inclusion.py:329`) `continue`s the loop when
  `ss == "supported"`, then its violation predicate is
  `handler not in (...) AND ss == "supported"` — which can never be true inside the
  loop body. The test therefore cannot fail on the current DB shape; it documents
  the invariant rather than empirically exercising the regression case. This is NOT
  a missing mitigation: the load-bearing runtime guard (T-66-01 Plan 05) is proven
  by `tests/test_chip_resolver.py` (M2716/AT28C04 raise + convert_to_programmer
  asserted not-called), and the live `check_dispatch.py` gate independently FAILs on
  any `supported` chip that loses its handler (errors / not_implemented buckets,
  L223-238). The CI-test predicate is redundant-but-harmless; consider tightening it
  in a future phase to assert directly on the live `dispatch()` outcome of each
  non-supported chip (proto demotion → ERROR/not_implemented) so the test fails if a
  future build_db.py change re-routes one to a real handler.

---

## Unregistered Flags

None. All SUMMARY `## Threat Flags` sections (Plans 01, 03, 04, 05) report "None"
and map every flag to a registered threat ID. Plan 02 uses a `## Threat Model
Review` section (T-66-03/05 dispositions) in lieu of `## Threat Flags`; both
disposed threats are registered and CLOSED above. No new attack surface appeared
during implementation without a threat mapping.

---

## Gate Results (read-only verification, this audit)

| Gate | Command | Result |
|------|---------|--------|
| Dispatch safety | `python3 tools/check_dispatch.py` | PASS (exit 0): 730 supported; 14 non-dispatchable; 0 non_supported_dispatchable; 0 regressions |
| Per-chip diff | `python3 tools/diff_db.py` | PASS (exit 0): 734 changed explained; 10 new; 0 unexplained; RULE_PHASE66 citation present |
| Inclusion + SC#3 invariant | `pytest tests/test_build_db_inclusion.py` | PASS |
| Runtime boundary guard | `pytest tests/test_chip_resolver.py` | PASS (M2716/AT28C04 raise; convert_to_programmer not called) |
| Non-supported → real handler | dispatch() one-liner over live DB | 0 of 14 reach a real handler |

---

## Security Audit 2026-06-15 (re-verification)

State-A re-audit: register re-derived from all 5 PLAN `<threat_model>` blocks
(`register_authored_at_plan_time: true`) and cross-checked against every SUMMARY
`## Threat Flags` / `## Threat Model Review` section (all "None", every flag mapped
to a registered ID). Mitigations independently re-verified in code, not trusted from
the prior pass.

| Metric | Count |
|--------|-------|
| Threats found | 18 |
| Closed | 18 |
| Open | 0 |

Read-only gate re-run (this audit):

| Gate | Command | Result |
|------|---------|--------|
| Dispatch safety | `python3 tools/check_dispatch.py` | PASS (exit 0): 744 scanned; 730 supported; 14 non-dispatchable; 0 non_supported_dispatchable; 0 regressions |
| Per-chip diff | `python3 tools/diff_db.py` | PASS (exit 0): 734 changed explained; 10 new; 0 unexplained |
| Inclusion + runtime guard | `pytest tests/test_build_db_inclusion.py tests/test_chip_resolver.py` | PASS (17/17) |
| Load-bearing host guard | `chip_resolver.py:54-57` raises ChipNotImplementedError before `convert_to_programmer` | PRESENT |
| Demotion sites | `build_db.py:442` (Site B) + `:584` (Site C) `proto_id = NON_DISPATCHABLE_ALGO` | PRESENT |
| Non-supported → real handler | live DB: 14 non-supported chips | 0 reach a real handler |

`threats_open: 0` — short-circuit honored (register authored at plan time, all CLOSED).
No new attack surface; no disposition changes. Residual T-66-09 py3.11 recommendation
unchanged (see Notes).

---

*Phase: 66-db-inclusion-vpp-correction-dispatch-gate*

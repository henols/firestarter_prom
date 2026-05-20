---
phase: 18
slug: beta-aware-firmware-downloader
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-20
---

# Phase 18 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution. Derived from RESEARCH.md §Validation Architecture (lines 861-897).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest ≥7.0 (already in `firestarter_app/pyproject.toml` dev deps) |
| **Config file** | `firestarter_app/pyproject.toml` — `[tool.pytest.ini_options]` testpaths=["tests"] |
| **Quick run command** | `cd firestarter_app && pytest tests/test_firmware_install.py -x -q` |
| **Full suite command** | `cd firestarter_app && pytest tests/ -q` |
| **Estimated runtime** | ~2-3 seconds (pure-Python; all network mocked via monkeypatch) |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_firmware_install.py -x -q` (~3s)
- **After every plan wave:** Run `pytest tests/ -q` (full suite — preserves regression coverage against the Phase 15 `test_update_version.py` + Phase 6 `test_fwguard.py` + the existing 47-test baseline)
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

> Task IDs are placeholders (`TBD-*`) — populated by planner. Below is the requirement→test-type mapping pre-derived from RESEARCH.md.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD-scaffold | wave0 | 0 | INST-01..04 | — | Failing-test scaffold so Wave 1 has a measurable target | unit | `cd firestarter_app && pytest tests/test_firmware_install.py -v --collect-only` | ❌ W0 | ⬜ pending |
| TBD-stable | wave1 | 1 | INST-01 | T-15-02-05 derivative | Bare `fw -i` on stable-installed app continues to hit `/releases/latest` byte-identically | unit | `cd firestarter_app && pytest tests/test_firmware_install.py::TestFirmwareInstallStable -x` | ❌ W0 | ⬜ pending |
| TBD-comparator | wave1 | 1 | INST-01 | — | `_compare_versions` handles PEP 440 pre-release strings via `packaging.version.Version`; never raises ValueError on `3.1.0b1` / `3.1.0rc2` / `2.0.7_dev` | unit | `cd firestarter_app && pytest tests/test_firmware_install.py::TestVersionComparator -x` | ❌ W0 | ⬜ pending |
| TBD-pre | wave1 | 1 | INST-02 | — | `--pre` enumerates `/releases`, filters `prerelease: true`, sorts by PEP 440, picks highest; falls back to stable when no prerelease exists | unit | `cd firestarter_app && pytest tests/test_firmware_install.py::TestFirmwareInstallPreRelease -x` | ❌ W0 | ⬜ pending |
| TBD-magic | wave1 | 1 | INST-02 | — | Magic default: bare `fw -i` on beta-app install (`Version(__version__).is_prerelease == True`) auto-routes to `--pre` + logs INFO line; stable-app bare `fw -i` does NOT auto-route | unit | `cd firestarter_app && pytest tests/test_firmware_install.py::TestMagicDefault -x` | ❌ W0 | ⬜ pending |
| TBD-pinned | wave1 | 1 | INST-03 | Input-validation (V5) | `--firmware-version` validates against `FIRMWARE_VERSION_RE` BEFORE network call; invalid input exits non-zero with no network; valid input fetches `/releases/tags/{tag}` and errors fatally on 404 | unit | `cd firestarter_app && pytest tests/test_firmware_install.py::TestFirmwareInstallPinned -x` | ❌ W0 | ⬜ pending |
| TBD-list | wave1 | 1 | INST-04 | — | `fw --list` prints plain table with version/channel/published/asset columns; `--json` outputs equivalent JSON array; `--pre`/`--stable` filter by channel; default `--all` | unit | `cd firestarter_app && pytest tests/test_firmware_install.py::TestFirmwareList -x` | ❌ W0 | ⬜ pending |
| TBD-mutex | wave1 | 1 | INST-02, INST-03 | Input-validation (V5) | argparse mutex groups reject `--pre + --firmware-version` and `--list + -i/--install` with non-zero exit | unit | `cd firestarter_app && pytest tests/test_firmware_install.py::TestArgparseMutex -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter_app/tests/test_firmware_install.py` — covers INST-01..04 + TestVersionComparator + TestMagicDefault + TestArgparseMutex (8 classes, ≥15 test methods). All tests fail RED on Wave-0 commit because the new `FirmwareManager.fetch_release_info` + `list_releases` methods + the new argparse flags don't exist yet.
- [ ] `mock_releases_factory` helper (local to `test_firmware_install.py`, not `conftest.py`) — builds paginated GitHub API response mocks with configurable release list, asset names per board, and `prerelease: true/false` flags.
- [ ] No new entries in `firestarter_app/tests/conftest.py` — fixture is module-local per RESEARCH note line 897.

*No new infrastructure beyond the single test file + module-local factory. `packaging` becomes a runtime dep in Wave 1 (Plan 18-02 modifies pyproject.toml).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real-network `fw --list` against henols/firestarter | INST-04 | Wave 1 mocks the GitHub API; the real-network call is exercised end-to-end in Phase 20 E2E-01. A manual smoke can be run during Phase 18 close to confirm the mocked shape matches reality | (1) `cd firestarter_app && pip install -e .`; (2) `firestarter fw --list --all` (with internet); (3) verify the table has at least one current stable release + 0 or more pre-releases. Operator runs this once at Phase 18 close as a sanity check; Phase 20 E2E-01 (e) makes this automated with a real fresh beta. |

*All Phase 18 behaviors have automated verification via mocked GitHub responses. The single manual check is a paranoia step at phase close.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (test file + module-local mock factory)
- [ ] No watch-mode flags (single-shot pytest runs only)
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

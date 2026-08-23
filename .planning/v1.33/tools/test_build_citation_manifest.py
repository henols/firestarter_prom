#!/usr/bin/env python3
r"""
Unit tests for the v1.33 citation-manifest toolchain (Phase 154 plan 04).

Two modules under test, both siblings of this file:

  * `citation_paths.py`      -- the shared five-step path-resolution rule
                               (SWEEP-09, D-09, research F5). Imported by BOTH
                               `build_citation_manifest.py` (this plan) and
                               `remap_citations.py` (plan 05), so the same
                               citation cannot resolve two different ways.
  * `build_citation_manifest.py` -- the pre-sweep manifest generator
                               (SWEEP-09, D-07, Ruling F).

Enumerated legs, each with the exit code or outcome it pins and the
requirement it discharges (the enumerated-docstring shape is copied from
`.planning/v1.16/ledger/tools/test_check_ledger.py`, the house analog):

  RESOLVE LEGS (task 1 -- citation_paths.py, D-09 / research F5)
   1. test_resolve_exact_repo_relative_path            -> "exact"
   2. test_resolve_unique_path_suffix                  -> "suffix"
   3. test_resolve_suffix_tie_is_broken_by_fixture_exclusion -> "suffix"
   4. test_resolve_bare_basename_skips_planted_fixture -> "basename", not a fixture
   5. test_resolve_firestarter_h_is_not_the_fake_fixture -> the name-collision trap
   6. test_resolve_host_stubs_is_ambiguous             -> "ambiguous", no path
   7. test_resolve_database_c_is_unresolved            -> "unresolved", no path
   8. test_resolve_parent_traversal_is_rejected        -> "rejected", recorded
   9. test_resolve_absolute_path_is_rejected           -> "rejected", recorded
  10. test_fixture_guard_raises_on_fixtures_inclusive_index -> raises (T-154-13)
  11. test_resolve_fixture_only_basename_falls_back    -> "basename" via fallback
  12. test_declared_fixture_exclusion_globs_are_present -> source assertion
  13. test_citation_paths_module_has_no_here_derived_root -> source assertion (D-09)

  GENERATOR LEGS (task 2 -- build_citation_manifest.py, SWEEP-09 / D-07)
  14. test_variant_colon_single_is_extracted
  15. test_variant_colon_range_is_extracted
  16. test_variant_colon_list_yields_two_independent_records
  17. test_variant_anchor_L_point_and_range_are_extracted
  18. test_backticked_wrapper_is_not_a_fifth_variant
  19. test_range_record_carries_both_endpoints_and_both_texts (REMAP-03)
  20. test_every_record_is_retarget_false                (D-08 pre-sweep)
  21. test_regeneration_is_byte_identical                (idempotence)
  22. test_zero_record_input_exits_two                   -> exit 2 (fail closed)
  23. test_header_record_is_first_and_self_describing
  24. test_generator_module_has_no_here_derived_root     -> source assertion (D-09)
  25. test_generator_imports_the_shared_resolver         -> source assertion
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

# `_HERE` is CORRECT in a test -- the D-09 ban is on the TOOL deriving its scan
# root from its own location, not on a test locating its own siblings. Same
# reading as `test_check_ledger.py`, the house analog.
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import citation_paths  # noqa: E402

_CITATION_PATHS_SRC = os.path.join(_HERE, "citation_paths.py")
_GENERATOR = os.path.join(_HERE, "build_citation_manifest.py")


# ---------------------------------------------------------------------------
# Synthetic candidate set. It DELIBERATELY includes the firmware-repo planted
# fixture copies that the real candidate set does not contain (the firmware
# repo's `tests/` -- plural -- is outside the sweep globs, so its fixtures
# never enter the real candidate set). Putting them in here is what makes the
# fixture-exclusion rule testable at all: on the real tree the rule is
# defence in depth, and a test that only used the real set would prove
# nothing about it.
# ---------------------------------------------------------------------------
_SYNTHETIC_CANDIDATES = [
    "firestarter/src/proms/eeprom_28c.cpp",
    "firestarter/src/firestarter.cpp",
    "firestarter/include/firestarter.h",
    "firestarter/src/boards/uno_rurp_shield.cpp",
    "firestarter/test/native/avr/test_a/host_stubs.cpp",
    "firestarter/test/native/avr/test_b/host_stubs.cpp",
    "firestarter/tests/fixtures/planted_cmake_manifest_missing_source/src/proms/eeprom_28c.cpp",
    "firestarter/tests/fixtures/planted_cmake_manifest_extra/src/firestarter.cpp",
    "firestarter_app/tests/fixtures/fake_firestarter/include/firestarter.h",
    "firestarter_app/tests/fixtures/planted_log_in_window.cpp",
    "firestarter_app/firestarter/database.py",
]


@pytest.fixture()
def roots(tmp_path):
    """Two explicit root directories -- never derived from __file__ by the tool."""
    fw = tmp_path / "firestarter"
    app = tmp_path / "firestarter_app"
    fw.mkdir()
    app.mkdir()
    return {"firestarter": fw, "firestarter_app": app}


@pytest.fixture()
def index(roots):
    return citation_paths.CandidateIndex(roots, _SYNTHETIC_CANDIDATES)


# ---------------------------------------------------------------------------
# 1-13: the resolve legs
# ---------------------------------------------------------------------------

def test_resolve_exact_repo_relative_path(index):
    r = index.resolve("firestarter/src/proms/eeprom_28c.cpp")
    assert r.resolution == citation_paths.EXACT
    assert r.path == "firestarter/src/proms/eeprom_28c.cpp"


def test_resolve_unique_path_suffix(index):
    r = index.resolve("src/boards/uno_rurp_shield.cpp")
    assert r.resolution == citation_paths.SUFFIX
    assert r.path == "firestarter/src/boards/uno_rurp_shield.cpp"


def test_resolve_suffix_tie_is_broken_by_fixture_exclusion(index):
    # `src/proms/eeprom_28c.cpp` is a suffix of BOTH the real firmware file and
    # the planted-CMake-manifest fixture copy. The tie must break toward the
    # real file, never toward the fixture.
    r = index.resolve("src/proms/eeprom_28c.cpp")
    assert r.resolution == citation_paths.SUFFIX
    assert r.path == "firestarter/src/proms/eeprom_28c.cpp"
    assert "fixtures/" not in r.path


def test_resolve_bare_basename_skips_planted_fixture(index):
    r = index.resolve("eeprom_28c.cpp")
    assert r.resolution == citation_paths.BASENAME
    assert r.path == "firestarter/src/proms/eeprom_28c.cpp"
    assert "fixtures/" not in r.path


def test_resolve_firestarter_h_is_not_the_fake_fixture(index):
    # The `firestarter` name-collision trap in citation form: the app's own
    # fixture tree carries an include/firestarter.h.
    r = index.resolve("firestarter.h")
    assert r.resolution == citation_paths.BASENAME
    assert r.path == "firestarter/include/firestarter.h"
    assert "fake_firestarter" not in r.path


def test_resolve_host_stubs_is_ambiguous(index):
    r = index.resolve("host_stubs.cpp")
    assert r.resolution == citation_paths.AMBIGUOUS
    assert r.path is None
    assert len(r.candidates) == 2


def test_resolve_database_c_is_unresolved(index):
    # infoic's external decompiled source -- out of repo by design.
    r = index.resolve("database.c")
    assert r.resolution == citation_paths.UNRESOLVED
    assert r.path is None


def test_resolve_parent_traversal_is_rejected(index):
    r = index.resolve("../firestarter/include/rurp_shield.h")
    assert r.resolution == citation_paths.REJECTED
    assert r.path is None
    assert r.reason  # the rejection is RECORDED, not raised


def test_resolve_absolute_path_is_rejected(index):
    r = index.resolve("/workspaces/firestarter/src/firestarter.cpp")
    assert r.resolution == citation_paths.REJECTED
    assert r.path is None
    assert r.reason


def test_fixture_guard_raises_on_fixtures_inclusive_index(roots):
    # T-154-13: a resolution onto a planted-fixture copy would round-trip green
    # against the WRONG file. Feeding a deliberately fixtures-INCLUSIVE index
    # must raise, because such a result is a bug and not a value.
    bad = citation_paths.CandidateIndex(
        roots,
        [
            "firestarter/tests/fixtures/planted_cmake_manifest_missing_source/src/proms/eeprom_28c.cpp",
        ],
        _exclude_fixtures=False,
    )
    with pytest.raises(citation_paths.FixtureResolutionError):
        bad.resolve("eeprom_28c.cpp")


def test_resolve_fixture_only_basename_falls_back(index):
    # A citation whose target genuinely IS a fixture file resolves, via the
    # explicitly-labelled fixture-inclusive fallback, rather than being lost as
    # a false `unresolved`.
    r = index.resolve("planted_log_in_window.cpp")
    assert r.resolution == citation_paths.BASENAME
    assert r.path == "firestarter_app/tests/fixtures/planted_log_in_window.cpp"
    assert "fallback" in r.reason


def test_declared_fixture_exclusion_globs_are_present():
    src = open(_CITATION_PATHS_SRC, encoding="utf-8").read()
    assert "**/fixtures/**" in src
    assert "**/fixture/**" in src


def test_citation_paths_module_has_no_here_derived_root():
    src = open(_CITATION_PATHS_SRC, encoding="utf-8").read()
    assert "_HERE" not in src

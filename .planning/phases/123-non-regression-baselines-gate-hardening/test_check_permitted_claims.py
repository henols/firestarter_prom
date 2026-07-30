"""Tests for check_permitted_claims.py (Phase 123 Plan 10, v1.23 adaptation
of Phase 122's BASE-07 checker).

This is the MANDATORY anti-hollow pairing for the v1.23 claim gate (BASE-07):
a checker with no negative-fixture test is exactly this project's v1.12
hollow-GATE-03 failure mode -- a declared-empty detector that could never
fail because nothing concrete was asserted against it. Every planted-
violation test below invokes the checker as a real subprocess against a
committed fixture file via the FIRESTARTER_CLAIMSCAN_TARGETS env seam --
never an in-process import -- so a passing test suite proves the checker
itself (not the test) fails the build on a real violation. The scanner is
never imported directly in this module.

Coverage:
  1. Clean-pass baseline via the seam: exits 0, PASS: in stdout.
  2. Planted py32 overclaim (planted_py32_overclaim.md) flips the checker
     to a non-zero exit with FAIL: and the bench-validated label named.
  3. D-16 negative direction: clean_avr_bench_control.md exits 0 despite
     containing bench-validated, because no py32 token is in its proximity
     window. Has no v1.22 analogue -- proves D-16 rather than asserting it.
  4. D-16 proximity is real, not accidental: inserting a py32 token
     adjacent to the same bench-validated line makes the run FAIL, proving
     test 3 passed because scoping suppressed the match, not because the
     pattern never matched at all.
  5. Planted missing-caveat violation (planted_missing_caveat.md) flips the
     checker to a non-zero exit naming the missing-caveat bucket.
  6. Never-vacuous on an explicitly empty FIRESTARTER_CLAIMSCAN_TARGETS --
     asserts the specific message, not merely a non-zero exit.
  7. Fail-closed on a nonexistent scan target.
  8. D-15 arming, both directions: a copy of the checker in an isolated
     tmp_path reports UNARMED + exit 0 with zero of the four named
     artifacts present, then becomes armed and FAILS naming the three
     still-missing targets once exactly one is created -- entirely inside
     tmp_path, never touching the real Phase 130 directory.
  9. Positional argv overrides the env seam (documented precedence, pinned
     against a future silent inversion).
  10. PASS-line names both scanned files at once (anti-skip).
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).parent
_SCANNER = _HERE / "check_permitted_claims.py"


def _run_scanner(targets=None, argv=None):
    """Invoke the scanner as a real subprocess.

    `targets`, when not None, sets FIRESTARTER_CLAIMSCAN_TARGETS to that
    exact string (so the empty string is reachable, per test 6) -- when
    None, the env var is left absent from the child's environment entirely,
    reaching the "variable absent -> use real defaults" path.
    """
    env = {**os.environ}
    if targets is not None:
        env["FIRESTARTER_CLAIMSCAN_TARGETS"] = targets
    else:
        env.pop("FIRESTARTER_CLAIMSCAN_TARGETS", None)
    return subprocess.run(
        [sys.executable, str(_SCANNER), *(argv or [])],
        cwd=str(_HERE),
        capture_output=True,
        text=True,
        env=env,
    )


# ---------------------------------------------------------------------------
# Test 1: clean-pass baseline via the seam (also the seam-innocence control)
# ---------------------------------------------------------------------------


def test_scanner_exits_zero_on_clean_fixture():
    """A clean fixture injected via the env seam must exit 0 with PASS: --
    proves the seam itself introduces no false positive."""
    result = _run_scanner(targets="fixtures/clean_control.md")
    assert result.returncode == 0, (
        f"scanner exited {result.returncode} on a clean fixture.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout, (
        f"Expected 'PASS:' in output but got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Test 2: planted py32 overclaim (anti-hollow, D-16 positive direction)
# ---------------------------------------------------------------------------


def test_planted_py32_overclaim_flips_checker_to_failure():
    """The committed planted_py32_overclaim.md fixture MUST fail the gate,
    attributed to the bench-validated label -- a py32 token and the
    forbidden phrase co-occur on one line."""
    result = _run_scanner(targets="fixtures/planted_py32_overclaim.md")
    assert result.returncode != 0, (
        f"scanner exited 0 on a planted py32 overclaim.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout, (
        f"Expected 'FAIL:' in output but got:\n{result.stdout}"
    )
    assert "bench-validated" in result.stdout, (
        f"Expected the bench-validated label in output but got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Test 3: D-16 negative direction (no v1.22 analogue)
# ---------------------------------------------------------------------------


def test_d16_negative_direction_avr_bench_control_passes():
    """clean_avr_bench_control.md contains bench-validated and
    hardware-validated (true statements about AVR silicon) but must exit 0,
    because no py32 token is within the 3-line proximity window of either
    forbidden-phrase match. This is the test that makes D-16 proven rather
    than merely asserted, and it has no v1.22 analogue."""
    fixture_text = (_HERE / "fixtures" / "clean_avr_bench_control.md").read_text()
    assert "bench-validated" in fixture_text, (
        "fixture must actually contain the forbidden phrase for this test "
        "to prove suppression rather than mere absence"
    )
    result = _run_scanner(targets="fixtures/clean_avr_bench_control.md")
    assert result.returncode == 0, (
        f"scanner exited {result.returncode} on the D-16 negative-direction "
        f"control -- proximity scoping failed to suppress a true AVR "
        f"statement.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout


# ---------------------------------------------------------------------------
# Test 4: D-16 proximity is real, not accidental
# ---------------------------------------------------------------------------


def test_d16_proximity_suppression_is_real_not_accidental(tmp_path):
    """Copy clean_avr_bench_control.md and insert a line carrying a py32
    token immediately adjacent to the bench-validated line. Without this
    test, test 3 could pass merely because the bench-validated pattern
    never matches this fixture's text at all, rather than because
    proximity scoping actively suppressed a real match. This test proves
    suppression is real: moving a py32 token into the window makes the
    identical bench-validated text FAIL."""
    original = (_HERE / "fixtures" / "clean_avr_bench_control.md").read_text()
    lines = original.splitlines()
    bench_idx = next(i for i, line in enumerate(lines) if "bench-validated" in line)
    lines.insert(bench_idx, "The PY32F071 bring-up notes are inserted right here.")
    mutated = "\n".join(lines) + "\n"
    target = tmp_path / "mutated_avr_bench_control.md"
    target.write_text(mutated)

    result = _run_scanner(targets=str(target))
    assert result.returncode != 0, (
        "expected the mutated fixture (py32 token moved adjacent to the "
        "bench-validated line) to FAIL -- if it still passes, D-16's "
        "suppression in test 3 cannot be distinguished from the pattern "
        f"simply never matching.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert "bench-validated" in result.stdout, (
        f"Expected the bench-validated label in output but got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Test 5: planted missing-caveat violation
# ---------------------------------------------------------------------------


def test_planted_missing_caveat_flips_checker_to_failure():
    """The committed planted_missing_caveat.md fixture MUST fail the gate,
    naming the missing required-caveat bucket."""
    result = _run_scanner(targets="fixtures/planted_missing_caveat.md")
    assert result.returncode != 0, (
        f"scanner exited 0 on a planted missing-caveat violation.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert "missing required silicon caveat" in result.stdout, (
        f"Expected the missing-caveat bucket label in output but got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Test 6: never-vacuous on an explicitly empty target list
# ---------------------------------------------------------------------------


def test_never_vacuous_on_explicitly_empty_target_list():
    """FIRESTARTER_CLAIMSCAN_TARGETS explicitly set to the empty string MUST
    resolve to zero targets and exit non-zero -- and must NOT silently fall
    back to the real default targets (which do not exist yet at this wave,
    so a fall-back would ALSO exit 1, but for the wrong reason and without
    a PASS:; this test asserts the never-vacuous message specifically,
    isolating the correct failure mode from that coincidental one)."""
    result = _run_scanner(targets="")
    assert result.returncode != 0, (
        f"scanner exited 0 with an explicitly empty target list.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" not in result.stdout
    assert "no scan targets resolved" in result.stdout, (
        f"Expected the never-vacuous message in output but got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Test 7: fail-closed on a nonexistent scan target
# ---------------------------------------------------------------------------


def test_fail_closed_on_nonexistent_target():
    """A scan target that does not exist on disk MUST fail closed (exit
    non-zero), never vacuously pass with the target silently skipped."""
    result = _run_scanner(targets="fixtures/does-not-exist.md")
    assert result.returncode != 0, (
        f"scanner exited 0 with a missing scan target.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert "not found on disk" in result.stdout, (
        f"Expected a not-found message in output but got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Test 8: D-15 arming, both directions -- entirely inside tmp_path
# ---------------------------------------------------------------------------


def test_d15_arming_both_directions(tmp_path):
    """Mechanism: copy check_permitted_claims.py itself into tmp_path and
    run the COPY directly (no env seam, no argv) -- its `_HERE` then
    resolves to tmp_path, so `_DEFAULT_TARGETS` names
    tmp_path/130-{LEDGER,DECISION,RELEASE-NOTES-fw,RELEASE-NOTES-app}.md.
    This drives the real default-target-resolution and D-15 arming code
    path without ever creating a real 130-*.md file inside the actual
    Phase 130 directory (which does not exist yet and must not be created
    as a side effect of this test).

    Direction 1: zero of the four named artifacts exist in tmp_path ->
    UNARMED, exit 0 (the close has not started).
    Direction 2: create exactly one -> armed but incomplete -> exit
    non-zero, naming the three still-missing targets (a half-written close
    is a hard failure)."""
    scanner_copy = tmp_path / "check_permitted_claims.py"
    shutil.copy(_SCANNER, scanner_copy)

    env = {**os.environ}
    env.pop("FIRESTARTER_CLAIMSCAN_TARGETS", None)

    result_unarmed = subprocess.run(
        [sys.executable, str(scanner_copy)],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        env=env,
    )
    assert result_unarmed.returncode == 0, (
        f"expected UNARMED exit 0 with zero of the four named artifacts "
        f"present in the isolated tmp_path.\nstdout:\n{result_unarmed.stdout}\n"
        f"stderr:\n{result_unarmed.stderr}"
    )
    assert "UNARMED:" in result_unarmed.stdout, (
        f"Expected the UNARMED: notice in output but got:\n{result_unarmed.stdout}"
    )

    (tmp_path / "130-LEDGER.md").write_text("no PY32F071 hardware exists.\n")

    result_armed = subprocess.run(
        [sys.executable, str(scanner_copy)],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        env=env,
    )
    assert result_armed.returncode != 0, (
        f"expected the run to become armed-but-incomplete and FAIL once "
        f"exactly one of the four named artifacts exists.\n"
        f"stdout:\n{result_armed.stdout}\nstderr:\n{result_armed.stderr}"
    )
    assert "FAIL:" in result_armed.stdout
    for missing_name in (
        "130-DECISION.md",
        "130-RELEASE-NOTES-fw.md",
        "130-RELEASE-NOTES-app.md",
    ):
        assert missing_name in result_armed.stdout, (
            f"Expected {missing_name!r} named among the still-missing "
            f"targets but got:\n{result_armed.stdout}"
        )

    # This test must never create a real Phase 130 artifact as a side
    # effect -- everything above happened inside tmp_path only.
    real_phase_130_dir = _HERE.parent / "130-close-honesty-ledger-claim-gate-release-decision"
    assert not real_phase_130_dir.exists() or not any(
        real_phase_130_dir.glob("130-*.md")
    ), "test must not create a real 130-*.md artifact as a side effect"


# ---------------------------------------------------------------------------
# Test 9: positional argv overrides the env seam (precedence pin)
# ---------------------------------------------------------------------------


def test_positional_argv_overrides_the_env_seam():
    """Positional argv must win over FIRESTARTER_CLAIMSCAN_TARGETS. The env
    seam is pointed at the planted violation while argv passes the clean
    control -- the run must succeed, pinning the documented precedence so a
    future change cannot silently invert it."""
    result = _run_scanner(
        targets="fixtures/planted_py32_overclaim.md",
        argv=["fixtures/clean_control.md"],
    )
    assert result.returncode == 0, (
        f"scanner exited {result.returncode} even though argv should have "
        f"overridden the env seam.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout


# ---------------------------------------------------------------------------
# Test 10: PASS line names every scanned file (anti-skip)
# ---------------------------------------------------------------------------


def test_pass_line_names_every_scanned_file():
    """Pointing the scanner at both clean controls at once must produce a
    single PASS: line naming BOTH basenames -- proves neither file was
    silently skipped."""
    result = _run_scanner(
        targets=os.pathsep.join(
            ["fixtures/clean_control.md", "fixtures/clean_control_second.md"]
        )
    )
    assert result.returncode == 0, (
        f"scanner exited {result.returncode} on two clean controls.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "clean_control.md" in result.stdout
    assert "clean_control_second.md" in result.stdout, (
        f"Expected both basenames in the PASS: line but got:\n{result.stdout}"
    )

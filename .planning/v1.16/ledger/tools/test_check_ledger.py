"""
pytest coverage for check_ledger.py — proves the 0/1/2 exit-code contract.

Drives the checker via subprocess.run() with env-overridable path constants
so each test controls exactly which fixture files are loaded.  All fixtures
live under tests/fixtures/; the failure-case tests mutate a copy of the valid
ledger in a tmp file rather than adding per-violation fixture files.

Tests:
  1. Exit 0 — a minimal valid ledger (all 12 buckets, PASS rows with full
     oracle/evidence/sha-match flags, UNVERIFIED no-silicon buckets,
     open_defects with status_changed=false, no raw SHAs).
  2. Exit 1 — a PASS row with the oracle field missing (D-09 violation).
  3. Exit 1 — a ledger containing a raw 64-hex SHA string (D-04 violation).
  4. Exit 1 — a ledger row with a matrix_family not present in the matrix
     fixture (LEDGER-01 join-key violation).
  5. Exit 2 — FIRESTARTER_LEDGER_FILE points at a missing path (load error).
"""

import json
import os
import subprocess
import sys
import tempfile

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_CHECKER = os.path.join(_HERE, "check_ledger.py")
_FIXTURES = os.path.join(_HERE, "fixtures")
_LEDGER_VALID = os.path.join(_FIXTURES, "ledger_valid.json")
_EVIDENCE_MIN = os.path.join(_FIXTURES, "evidence_min.json")
_MATRIX_MIN = os.path.join(_FIXTURES, "matrix_min.json")


def _run_checker(ledger_path, evidence_path=None, matrix_path=None):
    """Invoke check_ledger.py with the given file paths via env vars."""
    env = os.environ.copy()
    env["FIRESTARTER_LEDGER_FILE"] = ledger_path
    env["FIRESTARTER_EVIDENCE_FILE"] = evidence_path or _EVIDENCE_MIN
    env["FIRESTARTER_MATRIX_FILE"] = matrix_path or _MATRIX_MIN
    result = subprocess.run(
        [sys.executable, _CHECKER],
        env=env,
        capture_output=True,
        text=True,
    )
    return result


def _write_tmp_ledger(data):
    """Write a ledger dict to a named temp file and return its path.

    The caller is responsible for deleting the file (use with try/finally or
    the tmp_ledger_file fixture).
    """
    fd, path = tempfile.mkstemp(suffix=".json", prefix="ledger_test_")
    try:
        os.write(fd, json.dumps(data).encode("utf-8"))
    finally:
        os.close(fd)
    return path


def _load_valid_ledger():
    with open(_LEDGER_VALID, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Test 1: valid ledger → exit 0
# ---------------------------------------------------------------------------
def test_valid_ledger_exits_0():
    """A minimal well-formed ledger satisfies all LEDGER-01/02/03 assertions → exit 0."""
    result = _run_checker(_LEDGER_VALID)
    assert result.returncode == 0, (
        f"Expected exit 0 but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# Test 2: PASS row missing oracle → exit 1  (LEDGER-02 / D-09 violation)
# ---------------------------------------------------------------------------
def test_pass_row_missing_oracle_exits_1():
    """A PASS row without oracle='leonardo+Rev2.0' is a D-09 structural violation → exit 1."""
    ledger = _load_valid_ledger()
    # Find the first PASS row and remove its oracle field
    for row in ledger["rows"]:
        if row.get("verification_status") == "PASS":
            row.pop("oracle", None)
            break

    path = _write_tmp_ledger(ledger)
    try:
        result = _run_checker(path)
    finally:
        os.unlink(path)

    assert result.returncode == 1, (
        f"Expected exit 1 but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


# ---------------------------------------------------------------------------
# Test 3: raw 64-hex SHA copied into a row → exit 1  (D-04 no-copy guard)
# ---------------------------------------------------------------------------
def test_raw_sha_in_ledger_exits_1():
    """A 64-char hex string in the ledger body triggers the D-04 no-copy guard → exit 1."""
    # This is a fake SHA (safe to include in test source — it is 64 chars of hex but is
    # NOT a real hash of anything, and it lives in test code, not in the ledger fixture).
    FAKE_SHA = "a" * 64  # 64 'a' chars — matches [0-9a-f]{64}
    ledger = _load_valid_ledger()
    # Inject the fake SHA into a note field on the first row
    ledger["rows"][0]["_test_injected_sha"] = FAKE_SHA

    path = _write_tmp_ledger(ledger)
    try:
        result = _run_checker(path)
    finally:
        os.unlink(path)

    assert result.returncode == 1, (
        f"Expected exit 1 (D-04 no-copy guard) but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


# ---------------------------------------------------------------------------
# Test 4: matrix_family not in matrix fixture → exit 1  (LEDGER-01 join key)
# ---------------------------------------------------------------------------
def test_bad_matrix_family_exits_1():
    """A matrix_family value absent from the matrix fixture is a LEDGER-01 violation → exit 1."""
    ledger = _load_valid_ledger()
    # Mutate the first non-null matrix_family to an unknown value
    for row in ledger["rows"]:
        if row.get("matrix_family") is not None:
            row["matrix_family"] = "nonexistent_family_xyz"
            break

    path = _write_tmp_ledger(ledger)
    try:
        result = _run_checker(path)
    finally:
        os.unlink(path)

    assert result.returncode == 1, (
        f"Expected exit 1 (LEDGER-01 bad matrix_family) but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


# ---------------------------------------------------------------------------
# Test 5: missing ledger path → exit 2  (load error)
# ---------------------------------------------------------------------------
def test_missing_ledger_file_exits_2():
    """When FIRESTARTER_LEDGER_FILE points at a non-existent path, the checker exits 2."""
    result = _run_checker("/nonexistent/path/no_such_ledger.json")
    assert result.returncode == 2, (
        f"Expected exit 2 (load error) but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

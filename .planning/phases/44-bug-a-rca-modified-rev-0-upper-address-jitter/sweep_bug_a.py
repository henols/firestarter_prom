"""Phase 44 Bug A RCA — 2D sweep harness for Modified Rev 0 upper-address jitter.

PURPOSE
-------
Iterate a 2D grid of (read_settling_us × read_strobe_us) timing knob values,
calling `firestarter dev consistency-check` once per grid point and writing the
exit code + stdout tail to `sweep-grid.csv`.  The sweep is the causal lead for
RCA-01 (D-03/D-05 in 44-CONTEXT.md): if a timing knob drives the upper-address
jitter rate to ~zero, causality is proved and Phase 46 has an actionable fix.

D-05 INVARIANT (MANDATORY — DO NOT VIOLATE)
--------------------------------------------
The chip must remain seated in the socket for the ENTIRE sweep.
- NO chip reseating between data points.
- NO firmware re-flash between data points (no sideload commands).
- The timing knob travels as a runtime JSON parameter on each `consistency-check`
  invocation — no build define, no reflash required.
- Reseating per point would inject the very signal-integrity variance being
  measured and violate the chip-out-before-sideload rule on every point
  (see feedback_chip_out_before_sideload.md and CONTEXT.md Pitfall 4).

USAGE
-----
1. Verify the Modified Rev 0 board is on PORT (silkscreen + controller:
   identity confirmed per D-09 / feedback_verify_port_identity_each_task.md).
2. Seat W27C512 (or CHIP) in the socket.  Do NOT remove it during the sweep.
3. Run:
       python sweep_bug_a.py <PORT> [CHIP]
   e.g.:  python sweep_bug_a.py /dev/ttyACM1 W27C512
4. The script writes sweep-grid.csv in the current working directory.
5. After the sweep, call compare_to_baseline(<new_dir>) with the best run's
   output directory to byte-compare against the Phase 29 v2 reference (D-11).

OPERATOR CHECKLIST BEFORE RUNNING
-----------------------------------
- Confirm PORT is the Modified Rev 0 board: `firestarter -p <PORT> info`
  and verify controller: line matches the Modified Rev 0 identity.
- Chip is seated; no firmware change since last bench session.
- `firestarter` is installed and on PATH (`firestarter --version`).

References
----------
- 44-CONTEXT.md: D-03 (firmware sweep = causal lead), D-04 (2D sweep both
  knobs), D-05 (chip seated / no re-flash / no reseat), D-11 (baseline repro)
- 44-RESEARCH.md: Pattern 2 (sweep harness), Pattern 3 (baseline byte-compare),
  Pitfall 4 (chip-out-during-sweep is a D-05 violation)
"""

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Sweep configuration — operator may override via argv or by editing here
# ---------------------------------------------------------------------------

SETTLING_VALUES = [0, 3, 10, 25, 50, 100]  # µs — address-settling before /CE
STROBE_VALUES = [0, 3, 10, 25, 50]  # µs — /CE read-strobe pulse width
RUNS = 5  # consistency-check runs per grid point
CHIP = "W27C512"  # EPROM type (operator may override via argv)
# PORT: operator MUST confirm at session start (D-09).
# Default is a placeholder — pass the real port as argv[1].
PORT = "/dev/ttyACM1"

# Phase 29 v2 reference directory for byte-compare baseline (D-11).
# Contains 15 N=5 W27C512 binaries captured on 2026-05-26.
BASELINE_REF_DIR = (
    ".planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-155021-v2"
)

OUTPUT_CSV = "sweep-grid.csv"


# ---------------------------------------------------------------------------
# Sweep helper
# ---------------------------------------------------------------------------


def compare_to_baseline(new_dir: str, baseline_dir: str = BASELINE_REF_DIR) -> None:
    """Byte-compare the 5 run binaries in new_dir against the Phase 29 v2 reference.

    Prints per-run byte-difference counts and SHA-256 digests.  The operator
    calls this after the baseline run (D-11) to confirm bench continuity:
    WORST >= 1% differences and A15=1 address skew reproduced.

    Args:
        new_dir:     Path to the new consistency-check output directory
                     (contains run_01.bin .. run_05.bin).
        baseline_dir: Path to the Phase 29 v2 reference directory.
                     Default: BASELINE_REF_DIR constant above.
    """
    ref_path = Path(baseline_dir)
    new_path = Path(new_dir)
    print(f"\nBaseline comparison: {new_path} vs {ref_path}")
    for i in range(1, 6):
        ref_file = ref_path / f"run_{i:02d}.bin"
        new_file = new_path / f"run_{i:02d}.bin"
        if not ref_file.exists():
            print(f"  run_{i:02d}: SKIP — ref file not found: {ref_file}")
            continue
        if not new_file.exists():
            print(f"  run_{i:02d}: SKIP — new file not found: {new_file}")
            continue
        ref_data = ref_file.read_bytes()
        new_data = new_file.read_bytes()
        diffs = sum(a != b for a, b in zip(ref_data, new_data))
        total = max(len(ref_data), len(new_data))
        pct = 100.0 * diffs / total if total else 0.0
        ref_sha = hashlib.sha256(ref_data).hexdigest()[:16]
        new_sha = hashlib.sha256(new_data).hexdigest()[:16]
        print(
            f"  run_{i:02d}: {diffs}/{total} byte diffs ({pct:.2f}%) "
            f"ref={ref_sha} new={new_sha}"
        )


# ---------------------------------------------------------------------------
# Main sweep loop
# ---------------------------------------------------------------------------


def run_sweep(port: str, chip: str) -> None:
    """Run the 2D (settling_us × strobe_us) grid sweep and write sweep-grid.csv.

    D-05 reminder: chip stays seated for the full sweep — no re-flash, no reseat.
    """
    total_points = len(SETTLING_VALUES) * len(STROBE_VALUES)
    print(f"Bug A 2D sweep — {chip} on {port}")
    print(f"Grid: {len(SETTLING_VALUES)} settling × {len(STROBE_VALUES)} strobe "
          f"= {total_points} points, {RUNS} runs each")
    print(
        "D-05: chip stays seated for the entire sweep — no re-flash, no reseat.\n"
    )

    with open(OUTPUT_CSV, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["settling_us", "strobe_us", "exit_code", "stdout_tail"])

        for settling in SETTLING_VALUES:
            for strobe in STROBE_VALUES:
                cmd = [
                    "firestarter",
                    "-p", port,
                    "dev",
                    "consistency-check",
                    chip,
                    "--runs", str(RUNS),
                    "-q",
                    "--read-settling", str(settling),
                    "--read-strobe", str(strobe),
                ]
                print(
                    f"  settling={settling:3d}µs  strobe={strobe:3d}µs  "
                    f"(cmd: {' '.join(cmd[-6:])})",
                    end=" ",
                    flush=True,
                )
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=300,  # 5-minute timeout per grid point
                    )
                    stdout_tail = (result.stdout + result.stderr).strip()[-200:]
                    exit_code = result.returncode
                except subprocess.TimeoutExpired:
                    stdout_tail = "TIMEOUT"
                    exit_code = -1
                except FileNotFoundError:
                    print(
                        "\nERROR: `firestarter` not found on PATH. "
                        "Install with: pip install -e . (from firestarter_app/)"
                    )
                    sys.exit(1)

                writer.writerow([settling, strobe, exit_code, stdout_tail])
                csv_file.flush()
                print(f"-> exit={exit_code}")

    print(f"\nSweep complete. Results written to: {OUTPUT_CSV}")
    print("Next step: call compare_to_baseline('<output_dir>') on the baseline")
    print(f"  run (settling=0, strobe=0) output directory to confirm bench")
    print(f"  continuity vs {BASELINE_REF_DIR}")


if __name__ == "__main__":
    # Usage: python sweep_bug_a.py [PORT [CHIP]]
    port = sys.argv[1] if len(sys.argv) > 1 else PORT
    chip = sys.argv[2] if len(sys.argv) > 2 else CHIP

    if port == PORT and PORT == "/dev/ttyACM1":
        print(
            "WARNING: Using default PORT=/dev/ttyACM1. "
            "Verify this is the Modified Rev 0 board before continuing "
            "(D-09: confirm controller: identity per port at task start)."
        )

    run_sweep(port, chip)

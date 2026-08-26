#!/usr/bin/env python3
"""capture_provenance.py -- required-argument-or-refuse per-cell provenance collector (D-13).

D-16 boundary: this is meta-repo BENCH TOOLING, not host source. It is authored and lives
only under .planning/v1.34/tools/ in the meta repo. It must NEVER be copied into
firestarter/ or firestarter_app/ -- this phase changes no firmware and no host source.
Nothing here is imported by, or imports from, either sub-repo.

RIG-05's "zero fields sourced from session memory" is discharged by a mechanism here, not
by a transcriber's discipline: every machine-readable field is gathered by this tool
itself, and the one field only a human can supply -- the operator-declared shield revision
-- is a REQUIRED argument with NO default. `hw_revision` cannot distinguish the operator's
Rev 2.0 / Rev 2.2 / Modified Rev 0 shields (the A3 ADC band collides on 10 kOhm), so
silkscreen read by a human is the only authority; this tool refuses to run without it
rather than infer or default it.

Every probe below returns an explicit (ok, value, detail) triple, mirroring
tools/check_arms.py and tools/probe_board.py -- a failed subprocess call and a clean/absent
result must never collapse to the same null. A probe failure is always a hard non-zero
exit, never a null field.

Host-arm probes (git HEAD, porcelain, config-dir SHA, interpreter, dependency freeze) are
REUSED from tools/check_arms.py -- the standing D-06/D-07/D-08 verifier -- rather than
re-implemented, so a divergence between the two tools' results is itself a finding. The
`__file__` probe is kept as a direct local copy (not delegated) so this tool's own source
carries the load-bearing `-P` flag literally, per Pitfall 1: without it, the probe silently
prints `None` because /workspaces contains a directory literally named `firestarter` (the
firmware repo) that shadows the editable install as a PEP 420 namespace-package portion.

Conventions this tool assumes about the milestone layout (D-16):
  - rig-pins.json lives at the milestone root, one level above tools/.
  - The read-back verdict artifact for a given cell is written by judge_readback.py (a
    later plan in this phase) to
    <milestone>/bench/cells/<cell_slug>/readback_verdict.json
    with keys "judged_sha256" and "whole_flash_sha256". This tool reads that artifact; it
    does not compute it. Missing or incomplete -> hard failure, never a null field.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_MILESTONE_DIR = _HERE.parent
_DEFAULT_PINS = _MILESTONE_DIR / "rig-pins.json"
_PROBE_BOARD = _HERE / "probe_board.py"

_CELL_ID_RE = re.compile(r"^[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*$")
_FW_LINE_RE = re.compile(r"^I: FW: (.+)$", re.MULTILINE)
_HWREV_LINE_RE = re.compile(r"^I: Hardware revision: (.+)$", re.MULTILINE)

_SHIELD_REV_CHOICES = ["Rev 2.0", "Rev 2.2", "Modified Rev 0"]
_ARM_CHOICES = ["control", "v133"]
_TARGET_CHOICES = ["uno", "uno328pb", "leonardo"]
_CHIP_CHOICES = ["w27c512", "w29c020"]

# Field order matches this plan's "Artifacts this phase produces" key list exactly.
RECORD_KEYS = [
    "captured_at_step",
    "cell_id",
    "cell_slug",
    "position_id",
    "arm",
    "target_env",
    "port",
    "chip",
    "chip_package",
    "chip_size_bytes",
    "shield_rev_declared",
    "board_signature",
    "controller_string",
    "fw_sha",
    "fw_readback_sha_judged",
    "fw_readback_sha_whole_flash",
    "host_arm_sha",
    "host_arm_porcelain_clean",
    "host_arm_file",
    "config_dir_sha",
    "interpreter",
    "dep_freeze_sha",
    "avrdude_binary",
    "avrdude_conf",
    "eeprom_calibration",
    "commands",
]

# Pattern 6's derived per-cell step order (RESEARCH.md): step 2 is "re-verify port identity
# for this cell: signature probe (authoritative) + controller: string" -- this capture runs
# there, before any flash/write/read step (RIG-02's "before any test step executes").
CAPTURED_AT_STEP = 2


def _cell_id_type(value: str) -> str:
    if not _CELL_ID_RE.match(value):
        raise argparse.ArgumentTypeError(
            f"--cell-id {value!r} must be composed of [A-Za-z0-9_-]+ segments separated "
            "by '/', with no '..', no leading '/', and no other characters"
        )
    return value


def build_argparser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cell-id", type=_cell_id_type, required=True)
    ap.add_argument("--position-id", required=True)
    ap.add_argument("--arm", required=True, choices=_ARM_CHOICES)
    ap.add_argument("--target", required=True, choices=_TARGET_CHOICES)
    ap.add_argument("--port", required=True)
    ap.add_argument("--chip", required=True, choices=_CHIP_CHOICES)
    ap.add_argument(
        "--shield-rev",
        required=True,
        choices=_SHIELD_REV_CHOICES,
        help="operator-declared shield revision; silkscreen is authoritative, NO default",
    )
    ap.add_argument("--pins", default=str(_DEFAULT_PINS))
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    return ap


# ---------------------------------------------------------------------------
# Path safety
# ---------------------------------------------------------------------------


def resolve_out_path(candidate: str, milestone_dir: Path) -> tuple[bool, Path | None, str]:
    resolved = Path(candidate).resolve()
    milestone_resolved = milestone_dir.resolve()
    parent = resolved.parent
    if parent != milestone_resolved and milestone_resolved not in parent.parents:
        return False, None, (
            f"--out {candidate!r} resolves to {resolved}, whose parent is outside "
            f"{milestone_resolved} -- refusing a path that traverses out of the milestone dir"
        )
    return True, resolved, ""


# ---------------------------------------------------------------------------
# Probe: board signature (delegates to probe_board.py as a subprocess)
# ---------------------------------------------------------------------------


def probe_board_signature(
    port: str, target: str, pins_path: str, tmp_dir: Path
) -> tuple[bool, str | None, dict | None, str, list[str]]:
    out_path = tmp_dir / "probe_board_result.json"
    cmd = [
        sys.executable,
        str(_PROBE_BOARD),
        "--port", port,
        "--target", target,
        "--pins", pins_path,
        "--out", str(out_path),
    ]
    try:
        done = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except OSError as exc:
        return False, None, None, f"probe_board.py failed to execute: {exc}", cmd
    if done.returncode != 0:
        return False, None, None, (
            f"probe_board.py exited {done.returncode}: {(done.stderr or '').strip()[:500]}"
        ), cmd
    try:
        result = json.loads(out_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return False, None, None, f"probe_board.py output unreadable: {exc}", cmd
    sig = result.get("board_signature")
    if not sig:
        return False, None, None, "probe_board.py output missing board_signature", cmd
    return True, sig, result, "", cmd


# ---------------------------------------------------------------------------
# Probe: controller: string + hw-revision bucket (local hardware query, never network)
# ---------------------------------------------------------------------------


def _interpret_hw_probe(returncode: int, stdout: str, stderr: str) -> tuple[bool, str | None, str | None, str]:
    combined = (stdout or "") + (stderr or "")
    fw_m = _FW_LINE_RE.search(combined)
    if not fw_m:
        return False, None, None, (
            f"controller: string not found in `hw` output (exit {returncode}): "
            f"{combined.strip()[:500]!r}"
        )
    hwrev_m = _HWREV_LINE_RE.search(combined)
    hwrev = hwrev_m.group(1).strip() if hwrev_m else None
    return True, fw_m.group(1).strip(), hwrev, ""


def probe_controller_string(arm_bin: str, port: str) -> tuple[bool, str | None, str | None, str, list[str]]:
    cmd = [arm_bin, "-v", "-p", port, "hw"]
    try:
        done = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except OSError as exc:
        return False, None, None, f"hw probe (controller: string) failed to execute: {exc}", cmd
    ok, controller, hwrev, detail = _interpret_hw_probe(done.returncode, done.stdout, done.stderr)
    return ok, controller, hwrev, detail, cmd


# ---------------------------------------------------------------------------
# Probe: read-back verdict artifact (written by judge_readback.py, a later plan)
# ---------------------------------------------------------------------------


def read_readback_verdict(bench_dir: Path, cell_slug: str) -> tuple[bool, dict | None, str]:
    verdict_path = bench_dir / "cells" / cell_slug / "readback_verdict.json"
    if not verdict_path.exists():
        return False, None, (
            f"readback verdict artifact not found at {verdict_path} -- judge_readback.py "
            "must run and write this artifact before capture_provenance.py for this cell"
        )
    try:
        data = json.loads(verdict_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return False, None, f"readback verdict artifact unreadable: {exc}"
    judged = data.get("judged_sha256")
    whole = data.get("whole_flash_sha256")
    if not judged or not whole:
        return False, None, (
            f"readback verdict artifact at {verdict_path} is missing judged_sha256/"
            f"whole_flash_sha256: {data!r}"
        )
    return True, {"judged": judged, "whole": whole}, ""


# ---------------------------------------------------------------------------
# Probe: host-arm __file__ (kept LOCAL, not delegated, so `-P` is literally in this file)
# ---------------------------------------------------------------------------


def _interpret_file_probe(returncode: int, stdout: str, stderr: str, worktree: str) -> tuple[bool, str | None, str]:
    if returncode != 0:
        return False, None, f"__file__ probe exited {returncode}: {stderr.strip()}"
    path = stdout.strip()
    if not path or path == "None":
        return False, None, "__file__ probe returned empty/None (Pitfall 1 -- was -P dropped?)"
    if not path.startswith(worktree):
        return False, None, f"__file__ path {path!r} does not resolve under worktree {worktree!r}"
    return True, path, ""


def probe_host_arm_file(venv_python: str, worktree: str) -> tuple[bool, str | None, str, list[str]]:
    cmd = [venv_python, "-P", "-c", "import firestarter; print(firestarter.__file__)"]
    try:
        done = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except OSError as exc:
        return False, None, f"__file__ probe failed to execute: {exc}", cmd
    ok, path, detail = _interpret_file_probe(done.returncode, done.stdout, done.stderr, worktree)
    return ok, path, detail, cmd


# ---------------------------------------------------------------------------
# check_arms.py reuse (git HEAD, porcelain, config-dir SHA, interpreter, dep freeze)
# ---------------------------------------------------------------------------


def _load_check_arms():
    spec = importlib.util.spec_from_file_location("check_arms", _HERE / "check_arms.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def probe_dep_freeze_sha(ca_mod, venv_python: str, uv_cache_dir: str) -> tuple[bool, str | None, str]:
    ok, freeze = ca_mod.get_pip_freeze(venv_python, uv_cache_dir)
    if not ok:
        return False, None, f"dep freeze probe failed: {freeze}"
    text = "\n".join(sorted(freeze)) + "\n"
    return True, hashlib.sha256(text.encode("utf-8")).hexdigest(), ""


# ---------------------------------------------------------------------------
# Atomic write
# ---------------------------------------------------------------------------


def write_record_atomic(record: dict, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ordered = {key: record[key] for key in RECORD_KEYS}
    tmp_path = out_path.with_name(out_path.name + ".tmp")
    tmp_path.write_text(json.dumps(ordered, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    os.replace(tmp_path, out_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    # --selftest is scanned for BEFORE the full parse, deliberately: --shield-rev is
    # required=True with no default (D-13), so a normal `ap.parse_args()` would itself
    # refuse `--selftest` alone with a missing-required-argument error before this
    # function ever got a chance to route to the selftest, which carries no device
    # arguments at all.
    if "--selftest" in sys.argv[1:]:
        return _run_selftest()

    ap = build_argparser()
    args = ap.parse_args()

    try:
        pins = json.loads(Path(args.pins).read_text())
    except OSError as exc:
        print(f"FAIL: could not read pins file {args.pins}: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"FAIL: pins file {args.pins} is not valid JSON: {exc}", file=sys.stderr)
        return 1

    cell_slug = args.cell_id.replace("/", "-")
    out_candidate = args.out or str(
        _MILESTONE_DIR / "bench" / "cells" / cell_slug / "provenance.json"
    )
    ok, out_path, detail = resolve_out_path(out_candidate, _MILESTONE_DIR)
    if not ok:
        print(f"FAIL: {detail}", file=sys.stderr)
        return 1

    try:
        arm_cfg = pins["arms"][args.arm]
        chip_cfg = pins["chips"][args.chip]
        avrdude_cfg = pins["avrdude"]
    except KeyError as exc:
        print(f"FAIL: rig-pins.json missing expected key: {exc}", file=sys.stderr)
        return 1

    forbidden = {e.get("path") for e in pins.get("forbidden_binaries", []) if isinstance(e, dict)}
    if avrdude_cfg.get("binary") in forbidden:
        print(f"FAIL: pinned avrdude binary {avrdude_cfg.get('binary')!r} is forbidden", file=sys.stderr)
        return 1

    commands_log: list[dict] = []
    tmp_dir = Path(tempfile.mkdtemp(prefix="capture_provenance_"))

    def _log(cmd: list[str]) -> None:
        commands_log.append({"argv": list(cmd), "cwd": os.getcwd()})

    ok, board_signature, _probe_result, detail, cmd = probe_board_signature(
        args.port, args.target, args.pins, tmp_dir
    )
    _log(cmd)
    if not ok:
        print(f"FAIL: board-signature probe: {detail}", file=sys.stderr)
        return 1

    ok, controller_string, hwrev, detail, cmd = probe_controller_string(arm_cfg["venv_bin"], args.port)
    _log(cmd)
    if not ok:
        print(f"FAIL: controller-string probe: {detail}", file=sys.stderr)
        return 1

    ok, readback, detail = read_readback_verdict(_MILESTONE_DIR / "bench", cell_slug)
    if not ok:
        print(f"FAIL: readback-verdict probe: {detail}", file=sys.stderr)
        return 1

    ca_mod = _load_check_arms()

    ok, head, detail = ca_mod.check_head(arm_cfg["worktree"], arm_cfg["app_sha"])
    _log(["git", "-C", arm_cfg["worktree"], "rev-parse", "HEAD"])
    if not ok:
        print(f"FAIL: host-arm HEAD probe: {detail}", file=sys.stderr)
        return 1

    ok, porc_detail = ca_mod.check_porcelain(arm_cfg["worktree"])
    _log(["git", "-C", arm_cfg["worktree"], "status", "--porcelain"])
    if not ok:
        print(f"FAIL: host-arm porcelain probe: {porc_detail}", file=sys.stderr)
        return 1

    ok, file_path, detail, cmd = probe_host_arm_file(arm_cfg["venv_python"], arm_cfg["worktree"])
    _log(cmd)
    if not ok:
        print(f"FAIL: host-arm __file__ probe: {detail}", file=sys.stderr)
        return 1

    ok, config_sha, detail = (
        (True, ca_mod.compute_config_dir_sha(pins["config_dir"]), "")
        if Path(pins["config_dir"]).is_dir()
        else (False, None, f"config_dir {pins.get('config_dir')!r} does not exist")
    )
    if not ok:
        print(f"FAIL: config-dir-sha probe: {detail}", file=sys.stderr)
        return 1

    ok, interpreter, detail = ca_mod.get_python_version(arm_cfg["venv_python"])
    _log([arm_cfg["venv_python"], "--version"])
    if not ok:
        print(f"FAIL: interpreter probe: {detail}", file=sys.stderr)
        return 1

    ok, dep_freeze_sha, detail = probe_dep_freeze_sha(ca_mod, arm_cfg["venv_python"], pins["uv_cache_dir"])
    if not ok:
        print(f"FAIL: dep-freeze-sha probe: {detail}", file=sys.stderr)
        return 1

    eeprom_calibration = {
        "hw_revision_bucket": hwrev if hwrev else "not measured — `hw` command's revision line not found in this session's output",
        "r16_ohms": "not measured — no read-back CLI path exists for R16; firestarter config is write-only in this app version",
        "r14r15_ohms": "not measured — no read-back CLI path exists for R14/R15; firestarter config is write-only in this app version",
    }

    record = {
        "captured_at_step": CAPTURED_AT_STEP,
        "cell_id": args.cell_id,
        "cell_slug": cell_slug,
        "position_id": args.position_id,
        "arm": args.arm,
        "target_env": args.target,
        "port": args.port,
        "chip": args.chip,
        "chip_package": chip_cfg["package"],
        "chip_size_bytes": chip_cfg["size_bytes"],
        "shield_rev_declared": args.shield_rev,
        "board_signature": board_signature,
        "controller_string": controller_string,
        "fw_sha": arm_cfg["fw_sha"],
        "fw_readback_sha_judged": readback["judged"],
        "fw_readback_sha_whole_flash": readback["whole"],
        "host_arm_sha": head,
        "host_arm_porcelain_clean": True,
        "host_arm_file": file_path,
        "config_dir_sha": config_sha,
        "interpreter": interpreter,
        "dep_freeze_sha": dep_freeze_sha,
        "avrdude_binary": avrdude_cfg["binary"],
        "avrdude_conf": avrdude_cfg["conf"],
        "eeprom_calibration": eeprom_calibration,
        "commands": commands_log,
    }

    write_record_atomic(record, out_path)
    print(f"OK: provenance captured for cell {args.cell_id!r} -> {out_path}")
    return 0


# ---------------------------------------------------------------------------
# --selftest: stubbed probe results in a temp directory; no device, no arm.
# ---------------------------------------------------------------------------


def _run_selftest() -> int:
    import shutil

    ok_overall = True

    def report(name: str, passed: bool, detail: str = "") -> None:
        nonlocal ok_overall
        status = "PASS" if passed else "FAIL"
        if not passed:
            ok_overall = False
        suffix = f" -- {detail}" if detail else ""
        print(f"{status}: {name}{suffix}")

    # --- negative: missing --shield-rev exits non-zero at argument parsing ---
    ap = build_argparser()
    try:
        ap.parse_args(
            [
                "--cell-id", "A3/B2", "--position-id", "x", "--arm", "control",
                "--target", "uno", "--port", "/dev/null", "--chip", "w27c512",
            ]
        )
        missing_shield_rev_failed = False
    except SystemExit as exc:
        missing_shield_rev_failed = exc.code != 0
    report("negative: missing --shield-rev exits non-zero", missing_shield_rev_failed)

    # --- negative: out-of-set --shield-rev is rejected ---
    try:
        ap.parse_args(
            [
                "--cell-id", "A3/B2", "--position-id", "x", "--arm", "control",
                "--target", "uno", "--port", "/dev/null", "--chip", "w27c512",
                "--shield-rev", "Rev 1.0",
            ]
        )
        bad_shield_rev_failed = False
    except SystemExit as exc:
        bad_shield_rev_failed = exc.code != 0
    report("negative: out-of-set --shield-rev value is rejected", bad_shield_rev_failed)

    # --- negative: --cell-id with '..' or an absolute path is rejected ---
    for bad_cell_id in ("../etc/passwd", "/abs/path", "a b", "a..b"):
        try:
            _cell_id_type(bad_cell_id)
            passed = False
        except argparse.ArgumentTypeError:
            passed = True
        report(f"negative: --cell-id {bad_cell_id!r} is rejected", passed)

    # --- positive: a well-formed --cell-id derives the expected cell_slug ---
    good_cell_id = "A3/B2"
    report(
        "positive: --cell-id 'A3/B2' is accepted and slugs to 'A3-B2'",
        _cell_id_type(good_cell_id) == good_cell_id and good_cell_id.replace("/", "-") == "A3-B2",
    )

    # --- negative: a stubbed git failure produces a non-zero exit, never a null field ---
    ca_mod = _load_check_arms()
    ok, detail = ca_mod.check_head("/nonexistent-worktree-for-selftest", "deadbeef")
    report("negative: a git HEAD probe on a nonexistent worktree fails hard (never null)", not ok, detail)

    # --- negative: a stubbed __file__ probe returning empty produces a non-zero exit ---
    ok, path, detail = _interpret_file_probe(0, "None\n", "", "/some/worktree")
    report("negative: an empty/None __file__ probe result is a hard failure", not ok, detail)
    ok, path, detail = _interpret_file_probe(1, "", "boom", "/some/worktree")
    report("negative: a nonzero __file__ probe exit is a hard failure", not ok, detail)

    # --- negative: an --out path resolving outside .planning/v1.34/ is rejected ---
    ok, resolved, detail = resolve_out_path("/tmp/outside-milestone.json", _MILESTONE_DIR)
    report("negative: --out outside .planning/v1.34/ is rejected", not ok, detail)

    # --- positive: an --out path resolving inside .planning/v1.34/ is accepted ---
    ok, resolved, detail = resolve_out_path(
        str(_MILESTONE_DIR / "bench" / "cells" / "_selftest" / "provenance.json"), _MILESTONE_DIR
    )
    report("positive: --out inside .planning/v1.34/ is accepted", ok, detail)

    # --- positive: a complete record round-trips through the atomic writer with every
    #     documented key present and non-null ---
    tmp = Path(tempfile.mkdtemp(prefix="capture_provenance_selftest_"))
    try:
        fake_record = {
            "captured_at_step": CAPTURED_AT_STEP,
            "cell_id": "BRINGUP-wrv",
            "cell_slug": "BRINGUP-wrv",
            "position_id": "bringup",
            "arm": "v133",
            "target_env": "uno",
            "port": "/dev/ttyACM0",
            "chip": "w27c512",
            "chip_package": "DIP28",
            "chip_size_bytes": 65536,
            "shield_rev_declared": "Rev 2.0",
            "board_signature": "0x1e950f",
            "controller_string": "3.0.0b32:uno",
            "fw_sha": "5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463",
            "fw_readback_sha_judged": hashlib.sha256(b"judged").hexdigest(),
            "fw_readback_sha_whole_flash": hashlib.sha256(b"whole").hexdigest(),
            "host_arm_sha": "cb189a9b001e9e34fb7651535de339761301d061",
            "host_arm_porcelain_clean": True,
            "host_arm_file": "/workspaces/.v1.34-arms/v133/firestarter/__init__.py",
            "config_dir_sha": hashlib.sha256(b"config").hexdigest(),
            "interpreter": "Python 3.12.14",
            "dep_freeze_sha": hashlib.sha256(b"freeze").hexdigest(),
            "avrdude_binary": "/home/vscode/.platformio/packages/tool-avrdude/avrdude",
            "avrdude_conf": "/home/vscode/.platformio/packages/tool-avrdude/avrdude.conf",
            "eeprom_calibration": {
                "hw_revision_bucket": "not measured — selftest fixture, no board attached",
                "r16_ohms": "not measured — no read-back CLI path exists for R16",
                "r14r15_ohms": "not measured — no read-back CLI path exists for R14/R15",
            },
            "commands": [{"argv": ["/fake/bin"], "cwd": "/tmp"}],
        }
        out_path = tmp / "provenance.json"
        write_record_atomic(fake_record, out_path)
        loaded = json.loads(out_path.read_text())
        missing_or_null = [k for k in RECORD_KEYS if k not in loaded or loaded[k] is None]
        report(
            "positive: a complete record has every documented key present and non-null after round-trip",
            not missing_or_null,
            f"missing/null: {missing_or_null}" if missing_or_null else "",
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    return 0 if ok_overall else 1


if __name__ == "__main__":
    sys.exit(main())

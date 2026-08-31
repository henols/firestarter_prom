#!/usr/bin/env python3
"""
tools/wiki/dispatch_mirror.py -- standalone stdlib-only checker that mirrors
the EPROM programming-protocol dispatch order across three representations:
the published wiki page, the host application's dispatch function, and the
firmware's native dispatch test.

Exit-code contract:
  0 = the asserted property holds
  1 = the asserted property is false
  2 = a precondition was not met (source directory missing, or missing
      on the command line at all)

The claims region on the published Programming-Protocols page is the doc
leg's only input. A region that is absent, or that parses to a bucket-row
count below MIN_BUCKET_ROWS, is treated as a reformatted table rather than
a real change in firmware behaviour -- and returns 2, never 0. MIN_BUCKET_ROWS
is set to half of the current 12-row production table, so removing a single
real row is still caught as a named exit-1 disagreement below, not masked
as a precondition failure.
"""

from __future__ import annotations

import argparse
import importlib
import re
import sys
from pathlib import Path

PROTOCOLS_PAGE = "Programming-Protocols.md"
CLAIMS_BEGIN = "<!-- firestarter-claims-begin -->"
CLAIMS_END = "<!-- firestarter-claims-end -->"
FW_DISPATCH_TEST_REL = Path("test/native/avr/test_dispatch/test_configure_memory.cpp")
DISPATCH_MODULE_NAME = "tools.check_dispatch"
MIN_BUCKET_ROWS = 6

_BUCKET_ROW_RE = re.compile(
    r"^\|\s*0x([0-9A-Fa-f]+)\s*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|"
)
_FAMILY_ROW_RE = re.compile(
    r"^\|\s*([a-z0-9_-]+)\s*\|\s*`[a-z0-9_]+\(\)`\s*\|\s*`([a-z0-9_]+\.cpp)`\s*\|"
)
_FW_HEX_TOKEN_RE = re.compile(r"0x([0-9A-Fa-f]+)")

DOC_FILE_TO_FUNC: dict[str, str] = {
    "flash_5v_page.cpp": "configure_flash_5v_page",
    "flash_nor_unlock.cpp": "configure_flash_nor_unlock",
    "eprom.cpp": "configure_eprom",
    "eeprom_28c.cpp": "configure_eeprom28c",
    "flash_intel.cpp": "configure_flash_intel",
    "sram.cpp": "configure_sram",
    "not_implemented.cpp": "not_implemented",
}


def parse_claims_region(text: str) -> str | None:
    begin = text.find(CLAIMS_BEGIN)
    if begin == -1:
        return None
    end = text.find(CLAIMS_END, begin)
    if end == -1:
        return None
    return text[begin + len(CLAIMS_BEGIN) : end]


def parse_bucket_rows(region: str) -> list[tuple[int, str, bool]]:
    rows: list[tuple[int, str, bool]] = []
    for line in region.splitlines():
        match = _BUCKET_ROW_RE.match(line)
        if match is None:
            continue
        hex_id = int(match.group(1), 16)
        family_col = match.group(2).strip()
        family = family_col.split()[0] if family_col else ""
        phantom = match.group(3).strip().upper() == "YES"
        rows.append((hex_id, family, phantom))
    return rows


def parse_family_rows(region: str) -> dict[str, str]:
    families: dict[str, str] = {}
    for line in region.splitlines():
        match = _FAMILY_ROW_RE.match(line)
        if match is not None:
            families[match.group(1).strip()] = match.group(2).strip()
    return families


def build_doc_table(
    bucket_rows: list[tuple[int, str, bool]], family_to_file: dict[str, str]
) -> dict[int, str]:
    table: dict[int, str] = {}
    for hex_id, family, phantom in bucket_rows:
        if phantom:
            continue
        handler_file = family_to_file.get(family)
        if handler_file is not None:
            table[hex_id] = handler_file
    return table


def check_dispatch_mirror(
    doc_table: dict[int, str],
    known_protocols: set[int],
    algo_mem_type: dict[int, int],
    dispatch,
    fw_text: str,
) -> list[str]:
    failures: list[str] = []

    for hex_id in sorted(known_protocols):
        if hex_id not in doc_table:
            failures.append(
                f"0x{hex_id:02X} is dispatched by the host tool but has no "
                "bucket row in the claims region"
            )

    for hex_id, handler_file in sorted(doc_table.items()):
        expected_func = DOC_FILE_TO_FUNC.get(handler_file)
        if expected_func is None:
            failures.append(
                f"0x{hex_id:02X}: handler file {handler_file!r} parsed from "
                "the claims region has no known dispatch function mapping"
            )
            continue
        mem_type = algo_mem_type.get(hex_id, 0)
        got_func = dispatch(hex_id, mem_type)
        if got_func != expected_func:
            failures.append(
                f"0x{hex_id:02X}: doc says {expected_func} but the host "
                f"tool returned {got_func}"
            )

    fw_hex_tokens = {int(tok, 16) for tok in _FW_HEX_TOKEN_RE.findall(fw_text)}
    real_handler_protocols = {
        hex_id
        for hex_id, handler_file in doc_table.items()
        if handler_file != "not_implemented.cpp"
    }
    missing_from_fw = sorted(real_handler_protocols - fw_hex_tokens)
    if missing_from_fw:
        missing_str = ", ".join(f"0x{h:02X}" for h in missing_from_fw)
        failures.append(
            f"firmware dispatch test does not enumerate protocol(s): {missing_str}"
        )

    return failures


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dispatch_mirror.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--wiki-dir", type=Path, required=True, default=None)
    parser.add_argument("--app-dir", type=Path, required=True, default=None)
    parser.add_argument("--fw-dir", type=Path, required=True, default=None)
    return parser


def _load_dispatch_module(app_dir: Path):
    inserted = str(app_dir)
    sys.path.insert(0, inserted)
    try:
        module = importlib.import_module(DISPATCH_MODULE_NAME)
    finally:
        if inserted in sys.path:
            sys.path.remove(inserted)
    return module


def main() -> int:
    args = _build_argparser().parse_args()

    if not args.wiki_dir.is_dir():
        print(f"ERROR: --wiki-dir not found: {args.wiki_dir}", file=sys.stderr)
        return 2
    if not args.app_dir.is_dir():
        print(f"ERROR: --app-dir not found: {args.app_dir}", file=sys.stderr)
        return 2
    if not args.fw_dir.is_dir():
        print(f"ERROR: --fw-dir not found: {args.fw_dir}", file=sys.stderr)
        return 2

    page = args.wiki_dir / PROTOCOLS_PAGE
    if not page.is_file():
        print(f"ERROR: {PROTOCOLS_PAGE} not found under {args.wiki_dir}", file=sys.stderr)
        return 2

    region = parse_claims_region(page.read_text(encoding="utf-8"))
    if region is None:
        print(
            f"ERROR: claims region ({CLAIMS_BEGIN} / {CLAIMS_END}) not found "
            f"in {PROTOCOLS_PAGE}",
            file=sys.stderr,
        )
        return 2

    bucket_rows = parse_bucket_rows(region)
    non_phantom_rows = [row for row in bucket_rows if not row[2]]
    if len(non_phantom_rows) < MIN_BUCKET_ROWS:
        print(
            f"ERROR: claims region parsed to {len(non_phantom_rows)} bucket "
            f"row(s), fewer than the required minimum of {MIN_BUCKET_ROWS}",
            file=sys.stderr,
        )
        return 2

    family_to_file = parse_family_rows(region)
    doc_table = build_doc_table(bucket_rows, family_to_file)

    fw_test_path = args.fw_dir / FW_DISPATCH_TEST_REL
    if not fw_test_path.is_file():
        print(f"ERROR: firmware dispatch test not found: {fw_test_path}", file=sys.stderr)
        return 2

    try:
        dispatch_module = _load_dispatch_module(args.app_dir)
    except ImportError as exc:
        print(
            f"ERROR: could not import {DISPATCH_MODULE_NAME} from "
            f"{args.app_dir}: {exc}",
            file=sys.stderr,
        )
        return 2

    try:
        known_protocols = set(dispatch_module.KNOWN_PROTOCOLS)
        algo_mem_type = dict(dispatch_module._ALGO_MEM_TYPE)
        dispatch = dispatch_module.dispatch
    except AttributeError as exc:
        print(
            f"ERROR: {DISPATCH_MODULE_NAME} is missing an expected symbol: {exc}",
            file=sys.stderr,
        )
        return 2

    fw_text = fw_test_path.read_text(encoding="utf-8")

    failures = check_dispatch_mirror(
        doc_table, known_protocols, algo_mem_type, dispatch, fw_text
    )

    if failures:
        for message in failures:
            print(f"ERROR: {message}", file=sys.stderr)
        return 1

    print(f"OK: {len(doc_table)} protocols compared across wiki, host tool and firmware.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Print the raw minipro infoic.xml record(s) for a part, plus the decode
build_db.py derives from them.

Self-contained: stdlib only. This skill OWNS its decode tables — it does not
import build_db.py, so it keeps working if firestarter_app moves or is absent.

Because a private copy of a table can drift from the generator it describes,
`--check` re-reads the constants out of build_db.py *as text* (never importing
or executing it) and reports any disagreement. Run it after touching the
generator. A drift is reported loudly and never silently papered over.

Read-only: never writes the chip database, never invents a value.

    python3 infoic_lookup.py AT28C256
    python3 infoic_lookup.py W27E257 --raw
    python3 infoic_lookup.py --check
"""

from __future__ import annotations

import argparse
import ast
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

def _repo_root() -> str:
    """Locate the checkout from this file: <root>/.claude/skills/<s>/scripts/.

    Falls back to the current directory when the skill is installed outside a
    checkout, where an explicit flag or env override is the only sane source.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.normpath(os.path.join(here, *[os.pardir] * 4))
    return root if os.path.isdir(os.path.join(root, "firestarter_app")) else os.getcwd()


DEFAULT_APP = os.environ.get(
    "FIRESTARTER_APP", os.path.join(_repo_root(), "firestarter_app"))

# ---------------------------------------------------------------------------
# Owned decode tables. Transcribed from minipro's own constants; `--check`
# verifies them against build_db.py. Do not "improve" a value from memory —
# an earlier draft guessed 0x80 as 18V when it is 13.5V, which would have
# fabricated a decode bug in W27E257 that does not exist.
# ---------------------------------------------------------------------------

# Pinned upstream catalog. Must match build_db.py:MINIPRO_XML_URL.
MINIPRO_XML_URL = (
    "https://gitlab.com/DavidGriffith/minipro/-/raw/"
    "a8efaedc236c1d9718bd28299dfbb99536b010ff/infoic.xml"
)

# Key is (voltages & 0xF0) — the HIGH nibble. Masking the full byte is the
# classic build_db.py bug: option bits in 3-0 push the lookup off the table
# and silently yield 0 mV.
#
# Values are MILLIVOLTS, deliberately the same unit as the generator's own
# table, so `--check` is a direct dict comparison with no lossy string
# round-trip in the middle. Display formatting happens in `format_vpp()`.
VPP_MV = {
    0x00: 12000, 0x10: 9000, 0x20: 9500, 0x30: 10000,
    0x40: 11000, 0x50: 11500, 0x60: 12500, 0x70: 13000,
    0x80: 13500, 0x90: 14000, 0xA0: 14500, 0xB0: 15500,
    0xC0: 16000, 0xD0: 16500, 0xE0: 17000, 0xF0: 18000,
}

# What the generator calls the table above. It was `VPP_VOLTAGES` when this
# script was written (2026-08-07) and is `VPP_MV` today. That rename is
# exactly how the drift check rotted: it looked for one hard-coded name,
# found nothing, printed a WARN and exited 0 — so from the rename onward the
# single table this script most needs verified was verified by nothing.
# Tried in order; the first one present wins.
GENERATOR_VPP_NAMES = ("VPP_MV", "VPP_VOLTAGES")


def format_vpp(mv: object) -> str:
    """Render a millivolt table value the way the old string table read.

    12000 -> "12V", 9500 -> "9.5V". `%g` drops the trailing ".0" so whole
    volts stay unadorned.
    """
    if not isinstance(mv, int):
        return "NOT IN TABLE"
    return f"{mv / 1000:g}V"


def check_drift(app_dir: str) -> int:
    """Compare our owned tables against build_db.py WITHOUT importing it.

    The generator is read as text and the two constants are extracted with
    `ast`, so nothing in it executes — importing would be a dependency, and
    running it would regenerate the database.
    """
    path = os.path.join(app_dir, "tools", "build_db.py")
    try:
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=path)
    except (OSError, SyntaxError) as exc:
        print(f"SKIP: cannot read {path} ({exc}). "
              "Tables unverified — this tool still works standalone.")
        return 0

    found: dict[str, object] = {}
    for node in ast.walk(tree):
        targets = []
        if isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            targets = [node.target.id]
        if not targets:
            continue
        for name in targets:
            wanted = ("MINIPRO_XML_URL", *GENERATOR_VPP_NAMES)
            if name in wanted and node.value is not None:
                try:
                    found[name] = ast.literal_eval(node.value)
                except (ValueError, SyntaxError):
                    pass

    drift = 0
    theirs_url = found.get("MINIPRO_XML_URL")
    if theirs_url is None:
        # Fail CLOSED. A constant this script cannot find is a constant it
        # cannot verify, which is indistinguishable from a drift for every
        # purpose this check exists to serve.
        drift += 1
        print("DRIFT: MINIPRO_XML_URL not found in build_db.py — the "
              "generator renamed or restructured it, so the pinned catalog "
              "SHA is now unverified. Re-read the generator and update this "
              "script.")
    elif theirs_url != MINIPRO_XML_URL:
        drift += 1
        print("DRIFT: pinned infoic.xml URL differs\n"
              f"  ours  : {MINIPRO_XML_URL}\n  theirs: {theirs_url}")
    else:
        print("ok: MINIPRO_XML_URL matches build_db.py")

    their_vpp_name = next(
        (n for n in GENERATOR_VPP_NAMES if isinstance(found.get(n), dict)), None
    )
    theirs_vpp = found.get(their_vpp_name) if their_vpp_name else None
    if not isinstance(theirs_vpp, dict):
        # Fail CLOSED, and say what was looked for — the previous WARN+exit-0
        # here is what let the VPP table go unchecked across a rename.
        drift += 1
        print("DRIFT: no VPP table found in build_db.py under any known name "
              f"({', '.join(GENERATOR_VPP_NAMES)}). The generator renamed it "
              "again. Find the new name, add it to GENERATOR_VPP_NAMES, and "
              "re-verify the values — do NOT assume they are unchanged.")
    elif theirs_vpp != VPP_MV:
        drift += 1
        keys = set(theirs_vpp) | set(VPP_MV)
        print(f"DRIFT: VPP table differs (generator calls it {their_vpp_name})")
        for k in sorted(keys):
            a, b = VPP_MV.get(k), theirs_vpp.get(k)
            if a != b:
                print(f"  0x{k:02X}: ours={a!r} mV  theirs={b!r} mV")
    else:
        print(f"ok: VPP table matches build_db.py:{their_vpp_name} "
              f"({len(VPP_MV)} entries, compared in mV)")

    if drift:
        print(f"\n{drift} table(s) drifted. Update this script to match the "
              "generator before trusting its decode.")
        return 1
    return 0


def fetch(path: str, url: str) -> str:
    """Download infoic.xml once and cache it (17.8 MB)."""
    if os.path.exists(path) and os.path.getsize(path) > 1_000_000:
        return path
    print(f"fetching {url}\n     -> {path}", file=sys.stderr)
    with urllib.request.urlopen(url, timeout=120) as r:  # noqa: S310
        data = r.read()
    with open(path, "wb") as f:
        f.write(data)
    return path


def split_pkg(token: str) -> tuple[str, str | None]:
    """Split an infoic name token into (part, package).

    Upstream qualifies most names with a package suffix — `W27E257@DIP28`.
    Some parts appear ONLY suffixed, so matching the whole token misses them
    outright. build_db.py strips the same suffix when it emits part_number.
    """
    part, _, pkg = token.strip().partition("@")
    return part, (pkg or None)


def norm(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", s).upper()


def as_int(v: str | None) -> int | None:
    if v is None:
        return None
    v = v.strip()
    try:
        return int(v, 16) if v.lower().startswith("0x") else int(v)
    except ValueError:
        return None


# From the infoic.xml header comment (the file documents its own `type` codes).
TYPE_NAMES = {1: "EEPROM", 2: "MCU/MPU", 3: "PLD/CPLD", 4: "SRAM",
              5: "LOGIC", 6: "NAND", 7: "EMMC", 8: "VGA/HDMI"}


def decode(ic: ET.Element) -> list[str]:
    """Report only what infoic.xml itself carries. Nothing here is invented."""
    out = []
    flags = as_int(ic.get("flags"))
    if flags is not None:
        erasable = bool(flags & 0x10)
        out.append(
            f"  flags & 0x10      = {'SET' if erasable else 'clear'}"
            f"   -> {'electrically erasable' if erasable else 'UV-EPROM'}"
            f"   (raw flags 0x{flags:X})"
        )
    volt = as_int(ic.get("voltages"))
    if volt is not None:
        idx = volt & 0xF0
        out.append(
            f"  voltages & 0xF0   = 0x{idx:02X}"
            f"  -> VPP {format_vpp(VPP_MV.get(idx))}"
            f"   (option bits 0x{volt & 0x0F:X})"
        )
    proto = as_int(ic.get("protocol_id"))
    if proto is not None:
        out.append(
            f"  protocol_id       = 0x{proto:02X}"
            "  -> programming.algorithm, before any safety flip"
        )
    var = as_int(ic.get("variant"))
    if var is not None:
        out.append(
            f"  variant           = 0x{var:04X}"
            f" (lo=0x{var & 0xFF:02X}, hi=0x{var >> 8:02X})  -> resolve_pinout_key()"
        )
    pm = as_int(ic.get("pin_map"))
    if pm is not None:
        out.append(
            f"  pin_map           = 0x{pm:04X}"
            f" (lo=0x{pm & 0xFF:02X} = pm_idx)  -> resolve_pinout_key()"
        )
    t = as_int(ic.get("type"))
    if t is not None:
        out.append(f"  type              = {t} ({TYPE_NAMES.get(t, '?')})")
    size = as_int(ic.get("code_memory_size"))
    if size is not None:
        out.append(f"  code_memory_size  = {size} (0x{size:X})  -> electrical.size_bytes")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("part", nargs="?",
                    help="part number, e.g. AT28C256 (case/punctuation insensitive)")
    ap.add_argument("--app", default=DEFAULT_APP,
                    help=f"firestarter_app root, for --check (default {DEFAULT_APP})")
    ap.add_argument("--xml", default=None, help="local infoic.xml cache path")
    ap.add_argument("--raw", action="store_true", help="dump every attribute verbatim")
    ap.add_argument("--check", action="store_true",
                    help="verify our decode tables against build_db.py, then exit")
    args = ap.parse_args()

    if args.check:
        return check_drift(args.app)
    if not args.part:
        ap.error("a part number is required (or use --check)")

    url = MINIPRO_XML_URL
    sha = re.search(r"/raw/([0-9a-f]{8})", url)
    cache = args.xml or os.path.join(
        os.environ.get("TMPDIR", "/tmp"),
        f"infoic-{sha.group(1) if sha else 'unpinned'}.xml",
    )
    path = fetch(cache, url)
    want = norm(args.part)

    hits = 0
    mfg = dbtype = "?"
    for event, el in ET.iterparse(path, events=("start", "end")):
        if event == "start":
            if el.tag == "database":
                dbtype = el.get("type", "?")
            elif el.tag == "manufacturer":
                mfg = el.get("name", "?").strip()
            continue
        if el.tag != "ic":
            continue
        name = (el.get("name") or "").strip()
        matched = [tok for tok in name.split(",") if want == norm(split_pkg(tok)[0])]
        if matched:
            hits += 1
            pkgs = sorted({split_pkg(t)[1] or "(unqualified)" for t in matched})
            print(f"\n=== {name}   [{mfg}]   ({dbtype}) ===")
            print(f"  matched           : {', '.join(matched)}   packages: {', '.join(pkgs)}")
            if args.raw:
                for k, v in sorted(el.attrib.items()):
                    print(f"  {k:18} = {v}")
            else:
                for line in decode(el):
                    print(line)
        el.clear()

    if not hits:
        print(f"\nno <ic> record matches {args.part!r} in {os.path.basename(path)}.",
              file=sys.stderr)
        print("If the chip is physically real, this is tools/extra_chips.json "
              "territory — upstream genuinely lacks it.", file=sys.stderr)
        return 1
    print(f"\n{hits} record(s). DIP is the package this project programs; "
          "ignore PLCC/SOIC/TSOP rows unless an adapter is in play.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

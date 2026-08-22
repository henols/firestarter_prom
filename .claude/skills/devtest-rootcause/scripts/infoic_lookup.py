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

DEFAULT_APP = os.environ.get("FIRESTARTER_APP", "/workspaces/firestarter_app")

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
VPP_VOLTAGES = {
    0x00: "12V", 0x10: "9V", 0x20: "9.5V", 0x30: "10V",
    0x40: "11V", 0x50: "11.5V", 0x60: "12.5V", 0x70: "13V",
    0x80: "13.5V", 0x90: "14V", 0xA0: "14.5V", 0xB0: "15.5V",
    0xC0: "16V", 0xD0: "16.5V", 0xE0: "17V", 0xF0: "18V",
}


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
            if name in ("VPP_VOLTAGES", "MINIPRO_XML_URL") and node.value is not None:
                try:
                    found[name] = ast.literal_eval(node.value)
                except (ValueError, SyntaxError):
                    pass

    drift = 0
    theirs_url = found.get("MINIPRO_XML_URL")
    if theirs_url is None:
        print("WARN: MINIPRO_XML_URL not found in build_db.py")
    elif theirs_url != MINIPRO_XML_URL:
        drift += 1
        print("DRIFT: pinned infoic.xml URL differs\n"
              f"  ours  : {MINIPRO_XML_URL}\n  theirs: {theirs_url}")
    else:
        print("ok: MINIPRO_XML_URL matches build_db.py")

    theirs_vpp = found.get("VPP_VOLTAGES")
    if not isinstance(theirs_vpp, dict):
        print("WARN: VPP_VOLTAGES not found in build_db.py")
    elif theirs_vpp != VPP_VOLTAGES:
        drift += 1
        keys = set(theirs_vpp) | set(VPP_VOLTAGES)
        print("DRIFT: VPP_VOLTAGES differs")
        for k in sorted(keys):
            a, b = VPP_VOLTAGES.get(k), theirs_vpp.get(k)
            if a != b:
                print(f"  0x{k:02X}: ours={a!r}  theirs={b!r}")
    else:
        print(f"ok: VPP_VOLTAGES matches build_db.py ({len(VPP_VOLTAGES)} entries)")

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
            f"  -> VPP {VPP_VOLTAGES.get(idx, 'NOT IN TABLE')}"
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

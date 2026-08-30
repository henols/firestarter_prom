#!/usr/bin/env python3
"""
tools/wiki/wiki.py -- single stdlib-only CLI for the in-repo wiki source
tree at wiki/ and its published GitHub wiki mirror.

Exit-code contract:
  0 = the asserted property holds
  1 = the asserted property is false
  2 = a precondition was not met (source directory missing, or wiki
      remote absent)

Determinism contract for every generated artifact (starting with
_Sidebar.md): pages are listed in sorted() order with Home first, no
timestamps, hostnames or hashes appear anywhere in the output, and every
write forces LF line endings via Path.write_text's newline argument,
regardless of platform. Two consecutive runs over an unchanged source
directory must produce byte-identical output.

--source-dir and --wiki-remote are parameters, not module constants,
because that is what makes every offline negative case testable against
a fixture before the operator creates the real GitHub wiki.

Subcommands:
  sidebar   generate or check _Sidebar.md from the wiki source tree
"""

from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
from pathlib import Path

DEFAULT_WIKI_REMOTE = "https://github.com/henols/firestarter_prom.wiki.git"
WIKI_BRANCH = "master"
DEFAULT_SOURCE_DIR = Path(__file__).resolve().parent.parent.parent / "wiki"
HOME_PAGE = "Home.md"
SIDEBAR_PAGE = "_Sidebar.md"
NAV_EXCLUDED_PAGES = ("_Sidebar.md", "_Footer.md")


def render_title(stem: str) -> str:
    return stem.replace("-", " ")


def page_files(source_dir: Path) -> list[Path]:
    return sorted(source_dir.glob("*.md"), key=lambda p: p.name)


def generate_sidebar(source_dir: Path) -> str:
    stems = [
        p.stem for p in page_files(source_dir) if p.name not in NAV_EXCLUDED_PAGES
    ]
    parts: list[str] = []
    if "Home" in stems:
        parts.append(f"- [{render_title('Home')}](Home)\n")
    for stem in sorted(s for s in stems if s != "Home"):
        parts.append(f"- [{render_title(stem)}]({stem})\n")
    return "".join(parts)


def cmd_sidebar(args: argparse.Namespace) -> int:
    target = args.source_dir / SIDEBAR_PAGE
    content = generate_sidebar(args.source_dir)
    entry_count = len(content.splitlines())

    if args.check:
        existing = target.read_text(encoding="utf-8") if target.is_file() else ""
        if existing != content:
            print(f"ERROR: {SIDEBAR_PAGE} is stale", file=sys.stderr)
            diff = difflib.unified_diff(
                existing.splitlines(keepends=True),
                content.splitlines(keepends=True),
                fromfile=str(target),
                tofile="generated",
            )
            sys.stderr.writelines(diff)
            return 1
        print(f"OK: {SIDEBAR_PAGE} is fresh ({entry_count} entries).")
        return 0

    target.write_text(content, encoding="utf-8", newline="\n")
    print(f"OK: wrote {target} ({entry_count} entries).")
    return 0


COMMANDS = {
    "sidebar": cmd_sidebar,
}


def _build_common_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE_DIR,
        help="In-repo wiki source tree to operate on. A fixture directory "
        "overrides this so every offline case is testable before the "
        "operator creates the GitHub wiki.",
    )
    common.add_argument(
        "--wiki-remote",
        default=DEFAULT_WIKI_REMOTE,
        help="Wiki git remote to publish to or check against. A local bare "
        "repository path is accepted so the publish path is testable "
        "before the GitHub wiki exists.",
    )
    return common


def _build_argparser() -> argparse.ArgumentParser:
    common = _build_common_parser()
    parser = argparse.ArgumentParser(
        prog="wiki.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[common],
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    sidebar_parser = subparsers.add_parser(
        "sidebar",
        parents=[common],
        help="Generate or check _Sidebar.md from the wiki source tree.",
    )
    sidebar_parser.add_argument(
        "--check",
        action="store_true",
        help="Validate _Sidebar.md against the generated content and exit "
        "0/1. No files written.",
    )

    return parser


def main() -> int:
    args = _build_argparser().parse_args()

    if not args.source_dir.is_dir():
        print(
            f"ERROR: source directory not found: {args.source_dir}",
            file=sys.stderr,
        )
        return 2

    return COMMANDS[args.command](args)


if __name__ == "__main__":
    sys.exit(main())

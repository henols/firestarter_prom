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
  links     check reachability from Home.md, internal link resolution and
            page filename legality
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
ILLEGAL_NAME_CHARS = '\\/:*?"<>|'
LEGAL_LINK_RE = re.compile(r"\[([^\]]*)\]\(([A-Za-z0-9][A-Za-z0-9-]*)(?:#([A-Za-z0-9_-]*))?\)")
EXTERNAL_LINK_PREFIXES = ("http://", "https://", "mailto:", "#")
_LEGAL_TARGET_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]*(?:#[A-Za-z0-9_-]*)?")
_DOUBLE_BRACKET_RE = re.compile(r"\[\[[^\]]*\]\]")
_REFERENCE_LINK_RE = re.compile(r"\[[^\]]*\]\[[^\]]*\]")
_PAREN_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def render_title(stem: str) -> str:
    return stem.replace("-", " ")


def page_files(source_dir: Path) -> list[Path]:
    return sorted(source_dir.glob("*.md"), key=lambda p: p.name)


def page_stems(source_dir: Path) -> list[str]:
    return [p.stem for p in page_files(source_dir)]


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


def strip_code_spans(text: str) -> str:
    def _fence_repl(match: re.Match[str]) -> str:
        return "\n" * match.group(0).count("\n")

    text = _FENCE_RE.sub(_fence_repl, text)
    return _INLINE_CODE_RE.sub(lambda match: " " * len(match.group(0)), text)


def extract_internal_links(page: Path) -> list[tuple[int, str, str]]:
    stripped = strip_code_spans(page.read_text(encoding="utf-8"))
    links: list[tuple[int, str, str]] = []
    for lineno, line in enumerate(stripped.splitlines(), start=1):
        remaining = line
        for match in _DOUBLE_BRACKET_RE.finditer(remaining):
            links.append((lineno, match.group(0), match.group(0)))
        remaining = _DOUBLE_BRACKET_RE.sub("", remaining)
        for match in _REFERENCE_LINK_RE.finditer(remaining):
            links.append((lineno, match.group(0), match.group(0)))
        remaining = _REFERENCE_LINK_RE.sub("", remaining)
        for match in LEGAL_LINK_RE.finditer(remaining):
            anchor = match.group(3)
            target = match.group(2) + (f"#{anchor}" if anchor is not None else "")
            links.append((lineno, match.group(1), target))
        remaining = LEGAL_LINK_RE.sub("", remaining)
        for match in _PAREN_LINK_RE.finditer(remaining):
            link_text, target = match.group(1), match.group(2)
            if target.startswith(EXTERNAL_LINK_PREFIXES):
                continue
            links.append((lineno, link_text, target))
    return links


def check_page_names(source_dir: Path) -> list[str]:
    failures: list[str] = []
    for entry in sorted(source_dir.iterdir(), key=lambda p: p.name):
        name = entry.name
        if entry.is_dir():
            failures.append(
                f"illegal page filename {name!r}: directory found in flat "
                "wiki/ tree"
            )
            continue
        problems: list[str] = []
        if entry.suffix != ".md":
            problems.append(f"suffix {entry.suffix!r} is not .md")
        illegal_found = sorted(set(name) & set(ILLEGAL_NAME_CHARS))
        if illegal_found:
            problems.append(
                f"contains illegal characters {illegal_found}; rejected set "
                f"is {sorted(ILLEGAL_NAME_CHARS)}"
            )
        if ".." in name:
            problems.append("contains '..'")
        if problems:
            failures.append(
                f"illegal page filename {name!r}: " + "; ".join(problems)
            )
    return failures


def check_link_forms(source_dir: Path) -> list[str]:
    failures: list[str] = []
    stems = set(page_stems(source_dir))
    lower_stems = {stem.lower() for stem in stems}
    for page in page_files(source_dir):
        if page.name in NAV_EXCLUDED_PAGES:
            continue
        for lineno, link_text, target in extract_internal_links(page):
            if not _LEGAL_TARGET_RE.fullmatch(target):
                if link_text == target:
                    failures.append(
                        f"illegal internal link form in {page.name}:{lineno}: "
                        f"{target} -- the only legal internal link form is "
                        "[Text](Page-Name) or [Text](Page-Name#anchor)"
                    )
                else:
                    failures.append(
                        f"illegal internal link form in {page.name}:{lineno}: "
                        f"[{link_text}]({target}) -- the only legal internal "
                        "link form is [Text](Page-Name) or "
                        "[Text](Page-Name#anchor)"
                    )
                continue
            base = target.split("#", 1)[0]
            if base in stems:
                continue
            if base.lower() in lower_stems:
                failures.append(
                    f"unresolved internal link in {page.name}:{lineno}: "
                    f"{target} does not match any page filename exactly "
                    "(case-sensitive; GitHub resolves this case-"
                    "insensitively and will never report the mismatch)"
                )
            else:
                failures.append(
                    f"unresolved internal link in {page.name}:{lineno}: "
                    f"{target} has no matching page"
                )
    return failures


def check_orphans(source_dir: Path) -> list[str]:
    failures: list[str] = []
    home = source_dir / HOME_PAGE
    if not home.is_file():
        failures.append(f"orphan check requires {HOME_PAGE} to exist")
        return failures
    reachable: set[str] = set()
    for _lineno, _link_text, target in extract_internal_links(home):
        if _LEGAL_TARGET_RE.fullmatch(target):
            reachable.add(target.split("#", 1)[0])
    home_stem = Path(HOME_PAGE).stem
    for stem in page_stems(source_dir):
        if stem == home_stem:
            continue
        if f"{stem}.md" in NAV_EXCLUDED_PAGES:
            continue
        if stem not in reachable:
            failures.append(f"orphan page not linked from {HOME_PAGE}: {stem}")
    return failures


def cmd_links(args: argparse.Namespace) -> int:
    source_dir = args.source_dir
    failures = check_page_names(source_dir)
    failures += check_link_forms(source_dir)
    failures += check_orphans(source_dir)
    if failures:
        for message in failures:
            print(f"ERROR: {message}", file=sys.stderr)
        return 1
    pages = [
        stem for stem in page_stems(source_dir) if f"{stem}.md" not in NAV_EXCLUDED_PAGES
    ]
    for stem in pages:
        print(f'{stem} -> "{render_title(stem)}"')
    print(
        f"OK: {len(pages)} pages, all reachable from {HOME_PAGE}, all "
        "internal links resolve, all filenames legal."
    )
    return 0


COMMANDS = {
    "sidebar": cmd_sidebar,
    "links": cmd_links,
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

    subparsers.add_parser(
        "links",
        parents=[common],
        help="Check reachability from Home.md, resolve internal links and "
        "validate page filenames.",
        description="The single legal internal link form is "
        "[Text](Page-Name) or [Text](Page-Name#anchor). A .md-suffixed "
        "link, a [[Page]] link, a reference-style [Text][ref] link and a "
        "wrong-case link are each rejected, because GitHub's read path "
        "silently tolerates all of them. Only Home.md links count as "
        "reachability evidence; the generated _Sidebar.md does not.",
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

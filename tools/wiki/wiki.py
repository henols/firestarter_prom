#!/usr/bin/env python3
"""
tools/wiki/wiki.py -- single stdlib-only CLI that checks a clone of the
published GitHub wiki for reachability, internal-link legality and
filename legality.

Exit-code contract:
  0 = the asserted property holds
  1 = the asserted property is false
  2 = a precondition was not met (source directory missing, or missing
      on the command line at all)

Subcommand:
  links   check reachability from Home.md, resolve internal links,
          validate page filenames, and confirm every page is listed in
          _Sidebar.md

--source-dir is a required argument, not a module constant with a
default. The wiki's former in-repo source tree under wiki/ was retired
along with the publish path it fed (a retired-but-present default would
either point at a directory that no longer exists -- a guaranteed
exit-2 -- or silently default to a "conventional" clone path and check
a stale or absent tree while still printing OK). Requiring the caller
to name the tree under test keeps every offline fixture case testable
without ever touching the operator's real wiki clone.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HOME_PAGE = "Home.md"
SIDEBAR_PAGE = "_Sidebar.md"
NAV_EXCLUDED_PAGES = ("_Sidebar.md", "_Footer.md")
ILLEGAL_NAME_CHARS = '\\/:*?"<>|'
LEGAL_LINK_RE = re.compile(r"\[([^\]]*)\]\(([A-Za-z0-9][A-Za-z0-9-]*)(?:#([A-Za-z0-9_-]*))?\)")
EXTERNAL_LINK_PREFIXES = ("http://", "https://", "mailto:", "#")
_LEGAL_TARGET_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]*(?:#[A-Za-z0-9_-]*)?")
_DOUBLE_BRACKET_RE = re.compile(r"\[\[[^\]]*\]\]")
_REFERENCE_LINK_RE = re.compile(r"\[([^\]]*)\]\[([^\]]*)\]")
_REFERENCE_DEF_RE = re.compile(r"^\[([^\]]+)\]:\s*(\S+)", re.MULTILINE)
_PAREN_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def render_title(stem: str) -> str:
    return stem.replace("-", " ")


def page_files(source_dir: Path) -> list[Path]:
    return sorted(source_dir.glob("*.md"), key=lambda p: p.name)


def page_stems(source_dir: Path) -> list[str]:
    return [p.stem for p in page_files(source_dir)]


def strip_code_spans(text: str) -> str:
    def _fence_repl(match: re.Match[str]) -> str:
        return "\n" * match.group(0).count("\n")

    text = _FENCE_RE.sub(_fence_repl, text)
    return _INLINE_CODE_RE.sub(lambda match: " " * len(match.group(0)), text)


def extract_reference_definitions(text: str) -> dict[str, str]:
    defs: dict[str, str] = {}
    for match in _REFERENCE_DEF_RE.finditer(text):
        defs[match.group(1).strip().lower()] = match.group(2).strip()
    return defs


def extract_internal_links(page: Path) -> list[tuple[int, str, str]]:
    raw = page.read_text(encoding="utf-8")
    ref_defs = extract_reference_definitions(raw)
    stripped = strip_code_spans(raw)
    links: list[tuple[int, str, str]] = []
    for lineno, line in enumerate(stripped.splitlines(), start=1):
        remaining = line
        for match in _DOUBLE_BRACKET_RE.finditer(remaining):
            links.append((lineno, match.group(0), match.group(0)))
        remaining = _DOUBLE_BRACKET_RE.sub("", remaining)
        for match in _REFERENCE_LINK_RE.finditer(remaining):
            link_text, ref_label = match.group(1), match.group(2)
            resolved_label = (ref_label or link_text).strip().lower()
            ref_target = ref_defs.get(resolved_label)
            if ref_target is not None and ref_target.startswith(EXTERNAL_LINK_PREFIXES):
                continue
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
        if name.startswith("."):
            continue
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


def check_sidebar_lists_every_page(source_dir: Path) -> list[str]:
    failures: list[str] = []
    sidebar = source_dir / SIDEBAR_PAGE
    if not sidebar.is_file():
        failures.append(
            f"sidebar containment check requires {SIDEBAR_PAGE} to exist"
        )
        return failures
    listed: set[str] = set()
    for _lineno, _link_text, target in extract_internal_links(sidebar):
        if _LEGAL_TARGET_RE.fullmatch(target):
            listed.add(target.split("#", 1)[0])
    for stem in page_stems(source_dir):
        if f"{stem}.md" in NAV_EXCLUDED_PAGES:
            continue
        if stem not in listed:
            failures.append(f"page missing from {SIDEBAR_PAGE}: {stem}")
    return failures


def cmd_links(args: argparse.Namespace) -> int:
    source_dir = args.source_dir
    failures = check_page_names(source_dir)
    failures += check_link_forms(source_dir)
    failures += check_orphans(source_dir)
    failures += check_sidebar_lists_every_page(source_dir)
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
        f"internal links resolve, all filenames legal, and all listed in "
        f"{SIDEBAR_PAGE}."
    )
    return 0


COMMANDS = {
    "links": cmd_links,
}


def _build_common_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--source-dir",
        type=Path,
        required=True,
        help="Wiki clone (or fixture directory) to operate on. Required: "
        "the wiki's former in-repo source tree no longer exists, so there "
        "is no default that is not either a guaranteed exit-2 or a silent "
        "check of the wrong tree.",
    )
    return common


def _build_argparser() -> argparse.ArgumentParser:
    common = _build_common_parser()
    parser = argparse.ArgumentParser(
        prog="wiki.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "links",
        parents=[common],
        help="Check reachability from Home.md, resolve internal links, "
        "validate page filenames, and confirm every page is listed in "
        "_Sidebar.md.",
        description="The single legal internal link form is "
        "[Text](Page-Name) or [Text](Page-Name#anchor). A .md-suffixed "
        "link, a [[Page]] link, a reference-style [Text][ref] link and a "
        "wrong-case link are each rejected, because GitHub's read path "
        "silently tolerates all of them. Only Home.md links count as "
        "reachability evidence; _Sidebar.md is checked separately for "
        "completeness (every page must be listed in it), not for "
        "reachability.",
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

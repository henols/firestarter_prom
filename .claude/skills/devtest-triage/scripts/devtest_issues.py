#!/usr/bin/env python3
"""List and parse community `dev test` chip-validation issues.

Self-contained: stdlib only, plus the `gh` CLI for GitHub access. This skill
owns this parser outright — it does not import or shell out to any script in
firestarter_app or firestarter, so it keeps working if those repos move.

    devtest_issues.py list                  # open [dev test] issues + verdicts
    devtest_issues.py list --state all
    devtest_issues.py show 32               # parse one issue
    devtest_issues.py show --body-file b.txt --title "$T"   # offline
    devtest_issues.py fold                  # group issues by EPROM (dry run)
    devtest_issues.py fold --apply          # comment on canonical, close the rest

UNTRUSTED INPUT. Every issue body is community-authored and treated as hostile:
the body is size-bounded before parsing, never `eval`/`exec`d, never shelled
out, never interpolated into a command. Every extraction fails soft (returns
None / skips) rather than raising.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

REPO = "henols/firestarter_prom"
DEFAULT_DB = os.environ.get(
    "FIRESTARTER_DB",
    "/workspaces/firestarter_app/firestarter/data/chip_database.json",
)

# Cap before parsing — a hostile body must not be able to exhaust memory.
MAX_BODY = 1_000_000

# Literal #3 of three (D-11/D-16, v1.32 Phase 147 plan 147-06). Identical in
# VALUE to `firestarter/diagnostic_report.py`'s `NOT_REPORTED` (147-03) and
# `firestarter_app/tools/parse_devtest_issue.py`'s `NOT_REPORTED` (147-05),
# but defined separately here rather than imported: skills own their
# scripts (module docstring above, `:4-6`) and this file lives in a
# DIFFERENT repo entirely (the meta repo, not firestarter_app), so importing
# either module would break the moment that repo moves or is not checked
# out. The app suite's value-parity test
# (`tests/test_parse_devtest_issue.py::test_unknown_marker_string_matches_the_report_model`)
# covers only the other two literals — it cannot reach into
# `/workspaces/.claude/` without coupling the app CI to a meta-repo path
# (that would fail OPEN in standalone CI, RESEARCH P-6). This literal's
# parity with the other two is instead proven by the 147-06 plan's
# checkpoint (Task 3), which greps this constant into the render output and
# a human confirms it there. Not automated — no substitute is invented.
NOT_REPORTED = "not reported"

# D-14/D-17: one action-oriented clause, true under EITHER reading of an
# absent identity (an old report whose host build never captured it, or a
# post-bump report where capture failed) — no schema-version ordering logic
# is added here or anywhere else. Same value as the other two modules'
# clause. Checked by this script's own no-forbidden-vocabulary grep leg in
# 147-06's acceptance criteria; the checkpoint's step 7 re-checks it by a
# human read of the same boundary.
NOT_ATTRIBUTABLE = (
    "NOT attributable to a firmware version -- ask the reporter for a "
    "fresh dev test run on a current host build"
)

# submit.py:build_title — "[dev test] <chip> — <VERDICT> (<fingerprint>)".
# Accepts an em dash or a plain hyphen so a hand-edited title still parses.
TITLE_RE = re.compile(
    r"^\[dev test\]\s+(?P<chip>\S+)\s+[—-]\s+(?P<verdict>[A-Za-z]+)"
)
FENCE_RE = re.compile(r"```(?:json)?\s*\n(.*?)```", re.DOTALL)

BAD = {"BAD", "FAIL"}
SOFT = {"MARGINAL", "INCONCLUSIVE"}
OK = {"OK", "NA", "SKIPPED"}


def gh(args: list[str]) -> str:
    """Run gh with a fixed argv list. Never uses a shell."""
    try:
        r = subprocess.run(
            ["gh", *args], capture_output=True, text=True, timeout=120, check=False
        )
    except FileNotFoundError:
        sys.exit("error: `gh` not found — install the GitHub CLI")
    except subprocess.TimeoutExpired:
        sys.exit("error: `gh` timed out")
    if r.returncode != 0:
        sys.exit(f"error: gh {' '.join(args)} failed: {r.stderr.strip()[:400]}")
    return r.stdout


def parse_title(title: str) -> dict | None:
    m = TITLE_RE.match((title or "").strip())
    return m.groupdict() if m else None


def extract_report(body: str) -> dict | None:
    """Return the embedded diagnostic report.

    Detection requires a fenced block whose parsed object carries
    `schema_version` — accepted by PRESENCE, not by exact value, so a schema
    bump does not need a code change here. Defensive against unrelated fenced
    blocks elsewhere in the issue: every block is tried, the first qualifying
    one wins.
    """
    if not body:
        return None
    for block in FENCE_RE.findall(body[:MAX_BODY]):
        try:
            obj = json.loads(block)
        except (json.JSONDecodeError, ValueError, RecursionError):
            continue
        if isinstance(obj, dict) and "schema_version" in obj:
            return obj
    return None


def is_devtest(title: str, body: str) -> bool:
    """Both markers required: the title marker AND a schema_version report."""
    return parse_title(title) is not None and extract_report(body) is not None


def fingerprint(report: dict | None, body: str) -> str:
    if isinstance(report, dict):
        fp = report.get("dedup_fingerprint")
        if isinstance(fp, str) and re.fullmatch(r"[0-9a-f]{4,32}", fp):
            return fp
    m = re.search(r'"dedup_fingerprint"\s*:\s*"([0-9a-f]{4,32})"', body or "")
    return m.group(1) if m else "-"


def cmd_list(args: argparse.Namespace) -> int:
    raw = gh([
        "issue", "list", "--repo", args.repo, "--state", args.state,
        "--limit", str(args.limit), "--json", "number,title,body",
    ])
    try:
        issues = json.loads(raw)
    except json.JSONDecodeError:
        sys.exit("error: gh returned unparseable JSON")

    rows = []
    for i in issues:
        t = parse_title(i.get("title", ""))
        if not t:
            continue
        body = i.get("body") or ""
        rep = extract_report(body)
        rows.append((
            i.get("number", 0), t["verdict"].upper(), t["chip"],
            fingerprint(rep, body), "" if rep else "  (no JSON report)",
        ))

    rows.sort(key=lambda r: -r[0])
    for n, verdict, chip, fp, note in rows:
        print(f"#{n:<5}{verdict:<15}{chip:<15}{fp}{note}")
    if not rows:
        print("no [dev test] issues found")
    return 0


def load_alias_map(db_path: str) -> dict[str, str]:
    """chip token -> canonical EPROM key, from the chip database if readable.

    Two issues can name one EPROM differently (`w27c020` / `w27e020` are the
    same DB entry). Without this, folding is only string-deep. Degrades to {}
    when the database is absent — the caller then falls back to normalisation.
    Reads the JSON as DATA; imports nothing.
    """
    try:
        with open(db_path, encoding="utf-8") as f:
            db = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}
    out: dict[str, str] = {}
    for mfg, chips in (db.items() if isinstance(db, dict) else []):
        if not isinstance(chips, list):
            continue
        for entry in chips:
            if not isinstance(entry, dict):
                continue
            pn = entry.get("part_number", "")
            key = f"{mfg}/{pn.split(',')[0].strip()}"
            for tok in pn.split(","):
                norm = re.sub(r"[^a-z0-9]", "", tok.strip().lower())
                if norm:
                    out.setdefault(norm, key)
    return out


def eprom_key(chip: str, aliases: dict[str, str]) -> str:
    norm = re.sub(r"[^a-z0-9]", "", chip.lower())
    return aliases.get(norm, norm)


def _summarize(issue: dict) -> dict | None:
    t = parse_title(issue.get("title", ""))
    if not t:
        return None
    body = issue.get("body") or ""
    rep = extract_report(body) or {}
    steps = rep.get("steps") or []
    failing = [str(s.get("op")) for s in steps if isinstance(s, dict)
               and str(s.get("verdict", "")).upper() in BAD | SOFT]
    auto = rep.get("auto_capture") or {}
    return {
        "number": issue.get("number", 0),
        "chip": t["chip"],
        "verdict": t["verdict"].upper(),
        "fp": fingerprint(rep, body),
        "host": auto.get("host_version") or "?",
        "generated": (rep.get("generated") or "?")[:10],
        "failing": failing,
    }


def cmd_fold(args: argparse.Namespace) -> int:
    """Group open issues by EPROM and fold each group into one canonical issue."""
    raw = gh([
        "issue", "list", "--repo", args.repo, "--state", "open",
        "--limit", str(args.limit), "--json", "number,title,body",
    ])
    try:
        issues = json.loads(raw)
    except json.JSONDecodeError:
        sys.exit("error: gh returned unparseable JSON")

    aliases = load_alias_map(args.db)
    if not aliases:
        print("note: chip database not readable — grouping by chip NAME only; "
              "alias-different names for one EPROM will not group\n", file=sys.stderr)

    groups: dict[str, list[dict]] = {}
    for i in issues:
        s = _summarize(i)
        if s:
            groups.setdefault(eprom_key(s["chip"], aliases), []).append(s)

    multi = {k: sorted(v, key=lambda r: r["number"])
             for k, v in groups.items() if len(v) > 1}
    if not multi:
        print("nothing to fold — every open EPROM has a single issue")
        return 0

    planned = []
    for key, members in sorted(multi.items()):
        verdicts = {m["verdict"] for m in members}
        all_pass = verdicts <= {"PASS"}
        # Canonical = oldest actionable issue; an all-PASS group keeps the oldest.
        actionable = [m for m in members if m["verdict"] != "PASS"]
        canonical = (actionable or members)[0]
        if args.canonical:
            match = [m for m in members if m["number"] == args.canonical]
            if match:
                canonical = match[0]
        dupes = [m for m in members if m["number"] != canonical["number"]]

        names = sorted({m["chip"] for m in members})
        print(f"\n{key}   ({', '.join(names)})")
        if all_pass:
            print("  ALL PASS — do not fold. Close each and log the chip "
                  "(triage §4); a fold would bury a clean result.")
            continue
        print(f"  canonical #{canonical['number']}   fold in: "
              f"{', '.join('#' + str(m['number']) for m in dupes)}")
        for m in members:
            same = [o["number"] for o in members
                    if o["fp"] == m["fp"] and o["number"] != m["number"]
                    and m["fp"] != "-"]
            tags = []
            if same:
                tags.append("same fingerprint as "
                            + ", ".join(f"#{n}" for n in same))
            if m["verdict"] == "PASS":
                tags.append("PASS — folds as EVIDENCE, does not close the canonical")
            mark = "*" if m["number"] == canonical["number"] else " "
            print(f"   {mark}#{m['number']:<4} {m['verdict']:<13}{m['fp']}  "
                  f"host {m['host']}  {m['generated']}  "
                  f"failing: {', '.join(m['failing']) or '-'}"
                  + (f"   [{'; '.join(tags)}]" if tags else ""))
        planned.append((key, names, canonical, dupes, members))

    if not planned:
        return 0
    if not args.apply:
        print(f"\nDRY RUN — {len(planned)} group(s) would be folded. "
              "Re-run with --apply to comment and close.")
        return 0

    for key, names, canonical, dupes, members in planned:
        rows = "\n".join(
            f"| #{m['number']} | {m['verdict']} | `{m['fp']}` | {m['host']} | "
            f"{m['generated']} | {', '.join(m['failing']) or '—'} |"
            for m in members
        )
        summary = (
            f"### Consolidated reports for {' / '.join(names)}\n\n"
            f"{len(members)} `dev test` reports describe this EPROM. Folding them "
            f"here so it is triaged once.\n\n"
            "| Issue | Verdict | Fingerprint | Host | Report date | Failing steps |\n"
            "|---|---|---|---|---|---|\n" + rows + "\n\n"
            "Issues sharing a fingerprint are the same failure re-reported. A PASS "
            "row is evidence (the chip can work — suspect intermittency or a since-"
            "fixed path), not grounds to close this issue.\n"
        )
        gh(["issue", "comment", str(canonical["number"]), "--repo", args.repo,
            "--body", summary])
        print(f"commented on #{canonical['number']}")
        for m in dupes:
            gh(["issue", "close", str(m["number"]), "--repo", args.repo,
                "--comment",
                f"Folded into #{canonical['number']} — same EPROM "
                f"({m['chip']}). This report is preserved in the consolidated "
                f"table there. Continue the discussion on "
                f"#{canonical['number']}."])
            print(f"  closed #{m['number']} -> #{canonical['number']}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    if args.number is not None:
        title = gh(["issue", "view", str(args.number), "--repo", args.repo,
                    "--json", "title", "-q", ".title"]).strip()
        body = gh(["issue", "view", str(args.number), "--repo", args.repo,
                   "--json", "body", "-q", ".body"])
    else:
        if not args.body_file:
            sys.exit("error: pass an issue NUMBER, or --body-file with --title")
        title = args.title or ""
        try:
            with open(args.body_file, encoding="utf-8", errors="replace") as f:
                body = f.read(MAX_BODY + 1)
        except OSError as exc:
            sys.exit(f"error: cannot read body file: {exc}")

    if len(body) > MAX_BODY:
        print(f"warning: body over {MAX_BODY} bytes — truncated for parsing",
              file=sys.stderr)
        body = body[:MAX_BODY]

    t = parse_title(title)
    report = extract_report(body)
    if not t or not report:
        print("NOT a parseable `dev test` issue "
              f"(title marker: {'yes' if t else 'no'}, "
              f"JSON report: {'yes' if report else 'no'})")
        return 1

    auto = report.get("auto_capture") or {}
    steps = report.get("steps") or []
    volt = report.get("voltage") or {}
    dbd = report.get("db_diff") or {}

    print(f"#{args.number if args.number is not None else '?'}  "
          f"{t['chip']}  —  {t['verdict'].upper()}")
    print(f"  schema      {report.get('schema_version')}   "
          f"generated {report.get('generated')}")

    # Explicit two-clause `is None or == ""` conditions, never an
    # `or`-coalescing expression — an `or` also fires on `""`, which hides
    # the empty-string transport fault D-07/P-8 want visible. Mirrors the
    # `cid_e is not None` idiom already used below for the chip-id pair.
    host_version = auto.get("host_version")
    host_version_cell = (
        NOT_REPORTED if host_version is None or host_version == ""
        else host_version
    )
    hw_revision = auto.get("hw_revision")
    hw_revision_cell = (
        NOT_REPORTED if hw_revision is None or hw_revision == ""
        else hw_revision
    )
    print(f"  host        {host_version_cell}   hw {hw_revision_cell}")

    # Firmware identity row (PROV-06/D-14/D-15/D-16), placed directly after
    # the host/hw row so provenance reads as one block. `hw_revision` above
    # stays out of this marker's scope (D-15) — it is a coarse silkscreen
    # bucket that cannot discriminate the operator's Rev 2.2 / Rev 2.0 /
    # modified Rev 0 boards, so it is fixed for its own bare-null defect
    # (D-12) but never treated as attribution evidence.
    fw_board_identity = auto.get("fw_board_identity")
    identity_absent = fw_board_identity is None or fw_board_identity == ""
    firmware_cell = (
        f"{NOT_REPORTED} -- {NOT_ATTRIBUTABLE}" if identity_absent
        else fw_board_identity
    )
    print(f"  firmware    {firmware_cell}")

    print(f"  protocol    {auto.get('protocol')}   chip {auto.get('chip')}")
    cid_e, cid_a = auto.get("chip_id_expected"), auto.get("chip_id_actual")
    if cid_e is not None or cid_a is not None:
        exp = f"0x{cid_e:X}" if isinstance(cid_e, int) else str(cid_e)
        act = f"0x{cid_a:X}" if isinstance(cid_a, int) else str(cid_a)
        print(f"  chip id     expected {exp}  actual {act}")
    print(f"  fingerprint {fingerprint(report, body)}")

    print("\n  step         verdict    reason")
    failing, soft = [], []
    for s in steps:
        if not isinstance(s, dict):
            continue
        op = str(s.get("op", "?"))
        v = str(s.get("verdict", "?"))
        reason = str(s.get("reason") or "")[:90]
        print(f"  {op:<12} {v:<10} {reason}")
        if v.upper() in BAD:
            failing.append(op)
        elif v.upper() in SOFT:
            soft.append(op)

    if volt:
        print(f"\n  voltage     vpp {volt.get('vpp_before_mv')} -> "
              f"{volt.get('vpp_after_mv')} mV   "
              f"vpe {volt.get('vpe_before_mv')} -> {volt.get('vpe_after_mv')} mV")
    if dbd:
        print(f"  db_diff     status={dbd.get('current_support_status')}  "
              f"ladder={dbd.get('ladder_state')}")

    print()
    if failing:
        print(f"  ROUTE: FAIL — datasheet cross-check needed. Failing: "
              f"{', '.join(failing)}")
    elif soft:
        print(f"  ROUTE: MARGINAL — datasheet cross-check needed. Marginal: "
              f"{', '.join(soft)}")
    else:
        print("  ROUTE: PASS — every applicable step OK/NA/SKIPPED. "
              "Close the issue and log the chip.")
    print("  NA means the step does not apply to this family — never report it "
          "as a failure.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--repo", default=REPO, help=f"default {REPO}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list", help="list [dev test] issues with verdicts")
    p.add_argument("--state", default="open", choices=["open", "closed", "all"])
    p.add_argument("--limit", type=int, default=200)
    p.set_defaults(fn=cmd_list)

    p = sub.add_parser(
        "fold", help="group open issues by EPROM and fold each group into one")
    p.add_argument("--limit", type=int, default=200)
    p.add_argument("--db", default=DEFAULT_DB,
                   help="chip database, read as data for alias-aware grouping")
    p.add_argument("--canonical", type=int,
                   help="force this issue number as the canonical one")
    p.add_argument("--apply", action="store_true",
                   help="actually comment and close (default is a dry run)")
    p.set_defaults(fn=cmd_fold)

    p = sub.add_parser("show", help="parse one issue and route it")
    p.add_argument("number", nargs="?", type=int)
    p.add_argument("--title", help="issue title (with --body-file)")
    p.add_argument("--body-file", help="issue body on disk (offline mode)")
    p.set_defaults(fn=cmd_show)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())

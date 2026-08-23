#!/usr/bin/env python3
"""
pytest coverage for remap_citations.py -- SWEEP-11's whole proof burden.

The tool is BUILT in Phase 154 and APPLIED in Phase 159 (D-01/D-10), so nothing
else in the repository ever exercises it. Every property the requirement names
is therefore proven here against committed synthetic fixtures, and two of the
tests exist purely to prove that the proofs are DISCRIMINATING rather than
accidentally green.

Tests (expected exit code / requirement discharged):
   1. build_map on the committed fixture pair is EXACTLY the 20->15 map with two
      separated non-surviving runs -- n/a (unit) / SWEEP-11.
   2. A range spanning both deleted blocks SHRINKS: old 3-18 (span 16) becomes
      new 3-13 (span 11) -- n/a (unit) / SWEEP-11, REMAP-03.
   3. A constant-offset implementation FAILS test 2, so test 2 is not vacuous
      (it would produce -2-13) -- n/a (unit) / anti-vacuity for SWEEP-11.
   4. The fixture's map contains a CHAIN (map[a]=b and map[b]=c, c != b) and at
      least two separated non-surviving runs. Runs BEFORE the idempotency
      assertion, because a one-deletion-block fixture cannot produce a chain and
      would pass even against a blind implementation -- n/a (unit) / SWEEP-11.
   5. A BLIND remapper drifts along that chain (15 -> 10 -> 8 -> 6), so test 6 is
      not vacuous -- n/a (unit) / anti-vacuity for SWEEP-11.
   6. Idempotent on the chained map: run 1 rewrites, runs 2 and 3 are EXACT
      byte-for-byte no-ops -- exit 0 / SWEEP-11.
   7. A range whose BOTH endpoints chain keeps a STABLE span across runs 1, 2
      and 3 -- exit 0 / SWEEP-11, REMAP-03.
   8. A colon_list element does not drift (`10,15` stays `10,15`). This is the
      regression the chained fixture caught while this plan was executed --
      exit 0 / SWEEP-11.
   9. `manifest_empty.jsonl` (header only, zero records) exits 2 -- exit 2 /
      SWEEP-11, D-09.
  10. The module has no location-derived root: neither `_HERE` nor `__file__`
      appears in it, `autojunk=False` does, and the docstring carries the house
      `Exit codes:` block -- n/a (source) / SWEEP-11, D-09.
  11. The difflib map agrees EXACTLY with an independently-parsed `git diff -U0`
      unified-hunk map on a real ~500-line repository file -- n/a (unit) /
      SWEEP-11, T-154-18.
  12. `autojunk=True` really would corrupt the map on a real ~900-line source
      file, so `autojunk=False` is load-bearing rather than decorative --
      n/a (unit) / T-154-18.  Skips if the firmware sub-repo is not populated.
  13. `replace` is treated as non-surviving: a reflowed line maps to None and its
      citation is flagged retarget, not assigned a positional number --
      exit 0 / SWEEP-11.
  14. Dry run (no `--apply`) writes nothing at all -- exit 0 / SWEEP-11, D-01.
  15. An oracle violation exits 1 and writes NOTHING, not even the records that
      would have succeeded -- exit 1 / REMAP-02, T-154-17.
  16. A record whose `target_file_resolved` does not exist exits 1 -- exit 1 /
      D-09.
  17. An unloadable manifest exits 2, kept distinct from a real BLOCK -- exit 2 /
      D-09.
  18. A `..`-carrying `planning_file` is refused and nothing is written --
      exit 1 / ASVS V5.
  19. The tool was NOT applied to any real citation-bearing `.planning/`
      document in this phase -- n/a (repo) / SWEEP-11, D-01, D-10, T-154-21.

`_HERE` IS correct in this file: the ban is on the TOOL deriving its scan root,
not on a test locating its own sibling fixtures.
"""

import json
import os
import re
import shutil
import subprocess
import sys

import pytest

# ---------------------------------------------------------------------------
# Paths. `_HERE` is legitimate here -- see the module docstring.
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_TOOL = os.path.join(_HERE, "remap_citations.py")
_FIXTURES = os.path.join(_HERE, "fixtures")
_CHAINED_OLD = os.path.join(_FIXTURES, "citations_chained_old.txt")
_CHAINED_NEW = os.path.join(_FIXTURES, "citations_chained_new.txt")
_MANIFEST_MIN = os.path.join(_FIXTURES, "manifest_min.jsonl")
_MANIFEST_EMPTY = os.path.join(_FIXTURES, "manifest_empty.jsonl")
_DOC_MIN = os.path.join(_FIXTURES, "doc_min.md")
_CITATION_PATHS = os.path.join(_HERE, "citation_paths.py")

if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import remap_citations as rc  # noqa: E402 -- sys.path is prepared above

#: The target the fixture manifest cites, and the two content sides.
_TARGET_REL = "firestarter/src/chained_demo.cpp"
_DOC_REL = ".planning/doc_min.md"

#: The map the committed fixture pair MUST produce. Stated here so a fixture
#: edit that silently changes the map fails loudly instead of weakening every
#: test below.
_EXPECTED_MAP = {
    1: 1, 2: 2, 3: 3, 4: None, 5: None, 6: 4, 7: 5, 8: 6, 9: 7, 10: 8,
    11: None, 12: None, 13: None, 14: 9, 15: 10, 16: 11, 17: 12, 18: 13,
    19: 14, 20: 15,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _read_lines(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read().splitlines()


def _git(repo, *args):
    return subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.email=remap-test@example.invalid",
            "-c",
            "user.name=remap test",
            *args,
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def _shown(result, expected):
    return (
        f"Expected exit {expected} but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


class Harness:
    """A throwaway git repository holding the fixture's pre- and post-sweep sides.

    The pre-sweep side is COMMITTED and then overwritten on disk, because the
    tool must read the old content from git -- by the time Phase 159 runs, the
    pre-sweep content exists nowhere on disk. No escape hatch is provided for
    the test, so the tested code path is the production code path.
    """

    def __init__(self, tmp_path, old_lines=None, new_lines=None, doc_text=None):
        self.root = tmp_path / "repo"
        (self.root / "firestarter" / "src").mkdir(parents=True)
        (self.root / ".planning").mkdir(parents=True)
        self.target = self.root / _TARGET_REL
        self.doc = self.root / _DOC_REL
        self.manifest = tmp_path / "manifest.jsonl"

        old = old_lines if old_lines is not None else _read_lines(_CHAINED_OLD)
        new = new_lines if new_lines is not None else _read_lines(_CHAINED_NEW)
        self.old_lines, self.new_lines = old, new

        self.target.write_text("\n".join(old) + "\n", encoding="utf-8")
        if doc_text is None:
            shutil.copyfile(_DOC_MIN, self.doc)
        else:
            self.doc.write_text(doc_text, encoding="utf-8")
        shutil.copyfile(_MANIFEST_MIN, self.manifest)

        assert _git(self.root, "init", "-q").returncode == 0
        assert _git(self.root, "add", "-A").returncode == 0
        assert _git(self.root, "commit", "-qm", "pre-sweep").returncode == 0
        self.sha = _git(self.root, "rev-parse", "HEAD").stdout.strip()
        assert len(self.sha) == 40, self.sha

        # The sweep: the pre-sweep content now exists only in git.
        self.target.write_text("\n".join(new) + "\n", encoding="utf-8")

    def load_manifest(self):
        header, records = None, []
        for line in self.manifest.read_text(encoding="utf-8").splitlines():
            obj = json.loads(line)
            if "_schema" in obj:
                header = obj
            else:
                records.append(obj)
        return header, records

    def write_manifest(self, header, records):
        with open(self.manifest, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(header, ensure_ascii=False) + "\n")
            for rec in records:
                handle.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def run(self, *extra, manifest=None):
        return subprocess.run(
            [
                sys.executable,
                _TOOL,
                str(self.root),
                "--manifest",
                str(manifest or self.manifest),
                "--pre-sweep-sha",
                self.sha,
                *extra,
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def apply(self, *extra):
        return self.run("--apply", "--quiet-notes", *extra)

    def doc_text(self):
        return self.doc.read_text(encoding="utf-8")

    def cited(self, lineno):
        """The citation as it currently reads on `lineno` of the citing doc."""
        line = self.doc_text().splitlines()[lineno - 1]
        match = rc.CITATION_RE.search(line)
        assert match, f"no citation on line {lineno}: {line!r}"
        return match.group(0)


@pytest.fixture
def harness(tmp_path):
    return Harness(tmp_path)


def _naive_offset_range(map_, a, b):
    """A CONSTANT-OFFSET range mapping -- the wrong implementation, for contrast.

    It takes the offset measured at the range END and applies it to both
    endpoints, which is what "translate the citation" means. It must fail the
    shrink assertion.
    """
    offset = map_[b] - b
    return a + offset, b + offset


def _blind_apply(map_, number, runs):
    """A BLIND remapper: apply the map to whatever integer is found, every run."""
    seen = []
    for _ in range(runs):
        number = map_.get(number) or number
        seen.append(number)
    return seen


def _map_from_unified_diff(diff_text, n_old):
    """old 1-based line -> new 1-based line, parsed from `git diff -U0` hunks.

    An INDEPENDENT second implementation of the same mapping, used only to
    cross-check difflib on a real file. Removed lines map to None, exactly as
    the tool treats `delete`/`replace`.
    """
    hunk = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
    result, cursor, offset = {}, 1, 0
    for line in diff_text.splitlines():
        found = hunk.match(line)
        if not found:
            continue
        a = int(found.group(1))
        b = 1 if found.group(2) is None else int(found.group(2))
        d = 1 if found.group(4) is None else int(found.group(4))
        if b == 0:
            # Pure insertion AFTER old line `a`: that line keeps the old offset.
            for ln in range(cursor, a + 1):
                result[ln] = ln + offset
            cursor = a + 1
        else:
            for ln in range(cursor, a):
                result[ln] = ln + offset
            for ln in range(a, a + b):
                result[ln] = None
            cursor = a + b
        offset += d - b
    for ln in range(cursor, n_old + 1):
        result[ln] = ln + offset
    return result


def _none_runs(map_, n_old):
    """Maximal runs of non-surviving old lines, in order."""
    runs, current = [], []
    for line in range(1, n_old + 1):
        if map_.get(line) is None:
            current.append(line)
        elif current:
            runs.append(current)
            current = []
    if current:
        runs.append(current)
    return runs


def _record(planning_line, variant, cited, start, end, old_lines):
    return {
        "planning_file": _DOC_REL,
        "planning_line": planning_line,
        "variant": variant,
        "target_file_cited": cited,
        "target_file_resolved": _TARGET_REL,
        "resolution": "exact",
        "resolution_reason": "test-authored record",
        "target_line": start,
        "target_line_end": end,
        "source_text": old_lines[start - 1],
        "source_text_end": None if end is None else old_lines[end - 1],
        "text_status": "read",
        "text_status_end": None if end is None else "read",
        "retarget": False,
    }


# ---------------------------------------------------------------------------
# Test 1 -- the committed fixture pair produces exactly the expected map
# ---------------------------------------------------------------------------
def test_fixture_pair_produces_the_expected_map():
    old, new = _read_lines(_CHAINED_OLD), _read_lines(_CHAINED_NEW)
    assert len(old) == 20 and len(new) == 15, (len(old), len(new))
    assert rc.build_map(old, new) == _EXPECTED_MAP


# ---------------------------------------------------------------------------
# Test 2 -- SWEEP-11 / REMAP-03: a range spanning a deleted block SHRINKS
# ---------------------------------------------------------------------------
def test_range_spanning_deleted_block_shrinks():
    old, new = _read_lines(_CHAINED_OLD), _read_lines(_CHAINED_NEW)
    map_ = rc.build_map(old, new)
    start, end, retarget = rc.map_range(map_, 3, 18, len(old))
    assert (start, end, retarget) == (3, 13, False)
    old_span, new_span = 18 - 3 + 1, end - start + 1
    # The SPAN must change. This is the assertion a constant-offset
    # implementation fails -- see the next test.
    assert new_span != old_span, "the span did not change: this is a translate"
    assert old_span - new_span == 5, (old_span, new_span)
    deleted = sum(1 for line in range(3, 19) if map_[line] is None)
    assert old_span - new_span == deleted == 5


# ---------------------------------------------------------------------------
# Test 3 -- anti-vacuity: a constant-offset implementation FAILS test 2
# ---------------------------------------------------------------------------
def test_a_constant_offset_implementation_fails_the_shrink_leg():
    old, new = _read_lines(_CHAINED_OLD), _read_lines(_CHAINED_NEW)
    map_ = rc.build_map(old, new)
    naive = _naive_offset_range(map_, 3, 18)
    assert naive == (-2, 13), naive
    assert naive[1] - naive[0] + 1 == 18 - 3 + 1, "a translate preserves the span"
    assert naive != rc.map_range(map_, 3, 18, len(old))[:2]


# ---------------------------------------------------------------------------
# Test 4 -- the fixture's map really contains a CHAIN. MUST run before the
# idempotency assertion: a one-deletion-block fixture cannot produce a chain and
# would pass even against a blind implementation (research Pitfall 3).
# ---------------------------------------------------------------------------
def test_chained_map_has_a_chain():
    old, new = _read_lines(_CHAINED_OLD), _read_lines(_CHAINED_NEW)
    map_ = rc.build_map(old, new)
    chains = [
        (a, map_[a], map_[map_[a]])
        for a in sorted(map_)
        if map_[a] is not None
        and map_[a] in map_
        and map_[map_[a]] is not None
        and map_[map_[a]] != map_[a]
    ]
    assert chains, "the fixture map contains NO chain -- the idempotency leg would be vacuous"
    assert (15, 10, 8) in chains, chains

    runs = _none_runs(map_, len(old))
    assert len(runs) >= 2, f"only {len(runs)} non-surviving run(s): no chain possible"
    assert runs == [[4, 5], [11, 12, 13]], runs
    # The runs are SEPARATED by at least one surviving line.
    assert runs[1][0] - runs[0][-1] > 1


# ---------------------------------------------------------------------------
# Test 5 -- anti-vacuity: a BLIND remapper drifts along that chain
# ---------------------------------------------------------------------------
def test_a_blind_remapper_drifts_along_the_chain():
    old, new = _read_lines(_CHAINED_OLD), _read_lines(_CHAINED_NEW)
    map_ = rc.build_map(old, new)
    assert _blind_apply(map_, 15, 3) == [10, 8, 6]


# ---------------------------------------------------------------------------
# Test 6 -- SWEEP-11: idempotent on the chained map
# ---------------------------------------------------------------------------
def test_idempotent_on_chained_map(harness):
    before = harness.doc_text()
    assert harness.cited(3).endswith(":15")

    first = harness.apply()
    assert first.returncode == 0, _shown(first, 0)
    after_run_1 = harness.doc_text()
    assert after_run_1 != before
    assert harness.cited(3).endswith(":10"), harness.cited(3)
    assert "7 rewritten" in first.stdout, first.stdout

    second = harness.apply()
    assert second.returncode == 0, _shown(second, 0)
    assert harness.doc_text() == after_run_1, "run 2 was not an exact no-op"
    assert "0 rewritten" in second.stdout and "7 already at their fixed point" in second.stdout

    third = harness.apply()
    assert third.returncode == 0, _shown(third, 0)
    assert harness.doc_text() == after_run_1, "run 3 was not an exact no-op"
    assert harness.cited(3).endswith(":10")


# ---------------------------------------------------------------------------
# Test 7 -- SWEEP-11: a range whose BOTH endpoints chain keeps a stable span
# ---------------------------------------------------------------------------
def test_idempotent_range_span_is_stable(harness):
    old, new = harness.old_lines, harness.new_lines
    map_ = rc.build_map(old, new)
    # Both endpoints of old 10-20 chain: map[10]=8 with map[8]=6, and
    # map[20]=15 with map[15]=10. A blind implementation shrinks it again.
    assert map_[map_[10]] == 6 and map_[map_[20]] == 10

    assert harness.cited(5).endswith(":10-20")
    spans = []
    for _ in range(3):
        assert harness.apply().returncode == 0
        text = harness.cited(5)
        start, end = (int(n) for n in text.rsplit(":", 1)[1].split("-"))
        spans.append((start, end, end - start + 1))
    assert spans[0] == (8, 15, 8), spans
    assert spans[1] == spans[0] and spans[2] == spans[0], spans
    # A blind implementation would have gone 8-15 -> 6-10 on run 2.
    assert _blind_apply(map_, 8, 1)[0] == 6


# ---------------------------------------------------------------------------
# Test 8 -- regression the chained fixture caught: a colon_list element must not
# drift. After run 1 `:15,20` reads `:10,15`, and that `15` is the rewritten
# value of the record for old line 20 -- a number-keyed record lookup binds it to
# the record for old line 15 and rewrites it to 10, giving `10,10`.
# ---------------------------------------------------------------------------
def test_colon_list_element_does_not_drift(harness):
    assert harness.cited(6).endswith(":15,20")
    assert harness.apply().returncode == 0
    assert harness.cited(6).endswith(":10,15"), harness.cited(6)
    assert harness.apply().returncode == 0
    assert harness.cited(6).endswith(":10,15"), harness.cited(6)
    assert harness.apply().returncode == 0
    assert harness.cited(6).endswith(":10,15"), harness.cited(6)


# ---------------------------------------------------------------------------
# Test 9 -- SWEEP-11 / D-09: an empty input set exits 2
# ---------------------------------------------------------------------------
def test_exits_nonzero_on_empty_input(harness):
    result = harness.run(manifest=_MANIFEST_EMPTY)
    assert result.returncode == 2, _shown(result, 2)
    assert "ZERO records" in result.stderr
    assert result.returncode != 0, "silence must never be success"


def test_exits_nonzero_when_no_record_is_actionable(harness):
    header, records = harness.load_manifest()
    for rec in records:
        rec["retarget"] = True
    harness.write_manifest(header, records)
    result = harness.run()
    assert result.returncode == 2, _shown(result, 2)
    assert "NONE is" in result.stderr


# ---------------------------------------------------------------------------
# Test 10 -- SWEEP-11 / D-09: the module has no location-derived root
# ---------------------------------------------------------------------------
def test_here_is_absent_from_the_module():
    source = open(_TOOL, encoding="utf-8").read()
    assert source.count("_HERE") == 0, "the tool must not derive a root from its location"
    assert source.count("__file__") == 0, "no __file__-derived root is permitted"
    assert source.count("autojunk=False") >= 1, "autojunk=False is load-bearing"
    assert "autojunk=True" not in source.replace(
        "`autojunk=True`", ""
    ).replace("autojunk=True` ", ""), "the tool must never build a map with autojunk on"
    assert "Exit codes" in rc.__doc__
    for code in ("0 --", "1 --", "2 --"):
        assert code in rc.__doc__, code
    assert "import citation_paths" in source, "the shared resolver must be imported"
    assert source.count("fixtures/**") == 0, "no independent resolution logic"


def test_repo_root_is_a_required_positional_and_manifest_has_no_default():
    helped = subprocess.run(
        [sys.executable, _TOOL, "--help"], capture_output=True, text=True, check=False
    )
    assert helped.returncode == 0, _shown(helped, 0)
    assert "repo_root" in helped.stdout
    assert "--manifest MANIFEST" in helped.stdout
    assert "--apply" in helped.stdout

    no_manifest = subprocess.run(
        [sys.executable, _TOOL, os.sep], capture_output=True, text=True, check=False
    )
    assert no_manifest.returncode != 0
    assert "--manifest" in no_manifest.stderr


# ---------------------------------------------------------------------------
# Test 11 -- T-154-18: difflib agrees with an independent git diff -U0 map
# ---------------------------------------------------------------------------
def test_difflib_map_agrees_with_git_diff_u0(tmp_path):
    real = _read_lines(_CITATION_PATHS)
    assert len(real) > 200, "the cross-check needs a real file over difflib's junk threshold"

    # Two disjoint 6-line windows in which every line is unique in the file, so
    # the two diff algorithms cannot legitimately disagree about the alignment.
    seen = {}
    for index, text in enumerate(real):
        seen.setdefault(text, []).append(index)
    unique = {index for indexes in seen.values() if len(indexes) == 1 for index in indexes}
    windows = [
        start
        for start in range(len(real) - 6)
        if all(start + k in unique for k in range(6))
    ]
    assert len(windows) >= 2, "no unique 6-line window found"
    first = windows[0]
    later = [start for start in windows if start > first + 26]
    assert later, "no second unique window far enough from the first"
    second = later[0]
    dropped = set(range(first, first + 6)) | set(range(second, second + 6))
    edited = [text for index, text in enumerate(real) if index not in dropped]

    repo = tmp_path / "cross"
    repo.mkdir()
    target = repo / "citation_paths.py"
    target.write_text("\n".join(real) + "\n", encoding="utf-8")
    assert _git(repo, "init", "-q").returncode == 0
    assert _git(repo, "add", "-A").returncode == 0
    assert _git(repo, "commit", "-qm", "before").returncode == 0
    target.write_text("\n".join(edited) + "\n", encoding="utf-8")

    diff = _git(repo, "diff", "-U0", "HEAD", "--", "citation_paths.py")
    assert diff.returncode == 0, diff.stderr
    from_git = _map_from_unified_diff(diff.stdout, len(real))
    from_difflib = rc.build_map(real, edited)
    assert from_difflib == from_git, {
        line: (from_difflib.get(line), from_git.get(line))
        for line in sorted(set(from_difflib) | set(from_git))
        if from_difflib.get(line) != from_git.get(line)
    }
    assert sum(1 for v in from_difflib.values() if v is None) == 12


# ---------------------------------------------------------------------------
# Test 12 -- T-154-18: autojunk=True really does corrupt the map on a real file
# ---------------------------------------------------------------------------
def test_autojunk_true_would_corrupt_the_map_on_a_real_file():
    import difflib

    # A FROZEN pre-sweep copy of firestarter/src/proms/eeprom_28c.cpp, not the live
    # file. Reading the live file made this leg self-invalidating: plan 154-06 swept
    # that exact file later in this same phase, so the provenance-stripping edit below
    # became a no-op and the leg reported good=873 bad=873 -- proving nothing, and
    # failing on its own non-vacuity assertion. The frozen copy keeps the control
    # hermetic. It must stay a REAL file: research established that a purpose-built
    # 500-line synthetic equivalent does NOT diverge, which is the whole point --
    # autojunk only bites on real files, so a synthetic fixture would pass either way.
    candidate = os.path.join(_HERE, "fixtures", "autojunk_real_file_presweep.cpp")
    assert os.path.isfile(candidate), (
        "the frozen pre-sweep fixture is missing; it is committed alongside this "
        "test precisely so this leg cannot depend on live, sweepable source"
    )
    old = _read_lines(candidate)
    assert len(old) > 200
    new = [
        line
        for line in old
        if not re.search(r"(Phase \d+|D-\d\d|[A-Z]{3,}-\d\d)", line)
    ]
    assert new != old, "the realistic provenance-stripping edit changed nothing"

    def mapped(autojunk):
        matcher = difflib.SequenceMatcher(None, old, new, autojunk=autojunk)
        out = {}
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                for k in range(i2 - i1):
                    out[i1 + k + 1] = j1 + k + 1
            elif tag in ("delete", "replace"):
                for k in range(i1, i2):
                    out[k + 1] = None
        return out

    good, bad = mapped(False), mapped(True)
    assert good == rc.build_map(old, new), "the tool must use autojunk=False"
    survivors_good = sum(1 for v in good.values() if v is not None)
    survivors_bad = sum(1 for v in bad.values() if v is not None)
    assert survivors_good == len(new), (survivors_good, len(new))
    assert survivors_bad < survivors_good, (
        "autojunk=True did not diverge on this file, so this leg proves nothing; "
        f"good={survivors_good} bad={survivors_bad}"
    )


# ---------------------------------------------------------------------------
# Test 13 -- SWEEP-11: `replace` is non-surviving, exactly like `delete`
# ---------------------------------------------------------------------------
def test_replace_is_treated_as_non_surviving(tmp_path):
    # (a) the opcode itself: a changed line yields `replace` and maps to None.
    assert rc.build_map(["a", "b", "c"], ["a", "B", "c"]) == {1: 1, 2: None, 3: 3}

    # (b) end to end: a REFLOWED line's citation is flagged retarget and left
    # exactly as written -- never assigned a positional number.
    old = _read_lines(_CHAINED_OLD)
    new = _read_lines(_CHAINED_NEW)
    reflow_index = new.index("static uint8_t demo_state;")
    new = list(new)
    new[reflow_index] = "static uint8_t demo_state;  // reflowed by the sweep"
    doc = "A citation at the reflowed line: firestarter/src/chained_demo.cpp:6\n"
    harness = Harness(tmp_path, old_lines=old, new_lines=new, doc_text=doc)
    assert rc.build_map(old, new)[6] is None, "a reflowed line must not survive"

    header, _ = harness.load_manifest()
    harness.write_manifest(
        header, [_record(1, "colon_single", _TARGET_REL, 6, None, old)]
    )
    result = harness.run("--apply")
    assert result.returncode == 0, _shown(result, 0)
    assert harness.doc_text() == doc, "a retarget record must never be rewritten"
    assert "SUGGESTION for a human" in result.stdout
    assert "1 flagged retarget" in result.stdout


# ---------------------------------------------------------------------------
# Test 14 -- SWEEP-11 / D-01: dry run is the default and writes nothing
# ---------------------------------------------------------------------------
def test_dry_run_writes_nothing(harness):
    before = harness.doc_text()
    before_target = harness.target.read_text(encoding="utf-8")
    result = harness.run()
    assert result.returncode == 0, _shown(result, 0)
    assert "DRY RUN" in result.stdout and "would change" in result.stdout
    assert harness.doc_text() == before, "the dry run modified the citing document"
    assert harness.target.read_text(encoding="utf-8") == before_target
    # The sweep's own edit to the target file is the ONLY thing the working
    # tree carries; the dry run added nothing to it.
    listing = _git(harness.root, "status", "--porcelain")
    assert [row[3:] for row in listing.stdout.splitlines()] == [
        _TARGET_REL
    ], listing.stdout


# ---------------------------------------------------------------------------
# Test 15 -- REMAP-02 / T-154-17: an oracle violation exits 1 and writes nothing
# ---------------------------------------------------------------------------
def test_oracle_violation_exits_1_and_writes_nothing(harness):
    before = harness.doc_text()
    header, records = harness.load_manifest()
    for rec in records:
        if rec["target_line"] == 15 and rec["variant"] == "colon_single":
            rec["source_text"] = "this text is at no line of either side"
    harness.write_manifest(header, records)
    result = harness.run("--apply")
    assert result.returncode == 1, _shown(result, 1)
    assert "oracle violated" in result.stderr
    assert "nothing was written" in result.stderr
    assert harness.doc_text() == before, (
        "a violation must abort the WHOLE run, including records that would "
        "have succeeded"
    )


# ---------------------------------------------------------------------------
# Test 16 -- D-09: a missing resolved target is a real violation (exit 1)
# ---------------------------------------------------------------------------
def test_missing_resolved_target_exits_1(harness):
    harness.target.unlink()
    result = harness.run("--apply")
    assert result.returncode == 1, _shown(result, 1)
    assert "does not exist on disk" in result.stderr


# ---------------------------------------------------------------------------
# Test 17 -- D-09: infrastructure failures exit 2, not 1
# ---------------------------------------------------------------------------
def test_unloadable_manifest_exits_2(harness, tmp_path):
    absent = harness.run(manifest=tmp_path / "not-a-file.jsonl")
    assert absent.returncode == 2, _shown(absent, 2)
    assert "cannot load manifest" in absent.stderr

    broken = tmp_path / "broken.jsonl"
    broken.write_text('{"planning_file": nope}\n', encoding="utf-8")
    result = harness.run(manifest=broken)
    assert result.returncode == 2, _shown(result, 2)
    assert "not valid JSON" in result.stderr

    missing_root = subprocess.run(
        [
            sys.executable,
            _TOOL,
            str(tmp_path / "no-such-root"),
            "--manifest",
            str(harness.manifest),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert missing_root.returncode == 2, _shown(missing_root, 2)


# ---------------------------------------------------------------------------
# Test 18 -- ASVS V5: a traversal path is refused and nothing is written
# ---------------------------------------------------------------------------
def test_traversal_in_planning_file_is_refused(harness):
    before = harness.doc_text()
    header, records = harness.load_manifest()
    for rec in records:
        rec["planning_file"] = "../escaped.md"
    harness.write_manifest(header, records)
    result = harness.run("--apply")
    assert result.returncode != 0, _shown(result, 1)
    assert "parent-traversal" in result.stderr
    assert harness.doc_text() == before


# ---------------------------------------------------------------------------
# Test 19 -- SWEEP-11 / D-01 / D-10 / T-154-21: the tool was NOT applied here
# ---------------------------------------------------------------------------
def test_the_tool_is_not_applied_to_any_real_planning_document():
    meta = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
    real_manifest = os.path.join(
        meta, ".planning", "v1.33", "sweep-citation-manifest.jsonl"
    )
    if not os.path.isfile(real_manifest) or not os.path.isdir(
        os.path.join(meta, ".git")
    ):
        pytest.skip("the real manifest or the meta repository is not present here")

    citing = set()
    with open(real_manifest, encoding="utf-8") as handle:
        for line in handle:
            if '"_schema"' in line[:20]:
                continue
            citing.add(json.loads(line)["planning_file"])
    assert len(citing) > 100, "the citation-bearing set is implausibly small"

    changed = subprocess.run(
        ["git", "-C", meta, "diff", "--name-only", "HEAD", "--", ".planning"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert changed.returncode == 0, changed.stderr
    touched = {
        path
        for path in changed.stdout.split()
        if not path.startswith(".planning/v1.33/")
    }
    applied = sorted(touched & citing)
    assert not applied, (
        "the remap tool must be BUILT in Phase 154 and APPLIED in Phase 159 "
        f"(D-01/D-10), but these citation-bearing documents are modified: {applied}"
    )

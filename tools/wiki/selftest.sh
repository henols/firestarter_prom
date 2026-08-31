#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WIKI_PY="$SCRIPT_DIR/wiki.py"
REPO_ROOT="$SCRIPT_DIR/../.."

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

EVIDENCE=()

banner() {
    echo "=== $1 ==="
}

new_source_dir() {
    local dir="$1"
    mkdir -p "$dir"
    printf '%s\n' '# Home' '' '[Page One](Page-One)' > "$dir/Home.md"
    printf '%s\n' '# Page One' '' 'Fixture body with no internal links.' > "$dir/Page-One.md"
    printf '%s\n' '- [Home](Home)' '- [Page One](Page-One)' > "$dir/_Sidebar.md"
}

new_bare_wiki() {
    git init --bare --initial-branch=master -q "$1"
}

rc_of() {
    local out="$WORK/$1"
    shift
    local rc=0
    "$@" >"$out" 2>&1 || rc=$?
    echo "$rc"
}

record() {
    EVIDENCE+=("$1|$2|$3|$4|$5")
}

assert_rc() {
    local case_id="$1"
    local expected="$2"
    local observed="$3"
    if [ "$expected" != "$observed" ]; then
        echo "ERROR: $case_id: expected exit $expected, observed $observed" >&2
        return 1
    fi
    echo "OK: $case_id exit $observed"
}

print_evidence_table() {
    echo "case | expected | observed | control | note | verdict"
    local row case_id expected observed control note verdict
    for row in "${EVIDENCE[@]}"; do
        IFS='|' read -r case_id expected observed control note <<< "$row"
        verdict="FAIL"
        if [ "$expected" = "$observed" ]; then
            verdict="PASS"
        fi
        echo "$case_id | $expected | $observed | $control | $note | $verdict"
    done
}

case_orphan_exit_1() {
    local src="$WORK/orphan_exit_1_src"
    new_source_dir "$src"
    local ok=0

    local control_rc
    control_rc=$(rc_of orphan_exit_1_control.log python3 "$WIKI_PY" links --source-dir "$src")
    assert_rc "orphan_exit_1_control" 0 "$control_rc" || ok=1

    printf '%s\n' '# Page Orphan' '' 'Fixture body with no internal links.' > "$src/Page-Orphan.md"
    printf '%s\n' '- [Home](Home)' '- [Page One](Page-One)' '- [Page Orphan](Page-Orphan)' > "$src/_Sidebar.md"

    local mutated_rc
    mutated_rc=$(rc_of orphan_exit_1_mutated.log python3 "$WIKI_PY" links --source-dir "$src")
    assert_rc "orphan_exit_1" 1 "$mutated_rc" || ok=1

    if ! grep -q 'Page-Orphan' "$WORK/orphan_exit_1_mutated.log"; then
        echo "ERROR: orphan_exit_1: stderr missing Page-Orphan" >&2
        ok=1
    fi

    record "orphan_exit_1" 1 "$mutated_rc" "$control_rc" "orphan absent from Home.md"

    return "$ok"
}

case_sidebar_link_is_not_evidence() {
    local src="$WORK/sidebar_link_is_not_evidence_src"
    new_source_dir "$src"
    local ok=0

    local control_rc
    control_rc=$(rc_of sidebar_link_is_not_evidence_control.log python3 "$WIKI_PY" links --source-dir "$src")
    assert_rc "sidebar_link_is_not_evidence_control" 0 "$control_rc" || ok=1

    printf '%s\n' '# Page Orphan' '' 'Fixture body with no internal links.' > "$src/Page-Orphan.md"
    printf '%s\n' '- [Home](Home)' '- [Page One](Page-One)' '- [Page Orphan](Page-Orphan)' > "$src/_Sidebar.md"

    if ! grep -q 'Page-Orphan' "$src/_Sidebar.md"; then
        echo "ERROR: sidebar_link_is_not_evidence: fixture sidebar missing Page-Orphan link" >&2
        ok=1
    fi

    local links_rc
    links_rc=$(rc_of sidebar_link_is_not_evidence_links.log python3 "$WIKI_PY" links --source-dir "$src")
    assert_rc "sidebar_link_is_not_evidence" 1 "$links_rc" || ok=1

    if ! grep -q 'Page-Orphan' "$WORK/sidebar_link_is_not_evidence_links.log"; then
        echo "ERROR: sidebar_link_is_not_evidence: stderr missing Page-Orphan" >&2
        ok=1
    fi

    record "sidebar_link_is_not_evidence" 1 "$links_rc" "$control_rc" "home-only evidence"

    return "$ok"
}

case_broken_link_exit_1() {
    local src="$WORK/broken_link_exit_1_src"
    new_source_dir "$src"
    local ok=0

    local control_rc
    control_rc=$(rc_of broken_link_exit_1_control.log python3 "$WIKI_PY" links --source-dir "$src")
    assert_rc "broken_link_exit_1_control" 0 "$control_rc" || ok=1

    printf '%s\n' '[x](No-Such-Page)' >> "$src/Home.md"

    local mutated_rc
    mutated_rc=$(rc_of broken_link_exit_1_mutated.log python3 "$WIKI_PY" links --source-dir "$src")
    assert_rc "broken_link_exit_1" 1 "$mutated_rc" || ok=1

    if ! grep -q 'No-Such-Page' "$WORK/broken_link_exit_1_mutated.log"; then
        echo "ERROR: broken_link_exit_1: stderr missing No-Such-Page" >&2
        ok=1
    fi

    record "broken_link_exit_1" 1 "$mutated_rc" "$control_rc" "unresolved internal link target"

    return "$ok"
}

case_md_suffix_link_exit_1() {
    local src="$WORK/md_suffix_link_exit_1_src"
    new_source_dir "$src"
    local ok=0

    local control_rc
    control_rc=$(rc_of md_suffix_link_exit_1_control.log python3 "$WIKI_PY" links --source-dir "$src")
    assert_rc "md_suffix_link_exit_1_control" 0 "$control_rc" || ok=1

    printf '%s\n' '[x](Home.md)' >> "$src/Page-One.md"

    local mutated_rc
    mutated_rc=$(rc_of md_suffix_link_exit_1_mutated.log python3 "$WIKI_PY" links --source-dir "$src")
    assert_rc "md_suffix_link_exit_1" 1 "$mutated_rc" || ok=1

    if ! grep -q 'Home.md' "$WORK/md_suffix_link_exit_1_mutated.log"; then
        echo "ERROR: md_suffix_link_exit_1: stderr missing Home.md" >&2
        ok=1
    fi

    record "md_suffix_link_exit_1" 1 "$mutated_rc" "$control_rc" "md-suffixed internal link rejected"

    return "$ok"
}

case_illegal_filename_exit_1() {
    local src="$WORK/illegal_filename_exit_1_src"
    new_source_dir "$src"
    local ok=0

    local control_rc
    control_rc=$(rc_of illegal_filename_exit_1_control.log python3 "$WIKI_PY" links --source-dir "$src")
    assert_rc "illegal_filename_exit_1_control" 0 "$control_rc" || ok=1

    printf '%s\n' '# Page Bad' '' 'Fixture body with no internal links.' > "$src/Page:Bad.md"
    if ! ls "$src/Page:Bad.md" >/dev/null 2>&1; then
        echo "ERROR: illegal_filename_exit_1: fixture file Page:Bad.md was not created" >&2
        ok=1
    fi

    local mutated_rc
    mutated_rc=$(rc_of illegal_filename_exit_1_mutated.log python3 "$WIKI_PY" links --source-dir "$src")
    assert_rc "illegal_filename_exit_1" 1 "$mutated_rc" || ok=1

    if ! grep -q 'Page:Bad.md' "$WORK/illegal_filename_exit_1_mutated.log"; then
        echo "ERROR: illegal_filename_exit_1: stderr missing offending filename" >&2
        ok=1
    fi

    record "illegal_filename_exit_1" 1 "$mutated_rc" "$control_rc" "illegal filename character"

    return "$ok"
}

case_wiki05_unreferenced_page_exit_1() {
    local src="$WORK/wiki05_unreferenced_page_exit_1_src"
    new_source_dir "$src"
    local ok=0

    local control_rc
    control_rc=$(rc_of wiki05_unreferenced_page_exit_1_control.log python3 "$WIKI_PY" links --source-dir "$src")
    assert_rc "wiki05_unreferenced_page_exit_1_control" 0 "$control_rc" || ok=1

    printf '%s\n' '# Page Two' '' 'Fixture body with no internal links.' > "$src/Page-Two.md"
    printf '%s\n' '[Page Two](Page-Two)' >> "$src/Home.md"

    printf '%s\n' '# Page Three' '' 'Fixture body with no internal links.' > "$src/Page-Three.md"
    printf '%s\n' '- [Home](Home)' '- [Page One](Page-One)' '- [Page Three](Page-Three)' > "$src/_Sidebar.md"

    local mutated_rc
    mutated_rc=$(rc_of wiki05_unreferenced_page_exit_1_mutated.log python3 "$WIKI_PY" links --source-dir "$src")
    assert_rc "wiki05_unreferenced_page_exit_1" 1 "$mutated_rc" || ok=1

    if ! grep -q 'Page-Two' "$WORK/wiki05_unreferenced_page_exit_1_mutated.log"; then
        echo "ERROR: wiki05_unreferenced_page_exit_1: stderr missing Page-Two (sidebar containment leg)" >&2
        ok=1
    fi
    if ! grep -q 'Page-Three' "$WORK/wiki05_unreferenced_page_exit_1_mutated.log"; then
        echo "ERROR: wiki05_unreferenced_page_exit_1: stderr missing Page-Three (Home reachability leg)" >&2
        ok=1
    fi

    record "wiki05_unreferenced_page_exit_1" 1 "$mutated_rc" "$control_rc" "sidebar-containment leg (Page-Two) and Home-reachability leg (Page-Three) both trip"

    return "$ok"
}

case_reference_style_external_citation_exit_0() {
    local src="$WORK/reference_style_external_citation_exit_0_src"
    new_source_dir "$src"
    local ok=0

    local control_rc
    control_rc=$(rc_of reference_style_external_citation_exit_0_control.log python3 "$WIKI_PY" links --source-dir "$src")
    assert_rc "reference_style_external_citation_exit_0_control" 0 "$control_rc" || ok=1

    printf '%s\n' '' 'See ([Vendor][1]) for the datasheet.' '' '[1]: https://example.com/datasheet.pdf' >> "$src/Page-One.md"

    local cited_rc
    cited_rc=$(rc_of reference_style_external_citation_exit_0_cited.log python3 "$WIKI_PY" links --source-dir "$src")
    assert_rc "reference_style_external_citation_exit_0" 0 "$cited_rc" || ok=1

    printf '%s\n' 'See ([Orphan Ref][9]) with no matching definition.' >> "$src/Page-One.md"

    local unresolved_rc
    unresolved_rc=$(rc_of reference_style_external_citation_exit_0_unresolved.log python3 "$WIKI_PY" links --source-dir "$src")
    assert_rc "reference_style_external_citation_exit_0_unresolved" 1 "$unresolved_rc" || ok=1

    if ! grep -q 'Orphan Ref' "$WORK/reference_style_external_citation_exit_0_unresolved.log"; then
        echo "ERROR: reference_style_external_citation_exit_0: stderr missing Orphan Ref (unresolved reference-style link still rejected)" >&2
        ok=1
    fi

    record "reference_style_external_citation_exit_0" 0 "$cited_rc" "$control_rc" "external [text][ref] resolved by a [ref]: url definition is not flagged; an unresolved [text][ref] is still rejected"

    return "$ok"
}

case_dotdir_ignored_exit_0() {
    local src="$WORK/dotdir_ignored_exit_0_src"
    new_source_dir "$src"
    local ok=0

    mkdir -p "$src/.git/objects"
    printf 'ref: refs/heads/master\n' > "$src/.git/HEAD"

    local rc
    rc=$(rc_of dotdir_ignored_exit_0.log python3 "$WIKI_PY" links --source-dir "$src")
    assert_rc "dotdir_ignored_exit_0" 0 "$rc" || ok=1

    if grep -q '\.git' "$WORK/dotdir_ignored_exit_0.log"; then
        echo "ERROR: dotdir_ignored_exit_0: stderr mentions .git; a real clone's .git directory must not be treated as an illegal wiki page" >&2
        ok=1
    fi

    record "dotdir_ignored_exit_0" 0 "$rc" "0" "a git clone's .git directory is not a wiki page and must not fail filename legality"

    return "$ok"
}

CASES=(orphan_exit_1 sidebar_link_is_not_evidence broken_link_exit_1 md_suffix_link_exit_1 illegal_filename_exit_1 wiki05_unreferenced_page_exit_1 reference_style_external_citation_exit_0 dotdir_ignored_exit_0)

exit_code=0
fail_count=0
for id in "${CASES[@]}"; do
    banner "$id"
    if ! "case_$id"; then
        exit_code=1
        fail_count=$((fail_count + 1))
    fi
done

print_evidence_table

total=${#CASES[@]}
if [ "$exit_code" -eq 0 ]; then
    echo "OK: selftest complete ($total cases)"
else
    echo "ERROR: selftest failed ($fail_count of $total cases red)" >&2
fi

exit "$exit_code"

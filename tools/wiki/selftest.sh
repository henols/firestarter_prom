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

case_stale_sidebar_exit_1() {
    local src="$WORK/stale_sidebar_exit_1_src"
    new_source_dir "$src"
    local ok=0

    local control_rc
    control_rc=$(rc_of stale_sidebar_exit_1_control.log python3 "$WIKI_PY" sidebar --check --source-dir "$src")
    assert_rc "stale_sidebar_exit_1_control" 0 "$control_rc" || ok=1

    cp "$src/_Sidebar.md" "$WORK/stale_sidebar_exit_1_before.md"

    printf '%s\n' '# Page Two' '' 'Fixture body with no internal links.' > "$src/Page-Two.md"

    local mutated_rc
    mutated_rc=$(rc_of stale_sidebar_exit_1_mutated.log python3 "$WIKI_PY" sidebar --check --source-dir "$src")
    assert_rc "stale_sidebar_exit_1" 1 "$mutated_rc" || ok=1

    if ! grep -q 'Page-Two' "$WORK/stale_sidebar_exit_1_mutated.log"; then
        echo "ERROR: stale_sidebar_exit_1: delta output missing Page-Two" >&2
        ok=1
    fi

    if ! cmp -s "$src/_Sidebar.md" "$WORK/stale_sidebar_exit_1_before.md"; then
        echo "ERROR: stale_sidebar_exit_1: _Sidebar.md was modified by a failing --check" >&2
        ok=1
    fi

    record "stale_sidebar_exit_1" 1 "$mutated_rc" "$control_rc" "a failing --check must not rewrite the file it checks"

    return "$ok"
}

case_sidebar_deterministic() {
    local src="$WORK/sidebar_deterministic_src"
    new_source_dir "$src"
    local ok=0

    local rc1
    rc1=$(rc_of sidebar_deterministic_run1.log python3 "$WIKI_PY" sidebar --source-dir "$src")
    assert_rc "sidebar_deterministic_run1" 0 "$rc1" || ok=1

    cp "$src/_Sidebar.md" "$WORK/sidebar_deterministic_run1_copy.md"

    local rc2
    rc2=$(rc_of sidebar_deterministic_run2.log python3 "$WIKI_PY" sidebar --source-dir "$src")
    assert_rc "sidebar_deterministic" 0 "$rc2" || ok=1

    if ! cmp -s "$WORK/sidebar_deterministic_run1_copy.md" "$src/_Sidebar.md"; then
        echo "ERROR: sidebar_deterministic: _Sidebar.md differs between run 1 and run 2" >&2
        ok=1
    fi

    local last_byte last_line
    last_byte=$(tail -c1 "$src/_Sidebar.md")
    last_line=$(tail -n1 "$src/_Sidebar.md")
    if [ "$last_byte" != "" ] || [ "$last_line" = "" ]; then
        echo "ERROR: sidebar_deterministic: _Sidebar.md does not end with a single trailing LF" >&2
        ok=1
    fi

    local cr_count
    cr_count=$(grep -c $'\r' "$src/_Sidebar.md")
    if [ "$cr_count" != "0" ]; then
        echo "ERROR: sidebar_deterministic: _Sidebar.md contains CR bytes" >&2
        ok=1
    fi

    record "sidebar_deterministic" 0 "$rc2" "$rc1" "two runs over an unchanged source must be byte-identical"

    return "$ok"
}

case_orphan_exit_1() {
    local src="$WORK/orphan_exit_1_src"
    new_source_dir "$src"
    local ok=0

    local control_rc
    control_rc=$(rc_of orphan_exit_1_control.log python3 "$WIKI_PY" links --source-dir "$src")
    assert_rc "orphan_exit_1_control" 0 "$control_rc" || ok=1

    printf '%s\n' '# Page Orphan' '' 'Fixture body with no internal links.' > "$src/Page-Orphan.md"
    python3 "$WIKI_PY" sidebar --source-dir "$src" >/dev/null

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
    python3 "$WIKI_PY" sidebar --source-dir "$src" >/dev/null

    if ! grep -q 'Page-Orphan' "$src/_Sidebar.md"; then
        echo "ERROR: sidebar_link_is_not_evidence: regenerated sidebar missing Page-Orphan link" >&2
        ok=1
    fi

    local sidebar_check_rc
    sidebar_check_rc=$(rc_of sidebar_link_is_not_evidence_sidebar_check.log python3 "$WIKI_PY" sidebar --check --source-dir "$src")
    assert_rc "sidebar_link_is_not_evidence_sidebar_check" 0 "$sidebar_check_rc" || ok=1

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

CASES=(stale_sidebar_exit_1 sidebar_deterministic orphan_exit_1 sidebar_link_is_not_evidence broken_link_exit_1 md_suffix_link_exit_1 illegal_filename_exit_1)

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

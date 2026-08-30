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

case_wiki_absent_exit_2() {
    local src="$WORK/wiki_absent_exit_2_src"
    new_source_dir "$src"
    local ok=0

    local nonexistent="$WORK/wiki_absent_exit_2_nonexistent.git"
    local rc
    rc=$(rc_of wiki_absent_exit_2.log python3 "$WIKI_PY" publish --source-dir "$src" --wiki-remote "$nonexistent")
    assert_rc "wiki_absent_exit_2" 2 "$rc" || ok=1

    if ! grep -q 'WIKI-01' "$WORK/wiki_absent_exit_2.log"; then
        echo "ERROR: wiki_absent_exit_2: stderr missing WIKI-01" >&2
        ok=1
    fi
    if ! grep -q 'https://github.com/henols/firestarter_prom/wiki' "$WORK/wiki_absent_exit_2.log"; then
        echo "ERROR: wiki_absent_exit_2: stderr missing operator URL" >&2
        ok=1
    fi

    local existing="$WORK/wiki_absent_exit_2_existing.git"
    new_bare_wiki "$existing"
    local control_rc
    control_rc=$(rc_of wiki_absent_exit_2_control.log python3 "$WIKI_PY" publish --source-dir "$src" --wiki-remote "$existing")
    if [ "$control_rc" = "2" ]; then
        echo "ERROR: wiki_absent_exit_2_control: existing remote must not exit 2, observed 2" >&2
        ok=1
    fi

    record "wiki_absent_exit_2" 2 "$rc" "$control_rc" "nonexistent remote vs existing bare fixture"

    return "$ok"
}

case_drift_detected_exit_1() {
    local src="$WORK/drift_detected_exit_1_src"
    new_source_dir "$src"
    local wiki="$WORK/drift_detected_exit_1_wiki.git"
    new_bare_wiki "$wiki"
    local ok=0

    local seed_rc
    seed_rc=$(rc_of drift_detected_exit_1_seed.log python3 "$WIKI_PY" publish --push --source-dir "$src" --wiki-remote "$wiki")
    assert_rc "drift_detected_exit_1_seed" 0 "$seed_rc" || ok=1

    local control_rc
    control_rc=$(rc_of drift_detected_exit_1_control.log python3 "$WIKI_PY" publish --source-dir "$src" --wiki-remote "$wiki")
    assert_rc "drift_detected_exit_1_control" 0 "$control_rc" || ok=1

    local clone_dir="$WORK/drift_detected_exit_1_clone"
    git clone -q "$wiki" "$clone_dir"
    printf '%s\n' '# Page One' '' 'Mutated wiki-side content.' > "$clone_dir/Page-One.md"
    git -C "$clone_dir" add -A
    git -C "$clone_dir" -c user.name=selftest -c user.email=selftest@example.invalid commit -q -m mutate
    git -C "$clone_dir" push -q origin master

    local mutated_rc
    mutated_rc=$(rc_of drift_detected_exit_1_mutated.log python3 "$WIKI_PY" publish --source-dir "$src" --wiki-remote "$wiki")
    assert_rc "drift_detected_exit_1" 1 "$mutated_rc" || ok=1

    if ! grep -q 'Page-One' "$WORK/drift_detected_exit_1_mutated.log"; then
        echo "ERROR: drift_detected_exit_1: diff output missing Page-One" >&2
        ok=1
    fi

    record "drift_detected_exit_1" 1 "$mutated_rc" "$control_rc" "wiki-side edit pushed then dry-run detects drift"

    return "$ok"
}

case_hand_edit_overwritten() {
    local src="$WORK/hand_edit_overwritten_src"
    new_source_dir "$src"
    local wiki="$WORK/hand_edit_overwritten_wiki.git"
    new_bare_wiki "$wiki"
    local ok=0

    local push1_rc
    push1_rc=$(rc_of hand_edit_overwritten_push1.log python3 "$WIKI_PY" publish --push --source-dir "$src" --wiki-remote "$wiki")
    assert_rc "hand_edit_overwritten_push1" 0 "$push1_rc" || ok=1

    local wiki_page_before source_page_before control_rc=0
    wiki_page_before=$(git --git-dir "$wiki" show master:Page-One.md 2>/dev/null || true)
    source_page_before=$(cat "$src/Page-One.md")
    if [ "$wiki_page_before" != "$source_page_before" ]; then
        echo "ERROR: hand_edit_overwritten_control: fixture page does not match source immediately after push" >&2
        control_rc=1
        ok=1
    fi

    local clone_dir="$WORK/hand_edit_overwritten_clone"
    git clone -q "$wiki" "$clone_dir"
    printf '%s\n' '# Page One' '' 'Hand-edited directly on the wiki.' > "$clone_dir/Page-One.md"
    printf '%s\n' '# Stray Page' '' 'Added directly on the wiki, never in source.' > "$clone_dir/Stray-Page.md"
    git -C "$clone_dir" add -A
    git -C "$clone_dir" -c user.name=selftest -c user.email=selftest@example.invalid commit -q -m handedit
    git -C "$clone_dir" push -q origin master

    local push2_rc
    push2_rc=$(rc_of hand_edit_overwritten_push2.log python3 "$WIKI_PY" publish --push --source-dir "$src" --wiki-remote "$wiki")
    assert_rc "hand_edit_overwritten" 0 "$push2_rc" || ok=1

    local final_wiki_page final_source_page
    final_wiki_page=$(git --git-dir "$wiki" show master:Page-One.md 2>/dev/null || true)
    final_source_page=$(cat "$src/Page-One.md")
    if [ "$final_wiki_page" != "$final_source_page" ]; then
        echo "ERROR: hand_edit_overwritten: fixture page not overwritten back to source content" >&2
        ok=1
    fi

    if git --git-dir "$wiki" ls-tree --name-only master | grep -q '^Stray-Page.md$'; then
        echo "ERROR: hand_edit_overwritten: wiki-only stray page survived republish" >&2
        ok=1
    fi

    record "hand_edit_overwritten" 0 "$push2_rc" "$control_rc" "wiki-side hand edit and stray page both destroyed by republish"

    return "$ok"
}

case_idempotent_head_unchanged() {
    local src="$WORK/idempotent_head_unchanged_src"
    new_source_dir "$src"
    local wiki="$WORK/idempotent_head_unchanged_wiki.git"
    new_bare_wiki "$wiki"
    local ok=0

    local push1_rc
    push1_rc=$(rc_of idempotent_head_unchanged_push1.log python3 "$WIKI_PY" publish --push --source-dir "$src" --wiki-remote "$wiki")
    assert_rc "idempotent_head_unchanged_push1" 0 "$push1_rc" || ok=1

    local head1
    head1=$(git --git-dir "$wiki" rev-parse master)

    local push2_rc
    push2_rc=$(rc_of idempotent_head_unchanged_push2.log python3 "$WIKI_PY" publish --push --source-dir "$src" --wiki-remote "$wiki")
    assert_rc "idempotent_head_unchanged" 0 "$push2_rc" || ok=1

    local head2
    head2=$(git --git-dir "$wiki" rev-parse master)

    if [[ "$head1" != "$head2" ]]; then
        echo "ERROR: idempotent_head_unchanged: rev-parse master changed across two --push runs" >&2
        ok=1
    fi

    if ! grep -qi 'no change' "$WORK/idempotent_head_unchanged_push2.log"; then
        echo "ERROR: idempotent_head_unchanged: second run stdout does not report no-change" >&2
        ok=1
    fi

    record "idempotent_head_unchanged" 0 "$push2_rc" "$push1_rc" "two pushes with no source change: HEAD identical"

    return "$ok"
}

case_deleted_page_removed() {
    local src="$WORK/deleted_page_removed_src"
    new_source_dir "$src"
    local wiki="$WORK/deleted_page_removed_wiki.git"
    new_bare_wiki "$wiki"
    local ok=0

    local push1_rc
    push1_rc=$(rc_of deleted_page_removed_push1.log python3 "$WIKI_PY" publish --push --source-dir "$src" --wiki-remote "$wiki")
    assert_rc "deleted_page_removed_push1" 0 "$push1_rc" || ok=1

    local wiki_listing_before source_listing_before control_rc=0
    wiki_listing_before=$(git --git-dir "$wiki" ls-tree --name-only master | sort)
    source_listing_before=$(ls "$src" | sort)
    if [ "$wiki_listing_before" != "$source_listing_before" ]; then
        echo "ERROR: deleted_page_removed_control: fixture tree does not match source directory immediately after push" >&2
        control_rc=1
        ok=1
    fi

    rm "$src/Page-One.md"
    printf '%s\n' '# Home' '' 'Fixture body with no internal links.' > "$src/Home.md"
    python3 "$WIKI_PY" sidebar --source-dir "$src" >/dev/null

    local push2_rc
    push2_rc=$(rc_of deleted_page_removed_push2.log python3 "$WIKI_PY" publish --push --source-dir "$src" --wiki-remote "$wiki")
    assert_rc "deleted_page_removed" 0 "$push2_rc" || ok=1

    local wiki_listing_after source_listing_after
    wiki_listing_after=$(git --git-dir "$wiki" ls-tree --name-only master | sort)
    source_listing_after=$(ls "$src" | sort)
    if [ "$wiki_listing_after" != "$source_listing_after" ]; then
        echo "ERROR: deleted_page_removed: fixture tree does not match source directory after deletion" >&2
        ok=1
    fi
    if echo "$wiki_listing_after" | grep -q '^Page-One.md$'; then
        echo "ERROR: deleted_page_removed: Page-One.md still present in fixture after deletion" >&2
        ok=1
    fi
    if ! echo "$wiki_listing_after" | grep -q '^Home.md$'; then
        echo "ERROR: deleted_page_removed: Home.md missing from fixture after deletion" >&2
        ok=1
    fi

    record "deleted_page_removed" 0 "$push2_rc" "$control_rc" "source page deleted then republished; wiki tree matches source exactly"

    return "$ok"
}

CASES=(stale_sidebar_exit_1 sidebar_deterministic orphan_exit_1 sidebar_link_is_not_evidence broken_link_exit_1 md_suffix_link_exit_1 illegal_filename_exit_1 wiki_absent_exit_2 drift_detected_exit_1 hand_edit_overwritten idempotent_head_unchanged deleted_page_removed)

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

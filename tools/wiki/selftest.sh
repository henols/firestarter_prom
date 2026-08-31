#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WIKI_PY="$SCRIPT_DIR/wiki.py"
DISPATCH_MIRROR_PY="$SCRIPT_DIR/dispatch_mirror.py"
HONEST01_PY="$SCRIPT_DIR/honest01_claims.py"
CLAIM_VOCAB="$SCRIPT_DIR/claim-vocabulary.json"
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

new_source_repo() {
    local dir="$1"
    mkdir -p "$dir/doc"
    git init -q "$dir"
    printf '%s\n' \
        '# Fixture Source Document' \
        '' \
        'support_status: adapter-required' \
        '' \
        'This chip is adapter-required for programming; the adapter-required note repeats' \
        'here for a second occurrence.' \
        > "$dir/doc/FIXTURE.md"
    (
        cd "$dir"
        git add doc/FIXTURE.md
        GIT_AUTHOR_NAME="gsd-selftest" GIT_AUTHOR_EMAIL="gsd-selftest@example.invalid" \
        GIT_COMMITTER_NAME="gsd-selftest" GIT_COMMITTER_EMAIL="gsd-selftest@example.invalid" \
        git commit -q -m "fixture source document"
        git rev-parse HEAD
    )
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

new_dispatch_mirror_fixture() {
    local dir="$1"
    mkdir -p "$dir/wiki" "$dir/app/tools" "$dir/fw/test/native/avr/test_dispatch"

    printf '%s\n' \
        '# Programming Protocols' \
        '' \
        'Fixture protocol page for dispatch_mirror.py selftest coverage.' \
        '' \
        '<!-- firestarter-claims-begin -->' \
        '| hex | note | slug | token | name | handler-family | phantom? |' \
        '|-----|------|------|-------|------|-----------------|----------|' \
        '| 0xA1 | 1 | s | t | n | eprom | no |' \
        '| 0xA2 | 1 | s | t | n | eprom | no |' \
        '| 0xA3 | 1 | s | t | n | eprom | no |' \
        '| 0xA4 | 1 | s | t | n | eprom | no |' \
        '| 0xA5 | 1 | s | t | n | eprom | no |' \
        '| 0xB1 | 1 | s | t | n | sram | no |' \
        '| 0xB2 | 1 | s | t | n | sram | no |' \
        '| 0xB3 | 1 | s | t | n | sram | no |' \
        '| 0xB4 | 1 | s | t | n | sram | no |' \
        '| 0xB5 | 1 | s | t | n | sram | no |' \
        '| 0xC1 | 1 | s | t | n | not-implemented | no |' \
        '| 0xC2 | 1 | s | t | n | not-implemented | no |' \
        '| 0xC3 | 1 | s | t | n | not-implemented | no |' \
        '' \
        '| Handler-family | function | File | Protocols |' \
        '|-----------------|----------|------|-----------|' \
        '| eprom | `configure_eprom()` | `eprom.cpp` | 0xA1-0xA5 |' \
        '| sram | `configure_sram()` | `sram.cpp` | 0xB1-0xB5 |' \
        '| not-implemented | `configure_not_implemented()` | `not_implemented.cpp` | 0xC1-0xC3 |' \
        '<!-- firestarter-claims-end -->' \
        > "$dir/wiki/Programming-Protocols.md"

    printf '%s\n' \
        'KNOWN_PROTOCOLS = {0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0xB1, 0xB2, 0xB3, 0xB4, 0xB5}' \
        '_ALGO_MEM_TYPE = {}' \
        '' \
        '' \
        'def dispatch(protocol, mem_type):' \
        '    if protocol in (0xA1, 0xA2, 0xA3, 0xA4, 0xA5):' \
        '        return "configure_eprom"' \
        '    if protocol in (0xB1, 0xB2, 0xB3, 0xB4, 0xB5):' \
        '        return "configure_sram"' \
        '    return "not_implemented"' \
        > "$dir/app/tools/check_dispatch.py"

    printf '%s\n' \
        'void test_protocol_0xA1(void) { make_handle(0xA1, 0, CMD_READ); }' \
        'void test_protocol_0xA2(void) { make_handle(0xA2, 0, CMD_READ); }' \
        'void test_protocol_0xA3(void) { make_handle(0xA3, 0, CMD_READ); }' \
        'void test_protocol_0xA4(void) { make_handle(0xA4, 0, CMD_READ); }' \
        'void test_protocol_0xA5(void) { make_handle(0xA5, 0, CMD_READ); }' \
        'void test_protocol_0xB1(void) { make_handle(0xB1, 0, CMD_READ); }' \
        'void test_protocol_0xB2(void) { make_handle(0xB2, 0, CMD_READ); }' \
        'void test_protocol_0xB3(void) { make_handle(0xB3, 0, CMD_READ); }' \
        'void test_protocol_0xB4(void) { make_handle(0xB4, 0, CMD_READ); }' \
        'void test_protocol_0xB5(void) { make_handle(0xB5, 0, CMD_READ); }' \
        > "$dir/fw/test/native/avr/test_dispatch/test_configure_memory.cpp"
}

case_dispatch_mirror_planted_drift_exit_1() {
    local base="$WORK/dispatch_mirror_planted_drift_exit_1_base"
    new_dispatch_mirror_fixture "$base"
    local ok=0

    local control_rc
    control_rc=$(rc_of dispatch_mirror_planted_drift_exit_1_control.log python3 "$DISPATCH_MIRROR_PY" --wiki-dir "$base/wiki" --app-dir "$base/app" --fw-dir "$base/fw")
    assert_rc "dispatch_mirror_planted_drift_exit_1_control" 0 "$control_rc" || ok=1

    local control_count
    control_count=$(grep -oE '^OK: [0-9]+' "$WORK/dispatch_mirror_planted_drift_exit_1_control.log" | grep -oE '[0-9]+')

    local missing_row="$WORK/dispatch_mirror_planted_drift_exit_1_missing_row"
    cp -r "$base" "$missing_row"
    sed -i '/^| 0xA5 /d' "$missing_row/wiki/Programming-Protocols.md"

    local mutated_rc
    mutated_rc=$(rc_of dispatch_mirror_planted_drift_exit_1_mutated.log python3 "$DISPATCH_MIRROR_PY" --wiki-dir "$missing_row/wiki" --app-dir "$missing_row/app" --fw-dir "$missing_row/fw")
    assert_rc "dispatch_mirror_planted_drift_exit_1" 1 "$mutated_rc" || ok=1

    if ! grep -q '0xA5' "$WORK/dispatch_mirror_planted_drift_exit_1_mutated.log"; then
        echo "ERROR: dispatch_mirror_planted_drift_exit_1: stderr missing 0xA5" >&2
        ok=1
    fi

    local evidence_file="$REPO_ROOT/.planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/dispatch-mirror-planted-RED.txt"
    {
        echo "command: python3 tools/wiki/dispatch_mirror.py --wiki-dir <fixture>/wiki --app-dir <fixture>/app --fw-dir <fixture>/fw"
        echo "mutation: deleted the 0xA5 bucket row from the claims region while the host dispatch stub and firmware stub both retain 0xA5"
        echo "exit status: $mutated_rc"
        echo "--- captured output ---"
        cat "$WORK/dispatch_mirror_planted_drift_exit_1_mutated.log"
    } > "$evidence_file"

    record "dispatch_mirror_planted_drift_exit_1" 1 "$mutated_rc" "$control_rc" "planted missing bucket row (0xA5) detected by name"

    local comment_only="$WORK/dispatch_mirror_planted_drift_exit_1_comment_only"
    cp -r "$base" "$comment_only"
    sed -i 's/0xB5/0xFF/g' "$comment_only/fw/test/native/avr/test_dispatch/test_configure_memory.cpp"
    printf '%s\n' '// handled via legacy path 0xB5' >> "$comment_only/fw/test/native/avr/test_dispatch/test_configure_memory.cpp"

    local comment_only_rc
    comment_only_rc=$(rc_of dispatch_mirror_planted_drift_exit_1_comment_only.log python3 "$DISPATCH_MIRROR_PY" --wiki-dir "$comment_only/wiki" --app-dir "$comment_only/app" --fw-dir "$comment_only/fw")
    assert_rc "dispatch_mirror_planted_drift_exit_1_comment_only" 0 "$comment_only_rc" || ok=1

    local comment_only_count
    comment_only_count=$(grep -oE '^OK: [0-9]+' "$WORK/dispatch_mirror_planted_drift_exit_1_comment_only.log" | grep -oE '[0-9]+')
    if [ "$comment_only_count" != "$control_count" ]; then
        echo "ERROR: dispatch_mirror_planted_drift_exit_1_comment_only: compared-protocol count changed ($control_count -> $comment_only_count); a commented-out firmware entry must not move the count" >&2
        ok=1
    fi

    record "dispatch_mirror_planted_drift_exit_1_comment_only" 0 "$comment_only_rc" "$control_rc" "commented-out firmware entry (0xB5) is not counted as a dispatch entry; count unchanged at $comment_only_count"

    return "$ok"
}

case_honest01_weakened_claim_exit_1() {
    local repo_root="$WORK/honest01_weakened_claim_exit_1_repo_root"
    local src_repo="$repo_root/fixture-source"
    mkdir -p "$repo_root"
    local sha
    sha=$(new_source_repo "$src_repo")
    local ok=0

    local wiki_dir="$WORK/honest01_weakened_claim_exit_1_wiki"
    mkdir -p "$wiki_dir"
    printf '%s\n' \
        '# Fixture Page' \
        '' \
        'support_status: adapter-required' \
        '' \
        'This chip is adapter-required for programming; the adapter-required note repeats' \
        'here for a second occurrence.' \
        > "$wiki_dir/Fixture-Page.md"

    local table="$WORK/honest01_weakened_claim_exit_1_table.md"
    printf '%s\n' \
        '| Source repo | Source path | Wiki page | Rendered title | Pre-deletion SHA | Moved in |' \
        '|---|---|---|---|---|---|' \
        "| fixture-source | fixture-source/doc/FIXTURE.md | Fixture-Page | Fixture Page | $sha | test |" \
        > "$table"

    local control_rc
    control_rc=$(rc_of honest01_weakened_claim_exit_1_control.log python3 "$HONEST01_PY" --table "$table" --wiki-dir "$wiki_dir" --vocab "$CLAIM_VOCAB" --repo-root "$repo_root")
    assert_rc "honest01_weakened_claim_exit_1_control" 0 "$control_rc" || ok=1

    sed -i 's/This chip is adapter-required for programming/This chip may need an adapter for programming/' "$wiki_dir/Fixture-Page.md"

    local mutated_rc
    mutated_rc=$(rc_of honest01_weakened_claim_exit_1_mutated.log python3 "$HONEST01_PY" --table "$table" --wiki-dir "$wiki_dir" --vocab "$CLAIM_VOCAB" --repo-root "$repo_root")
    assert_rc "honest01_weakened_claim_exit_1" 1 "$mutated_rc" || ok=1

    if ! grep -q 'adapter-required' "$WORK/honest01_weakened_claim_exit_1_mutated.log"; then
        echo "ERROR: honest01_weakened_claim_exit_1: stderr missing adapter-required" >&2
        ok=1
    fi
    if ! grep -q 'Fixture-Page' "$WORK/honest01_weakened_claim_exit_1_mutated.log"; then
        echo "ERROR: honest01_weakened_claim_exit_1: stderr missing Fixture-Page" >&2
        ok=1
    fi

    local evidence_file="$REPO_ROOT/.planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/honest01-weakened-claim-RED.txt"
    {
        echo "command: python3 tools/wiki/honest01_claims.py --table <fixture-table> --wiki-dir <fixture-wiki> --vocab tools/wiki/claim-vocabulary.json --repo-root <fixture-repo-root>"
        echo "mutation: softened one of two adapter-required occurrences on the wiki-side Fixture-Page.md to 'may need an adapter'; the git-committed source fixture (sha $sha) still carries both occurrences"
        echo "control: exit 0 (both sides start at 2 occurrences of adapter-required)"
        echo "result: exit 1"
        echo "--- captured output ---"
        cat "$WORK/honest01_weakened_claim_exit_1_mutated.log"
    } > "$evidence_file"

    record "honest01_weakened_claim_exit_1" 1 "$mutated_rc" "$control_rc" "softened adapter-required (2->1) on the wiki side, source side unchanged; DROPPED bucket names the token and Fixture-Page"

    return "$ok"
}

CASES=(orphan_exit_1 sidebar_link_is_not_evidence broken_link_exit_1 md_suffix_link_exit_1 illegal_filename_exit_1 wiki05_unreferenced_page_exit_1 reference_style_external_citation_exit_0 dotdir_ignored_exit_0 dispatch_mirror_planted_drift_exit_1 honest01_weakened_claim_exit_1)

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

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

CASES=()

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

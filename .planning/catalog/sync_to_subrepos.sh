#!/usr/bin/env bash
#
# Firestarter v1.2 catalog sync.
#
# Copies the canonical messages.toml + codegen.py from the meta-repo into the
# two sub-repos' tools/catalog/ directories. Verifies byte-identical copies
# via `diff -q` after each copy. Exits non-zero on any mismatch.
#
# Authoritative source: .planning/catalog/{messages.toml,codegen.py}
# Targets:
#   firestarter/tools/catalog/{messages.toml,codegen.py}
#   firestarter_app/tools/catalog/{messages.toml,codegen.py}
#
# Idempotent: re-running with no upstream change is a no-op (cp overwrites,
# diff confirms identity). Run after every catalog edit.
#
# Requirements: bash, cp, diff, mkdir. No external deps.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
META_REPO_CATALOG="$SCRIPT_DIR"

FILES=(messages.toml codegen.py)

# Targets are relative to the meta-repo (this script lives at
# .planning/catalog/, so the two sub-repos are ../../{firestarter,firestarter_app}).
TARGETS=(
    "$META_REPO_CATALOG/../../firestarter/tools/catalog"
    "$META_REPO_CATALOG/../../firestarter_app/tools/catalog"
)

exit_code=0

for target in "${TARGETS[@]}"; do
    mkdir -p "$target"
    for f in "${FILES[@]}"; do
        src="$META_REPO_CATALOG/$f"
        dst="$target/$f"
        if [[ ! -f "$src" ]]; then
            echo "ERROR: source missing: $src" >&2
            exit 1
        fi
        cp "$src" "$dst"
        if diff -q "$src" "$dst" >/dev/null; then
            echo "  copied: $f -> $target"
        else
            echo "ERROR: copy mismatch: $src vs $dst" >&2
            exit_code=1
        fi
    done
done

if [[ $exit_code -ne 0 ]]; then
    exit $exit_code
fi

# Cross-sub-repo invariant: both vendored messages.toml copies must be
# byte-identical to each other (the canonical CI assertion from RESEARCH
# §"Authority Assertion"). If this diff fails, the sync left the sub-repos
# inconsistent and downstream codegen will silently diverge.
fs_toml="$META_REPO_CATALOG/../../firestarter/tools/catalog/messages.toml"
fa_toml="$META_REPO_CATALOG/../../firestarter_app/tools/catalog/messages.toml"
if diff -q "$fs_toml" "$fa_toml" >/dev/null; then
    echo "OK: sub-repo catalogs are byte-identical."
else
    echo "ERROR: sub-repo catalogs diverge: $fs_toml vs $fa_toml" >&2
    exit 1
fi

echo "OK: catalog synced to both sub-repos."

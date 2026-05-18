#!/usr/bin/env bash
#
# Firestarter v1.2 catalog sync.
#
# 1. Copies the canonical messages.toml + codegen.py from the meta-repo into
#    both sub-repos' tools/catalog/ directories.
# 2. Regenerates messages.h (firmware) and messages.py (host) in each sub-repo
#    using the freshly-copied codegen.py.
# 3. Verifies byte-identical copies and asserts sub-repo catalog invariant.
#
# Authoritative source: tools/catalog/{messages.toml,codegen.py}
# Generated firmware artifact: firestarter/include/messages.h
# Generated host artifact:     firestarter_app/firestarter/messages.py
#
# Idempotent: re-running with no upstream change is a no-op.
# Run after every catalog or codegen edit.
#
# Requirements: bash, cp, diff, python3, mkdir.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
META_REPO_CATALOG="$SCRIPT_DIR"

FILES=(messages.toml codegen.py)

# Sub-repo tools/catalog/ targets
TARGETS=(
    "$META_REPO_CATALOG/../../firestarter/tools/catalog"
    "$META_REPO_CATALOG/../../firestarter_app/tools/catalog"
)

exit_code=0

# ---------------------------------------------------------------------------
# Step 1: copy messages.toml + codegen.py to each sub-repo
# ---------------------------------------------------------------------------
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
# byte-identical to each other.
fs_toml="$META_REPO_CATALOG/../../firestarter/tools/catalog/messages.toml"
fa_toml="$META_REPO_CATALOG/../../firestarter_app/tools/catalog/messages.toml"
if diff -q "$fs_toml" "$fa_toml" >/dev/null; then
    echo "OK: sub-repo catalogs are byte-identical."
else
    echo "ERROR: sub-repo catalogs diverge: $fs_toml vs $fa_toml" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Step 2: regenerate messages.h in firestarter sub-repo
# ---------------------------------------------------------------------------
FS_ROOT="$META_REPO_CATALOG/../../firestarter"
FA_ROOT="$META_REPO_CATALOG/../../firestarter_app"

echo "Regenerating firestarter/include/messages.h ..."
python3 "$META_REPO_CATALOG/codegen.py" \
    --catalog "$META_REPO_CATALOG/messages.toml" \
    --language cpp \
    --target "$FS_ROOT/include/messages.h"

if diff -q "$FS_ROOT/include/messages.h" "$FS_ROOT/include/messages.h" >/dev/null 2>&1; then
    echo "  OK: firestarter/include/messages.h regenerated."
fi

# ---------------------------------------------------------------------------
# Step 3: regenerate messages.py in firestarter_app sub-repo
# ---------------------------------------------------------------------------
echo "Regenerating firestarter_app/firestarter/messages.py ..."
python3 "$META_REPO_CATALOG/codegen.py" \
    --catalog "$META_REPO_CATALOG/messages.toml" \
    --language python \
    --target "$FA_ROOT/firestarter/messages.py"

if diff -q "$FA_ROOT/firestarter/messages.py" "$FA_ROOT/firestarter/messages.py" >/dev/null 2>&1; then
    echo "  OK: firestarter_app/firestarter/messages.py regenerated."
fi

echo "OK: catalog synced to both sub-repos."

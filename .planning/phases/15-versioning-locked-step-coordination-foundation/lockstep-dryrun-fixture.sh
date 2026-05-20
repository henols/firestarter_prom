#!/usr/bin/env bash
# lockstep-dryrun-fixture.sh
#
# Proves the VER-03 lockstep contract: invoking both sub-repos' update_version.py
# --beta --dry-run --set-version <X.Y.ZbN> produces byte-identical DRY_RUN output.
#
# Usage:
#   bash lockstep-dryrun-fixture.sh                          # uses default BETA_VERSION=1.2.3b1
#   BETA_VERSION=3.1.0b2 bash lockstep-dryrun-fixture.sh    # override
#   BETA_VERSION=0.0.1b1 bash lockstep-dryrun-fixture.sh    # E2E-01 Phase 19 smoke test version
#
# Exit code: 0 on lockstep match; 1 on any mismatch or script error.
#
# Manual probe (D-21 rejection verification — NOT a default behavior):
#   BETA_VERSION=1.2.3beta1 bash lockstep-dryrun-fixture.sh   # should exit 1 in both scripts
#   (Both scripts raise ValueError: version string does not match ^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$)
#
# This fixture is callable from Phase 19's E2E-01 smoke test as a pre-flight check.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
META_REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
APP_REPO="$META_REPO_ROOT/firestarter_app"
FW_REPO="$META_REPO_ROOT/firestarter"
BETA_VERSION="${BETA_VERSION:-1.2.3b1}"

echo "LOCKSTEP DRY-RUN FIXTURE"
echo "========================"
echo "Meta-repo root: $META_REPO_ROOT"
echo "App repo:       $APP_REPO"
echo "Firmware repo:  $FW_REPO"
echo "BETA_VERSION:   $BETA_VERSION"
echo ""

# Verify both sub-repos exist with the expected script
for REPO_PATH in "$APP_REPO" "$FW_REPO"; do
    if [[ ! -f "$REPO_PATH/.github/scripts/update_version.py" ]]; then
        echo "ERROR: $REPO_PATH/.github/scripts/update_version.py not found" >&2
        exit 1
    fi
done

# Invoke app dry-run (capture both stdout and stderr; failures abort via set -e)
APP_OUTPUT="$(cd "$APP_REPO" && python3 .github/scripts/update_version.py --beta --dry-run --set-version "$BETA_VERSION" 2>&1)"
APP_VERSION="$(echo "$APP_OUTPUT" | grep '^DRY_RUN:' | head -1 | awk '{print $2}')"

# Invoke firmware dry-run
FW_OUTPUT="$(cd "$FW_REPO" && python3 .github/scripts/update_version.py --beta --dry-run --set-version "$BETA_VERSION" 2>&1)"
FW_VERSION="$(echo "$FW_OUTPUT" | grep '^DRY_RUN:' | head -1 | awk '{print $2}')"

echo "App emits:       DRY_RUN: $APP_VERSION"
echo "Firmware emits:  DRY_RUN: $FW_VERSION"
echo ""

# Assert byte-identity: both must equal the requested BETA_VERSION
if [[ "$APP_VERSION" == "$FW_VERSION" ]] && [[ "$APP_VERSION" == "$BETA_VERSION" ]]; then
    echo "LOCKSTEP OK"
    exit 0
else
    echo "LOCKSTEP FAILED: app=$APP_VERSION firmware=$FW_VERSION expected=$BETA_VERSION" >&2
    echo "" >&2
    echo "--- App stdout ---" >&2
    echo "$APP_OUTPUT" >&2
    echo "--- Firmware stdout ---" >&2
    echo "$FW_OUTPUT" >&2
    exit 1
fi

#!/usr/bin/env bash
set -e

echo "=== Generating platformio.ini wrapper ==="
python3 /workspaces/.devcontainer/gen-platformio-ini.py

echo "=== Installing Python CLI (dev mode) ==="
pip install -e /workspaces/firestarter_app

echo "=== Initialising PlatformIO project dependencies ==="
cd /workspaces/firestarter && pio pkg install

echo "=== Done ==="

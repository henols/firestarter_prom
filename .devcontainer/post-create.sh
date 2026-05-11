#!/usr/bin/env bash
set -e

echo "=== Installing Python CLI (dev mode) ==="
cd firestarter_app
pip install -e .
cd ..

echo "=== Initialising PlatformIO project dependencies ==="
cd firestarter
pio pkg install
cd ..

echo "=== Done ==="

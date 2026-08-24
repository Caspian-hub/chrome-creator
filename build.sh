#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo
echo "========================================================"
echo "  Chrome Profile Creator - Build"
echo "========================================================"
echo

echo "[1/3] Installing dependencies..."
python3 -m pip install --upgrade pip -q
python3 -m pip install . pyinstaller -q || {
    echo "[ERROR] Failed to install dependencies."
    exit 1
}

echo "[2/3] Building executable..."
python3 build.py || {
    echo "[ERROR] Build failed."
    exit 1
}

echo
echo "[3/3] Done! (build and __pycache__ cleaned up)"
echo "Output folder: $(pwd)/ChromeProfileTool"
echo

#!/bin/bash
set -e

# Build the release zip for HACS / manual install.

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$REPO_DIR/build"
OUT="$REPO_DIR/custom_components/luxmon.zip"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/custom_components"

cp -r "$REPO_DIR/custom_components/luxmon" "$BUILD_DIR/custom_components/"

# Remove Python cache and hidden files before zipping.
find "$BUILD_DIR/custom_components/luxmon" \
    -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find "$BUILD_DIR/custom_components/luxmon" \
    -type f \( -name '*.pyc' -o -name '.DS_Store' -o -name '.addon-defaults.json' \) -delete

rm -f "$OUT"

cd "$BUILD_DIR"
zip -r "$OUT" custom_components/luxmon

echo "Built: $OUT"

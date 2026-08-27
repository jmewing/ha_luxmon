#!/bin/bash
set -e

# Local validation script that does not require the Home Assistant core
# checkout (which is Python 3.13-incompatible at this revision).

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== Python compile check ==="
python3 -m py_compile "$REPO_DIR"/custom_components/luxmon/*.py

echo "=== JSON manifest check ==="
python3 -m json.tool "$REPO_DIR"/custom_components/luxmon/manifest.json > /dev/null

echo "=== Translation JSON check ==="
python3 -m json.tool "$REPO_DIR"/custom_components/luxmon/strings.json > /dev/null
python3 -m json.tool "$REPO_DIR"/custom_components/luxmon/translations/en.json > /dev/null

echo "=== HACS JSON check ==="
python3 -m json.tool "$REPO_DIR"/hacs.json > /dev/null

if [ -d "$REPO_DIR"/tests ]; then
    echo "=== Running pytest ==="
    cd "$REPO_DIR"
    python3 -m pytest tests/ -q
fi

echo "=== Validation passed ==="

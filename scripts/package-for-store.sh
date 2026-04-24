#!/usr/bin/env bash
# Build dist/<slug>-<version>.zip for Chrome Web Store upload.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VER=$(python3 -c "import json; print(json.load(open('$ROOT/manifest.json'))['version'])")
SLUG="hide-x-followers"
OUT_DIR="$ROOT/dist"
OUT_ZIP="$OUT_DIR/${SLUG}-${VER}.zip"
mkdir -p "$OUT_DIR"
cd "$ROOT"
rm -f "$OUT_ZIP"
zip -r "$OUT_ZIP" \
  manifest.json \
  content.js \
  _locales/ \
  icons/ \
  -x "*.DS_Store" -x "*/.DS_Store"
echo "Created: $OUT_ZIP"
unzip -l "$OUT_ZIP"

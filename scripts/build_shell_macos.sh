#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OUT=${1:-dist}
case "$OUT" in
  /*) ;;
  *) OUT="$ROOT/$OUT" ;;
esac
VENV="$OUT/.macos-build-venv"
ONEDIR="$OUT/itembank-sidecar-onedir"

cd "$ROOT"
echo "Building the portable runtime"
python3 build.py --out "$OUT"

if [ ! -x "$VENV/bin/pyinstaller" ]; then
  echo "Creating the pinned macOS packaging environment"
  python3 -m venv "$VENV"
  "$VENV/bin/python" -m pip install --disable-pip-version-check -r requirements-build.txt
fi

echo "Freezing the self-contained sidecar"
rm -rf "$ONEDIR" "$OUT/.pyinstaller-work" "$OUT/.pyinstaller-spec"
"$VENV/bin/pyinstaller" \
  --onedir --noupx --clean \
  --name itembank-sidecar \
  --distpath "$ONEDIR" \
  --workpath "$OUT/.pyinstaller-work" \
  --specpath "$OUT/.pyinstaller-spec" \
  --add-data "$ROOT/schemas:schemas" \
  --add-data "$ROOT/styles:styles" \
  --add-data "$ROOT/fonts:fonts" \
  "$ROOT/itembank.py"

test -x "$ONEDIR/itembank-sidecar/itembank-sidecar"
SIZE_KIB=$(du -sk "$ONEDIR/itembank-sidecar" | awk '{print $1}')
echo "Frozen sidecar size: $((SIZE_KIB / 1024)) MiB"

echo "Building the macOS app"
npx --yes @tauri-apps/cli@2 build --config src-tauri/tauri.conf.json --bundles app

APP="$ROOT/src-tauri/target/release/bundle/macos/itembank.app"
test -d "$APP"

# Sign only after Tauri has embedded the complete PyInstaller directory.
# This local ad-hoc signature makes the bundle internally consistent. Public
# downloads still need an Apple Developer ID signature and notarization.
codesign --force --deep --sign - "$APP"
codesign --verify --deep --strict "$APP"

mkdir -p "$OUT"
rm -rf "$OUT/itembank.app"
ditto "$APP" "$OUT/itembank.app"

DMG_STAGE=$(mktemp -d "$OUT/.itembank-dmg.XXXXXX")
trap 'rm -rf "$DMG_STAGE"' EXIT INT TERM
ditto "$APP" "$DMG_STAGE/itembank.app"
ln -s /Applications "$DMG_STAGE/Applications"
hdiutil create \
  -volname "itembank" \
  -srcfolder "$DMG_STAGE" \
  -ov -format UDZO \
  "$OUT/itembank-$(uname -m).dmg"
hdiutil verify "$OUT/itembank-$(uname -m).dmg"

echo "App: $OUT/itembank.app"
echo "Installer: $OUT/itembank-$(uname -m).dmg"

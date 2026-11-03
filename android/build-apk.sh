#!/usr/bin/env bash
# Builds dist/the-quiet.apk from the-quiet.html without Gradle or Android Studio.
#
# Needs: a JDK (javac, keytool), curl, unzip, zip.
# The Android build-tools and platform jar are downloaded once into android/.sdk/
# (or point ANDROID_BUILD_TOOLS / ANDROID_JAR at an existing SDK).
#
# The APK is signed with android/debug.keystore, created on first run. Keep that
# file if you want later builds to install as updates over this one; it is not
# committed to git.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
SDK="$HERE/.sdk"
BUILD="$HERE/build"
OUT="$ROOT/dist/the-quiet.apk"
THREE_URL="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"
VERSION_CODE="${VERSION_CODE:-1}"
VERSION_NAME="${VERSION_NAME:-1.0}"

if [[ -z "${ANDROID_BUILD_TOOLS:-}" || -z "${ANDROID_JAR:-}" ]]; then
  mkdir -p "$SDK"
  if [[ ! -x "$SDK/android-15/aapt2" ]]; then
    echo "Downloading Android build-tools 35..."
    curl -fsSL -o "$SDK/bt.zip" https://dl.google.com/android/repository/build-tools_r35_linux.zip
    (cd "$SDK" && unzip -q -o bt.zip && rm bt.zip)
  fi
  if [[ ! -f "$SDK/android-35/android.jar" ]]; then
    echo "Downloading Android platform 35..."
    curl -fsSL -o "$SDK/pl.zip" https://dl.google.com/android/repository/platform-35_r02.zip
    (cd "$SDK" && unzip -q -o pl.zip && rm pl.zip)
  fi
  ANDROID_BUILD_TOOLS="$SDK/android-15"
  ANDROID_JAR="$SDK/android-35/android.jar"
fi
BT="$ANDROID_BUILD_TOOLS"

rm -rf "$BUILD"; mkdir -p "$BUILD/assets/www" "$BUILD/classes" "$BUILD/dex" "$(dirname "$OUT")"

# 1. Web assets: the game, with three.js bundled locally so it runs offline
if [[ ! -f "$SDK/three.min.js" ]]; then mkdir -p "$SDK"; curl -fsSL -o "$SDK/three.min.js" "$THREE_URL"; fi
cp "$SDK/three.min.js" "$BUILD/assets/www/three.min.js"
sed "s#<script src=\"$THREE_URL\"></script>#<script src=\"three.min.js\"></script>#" "$ROOT/the-quiet.html" > "$BUILD/assets/www/index.html"
grep -q '<script src="three.min.js"></script>' "$BUILD/assets/www/index.html" || { echo "could not rewrite the three.js script tag" >&2; exit 1; }

# 2. Resources + manifest
"$BT/aapt2" compile --dir "$HERE/res" -o "$BUILD/res.zip"
"$BT/aapt2" link -o "$BUILD/base.apk" -I "$ANDROID_JAR" --manifest "$HERE/AndroidManifest.xml" \
  -A "$BUILD/assets" "$BUILD/res.zip" --min-sdk-version 24 --target-sdk-version 35 \
  --version-code "$VERSION_CODE" --version-name "$VERSION_NAME"

# 3. Java -> dex
javac -nowarn -source 11 -target 11 -classpath "$ANDROID_JAR" -d "$BUILD/classes" \
  $(find "$HERE/src" -name '*.java') 2>&1 | grep -v "bootstrap classpath" || true
"$BT/d8" --release --min-api 24 --lib "$ANDROID_JAR" --output "$BUILD/dex" $(find "$BUILD/classes" -name '*.class')

# 4. Package, align, sign
cp "$BUILD/base.apk" "$BUILD/unaligned.apk"
(cd "$BUILD/dex" && zip -q -j "$BUILD/unaligned.apk" classes.dex)
"$BT/zipalign" -p -f 4 "$BUILD/unaligned.apk" "$BUILD/aligned.apk"
KS="$HERE/debug.keystore"
if [[ ! -f "$KS" ]]; then
  keytool -genkeypair -keystore "$KS" -storepass android -keypass android -alias thequiet \
    -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=The Quiet, O=Hobby, C=US" >/dev/null 2>&1
fi
"$BT/apksigner" sign --ks "$KS" --ks-pass pass:android --key-pass pass:android --ks-key-alias thequiet \
  --out "$OUT" "$BUILD/aligned.apk"
"$BT/apksigner" verify "$OUT"
rm -f "$OUT.idsig"
echo "Built $OUT ($(du -h "$OUT" | cut -f1))"

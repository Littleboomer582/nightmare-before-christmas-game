#!/usr/bin/env bash
# Builds android/dist/DeadEndDepot.apk from zombies.html without the Android SDK.
# Needs: a JDK (javac, java, keytool), python3, npm, curl. Downloads its tools from Maven Central
# and npm into android/.cache the first time.
#
#   android/build.sh [versionCode] [versionName]
#
# Signing: uses $KEYSTORE (PKCS12, password $KEYSTORE_PASS, alias $KEY_ALIAS). If it doesn't exist,
# a new key is created there. Keep that file safe: Android only installs updates signed with the
# same key, so a new key means uninstalling the old app first.
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(dirname "$HERE")
CACHE=${CACHE:-$HERE/.cache}
DIST=$HERE/dist
KEYSTORE=${KEYSTORE:-$HERE/keystore/release.p12}
KEYSTORE_PASS=${KEYSTORE_PASS:-dead-end-depot}
KEY_ALIAS=${KEY_ALIAS:-dead-end-depot}
VERSION_CODE=${1:-1}
VERSION_NAME=${2:-1.0}
MIN_SDK=24
mkdir -p "$CACHE/tools" "$CACHE/npm" "$DIST"

fetch() {   # Maven Central rate-limits bursts, so retry with backoff
  [ -s "$2" ] && return 0
  for i in 1 2 3 4 5 6; do
    if curl -fsS --max-time 120 -o "$2.part" "$1"; then mv "$2.part" "$2"; return 0; fi
    sleep $((i * 8))
  done
  echo "could not download $1" >&2; return 1
}
MC=https://repo1.maven.org/maven2
fetch $MC/com/jakewharton/android/repackaged/dalvik-dx/16.0.1/dalvik-dx-16.0.1.jar "$CACHE/tools/dx.jar"
fetch $MC/com/google/android/android/4.1.1.4/android-4.1.1.4.jar "$CACHE/tools/android-stubs.jar"
fetch $MC/com/android/tools/build/apksig/2.3.0/apksig-2.3.0.jar "$CACHE/tools/apksig.jar"

# offline web assets: the game plus local fonts and three.js
( cd "$CACHE/npm"
  for pkg in @fontsource/creepster @fontsource/special-elite @fontsource/oswald @fontsource/teko three@0.128.0; do
    name=$(echo "$pkg" | sed 's/^@//; s/\//-/; s/@.*//')
    ls -d "$name"-*/ >/dev/null 2>&1 && continue
    tgz=$(npm pack -q "$pkg" | tail -1); d=${tgz%.tgz}; mkdir -p "$d"; tar xzf "$tgz" -C "$d"
  done )
python3 "$HERE/tools/apk.py" web "$ROOT/zombies.html" "$CACHE/npm" "$CACHE/web"

# Java -> Dalvik bytecode. The JavascriptInterface stub is only for compiling.
rm -rf "$CACHE/classes" "$CACHE/stubclasses"
javac -Xlint:-options --release 8 -d "$CACHE/stubclasses" "$HERE/app/stubs/android/webkit/JavascriptInterface.java"
javac -Xlint:-options --release 8 -cp "$CACHE/tools/android-stubs.jar:$CACHE/stubclasses" -d "$CACHE/classes" \
  "$HERE/app/src/com/deadenddepot/zombies/MainActivity.java"
java -cp "$CACHE/tools/dx.jar" com.android.dx.command.Main --dex --min-sdk-version=$MIN_SDK --output="$CACHE/classes.dex" "$CACHE/classes"

python3 "$HERE/tools/apk.py" pack "$CACHE/classes.dex" "$HERE/app/icon.png" "$CACHE/web" "$CACHE/unsigned.apk" "$VERSION_CODE" "$VERSION_NAME"

if [ ! -f "$KEYSTORE" ]; then
  mkdir -p "$(dirname "$KEYSTORE")"
  keytool -genkeypair -keystore "$KEYSTORE" -storetype PKCS12 -storepass "$KEYSTORE_PASS" -keypass "$KEYSTORE_PASS" \
    -alias "$KEY_ALIAS" -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=Dead End Depot" 2>&1 | grep -v '^Picked up' || true
fi
rm -rf "$CACHE/signer"; mkdir -p "$CACHE/signer"
javac -Xlint:-options -cp "$CACHE/tools/apksig.jar" -d "$CACHE/signer" "$HERE/tools/Sign.java"
# this apksig release predates Java's module system and needs a JDK internal opened up
java --add-exports java.base/sun.security.x509=ALL-UNNAMED -cp "$CACHE/tools/apksig.jar:$CACHE/signer" Sign "$KEYSTORE" "$KEYSTORE_PASS" "$KEY_ALIAS" \
  "$CACHE/unsigned.apk" "$DIST/DeadEndDepot.apk" $MIN_SDK
echo "built $DIST/DeadEndDepot.apk"

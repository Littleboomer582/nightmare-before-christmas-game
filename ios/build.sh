#!/usr/bin/env bash
# Builds ios/dist/DeadEndDepot.ipa (unsigned) from zombies.html. Needs a Mac with Xcode; the
# GitHub workflow in .github/workflows/ios.yml runs this on a macOS runner.
#
#   ios/build.sh [versionCode] [versionName]
#
# The IPA is not signed for any device: install it with a sideloading tool (Sideloadly, AltStore),
# which signs it with your Apple ID, or sign it yourself with an Apple Developer account.
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(dirname "$HERE")
VERSION_CODE=${1:-1}
VERSION_NAME=${2:-1.0}
BUILD=${BUILD:-$HERE/build}
APP="$BUILD/Payload/DeadEndDepot.app"
MIN_IOS=15.0
rm -rf "$BUILD"; mkdir -p "$APP" "$BUILD/npm" "$HERE/dist"

# the game, offline: local fonts and three.js instead of Google Fonts and the CDN (same as Android)
( cd "$BUILD/npm"
  for pkg in @fontsource/creepster @fontsource/special-elite @fontsource/oswald @fontsource/teko three@0.128.0; do
    tgz=$(npm pack -q "$pkg" | tail -1); d=${tgz%.tgz}; mkdir -p "$d"; tar xzf "$tgz" -C "$d"
  done )
python3 "$ROOT/android/tools/apk.py" web "$ROOT/zombies.html" "$BUILD/npm" "$APP/web"

# the app: one Swift file, compiled for arm64 iPhones and iPads
SDK=$(xcrun --sdk iphoneos --show-sdk-path)
xcrun -sdk iphoneos swiftc -O -target "arm64-apple-ios$MIN_IOS" -sdk "$SDK" \
  -o "$APP/DeadEndDepot" "$HERE/App/main.swift"

# Info.plist with the version filled in
sed -e "s/@VERSION_CODE@/$VERSION_CODE/" -e "s/@VERSION_NAME@/$VERSION_NAME/" "$HERE/Info.plist" > "$APP/Info.plist"
SDKV=$(xcrun --sdk iphoneos --show-sdk-version)
/usr/libexec/PlistBuddy -c "Add :DTPlatformName string iphoneos" -c "Add :DTSDKName string iphoneos$SDKV" -c "Add :DTPlatformVersion string $SDKV" "$APP/Info.plist"

# app icon: an asset catalog compiled to Assets.car, its keys merged into Info.plist
ICONSET="$BUILD/Assets.xcassets/AppIcon.appiconset"; mkdir -p "$ICONSET"
cp "$HERE/icon-1024.png" "$ICONSET/icon-1024.png"
cat > "$ICONSET/Contents.json" <<'JSON'
{ "images": [ { "filename": "icon-1024.png", "idiom": "universal", "platform": "ios", "size": "1024x1024" } ], "info": { "author": "xcode", "version": 1 } }
JSON
echo '{ "info": { "author": "xcode", "version": 1 } }' > "$BUILD/Assets.xcassets/Contents.json"
xcrun actool "$BUILD/Assets.xcassets" --compile "$APP" --platform iphoneos --minimum-deployment-target "$MIN_IOS" \
  --app-icon AppIcon --target-device iphone --target-device ipad --output-partial-info-plist "$BUILD/assets.plist" --output-format human-readable-text
/usr/libexec/PlistBuddy -c "Merge $BUILD/assets.plist" "$APP/Info.plist"
plutil -lint "$APP/Info.plist"

# an ad-hoc signature (sideloading tools replace it with yours)
codesign --force --sign - --timestamp=none "$APP"

# package: Payload/DeadEndDepot.app inside a zip
rm -f "$HERE/dist/DeadEndDepot.ipa"
( cd "$BUILD" && zip -qry "$HERE/dist/DeadEndDepot.ipa" Payload )
echo "built $HERE/dist/DeadEndDepot.ipa ($(du -k "$HERE/dist/DeadEndDepot.ipa" | cut -f1) KB)"

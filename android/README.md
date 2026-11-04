# Dead Reckoning for Android

A small WebView app that runs the game (`zombies.html`) full screen, in landscape,
with touch controls and everything bundled so it plays offline.

## Build

1. Copy the latest game into the app: `python3 sync-web.py`
2. Build with the Android SDK (platform 34, build-tools 34) and Gradle 8.9 or newer:

   ```
   export ANDROID_HOME=/path/to/android-sdk
   gradle assembleRelease
   ```

The APK lands in `app/build/outputs/apk/release/app-release.apk`. A prebuilt copy is in
`dist/DeadReckoning.apk` at the repo root.

It is signed with `keystore/dead-reckoning.jks` so new builds install over old ones.
That key only identifies this hobby app; make your own before publishing anywhere.

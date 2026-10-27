#!/usr/bin/env bash
# Android build used by .github/workflows/android.yml (also runs on any Linux/macOS machine with Node and Java 21).
#   - test APK (operator mode on)   -> $OUT_DIR/orbit-hop-test.apk
#   - Play bundle (operator mode off), only when ORBITHOP_KEYSTORE is set -> $OUT_DIR/orbit-hop-<code>.aab
set -euo pipefail
cd "$(dirname "$0")/.."
OUT_DIR="${OUT_DIR:-$PWD/dist}"
mkdir -p "$OUT_DIR"

# Android SDK: use the one on the machine if it has command-line tools, otherwise install a private copy
SDKMANAGER=""
for candidate in "${ANDROID_HOME:-}/cmdline-tools/latest/bin/sdkmanager" "${ANDROID_SDK_ROOT:-}/cmdline-tools/latest/bin/sdkmanager"; do
  if [ -x "$candidate" ]; then SDKMANAGER="$candidate"; break; fi
done
if [ -z "$SDKMANAGER" ]; then
  echo "== Installing Android command-line tools"
  export ANDROID_HOME="${RUNNER_TEMP:-$HOME}/android-sdk"
  mkdir -p "$ANDROID_HOME/cmdline-tools"
  curl -fsSL -o "$ANDROID_HOME/clt.zip" https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
  unzip -q "$ANDROID_HOME/clt.zip" -d "$ANDROID_HOME/cmdline-tools"
  mv "$ANDROID_HOME/cmdline-tools/cmdline-tools" "$ANDROID_HOME/cmdline-tools/latest"
  SDKMANAGER="$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager"
fi
export ANDROID_HOME="${ANDROID_HOME:-$(cd "$(dirname "$SDKMANAGER")/../../.." && pwd)}"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
echo "== Android SDK at $ANDROID_HOME"
yes | "$SDKMANAGER" --licenses > /dev/null || true
"$SDKMANAGER" --install "platform-tools" "platforms;android-36" > /dev/null

echo "== Test APK (operator mode on)"
npm run build:dev
npx cap sync android
(cd android && ./gradlew --no-daemon assembleDebug)
cp android/app/build/outputs/apk/debug/app-debug.apk "$OUT_DIR/orbit-hop-test.apk"

if [ -n "${ORBITHOP_KEYSTORE:-}" ]; then
  echo "== Play bundle (operator mode off)"
  npm run build
  npx cap sync android
  (cd android && ./gradlew --no-daemon bundleRelease)
  cp android/app/build/outputs/bundle/release/app-release.aab "$OUT_DIR/orbit-hop-${ORBITHOP_VERSION_CODE:-1}.aab"
else
  echo "== No upload key: skipping the Play bundle"
fi
echo "== Done: $(ls "$OUT_DIR")"

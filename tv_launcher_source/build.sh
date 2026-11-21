#!/bin/bash
set -e

cd "$(dirname "$0")"

# 1. Locate Java
if [ -z "$JAVA_HOME" ]; then
    if [ -d "/Applications/Android Studio.app/Contents/jbr/Contents/Home" ]; then
        export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
    fi
fi
if [ -n "$JAVA_HOME" ]; then
    export PATH="$JAVA_HOME/bin:$PATH"
fi

# 2. Locate Android SDK
SDK_ROOT="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-$HOME/Library/Android/sdk}}"

if [ -z "$ANDROID_JAR" ]; then
    ANDROID_JAR=$(find "$SDK_ROOT/platforms" -name "android.jar" 2>/dev/null | sort -V | tail -n 1)
fi

if [ -z "$BUILD_TOOLS" ]; then
    BUILD_TOOLS=$(find "$SDK_ROOT/build-tools" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort -V | tail -n 1)
fi

# 3. Locate kotlinc & kotlin-stdlib
if [ -z "$KOTLINC" ]; then
    if [ -f "/Applications/Android Studio.app/Contents/plugins/Kotlin/kotlinc/bin/kotlinc" ]; then
        KOTLINC="/Applications/Android Studio.app/Contents/plugins/Kotlin/kotlinc/bin/kotlinc"
        KOTLIN_LIB="/Applications/Android Studio.app/Contents/plugins/Kotlin/kotlinc/lib"
    elif command -v kotlinc >/dev/null 2>&1; then
        KOTLINC="kotlinc"
        KOTLIN_BIN_DIR="$(dirname "$(which kotlinc)")"
        KOTLIN_LIB="$(dirname "$KOTLIN_BIN_DIR")/lib"
        if [ ! -f "$KOTLIN_LIB/kotlin-stdlib.jar" ]; then
            KOTLIN_LIB="/usr/share/kotlin/lib"
        fi
    fi
fi

if [ ! -f "$ANDROID_JAR" ]; then
    echo "Error: android.jar not found at $ANDROID_JAR"
    exit 1
fi

if [ ! -d "$BUILD_TOOLS" ]; then
    echo "Error: build-tools directory not found at $BUILD_TOOLS"
    exit 1
fi

AAPT2="$BUILD_TOOLS/aapt2"
D8="$BUILD_TOOLS/d8"
ZIPALIGN="$BUILD_TOOLS/zipalign"
APKSIGNER="$BUILD_TOOLS/apksigner"

echo "Using Android JAR: $ANDROID_JAR"
echo "Using Build Tools: $BUILD_TOOLS"
echo "Using Kotlinc:     $KOTLINC"

rm -rf obj bin compiled_res.zip unaligned.apk aligned.apk classes.dex lean_home.apk
mkdir -p obj bin

echo "1. Compiling resources with aapt2..."
"$AAPT2" compile --dir res -o compiled_res.zip

echo "2. Linking resources and generating R.java..."
"$AAPT2" link -I "$ANDROID_JAR" compiled_res.zip --manifest AndroidManifest.xml -o unaligned.apk --java src --auto-add-overlay

echo "3. Compiling Kotlin and Java sources with kotlinc..."
"$KOTLINC" -cp "$ANDROID_JAR" -jvm-target 1.8 -d obj $(find src -name "*.kt" -o -name "*.java")

echo "4. Converting bytecode to DEX with d8..."
CLASS_FILES=$(find obj -name "*.class")

STDLIB_JAR="$KOTLIN_LIB/kotlin-stdlib.jar"
if [ ! -f "$STDLIB_JAR" ]; then
    # Try finding kotlin-stdlib in system
    STDLIB_JAR=$(find /usr -name "kotlin-stdlib*.jar" 2>/dev/null | head -n 1 || true)
fi

if [ -f "$STDLIB_JAR" ]; then
    "$D8" --lib "$ANDROID_JAR" --output . $CLASS_FILES "$STDLIB_JAR" 2>/dev/null || \
    "$D8" --lib "$ANDROID_JAR" --output . $CLASS_FILES "$STDLIB_JAR"
else
    "$D8" --lib "$ANDROID_JAR" --output . $CLASS_FILES
fi

echo "5. Adding classes.dex to APK..."
zip -u unaligned.apk classes.dex

echo "6. Aligning APK with zipalign..."
"$ZIPALIGN" -f -p 4 unaligned.apk aligned.apk

echo "7. Signing APK..."
if [ ! -f debug.keystore ]; then
    keytool -genkey -v -keystore debug.keystore -storepass android -alias androiddebugkey -keypass android -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=Android Debug,O=Android,C=US"
fi

"$APKSIGNER" sign --ks debug.keystore --ks-pass pass:android --ks-key-alias androiddebugkey --key-pass pass:android --out lean_home.apk aligned.apk

echo "BUILD SUCCESS! Resulting APK: lean_home.apk"
ls -lh lean_home.apk

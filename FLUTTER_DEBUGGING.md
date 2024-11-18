# Flutter Development & Debugging with ADB

## 1. Flutter App Installation

```bash
# Build Flutter APK
flutter build apk --release

# Install via ADB
adb install build/app/outputs/flutter-app-release.apk

# Install debug APK
flutter install

# Uninstall
adb uninstall com.example.app
```

## 2. Hot Reload & Hot Restart

```bash
# Hot reload
flutter hot-reload

# Hot restart
flutter hot-restart

# Via ADB
adb shell am start -n com.example.app/.MainActivity
```

## 3. Debugging

```bash
# Enable debug logs
adb logcat | grep "flutter"

# Debug mode
flutter run -v

# Profiling
flutter run --profile

# Release mode
flutter run --release
```

## 4. Performance Analysis

```bash
# Timeline profiling
flutter run --profile
# Then in app, check DevTools

# Memory profiling
adb shell dumpsys meminfo com.example.app

# Frame rate
adb shell dumpsys gfxinfo com.example.app
```

## 5. State Management Testing

```bash
# Test Provider
# Use DevTools to inspect state

# Monitor rebuilds
flutter run -v | grep "rebuild"
```


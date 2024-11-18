# Android Versions & ADB Compatibility

## 1. Android Version Overview

### Version History with ADB
```
Android 4.0 (API 14): ICS - Legacy
Android 5.0-5.1 (API 21-22): Lollipop - Runtime permissions introduced
Android 6.0 (API 23): Marshmallow - Runtime permissions required
Android 7.0-7.1 (API 24-25): Nougat - Multi-window support
Android 8.0-8.1 (API 26-27): Oreo - Background limits
Android 9.0 (API 28): Pie - Gesture navigation
Android 10 (API 29): Q - Scoped storage
Android 11 (API 30): R - More storage restrictions
Android 12 (API 31): S - Material You design
Android 13 (API 32): T - Per-app language
Android 14 (API 33): U - Lockdown mode
Android 15 (API 34): V - Latest features
```

---

## 2. Permission Models by Version

### Runtime Permissions (Android 6.0+)
```bash
# Android 6.0 and above require runtime permission grants
adb shell pm grant com.example.app android.permission.CAMERA

# List permissions
adb shell pm list permissions

# Check granted permissions
adb shell dumpsys package com.example.app | grep permission
```

### Legacy Permissions (Android 5.1 and below)
```bash
# Android 5.1: Manifest only, no runtime grants
# These devices typically not supported in modern apps
```

---

## 3. Feature Support by API Level

### Android 14+ Features
```bash
# API 34 (Android 14)
- Predictive Back Gesture
- User-facing Easter Eggs

# Check if supported
adb shell getprop ro.build.version.sdk
# Output: 34
```

### Android 13 Features
```bash
# API 32 (Android 13)
- Per-app language selection
adb shell settings get global per_app_language

# Material You theming
adb shell settings get global theme_customization_overlay_packages
```

### Android 12 Features
```bash
# API 31 (Android 12)
- Material You design
- Approximate location
- Clipboard access notifications
```

---

## 4. Checking Android Version

### Get Version
```bash
# Release name
adb shell getprop ro.build.version.release
# Output: 14.0

# API Level
adb shell getprop ro.build.version.sdk
# Output: 34

# Build number
adb shell getprop ro.build.display.id

# Full fingerprint
adb shell getprop ro.build.fingerprint
```

---

## 5. Version-Specific ADB Commands

### Android 10+ Scoped Storage
```bash
# Access to SAF (Storage Access Framework)
adb shell ls /sdcard/
# Limited access compared to Android 9

# App-specific directory (always accessible)
adb shell ls /sdcard/Android/data/com.example.app/
```

### Android 9- Direct File Access
```bash
# Full sdcard access
adb shell ls /sdcard/

# All directories accessible
adb shell ls /sdcard/DCIM/
adb shell ls /sdcard/Documents/
```

---

## 6. Device Testing Matrix

```bash
#!/bin/bash
# test_compatibility.sh

# Test on multiple Android versions
DEVICES=$(adb devices | grep device | awk '{print $1}')

for device in $DEVICES; do
    VERSION=$(adb -s "$device" shell getprop ro.build.version.release)
    API=$(adb -s "$device" shell getprop ro.build.version.sdk)
    
    echo "$device: Android $VERSION (API $API)"
    
    # Run version-specific tests
    case "$API" in
        34) echo "  - Android 14 features available" ;;
        33) echo "  - Android 13 features available" ;;
        32) echo "  - Android 12 features available" ;;
        *) echo "  - Legacy Android version" ;;
    esac
done
```

---

## 7. Minimum API Support

### Common App Requirements
```
YouTube:         API 24+ (Android 7.0)
Gmail:           API 24+ (Android 7.0)
Google Maps:     API 24+ (Android 7.0)
WhatsApp:        API 24+ (Android 7.0)
Modern apps:     API 28+ (Android 9.0)
Latest apps:     API 30+ (Android 11.0)
```

### Check App Requirements
```bash
# Pull APK
adb pull /data/app/com.example.app/base.apk

# Extract AndroidManifest.xml
unzip base.apk AndroidManifest.xml

# Check with aapt
aapt dump badging base.apk | grep "sdk"
# Output: sdkVersion:'24' targetSdkVersion:'34'
```

---

## 8. Version-Specific Testing

### Test All Versions
```bash
#!/bin/bash
# test_all_versions.sh

# Create emulators for key versions
for api in 24 28 30 31 32 33 34; do
    avdmanager create avd -n "Android${api}" \
        -k "system-images;android-${api};google_apis;x86_64"
done

# Run app on each
for api in 24 28 30 31 32 33 34; do
    echo "Testing on Android API $api"
    emulator -avd "Android${api}" &
    EMULATOR_PID=$!
    
    sleep 10
    adb install app.apk
    adb shell am start -n com.example.app/.MainActivity
    
    sleep 5
    adb logcat | grep -i "error\|crash"
    
    kill $EMULATOR_PID
done
```

---

## 9. Behavior Changes by Version

### Android 14 Changes
```bash
# Predictive Back
adb shell getprop ro.predictive_back_gesture_enabled

# Private space
adb shell getprop ro.lockscreen_private_space_visible
```

### Android 13 Changes
```bash
# Approximate location
adb shell pm grant com.example.app android.permission.ACCESS_COARSE_LOCATION

# Clipboard access
adb shell settings put secure clipboard_monitoring_enabled 0
```

### Android 12 Changes
```bash
# Bluetooth 5.2
adb shell getprop ro.hardware.bluetooth

# Material You
adb shell settings put secure theme_customization_overlay_packages com.android.theme.icon.system
```

---

## 10. Deprecated Features by Version

```
Android 6.0:
- Apache HTTP client removed
- File URIs no longer allowed

Android 7.0:
- /system write-protection
- WRITE_SETTINGS permission restricted

Android 9.0:
- Non-encrypted traffic blocked
- Direct access to /proc/net removed

Android 10:
- Scoped storage enforcement
- /sdcard direct access limited

Android 11:
- Legacy storage deprecated
- /system/priv-app access removed

Android 12:
- Clipboard access notifications
- Sensitive permissions more restricted

Android 13+:
- Further storage restrictions
- MAC randomization default
```

---

## 11. ADB Features by Version

```
Android 4.0-4.4: Basic ADB
Android 5.0-5.1: Improved stability
Android 6.0+: Runtime permissions via ADB
Android 10+: Storage restrictions affect ADB access
Android 11+: SELinux stricter
Android 12+: Extended hibernation
Android 13+: Advanced security features
```

---

## 12. Testing Old Devices

### Support Legacy Devices
```bash
# Test compatibility APK on API 21
adb shell getprop ro.build.version.sdk

# If < 24, need minSdk support
# Rebuild with: minSdk = 21

# Download legacy emulator
# API 19, 21, 22 images available
```

---

## 13. Version Upgrade Testing

### Test Upgrade Path
```bash
# Start on older Android
emulator -avd Android28 &

# Install app
adb install app.apk

# Verify functionality
adb shell am start -n com.example.app/.MainActivity

# Simulate upgrade
# (In real scenario, would use Android Upgrade)

# Verify data persists
adb shell getprop ro.data.large_disk
```


# Real-World ADB Workflows

## Workflow 1: Daily Development Cycle

### Morning Setup
```bash
#!/bin/bash
# morning_setup.sh

echo "🌅 Starting daily development..."

# Update ADB
adb kill-server
adb start-server

# Check connected devices
echo "Connected devices:"
adb devices

# Connect WiFi devices
adb connect 192.168.1.100:5555

# Check all devices again
echo "Final device list:"
adb devices -l
```

### Development Build & Deploy
```bash
# 1. Build
./gradlew assembleDebug

# 2. Install on primary device
adb install -r app/build/outputs/apk/debug/app-debug.apk

# 3. Launch app
adb shell am start -n com.example.app/.MainActivity

# 4. Watch logs
adb logcat | grep com.example.app
```

### Evening Cleanup
```bash
#!/bin/bash
# evening_cleanup.sh

echo "🌙 Cleaning up devices..."

# Clear caches
for device in $(adb devices | grep device | awk '{print $1}'); do
    adb -s "$device" shell pm clear com.example.app
done

# Disconnect WiFi devices
adb disconnect

# Stop server
adb kill-server

echo "Done! Have a nice evening 👋"
```

---

## Workflow 2: Bug Investigation

### Reproduce Bug
```bash
#!/bin/bash
# investigate_bug.sh

DEVICE=$1
BUG_ID=$2

mkdir -p "bugs/$BUG_ID"

echo "Investigating bug #$BUG_ID"

# Clear logs
adb -s "$DEVICE" logcat -c

# Get device info
adb -s "$DEVICE" shell getprop > "bugs/$BUG_ID/device_info.txt"

# Start recording logs
adb -s "$DEVICE" logcat -v threadtime > "bugs/$BUG_ID/logcat.txt" &
LOG_PID=$!

# Reproduce steps (automated or manual)
echo "Reproduce steps:"
echo "1. Open app"
echo "2. Navigate to bug scenario"
echo "3. Trigger the bug"
read -p "Press Enter when done..."

# Stop logging
kill $LOG_PID

# Collect additional data
adb -s "$DEVICE" pull /data/anr/ "bugs/$BUG_ID/anr/" 2>/dev/null || true
adb -s "$DEVICE" shell dumpsys meminfo > "bugs/$BUG_ID/meminfo.txt"
adb -s "$DEVICE" shell dumpsys battery >> "bugs/$BUG_ID/device_info.txt"

echo "✓ Bug data collected to bugs/$BUG_ID/"
```

---

## Workflow 3: Release Preparation

### Pre-Release Checklist
```bash
#!/bin/bash
# pre_release.sh

VERSION=$1

echo "Preparing release v$VERSION"

mkdir -p "releases/v$VERSION"

# Build release APK
echo "Building release APK..."
./gradlew assembleRelease

# Test on devices
echo "Testing on devices..."
DEVICES=$(adb devices | grep device | grep -v List | awk '{print $1}')

for device in $DEVICES; do
    echo "Testing on $device..."
    
    adb -s "$device" install -r build/outputs/apk/release/app-release.apk
    adb -s "$device" shell am start -n com.example.app/.SplashActivity
    
    sleep 2
    
    # Check for crashes
    adb -s "$device" logcat -c
    sleep 5
    
    CRASHES=$(adb -s "$device" logcat | grep -i "crash\|exception" | wc -l)
    
    if [ $CRASHES -eq 0 ]; then
        echo "✓ $device: OK"
    else
        echo "✗ $device: Found crashes"
    fi
done

# Generate report
cp build/outputs/apk/release/app-release.apk "releases/v$VERSION/"
echo "v$VERSION - $(date)" > "releases/v$VERSION/release_notes.txt"

echo "Release prepared!"
```

---

## Workflow 4: Performance Investigation

### Performance Analysis
```bash
#!/bin/bash
# analyze_performance.sh

APP=$1

mkdir -p "performance_reports"
REPORT="performance_reports/report_$(date +%Y%m%d_%H%M%S).txt"

{
    echo "=== Performance Analysis for $APP ==="
    echo "Date: $(date)"
    echo ""
    
    echo "=== Startup Performance ==="
    for i in {1..3}; do
        echo "Run $i:"
        adb shell am start -W -n $APP/.MainActivity 2>&1 | grep -E "This|Total"
    done
    
    echo ""
    echo "=== Memory Analysis ==="
    adb shell dumpsys meminfo $APP
    
    echo ""
    echo "=== CPU Usage ==="
    adb shell top -n 1 | grep $APP
    
    echo ""
    echo "=== Frame Rate ==="
    adb shell dumpsys gfxinfo $APP | grep "Frames"
    
} | tee "$REPORT"

echo "Report saved: $REPORT"
```

---

## Workflow 5: Beta Testing Campaign

### Deploy to Beta Testers
```bash
#!/bin/bash
# beta_deploy.sh

BETA_DEVICES_FILE="beta_devices.txt"
APK="app-beta.apk"

echo "Deploying beta build..."

while IFS= read -r device; do
    echo "Deploying to $device..."
    
    # Get device info
    MODEL=$(adb -s "$device" shell getprop ro.product.model)
    ANDROID=$(adb -s "$device" shell getprop ro.build.version.release)
    
    # Install APK
    adb -s "$device" install -r "$APK"
    
    # Send notification
    adb -s "$device" shell cmd package set-home-activity com.example.app/.MainActivity
    
    echo "✓ Deployed to $device ($MODEL - Android $ANDROID)"
    
done < "$BETA_DEVICES_FILE"

echo "Beta deployment complete!"
```

### Collect Beta Feedback
```bash
#!/bin/bash
# collect_feedback.sh

BETA_DEVICES_FILE="beta_devices.txt"
FEEDBACK_DIR="beta_feedback"

mkdir -p "$FEEDBACK_DIR"

while IFS= read -r device; do
    echo "Collecting from $device..."
    
    # Pull logs
    adb -s "$device" pull /data/data/com.example.app/logs/ \
        "$FEEDBACK_DIR/$device/" 2>/dev/null || true
    
    # Pull screenshots
    adb -s "$device" pull /sdcard/DCIM/Camera/ \
        "$FEEDBACK_DIR/$device/photos/" 2>/dev/null || true
    
    # Get crash reports
    adb -s "$device" pull /data/anr/ \
        "$FEEDBACK_DIR/$device/crashes/" 2>/dev/null || true
    
done < "$BETA_DEVICES_FILE"

echo "Feedback collected to $FEEDBACK_DIR"
```

---

## Workflow 6: Multi-Language Testing

### Test All Languages
```bash
#!/bin/bash
# test_languages.sh

DEVICE=$1
LANGUAGES=("en" "es" "fr" "de" "zh" "ja" "ar" "ko")

for LANG in "${LANGUAGES[@]}"; do
    echo "Testing $LANG..."
    
    # Set language
    adb -s "$DEVICE" shell setprop persist.sys.locale "$LANG"
    
    # Restart app
    adb -s "$DEVICE" shell am force-stop com.example.app
    adb -s "$DEVICE" shell am start -n com.example.app/.MainActivity
    
    # Wait for UI to load
    sleep 3
    
    # Screenshot
    adb -s "$DEVICE" shell screencap -p "/sdcard/screenshot_$LANG.png"
    adb pull "/sdcard/screenshot_$LANG.png" "./lang_screenshots/"
    
    echo "✓ $LANG tested and screenshotted"
done

# Reset to default
adb -s "$DEVICE" shell setprop persist.sys.locale "en_US"
```

---

## Workflow 7: Accessibility Testing

### Test Accessibility Features
```bash
#!/bin/bash
# test_accessibility.sh

DEVICE=$1

echo "Testing accessibility features..."

# Enable TalkBack
adb -s "$DEVICE" shell settings put secure enabled_accessibility_services \
    com.google.android.marktalkback/com.google.android.marktalkback.TalkBackService

# Enable high contrast
adb -s "$DEVICE" shell settings put secure high_text_contrast_enabled 1

# Increase font size
adb -s "$DEVICE" shell settings put system font_scale 1.3

# Test with screen reader
adb -s "$DEVICE" shell am start -n com.example.app/.MainActivity

# Record navigation
adb -s "$DEVICE" shell screenrecord /sdcard/accessibility_test.mp4 &
RECORD_PID=$!

echo "Test accessibility. Press Ctrl+C to stop."
wait

kill $RECORD_PID

# Pull video
adb pull /sdcard/accessibility_test.mp4 ./

# Disable features
adb -s "$DEVICE" shell settings put secure enabled_accessibility_services ""
adb -s "$DEVICE" shell settings put secure high_text_contrast_enabled 0
adb -s "$DEVICE" shell settings put system font_scale 1.0
```

---

## Workflow 8: Enterprise Deployment

### Deploy to Company Devices
```bash
#!/bin/bash
# enterprise_deploy.sh

DEVICE_LIST="company_devices.txt"
APP_APK="app-enterprise.apk"
CONFIG_FILE="config.json"

echo "Enterprise deployment starting..."

SUCCESS=0
FAILED=0

while IFS= read -r device; do
    echo "Deploying to $device..."
    
    if adb -s "$device" install -r "$APP_APK"; then
        # Push configuration
        adb -s "$device" push "$CONFIG_FILE" /sdcard/
        
        # Grant required permissions
        adb -s "$device" shell pm grant com.example.app android.permission.CAMERA
        adb -s "$device" shell pm grant com.example.app android.permission.RECORD_AUDIO
        
        SUCCESS=$((SUCCESS + 1))
        echo "✓ Deployed"
    else
        FAILED=$((FAILED + 1))
        echo "✗ Failed"
    fi
    
done < "$DEVICE_LIST"

echo ""
echo "Deployment Summary:"
echo "Success: $SUCCESS"
echo "Failed: $FAILED"
```

---

## Workflow 9: Security Audit

### Security Testing
```bash
#!/bin/bash
# security_audit.sh

APP="com.example.app"
DEVICE=$1

echo "Running security audit..."

mkdir -p "security_audit"

# Check app permissions
adb -s "$DEVICE" shell dumpsys package "$APP" | grep "permission" \
    > "security_audit/permissions.txt"

# Check for hardcoded secrets
adb -s "$DEVICE" pull /data/data/$APP/shared_prefs/ \
    "security_audit/prefs/" 2>/dev/null || true

# Check database security
adb -s "$DEVICE" shell "find /data/data/$APP -name '*.db'" \
    > "security_audit/databases.txt"

# Check file permissions
adb -s "$DEVICE" shell "ls -la /data/data/$APP/" \
    > "security_audit/file_permissions.txt"

# Check logcat for sensitive data
adb -s "$DEVICE" logcat -c
adb -s "$DEVICE" shell am start -n $APP/.MainActivity
sleep 5
adb -s "$DEVICE" logcat -d | grep -iE "password|token|secret|key" \
    > "security_audit/sensitive_logs.txt"

echo "Security audit complete: security_audit/"
```


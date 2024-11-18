# Complete Device Testing Guide

## 1. Multi-Device Testing Strategy

### Device Selection Matrix
```
┌─────────────────┬──────────────┬──────────────┬──────────────┐
│ Test Type       │ Phone        │ Tablet       │ Emulator     │
├─────────────────┼──────────────┼──────────────┼──────────────┤
│ Functional      │ Real Device  │ Real Device  │ Emulator     │
│ Performance     │ Real Device  │ Real Device  │ Real Device  │
│ UI/UX           │ Real Device  │ Real Device  │ Emulator     │
│ Compatibility   │ Multiple     │ Multiple     │ Multiple API │
│ Battery         │ Real Device  │ Real Device  │ N/A          │
└─────────────────┴──────────────┴──────────────┴──────────────┘
```

### Device Pool Recommendation
```
Minimum:
- 1 Low-end device (API 24)
- 1 Mid-range device (API 28)
- 1 High-end device (API 33)
- 1 Tablet (API 30)
- 2 Emulators (API 28, 33)

Comprehensive:
- Multiple manufacturers (Samsung, Google, Xiaomi, OnePlus)
- Multiple screen sizes (4.5", 5.5", 6.5", 7", 10")
- Multiple RAM configurations (2GB, 4GB, 8GB, 12GB)
- Different OS versions (Android 7-13)
```

---

## 2. Automated Device Testing Framework

### Test Runner Script
```bash
#!/bin/bash
# run_device_tests.sh

DEVICES=$(adb devices | grep device | grep -v "List of attached" | awk '{print $1}')
TEST_APK="app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk"
TARGET_APK="app/build/outputs/apk/debug/app-debug.apk"

RESULTS_DIR="test_results"
mkdir -p "$RESULTS_DIR"

for DEVICE in $DEVICES; do
    echo "==== Testing on $DEVICE ===="
    
    # Get device info
    MODEL=$(adb -s "$DEVICE" shell getprop ro.product.model)
    ANDROID=$(adb -s "$DEVICE" shell getprop ro.build.version.release)
    echo "Device: $MODEL (Android $ANDROID)"
    
    # Clear previous data
    adb -s "$DEVICE" shell pm clear com.example.app 2>/dev/null || true
    
    # Install apps
    adb -s "$DEVICE" install -r "$TARGET_APK"
    adb -s "$DEVICE" install -r "$TEST_APK"
    
    # Run tests
    adb -s "$DEVICE" shell am instrument -w \
        -e debug false \
        com.example.app.test/androidx.test.runner.AndroidJUnitRunner \
        > "$RESULTS_DIR/results_$DEVICE.txt" 2>&1
    
    # Pull results
    adb -s "$DEVICE" pull /data/data/com.example.app/test_results/ \
        "$RESULTS_DIR/$DEVICE/" 2>/dev/null || true
    
    echo "✓ Tests completed on $DEVICE"
done

echo "All tests completed! Results in $RESULTS_DIR"
```

---

## 3. Compatibility Testing

### API Level Testing Matrix
```bash
#!/bin/bash
# test_all_apis.sh

# Define API levels to test
declare -a APIS=("24" "26" "28" "30" "32" "33")

for API in "${APIS[@]}"; do
    echo "Testing on API $API"
    
    # Create or use existing emulator
    emulator_name="api_$API"
    
    # Start emulator (if not running)
    pgrep -f "emulator.*$emulator_name" > /dev/null
    if [ $? -ne 0 ]; then
        emulator -avd "$emulator_name" -no-window &
        sleep 30  # Wait for boot
    fi
    
    # Get emulator serial
    DEVICE=$(adb devices | grep "$emulator_name" | awk '{print $1}')
    
    # Run tests
    adb -s "$DEVICE" install -r app.apk
    adb -s "$DEVICE" shell am instrument -w com.example.app.test/.TestRunner
done
```

---

## 4. Screen Size & Orientation Testing

### Multi-Screen Testing
```bash
#!/bin/bash
# test_screen_sizes.sh

DEVICE=$1

# Configurations
declare -A SCREENS=(
    ["small"]="360x640"
    ["normal"]="400x800"
    ["large"]="480x854"
    ["xlarge"]="720x1280"
    ["xxlarge"]="1080x1920"
)

for size in "${!SCREENS[@]}"; do
    RESOLUTION="${SCREENS[$size]}"
    
    echo "Testing at $size ($RESOLUTION)"
    
    # Set display resolution
    adb -s "$DEVICE" shell wm size $RESOLUTION
    
    # Take screenshot for verification
    adb -s "$DEVICE" shell screencap -p "/sdcard/screenshot_$size.png"
    adb pull "/sdcard/screenshot_$size.png" "./screenshots/"
    
    # Run UI tests
    adb -s "$DEVICE" shell am instrument -w com.example.app.test/.UITestRunner
done

# Reset to default
adb -s "$DEVICE" shell wm size reset
```

---

## 5. Orientation Testing

### Landscape & Portrait Testing
```bash
#!/bin/bash
# test_orientations.sh

DEVICE=$1

# Test both orientations
for ORIENTATION in 0 1; do
    if [ $ORIENTATION -eq 0 ]; then
        echo "Testing PORTRAIT mode"
        MODE="portrait"
    else
        echo "Testing LANDSCAPE mode"
        MODE="landscape"
    fi
    
    # Set orientation
    adb -s "$DEVICE" shell settings put system user_rotation $ORIENTATION
    
    # Run tests
    adb -s "$DEVICE" shell am instrument -w \
        -e "orientation=$MODE" \
        com.example.app.test/.TestRunner
    
    # Capture screenshot
    adb shell screencap -p "/sdcard/screenshot_$MODE.png"
done
```

---

## 6. Language & Locale Testing

### Multi-Language Testing
```bash
#!/bin/bash
# test_locales.sh

DEVICE=$1

# Languages to test
declare -a LOCALES=("en_US" "es_ES" "fr_FR" "de_DE" "zh_CN" "ja_JP" "ar_SA")

for LOCALE in "${LOCALES[@]}"; do
    echo "Testing locale: $LOCALE"
    
    # Set locale
    adb -s "$DEVICE" shell am broadcast -a com.android.intent.action.DEVICE_LOCALE \
        -e "locale=$LOCALE"
    
    # Alternative: Set via settings
    adb -s "$DEVICE" shell setprop persist.sys.locale "${LOCALE%_*}"
    
    # Restart app
    adb -s "$DEVICE" shell am force-stop com.example.app
    adb -s "$DEVICE" shell am start -n com.example.app/.MainActivity
    
    # Run tests
    adb -s "$DEVICE" shell am instrument -w \
        -e "locale=$LOCALE" \
        com.example.app.test/.TestRunner
    
    # Take screenshot
    adb shell screencap -p "/sdcard/screenshot_$LOCALE.png"
done
```

---

## 7. Permission Testing

### Permission Scenario Testing
```bash
#!/bin/bash
# test_permissions.sh

DEVICE=$1
APP="com.example.app"

declare -a PERMISSIONS=(
    "android.permission.CAMERA"
    "android.permission.ACCESS_FINE_LOCATION"
    "android.permission.READ_CONTACTS"
    "android.permission.RECORD_AUDIO"
)

# Test with permissions granted
echo "Testing WITH permissions..."
for PERM in "${PERMISSIONS[@]}"; do
    adb -s "$DEVICE" shell pm grant "$APP" "$PERM"
done
adb -s "$DEVICE" shell am instrument -w com.example.app.test/.TestRunner

# Test with permissions revoked
echo "Testing WITHOUT permissions..."
for PERM in "${PERMISSIONS[@]}"; do
    adb -s "$DEVICE" shell pm revoke "$APP" "$PERM"
done
adb -s "$DEVICE" shell am instrument -w com.example.app.test/.TestRunner
```

---

## 8. Network Condition Testing

### Network Simulation
```bash
#!/bin/bash
# test_network_conditions.sh

DEVICE=$1

# Different network profiles
declare -A NETWORKS=(
    ["wifi"]="none"
    ["4g"]="4g"
    ["3g"]="3g"
    ["2g"]="edge"
    ["offline"]="none"
)

for profile in "${!NETWORKS[@]}"; do
    echo "Testing $profile network"
    
    case "$profile" in
        "offline")
            adb -s "$DEVICE" shell cmd connectivity airplane-mode enable
            ;;
        *)
            adb -s "$DEVICE" shell cmd connectivity airplane-mode disable
            # Use Android 11+ throttle API
            adb -s "$DEVICE" shell cmd net_policy set restrict-background true
            ;;
    esac
    
    # Run network tests
    adb -s "$DEVICE" shell am instrument -w \
        -e "network=$profile" \
        com.example.app.test/.NetworkTestRunner
    
    # Reset
    adb -s "$DEVICE" shell cmd connectivity airplane-mode disable
done
```

---

## 9. RAM & Storage Testing

### Low-Memory Scenario
```bash
#!/bin/bash
# test_low_memory.sh

DEVICE=$1

echo "Testing LOW MEMORY scenarios"

# Fill device storage
adb shell "dd if=/dev/zero of=/sdcard/filler bs=1M count=1000"

# Monitor memory
echo "Available memory:"
adb shell "free -h"

# Run tests
adb shell am instrument -w com.example.app.test/.StressTestRunner

# Clear
adb shell "rm /sdcard/filler"
```

---

## 10. Battery & Temperature Testing

### Battery Drain Testing
```bash
#!/bin/bash
# test_battery.sh

DEVICE=$1

echo "Starting battery drain test"
echo "Initial battery level:"
adb -s "$DEVICE" shell dumpsys battery | grep level

# Keep screen on
adb -s "$DEVICE" shell "settings put system screen_off_timeout 2147483647"

# Run intensive operations
for i in {1..60}; do
    echo "Minute $i - Battery:"
    adb -s "$DEVICE" shell dumpsys battery | grep level
    sleep 60
done

# Reset
adb -s "$DEVICE" shell "settings put system screen_off_timeout 300000"
```

---

## 11. Stress Testing

### Long-Duration Test
```bash
#!/bin/bash
# stress_test.sh

DEVICE=$1
DURATION=3600  # 1 hour

echo "Starting stress test for $DURATION seconds"
START_TIME=$(date +%s)

while true; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    
    if [ $ELAPSED -gt $DURATION ]; then
        echo "Stress test completed!"
        break
    fi
    
    # Continuous interactions
    adb -s "$DEVICE" shell input tap 500 500
    adb -s "$DEVICE" shell input swipe 100 500 900 500
    adb -s "$DEVICE" shell input keyevent 4
    
    # Memory check every 5 minutes
    if [ $((ELAPSED % 300)) -eq 0 ]; then
        echo "Memory at $ELAPSED seconds:"
        adb -s "$DEVICE" shell dumpsys meminfo com.example.app | grep TOTAL
    fi
done
```

---

## 12. Device-Specific Edge Cases

### Samsung Galaxy Specific
```bash
# Samsung-specific tests
adb shell getprop ro.product.brand | grep -i samsung

# Test Samsung Knox
adb shell settings get secure knox_seprw_is_ready

# Test Samsung features
adb shell am start -a android.intent.action.MAIN \
    -n com.sec.android.app.home/.AppsTabActivity
```

### Google Pixel Specific
```bash
# Pixel-specific tests
adb shell getprop ro.product.model | grep -i pixel

# Test Pixel features
adb shell settings get secure display_smoothness_enabled

# Test Magic Eraser (if supported)
adb shell cmd media.camera test-pixel-features
```

---

## 13. Test Reporting

### Generate Test Report
```bash
#!/bin/bash
# generate_report.sh

cat > test_report.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Device Test Report</title>
    <style>
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>Device Test Report</h1>
    <table>
        <tr>
            <th>Device</th>
            <th>Model</th>
            <th>Android</th>
            <th>Tests Passed</th>
            <th>Tests Failed</th>
            <th>Status</th>
        </tr>
EOF

for result_file in test_results/*.txt; do
    DEVICE=$(basename "$result_file" .txt)
    # Parse results and add to table
    echo "<tr><td>$DEVICE</td>...</tr>" >> test_report.html
done

echo "</table></body></html>" >> test_report.html
```

---

## 14. Common Testing Patterns

### Before Each Test
```bash
# Clear app data
adb shell pm clear com.example.app

# Clear cache
adb shell rm -rf /data/data/com.example.app/cache

# Reset settings
adb shell settings reset system

# Grant all permissions
adb shell pm grant-all-permissions com.example.app
```

### After Each Test
```bash
# Collect logs
adb logcat -d > "logs_$DEVICE.txt"

# Pull crash data
adb pull /data/anr/ ./crashes/

# Clear device
adb shell pm clear com.example.app

# Restart device
adb reboot
```


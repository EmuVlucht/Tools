# Comprehensive Testing Strategies with ADB

## 1. Unit Testing

### Run Unit Tests
```bash
# Build and run unit tests
./gradlew test

# Run tests on device
./gradlew connectedAndroidTest

# Specific test
./gradlew test com.example.AppTest
```

### Using Espresso
```bash
# Build test APK
./gradlew assembleDebugAndroidTest

# Run on device
adb shell am instrument -w \
    com.example.test/androidx.test.runner.AndroidJUnitRunner
```

---

## 2. Integration Testing

### Multi-Activity Tests
```bash
adb shell am start -n com.example.app/.ActivityA
sleep 2
adb shell am start -n com.example.app/.ActivityB
sleep 2
adb shell am start -n com.example.app/.ActivityC

# Verify all work
adb shell dumpsys activity | grep "ActivityRecord"
```

---

## 3. UI Testing

### Screenshot-Based Testing
```bash
#!/bin/bash
# ui_test.sh

for i in {1..10}; do
    # Perform action
    adb shell input tap 500 500
    
    # Take screenshot
    adb shell screencap -p "/sdcard/screen_$i.png"
    
    # Save locally
    adb pull "/sdcard/screen_$i.png" "./ui_screenshots/"
    
    sleep 1
done
```

---

## 4. Performance Testing

### Startup Performance
```bash
# Cold start
for i in {1..5}; do
    adb shell am start -W -n com.example.app/.MainActivity
done

# Warm start
for i in {1..5}; do
    adb shell input keyevent 4  # Back
    sleep 1
    adb shell am start -W -n com.example.app/.MainActivity
done
```

---

## 5. Memory Testing

### Memory Profiling
```bash
# Start recording
adb shell am profile start

# Run actions
adb shell am start -n com.example.app/.MainActivity
sleep 30

# Stop recording
adb shell am profile stop --output-dir /sdcard/

# Pull results
adb pull /sdcard/profile-results.txt ./
```

---

## 6. Battery Testing

### Battery Drain Simulation
```bash
#!/bin/bash
# battery_test.sh

# Monitor battery
for i in {1..100}; do
    BATTERY=$(adb shell dumpsys battery | grep "level")
    echo "$(date): $BATTERY"
    sleep 60
done
```

---

## 7. Network Testing

### Network Condition Simulation
```bash
# Slow network
adb shell tc qdisc add dev eth0 root netem \
    delay 500ms rate 1mbit

# Run app
adb shell am start -n com.example.app/.MainActivity

# Monitor behavior
adb logcat | grep -i "timeout\|error"

# Reset network
adb shell tc qdisc del dev eth0 root
```

---

## 8. Security Testing

### Permission Testing
```bash
# Revoke permissions
adb shell pm revoke com.example.app android.permission.CAMERA

# Verify app behavior
adb shell am start -n com.example.app/.MainActivity

# Check logs for errors
adb logcat | grep "SecurityException"

# Grant permission back
adb shell pm grant com.example.app android.permission.CAMERA
```

---

## 9. Localization Testing

### Test All Languages
```bash
LANGUAGES=("en" "es" "fr" "de" "zh" "ja" "ar" "ko")

for lang in "${LANGUAGES[@]}"; do
    echo "Testing $lang..."
    adb shell setprop persist.sys.locale "${lang:0:2}"
    adb shell am start -n com.example.app/.MainActivity
    sleep 3
    adb shell screencap "/sdcard/lang_${lang}.png"
done
```

---

## 10. Crash Testing

### Trigger Common Crashes
```bash
# Null pointer
adb shell am start -n com.example.app/.MainActivity
sleep 1
adb shell input tap 500 500  # Tap null object

# Memory pressure
adb shell am send-trim-memory com.example.app RUNNING_CRITICAL

# Force stop recovery
adb shell kill -9 $(adb shell pidof com.example.app)

# Verify recovery behavior
adb logcat | grep "FATAL\|crash"
```

---

## 11. Automated Test Suite

```bash
#!/bin/bash
# automated_test_suite.sh

APP="com.example.app"
DEVICE=${1:-emulator-5554}

echo "=== Running Automated Test Suite ==="

# 1. Installation test
echo "[1/5] Installation test..."
adb -s "$DEVICE" install -r app.apk
if [ $? -eq 0 ]; then echo "✓ Pass"; else echo "✗ Fail"; fi

# 2. Functionality test
echo "[2/5] Functionality test..."
adb -s "$DEVICE" shell am start -n "$APP/.MainActivity"
sleep 3
ACTIVITIES=$(adb -s "$DEVICE" dumpsys activity | grep "ActivityRecord" | wc -l)
if [ $ACTIVITIES -gt 0 ]; then echo "✓ Pass"; else echo "✗ Fail"; fi

# 3. Crash test
echo "[3/5] Crash test..."
CRASHES=$(adb -s "$DEVICE" logcat | grep -i "crash" | wc -l)
if [ $CRASHES -eq 0 ]; then echo "✓ Pass"; else echo "✗ Fail"; fi

# 4. Performance test
echo "[4/5] Performance test..."
TIME=$(adb -s "$DEVICE" shell am start -W "$APP/.MainActivity" | grep TotalTime | awk '{print $NF}')
if [ $TIME -lt 5000 ]; then echo "✓ Pass ($TIME ms)"; else echo "✗ Fail ($TIME ms)"; fi

# 5. Uninstall test
echo "[5/5] Uninstall test..."
adb -s "$DEVICE" uninstall "$APP"
if [ $? -eq 0 ]; then echo "✓ Pass"; else echo "✗ Fail"; fi

echo "=== Test Suite Complete ==="
```

---

## 12. Continuous Integration Testing

### GitHub Actions
```yaml
name: Test APK

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build APK
        run: ./gradlew assembleDebug
      
      - name: Run tests
        run: ./gradlew connectedAndroidTest
```

---

## 13. Device Test Matrix

```bash
#!/bin/bash
# test_matrix.sh

DEVICES=$(adb devices | grep device | grep -v List | awk '{print $1}')

for device in $DEVICES; do
    echo "Testing on $device..."
    
    MODEL=$(adb -s "$device" shell getprop ro.product.model)
    ANDROID=$(adb -s "$device" shell getprop ro.build.version.release)
    
    # Install and test
    adb -s "$device" install app.apk
    adb -s "$device" shell am start -n com.example.app/.MainActivity
    
    # Check for crashes
    adb -s "$device" logcat -c
    sleep 5
    CRASHES=$(adb -s "$device" logcat | grep -i crash | wc -l)
    
    if [ $CRASHES -eq 0 ]; then
        echo "✓ PASS: $MODEL (Android $ANDROID)"
    else
        echo "✗ FAIL: $MODEL (Android $ANDROID) - $CRASHES crashes"
    fi
done
```

---

## 14. Regression Testing

### Detect Regressions
```bash
# Create baseline
adb install baseline_app.apk
adb shell screencap /sdcard/baseline.png
adb pull /sdcard/baseline.png

# Test new version
adb install new_app.apk
adb shell screencap /sdcard/current.png
adb pull /sdcard/current.png

# Compare
compare baseline.png current.png diff.png
DIFF_PIXELS=$(convert diff.png -print "%[fx:mean*100]" /dev/null)

if [ "$DIFF_PIXELS" -gt 5 ]; then
    echo "⚠️ Regression detected: $DIFF_PIXELS% different"
else
    echo "✓ No regression"
fi
```


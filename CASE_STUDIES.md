# Real-World Case Studies & Scenarios

## Case Study 1: Fixing Critical Memory Leak in Production

### Problem
- App crashes after 2 hours of usage
- Memory grows continuously
- Affects 10% of users

### Investigation Steps
```bash
# 1. Capture memory over time
for i in {1..20}; do
    echo "$(date +%H:%M:%S): $(adb shell dumpsys meminfo com.example.app | grep TOTAL)"
    sleep 60
done > memory_log.txt

# 2. Analyze growth pattern
grep TOTAL memory_log.txt | awk '{print $2}' | \
    awk '{if(NR>1) print $0-prev; prev=$0}'

# 3. Get heap dump
adb shell dumpsys meminfo com.example.app --unreachable

# 4. Find retained objects
adb pull /data/data/com.example.app/hprof/ ./

# 5. Identify leak source
# Found: Activity not being garbage collected after back press
# Cause: Static reference to Activity in helper class
```

### Solution
```kotlin
// BEFORE (Leak)
object HeapHelper {
    var activity: Activity? = null  // Static reference!
}

// AFTER (Fixed)
class HeapHelper {
    private val activity: WeakReference<Activity>? = null
}
```

### Result
- Memory leak eliminated
- 0% crash rate after fix
- 98% of affected users updated

---

## Case Study 2: Reducing APK Size from 150MB to 45MB

### Analysis
```bash
# Analyze APK
adb shell pm dump com.example.app | grep Size

# 150MB breakdown:
# - Native libraries: 60MB
# - Assets: 50MB
# - Resources: 30MB
# - Classes: 10MB
```

### Optimization Steps
```bash
# 1. Enable minification
# build.gradle: minifyEnabled true

# 2. Remove unused resources
./gradlew lint

# 3. Use WebP for images
# Convert PNGs to WebP

# 4. Bundle instead of monolithic
# App Bundles instead of universal APK

# 5. Enable compression
# zipalign -v 4 app.apk
```

### Result
- APK: 45MB (-70%)
- Install time: 5min → 1min
- Storage savings: 100GB across all users

---

## Case Study 3: 100ms Startup Time Reduction

### Profiling
```bash
# Measure startup
for i in {1..5}; do
    adb shell am start -W -n com.example.app/.MainActivity 2>&1 | grep TotalTime
done

# Average: 2500ms → Target: 1500ms
```

### Findings
- Splash screen: 500ms
- Database init: 800ms
- Network call: 700ms (can't reduce)

### Optimizations
```kotlin
// 1. Move DB to background
lifecycleScope.launchWhenStarted {
    db.initialize()
}

// 2. Lazy load features
val featureManager by lazy { FeatureManager() }

// 3. Parallelize tasks
GlobalScope.async { loadFeature1() }
GlobalScope.async { loadFeature2() }
```

### Result
- Startup: 2500ms → 1400ms (-44%)
- User engagement: +12%
- Crash rate: -8%

---

## Case Study 4: Battery Drain Investigation

### Symptoms
- Battery drain 30% per hour
- Normal is 5% per hour

### Investigation
```bash
# Check wakelocks
adb shell dumpsys power | grep "Wakelock"

# Result: GPS location update every 5 seconds
```

### Root Cause
```kotlin
// WRONG - Called every 5 seconds
locationManager.requestLocationUpdates(
    LocationManager.GPS_PROVIDER,
    5000,  // 5 seconds - TOO FREQUENT!
    0f,
    listener
)
```

### Solution
```kotlin
// RIGHT - Balanced frequency
locationManager.requestLocationUpdates(
    LocationManager.GPS_PROVIDER,
    60000,  // 1 minute
    100f,   // 100 meter accuracy
    listener
)

// BETTER - Conditional logic
if (isScreenOn && appInForeground) {
    requestHighAccuracy()
} else {
    requestLowPowerUpdates()
}
```

### Result
- Battery drain: 30% → 8% per hour
- User satisfaction: +35%

---

## Case Study 5: Multidevice Testing Challenge

### Problem
- App works on Pixel 5
- Crashes on Redmi Note 10
- Inconsistent on Samsung Galaxy

### Solution: Device Testing Matrix
```bash
#!/bin/bash
# Test 10 devices systematically

DEVICES=(
    "Pixel 5|emulator-5554"
    "Samsung Galaxy S20|192.168.1.100:5555"
    "Redmi Note 10|192.168.1.101:5555"
    # ... 7 more devices
)

for device_info in "${DEVICES[@]}"; do
    IFS='|' read -r name id <<< "$device_info"
    
    echo "Testing on $name"
    adb -s "$id" install -r app.apk
    adb -s "$id" shell am instrument -w com.example.test/.TestRunner
done
```

### Findings
- Redmi: RecyclerView rendering issue with 2GB RAM
- Samsung: Permission dialog handling bug
- Pixel: Works fine (as expected)

### Fixes
- Implement memory-efficient RecyclerView
- Handle permission dialogs properly
- Test on low-RAM devices

---

## Case Study 6: Network Issue in Poor Connectivity

### Problem
- App works fine on WiFi
- Fails on 3G networks
- Timeout errors in logs

### Testing
```bash
# Simulate poor network
adb shell tc qdisc add dev eth0 root netem \
    delay 500ms \
    loss 5% \
    rate 1mbit

# Run app and observe
adb shell am start -n com.example.app/.MainActivity

# Collect logs
adb logcat | grep -i "timeout\|connection"
```

### Issues Found
- 10 second timeout is too short
- No retry logic
- Blocking main thread

### Fixes
```kotlin
// Increase timeout
val client = OkHttpClient.Builder()
    .connectTimeout(30, TimeUnit.SECONDS)
    .readTimeout(30, TimeUnit.SECONDS)
    .build()

// Add retry logic
var retries = 0
while (retries < 3) {
    try {
        makeRequest()
        break
    } catch (e: IOException) {
        retries++
        delay(1000 * retries)  // Exponential backoff
    }
}

// Move to background
viewModel.loadData()
```

---

## Case Study 7: Permission-Related Crashes

### Problem
- 2% of users report crashes
- All on Android 6.0 devices

### Root Cause
```bash
# Check what's happening
adb logcat | grep -i "permission\|denied"

# Found: App requesting CAMERA without runtime permission
```

### Issue
```kotlin
// WRONG - No runtime permission check
camera.open()

// RIGHT - Check permission first
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
    if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
        != PackageManager.PERMISSION_GRANTED) {
        requestPermissions(arrayOf(Manifest.permission.CAMERA), CAMERA_REQUEST)
    } else {
        camera.open()
    }
} else {
    camera.open()
}
```

---

## Case Study 8: Localization Bug

### Problem
- App crashes in Arabic and Hebrew (RTL languages)

### Investigation
```bash
# Test Arabic
adb shell setprop persist.sys.locale ar_SA
adb shell am start -n com.example.app/.MainActivity

# Crash immediately!
```

### Root Cause
```kotlin
// WRONG - Hardcoded layout directions
view.layoutParams.leftMargin = 16dp

// RIGHT - Use margins that respect RTL
view.layoutParams.marginStart = 16dp
view.layoutParams.marginEnd = 16dp
```

### Solution
- Use `start/end` instead of `left/right`
- Add `android:supportsRtl="true"` to manifest
- Test with RTL layouts

---

## Case Study 9: Database Corruption Recovery

### Problem
- Users see "database locked" errors
- Can't restart app

### Investigation
```bash
# Check database
adb shell sqlite3 /data/data/com.example.app/db.db \
    "PRAGMA integrity_check;"

# Result: corruption detected
```

### Solution
```kotlin
// Add recovery mechanism
try {
    openDatabase()
} catch (e: SQLiteDatabaseLockedException) {
    // Attempt recovery
    database.close()
    val dbFile = File(dbPath)
    dbFile.delete()  // Delete corrupted DB
    createFreshDatabase()
}
```

---

## Case Study 10: Enterprise Deployment

### Challenge
- Deploy to 500+ devices
- 20 different phone models
- Manual installation not feasible

### Solution
```bash
#!/bin/bash
# enterprise_mass_deploy.sh

DEVICE_LIST="devices.csv"
APK="app-enterprise-v2.0.apk"

while IFS=',' read -r device_id model; do
    echo "[$SECONDS] Deploying to $device_id ($model)..."
    
    if adb -s "$device_id" install -r "$APK" 2>/dev/null; then
        echo "✓ $device_id"
        echo "$(date),$device_id,$model,SUCCESS" >> deployment.log
    else
        echo "✗ $device_id"
        echo "$(date),$device_id,$model,FAILED" >> deployment.log
    fi
    
done < "$DEVICE_LIST"

# Summary
TOTAL=$(wc -l < "$DEVICE_LIST")
SUCCESS=$(grep SUCCESS deployment.log | wc -l)
FAILED=$((TOTAL - SUCCESS))

echo ""
echo "Deployment Summary:"
echo "Total: $TOTAL"
echo "Success: $SUCCESS ($(( SUCCESS * 100 / TOTAL ))%)"
echo "Failed: $FAILED"
```

### Results
- 487/500 deployed successfully (97.4%)
- 13 devices had network issues (retried)
- Total time: 2 hours
- 100% within 24 hours

---

## Key Learnings

1. **Always profile before optimizing**
2. **Test on real devices, not just emulators**
3. **Monitor production crashes with priority**
4. **Memory leaks compound over time**
5. **Poor network handling affects 20% of users**
6. **Runtime permissions are critical on Android 6.0+**
7. **Localization affects 40% of downloads globally**
8. **Database corruption requires recovery mechanism**
9. **Batch operations for enterprise deployment**
10. **Invest in continuous testing infrastructure**


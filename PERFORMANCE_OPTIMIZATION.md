# Performance Optimization Guide Using ADB

## 1. Measuring Performance

### CPU Performance
```bash
# Real-time CPU usage
adb shell top -n 1

# Detailed CPU info
adb shell cat /proc/cpuinfo

# CPU frequency
adb shell cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_cur_freq

# Monitor specific app
adb shell top -p $(adb shell pidof com.example.app)
```

### Memory Performance
```bash
# Total memory
adb shell cat /proc/meminfo

# App memory breakdown
adb shell dumpsys meminfo com.example.app

# Memory over time (monitoring)
while true; do
    echo "$(date): $(adb shell dumpsys meminfo com.example.app | grep TOTAL)"
    sleep 5
done

# PSS (Proportional Set Size) memory
adb shell dumpsys meminfo | grep "Pss"
```

### Frame Rate & Jank
```bash
# Monitor frame drops
adb shell dumpsys SurfaceFlinger | grep -i "dropped\|jank"

# Profile rendering
adb shell cmd monitoring profile start
adb shell cmd monitoring profile stop --output-dir /sdcard/

# GPU profiling
adb shell cmd gpu profile
```

---

## 2. Identifying Performance Bottlenecks

### Method Tracing
```bash
# Start tracing
adb shell am trace-ipc start

# Do operations on app

# Stop and analyze
adb shell am trace-ipc stop
adb pull /data/anr/method_trace.bin ./

# Analyze with Perfetto
# Open in Android Studio Profiler
```

### Systrace
```bash
# Capture systrace
python3 $ANDROID_HOME/platform-tools/systrace/systrace.py \
    --out=trace.html \
    -t 10 \
    gfx input view wm am

# View in browser
# Open trace.html
```

### ANR Traces
```bash
# Find ANR files
adb shell ls /data/anr/

# Pull trace
adb pull /data/anr/traces.txt ./

# Search for blocking operations
grep "waiting on" traces.txt
```

---

## 3. Battery Optimization

### Monitor Battery Usage
```bash
# Current battery stats
adb shell dumpsys battery

# Detailed stats
adb shell dumpsys batterystats com.example.app

# Wakelock analysis
adb shell dumpsys power | grep "Wakelock"

# Partial wakelock
adb shell "cat /proc/wakelocks"

# CPU wakelock
adb shell dumpsys cpuinfo
```

### Reduce Battery Drain
```bash
# Disable location when not needed
adb shell settings put secure location_mode 0

# Disable Bluetooth
adb shell settings put global bluetooth_on 0

# Reduce sync frequency
adb shell settings put global sync_interval 3600000

# Disable WiFi scanning
adb shell settings put global wifi_scan_always_enabled 0

# Reduce screen brightness
adb shell settings put system screen_brightness 100
```

---

## 4. Network Optimization

### Monitor Network Usage
```bash
# Network stats
adb shell dumpsys netstats

# App network usage
adb shell cat /proc/net/dev

# Connection status
adb shell dumpsys connectivity

# DNS lookups
adb shell cat /etc/hosts

# Bandwidth usage
adb shell netstat -s
```

### Optimize Network
```bash
# Enable WiFi only mode
adb shell settings put global mobile_data_enabled 0

# Disable background data
adb shell settings put global background_restrict_mode 1

# Reduce sync
adb shell settings put global background_restrict_enabled 1

# Connection pooling (in code)
# Use HTTP/2 keep-alive
# Batch requests
# Compress data
```

---

## 5. Storage Optimization

### Check Storage
```bash
# Total disk space
adb shell df -h

# App cache size
adb shell du -sh /data/data/com.example.app/cache

# Total cache
adb shell du -sh /data/cache

# Storage by app
adb shell du -sh /data/data/*
```

### Cleanup
```bash
# Clear app cache
adb shell pm clear --cache com.example.app

# Remove old files
adb shell find /sdcard -type f -mtime +30 -delete

# Defragmentation
adb shell fstrim /data
```

---

## 6. Database Optimization

### Analyze Database
```bash
# Find database
adb shell find /data/data/com.example.app -name "*.db"

# Query database
adb shell sqlite3 /data/data/com.example.app/db.db ".schema"

# Check fragmentation
adb shell sqlite3 /data/data/com.example.app/db.db "PRAGMA freelist_count;"

# Get page count
adb shell sqlite3 /data/data/com.example.app/db.db "PRAGMA page_count;"
```

### Optimize Database
```bash
# Vacuum database (defragment)
adb shell sqlite3 /data/data/com.example.app/db.db "VACUUM;"

# Analyze database
adb shell sqlite3 /data/data/com.example.app/db.db "ANALYZE;"

# Create indexes
adb shell sqlite3 /data/data/com.example.app/db.db \
    "CREATE INDEX idx_column ON table(column);"

# Check query plan
adb shell sqlite3 /data/data/com.example.app/db.db \
    "EXPLAIN QUERY PLAN SELECT * FROM table WHERE id = 1;"
```

---

## 7. App Startup Optimization

### Measure Startup Time
```bash
# Cold start
adb shell am start -W -n com.example.app/.MainActivity

# Output shows:
# ThisTime: Time for this activity
# TotalTime: Total startup time

# Warm start
adb shell input keyevent 4  # Press back
sleep 1
adb shell am start -W -n com.example.app/.MainActivity

# Hot start
adb shell am start -W -n com.example.app/.MainActivity
```

### Optimize Startup
```bash
# Lazy loading pattern
# Defer non-essential initialization

# App Startup Library (Jetpack)
# Use InitializationProvider

# Profile startup
adb shell am profile start

adb shell am start -n com.example.app/.MainActivity

adb shell am profile stop --output-dir /sdcard/

adb pull /sdcard/profile-results.txt ./
```

---

## 8. Memory Leak Detection

### Monitor Memory Growth
```bash
#!/bin/bash
# memory_leak_detector.sh

APP=$1
MAX_ITERATIONS=20

echo "Time,MemoryKB" > memory_log.csv

for i in $(seq 1 $MAX_ITERATIONS); do
    TIME=$(date +%H:%M:%S)
    MEM=$(adb shell dumpsys meminfo $APP | grep TOTAL | awk '{print $2}')
    echo "$TIME,$MEM" >> memory_log.csv
    
    # Trigger actions that might leak
    adb shell input tap 500 500
    sleep 5
done

# Analyze growth
python3 << 'PYTHON'
import csv

prev_mem = 0
growth = 0

with open('memory_log.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        curr_mem = int(row['MemoryKB'])
        if curr_mem > prev_mem:
            growth += (curr_mem - prev_mem)
        prev_mem = curr_mem

if growth > 100000:  # > 100MB
    print("⚠️ Potential memory leak detected!")
else:
    print("✓ No significant memory leak")
PYTHON
```

---

## 9. Rendering Performance

### Monitor GPU Usage
```bash
# GPU profiling
adb shell cmd gpu profile

# Hardware rendering info
adb shell dumpsys gfxinfo com.example.app

# Frame timing
adb shell dumpsys gfxinfo com.example.app framestats

# Analyze slowness
adb shell dumpsys gfxinfo com.example.app | grep -E "Frames|missed"
```

### Optimize Rendering
```bash
# Reduce overdraw
adb shell setprop debug.hwui.overdraw show_overdraw

# Show GPU usage
adb shell setprop debug.hwui.debug_mode true

# Profile rendering
adb shell setprop debug.hwui.profile DRAW_TIME

# Disable for optimization
adb shell setprop debug.hwui.overdraw off
```

---

## 10. Compile Optimization

### Runtime/JIT Compilation
```bash
# Force JIT compilation
adb shell cmd package compile --mode=speed com.example.app

# Compile all apps
adb shell cmd package bg-dexopt-step

# Verify compiled
adb shell dumpsys package dexopt com.example.app

# AOT (Ahead-of-Time) compilation
adb shell cmd package compile --mode=speed-profile com.example.app
```

---

## 11. System-Level Optimization

### Enable Developer Options
```bash
# Disable animations
adb shell settings put global window_animation_scale 0
adb shell settings put global transition_animation_scale 0
adb shell settings put global animator_duration_scale 0

# Enable all cores
adb shell settings put global nfiq_enabled 1

# Increase Java heap
# Requires system modification (not recommended)
```

### Performance Profile
```bash
# Check current profile
adb shell getprop ro.build.type

# Set performance mode
adb shell settings put global powersaver_mode 0

# Check power saving
adb shell settings get global power_manager_level
```

---

## 12. Automated Performance Testing

### Performance Test Script
```bash
#!/bin/bash
# performance_benchmark.sh

APP=$1
ITERATIONS=5

echo "Running performance benchmark..."

{
    echo "Startup Time:"
    for i in $(seq 1 $ITERATIONS); do
        adb shell am start -W -n $APP/.MainActivity 2>&1 | grep TotalTime
    done
    
    echo ""
    echo "Memory Usage:"
    adb shell dumpsys meminfo $APP | grep -E "Native|Heap|Stack|TOTAL"
    
    echo ""
    echo "CPU Usage:"
    adb shell top -n 1 | grep $APP
    
    echo ""
    echo "Frame Rate:"
    adb shell dumpsys gfxinfo $APP | grep "Frames"
    
} | tee performance_report.txt
```

---

## 13. Performance Regression Testing

### Compare Performance Over Time
```bash
#!/bin/bash
# regression_test.sh

BASELINE="baseline_perf.txt"
CURRENT="current_perf.txt"

# Get current performance
./performance_benchmark.sh com.example.app > "$CURRENT"

# Compare with baseline
if [ -f "$BASELINE" ]; then
    echo "Comparing with baseline..."
    diff "$BASELINE" "$CURRENT"
    
    if [ $? -ne 0 ]; then
        echo "⚠️ Performance regression detected!"
    else
        echo "✓ Performance maintained"
    fi
else
    echo "Creating baseline..."
    cp "$CURRENT" "$BASELINE"
fi
```

---

## 14. Best Practices Summary

```
DO:
✓ Profile before optimizing
✓ Use Android Profiler
✓ Monitor real devices
✓ Test battery impact
✓ Measure startup time
✓ Test with low RAM devices
✓ Use background tasks wisely
✓ Compress images
✓ Lazy load data
✓ Cache appropriately

DON'T:
✗ Optimize prematurely
✗ Hardcode delays
✗ Leak memory
✗ Block main thread
✗ Load all data at once
✗ Use high resolution images
✗ Continuous location updates
✗ Excessive logging
✗ Ignore GC warnings
✗ Over-design for edge cases
```


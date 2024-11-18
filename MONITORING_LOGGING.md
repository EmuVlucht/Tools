# Monitoring & Logging Guide

## 1. Logcat Basics

```bash
# View logs
adb logcat

# Filter by tag
adb logcat | grep "MyTag"

# Filter by package
adb logcat | grep com.example.app

# Save to file
adb logcat > logs.txt
```

---

## 2. Advanced Logging

```bash
# Verbose logging
ANDROID_LOG_TAGS="*:V" adb logcat

# Timestamp format
adb logcat -v threadtime

# Process ID
adb logcat -v thread

# All formats
adb logcat -v long   # Most verbose
adb logcat -v raw    # Minimal
```

---

## 3. Crash Monitoring

```bash
# Monitor crashes
adb logcat | grep -i "crash\|fatal\|exception"

# ANR detection
adb logcat | grep "ANR in"

# Stack traces
adb logcat | grep "at " | head -50
```

---

## 4. Performance Monitoring

```bash
# Frame rate
adb shell dumpsys gfxinfo com.example.app

# CPU usage
adb shell top -n 1 | grep com.example.app

# Memory
adb shell dumpsys meminfo com.example.app
```

---

## 5. Battery Monitoring

```bash
# Battery stats
adb shell dumpsys battery

# Wakelock analysis
adb shell dumpsys power | grep Wakelock

# CPU usage by app
adb shell dumpsys cpuinfo
```

---

## 6. Network Monitoring

```bash
# Network connections
adb shell netstat

# DNS queries
adb shell cat /proc/net/udp

# Traffic analysis
adb shell dumpsys netstats
```

---

## 7. Firebase Analytics

```bash
# Send event
adb shell am broadcast -a com.google.android.gms.analytics.ANALYTICS_DISPATCH

# View analytics
Firebase Console → Real-time
```

---

## 8. Custom Logging

```bash
# Log to file on device
adb shell "echo 'log message' >> /sdcard/app.log"

# Pull logs
adb pull /sdcard/app.log

# Monitor live
adb shell tail -f /sdcard/app.log
```

---

## 9. System Monitoring

```bash
# Full system dump
adb shell dumpsys

# Activity history
adb shell dumpsys activity

# Package manager
adb shell dumpsys package
```

---

## 10. Continuous Monitoring Script

```bash
#!/bin/bash
# monitor.sh

while true; do
    DATE=$(date '+%Y-%m-%d %H:%M:%S')
    CPU=$(adb shell top -n 1 | grep com.example.app | awk '{print $9}')
    MEM=$(adb shell dumpsys meminfo com.example.app | grep TOTAL | awk '{print $2}')
    
    echo "[$DATE] CPU: $CPU% | Memory: $MEM KB"
    sleep 5
done
```


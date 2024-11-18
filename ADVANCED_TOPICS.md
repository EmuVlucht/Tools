# Advanced Topics ADB

## 1. Custom Port Configurations

### Non-Standard Port Configuration
```bash
# Set custom ADB port
adb -P <port_number> devices

# Connect ke custom port
adb -P 5037 connect 192.168.1.100:5555

# Restart server dengan port custom
adb -P 5038 kill-server
adb -P 5038 start-server
```

### Multiple ADB Instances
```bash
# Instance 1 - default port 5037
adb -P 5037 devices

# Instance 2 - custom port 5038
adb -P 5038 devices

# Hubungkan device ke instance berbeda
adb -P 5037 connect 192.168.1.100:5555
adb -P 5038 connect 192.168.1.101:5555
```

---

## 2. USB Debugging Advanced

### Authorize dengan Private Key
```bash
# List authorized keys
cat ~/.android/adbkey.pub

# Revoke authorization
adb disconnect
adb usb
```

### View Authorized Devices
```bash
adb shell dumpsys usb
```

---

## 3. Shell Command Chaining

### Execute Multiple Commands
```bash
# Sequential execution (dependensi)
adb shell "cd /sdcard && ls -la"

# Multiple commands dengan &&
adb shell "mkdir /sdcard/test && echo 'Created' > /sdcard/test/file.txt"

# Multiple commands dengan ;
adb shell "pwd; cd /sdcard; pwd"

# Pipe commands
adb shell "ps | grep com.example"
```

### Redirection pada Shell
```bash
# Output ke file
adb shell "logcat > /sdcard/log.txt"

# Append ke file
adb shell "echo 'test' >> /sdcard/output.txt"

# Error handling
adb shell "command 2>/dev/null"
```

---

## 4. Advanced Logcat Filtering

### Complex Filtering
```bash
# Multiple tags dengan filter level
adb logcat ActivityManager:I MyApp:D *:S

# Filter dengan regex
adb logcat | grep -E "ERROR|Exception"

# Save dengan rotation
adb logcat -G 100M
adb logcat -g

# Binary logcat (compact format)
adb logcat -B

# Readable dengan timestamp
adb logcat -v threadtime
adb logcat -v long
adb logcat -v color
```

### Process-Specific Logging
```bash
# Get PID aplikasi
adb shell pidof com.example.app

# Monitor spesifik PID
adb shell "logcat --pid=<PID>"
```

### Dump Crash Logs
```bash
# Cek native crashes
adb shell cat /data/anr/*

# Cek tombstone (native crash data)
adb shell ls -la /data/tombstones/

# Pull crash file
adb pull /data/tombstones/crash.txt ./
```

---

## 5. Performance Analysis

### Memory Profiling
```bash
# Detailed memory info
adb shell dumpsys meminfo com.example.app

# Memory by app
adb shell dumpsys meminfo --unreachable

# GC stats
adb shell dumpsys meminfo --local

# PSS memory
adb shell dumpsys meminfo --oom
```

### CPU Profiling
```bash
# Real-time CPU usage
adb shell top -n 1

# CPU usage per app
adb shell dumpsys cpuinfo

# Detailed perf data
adb shell "cat /proc/stat"

# Process threads
adb shell ps -T
```

### Battery Analysis
```bash
# Battery status
adb shell dumpsys battery

# Battery history
adb shell dumpsys batteryproperties

# Power usage breakdown
adb shell dumpsys power
```

---

## 6. Network Debugging

### Network Interface Info
```bash
# Network interfaces
adb shell ifconfig
adb shell ip addr

# Network statistics
adb shell netstat -a

# DNS resolution
adb shell getprop ro.com.google.clientidbase

# Connectivity status
adb shell dumpsys connectivity
```

### Network Simulation
```bash
# Simulate poor network
adb shell tc qdisc add dev eth0 root netem delay 500ms

# Simulate packet loss
adb shell tc qdisc add dev eth0 root netem loss 10%

# Clear simulation
adb shell tc qdisc del dev eth0 root
```

### Monitor Network Traffic
```bash
# Real-time traffic
adb shell dumpsys traffic_stats

# Network history
adb shell cat /sys/class/net/*/statistics/rx_bytes

# Monitor specific app traffic
adb shell dumpsys netstats detail
```

---

## 7. File System Advanced Operations

### Permissions Management
```bash
# View file permissions
adb shell ls -la /sdcard/

# Change permissions
adb shell chmod 755 /sdcard/file.txt

# Change owner
adb shell chown user:group /sdcard/file.txt

# SELinux context
adb shell ls -Z /sdcard/
```

### Disk Space Analysis
```bash
# Disk usage
adb shell df -h

# Directory size
adb shell du -sh /sdcard/

# Size per app
adb shell du -sh /data/data/*/
```

### Inode Management
```bash
# Check inode count
adb shell df -i

# Find files by inode
adb shell find /sdcard -inode 123456
```

---

## 8. Database Access via ADB

### SQLite Database Access
```bash
# List databases
adb shell find /data/data/com.example.app -name "*.db"

# Pull database
adb pull /data/data/com.example.app/databases/app.db ./

# Query SQLite via shell
adb shell "sqlite3 /data/data/com.example.app/databases/app.db 'SELECT * FROM table_name;'"
```

### Database Backup
```bash
# Backup database
adb shell "sqlite3 /data/data/com.example.app/databases/app.db '.dump' > /sdcard/backup.sql"

# Pull backup
adb pull /sdcard/backup.sql ./
```

---

## 9. Advanced Debugging

### Straceング (System Call Tracing)
```bash
# Trace system calls
adb shell strace -p <PID>

# Save trace ke file
adb shell strace -p <PID> -o /sdcard/trace.txt

# Follow child processes
adb shell strace -f -p <PID>
```

### Native Debugging
```bash
# gdb debugging (jika tersedia)
adb shell gdb

# Breakpoint
(gdb) break function_name

# Continue
(gdb) continue

# Backtrace
(gdb) bt
```

### Java Method Tracing
```bash
# Method tracing
adb shell am trace-ipc start

# Stop trace
adb shell am trace-ipc stop

# Pull hasil
adb pull /data/anr/method_trace.bin ./
```

---

## 10. Emulator-Specific Commands

### Emulator Control
```bash
# Get emulator name
adb shell getprop ro.kernel.android.checkjni

# Boot options
adb shell getprop ro.bootmode

# Emulator features
adb shell getprop ro.kernel.qemu
```

### Emulator Snapshots
```bash
# List snapshots
adb shell avdmanager list avd

# Save state
emulator -avd MyAVD -snapshot save my_snapshot

# Load state
emulator -avd MyAVD -snapshot load my_snapshot
```

---

## 11. Security & Permission Deep Dive

### SELinux Context
```bash
# Check SELinux policy
adb shell getenforce

# View file contexts
adb shell ls -Z /system/

# App contexts
adb shell ps -Z | grep com.example
```

### App Sandboxing
```bash
# Check sandbox restrictions
adb shell getprop ro.iorap.perfetto_uidumpstate_app_enabled

# List restricted resources
adb shell dumpsys package com.example.app
```

### Capability Analysis
```bash
# View capabilities
adb shell cat /proc/<PID>/status | grep Cap

# Required permissions
adb shell dumpsys package com.example.app | grep "granted permissions"
```

---

## 12. Performance Optimization Tips

### Reduce Startup Time
```bash
# Profile startup
adb shell dumpsys activity | grep TOTAL

# Check cold/warm start
adb logcat | grep "Displayed"
```

### Optimize Memory
```bash
# Check memory fragmentation
adb shell dumpsys meminfo --unreachable

# Force GC
adb shell am send-trim-memory com.example.app TRIM_MEMORY_RUNNING_CRITICAL
```

### Battery Optimization
```bash
# Check wakelock
adb shell dumpsys batterystats | grep Wakelock

# Check partial wakelock
adb shell dumpsys power | grep "Partial wake locks"
```

---

## 13. OTA (Over-The-Air) Updates

### Check Update Status
```bash
# OTA update status
adb shell getprop ro.build.version.ota

# Build fingerprint
adb shell getprop ro.build.fingerprint

# System update path
adb shell ls /cache/recovery/
```

### Manual Update
```bash
# Push update
adb push update.zip /cache/

# Recovery command
adb shell echo "update_package=/cache/update.zip" > /cache/recovery/command
```

---

## 14. Accessibility Features

### Screen Reader Testing
```bash
# Enable TalkBack
adb shell settings put secure enabled_accessibility_services \
  com.google.android.marktalkback/com.google.android.marktalkback.TalkBackService

# Disable
adb shell settings put secure enabled_accessibility_services ""
```

### High Contrast Mode
```bash
# Enable high contrast
adb shell settings put secure high_text_contrast_enabled 1

# Disable
adb shell settings put secure high_text_contrast_enabled 0
```

---

## 15. Build & System Information

### System Details
```bash
# Android API level
adb shell getprop ro.build.version.sdk

# Kernel version
adb shell uname -a

# CPU architecture
adb shell getprop ro.product.cpu.abi

# RAM size
adb shell cat /proc/meminfo | grep MemTotal
```

### Build Metadata
```bash
# Build date
adb shell getprop ro.build.date.utc

# Build type (user/userdebug)
adb shell getprop ro.build.type

# Security patch level
adb shell getprop ro.build.version.security_patch
```


# Comprehensive ADB Debugging Guide

## Chapter 1: Logcat Mastery

### Logcat Format Understanding
```
I/TAG ( PID): Message

I = Level (I=Info, W=Warning, E=Error, D=Debug, V=Verbose)
TAG = Log tag (usually class name)
PID = Process ID
Message = Log message
```

### Advanced Logcat Usage

#### View with Timestamps
```bash
# Thread time format (most detailed)
adb logcat -v threadtime

# Time format
adb logcat -v time

# Long format
adb logcat -v long

# Color output
adb logcat -v color

# Brief output
adb logcat -v brief
```

#### Filter by Process
```bash
# Get PID of app
adb shell pidof com.example.app
# Output: 12345

# Monitor specific PID
adb logcat --pid=12345

# Or one-liner
adb logcat --pid=$(adb shell pidof com.example.app)
```

#### Save and Analyze Logs
```bash
# Save with threading info
adb logcat -v threadtime > app.log

# Parse specific lines
grep "MyTag" app.log

# Find exceptions
grep -i "exception\|error" app.log

# Timeline analysis
cat app.log | awk '{print $1, $2}' | sort | uniq -c

# Filter by timestamp
awk '/10:30:00/,/10:35:00/' app.log
```

### Common Log Patterns

#### Crash/Exception Logs
```bash
# Find crashes
adb logcat | grep -i "exception\|crash\|fatal"

# ANR (Application Not Responding)
adb logcat | grep "ANR"

# Segmentation Fault
adb logcat | grep "SIGSEGV"

# Out of Memory
adb logcat | grep "OutOfMemory"
```

#### Performance Logs
```bash
# Frame drops (jank)
adb logcat | grep "Skipped"

# Method trace
adb logcat | grep "method_trace"

# GC events
adb logcat | grep "GC_"

# Memory pressure
adb logcat | grep "TRIM_MEMORY"
```

---

## Chapter 2: Crash Debugging

### Stack Traces Decoding

#### Get Full Stack Trace
```bash
# Clear existing logs
adb logcat -c

# Start app (will crash)
adb shell am start -n com.example.app/.MainActivity

# Get full trace
adb logcat *:E

# Example trace:
# FATAL EXCEPTION: main
# Process: com.example.app, PID: 12345
# java.lang.NullPointerException: Attempt to invoke virtual method...
#     at com.example.app.MainActivity.onCreate(MainActivity.java:45)
```

### Analyzing Crash Information

```bash
# Extract line number
# MainActivity.java:45 means line 45 of MainActivity.java

# Use ProGuard mapping (if obfuscated)
retrace.bat mapping.txt crash_trace.txt  # Windows
./retrace.sh mapping.txt crash_trace.txt # Linux/Mac
```

### Native Crashes

#### Logcat Native Crash
```bash
# Monitor native crashes
adb logcat | grep -E "backtrace:|signal|tombstone"

# View tombstone files
adb shell ls -la /data/tombstones/

# Pull tombstone
adb pull /data/tombstones/tombstone_01 ./

# View with symbolication
adb logcat | grep -A 50 "backtrace:"
```

---

## Chapter 3: Memory Debugging

### Memory Analysis

#### Monitor Memory Usage
```bash
# Overall memory
adb shell dumpsys meminfo | head -20

# App-specific memory
adb shell dumpsys meminfo com.example.app

# Memory breakdown
adb shell dumpsys meminfo | grep -E "TOTAL|PSS|USS|VSS"
```

#### Memory Leak Detection
```bash
# Check for growing memory
for i in {1..5}; do
  sleep 10
  echo "Check $i:"
  adb shell dumpsys meminfo com.example.app | grep TOTAL
done

# Monitor native heap
adb shell dumpsys meminfo --local com.example.app

# Check retained objects
adb shell dumpsys meminfo --unreachable
```

### Heap Dump

#### Capture Heap
```bash
# Get process PID
PID=$(adb shell pidof com.example.app)

# Capture heap
adb shell dumpsys meminfo --unreachable $PID

# Or via Android Studio (built-in profiler)
```

---

## Chapter 4: Performance Debugging

### CPU Analysis

#### Monitor CPU Usage
```bash
# Real-time top
adb shell top

# Non-interactive top
adb shell top -n 1

# Top for specific app
adb shell top -n 1 | grep com.example.app

# All processes
adb shell top -p $(adb shell pidof com.example.app)
```

#### Trace Method Execution
```bash
# Start method trace
adb shell am trace-ipc start

# Do actions on device

# Stop trace
adb shell am trace-ipc stop

# Pull trace file
adb pull /data/anr/method_trace.bin ./

# Analyze with Perfetto or Android Profiler
```

### Frame Rate Monitoring

```bash
# Monitor frames
adb shell dumpsys SurfaceFlinger | grep "Missed frames:"

# Get refresh rate
adb shell getprop ro.hardware.keystore

# Profile app frames
adb shell cmd screenrecord --profile=low /sdcard/recording.mp4
```

---

## Chapter 5: Network Debugging

### Network Monitoring

#### Monitor Network Traffic
```bash
# Check network interfaces
adb shell ifconfig

# Network statistics
adb shell netstat -a

# Per-app network stats
adb shell cat /proc/net/dev

# Realtime traffic
adb shell dumpsys traffic_stats
```

#### Network Simulation

```bash
# Add delay
adb shell tc qdisc add dev eth0 root netem delay 500ms

# Simulate packet loss
adb shell tc qdisc add dev eth0 root netem loss 10%

# Limit bandwidth
adb shell tc qdisc add dev eth0 root tbf rate 1mbit burst 32kbit latency 400ms

# Remove simulation
adb shell tc qdisc del dev eth0 root
```

### Traffic Analysis

```bash
# Tcpdump capture
adb shell tcpdump -i any -w /sdcard/capture.pcap

# View capture
adb pull /sdcard/capture.pcap ./
# Open with Wireshark on PC
```

---

## Chapter 6: Battery Debugging

### Battery Status

#### Monitor Battery
```bash
# Current status
adb shell dumpsys battery

# Battery history
adb shell dumpsys battery history

# Power consumption
adb shell dumpsys power

# Wakelock info
adb shell dumpsys power | grep "Wakelock"

# CPU wakelock
adb shell dumpsys cpuinfo | grep "CPU usage"
```

#### Optimize Battery Usage
```bash
# Check wakelocks by app
adb shell dumpsys batterystats | grep -A5 "Wakelocks"

# View wake reasons
adb shell dumpsys power | grep "Wake lock"

# Monitor partial wakelock
adb shell "cat /proc/wakelocks"
```

---

## Chapter 7: Database Debugging

### SQLite Access

#### Query Databases
```bash
# Find app database
adb shell find /data/data/com.example.app -name "*.db"

# Connect to database
adb shell sqlite3 /data/data/com.example.app/db.db

# Common SQL commands
> .tables          # Show tables
> .schema          # Show schema
> SELECT * FROM table_name LIMIT 10;
> .dump            # Dump all data
> .quit            # Exit
```

#### Export and Import
```bash
# Export data
adb shell "sqlite3 /data/data/com.example.app/db.db '.dump' > /sdcard/backup.sql"

# Pull to computer
adb pull /sdcard/backup.sql ./

# Analyze on PC with SQLBrowser
```

---

## Chapter 8: ANR (Application Not Responding) Debugging

### Capture ANR Data

```bash
# Find ANR files
adb shell ls -la /data/anr/

# Pull ANR trace
adb pull /data/anr/traces.txt ./

# View ANR info
cat traces.txt | head -100
```

### Analyze ANR

```bash
# Common ANR causes:
# 1. Heavy operation on main thread
# 2. Deadlock
# 3. Infinite loop
# 4. Waiting for network/IO

# Monitor for ANR in logcat
adb logcat | grep "ANR in"

# Check blocked threads
grep "MONITOR CONTENTION" traces.txt
```

---

## Chapter 9: System Service Debugging

### Monitor System Services

```bash
# List running services
adb shell dumpsys

# Activity manager
adb shell dumpsys activity

# Package manager
adb shell dumpsys package

# Window manager
adb shell dumpsys window

# Surface flinger
adb shell dumpsys SurfaceFlinger
```

### Service-Specific Commands

```bash
# All settings
adb shell dumpsys settings

# Connectivity
adb shell dumpsys connectivity

# Notification manager
adb shell dumpsys notification

# Alarm manager
adb shell dumpsys alarm
```

---

## Chapter 10: UI/View Debugging

### View Hierarchy

#### Get Layout Hierarchy
```bash
# Dump view hierarchy
adb shell dumpsys activity top | grep -A 30 "mCurrentFocus"

# Window manager dump
adb shell dumpsys window windows | grep -A 5 "mCurrentFocus"
```

#### Layout Inspection
```bash
# Get all visible windows
adb shell dumpsys window windows | grep "Window #"

# Focus window
adb shell dumpsys window windows | grep "mCurrentFocus"

# Input focus
adb shell dumpsys input | grep "mFocusedApplication"
```

---

## Chapter 11: Debuggable App Features

### Debugging Options

#### Enable Debug Features
```bash
# Check if debuggable
adb shell getprop ro.debuggable

# Enable USB debugging via shell
adb shell settings put global adb_enabled 1

# Debug port forwarding
adb forward tcp:5005 jdwp:$(adb shell pidof com.example.app)
```

#### Runtime Debugging
```bash
# Start debugger
adb jdwp
# Lists JDWP PIDs

# Connect to JDWP
adb forward tcp:5005 jdwp:12345

# Use IDE (Android Studio) to connect
```

---

## Chapter 12: Common Debugging Workflows

### Workflow 1: Find Crash in New App
```bash
# 1. Clear logs
adb logcat -c

# 2. Launch app
adb shell am start -n com.example.app/.MainActivity

# 3. Trigger crash
# (Do actions that crash the app)

# 4. Get trace
adb logcat | grep -A 50 "FATAL EXCEPTION"

# 5. Find line number and check code
```

### Workflow 2: Diagnose Slow App
```bash
# 1. Check memory
adb shell dumpsys meminfo com.example.app

# 2. Monitor CPU
adb shell top -n 1

# 3. Check for ANR
adb logcat | grep "ANR"

# 4. Profile with Android Studio
# (Use built-in profiler)
```

### Workflow 3: Fix Memory Leak
```bash
# 1. Trigger suspected leak
# (Do actions repeatedly)

# 2. Monitor memory
for i in {1..10}; do
  sleep 5
  adb shell dumpsys meminfo com.example.app | grep TOTAL
done

# 3. If memory grows:
# - Check logcat for "GC_FOR_ALLOC"
# - Use heap dump to find retained objects
# - Fix by releasing resources
```

---

## Chapter 13: Debugging Tools

### Built-in Tools
- **Android Studio Profiler** - UI, CPU, Memory, Network
- **Logcat** - System logs
- **Device Monitor** - System monitoring
- **Android Emulator** - Simulated device

### External Tools
- **Wireshark** - Network analysis
- **SQLBrowser** - Database inspection
- **Android SDK Platform Tools** - ADB suite
- **Custom scripts** - Automation

---

## Chapter 14: Debugging Checklist

```
□ Clear logcat buffer
□ Reproduce issue
□ Check logcat for errors/warnings
□ Verify crashes in ANR files
□ Monitor memory with dumpsys
□ Profile with Android Studio
□ Check network with netstat
□ Verify database integrity
□ Test with different Android versions
□ Test on different devices
□ Check device logs/diagnostics
□ Document findings
```

---

## Chapter 15: Debug Commands Quick Reference

```bash
# Immediate crash debugging
adb logcat -c
adb shell am start -n com.example.app/.MainActivity
adb logcat *:E

# Memory issues
adb shell dumpsys meminfo com.example.app | grep TOTAL

# ANR/Freeze issues
adb shell ls /data/anr/
adb pull /data/anr/traces.txt ./

# Performance issues
adb shell top -n 1
adb shell dumpsys SurfaceFlinger

# Network issues
adb shell netstat -a
adb shell dumpsys connectivity

# Database issues
adb shell find /data/data/com.example.app -name "*.db"
adb shell sqlite3 /path/to/db.db ".tables"

# View hierarchy issues
adb shell dumpsys activity top
adb shell dumpsys window windows

# Permission issues
adb shell dumpsys package com.example.app | grep permission

# Service issues
adb shell dumpsys servicename
```


# Advanced Troubleshooting Guide

## 1. Connection Issues Deep Dive

### Device Not Recognized
```bash
# Comprehensive fix checklist
adb kill-server
adb start-server

# Check if daemon is running
ps aux | grep adb

# Verify USB connection
lsusb | grep -i android

# Check permissions (Linux)
ls -la /dev/bus/usb/

# Add user to group
sudo usermod -a -G plugdev $USER

# Check udev rules
cat /etc/udev/rules.d/51-android.rules

# Reload rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Unauthorized Device
```bash
# Check ADB keys
ls -la ~/.android/

# Revoke all authorizations
rm ~/.android/adbkey*

# Disconnect and reconnect
adb disconnect
adb usb

# Verify connection
adb devices
```

---

## 2. Port & Network Issues

### Port Already in Use
```bash
# Find what's using port 5037
lsof -i :5037

# Kill the process
kill -9 <PID>

# Or use different port
adb -P 5038 devices

# Windows - Find process
netstat -ano | findstr :5037
taskkill /PID <PID> /F
```

### Network Debugging
```bash
# Test connectivity
ping 192.168.1.100

# Check if port open
nc -zv 192.168.1.100 5555

# Network interface info
ifconfig
ipconfig  # Windows

# DNS resolution
nslookup 192.168.1.100
```

---

## 3. Performance Issues

### Slow ADB Operations
```bash
# Check system load
top
uptime

# Check disk I/O
iostat

# Monitor ADB process
strace -p $(pgrep adb)

# Enable debug logging
ANDROID_LOG_TAGS="*:V" adb logcat

# Profile ADB
adb -v devices  # Verbose mode
```

---

## 4. Logcat Problems

### Logcat Not Showing Output
```bash
# Clear buffer and restart
adb logcat -c
adb logcat -v threadtime

# Check process is running
adb shell ps | grep com.example.app

# Verify logging is enabled
adb shell getprop ro.debuggable

# Try alternative format
adb logcat -v long
adb logcat -v raw

# Check log buffer size
adb logcat -g
adb logcat -G 16M
```

---

## 5. Installation Issues

### APK Installation Fails
```bash
# Check error details
adb install app.apk

# Common errors & solutions
# Error: INSTALL_FAILED_INVALID_APK
  → APK is corrupted, re-sign and rebuild
  
# Error: INSTALL_FAILED_VERSION_DOWNGRADE
  → Use -r flag or uninstall first
  adb uninstall com.example.app
  adb install app.apk
  
# Error: INSTALL_FAILED_INSUFFICIENT_STORAGE
  → Clear device storage
  adb shell pm clear com.example.app
  adb shell rm -rf /cache/*
  
# Error: INSTALL_FAILED_PERMISSION_MODEL_DOWNGRADE
  → Device permission model incompatible
  → Rebuild targeting correct API
```

---

## 6. Device-Specific Issues

### Emulator Problems
```bash
# Emulator won't start
emulator -avd MyAVD -verbose

# Check if AVD exists
emulator -list-avds

# Create new AVD
avdmanager create avd -n TestAVD -k "system-images;android-30;google_apis;x86_64"

# Delete corrupted AVD
emulator -delete-avd OldAVD

# Clear emulator data
rm -rf ~/.android/avd/MyAVD/
```

### Samsung-Specific
```bash
# ADB not recognizing Samsung device
# 1. Install Samsung USB driver
# 2. Enable developer mode
# 3. Enable MTP mode (not PTP)
# 4. Restart ADB

adb kill-server
adb start-server
adb devices
```

---

## 7. Memory & Crash Issues

### Out of Memory
```bash
# Check available memory
adb shell cat /proc/meminfo

# Clear caches
adb shell pm clear com.example.app
adb shell fstrim /data

# Reduce app processes
adb shell ps -A | wc -l

# Kill background processes
adb shell am kill-all
```

### App Crashes
```bash
# Get crash details
adb logcat | grep FATAL

# Collect ANR data
adb pull /data/anr/traces.txt ./

# Check for segfault
adb logcat | grep SIGSEGV

# Debug with strace
adb shell strace -p $(adb shell pidof com.example.app)
```

---

## 8. Permission Issues

### Permission Denied Errors
```bash
# Linux - Add to plugdev group
sudo usermod -a -G plugdev $USER
newgrp plugdev

# Check current groups
groups

# Try with sudo
sudo adb devices

# Or change permissions
sudo chmod 666 /dev/bus/usb/*/
```

### App Permissions
```bash
# List permissions
adb shell pm list permissions

# Grant permission
adb shell pm grant com.example.app android.permission.CAMERA

# Verify granted
adb shell dumpsys package com.example.app | grep permissions
```

---

## 9. File Transfer Issues

### Push/Pull Failures
```bash
# Check file exists locally
ls -la file.txt

# Check destination writable
adb shell ls -la /sdcard/

# Try with different destination
adb push file.txt /data/local/tmp/

# Check file size
adb shell df -h /sdcard/

# Use direct path
adb push file.txt /sdcard/Documents/
```

---

## 10. WiFi Connection Issues

### ADB over Network Not Working
```bash
# Verify both devices on same network
adb shell ifconfig | grep inet

# Check firewall
# Ensure port 5555 open

# Try explicit IP
adb connect 192.168.1.100:5555

# Debug connection
adb -v connect 192.168.1.100:5555

# Enable tcpip on device
adb tcpip 5555

# Test connectivity
ping 192.168.1.100
nc -zv 192.168.1.100 5555
```

---

## 11. Build Issues

### Gradle/Build Problems
```bash
# Clean rebuild
./gradlew clean assembleDebug

# Check plugin compatibility
./gradlew --version

# Force update dependencies
./gradlew build --refresh-dependencies

# Check for lint errors
./gradlew lint

# View detailed build log
./gradlew assembleDebug -i
```

---

## 12. Debugging ADB Itself

### ADB Internal Issues
```bash
# Check ADB version
adb version

# Update ADB
adb update-server

# Verbose mode
adb -d -v install app.apk

# Generate ADB logs
ANDROID_ADB_SERVER_PORT=5037 adb devices

# Check server socket
netstat -tlnp | grep adb

# Reset ADB state
adb disconnect-all
adb kill-server
adb start-server
```

---

## 13. Diagnostic Commands

```bash
# System diagnostics
adb shell getprop > device_properties.txt

# USB diagnostics
adb shell dumpsys usb

# Hardware info
adb shell cat /proc/cpuinfo
adb shell cat /proc/meminfo

# SELinux status
adb shell getenforce

# Kernel version
adb shell uname -a

# Build info
adb shell getprop ro.build.fingerprint
```

---

## 14. Common Error Codes

```
INSTALL_FAILED_INVALID_APK
  → APK signature invalid or corrupted

INSTALL_FAILED_INSUFFICIENT_STORAGE
  → Device storage full

INSTALL_FAILED_DUPLICATE_PACKAGE
  → App already installed

INSTALL_FAILED_NO_SHARED_USER
  → SharedUserID mismatch

INSTALL_FAILED_UPDATE_INCOMPATIBLE
  → Version/signature mismatch

INSTALL_FAILED_VERSION_DOWNGRADE
  → Trying to install older version

INSTALL_FAILED_PERMISSION_MODEL_DOWNGRADE
  → Permission model mismatch
```

---

## 15. Quick Diagnostic Script

```bash
#!/bin/bash
# diagnose.sh

echo "=== ADB Diagnostic Report ==="
echo "Date: $(date)"
echo ""

echo "ADB Version:"
adb version
echo ""

echo "Connected Devices:"
adb devices -l
echo ""

echo "Device Properties:"
adb shell getprop | head -20
echo ""

echo "Disk Space:"
adb shell df -h
echo ""

echo "Memory:"
adb shell free -h
echo ""

echo "Running Processes:"
adb shell ps | wc -l
echo ""

echo "Recent Crashes:"
adb pull /data/anr/traces.txt ./ 2>/dev/null && tail -20 traces.txt || echo "No crashes"
```


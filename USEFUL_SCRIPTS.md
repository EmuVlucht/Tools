# Useful ADB Scripts & Automation

## Script 1: Multi-Device Installer

**install_all_devices.sh**
```bash
#!/bin/bash
# Install APK on all connected devices

APK_FILE=$1

if [ -z "$APK_FILE" ]; then
    echo "Usage: ./install_all_devices.sh app.apk"
    exit 1
fi

if [ ! -f "$APK_FILE" ]; then
    echo "Error: $APK_FILE not found"
    exit 1
fi

echo "Installing $APK_FILE on all devices..."

# Get list of devices
DEVICES=$(adb devices | grep device | grep -v "List of attached" | awk '{print $1}')

if [ -z "$DEVICES" ]; then
    echo "No devices found!"
    exit 1
fi

COUNT=0
for DEVICE in $DEVICES; do
    echo "Installing on $DEVICE..."
    adb -s "$DEVICE" install -r "$APK_FILE"
    if [ $? -eq 0 ]; then
        COUNT=$((COUNT + 1))
        echo "✓ Successfully installed on $DEVICE"
    else
        echo "✗ Failed to install on $DEVICE"
    fi
done

echo "Installation complete! Installed on $COUNT device(s)"
```

Usage:
```bash
chmod +x install_all_devices.sh
./install_all_devices.sh myapp.apk
```

---

## Script 2: Device Information Collector

**device_info.sh**
```bash
#!/bin/bash
# Collect comprehensive device information

DEVICE=$1
if [ -z "$DEVICE" ]; then
    DEVICE=$(adb devices | grep device | head -1 | awk '{print $1}')
fi

echo "===== Device Information ====="
echo "Device ID: $DEVICE"
echo ""

echo "=== System Information ==="
echo "Android Version: $(adb -s $DEVICE shell getprop ro.build.version.release)"
echo "API Level: $(adb -s $DEVICE shell getprop ro.build.version.sdk)"
echo "Device Model: $(adb -s $DEVICE shell getprop ro.product.model)"
echo "Brand: $(adb -s $DEVICE shell getprop ro.product.brand)"
echo "Manufacturer: $(adb -s $DEVICE shell getprop ro.product.manufacturer)"
echo "Device ID: $(adb -s $DEVICE shell settings get secure android_id)"
echo ""

echo "=== Hardware Information ==="
echo "CPU ABI: $(adb -s $DEVICE shell getprop ro.product.cpu.abi)"
echo "CPU ABI2: $(adb -s $DEVICE shell getprop ro.product.cpu.abi2)"
echo "RAM: $(adb -s $DEVICE shell "cat /proc/meminfo | grep MemTotal")"
echo ""

echo "=== Build Information ==="
echo "Build ID: $(adb -s $DEVICE shell getprop ro.build.id)"
echo "Build Fingerprint: $(adb -s $DEVICE shell getprop ro.build.fingerprint)"
echo "Security Patch: $(adb -s $DEVICE shell getprop ro.build.version.security_patch)"
echo "Build Date: $(adb -s $DEVICE shell getprop ro.build.date)"
echo ""

echo "=== Storage Information ==="
adb -s $DEVICE shell df -h /data /cache /sdcard
echo ""

echo "=== Display Information ==="
echo "Display Size: $(adb -s $DEVICE shell wm size)"
echo "Display Density: $(adb -s $DEVICE shell wm density)"
```

Usage:
```bash
chmod +x device_info.sh
./device_info.sh          # Use default device
./device_info.sh 192.168.1.100:5555  # Specific device
```

---

## Script 3: Logcat Capture with Timestamp

**capture_logs.sh**
```bash
#!/bin/bash
# Capture logs with timestamp and app filtering

APP_NAME=$1
DURATION=${2:-300}  # Default 5 minutes

if [ -z "$APP_NAME" ]; then
    echo "Usage: ./capture_logs.sh com.example.app [duration_seconds]"
    exit 1
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="logs_${APP_NAME}_${TIMESTAMP}.txt"

echo "Capturing logs for $APP_NAME for $DURATION seconds..."
echo "Output: $OUTPUT_FILE"

# Clear existing logs
adb logcat -c

# Start capturing
timeout $DURATION adb logcat -v threadtime | tee "$OUTPUT_FILE"

echo "Log capture complete!"
echo "Total lines: $(wc -l < "$OUTPUT_FILE")"
```

Usage:
```bash
chmod +x capture_logs.sh
./capture_logs.sh com.example.app    # 5 minutes
./capture_logs.sh com.example.app 600  # 10 minutes
```

---

## Script 4: Batch File Transfer

**transfer_files.sh**
```bash
#!/bin/bash
# Transfer multiple files from PC to device

SOURCE_DIR=$1
DEST_DIR=${2:-"/sdcard/"}

if [ -z "$SOURCE_DIR" ] || [ ! -d "$SOURCE_DIR" ]; then
    echo "Usage: ./transfer_files.sh /path/to/files [destination]"
    echo "Example: ./transfer_files.sh ./data /sdcard/data"
    exit 1
fi

echo "Transferring files from $SOURCE_DIR to $DEST_DIR"

FILE_COUNT=0
for file in "$SOURCE_DIR"/*; do
    if [ -f "$file" ]; then
        FILENAME=$(basename "$file")
        echo "Pushing: $FILENAME"
        adb push "$file" "$DEST_DIR"
        FILE_COUNT=$((FILE_COUNT + 1))
    fi
done

echo "Transfer complete! $FILE_COUNT files transferred"
```

Usage:
```bash
chmod +x transfer_files.sh
./transfer_files.sh ./my_files /sdcard/Documents
```

---

## Script 5: Automatic Daily Backup

**daily_backup.sh**
```bash
#!/bin/bash
# Create daily backup of app data

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

echo "Creating backup at $BACKUP_DIR/backup_$TIMESTAMP.ab"

adb backup -all -f "$BACKUP_DIR/backup_$TIMESTAMP.ab"

if [ $? -eq 0 ]; then
    SIZE=$(du -h "$BACKUP_DIR/backup_$TIMESTAMP.ab" | cut -f1)
    echo "✓ Backup created successfully ($SIZE)"
    
    # Keep only last 7 backups
    cd "$BACKUP_DIR"
    ls -t backup_*.ab | tail -n +8 | xargs rm -f
    echo "Cleaned up old backups (keeping last 7)"
else
    echo "✗ Backup failed"
fi
```

Usage:
```bash
chmod +x daily_backup.sh
./daily_backup.sh

# Schedule with cron
# 0 2 * * * /path/to/daily_backup.sh  (2 AM daily)
```

---

## Script 6: Monitor App Memory

**monitor_memory.sh**
```bash
#!/bin/bash
# Monitor app memory usage over time

APP=$1
INTERVAL=${2:-5}    # Interval in seconds
DURATION=${3:-300}  # Duration in seconds

if [ -z "$APP" ]; then
    echo "Usage: ./monitor_memory.sh com.example.app [interval] [duration]"
    exit 1
fi

OUTPUT_FILE="memory_monitor_$(date +%Y%m%d_%H%M%S).csv"

echo "Time,Heap,Native,PSS" > "$OUTPUT_FILE"

echo "Monitoring memory for $DURATION seconds (every $INTERVAL seconds)..."

ELAPSED=0
while [ $ELAPSED -lt $DURATION ]; do
    TIMESTAMP=$(date +%H:%M:%S)
    
    MEMINFO=$(adb shell dumpsys meminfo "$APP")
    HEAP=$(echo "$MEMINFO" | grep "TOTAL" | head -1 | awk '{print $2}')
    
    echo "$TIMESTAMP,$HEAP" >> "$OUTPUT_FILE"
    echo "[$TIMESTAMP] Memory: $HEAP KB"
    
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
done

echo "Memory monitoring complete!"
echo "Results saved to: $OUTPUT_FILE"
```

Usage:
```bash
chmod +x monitor_memory.sh
./monitor_memory.sh com.example.app         # 5 sec interval, 5 min duration
./monitor_memory.sh com.example.app 2 600   # 2 sec interval, 10 min duration
```

---

## Script 7: Test Multiple Devices

**test_all_devices.sh**
```bash
#!/bin/bash
# Run tests on all connected devices

TEST_APK=$1
TARGET_APK=$2

if [ -z "$TEST_APK" ] || [ -z "$TARGET_APK" ]; then
    echo "Usage: ./test_all_devices.sh test.apk target.apk"
    exit 1
fi

DEVICES=$(adb devices | grep device | grep -v "List of attached" | awk '{print $1}')

for DEVICE in $DEVICES; do
    echo "=== Testing on $DEVICE ==="
    
    # Install apps
    adb -s "$DEVICE" install -r "$TARGET_APK"
    adb -s "$DEVICE" install -r "$TEST_APK"
    
    # Run tests
    adb -s "$DEVICE" shell am instrument -w com.example.tests/android.test.InstrumentationTestRunner
    
    # Collect results
    adb -s "$DEVICE" pull /data/data/com.example.app/results.xml ./results_$DEVICE.xml
    
    echo "✓ Tests completed on $DEVICE"
done

echo "All tests completed!"
```

---

## Script 8: Screenshot & Download

**quick_screenshot.sh**
```bash
#!/bin/bash
# Quick screenshot and download

DEVICE=$1
OUTPUT_DIR="./screenshots"

mkdir -p "$OUTPUT_DIR"

FILENAME="screenshot_$(date +%Y%m%d_%H%M%S).png"
FULL_PATH="$OUTPUT_DIR/$FILENAME"

echo "Taking screenshot..."

adb -s "$DEVICE" shell screencap -p /sdcard/sc.png
adb -s "$DEVICE" pull /sdcard/sc.png "$FULL_PATH"
adb -s "$DEVICE" shell rm /sdcard/sc.png

echo "✓ Screenshot saved: $FULL_PATH"

# Open image (macOS)
# open "$FULL_PATH"

# Open image (Linux)
# xdg-open "$FULL_PATH"

# Open image (Windows)
# start "$FULL_PATH"
```

Usage:
```bash
chmod +x quick_screenshot.sh
./quick_screenshot.sh
```

---

## Script 9: Performance Test

**performance_test.sh**
```bash
#!/bin/bash
# Collect performance metrics

APP=$1
OUTPUT_FILE="perf_$(date +%Y%m%d_%H%M%S).txt"

if [ -z "$APP" ]; then
    echo "Usage: ./performance_test.sh com.example.app"
    exit 1
fi

{
    echo "=== Performance Test for $APP ==="
    echo "Timestamp: $(date)"
    echo ""
    
    echo "=== Memory Usage ==="
    adb shell dumpsys meminfo "$APP" | head -20
    echo ""
    
    echo "=== CPU Usage (top) ==="
    adb shell top -n 1 | grep "$APP"
    echo ""
    
    echo "=== Running Processes ==="
    adb shell ps | grep "$APP"
    echo ""
    
    echo "=== Battery Status ==="
    adb shell dumpsys battery
    
} | tee "$OUTPUT_FILE"

echo ""
echo "Results saved to: $OUTPUT_FILE"
```

---

## Script 10: Git Ignore Generator

**create_gitignore.sh**
```bash
#!/bin/bash
# Generate .gitignore for ADB project

cat > .gitignore << 'EOF'
# Logs and traces
*.log
*.txt
logs/
traces/

# Backups
*.ab
*.backup
backups/
*.bak

# APKs and binaries
*.apk
*.dex
*.so

# Screenshots and recordings
screenshots/
*.png
*.jpg
*.mp4

# OS files
.DS_Store
Thumbs.db

# IDE
.idea/
.vscode/
*.swp
*.swo

# Databases
*.db
*.sqlite

# Temporary files
*.tmp
tmp/
temp/

# System
.gradle/
build/
dist/

# Generated files
*.out
EOF

echo "✓ .gitignore created"
```

---

## Script 11: Emulator Manager

**emulator_manager.sh**
```bash
#!/bin/bash
# Manage emulator instances

COMMAND=$1
AVD_NAME=$2

create_emulator() {
    echo "Creating emulator: $AVD_NAME"
    echo "n" | avdmanager create avd -n "$AVD_NAME" -k "system-images;android-30;google_apis;x86_64"
}

start_emulator() {
    echo "Starting emulator: $AVD_NAME"
    emulator -avd "$AVD_NAME" -no-snapshot-load &
}

stop_emulator() {
    echo "Stopping all emulators"
    killall emulator64-x86_64
}

list_emulators() {
    echo "Available emulators:"
    emulator -list-avds
}

case $COMMAND in
    create)
        [ -z "$AVD_NAME" ] && echo "Specify AVD name" && exit 1
        create_emulator
        ;;
    start)
        [ -z "$AVD_NAME" ] && echo "Specify AVD name" && exit 1
        start_emulator
        ;;
    stop)
        stop_emulator
        ;;
    list)
        list_emulators
        ;;
    *)
        echo "Usage: ./emulator_manager.sh [create|start|stop|list] [AVD_NAME]"
        ;;
esac
```

---

## Python Script: ADB Wrapper

**adb_wrapper.py**
```python
#!/usr/bin/env python3

import subprocess
import sys
import json
from pathlib import Path

class ADBWrapper:
    def __init__(self):
        self.devices = self.get_devices()
    
    def run_command(self, cmd, device=None):
        """Run ADB command"""
        if device:
            full_cmd = f"adb -s {device} {cmd}"
        else:
            full_cmd = f"adb {cmd}"
        
        try:
            result = subprocess.check_output(full_cmd, shell=True, text=True)
            return result.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            return None
    
    def get_devices(self):
        """Get list of connected devices"""
        output = self.run_command("devices")
        devices = []
        for line in output.split("\n")[1:]:
            if "device" in line:
                device_id = line.split()[0]
                devices.append(device_id)
        return devices
    
    def install_app(self, apk_path, device=None):
        """Install APK on device"""
        return self.run_command(f"install {apk_path}", device)
    
    def get_device_info(self, device=None):
        """Get device information"""
        info = {}
        info['model'] = self.run_command("shell getprop ro.product.model", device)
        info['android_version'] = self.run_command("shell getprop ro.build.version.release", device)
        info['api_level'] = self.run_command("shell getprop ro.build.version.sdk", device)
        return info
    
    def push_file(self, local, remote, device=None):
        """Push file to device"""
        return self.run_command(f"push {local} {remote}", device)
    
    def pull_file(self, remote, local, device=None):
        """Pull file from device"""
        return self.run_command(f"pull {remote} {local}", device)

if __name__ == "__main__":
    adb = ADBWrapper()
    
    print("Connected devices:")
    for device in adb.devices:
        info = adb.get_device_info(device)
        print(f"  {device}: {info['model']} (Android {info['android_version']})")
```

Usage:
```python
python3 adb_wrapper.py
```


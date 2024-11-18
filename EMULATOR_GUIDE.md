# Android Emulator Guide with ADB

## 1. Emulator Setup

### Create Virtual Device
```bash
# List available images
sdkmanager --list | grep "system-images"

# Create AVD
avdmanager create avd -n TestDevice -k "system-images;android-33;google_apis;x86_64"

# List AVDs
avdmanager list avds

# Delete AVD
avdmanager delete avd -n TestDevice
```

### Launch Emulator
```bash
# Launch with specific AVD
emulator -avd TestDevice

# With options
emulator -avd TestDevice -writable-system -no-snapshot-load

# Headless mode (no GUI)
emulator -avd TestDevice -no-window

# With specific resolution
emulator -avd TestDevice -screen 1080x1920

# With more RAM
emulator -avd TestDevice -memory 4096
```

---

## 2. Emulator ADB Connection

### Connect to Emulator
```bash
# Emulator auto-detected
adb devices
# Output: emulator-5554 device

# Multiple emulators
emulator -avd TestDevice1 &
emulator -avd TestDevice2 &

adb devices
# emulator-5554 (first)
# emulator-5556 (second)

# Run on specific emulator
adb -s emulator-5554 shell
```

### Network Configuration
```bash
# Emulator IP (usually 10.0.2.2 for accessing host)
adb shell ip addr show

# Access host from emulator
adb shell ping 10.0.2.2

# Port forward (desktop to emulator)
adb -s emulator-5554 forward tcp:8888 tcp:80
```

---

## 3. Performance Optimization

### Emulator Settings
```bash
# GPU acceleration (if supported)
emulator -avd TestDevice -gpu auto

# Disable snapshot
emulator -avd TestDevice -no-snapshot-load

# Cold boot (slower)
emulator -avd TestDevice -no-snapshot

# Faster boot options
emulator -avd TestDevice -snapshot default -snapshot-save-on-exit

# Disable audio
emulator -avd TestDevice -audio none

# Verbose mode
emulator -avd TestDevice -verbose
```

### Speed Improvements
```
Fastest configuration:
- API 30+ (newer = faster)
- x86_64 architecture
- GPU acceleration enabled
- Adequate RAM allocation (4GB+)
- No snapshot on exit
- SSD storage for .android directory
```

---

## 4. Emulator Snapshots

### Take Snapshot
```bash
# During emulator session
adb shell save-snapshot TestSnapshot

# Or via emulator interface
# Extended controls → Snapshots → Save
```

### Load Snapshot
```bash
emulator -avd TestDevice -snapshot TestSnapshot

# Quick restoration
emulator -avd TestDevice -snapshot default
```

---

## 5. Emulator Telnet Control

### Connect via Telnet
```bash
# Get emulator console port
netstat -ano | findstr emulator

# Connect (e.g., port 5554)
telnet localhost 5554

# Commands in console
help              # Show help
ping              # Check connection
power on/off      # Power control
gsm call 1234567  # Simulate call
gsm accept        # Accept call
sms send 1234567 "message"  # Send SMS
```

---

## 6. Emulator Data Management

### Backup Emulator Data
```bash
# Pull emulator storage
adb -s emulator-5554 pull /data/ ./emulator_data/

# Backup entire sdcard
adb -s emulator-5554 pull /sdcard/ ./emulator_sdcard/
```

### Restore Emulator Data
```bash
# Push data back
adb -s emulator-5554 push ./emulator_data /data/

# Restore sdcard
adb -s emulator-5554 push ./emulator_sdcard /sdcard/
```

---

## 7. Sensors Simulation

### Simulate GPS
```bash
# Via telnet console
telnet localhost 5554

geo fix -74.0096 40.7128  # New York
geo fix 0 0              # Reset

# Via ADB
adb shell provider call gps 1 "SELECT 0" 2>&1
```

### Simulate Accelerometer
```bash
# Via extended controls
# Extended controls → Sensors → Accelerometer
# Tilt device to simulate movement

# Or telnet:
sensor set acceleration 0 0 10
sensor set acceleration 10 0 0
```

### Simulate Battery
```bash
# Via telnet
power capacity 50        # 50% battery
power ac off            # Unplugged
power ac on             # Plugged in
power status full       # Full charge
```

---

## 8. Network Simulation

### Simulate Poor Network
```bash
# Via extended controls
# Network → Throttle
# Options: Full, LTE, UMTS, Edge, GPRS

# Via telnet
netdelay gprs
netdelay umts
netdelay lte
netdelay none
```

### Network Speed Limits
```bash
# Download/upload speed
netspeed full        # Unlimited
netspeed umts        # Limited
netspeed wifi        # Fast
```

---

## 9. Emulator Debugging

### Enable USB Debugging in Emulator
```bash
# Already enabled by default
# Settings → System → Developer Options
# USB Debugging enabled

# If not:
adb -s emulator-5554 shell settings put secure adb_enabled 1
```

### Logcat from Emulator
```bash
# View logs
adb -s emulator-5554 logcat

# Filter logs
adb -s emulator-5554 logcat | grep "com.example"

# Save to file
adb -s emulator-5554 logcat > emulator_logs.txt
```

---

## 10. Multiple Emulator Testing

### Run Multiple Emulators
```bash
#!/bin/bash
# run_multiple_emulators.sh

# Start multiple emulators
emulator -avd Pixel5 -port 5554 &
emulator -avd Nexus6 -port 5556 &
emulator -avd Tablet -port 5558 &

sleep 20  # Wait for boot

# Test on all
adb devices

# Run test on each
for device in emulator-5554 emulator-5556 emulator-5558; do
    echo "Testing on $device"
    adb -s $device install app.apk
    adb -s $device shell am start -n com.example.app/.MainActivity
done
```

---

## 11. Emulator Files

### Locate Emulator Files
```
Windows:
C:\Users\[User]\.android\avd\[AVD_Name]\

Linux:
~/.android/avd/[AVD_Name]/

macOS:
~/.android/avd/[AVD_Name]/

Files:
- system.img (system partition)
- userdata.img (user data)
- cache.img (cache)
- hardware.ini (configuration)
```

### Resize Emulator Storage
```bash
# Edit hardware.ini
nano ~/.android/avd/TestDevice/hardware.ini

# Change:
disk.dataPartition.size=2048M  # Increase to 4096M

# Restart emulator
```

---

## 12. Emulator Advanced Features

### Copy-Paste to Emulator
```bash
# Copy on host
# Paste in emulator
Ctrl+V

# Via clipboard
adb shell input text "paste this text"
```

### File Drag and Drop
```bash
# Drag file to emulator window
# File transferred to /sdcard/

# Or via ADB
adb push file.txt /sdcard/
```

---

## 13. Emulator Troubleshooting

### Emulator Won't Start
```bash
# Check if process exists
ps aux | grep emulator

# Kill and restart
pkill emulator
emulator -avd TestDevice

# Clear cache
rm -rf ~/.android/avd/TestDevice/cache.img
```

### Slow Emulator
```bash
# Solutions:
1. Enable GPU acceleration
   emulator -avd TestDevice -gpu auto

2. Allocate more RAM
   Edit hardware.ini: hw.ramSize=4096

3. Use x86_64 architecture

4. Use SSD for .android directory

5. Disable unnecessary background services
   adb shell pm disable-user --user 0 com.android.chrome
```

### Emulator Freezes
```bash
# Kill emulator
adb kill-server
pkill emulator

# Start fresh
emulator -avd TestDevice -no-snapshot-load
```

---

## 14. Android Version Specific

### Test Different Android Versions
```bash
# Create emulators for different versions
avdmanager create avd -n Android10 -k "system-images;android-30;google_apis;x86_64"
avdmanager create avd -n Android11 -k "system-images;android-31;google_apis;x86_64"
avdmanager create avd -n Android12 -k "system-images;android-32;google_apis;x86_64"
avdmanager create avd -n Android13 -k "system-images;android-33;google_apis;x86_64"

# Launch each
for api in 30 31 32 33; do
    emulator -avd Android$api &
done
```

---

## 15. Emulator Best Practices

```
DO:
✓ Use latest Android API when possible
✓ Enable GPU acceleration
✓ Use x86_64 architecture
✓ Allocate sufficient RAM (4GB+)
✓ Take snapshots before major changes
✓ Use SSD for storage
✓ Close unused emulators

DON'T:
✗ Run too many emulators simultaneously
✗ Use old Android versions unless testing compatibility
✗ Disable GPU without reason
✗ Keep massive snapshots
✗ Fill emulator storage completely
✗ Run on HDD (too slow)
✗ Leave emulator running indefinitely
```


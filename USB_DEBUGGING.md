# USB Debugging - Driver & Connection Issues

## 1. USB Driver Installation

### Windows - USB Driver Setup

#### Method 1: Official Google USB Driver
```
1. Go to https://developer.android.com/studio/run/win-usb
2. Download Google USB Driver
3. Extract to: C:\Program Files (x86)\Android\android-sdk\extras\google\usb_driver\
4. Device Manager → Right-click Android device
5. Update driver → Browse to usb_driver folder
```

#### Method 2: Manufacturer Driver
```
Manufacturer drivers by brand:
- Samsung: Download from samsung.com (Kies or driver package)
- Xiaomi: Download from xiaomi.com
- Huawei: Download from huawei.com
- OnePlus: Download from oneplus.com
- Google: Built-in (usually)
```

#### Driver Installation Steps
```
1. Enable Developer Mode:
   - Settings → About Phone
   - Tap Build Number 7 times
   
2. Enable USB Debugging:
   - Settings → Developer Options
   - Toggle USB Debugging ON
   
3. Plug USB cable to computer
4. Device shows: "Allow USB Debugging?" → TAP OK
5. Install driver when prompted
6. Verify in Device Manager
```

### Linux - USB Device Setup

```bash
# 1. Add udev rules
sudo nano /etc/udev/rules.d/51-android.rules

# Add line (change VENDOR_ID & PRODUCT_ID):
SUBSYSTEM=="usb", ATTR{idVendor}=="18d1", MODE="0666"
SUBSYSTEM=="usb", ATTR{idProduct}=="4e42", MODE="0666"

# 2. Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# 3. Add user to group
sudo usermod -a -G plugdev $USER
newgrp plugdev

# 4. Reconnect device
# Disconnect and reconnect USB cable

# 5. Verify
adb devices
```

### macOS - USB Setup
```bash
# Usually no drivers needed on macOS
# Sometimes require:

# Install via Homebrew
brew install android-platform-tools

# If permission issues:
sudo killall -9 usbmuxd

# Reconnect device
adb devices
```

---

## 2. Finding USB Device IDs

### Get Vendor & Product IDs

```bash
# Linux
lsusb
# Output: Bus 001 Device 005: ID 18d1:4e42 Google Inc.
# Vendor ID: 18d1, Product ID: 4e42

lsusb -v -s 001:005
# Detailed information

# Windows (PowerShell)
Get-PnpDevice | Where-Object {$_.Name -like "*Android*"}

# macOS
system_profiler SPUSBDataType | grep -A 10 Android
```

### Common Device IDs
```
Google Pixel:        18d1:4ee0
Samsung S20:         04e8:6860
Xiaomi:              2717:1234
OnePlus:             09e8:6860
Huawei:              12d1:15c1
LG:                  1004:625e
HTC:                 0bb4:0c02
```

---

## 3. USB Connection Troubleshooting

### Device Not Showing Up

```bash
# 1. Basic checks
adb kill-server
adb start-server
adb devices

# 2. Check physical connection
lsusb  # Linux
# Device should appear

# 3. Check device mode
adb shell getprop usb.state

# 4. Manually set ADB mode
adb shell setprop sys.usb.config adb

# 5. Check permissions (Linux)
ls -la /dev/bus/usb/*/
sudo chmod 666 /dev/bus/usb/*/*

# 6. Try different USB port
# USB 2.0 port more reliable than 3.0

# 7. Try different cable
# Some cables charge-only, not data
```

### Device Offline

```bash
# Problem: "offline" in adb devices
adb devices
# emulator-5554        offline

# Solutions:
1. adb reconnect
2. adb -s emulator-5554 reconnect
3. Kill and restart server:
   adb kill-server
   adb start-server
4. Check logs:
   adb logcat | grep usb
```

### Unauthorized Device

```bash
# Problem: "unauthorized" in adb devices
adb devices
# 06050fa4c0e2d1f5       unauthorized

# Solutions:
1. Check device screen - should show "Allow USB Debugging" prompt
2. Tap Allow on device
3. If prompt doesn't appear:
   - Disconnect cable
   - Go to Settings → Apps → Uninstall all ADB apps
   - Reconnect
4. Clear authorizations:
   rm ~/.android/adbkey*
```

---

## 4. USB Debugging Mode Advanced

### USB Modes

```bash
# Check current mode
adb shell getprop usb.state

# Possible states:
adb             # ADB only
mtp             # Media Transfer Protocol
ptp             # Photo Transfer Protocol  
mtp,adb         # MTP + ADB
ptp,adb         # PTP + ADB
charging        # Charging only
```

### Switching USB Modes

```bash
# Via adb (if already connected)
adb shell setprop sys.usb.config mtp

# Via device:
# Settings → Developer Options → USB Configuration
# Or Settings → USB → Select mode

# Force ADB mode
adb shell setprop sys.usb.config adb
```

### Persistent ADB Mode
```bash
# Make ADB mode default
adb shell settings put global adb_enabled 1

# Android 6.0+: Always show MTP notification
adb shell settings put global usb_notification_enabled 1
```

---

## 5. USB Connection Diagnostics

### Detailed USB Info

```bash
# Linux - Full USB device info
sudo lsusb -v -s 001:005

# macOS - USB details
system_profiler SPUSBDataType -json

# Windows - Device Manager details
# Device Manager → Android device → Properties → Details
```

### Monitor USB Events

```bash
# Linux - Real-time USB events
sudo udevadm monitor

# When you plug/unplug, you'll see events

# macOS - Monitor USB changes
ioreg -p IOUSB -w0

# Windows - USB events
# Event Viewer → System → Filter for usb
```

### Test Connection Stability

```bash
#!/bin/bash
# usb_stability_test.sh

for i in {1..100}; do
    echo "Test $i: $(date)"
    adb devices | grep device
    
    if [ $? -ne 0 ]; then
        echo "⚠️ Connection lost!"
    fi
    
    sleep 5
done
```

---

## 6. High-Speed USB Setup

### USB 3.0 Optimization

```bash
# Use USB 3.0 ports (blue) for speed
# Speed comparison:
# USB 2.0: 480 Mbps
# USB 3.0: 5 Gbps (10x faster)

# Check USB version:
lsusb -v | grep bcdUSB

# Verify high-speed
adb shell cat /sys/kernel/debug/usb/devices | grep speed
```

### Multi-Device USB Optimization

```bash
# Connect multiple devices
adb devices

# USB hub recommended for 4+ devices
# Powered USB hub better than unpowered

# Check USB bus load
lsusb -t  # Tree view

# Balance across hubs if available
```

---

## 7. Fastboot & Bootloader USB

### Fastboot Mode Detection

```bash
# Normal mode
adb devices

# Fastboot mode
fastboot devices

# Check mode
adb shell getprop ro.bootloader

# Enter bootloader/fastboot
adb reboot bootloader
```

### USB in Bootloader Mode

```bash
# Device may need different driver in bootloader
# Windows: May need to manually select driver

# Once in bootloader:
fastboot devices

# If not showing:
# 1. Install fastboot drivers
# 2. Check USB connection
# 3. Try fastboot -u devices (unbuffered)
```

---

## 8. Cable & Connector Issues

### Common Cable Problems

```
Issues:
- Loose connection → reconnect firmly
- Damaged cable → try different cable
- Charge-only cable → need data cable
- Bent connector → replace cable
- Dirty connector → clean gently with isopropyl alcohol
```

### Cable Testing

```bash
# Test file transfer speed
time adb push 100MB_file /sdcard/

# Fast: < 30 seconds for 100MB
# Slow: > 60 seconds indicates USB issue

# Test multiple operations
for i in {1..10}; do
    adb shell getprop ro.build.version.release
done
```

---

## 9. Power Delivery Issues

### USB Power Management

```bash
# Check device charging via USB
adb shell dumpsys battery | grep -i usb

# Reduce USB power usage
adb shell settings put global usb_power_mode 1

# Monitor power:
adb shell cat /sys/class/power_supply/usb/
```

### USB Battery Drain

```bash
# If phone drains fast connected to computer:

# 1. Disable MTP
adb shell setprop sys.usb.config adb

# 2. Disable USB debugging when not needed
adb shell settings put secure adb_enabled 0

# 3. Enable battery saving
adb shell settings put global power_save_mode 1
```

---

## 10. Multi-Device USB Setup

### Connect Multiple Devices

```bash
# Via multiple USB ports
# 1. Plug device 1
adb devices

# 2. Plug device 2
adb devices

# 3. Each gets unique identifier
adb devices
# emulator-5554
# 06050fa4c0e2d1f5
# 192168l100:5555

# Run commands on specific device
adb -s 06050fa4c0e2d1f5 install app.apk
```

### USB Hub Setup

```bash
# Recommended setup for 4+ devices:
# - Powered USB 3.0 hub (provides power)
# - Each device on separate port
# - Sufficient USB bandwidth

# Check bandwidth usage
lsusb -t | grep Device
```

---

## 11. Driver Removal & Cleanup

### Windows Driver Cleanup

```
Device Manager → Right-click Android device
→ Uninstall device
→ Physically disconnect
→ Clean registry (advanced):
  HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Enum\USB
  (Find and delete android entries)
```

### Linux Driver Cleanup

```bash
# Remove udev rules
sudo rm /etc/udev/rules.d/51-android.rules

# Reload
sudo udevadm control --reload-rules

# Disconnect and reconnect
```

---

## 12. USB Debugging Logs

### Capture USB Communications

```bash
# Linux - Capture with tcpdump (if USB Ethernet)
sudo tcpdump -i eth0 -n 'port 5555 or port 16 or port 17'

# Linux - USB packet capture
sudo modprobe usbmon
sudo tcpdump -i usbmon0 -w usb_capture.pcap

# Analyze with Wireshark
wireshark usb_capture.pcap
```

### ADB Debug Logs

```bash
# Enable verbose ADB logging
ANDROID_LOG_TAGS="*:V" adb logcat
adb logcat | grep usb

# Server logs
adb -v devices  # Verbose mode shows connection attempts
```

---

## 13. USB Device Properties

### Get Device USB Info

```bash
# Manufacturer
adb shell getprop ro.product.manufacturer

# Model
adb shell getprop ro.product.model

# Serial number
adb shell getprop ro.serialno

# USB config
adb shell getprop sys.usb.config

# USB state
adb shell getprop usb.state
```

---

## 14. Common USB Error Codes

```
Windows:
- Code 10: Device cannot start
  Fix: Update/reinstall driver
  
- Code 14: Device cannot be started
  Fix: Remove and reinstall device
  
- Code 28: No compatible drivers
  Fix: Install correct driver

Linux:
- "Permission denied"
  Fix: Add to plugdev group
  
- "usb_device not found"
  Fix: Check udev rules
```

---

## 15. USB Debugging Best Practices

```
DO:
✓ Use original USB cables
✓ Use powered USB hubs for multiple devices
✓ Keep drivers updated
✓ Enable USB Debugging on device
✓ Test connection before deployment
✓ Monitor USB load with many devices

DON'T:
✗ Use charge-only cables
✗ Plug into unpowered hubs with many devices
✗ Use damaged or bent connectors
✗ Leave USB Debugging on unnecessarily
✗ Mix different USB versions on same hub
✗ Ignore "Unauthorized" warnings
```


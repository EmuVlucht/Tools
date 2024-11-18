# ADB Quick Reference Card

## Most Used Commands (Cheat Sheet)

### Device Management
```
adb devices                           # List connected devices
adb connect IP:5555                   # Connect via WiFi
adb disconnect IP:5555                # Disconnect device
adb -s DEVICE_ID COMMAND              # Execute on specific device
adb usb                               # Revert to USB connection
adb kill-server                       # Stop ADB server
adb start-server                      # Start ADB server
```

### Application Installation
```
adb install app.apk                   # Install application
adb install -r app.apk                # Replace existing app
adb uninstall package.name            # Uninstall application
adb shell am start -n package/.Activity  # Launch activity
adb shell pm list packages            # List installed apps
adb shell pm list packages -3         # List third-party apps
```

### File Transfer
```
adb push local_file /sdcard/          # Send file to device
adb pull /sdcard/file ./              # Get file from device
adb shell ls /sdcard/                 # List directory contents
adb shell rm /sdcard/file.txt         # Delete file
```

### Logging & Debugging
```
adb logcat                            # View system logs
adb logcat -c                         # Clear log buffer
adb logcat *:E                        # Show only errors
adb logcat | grep "TAG"               # Filter logs
adb logcat > log.txt                  # Save logs to file
adb shell dumpsys                     # System information
```

### Monitoring
```
adb shell top                         # CPU/Memory usage
adb shell df -h                       # Disk space
adb shell dumpsys battery             # Battery info
adb shell ps                          # Running processes
adb shell dumpsys meminfo             # Memory details
```

### Control
```
adb shell screencap -p /sdcard/ss.png     # Screenshot
adb shell screenrecord /sdcard/video.mp4  # Record screen
adb shell input tap 500 500               # Tap screen
adb shell input text "Hello"              # Type text
adb reboot                                # Restart device
adb shell input keyevent 4                # Press back button
```

### Port Forwarding
```
adb forward tcp:8000 tcp:8000        # Forward port
adb forward --list                   # List forwards
adb forward --remove tcp:8000        # Remove forward
adb reverse tcp:8000 tcp:8000        # Reverse forward
```

### Backup
```
adb backup -all -f backup.ab         # Full backup
adb restore backup.ab                # Restore backup
adb backup -all -noapk -f data.ab    # Backup data only
```

---

## One-Liners (Copy & Paste Ready)

```bash
# Get Android version
adb shell getprop ro.build.version.release

# Get device model
adb shell getprop ro.product.model

# Get device ID
adb shell settings get secure android_id

# Connect via IP (replace IP address)
adb connect 192.168.1.100:5555

# Take screenshot to Desktop
adb shell screencap -p /sdcard/screenshot.png && adb pull /sdcard/screenshot.png ~/Desktop/

# Clear app cache
adb shell pm clear com.example.app

# Enable USB debugging programmatically
adb shell settings put global adb_enabled 1

# Get full device info
adb shell getprop | grep ro.product

# List all packages with size
adb shell pm list packages -3 && adb shell du -sh /data/app/*/

# Monitor app's memory real-time
watch -n 1 "adb shell dumpsys meminfo com.example.app"

# Extract apk from device
adb shell pm path com.example.app && adb pull /data/app/com.example.app/...

# Kill all ADB processes
killall adb

# See device's ADB version
adb shell "getprop ro.debuggable"
```

---

## Keyboard Key Events

```
3   = HOME
4   = BACK
5   = CALL
6   = ENDCALL
24  = VOLUME_UP
25  = VOLUME_DOWN
26  = POWER
27  = CAMERA
66  = ENTER
67  = DEL
82  = MENU
122 = MOVE_HOME
123 = MOVE_END
```

---

## Common Package Names

```
com.android.settings          # Settings
com.android.chrome            # Chrome Browser
com.google.android.gms        # Google Play Services
com.google.android.apps.maps  # Google Maps
com.instagram.android         # Instagram
com.whatsapp                  # WhatsApp
com.facebook.katana           # Facebook
com.spotify.music             # Spotify
com.netflix.mediaclient       # Netflix
```

---

## Useful Aliases (Linux/Mac)

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# Device shortcuts
alias adb-devices="adb devices"
alias adb-connect="adb connect"
alias adb-install="adb install"
alias adb-uninstall="adb uninstall"
alias adb-logcat="adb logcat"
alias adb-shell="adb shell"
alias adb-ss="adb shell screencap -p /sdcard/ss.png && adb pull /sdcard/ss.png ~/"

# Common operations
alias android-version="adb shell getprop ro.build.version.release"
alias android-model="adb shell getprop ro.product.model"
alias android-id="adb shell settings get secure android_id"
alias device-info="adb shell getprop | grep ro.product"
```

---

## File Paths Reference

```
/sdcard/                    # User storage
/data/                      # App data directory
/data/app/                  # Installed apps
/data/data/APP_PACKAGE/     # App private data
/system/                    # System files
/cache/                     # Cache directory
/data/anr/                  # ANR (crash) logs
/data/tombstones/           # Native crash data
/dev/                       # Device files
/proc/                      # Process info
/sys/                       # System info
```

---

## Common Settings Commands

```bash
# Screen brightness (0-255)
adb shell settings put system screen_brightness 200

# Screen timeout (milliseconds)
adb shell settings put system screen_off_timeout 300000

# Developer mode
adb shell settings put secure development_settings_enabled 1

# Airplane mode on
adb shell settings put global airplane_mode_on 1

# WiFi power saving
adb shell settings put global wifi_sleep_policy 2

# USB debugging
adb shell settings put global adb_enabled 1

# Stay awake while charging
adb shell settings put global stay_on_while_plugged_in 7
```

---

## Troubleshooting Quick Fixes

```bash
# Device not found
adb kill-server && adb start-server && adb devices

# Permission denied
sudo adb devices  # or add user to plugdev group

# Connection refused
adb connect 192.168.1.100:5555

# Device offline
adb usb
adb devices

# Daemon unresponsive
adb kill-server
adb start-server

# Check ADB version
adb version

# Restart device
adb reboot

# Reboot to recovery
adb reboot recovery

# Reboot to bootloader
adb reboot bootloader
```

---

## Performance Monitoring

```bash
# Real-time performance
adb shell top -m 5 -n 1

# Memory usage (megabytes)
adb shell dumpsys meminfo | grep TOTAL

# Battery percentage
adb shell dumpsys battery | grep level

# CPU temperature
adb shell cat /sys/class/thermal/thermal_zone0/temp

# Network stats
adb shell dumpsys netstats

# Storage usage
adb shell df -h /sdcard/

# App memory usage
adb shell dumpsys meminfo com.example.app
```

---

## Regex Patterns for Logcat

```bash
# Only crashes
adb logcat | grep -E "FATAL|crash|Exception"

# Specific app
adb logcat | grep "com.example"

# Error and warnings
adb logcat | grep -E "[EW]/"

# ANR (Application Not Responding)
adb logcat | grep "ANR"

# Multiple filters
adb logcat | grep -E "error|fail|warning"
```

---

## Multiple Devices Workflow

```bash
# List all devices with more info
adb devices -l

# Install on all devices
for device in $(adb devices | grep device | awk '{print $1}'); do
    adb -s $device install app.apk
done

# Execute on specific device
adb -s emulator-5554 logcat
adb -s 192.168.1.100:5555 shell ls

# Broadcast to all
adb shell am broadcast -a ACTION
```

---

## Emergency Commands

```bash
# Force stop app
adb shell am force-stop com.example.app

# Clear app data
adb shell pm clear com.example.app

# Disable app
adb shell pm disable com.example.app

# Enable app
adb shell pm enable com.example.app

# Grant permission
adb shell pm grant com.example.app android.permission.CAMERA

# Revoke permission
adb shell pm revoke com.example.app android.permission.CAMERA

# Set default launcher
adb shell cmd package set-home-activity com.example.app/.MainActivity
```

---

## Version Info

| Component | Get Command |
|-----------|------------|
| ADB Version | `adb version` |
| Android OS | `adb shell getprop ro.build.version.release` |
| Android API | `adb shell getprop ro.build.version.sdk` |
| Device Model | `adb shell getprop ro.product.model` |
| Device Brand | `adb shell getprop ro.product.brand` |
| Kernel Version | `adb shell uname -a` |
| Build Date | `adb shell getprop ro.build.date` |
| Security Patch | `adb shell getprop ro.build.version.security_patch` |
| CPU ABI | `adb shell getprop ro.product.cpu.abi` |


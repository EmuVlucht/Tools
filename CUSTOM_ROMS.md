# Custom ROMs Installation & Management via ADB

## 1. Preparation for ROM Installation

### Prerequisites Checklist
```bash
# 1. Unlock bootloader
adb reboot bootloader
fastboot flashing unlock

# 2. Install custom recovery
fastboot flash recovery recovery.img

# 3. Verify device
adb devices

# 4. Backup data
adb backup -apk -shared -all -f backup.ab

# 5. Download ROM
# Download from: LineageOS, AICP, Resurrection Remix, etc.
```

### File Structure
```
Expected ROM files:
custom_rom_v1.0.zip
├── META-INF/
├── system/
├── boot.img
├── build.prop
└── flash-script.sh
```

---

## 2. ROM Installation Methods

### Method 1: Via Custom Recovery (TWRP)
```bash
# 1. Push ROM to device
adb push LineageOS-20.zip /sdcard/

# 2. Reboot to recovery
adb reboot recovery

# 3. In TWRP:
# - Select "Install"
# - Navigate to LineageOS-20.zip
# - Swipe to install
# - Wipe cache/dalvik (optional)
# - Reboot
```

### Method 2: Via ADB Sideload
```bash
# 1. Boot to recovery
adb reboot recovery

# 2. Select "Apply update from ADB"

# 3. From computer
adb sideload LineageOS-20.zip

# Device installs and reboots
```

### Method 3: Fastboot Flash
```bash
adb reboot bootloader

# Flash system partition
fastboot flash system system.img

# Flash boot
fastboot flash boot boot.img

fastboot reboot
```

---

## 3. Wipe Before Installation

### Factory Reset
```bash
# Via ADB (if device boots)
adb shell wipe data

# Via recovery
adb reboot recovery
# In TWRP: Wipe → Factory Reset → Swipe

# Via fastboot
adb reboot bootloader
fastboot -w reboot
```

### Selective Wipe
```bash
# Keep files on sdcard, wipe app data
adb reboot recovery
# In TWRP: Wipe → Advanced Wipe
# Select: Data, Cache (NOT sdcard)
```

---

## 4. Popular Custom ROMs

### LineageOS
```bash
# Download from lineageos.org
# For device: Find your exact model

adb reboot recovery
# Install ROM via TWRP
# First boot takes 5-10 minutes
```

### AICP (Android Ice Cold Project)
```bash
# Download from aicp-rom.com
adb reboot recovery
# Follow TWRP installation
```

### Resurrection Remix
```bash
# Download from resurrectionremix.com
adb reboot recovery
# Install via TWRP
```

### Pixel Experience
```bash
# Download from pixelexperience.org
# Usually includes latest Android features
adb reboot recovery
```

---

## 5. GApps Installation

### Flash GApps
```bash
# GApps package (Google apps)
# Download from opengapps.org

# After ROM install, don't reboot yet
adb shell
# In recovery terminal:

# 1. Flash GApps
cd /sdcard
unzip opengapps_arm64.zip
# Follow installation script

# Or via recovery UI:
# Install opengapps_arm64.zip
```

### GApps Variants
```
Sizes (largest to smallest):
- Super: All Google apps (1GB+)
- Stock: Standard Google apps (500MB)
- Minimal: Just core Google apps (100MB)
- Pico: Very minimal (50MB)
```

---

## 6. Verification After Installation

### Check ROM Version
```bash
adb shell getprop ro.build.version.release

adb shell getprop ro.build.fingerprint

adb shell cat /system/build.prop | grep ro.build.version
```

### Verify Installation Success
```bash
# Boot to system takes time (first boot)
# Wait 10+ minutes

# Check if device boots
adb devices

# Boot time tracking
adb shell date
```

### Check Functions
```bash
# Camera works
adb shell am start -n com.android.camera/.CameraActivity

# Settings available
adb shell am start -n com.android.settings/.Settings

# Phone app works
adb shell am start -n com.android.phone/.PhoneApp
```

---

## 7. Troubleshooting ROM Issues

### ROM Won't Boot
```bash
# Solution: Wipe again and reflash

# 1. Reboot to recovery
adb reboot recovery

# 2. Full wipe
# TWRP: Wipe → Advanced Wipe
# Select: System, Data, Cache, Dalvik

# 3. Reflash ROM
# Install → ROM zip

# 4. Reboot
```

### Bootloop
```bash
# Infinite reboot loop fix

adb reboot recovery

# Check recovery logs
adb logcat | grep -i "error\|fail"

# Try:
1. Wipe cache only
2. Reflash ROM
3. Verify ROM is for correct device

# If persists: Restore backup
adb restore backup.ab
```

### App Crashes
```bash
# Check app logs
adb logcat | grep -i "crash"

# Clear app cache
adb shell pm clear app_package_name

# Reinstall apps
adb shell pm install app.apk
```

---

## 8. Rolling Back to Stock ROM

### Restore Original ROM
```bash
# Option 1: Use factory image
./flash-all.sh

# Option 2: Manual flash
adb reboot bootloader
fastboot flash system original_system.img
fastboot flash boot boot.img
fastboot flash userdata userdata.img
fastboot reboot

# Option 3: From backup
adb restore backup.ab
```

---

## 9. ROM Customization

### Modify ROM Before Installation
```bash
# Extract ROM
unzip -q LineageOS-20.zip -d rom_extracted/

# Modify files
cd rom_extracted/system/
# Edit system files

# Repackage
zip -r -q ../LineageOS-20-modified.zip *

# Install modified ROM
adb sideload LineageOS-20-modified.zip
```

### Add Custom Mods
```bash
# TWRP magisk modules
adb push magisk_module.zip /sdcard/

adb reboot recovery
# Install magisk_module.zip via TWRP
```

---

## 10. Multi-ROM Management

### Maintain Multiple ROMs
```bash
# Storage organization
/sdcard/ROMs/
├── LineageOS-20.zip
├── AICP.zip
├── Pixel-Experience.zip
└── Backups/
    ├── stock_backup.ab
    └── lineage_backup.ab

# Easy switching
adb push /sdcard/ROMs/AICP.zip /sdcard/
adb reboot recovery
```

---

## 11. Performance Optimization After ROM Install

### Clean Installation
```bash
# After ROM install
adb shell pm clear --cache com.android.systemui

# Optimize database
adb shell cmd package optimize-profiles all

# Clear cache
adb shell rm -rf /cache/*
```

### System Optimization
```bash
# Enable zram if supported
adb shell echo 1 > /sys/module/zswap/parameters/enabled

# Adjust animation speeds
adb shell settings put global window_animation_scale 0.5

# Optimize app startup
adb shell cmd package compile --mode=speed com.app.name
```

---

## 12. Common ROM Issues & Fixes

### WiFi Not Working
```bash
# Solution: Flash WiFi firmware again

adb reboot recovery
# Reflash ROM (WiFi drivers included)

# If persists:
adb shell wpa_cli status
adb shell settings put global wifi_on 1
```

### Bluetooth Issues
```bash
# Reset bluetooth
adb shell settings put global bluetooth_on 0
sleep 2
adb shell settings put global bluetooth_on 1

# Clear bluetooth cache
adb shell pm clear com.android.bluetooth
adb shell pm clear com.android.systemui
```

### Charging Issues
```bash
# Check battery
adb shell dumpsys battery

# Verify USB port
adb shell getprop ro.usb.state

# Force restart charging
adb shell settings put global usb_power_mode 1
```

---

## 13. ROM Comparison

```
ROM Comparison:

LineageOS:
+ Most stable, long-term support
+ Regular security updates
+ Minimal modifications
- Less features than others

AICP:
+ Feature-rich
+ Regular updates
- Can be less stable sometimes

Pixel Experience:
+ Closest to stock Google Android
+ Latest features
- May not have all customizations

Resurrection Remix:
+ Highly customizable
+ Performance-tuned
- More modifications = more potential issues
```

---

## 14. Post-Installation Setup

### First Boot Setup
```bash
# First boot takes 10-20 minutes (let it complete)
# Wait for "Welcome to LineageOS" screen

# Complete setup wizard
adb shell am start -n com.google.android.setupwizard/.SetupWizardActivity
```

### Install Essential Apps
```bash
# After ROM installation
adb shell pm install GApps.apk
adb shell pm install MagiskManager.apk
adb shell pm install Xposed.apk

# Update system
adb shell pm update -all
```

---

## 15. Backup Before ROM Install

### Create System Backup
```bash
# ADB backup
adb backup -apk -shared -all -f full_backup.ab

# Via TWRP
adb reboot recovery
# TWRP: Backup → Select all → Backup

# Via fastboot (partition backup)
adb reboot bootloader
fastboot dump system > system_backup.img
fastboot dump data > data_backup.img
```

### Restore From Backup
```bash
# From ADB backup
adb restore full_backup.ab

# From TWRP
adb reboot recovery
# TWRP: Restore → Select backup → Restore

# From fastboot backup
adb reboot bootloader
fastboot flash system system_backup.img
fastboot reboot
```


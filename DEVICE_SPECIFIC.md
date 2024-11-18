# Device-Specific ADB Configurations

## 1. Google Pixel

### Pixel Setup
```bash
# Enable Developer Mode
Settings → About Phone → Tap Build Number 7x

# Enable USB Debugging
Settings → System → Developer Options → USB Debugging

# Factory images for Pixel
# Download from https://developers.google.com/android/images

# Flash factory image
cd extracted_factory_image
./flash-all.sh
```

### Pixel Specific Features
```bash
# Access Pixel exclusive features
adb shell getprop ro.product.model

# Pixel 6/7 Tensor chip
adb shell getprop ro.soc.model

# Bootloader unlock
adb reboot bootloader
fastboot flashing unlock
```

---

## 2. Samsung Devices

### Samsung USB Drivers
```bash
# Windows: Install Samsung USB Drivers
# Download from https://developer.samsung.com/

# Enable Developer Mode
Settings → About Phone → Tap Build Number 7x

# Enable USB Debugging
Settings → Developer Options → USB Debugging

# Set USB mode to MTP
Settings → USB → Select mode
```

### Samsung Commands
```bash
# Knox Security
adb shell getprop ro.boot.knox_patch

# Samsung specific properties
adb shell getprop ro.product.manufacturer  # Samsung

# Disable Knox warnings
adb shell settings put global update_service_use_firewall 0

# Samsung ADB settings
adb shell settings put global adb_enabled 1
```

### Galaxy S Series Specific
```bash
# S23 specific
adb shell getprop ro.product.model
# Output: SM-S911B (S23), SM-S918B (S23+), etc.

# Device codename
adb shell getprop ro.product.device

# Firmware version
adb shell getprop ro.build.version.release
```

---

## 3. Xiaomi Devices

### Xiaomi Setup
```bash
# Enable Developer Mode
Settings → About Phone → Tap MIUI Version 7x

# Enable USB Debugging
Settings → Additional Settings → Developer Options → USB Debugging

# MiUSB Tool (optional)
# Download: https://www.miui.com/
```

### Xiaomi Specific
```bash
# Manufacturer
adb shell getprop ro.product.manufacturer  # Xiaomi

# MIUI Version
adb shell getprop ro.build.version.incremental

# Device model
adb shell getprop ro.product.model  # Redmi, Poco, Mi, etc.

# Unlock bootloader
# Need to unlock via Mi Account
```

---

## 4. OnePlus Devices

### OnePlus Setup
```bash
# Enable Developer Mode
Settings → About Phone → Tap Build Number 7x

# Enable USB Debugging
Settings → System Settings → Developer Options → USB Debugging

# OxygenOS features
adb shell getprop ro.os.version  # OxygenOS 13.x etc.
```

### OnePlus Bootloader
```bash
# OnePlus allows bootloader unlock relatively easily
adb reboot bootloader
fastboot flashing unlock
# May require OTP verification
```

---

## 5. Huawei Devices

### Huawei Setup
```bash
# Enable Developer Mode
Settings → About Phone → Tap Build Number 7x

# Enable USB Debugging
Settings → System → Developer Options → USB Debugging

# Note: Huawei devices may have limited ADB access in some regions
```

### Huawei Specific
```bash
# EMUI Version
adb shell getprop ro.build.version.emui

# Huawei security
adb shell getprop ro.boot.baseband  # Baseband info

# HarmonyOS compatibility
adb shell getprop ro.os.version
```

---

## 6. LG Devices

### LG Setup
```bash
# Enable Developer Mode
Settings → About Phone → Tap Build Number 7x

# Enable USB Debugging
Settings → Developer Options → USB Debugging

# LG software
adb shell getprop ro.lge.swversion
```

---

## 7. HTC Devices

### HTC Setup
```bash
# Enable Developer Mode
Settings → About → Tap Build Number 7x

# Enable USB Debugging
Settings → Developer Options → USB Debugging

# HTC unlock via htcdev.com
# Requires device unlock code
```

---

## 8. Motorola/Moto Devices

### Motorola Setup
```bash
# Enable Developer Mode
Settings → About Phone → Tap Build Number 7x

# Enable USB Debugging
Settings → System → Developer Options → USB Debugging

# Motorola specific
adb shell getprop ro.product.brand  # motorola
```

---

## 9. Sony/Xperia Devices

### Sony Setup
```bash
# Enable Developer Mode
Settings → About → Tap Build Number 7x

# Enable USB Debugging
Settings → Developer → USB Debugging

# Xperia specific
adb shell getprop ro.product.manufacturer  # Sony

# Android One certification
adb shell getprop ro.com.google.clientidbase
```

---

## 10. Tablets (iPad, Samsung Tab)

### Tablet Detection
```bash
# Detect if tablet
adb shell getprop ro.com.google.gmsversion

# Check screen size
adb shell getprop ro.screenSize

# Aspect ratio
adb shell getprop ro.screenAspectRatio
```

### Tablet Specific Commands
```bash
# Larger screen management
adb shell settings put global window_animation_scale 1

# Split screen
adb shell am force-stop com.android.systemui

# Multi-window
adb shell settings put global development_enable_multi_window 1
```

---

## 11. Foldable Devices

### Samsung Galaxy Fold/Z Series
```bash
# Detect foldable
adb shell getprop ro.hardware.keystore

# Fold state detection
adb shell dumpsys sensorservice | grep -i fold

# Multi-display support
adb shell getprop ro.opengles.version
```

---

## 12. Gaming Devices (ROG, Black Shark, etc.)

### Gaming Phone Specific
```bash
# ASUS ROG Phone
adb shell getprop ro.product.model  # Asus

# Performance mode
adb shell settings put secure performance_profile 2

# Cooling system
adb shell dumpsys thermalmanager
```

---

## 13. Budget Devices (Android Go)

### Android Go Configuration
```bash
# Check if Android Go
adb shell getprop ro.build.characteristics

# Limited RAM (typically 1-2GB)
adb shell cat /proc/meminfo | grep MemTotal

# Lite apps
adb shell pm list packages | grep lite
```

---

## 14. Device Detection Script

```bash
#!/bin/bash
# device_info.sh

echo "=== Device Information ==="
echo "Manufacturer: $(adb shell getprop ro.product.manufacturer)"
echo "Model: $(adb shell getprop ro.product.model)"
echo "Device: $(adb shell getprop ro.product.device)"
echo "Android Version: $(adb shell getprop ro.build.version.release)"
echo "API Level: $(adb shell getprop ro.build.version.sdk)"
echo "Build Type: $(adb shell getprop ro.build.type)"
echo "CPU ABI: $(adb shell getprop ro.product.cpu.abi)"
echo "RAM: $(adb shell cat /proc/meminfo | grep MemTotal)"
echo ""
echo "Bootloader Locked: $(adb shell getprop ro.boot.secure)"
echo "Developer Mode: $(adb shell getprop persist.sys.usb.debug)"
```

---

## 15. Regional Variants

### China Region
```bash
# Chinese device
adb shell getprop persist.sys.locale  # zh_CN

# Chinese ROM
adb shell getprop ro.rom.zone  # China

# Limited services
adb shell settings get global gms_enabled
```

### India Region
```bash
# India specific properties
adb shell getprop persist.sys.locale  # en_IN

# Regulatory info
adb shell getprop ro.carrier  # India carriers
```

### US/International
```bash
# US carrier specific
adb shell getprop ro.carrier  # Verizon, AT&T, etc.

# Different firmware variants
adb shell getprop ro.build.fingerprint
```


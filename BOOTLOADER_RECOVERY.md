# Bootloader & Recovery Mode via ADB

## 1. Bootloader Access

### Enter Bootloader Mode
```bash
# Reboot to bootloader
adb reboot bootloader

# Device shows bootloader menu
# Display: fastboot mode (USB)

# Fastboot commands work now
fastboot devices
```

### Bootloader Information
```bash
# Get bootloader version
adb shell getprop ro.bootloader

# Get bootloader commands (in bootloader mode)
fastboot getvar all

# Lock status
fastboot getvar locked
# Output: locked or unlocked
```

### Unlock Bootloader
```bash
# WARNING: Erases all data!

# Reboot to bootloader
adb reboot bootloader

# Unlock (ERASES device)
fastboot flashing unlock

# Device shows confirmation
# Use volume keys to select YES
# Press power to confirm

# Device erases and reboots
```

### Lock Bootloader
```bash
# Reboot to bootloader
adb reboot bootloader

# Lock bootloader
fastboot flashing lock

# Requires confirmation
```

---

## 2. Recovery Mode

### Enter Recovery Mode
```bash
# Reboot to recovery
adb reboot recovery

# Shows recovery menu
# Options: reboot, wipe cache, etc.
```

### Recovery Mode Navigation
```
Recovery Menu typically shows:
- Reboot system now
- Reboot to bootloader
- Wipe data/factory reset
- Wipe cache partition
- Apply update from ADB
- Apply update from SD card
- View recovery logs
- Power off
```

### Sideload from Recovery
```bash
# 1. Boot to recovery
adb reboot recovery

# 2. Select "Apply update from ADB"
# (Use volume keys to navigate, power to select)

# 3. From computer:
adb sideload update.zip

# Updates device from ZIP file
```

---

## 3. Flash Partitions

### Flash Boot Partition
```bash
# Reboot to bootloader
adb reboot bootloader

# Flash boot image
fastboot flash boot boot.img

# Verify
fastboot getvar boot_version

# Reboot
fastboot reboot
```

### Flash System Partition
```bash
adb reboot bootloader

# Flash system image
fastboot flash system system.img

# For large images (may timeout)
fastboot --slot=all flash system system.img

fastboot reboot
```

### Flash Multiple Partitions
```bash
adb reboot bootloader

# Flash all necessary partitions
fastboot flash bootloader bootloader.img
fastboot flash radio radio.img
fastboot flash boot boot.img
fastboot flash system system.img

# If supported:
fastboot flash vendor vendor.img

fastboot reboot
```

---

## 4. Factory Images

### Flash Factory Image
```bash
# Download factory image from Google (Pixels)
# Extract ZIP

# Run included flash script
cd extracted_factory_image/
./flash-all.sh

# Or manually:
adb reboot bootloader
fastboot flash bootloader bootloader.img
fastboot flash radio radio.img
fastboot flash system system.img
fastboot flash userdata userdata.img
fastboot reboot
```

---

## 5. Custom Recovery

### Install Custom Recovery
```bash
# Prerequisites: Bootloader unlocked

adb reboot bootloader

# Flash custom recovery (TWRP, CWM)
fastboot flash recovery recovery.img

# Verify
fastboot getvar recovery_version

fastboot reboot

# Boot to custom recovery
adb reboot recovery
```

### Boot Custom Recovery Without Installing
```bash
# Temporary boot (doesn't install)
adb reboot bootloader

fastboot boot recovery.img

# Custom recovery boots temporarily
# Doesn't persist after reboot
```

---

## 6. ROM Flashing

### Flash Custom ROM via Recovery
```bash
# 1. Boot to recovery
adb reboot recovery

# 2. Connect via ADB (in recovery)
adb devices
# Should show recovery device

# 3. Push ROM
adb push custom_rom.zip /sdcard/

# 4. In recovery menu:
# - Select "Install"
# - Choose custom_rom.zip
# - Swipe to install
# - Reboot
```

### Flash via ADB Sideload
```bash
# 1. Boot to recovery
adb reboot recovery

# 2. Select "Apply update from ADB"

# 3. From computer:
adb sideload custom_rom.zip

# ROM flashes and device reboots
```

---

## 7. Partition Management

### List Partitions
```bash
adb shell ls -la /dev/block/by-name/

# Shows all partition mappings
```

### Partition Info
```bash
# In bootloader mode
fastboot getvar partition-type:system
fastboot getvar partition-size:system

# From ADB shell
adb shell cat /proc/partitions

adb shell dumpsys block_manager
```

### Resize Partitions (Advanced)
```bash
# WARNING: Very risky!

# Requires unlocked bootloader and custom recovery

# In TWRP recovery terminal:
adb shell

# List partitions
parted /dev/block/mmcblk0 print

# Resize (example)
parted /dev/block/mmcblk0 resizepart 15 +5GB
```

---

## 8. Backup & Restore Partitions

### Backup Boot Partition
```bash
adb shell su -c "dd if=/dev/block/by-name/boot of=/sdcard/boot.img"

adb pull /sdcard/boot.img
```

### Backup All Partitions
```bash
#!/bin/bash
# backup_all_partitions.sh

adb shell su -c "ls /dev/block/by-name/" | while read partition; do
    echo "Backing up $partition..."
    adb shell su -c "dd if=/dev/block/by-name/$partition of=/sdcard/backup_$partition.img"
done

adb pull /sdcard/backup_*.img ./
```

### Restore Partition
```bash
adb push boot_backup.img /sdcard/

adb shell su -c "dd if=/sdcard/boot_backup.img of=/dev/block/by-name/boot"
```

---

## 9. Fastboot Commands

### Common Fastboot Operations
```bash
# Device list
fastboot devices

# Reboot
fastboot reboot
fastboot reboot-bootloader

# Power off
fastboot poweroff

# Flash image
fastboot flash partition_name image.img

# Erase partition
fastboot erase partition_name

# Lock/Unlock
fastboot flashing lock
fastboot flashing unlock

# Get variables
fastboot getvar all
fastboot getvar product
fastboot getvar serialno

# Set variables (some devices)
fastboot oem unlock
fastboot oem lock
```

---

## 10. Fastboot Troubleshooting

### Device Not Recognized in Bootloader
```bash
# Windows: Install fastboot drivers
# Settings → Developer Options → USB Configuration
# Select "Fastboot"

# Linux: udev rules
sudo nano /etc/udev/rules.d/51-android.rules
# Add fastboot vendor IDs

# Reload
sudo udevadm control --reload-rules
```

### Fastboot Timeout
```bash
# Issue: Fastboot command hangs

# Solutions:
1. Try different USB port
2. Try different USB cable
3. adb kill-server && adb start-server
4. fastboot --version (verify installation)
5. Restart bootloader:
   adb reboot bootloader
```

### Flash Failures
```bash
# Common error: "cannot load kernel"
# Solution: Ensure image format is correct

# Check image type:
file boot.img

# Should be: Android bootimg

# Verify device:
fastboot devices

# Check space:
fastboot getvar partition-size:boot
```

---

## 11. Advanced Bootloader Features

### A/B Bootloader Slots
```bash
# Some devices have A/B slots for OTA

# Check slots
fastboot getvar has-slot:system

# Flash to specific slot
fastboot --slot=a flash system system.img
fastboot --slot=b flash system system.img

# Set active slot
fastboot set_active a
```

### Secure Boot
```bash
# Check secure boot status
adb shell getprop ro.secure

# Verify boot partition
fastboot getvar secure
# Output: yes or no

# Disable secure boot (if supported and unlocked)
# Usually requires manufacturer unlock codes
```

---

## 12. Emergency Boot

### Force Reboot
```bash
# Infinite reboot loop fix
adb reboot bootloader

# Flash working boot image
fastboot flash boot boot_backup.img

fastboot reboot
```

### Recovery from Soft Brick
```bash
# 1. Boot to bootloader
# If device won't boot: Press power+volume down until bootloader

# 2. In bootloader
fastboot devices

# 3. Flash working images
fastboot flash system system.img
fastboot flash boot boot.img

fastboot reboot
```

### Hard Brick Recovery
```bash
# If fastboot doesn't work:
1. Connect with JTAG/EDL device (extreme case)
2. Contact manufacturer support
3. May require factory reset at service center

# EDL Mode (Some Qualcomm devices)
# Hold power+volume down+volume up
# Try: fastboot -c "oem edl"
```

---

## 13. Bootloader Serial Number

### View Bootloader Serial
```bash
adb shell getprop ro.serialno

# Or in bootloader:
adb reboot bootloader
fastboot getvar serialno
```

### Unlock Codes (Some Devices)
```bash
# Some manufacturers require unlock codes
# Example: HTC, some Sony devices

# Typically obtained from:
1. Manufacturer website (with serial number)
2. htcdev.com (for HTC)
3. Unlock apps from PlayStore
```

---

## 14. Verification

### Verify Flashed Image
```bash
# After flashing, verify partition
adb shell su -c "dd if=/dev/block/by-name/boot of=/sdcard/verify.img"

adb pull /sdcard/verify.img

# Compare with original
diff boot.img verify.img
```

### Checksum Verification
```bash
# Before flashing
md5sum boot.img
# Output: abc123def456

# After flashing, verify
adb shell su -c "md5sum /dev/block/by-name/boot"
# Should match

# Store checksums
echo "boot.img: abc123def456" > checksums.txt
```

---

## 15. Safety Best Practices

```
BEFORE FLASHING:
✓ Backup everything
✓ Verify file integrity (checksums)
✓ Read all instructions
✓ Ensure battery > 80%
✓ Test on non-critical device first
✓ Have recovery image available
✓ Disable antivirus if it interferes

DURING FLASHING:
✓ Don't disconnect USB cable
✓ Don't turn off device
✓ Don't close terminal
✓ Monitor for errors
✓ Be patient - some flashing takes time

AFTER FLASHING:
✓ Verify device boots
✓ Check all functions
✓ Re-enable security features
✓ Restore data from backup
✓ Update apps from PlayStore

NEVER:
✗ Flash wrong image for device
✗ Skip firmware flashing
✗ Skip checksum verification
✗ Flash without backup
✗ Experiment with bootloader
```


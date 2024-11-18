# Advanced ADB on Rooted Devices

## 1. Root Access via ADB

### Root Remounting

```bash
# Check if rooted
adb shell su -c "id"

# If successful output: uid=0(root) gid=0(root)

# Remount /system as writable
adb shell su -c "mount -o rw,remount /system"

# Verify writable
adb shell su -c "touch /system/test.txt"
adb shell su -c "rm /system/test.txt"
```

### Root Shell Access

```bash
# Interactive root shell
adb shell su

# Non-interactive root command
adb shell su -c "command here"

# Example:
adb shell su -c "cat /data/system/packages.xml"

# Multiple commands
adb shell su -c "mount -o rw,remount /system && echo 'Done'"
```

---

## 2. System File Modifications

### Edit System Files

```bash
# Pull system file
adb pull /system/build.prop

# Edit locally
# (Modify build.prop with text editor)

# Remount as writable
adb shell su -c "mount -o rw,remount /system"

# Push back
adb push build.prop /system/

# Set permissions
adb shell su -c "chmod 644 /system/build.prop"
adb shell su -c "chown root:root /system/build.prop"
```

### Modify System Properties

```bash
# Persistent property modification
adb shell su -c "setprop ro.build.version.release 12"

# Verify (may not persist after reboot without proper setup)
adb shell getprop ro.build.version.release

# For persistent changes, edit build.prop:
adb shell su -c "echo 'ro.build.version.release=12' >> /system/build.prop"
```

---

## 3. Remove System Apps

### Uninstall System Applications

```bash
# List system apps
adb shell pm list packages -s

# Remove system app
adb shell su -c "pm uninstall -k --user 0 com.facebook.katana"

# Or delete APK directly
adb shell su -c "rm /system/app/Facebook/Facebook.apk"

# Remove bloatware
adb shell su -c "rm /system/app/ChromeHome/*"
adb shell su -c "rm /system/priv-app/PermissionController/*"
```

### Reinstall Removed System Apps

```bash
# If you need to restore:
# System apps stored in backups usually

# Or use:
adb shell pm install-existing com.facebook.katana
```

---

## 4. Access Protected Data

### Protected Directory Access

```bash
# Access /data directories (normally restricted)
adb shell su -c "ls -la /data/data/"

# Pull protected app data
adb shell su -c "cat /data/data/com.example.app/databases/app.db" > app.db

# Pull shared preferences
adb shell su -c "cat /data/data/com.example.app/shared_prefs/config.xml"
```

### System Database Access

```bash
# Access system databases
adb shell su -c "sqlite3 /data/system/packages.xml"

# Export database
adb shell su -c "sqlite3 /data/system/locksettings.db '.dump'" > locksettings.sql

# Backup all system databases
adb shell su -c "tar -czf /sdcard/system_dbs.tar.gz /data/system/*.db"
adb pull /sdcard/system_dbs.tar.gz
```

---

## 5. Bootloader & Device Tree

### Access Bootloader Info

```bash
# Get bootloader info
adb shell su -c "getprop ro.bootloader"

# Access boot partitions
adb shell su -c "ls -la /dev/block/by-name/"

# Device tree info
adb shell su -c "ls -la /sys/firmware/devicetree/"

# Kernel info
adb shell su -c "cat /proc/version"
```

### Read Partition Data

```bash
# List partitions
adb shell su -c "lsblk"

# Dump partition
adb shell su -c "dd if=/dev/block/mmcblk0p1 of=/sdcard/boot.img"

# Or with block device:
adb shell su -c "dd if=/dev/block/by-name/boot of=/sdcard/boot.img"

# Pull dumped image
adb pull /sdcard/boot.img
```

---

## 6. Kernel Module Operations

### Load Kernel Modules

```bash
# List loaded modules
adb shell su -c "lsmod"

# Load custom module
adb shell su -c "insmod /system/lib/modules/custom_module.ko"

# Unload module
adb shell su -c "rmmod custom_module"

# Check module parameters
adb shell su -c "cat /sys/module/module_name/parameters/*"
```

---

## 7. SELinux Management

### Disable SELinux

```bash
# Check SELinux status
adb shell getenforce

# Current modes:
# - Enforcing (security enabled)
# - Permissive (warnings only)
# - Disabled

# Set permissive (requires root)
adb shell su -c "setenforce 0"

# Make persistent (edit boot config):
adb shell su -c "echo 'selinux=0' >> /system/etc/selinux/config"
```

### SELinux Policy

```bash
# Access SELinux policy
adb shell su -c "cat /sys/fs/selinux/policy"

# Check policy rules
adb shell su -c "sesearch /system/etc/selinux/precompiled_sepolicy -A"

# Modify policy (advanced)
# Usually not recommended - break things easily
```

---

## 8. Advanced Shell Features

### BusyBox Commands

```bash
# Check BusyBox (often available on rooted devices)
adb shell which busybox

# Useful BusyBox commands
adb shell su -c "busybox sed 's/old/new/g' file.txt"
adb shell su -c "busybox awk '{print $1}' file.txt"
adb shell su -c "busybox grep -r 'pattern' /data/"

# BusyBox utilities
adb shell busybox --list | head -20
```

### Package Managers

```bash
# Opkg (if installed)
adb shell su -c "opkg list-installed"
adb shell su -c "opkg install package_name"

# Apk (Alpine package manager, rare on Android)
adb shell su -c "apk info"
```

---

## 9. Memory & Process Management

### Direct Memory Access

```bash
# Read memory
adb shell su -c "dd if=/dev/mem of=/sdcard/memory.bin"

# Access /proc for process info
adb shell su -c "cat /proc/[PID]/maps"
adb shell su -c "cat /proc/[PID]/status"

# Dump process memory
adb shell su -c "gdb -p [PID]"
```

### Process Manipulation

```bash
# Kill process (including protected)
adb shell su -c "kill -9 [PID]"

# Change process priority
adb shell su -c "renice -n -10 [PID]"

# Monitor real-time
adb shell su -c "top -d 1"
```

---

## 10. System-Level Tweaks

### Performance Tuning

```bash
# CPU governor
adb shell su -c "cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"

# Set performance mode
adb shell su -c "echo performance > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"

# GPU settings
adb shell su -c "cat /sys/class/kgsl/kgsl-3d0/devfreq/governor"

# Memory settings
adb shell su -c "sysctl vm.swappiness"
adb shell su -c "sysctl -w vm.swappiness=0"
```

### Network Tweaking

```bash
# Change hostname
adb shell su -c "echo 'newname' > /proc/sys/kernel/hostname"

# Modify DNS
adb shell su -c "setprop net.dns1 8.8.8.8"
adb shell su -c "setprop net.dns2 8.8.4.4"

# Network stats
adb shell su -c "cat /proc/net/dev"
```

---

## 11. Backup & Recovery

### Full System Backup

```bash
# Backup entire /system
adb shell su -c "tar -czf /sdcard/system_backup.tar.gz /system/"
adb pull /sdcard/system_backup.tar.gz

# Backup /data (may be large)
adb shell su -c "tar -czf /sdcard/data_backup.tar.gz /data/"

# Backup partitions
adb shell su -c "dd if=/dev/block/mmcblk0 of=/sdcard/device.img"
```

### Selective Backup

```bash
# Backup only important directories
adb shell su -c "tar -czf /sdcard/backup.tar.gz \
  /data/data/com.example.app \
  /system/app/MyApp \
  /system/priv-app/MyApp"

adb pull /sdcard/backup.tar.gz
```

---

## 12. Custom ROM Installation

### Prepare for ROM Flash

```bash
# Backup current ROM
adb shell su -c "dd if=/dev/block/mmcblk0 of=/sdcard/original.img"

# Push ROM file to device
adb push custom_rom.zip /sdcard/

# Verify checksum (if provided)
adb shell "md5sum /sdcard/custom_rom.zip"

# Compare with expected:
echo "expected_hash custom_rom.zip" | md5sum -c
```

---

## 13. Root Dangers & Warnings

### Potential Issues

```
Root dangers:
- Lose warranty (usually)
- System instability if modifications wrong
- Security vulnerabilities (be careful what you run)
- Soft brick device if modifying critical partitions
- Mass storage encryption issues
```

### Safety Practices

```bash
# DO:
✓ Make backups before modifications
✓ Understand commands before running
✓ Verify checksums for downloads
✓ Test on non-critical files first
✓ Keep original ROMs

# DON'T:
✗ Delete critical system files
✗ Run unknown commands as root
✗ Modify boot partition carelessly
✗ Ignore error messages
✗ Flash ROMs without backups
```

---

## 14. Checking Root Status

### Verify Root Access

```bash
# Method 1: Check su availability
adb shell which su

# Method 2: Try su command
adb shell su -c "id"
# Should show: uid=0(root) gid=0(root)

# Method 3: Check for su binary
adb shell ls -la /system/bin/su
adb shell ls -la /system/xbin/su
adb shell ls -la /system/app/SuperSU/

# Method 4: Check if system writable
adb shell touch /system/test_file 2>&1
# If no error: writable (rooted)
# If permission denied: not writable
```

---

## 15. Advanced Root Usage

### Root-Only Debugging

```bash
# Access kernel logs that need root
adb shell su -c "dmesg"

# Monitor kernel events
adb shell su -c "tail -f /dev/kmsg"

# Check hardware info (restricted)
adb shell su -c "lshw"
adb shell su -c "hwinfo"

# View all system properties
adb shell su -c "getprop"
```


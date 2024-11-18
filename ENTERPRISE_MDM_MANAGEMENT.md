# Enterprise MDM & Device Management

## 1. MDM Setup

```bash
# Enroll device in MDM
adb shell settings put global mdm_enrolled 1

# MDM configuration
adb push mdm_config.xml /sdcard/
```

## 2. Device Control

```bash
# Remote wipe
adb shell wipe data factory reset

# Remote lock
adb shell cmd device_policy set-device-owner com.example.mdm/.DeviceAdminReceiver

# App restrictions
adb shell pm hide com.blocked.app
```

## 3. Compliance Checking

```bash
# Security patch level
adb shell getprop ro.build.version.security_patch

# Encryption status
adb shell getprop ro.crypto.state
```

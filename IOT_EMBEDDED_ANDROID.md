# IoT & Embedded Android with ADB

## 1. Android Things Setup

```bash
# Connect to Android Things device
adb connect 192.168.1.100:5555

# Verify connection
adb devices

# Check Android Things version
adb shell getprop ro.build.version.release

# Install on Android Things
adb install iot_app.apk
```

## 2. GPIO Control

```bash
# Access GPIO
adb shell cat /dev/gpio_pin_1

# Set GPIO high
adb shell echo 1 > /sys/class/gpio/gpio17/value

# Set GPIO low
adb shell echo 0 > /sys/class/gpio/gpio17/value
```

## 3. Serial Communication

```bash
# List serial ports
adb shell ls -la /dev/ttyUSB*

# Monitor serial data
adb shell cat /dev/ttyUSB0

# Send serial data
adb shell echo "data" > /dev/ttyUSB0
```

## 4. Sensor Integration

```bash
# Access sensor data
adb shell cat /sys/devices/platform/*/temperature

# Monitor device metrics
adb shell dumpsys sensorservice

# Real-time sensor monitoring
adb logcat | grep -i sensor
```

## 5. Power Management

```bash
# Check battery (if present)
adb shell dumpsys battery

# Power stats
adb shell dumpsys power

# Enable low power mode
adb shell settings put global low_power_mode 1
```

## 6. Network Configuration

```bash
# Static IP
adb shell netcfg eth0 netmask 192.168.1.0 255.255.255.0 up

# DNS configuration
adb shell settings put secure dns_1 8.8.8.8

# WiFi connection
adb shell am start -n com.android.settings/.wifi.WifiSettings
```

## 7. Headless Operation

```bash
# Run without display
# Edit build.prop to disable display

# Monitor via logcat
adb logcat | grep -i "app_name"

# Remote access
adb reverse tcp:5000 tcp:5000
```


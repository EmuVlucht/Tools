# Platform-Specific ADB Setup (Windows, Linux, macOS)

## 1. Windows Setup

### Installation
```powershell
# Method 1: Direct Download
# Download from https://developer.android.com/studio/releases/platform-tools
# Extract to: C:\Android\platform-tools
# Add to PATH

# Method 2: Chocolatey
choco install android-sdk

# Method 3: Android Studio
# Android Studio → SDK Manager → Platform Tools
```

### Add to PATH (Windows)
```powershell
# PowerShell as Administrator
$path = "C:\Android\platform-tools"
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$path", "Machine")

# Verify
adb version
```

### Windows Driver Installation
```
1. Enable Developer Mode
   Settings → Update & Security → For developers → Developer mode

2. Install USB Drivers
   Device Manager → Find Android device
   Right-click → Update driver
   Browse to: platform-tools\drivers

3. Or use Google USB Driver
   Download from: developer.android.com/studio/run/win-usb
```

### Windows Troubleshooting
```powershell
# Check if ADB running
Get-Process | findstr adb

# Kill ADB process
taskkill /IM adb.exe /F

# Restart
adb kill-server
adb start-server

# Check port
netstat -ano | findstr :5037

# Verify installation
adb version
```

---

## 2. Linux Setup

### Installation (Ubuntu/Debian)
```bash
# Method 1: Package Manager
sudo apt update
sudo apt install android-tools-adb android-tools-fastboot

# Method 2: Manual Download
wget https://dl.google.com/android/repository/platform-tools-latest-linux.zip
unzip platform-tools-latest-linux.zip
sudo mv platform-tools /opt/

# Add to PATH
echo 'export PATH=$PATH:/opt/platform-tools' >> ~/.bashrc
source ~/.bashrc
```

### Installation (Fedora/RHEL)
```bash
sudo dnf install android-tools

# Or manually
wget https://dl.google.com/android/repository/platform-tools-latest-linux.zip
unzip platform-tools-latest-linux.zip
sudo mv platform-tools /opt/

echo 'export PATH=$PATH:/opt/platform-tools' >> ~/.bashrc
```

### USB Permission Setup (Linux)
```bash
# Create udev rules
sudo nano /etc/udev/rules.d/51-android.rules

# Add for each vendor:
SUBSYSTEM=="usb", ATTR{idVendor}=="18d1", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="04e8", MODE="0666"  # Samsung
SUBSYSTEM=="usb", ATTR{idVendor}=="2717", MODE="0666"  # Xiaomi

# Reload rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Add user to group
sudo usermod -a -G plugdev $USER
newgrp plugdev
```

### Linux Troubleshooting
```bash
# Check running processes
ps aux | grep adb

# Check permissions
ls -la /dev/bus/usb/

# Manual permission fix
sudo chmod 666 /dev/bus/usb/*/

# Check rules loaded
sudo udevadm info -q all -n /dev/bus/usb/001/001

# Verify installation
adb version
```

---

## 3. macOS Setup

### Installation
```bash
# Method 1: Homebrew
brew install android-platform-tools

# Method 2: Manual Download
wget https://dl.google.com/android/repository/platform-tools-latest-darwin.zip
unzip platform-tools-latest-darwin.zip
sudo mv platform-tools /opt/

# Add to PATH
echo 'export PATH=$PATH:/opt/platform-tools' >> ~/.zprofile
source ~/.zprofile
```

### Verify Installation
```bash
# Check version
adb version

# Verify path
which adb

# Test connection
adb devices
```

### macOS Troubleshooting
```bash
# Clear ADB cache
rm -rf ~/.android/

# Restart ADB daemon
adb kill-server
adb start-server

# Check if device recognized
system_profiler SPUSBDataType | grep -i android

# If permission issues
sudo killall -9 usbmuxd
# Reconnect device
```

---

## 4. Cross-Platform Commands

### Universal Commands
```bash
# All platforms
adb devices                    # List devices
adb version                    # Version info
adb install app.apk           # Install app
adb pull /sdcard/file ./      # Pull file
adb push file /sdcard/        # Push file
adb shell                      # Shell access
```

### Platform Detection Script
```bash
#!/bin/bash
# detect_platform.sh

PLATFORM=$(uname)

case "$PLATFORM" in
    Darwin)
        echo "macOS detected"
        ANDROID_HOME="/opt/android-sdk"
        ;;
    Linux)
        echo "Linux detected"
        ANDROID_HOME="$HOME/Android/Sdk"
        ;;
    MINGW* | MSYS*)
        echo "Windows detected"
        ANDROID_HOME="C:\\Android\\Sdk"
        ;;
esac

export ANDROID_HOME
export PATH=$PATH:$ANDROID_HOME/platform-tools

adb version
```

---

## 5. Docker Setup

### Docker Image
```dockerfile
FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    android-tools-adb \
    android-tools-fastboot \
    wget

WORKDIR /workspace

ENTRYPOINT ["adb"]
```

### Docker Compose
```yaml
version: '3'
services:
  adb:
    build: .
    ports:
      - "5037:5037"
    volumes:
      - ~/.android:/root/.android
      - ./workspace:/workspace
    environment:
      - ADB_SERVER_PORT=5037
```

### Run in Docker
```bash
docker build -t adb-tools .
docker run -it --rm adb-tools devices
docker run -it --rm adb-tools shell getprop ro.build.version.release
```

---

## 6. CI/CD Environment Setup

### GitHub Actions
```yaml
name: Setup ADB
on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-java@v2
        with:
          java-version: '11'
      
      - name: Install ADB
        run: |
          sudo apt-get update
          sudo apt-get install -y android-tools-adb
      
      - name: Test ADB
        run: |
          adb version
          adb devices
```

### GitLab CI
```yaml
image: ubuntu:20.04

before_script:
  - apt-get update
  - apt-get install -y android-tools-adb
  - adb version

test:
  script:
    - adb devices
```

---

## 7. Virtual Machine Setup

### VirtualBox with Android
```bash
# Create VM with Linux
# Install base OS
# Follow Linux setup above

# Port forwarding (if needed)
VBoxManage modifyvm "VM Name" --natpf1 "adb,tcp,5037,,5037"
```

### WSL (Windows Subsystem for Linux)
```bash
# Install WSL2
wsl --install

# In WSL terminal
sudo apt update
sudo apt install android-tools-adb

# May need to access host devices
# Use: /mnt/c/path/to/adb.exe from Windows
```

---

## 8. Environment Variables

### Linux/macOS
```bash
# Add to ~/.bashrc or ~/.zprofile
export ANDROID_HOME=$HOME/Android/Sdk
export ADB_TRACE=1                    # Enable tracing
export ANDROID_LOG_TAGS="*:V"        # Verbose logging
export ADB_SERVER_PORT=5037          # Custom port

# Reload
source ~/.bashrc
```

### Windows (PowerShell)
```powershell
# Permanent environment variable
[Environment]::SetEnvironmentVariable("ANDROID_HOME", "C:\Android\Sdk", "User")
[Environment]::SetEnvironmentVariable("ADB_SERVER_PORT", "5037", "User")

# Verify
$env:ANDROID_HOME
```

---

## 9. Installation Verification

### Test Installation
```bash
# 1. Check version
adb version

# 2. Check path
which adb  # Linux/macOS
where adb  # Windows

# 3. Start server
adb start-server

# 4. List devices
adb devices

# 5. Test connection
adb shell getprop ro.build.version.release
```

---

## 10. Advanced Configuration

### Custom ADB Server
```bash
# Run on custom port
adb -P 5038 start-server

# Connect clients
adb -P 5038 devices

# Persistent in environment
export ADB_SERVER_PORT=5038
```

### Multiple ADB Versions
```bash
# Keep multiple versions
~/adb/platform-tools-32/adb
~/adb/platform-tools-33/adb

# Alias for switching
alias adb32='~/adb/platform-tools-32/adb'
alias adb33='~/adb/platform-tools-33/adb'
```


# Panduan Instalasi ADB

## Windows

### Metode 1: Download dari Android SDK

1. Download Android Studio dari https://developer.android.com/studio
2. Install Android Studio
3. Buka Android Studio → Tools → SDK Manager
4. Pilih "SDK Tools" tab
5. Centang "Android SDK Platform-Tools"
6. Klik "Apply" dan tunggu instalasi selesai
7. ADB akan tersimpan di: `C:\Users\YourUsername\AppData\Local\Android\sdk\platform-tools`

### Metode 2: Download Platform Tools Langsung

1. Download dari https://developer.android.com/tools/releases/platform-tools
2. Extract ke folder, misal: `C:\Users\YourUsername\platform-tools`
3. Tambahkan ke PATH environment variable

### Tambahkan ke PATH (Windows)

1. Buka Settings → System → About
2. Klik "Advanced system settings"
3. Klik "Environment Variables"
4. Klik "New" di bagian System variables
5. Variable name: `ANDROID_SDK_ROOT`
6. Variable value: `C:\Users\YourUsername\AppData\Local\Android\sdk`
7. Klik OK
8. Edit Path variable, tambahkan: `%ANDROID_SDK_ROOT%\platform-tools`
9. Buka Command Prompt baru dan test:
```bash
adb --version
```

---

## Linux (Ubuntu/Debian)

### Instalasi via APT

```bash
# Update package list
sudo apt update

# Install ADB
sudo apt install android-tools-adb

# Verifikasi instalasi
adb --version
```

### Instalasi Manual

```bash
# Download platform tools
wget https://dl.google.com/android/repository/platform-tools-latest-linux.zip

# Extract
unzip platform-tools-latest-linux.zip

# Move ke /opt
sudo mv platform-tools /opt/android-tools

# Tambah ke PATH
echo 'export PATH=$PATH:/opt/android-tools' >> ~/.bashrc
source ~/.bashrc

# Verifikasi
adb --version
```

### Izin USB (Ubuntu/Debian)

```bash
# Tambah udev rules
sudo wget -O /etc/udev/rules.d/51-android.rules https://raw.githubusercontent.com/M0Rf30/android-udev-rules/master/51-android.rules

# Set permission
sudo chmod a+r /etc/udev/rules.d/51-android.rules

# Reload rules
sudo service udev restart

# Restart ADB daemon
adb kill-server
adb start-server
```

---

## macOS

### Metode 1: Homebrew

```bash
# Install Homebrew jika belum ada
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install ADB
brew install android-platform-tools

# Verifikasi
adb --version
```

### Metode 2: Manual Download

```bash
# Download
wget https://dl.google.com/android/repository/platform-tools-latest-darwin.zip

# Extract
unzip platform-tools-latest-darwin.zip

# Move
sudo mv platform-tools /Library/Android/sdk/

# Tambah ke PATH
echo 'export PATH=$PATH:/Library/Android/sdk/platform-tools' >> ~/.zprofile
source ~/.zprofile

# Verifikasi
adb --version
```

---

## Setup Perangkat Android

### Persiapan Perangkat

1. **Enable Developer Mode**
   - Buka Settings → About phone
   - Tap "Build Number" 7 kali
   - Kembali ke Settings, akan muncul "Developer options"

2. **Enable USB Debugging**
   - Buka Settings → Developer options
   - Aktifkan "USB Debugging"

3. **Install USB Driver (Windows)**
   - Download USB driver sesuai brand (Samsung, Google, etc.)
   - Install driver

4. **Connect Device**
   - Hubungkan perangkat dengan kabel USB
   - Pilih "Allow" ketika dialog permission muncul

5. **Verify Connection**
   ```bash
   adb devices
   ```
   Output should show device sebagai "device"

---

## Test Instalasi

### Verifikasi ADB terinstal

```bash
# Cek versi
adb version

# Lihat bantuan
adb help
```

### Test Koneksi Perangkat

```bash
# Pastikan device terhubung via USB
adb devices

# Contoh output:
# List of attached devices
# emulator-5554          device

# Atau untuk TCP/IP connection
adb connect 192.168.1.100:5555
```

### Test Dasar

```bash
# Lihat info perangkat
adb shell getprop ro.build.version.release

# Lihat file di perangkat
adb shell ls /sdcard/

# Install test app
adb install test.apk
```

---

## Troubleshooting

### ADB tidak ditemukan (command not found)

**Windows:**
- Pastikan PATH variable sudah di-add ke environment
- Restart Command Prompt
- Check: `echo %PATH%`

**Linux/Mac:**
- Restart terminal
- Check: `echo $PATH`
- Verifikasi lokasi: `which adb`

### Device tidak terdeteksi

```bash
# Restart ADB daemon
adb kill-server
adb start-server

# Check devices
adb devices
```

### Permission Denied (Linux)

```bash
# Check grup
groups

# Tambah user ke grup plugdev
sudo usermod -a -G plugdev $USER

# Logout dan login kembali
```

### Device Offline

1. Disconnect dan reconnect USB cable
2. Restart device
3. Restart ADB server:
   ```bash
   adb kill-server
   adb start-server
   ```

### "no devices found"

- Pastikan USB debugging diaktifkan di perangkat
- Hubungkan dengan kabel USB original
- Install driver USB yang benar
- Coba port USB yang berbeda

---

## Uninstall ADB

### Windows
1. Buka Control Panel → Programs → Programs and Features
2. Cari Android Studio atau platform-tools
3. Klik Uninstall

### Linux
```bash
sudo apt remove android-tools-adb
# atau
sudo apt remove android-tools
```

### macOS
```bash
brew uninstall android-platform-tools
# atau hapus folder manual
rm -rf /Library/Android/sdk/platform-tools
```


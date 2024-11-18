# FAQ - Frequently Asked Questions ADB

## General Questions

### Q1: Apa perbedaan antara USB Debugging dan ADB over Network?

**Jawab:** 
- **USB Debugging**: Koneksi langsung via kabel USB, lebih cepat dan stabil, lebih aman karena fisik
- **ADB over Network**: Koneksi via WiFi, lebih fleksibel karena tidak perlu kabel, tapi lebih lambat dan bisa unstable

Pilih USB untuk development, network untuk testing di lokasi yang jauh dari komputer.

---

### Q2: Bagaimana cara ADB tahu perangkat mana yang harus menerima perintah?

**Jawab:**
Saat multiple devices terhubung, gunakan flag `-s`:
```bash
adb -s <device_id> <command>
adb -s emulator-5554 install app.apk
adb -s 192.168.1.100:5555 shell ls
```

Atau gunakan `adb devices` untuk melihat ID perangkat yang tersedia.

---

### Q3: Apakah ADB aman digunakan?

**Jawab:**
Ya, ADB aman jika:
- Hanya digunakan untuk development
- USB Debugging hanya diaktifkan saat dibutuhkan
- Tidak terhubung ke jaringan publik yang tidak terpercaya
- Menggunakan authorized devices

Untuk production, pastikan USB Debugging dimatikan.

---

### Q4: Berapa port default ADB?

**Jawab:**
- **Server Port**: 5037 (port komunikasi server ADB di komputer)
- **Daemon Port**: 5555 (port daemon di perangkat untuk TCP/IP)

Contoh: `adb connect 192.168.1.100:5555`

---

## Installation Issues

### Q5: ADB tidak ditemukan meskipun sudah install, bagaimana?

**Jawab:**
Windows:
```bash
# Check PATH
echo %PATH%

# Add ke PATH secara manual
setx PATH "%PATH%;C:\Users\YourUsername\AppData\Local\Android\sdk\platform-tools"

# Restart Command Prompt
```

Linux/Mac:
```bash
# Check PATH
echo $PATH

# Add ke ~/.bashrc atau ~/.zshrc
echo 'export PATH=$PATH:/path/to/platform-tools' >> ~/.bashrc
source ~/.bashrc
```

---

### Q6: "permission denied" saat menjalankan adb di Linux?

**Jawab:**
Tambahkan user ke grup plugdev:
```bash
# Check grup
groups

# Tambah ke plugdev
sudo usermod -a -G plugdev $USER

# Logout dan login ulang

# Atau jalankan dengan sudo (tidak recommended)
sudo adb devices
```

---

### Q7: Bagaimana install ADB tanpa Android Studio?

**Jawab:**
Download langsung dari Google:
```bash
# Windows
# Download dari https://dl.google.com/android/repository/platform-tools-latest-windows.zip

# Linux
wget https://dl.google.com/android/repository/platform-tools-latest-linux.zip
unzip platform-tools-latest-linux.zip

# Mac
wget https://dl.google.com/android/repository/platform-tools-latest-darwin.zip
unzip platform-tools-latest-darwin.zip
```

---

## Connection Issues

### Q8: Device tidak terdeteksi, apa yang harus dilakukan?

**Jawab:**
1. Restart ADB server:
   ```bash
   adb kill-server
   adb start-server
   ```

2. Aktivasi USB Debugging di perangkat:
   - Settings → Developer Options → USB Debugging

3. Ganti kabel USB atau port USB

4. Install driver USB yang sesuai (Windows)

5. Disconnect dan reconnect device

---

### Q9: "offline" atau "unauthorized" status, bagaimana cara fix?

**Jawab:**
```bash
# Disconnect semua
adb disconnect
adb usb

# Reconnect via USB

# Terima prompt di device

# Check status
adb devices
```

Status akan berubah menjadi "device"

---

### Q10: Bagaimana connect ADB via WiFi?

**Jawab:**
```bash
# 1. Connect via USB dulu
adb devices

# 2. Enable TCP/IP mode
adb tcpip 5555

# 3. Cari IP perangkat
adb shell ifconfig | grep inet

# 4. Disconnect USB dan connect via WiFi
adb connect 192.168.1.100:5555

# 5. Verify
adb devices
```

---

## Command Issues

### Q11: ADB command menampilkan "command not found" atau error aneh?

**Jawab:**
Tiga kemungkinan:
1. Typo dalam perintah
2. ADB server tidak berjalan
3. Device tidak terhubung

Solusi:
```bash
# Restart server
adb kill-server
adb start-server

# Verify connection
adb devices

# Cek versi
adb version
```

---

### Q12: Output dari perintah ADB terpotong atau tidak lengkap?

**Jawab:**
Gunakan redirect ke file:
```bash
# Simpan ke file
adb logcat > logcat_output.txt

# Atau gunakan grep untuk filter
adb logcat | grep "search term"

# Atau limit output
adb logcat -n 50  # Last 50 lines
```

---

### Q13: Bagaimana membatalkan perintah ADB yang sedang berjalan?

**Jawab:**
Tekan `Ctrl+C` di terminal untuk menghentikan perintah yang sedang berjalan:
```bash
adb logcat   # Tekan Ctrl+C untuk berhenti
```

---

## File Transfer Issues

### Q14: "Permission denied" saat push file ke /system/ atau /data/?

**Jawab:**
Folder tersebut adalah system folder yang read-only. Transfer ke folder yang writable:
```bash
# Push ke /sdcard/
adb push file.txt /sdcard/

# Jika need system access, perlu root:
adb root
adb remount
adb push file.txt /system/app/
```

⚠️ Rooting device bisa merusak warranty dan security!

---

### Q15: "No space left on device" saat push file besar?

**Jawab:**
```bash
# Check disk space
adb shell df -h

# Delete unnecessary files
adb shell rm /sdcard/large_file.zip

# Atau push ke USB storage
adb push file.zip /storage/usbdisk/
```

---

### Q16: Transfer file lambat, bagaimana mempercepat?

**Jawab:**
- Gunakan USB Debugging (lebih cepat dari network)
- Transfer file lebih kecil atau compress terlebih dahulu
- Hubungkan ke USB port 3.0 atau lebih tinggi
- Gunakan SSD untuk komputer

```bash
# Compress sebelum transfer
zip -r files.zip folder/
adb push files.zip /sdcard/
adb shell unzip /sdcard/files.zip -d /sdcard/
```

---

## Application Issues

### Q17: APK tidak bisa install via ADB, apa penyebabnya?

**Jawab:**
Kemungkinan penyebab:
1. File APK corrupt atau incomplete
2. Android version incompatible
3. Storage penuh
4. Signature mismatch

Solusi:
```bash
# Check APK
adb install -r app.apk  # Force install/replace

# Check Android version
adb shell getprop ro.build.version.release

# Check storage
adb shell df -h

# Jika masih error, lihat error detail
adb install app.apk  # Lihat error message
```

---

### Q18: Bagaimana check versi aplikasi yang terinstal?

**Jawab:**
```bash
# List dengan versi
adb shell dumpsys package com.example.app | grep -i version

# Atau
adb shell pm dump com.example.app | grep version

# Atau check file
adb shell ls -la /data/app/com.example.app/
```

---

### Q19: Aplikasi crash dengan error, bagaimana debug?

**Jawab:**
```bash
# Clear log
adb logcat -c

# Run aplikasi
adb shell am start -n com.example.app/.MainActivity

# Cek log untuk crash
adb logcat | grep "FATAL\|Exception\|crash"

# Atau save ke file untuk analisis
adb logcat > crash.txt
```

---

## Performance Issues

### Q20: Bagaimana check apakah device itu slow atau app itu slow?

**Jawab:**
```bash
# Check memory
adb shell dumpsys meminfo

# Check CPU
adb shell top -n 1

# Check temperature
adb shell cat /sys/class/thermal/thermal_zone0/temp

# Monitor realtime
adb shell top

# App-specific
adb shell dumpsys meminfo com.example.app
```

---

### Q21: Bagaimana meningkatkan performa transfer file?

**Jawab:**
```bash
# 1. Gunakan USB 3.0+ port
# 2. Restart server
adb kill-server
adb start-server

# 3. Untuk banyak file, gunakan tar
adb shell "tar czf /sdcard/backup.tar.gz /data/app/"
adb pull /sdcard/backup.tar.gz ./

# 4. Transfer paralel
for file in *.apk; do
    adb install "$file" &
done
wait
```

---

## Logcat Issues

### Q22: Logcat terlalu banyak output, bagaimana filter?

**Jawab:**
```bash
# Filter by level
adb logcat *:E   # Only errors
adb logcat *:W   # Warnings and above

# Filter by tag
adb logcat MyApp:I *:S

# Filter by app package
adb logcat --pid=$(adb shell pidof com.example.app)

# Grep untuk search
adb logcat | grep "search term"

# Save dan analyze
adb logcat > log.txt
cat log.txt | grep "error"
```

---

### Q23: Bagaimana capture logcat ke file untuk long-term monitoring?

**Jawab:**
```bash
# Simple save
adb logcat > logcat_$(date +%Y%m%d_%H%M%S).txt

# With rotation (max 10 files, each 1MB)
adb logcat -v threadtime -G 1M -n 10

# Background process
nohup adb logcat > logcat.txt 2>&1 &

# Or use script
#!/bin/bash
adb logcat > logcat_$(date +%Y%m%d).txt &
```

---

## Advanced Issues

### Q24: Bagaimana debug network issues pada device?

**Jawab:**
```bash
# Check network interfaces
adb shell ifconfig

# Check DNS
adb shell getprop net.hostname

# Network statistics
adb shell netstat -a

# Trace network calls
adb shell dumpsys connectivity

# Monitor traffic
adb shell "cat /proc/net/dev"
```

---

### Q25: Bagaimana access database aplikasi?

**Jawab:**
```bash
# Find database
adb shell find /data/data/com.example.app -name "*.db"

# Pull database
adb pull /data/data/com.example.app/databases/app.db ./

# Query via shell
adb shell "sqlite3 /data/data/com.example.app/databases/app.db '.tables'"

# Or extract data
adb shell "sqlite3 /data/data/com.example.app/databases/app.db '.dump' > /sdcard/dump.sql"
adb pull /sdcard/dump.sql ./
```

---

## Best Practices

### Q26: Best practice untuk ADB development?

**Jawab:**
1. **Security**: Matikan USB Debugging saat tidak digunakan
2. **Organization**: Kelompokkan devices dan gunakan aliases
3. **Logging**: Selalu save logcat untuk debugging
4. **Automation**: Gunakan script untuk repetitif tasks
5. **Documentation**: Document semua perintah custom
6. **Testing**: Test di multiple devices dan Android versions
7. **Backup**: Backup sebelum push ke system folder

---

### Q27: Bagaimana automation berbagai ADB tasks?

**Jawab:**
```bash
#!/bin/bash
# Multi-device deployment

DEVICES=$(adb devices | awk 'NR>1 {print $1}')

for device in $DEVICES; do
    echo "Installing on $device..."
    adb -s $device install app.apk
done

echo "Done!"
```

Atau gunakan Python:
```python
import subprocess
import json

devices = subprocess.check_output(['adb', 'devices']).decode().split('\n')[1:-2]
for device in devices:
    subprocess.call(['adb', '-s', device.split()[0], 'install', 'app.apk'])
```

---

### Q28: Tools apa saja yang bisa diintegrasikan dengan ADB?

**Jawab:**
- **Android Studio** - Built-in ADB integration
- **Gradle** - `./gradlew install`
- **Python** - `subprocess` library
- **Bash** - Shell scripts
- **CI/CD** - Jenkins, GitHub Actions, etc.
- **Docker** - ADB dalam container
- **VS Code** - Extensions untuk ADB

---

### Q29: Bagaimana setup CI/CD dengan ADB?

**Jawab:**
```yaml
# GitHub Actions Example
name: ADB Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install ADB
        run: sudo apt-get install android-tools-adb
      - name: List devices
        run: adb devices
      - name: Run tests
        run: adb shell am instrument com.example.test
```

---

## Miscellaneous

### Q30: Apakah ADB bisa digunakan untuk produksi?

**Jawab:**
Tidak, ADB adalah development tool. Untuk produksi:
- Gunakan app store (Google Play)
- Atau enterprise distribution
- ADB hanya untuk testing dan development

USB Debugging harus dimatikan untuk production devices.

---

## Getting Help

### Q31: Bagaimana cara mendapat bantuan jika error tidak tercantum di FAQ?

**Jawab:**
1. Check error message dengan detail
2. Search di Stack Overflow
3. Lihat Android Developer Documentation
4. Check Android SDK release notes
5. Konsultasikan dengan komunitas Android
6. Buat detailed bug report dengan:
   - ADB version: `adb version`
   - Android version: `adb shell getprop ro.build.version.release`
   - Device info: `adb shell getprop ro.product.model`
   - Error message lengkap

---

## More Resources

- Official ADB Documentation: https://developer.android.com/tools/adb
- Android SDK: https://developer.android.com/studio
- Android Developers: https://developer.android.com
- GitHub Issues: Search di Android open-source repos
- Stack Overflow: Tag dengan [android], [adb]


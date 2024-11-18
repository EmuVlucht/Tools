# Contoh Penggunaan ADB

## Setup Awal

### 1. Cek Perangkat Terhubung
```bash
$ adb devices
List of attached devices
emulator-5554          device
192.168.1.100:5555     device
```

### 2. Koneksi Melalui USB
Pastikan USB Debugging diaktifkan di perangkat Android:
- Buka Settings → Developer Options
- Aktifkan USB Debugging
- Hubungkan perangkat dengan kabel USB

```bash
adb devices
```

### 3. Koneksi Melalui WiFi
```bash
# Pada perangkat atau emulator yang sudah terhubung USB
adb tcpip 5555

# Cari IP perangkat dari Settings atau
adb shell ifconfig

# Disconnect USB dan connect via WiFi
adb connect 192.168.1.100:5555
adb devices
```

---

## Contoh Praktis Sehari-hari

### Scenario 1: Install dan Test Aplikasi

```bash
# 1. Install aplikasi
adb install myapp.apk

# 2. Lihat aplikasi terinstal
adb shell pm list packages | grep myapp

# 3. Jalankan aplikasi
adb shell am start -n com.example.myapp/.MainActivity

# 4. Baca log aplikasi
adb logcat | grep com.example.myapp

# 5. Uninstall aplikasi
adb uninstall com.example.myapp
```

### Scenario 2: Transfer File

```bash
# Upload file ke perangkat
adb push /home/user/documents/file.pdf /sdcard/Documents/

# Upload folder
adb push /home/user/photos /sdcard/

# Download file dari perangkat
adb pull /sdcard/screenshot.png ~/Downloads/

# Download folder
adb pull /sdcard/DCIM/Camera ~/Pictures/backup/
```

### Scenario 3: Debugging Aplikasi

```bash
# Bersihkan log
adb logcat -c

# Lihat log real-time
adb logcat

# Filter log berdasarkan tag aplikasi
adb logcat | grep "MyApp"

# Lihat hanya error dan warning
adb logcat *:W

# Simpan log ke file
adb logcat > app_log.txt

# Hentikan dengan Ctrl+C

# Lihat error stack trace
adb logcat *:E
```

### Scenario 4: Screenshot dan Recording

```bash
# Ambil screenshot
adb shell screencap -p /sdcard/screenshot.png
adb pull /sdcard/screenshot.png ~/

# Record video selama 30 detik
adb shell screenrecord --time-limit=30 /sdcard/video.mp4
adb pull /sdcard/video.mp4 ~/

# Record dengan resolusi custom
adb shell screenrecord --size 1280x720 /sdcard/video.mp4
```

### Scenario 5: Tap dan Input

```bash
# Tap pada koordinat (x=500, y=1000)
adb shell input tap 500 1000

# Ketik teks
adb shell input text "Hello World"

# Tekan tombol back
adb shell input keyevent 4

# Tekan tombol home
adb shell input keyevent 3

# Tekan tombol power
adb shell input keyevent 26

# List keyevent codes
# 3 = HOME
# 4 = BACK
# 26 = POWER
# 82 = MENU
# 121 = VOLUME_MUTE
```

### Scenario 6: Backup dan Restore

```bash
# Backup semua data aplikasi
adb backup -all -f backup.ab

# Restore dari backup
adb restore backup.ab

# Backup aplikasi spesifik
adb backup -f telegram.ab com.telegram.messenger

# Backup tanpa APK (hanya data)
adb backup -all -noapk -f data_only.ab
```

### Scenario 7: Port Forwarding

```bash
# Forward localhost port 8000 ke port 8888 di perangkat
adb forward tcp:8000 tcp:8888

# Cek port forwarding yang aktif
adb forward --list

# Akses dari browser
# http://localhost:8000

# Hapus forwarding
adb forward --remove tcp:8000
```

### Scenario 8: Monitoring Performa

```bash
# Lihat process yang berjalan
adb shell ps

# Lihat memory usage
adb shell dumpsys meminfo

# Monitor memory aplikasi spesifik
adb shell dumpsys meminfo com.example.app

# Lihat battery status
adb shell dumpsys battery

# Lihat CPU usage
adb shell top

# Export bugreport
adb bugreport > bugreport.zip
```

### Scenario 9: Permission Management

```bash
# List semua permission
adb shell pm list permissions

# Grant permission ke aplikasi
adb shell pm grant com.example.app android.permission.CAMERA
adb shell pm grant com.example.app android.permission.ACCESS_FINE_LOCATION

# Revoke permission
adb shell pm revoke com.example.app android.permission.CAMERA
```

### Scenario 10: System Settings

```bash
# Ubah brightness
adb shell settings put system screen_brightness 200

# Ubah volume
adb shell service call audio 3 i32 3 i32 10

# Baca Android ID
adb shell settings get secure android_id

# Baca versi Android
adb shell getprop ro.build.version.release

# Baca model device
adb shell getprop ro.product.model

# Baca manufacturer
adb shell getprop ro.product.manufacturer
```

---

## Contoh Script Automation

### Script 1: Install Multiple APKs

```bash
#!/bin/bash
# install_apps.sh

APK_DIR="./apks"

for apk in $APK_DIR/*.apk; do
    echo "Installing: $apk"
    adb install "$apk"
done

echo "Done!"
```

### Script 2: Daily Backup

```bash
#!/bin/bash
# daily_backup.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="./backups"

mkdir -p $BACKUP_DIR

adb backup -all -f "$BACKUP_DIR/backup_$DATE.ab"

echo "Backup created: $BACKUP_DIR/backup_$DATE.ab"
```

### Script 3: Batch File Transfer

```bash
#!/bin/bash
# transfer_files.sh

SOURCE=$1
DEST=$2

for file in $SOURCE/*; do
    echo "Pushing: $(basename $file)"
    adb push "$file" "/sdcard/Downloads/"
done

echo "All files transferred!"
```

---

## Tips dan Trik

### 1. Multiple Devices
Jika ada lebih dari satu device terhubung:
```bash
# Lihat device
adb devices

# Execute pada device spesifik
adb -s emulator-5554 install app.apk
adb -s 192.168.1.100:5555 shell ls /sdcard/
```

### 2. Create Alias (Linux/Mac)
```bash
# Tambahkan ke ~/.bashrc atau ~/.zshrc
alias adb-logcat='adb logcat'
alias adb-devices='adb devices'
alias adb-install='adb install'
alias adb-shell='adb shell'

# Gunakan
adb-logcat
```

### 3. Quick Screenshot
```bash
# Buat function di shell
screenshot() {
    adb shell screencap -p /sdcard/screenshot.png
    adb pull /sdcard/screenshot.png ~/Desktop/
    echo "Screenshot saved to Desktop"
}

# Gunakan
screenshot
```

### 4. Device Info Function
```bash
device-info() {
    echo "=== Device Information ==="
    echo "Model: $(adb shell getprop ro.product.model)"
    echo "Android: $(adb shell getprop ro.build.version.release)"
    echo "Brand: $(adb shell getprop ro.product.brand)"
    echo "Device ID: $(adb shell settings get secure android_id)"
}

# Gunakan
device-info
```

### 5. Watch Logcat
```bash
# Lihat log spesifik secara real-time
watch_log() {
    adb logcat | grep --color=auto "$1"
}

# Gunakan
watch_log "MyApp"
```

---

## Troubleshooting

### Device Offline
```bash
# Kill dan restart server
adb kill-server
adb start-server
adb devices
```

### Permission Denied
```bash
# Cek ADB daemon
adb devices

# Restart daemon
adb kill-server
adb start-server

# Atau reconnect device
```

### Tidak Terdeteksi
```bash
# Restart komputer dan device
# Check driver di Device Manager (Windows)
# Atau
sudo apt-get install android-tools-adb  # Linux

# Verifikasi USB cable
# Aktifkan USB Debugging di perangkat
```

### Port Forwarding Tidak Bekerja
```bash
# Clear forwarding
adb forward --remove-all

# Setup ulang
adb forward tcp:8000 tcp:8000
adb forward --list
```


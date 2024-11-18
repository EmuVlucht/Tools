# Fungsi-Fungsi Detail ADB

## 1. Perintah Koneksi & Device

### `adb devices`
**Fungsi**: Menampilkan semua perangkat Android yang terhubung
```
adb devices
```
**Output Kemungkinan**:
- `device` - Perangkat terhubung dengan baik
- `offline` - Perangkat terdeteksi tapi tidak responsif
- `unauthorized` - Perlu konfirmasi dari perangkat

### `adb connect <host>:<port>`
**Fungsi**: Terhubung ke perangkat melalui jaringan TCP/IP
```
adb connect 192.168.1.100:5555
```

### `adb disconnect [host:port]`
**Fungsi**: Memutuskan koneksi dari perangkat
```
adb disconnect          # Putus semua koneksi
adb disconnect 192.168.1.100:5555  # Putus koneksi spesifik
```

### `adb usb`
**Fungsi**: Menghubungkan kembali perangkat melalui USB
```
adb usb
```

---

## 2. Perintah File Transfer

### `adb push <local> <remote>`
**Fungsi**: Mengirim file dari komputer ke perangkat
```
adb push /path/to/file.txt /sdcard/
adb push image.jpg /storage/emulated/0/Pictures/
```

### `adb pull <remote> <local>`
**Fungsi**: Mengambil file dari perangkat ke komputer
```
adb pull /sdcard/file.txt ./
adb pull /data/app/com.example.app/ ./app_data/
```

### `adb shell ls`
**Fungsi**: Melihat daftar file di perangkat
```
adb shell ls /sdcard/
adb shell ls -la /data/
```

---

## 3. Perintah Aplikasi

### `adb install <apk>`
**Fungsi**: Menginstal aplikasi dari file APK
```
adb install myapp.apk
adb install -r myapp.apk        # Install dan replace
adb install -g myapp.apk        # Install dengan grant permissions
```

### `adb uninstall <package>`
**Fungsi**: Menghapus aplikasi dari perangkat
```
adb uninstall com.example.app
adb uninstall -k com.example.app  # Keep data and cache
```

### `adb shell am start`
**Fungsi**: Menjalankan aplikasi atau activity
```
adb shell am start -n com.example.app/.MainActivity
adb shell am start com.example.app
```

### `adb shell pm list packages`
**Fungsi**: Menampilkan daftar paket/aplikasi yang terinstal
```
adb shell pm list packages              # Semua paket
adb shell pm list packages -3           # Aplikasi pihak ketiga
adb shell pm list packages -s           # Sistem aplikasi
```

---

## 4. Perintah Logging & Debugging

### `adb logcat`
**Fungsi**: Menampilkan log sistem real-time
```
adb logcat                              # Tampilkan semua log
adb logcat -c                           # Clear log
adb logcat *:W                          # Tampilkan warning dan error
adb logcat | grep "tag_name"            # Filter berdasarkan tag
adb logcat > logcat.txt                 # Simpan ke file
```

### `adb shell dumpsys`
**Fungsi**: Dump informasi sistem detail
```
adb shell dumpsys battery               # Info baterai
adb shell dumpsys package com.example   # Info paket
adb shell dumpsys meminfo               # Info memori
```

### `adb bugreport`
**Fungsi**: Generate laporan bug lengkap
```
adb bugreport > bugreport.zip
```

---

## 5. Perintah Kontrol Perangkat

### `adb shell screencap`
**Fungsi**: Mengambil screenshot
```
adb shell screencap /sdcard/screenshot.png
adb pull /sdcard/screenshot.png ./
```

### `adb shell screenrecord`
**Fungsi**: Merekam layar perangkat
```
adb shell screenrecord /sdcard/video.mp4
adb shell screenrecord --time-limit=10 /sdcard/video.mp4
```

### `adb shell input`
**Fungsi**: Mengirim input ke perangkat (tap, text, key)
```
adb shell input tap 500 500              # Tap pada koordinat
adb shell input text "Hello World"       # Ketik teks
adb shell input keyevent 26              # Tekan key (26 = Power)
```

### `adb reboot`
**Fungsi**: Restart perangkat
```
adb reboot                  # Reboot normal
adb reboot bootloader       # Reboot ke bootloader
adb reboot recovery         # Reboot ke recovery mode
```

---

## 6. Perintah Backup & Restore

### `adb backup`
**Fungsi**: Membuat backup aplikasi dan data
```
adb backup -all -f backup.ab            # Backup semua dengan data
adb backup -all -noapk -f backup.ab     # Backup tanpa APK
adb backup com.example.app -f app.ab    # Backup aplikasi spesifik
```

### `adb restore`
**Fungsi**: Memulihkan backup
```
adb restore backup.ab
```

---

## 7. Perintah Port Forwarding

### `adb forward`
**Fungsi**: Forward port dari perangkat ke komputer
```
adb forward tcp:8888 tcp:8000           # Forward port
adb forward --list                      # Lihat forwarding aktif
adb forward --remove tcp:8888           # Hapus forwarding
adb forward --remove-all                # Hapus semua forwarding
```

### `adb reverse`
**Fungsi**: Reverse forward (dari perangkat ke host)
```
adb reverse tcp:8000 tcp:8000
```

---

## 8. Perintah Server ADB

### `adb kill-server`
**Fungsi**: Hentikan server ADB
```
adb kill-server
```

### `adb start-server`
**Fungsi**: Jalankan server ADB
```
adb start-server
```

### `adb version`
**Fungsi**: Tampilkan versi ADB
```
adb version
```

---

## 9. Perintah Shell Lanjutan

### `adb shell pm grant`
**Fungsi**: Memberikan permission ke aplikasi
```
adb shell pm grant com.example.app android.permission.CAMERA
```

### `adb shell setting get`
**Fungsi**: Membaca setting sistem
```
adb shell settings get secure android_id
adb shell settings get system screen_brightness
```

### `adb shell setting put`
**Fungsi**: Mengubah setting sistem
```
adb shell settings put system screen_brightness 200
```

### `adb shell getprop`
**Fungsi**: Membaca property perangkat
```
adb shell getprop                       # Semua property
adb shell getprop ro.build.version.release  # Versi Android
```


# ADB (Android Debug Bridge)

## Penjelasan

ADB (Android Debug Bridge) adalah alat baris perintah yang memungkinkan komunikasi antara komputer dan perangkat Android. ADB adalah bagian dari Android SDK (Software Development Kit) dan digunakan untuk:

- **Debugging aplikasi** - Menguji dan memperbaiki bug dalam aplikasi Android
- **Mengontrol perangkat** - Menjalankan perintah dan operasi pada perangkat Android
- **File transfer** - Mentransfer file antara komputer dan perangkat
- **Shell access** - Mengakses shell perangkat untuk menjalankan perintah sistem
- **Instalasi aplikasi** - Menginstal APK (paket aplikasi) ke perangkat
- **Monitoring** - Memantau log dan performa perangkat

ADB bekerja dengan model klien-server:
- **Klien ADB** - Berjalan di komputer (mengirim perintah)
- **Server ADB** - Berjalan di latar belakang komputer (mengelola koneksi)
- **Daemon ADB** - Berjalan di perangkat Android (melaksanakan perintah)

## Tabel Perintah Dasar ADB

| Perintah | Deskripsi | Contoh |
|----------|-----------|--------|
| `adb devices` | Menampilkan daftar perangkat yang terhubung | `adb devices` |
| `adb connect` | Menghubungkan ke perangkat melalui jaringan | `adb connect 192.168.1.100:5555` |
| `adb disconnect` | Memutuskan koneksi dari perangkat | `adb disconnect 192.168.1.100:5555` |
| `adb push` | Mengirim file dari komputer ke perangkat | `adb push file.txt /sdcard/` |
| `adb pull` | Mengambil file dari perangkat ke komputer | `adb pull /sdcard/file.txt ./` |
| `adb install` | Menginstal aplikasi APK ke perangkat | `adb install app.apk` |
| `adb uninstall` | Menghapus aplikasi dari perangkat | `adb uninstall com.example.app` |
| `adb shell` | Mengakses shell perangkat Android | `adb shell` |
| `adb logcat` | Menampilkan log sistem perangkat | `adb logcat` |
| `adb forward` | Meneruskan port dari perangkat ke komputer | `adb forward tcp:8000 tcp:8000` |
| `adb backup` | Membuat backup data perangkat | `adb backup -all -f backup.ab` |
| `adb restore` | Memulihkan backup ke perangkat | `adb restore backup.ab` |
| `adb reboot` | Restart perangkat | `adb reboot` |
| `adb kill-server` | Menghentikan server ADB | `adb kill-server` |
| `adb start-server` | Menjalankan server ADB | `adb start-server` |

## Fungsi-Fungsi Utama ADB

### 1. **Debugging Aplikasi**
Membantu developer menemukan dan memperbaiki bug dalam aplikasi:
- Melihat log real-time (logcat)
- Mengakses stack trace error
- Menggunakan debugger

### 2. **File Management**
Mengelola file pada perangkat:
- Upload file (push)
- Download file (pull)
- Navigasi file system

### 3. **Application Management**
Mengelola aplikasi pada perangkat:
- Instalasi APK
- Uninstal aplikasi
- Launch activity

### 4. **System Control**
Mengontrol sistem perangkat:
- Restart/reboot
- Screenshot
- Record screen
- Change settings

### 5. **Performance Monitoring**
Memantau performa perangkat:
- Monitor memory usage
- CPU usage
- Battery status
- Process list

### 6. **Network & Connectivity**
Mengelola konektivitas jaringan:
- TCP/IP connection
- Port forwarding
- Network simulation


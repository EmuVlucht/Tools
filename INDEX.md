# Indeks Repository ADB

Dokumentasi lengkap tentang ADB (Android Debug Bridge) dengan penjelasan, tabel, fungsi-fungsi, dan contoh penggunaan.

## Isi Dokumentasi

### 1. **README.md** - Pengenalan ADB
   - Penjelasan umum ADB
   - Model klien-server ADB
   - Tabel perintah dasar
   - Fungsi-fungsi utama

### 2. **FUNGSI_DETIL.md** - Detail Fungsi Perintah
   - Perintah Koneksi & Device
   - Perintah File Transfer
   - Perintah Aplikasi
   - Perintah Logging & Debugging
   - Perintah Kontrol Perangkat
   - Perintah Backup & Restore
   - Perintah Port Forwarding
   - Perintah Server ADB
   - Perintah Shell Lanjutan

### 3. **CONTOH_PENGGUNAAN.md** - Praktik Penggunaan
   - Setup Awal
   - Scenario Praktis Sehari-hari (10 skenario)
   - Script Automation
   - Tips dan Trik
   - Troubleshooting

### 4. **INSTALASI.md** - Panduan Instalasi
   - Instalasi di Windows
   - Instalasi di Linux
   - Instalasi di macOS
   - Setup Perangkat Android
   - Test Instalasi
   - Troubleshooting
   - Cara Uninstall

---

## Quick Start

### 1. Instalasi ADB
Lihat **INSTALASI.md** untuk panduan lengkap sesuai OS Anda.

### 2. Hubungkan Perangkat
```bash
adb devices
```

### 3. Jalankan Perintah
Lihat **FUNGSI_DETIL.md** atau **CONTOH_PENGGUNAAN.md** untuk perintah yang ingin dijalankan.

---

## Tabel Referensi Cepat

| File | Isi | Gunakan Untuk |
|------|-----|---------------|
| README.md | Intro & Tabel Dasar | Pembelajaran awal |
| FUNGSI_DETIL.md | Referensi Fungsi | Mencari fungsi spesifik |
| CONTOH_PENGGUNAAN.md | Contoh & Script | Praktik langsung |
| INSTALASI.md | Setup & Config | Instalasi & troubleshooting |

---

## Perintah Yang Sering Digunakan

```bash
# Cek device
adb devices

# Install app
adb install app.apk

# Lihat log
adb logcat

# Transfer file
adb push file.txt /sdcard/
adb pull /sdcard/file.txt ./

# Shell access
adb shell

# Screenshot
adb shell screencap -p /sdcard/screenshot.png
```

---

## Navigasi Cepat

- **Pemula**: Mulai dari README.md → INSTALASI.md → CONTOH_PENGGUNAAN.md
- **User Menengah**: Cek FUNGSI_DETIL.md untuk perintah spesifik
- **Advanced**: Lihat script automation di CONTOH_PENGGUNAAN.md

---

## Contribution

Repository ini terbuka untuk kontribusi. Silakan fork dan buat pull request.

---

## License

Documentation Under Creative Commons Attribution 4.0

---

## Changelog

### v1.0 (Nov 2025)
- Dokumentasi lengkap ADB
- 4 file dokumentasi utama
- 10+ skenario praktis
- Script automation
- Troubleshooting guide


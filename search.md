# Search Script - Dokumentasi

Script bash untuk mencari string pada nama file/folder dan isi file dengan output berwarna, animasi disko, dan fitur exclude path.

## Fitur

- 🎨 **Animasi Disko Bergerak** - Pesan pencarian ditampilkan dengan 4 mode animasi warna
- 🔍 **Pencarian Case-Insensitive** - Mencari tanpa mempedulikan huruf besar/kecil
- 🎯 **Highlight Hasil** - Query yang ditemukan dihighlight dengan warna biru
- 📁 **Pencarian Ganda** - Mencari di nama file/folder DAN isi file
- 🌈 **Output Berwarna** - Setiap bagian memiliki warna yang berbeda untuk kemudahan membaca
- 🚫 **Exclude Paths** - Abaikan folder/file tertentu untuk mempercepat pencarian

## Instalasi

1. Download atau copy script ke file `search.sh`
2. Berikan permission execute:
   ```bash
   chmod +x search.sh
   ```

## Penggunaan

### Syntax
```bash
./search.sh [path]
```

### Contoh Penggunaan

**Mencari di direktori saat ini:**
```bash
./search.sh
```

**Mencari di direktori tertentu:**
```bash
./search.sh /sdcard/
```

**Mencari di direktori Documents:**
```bash
./search.sh ~/Documents
```

### Interaksi

#### 1. Konfigurasi Exclude (Opsional)
```
Ingin mengatur folder/file yang diabaikan? (y/n):
> y
```

Jika Anda pilih 'y', akan muncul menu:
```
=== Konfigurasi Path yang Diabaikan ===
1. Lihat daftar path yang diabaikan
2. Tambah path baru yang ingin diabaikan
3. Hapus path dari daftar
4. Reset ke default
5. Lanjut ke pencarian

Pilih (1-5):
```

#### 2. Input Query Pencarian
```
Masukan Sesuatu yang mau dicari : bug
```

## Fitur Exclude Path

### Default Excluded Paths

Script secara otomatis mengabaikan folder-folder berikut:
- `*/node_modules/*` - Dependencies Node.js
- `*/.git/*` - Git repository
- `*/.cache/*` - Cache folder
- `*/cache/*` - Cache folder
- `*/.tmp/*` - Temporary folder
- `*/tmp/*` - Temporary folder
- `*/.Trash/*` - Trash/Recycle bin
- `*/Android/data/*` - Android app data
- `*/Android/obb/*` - Android OBB files

### Menambah Exclude Path

Anda bisa menambahkan path yang ingin diabaikan dengan format:

**Pattern Wildcard:**
```
*/folder_name/*        - Abaikan folder dengan nama tertentu di mana saja
/sdcard/DCIM/*         - Abaikan semua di dalam /sdcard/DCIM/
*/backup/*/old/*       - Pattern kompleks dengan multiple wildcard
*.log                  - Abaikan semua file .log (dalam development)
```

**Contoh:**
```
Masukkan path yang ingin diabaikan:
> */Music/*
✓ Path '*/Music/*' ditambahkan ke daftar exclude
```

### Menghapus Exclude Path

1. Pilih menu "3. Hapus path dari daftar"
2. Pilih nomor path yang ingin dihapus
3. Konfirmasi

### Reset ke Default

Pilih menu "4. Reset ke default" untuk mengembalikan daftar exclude ke pengaturan awal.

## Output

### Warna Output

| Bagian | Warna | Keterangan |
|--------|-------|------------|
| Prompt input | 🟢 Hijau | "Masukan Sesuatu yang mau dicari : " |
| Pesan pencarian | 🌈 Disko | "Mencari: 'query' di: /path" dengan animasi |
| Header pencarian | 🟡 Kuning | ">>> Pencarian pada NAMA file / folder:" |
| Query match | 🔵 Biru | Setiap kemunculan query dihighlight |
| Pesan selesai | 🟢 Hijau | "Selesai." |

### Animasi Disko

Pesan "Mencari: 'query' di: /path" ditampilkan dengan 4 mode animasi:

1. **Kiri ke Kanan** → Warna bergerak dari kiri ke kanan
2. **Kanan ke Kiri** ← Warna bergerak dari kanan ke kiri
3. **Tengah ke Pinggir** ↔ Warna menyebar dari tengah ke pinggir
4. **Pinggir ke Tengah** →← Warna masuk dari pinggir ke tengah

## Contoh Output

```
Ingin mengatur folder/file yang diabaikan? (y/n):
> n

Masukan Sesuatu yang mau dicari : bug

[Animasi disko bergerak]
Mencari: 'bug' di: /sdcard/

>>> Pencarian pada NAMA file / folder:
/sdcard/Documents/de[BIRU]bug[RESET]ger.log
/sdcard/Projects/[BIRU]Bug[RESET]Report.txt

>>> Pencarian pada ISI file (rekursif):
/sdcard/notes.txt:15:This is a [BIRU]bug[RESET] report
/sdcard/code.js:42:// TODO: fix [BIRU]bug[RESET] here

Selesai.
```

## Fitur Pencarian

### 1. Pencarian Nama File/Folder
- Mencari di seluruh struktur direktori secara rekursif
- Case-insensitive (tidak peduli huruf besar/kecil)
- Menampilkan path lengkap file/folder yang cocok
- Mengabaikan path yang ada di exclude list

### 2. Pencarian Isi File
- Mencari string di dalam isi file
- Menampilkan nama file, nomor baris, dan baris yang mengandung query
- Dapat membaca file binary (ditampilkan sebagai text)
- Case-sensitive untuk konten file
- Mengabaikan direktori yang ada di exclude list

## Konfigurasi

### Mengubah Default Exclude Paths

Edit bagian ini dalam script:

```bash
EXCLUDE_PATHS=(
    "*/node_modules/*"
    "*/.git/*"
    "*/.cache/*"
    "*/cache/*"
    "*/.tmp/*"
    "*/tmp/*"
    "*/.Trash/*"
    "*/Android/data/*"
    "*/Android/obb/*"
    # Tambahkan path Anda di sini
    "*/Music/*"
    "*/Videos/*"
)
```

### Kecepatan Animasi
```bash
local frames=20      # Jumlah frame per mode (default: 20)
local delay=0.05     # Delay antar frame dalam detik (default: 0.05)
```

### Warna ANSI
```bash
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
```

## Use Cases

### Mencari tanpa folder besar
```bash
# Skip folder Music dan Videos
./search.sh /sdcard/
# Saat konfigurasi, tambahkan:
# */Music/*
# */Videos/*
```

### Mencari di project tanpa dependencies
```bash
# Default sudah exclude node_modules
./search.sh ~/Projects/myapp/
```

### Mencari log tanpa cache
```bash
# Default sudah exclude cache folders
./search.sh /var/log/
```

## Troubleshooting

### Script tidak bisa dijalankan
```bash
# Pastikan file executable
chmod +x search.sh

# Atau jalankan dengan bash
bash search.sh
```

### Animasi tidak muncul
- Pastikan terminal Anda mendukung ANSI color codes
- Coba gunakan terminal yang berbeda (seperti Termux, iTerm2, atau Terminal modern lainnya)

### Pencarian lambat
- Tambahkan lebih banyak folder ke exclude list
- Gunakan path yang lebih spesifik
- Exclude folder besar seperti Music, Videos, Downloads

### Permission denied
```bash
# Tambahkan sudo jika perlu akses root
sudo ./search.sh /root/
```

### Exclude tidak bekerja
- Pastikan pattern menggunakan wildcard yang benar
- Pattern harus match dengan path lengkap
- Gunakan `*/folder/*` untuk folder di mana saja

## Tips & Tricks

### Exclude folder spesifik sementara
```bash
# Gunakan menu konfigurasi dan pilih "n" di run berikutnya
# Atau edit EXCLUDE_PATHS langsung di script
```

### Mencari hanya di folder tertentu
```bash
# Specify path yang lebih spesifik
./search.sh /sdcard/Documents/
```

### Pattern exclude yang umum
```bash
*/.*/*           # Semua hidden folders
*/.venv/*        # Python virtual environment
*/dist/*         # Build folders
*/build/*        # Build folders
*/__pycache__/*  # Python cache
*.pyc            # Python compiled files
```

### Menyimpan hasil pencarian
```bash
./search.sh /sdcard/ > hasil.txt 2>&1
```

### Skip konfigurasi exclude
```bash
# Tekan 'n' saat ditanya konfigurasi
# Atau hapus bagian konfigurasi dari script
```

## Performa

### Faktor yang mempengaruhi kecepatan:
- Jumlah file dan folder
- Ukuran file yang di-scan
- Jumlah path di exclude list (lebih banyak = lebih cepat)
- Kecepatan disk/storage

### Tips optimasi:
- Tambahkan folder besar yang tidak perlu ke exclude
- Gunakan path pencarian yang spesifik
- Exclude file binary yang besar
- Jalankan di SSD untuk hasil lebih cepat

## Keterbatasan

- Binary files ditampilkan dalam format text (mungkin tidak readable)
- Pencarian pada direktori besar bisa memakan waktu lama
- Memerlukan permission read untuk file/folder yang dicari
- Animasi mungkin tidak berfungsi di terminal yang tidak mendukung ANSI
- Exclude pattern menggunakan glob pattern (bukan regex)

## Lisensi

Script ini bebas digunakan dan dimodifikasi sesuai kebutuhan.

## Changelog

### Version 1.1
- ➕ Tambah fitur exclude paths
- ➕ Menu interaktif untuk konfigurasi exclude
- ➕ Default exclude untuk folder umum
- ⚡ Peningkatan performa dengan skip folder yang tidak perlu

### Version 1.0
- 🎉 Release awal dengan fitur dasar
- 🎨 Animasi disko
- 🔍 Pencarian case-insensitive
- 🎯 Highlight hasil

## Kontributor

Dibuat dengan secangkir Teh menggunakan Bash

---

**Versi:** 1.1  
**Terakhir diupdate:** Januari 2025

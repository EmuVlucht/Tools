```markdown
# Search Script - Dokumentasi

Script bash untuk mencari string pada nama file/folder dan isi file dengan output berwarna dan animasi disko.

## Fitur

- 🎨 **Animasi Disko Bergerak** - Pesan pencarian ditampilkan dengan 4 mode animasi warna
- 🔍 **Pencarian Case-Insensitive** - Mencari tanpa mempedulikan huruf besar/kecil
- 🎯 **Highlight Hasil** - Query yang ditemukan dihighlight dengan warna biru
- 📁 **Pencarian Ganda** - Mencari di nama file/folder DAN isi file
- 🌈 **Output Berwarna** - Setiap bagian memiliki warna yang berbeda untuk kemudahan membaca

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

Setelah menjalankan script, Anda akan diminta memasukkan query pencarian:
```
Masukan Sesuatu yang mau dicari : bug
```

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
Masukan Sesuatu yang mau dicari : bug

[Animasi disko bergerak]
Mencari: 'bug' di: /sdcard/

>>> Pencarian pada NAMA file / folder:
/sdcard/Documents/de[BIRU]bug[RESET]ger.log
/sdcard/Android/[BIRU]Bug[RESET]Report.txt

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

### 2. Pencarian Isi File
- Mencari string di dalam isi file
- Menampilkan nama file, nomor baris, dan baris yang mengandung query
- Dapat membaca file binary (ditampilkan sebagai text)
- Case-sensitive untuk konten file

## Konfigurasi

Anda dapat mengubah beberapa parameter dalam script:

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
- Batasi direktori pencarian ke area yang lebih spesifik
- Gunakan path yang lebih spesifik daripada root directory

### Permission denied
```bash
# Tambahkan sudo jika perlu akses root
sudo ./search.sh /root/
```

## Keterbatasan

- Binary files ditampilkan dalam format text (mungkin tidak readable)
- Pencarian pada direktori besar bisa memakan waktu lama
- Memerlukan permission read untuk file/folder yang dicari
- Animasi mungkin tidak berfungsi di terminal yang tidak mendukung ANSI

## Tips & Tricks

### Mencari file dengan ekstensi tertentu
```bash
# Setelah menjalankan script, ketik ekstensi:
.pdf
.txt
.log
```

### Mencari di multiple direktori
```bash
# Jalankan script beberapa kali atau gunakan loop:
for dir in /sdcard/Documents /sdcard/Downloads; do
    ./search.sh "$dir"
done
```

### Menyimpan hasil pencarian
```bash
./search.sh /sdcard/ > hasil.txt 2>&1
```

### Mencari kata yang mengandung spasi
```bash
# Input: bug report
# Script akan mencari "bug report" secara literal
```

## Lisensi

Script ini bebas digunakan dan dimodifikasi sesuai kebutuhan.

## Kontributor

Dibuat dengan ❤️ menggunakan Bash

---

**Versi:** 1.0  
**Terakhir diupdate:** Desember 2024
```
# Termux Backup Guide (Complete)

**Dokumentasi lengkap untuk backup, migrasi, dan restore Termux environment**

---

## 📚 Table of Contents

1. [Introduction](#1-introduction)
2. [Quick Start (TL;DR)](#2-quick-start-tldr)
3. [What to Backup](#3-what-to-backup)
4. [Backup Methods](#4-backup-methods)
5. [Transfer Methods](#5-transfer-methods)
6. [Automated Scripts](#6-automated-scripts)
7. [Restore Procedures](#7-restore-procedures)
8. [Troubleshooting](#8-troubleshooting)
9. [Advanced Topics](#9-advanced-topics)

---

## 1. Introduction

### 1.1 Apa yang Di-backup?

Dokumentasi ini membahas backup **aplikasi dan environment**, bukan data user (seperti foto, video, dokumen). Analogi: backup aplikasi kamera-nya, bukan foto hasil jepretannya.

Yang di-backup:
- **Binary executables** (`$PREFIX/bin/`)
- **Libraries** (`$PREFIX/lib/`)
- **Package lists** (daftar yang terinstall)
- **Configuration files** (`.bashrc`, `.zshrc`, dll)
- **Symlinks** (link antar file)
- **Dependencies** (package yang dibutuhkan)

### 1.2 Kapan Butuh Backup?

- 🔄 **Migrasi ke HP baru**
- 💾 **Recovery plan** (jaga-jaga HP rusak)
- 🧪 **Duplikasi environment** (punya setup identik di banyak device)
- 🚀 **Before major upgrade** (sebelum upgrade Termux/Android)
- 📦 **Distribusi environment** (share setup ke tim/teman)

### 1.3 Perbedaan Backup List vs Backup Binary

| Aspek | Backup List | Backup Binary |
|-------|-------------|---------------|
| **Ukuran** | Kecil (KB) | Besar (MB-GB) |
| **Kecepatan** | Cepat | Lambat |
| **Internet** | Butuh (saat restore) | Tidak butuh |
| **Kompatibilitas** | Cross-architecture OK | Harus sama (arm64/x86) |
| **Kelebihan** | Selalu dapat versi terbaru | Offline-friendly, cepat restore |
| **Kekurangan** | Butuh download ulang | File besar, versi freeze |

**Rekomendasi:** Backup keduanya! List untuk flexibility, binary untuk speed.

---

## 2. Quick Start (TL;DR)

### 2.1 Full Backup (One Command)

```bash
# Download backup script
curl -O https://raw.githubusercontent.com/yourrepo/termux-backup.sh
chmod +x termux-backup.sh

# Jalankan backup
./termux-backup.sh
```

Output: `/sdcard/backup/termux-backup-[timestamp]/`

### 2.2 Full Restore (One Command)

```bash
# Download restore script
curl -O https://raw.githubusercontent.com/yourrepo/termux-restore.sh
chmod +x termux-restore.sh

# Jalankan restore
./termux-restore.sh /sdcard/backup/termux-backup-YYYYMMDD-HHMMSS/
```

---

## 3. What to Backup

### 3.1 Struktur Direktori Termux

```
$PREFIX = /data/data/com.termux/files/usr/

├── bin/           # Binary executables
├── lib/           # Shared libraries
├── share/         # Data files, docs
├── etc/           # Configuration files
├── var/           # Variable data (logs, cache)
└── tmp/           # Temporary files
```

### 3.2 Home Directory

```
$HOME = /data/data/com.termux/files/home/

├── .bashrc        # Bash configuration
├── .zshrc         # Zsh configuration
├── .termux/       # Termux-specific config
├── .config/       # App configurations
├── .local/        # Local data
└── storage/       # Symlink ke Android storage
```

### 3.3 Package Managers & Tools

| Tool | Command | Config Location |
|------|---------|----------------|
| **apt/pkg** | `apt list --installed` | `/data/data/com.termux/files/usr/var/lib/apt/` |
| **pip** | `pip freeze` | `~/.local/lib/pythonX.X/site-packages/` |
| **npm** | `npm list -g --depth=0` | `$PREFIX/lib/node_modules/` |
| **cargo** | `cargo install --list` | `~/.cargo/bin/` |
| **gem** | `gem list` | `$PREFIX/lib/ruby/gems/` |
| **composer** | `composer global show` | `~/.composer/` |
| **go** | `go list -m all` | `~/go/bin/` |

---

## 4. Backup Methods

### 4.1 Package List Backup

#### 4.1.1 APT/PKG (Termux Native)

```bash
# Backup
pkg list-installed > /sdcard/backup/pkg-list.txt

# Alternative dengan detail versi
dpkg --get-selections > /sdcard/backup/dpkg-selections.txt

# Restore
pkg install $(cat /sdcard/backup/pkg-list.txt | awk '{print $1}')
```

#### 4.1.2 Python (pip)

```bash
# Backup
pip freeze > /sdcard/backup/pip-requirements.txt

# Backup dengan hash (lebih aman)
pip freeze --all > /sdcard/backup/pip-all.txt

# Restore
pip install -r /sdcard/backup/pip-requirements.txt
```

#### 4.1.3 Node.js (npm)

```bash
# Backup global packages
npm list -g --depth=0 --json > /sdcard/backup/npm-global.json

# Backup dengan parsing sederhana
npm list -g --depth=0 | grep -v npm | awk '{print $2}' | grep -v "^$" > /sdcard/backup/npm-list.txt

# Restore
cat /sdcard/backup/npm-list.txt | xargs npm install -g
```

#### 4.1.4 Rust (cargo)

```bash
# Backup
cargo install --list | grep -E '^[a-z]' | awk '{print $1}' > /sdcard/backup/cargo-list.txt

# Restore
cat /sdcard/backup/cargo-list.txt | xargs cargo install
```

#### 4.1.5 Ruby (gem)

```bash
# Backup
gem list > /sdcard/backup/gem-list.txt

# Backup dengan versi
gem list --local --no-versions | sed 's/ /,/g' > /sdcard/backup/gem-list-versioned.txt

# Restore
cat /sdcard/backup/gem-list.txt | awk '{print $1}' | xargs gem install
```

#### 4.1.6 PHP (composer)

```bash
# Backup global packages
composer global show --name-only > /sdcard/backup/composer-global.txt

# Restore
cat /sdcard/backup/composer-global.txt | xargs -I {} composer global require {}
```

#### 4.1.7 Go

```bash
# Backup installed binaries
ls ~/go/bin > /sdcard/backup/go-binaries.txt

# Manual restore (tidak ada cara otomatis karena Go tidak punya package manager seperti npm)
# User harus install ulang dengan `go install package@version`
```

#### 4.1.8 Linux Package Managers (jika di proot/chroot)

```bash
# DNF (Fedora, RHEL)
dnf list installed > /sdcard/backup/dnf-list.txt

# YUM (RHEL lama, CentOS)
yum list installed > /sdcard/backup/yum-list.txt

# Pacman (Arch Linux, Manjaro)
pacman -Qqe > /sdcard/backup/pacman-explicit.txt
pacman -Qqm > /sdcard/backup/pacman-aur.txt

# Zypper (openSUSE)
zypper search --installed-only > /sdcard/backup/zypper-list.txt

# APK (Alpine Linux)
apk info > /sdcard/backup/apk-list.txt

# Emerge (Gentoo)
qlist -I > /sdcard/backup/gentoo-packages.txt
```

#### 4.1.9 Alternative JavaScript Package Managers

```bash
# Yarn
yarn global list > /sdcard/backup/yarn-global.txt

# pnpm
pnpm list -g --depth=0 > /sdcard/backup/pnpm-global.txt

# Bun
bun pm ls --global > /sdcard/backup/bun-global.txt
```

#### 4.1.10 Python Alternative Managers

```bash
# Poetry
poetry show --tree > /sdcard/backup/poetry-deps.txt

# Conda
conda list --export > /sdcard/backup/conda-packages.txt

# Pipx (isolated CLI tools)
pipx list > /sdcard/backup/pipx-list.txt
```

#### 4.1.11 Windows Package Managers (via WSL/proot)

```bash
# Winget (Windows Package Manager)
winget export -o /sdcard/backup/winget-packages.json

# Chocolatey
choco list --local-only > /sdcard/backup/choco-packages.txt

# Scoop
scoop export > /sdcard/backup/scoop-packages.json
```

#### 4.1.12 Container & Virtualization

```bash
# Docker images
docker images --format "{{.Repository}}:{{.Tag}}" > /sdcard/backup/docker-images.txt

# Podman
podman images --format "{{.Repository}}:{{.Tag}}" > /sdcard/backup/podman-images.txt

# Helm (Kubernetes)
helm list --all-namespaces > /sdcard/backup/helm-releases.txt
```

#### 4.1.13 Android-Specific

```bash
# Termux (pkg adalah wrapper apt)
pkg list-all > /sdcard/backup/pkg-all-available.txt

# Homebrew (bisa di Android via Termux mod)
brew list > /sdcard/backup/brew-list.txt

# Snap (jika tersedia via proot)
snap list > /sdcard/backup/snap-list.txt

# Flatpak (jika tersedia via proot)
flatpak list > /sdcard/backup/flatpak-list.txt
```

### 4.2 Binary Backup (Direct Copy)

#### 4.2.1 Backup $PREFIX/bin dengan Symlink Handling

```bash
# 1. Simpan daftar symlink
find $PREFIX/bin -type l -printf "%p -> %l\n" > /sdcard/backup/symlink-bin.txt

# 2. Copy semua binary (follow symlink jadi file asli)
mkdir -p /sdcard/backup/bin
cp -rL $PREFIX/bin/* /sdcard/backup/bin/

# 3. Compress ke tar.gz
cd /sdcard/backup
tar -czf bin-backup.tar.gz bin/ symlink-bin.txt
rm -rf bin/
```

#### 4.2.2 Backup $PREFIX/lib

```bash
# 1. Simpan symlink libraries
find $PREFIX/lib -type l -printf "%p -> %l\n" > /sdcard/backup/symlink-lib.txt

# 2. Copy libraries (HATI-HATI: ukuran bisa sangat besar!)
mkdir -p /sdcard/backup/lib
cp -rL $PREFIX/lib/* /sdcard/backup/lib/

# 3. Compress
cd /sdcard/backup
tar -czf lib-backup.tar.gz lib/ symlink-lib.txt
rm -rf lib/
```

#### 4.2.3 Backup $PREFIX/share

```bash
mkdir -p /sdcard/backup/share
cp -r $PREFIX/share/* /sdcard/backup/share/
cd /sdcard/backup
tar -czf share-backup.tar.gz share/
rm -rf share/
```

#### 4.2.4 Backup $PREFIX/etc (Configuration)

```bash
mkdir -p /sdcard/backup/etc
cp -r $PREFIX/etc/* /sdcard/backup/etc/
cd /sdcard/backup
tar -czf etc-backup.tar.gz etc/
rm -rf etc/
```

### 4.3 Home Directory Backup

```bash
# Backup configuration files
mkdir -p /sdcard/backup/home-config

# Bash/Zsh
cp ~/.bashrc ~/.bash_profile ~/.zshrc /sdcard/backup/home-config/ 2>/dev/null

# Termux-specific
cp -r ~/.termux /sdcard/backup/home-config/

# Other configs (selective)
cp -r ~/.config /sdcard/backup/home-config/
cp -r ~/.local /sdcard/backup/home-config/

# Compress
cd /sdcard/backup
tar -czf home-config-backup.tar.gz home-config/
rm -rf home-config/
```

### 4.4 Combined Backup Strategy

```bash
# Folder struktur yang direkomendasikan
/sdcard/backup/
├── package-lists/
│   ├── pkg-list.txt
│   ├── pip-requirements.txt
│   ├── npm-list.txt
│   ├── cargo-list.txt
│   └── ... (semua list lainnya)
├── bin-backup.tar.gz
├── lib-backup.tar.gz
├── share-backup.tar.gz
├── etc-backup.tar.gz
├── home-config-backup.tar.gz
└── backup-info.txt  # Metadata backup
```

---

## 5. Transfer Methods

### 5.1 Physical Media

#### 5.1.1 Flashdisk / USB OTG

**Kelebihan:**
- Kapasitas besar (8GB - 256GB+)
- Cepat (USB 3.0: ~100MB/s)
- Universal (hampir semua HP support)

**Kekurangan:**
- Butuh OTG adapter (kecuali USB-C native)
- File system FAT32 limit 4GB per file

**Cara:**

```bash
# 1. Deteksi USB OTG di Termux
termux-usb -l

# 2. Mount USB (biasanya auto-mount di /storage atau /mnt)
# Jika tidak auto-mount, cek di file manager

# 3. Copy backup
cp -r /sdcard/backup/* /storage/usb-otg/termux-backup/

# Atau langsung extract tar.gz ke USB
tar -xzf /sdcard/backup/bin-backup.tar.gz -C /storage/usb-otg/
```

**Catatan FAT32 4GB Limit:**
Jika backup file > 4GB, split dulu:

```bash
# Split file besar jadi chunk 3GB
split -b 3G bin-backup.tar.gz bin-backup.tar.gz.part

# Gabungkan lagi di HP tujuan
cat bin-backup.tar.gz.part* > bin-backup.tar.gz
```

#### 5.1.2 Memory Card (SD Card)

**Kelebihan:**
- Tidak butuh OTG
- Permanen (bisa dijadikan backup storage)
- Kapasitas besar tersedia

**Kekurangan:**
- Banyak HP modern tidak punya slot SD
- Kecepatan tergantung class (Class 10 / UHS: ~90MB/s)

**Cara:**

```bash
# SD Card biasanya auto-mount di /storage/XXXX-XXXX
ls /storage/

# Copy backup
cp -r /sdcard/backup /storage/XXXX-XXXX/termux-backup
```

#### 5.1.3 Kabel Data USB (File Transfer Mode)

**Kelebihan:**
- Tidak butuh adapter tambahan
- Bisa langsung ke PC/Laptop
- Cepat (USB 3.0: ~100MB/s)

**Kekurangan:**
- Butuh PC sebagai perantara
- Tidak direct phone-to-phone

**Cara:**

```bash
# Di HP: Enable File Transfer Mode (MTP)
# Di PC: Akses HP via File Explorer/Finder

# Copy dari HP ke PC
PC: /Phones/YourPhone/Internal Storage/backup/ → PC: /backups/termux/

# Copy dari PC ke HP tujuan
PC: /backups/termux/ → PC: /Phones/NewPhone/Internal Storage/backup/
```

### 5.2 Wireless Transfer (Short Range)

#### 5.2.1 Bluetooth

**Kelebihan:**
- Universal (semua HP punya)
- Tidak butuh internet
- Pairing sekali, selanjutnya otomatis

**Kekurangan:**
- **Sangat lambat** (~1-3MB/s, praktis < 1MB/s)
- Tidak cocok untuk backup besar (>100MB)
- Timeout untuk file besar

**Cara:**

```bash
# Install bluetooth tools di Termux (opsional)
pkg install bluez-utils

# Via Android Share Menu (termudah):
# 1. Buka file manager
# 2. Pilih file backup
# 3. Share → Bluetooth → Pilih device tujuan

# Estimasi waktu transfer:
# 100MB backup ≈ 2-5 menit
# 1GB backup ≈ 20-60 menit (TIDAK DIREKOMENDASIKAN)
```

**Rekomendasi:** Gunakan Bluetooth hanya untuk package-lists (file kecil < 10MB).

#### 5.2.2 Wi-Fi Direct

**Kelebihan:**
- Cepat (~10-25MB/s, bisa sampai 250MB/s pada Wi-Fi 6)
- Tidak butuh router
- Tidak konsumsi kuota internet

**Kekurangan:**
- Setup agak rumit
- Tidak semua HP support dengan baik
- Kadang putus koneksi

**Cara (via Termux):**

```bash
# Install HTTP server sederhana
pkg install python

# Di HP sumber (server):
cd /sdcard/backup
python -m http.server 8000

# Cek IP address HP sumber
ifconfig wlan0 | grep "inet "
# Contoh output: inet 192.168.49.1

# Di HP tujuan (client):
# 1. Connect ke Wi-Fi Direct HP sumber
# 2. Download via browser: http://192.168.49.1:8000
# Atau via wget:
wget -r -np -nH --cut-dirs=1 http://192.168.49.1:8000/
```

#### 5.2.3 Quick Share / Nearby Share (Android)

**Kelebihan:**
- **Sangat cepat** (20-50MB/s untuk file besar)
- User-friendly (drag & drop)
- Support file besar
- Auto-resume jika terputus

**Kekurangan:**
- Hanya untuk Android ke Android (atau Windows dengan app Google)
- Butuh Bluetooth + Wi-Fi aktif (tapi tidak butuh internet)

**Cara:**

```bash
# 1. Pastikan Bluetooth & Wi-Fi ON di kedua HP
# 2. Buka file manager
# 3. Select file/folder backup
# 4. Share → Nearby Share / Quick Share
# 5. Pilih device tujuan
# 6. Terima di HP tujuan

# Estimasi waktu:
# 1GB backup ≈ 30 detik - 2 menit
# 10GB backup ≈ 5-10 menit
```

**Rekomendasi:** **Metode terbaik** untuk backup besar Android-to-Android!

#### 5.2.4 AirDrop (iOS/macOS) - Limited Support

**Kelebihan:**
- Sangat cepat (~50MB/s+)
- Seamless integration di ekosistem Apple

**Kekurangan:**
- **Tidak support langsung dari Android**
- Butuh device Apple sebagai perantara

**Workaround:**

```bash
# Android → Mac → Android (via AirDrop + Quick Share):
# 1. Share dari Android ke Mac via cable/cloud
# 2. AirDrop dari Mac ke iPhone
# 3. Quick Share dari iPhone ke Android (tidak bisa langsung, butuh cloud)

# Kesimpulan: TIDAK PRAKTIS untuk Android Termux backup
```

#### 5.2.5 NFC (Near Field Communication)

**Kelebihan:**
- Sangat mudah (tap HP)
- Tidak butuh pairing

**Kekurangan:**
- **Sangat lambat** (~424 kbps teoritis, praktis ~100 kbps)
- **Hanya untuk file sangat kecil** (< 1MB)
- Range sangat pendek (~4cm)

**Rekomendasi:** **JANGAN GUNAKAN untuk backup Termux!** NFC hanya cocok untuk:
- Transfer kontak
- Pairing device (kemudian switch ke Bluetooth/Wi-Fi)
- File teks kecil

**Estimasi waktu (hipotetis):**
- 1MB ≈ 1-2 menit
- 100MB ≈ **2-3 JAM**
- 1GB ≈ **20-30 JAM** (tidak realistis)

#### 5.2.6 Infrared (IR)

**Kelebihan:**
- Tidak butuh pairing
- Simple

**Kekurangan:**
- **OBSOLETE** (hampir tidak ada HP modern dengan IR)
- **Sangat lambat** (~115 kbps untuk IrDA, praktis < 10 kbps)
- Harus line-of-sight, tidak boleh terhalang

**Rekomendasi:** **JANGAN GUNAKAN!** Teknologi sudah mati sejak ~2015.

#### 5.2.7 Ultra Wideband (UWB)

**Kelebihan:**
- **Sangat cepat** (teoritis 500Mbps+)
- Presisi lokasi tinggi (< 10cm)
- Low latency

**Kekurangan:**
- **Hanya di flagship HP** (Samsung S21+, iPhone 11+, Google Pixel 6+)
- Belum banyak app yang support transfer file via UWB murni
- Biasanya UWB hanya untuk lokasi, file transfer tetap via Wi-Fi

**Cara (terintegrasi dalam Quick Share/AirDrop):**

```bash
# UWB digunakan untuk:
# 1. Deteksi device terdekat dengan presisi
# 2. Arahkan HP satu sama lain untuk faster pairing
# 3. Kemudian transfer tetap via Wi-Fi Direct

# User tidak perlu setup khusus, Quick Share otomatis pakai UWB jika tersedia
```

**Rekomendasi:** Gunakan Quick Share seperti biasa, UWB akan otomatis aktif jika HP support.

### 5.3 Wireless Transfer (Internet-Based)

#### 5.3.1 Wi-Fi Hotspot Transfer (LAN Transfer)

**Kelebihan:**
- Cepat (~20-50MB/s, tergantung router)
- Tidak konsumsi kuota internet jika lokal
- Reliable

**Kekurangan:**
- Butuh router atau HP sebagai hotspot
- Setup agak teknis

**Cara (via HTTP Server):**

```bash
# Di HP sumber:
pkg install python
cd /sdcard/backup
python -m http.server 8000

# Cek IP HP sumber (harus di network yang sama)
ip addr show wlan0 | grep inet
# Contoh: 192.168.1.100

# Di HP tujuan (via browser):
# Buka: http://192.168.1.100:8000

# Atau via wget:
wget -r -np -nH --cut-dirs=1 http://192.168.1.100:8000/
```

**Cara (via FTP Server - lebih cepat):**

```bash
# Install FTP server
pkg install vsftpd

# Start FTP server (anonymous)
vsftpd &

# Di HP tujuan:
# Install FTP client (atau via Total Commander, dll)
# Connect ke: ftp://192.168.1.100
```

#### 5.3.2 Cloud Storage (Google Drive, Dropbox, dll)

**Kelebihan:**
- Universal access
- Automatic backup history
- Tidak butuh kedua HP online bersamaan

**Kekurangan:**
- **Konsumsi kuota internet**
- Tergantung kecepatan upload/download
- Limit storage (free tier biasanya 5-15GB)

**Cara:**

```bash
# Install rclone (universal cloud sync tool)
pkg install rclone

# Config rclone (one-time setup)
rclone config
# Pilih provider: Google Drive / Dropbox / OneDrive / dll

# Upload backup
rclone copy /sdcard/backup gdrive:termux-backup/ -P

# Download di HP tujuan
rclone copy gdrive:termux-backup/ /sdcard/backup/ -P
```

### 5.4 Comparison Table

| Metode | Kecepatan | Ukuran Max | Range | Rekomendasi |
|--------|-----------|------------|-------|-------------|
| **USB OTG** | ⚡⚡⚡⚡⚡ 100MB/s | 🔥 Unlimited | 📏 Cable | ✅ TERBAIK untuk backup besar |
| **Quick Share** | ⚡⚡⚡⚡ 30MB/s | 🔥 Unlimited | 📏 ~10m | ✅ TERBAIK untuk wireless |
| **Wi-Fi Direct** | ⚡⚡⚡ 15MB/s | ✔️ Besar | 📏 ~50m | ✅ Bagus |
| **Wi-Fi Hotspot** | ⚡⚡⚡ 20MB/s | ✔️ Besar | 📏 ~100m | ✅ Bagus |
| **SD Card** | ⚡⚡⚡ 50MB/s | 🔥 Unlimited | 📏 N/A | ✅ Bagus untuk arsip |
| **Kabel USB** | ⚡⚡⚡⚡⚡ 100MB/s | 🔥 Unlimited | 📏 Cable | ✅ Bagus (butuh PC) |
| **Bluetooth** | ⚡ 1MB/s | ⚠️ <100MB | 📏 ~10m | ⚠️ Hanya file kecil |
| **Cloud (rclone)** | ⚡⚡ 5-20MB/s | ⚠️ Limit quota | 🌐 Internet | ⚠️ Konsumsi kuota |
| **NFC** | 🐌 0.1MB/s | ❌ <1MB | 📏 ~4cm | ❌ JANGAN |
| **Infrared** | 🐌 0.01MB/s | ❌ <1MB | 📏 Line-of-sight | ❌ OBSOLETE |
| **UWB** | N/A | N/A | 📏 ~10m | ℹ️ Integrated di Quick Share |

**Rekomendasi Final:**
1. **Backup besar (>1GB):** USB OTG atau SD Card
2. **Wireless cepat:** Quick Share / Nearby Share
3. **File kecil (<100MB):** Bluetooth OK
4. **Remote backup:** Cloud + rclone

---

## 6. Automated Scripts

### 6.1 Full Backup Script

Simpan sebagai `termux-backup.sh`:

```bash
#!/data/data/com.termux/files/usr/bin/bash

# Termux Full Backup Script
# Author: Your Name
# Version: 1.0

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="/sdcard/backup/termux-backup-$TIMESTAMP"

echo -e "${GREEN}=== Termux Backup Script ===${NC}"
echo "Backup akan disimpan di: $BACKUP_DIR"
echo ""

# Create backup directory structure
mkdir -p "$BACKUP_DIR/package-lists"
mkdir -p "$BACKUP_DIR/archives"

echo -e "${YELLOW}[1/8] Backing up package lists...${NC}"

# APT/PKG
echo "  - pkg list..."
pkg list-installed > "$BACKUP_DIR/package-lists/pkg-list.txt"
dpkg --get-selections > "$BACKUP_DIR/package-lists/dpkg-selections.txt"

# Python pip
if command -v pip &> /dev/null; then
    echo "  - pip freeze..."
    pip freeze > "$BACKUP_DIR/package-lists/pip-requirements.txt" 2>/dev/null || echo "pip: no packages"
fi

# Node.js npm
if command -v npm &> /dev/null; then
    echo "  - npm list..."
    npm list -g --depth=0 2>/dev/null | grep -v npm | awk '{print $2}' | grep -v "^$" > "$BACKUP_DIR/package-lists/npm-list.txt" || echo "npm: no packages"
fi

# Rust cargo
if command -v cargo &> /dev/null; then
    echo "  - cargo list..."
    cargo install --list 2>/dev/null | grep -E '^[a-z]' | awk '{print $1}' > "$BACKUP_DIR/package-lists/cargo-list.txt" || echo "cargo: no packages"
fi

# Ruby gem
if command -v gem &> /dev/null; then
    echo "  - gem list..."
    gem list --no-versions > "$BACKUP_DIR/package-lists/gem-list.txt" 2>/dev/null || echo "gem: no packages"
fi

# PHP composer
if command -v composer &> /dev/null; then
    echo "  - composer global..."
    composer global show --name-only > "$BACKUP_DIR/package-lists/composer-global.txt" 2>/dev/null || echo "composer: no packages"
fi

# Go binaries
if [ -d "$HOME/go/bin" ]; then
    echo "  - go binaries..."
    ls "$HOME/go/bin" > "$BACKUP_DIR/package-lists/go-binaries.txt" 2>/dev/null || echo "go: no binaries"
fi

# Yarn
if command -v yarn &> /dev/null; then
    echo "  - yarn global..."
    yarn global list 2>/dev/null | grep -E '^\s+' | awk '{print $2}' > "$BACKUP_DIR/package-lists/yarn-global.txt" || echo "yarn: no packages"
fi

# pnpm
if command -v pnpm &> /dev/null; then
    echo "  - pnpm global..."
    pnpm list -g --depth=0 2>/dev/null | grep -v pnpm | awk '{print $2}' > "$BACKUP_DIR/package-lists/pnpm-global.txt" || echo "pnpm: no packages"
fi

# Poetry
if command -v poetry &> /dev/null; then
    echo "  - poetry packages..."
    poetry show --tree > "$BACKUP_DIR/package-lists/poetry-deps.txt" 2>/dev/null || echo "poetry: no packages"
fi

# Pipx
if command -v pipx &> /dev/null; then
    echo "  - pipx list..."
    pipx list > "$BACKUP_DIR/package-lists/pipx-list.txt" 2>/dev/null || echo "pipx: no packages"
fi

echo -e "${GREEN}✓ Package lists saved${NC}\n"

echo -e "${YELLOW}[2/8] Backing up $PREFIX/bin...${NC}"
# Save symlinks
find $PREFIX/bin -type l -printf "%p -> %l\n" > "$BACKUP_DIR/archives/symlink-bin.txt"
# Create temporary directory
mkdir -p /data/data/com.termux/files/tmp-backup/bin
cp -rL $PREFIX/bin/* /data/data/com.termux/files/tmp-backup/bin/ 2>/dev/null || true
# Compress
tar -czf "$BACKUP_DIR/archives/bin-backup.tar.gz" -C /data/data/com.termux/files/tmp-backup bin
rm -rf /data/data/com.termux/files/tmp-backup/bin
echo -e "${GREEN}✓ bin archived${NC}\n"

echo -e "${YELLOW}[3/8] Backing up $PREFIX/lib...${NC}"
echo "  (This may take a while due to large size)"
find $PREFIX/lib -type l -printf "%p -> %l\n" > "$BACKUP_DIR/archives/symlink-lib.txt"
mkdir -p /data/data/com.termux/files/tmp-backup/lib
cp -rL $PREFIX/lib/* /data/data/com.termux/files/tmp-backup/lib/ 2>/dev/null || true
tar -czf "$BACKUP_DIR/archives/lib-backup.tar.gz" -C /data/data/com.termux/files/tmp-backup lib
rm -rf /data/data/com.termux/files/tmp-backup/lib
echo -e "${GREEN}✓ lib archived${NC}\n"

echo -e "${YELLOW}[4/8] Backing up $PREFIX/share...${NC}"
mkdir -p /data/data/com.termux/files/tmp-backup/share
cp -r $PREFIX/share/* /data/data/com.termux/files/tmp-backup/share/ 2>/dev/null || true
tar -czf "$BACKUP_DIR/archives/share-backup.tar.gz" -C /data/data/com.termux/files/tmp-backup share
rm -rf /data/data/com.termux/files/tmp-backup/share
echo -e "${GREEN}✓ share archived${NC}\n"

echo -e "${YELLOW}[5/8] Backing up $PREFIX/etc...${NC}"
mkdir -p /data/data/com.termux/files/tmp-backup/etc
cp -r $PREFIX/etc/* /data/data/com.termux/files/tmp-backup/etc/ 2>/dev/null || true
tar -czf "$BACKUP_DIR/archives/etc-backup.tar.gz" -C /data/data/com.termux/files/tmp-backup etc
rm -rf /data/data/com.termux/files/tmp-backup/etc
echo -e "${GREEN}✓ etc archived${NC}\n"

echo -e "${YELLOW}[6/8] Backing up home config...${NC}"
mkdir -p /data/data/com.termux/files/tmp-backup/home-config
# Bash/Zsh configs
cp ~/.bashrc ~/.bash_profile ~/.zshrc /data/data/com.termux/files/tmp-backup/home-config/ 2>/dev/null || true
# Termux specific
cp -r ~/.termux /data/data/com.termux/files/tmp-backup/home-config/ 2>/dev/null || true
# Other configs
cp -r ~/.config /data/data/com.termux/files/tmp-backup/home-config/ 2>/dev/null || true
cp -r ~/.local /data/data/com.termux/files/tmp-backup/home-config/ 2>/dev/null || true
tar -czf "$BACKUP_DIR/archives/home-config-backup.tar.gz" -C /data/data/com.termux/files/tmp-backup home-config
rm -rf /data/data/com.termux/files/tmp-backup/home-config
echo -e "${GREEN}✓ home config archived${NC}\n"

echo -e "${YELLOW}[7/8] Creating backup metadata...${NC}"
cat > "$BACKUP_DIR/backup-info.txt" << EOF
Termux Backup Information
=========================
Date: $(date)
Hostname: $(hostname)
Architecture: $(uname -m)
Kernel: $(uname -r)
Termux Version: $(termux-info | grep "TERMUX_VERSION" | cut -d'"' -f2)

Backup Contents:
- Package lists (apt, pip, npm, cargo, etc)
- Binary executables ($PREFIX/bin)
- Libraries ($PREFIX/lib)
- Shared files ($PREFIX/share)
- Configuration files ($PREFIX/etc)
- Home configuration (~/.bashrc, ~/.termux, etc)

Total Size: $(du -sh "$BACKUP_DIR" | cut -f1)

Restore Command:
./termux-restore.sh $BACKUP_DIR
EOF
echo -e "${GREEN}✓ Metadata created${NC}\n"

echo -e "${YELLOW}[8/8] Calculating backup size...${NC}"
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo -e "${GREEN}✓ Backup completed!${NC}\n"

echo "=========================================="
echo -e "${GREEN}Backup Summary:${NC}"
echo "Location: $BACKUP_DIR"
echo "Total Size: $BACKUP_SIZE"
echo ""
echo "Files created:"
echo "  - package-lists/ (package managers)"
echo "  - archives/bin-backup.tar.gz"
echo "  - archives/lib-backup.tar.gz"
echo "  - archives/share-backup.tar.gz"
echo "  - archives/etc-backup.tar.gz"
echo "  - archives/home-config-backup.tar.gz"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Transfer folder ke HP tujuan (via USB/Quick Share/dll)"
echo "2. Run: ./termux-restore.sh $BACKUP_DIR"
echo "=========================================="
```

Simpan dan jalankan:

```bash
chmod +x termux-backup.sh
./termux-backup.sh
```

### 6.2 Full Restore Script

Simpan sebagai `termux-restore.sh`:

```bash
#!/data/data/com.termux/files/usr/bin/bash

# Termux Full Restore Script
# Author: Your Name
# Version: 1.0

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check argument
if [ -z "$1" ]; then
    echo -e "${RED}Error: Backup directory not specified${NC}"
    echo "Usage: ./termux-restore.sh /sdcard/backup/termux-backup-YYYYMMDD-HHMMSS"
    exit 1
fi

BACKUP_DIR="$1"

# Validate backup directory
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}Error: Backup directory not found: $BACKUP_DIR${NC}"
    exit 1
fi

if [ ! -f "$BACKUP_DIR/backup-info.txt" ]; then
    echo -e "${RED}Warning: backup-info.txt not found. This may not be a valid backup.${NC}"
    read -p "Continue anyway? (y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        exit 1
    fi
fi

echo -e "${GREEN}=== Termux Restore Script ===${NC}"
echo "Restore from: $BACKUP_DIR"
echo ""

# Show backup info if exists
if [ -f "$BACKUP_DIR/backup-info.txt" ]; then
    echo -e "${BLUE}Backup Information:${NC}"
    cat "$BACKUP_DIR/backup-info.txt"
    echo ""
fi

read -p "Start restore? (y/N): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Restore cancelled."
    exit 0
fi

echo ""
echo -e "${YELLOW}[1/7] Restoring package lists...${NC}"

# Function to restore packages from list
restore_packages() {
    local pkg_manager=$1
    local list_file=$2
    local install_cmd=$3
    
    if [ -f "$BACKUP_DIR/package-lists/$list_file" ]; then
        echo "  - Restoring $pkg_manager packages..."
        while read -r package; do
            [ -z "$package" ] && continue
            echo "    Installing: $package"
            eval "$install_cmd $package" 2>/dev/null || echo "    Failed: $package"
        done < "$BACKUP_DIR/package-lists/$list_file"
    else
        echo "  - $pkg_manager: list not found, skipping"
    fi
}

# Ask user which package managers to restore
echo "Available package lists:"
ls -1 "$BACKUP_DIR/package-lists/" 2>/dev/null || echo "No package lists found"
echo ""
read -p "Restore all package lists? (y/N): " restore_all

if [ "$restore_all" = "y" ] || [ "$restore_all" = "Y" ]; then
    # APT/PKG
    if [ -f "$BACKUP_DIR/package-lists/pkg-list.txt" ]; then
        echo "  - Installing apt/pkg packages..."
        pkg install $(cat "$BACKUP_DIR/package-lists/pkg-list.txt" | awk '{print $1}') -y 2>/dev/null || true
    fi
    
    # Python pip
    if [ -f "$BACKUP_DIR/package-lists/pip-requirements.txt" ] && command -v pip &> /dev/null; then
        echo "  - Installing pip packages..."
        pip install -r "$BACKUP_DIR/package-lists/pip-requirements.txt" 2>/dev/null || true
    fi
    
    # Node.js npm
    restore_packages "npm" "npm-list.txt" "npm install -g"
    
    # Rust cargo
    restore_packages "cargo" "cargo-list.txt" "cargo install"
    
    # Ruby gem
    restore_packages "gem" "gem-list.txt" "gem install"
    
    # PHP composer
    restore_packages "composer" "composer-global.txt" "composer global require"
    
    # Yarn
    restore_packages "yarn" "yarn-global.txt" "yarn global add"
    
    # pnpm
    restore_packages "pnpm" "pnpm-global.txt" "pnpm add -g"
    
    # Pipx
    restore_packages "pipx" "pipx-list.txt" "pipx install"
else
    echo "  - Skipping package installation"
fi

echo -e "${GREEN}✓ Package lists processed${NC}\n"

echo -e "${YELLOW}[2/7] Restoring $PREFIX/bin...${NC}"
if [ -f "$BACKUP_DIR/archives/bin-backup.tar.gz" ]; then
    tar -xzf "$BACKUP_DIR/archives/bin-backup.tar.gz" -C /data/data/com.termux/files/tmp/
    cp -r /data/data/com.termux/files/tmp/bin/* $PREFIX/bin/
    rm -rf /data/data/com.termux/files/tmp/bin
    
    # Restore symlinks
    if [ -f "$BACKUP_DIR/archives/symlink-bin.txt" ]; then
        while IFS=" -> " read -r link target; do
            [ -z "$link" ] && continue
            rm -f "$link" 2>/dev/null || true
            ln -sf "$target" "$link" 2>/dev/null || true
        done < "$BACKUP_DIR/archives/symlink-bin.txt"
    fi
    
    # Fix permissions
    chmod -R +x $PREFIX/bin 2>/dev/null || true
    echo -e "${GREEN}✓ bin restored${NC}"
else
    echo -e "${YELLOW}⚠ bin-backup.tar.gz not found, skipping${NC}"
fi
echo ""

echo -e "${YELLOW}[3/7] Restoring $PREFIX/lib...${NC}"
if [ -f "$BACKUP_DIR/archives/lib-backup.tar.gz" ]; then
    echo "  (This may take a while)"
    tar -xzf "$BACKUP_DIR/archives/lib-backup.tar.gz" -C /data/data/com.termux/files/tmp/
    cp -r /data/data/com.termux/files/tmp/lib/* $PREFIX/lib/
    rm -rf /data/data/com.termux/files/tmp/lib
    
    # Restore symlinks
    if [ -f "$BACKUP_DIR/archives/symlink-lib.txt" ]; then
        while IFS=" -> " read -r link target; do
            [ -z "$link" ] && continue
            rm -f "$link" 2>/dev/null || true
            ln -sf "$target" "$link" 2>/dev/null || true
        done < "$BACKUP_DIR/archives/symlink-lib.txt"
    fi
    
    echo -e "${GREEN}✓ lib restored${NC}"
else
    echo -e "${YELLOW}⚠ lib-backup.tar.gz not found, skipping${NC}"
fi
echo ""

echo -e "${YELLOW}[4/7] Restoring $PREFIX/share...${NC}"
if [ -f "$BACKUP_DIR/archives/share-backup.tar.gz" ]; then
    tar -xzf "$BACKUP_DIR/archives/share-backup.tar.gz" -C /data/data/com.termux/files/tmp/
    cp -r /data/data/com.termux/files/tmp/share/* $PREFIX/share/
    rm -rf /data/data/com.termux/files/tmp/share
    echo -e "${GREEN}✓ share restored${NC}"
else
    echo -e "${YELLOW}⚠ share-backup.tar.gz not found, skipping${NC}"
fi
echo ""

echo -e "${YELLOW}[5/7] Restoring $PREFIX/etc...${NC}"
if [ -f "$BACKUP_DIR/archives/etc-backup.tar.gz" ]; then
    tar -xzf "$BACKUP_DIR/archives/etc-backup.tar.gz" -C /data/data/com.termux/files/tmp/
    cp -r /data/data/com.termux/files/tmp/etc/* $PREFIX/etc/
    rm -rf /data/data/com.termux/files/tmp/etc
    echo -e "${GREEN}✓ etc restored${NC}"
else
    echo -e "${YELLOW}⚠ etc-backup.tar.gz not found, skipping${NC}"
fi
echo ""

echo -e "${YELLOW}[6/7] Restoring home config...${NC}"
if [ -f "$BACKUP_DIR/archives/home-config-backup.tar.gz" ]; then
    tar -xzf "$BACKUP_DIR/archives/home-config-backup.tar.gz" -C /data/data/com.termux/files/tmp/
    cp -r /data/data/com.termux/files/tmp/home-config/.bashrc ~/ 2>/dev/null || true
    cp -r /data/data/com.termux/files/tmp/home-config/.bash_profile ~/ 2>/dev/null || true
    cp -r /data/data/com.termux/files/tmp/home-config/.zshrc ~/ 2>/dev/null || true
    cp -r /data/data/com.termux/files/tmp/home-config/.termux ~/ 2>/dev/null || true
    cp -r /data/data/com.termux/files/tmp/home-config/.config ~/ 2>/dev/null || true
    cp -r /data/data/com.termux/files/tmp/home-config/.local ~/ 2>/dev/null || true
    rm -rf /data/data/com.termux/files/tmp/home-config
    echo -e "${GREEN}✓ home config restored${NC}"
else
    echo -e "${YELLOW}⚠ home-config-backup.tar.gz not found, skipping${NC}"
fi
echo ""

echo -e "${YELLOW}[7/7] Final cleanup and verification...${NC}"
# Clean tmp
rm -rf /data/data/com.termux/files/tmp/*

# Fix ownership (just in case)
chown -R $(whoami) $PREFIX 2>/dev/null || true
chown -R $(whoami) $HOME 2>/dev/null || true

echo -e "${GREEN}✓ Cleanup completed${NC}\n"

echo "=========================================="
echo -e "${GREEN}Restore Summary:${NC}"
echo "✓ Package lists processed"
echo "✓ Binaries restored"
echo "✓ Libraries restored"
echo "✓ Shared files restored"
echo "✓ Configurations restored"
echo "✓ Home configs restored"
echo ""
echo -e "${YELLOW}Post-restore steps:${NC}"
echo "1. Restart Termux: exit (tutup app, buka lagi)"
echo "2. Verify: hash -r && rehash"
echo "3. Test commands: python --version, npm --version, dll"
echo ""
echo -e "${BLUE}Troubleshooting:${NC}"
echo "- Jika command not found: export PATH=\$PREFIX/bin:\$PATH"
echo "- Jika library error: pkg reinstall <package-name>"
echo "- Jika symlink rusak: cek file symlink-*.txt di backup"
echo "=========================================="
```

Simpan dan jalankan:

```bash
chmod +x termux-restore.sh
./termux-restore.sh /sdcard/backup/termux-backup-20241212-143022
```

### 6.3 Selective Backup Script

Simpan sebagai `termux-selective-backup.sh`:

```bash
#!/data/data/com.termux/files/usr/bin/bash

# Termux Selective Backup Script
# Allows user to choose what to backup

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="/sdcard/backup/termux-selective-$TIMESTAMP"

echo -e "${GREEN}=== Termux Selective Backup ===${NC}"
echo ""
echo "Pilih komponen yang ingin di-backup:"
echo ""

# Interactive selection
echo -n "1. Package lists (apt, pip, npm, dll)? [Y/n]: "
read backup_lists
backup_lists=${backup_lists:-Y}

echo -n "2. Binaries ($PREFIX/bin)? [Y/n]: "
read backup_bin
backup_bin=${backup_bin:-Y}

echo -n "3. Libraries ($PREFIX/lib)? [y/N]: "
read backup_lib
backup_lib=${backup_lib:-N}

echo -n "4. Shared files ($PREFIX/share)? [y/N]: "
read backup_share
backup_share=${backup_share:-N}

echo -n "5. Config files ($PREFIX/etc)? [Y/n]: "
read backup_etc
backup_etc=${backup_etc:-Y}

echo -n "6. Home config (~/.bashrc, ~/.termux, dll)? [Y/n]: "
read backup_home
backup_home=${backup_home:-Y}

echo ""
echo "Membuat backup di: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR/package-lists"
mkdir -p "$BACKUP_DIR/archives"

# Backup based on selection
if [[ "$backup_lists" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Backing up package lists...${NC}"
    pkg list-installed > "$BACKUP_DIR/package-lists/pkg-list.txt"
    pip freeze > "$BACKUP_DIR/package-lists/pip-requirements.txt" 2>/dev/null || true
    npm list -g --depth=0 | grep -v npm | awk '{print $2}' > "$BACKUP_DIR/package-lists/npm-list.txt" 2>/dev/null || true
    # ... (tambahkan package managers lain sesuai kebutuhan)
    echo -e "${GREEN}✓ Package lists done${NC}"
fi

if [[ "$backup_bin" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Backing up binaries...${NC}"
    find $PREFIX/bin -type l -printf "%p -> %l\n" > "$BACKUP_DIR/archives/symlink-bin.txt"
    mkdir -p /data/data/com.termux/files/tmp-backup/bin
    cp -rL $PREFIX/bin/* /data/data/com.termux/files/tmp-backup/bin/
    tar -czf "$BACKUP_DIR/archives/bin-backup.tar.gz" -C /data/data/com.termux/files/tmp-backup bin
    rm -rf /data/data/com.termux/files/tmp-backup/bin
    echo -e "${GREEN}✓ Binaries done${NC}"
fi

if [[ "$backup_lib" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Backing up libraries (ini akan lama)...${NC}"
    find $PREFIX/lib -type l -printf "%p -> %l\n" > "$BACKUP_DIR/archives/symlink-lib.txt"
    mkdir -p /data/data/com.termux/files/tmp-backup/lib
    cp -rL $PREFIX/lib/* /data/data/com.termux/files/tmp-backup/lib/
    tar -czf "$BACKUP_DIR/archives/lib-backup.tar.gz" -C /data/data/com.termux/files/tmp-backup lib
    rm -rf /data/data/com.termux/files/tmp-backup/lib
    echo -e "${GREEN}✓ Libraries done${NC}"
fi

if [[ "$backup_share" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Backing up share files...${NC}"
    mkdir -p /data/data/com.termux/files/tmp-backup/share
    cp -r $PREFIX/share/* /data/data/com.termux/files/tmp-backup/share/
    tar -czf "$BACKUP_DIR/archives/share-backup.tar.gz" -C /data/data/com.termux/files/tmp-backup share
    rm -rf /data/data/com.termux/files/tmp-backup/share
    echo -e "${GREEN}✓ Share done${NC}"
fi

if [[ "$backup_etc" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Backing up etc configs...${NC}"
    mkdir -p /data/data/com.termux/files/tmp-backup/etc
    cp -r $PREFIX/etc/* /data/data/com.termux/files/tmp-backup/etc/
    tar -czf "$BACKUP_DIR/archives/etc-backup.tar.gz" -C /data/data/com.termux/files/tmp-backup etc
    rm -rf /data/data/com.termux/files/tmp-backup/etc
    echo -e "${GREEN}✓ Etc done${NC}"
fi

if [[ "$backup_home" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Backing up home configs...${NC}"
    mkdir -p /data/data/com.termux/files/tmp-backup/home-config
    cp ~/.bashrc ~/.zshrc /data/data/com.termux/files/tmp-backup/home-config/ 2>/dev/null || true
    cp -r ~/.termux ~/.config ~/.local /data/data/com.termux/files/tmp-backup/home-config/ 2>/dev/null || true
    tar -czf "$BACKUP_DIR/archives/home-config-backup.tar.gz" -C /data/data/com.termux/files/tmp-backup home-config
    rm -rf /data/data/com.termux/files/tmp-backup/home-config
    echo -e "${GREEN}✓ Home config done${NC}"
fi

# Create metadata
cat > "$BACKUP_DIR/backup-info.txt" << EOF
Selective Backup
================
Date: $(date)
Components: 
$([ "$backup_lists" = "Y" ] || [ "$backup_lists" = "y" ] && echo "  - Package lists")
$([ "$backup_bin" = "Y" ] || [ "$backup_bin" = "y" ] && echo "  - Binaries")
$([ "$backup_lib" = "Y" ] || [ "$backup_lib" = "y" ] && echo "  - Libraries")
$([ "$backup_share" = "Y" ] || [ "$backup_share" = "y" ] && echo "  - Share files")
$([ "$backup_etc" = "Y" ] || [ "$backup_etc" = "y" ] && echo "  - Etc configs")
$([ "$backup_home" = "Y" ] || [ "$backup_home" = "y" ] && echo "  - Home configs")

Total Size: $(du -sh "$BACKUP_DIR" | cut -f1)
EOF

echo ""
echo -e "${GREEN}✓ Backup completed!${NC}"
echo "Location: $BACKUP_DIR"
echo "Size: $(du -sh "$BACKUP_DIR" | cut -f1)"
```

Simpan dan jalankan:

```bash
chmod +x termux-selective-backup.sh
./termux-selective-backup.sh
```

---

## 7. Restore Procedures

### 7.1 Full Restore (Automated)

Gunakan script di Section 6.2.

### 7.2 Manual Restore (Step-by-Step)

Jika script tidak bekerja atau Anda ingin kontrol penuh:

#### Step 1: Extract Archives

```bash
cd /sdcard/backup/termux-backup-YYYYMMDD-HHMMSS/archives

# Extract semua
tar -xzf bin-backup.tar.gz -C /data/data/com.termux/files/tmp/
tar -xzf lib-backup.tar.gz -C /data/data/com.termux/files/tmp/
tar -xzf etc-backup.tar.gz -C /data/data/com.termux/files/tmp/
tar -xzf share-backup.tar.gz -C /data/data/com.termux/files/tmp/
tar -xzf home-config-backup.tar.gz -C /data/data/com.termux/files/tmp/
```

#### Step 2: Copy Files

```bash
# Copy binaries
cp -r /data/data/com.termux/files/tmp/bin/* $PREFIX/bin/

# Copy libraries
cp -r /data/data/com.termux/files/tmp/lib/* $PREFIX/lib/

# Copy configs
cp -r /data/data/com.termux/files/tmp/etc/* $PREFIX/etc/
cp -r /data/data/com.termux/files/tmp/share/* $PREFIX/share/

# Copy home configs
cp /data/data/com.termux/files/tmp/home-config/.bashrc ~/
cp /data/data/com.termux/files/tmp/home-config/.zshrc ~/
cp -r /data/data/com.termux/files/tmp/home-config/.termux ~/
cp -r /data/data/com.termux/files/tmp/home-config/.config ~/
```

#### Step 3: Restore Symlinks

```bash
# Restore bin symlinks
while IFS=" -> " read -r link target; do
    [ -z "$link" ] && continue
    rm -f "$link"
    ln -sf "$target" "$link"
done < /sdcard/backup/termux-backup-YYYYMMDD-HHMMSS/archives/symlink-bin.txt

# Restore lib symlinks
while IFS=" -> " read -r link target; do
    [ -z "$link" ] && continue
    rm -f "$link"
    ln -sf "$target" "$link"
done < /sdcard/backup/termux-backup-YYYYMMDD-HHMMSS/archives/symlink-lib.txt
```

#### Step 4: Fix Permissions

```bash
chmod -R +x $PREFIX/bin
chown -R $(whoami) $PREFIX
chown -R $(whoami) $HOME
```

#### Step 5: Reinstall Packages (Optional)

```bash
# Dari package lists
pkg install $(cat /sdcard/backup/.../package-lists/pkg-list.txt | awk '{print $1}')
pip install -r /sdcard/backup/.../package-lists/pip-requirements.txt
# ... dll
```

### 7.3 Partial Restore

Restore hanya komponen tertentu:

#### Restore Only Package Lists

```bash
cd /sdcard/backup/termux-backup-YYYYMMDD-HHMMSS/package-lists

# Install apt packages
pkg install $(cat pkg-list.txt | awk '{print $1}')

# Install pip packages
pip install -r pip-requirements.txt

# Install npm packages
cat npm-list.txt | xargs npm install -g
```

#### Restore Only Binaries

```bash
cd /sdcard/backup/termux-backup-YYYYMMDD-HHMMSS/archives
tar -xzf bin-backup.tar.gz -C /data/data/com.termux/files/tmp/
cp -r /data/data/com.termux/files/tmp/bin/* $PREFIX/bin/

# Restore symlinks
while IFS=" -> " read -r link target; do
    rm -f "$link"
    ln -sf "$target" "$link"
done < symlink-bin.txt

chmod -R +x $PREFIX/bin
```

#### Restore Only Configs

```bash
cd /sdcard/backup/termux-backup-YYYYMMDD-HHMMSS/archives
tar -xzf home-config-backup.tar.gz -C /data/data/com.termux/files/tmp/
cp /data/data/com.termux/files/tmp/home-config/.bashrc ~/
cp /data/data/com.termux/files/tmp/home-config/.zshrc ~/
cp -r /data/data/com.termux/files/tmp/home-config/.termux ~/
```

---

## 8. Troubleshooting

### 8.1 Common Errors & Solutions

#### Error: "command not found" setelah restore

**Penyebab:** PATH tidak ter-set dengan benar.

**Solusi:**
```bash
# Temporary fix
export PATH=$PREFIX/bin:$PATH

# Permanent fix
echo 'export PATH=$PREFIX/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# Refresh shell hash table
hash -r
rehash  # untuk zsh
```

#### Error: "Permission denied" saat menjalankan binary

**Penyebab:** Execute permission hilang setelah transfer via `/sdcard`.

**Solusi:**

```bash
# Fix semua binary di bin
chmod -R +x $PREFIX/bin

# Fix specific file
chmod +x $PREFIX/bin/python

# Verify
ls -la $PREFIX/bin/python
# Should show: -rwxr-xr-x
```

#### Error: Library tidak ditemukan (ld.so error)

**Penyebab:** Symlink library rusak atau library hilang.

**Solusi:**

```bash
# 1. Check symlink
ls -la $PREFIX/lib/libpython*.so
# Jika broken: libpython3.11.so -> (tidak ada target)

# 2. Restore symlink dari backup
cd /sdcard/backup/termux-backup-YYYYMMDD-HHMMSS/archives
grep "libpython" symlink-lib.txt
# Output: /path/to/libpython3.11.so -> libpython3.11.so.1.0

# 3. Recreate symlink
ln -sf $PREFIX/lib/libpython3.11.so.1.0 $PREFIX/lib/libpython3.11.so

# 4. Jika library benar-benar hilang, reinstall package
pkg reinstall python
```

#### Error: "Text file busy" saat copy binary

**Penyebab:** Binary sedang digunakan.

**Solusi:**

```bash
# 1. Kill process yang menggunakan binary
fuser -k $PREFIX/bin/python  # Hati-hati: ini kill semua proses python!

# 2. Atau restart Termux dan coba lagi

# 3. Atau copy dengan force
cp -f /backup/bin/python $PREFIX/bin/python
```

#### Error: Tar extraction gagal "Cannot open: Permission denied"

**Penyebab:** Target directory tidak writable atau tar.gz corrupt.

**Solusi:**

```bash
# 1. Check ownership
ls -ld $PREFIX/bin
# Should be owned by you

# 2. Fix ownership
chown -R $(whoami) $PREFIX

# 3. Verify tar.gz integrity
tar -tzf bin-backup.tar.gz > /dev/null
# Jika error, file corrupt. Re-backup atau gunakan backup lain.

# 4. Extract ke lokasi lain dulu
mkdir -p ~/temp-restore
tar -xzf bin-backup.tar.gz -C ~/temp-restore
cp -r ~/temp-restore/bin/* $PREFIX/bin/
```

#### Error: Package installation failed (apt/pip/npm)

**Penyebab:** Repository tidak tersedia, internet issue, atau dependency conflict.

**Solusi:**

```bash
# APT: Update repository dulu
pkg update && pkg upgrade
pkg install <package-name>

# PIP: Use specific mirror
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple <package-name>

# NPM: Clear cache
npm cache clean --force
npm install -g <package-name>

# Jika masih gagal, install manual dari source atau skip package tersebut
```

### 8.2 Symlink Issues

#### Check Broken Symlinks

```bash
# Find all broken symlinks in bin
find $PREFIX/bin -xtype l

# Find all broken symlinks in lib
find $PREFIX/lib -xtype l

# Detailed info
find $PREFIX/bin -type l -exec ls -l {} \; | grep -- '->'
```

#### Batch Fix Symlinks

```bash
# Script untuk auto-fix broken symlinks
#!/bin/bash

# File: fix-symlinks.sh
SYMLINK_FILE="/sdcard/backup/termux-backup-YYYYMMDD-HHMMSS/archives/symlink-bin.txt"

echo "Fixing broken symlinks from: $SYMLINK_FILE"

while IFS=" -> " read -r link target; do
    [ -z "$link" ] && continue
    
    # Check if symlink exists and is broken
    if [ -L "$link" ] && [ ! -e "$link" ]; then
        echo "Fixing: $link -> $target"
        rm -f "$link"
        ln -sf "$target" "$link"
    elif [ ! -e "$link" ]; then
        echo "Creating: $link -> $target"
        ln -sf "$target" "$link"
    else
        echo "OK: $link"
    fi
done < "$SYMLINK_FILE"

echo "Done!"
```

### 8.3 Cross-Device Compatibility Issues

#### Architecture Mismatch (arm64 vs x86_64)

**Problem:** Binary dari ARM64 tidak jalan di x86_64 dan sebaliknya.

**Detection:**

```bash
# Check architecture backup
cat /sdcard/backup/termux-backup-YYYYMMDD-HHMMSS/backup-info.txt | grep Architecture

# Check current architecture
uname -m
# arm64 / aarch64 = ARM 64-bit
# x86_64 = Intel/AMD 64-bit
# armv7l = ARM 32-bit
```

**Solution:**

```bash
# TIDAK BISA restore binary directly!
# Harus reinstall semua dari package lists:

cd /sdcard/backup/termux-backup-YYYYMMDD-HHMMSS/package-lists

# Install semua package
pkg install $(cat pkg-list.txt | awk '{print $1}')
pip install -r pip-requirements.txt
cat npm-list.txt | xargs npm install -g
# ... dll

# Binary akan di-compile untuk architecture yang sesuai
```

#### Android Version Issues

**Problem:** Termux/binary dari Android 11 tidak jalan di Android 7.

**Solution:**

```bash
# Cek Android version
getprop ro.build.version.release

# Jika terlalu jauh beda (>2 versi):
# 1. Restore package lists saja
# 2. Reinstall semua package
# 3. Restore config files (ini aman)

# Skip restore binary jika Android version beda jauh
```

### 8.4 Storage & Space Issues

#### Error: "No space left on device"

**Detection:**

```bash
# Check available space
df -h $PREFIX
df -h /sdcard

# Check backup size
du -sh /sdcard/backup/termux-backup-*
```

**Solution:**

```bash
# 1. Clean Termux cache
pkg clean
apt autoremove

# 2. Clean tmp files
rm -rf /data/data/com.termux/files/tmp/*
rm -rf $PREFIX/tmp/*

# 3. Remove old packages
pkg autoclean

# 4. Selective restore: skip lib-backup.tar.gz (biasanya paling besar)
# Reinstall package instead of restore binary

# 5. Move backup to external storage
mv /sdcard/backup /storage/XXXX-XXXX/termux-backup
```

#### Backup Too Large (>4GB) untuk FAT32

**Problem:** USB/SD Card pakai FAT32, limit 4GB per file.

**Solution:**

```bash
# Split file saat backup
cd /sdcard/backup/termux-backup-YYYYMMDD-HHMMSS/archives

# Split lib-backup.tar.gz (biasanya file terbesar)
split -b 3G lib-backup.tar.gz lib-backup.tar.gz.part

# Hasil: lib-backup.tar.gz.partaa, lib-backup.tar.gz.partab, ...

# Gabungkan lagi saat restore
cat lib-backup.tar.gz.part* > lib-backup.tar.gz

# Verify integrity
tar -tzf lib-backup.tar.gz > /dev/null
```

### 8.5 Verification After Restore

#### Comprehensive Health Check

```bash
#!/bin/bash
# File: termux-healthcheck.sh

echo "=== Termux Health Check ==="
echo ""

# 1. Check PATH
echo "[1] PATH:"
echo $PATH | grep -q "$PREFIX/bin" && echo "✓ OK" || echo "✗ FAIL: \$PREFIX/bin not in PATH"
echo ""

# 2. Check common commands
echo "[2] Common Commands:"
commands=(bash python python3 pip npm node git vim nano curl wget)
for cmd in "${commands[@]}"; do
    if command -v $cmd &> /dev/null; then
        version=$(${cmd} --version 2>&1 | head -n1)
        echo "✓ $cmd: $version"
    else
        echo "✗ $cmd: NOT FOUND"
    fi
done
echo ""

# 3. Check broken symlinks
echo "[3] Broken Symlinks in bin:"
broken=$(find $PREFIX/bin -xtype l 2>/dev/null | wc -l)
if [ "$broken" -eq 0 ]; then
    echo "✓ No broken symlinks"
else
    echo "✗ Found $broken broken symlinks:"
    find $PREFIX/bin -xtype l 2>/dev/null | head -n 5
fi
echo ""

# 4. Check library dependencies
echo "[4] Library Check:"
if command -v python &> /dev/null; then
    python -c "import sys; print('✓ Python libs OK')" 2>/dev/null || echo "✗ Python libs issue"
fi
if command -v node &> /dev/null; then
    node -e "console.log('✓ Node.js OK')" 2>/dev/null || echo "✗ Node.js issue"
fi
echo ""

# 5. Check permissions
echo "[5] Permissions:"
writable=$([ -w $PREFIX/bin ] && echo "✓" || echo "✗")
executable=$([ -x $PREFIX/bin/bash ] && echo "✓" || echo "✗")
echo "$writable \$PREFIX/bin writable"
echo "$executable bash executable"
echo ""

# 6. Check disk space
echo "[6] Disk Space:"
df -h $PREFIX | tail -n 1
echo ""

echo "=== Health Check Complete ==="
```

Run:

```bash
chmod +x termux-healthcheck.sh
./termux-healthcheck.sh
```

---

## 9. Advanced Topics

### 9.1 Incremental Backup

Backup hanya perubahan sejak backup terakhir:

```bash
#!/bin/bash
# File: termux-incremental-backup.sh

LAST_BACKUP="/sdcard/backup/last-full-backup"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
INCREMENTAL_DIR="/sdcard/backup/incremental-$TIMESTAMP"

mkdir -p "$INCREMENTAL_DIR"

# Find files modified after last backup
if [ -f "$LAST_BACKUP/backup-info.txt" ]; then
    LAST_BACKUP_TIME=$(stat -c %Y "$LAST_BACKUP/backup-info.txt")
    
    echo "Finding changes since last backup..."
    
    # Backup only changed binaries
    find $PREFIX/bin -newer "$LAST_BACKUP/backup-info.txt" -type f > "$INCREMENTAL_DIR/changed-files.txt"
    
    mkdir -p "$INCREMENTAL_DIR/bin"
    while read -r file; do
        cp "$file" "$INCREMENTAL_DIR/bin/"
    done < "$INCREMENTAL_DIR/changed-files.txt"
    
    tar -czf "$INCREMENTAL_DIR/incremental-bin.tar.gz" -C "$INCREMENTAL_DIR" bin
    rm -rf "$INCREMENTAL_DIR/bin"
    
    echo "Incremental backup completed!"
    echo "Location: $INCREMENTAL_DIR"
else
    echo "Error: No previous full backup found. Run full backup first."
    exit 1
fi
```

### 9.2 Automated Scheduled Backup

Menggunakan `cronie` (cron for Termux):

```bash
# Install cronie
pkg install cronie

# Enable cron daemon
crond

# Edit crontab
crontab -e

# Tambahkan jadwal backup (setiap hari jam 2 pagi):
0 2 * * * /data/data/com.termux/files/home/termux-backup.sh

# Atau setiap minggu (Minggu jam 3 pagi):
0 3 * * 0 /data/data/com.termux/files/home/termux-backup.sh

# Verify crontab
crontab -l
```

### 9.3 Remote Backup (rsync to Server)

Backup langsung ke remote server:

```bash
# Install rsync
pkg install rsync openssh

# Setup SSH key (one-time)
ssh-keygen -t rsa -b 4096
ssh-copy-id user@backup-server.com

# Backup script dengan rsync
#!/bin/bash
# File: termux-remote-backup.sh

REMOTE_USER="user"
REMOTE_HOST="backup-server.com"
REMOTE_PATH="/backups/termux/"
LOCAL_BACKUP="/sdcard/backup/latest"

# Backup locally first
./termux-backup.sh

# Sync ke remote server
rsync -avz --progress "$LOCAL_BACKUP/" \
    ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/$(basename $LOCAL_BACKUP)/

echo "Remote backup completed!"
```

### 9.4 Encrypted Backup

Encrypt backup untuk keamanan:

```bash
# Install GPG
pkg install gnupg

# Generate GPG key (one-time)
gpg --full-generate-key
# Follow prompts: pilih RSA, 4096 bits, set passphrase

# Encrypt backup
#!/bin/bash
# File: termux-encrypted-backup.sh

BACKUP_DIR="/sdcard/backup/termux-backup-$(date +%Y%m%d-%H%M%S)"
ENCRYPTED_DIR="/sdcard/backup-encrypted"

# Run normal backup
./termux-backup.sh

# Encrypt archives
mkdir -p "$ENCRYPTED_DIR"
cd "$BACKUP_DIR/archives"

for file in *.tar.gz; do
    echo "Encrypting $file..."
    gpg --encrypt --recipient your-email@example.com "$file"
    mv "$file.gpg" "$ENCRYPTED_DIR/"
done

echo "Encrypted backup saved to: $ENCRYPTED_DIR"
```

Decrypt saat restore:

```bash
# Decrypt
cd /sdcard/backup-encrypted
for file in *.tar.gz.gpg; do
    gpg --decrypt "$file" > "${file%.gpg}"
done

# Kemudian restore seperti biasa
```

### 9.5 Differential Backup Strategy

Kombinasi full + incremental:

```bash
# Week 1 Sunday: Full backup
./termux-backup.sh

# Week 1 Monday-Saturday: Incremental
./termux-incremental-backup.sh

# Week 2 Sunday: Full backup lagi
./termux-backup.sh

# Pattern: Full setiap minggu, incremental setiap hari
```

**Keuntungan:**
- Save space (incremental kecil)
- Faster daily backup
- Recovery: restore last full + all incrementals

### 9.6 Backup Validation

Verifikasi integrity backup:

```bash
#!/bin/bash
# File: validate-backup.sh

BACKUP_DIR="$1"

if [ -z "$BACKUP_DIR" ]; then
    echo "Usage: ./validate-backup.sh /sdcard/backup/termux-backup-YYYYMMDD-HHMMSS"
    exit 1
fi

echo "Validating backup: $BACKUP_DIR"
echo ""

# 1. Check structure
echo "[1] Checking directory structure..."
required_dirs=("archives" "package-lists")
for dir in "${required_dirs[@]}"; do
    if [ -d "$BACKUP_DIR/$dir" ]; then
        echo "  ✓ $dir exists"
    else
        echo "  ✗ $dir MISSING"
    fi
done
echo ""

# 2. Validate tar.gz files
echo "[2] Validating archives..."
cd "$BACKUP_DIR/archives"
for archive in *.tar.gz; do
    if tar -tzf "$archive" > /dev/null 2>&1; then
        size=$(du -h "$archive" | cut -f1)
        echo "  ✓ $archive ($size)"
    else
        echo "  ✗ $archive CORRUPTED"
    fi
done
echo ""

# 3. Check package lists
echo "[3] Checking package lists..."
cd "$BACKUP_DIR/package-lists"
for list in *.txt; do
    lines=$(wc -l < "$list")
    echo "  ✓ $list ($lines packages)"
done
echo ""

# 4. Check metadata
echo "[4] Metadata:"
if [ -f "$BACKUP_DIR/backup-info.txt" ]; then
    cat "$BACKUP_DIR/backup-info.txt"
else
    echo "  ✗ backup-info.txt missing"
fi
echo ""

echo "Validation complete!"
```

### 9.7 Multi-Device Sync

Sinkronisasi Termux environment antar banyak device:

```bash
# Konsep: Central backup + selective restore

# Device A (development):
# - Full environment
# - Heavy packages

# Device B (light):
# - Restore package lists only
# - Install on-demand

# Device C (production):
# - Restore specific tools only
# - Minimal footprint

# Strategy:
# 1. Backup dari Device A (full)
# 2. Restore ke B & C selectively
# 3. Maintain separate package lists per device
```

### 9.8 Backup Rotation

Auto-delete old backups untuk save space:

```bash
#!/bin/bash
# File: backup-rotation.sh

BACKUP_BASE="/sdcard/backup"
MAX_BACKUPS=5  # Keep last 5 backups only

# List backups by date (oldest first)
backups=($(ls -dt $BACKUP_BASE/termux-backup-* 2>/dev/null))

# Count
total=${#backups[@]}

if [ $total -gt $MAX_BACKUPS ]; then
    echo "Found $total backups, keeping latest $MAX_BACKUPS"
    
    # Delete oldest
    to_delete=$((total - MAX_BACKUPS))
    for ((i=total-1; i>=total-to_delete; i--)); do
        echo "Deleting old backup: ${backups[$i]}"
        rm -rf "${backups[$i]}"
    done
    
    echo "Cleanup completed!"
else
    echo "Only $total backups found, no cleanup needed"
fi
```

Run after setiap backup:

```bash
./termux-backup.sh && ./backup-rotation.sh
```

---

## 10. Best Practices & Tips

### 10.1 Backup Checklist

**Sebelum Backup:**
- [ ] Update semua package (`pkg upgrade`)
- [ ] Bersihkan cache (`pkg clean`)
- [ ] Test critical commands
- [ ] Cek available space

**Saat Backup:**
- [ ] Gunakan timestamp di nama folder
- [ ] Simpan metadata (backup-info.txt)
- [ ] Verify tar.gz integrity
- [ ] Document special configuration

**Setelah Backup:**
- [ ] Test restore di device lain (jika mungkin)
- [ ] Simpan di 2+ lokasi berbeda
- [ ] Label backup dengan jelas
- [ ] Rotate old backups

### 10.2 Recommended Backup Frequency

| Environment Type | Frequency | Method |
|------------------|-----------|---------|
| **Development (aktif)** | Daily | Incremental |
| **Production (stable)** | Weekly | Full |
| **Personal (casual)** | Monthly | Full |
| **Before major changes** | On-demand | Full |

### 10.3 Storage Recommendations

**Local Storage:**
- `/sdcard/backup` - Convenient, tapi hilang jika factory reset
- SD Card - Persistent, removable
- USB OTG - Large capacity, portable

**Remote Storage:**
- Cloud (rclone) - Universal access, auto-sync
- Home server (rsync) - Fast local network, unlimited space
- Git (config only) - Version control, small files

**Redundancy Strategy:**
1. Primary: `/sdcard/backup` (quick access)
2. Secondary: USB/SD Card (offline backup)
3. Tertiary: Cloud (disaster recovery)

### 10.4 What NOT to Backup

❌ **Skip these:**
- `/sdcard/DCIM`, `/sdcard/Pictures` (user data, bukan Termux)
- `$PREFIX/tmp` (temporary files)
- `$PREFIX/var/cache` (will be regenerated)
- `~/.cache` (application cache)
- Large datasets (backup separately)

✅ **Always backup:**
- `$PREFIX/bin` & `$PREFIX/lib` (jika pakai binary method)
- Package lists (ringan, penting)
- `~/.bashrc`, `~/.zshrc`, `~/.termux` (configurations)
- Custom scripts di `$HOME`

### 10.5 Security Considerations

🔒 **Protect Sensitive Data:**

```bash
# Exclude sensitive files dari backup
# Edit termux-backup.sh, tambahkan:

# Skip SSH keys
tar --exclude='home-config/.ssh' -czf home-config-backup.tar.gz home-config/

# Skip GPG keys
tar --exclude='home-config/.gnupg' -czf home-config-backup.tar.gz home-config/

# Atau encrypt seluruh backup (lihat section 9.4)
```

### 10.6 Troubleshooting Decision Tree

```
Restore Failed?
├─ Binary not working?
│  ├─ Architecture mismatch? → Reinstall dari package list
│  ├─ Permission denied? → chmod +x
│  └─ Library missing? → Restore lib / reinstall package
│
├─ Symlink broken?
│  ├─ Find in symlink-*.txt → Recreate manually
│  └─ Target missing? → Restore target file
│
├─ Command not found?
│  ├─ Check PATH → export PATH=$PREFIX/bin:$PATH
│  └─ Binary missing? → Reinstall package
│
└─ Package install failed?
   ├─ Update repo → pkg update
   ├─ Check internet → ping google.com
   └─ Install manually from source
```

---

## 11. Quick Reference

### 11.1 One-Liner Commands

```bash
# Full backup (quick)
mkdir -p /sdcard/backup && tar -czf /sdcard/backup/termux-full-$(date +%Y%m%d).tar.gz -C /data/data/com.termux/files .

# Package lists only
pkg list-installed > /sdcard/pkg.txt && pip freeze > /sdcard/pip.txt && npm list -g --depth=0 > /sdcard/npm.txt

# Quick restore binaries
tar -xzf /sdcard/backup/bin-backup.tar.gz -C $PREFIX && chmod -R +x $PREFIX/bin

# Fix PATH
export PATH=$PREFIX/bin:$PATH && hash -r

# Health check
command -v python && command -v pip && command -v npm && echo "OK" || echo "FAIL"
```

### 11.2 File Size Reference

| Component | Typical Size | Transfer Time (USB 3.0) | Transfer Time (Quick Share) |
|-----------|--------------|-------------------------|-----------------------------|
| Package lists | 10-50 KB | < 1 sec | < 1 sec |
| bin-backup.tar.gz | 50-500 MB | 1-5 sec | 5-20 sec |
| lib-backup.tar.gz | 500MB-3GB | 5-30 sec | 30 sec-2 min |
| etc-backup.tar.gz | 1-10 MB | < 1 sec | < 1 sec |
| share-backup.tar.gz | 50-200 MB | 1-2 sec | 5-10 sec |
| home-config-backup.tar.gz | 1-50 MB | < 1 sec | 1-3 sec |
| **Total (typical)** | **1-4 GB** | **10-40 sec** | **1-3 min** |

### 11.3 Compatibility Matrix

| Source | → | arm64 | x86_64 | armv7l |
|--------|---|-------|--------|--------|
| **arm64** | | ✅ Yes | ❌ No* | ⚠️ Maybe** |
| **x86_64** | | ❌ No* | ✅ Yes | ❌ No |
| **armv7l** | | ⚠️ Maybe** | ❌ No | ✅ Yes |

\* Use package lists only, reinstall everything  
\** Some binaries may work, test carefully

---

## 12. Conclusion

### 12.1 Summary

Dokumentasi ini mencakup:
✅ Complete backup methods (lists & binaries)  
✅ 15+ package managers support  
✅ 10+ transfer methods comparison  
✅ Automated backup/restore scripts  
✅ Troubleshooting guide  
✅ Advanced topics (encryption, remote, incremental)  

### 12.2 Recommended Workflow

**For Beginners:**
1. Use automated scripts (`termux-backup.sh`)
2. Transfer via Quick Share
3. Restore dengan `termux-restore.sh`

**For Advanced Users:**
1. Selective backup (binary untuk tools penting, list untuk sisanya)
2. Setup automated scheduled backup
3. Sync ke remote server
4. Maintain multiple backup versions

**For Developers:**
1. Daily incremental backup
2. Git untuk config files
3. Cloud sync untuk code
4. Test restore regularly

### 12.3 Additional Resources

**Official Documentation:**
- Termux Wiki: https://wiki.termux.com
- Termux GitHub: https://github.com/termux

**Community:**
- r/termux (Reddit)
- Termux Discord
- Stack Overflow (tag: termux)

**Tools Referenced:**
- `rsync` - https://rsync.samba.org/
- `rclone` - https://rclone.org/
- `gpg` - https://gnupg.org/

---

## 13. Changelog

**v1.0 (2025-01-18)**
- Initial complete documentation
- 15+ package managers covered
- 10+ transfer methods
- Automated scripts included
- Comprehensive troubleshooting

---

## 14. License & Credits

**Author:** EmuVlucht  
**License:** MIT 
**Contributors:** Welcome!  

<div align="center">
<a href="https://github.com/EmuVlucht/Tools/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=EmuVlucht/Tools" />
</a>
</div>

Jika ada pertanyaan, issue, atau improvement ideas:
- Email: emuvlucht@gmail.com
- GitHub Issues: https://github.com/EmuVlucht/Tools

---

**End of Documentation**

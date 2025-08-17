# Ultimate Gitignore & Git Automation

Skrip ini memudahkan manajemen `.gitignore` untuk multi-project dan submodules, sekaligus melakukan commit batch otomatis dengan Git LFS.

---

## 1. ultimate_gitignore.sh

Skrip Bash untuk **auto-update `.gitignore`** berdasarkan project type:

- Node.js
- Python
- Java / Android
- iOS / Swift
- Sistem / editor / logs / backup

### Fitur
- Deteksi project type secara rekursif (termasuk submodules).
- Tambahkan rules umum (`.DS_Store`, `.vscode/`, `*.log`, dll.).
- Tambahkan rules spesifik tiap bahasa/framework.
- Merge dengan rules lama dan hapus duplikat otomatis.

### Cara Pakai
1. Jadikan executable:
   ```bash
   chmod +x generator_gitignore.sh

2. Tambahkan pre-commit hook di `.git/hooks/pre-commit.sh`:
   ```bash
   #!/bin/bash
   bash ./generator_gitignore.sh
   git add .gitignore

3. Jadikan hook executable:
   ```bash
   chmod +x .git/hooks/pre-commit.sh

Setiap commit, `.gitignore` akan otomatis diperbarui.

---

## 2. Git Auto Batch Commit Script

Skrip Bash untuk inisialisasi repo, konfigurasi global, setup Git LFS, dan commit file/folder secara acak.

### Fitur

- Konfigurasi Git global (`user.name`, `user.email`, `safe.directory`).
- Inisialisasi repo Git & set branch default `main`.
- Set remote GitHub menggunakan environment variable `GITHUB_TOKEN`.
- Setup Git LFS untuk file besar (>50MB) seperti `*.zip`, `*.z01`, `*.z02`.
- Commit file/folder secara batch acak (1–5) dengan tanggal AUTHOR & COMMITTER acak.
- Push aman dengan `--force-with-lease`.

### Cara Pakai

1. Set environment variable GITHUB_TOKEN:
   ```bash
   export GITHUB_TOKEN="ghp_xxxxx"

2. Jalankan skrip:
   ```bash
   bash upload.sh

3. Semua file/folder akan di-upload batch demi batch, aman dari token di log.

---

## 3. Rekomendasi

- Gunakan kedua skrip ini di repo multi-project untuk menjaga `.gitignore` bersih.
- Pastikan Git LFS terinstal jika ada file besar (>50MB).
- Selalu cek `git status` sebelum push untuk menghindari overwrite.

---

## 4. License

MIT License ✅

---
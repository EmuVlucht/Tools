#!/bin/bash

# ==== Konfigurasi Git Global ====
git config --global user.name "EmuVlucht"
git config --global user.email "emuvlucht@gmail.com"
git config --global --add safe.directory "$(pwd)"

# ==== Inisialisasi Git ====
git init
git config --global init.defaultBranch main

# ==== Set remote ====
# Isi token melalui environment variable GITHUB_TOKEN
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN belum diset di environment variable!"
    echo "Misal: export GITHUB_TOKEN='ghp_xxxxx'"
    exit 1
fi

REMOTE_URL="https://${GITHUB_TOKEN}@github.com/EmuVlucht/My-Bot.git"
if git remote get-url origin &>/dev/null; then
    git remote set-url origin "$REMOTE_URL"
else
    git remote add origin "$REMOTE_URL"
fi

# ==== Setup Git LFS untuk file >50MB ====
git lfs install
# Misal track file zip/z01/z02
git lfs track "*.zip"
git lfs track "*.z01"
git lfs track "*.z02"
git add .gitattributes

# ==== Fungsi tanggal acak ====
random_date() {
    now=$(date +%s)
    start=0  # Unix epoch
    echo $(date -d "@$((RANDOM*(now-start)/32768 + start))" +"%Y-%m-%dT%H:%M:%S")
}

# ==== Ambil semua file/folder rekursif kecuali .git ====
mapfile -t ALL_ITEMS < <(find . -mindepth 1 ! -path "*/.git/*" | shuf)

# ==== Commit batch acak 1-5 file/folder ====
TOTAL=${#ALL_ITEMS[@]}
INDEX=0

while [ $INDEX -lt $TOTAL ]; do
    BATCH_SIZE=$((RANDOM % 5 + 1))
    BATCH=("${ALL_ITEMS[@]:INDEX:BATCH_SIZE}")

    # git add batch
    for item in "${BATCH[@]}"; do
        git add -vf "$item"
    done

    # Tanggal AUTHOR dan COMMITTER
    AUTHOR_DATE=$(random_date)
    AUTHOR_SEC=$(date -d "$AUTHOR_DATE" +%s)
    NOW_SEC=$(date +%s)
    COMMITTER_DATE=$(date -d "@$((RANDOM*(NOW_SEC-AUTHOR_SEC)/32768 + AUTHOR_SEC + 1))" +"%Y-%m-%dT%H:%M:%S")

    export GIT_AUTHOR_DATE="$AUTHOR_DATE"
    export GIT_COMMITTER_DATE="$COMMITTER_DATE"

    # Commit
    git commit -m "Upload batch $(($INDEX + 1))"
    git branch -M main

    # Next batch
    INDEX=$((INDEX + BATCH_SIZE))
done

# ==== Push aman ====
git pull --rebase origin main
git push -u origin main --force-with-lease

echo "✅ Selesai: semua file/folder sudah di-upload dengan Git LFS dan aman dari secret token."
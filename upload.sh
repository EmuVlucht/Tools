#!/bin/bash
# ==========================
# upload_git.sh
# ==========================
# Versi siap pakai: pilih GitHub/GitLab/Custom, tampilkan repo, lalu push semua file/folder
# ==========================

# ==== Konfigurasi Global ====
git config --global user.name "EmuVlucht"
git config --global user.email "emuvlucht@gmail.com"
git config --global --add safe.directory "$(pwd)"

# ==== Inisialisasi Git ====
git init
git config --global init.defaultBranch main

# ==== Variabel USER & Token ====
# Ganti sesuai akunmu
USER="EmuVlucht"
GITHUB_TOKEN="ghp_xxxxx"
GITLAB_TOKEN="glpat_xxxxx"

# ==== Pilih Platform ====
echo "Pilih platform upload ke repository Git:"
echo "1) GitHub"
echo "2) GitLab"
echo "3) Remote custom"
read -p "Masukkan pilihan (1/2/3): " PLATFORM

case "$PLATFORM" in
    1)
        if [ -z "$GITHUB_TOKEN" ]; then
            echo "Error: GITHUB_TOKEN belum diset!"
            exit 1
        fi
        API_URL="https://api.github.com/user/repos"
        AUTH_HEADER="Authorization: token ${GITHUB_TOKEN}"
        PLATFORM_NAME="GitHub"
        ;;
    2)
        if [ -z "$GITLAB_TOKEN" ]; then
            echo "Error: GITLAB_TOKEN belum diset!"
            exit 1
        fi
        API_URL="https://gitlab.com/api/v4/projects?owned=true"
        AUTH_HEADER="PRIVATE-TOKEN: ${GITLAB_TOKEN}"
        PLATFORM_NAME="GitLab"
        ;;
    3)
        read -p "Masukkan URL remote Git custom: " CUSTOM_URL
        REMOTE_URL="$CUSTOM_URL"
        PLATFORM_NAME="Custom"
        ;;
    *)
        echo "Pilihan tidak valid!"
        exit 1
        ;;
esac

# ==== Ambil daftar repo jika bukan custom ====
if [ "$PLATFORM" != "3" ]; then
    echo "Mengambil daftar repository di ${PLATFORM_NAME} …"
    REPO_LIST_JSON=$(curl -s -H "${AUTH_HEADER}" "${API_URL}?per_page=100")
    # Pastikan jq sudah terinstall
    if ! command -v jq &> /dev/null; then
        echo "Error: jq belum terinstall. Silakan install jq dulu."
        exit 1
    fi
    echo "Daftar repo:"
    echo "$REPO_LIST_JSON" | jq -r '.[].name'
    read -p "Ketik nama repo yang ingin digunakan: " REPO_CHOICE

    if [ "$PLATFORM" = "1" ]; then
        REMOTE_URL="https://${GITHUB_TOKEN}@github.com/${USER}/${REPO_CHOICE}.git"
    else
        REMOTE_URL="https://${GITLAB_TOKEN}@gitlab.com/${USER}/${REPO_CHOICE}.git"
    fi
fi

# ==== Set remote Git ====
if git remote get-url origin &>/dev/null; then
    git remote set-url origin "$REMOTE_URL"
else
    git remote add origin "$REMOTE_URL"
fi

# ==== Setup Git LFS untuk file besar ====
git lfs install
git lfs track "*.zip"
git lfs track "*.z01"
git lfs track "*.z02"
git add .gitattributes

# ==== Fungsi tanggal acak ====
random_date(){
    now=$(date +%s)
    start=0
    echo $(date -d "@$((RANDOM*(now-start)/32768 + start))" +"%Y-%m-%dT%H:%M:%S")
}

# ==== Ambil semua file/folder kecuali .git dan skrip ====
mapfile -t ALL_ITEMS < <(find . -mindepth 1 \
  ! -path "*/.git/*" \
  ! -name ".git" \
  ! -name "$0" \
  ! -name "gen-gitignore.sh" \
  | shuf)

TOTAL=${#ALL_ITEMS[@]}
INDEX=0

while [ $INDEX -lt $TOTAL ]; do
    BATCH_SIZE=$((RANDOM % 5 + 1))
    BATCH=("${ALL_ITEMS[@]:INDEX:BATCH_SIZE}")
    for item in "${BATCH[@]}"; do
        git add -vf "$item"
    done
    AUTHOR_DATE=$(random_date)
    AUTHOR_SEC=$(date -d "$AUTHOR_DATE" +%s)
    NOW_SEC=$(date +%s)
    COMMITTER_DATE=$(date -d "@$((RANDOM*(NOW_SEC-AUTHOR_SEC)/32768 + AUTHOR_SEC + 1))" +"%Y-%m-%dT%H:%M:%S")

    export GIT_AUTHOR_DATE="$AUTHOR_DATE"
    export GIT_COMMITTER_DATE="$COMMITTER_DATE"

    git commit -m "Upload batch $(($INDEX + 1))"
    git branch -M main

    INDEX=$((INDEX + BATCH_SIZE))
done

# ==== Push ====
git pull --rebase origin main
git push -u origin main --force-with-lease

echo "✅ Selesai: upload ke ${PLATFORM_NAME} repo '${REPO_CHOICE}'"
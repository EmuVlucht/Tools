#!/usr/bin/env bash
# search.sh
# Cari string pada nama file/folder dan isi file dengan output berwarna.
# Usage:
#   ./search.sh [path]
# default path = current directory

# Warna ANSI
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
RESET='\033[0m'

# Fungsi untuk teks disko bergerak
print_disco_animated() {
    local text="$1"
    local colors=("$RED" "$GREEN" "$YELLOW" "$BLUE" "$MAGENTA" "$CYAN")
    local color_count=${#colors[@]}
    local length=${#text}
    local frames=20
    local delay=0.05
    
    # Mode 1: Kiri ke Kanan
    for (( frame=0; frame<frames; frame++ )); do
        echo -ne "\r"
        for (( i=0; i<length; i++ )); do
            color_index=$(( (i + frame) % color_count ))
            echo -en "${colors[$color_index]}${text:$i:1}"
        done
        echo -en "$RESET"
        sleep $delay
    done
    
    # Mode 2: Kanan ke Kiri
    for (( frame=0; frame<frames; frame++ )); do
        echo -ne "\r"
        for (( i=0; i<length; i++ )); do
            color_index=$(( (i - frame + color_count * 100) % color_count ))
            echo -en "${colors[$color_index]}${text:$i:1}"
        done
        echo -en "$RESET"
        sleep $delay
    done
    
    # Mode 3: Tengah ke Pinggir
    for (( frame=0; frame<frames; frame++ )); do
        echo -ne "\r"
        local mid=$((length / 2))
        for (( i=0; i<length; i++ )); do
            local distance=$(( i > mid ? i - mid : mid - i ))
            color_index=$(( (distance + frame) % color_count ))
            echo -en "${colors[$color_index]}${text:$i:1}"
        done
        echo -en "$RESET"
        sleep $delay
    done
    
    # Mode 4: Pinggir ke Tengah
    for (( frame=0; frame<frames; frame++ )); do
        echo -ne "\r"
        local mid=$((length / 2))
        for (( i=0; i<length; i++ )); do
            local distance=$(( i > mid ? i - mid : mid - i ))
            color_index=$(( (color_count - distance + frame) % color_count ))
            echo -en "${colors[$color_index]}${text:$i:1}"
        done
        echo -en "$RESET"
        sleep $delay
    done
    
    echo # Newline setelah animasi selesai
}

# Fungsi untuk highlight case-insensitive
highlight_query() {
    local line="$1"
    local query="$2"
    
    # Gunakan awk untuk case-insensitive replacement
    echo "$line" | awk -v q="$query" -v blue="$BLUE" -v reset="$RESET" '
    {
        result = ""
        text = $0
        query_len = length(q)
        
        while (length(text) > 0) {
            # Cari posisi query (case-insensitive)
            pos = index(tolower(text), tolower(q))
            
            if (pos > 0) {
                # Tambahkan teks sebelum match
                result = result substr(text, 1, pos - 1)
                # Tambahkan match dengan warna biru
                result = result blue substr(text, pos, query_len) reset
                # Lanjutkan dari setelah match
                text = substr(text, pos + query_len)
            } else {
                # Tidak ada match lagi
                result = result text
                break
            }
        }
        print result
    }'
}

# Input query
echo -en "${GREEN}"
read -p "Masukan Sesuatu yang mau dicari : " QUERY
echo -en "$RESET"

ROOT="${1:-.}"

# Tampilkan pesan pencarian dengan efek disko animasi
echo
print_disco_animated "Mencari: '$QUERY' di: $ROOT"
echo

# Pencarian pada NAMA file/folder
echo -e "${YELLOW}>>> Pencarian pada NAMA file / folder:${RESET}"
find "$ROOT" -iname "*$QUERY*" -print 2>/dev/null | while IFS= read -r line; do
    highlight_query "$line" "$QUERY"
done

echo
# Pencarian pada ISI file
echo -e "${YELLOW}>>> Pencarian pada ISI file (rekursif):${RESET}"
grep -RInF --binary-files=text --line-number "$QUERY" "$ROOT" 2>/dev/null | while IFS= read -r line; do
    highlight_query "$line" "$QUERY"
done

echo
echo -e "${GREEN}Selesai.${RESET}"
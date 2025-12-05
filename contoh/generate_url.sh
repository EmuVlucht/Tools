#!/bin/bash

# Script untuk membuat URL dengan parameter acak terstruktur
# Format: key=value&key=value&...
# Maksimal total 123456 karakter setelah tanda "?"

# URL dasar (bisa diganti sesuai kebutuhan)
BASE_URL="https://chat.whatsapp.com/DEWH54Hdqk281Vl2hp0Hdy"

# Karakter untuk key dan value
CHARS_KEY="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
CHARS_VALUE="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_=-.%+"

# Panjang target parameter (maksimal 123456)
MAX_LENGTH=123456

# Fungsi untuk generate string acak
generate_random_string() {
    local length=$1
    local charset=$2
    local result=""
    
    for ((i=0; i<length; i++)); do
        random_index=$((RANDOM % ${#charset}))
        result="${result}${charset:$random_index:1}"
    done
    
    echo "$result"
}

# Fungsi untuk generate parameter terstruktur
generate_structured_params() {
    local target_length=$1
    local result=""
    local current_length=0
    
    while [ $current_length -lt $target_length ]; do
        # Panjang key dan value acak (antara 5-50 karakter)
        key_length=$((RANDOM % 46 + 5))
        value_length=$((RANDOM % 100 + 20))
        
        # Generate key dan value
        key=$(generate_random_string $key_length "$CHARS_KEY")
        value=$(generate_random_string $value_length "$CHARS_VALUE")
        
        # Buat pasangan key=value
        if [ -z "$result" ]; then
            pair="${key}=${value}"
        else
            pair="&${key}=${value}"
        fi
        
        # Cek apakah masih muat
        pair_length=${#pair}
        if [ $((current_length + pair_length)) -gt $target_length ]; then
            # Jika tidak muat, buat pair terakhir yang pas
            remaining=$((target_length - current_length - 1))
            if [ $remaining -gt 5 ]; then
                key=$(generate_random_string 3 "$CHARS_KEY")
                value_len=$((remaining - 4))
                if [ $value_len -gt 0 ]; then
                    value=$(generate_random_string $value_len "$CHARS_VALUE")
                    result="${result}&${key}=${value}"
                fi
            fi
            break
        fi
        
        # Tambahkan ke result
        result="${result}${pair}"
        current_length=${#result}
    done
    
    echo "$result"
}

# Main
echo "=== Generator URL dengan Parameter Terstruktur Acak ==="
echo "Target panjang parameter: $MAX_LENGTH karakter"
echo "Generating parameters..."
echo ""

# Generate parameter terstruktur
RANDOM_PARAMS=$(generate_structured_params $MAX_LENGTH)

# Gabungkan URL dasar dengan parameter
FINAL_URL="${BASE_URL}?${RANDOM_PARAMS}"

# Tampilkan hasil
echo "✓ URL telah dibuat!"
echo ""
echo "Statistik:"
echo "- Panjang parameter: ${#RANDOM_PARAMS} karakter"
echo "- Panjang total URL: ${#FINAL_URL} karakter"
echo "- Jumlah parameter: $(echo "$RANDOM_PARAMS" | grep -o '&' | wc -l) pasang"
echo ""
echo "--- Preview (150 karakter pertama) ---"
echo "${FINAL_URL:0:150}..."
echo ""

# Simpan ke file
OUTPUT_FILE="generated_url.txt"
echo "$FINAL_URL" > "$OUTPUT_FILE"
echo "✓ URL lengkap telah disimpan ke: $OUTPUT_FILE"
echo ""

# Opsi untuk melihat URL lengkap
read -p "Tampilkan URL lengkap? (y/n): " show_full
if [[ "$show_full" == "y" || "$show_full" == "Y" ]]; then
    echo ""
    echo "=== URL LENGKAP ==="
    echo "$FINAL_URL"
fi

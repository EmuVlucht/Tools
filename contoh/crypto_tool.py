#!/usr/bin/env python3
"""
SECURE FILE ENCRYPTION/DECRYPTION TOOL
=====================================
Menggunakan AES-256-GCM dengan PBKDF2 key derivation
Output dalam format URL WhatsApp yang aman

PERINGATAN: Jangan modifikasi script ini!
Modifikasi dapat menyebabkan data terenkripsi tidak bisa didekripsi.
"""

import sys
import os
import hashlib
import secrets
import base64
import struct
import hmac
from getpass import getpass
from pathlib import Path

try:
    from Crypto.Cipher import AES
except ImportError:
    print("ERROR: Modul tidak lengkap!")
    print("Jalankan: pip install pycryptodome")
    sys.exit(1)

# Karakter untuk encoding output (sesuai permintaan)
# Mapping dari base64 ke charset custom
CUSTOM_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
B64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

# URL prefix
URL_PREFIX = "https://chat.whatsapp.com/DEWH54Hdqk281Vl2hp0Hdy?"

# Konstanta keamanan
SALT_SIZE = 32
NONCE_SIZE = 12
TAG_SIZE = 16
KEY_SIZE = 32

# PBKDF2 parameters (sangat kuat)
PBKDF2_ITERATIONS = 600000


def _derive_key(password: str, salt: bytes) -> bytes:
    """Derive encryption key menggunakan PBKDF2-SHA512"""
    key = hashlib.pbkdf2_hmac(
        'sha512',
        password.encode('utf-8'),
        salt,
        iterations=PBKDF2_ITERATIONS,
        dklen=KEY_SIZE
    )
    return key


def _bytes_to_custom_encoding(data: bytes) -> str:
    """Convert bytes ke custom encoding menggunakan charset yang diminta
    Karakter yang digunakan: a-z A-Z 0-9 _ - . % +
    (& dan = digunakan sebagai separator URL)
    """
    # Encode ke base64 terlebih dahulu
    b64_encoded = base64.b64encode(data).decode('ascii')
    
    # Replace karakter base64 dengan custom chars
    # Base64 chars: A-Z a-z 0-9 + / =
    # Target chars: a-z A-Z 0-9 _ - . % +
    result = []
    for char in b64_encoded:
        if char == '=':
            result.append('_')  # padding -> underscore
        elif char == '+':
            result.append('%')  # plus -> percent
        elif char == '/':
            result.append('-')  # slash -> dash
        else:
            # Huruf dan angka tetap
            result.append(char)
    
    return ''.join(result)


def _custom_encoding_to_bytes(encoded: str) -> bytes:
    """Convert custom encoding kembali ke bytes"""
    # Replace custom chars kembali ke base64
    result = []
    for char in encoded:
        if char == '_':
            result.append('=')  # underscore -> padding
        elif char == '%':
            result.append('+')  # percent -> plus
        elif char == '-':
            result.append('/')  # dash -> slash
        else:
            result.append(char)
    
    b64_string = ''.join(result)
    
    # Decode dari base64
    return base64.b64decode(b64_string)


def _format_as_url_params(data: str, seed: int) -> str:
    """Format data sebagai URL parameters yang terstruktur (deterministic)"""
    import random
    rng = random.Random(seed)
    
    result = []
    i = 0
    data_len = len(data)
    
    while i < data_len:
        # Deterministic key length (5-20 chars)
        key_len = rng.randint(5, 20)
        key_len = min(key_len, data_len - i)
        
        if key_len <= 0:
            break
            
        key = data[i:i + key_len]
        i += key_len
        
        # Deterministic value length (20-80 chars)
        val_len = rng.randint(20, 80)
        val_len = min(val_len, data_len - i)
        
        value = data[i:i + val_len] if val_len > 0 else ""
        i += val_len
        
        if result:
            result.append(f"&{key}={value}")
        else:
            result.append(f"{key}={value}")
    
    return ''.join(result)


def _parse_url_params(url_data: str) -> str:
    """Parse URL parameters kembali ke data asli"""
    # Remove URL prefix if exists
    if url_data.startswith(URL_PREFIX):
        url_data = url_data[len(URL_PREFIX):]
    
    # Remove separators & and =
    result = url_data.replace('=', '').replace('&', '')
    
    return result


def encrypt_file(input_path: str, output_path: str, password: str) -> bool:
    """Enkripsi file dengan keamanan tinggi"""
    try:
        # Baca file input
        with open(input_path, 'rb') as f:
            plaintext = f.read()
        
        # Generate random salt dan nonce
        salt = secrets.token_bytes(SALT_SIZE)
        nonce = secrets.token_bytes(NONCE_SIZE)
        
        # Derive key
        key = _derive_key(password, salt)
        
        # Encrypt dengan AES-256-GCM
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        
        # Add associated data untuk integrity
        original_filename = os.path.basename(input_path).encode('utf-8')
        cipher.update(original_filename)
        
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        
        # Pack data: salt + nonce + tag + filename_len + filename + ciphertext
        filename_len = struct.pack('>H', len(original_filename))
        packed_data = salt + nonce + tag + filename_len + original_filename + ciphertext
        
        # Compute HMAC untuk verifikasi tambahan
        hmac_key = hashlib.sha256(key + b'hmac_verify').digest()
        data_hmac = hmac.new(hmac_key, packed_data, hashlib.sha256).digest()
        
        # Final data dengan HMAC
        final_data = data_hmac + packed_data
        
        # Convert ke custom encoding
        encoded = _bytes_to_custom_encoding(final_data)
        
        # Generate deterministic seed untuk formatting
        format_seed = int.from_bytes(salt[:4], 'big')
        
        # Format sebagai URL parameters
        url_params = _format_as_url_params(encoded, format_seed)
        
        # Final output dengan URL prefix
        final_output = URL_PREFIX + url_params
        
        # Tulis ke file output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_output)
        
        return True
        
    except Exception as e:
        print(f"ERROR saat enkripsi: {e}")
        import traceback
        traceback.print_exc()
        return False


def decrypt_file(input_path: str, output_dir: str, password: str) -> bool:
    """Dekripsi file terenkripsi"""
    try:
        # Baca file terenkripsi
        with open(input_path, 'r', encoding='utf-8') as f:
            encrypted_data = f.read().strip()
        
        # Parse URL params
        encoded = _parse_url_params(encrypted_data)
        
        # Decode dari custom encoding
        packed_with_hmac = _custom_encoding_to_bytes(encoded)
        
        # Extract HMAC dan data
        data_hmac = packed_with_hmac[:32]
        packed_data = packed_with_hmac[32:]
        
        # Extract components
        salt = packed_data[:SALT_SIZE]
        nonce = packed_data[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
        tag = packed_data[SALT_SIZE + NONCE_SIZE:SALT_SIZE + NONCE_SIZE + TAG_SIZE]
        
        offset = SALT_SIZE + NONCE_SIZE + TAG_SIZE
        filename_len = struct.unpack('>H', packed_data[offset:offset + 2])[0]
        offset += 2
        
        original_filename = packed_data[offset:offset + filename_len]
        offset += filename_len
        
        ciphertext = packed_data[offset:]
        
        # Derive key
        key = _derive_key(password, salt)
        
        # Verify HMAC
        hmac_key = hashlib.sha256(key + b'hmac_verify').digest()
        expected_hmac = hmac.new(hmac_key, packed_data, hashlib.sha256).digest()
        
        if not hmac.compare_digest(data_hmac, expected_hmac):
            print("ERROR: Kata rahasia salah atau file rusak!")
            return False
        
        # Decrypt dengan AES-256-GCM
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        cipher.update(original_filename)
        
        try:
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        except ValueError:
            print("ERROR: Kata rahasia salah atau file telah dimodifikasi!")
            return False
        
        # Tulis file output
        output_filename = original_filename.decode('utf-8')
        output_path = os.path.join(output_dir, f"decrypted_{output_filename}")
        
        with open(output_path, 'wb') as f:
            f.write(plaintext)
        
        print(f"File berhasil didekripsi: {output_path}")
        return True
        
    except Exception as e:
        print(f"ERROR saat dekripsi: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("   SECURE FILE ENCRYPTION/DECRYPTION TOOL")
    print("   AES-256-GCM + PBKDF2 Key Derivation")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 3:
        print("Penggunaan:")
        print("  Enkripsi: python crypto_tool.py encrypt <file_input>")
        print("  Dekripsi: python crypto_tool.py decrypt <file_terenkripsi>")
        print()
        print("Contoh:")
        print("  python crypto_tool.py encrypt dokumen.txt")
        print("  python crypto_tool.py decrypt dokumen.txt.encrypted")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    input_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"ERROR: File tidak ditemukan: {input_file}")
        sys.exit(1)
    
    if mode == 'encrypt':
        print(f"Mode: ENKRIPSI")
        print(f"File: {input_file}")
        print()
        
        # Minta kata rahasia
        password = getpass("Masukkan kata rahasia: ")
        if len(password) < 8:
            print("ERROR: Kata rahasia minimal 8 karakter!")
            sys.exit(1)
        
        password_confirm = getpass("Konfirmasi kata rahasia: ")
        if password != password_confirm:
            print("ERROR: Kata rahasia tidak cocok!")
            sys.exit(1)
        
        output_file = input_file + ".encrypted"
        
        print()
        print("Mengenkripsi file... (ini mungkin memakan waktu)")
        
        if encrypt_file(input_file, output_file, password):
            print()
            print("=" * 60)
            print("SUKSES! File berhasil dienkripsi!")
            print(f"Output: {output_file}")
            print("=" * 60)
        else:
            print("GAGAL! Enkripsi tidak berhasil.")
            sys.exit(1)
    
    elif mode == 'decrypt':
        print(f"Mode: DEKRIPSI")
        print(f"File: {input_file}")
        print()
        
        # Minta kata rahasia
        password = getpass("Masukkan kata rahasia: ")
        
        output_dir = os.path.dirname(input_file) or "."
        
        print()
        print("Mendekripsi file... (ini mungkin memakan waktu)")
        
        if decrypt_file(input_file, output_dir, password):
            print()
            print("=" * 60)
            print("SUKSES! File berhasil didekripsi!")
            print("=" * 60)
        else:
            print("GAGAL! Dekripsi tidak berhasil.")
            sys.exit(1)
    
    else:
        print(f"ERROR: Mode tidak dikenal: {mode}")
        print("Gunakan 'encrypt' atau 'decrypt'")
        sys.exit(1)


if __name__ == "__main__":
    main()

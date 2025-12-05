#!/usr/bin/env python3
"""
Test script untuk crypto_tool.py
"""

import os
import sys

# Import fungsi dari crypto_tool
from crypto_tool import encrypt_file, decrypt_file

def test_encryption_decryption():
    """Test enkripsi dan dekripsi"""
    
    test_file = "text.txt"
    encrypted_file = "text.txt.encrypted"
    password = "KataRahasia123!"
    
    print("=" * 60)
    print("TEST ENKRIPSI/DEKRIPSI")
    print("=" * 60)
    print()
    
    # Check if test file exists
    if not os.path.exists(test_file):
        print(f"ERROR: File test tidak ditemukan: {test_file}")
        return False
    
    # Read original content
    with open(test_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    print(f"1. File asli: {test_file}")
    print(f"   Ukuran: {len(original_content)} bytes")
    print()
    
    # Test enkripsi
    print("2. Mengenkripsi file...")
    if not encrypt_file(test_file, encrypted_file, password):
        print("   GAGAL!")
        return False
    print("   SUKSES!")
    
    # Check encrypted file
    with open(encrypted_file, 'r', encoding='utf-8') as f:
        encrypted_content = f.read()
    
    print(f"   File terenkripsi: {encrypted_file}")
    print(f"   Ukuran: {len(encrypted_content)} bytes")
    print()
    print("   Preview hasil enkripsi (200 karakter pertama):")
    print(f"   {encrypted_content[:200]}...")
    print()
    
    # Test dekripsi
    print("3. Mendekripsi file...")
    if not decrypt_file(encrypted_file, ".", password):
        print("   GAGAL!")
        return False
    print("   SUKSES!")
    
    # Verify decrypted content
    decrypted_file = f"decrypted_{test_file}"
    with open(decrypted_file, 'r', encoding='utf-8') as f:
        decrypted_content = f.read()
    
    print()
    print("4. Verifikasi hasil dekripsi...")
    if original_content == decrypted_content:
        print("   SUKSES! Konten sama persis dengan aslinya!")
    else:
        print("   GAGAL! Konten berbeda!")
        return False
    
    print()
    print("=" * 60)
    print("SEMUA TEST BERHASIL!")
    print("=" * 60)
    
    # Cleanup
    os.remove(decrypted_file)
    print(f"\nFile test '{decrypted_file}' telah dihapus.")
    
    return True


def test_wrong_password():
    """Test dengan password salah"""
    
    encrypted_file = "text.txt.encrypted"
    wrong_password = "PasswordSalah!"
    
    print()
    print("=" * 60)
    print("TEST PASSWORD SALAH")
    print("=" * 60)
    print()
    
    if not os.path.exists(encrypted_file):
        print("Tidak ada file terenkripsi untuk ditest.")
        return True
    
    print("Mencoba dekripsi dengan password salah...")
    result = decrypt_file(encrypted_file, ".", wrong_password)
    
    if not result:
        print("SUKSES! Dekripsi gagal seperti yang diharapkan.")
        return True
    else:
        print("GAGAL! Dekripsi seharusnya gagal dengan password salah!")
        return False


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    success = test_encryption_decryption()
    if success:
        test_wrong_password()

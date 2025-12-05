#!/usr/bin/env python3
"""
Script contoh untuk testing obfuscator.
Ini akan menampilkan beberapa output untuk membuktikan kode berjalan.
"""

import os
import sys
from datetime import datetime

def greeting():
    print("=" * 50)
    print("  SCRIPT INI BERHASIL DIJALANKAN!")
    print("=" * 50)
    print()

def show_info():
    print(f"Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: {sys.platform}")
    print(f"Working dir: {os.getcwd()}")
    print()

def calculate():
    print("Test perhitungan:")
    for i in range(1, 6):
        result = i ** 2
        print(f"  {i}^2 = {result}")
    print()

def secret_message():
    message = "Ini adalah pesan rahasia yang ter-obfuscate!"
    print(f"Pesan: {message}")
    print()

def main():
    greeting()
    show_info()
    calculate()
    secret_message()
    print("Script selesai dengan sukses!")

if __name__ == "__main__":
    main()

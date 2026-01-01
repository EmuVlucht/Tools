#!/usr/bin/env python3
"""
PYTHON CODE OBFUSCATOR
======================
Mengubah kode Python menjadi bentuk URL WhatsApp yang bisa dijalankan langsung.
Output bisa dijalankan dengan: python3 nama_file.py

Karakter yang digunakan: a-z A-Z 0-9 _ = - . & % +
"""

import sys
import os
import marshal
import base64
import zlib
import random
from getpass import getpass


# URL prefix
URL_PREFIX = "https://chat.whatsapp.com/LZU6fs32eGnHtWaI3IIg4Y?"


def _bytes_to_custom_encoding(data: bytes) -> str:
    """Convert bytes ke custom encoding"""
    b64_encoded = base64.b64encode(data).decode('ascii')
    
    result = []
    for char in b64_encoded:
        if char == '=':
            result.append('_')
        elif char == '+':
            result.append('%')
        elif char == '/':
            result.append('-')
        else:
            result.append(char)
    
    return ''.join(result)


def _custom_encoding_to_bytes(encoded: str) -> bytes:
    """Convert custom encoding kembali ke bytes"""
    result = []
    for char in encoded:
        if char == '_':
            result.append('=')
        elif char == '%':
            result.append('+')
        elif char == '-':
            result.append('/')
        else:
            result.append(char)
    
    return base64.b64decode(''.join(result))


def _add_extra_chars(data: str, seed: int) -> str:
    """Tambahkan karakter . dan + secara acak"""
    rng = random.Random(seed)
    result = list(data)
    extra_chars = '.+'
    num_extras = max(1, len(data) // 15)
    
    for _ in range(num_extras):
        pos = rng.randint(0, len(result))
        char = extra_chars[rng.randint(0, 1)]
        result.insert(pos, char)
    
    return ''.join(result)


def _format_as_url(data: str, seed: int) -> str:
    """Format sebagai URL parameters"""
    rng = random.Random(seed)
    data = _add_extra_chars(data, seed + 1)
    
    result = []
    i = 0
    data_len = len(data)
    
    while i < data_len:
        key_len = rng.randint(5, 15)
        key_len = min(key_len, data_len - i)
        
        if key_len <= 0:
            break
            
        key = data[i:i + key_len]
        i += key_len
        
        val_len = rng.randint(20, 60)
        val_len = min(val_len, data_len - i)
        
        value = data[i:i + val_len] if val_len > 0 else ""
        i += val_len
        
        if result:
            result.append(f"&{key}={value}")
        else:
            result.append(f"{key}={value}")
    
    return URL_PREFIX + ''.join(result)


def obfuscate_file(input_path: str, output_path: str, password: str = None) -> bool:
    """Obfuscate file Python menjadi bentuk URL yang bisa dijalankan"""
    try:
        # Baca source code
        with open(input_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Compile ke bytecode
        code_obj = compile(source_code, '<obfuscated>', 'exec')
        marshaled = marshal.dumps(code_obj)
        
        # Compress
        compressed = zlib.compress(marshaled, 9)
        
        # Encode ke custom format
        seed = random.randint(10000, 99999)
        encoded = _bytes_to_custom_encoding(compressed)
        url_data = _format_as_url(encoded, seed)
        
        # Generate decoder script
        decoder_template = '''# -*- coding: utf-8 -*-
import marshal as _m, zlib as _z, base64 as _b
_U="{url_data}"
def _d(s):
    s=s.split("?",1)[1] if "?" in s else s
    s=s.replace("=","").replace("&","").replace(".","").replace("+","")
    r=[]
    for c in s:
        if c=="_":r.append("=")
        elif c=="%":r.append("+")
        elif c=="-":r.append("/")
        else:r.append(c)
    return _b.b64decode("".join(r))
exec(_m.loads(_z.decompress(_d(_U))))
'''
        
        # Jika ada password, enkripsi URL data
        if password:
            import hashlib
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import pad, unpad
            import secrets
            
            # Derive key
            salt = secrets.token_bytes(16)
            key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, 32)
            
            # Encrypt
            iv = secrets.token_bytes(16)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            encrypted = cipher.encrypt(pad(url_data.encode(), AES.block_size))
            
            # Encode encrypted data
            enc_data = base64.b64encode(salt + iv + encrypted).decode()
            
            decoder_template = '''# -*- coding: utf-8 -*-
import marshal as _m, zlib as _z, base64 as _b, hashlib as _h
from Crypto.Cipher import AES as _A
from Crypto.Util.Padding import unpad as _u
_E="{enc_data}"
def _k():
    import getpass
    return getpass.getpass("Masukkan kata rahasia: ")
def _d(s):
    s=s.split("?",1)[1] if "?" in s else s
    s=s.replace("=","").replace("&","").replace(".","").replace("+","")
    r=[]
    for c in s:
        if c=="_":r.append("=")
        elif c=="%":r.append("+")
        elif c=="-":r.append("/")
        else:r.append(c)
    return _b.b64decode("".join(r))
def _x():
    p=_k()
    d=_b.b64decode(_E)
    s,i,e=d[:16],d[16:32],d[32:]
    k=_h.pbkdf2_hmac("sha256",p.encode(),s,100000,32)
    try:
        c=_A.new(k,_A.MODE_CBC,i)
        return _u(c.decrypt(e),_A.block_size).decode()
    except:
        print("ERROR: Kata rahasia salah!")
        exit(1)
exec(_m.loads(_z.decompress(_d(_x()))))
'''.replace("{enc_data}", enc_data)
        else:
            decoder_template = decoder_template.replace("{url_data}", url_data)
        
        # Write output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(decoder_template)
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("   PYTHON CODE OBFUSCATOR")
    print("   Mengubah kode Python menjadi URL WhatsApp")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("Penggunaan:")
        print("  python Python_obfuscator.py <file.py> [output.py]")
        print()
        print("Contoh:")
        print("  python Python_obfuscator.py script.py")
        print("  python Python_obfuscator.py script.py protected.py")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"ERROR: File tidak ditemukan: {input_file}")
        sys.exit(1)
    
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_protected.py"
    
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print()
    
    # Tanya apakah mau pakai password
    use_password = input("Gunakan kata rahasia? (y/n): ").lower().strip()
    
    password = None
    if use_password == 'y':
        password = getpass("Masukkan kata rahasia: ")
        if len(password) < 6:
            print("ERROR: Kata rahasia minimal 6 karakter!")
            sys.exit(1)
        password_confirm = getpass("Konfirmasi kata rahasia: ")
        if password != password_confirm:
            print("ERROR: Kata rahasia tidak cocok!")
            sys.exit(1)
    
    print()
    print("Memproses...")
    
    if obfuscate_file(input_file, output_file, password):
        print()
        print("=" * 60)
        print("SUKSES!")
        print(f"File terproteksi: {output_file}")
        print()
        print("Cara menjalankan:")
        print(f"  python3 {output_file}")
        print("=" * 60)
    else:
        print("GAGAL!")
        sys.exit(1)


if __name__ == "__main__":
    main()

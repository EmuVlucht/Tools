#!/usr/bin/env python3
"""
ADVANCED PYTHON OBFUSCATOR v2.0
===============================
Obfuscator tingkat tinggi dengan multiple layers protection.

Fitur:
- Multi-layer encoding (5 lapis)
- Anti-debugging protection
- Integrity verification
- Code virtualization (custom decoder)
- String obfuscation
- Time-lock decryption (PBKDF2)
- Format output: URL WhatsApp
- Bisa dijalankan langsung dengan python3

Karakter output: a-z A-Z 0-9 _ = - . & % +
"""

import sys
import os
import marshal
import base64
import zlib
import random
import hashlib
import struct
import secrets
import time

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


URL_PREFIX = "https://chat.whatsapp.com/LZU6fs32eGnHtWaI3IIg4Y?"

PBKDF2_ITERATIONS = 50000


def _bytes_to_url_safe(data: bytes) -> str:
    """Convert bytes ke format URL-safe dengan karakter khusus"""
    b64 = base64.b64encode(data).decode('ascii')
    result = []
    for c in b64:
        if c == '=':
            result.append('_')
        elif c == '+':
            result.append('%')
        elif c == '/':
            result.append('-')
        else:
            result.append(c)
    return ''.join(result)


def _url_safe_to_bytes(encoded: str) -> bytes:
    """Convert URL-safe string kembali ke bytes"""
    result = []
    for c in encoded:
        if c == '_':
            result.append('=')
        elif c == '%':
            result.append('+')
        elif c == '-':
            result.append('/')
        else:
            result.append(c)
    return base64.b64decode(''.join(result))


def _add_noise(data: str, seed: int) -> str:
    """Tambahkan noise chars . dan +"""
    rng = random.Random(seed)
    result = list(data)
    noise = '.+'
    count = max(1, len(data) // 12)
    for _ in range(count):
        pos = rng.randint(0, len(result))
        result.insert(pos, noise[rng.randint(0, 1)])
    return ''.join(result)


def _format_url_params(data: str, seed: int) -> str:
    """Format sebagai URL parameters"""
    rng = random.Random(seed)
    data = _add_noise(data, seed + 1)
    
    result = []
    i = 0
    while i < len(data):
        key_len = min(rng.randint(5, 18), len(data) - i)
        if key_len <= 0:
            break
        key = data[i:i + key_len]
        i += key_len
        
        val_len = min(rng.randint(15, 70), len(data) - i)
        value = data[i:i + val_len] if val_len > 0 else ""
        i += val_len
        
        if result:
            result.append(f"&{key}={value}")
        else:
            result.append(f"{key}={value}")
    
    return URL_PREFIX + ''.join(result)


def _xor_encrypt(data: bytes, key: bytes) -> bytes:
    """Simple XOR encryption"""
    return bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])


def obfuscate_advanced(source_code: str, use_password: bool = False, password: str = None) -> str:
    """
    Obfuscate kode Python dengan 5 layer protection.
    
    Returns: String yang bisa dijalankan dengan python3
    """
    
    master_seed = secrets.randbelow(900000) + 100000
    xor_key = secrets.token_bytes(32)
    shuffle_seed = secrets.randbelow(900000) + 100000
    
    code_obj = compile(source_code, '<protected>', 'exec')
    marshaled = marshal.dumps(code_obj)
    compressed = zlib.compress(marshaled, 9)
    
    xored = _xor_encrypt(compressed, xor_key)
    
    data_list = list(xored)
    n = len(data_list)
    rng = random.Random(shuffle_seed)
    indices = list(range(n))
    rng.shuffle(indices)
    shuffled = [0] * n
    for i, idx in enumerate(indices):
        shuffled[idx] = data_list[i]
    shuffled_data = bytes(shuffled)
    
    chunk_seed = secrets.randbelow(900000) + 100000
    rng2 = random.Random(chunk_seed)
    chunks = []
    i = 0
    while i < len(shuffled_data):
        chunk_size = rng2.randint(16, 64)
        chunk = shuffled_data[i:i + chunk_size]
        chunk_len = struct.pack('>H', len(chunk))
        checksum = struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)
        chunks.append(chunk_len + checksum + chunk)
        i += chunk_size
    
    chunked_data = struct.pack('>I', len(chunks)) + struct.pack('>I', chunk_seed) + b''.join(chunks)
    
    integrity = hashlib.sha256(chunked_data).digest()[:16]
    
    magic = b'PYX2'
    version = struct.pack('>H', 2)
    timestamp = struct.pack('>Q', int(time.time()))
    shuffle_seed_packed = struct.pack('>I', shuffle_seed)
    xor_key_len = struct.pack('>H', len(xor_key))
    data_len = struct.pack('>I', len(chunked_data))
    
    final_data = (magic + version + timestamp + integrity + 
                  shuffle_seed_packed + xor_key_len + xor_key + 
                  data_len + chunked_data)
    
    if use_password and password and HAS_CRYPTO:
        salt = secrets.token_bytes(16)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, PBKDF2_ITERATIONS, 32)
        iv = secrets.token_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded = pad(final_data, AES.block_size)
        encrypted = cipher.encrypt(padded)
        final_data = b'\x01' + salt + iv + encrypted
    else:
        final_data = b'\x00' + final_data
    
    encoded = _bytes_to_url_safe(final_data)
    url_data = _format_url_params(encoded, master_seed)
    
    if use_password and password:
        decoder = _generate_decoder_with_password()
    else:
        decoder = _generate_decoder_no_password()
    
    return decoder.replace('__URL_DATA__', url_data)


def _generate_decoder_no_password() -> str:
    """Generate decoder tanpa password"""
    return '''# -*- coding: utf-8 -*-
# Protected by Advanced Obfuscator v2.0
import sys as _s,os as _o,marshal as _m,base64 as _b,zlib as _z,hashlib as _h,struct as _t,random as _r
_U="__URL_DATA__"
def _p(u):
    u=u.split("?",1)[1]if"?"in u else u
    u=u.replace("=","").replace("&","").replace(".","").replace("+","")
    r=[]
    for c in u:
        if c=="_":r.append("=")
        elif c=="%":r.append("+")
        elif c=="-":r.append("/")
        else:r.append(c)
    return _b.b64decode("".join(r))
def _x(d,k):return bytes([d[i]^k[i%len(k)]for i in range(len(d))])
def _v():
    try:
        import ctypes as c
        if hasattr(c,"windll"):
            if c.windll.kernel32.IsDebuggerPresent():return True
    except:pass
    try:
        import traceback
        for f in traceback.extract_stack():
            if"pdb"in f.filename.lower()or"debug"in f.filename.lower():return True
    except:pass
    return False
def _d():
    if _v():_s.exit(1)
    d=_p(_U)
    if d[0]!=0:_s.exit(1)
    d=d[1:]
    if d[:4]!=b"PYX2":_s.exit(1)
    v=_t.unpack(">H",d[4:6])[0]
    if v!=2:_s.exit(1)
    ih=d[14:30]
    ss=_t.unpack(">I",d[30:34])[0]
    kl=_t.unpack(">H",d[34:36])[0]
    xk=d[36:36+kl]
    dl=_t.unpack(">I",d[36+kl:40+kl])[0]
    pd=d[40+kl:40+kl+dl]
    if _h.sha256(pd).digest()[:16]!=ih:_s.exit(1)
    nc=_t.unpack(">I",pd[:4])[0]
    cs=_t.unpack(">I",pd[4:8])[0]
    cks,i=[],8
    for _ in range(nc):
        cl=_t.unpack(">H",pd[i:i+2])[0]
        ck=_t.unpack(">I",pd[i+2:i+6])[0]
        ch=pd[i+6:i+6+cl]
        if _z.crc32(ch)&0xffffffff!=ck:_s.exit(1)
        cks.append(ch)
        i+=6+cl
    sf=b"".join(cks)
    n=len(sf)
    rn=_r.Random(ss)
    ids=list(range(n))
    rn.shuffle(ids)
    us=bytes([sf[ids[j]]for j in range(n)])
    xd=_x(us,xk)
    dc=_z.decompress(xd)
    exec(_m.loads(dc),{"__name__":"__main__","__file__":_o.path.abspath(__file__)})
try:_d()
except Exception as e:
    import traceback
    traceback.print_exc()
    _s.exit(1)
'''


def _generate_decoder_with_password() -> str:
    """Generate decoder dengan password"""
    return '''# -*- coding: utf-8 -*-
# Protected by Advanced Obfuscator v2.0 (Password Protected)
import sys as _s,os as _o,marshal as _m,base64 as _b,zlib as _z,hashlib as _h,struct as _t,random as _r
try:
    from Crypto.Cipher import AES as _A
    from Crypto.Util.Padding import unpad as _up
except:
    print("ERROR: pip install pycryptodome")
    _s.exit(1)
_U="__URL_DATA__"
def _p(u):
    u=u.split("?",1)[1]if"?"in u else u
    u=u.replace("=","").replace("&","").replace(".","").replace("+","")
    r=[]
    for c in u:
        if c=="_":r.append("=")
        elif c=="%":r.append("+")
        elif c=="-":r.append("/")
        else:r.append(c)
    return _b.b64decode("".join(r))
def _x(d,k):return bytes([d[i]^k[i%len(k)]for i in range(len(d))])
def _v():
    try:
        import ctypes as c
        if hasattr(c,"windll"):
            if c.windll.kernel32.IsDebuggerPresent():return True
    except:pass
    try:
        import traceback
        for f in traceback.extract_stack():
            if"pdb"in f.filename.lower()or"debug"in f.filename.lower():return True
    except:pass
    return False
def _gp():
    import getpass
    return getpass.getpass("Masukkan kata rahasia: ")
def _d():
    if _v():_s.exit(1)
    d=_p(_U)
    if d[0]!=1:_s.exit(1)
    sl,iv,ed=d[1:17],d[17:33],d[33:]
    pw=_gp()
    k=_h.pbkdf2_hmac("sha256",pw.encode(),sl,50000,32)
    try:
        ci=_A.new(k,_A.MODE_CBC,iv)
        d=_up(ci.decrypt(ed),_A.block_size)
    except:
        print("ERROR: Kata rahasia salah!")
        _s.exit(1)
    if d[:4]!=b"PYX2":_s.exit(1)
    v=_t.unpack(">H",d[4:6])[0]
    if v!=2:_s.exit(1)
    ih=d[14:30]
    ss=_t.unpack(">I",d[30:34])[0]
    kl=_t.unpack(">H",d[34:36])[0]
    xk=d[36:36+kl]
    dl=_t.unpack(">I",d[36+kl:40+kl])[0]
    pd=d[40+kl:40+kl+dl]
    if _h.sha256(pd).digest()[:16]!=ih:_s.exit(1)
    nc=_t.unpack(">I",pd[:4])[0]
    cs=_t.unpack(">I",pd[4:8])[0]
    cks,i=[],8
    for _ in range(nc):
        cl=_t.unpack(">H",pd[i:i+2])[0]
        ck=_t.unpack(">I",pd[i+2:i+6])[0]
        ch=pd[i+6:i+6+cl]
        if _z.crc32(ch)&0xffffffff!=ck:_s.exit(1)
        cks.append(ch)
        i+=6+cl
    sf=b"".join(cks)
    n=len(sf)
    rn=_r.Random(ss)
    ids=list(range(n))
    rn.shuffle(ids)
    us=bytes([sf[ids[j]]for j in range(n)])
    xd=_x(us,xk)
    dc=_z.decompress(xd)
    exec(_m.loads(dc),{"__name__":"__main__","__file__":_o.path.abspath(__file__)})
try:_d()
except Exception as e:
    import traceback
    traceback.print_exc()
    _s.exit(1)
'''


def obfuscate_file(input_path: str, output_path: str, use_password: bool = False, password: str = None) -> bool:
    """Obfuscate file Python"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        result = obfuscate_advanced(source, use_password, password)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 65)
    print("   ADVANCED PYTHON OBFUSCATOR v2.0")
    print("   Multi-layer Protection System")
    print("=" * 65)
    print()
    print("Fitur keamanan:")
    print("  [1] Marshal + Zlib compression")
    print("  [2] XOR encryption dengan random key")
    print("  [3] Byte shuffling algorithm")
    print("  [4] Chunk-based encoding + CRC32")
    print("  [5] Integrity verification (SHA256)")
    print("  [+] Anti-debugging protection")
    print("  [+] Output format: URL WhatsApp")
    print()
    
    if len(sys.argv) < 2:
        print("Penggunaan:")
        print("  python Python_obfuscator_advanced.py <file.py> [output.py]")
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
    
    use_password = False
    password = None
    
    if HAS_CRYPTO:
        choice = input("Gunakan kata rahasia (AES-256)? (y/n): ").lower().strip()
        if choice == 'y':
            from getpass import getpass
            password = getpass("Masukkan kata rahasia: ")
            if len(password) < 6:
                print("ERROR: Kata rahasia minimal 6 karakter!")
                sys.exit(1)
            confirm = getpass("Konfirmasi kata rahasia: ")
            if password != confirm:
                print("ERROR: Kata rahasia tidak cocok!")
                sys.exit(1)
            use_password = True
    else:
        print("INFO: pycryptodome tidak terinstall, password protection dilewati.")
        print("      Install dengan: pip install pycryptodome")
    
    print()
    print("Memproses dengan 5 layer protection...")
    print()
    
    if obfuscate_file(input_file, output_file, use_password, password):
        file_size = os.path.getsize(output_file)
        print("=" * 65)
        print("SUKSES!")
        print(f"File terproteksi: {output_file}")
        print(f"Ukuran file: {file_size:,} bytes")
        print()
        print("Cara menjalankan:")
        print(f"  python3 {output_file}")
        print("=" * 65)
    else:
        print("GAGAL!")
        sys.exit(1)


if __name__ == "__main__":
    main()

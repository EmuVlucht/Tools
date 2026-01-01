#!/usr/bin/env python3
"""
ADVANCED SHELL SCRIPT OBFUSCATOR v2.0
=====================================
Obfuscator tingkat tinggi untuk Shell Script dengan 5 layer protection.

Fitur:
- Multi-layer encoding (5 lapis)
- Zlib compression
- XOR encryption dengan random key
- Byte shuffling algorithm
- Chunk-based encoding + CRC32
- Integrity verification (SHA256)
- Password protection (AES-256) - opsional
- Format output: URL WhatsApp
- Support: sh, bash, dash, zsh, fish, ksh, csh, tcsh
- Support semua jenis argumen (string, angka, path, flag, simbol, dll)

Karakter output: a-z A-Z 0-9 _ = - . & % +
"""

import sys
import os
import base64
import zlib
import hashlib
import struct
import secrets
import random

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


URL_PREFIX = "https://chat.whatsapp.com/LZU6fs32eGnHtWaI3IIg4Y?"

PBKDF2_ITERATIONS = 50000

SHELL_EXTENSIONS = {
    '.sh': 'bash',
    '.bash': 'bash',
    '.dash': 'dash',
    '.zsh': 'zsh',
    '.fish': 'fish',
    '.ksh': 'ksh',
    '.csh': 'csh',
    '.tcsh': 'tcsh'
}


def _lcg_next(state):
    """Linear Congruential Generator step"""
    return (state * 1103515245 + 12345) & 0x7fffffff


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
    """Tambahkan noise chars . dan + secara deterministik"""
    result = list(data)
    noise_chars = '.+'
    count = max(2, len(data) // 10)
    
    state = seed & 0x7fffffff
    for i in range(count):
        state = _lcg_next(state)
        pos = state % (len(result) + 1)
        noise = noise_chars[i % 2]
        result.insert(pos, noise)
    return ''.join(result)


def _format_url_params(data: str, seed: int) -> str:
    """Format sebagai URL parameters"""
    data = _add_noise(data, seed)
    
    state = (seed + 999) & 0x7fffffff
    result = []
    i = 0
    while i < len(data):
        state = _lcg_next(state)
        key_len = min((state % 14) + 5, len(data) - i)
        if key_len <= 0:
            break
        key = data[i:i + key_len]
        i += key_len
        
        state = _lcg_next(state)
        val_len = min((state % 56) + 15, len(data) - i)
        value = data[i:i + val_len] if val_len > 0 else ""
        i += val_len
        
        if result:
            result.append(f"&{key}={value}")
        else:
            result.append(f"{key}={value}")
    
    return URL_PREFIX + ''.join(result)


def _xor_bytes(data: bytes, key: bytes) -> bytes:
    """XOR encryption"""
    return bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])


def _lcg_shuffle(data: bytes, seed: int) -> tuple:
    """
    Fisher-Yates shuffle menggunakan LCG yang bisa direplikasi.
    Returns: (shuffled_data, shuffle_map)
    """
    n = len(data)
    data_list = list(data)
    indices = list(range(n))
    
    state = seed & 0x7fffffff
    for i in range(n - 1, 0, -1):
        state = (state * 1103515245 + 12345) & 0x7fffffff
        j = state % (i + 1)
        indices[i], indices[j] = indices[j], indices[i]
    
    shuffled = [0] * n
    for i, idx in enumerate(indices):
        shuffled[idx] = data_list[i]
    
    return bytes(shuffled), indices


def obfuscate_shell_advanced(source_code: str, shell_type: str = 'bash', use_password: bool = False, password: str = None) -> str:
    """
    Obfuscate kode Shell Script dengan 5 layer protection.
    
    Layer 1: Zlib compression
    Layer 2: XOR encryption dengan random key
    Layer 3: Byte shuffling algorithm (Fisher-Yates dengan LCG)
    Layer 4: Chunk-based encoding + CRC32
    Layer 5: Integrity verification (SHA256)
    
    Returns: String Shell Script yang bisa dijalankan
    """
    
    master_seed = secrets.randbelow(900000) + 100000
    xor_key = secrets.token_bytes(32)
    shuffle_seed = secrets.randbelow(900000) + 100000
    
    source_bytes = source_code.encode('utf-8')
    compressed = zlib.compress(source_bytes, 9)
    
    xored = _xor_bytes(compressed, xor_key)
    
    shuffled_data, _ = _lcg_shuffle(xored, shuffle_seed)
    
    chunk_seed = secrets.randbelow(900000) + 100000
    chunks = []
    i = 0
    state = chunk_seed & 0x7fffffff
    while i < len(shuffled_data):
        state = (state * 1103515245 + 12345) & 0x7fffffff
        chunk_size = (state % 49) + 16
        chunk = shuffled_data[i:i + chunk_size]
        chunk_len = struct.pack('>H', len(chunk))
        checksum = struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)
        chunks.append(chunk_len + checksum + chunk)
        i += chunk_size
    
    chunked_data = struct.pack('>I', len(chunks)) + struct.pack('>I', chunk_seed) + b''.join(chunks)
    
    integrity = hashlib.sha256(chunked_data).digest()[:16]
    
    magic = b'SHX2'
    version = struct.pack('>H', 2)
    timestamp = struct.pack('>Q', int(__import__('time').time()))
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
        decoder = _generate_decoder_with_password(shell_type)
    else:
        decoder = _generate_decoder_no_password(shell_type)
    
    return decoder.replace('__URL_DATA__', url_data)


def _generate_decoder_no_password(shell_type: str = 'bash') -> str:
    """Generate Shell decoder tanpa password"""
    shebang = f"#!/usr/bin/env {shell_type}" if shell_type != 'sh' else "#!/bin/sh"
    
    return f'''{shebang}
# Protected by Advanced Shell Obfuscator v2.0
_D="__URL_DATA__"
_decode() {{
python3 -c "
import sys,base64,zlib,hashlib,struct

def lcg(s):
    return (s*1103515245+12345)&0x7fffffff

def xor_d(d,k):
    return bytes([d[i]^k[i%len(k)]for i in range(len(d))])

def unshuffle(d,seed):
    n=len(d)
    idx=list(range(n))
    st=seed&0x7fffffff
    for i in range(n-1,0,-1):
        st=lcg(st)
        j=st%(i+1)
        idx[i],idx[j]=idx[j],idx[i]
    r=bytearray(n)
    for i in range(n):
        r[i]=d[idx[i]]
    return bytes(r)

def parse_url(u):
    u=u.split('?',1)[1]if'?'in u else u
    u=u.replace('=','').replace('&','').replace('.','').replace('+','')
    r=[]
    for c in u:
        if c=='_':r.append('=')
        elif c=='%':r.append('+')
        elif c=='-':r.append('/')
        else:r.append(c)
    return base64.b64decode(''.join(r))

d=parse_url('$_D')
if d[0]!=0:sys.exit(1)
d=d[1:]
if d[:4]!=b'SHX2':sys.exit(1)
v=struct.unpack('>H',d[4:6])[0]
if v!=2:sys.exit(1)
ih=d[14:30]
ss=struct.unpack('>I',d[30:34])[0]
kl=struct.unpack('>H',d[34:36])[0]
xk=d[36:36+kl]
dl=struct.unpack('>I',d[36+kl:40+kl])[0]
pd=d[40+kl:40+kl+dl]
if hashlib.sha256(pd).digest()[:16]!=ih:sys.exit(1)
nc=struct.unpack('>I',pd[:4])[0]
cs=struct.unpack('>I',pd[4:8])[0]
cks=[]
i=8
for _ in range(nc):
    cl=struct.unpack('>H',pd[i:i+2])[0]
    ck=struct.unpack('>I',pd[i+2:i+6])[0]
    ch=pd[i+6:i+6+cl]
    if zlib.crc32(ch)&0xffffffff!=ck:sys.exit(1)
    cks.append(ch)
    i+=6+cl
sf=b''.join(cks)
us=unshuffle(sf,ss)
xd=xor_d(us,xk)
dc=zlib.decompress(xd)
print(dc.decode('utf-8'))
"
}}
_C=$(_decode)
if [ -z "$_C" ]; then
    echo "ERROR: Decode failed" >&2
    exit 1
fi
_T=$(mktemp)
echo "$_C" > "$_T"
chmod +x "$_T"
{shebang.replace('#!', '')} "$_T" "$@"
_R=$?
rm -f "$_T"
exit $_R
'''


def _generate_decoder_with_password(shell_type: str = 'bash') -> str:
    """Generate Shell decoder dengan password"""
    shebang = f"#!/usr/bin/env {shell_type}" if shell_type != 'sh' else "#!/bin/sh"
    
    return f'''{shebang}
# Protected by Advanced Shell Obfuscator v2.0 (Password Protected)
_D="__URL_DATA__"
_decode() {{
python3 -c "
import sys,base64,zlib,hashlib,struct,getpass
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
except:
    print('ERROR: pip install pycryptodome',file=sys.stderr)
    sys.exit(1)

def lcg(s):
    return (s*1103515245+12345)&0x7fffffff

def xor_d(d,k):
    return bytes([d[i]^k[i%len(k)]for i in range(len(d))])

def unshuffle(d,seed):
    n=len(d)
    idx=list(range(n))
    st=seed&0x7fffffff
    for i in range(n-1,0,-1):
        st=lcg(st)
        j=st%(i+1)
        idx[i],idx[j]=idx[j],idx[i]
    r=bytearray(n)
    for i in range(n):
        r[i]=d[idx[i]]
    return bytes(r)

def parse_url(u):
    u=u.split('?',1)[1]if'?'in u else u
    u=u.replace('=','').replace('&','').replace('.','').replace('+','')
    r=[]
    for c in u:
        if c=='_':r.append('=')
        elif c=='%':r.append('+')
        elif c=='-':r.append('/')
        else:r.append(c)
    return base64.b64decode(''.join(r))

d=parse_url('$_D')
if d[0]!=1:sys.exit(1)
sl,iv,ed=d[1:17],d[17:33],d[33:]
pw=getpass.getpass('Masukkan kata rahasia: ')
k=hashlib.pbkdf2_hmac('sha256',pw.encode(),sl,50000,32)
try:
    ci=AES.new(k,AES.MODE_CBC,iv)
    d=unpad(ci.decrypt(ed),AES.block_size)
except:
    print('ERROR: Kata rahasia salah!',file=sys.stderr)
    sys.exit(1)
if d[:4]!=b'SHX2':sys.exit(1)
v=struct.unpack('>H',d[4:6])[0]
if v!=2:sys.exit(1)
ih=d[14:30]
ss=struct.unpack('>I',d[30:34])[0]
kl=struct.unpack('>H',d[34:36])[0]
xk=d[36:36+kl]
dl=struct.unpack('>I',d[36+kl:40+kl])[0]
pd=d[40+kl:40+kl+dl]
if hashlib.sha256(pd).digest()[:16]!=ih:sys.exit(1)
nc=struct.unpack('>I',pd[:4])[0]
cs=struct.unpack('>I',pd[4:8])[0]
cks=[]
i=8
for _ in range(nc):
    cl=struct.unpack('>H',pd[i:i+2])[0]
    ck=struct.unpack('>I',pd[i+2:i+6])[0]
    ch=pd[i+6:i+6+cl]
    if zlib.crc32(ch)&0xffffffff!=ck:sys.exit(1)
    cks.append(ch)
    i+=6+cl
sf=b''.join(cks)
us=unshuffle(sf,ss)
xd=xor_d(us,xk)
dc=zlib.decompress(xd)
print(dc.decode('utf-8'))
"
}}
_C=$(_decode)
if [ -z "$_C" ]; then
    echo "ERROR: Decode failed" >&2
    exit 1
fi
_T=$(mktemp)
echo "$_C" > "$_T"
chmod +x "$_T"
{shebang.replace('#!', '')} "$_T" "$@"
_R=$?
rm -f "$_T"
exit $_R
'''


def detect_shell_type(file_path: str) -> str:
    """Detect shell type from file extension or shebang"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in SHELL_EXTENSIONS:
        return SHELL_EXTENSIONS[ext]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line.startswith('#!'):
                for shell in ['bash', 'zsh', 'fish', 'ksh', 'csh', 'tcsh', 'dash']:
                    if shell in first_line:
                        return shell
    except:
        pass
    
    return 'bash'


def obfuscate_file(input_path: str, output_path: str, use_password: bool = False, password: str = None) -> bool:
    """Obfuscate file Shell Script"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        shell_type = detect_shell_type(input_path)
        result = obfuscate_shell_advanced(source, shell_type, use_password, password)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        
        os.chmod(output_path, 0o755)
        
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 70)
    print("   ADVANCED SHELL SCRIPT OBFUSCATOR v2.0")
    print("   Multi-layer Protection System (5 Layers)")
    print("=" * 70)
    print()
    print("Support shell:")
    print("  sh, bash, dash, zsh, fish, ksh, csh, tcsh")
    print()
    print("Fitur keamanan:")
    print("  [1] Zlib compression")
    print("  [2] XOR encryption dengan random key 32 byte")
    print("  [3] Byte shuffling algorithm")
    print("  [4] Chunk-based encoding + CRC32")
    print("  [5] Integrity verification (SHA256)")
    print("  [+] Password protection (AES-256) - opsional")
    print("  [+] Output format: URL WhatsApp")
    print("  [+] Support semua jenis argumen")
    print()
    
    if len(sys.argv) < 2:
        print("Penggunaan:")
        print("  python Shell_obfuscator.py <file.sh> [output.sh]")
        print()
        print("Contoh:")
        print("  python Shell_obfuscator.py script.sh")
        print("  python Shell_obfuscator.py script.sh protected.sh")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"ERROR: File tidak ditemukan: {input_file}")
        sys.exit(1)
    
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        base_name = os.path.splitext(input_file)[0]
        ext = os.path.splitext(input_file)[1] or '.sh'
        output_file = f"{base_name}_protected{ext}"
    
    shell_type = detect_shell_type(input_file)
    
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print(f"Shell:  {shell_type}")
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
        print("=" * 70)
        print("SUKSES!")
        print(f"File terproteksi: {output_file}")
        print(f"Ukuran file: {file_size:,} bytes")
        print()
        print("Cara menjalankan:")
        print(f"  {shell_type} {output_file}")
        print(f"  atau: ./{output_file}")
        print()
        print("Support argumen:")
        print(f"  {shell_type} {output_file} arg1 arg2 \"string dengan spasi\" --flag")
        print("=" * 70)
    else:
        print("GAGAL!")
        sys.exit(1)


if __name__ == "__main__":
    main()

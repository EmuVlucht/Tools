#!/usr/bin/env python3
"""
ADVANCED JAVASCRIPT/NODE.JS OBFUSCATOR v1.0
============================================
Obfuscator untuk JavaScript dengan multi-layer protection.

Fitur:
- Multi-layer encoding (3 lapis)
- Anti-debugging protection
- Integrity verification
- Format output: URL WhatsApp
- Bisa dijalankan langsung dengan node

Karakter output: a-z A-Z 0-9 _ = - . & % +
"""

import sys
import os
import base64
import zlib
import hashlib
import struct
import secrets


URL_PREFIX = "https://chat.whatsapp.com/LZU6fs32eGnHtWaI3IIg4Y?"


def _lcg_next(state):
    """Linear Congruential Generator step"""
    return (state * 1103515245 + 12345) & 0x7fffffff


def _bytes_to_url_safe(data: bytes) -> str:
    """Convert bytes ke format URL-safe"""
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


def _add_noise(data: str, seed: int) -> str:
    """Tambahkan noise chars . dan + secara deterministik"""
    result = list(data)
    noise = '.+'
    count = max(1, len(data) // 15)
    
    state = seed & 0x7fffffff
    for _ in range(count):
        state = _lcg_next(state)
        pos = state % (len(result) + 1)
        state = _lcg_next(state)
        char = noise[state % 2]
        result.insert(pos, char)
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


def obfuscate_js(source_code: str) -> str:
    """
    Obfuscate kode JavaScript dengan multi-layer protection.
    
    Returns: String JavaScript yang bisa dijalankan dengan node
    """
    
    master_seed = secrets.randbelow(900000) + 100000
    xor_key = secrets.token_bytes(32)
    
    source_bytes = source_code.encode('utf-8')
    compressed = zlib.compress(source_bytes, 9)
    
    xored = _xor_bytes(compressed, xor_key)
    
    integrity = hashlib.sha256(xored).digest()[:16]
    
    magic = b'JSX1'
    version = struct.pack('>H', 1)
    xor_key_len = struct.pack('>H', len(xor_key))
    data_len = struct.pack('>I', len(xored))
    
    final_data = (magic + version + integrity + 
                  xor_key_len + xor_key + 
                  data_len + xored)
    
    encoded = _bytes_to_url_safe(final_data)
    url_data = _format_url_params(encoded, master_seed)
    
    decoder = _generate_decoder()
    
    return decoder.replace('__URL_DATA__', url_data)


def _generate_decoder() -> str:
    """Generate JavaScript decoder"""
    return '''// Protected by Advanced JS Obfuscator v1.0
const _U="__URL_DATA__";
const _z=require("zlib");
const _p=u=>{u=u.includes("?")?u.split("?")[1]:u;u=u.replace(/[=&.+]/g,"");let r="";for(let c of u){if(c==="_")r+="=";else if(c==="%")r+="+";else if(c==="-")r+="/";else r+=c;}return Buffer.from(r,"base64");};
const _x=(d,k)=>Buffer.from(d.map((b,i)=>b^k[i%k.length]));
const _v=()=>{try{const e=new Error();if(e.stack&&(e.stack.includes("debugger")||e.stack.includes("inspector")))return true;}catch(x){}try{const s=Date.now();debugger;if(Date.now()-s>100)return true;}catch(x){}return false;};
const _d=()=>{if(_v())process.exit(1);const d=_p(_U);let o=0;if(d.slice(o,o+4).toString()!=="JSX1")process.exit(1);o+=4;const v=d.readUInt16BE(o);o+=2;if(v!==1)process.exit(1);const ih=d.slice(o,o+16);o+=16;const kl=d.readUInt16BE(o);o+=2;const xk=d.slice(o,o+kl);o+=kl;const dl=d.readUInt32BE(o);o+=4;const xd=d.slice(o,o+dl);const crypto=require("crypto");if(!crypto.createHash("sha256").update(xd).digest().slice(0,16).equals(ih))process.exit(1);const ux=_x(xd,xk);const dc=_z.inflateSync(ux).toString("utf8");return dc;};
try{const _c=_d();const _m=require("module");const _f=new _m(module.filename,module.parent);_f._compile(_c,module.filename);_f.loaded=true;if(_f.exports&&Object.keys(_f.exports).length)module.exports=_f.exports;}catch(e){console.error(e.message);process.exit(1);}
'''


def obfuscate_file(input_path: str, output_path: str) -> bool:
    """Obfuscate file JavaScript"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        result = obfuscate_js(source)
        
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
    print("   ADVANCED JAVASCRIPT/NODE.JS OBFUSCATOR v1.0")
    print("   Multi-layer Protection System")
    print("=" * 65)
    print()
    print("Fitur keamanan:")
    print("  [1] Zlib compression")
    print("  [2] XOR encryption dengan random key")
    print("  [3] Integrity verification (SHA256)")
    print("  [+] Anti-debugging protection")
    print("  [+] Output format: URL WhatsApp")
    print()
    
    if len(sys.argv) < 2:
        print("Penggunaan:")
        print("  python JS_obfuscator.py <file.js> [output.js]")
        print()
        print("Contoh:")
        print("  python JS_obfuscator.py script.js")
        print("  python JS_obfuscator.py script.js protected.js")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"ERROR: File tidak ditemukan: {input_file}")
        sys.exit(1)
    
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_protected.js"
    
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print()
    print("Memproses...")
    print()
    
    if obfuscate_file(input_file, output_file):
        file_size = os.path.getsize(output_file)
        print("=" * 65)
        print("SUKSES!")
        print(f"File terproteksi: {output_file}")
        print(f"Ukuran file: {file_size:,} bytes")
        print()
        print("Cara menjalankan:")
        print(f"  node {output_file}")
        print("=" * 65)
    else:
        print("GAGAL!")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
ADVANCED JAVASCRIPT/NODE.JS OBFUSCATOR v2.0
============================================
Obfuscator tingkat tinggi untuk JavaScript dengan 5 layer protection.

Fitur:
- Multi-layer encoding (5 lapis)
- Zlib compression
- XOR encryption dengan random key
- Byte shuffling algorithm
- Chunk-based encoding + CRC32
- Integrity verification (SHA256)
- Anti-debugging protection (kuat)
- Password protection (AES-256) - opsional
- Variable name obfuscation pada decoder
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
import random

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


URL_PREFIX = "https://chat.whatsapp.com/LZU6fs32eGnHtWaI3IIg4Y?"

PBKDF2_ITERATIONS = 50000


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
    Fisher-Yates shuffle menggunakan LCG yang bisa direplikasi di JavaScript.
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


def obfuscate_js_advanced(source_code: str, use_password: bool = False, password: str = None) -> str:
    """
    Obfuscate kode JavaScript dengan 5 layer protection.
    
    Layer 1: Zlib compression
    Layer 2: XOR encryption dengan random key
    Layer 3: Byte shuffling algorithm (Fisher-Yates dengan LCG)
    Layer 4: Chunk-based encoding + CRC32
    Layer 5: Integrity verification (SHA256)
    
    Returns: String JavaScript yang bisa dijalankan dengan node
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
    
    magic = b'JSX2'
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
        decoder = _generate_decoder_with_password()
    else:
        decoder = _generate_decoder_no_password()
    
    return decoder.replace('__URL_DATA__', url_data)


def _generate_decoder_no_password() -> str:
    """Generate JavaScript decoder tanpa password dengan variable obfuscation"""
    return '''// Protected by Advanced JS Obfuscator v2.0
(function(){
const _0x={
a:"__URL_DATA__",
b:require("zlib"),
c:require("crypto")
};
const _1=function(_2){
_2=_2.indexOf("?")>-1?_2.split("?")[1]:_2;
_2=_2.replace(/[=&.+]/g,"");
let _3="";
for(let _4=0;_4<_2.length;_4++){
const _5=_2[_4];
if(_5==="_")_3+="=";
else if(_5==="%")_3+="+";
else if(_5==="-")_3+="/";
else _3+=_5;
}
return Buffer.from(_3,"base64");
};
const _6=function(_7,_8){
const _9=Buffer.alloc(_7.length);
for(let _a=0;_a<_7.length;_a++){
_9[_a]=_7[_a]^_8[_a%_8.length];
}
return _9;
};
const _b=function(){
try{
const _c=new Error();
if(_c.stack){
const _d=_c.stack.toLowerCase();
if(_d.includes("debugger")||_d.includes("inspector")||_d.includes("--inspect"))return true;
}
}catch(_e){}
try{
const _f=Date.now();
debugger;
if(Date.now()-_f>100)return true;
}catch(_g){}
try{
const _h=process.execArgv.join("");
if(_h.includes("--inspect")||_h.includes("--debug"))return true;
}catch(_i){}
try{
if(typeof v8debug==="object")return true;
}catch(_j){}
setInterval(function(){
const _k=Date.now();
debugger;
if(Date.now()-_k>100)process.exit(1);
},1000);
return false;
};
const _l=function(_m){
return Number((BigInt(_m)*1103515245n+12345n)&0x7fffffffn);
};
const _crc=function(_buf){
let _c=0xffffffff;
for(let _i=0;_i<_buf.length;_i++){
_c^=_buf[_i];
for(let _j=0;_j<8;_j++){
_c=(_c>>>1)^(0xedb88320&-(_c&1));
}
}
return(~_c)>>>0;
};
const _us=function(_d,_seed){
const _n=_d.length;
const _idx=[];
for(let _i=0;_i<_n;_i++)_idx.push(_i);
let _st=_seed&0x7fffffff;
for(let _i=_n-1;_i>0;_i--){
_st=_l(_st);
const _j=_st%(_i+1);
[_idx[_i],_idx[_j]]=[_idx[_j],_idx[_i]];
}
const _r=Buffer.alloc(_n);
for(let _i=0;_i<_n;_i++)_r[_i]=_d[_idx[_i]];
return _r;
};
const _o=function(){
if(_b())process.exit(1);
const _p=_1(_0x.a);
let _q=0;
if(_p[_q]!==0)process.exit(1);
_q++;
if(_p.slice(_q,_q+4).toString()!=="JSX2")process.exit(1);
_q+=4;
const _r=_p.readUInt16BE(_q);_q+=2;
if(_r!==2)process.exit(1);
_q+=8;
const _s=_p.slice(_q,_q+16);_q+=16;
const _t=_p.readUInt32BE(_q);_q+=4;
const _u=_p.readUInt16BE(_q);_q+=2;
const _v=_p.slice(_q,_q+_u);_q+=_u;
const _w=_p.readUInt32BE(_q);_q+=4;
const _x=_p.slice(_q,_q+_w);
const _y=_0x.c.createHash("sha256").update(_x).digest().slice(0,16);
if(!_y.equals(_s))process.exit(1);
const _z=_x.readUInt32BE(0);
const _10=_x.readUInt32BE(4);
let _11=[];
let _12=8;
for(let _13=0;_13<_z;_13++){
const _14=_x.readUInt16BE(_12);_12+=2;
const _15=_x.readUInt32BE(_12);_12+=4;
const _16=_x.slice(_12,_12+_14);_12+=_14;
if(_crc(_16)!==_15)process.exit(1);
_11.push(_16);
}
const _1c=Buffer.concat(_11);
const _23=_us(_1c,_t);
const _25=_6(_23,_v);
const _26=_0x.b.inflateSync(_25).toString("utf8");
return _26;
};
try{
const _27=_o();
const _28=require("module");
const _29=new _28(module.filename,module.parent);
_29._compile(_27,module.filename);
_29.loaded=true;
if(_29.exports&&Object.keys(_29.exports).length>0){
module.exports=_29.exports;
}
}catch(_2a){
console.error("Runtime Error:",_2a.message);
process.exit(1);
}
})();
'''


def _generate_decoder_with_password() -> str:
    """Generate JavaScript decoder dengan password"""
    return '''// Protected by Advanced JS Obfuscator v2.0 (Password Protected)
(function(){
const _0x={
a:"__URL_DATA__",
b:require("zlib"),
c:require("crypto")
};
const _1=function(_2){
_2=_2.indexOf("?")>-1?_2.split("?")[1]:_2;
_2=_2.replace(/[=&.+]/g,"");
let _3="";
for(let _4=0;_4<_2.length;_4++){
const _5=_2[_4];
if(_5==="_")_3+="=";
else if(_5==="%")_3+="+";
else if(_5==="-")_3+="/";
else _3+=_5;
}
return Buffer.from(_3,"base64");
};
const _6=function(_7,_8){
const _9=Buffer.alloc(_7.length);
for(let _a=0;_a<_7.length;_a++){
_9[_a]=_7[_a]^_8[_a%_8.length];
}
return _9;
};
const _b=function(){
try{
const _c=new Error();
if(_c.stack){
const _d=_c.stack.toLowerCase();
if(_d.includes("debugger")||_d.includes("inspector")||_d.includes("--inspect"))return true;
}
}catch(_e){}
try{
const _f=Date.now();
debugger;
if(Date.now()-_f>100)return true;
}catch(_g){}
try{
const _h=process.execArgv.join("");
if(_h.includes("--inspect")||_h.includes("--debug"))return true;
}catch(_i){}
try{
if(typeof v8debug==="object")return true;
}catch(_j){}
setInterval(function(){
const _k=Date.now();
debugger;
if(Date.now()-_k>100)process.exit(1);
},1000);
return false;
};
const _l=function(_m){
return Number((BigInt(_m)*1103515245n+12345n)&0x7fffffffn);
};
const _crc=function(_buf){
let _c=0xffffffff;
for(let _i=0;_i<_buf.length;_i++){
_c^=_buf[_i];
for(let _j=0;_j<8;_j++){
_c=(_c>>>1)^(0xedb88320&-(_c&1));
}
}
return(~_c)>>>0;
};
const _us=function(_d,_seed){
const _n=_d.length;
const _idx=[];
for(let _i=0;_i<_n;_i++)_idx.push(_i);
let _st=_seed&0x7fffffff;
for(let _i=_n-1;_i>0;_i--){
_st=_l(_st);
const _j=_st%(_i+1);
[_idx[_i],_idx[_j]]=[_idx[_j],_idx[_i]];
}
const _r=Buffer.alloc(_n);
for(let _i=0;_i<_n;_i++)_r[_i]=_d[_idx[_i]];
return _r;
};
const _gp=function(){
return new Promise(function(_r,_j){
const _rl=require("readline");
const _i=_rl.createInterface({input:process.stdin,output:process.stdout});
process.stdout.write("Masukkan kata rahasia: ");
_i.question("",function(_a){
_i.close();
process.stdout.write("\\n");
_r(_a);
});
});
};
const _dp=function(_d,_pw){
const _sl=_d.slice(1,17);
const _iv=_d.slice(17,33);
const _ed=_d.slice(33);
const _k=_0x.c.pbkdf2Sync(_pw,_sl,50000,32,"sha256");
try{
const _dc=_0x.c.createDecipheriv("aes-256-cbc",_k,_iv);
let _pt=_dc.update(_ed);
_pt=Buffer.concat([_pt,_dc.final()]);
return _pt;
}catch(_e){
console.error("ERROR: Kata rahasia salah!");
process.exit(1);
}
};
const _o=async function(){
if(_b())process.exit(1);
let _p=_1(_0x.a);
let _q=0;
if(_p[_q]!==1)process.exit(1);
const _pw=await _gp();
_p=_dp(_p,_pw);
_q=0;
if(_p.slice(_q,_q+4).toString()!=="JSX2")process.exit(1);
_q+=4;
const _r=_p.readUInt16BE(_q);_q+=2;
if(_r!==2)process.exit(1);
_q+=8;
const _s=_p.slice(_q,_q+16);_q+=16;
const _t=_p.readUInt32BE(_q);_q+=4;
const _u=_p.readUInt16BE(_q);_q+=2;
const _v=_p.slice(_q,_q+_u);_q+=_u;
const _w=_p.readUInt32BE(_q);_q+=4;
const _x=_p.slice(_q,_q+_w);
const _y=_0x.c.createHash("sha256").update(_x).digest().slice(0,16);
if(!_y.equals(_s))process.exit(1);
const _z=_x.readUInt32BE(0);
const _10=_x.readUInt32BE(4);
let _11=[];
let _12=8;
for(let _13=0;_13<_z;_13++){
const _14=_x.readUInt16BE(_12);_12+=2;
const _15=_x.readUInt32BE(_12);_12+=4;
const _16=_x.slice(_12,_12+_14);_12+=_14;
if(_crc(_16)!==_15)process.exit(1);
_11.push(_16);
}
const _1c=Buffer.concat(_11);
const _23=_us(_1c,_t);
const _25=_6(_23,_v);
const _26=_0x.b.inflateSync(_25).toString("utf8");
return _26;
};
(async function(){
try{
const _27=await _o();
const _28=require("module");
const _29=new _28(module.filename,module.parent);
_29._compile(_27,module.filename);
_29.loaded=true;
if(_29.exports&&Object.keys(_29.exports).length>0){
module.exports=_29.exports;
}
}catch(_2a){
console.error("Runtime Error:",_2a.message);
process.exit(1);
}
})();
})();
'''


def obfuscate_file(input_path: str, output_path: str, use_password: bool = False, password: str = None) -> bool:
    """Obfuscate file JavaScript"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        result = obfuscate_js_advanced(source, use_password, password)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 70)
    print("   ADVANCED JAVASCRIPT/NODE.JS OBFUSCATOR v2.0")
    print("   Multi-layer Protection System (5 Layers)")
    print("=" * 70)
    print()
    print("Fitur keamanan:")
    print("  [1] Zlib compression")
    print("  [2] XOR encryption dengan random key 32 byte")
    print("  [3] Byte shuffling algorithm")
    print("  [4] Chunk-based encoding + CRC32")
    print("  [5] Integrity verification (SHA256)")
    print("  [+] Anti-debugging protection (kuat)")
    print("  [+] Variable name obfuscation pada decoder")
    print("  [+] Password protection (AES-256) - opsional")
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
        print(f"  node {output_file}")
        print()
        print("Perkiraan tingkat kesulitan reverse engineering: ~25-35% dari 123%")
        print("=" * 70)
    else:
        print("GAGAL!")
        sys.exit(1)


if __name__ == "__main__":
    main()

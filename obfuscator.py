#!/usr/bin/env python3
"""
FILES OBFUSCATOR TOOLS v2.0
============================
Obfuscator all-in-one untuk Python, JavaScript, dan Shell Script.

Fitur:
- Multi-layer encoding (5 lapis)
- Zlib compression
- XOR encryption dengan random key
- Byte shuffling algorithm
- Chunk-based encoding + CRC32
- Integrity verification (SHA256)
- Password protection (AES-256) - opsional
- Format output: URL WhatsApp
- Support semua jenis argumen

Support:
- Python (.py)
- JavaScript/Node.js (.js)
- Shell Script (.sh, .bash, .dash, .zsh, .fish, .ksh, .csh, .tcsh)
"""

import sys
import os
import marshal
import base64
import zlib
import hashlib
import struct
import secrets
import random
import time

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


URL_PREFIX = "https://chat.whatsapp.com/DEWH54Hdqk281Vl2hp0Hdy?"
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
    return (state * 1103515245 + 12345) & 0x7fffffff


def _bytes_to_url_safe(data: bytes) -> str:
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
    return bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])


def _lcg_shuffle(data: bytes, seed: int) -> tuple:
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


def _python_add_noise(data: str, seed: int) -> str:
    rng = random.Random(seed)
    result = list(data)
    noise = '.+'
    count = max(1, len(data) // 12)
    for _ in range(count):
        pos = rng.randint(0, len(result))
        result.insert(pos, noise[rng.randint(0, 1)])
    return ''.join(result)


def _python_format_url_params(data: str, seed: int) -> str:
    rng = random.Random(seed)
    data = _python_add_noise(data, seed + 1)
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


def obfuscate_python(source_code: str, use_password: bool = False, password: str = None) -> str:
    master_seed = secrets.randbelow(900000) + 100000
    xor_key = secrets.token_bytes(32)
    shuffle_seed = secrets.randbelow(900000) + 100000
    
    code_obj = compile(source_code, '<protected>', 'exec')
    marshaled = marshal.dumps(code_obj)
    compressed = zlib.compress(marshaled, 9)
    
    xored = _xor_bytes(compressed, xor_key)
    
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
    url_data = _python_format_url_params(encoded, master_seed)
    
    if use_password and password:
        decoder = _python_decoder_with_password()
    else:
        decoder = _python_decoder_no_password()
    
    return decoder.replace('__URL_DATA__', url_data)


def _python_decoder_no_password() -> str:
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


def _python_decoder_with_password() -> str:
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


def obfuscate_javascript(source_code: str, use_password: bool = False, password: str = None) -> str:
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
        decoder = _js_decoder_with_password()
    else:
        decoder = _js_decoder_no_password()
    
    return decoder.replace('__URL_DATA__', url_data)


def _js_decoder_no_password() -> str:
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


def _js_decoder_with_password() -> str:
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


def detect_shell_type(file_path: str) -> str:
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


def obfuscate_shell(source_code: str, shell_type: str = 'bash', use_password: bool = False, password: str = None) -> str:
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
        decoder = _shell_decoder_with_password(shell_type)
    else:
        decoder = _shell_decoder_no_password(shell_type)
    
    return decoder.replace('__URL_DATA__', url_data)


def _shell_decoder_no_password(shell_type: str = 'bash') -> str:
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


def _shell_decoder_with_password(shell_type: str = 'bash') -> str:
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


def obfuscate_file_python(input_path: str, output_path: str, use_password: bool = False, password: str = None) -> bool:
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            source = f.read()
        result = obfuscate_python(source, use_password, password)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def obfuscate_file_javascript(input_path: str, output_path: str, use_password: bool = False, password: str = None) -> bool:
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            source = f.read()
        result = obfuscate_javascript(source, use_password, password)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def obfuscate_file_shell(input_path: str, output_path: str, use_password: bool = False, password: str = None) -> bool:
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            source = f.read()
        shell_type = detect_shell_type(input_path)
        result = obfuscate_shell(source, shell_type, use_password, password)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        os.chmod(output_path, 0o755)
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_banner():
    print()
    print("\u2554" + "\u2550" * 52 + "\u2557")
    print("\u2551" + "       FILES OBFUSCATOR TOOLS v2.0".center(52) + "\u2551")
    print("\u2551" + "          (FIXED VERSION)".center(52) + "\u2551")
    print("\u255A" + "\u2550" * 52 + "\u255D")
    print()


def print_menu():
    print("Pilih operasi yang ingin dijalankan:")
    print("  1. Obfuscator for Python - Menyamarkan file python atau python3")
    print("  2. Obfuscator for JavaScript - Menyamarkan file Nodejs atau JavaScript")
    print("  3. Obfuscator for Script Shell - Menyamarkan file sh, bash, dash, zsh, fish, ksh, csh, tcsh")
    print("  4. Crypto Tool - Enkripsi/Dekripsi file dengan AES-256-GCM")
    print("  5. Generate URL - Membuat URL dengan parameter acak terstruktur")
    print()


def get_password_option():
    use_password = False
    password = None
    if HAS_CRYPTO:
        choice = input("Gunakan kata rahasia (AES-256)? (y/n): ").lower().strip()
        if choice == 'y':
            from getpass import getpass
            password = getpass("Masukkan kata rahasia: ")
            if len(password) < 6:
                print("ERROR: Kata rahasia minimal 6 karakter!")
                return None, None, False
            confirm = getpass("Konfirmasi kata rahasia: ")
            if password != confirm:
                print("ERROR: Kata rahasia tidak cocok!")
                return None, None, False
            use_password = True
    else:
        print("INFO: pycryptodome tidak terinstall, password protection dilewati.")
        print("      Install dengan: pip install pycryptodome")
    return use_password, password, True


def process_python():
    print()
    print("=" * 55)
    print("   PYTHON OBFUSCATOR")
    print("=" * 55)
    print()
    
    input_file = input("Masukkan path file Python (.py): ").strip()
    if not input_file:
        print("ERROR: Path file tidak boleh kosong!")
        return
    
    if not os.path.exists(input_file):
        print(f"ERROR: File tidak ditemukan: {input_file}")
        return
    
    output_file = input("Masukkan path output (kosongkan untuk default): ").strip()
    if not output_file:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_protected.py"
    
    print()
    use_password, password, ok = get_password_option()
    if not ok:
        return
    
    print()
    print("Memproses dengan 5 layer protection...")
    print()
    
    if obfuscate_file_python(input_file, output_file, use_password, password):
        file_size = os.path.getsize(output_file)
        print("=" * 55)
        print("SUKSES!")
        print(f"File terproteksi: {output_file}")
        print(f"Ukuran file: {file_size:,} bytes")
        print()
        print("Cara menjalankan:")
        print(f"  python3 {output_file}")
        print(f"  python3 {output_file} arg1 arg2 \"string spasi\" --flag")
        print("=" * 55)
    else:
        print("GAGAL!")


def process_javascript():
    print()
    print("=" * 55)
    print("   JAVASCRIPT/NODE.JS OBFUSCATOR")
    print("=" * 55)
    print()
    
    input_file = input("Masukkan path file JavaScript (.js): ").strip()
    if not input_file:
        print("ERROR: Path file tidak boleh kosong!")
        return
    
    if not os.path.exists(input_file):
        print(f"ERROR: File tidak ditemukan: {input_file}")
        return
    
    output_file = input("Masukkan path output (kosongkan untuk default): ").strip()
    if not output_file:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_protected.js"
    
    print()
    use_password, password, ok = get_password_option()
    if not ok:
        return
    
    print()
    print("Memproses dengan 5 layer protection...")
    print()
    
    if obfuscate_file_javascript(input_file, output_file, use_password, password):
        file_size = os.path.getsize(output_file)
        print("=" * 55)
        print("SUKSES!")
        print(f"File terproteksi: {output_file}")
        print(f"Ukuran file: {file_size:,} bytes")
        print()
        print("Cara menjalankan:")
        print(f"  node {output_file}")
        print(f"  node {output_file} arg1 arg2 \"string spasi\" --flag")
        print("=" * 55)
    else:
        print("GAGAL!")


def process_shell():
    print()
    print("=" * 55)
    print("   SHELL SCRIPT OBFUSCATOR")
    print("=" * 55)
    print()
    print("Support: sh, bash, dash, zsh, fish, ksh, csh, tcsh")
    print()
    
    input_file = input("Masukkan path file Shell Script: ").strip()
    if not input_file:
        print("ERROR: Path file tidak boleh kosong!")
        return
    
    if not os.path.exists(input_file):
        print(f"ERROR: File tidak ditemukan: {input_file}")
        return
    
    shell_type = detect_shell_type(input_file)
    print(f"Shell terdeteksi: {shell_type}")
    
    output_file = input("Masukkan path output (kosongkan untuk default): ").strip()
    if not output_file:
        base_name = os.path.splitext(input_file)[0]
        ext = os.path.splitext(input_file)[1] or '.sh'
        output_file = f"{base_name}_protected{ext}"
    
    print()
    use_password, password, ok = get_password_option()
    if not ok:
        return
    
    print()
    print("Memproses dengan 5 layer protection...")
    print()
    
    if obfuscate_file_shell(input_file, output_file, use_password, password):
        file_size = os.path.getsize(output_file)
        print("=" * 55)
        print("SUKSES!")
        print(f"File terproteksi: {output_file}")
        print(f"Ukuran file: {file_size:,} bytes")
        print()
        print("Cara menjalankan:")
        print(f"  {shell_type} {output_file}")
        print(f"  ./{output_file}")
        print(f"  {shell_type} {output_file} arg1 arg2 \"string spasi\" --flag")
        print("=" * 55)
    else:
        print("GAGAL!")


CRYPTO_SALT_SIZE = 32
CRYPTO_NONCE_SIZE = 12
CRYPTO_TAG_SIZE = 16
CRYPTO_KEY_SIZE = 32
CRYPTO_PBKDF2_ITERATIONS = 600000


def _crypto_derive_key(password: str, salt: bytes) -> bytes:
    key = hashlib.pbkdf2_hmac(
        'sha512',
        password.encode('utf-8'),
        salt,
        iterations=CRYPTO_PBKDF2_ITERATIONS,
        dklen=CRYPTO_KEY_SIZE
    )
    return key


def _crypto_add_extra_chars(data: str, seed: int) -> str:
    import random as rnd
    rng = rnd.Random(seed)
    result = list(data)
    extra_chars = '.+'
    num_extras = max(1, len(data) // 20)
    for _ in range(num_extras):
        pos = rng.randint(0, len(result))
        char = extra_chars[rng.randint(0, 1)]
        result.insert(pos, char)
    return ''.join(result)


def _crypto_format_as_url_params(data: str, seed: int) -> str:
    import random as rnd
    rng = rnd.Random(seed)
    data = _crypto_add_extra_chars(data, seed + 1)
    result = []
    i = 0
    data_len = len(data)
    while i < data_len:
        key_len = rng.randint(5, 20)
        key_len = min(key_len, data_len - i)
        if key_len <= 0:
            break
        key = data[i:i + key_len]
        i += key_len
        val_len = rng.randint(20, 80)
        val_len = min(val_len, data_len - i)
        value = data[i:i + val_len] if val_len > 0 else ""
        i += val_len
        if result:
            result.append(f"&{key}={value}")
        else:
            result.append(f"{key}={value}")
    return ''.join(result)


def _crypto_parse_url_params(url_data: str) -> str:
    url_prefix = "https://chat.whatsapp.com/DEWH54Hdqk281Vl2hp0Hdy?"
    if url_data.startswith(url_prefix):
        url_data = url_data[len(url_prefix):]
    result = url_data.replace('=', '').replace('&', '')
    result = result.replace('.', '').replace('+', '')
    return result


def encrypt_file(input_path: str, output_path: str, password: str) -> bool:
    import hmac as hmac_mod
    try:
        if not HAS_CRYPTO:
            print("ERROR: pycryptodome tidak terinstall!")
            print("Jalankan: pip install pycryptodome")
            return False
        with open(input_path, 'rb') as f:
            plaintext = f.read()
        salt = secrets.token_bytes(CRYPTO_SALT_SIZE)
        nonce = secrets.token_bytes(CRYPTO_NONCE_SIZE)
        key = _crypto_derive_key(password, salt)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        original_filename = os.path.basename(input_path).encode('utf-8')
        cipher.update(original_filename)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        filename_len = struct.pack('>H', len(original_filename))
        packed_data = salt + nonce + tag + filename_len + original_filename + ciphertext
        hmac_key = hashlib.sha256(key + b'hmac_verify').digest()
        data_hmac = hmac_mod.new(hmac_key, packed_data, hashlib.sha256).digest()
        final_data = data_hmac + packed_data
        encoded = _bytes_to_url_safe(final_data)
        format_seed = int.from_bytes(salt[:4], 'big')
        url_params = _crypto_format_as_url_params(encoded, format_seed)
        url_prefix = "https://chat.whatsapp.com/DEWH54Hdqk281Vl2hp0Hdy?"
        final_output = url_prefix + url_params
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_output)
        return True
    except Exception as e:
        print(f"ERROR saat enkripsi: {e}")
        import traceback
        traceback.print_exc()
        return False


def decrypt_file(input_path: str, output_dir: str, password: str) -> bool:
    import hmac as hmac_mod
    try:
        if not HAS_CRYPTO:
            print("ERROR: pycryptodome tidak terinstall!")
            print("Jalankan: pip install pycryptodome")
            return False
        with open(input_path, 'r', encoding='utf-8') as f:
            encrypted_data = f.read().strip()
        encoded = _crypto_parse_url_params(encrypted_data)
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
        packed_with_hmac = base64.b64decode(''.join(result))
        data_hmac = packed_with_hmac[:32]
        packed_data = packed_with_hmac[32:]
        salt = packed_data[:CRYPTO_SALT_SIZE]
        nonce = packed_data[CRYPTO_SALT_SIZE:CRYPTO_SALT_SIZE + CRYPTO_NONCE_SIZE]
        tag = packed_data[CRYPTO_SALT_SIZE + CRYPTO_NONCE_SIZE:CRYPTO_SALT_SIZE + CRYPTO_NONCE_SIZE + CRYPTO_TAG_SIZE]
        offset = CRYPTO_SALT_SIZE + CRYPTO_NONCE_SIZE + CRYPTO_TAG_SIZE
        filename_len = struct.unpack('>H', packed_data[offset:offset + 2])[0]
        offset += 2
        original_filename = packed_data[offset:offset + filename_len]
        offset += filename_len
        ciphertext = packed_data[offset:]
        key = _crypto_derive_key(password, salt)
        hmac_key = hashlib.sha256(key + b'hmac_verify').digest()
        expected_hmac = hmac_mod.new(hmac_key, packed_data, hashlib.sha256).digest()
        if not hmac_mod.compare_digest(data_hmac, expected_hmac):
            print("ERROR: Kata rahasia salah atau file rusak!")
            return False
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        cipher.update(original_filename)
        try:
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        except ValueError:
            print("ERROR: Kata rahasia salah atau file telah dimodifikasi!")
            return False
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


def process_crypto():
    print()
    print("=" * 60)
    print("   SECURE FILE ENCRYPTION/DECRYPTION TOOL")
    print("   AES-256-GCM + PBKDF2 Key Derivation")
    print("=" * 60)
    print()
    
    if not HAS_CRYPTO:
        print("ERROR: pycryptodome tidak terinstall!")
        print("Jalankan: pip install pycryptodome")
        return
    
    print("Pilih mode:")
    print("  1. Encrypt - Enkripsi file")
    print("  2. Decrypt - Dekripsi file")
    print()
    mode = input("Pilihan [1/2]: ").strip()
    
    if mode == '1':
        print()
        input_file = input("Masukkan path file yang akan dienkripsi: ").strip()
        if not input_file:
            print("ERROR: Path file tidak boleh kosong!")
            return
        if not os.path.exists(input_file):
            print(f"ERROR: File tidak ditemukan: {input_file}")
            return
        
        from getpass import getpass
        password = getpass("Masukkan kata rahasia (min 8 karakter): ")
        if len(password) < 8:
            print("ERROR: Kata rahasia minimal 8 karakter!")
            return
        password_confirm = getpass("Konfirmasi kata rahasia: ")
        if password != password_confirm:
            print("ERROR: Kata rahasia tidak cocok!")
            return
        
        output_file = input_file + ".encrypted"
        print()
        print("Mengenkripsi file... (ini mungkin memakan waktu)")
        
        if encrypt_file(input_file, output_file, password):
            file_size = os.path.getsize(output_file)
            print()
            print("=" * 60)
            print("SUKSES! File berhasil dienkripsi!")
            print(f"Output: {output_file}")
            print(f"Ukuran: {file_size:,} bytes")
            print("=" * 60)
        else:
            print("GAGAL! Enkripsi tidak berhasil.")
    
    elif mode == '2':
        print()
        input_file = input("Masukkan path file terenkripsi: ").strip()
        if not input_file:
            print("ERROR: Path file tidak boleh kosong!")
            return
        if not os.path.exists(input_file):
            print(f"ERROR: File tidak ditemukan: {input_file}")
            return
        
        from getpass import getpass
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
    else:
        print("ERROR: Pilihan tidak valid!")


def generate_random_string(length: int, charset: str) -> str:
    result = []
    for _ in range(length):
        result.append(charset[secrets.randbelow(len(charset))])
    return ''.join(result)


def generate_structured_params(target_length: int) -> str:
    chars_key = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
    chars_value = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_=-.%+"
    
    result = []
    current_length = 0
    
    while current_length < target_length:
        key_length = secrets.randbelow(46) + 5
        value_length = secrets.randbelow(100) + 20
        
        key = generate_random_string(key_length, chars_key)
        value = generate_random_string(value_length, chars_value)
        
        if not result:
            pair = f"{key}={value}"
        else:
            pair = f"&{key}={value}"
        
        pair_length = len(pair)
        if current_length + pair_length > target_length:
            remaining = target_length - current_length - 1
            if remaining > 5:
                key = generate_random_string(3, chars_key)
                value_len = remaining - 4
                if value_len > 0:
                    value = generate_random_string(value_len, chars_value)
                    result.append(f"&{key}={value}")
            break
        
        result.append(pair)
        current_length = sum(len(p) for p in result)
    
    return ''.join(result)


def process_generate_url():
    print()
    print("=" * 60)
    print("   GENERATOR URL DENGAN PARAMETER TERSTRUKTUR ACAK")
    print("=" * 60)
    print()
    
    base_url = "https://chat.whatsapp.com/DEWH54Hdqk281Vl2hp0Hdy"
    max_length = 123456
    
    length_input = input(f"Panjang parameter (default {max_length}): ").strip()
    if length_input:
        try:
            max_length = int(length_input)
        except ValueError:
            print("ERROR: Masukkan angka yang valid!")
            return
    
    print()
    print(f"Target panjang parameter: {max_length} karakter")
    print("Generating parameters...")
    print()
    
    random_params = generate_structured_params(max_length)
    final_url = f"{base_url}?{random_params}"
    
    print("URL telah dibuat!")
    print()
    print("Statistik:")
    print(f"- Panjang parameter: {len(random_params):,} karakter")
    print(f"- Panjang total URL: {len(final_url):,} karakter")
    print(f"- Jumlah parameter: {random_params.count('&') + 1} pasang")
    print()
    print("--- Preview (150 karakter pertama) ---")
    print(f"{final_url[:150]}...")
    print()
    
    output_file = input("Simpan ke file (default: generated_url.txt): ").strip()
    if not output_file:
        output_file = "generated_url.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_url)
    
    print()
    print("=" * 60)
    print(f"SUKSES! URL lengkap telah disimpan ke: {output_file}")
    print("=" * 60)
    
    show_full = input("Tampilkan URL lengkap? (y/n): ").strip().lower()
    if show_full == 'y':
        print()
        print("=== URL LENGKAP ===")
        print(final_url)


def main():
    print_banner()
    print_menu()
    
    choice = input("Gulir atau ketik Pilihan Anda [1/2/3/4/5]: ").strip()
    
    if choice == '1':
        process_python()
    elif choice == '2':
        process_javascript()
    elif choice == '3':
        process_shell()
    elif choice == '4':
        process_crypto()
    elif choice == '5':
        process_generate_url()
    else:
        print("ERROR: Pilihan tidak valid! Pilih 1, 2, 3, 4, atau 5.")
        sys.exit(1)


if __name__ == "__main__":
    main()

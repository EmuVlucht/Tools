# Security & Penetration Testing with ADB

## 1. Permission Analysis

### Check App Permissions
```bash
# List all permissions requested
adb shell dumpsys package com.example.app | grep "permission"

# Check dangerous permissions
adb shell dumpsys package com.example.app | grep -i "camera\|location\|storage"

# Get granted permissions
adb shell pm list permissions -d

# Check permission grants
adb shell dumpsys package com.example.app | grep "grant"
```

### Permission Exploitation
```bash
# Revoke critical permission
adb shell pm revoke com.example.app android.permission.CAMERA

# Grant elevated permission
adb shell pm grant com.example.app android.permission.WRITE_SECURE_SETTINGS

# Verify permission grant
adb shell pm dump com.example.app | grep "Permission"
```

---

## 2. Intent & Broadcast Analysis

### Monitor Intents
```bash
# Capture all intents
adb shell dumpsys activity intents

# Monitor broadcasts
adb logcat | grep "Broadcast"

# Track implicit intents
adb shell dumpsys activity broadcasts

# Export implicit intent filters
adb shell dumpsys package com.example.app | grep -A 5 "intent-filter"
```

### Intent Exploitation
```bash
# Send arbitrary intent
adb shell am start -a android.intent.action.VIEW -d "http://malicious.com"

# Send broadcast
adb shell am broadcast -a com.example.CUSTOM_ACTION

# Exploit content provider
adb shell am start -a android.intent.action.VIEW content://com.example.app/sensitive
```

---

## 3. Data Encryption Verification

### Check Encryption Status
```bash
# Full disk encryption
adb shell getprop ro.crypto.state

# Encryption type
adb shell getprop ro.crypto.type

# Encryption algorithm
adb shell dumpsys cryptfs

# File-based encryption
adb shell stat /data/user/
```

### Verify HTTPS Only
```bash
# Monitor network traffic
adb shell tcpdump -i any 'tcp port 80'

# Check cleartext traffic policy
adb pull /data/app/com.example.app/network_security_config.xml

# Verify certificate pinning
strings app.apk | grep -i "pin\|cert"
```

---

## 4. SQL Injection Testing

### Database Vulnerability Check
```bash
# Find databases
adb shell find /data/data/com.example.app -name "*.db"

# Test SQL injection
adb shell sqlite3 /data/data/com.example.app/db.db "SELECT * FROM users WHERE id='1 OR 1=1'"

# Check for parameterized queries
strings app.apk | grep "PreparedStatement"
```

---

## 5. Hardcoded Secrets Detection

### Search for Secrets
```bash
# API keys
strings app.apk | grep -i "api_key\|apikey"

# Passwords
strings app.apk | grep -i "password"

# Tokens
strings app.apk | grep -i "token\|bearer"

# Database credentials
strings app.apk | grep -i "mysql\|postgres"

# AWS keys
strings app.apk | grep -i "AKIA\|aws"
```

### Automated Secret Scanning
```bash
#!/bin/bash
# scan_secrets.sh

adb pull /data/app/com.example.app/base.apk app.apk

# Extract and scan
strings app.apk > app_strings.txt

grep -E "password|secret|key|token|credential" app_strings.txt > potential_secrets.txt

echo "Found $(wc -l < potential_secrets.txt) potential secrets"
cat potential_secrets.txt
```

---

## 6. Man-in-the-Middle (MITM) Testing

### Setup MITM Proxy
```bash
# Install Burp Suite or Mitmproxy
pip install mitmproxy

# Start proxy
mitmproxy -p 8080

# Configure device proxy
adb shell settings put global http_proxy 127.0.0.1:8080

# Monitor traffic
# View in Burp/Mitmproxy console
```

### SSL Certificate Pinning Bypass
```bash
# Identify pinning
strings app.apk | grep -i "pin"

# Try MITM with custom certificate
# Install custom CA certificate on device
adb push cacert.pem /sdcard/

# Use Frida to bypass
frida -U -l bypass_pinning.js -f com.example.app
```

---

## 7. Reverse Engineering for Security

### Extract Sensitive Code Paths
```bash
# Decompile authentication logic
apktool d app.apk
grep -r "login\|authenticate" app/smali/

# Find encryption methods
grep -r "encrypt\|cipher" app/smali/

# Locate key storage
grep -r "keyStore\|keyAlias" app/smali/
```

---

## 8. Android Keystore Analysis

### Verify Keystore Usage
```bash
# Check if using Android Keystore
strings app.apk | grep "AndroidKeystore"

# Verify key properties
adb shell dumpsys keystore | grep -i "key"

# Extract keys (if possible)
adb shell su -c "keytool -list -v -keystore /data/system/users/0/keyrings/keystore.db"
```

---

## 9. Vulnerability Scanning

### Automated Vulnerability Detection
```bash
#!/bin/bash
# vulnerability_scan.sh

APP="com.example.app"

echo "=== Security Vulnerability Scan ==="

# 1. Check for debuggable flag
echo "[*] Checking debuggable flag..."
adb shell dumpsys package $APP | grep "debuggable"

# 2. Check for exported components
echo "[*] Checking exported components..."
adb shell am instrument -w $APP | grep "exported"

# 3. Monitor for crashes
echo "[*] Monitoring for crashes..."
adb logcat -c
adb shell am start -n $APP/.MainActivity
sleep 5
CRASHES=$(adb logcat | grep -i "crash" | wc -l)
echo "Found $CRASHES crashes"

# 4. Check for SQL injection
echo "[*] Checking SQL injection vulnerability..."
adb shell am start -a android.intent.action.SEARCH -n $APP --es query "1' OR '1'='1"
```

---

## 10. Network Security Testing

### Test SSL/TLS Configuration
```bash
# Check SSL version
adb shell dumpsys ssl_engine | grep "version"

# Test cipher suites
adb shell dumpsys ssl_engine | grep "cipher"

# Verify certificate validation
adb logcat | grep "certificate"
```

---

## 11. Frida-Based Security Testing

```javascript
// bypass_ssl.js - Bypass SSL pinning with Frida

if (Java.available) {
    var TrustManager = Java.use("javax.net.ssl.TrustManager");
    var X509TrustManager = Java.use("javax.net.ssl.X509TrustManager");
    
    var TrustManagerImpl = Java.use("com.android.org.conscrypt.TrustManagerImpl");
    TrustManagerImpl.checkServerTrusted.implementation = function(chain, authType) {
        return;
    };
    
    console.log("SSL pinning bypassed");
}
```

---

## 12. Code Obfuscation Analysis

```bash
# Check if R8/ProGuard applied
strings app.apk | grep -i "r8\|proguard"

# Analyze obfuscated class names
apktool d app.apk
grep -r "^public.*class [a-z]$" app/smali/ | head -20

# Deobfuscation mapping
cat app/mapping.txt | head -20
```

---

## 13. Input Validation Testing

```bash
# Test with malicious input
adb shell am start -n com.example.app/.SearchActivity --es query "<script>alert(1)</script>"

# Path traversal
adb shell am start -n com.example.app/.FileActivity --es path "../../sensitive"

# Buffer overflow
adb shell am start -n com.example.app/.MainActivity --es input "AAAAAAAAAAAAA[1000 chars]"
```

---

## 14. Insecure Storage Testing

### Check for Unencrypted Data
```bash
# Pull app data
adb pull /data/data/com.example.app/shared_prefs/ ./prefs/

# Check plaintext storage
cat ./prefs/config.xml | grep -i "password\|token"

# Verify file permissions
adb shell ls -la /data/data/com.example.app/

# Check world-readable files
find ./prefs -type f -perm -004
```

---

## 15. Security Best Practices Checklist

```
Security Audit Checklist:
□ All data encrypted at rest
□ HTTPS only for network
□ Certificate pinning implemented
□ No hardcoded secrets
□ Permissions minimized
□ Input validation enforced
□ SQL injection prevention
□ CSRF protection
□ XSS protection
□ Secure random generation
□ Proper error handling
□ No sensitive data in logs
□ Secure storage used
□ Code obfuscation enabled
□ Security updates applied
```


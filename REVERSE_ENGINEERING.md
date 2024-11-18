# APK Reverse Engineering & Analysis

## 1. APK Extraction & Decompilation

```bash
# Extract APK
adb pull /data/app/com.example.app/base.apk app.apk

# Decompile APK
apktool d app.apk -o app_decompiled

# Extract resources
apktool d --no-src app.apk -o app_resources

# Decompile to Java
cfr app.apk --outputdir src/
```

---

## 2. AndroidManifest Analysis

```bash
# Extract manifest
adb pull /data/app/com.example.app/base.apk app.apk
apktool d app.apk

# View manifest
cat app/AndroidManifest.xml

# Find activities
grep "activity" AndroidManifest.xml

# Find permissions
grep "uses-permission" AndroidManifest.xml

# Decompile manifest
aapt dump badging app.apk
```

---

## 3. DEX & Classes Analysis

```bash
# Extract DEX files
adb shell "find /data/app -name '*.dex' -exec cp {} /sdcard/ \;"
adb pull /sdcard/*.dex ./

# Decompile DEX
d2j-dex2jar classes.dex
cfr classes-dex2jar.jar

# String analysis
strings classes.dex | grep -i "password\|token\|key"

# Bytecode inspection
baksmali d classes.dex -o output/
```

---

## 4. Resource Analysis

```bash
# Extract resources
apktool d app.apk

# Resource layout files
cat app/res/layout/activity_main.xml

# String resources
cat app/res/values/strings.xml

# Configuration files
find app/res -name "*.xml"

# Asset extraction
unzip app.apk assets/* -d extracted_assets/
```

---

## 5. Security Analysis

```bash
# Certificate info
keytool -printcert -jarfile app.apk

# Check signing
jarsigner -verify -verbose -certs app.apk

# String extraction for hardcoded secrets
strings app.apk | grep -i "api\|secret\|key\|password"

# Network endpoint discovery
strings app.apk | grep -E "http|https"
```

---

## 6. Smali Code Analysis

```bash
# Decompile to Smali
baksmali d classes.dex

# Search for specific functions
grep -r "onCreate" smali_classes/

# Analyze critical functions
grep -r "String\|Intent\|Bundle" smali_classes/

# Find obfuscated code
grep -r "a\|b\|c" smali_classes/ | head -20
```

---

## 7. Network Communication

```bash
# Extract URLs
strings app.apk | grep -E "http|url|endpoint"

# Intercept with proxy
adb shell settings put global http_proxy 127.0.0.1:8080

# Monitor traffic with Wireshark
tcpdump -i any 'host device_ip' -w capture.pcap
```

---

## 8. Frida Dynamic Analysis

```bash
# Install Frida
pip install frida-tools

# Start Frida server on device
adb push frida-server /data/local/tmp/
adb shell chmod +x /data/local/tmp/frida-server
adb shell /data/local/tmp/frida-server

# Hook functions
frida -U -l hook.js -f com.example.app
```

---

## 9. Xposed Framework

```bash
# Install Xposed
adb push XposedInstaller.apk /sdcard/
adb install /sdcard/XposedInstaller.apk

# Create module
# Module hook sensitive functions
# Log method calls
# Modify return values
```

---

## 10. APK Signing Analysis

```bash
# Extract certificate
unzip app.apk "META-INF/*" -d cert_extract/

# Analyze certificate
openssl pkcs7 -inform DER -in META-INF/CERT.RSA -print_certs

# Verify APK signature
jarsigner -verify -certs app.apk

# Re-sign APK
jarsigner -keystore keystore.jks app.apk key_alias
```


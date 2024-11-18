# ADB Security Best Practices

## 1. USB Debugging Security

### Enable Only When Needed
```bash
# Check USB Debugging status
adb shell getprop ro.debuggable

# Only enable when developing/testing
# Settings → Developer Options → USB Debugging
```

**Risk**: Anyone with USB access can control device

**Mitigation**:
- Disable after development
- Use PIN/password protection
- Keep device with you
- Don't leave unattended while enabled

---

## 2. Network ADB Security

### Restrict Network Access
```bash
# Only connect to trusted networks
# Avoid public WiFi when using ADB

# If must use public WiFi, use VPN
# Or use SSH tunnel

# SSH tunnel example
ssh -L 5555:localhost:5555 remote_host
adb connect localhost:5555
```

**Risk**: Network ADB traffic not encrypted

**Mitigation**:
- Use private networks only
- Use VPN if on public networks
- Use SSH tunneling
- Disconnect when not in use

---

## 3. Authorization & Verification

### Verify Device Authorization
```bash
# Authorized devices stored in
ls -la ~/.android/

# View fingerprint
adb shell settings get secure android_id

# Verify in device popup when connecting
# Accept only on trusted devices
```

**Risk**: Unauthorized access to device

**Mitigation**:
- Always verify fingerprint
- Reject unknown connections
- Revoke old authorizations regularly

---

## 4. Credential & Secret Protection

### Never Expose Secrets via ADB
```bash
# WRONG - Secrets in command history
adb shell settings put global api_key "my_secret_key"

# WRONG - Hardcoded in push file
adb push config_with_secrets.txt /sdcard/

# RIGHT - Use secure storage
# SharedPreferences with EncryptedSharedPreferences
# Or Keystore System
```

**Risk**: Secrets exposed in logs or file system

**Mitigation**:
- Use Android Keystore for sensitive data
- Never pass secrets via shell commands
- Don't push config files with secrets
- Clear shell history: `history -c`

---

## 5. Log Security

### Sanitize Logs
```bash
# WRONG - Sensitive data in logs
Log.d("TAG", "API Key: " + apiKey)

# RIGHT - Don't log sensitive data
if (BuildConfig.DEBUG) {
    Log.d("TAG", "Connecting to server...")
}
```

**Risk**: Sensitive data in logcat

**Mitigation**:
- Never log API keys or tokens
- Never log passwords
- Never log personal user data
- Use conditional logging with DEBUG flag

### Restrict Log Access
```bash
# Clear logs when sharing device
adb logcat -c

# Before device disposal
adb shell settings put global adb_enabled 0
adb shell settings put global usb_debug 0
```

---

## 6. File System Security

### Protect Files
```bash
# Don't push to world-readable locations
# WRONG
adb push credentials.txt /sdcard/

# RIGHT - Only to app private directory
adb shell "pm grant com.example.app android.permission.WRITE_EXTERNAL_STORAGE"

# Set proper permissions
adb shell chmod 600 /data/data/com.example.app/credentials
```

**Risk**: Files accessible by other apps

**Mitigation**:
- Store sensitive data in app-private directories
- Use proper file permissions
- Encrypt sensitive files
- Never store on /sdcard/ unless necessary

---

## 7. APK Security

### Verify APK Before Installation
```bash
# Check APK signature
adb shell pm dump com.example.app | grep "versionCode\|codePath"

# Verify signature
jarsigner -verify -verbose -certs app.apk

# Check for malware before installing
# Use VirusTotal or similar service
```

**Risk**: Malicious APK installation

**Mitigation**:
- Only install APKs from trusted sources
- Verify signatures
- Use antivirus scanning
- Keep Play Protect enabled

---

## 8. Root Access Security

### Avoid Rooting If Possible
```bash
# Check if device is rooted
adb shell "su -v"  # If succeeds, device is rooted

# Risks of rooting:
# - Disables security features
# - Disables SafetyNet
# - Voids warranty
# - Potential malware
```

**If Must Root:**
```bash
# Only on dedicated testing devices
# Isolate from production/personal use
# Never connect to untrusted networks
# Use managed root solutions (development boards)
```

---

## 9. Backup Security

### Secure Backups
```bash
# WRONG - Backup with sensitive data
adb backup -all -f backup.ab

# RIGHT - Encrypt backup after creation
adb backup -all -f backup.ab
gpg --symmetric backup.ab

# Or exclude sensitive data
adb backup -all -noapk -noshared -f backup.ab

# Store encrypted backup securely
chmod 600 backup.ab.gpg
```

**Risk**: Backup contains sensitive data

**Mitigation**:
- Encrypt backups
- Store securely
- Use full device encryption (Settings > Security > Encryption)
- Backup to encrypted storage only

---

## 10. Database Security

### Protect App Databases
```bash
# WRONG - Unencrypted database
SQLiteDatabase db = openDatabase("app.db", null, SQLiteDatabase.OPEN_READWRITE);

# RIGHT - Encrypted database (SQLCipher)
SQLiteDatabase db = SQLiteDatabase.openOrCreateDatabase("app.db", password, null);

# Or use Room with Encryption
Database db = Room.databaseBuilder(context, AppDatabase.class, "database-name")
    .openHelperFactory(new SqLiteCipherFactory(password))
    .build();
```

**Risk**: Unencrypted database readable by other apps

**Mitigation**:
- Use SQLCipher for database encryption
- Implement Room encryption
- Store encryption keys securely
- Never hardcode passwords

---

## 11. Network Security

### Secure Communication
```bash
# WRONG - HTTP communication
curl http://api.example.com/data

# RIGHT - HTTPS with certificate pinning
# Use okhttp3 CertificatePinner
CertificatePinner certificatePinner = new CertificatePinner.Builder()
    .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    .build();

OkHttpClient client = new OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .build();
```

**Risk**: Man-in-the-middle attacks

**Mitigation**:
- Always use HTTPS
- Implement certificate pinning
- Validate SSL certificates
- Use VPN for sensitive operations

---

## 12. Permission Security

### Minimize Permissions
```bash
# Check requested permissions
adb shell dumpsys package com.example.app | grep "requested permissions"

# Grant only necessary permissions
adb shell pm grant com.example.app android.permission.CAMERA
adb shell pm grant com.example.app android.permission.RECORD_AUDIO

# Revoke unnecessary permissions
adb shell pm revoke com.example.app android.permission.READ_CONTACTS
```

**Best Practices**:
- Request only necessary permissions
- Use runtime permissions (Android 6.0+)
- Implement permission rationale
- Regularly audit app permissions

---

## 13. Emulator Security

### Secure Emulator Usage
```bash
# Don't use emulator for production testing
# Create separate development emulator
emulator -avd MyDevEmulator

# Disable unnecessary features
# Don't enable root on production emulator
# Disable shared clipboard
emulator -avd MyEmulator -no-shared-libs
```

**Risk**: Emulator simulates production environment

**Mitigation**:
- Use separate emulators for dev/test/prod
- Don't expose to network
- Don't store production data
- Reset emulator state regularly

---

## 14. Script Security

### Secure ADB Scripts
```bash
# WRONG - Hardcoded credentials
#!/bin/bash
adb shell "sqlite3 db.db 'INSERT INTO users VALUES (1, \"password123\")'"

# RIGHT - Read from environment/secure storage
#!/bin/bash
if [ -z "$ADB_SECRET" ]; then
    echo "Set ADB_SECRET environment variable"
    exit 1
fi
# Use $ADB_SECRET

# Protect script file
chmod 700 script.sh

# Never commit to git
echo "script.sh" >> .gitignore
```

---

## 15. Device-Specific Security

### For Different Device Types

#### Personal Device
- Never enable USB Debugging on personal device
- Use device authentication
- Keep OS updated

#### Development Device
- Dedicated device for development
- Isolate from personal data
- Enable USB Debugging only
- Factory reset regularly

#### CI/CD Device
- Dedicated headless device/emulator
- Secure network access
- Automated cleanup
- No personal data

---

## 16. Disposal & Cleanup

### Before Device Disposal
```bash
# Factory reset
adb reboot recovery
# Select "Wipe data/factory reset"

# Or via ADB
adb shell wipe data

# Verify all data removed
adb shell ls /data/

# Remove authorization files from PC
rm ~/.android/adbkey
rm ~/.android/adbkey.pub
```

### Before Giving Device to Others
```bash
# Remove trusted USB devices
adb kill-server

# Clear development environment
rm -rf ~/.android/

# Remove ADB from PATH if not needed
```

---

## 17. Security Checklist

```
□ USB Debugging disabled when not needed
□ Only connect to trusted networks
□ Never log sensitive data
□ Verify APK signatures
□ Encrypt sensitive files
□ Use HTTPS for network communication
□ Implement certificate pinning
□ Encrypt databases
□ Minimize app permissions
□ Use Android Keystore for secrets
□ Secure backup files
□ Regular security updates
□ Factory reset before disposal
□ Remove authorizations
□ Test with multiple emulators/devices
□ Document security procedures
□ Train team on security practices
□ Regular security audits
□ Monitor for security vulnerabilities
```

---

## 18. Security Resources

- **Android Security**: https://developer.android.com/guide/topics/security
- **OWASP**: https://owasp.org/www-project-mobile-top-10/
- **Security Best Practices**: https://source.android.com/security
- **SSL/TLS Testing**: https://www.ssllabs.com/
- **Vulnerability Database**: https://nvd.nist.gov/

---

## 19. Common Security Mistakes

1. **Leaving USB Debugging on** - Always disable when not using
2. **Hardcoding secrets** - Use Keystore or environment variables
3. **Unencrypted backups** - Encrypt all backups
4. **HTTP instead of HTTPS** - Always use HTTPS
5. **Excessive logging** - Don't log sensitive data
6. **World-readable files** - Use proper permissions
7. **Unencrypted databases** - Use SQLCipher
8. **Over-permissioning** - Request minimum needed
9. **Ignoring warnings** - Address all security warnings
10. **Not updating** - Keep OS and tools updated

---

## 20. Security Incident Response

If device compromised:
```bash
# 1. Disconnect from network
# 2. Stop ADB connection
adb kill-server

# 3. Factory reset
adb shell "wipe data"

# 4. Remove from trusted devices
rm ~/.android/adbkey*

# 5. Update compromised passwords
# 6. Enable 2FA on accounts
# 7. Monitor for suspicious activity
```


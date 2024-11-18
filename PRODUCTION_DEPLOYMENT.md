# Production Deployment Guide

## 1. Pre-Production Checklist

```
BEFORE DEPLOYMENT:
□ All tests passing (unit, integration, UI)
□ Performance optimized (startup < 2s)
□ Crash rate zero on all devices
□ Memory leaks fixed
□ Battery drain acceptable
□ Security audit complete
□ App signing configured
□ ProGuard/R8 configured
□ Google Play policies reviewed
□ Version number bumped
□ Release notes prepared
□ Backup created
□ Rollback plan documented
```

---

## 2. Build Release APK

```bash
# Build signed release
./gradlew assembleRelease

# Verify APK
aapt dump badging app-release.apk

# Test before upload
adb install -r app-release.apk
adb shell am start -n com.example.app/.MainActivity
```

---

## 3. Google Play Upload

```bash
# Via Play Console web interface:
1. Go to https://play.google.com/console
2. Select app
3. Production → Create Release
4. Add APK/AAB
5. Add release notes
6. Review rollout percentage
7. Submit for review
```

---

## 4. Monitoring Deployment

```bash
# Monitor crash rate
adb logcat | grep -i crash

# Check user reviews
# Google Play Console → Reviews section

# Monitor downloads
# Google Play Console → Statistics
```

---

## 5. Multi-Region Deployment

```bash
# Configure per region
Google Play Console:
- Regions → Select countries
- Pricing → Set prices per region
- Localization → Translate for each region
```

---

## 6. Beta Testing

```bash
# Beta program
Google Play Console → Testing → Beta

# QA testing
adb install app-beta.apk
adb shell am start -n com.example.app/.MainActivity

# Collect feedback
ADB to capture logs during beta
```

---

## 7. Staged Rollout

```
Rollout strategy:
Day 1: 10% users
Day 2: 25% users
Day 3: 50% users
Day 4: 100% users

Monitor crash rate at each stage
Rollback if crashes > threshold
```

---

## 8. Analytics Integration

```bash
# Send analytics
adb shell am broadcast -a com.google.android.gms.analytics.ANALYTICS_DISPATCH

# Monitor events
Google Play Console → Real-time
```

---

## 9. Crash Monitoring

```bash
# Firebase Crashlytics
- Automatic crash reporting
- Real-time alerts
- Stack trace analysis

adb logcat | grep FirebaseCrashlytics
```

---

## 10. Version Management

```bash
# Version code increment
versionCode = 100 → 101

# Version name format
versionName = "1.0.0" → "1.0.1"

# Check in app
adb shell getprop ro.build.version
```


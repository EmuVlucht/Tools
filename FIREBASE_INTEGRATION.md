# Firebase Integration & Testing with ADB

## 1. Firebase Setup
```bash
# Verify Firebase connected
adb logcat | grep -i firebase

# Check Firebase version
adb shell dumpsys package com.google.firebase

# Monitor initialization
adb logcat | grep "FirebaseApp"
```

## 2. Analytics Testing
```bash
# Send test events
adb shell am broadcast -a com.google.android.gms.analytics.ANALYTICS_DISPATCH

# Verify events captured
# Check Firebase Console → Real-time

# Custom events
adb shell am start -n com.example.app/.MainActivity
# App sends analytics automatically
```

## 3. Crash Reporting
```bash
# Monitor crashes
adb logcat | grep "Crashlytics"

# Force crash for testing
adb shell am start -n com.example.app/.CrashActivity

# Verify in Firebase Console → Crashlytics
```

## 4. Remote Config
```bash
# Monitor remote config updates
adb logcat | grep "RemoteConfig"

# Force fetch
# In app: mFirebaseRemoteConfig.fetch()
```

## 5. Authentication
```bash
# Test login
adb shell am start -n com.example.app/.LoginActivity

# Monitor auth state
adb logcat | grep "Auth"
```

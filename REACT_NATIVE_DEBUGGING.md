# React Native Debugging with ADB

## 1. Metro Bundler Setup
```bash
# Start bundler
npm start

# Via ADB (device connects automatically)
adb reverse tcp:8081 tcp:8081
```

## 2. Debug Mode
```bash
# Reload JS
adb shell input keyevent 82  # Menu key

# Reload (React Native)
adb shell am start -a react.intent.action.LAUNCH_DEVTOOLS

# Debug via Chrome
Open: http://localhost:8081/debugger-ui
```

## 3. Monitoring
```bash
# Metro logs
adb logcat | grep ReactNative

# Performance monitoring
adb shell dumpsys meminfo com.example.app

# Frame rate
adb shell dumpsys gfxinfo com.example.app
```

## 4. Testing
```bash
# Jest tests
npm test

# E2E tests
detox build-framework-cache
detox build-app
detox test
```

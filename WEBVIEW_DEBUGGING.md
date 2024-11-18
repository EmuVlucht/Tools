# WebView Debugging & Testing

## 1. Enable WebView Debugging
```bash
# Enable Chrome debugging
adb shell settings put global webview_vmsize_mb 100

# Monitor WebView
adb logcat | grep "WebView"

# Chrome DevTools
# Visit: chrome://inspect
```

## 2. JavaScript Injection
```bash
# Test JavaScript execution
adb shell dumpsys webview

# Monitor JS console
adb logcat | grep "JavaScript"
```

## 3. Certificate Issues
```bash
# Handle untrusted certificates
# Update system CA store or use SSL bypass

# Test HTTPS
adb shell am start -n com.example.app/.WebActivity --es url "https://example.com"
```

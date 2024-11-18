# Accessibility Testing with ADB

## 1. TalkBack Setup

```bash
# Enable TalkBack
adb shell settings put secure enabled_accessibility_services com.google.android.marktalkback/com.google.android.marktalkback.TalkBackService

# Verify enabled
adb shell settings get secure enabled_accessibility_services

# Disable TalkBack
adb shell settings put secure enabled_accessibility_services ""
```

## 2. Screen Reader Testing

```bash
# Record with TalkBack
adb shell screenrecord --size=1080x1920 /sdcard/accessibility_test.mp4

# Monitor TalkBack events
adb logcat | grep -i talkback

# Check accessibility services
adb shell dumpsys accessibility
```

## 3. Font Size & Display

```bash
# Increase font scale
adb shell settings put system font_scale 1.5

# Enable high contrast
adb shell settings put secure high_text_contrast_enabled 1

# Disable animations
adb shell settings put global window_animation_scale 0
```

## 4. Color Blindness Testing

```bash
# Enable color correction
adb shell settings put secure accessibility_display_daltonizer 0

# Deuteranopia (red-green)
adb shell settings put secure accessibility_display_daltonizer 12

# Protanopia
adb shell settings put secure accessibility_display_daltonizer 11

# Tritanopia (blue-yellow)
adb shell settings put secure accessibility_display_daltonizer 13
```

## 5. Gesture Navigation

```bash
# Enable gesture navigation
adb shell settings put secure navigation_mode 2

# Test back gesture
adb shell input swipe 50 500 500 500

# Test home gesture
adb shell input swipe 500 2000 500 500

# Test recents gesture
adb shell input swipe 50 500 50 100
```

## 6. Voice Control

```bash
# Enable voice control
adb shell settings put secure accessibility_service_service_enabled voice_control 1

# Test voice input
adb shell am start -a android.intent.action.VOICE_COMMAND
```

## 7. Magnification

```bash
# Enable magnification
adb shell settings put secure accessibility_screen_magnification_enabled 1

# Set zoom level
adb shell settings put secure accessibility_display_magnification_scale 2.0
```


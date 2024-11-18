# Game Development & Testing with ADB

## 1. Game Performance Profiling

```bash
# Frame rate monitoring
adb shell dumpsys gfxinfo com.example.game | grep "Frames"

# GPU usage
adb shell cmd gpu profile

# Memory profiling
adb shell dumpsys meminfo com.example.game

# CPU usage
adb shell top -p $(adb shell pidof com.example.game)
```

---

## 2. Graphics & Rendering

```bash
# Enable GPU profiling
adb shell setprop debug.hwui.profile DRAW_TIME

# Show GPU overdraw
adb shell setprop debug.hwui.overdraw show_overdraw

# Profile rendering
adb shell cmd gpu profile

# Disable animations for testing
adb shell settings put global window_animation_scale 0
adb shell settings put global transition_animation_scale 0
adb shell settings put global animator_duration_scale 0
```

---

## 3. Input & Touch Testing

```bash
# Simulate touch
adb shell input tap 500 500

# Multi-touch gesture
adb shell input touchscreen swipe 100 100 500 500 200

# Pinch zoom
adb shell input touchscreen swipe 250 250 500 500 100
adb shell input touchscreen swipe 500 500 250 250 100

# Long press
adb shell input touchscreen press 500 500
sleep 1
adb shell input touchscreen release
```

---

## 4. Accelerometer & Gyroscope

```bash
# Simulate device rotation
adb shell settings put system screen_brightness 200

# Send sensor events
adb shell cmd sensor send_event accelerometer 0 0 10

# Simulate tilt
adb shell cmd sensor set_value accelerometer 10 0 0
```

---

## 5. Network Condition Simulation

```bash
# Simulate latency
adb shell tc qdisc add dev eth0 root netem delay 100ms

# Simulate packet loss
adb shell tc qdisc add dev eth0 root netem loss 5%

# Limit bandwidth
adb shell tc qdisc add dev eth0 root tbf rate 1mbit burst 32kbit latency 400ms

# Reset network
adb shell tc qdisc del dev eth0 root
```

---

## 6. Audio Testing

```bash
# Play sound
adb shell am start -a android.intent.action.VIEW -d file:///sdcard/sound.mp3 -t audio/mpeg

# Audio info
adb shell dumpsys audio

# Test microphone
adb shell am start -n com.android.soundrecorder/.SoundRecorder
```

---

## 7. Gameplay Recording

```bash
# Record gameplay
adb shell screenrecord --size=1920x1080 --bit-rate=20000000 /sdcard/gameplay.mp4

# Record with audio
ffmpeg -i /sdcard/gameplay.mp4 -i /sdcard/audio.m4a output.mp4
```

---

## 8. Battery Impact Testing

```bash
# Monitor battery during gameplay
for i in {1..100}; do
    BATTERY=$(adb shell dumpsys battery | grep level | awk '{print $2}')
    echo "$(date): $BATTERY%"
    sleep 60
done
```

---

## 9. Multiplayer Testing

```bash
# Test on multiple devices
emulator -avd Device1 &
emulator -avd Device2 &
emulator -avd Device3 &

# Install on all
for device in $(adb devices | grep device | awk '{print $1}'); do
    adb -s "$device" install game.apk
done

# Connect to same server
# Verify connectivity
```

---

## 10. Asset Validation

```bash
# Pull assets
adb pull /data/data/com.example.game/assets ./

# Check file sizes
du -sh ./assets/*

# Verify integrity
md5sum ./assets/* > checksums.md5
```


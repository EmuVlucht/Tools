# Machine Learning & TensorFlow with ADB

## 1. TensorFlow Lite Model Deployment

```bash
# Push model to device
adb push model.tflite /sdcard/

# Pull model from device
adb pull /data/data/com.example.app/model.tflite ./

# Monitor inference
adb logcat | grep "TensorFlow"
```

## 2. Performance Profiling

```bash
# Measure inference time
adb shell dumpsys meminfo

# GPU delegation
adb shell settings put global tflite_gpu_enabled 1

# NNAPI delegation
adb shell settings put global tflite_nnapi_enabled 1
```

## 3. Model Validation

```bash
# Test model inputs/outputs
adb shell dumpsys package com.example.app | grep -i ml

# Memory usage during inference
adb shell dumpsys meminfo | grep -i native

# CPU usage
adb shell top -p $(pidof com.example.app)
```


# Team Collaboration & Workflows with ADB

## 1. Shared Device Pool

```bash
#!/bin/bash
# device_pool.sh

# List available devices
adb devices

# Assign device to team member
adb forward tcp:5555 tcp:5555

# Lock device during use
adb shell settings put global device_locked true

# Release device
adb shell settings put global device_locked false
```

## 2. Build Sharing

```bash
# Build for team
./gradlew assembleDebug

# Upload to shared server
scp app.apk team_server:/builds/

# Team members pull
adb install http://team_server/builds/app.apk
```

## 3. Test Result Sharing

```bash
#!/bin/bash
# share_test_results.sh

# Run tests
adb shell am instrument -w com.example.test/androidx.test.runner.AndroidJUnitRunner > results.xml

# Upload results
scp results.xml team_server:/test_results/

# Generate report
xsltproc results.xml > report.html
```

## 4. Device Scheduling

```bash
# Reserve device for period
adb shell settings put global device_reserved_by "team_member_name"
adb shell settings put global device_reserved_until "2025-01-15"

# Release reservation
adb shell settings delete global device_reserved_by
```

## 5. Unified Logging

```bash
# Centralize logs
adb logcat | tee device_logs.txt | ssh team_server 'cat >> /logs/device_$(date +%Y%m%d).log'

# Query shared logs
ssh team_server 'grep -i error /logs/*.log'
```


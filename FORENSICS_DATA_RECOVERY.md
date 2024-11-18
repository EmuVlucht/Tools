# Digital Forensics & Data Recovery with ADB

## 1. Data Extraction

### Pull All Data
```bash
# Pull entire device storage
adb pull /sdcard/ ./device_backup/

# Pull app data (requires root)
adb shell su -c "tar -czf /sdcard/app_data.tar.gz /data/data/"
adb pull /sdcard/app_data.tar.gz ./

# Pull system data
adb shell su -c "tar -czf /sdcard/system_backup.tar.gz /system/"
adb pull /sdcard/system_backup.tar.gz ./
```

### Database Extraction
```bash
# Extract app databases
adb shell su -c "find /data/data -name '*.db' -exec cp {} /sdcard/backup/ \;"
adb pull /sdcard/backup/ ./databases/

# Export database content
adb shell su -c "sqlite3 /data/data/com.example.app/databases/app.db '.dump' > /sdcard/app_db.sql"
adb pull /sdcard/app_db.sql ./
```

---

## 2. Partition Forensics

### Extract Partitions
```bash
# List partitions
adb shell su -c "ls -la /dev/block/by-name/"

# Dump boot partition
adb shell su -c "dd if=/dev/block/by-name/boot of=/sdcard/boot.img"
adb pull /sdcard/boot.img ./

# Dump system partition
adb shell su -c "dd if=/dev/block/mmcblk0p1 of=/sdcard/system.img bs=4096"
adb pull /sdcard/system.img ./

# Dump all partitions
adb shell su -c "dd if=/dev/block/mmcblk0 of=/sdcard/full_device.img bs=4096"
```

---

## 3. File Carving

### Recover Deleted Files
```bash
# List deleted files in partition
adb shell su -c "debugfs -R 'ls -l' /dev/block/by-name/userdata"

# Use data carving tools
# Tools: PhotoRec, testdisk

# Copy entire partition for analysis
adb shell su -c "dd if=/dev/block/by-name/userdata of=/sdcard/userdata.img"
adb pull /sdcard/userdata.img ./

# Analyze with forensic tools on computer
strings userdata.img | grep -i "email\|password"
```

---

## 4. Memory Forensics

### Dump RAM
```bash
# Requires rooted device and Linux kernel module

# Method 1: Via /proc/mem
adb shell su -c "cat /proc/kmem | dd of=/sdcard/kernel_memory.bin"

# Method 2: Via crash dump
adb shell su -c "cat /proc/[PID]/maps > /sdcard/memory_map.txt"
adb shell su -c "cat /proc/[PID]/pagemap > /sdcard/page_map.bin"
```

---

## 5. Log Forensics

### Collect System Logs
```bash
# Pull event logs
adb pull /data/anr/ ./anr_traces/
adb pull /data/tombstones/ ./crashes/

# Extract kernel logs
adb shell su -c "dmesg > /sdcard/kernel_log.txt"
adb pull /sdcard/kernel_log.txt ./

# SELinux audit logs
adb shell su -c "cat /sys/fs/selinux/avc/cache_stats > /sdcard/selinux_audit.txt"
```

---

## 6. Evidence Collection

### Forensic Chain of Custody
```bash
#!/bin/bash
# forensic_collection.sh

EVIDENCE_DIR="evidence_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$EVIDENCE_DIR"

# Device information
adb shell getprop > "$EVIDENCE_DIR/device_props.txt"
adb shell dumpsys > "$EVIDENCE_DIR/system_dump.txt"

# User data
adb pull /sdcard/ "$EVIDENCE_DIR/sdcard/"
adb pull /data/data/ "$EVIDENCE_DIR/app_data/" 2>/dev/null || true

# Create checksum
cd "$EVIDENCE_DIR"
find . -type f -exec md5sum {} \; > ../checksums.md5
cd ..

# Compress evidence
tar -czf "${EVIDENCE_DIR}.tar.gz" "$EVIDENCE_DIR"

# Generate report
cat > "$EVIDENCE_DIR/REPORT.txt" << EOF
Evidence Collection Report
Date: $(date)
Device: $(adb shell getprop ro.product.model)
Collection Method: ADB Forensic Tools
Chain of Custody: Established
EOF

echo "Evidence collected to: $EVIDENCE_DIR"
```

---

## 7. Communication Recovery

### Extract Messages & Calls
```bash
# Pull SMS database
adb pull /data/data/com.android.providers.telephony/databases/mmssms.db ./

# Extract SMS content
adb shell su -c "sqlite3 /data/data/com.android.providers.telephony/databases/mmssms.db 'SELECT * FROM sms;' > /sdcard/sms_export.csv"

# Pull call logs
adb shell su -c "sqlite3 /data/data/com.android.providers.contacts/databases/contacts.db 'SELECT * FROM calls;' > /sdcard/calls_export.csv"

# Pull chat apps databases
adb pull /data/data/com.whatsapp/databases/ ./whatsapp_db/
adb pull /data/data/com.facebook.orca/databases/ ./messenger_db/
```

---

## 8. Browser History Recovery

### Extract Browser Data
```bash
# Chrome data
adb pull /data/data/com.android.chrome/app_chrome/Default/ ./chrome_data/

# Firefox data
adb pull /data/data/org.mozilla.firefox/files/mozilla/ ./firefox_data/

# Browser history
adb shell su -c "sqlite3 /data/data/com.android.chrome/app_chrome/Default/History 'SELECT * FROM urls;' > /sdcard/chrome_history.csv"
```

---

## 9. App Installation History

### Recover App List
```bash
# Get installed packages
adb shell pm list packages -i > installed_apps.txt

# Get package manager logs
adb shell su -c "cat /data/system/packages.xml > /sdcard/packages.xml"
adb pull /sdcard/packages.xml ./

# Parse installation times
adb shell su -c "dumpsys package > /sdcard/package_info.txt"
adb pull /sdcard/package_info.txt ./

# Extract timestamps
grep -i "install\|update" package_info.txt
```

---

## 10. Metadata Analysis

### Extract File Metadata
```bash
# Get file modification times
adb shell find /sdcard -type f -printf '%T@ %p\n' | sort -n

# Extract EXIF data from photos
adb pull /sdcard/DCIM/Camera/ ./photos/
exiftool *.jpg > photo_metadata.txt

# Get app installation dates
adb shell ls -la /data/app/ | grep date

# File access times
adb shell find /data/data -type f -printf '%a %T@ %p\n'
```

---

## 11. Hidden Files Recovery

### Find Hidden Data
```bash
# List all hidden files
adb shell find /sdcard -name ".*" -type f

# Search in app cache
adb shell find /data/data -name "cache" -type d

# Find system hidden files
adb shell su -c "find / -name '.*' -type f -size +0 2>/dev/null"

# Recovery .tmp files
adb shell find /data -name "*.tmp" -type f
```

---

## 12. Timeline Analysis

### Create File Access Timeline
```bash
#!/bin/bash
# timeline_analysis.sh

# Extract all file timestamps
adb shell find /sdcard -type f -printf '%T@ %Tc %p\n' | sort > timeline.txt

# Group by day
awk '{print $3}' timeline.txt | cut -d' ' -f1-3 | sort | uniq -c > timeline_by_day.txt

# Most recently accessed
head -20 timeline.txt

# Suspicious activity detection
awk '$NF ~ /\.apk$|\.exe$|\.sh$/ {print}' timeline.txt
```

---

## 13. Hash Verification

### Create Forensic Hashes
```bash
# MD5 hashing
adb shell find /sdcard -type f -exec md5sum {} \; > device_hashes_md5.txt
adb pull device_hashes_md5.txt ./

# SHA256 hashing
adb shell find /data/data -type f -exec sha256sum {} \; > data_hashes_sha256.txt

# Verify integrity
md5sum -c device_hashes_md5.txt
```

---

## 14. Incident Response

### Automated Incident Response
```bash
#!/bin/bash
# incident_response.sh

INCIDENT_ID=$1
RESPONSE_DIR="incident_$INCIDENT_ID"

mkdir -p "$RESPONSE_DIR"

# Immediate actions
echo "[*] Collecting evidence for incident: $INCIDENT_ID"

# Disconnect network (preserve volatile data)
adb shell settings put global airplane_mode_on 1

# Capture process list
adb shell ps -A > "$RESPONSE_DIR/process_list.txt"

# Capture network connections
adb shell netstat > "$RESPONSE_DIR/netstat.txt"

# Capture open files
adb shell lsof > "$RESPONSE_DIR/lsof.txt"

# Capture memory state
adb shell dumpsys > "$RESPONSE_DIR/dumpsys_full.txt"

# Preserve evidence
adb pull /data/ "$RESPONSE_DIR/data_snapshot/"

echo "[*] Incident response data saved to: $RESPONSE_DIR"
```

---

## 15. Best Practices

```
Forensic Collection:
✓ Maintain chain of custody
✓ Use write-blocking devices
✓ Create checksums/hashes
✓ Document all actions
✓ Use forensic tools on copies only
✓ Preserve timestamps
✓ Encrypt collected data
✓ Create backup copies

DON'T:
✗ Modify device
✗ Connect to WiFi/network
✗ Install apps
✗ Run system updates
✗ Clear logs
✗ Reset device
✗ Use adb without USB debugging
```


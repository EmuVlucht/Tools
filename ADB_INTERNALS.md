# ADB Internals - Arsitektur & Cara Kerja

## 1. ADB Protocol Architecture

### Tiga Komponen Utama
```
┌─────────────────────────────────────────────────────┐
│                  ADB Architecture                    │
├─────────────────────────────────────────────────────┤
│                                                      │
│  [ADB Client]  ←→ [ADB Server] ←→ [ADB Daemon]    │
│   (Komputer)        (Komputer)     (Perangkat)     │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Communication Flow
```
1. Client mengirim command ke Server
2. Server merutekan ke Device Daemon (adbd)
3. Daemon mengeksekusi command
4. Result dikirim balik ke Client
5. Semua berkomunikasi melalui socket TCP
```

---

## 2. ADB Server Internals

### Server Lifecycle
```bash
# Start server
adb start-server
# Output:
# * daemon not running; starting now at tcp:5037
# * daemon started successfully

# Check server status
ps aux | grep adb

# Kill server
adb kill-server

# Restart server
adb kill-server && adb start-server
```

### Server Port
```
Default: TCP port 5037
- Hanya 1 server bisa mendengarkan port ini
- Server mendengarkan localhost
- Clients terhubung ke server melalui socket
```

### Server State Management
```bash
# Lihat connected devices yang tracked
adb devices

# Server maintains:
# - Connection state untuk setiap device
# - Services yang sedang berjalan
# - Port forwarding rules
```

---

## 3. Device Daemon (adbd)

### Daemon Location & Process
```bash
# adbd berjalan di device dengan privilege tinggi
adb shell ls -la /system/bin/adbd

# Biasanya:
# /system/bin/adbd (Android 10+)
# atau bagian dari init process

# Cek apakah adbd running
adb shell ps | grep adbd
```

### Daemon Initialization
```
1. Device boot
2. adbd dimulai oleh init process
3. Mendengarkan koneksi dari server
4. USB atau Network connection
5. Siap menerima commands
```

### Daemon Capabilities
```bash
# List capabilities yang didukung
adb shell cat /system/etc/adb/capabilities

# Typical capabilities:
# - shell command execution
# - file transfer
# - app management
# - debugging
# - port forwarding
```

---

## 4. USB Communication Protocol

### USB Handshake
```bash
# USB device info
adb shell cat /proc/version

# USB descriptor
adb shell cat /sys/kernel/debug/usb/devices

# USB driver (Linux)
lsusb -v | grep -A 20 Android

# USB driver (Windows)
# Device Manager → Android Device → Properties
```

### USB Data Transmission
```
Protocol: ADB Protocol v2 (or compatible)
- Messages have format: [length:4][crc32:4][data:length][crc32:4]
- All integers in little-endian format
- Checksum menggunakan CRC32
```

### USB Connection States
```bash
# Check USB state
adb shell getprop usb.state

# States:
# - mtp (Media Transfer Protocol)
# - adb (ADB mode)
# - mtp,adb (MTP + ADB)
# - fastboot (Bootloader)
```

---

## 5. Network (WiFi) Communication

### TCP Connection Setup
```bash
# Enable TCP mode
adb tcpip 5555

# Device akan listen pada 0.0.0.0:5555
# Client dapat connect dari network

# Verify network mode
adb shell getprop service.adb.tcp.port
# Output: 5555
```

### Network Packet Structure
```
┌──────────────────────────────────┐
│ TCP Packet (port 5555)           │
├──────────────────────────────────┤
│ ADB Protocol Header              │
│ - Command (4 bytes)              │
│ - Arg0 (4 bytes)                 │
│ - Arg1 (4 bytes)                 │
│ - Data length (4 bytes)          │
│ - Data checksum (4 bytes)        │
│ - Magic (4 bytes)                │
├──────────────────────────────────┤
│ Actual Data                      │
└──────────────────────────────────┘
```

### Network Encryption
```bash
# Check if encrypted
adb shell getprop ro.secure

# Modern Android (API 30+): Encryption default
# Older versions: Plain text possible
```

---

## 6. Authentication & Security

### Key Generation
```bash
# Keys terletak di:
# Linux/Mac: ~/.android/
# Windows: %USERPROFILE%\.android\

ls -la ~/.android/

# Files:
# - adbkey (private key)
# - adbkey.pub (public key)
# - adb_usb.ini (authorized keys)
```

### Authentication Flow
```bash
# 1. Device request public key dari client
# 2. Client shows "Allow" prompt pada device
# 3. Device menyimpan public key
# 4. Future connections authenticated otomatis
```

### Reset Authentication
```bash
# Clear all authorizations
rm ~/.android/adbkey*

# Device akan menampilkan prompt lagi
adb connect 192.168.1.100:5555
```

---

## 7. Command Execution Pipeline

### Command Flow
```
adb shell <command>
    ↓
[Client] → "shell:<command>"
    ↓
[Server] → Transmit via protocol
    ↓
[Device Daemon] → Parse command
    ↓
[Shell Interpreter] → Execute
    ↓
[Output] → Send back
    ↓
[Server] → Forward to client
    ↓
[Client] → Display output
```

### Service Routing
```bash
# Services available:
adb shell service list

# Common services:
# - shell: (shell execution)
# - app: (app management)
# - file-sync: (file transfer)
# - debug: (debugging)
# - transport: (connection)
```

---

## 8. File Sync Protocol

### Sync Implementation
```bash
# File transfer menggunakan sync protocol
adb push file.txt /sdcard/

# Protocol steps:
# 1. Client → "sync:" command
# 2. Device → Acknowledge
# 3. Client → File data in chunks
# 4. Device → Verify & store
# 5. Device → "OKAY" response
```

### Data Chunks
```
Setiap file split menjadi chunks (64KB default)

┌──────────────────┐
│ FILE HEADER      │
│ - Name           │
│ - Size           │
├──────────────────┤
│ CHUNK 1 (64KB)   │
├──────────────────┤
│ CHUNK 2 (64KB)   │
├──────────────────┤
│ ... more chunks  │
├──────────────────┤
│ DONE             │
└──────────────────┘
```

---

## 9. Socket Management

### Local Sockets
```bash
# ADB creates local sockets untuk communication

# On device:
adb shell ls /dev/socket/ | grep adb

# Socket functions:
# - shell exchange
# - file sync
# - port forwarding
# - reverse forwarding
```

### Socket Forwarding
```bash
# TCP port forwarding
adb forward tcp:8888 tcp:80

# Mechanism:
# 1. Server listen pada tcp:8888
# 2. Data dari localhost:8888 forward ke device
# 3. Device forward ke tcp:80 locally
```

---

## 10. Thread Model

### ADB Server Threads
```
Main Thread
├── Accept connections
├── Handle clients
└── Route commands

Device Thread (per device)
├── Read from device
├── Write to device
└── Handle transport

Connection Thread (per client)
├── Read client commands
├── Validate syntax
└── Queue for device
```

### Concurrency Handling
```bash
# Multiple clients dapat terkoneksi bersamaan
# Server menggunakan event multiplexing

# Verify:
# - Open multiple terminals
# - Run adb commands simultaneously
# - Server menangani concurrent requests
```

---

## 11. Error Handling & Reliability

### Protocol Reliability
```
Mechanisms:
- Checksums untuk data integrity
- Retransmission untuk lost packets
- Timeout untuk stuck connections
- Keep-alive untuk connection monitoring
```

### Error Codes
```bash
# Lihat error messages
adb devices  # CONNECTION_REFUSED
adb install  # INSTALL_FAILED_*

# Error handling:
# - Client side validation
# - Server side error reporting
# - Device side command execution
```

---

## 12. Debugging ADB Internals

### Verbose Mode
```bash
# Maximum verbosity
adb -v devices

# Output includes:
# - Connection attempts
# - Protocol messages
# - Device state changes
```

### Log Analysis
```bash
# ADB server logs (if available)
adb logcat | grep adb

# System logs
adb shell cat /dev/kmsg | grep adb

# Strace monitoring
strace -f -e trace=network adb devices
```

### Protocol Capture
```bash
# Capture USB traffic
sudo tcpdump -i usb0 -A

# Capture TCP traffic (WiFi ADB)
tcpdump -i eth0 -n port 5555 -A

# Wireshark analysis
# - Start Wireshark
# - Capture on relevant interface
# - Filter: tcp.port == 5555
```

---

## 13. Performance Characteristics

### Latency
```
Typical latencies:
- USB: 5-50ms per roundtrip
- WiFi: 10-100ms per roundtrip
- Bluetooth: 50-500ms (if supported)
```

### Throughput
```
Typical speeds:
- USB 2.0: 480 Mbps theoretical
- USB 3.0: 5 Gbps theoretical
- WiFi 5GHz: 100-300 Mbps
- Practical: 50-200 Mbps depending on device
```

### Optimization
```bash
# Batch operations untuk reduce roundtrips
# Instead of:
for file in *.txt; do
    adb push $file /sdcard/
done

# Better:
adb push *.txt /sdcard/

# Parallel transfers
for file in *.txt; do
    adb push $file /sdcard/ &
done
wait
```

---

## 14. Memory Model

### Client Memory Usage
```bash
# ADB client typically uses: 10-50MB
# Scales dengan number of devices

# Check memory
ps aux | grep adb
# Lihat VSZ dan RSS columns
```

### Server Memory Management
```bash
# Server maintains state untuk:
# - Each connected device
# - Each client connection
# - Port forwarding rules
# - File sync buffers

# Can grow to 100MB+ dengan many devices
```

---

## 15. Source Code Reference

```
ADB Source Structure:
adb/ (AOSP repository)
├── client/
│   └── main.c
├── daemon/
│   ├── adbd.c
│   └── services.c
├── libadbd/
│   ├── transport.c
│   └── socket.c
└── libfd/
    └── fdevent.c
```

### Key Functions
```c
// Client side (adb command execution)
int main(int argc, char* argv[])  // Entry point
int adb_commandline()             // Command parsing
int connect_device()              // Device connection

// Server side (daemon)
int main()                        // Server startup
void accept_connection()          // Accept clients
void handle_command()             // Command handler

// Device side (adbd)
int main()                        // Daemon startup
void handle_packet()              // Packet handling
void service_bootstrap()          // Service initialization
```


# Advanced ADB Networking Configuration

## 1. WiFi ADB Connection

### Setup WiFi ADB
```bash
# Connect device via USB first
adb devices

# Enable TCP/IP mode on port 5555
adb tcpip 5555

# Check device IP
adb shell getprop dhcp.wlan0.ipaddress
# Or
adb shell ip addr show wlan0

# Connect via WiFi
adb connect 192.168.1.100:5555

# Verify
adb devices
# 192.168.1.100:5555     device
```

### Connect Without USB
```bash
# If adb not available via USB:
# Manual steps on device:

# 1. Enable Developer Mode
# 2. Enable USB Debugging
# 3. Find IP: Settings → WiFi → Current network
# 4. From computer:
adb connect 192.168.1.100:5555
```

---

## 2. Network Port Forwarding

### TCP Port Forwarding
```bash
# Forward device port to computer
adb forward tcp:8888 tcp:80

# Now: localhost:8888 → device:80

# List forwards
adb forward --list

# Remove forward
adb forward --remove tcp:8888

# Remove all
adb forward --remove-all
```

### Reverse Port Forwarding
```bash
# Forward computer port to device
adb reverse tcp:8888 tcp:3000

# device:8888 → computer:3000

# List reverse forwards
adb reverse --list

# Remove
adb reverse --remove tcp:8888
```

### Use Cases
```
Forward examples:
- Debug server: adb forward tcp:5555 tcp:5555
- HTTP: adb forward tcp:80 tcp:8080
- HTTPS: adb forward tcp:443 tcp:8443
- Database: adb forward tcp:3306 tcp:3306

Reverse examples:
- Webhook: adb reverse tcp:9000 tcp:3000
- Testing: adb reverse tcp:5000 tcp:5000
```

---

## 3. Multiple Device Networking

### Connect Multiple Devices
```bash
# List all
adb devices

# Connect multiple WiFi devices
adb connect 192.168.1.100:5555
adb connect 192.168.1.101:5555
adb connect 192.168.1.102:5555

# Run command on specific device
adb -s 192.168.1.100:5555 install app.apk

# Run on all devices
for device in $(adb devices | grep device | awk '{print $1}'); do
    adb -s "$device" shell getprop ro.build.version.release
done
```

### Device Load Balancing
```bash
#!/bin/bash
# parallel_tasks.sh

DEVICES=$(adb devices | grep device | grep -v List | awk '{print $1}')
DEVICE_ARRAY=($DEVICES)
TASK_COUNT=0

for file in *.apk; do
    DEVICE=${DEVICE_ARRAY[$((TASK_COUNT % ${#DEVICE_ARRAY[@]})}}
    
    echo "Installing $file on $DEVICE..."
    adb -s "$DEVICE" install -r "$file" &
    
    TASK_COUNT=$((TASK_COUNT + 1))
done

wait
echo "✓ All installations complete"
```

---

## 4. Network Diagnostics

### Check Network Connectivity
```bash
# Device network interfaces
adb shell ifconfig

# Or newer format
adb shell ip addr show

# Check default route
adb shell ip route show

# DNS settings
adb shell getprop net.dns1
adb shell getprop net.dns2
```

### Ping Test
```bash
# Test connectivity
adb shell ping -c 4 8.8.8.8

# From device to computer
adb shell ping -c 4 192.168.1.50

# Measure latency
adb shell ping -c 10 192.168.1.1 | grep "min/avg/max"
```

### Traceroute
```bash
# Device to host
adb shell traceroute google.com

# With busybox
adb shell busybox traceroute -m 20 google.com
```

---

## 5. ADB over SSH

### SSH Tunneling ADB
```bash
# Forward ADB through SSH to remote server

# Local setup:
ssh -L 5037:remote_device:5037 user@remote_server

# Now connect locally
adb devices
# Shows device from remote server

# Or:
adb connect localhost:5555
```

### SSH for WiFi ADB
```bash
# Complex setup for accessing device through SSH

# On SSH server (with access to device):
adb forward tcp:5555 tcp:5555

# From your computer:
ssh -L 5555:localhost:5555 user@server

# Connect:
adb connect localhost:5555
```

---

## 6. Network Performance Monitoring

### Monitor ADB Bandwidth
```bash
#!/bin/bash
# monitor_adb_speed.sh

# Large file transfer with speed measurement
FILE_SIZE=100  # MB

dd if=/dev/zero bs=1M count=$FILE_SIZE | \
    adb shell "cat > /sdcard/test_file.bin"

# Measure read speed
time adb pull /sdcard/test_file.bin ./

# Calculate speed
# real time 0m5.234s → ~19 MB/s
```

### USB vs WiFi Comparison
```bash
#!/bin/bash
# compare_connections.sh

# USB test
echo "USB Test:"
time adb -s emulator-5554 push 100MB_file /sdcard/

# WiFi test  
echo "WiFi Test:"
time adb -s 192.168.1.100:5555 push 100MB_file /sdcard/
```

---

## 7. Multi-Network Setup

### Device on Multiple Networks
```bash
# Check all connections
adb shell getprop net.dns1
adb shell getprop net.dns2

# Dual WiFi + Cellular
adb shell cat /sys/class/net/*/operstate

# Force network interface
adb shell sysctl net.ipv4.ip_forward=1
```

---

## 8. Network Address Translation (NAT)

### Port Forwarding through NAT
```bash
# If device behind NAT router

# On router: Forward external port → device IP:5555
# Example: Forward external 5555 → 192.168.1.100:5555

# From outside network:
adb connect external_ip:5555
```

### IPv4 vs IPv6
```bash
# Check device IP version
adb shell ip addr show | grep "inet"

# IPv4: inet 192.168.1.100
# IPv6: inet6 fe80::...

# Connect with IPv6
adb connect [fe80::1%eth0]:5555
```

---

## 9. VPN & Proxy Through ADB

### VPN Testing
```bash
# Check if VPN is active
adb shell getprop net.dns1

# If VPN: DNS may be different

# Kill VPN
adb shell am force-stop com.vpn.app

# Restart
adb shell am start -n com.vpn.app/.MainActivity
```

### Proxy Configuration
```bash
# Set device proxy
adb shell settings put global http_proxy 192.168.1.50:8080

# Remove proxy
adb shell settings put global http_proxy :0

# Verify
adb shell settings get global http_proxy
```

---

## 10. Network Packet Analysis

### Capture Network Traffic
```bash
# On device (with root)
adb shell su -c "tcpdump -i eth0 -w /sdcard/capture.pcap"

# Let it capture for 30 seconds, then Ctrl+C

# Pull capture
adb pull /sdcard/capture.pcap

# Analyze with Wireshark
wireshark capture.pcap
```

### Monitor Network Calls
```bash
# Monitor DNS queries
adb shell su -c "tcpdump -i any 'udp port 53'"

# Monitor HTTP
adb shell su -c "tcpdump -i any 'tcp port 80'"

# Monitor specific app
adb shell su -c "tcpdump -i any 'net 192.168.1.100'"
```

---

## 11. Custom Network Routes

### Add Network Routes
```bash
# Add static route
adb shell su -c "ip route add 192.168.2.0/24 via 192.168.1.1"

# List routes
adb shell ip route show

# Remove route
adb shell su -c "ip route del 192.168.2.0/24"
```

---

## 12. Socket Connection Debugging

### Monitor Open Connections
```bash
# List open sockets
adb shell netstat

# More detailed
adb shell ss -tulpn

# Monitor adb connections
adb shell netstat | grep 5555

# Foreign connections
adb shell netstat | grep ESTABLISHED
```

---

## 13. Network Latency Optimization

### Reduce ADB Latency
```bash
# USB 3.0 for faster speed
# WiFi: Use 5GHz band (better latency than 2.4GHz)

# Check WiFi quality
adb shell dumpsys wifi | grep "signal_poll"

# Reduce frame aggregation
adb shell settings put global wifi_frame_aggregation 0

# Increase WiFi power
adb shell settings put global wifi_power_save_mode 0
```

---

## 14. Device Discovery

### Find Connected Devices on Network
```bash
#!/bin/bash
# discover_adb_devices.sh

SUBNET="192.168.1"

echo "Scanning for ADB devices..."

for i in {1..254}; do
    IP="$SUBNET.$i"
    echo -n "Checking $IP... "
    
    timeout 1 adb connect $IP:5555 2>/dev/null && echo "Found!" || echo "No"
done
```

---

## 15. Network Troubleshooting

```bash
# WiFi Connection Fails
# Solution:
adb tcpip 5555  # Must do via USB first
adb disconnect
adb connect IP:5555

# Slow Connection
# Solution:
# - Use USB instead of WiFi
# - Check WiFi signal strength
# - Reduce concurrent operations

# Connection Drops
# Solution:
# - Increase keep-alive timeout
# - Use wired connection if possible
# - Check firewall rules

# Address Already in Use
# Solution:
netstat -ano | findstr :5555  # Windows
kill -9 PID
# Or use different port:
adb tcpip 5556
```


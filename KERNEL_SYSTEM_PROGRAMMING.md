# Kernel & System Programming with ADB

## 1. Kernel Access

```bash
# Check kernel version
adb shell uname -a

# Kernel compilation flags
adb shell cat /proc/cmdline

# Kernel modules
adb shell lsmod

# Load module
adb shell insmod module.ko
```

## 2. System Calls

```bash
# Monitor syscalls
adb shell strace -e open,read,write -f pidof app

# Profile syscalls
adb shell perf record -p $(pidof app)
adb shell perf report
```

## 3. Memory Management

```bash
# Virtual memory stats
adb shell cat /proc/meminfo

# Page cache info
adb shell cat /proc/sys/vm/

# Memory pressure
adb shell cat /proc/pressure/memory
```

## 4. Filesystem Access

```bash
# Filesystem info
adb shell df -h

# Inode usage
adb shell df -i

# Mount points
adb shell mount
```

## 5. Process Management

```bash
# Process tree
adb shell pstree

# Process details
adb shell ps -ef | head

# Resource limits
adb shell ulimit -a
```


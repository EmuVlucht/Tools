# Python Automation with ADB

## 1. PyADB Library

```python
from pyadb import adb

# Get device list
devices = adb.get_devices()
print(devices)

# Connect to device
device = adb.get_device('emulator-5554')

# Shell command
device.shell('getprop ro.build.version.release')

# Push/Pull files
device.push('local_file.txt', '/sdcard/file.txt')
device.pull('/sdcard/file.txt', 'local_file.txt')

# Install APK
device.install('app.apk')
```

---

## 2. Subprocess ADB Wrapper

```python
import subprocess
import json

def run_adb(command):
    """Run ADB command and return output"""
    result = subprocess.run(['adb'] + command.split(), 
                          capture_output=True, 
                          text=True)
    return result.stdout

def get_devices():
    """Get list of connected devices"""
    output = run_adb('devices')
    devices = []
    for line in output.split('\n')[1:]:
        if line.strip() and 'device' in line:
            device_id = line.split()[0]
            devices.append(device_id)
    return devices

def install_app(device_id, apk_path):
    """Install app on device"""
    cmd = f'adb -s {device_id} install -r {apk_path}'
    return subprocess.run(cmd.split())

# Usage
devices = get_devices()
for device in devices:
    install_app(device, 'app.apk')
```

---

## 3. Parallel Device Operations

```python
from concurrent.futures import ThreadPoolExecutor
import subprocess

def execute_on_device(device_id, command):
    """Execute command on single device"""
    cmd = f'adb -s {device_id} shell {command}'
    result = subprocess.run(cmd.split(), capture_output=True, text=True)
    return device_id, result.stdout

def execute_on_all_devices(command, max_workers=5):
    """Execute command on all devices in parallel"""
    devices = get_devices()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(execute_on_device, device, command)
            for device in devices
        ]
        
        results = {}
        for future in futures:
            device_id, output = future.result()
            results[device_id] = output
    
    return results

# Usage
results = execute_on_all_devices('getprop ro.build.version.release')
for device, version in results.items():
    print(f"{device}: {version}")
```

---

## 4. File Transfer Automation

```python
import os
import subprocess
from pathlib import Path

def batch_push(device_id, local_dir, remote_dir):
    """Push entire directory to device"""
    for file_path in Path(local_dir).rglob('*'):
        if file_path.is_file():
            relative_path = file_path.relative_to(local_dir)
            remote_path = f"{remote_dir}/{relative_path}"
            
            cmd = f'adb -s {device_id} push {file_path} {remote_path}'
            subprocess.run(cmd.split())

def batch_pull(device_id, remote_dir, local_dir):
    """Pull entire directory from device"""
    cmd = f'adb -s {device_id} pull {remote_dir} {local_dir}'
    subprocess.run(cmd.split())

# Usage
batch_push('emulator-5554', './configs', '/sdcard/configs')
batch_pull('emulator-5554', '/sdcard/logs', './device_logs')
```

---

## 5. Screenshot & Video Automation

```python
import subprocess
import time
from datetime import datetime

def capture_screenshot(device_id, output_file=None):
    """Capture screenshot"""
    if not output_file:
        output_file = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    
    subprocess.run(f'adb -s {device_id} shell screencap -p /sdcard/temp.png'.split())
    subprocess.run(f'adb -s {device_id} pull /sdcard/temp.png {output_file}'.split())
    subprocess.run(f'adb -s {device_id} shell rm /sdcard/temp.png'.split())
    
    return output_file

def record_video(device_id, duration=60, output_file=None):
    """Record screen video"""
    if not output_file:
        output_file = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    
    remote_file = f"/sdcard/video_{int(time.time())}.mp4"
    
    # Start recording
    cmd = f'adb -s {device_id} shell screenrecord --time-limit={duration} {remote_file}'
    subprocess.run(cmd.split())
    
    # Pull video
    subprocess.run(f'adb -s {device_id} pull {remote_file} {output_file}'.split())
    
    return output_file

# Usage
screenshot = capture_screenshot('emulator-5554')
video = record_video('emulator-5554', duration=30)
```

---

## 6. App Installation & Testing

```python
def install_multiple_apps(device_id, app_list):
    """Install multiple APKs on device"""
    for app_path in app_list:
        print(f"Installing {app_path}...")
        cmd = f'adb -s {device_id} install -r {app_path}'
        result = subprocess.run(cmd.split(), capture_output=True)
        
        if result.returncode == 0:
            print(f"  ✓ Success")
        else:
            print(f"  ✗ Failed: {result.stderr.decode()}")

def launch_app(device_id, package_name, activity):
    """Launch app on device"""
    cmd = f'adb -s {device_id} shell am start -n {package_name}/{activity}'
    return subprocess.run(cmd.split())

def uninstall_app(device_id, package_name):
    """Uninstall app"""
    cmd = f'adb -s {device_id} uninstall {package_name}'
    return subprocess.run(cmd.split())

# Usage
install_multiple_apps('emulator-5554', [
    'app1.apk',
    'app2.apk',
    'app3.apk'
])

launch_app('emulator-5554', 'com.example.app', '.MainActivity')
```

---

## 7. Logcat Parsing

```python
import subprocess
import re
from datetime import datetime

def get_logcat(device_id, filter_tag=None):
    """Get logcat output"""
    cmd = f'adb -s {device_id} logcat'
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, text=True)
    
    for line in process.stdout:
        if filter_tag is None or filter_tag in line:
            print(line.strip())

def parse_crashes(device_id):
    """Parse crash logs"""
    cmd = f'adb -s {device_id} logcat'
    result = subprocess.run(cmd.split(), capture_output=True, text=True)
    
    crashes = []
    for line in result.stdout.split('\n'):
        if 'FATAL' in line or 'crash' in line.lower():
            crashes.append(line)
    
    return crashes

def monitor_app_logs(device_id, app_package, duration=60):
    """Monitor logs for specific app"""
    cmd = f'adb -s {device_id} logcat | grep {app_package}'
    subprocess.run(cmd, shell=True, timeout=duration)

# Usage
crashes = parse_crashes('emulator-5554')
for crash in crashes:
    print(crash)
```

---

## 8. Device State Management

```python
class DeviceManager:
    def __init__(self, device_id):
        self.device_id = device_id
    
    def get_prop(self, prop_name):
        """Get device property"""
        cmd = f'adb -s {self.device_id} shell getprop {prop_name}'
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        return result.stdout.strip()
    
    def get_device_info(self):
        """Get full device info"""
        return {
            'manufacturer': self.get_prop('ro.product.manufacturer'),
            'model': self.get_prop('ro.product.model'),
            'android': self.get_prop('ro.build.version.release'),
            'api': self.get_prop('ro.build.version.sdk'),
            'device': self.get_prop('ro.product.device'),
        }
    
    def is_device_available(self):
        """Check if device is available"""
        cmd = f'adb -s {self.device_id} shell getprop ro.build.version.release'
        result = subprocess.run(cmd.split(), capture_output=True)
        return result.returncode == 0
    
    def reboot(self, mode='system'):
        """Reboot device"""
        cmd = f'adb -s {self.device_id} reboot {mode}'
        subprocess.run(cmd.split())

# Usage
device = DeviceManager('emulator-5554')
print(device.get_device_info())
print(f"Available: {device.is_device_available()}")
```

---

## 9. Performance Monitoring

```python
import time

class PerformanceMonitor:
    def __init__(self, device_id):
        self.device_id = device_id
    
    def measure_startup(self, package_name, activity, runs=3):
        """Measure app startup time"""
        times = []
        
        for i in range(runs):
            cmd = f'adb -s {self.device_id} shell am start -W {package_name}/{activity}'
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            
            # Parse TotalTime
            for line in result.stdout.split('\n'):
                if 'TotalTime' in line:
                    time_ms = int(line.split()[-1])
                    times.append(time_ms)
        
        return {
            'avg': sum(times) / len(times),
            'min': min(times),
            'max': max(times),
            'runs': times
        }
    
    def measure_memory(self, package_name):
        """Measure app memory usage"""
        cmd = f'adb -s {self.device_id} shell dumpsys meminfo {package_name}'
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        
        for line in result.stdout.split('\n'):
            if 'TOTAL' in line:
                return int(line.split()[-1])
    
    def measure_battery(self, duration=60):
        """Monitor battery usage"""
        battery_before = int(self.get_battery())
        time.sleep(duration)
        battery_after = int(self.get_battery())
        
        return battery_before - battery_after
    
    def get_battery(self):
        """Get battery percentage"""
        cmd = f'adb -s {self.device_id} shell dumpsys battery'
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        
        for line in result.stdout.split('\n'):
            if 'level' in line:
                return line.split()[-1]

# Usage
monitor = PerformanceMonitor('emulator-5554')
startup_times = monitor.measure_startup('com.example.app', '.MainActivity')
print(f"Avg startup: {startup_times['avg']}ms")
```

---

## 10. Batch Testing Script

```python
#!/usr/bin/env python3
import subprocess
import json
from datetime import datetime

class TestRunner:
    def __init__(self):
        self.results = []
    
    def run_test_suite(self, devices, app_path):
        """Run test suite on multiple devices"""
        for device in devices:
            result = self.test_device(device, app_path)
            self.results.append(result)
    
    def test_device(self, device_id, app_path):
        """Test app on single device"""
        result = {
            'device': device_id,
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        
        # Installation test
        cmd = f'adb -s {device_id} install -r {app_path}'
        install_result = subprocess.run(cmd.split(), capture_output=True)
        result['tests']['installation'] = install_result.returncode == 0
        
        # Launch test
        cmd = f'adb -s {device_id} shell am start -n com.example.app/.MainActivity'
        launch_result = subprocess.run(cmd.split(), capture_output=True)
        result['tests']['launch'] = launch_result.returncode == 0
        
        # Crash check
        cmd = f'adb -s {device_id} logcat | grep -i crash'
        crash_result = subprocess.run(cmd, shell=True, capture_output=True)
        result['tests']['no_crashes'] = crash_result.returncode != 0
        
        return result
    
    def generate_report(self):
        """Generate test report"""
        report = json.dumps(self.results, indent=2)
        with open('test_report.json', 'w') as f:
            f.write(report)
        return report

# Usage
def get_devices():
    result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
    devices = []
    for line in result.stdout.split('\n')[1:]:
        if line.strip() and 'device' in line:
            devices.append(line.split()[0])
    return devices

runner = TestRunner()
devices = get_devices()
runner.run_test_suite(devices, 'app.apk')
print(runner.generate_report())
```


# ADB Integration with Popular Tools

## 1. Android Studio Integration

### Direct IDE Integration
```
Android Studio → Tools → Device Manager
- Visual device management
- Logcat viewer built-in
- Device file explorer
- System profiler integration
```

### Terminal in Android Studio
```bash
# Use built-in terminal
View → Tool Windows → Terminal

# Common commands
adb devices
adb install app.apk
adb shell
adb logcat
```

---

## 2. Visual Studio Code

### Extensions
```
Recommended extensions:
- "Android" by Mishkin Berteig
- "ADB Interface" by Lonker
- "Android Debug Bridge" by Baha Abukaff
```

### Setup
```json
{
  "terminal.integrated.defaultProfile.linux": "bash",
  "adb.port": 5037,
  "adb.path": "/path/to/adb"
}
```

### Custom Tasks
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "ADB Install",
      "type": "shell",
      "command": "adb",
      "args": ["install", "-r", "app.apk"],
      "presentation": {
        "reveal": "always"
      }
    },
    {
      "label": "ADB Logcat",
      "type": "shell",
      "command": "adb",
      "args": ["logcat"],
      "isBackground": true
    }
  ]
}
```

---

## 3. Jetbrains IDEs

### IntelliJ IDEA / WebStorm
```
Tools → Android Device Manager
Tools → Analyze Stack Trace or Logcat
Tools → Device File Explorer
```

### Custom Run Configurations
```
Edit Configurations →
- Before launch: Gradle Task
- After launch: Upload to device
```

---

## 4. DevOps Tools

### Terraform Example
```hcl
resource "null_resource" "deploy_app" {
  provisioner "local-exec" {
    command = "adb install -r app.apk"
  }
}
```

### Ansible Integration
```yaml
- name: Deploy Android App
  hosts: build_servers
  tasks:
    - name: Install APK
      command: adb -s {{ device_id }} install -r app.apk
      
    - name: Run tests
      command: adb -s {{ device_id }} shell am instrument -w com.example.test/.TestRunner
```

---

## 5. Test Automation Frameworks

### Appium + ADB
```python
from appium import webdriver

desired_caps = {
    'platformName': 'Android',
    'automationName': 'UiAutomator2',
    'deviceName': 'Android Device',
    'app': '/path/to/app.apk'
}

driver = webdriver.Remote('http://localhost:4723', desired_caps)
driver.find_element_by_id('resource-id').click()
```

### Espresso + ADB
```kotlin
@RunWith(AndroidJUnit4::class)
class MainActivityTest {
    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)
    
    @Test
    fun testUI() {
        onView(withId(R.id.button)).perform(click())
    }
}

// Run via ADB
adb shell am instrument -w com.example.test/androidx.test.runner.AndroidJUnitRunner
```

---

## 6. Slack Integration

### Notify Slack on Build
```bash
#!/bin/bash
# notify_slack.sh

curl -X POST -H 'Content-type: application/json' \
    --data '{
        "text":"Android build completed",
        "blocks":[
            {
                "type":"section",
                "text": {
                    "type":"mrkdwn",
                    "text":"*Build Status*\nAPP: app.apk\nStatus: ✅ Success"
                }
            }
        ]
    }' \
    $SLACK_WEBHOOK_URL
```

---

## 7. GitHub Integration

### GitHub Actions Workflow
```yaml
name: Deploy APK

on: [push]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install ADB
        run: sudo apt-get install android-tools-adb
      
      - name: Deploy
        run: |
          adb kill-server
          adb start-server
          adb install -r app.apk
```

---

## 8. Docker with ADB

### Docker Image
```dockerfile
FROM ubuntu:20.04

RUN apt-get update && apt-get install -y android-tools-adb

WORKDIR /workspace
COPY . .

ENV ADB_SERVER_PORT=5037

ENTRYPOINT ["adb"]
```

### Docker Compose
```yaml
version: '3'
services:
  adb:
    build: .
    ports:
      - "5037:5037"
    volumes:
      - ~/.android:/root/.android
    command: start-server
```

---

## 9. Kubernetes Deployment

### K8s Job
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: adb-test
spec:
  template:
    spec:
      containers:
      - name: adb
        image: android-tools:latest
        command: ["adb", "install", "-r", "app.apk"]
      restartPolicy: Never
  backoffLimit: 3
```

---

## 10. Python Integration

### PyADB Library
```python
from pyadb import adb

# Get device list
devices = adb.get_devices()

# Connect
device = adb.get_device('emulator-5554')

# Commands
device.shell('am start -n com.example.app/.MainActivity')
device.install('app.apk')
device.pull('file.txt', 'local_file.txt')
```

### Subprocess Integration
```python
import subprocess

def run_adb_command(command):
    result = subprocess.run(['adb'] + command.split(), 
                          capture_output=True, 
                          text=True)
    return result.stdout

# Usage
devices = run_adb_command('devices')
print(devices)
```

---

## 11. Monitoring Tools

### Grafana + ADB
```python
# Export metrics
import time
import subprocess

while True:
    meminfo = subprocess.check_output(['adb', 'shell', 'dumpsys', 'meminfo']).decode()
    # Parse and send to Grafana
    time.sleep(60)
```

### Prometheus Integration
```python
from prometheus_client import Counter, Gauge
import subprocess

test_counter = Counter('adb_tests_total', 'Total ADB tests')
memory_gauge = Gauge('device_memory_bytes', 'Device memory')

def update_metrics():
    result = subprocess.check_output(['adb', 'shell', 'dumpsys', 'meminfo'])
    # Extract memory and update gauge
    test_counter.inc()
```

---

## 12. API Integration

### REST API Wrapper
```python
from flask import Flask
import subprocess

app = Flask(__name__)

@app.route('/devices')
def get_devices():
    result = subprocess.check_output(['adb', 'devices'])
    return {'devices': result.decode()}

@app.route('/install/<apk>')
def install_apk(apk):
    subprocess.run(['adb', 'install', apk])
    return {'status': 'installed'}

if __name__ == '__main__':
    app.run()
```

---

## 13. Logging & Observability

### ELK Stack Integration
```bash
#!/bin/bash
# send_to_elk.sh

adb logcat | while read line; do
    curl -X POST "http://elasticsearch:9200/android-logs/_doc" \
        -H "Content-Type: application/json" \
        -d "{\"log\": \"$line\", \"timestamp\": \"$(date -u +'%Y-%m-%dT%H:%M:%SZ')\"}"
done
```


# ADB Integration with CI/CD Pipelines

## 1. GitHub Actions Integration

### Basic Setup
```yaml
# .github/workflows/adb-test.yml
name: ADB Testing

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Install ADB
        run: |
          sudo apt-get update
          sudo apt-get install -y android-tools-adb
      
      - name: List devices
        run: adb devices
      
      - name: Run instrumented tests
        run: adb shell am instrument -w com.example.test/androidx.test.runner.AndroidJUnitRunner
```

### APK Installation & Testing
```yaml
name: Build and Test

on: [push]

jobs:
  test:
    runs-on: macos-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Android SDK
        uses: android-actions/setup-android@v2
      
      - name: Build APK
        run: ./gradlew assembleDebug
      
      - name: Start emulator
        uses: ReactiveCircus/android-emulator-runner@v2
        with:
          api-level: 30
          script: |
            adb install app/build/outputs/apk/debug/app-debug.apk
            adb shell am start -n com.example.app/.MainActivity
            adb shell am instrument -w com.example.app.test/androidx.test.runner.AndroidJUnitRunner
```

---

## 2. Jenkins Pipeline

### Jenkinsfile Example
```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh '''
                    which adb || echo "Installing ADB..."
                    adb devices
                '''
            }
        }
        
        stage('Build') {
            steps {
                sh './gradlew clean assembleDebug'
            }
        }
        
        stage('Install') {
            steps {
                sh '''
                    adb install -r app/build/outputs/apk/debug/app-debug.apk
                    sleep 5
                '''
            }
        }
        
        stage('Test') {
            steps {
                sh '''
                    adb shell am instrument -w \
                        com.example.app.test/androidx.test.runner.AndroidJUnitRunner
                '''
            }
        }
        
        stage('Collect Reports') {
            steps {
                sh '''
                    adb pull /data/data/com.example.app/test_results.xml ./
                '''
                junit 'test_results.xml'
            }
        }
    }
    
    post {
        always {
            sh 'adb kill-server'
        }
    }
}
```

---

## 3. GitLab CI

### .gitlab-ci.yml
```yaml
stages:
  - build
  - test
  - deploy

variables:
  GRADLE_OPTS: "-Dorg.gradle.daemon=false"
  ANDROID_SDK_ROOT: "/opt/android-sdk"

build:
  stage: build
  image: mcr.microsoft.com/windows/servercore:ltsc2019
  script:
    - ./gradlew assembleDebug
  artifacts:
    paths:
      - app/build/outputs/apk/debug/
    expire_in: 1 week

test:
  stage: test
  image: mcr.microsoft.com/windows/servercore:ltsc2019
  needs:
    - build
  script:
    - adb devices
    - adb install app/build/outputs/apk/debug/app-debug.apk
    - adb shell am instrument -w com.example.app.test/androidx.test.runner.AndroidJUnitRunner
  artifacts:
    reports:
      junit: test_results.xml
    paths:
      - screenshots/
      - logs/
```

---

## 4. Docker Integration

### Dockerfile
```dockerfile
FROM ubuntu:latest

# Install dependencies
RUN apt-get update && apt-get install -y \
    android-tools-adb \
    android-tools-fastboot \
    curl \
    git \
    build-essential

# Copy project
COPY . /workspace
WORKDIR /workspace

# Expose ADB port
EXPOSE 5037

# Set environment
ENV PATH="/android-sdk/platform-tools:${PATH}"

# Default command
CMD ["/bin/bash"]
```

### Docker Compose
```yaml
version: '3'

services:
  adb-server:
    build: .
    ports:
      - "5037:5037"
    volumes:
      - .:/workspace
    environment:
      - ADB_SERVER_PORT=5037
    command: adb start-server && sleep infinity
  
  test-runner:
    build: .
    depends_on:
      - adb-server
    volumes:
      - .:/workspace
      - ./results:/results
    environment:
      - ADB_HOST=adb-server
    command: |
      bash -c '
        adb connect adb-server:5037
        adb devices
        adb install app.apk
        adb shell am instrument -w com.example.test/androidx.test.runner.AndroidJUnitRunner
      '
```

---

## 5. Gradle Integration

### build.gradle.kts
```kotlin
plugins {
    id("com.android.application")
}

android {
    compileSdk = 33
    defaultConfig {
        applicationId = "com.example.app"
        minSdk = 24
        targetSdk = 33
    }
}

// Custom tasks
tasks.register<Exec>("installApp") {
    commandLine = listOf("adb", "install", "-r", 
        "build/outputs/apk/debug/app-debug.apk")
}

tasks.register<Exec>("runTests") {
    dependsOn("installApp")
    commandLine = listOf("adb", "shell", "am", "instrument", "-w",
        "com.example.app.test/androidx.test.runner.AndroidJUnitRunner")
}

tasks.register<Exec>("recordScreen") {
    commandLine = listOf("adb", "shell", "screenrecord",
        "/sdcard/recording.mp4")
}

// Wire to build cycle
tasks.named("assembleDebug").configure {
    finalizedBy("installApp")
}
```

---

## 6. Maven Integration

### pom.xml
```xml
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>android-app</artifactId>
    <version>1.0</version>
    <packaging>apk</packaging>
    
    <build>
        <plugins>
            <plugin>
                <groupId>com.jayway.maven.plugins.android.generation2</groupId>
                <artifactId>android-maven-plugin</artifactId>
                <version>4.6.2</version>
                <extensions>true</extensions>
                <configuration>
                    <sdk>
                        <platform>33</platform>
                    </sdk>
                </configuration>
                <executions>
                    <execution>
                        <goals>
                            <goal>deploy</goal>
                            <goal>run</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
```

---

## 7. Continuous Deployment

### Deploy Script
```bash
#!/bin/bash
# deploy.sh - Deploy to all devices

APK=$1
VERSION=$2

if [ -z "$APK" ] || [ -z "$VERSION" ]; then
    echo "Usage: ./deploy.sh app.apk version"
    exit 1
fi

# Get all devices
DEVICES=$(adb devices | grep device | grep -v "List of attached" | awk '{print $1}')

echo "Deploying $APK (v$VERSION) to all devices..."

for DEVICE in $DEVICES; do
    echo "=== Deploying to $DEVICE ==="
    
    # Backup current version
    adb -s "$DEVICE" shell pm dump com.example.app > "backup_$DEVICE.txt"
    
    # Uninstall old version
    adb -s "$DEVICE" uninstall com.example.app
    
    # Install new version
    adb -s "$DEVICE" install "$APK"
    
    # Verify installation
    if adb -s "$DEVICE" shell pm list packages | grep -q com.example.app; then
        echo "✓ Successfully deployed to $DEVICE"
        
        # Log deployment
        echo "$(date) - Deployed v$VERSION to $DEVICE" >> deploy.log
    else
        echo "✗ Failed to deploy to $DEVICE"
        exit 1
    fi
done

echo "Deployment complete!"
```

---

## 8. Test Report Collection

### Report Generator
```bash
#!/bin/bash
# collect_test_results.sh

REPORT_DIR="test_reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$REPORT_DIR/$TIMESTAMP"

# Collect from all devices
DEVICES=$(adb devices | grep device | grep -v "List of attached" | awk '{print $1}')

for DEVICE in $DEVICES; do
    echo "Collecting results from $DEVICE..."
    
    adb -s "$DEVICE" pull /data/data/com.example.app/test_results/ \
        "$REPORT_DIR/$TIMESTAMP/$DEVICE/"
    
    # Convert to XML if needed
    if [ -f "$REPORT_DIR/$TIMESTAMP/$DEVICE/results.txt" ]; then
        echo "Converting results..."
        # Custom conversion script
        python3 convert_to_junit.py \
            "$REPORT_DIR/$TIMESTAMP/$DEVICE/results.txt" \
            "$REPORT_DIR/$TIMESTAMP/$DEVICE/results.xml"
    fi
done

echo "✓ Reports collected to $REPORT_DIR/$TIMESTAMP"
```

---

## 9. Automated Performance Testing

### Performance CI Pipeline
```yaml
# .github/workflows/performance-test.yml
name: Performance Test

on: [push]

jobs:
  performance:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Android SDK
        uses: android-actions/setup-android@v2
      
      - name: Start emulator
        uses: ReactiveCircus/android-emulator-runner@v2
        with:
          api-level: 30
          script: |
            # Install app
            adb install app.apk
            
            # Collect baseline metrics
            adb shell dumpsys meminfo com.example.app > baseline.txt
            
            # Run performance test
            timeout 300 adb shell am start -n com.example.app/.MainActivity
            
            # Collect metrics after test
            adb shell dumpsys meminfo com.example.app > after.txt
            
            # Compare metrics
            python3 compare_metrics.py baseline.txt after.txt
      
      - name: Upload metrics
        uses: actions/upload-artifact@v2
        with:
          name: performance-metrics
          path: metrics/
```

---

## 10. Notification Integration

### Slack Notification
```bash
#!/bin/bash
# notify_slack.sh

STATUS=$1
BUILD_URL=$2

PAYLOAD=$(cat <<EOF
{
  "text": "Android Build Status",
  "attachments": [
    {
      "color": "$([ "$STATUS" = "SUCCESS" ] && echo "good" || echo "danger")",
      "title": "Build $STATUS",
      "text": "Build URL: $BUILD_URL",
      "fields": [
        {
          "title": "Branch",
          "value": "$GITHUB_REF",
          "short": true
        },
        {
          "title": "Commit",
          "value": "$GITHUB_SHA",
          "short": true
        }
      ]
    }
  ]
}
EOF
)

curl -X POST -H 'Content-type: application/json' \
    --data "$PAYLOAD" \
    $SLACK_WEBHOOK_URL
```

---

## 11. Email Notification
```yaml
name: Email Notification

on: [workflow_run]

jobs:
  notify:
    runs-on: ubuntu-latest
    if: github.event.workflow_run.conclusion == 'failure'
    
    steps:
      - name: Send email
        uses: davismatejcs/gmail-action@v1
        with:
          to: ${{ secrets.NOTIFY_EMAIL }}
          subject: "Build Failed"
          body: |
            Build failed for commit: ${{ github.event.workflow_run.head_commit.message }}
            
            Run: ${{ github.event.workflow_run.html_url }}
```

---

## 12. Artifact Management

### Store Test Results
```bash
#!/bin/bash
# upload_artifacts.sh

ARTIFACT_DIR="artifacts"
BUILD_NUMBER=$1

mkdir -p "$ARTIFACT_DIR"

# Collect logs
adb logcat -d > "$ARTIFACT_DIR/logcat.txt"

# Collect screenshots
adb pull /sdcard/screenshots/ "$ARTIFACT_DIR/" 2>/dev/null || true

# Collect crash data
adb pull /data/anr/ "$ARTIFACT_DIR/crashes/" 2>/dev/null || true

# Compress
zip -r "build-$BUILD_NUMBER.zip" "$ARTIFACT_DIR"

# Upload to S3
aws s3 cp "build-$BUILD_NUMBER.zip" s3://my-bucket/android-builds/

echo "✓ Artifacts uploaded"
```

---

## Best Practices

1. **Parallel Testing**: Run tests on multiple devices simultaneously
2. **Caching**: Cache APK and dependencies to speed up builds
3. **Timeouts**: Set appropriate timeouts for long-running tests
4. **Cleanup**: Always clean up resources (adb kill-server, rm temp files)
5. **Logging**: Capture detailed logs for debugging failures
6. **Notifications**: Alert team of build failures
7. **Versioning**: Tag builds with version numbers
8. **Rollback**: Have strategy to rollback failed deployments


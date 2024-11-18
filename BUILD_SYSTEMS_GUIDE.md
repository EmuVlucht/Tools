# ADB Integration with Build Systems

## 1. Gradle Build System

### Custom ADB Tasks
```gradle
android {
    defaultConfig {
        applicationId "com.example.app"
    }
}

task installDebugOnDevice {
    dependsOn 'assembleDebug'
    doLast {
        exec {
            commandLine 'adb', 'install', '-r', 
                'build/outputs/apk/debug/app-debug.apk'
        }
    }
}

task runApp {
    dependsOn 'installDebugOnDevice'
    doLast {
        exec {
            commandLine 'adb', 'shell', 'am', 'start', '-n',
                'com.example.app/.MainActivity'
        }
    }
}

task collectLogs {
    doLast {
        exec {
            commandLine 'adb', 'logcat', '-d'
            standardOutput new File('logcat.txt').newOutputStream()
        }
    }
}
```

### Run Commands
```bash
./gradlew runApp              # Build, install, run
./gradlew installDebugOnDevice # Install only
./gradlew collectLogs         # Collect logs
```

---

## 2. Maven Build System

### pom.xml Configuration
```xml
<plugin>
    <groupId>com.jayway.maven.plugins.android.generation2</groupId>
    <artifactId>android-maven-plugin</artifactId>
    <version>4.6.2</version>
    <configuration>
        <sdk>
            <platform>33</platform>
        </sdk>
    </configuration>
    <executions>
        <execution>
            <id>deploy</id>
            <phase>pre-integration-test</phase>
            <goals>
                <goal>deploy</goal>
            </goals>
        </execution>
    </executions>
</plugin>

<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-failsafe-plugin</artifactId>
    <configuration>
        <systemPropertyVariables>
            <adb.device.id>emulator-5554</adb.device.id>
        </systemPropertyVariables>
    </configuration>
</plugin>
```

### Maven Commands
```bash
mvn clean install           # Build
mvn android:deploy         # Deploy APK
mvn verify                  # Run tests
```

---

## 3. Bazel Build System

### BUILD File
```python
android_binary(
    name = "app",
    manifest = "AndroidManifest.xml",
    srcs = glob(["java/**/*.java"]),
    resource_files = glob(["res/**/*"]),
    deps = [
        "//common:utils",
    ],
)

genrule(
    name = "install",
    srcs = [":app"],
    outs = ["install.log"],
    cmd = "adb install -r $(location :app) > $@",
)
```

### Build Commands
```bash
bazel build //:app                  # Build
bazel run //:install               # Install
bazel test //:tests --test_arg=adb # Test
```

---

## 4. Buck Build System

### BUCK File
```python
android_binary(
    name = 'app',
    manifest = 'AndroidManifest.xml',
    target = 'android-33',
    srcs = glob(['src/**/*.java']),
    deps = [
        '//libs:common',
    ],
)

android_instrumentation_tests(
    name = 'tests',
    apk = ':app',
    test_apk = ':test_apk',
)
```

### Build Commands
```bash
buck build app              # Build APK
buck install app           # Install APK
buck test //:tests         # Run tests
```

---

## 5. CMake Integration

### CMakeLists.txt
```cmake
cmake_minimum_required(VERSION 3.0.0)
project(MyApp)

# Find ADB
find_program(ADB_EXECUTABLE adb)

if(NOT ADB_EXECUTABLE)
    message(FATAL_ERROR "ADB not found")
endif()

# Custom commands
add_custom_target(install_app
    COMMAND ${ADB_EXECUTABLE} install -r ${CMAKE_BINARY_DIR}/app.apk
    COMMENT "Installing APK..."
)

add_custom_target(run_app
    COMMAND ${ADB_EXECUTABLE} shell am start -n com.example.app/.MainActivity
    COMMENT "Running app..."
)
```

---

## 6. Make Build System

### Makefile
```makefile
.PHONY: build install run test clean

APP_NAME = app
APK_PATH = build/outputs/apk/debug/$(APP_NAME)-debug.apk
DEVICE = emulator-5554

build:
	./gradlew assembleDebug

install: build
	adb -s $(DEVICE) install -r $(APK_PATH)

run: install
	adb -s $(DEVICE) shell am start -n com.example.app/.MainActivity

test:
	./gradlew connectedAndroidTest

logcat:
	adb -s $(DEVICE) logcat | grep com.example.app

clean:
	./gradlew clean
	adb -s $(DEVICE) uninstall com.example.app

all: build install run
```

### Usage
```bash
make build          # Just build
make install        # Build and install
make run           # Build, install, run
make test          # Run tests
```

---

## 7. Composite Builds

### Multi-Module Gradle
```gradle
// settings.gradle
include ':app'
include ':library'

// app/build.gradle
android {
    dependencies {
        implementation project(':library')
    }
}

task deployAll {
    dependsOn ':app:assembleDebug', ':app:installDebugOnDevice'
}
```

---

## 8. Build Profiles

### Different Configurations
```gradle
android {
    buildTypes {
        debug {
            applicationIdSuffix ".debug"
            debuggable true
        }
        release {
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'),
                'proguard-rules.pro'
        }
    }
    
    flavorDimensions "environment"
    productFlavors {
        dev {
            dimension "environment"
        }
        staging {
            dimension "environment"
        }
        prod {
            dimension "environment"
        }
    }
}

// Install specific flavor
task installDevDebug {
    dependsOn 'assembleDevDebug'
    doLast {
        exec {
            commandLine 'adb', 'install', '-r',
                'build/outputs/apk/dev/debug/app-dev-debug.apk'
        }
    }
}
```

---

## 9. Build Variants

### Select Specific Variant
```bash
# Build specific variant
./gradlew assembleDevDebug              # Dev + Debug
./gradlew assembleStagingRelease       # Staging + Release

# Install and run specific variant
./gradlew installDevDebugOnDevice

# List available variants
./gradlew tasks | grep -i install
```

---

## 10. Automated Build Pipeline

### Complete Build Script
```bash
#!/bin/bash
# build_and_deploy.sh

VERSION=$1
FLAVOR=${2:-dev}

echo "Building $FLAVOR v$VERSION..."

# Build
./gradlew clean assemble${Flavor^}Debug

if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi

# Get APK path
APK_PATH="build/outputs/apk/${FLAVOR,,}/debug/app-${FLAVOR,,}-debug.apk"

if [ ! -f "$APK_PATH" ]; then
    echo "APK not found: $APK_PATH"
    exit 1
fi

# Deploy to devices
DEVICES=$(adb devices | grep device | grep -v List | awk '{print $1}')

for device in $DEVICES; do
    echo "Deploying to $device..."
    adb -s "$device" install -r "$APK_PATH"
done

echo "✓ Build v$VERSION ($FLAVOR) deployed successfully!"
```


# Gradle Build Configuration & ADB Integration

## 1. Basic Build Configuration

```gradle
android {
    compileSdk 34
    
    defaultConfig {
        applicationId "com.example.app"
        minSdk 21
        targetSdk 34
        versionCode 100
        versionName "1.0.0"
    }
    
    buildTypes {
        release {
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
            signingConfig signingConfigs.release
        }
    }
}
```

## 2. Custom ADB Tasks

```gradle
task adbInstall {
    doLast {
        exec {
            commandLine 'adb', 'install', '-r', 'app/build/outputs/apk/debug/app-debug.apk'
        }
    }
}

task adbUninstall {
    doLast {
        exec {
            commandLine 'adb', 'uninstall', 'com.example.app'
        }
    }
}

task adbRun {
    dependsOn 'assembleDebug', 'adbInstall'
    doLast {
        exec {
            commandLine 'adb', 'shell', 'am', 'start', '-n', 'com.example.app/.MainActivity'
        }
    }
}
```

## 3. Multi-Device Testing

```gradle
task adbTestAll {
    doLast {
        def devices = "adb devices".execute().text.split('\n').grep { it.contains('\t') }
        devices.each { device ->
            def deviceId = device.split('\t')[0]
            exec {
                commandLine 'adb', '-s', deviceId, 'install', '-r', 'app-debug.apk'
            }
            exec {
                commandLine 'adb', '-s', deviceId, 'shell', 'am', 'start', '-n', 'com.example.app/.MainActivity'
            }
        }
    }
}
```

## 4. Build Variants

```gradle
flavorDimensions "store", "version"

productFlavors {
    google {
        dimension "store"
    }
    samsung {
        dimension "store"
    }
    free {
        dimension "version"
        versionNameSuffix "-free"
    }
    premium {
        dimension "version"
    }
}
```

## 5. ADB Port Forwarding

```gradle
task adbForward {
    doLast {
        exec {
            commandLine 'adb', 'forward', 'tcp:8888', 'tcp:8080'
        }
    }
}

task adbReverseForward {
    doLast {
        exec {
            commandLine 'adb', 'reverse', 'tcp:3000', 'tcp:3000'
        }
    }
}
```

## 6. Automated Testing

```gradle
task runTests {
    dependsOn 'assembleDebugAndroidTest'
    doLast {
        exec {
            commandLine 'adb', 'shell', 'am', 'instrument', '-w', 
                'com.example.test/androidx.test.runner.AndroidJUnitRunner'
        }
    }
}
```


# Video Recording & Media Manipulation via ADB

## 1. Screen Recording

### Basic Screen Recording
```bash
# Record screen (30 seconds default)
adb shell screenrecord /sdcard/video.mp4

# Custom duration (up to 180 seconds)
adb shell screenrecord --time-limit=60 /sdcard/video.mp4

# With bit rate
adb shell screenrecord --bit-rate=8000000 /sdcard/video.mp4

# With resolution
adb shell screenrecord --size=1280x720 /sdcard/video.mp4

# Full command
adb shell screenrecord \
    --size=1920x1080 \
    --bit-rate=20000000 \
    --time-limit=120 \
    /sdcard/demo.mp4

# Stop recording (Ctrl+C) or wait for timeout
```

### Pull Video File
```bash
# After recording, pull the file
adb pull /sdcard/video.mp4 ./

# Check file size
adb shell ls -lh /sdcard/video.mp4

# Delete on device
adb shell rm /sdcard/video.mp4
```

### Recording with Device Info
```bash
#!/bin/bash
# record_with_metadata.sh

DURATION=${1:-60}
OUTPUT="recording_$(date +%Y%m%d_%H%M%S).mp4"

echo "Recording $DURATION seconds to $OUTPUT"

adb shell screenrecord \
    --size=1920x1080 \
    --bit-rate=20000000 \
    --time-limit=$DURATION \
    /sdcard/temp.mp4

adb pull /sdcard/temp.mp4 "$OUTPUT"
adb shell rm /sdcard/temp.mp4

echo "✓ Saved to: $OUTPUT"
```

---

## 2. Screenshot Management

### Take Screenshots
```bash
# Screenshot (saved as PNG)
adb shell screencap -p /sdcard/screenshot.png

# Without line endings (for binary)
adb shell screencap /sdcard/screenshot.png

# Multiple screenshots
for i in {1..5}; do
    adb shell screencap /sdcard/screenshot_$i.png
    sleep 2
done

# Pull all
adb pull /sdcard/screenshot_*.png ./
```

### Screenshot Automation
```bash
#!/bin/bash
# automated_screenshots.sh

DEVICE=$1
INTERVAL=${2:-5}
COUNT=${3:-10}

for i in $(seq 1 $COUNT); do
    echo "[$i/$COUNT] Screenshot at $(date)"
    adb -s "$DEVICE" shell screencap "/sdcard/screen_$i.png"
    sleep $INTERVAL
done

adb -s "$DEVICE" pull /sdcard/screen_*.png ./

echo "✓ Collected $COUNT screenshots"
```

---

## 3. Video Playback Verification

### Test Video Playback
```bash
# Push video to device
adb push video.mp4 /sdcard/

# Open with default player
adb shell am start -a android.intent.action.VIEW \
    -d file:///sdcard/video.mp4 \
    -t video/mp4

# Open with specific app
adb shell am start -a android.intent.action.VIEW \
    -n com.mxtech.videoplayer/.ActivityScreen \
    -d file:///sdcard/video.mp4
```

---

## 4. Photo & Image Management

### Transfer Images
```bash
# Pull all photos from DCIM
adb pull /sdcard/DCIM/Camera/ ./photos/

# Pull specific image
adb pull /sdcard/DCIM/Camera/IMG_001.jpg ./

# Push image
adb push photo.jpg /sdcard/Pictures/

# Organize images
adb shell mkdir -p /sdcard/Pictures/Organized
adb shell mv /sdcard/Pictures/*.jpg /sdcard/Pictures/Organized/
```

### Image Conversion
```bash
#!/bin/bash
# convert_images.sh

# Pull images
adb pull /sdcard/DCIM/Camera/ ./raw_photos/

# Convert with ImageMagick
for img in raw_photos/*.jpg; do
    convert "$img" -quality 85 "${img%.jpg}_compressed.jpg"
done

# Push back
adb push compressed_photos/* /sdcard/Pictures/
```

---

## 5. Audio Recording

### Record Audio
```bash
# Record audio from microphone
adb shell "recorder /sdcard/audio.m4a"

# Or using mediarecorder
adb shell am start -n com.android.soundrecorder/.SoundRecorder

# For some devices, use:
adb shell "mediarecorder -o /sdcard/recording.aac"
```

### Audio Playback
```bash
# Play audio file
adb shell am start -a android.intent.action.VIEW \
    -d file:///sdcard/music.mp3 \
    -t audio/mpeg

# Play using specific app
adb shell am start -n com.android.music/.MusicBrowserActivity \
    -d file:///sdcard/music.mp3
```

---

## 6. Video Editing & Processing

### Extract Frames from Video
```bash
#!/bin/bash
# extract_frames.sh

VIDEO_FILE=$1

adb pull "/sdcard/$VIDEO_FILE" ./

# Extract frames using ffmpeg
ffmpeg -i "$VIDEO_FILE" -vf fps=1/5 frame_%04d.jpg

# Upload back
adb push frame_*.jpg /sdcard/Frames/
```

### Create Video from Images
```bash
#!/bin/bash
# images_to_video.sh

# Pull images
adb pull /sdcard/DCIM/Camera/ ./images/

# Create video from images
ffmpeg -framerate 24 -i images/IMG_%04d.jpg \
    -c:v libx264 -pix_fmt yuv420p \
    output_video.mp4

# Push back
adb push output_video.mp4 /sdcard/Videos/
```

---

## 7. Live Stream Recording

### Stream Device Screen to Computer
```bash
#!/bin/bash
# stream_device_screen.sh

# Enable screen mirroring
adb shell screenrecord --output-format=h264 - | \
    ffmpeg -i pipe:0 -c:v libx264 -preset veryfast \
    -f flv rtmp://localhost/live/stream

# Or using scrcpy (if installed)
scrcpy --record=video.mp4 --size=1280x720
```

---

## 8. Screenshot Comparison

### Compare Screenshots Over Time
```bash
#!/bin/bash
# screenshot_diff.sh

# Take baseline
adb shell screencap /sdcard/baseline.png
adb pull /sdcard/baseline.png ./baseline.png

# Wait and take new screenshot
sleep 10
adb shell screencap /sdcard/current.png
adb pull /sdcard/current.png ./current.png

# Compare
compare baseline.png current.png diff.png

# View diff
feh diff.png
```

---

## 9. Video Format Conversion

### Convert Video Formats
```bash
#!/bin/bash
# convert_video.sh

INPUT=$1
OUTPUT="${INPUT%.*}.mp4"

# Pull video
adb pull "/sdcard/$INPUT" ./

# Convert with ffmpeg
ffmpeg -i "$INPUT" -c:v libx264 -crf 23 -c:a aac -b:a 192k "$OUTPUT"

# Compress
ffmpeg -i "$INPUT" -vf scale=1280:720 -c:v libx264 -crf 28 -c:a aac "$OUTPUT"

# Push back
adb push "$OUTPUT" "/sdcard/Videos/"
```

---

## 10. Animated GIF Creation

### Create GIF from Video
```bash
#!/bin/bash
# video_to_gif.sh

VIDEO_FILE=$1

adb pull "/sdcard/$VIDEO_FILE" ./

# Extract frames
ffmpeg -i "$VIDEO_FILE" -vf fps=10 frame_%04d.png

# Create GIF
convert -delay 10 -loop 0 frame_*.png output.gif

# Compress GIF
gifsicle -O3 output.gif -o output_optimized.gif

# Push back
adb push output_optimized.gif /sdcard/
```

---

## 11. Video Metadata

### Extract Metadata
```bash
# Get video properties
adb pull /sdcard/video.mp4 ./

# Extract metadata with ffprobe
ffprobe -show_format -show_streams video.mp4

# Extract specific info
ffprobe -v error -select_streams v:0 \
    -show_entries stream=width,height,duration \
    -of default=noprint_wrappers=1:nokey=1:nokey_sep=\= \
    video.mp4
```

### Modify Video Metadata
```bash
# Add metadata
ffmpeg -i input.mp4 \
    -metadata title="My Video" \
    -metadata artist="Developer" \
    -metadata date="2025" \
    -c copy output.mp4

# Push back
adb push output.mp4 /sdcard/Videos/
```

---

## 12. Batch Media Operations

### Batch Processing Script
```bash
#!/bin/bash
# batch_media_process.sh

echo "Processing media files..."

# Create directories
adb shell mkdir -p /sdcard/ProcessedMedia
adb shell mkdir -p /sdcard/Backup

# Backup original files
adb shell "cp /sdcard/DCIM/Camera/*.jpg /sdcard/Backup/"

# Process images
for img in /sdcard/DCIM/Camera/*.jpg; do
    filename=$(basename "$img")
    adb shell "convert $img -resize 1920x1080 /sdcard/ProcessedMedia/$filename"
done

# Compress videos
for video in /sdcard/Videos/*.mp4; do
    filename=$(basename "$video")
    adb shell "ffmpeg -i $video -c:v libx264 -crf 25 /sdcard/ProcessedMedia/$filename"
done

echo "✓ Processing complete"
```

---

## 13. Performance Optimization

### Optimize Video Recording
```bash
# Lower quality for better performance
adb shell screenrecord \
    --size=1280x720 \
    --bit-rate=5000000 \
    --time-limit=60 \
    /sdcard/video_low_quality.mp4

# High quality (requires more CPU)
adb shell screenrecord \
    --size=2560x1440 \
    --bit-rate=50000000 \
    --time-limit=30 \
    /sdcard/video_4k.mp4
```

---

## 14. Storage Management

### Check Media Storage
```bash
# Total storage
adb shell df /sdcard/

# Media folder sizes
adb shell du -sh /sdcard/DCIM/
adb shell du -sh /sdcard/Videos/
adb shell du -sh /sdcard/Pictures/

# Find large files
adb shell find /sdcard -type f -size +100M -exec ls -lh {} \;
```

### Clean Up Old Media
```bash
#!/bin/bash
# cleanup_old_media.sh

DAYS=30

# Delete old videos
adb shell find /sdcard/Videos -type f -mtime +$DAYS -delete

# Delete old screenshots
adb shell find /sdcard/Pictures -type f -name "screenshot*" -mtime +7 -delete

# Delete old recordings
adb shell find /sdcard -name "*.mp4" -mtime +$DAYS -delete

echo "✓ Cleanup complete"
```

---

## 15. Advanced Media Features

### Create Split-Screen Video
```bash
# Combine two videos
ffmpeg -i input1.mp4 -i input2.mp4 -filter_complex \
    "[0:v]pad=iw*2:ih[bg];[bg][1:v]overlay=w" \
    output.mp4

# Push to device
adb push output.mp4 /sdcard/Videos/
```

### Add Subtitles to Video
```bash
# Add SRT subtitles
ffmpeg -i video.mp4 -i subtitles.srt \
    -c:s mov_text output.mp4

# Push to device
adb push output.mp4 /sdcard/Videos/
```


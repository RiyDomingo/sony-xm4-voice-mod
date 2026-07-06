#!/bin/bash
set -e

# Accept volume as first parameter, default to 0.30
VOLUME=${1:-0.30}
# Accept language code suffix (XX of VGIDLPB04XX) as second parameter, default to 06 (portuguese)
LANG_CODE=${2:-06}

case "$LANG_CODE" in
  01) LANG_NAME="english" ;;
  02) LANG_NAME="french" ;;
  03) LANG_NAME="german" ;;
  04) LANG_NAME="spanish" ;;
  05) LANG_NAME="italian" ;;
  06) LANG_NAME="portuguese" ;;
  07) LANG_NAME="dutch" ;;
  08) LANG_NAME="swedish" ;;
  09) LANG_NAME="finnish" ;;
  10) LANG_NAME="turkish" ;;
  *) echo "Error: Invalid language code suffix $LANG_CODE (must be 01-10)"; exit 1 ;;
esac

echo "=== Quiet Sony WH-1000XM4 Voice Guidance Pack Generator ==="
echo "Target volume amplitude: $VOLUME"
echo "Target language:         $LANG_NAME (VGIDLPB04$LANG_CODE)"

# 1. Check dependencies
echo "Checking dependencies..."
MISSING=0
for cmd in uv ffmpeg curl mitmdump; do
    if ! command -v $cmd &> /dev/null; then
        echo "Error: '$cmd' is not installed or not in PATH."
        MISSING=1
    fi
done

if [ $MISSING -eq 1 ]; then
    echo "Please install the missing tools and try again."
    echo "On macOS, you can install them using Homebrew:"
    echo "  brew install ffmpeg mitmproxy"
    exit 1
fi
echo "All dependencies (uv, ffmpeg, curl, mitmdump) are present."

# 2. Create required folders
echo "Creating folders..."
mkdir -p voice-packs
mkdir -p slots
mkdir -p quiet_slots

# 3. Download the official voice packs and info files if not already cached
if [ ! -f "voice-packs/VP_english_UPG_03.bin" ]; then
    echo "Downloading English source voice pack..."
    curl -fsSL -o voice-packs/VP_english_UPG_03.bin \
      https://info.update.sony.net/HP002/VGIDLPB0401/contents/0002/VP_english_UPG_03.bin
else
    echo "English source voice pack already cached."
fi

if [ ! -f "voice-packs/VP_${LANG_NAME}_UPG_03.bin" ]; then
    echo "Downloading $LANG_NAME target voice pack..."
    curl -fsSL -o "voice-packs/VP_${LANG_NAME}_UPG_03.bin" \
      "https://info.update.sony.net/HP002/VGIDLPB04${LANG_CODE}/contents/0002/VP_${LANG_NAME}_UPG_03.bin"
else
    echo "$LANG_NAME target voice pack already cached."
fi

if [ ! -f "info_english.bin" ]; then
    echo "Downloading English manifest (info.xml) template..."
    curl -fsSL -o info_english.bin \
      https://info.update.sony.net/HP002/VGIDLPB0401/info/info.xml
else
    echo "English manifest template already cached."
fi

# 4. Extract all English slots
echo "Extracting English voice guidance slots..."
rm -f slots/slot_*.mp3
uv run extract_slots.py voice-packs/VP_english_UPG_03.bin slots/

# 5. Create quiet replacements for every extracted slot
echo "Modifying slot volumes to $VOLUME amplitude..."
rm -f quiet_slots/slot_*.mp3

EXTRACTED_COUNT=0
CONVERTED_COUNT=0

for file in slots/slot_*.mp3; do
    if [ -f "$file" ]; then
        EXTRACTED_COUNT=$((EXTRACTED_COUNT + 1))
        filename=$(basename "$file")
        quiet_file="quiet_slots/$filename"
        
        # Programmatically detect the original bitrate of the slot
        bitrate_bps=$(ffprobe -v error -show_entries stream=bit_rate -of default=noprint_wrappers=1:nokey=1 "$file" || echo "")
        if [[ ! "$bitrate_bps" =~ ^[0-9]+$ ]]; then
            bitrate_kbps=64
        else
            bitrate_kbps=$((bitrate_bps / 1000))
        fi
        
        # Apply volume reduction and match original properties (mono, 48kHz, original bitrate)
        # Strip metadata to minimize size overhead
        ffmpeg -y -i "$file" \
            -af "volume=${VOLUME}" \
            -ar 48000 \
            -ac 1 \
            -b:a "${bitrate_kbps}k" \
            -map_metadata -1 \
            -id3v2_version 0 \
            -write_xing 0 \
            "$quiet_file" 2>/dev/null
        
        if [ -f "$quiet_file" ]; then
            CONVERTED_COUNT=$((CONVERTED_COUNT + 1))
        fi
    fi
done

echo "Extracted $EXTRACTED_COUNT English slots, successfully converted $CONVERTED_COUNT to volume=$VOLUME."

if [ "$EXTRACTED_COUNT" -ne "$CONVERTED_COUNT" ]; then
    echo "Warning: Mismatch between extracted slots and converted slots!"
fi

# 6. Build the patched target-slot voice pack using all quiet English replacement slots
echo "Building patched $LANG_NAME-slot voice pack (patched.bin)..."
mp3_args=()
for file in quiet_slots/slot_*.mp3; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        slot_str=${filename#slot_}
        slot_str=${slot_str%.mp3}
        slot_num=$((10#$slot_str))
        mp3_args+=( "--mp3" "$slot_num=$file" )
    fi
done

# We run pack_voice_pack.py using the target lang bin as our base input
# and we overwrite all slots with the quiet English ones. We also pass --replace ""
# to prevent the default behavior of swapping slots 6/7/8 with default chimes.
uv run pack_voice_pack.py "voice-packs/VP_${LANG_NAME}_UPG_03.bin" patched.bin --replace "" "${mp3_args[@]}"

# 7. Build the patched info XML for the target language
echo "Building the patched $LANG_NAME manifest XML (patched_info.xml)..."
uv run pack_info_xml.py info_english.bin patched.bin \
  --lang-pack "VGIDLPB04${LANG_CODE}" --rewrite-lang \
  --out patched_info.xml

echo "=== Generation Complete for volume=$VOLUME in $LANG_NAME! ==="
echo "Patched Voice Pack: patched.bin"
echo "Patched Manifest:   patched_info.xml"

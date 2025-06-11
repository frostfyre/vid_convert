#!/bin/bash

MOV_DIR="${1:-.}"  # Set directory (default: current)
TOTAL_FRAMES=0

for file in "$MOV_DIR"/*.mov; do
    if [ -f "$file" ]; then
        FRAME_COUNT=$(ffmpeg -i "$file" -map 0:v:0 -c copy -f null - 2>&1 | grep "frame=" | awk '{print $2}')

        # Ensure valid frame count before adding
        if [[ "$FRAME_COUNT" =~ ^[0-9]+$ ]]; then
            TOTAL_FRAMES=$((TOTAL_FRAMES + FRAME_COUNT))
            echo "File: $file | Frames: $FRAME_COUNT"
        else
            echo "Error: Could not determine frame count for $file"
        fi
    fi
done

echo "**Total Combined Frames:** $TOTAL_FRAMES"

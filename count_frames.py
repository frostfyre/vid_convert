import os
import subprocess

def get_frame_count(file_path):
    """Returns the total number of frames in a .mov file using FFmpeg."""
    cmd = [
        "ffmpeg", "-i", file_path, "-map", "0:v:0", "-c", "copy", "-f", "null", "-"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Extract frame count from FFmpeg output
    for line in result.stderr.split("\n"):
        if "frame=" in line:
            try:
                return int(line.split("frame=")[1].split()[0])
            except ValueError:
                pass

    return 0  # Return 0 if frame count could not be determined

def calculate_total_frames(directory):
    """Calculates the total frame count for all .mov files in the specified directory."""
    total_frames = 0
    # recursicely find all .mov files in the directory
    mov_files = [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.endswith('.mov')]
    print(f"Found {len(mov_files)} .mov files to process.")
    for file in mov_files:
        print(f"Processing {file}")
        frame_count = get_frame_count(file)

        if frame_count > 0:
            print(f"File: {file} | Frames: {frame_count}")
            total_frames += frame_count
        else:
            print(f"Error: Could not determine frame count for {file}")

    print(f"**Total Combined Frames:** {total_frames}")

# Example usage: Change directory path if needed
directory = '/mnt/data-local/LA-June/Body'
calculate_total_frames(directory)

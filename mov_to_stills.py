import subprocess
import os
from multiprocessing import Pool

input_file = "input.mov"
output_dir = "frames_avif"
os.makedirs(output_dir, exist_ok=True)

# Get total frames
cmd_frame_count = [
    "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
    "stream=nb_frames", "-of", "default=nokey=1:noprint_wrappers=1", input_file
]
total_frames = int(subprocess.run(cmd_frame_count, capture_output=True, text=True).stdout.strip())

def extract_frame(i):
    output_file = os.path.join(output_dir, f"frame_{i:04d}.avif")
    cmd_extract = [
        "ffmpeg", "-i", input_file, "-vf",
        f"select='eq(n,{i})',colorspace=bt709",
        "-vsync", "vfr", "-pix_fmt", "yuv420p", "-quality", "50", output_file
    ]
    subprocess.run(cmd_extract, check=True)

# Use multiprocessing pool
with Pool(os.cpu_count()) as pool:
    pool.map(extract_frame, range(total_frames))

print("Parallel frame extraction complete.")


# let's make this a CLI tool that can be run with a single command
# Usage: python mov_to_stills.py input.mov output_dir

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python mov_to_stills.py input.mov output_dir")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    cmd_frame_count = [
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
        "stream=nb_frames", "-of", "default=nokey=1:noprint_wrappers=1", input_file
    ]
    total_frames = int(subprocess.run(cmd_frame_count, capture_output=True, text=True).stdout.strip())

    with Pool(os.cpu_count()) as pool:
        pool.map(extract_frame, range(total_frames))

    print("Parallel frame extraction complete.")
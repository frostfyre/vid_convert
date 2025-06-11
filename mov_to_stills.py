import subprocess
import os

input_file = '/mnt/data-local/LA-June/Body/001001_C025/001001_06051714_C025.mov'
output_dir = "./001001_C025-frames"
os.makedirs(output_dir, exist_ok=True)

frame_num = 0

while True:
    output_file = os.path.join(output_dir, f"{os.path.basename(input_file)}-{frame_num:04d}.avif")

    cmd = [
        "ffmpeg", "-i", input_file, "-vf",
        f"select='eq(n,{frame_num})',colorspace=bt709",
        "-vsync", "vfr", "-pix_fmt", "yuv420p", "-quality", "50", output_file,
        "-y"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Check if FFmpeg failed (end of file or error)
    if result.returncode != 0:
        print(f"Stopping at frame {frame_num} - FFmpeg could not read further.")
        break

    print(f"Extracted frame {frame_num} as AVIF")
    frame_num += 1

print("Frame extraction complete.")

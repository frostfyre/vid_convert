import subprocess
import os
from multiprocessing import Pool
# This script extracts frames from a ProRes .mov file and saves them as AVIF images.


def extract_frames_avif(input_file, output_dir):
    """ Extract frames from a ProRes .mov file and save as AVIF images. """
    os.makedirs(output_dir, exist_ok=True)
    basename = str(os.path.basename(input_file)).split('.')[0]
    frame_num = 0
    while True:
        output_file = os.path.join(output_dir, f"{basename}-{frame_num:04d}.avif")
        if os.path.exists(output_file):
            print(f"Skipping frame {frame_num} (already processed) for {input_file}")
            frame_num += 1
            continue
        cmd = [
            "ffmpeg", "-hwaccel cuda", "-i", input_file, "-vf",
            f"select='eq(n,{frame_num})',colorspace=bt709",
            "-vsync", "vfr", "-pix_fmt", "yuv420p", "-quality", "50", output_file,
            "-y"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Stop when FFmpeg fails to extract a frame
        if result.returncode != 0:
            print(f"Stopping at frame {frame_num} for {input_file} - End of file reached.")
            break

        print(f"Extracted frame {frame_num} from {input_file}")
        frame_num += 1

    print(f"Frame extraction complete for {input_file}")

def process_multiple_files(input_files):
    """ Run frame extraction on multiple files in parallel. """
    with Pool(os.cpu_count()) as pool:
        pool.starmap(extract_frames_avif, [(file, f"/mnt/data/datasets/LA-June-frames/{os.path.splitext(os.path.basename(file))[0]}") for file in input_files])


if __name__ == "__main__":
    # Example usage: Process a single .mov file
    source = '/mnt/data-local/LA-June/Body'
    # recusrsively find all .mov files in the source directory
    input_files= [os.path.join(root, file) for root, _, files in os.walk(source) for file in files if file.endswith('.mov')]
    print(f"Found {len(input_files)} .mov files to process.")
    process_multiple_files(input_files)


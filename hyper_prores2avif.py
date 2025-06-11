import os
import subprocess
import multiprocessing
from multiprocessing import Pool

# Explicitly set the multiprocessing start method to 'spawn'
multiprocessing.set_start_method("spawn", force=True)

def extract_frame(frame_num, input_file, output_dir):
    """ Extracts a single frame as AVIF, skipping if already processed. """
    os.makedirs(output_dir, exist_ok=True)
    basename = str(os.path.basename(input_file)).split('.')[0]
    output_file = os.path.join(output_dir, f"{basename}-{frame_num:04d}.avif")

    if os.path.exists(output_file):
        print(f"Skipping frame {frame_num} (already processed) for {input_file}")
        return

    cmd = [
        "ffmpeg", "-hwaccel cuda", "-i", input_file, "-vf",
        f"select='eq(n,{frame_num})',colorspace=bt709",
        "-vsync", "vfr", "-pix_fmt", "yuv420p", "-quality", "50", output_file,
        "-y"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Stopping at frame {frame_num} for {input_file} (end of file reached)")
        return

    print(f"Extracted frame {frame_num} from {input_file}")


def extract_frames_parallel(input_file):
    """ Extracts all frames from an input file in parallel, skipping existing frames. """
    output_dir = f"/mnt/data/datasets/LA-June-frames/{os.path.splitext(os.path.basename(input_file))[0]}"
    os.makedirs(output_dir, exist_ok=True)

    num_workers = min(os.cpu_count(), 120)
    frame_numbers = range(150000)  # Arbitrary large number, stops when FFmpeg fails

    with Pool(num_workers) as pool:
        pool.starmap(extract_frame, [(frame_num, input_file, output_dir) for frame_num in frame_numbers])

    # Use spawn method for multiprocessing compatibility
    with Pool(num_workers) as pool:
        pool.starmap(extract_frame, [(frame_num, input_file, output_dir) for frame_num in frame_numbers])


def process_multiple_files(input_files):
    """ Process multiple MOV files in parallel, each extracting frames in parallel. """
    with multiprocessing.Pool(len(input_files)) as pool:
        pool.map(extract_frames_parallel, input_files)

if __name__ == "__main__":
    # Example usage: Process a list of .mov files, ALLOW USER TO SUPPLY A FOLDER FULL OF MOV FILES

    import argparse
    parser = argparse.ArgumentParser(description="Extract frames from ProRes .mov files and save as AVIF images.")
    parser.add_argument('input_folder', type=str, help='Folder containing ProRes .mov files')
    args = parser.parse_args()
    input_folder = args.input_folder
    # recursively find all .mov files in the input folder
    if not os.path.exists(input_folder):
        print(f"Input folder does not exist: {input_folder}")
        exit(1)
    if not os.path.isdir(input_folder):
        print(f"Input path is not a directory: {input_folder}")
        exit(1)
    print(f"Searching for .mov files in {input_folder}...")
    input_files= [os.path.join(root, file) for root, _, files in os.walk(input_folder) for file in files if file.endswith('.mov')]

    if not input_files:
        print(f"No .mov files found in {input_folder}")
    else:
        print(f"Found {len(input_files)} .mov files to process.")
        process_multiple_files(input_files)
        print("All frames extraction complete.")
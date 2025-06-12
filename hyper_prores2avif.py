import os
import subprocess
import multiprocessing
import time
import logging

# Configure logging
logging.basicConfig(
    filename="avif_extraction.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Ensure proper multiprocessing start method
multiprocessing.set_start_method("spawn", force=True)

def extract_frames(input_file):

    """ Extract frames from an input file as AVIF, tracking estimated time. """
    output_dir = f"/mnt/data/datasets/LA-June-frames/{os.path.splitext(os.path.basename(input_file))[0]}"
    os.makedirs(output_dir, exist_ok=True)
    basename = str(os.path.basename(input_file)).split('.')[0]
    frame_num = 0
    start_time = time.time()

    while True:
        output_file = os.path.join(output_dir, f"{basename}-{frame_num:04d}.avif")
        if os.path.exists(output_file):
            logging.info(f"Skipping frame {frame_num} (already processed) for {input_file}")
            frame_num += 1
            continue

        cmd = [
            "ffmpeg", "-hwaccel cuda", "-i", input_file, "-vf",
            f"select='eq(n,{frame_num})',colorspace=bt709",
            "-vsync", "vfr", "-pix_fmt", "yuv420p", "-quality", "50", output_file,
            "-y"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logging.warning(f"EOF:\t{frame_num}\t{input_file}")
            break

        elapsed_time = time.time() - start_time
        avg_time_per_frame = elapsed_time / (frame_num + 1)
        estimated_remaining_time = avg_time_per_frame * (150000 - frame_num)

        logging.info(f"Extracted frame {frame_num} from {input_file} | Est. Remaining Time: {estimated_remaining_time:.2f} sec")

        frame_num += 1

    total_time = time.time() - start_time
    logging.info(f"Frame extraction complete for {input_file} | Total Time: {total_time:.2f} sec")

def process_multiple_files(input_files):
    """ Process multiple MOV files in parallel, tracking time per file. """
    processes = []

    for input_file in input_files:
        print(f"Processing {input_file}")
        p = multiprocessing.Process(target=extract_frames, args=(input_file,))
        p.start()
        processes.append(p)

    for p in processes:
        # report progress every 10 seconds
        while p.is_alive():
            time.sleep(10)
            logging.info(f"Process {p.name} is still running...")
        p.join()



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

# verify output
# This script verifies the output of the process_mp4.py script by checking if the frames have been extracted and converted to AVIF format.
# if any PNG files are found, it will also check if the corresponding AVIF files exist.

import os
import sys
import logging
import cv2
from process_mp4 import convert_png_to_avif, get_all_pngs, get_all_avifs

# Set up logging
logging.basicConfig(filename='verify_output.log', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler('verify_output.log'))
logger.addHandler(logging.StreamHandler(sys.stdout))


def seek_frame_and_convert(mp4_file, frame_number):
    """Seek to a specific frame in the mp4 file and convert it to PNG."""
    if not os.path.exists(mp4_file):
        logger.error(f'MP4 file not found: {mp4_file}')
        return

    vidcap = cv2.VideoCapture(mp4_file)
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    success, image = vidcap.read()
    if not success:
        logger.error(f'Failed to read frame {frame_number} from {mp4_file}')
        return

    # Save the frame as PNG
    png_path = mp4_file.replace('.mp4', f'-{frame_number}.png')
    cv2.imwrite(png_path, image)
    logger.info(f'Saved frame {frame_number} from {mp4_file} as {png_path}')


# compare if mp4_path from LA-data has corresponding frames in LA-data-frames

def verify_frames(mp4_path):
    """Verify if the frames extracted from the mp4 file exist in the frames folder."""
    frames_path = os.path.dirname(mp4_path.replace('/LA-data/', '/LA-data-frames/'))
    if not os.path.exists(frames_path):
        logger.error(f'Frames path not found: {frames_path}')
        return False

    camera = mp4_path.split('/')[-1].split('-')[0]
    pose = mp4_path.split('/')[-2]
    model = mp4_path.split('/')[-3]

    # Check for PNG files
    png_files = get_all_pngs(os.path.join(frames_path, camera))
    if not png_files:
        logger.warning(f'No PNG files found for camera {camera} in {frames_path}')
        return False

    # Check for corresponding AVIF files
    avif_files = get_all_avifs(os.path.join(frames_path, camera))
    if not avif_files:
        logger.warning(f'No AVIF files found for camera {camera} in {frames_path}')
        return False

    # Verify each PNG has a corresponding AVIF
    for png in png_files:
        avif_name = os.path.basename(png).replace('.png', '.avif')
        avif_path = os.path.join(frames_path, camera, avif_name)
        if not os.path.exists(avif_path):
            logger.error(f'Missing corresponding AVIF for {png}: {avif_path}')
            return False

    logger.info(f'All frames verified for {mp4_path}')
    return True

if __name__ == '__main__':
    #provide access to different functions based on args
    if len(sys.argv) < 2:
        logger.error('Please provide a folder to check, valid additional args include "png", "avif"')
        sys.exit(1)
    folder = sys.argv[1]
    if not os.path.exists(folder):
        logger.error(f'Folder not found: {folder}')
        sys.exit(1)
    if 'png' in sys.argv:
        png_files = get_all_pngs(folder)
        if png_files:
            logger.info(f'Found {len(png_files)} PNG files in {folder}')
            for png in png_files:
                print(f'trying to convert {png}')
                try:
                    convert_png_to_avif(png)
                except BaseException as e:
                    logger.error(f'Error converting {png} to AVIF:\n\t{e}')
                    pass
        else:
            logger.info(f'No PNG files found in {folder}')
    if 'avif' in sys.argv:
        avif_files = get_all_avifs(folder)
        if avif_files:
            logger.info(f'Found {len(avif_files)} AVIF files in {folder}')
        else:
            logger.info(f'No AVIF files found in {folder}')



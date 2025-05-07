# Script to go through AVIF frames and convert them to PNG
# renames the basename to include the camera number
# allows for a list of specific camera numbers, and a frame number

import os
import cv2
from PIL import Image
from pathlib import Path
import logging
import sys
import time


logging.basicConfig(filename='alt_frame_processing.log', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler('alt_frame_processing.log'))
logger.addHandler(logging.StreamHandler(sys.stdout))

def convert_avif_to_png(image_in):
    if not os.path.exists(image_in):
        logger.error(f'Image not found: {image_in}')
        return
    # convert image to PNG format
    if os.path.isfile(image_in):
        logger.debug(f'Converting {image_in} to PNG')
    im = Image.open(image_in)
    im.save(image_in.replace('.avif', '.png'), 'PNG')
    # remove the AVIF file
    os.remove(image_in)

def get_camera_number(mp4_path):
    # Extract the camera number from the mp4_path
    return mp4_path.split('/')[-1].split('-')[0]

def get_pose(mp4_path):
    # Extract the pose from the mp4_path
    return mp4_path.split('/')[-2]

def get_model(mp4_path):
    # Extract the model from the mp4_path
    return mp4_path.split('/')[-3]

def rename_frame(frame_path, camera_number):
    # Rename the frame file to include the camera number
    new_frame_path = f"{os.path.dirname(frame_path)}/{camera_number}_{os.path.basename(frame_path)}"
    os.rename(frame_path, new_frame_path)
    return new_frame_path

def process_frames(frames_root, camera_numbers, frame_number, out_dir):
    # for each camera folder in frames_root, find those avif files matching frame_number
    for camera_number in camera_numbers:
        camera_folder = os.path.join(frames_root, camera_number)
        if not os.path.exists(camera_folder):
            logger.warning(f'Camera folder not found: {camera_folder}')
            continue

        # look for avif files in the camera folder
        for root, dirs, files in os.walk(camera_folder):
            for file in files:
                if file.endswith('.avif') and f'-{frame_number}.' in file:
                    avif_path = os.path.join(root, file)
                    convert_avif_to_png(avif_path)
                    png_path = avif_path.replace('.avif', '.png')
                    renamed_frame_path = rename_frame(png_path, camera_number)
                    logger.info(f'Processed frame: {renamed_frame_path}')
                    # Move the renamed frame to out_dir
                    if not os.path.exists(out_dir):
                        os.makedirs(out_dir)
                    os.rename(renamed_frame_path, os.path.join(out_dir, os.path.basename(renamed_frame_path)))


if __name__ == '__main__':
    # Example usage
    frames_root = '/Users/spooky/Downloads/LA-data-frames/Model2/EXP_eye_neutral/'  # Root directory containing camera folders
    # frames_root = '/mnt/data/datasets/LA-data-frames/Model2/EXP_eye_neutral/'  # Root directory containing camera folders
    # camera_numbers = ['camera_01', 'camera_02', 'camera_03', 'camera_04',
    #                   'camera_08', 'camera_09','camera_10', 'camera_11',
    #                   'camera_12','camera_13','camera_14','camera_15',
    #                   'camera_16', 'camera_17', 'camera_24', 'camera_25',
    #                   'camera_26', 'camera_27','camera_29','camera_30',
    #                   'camera_35', 'camera_36','camera_37','camera_38',
    #                   'camera_39','camera_40', 'camera_49', 'camera_50',
    #                   'camera_51', 'camera_52','camera_53', 'camera_54',
    #                   'camera_60', 'camera_61', 'camera_62', 'camera_63',
    #                   'camera_68', 'camera_87', ]  # List of camera numbers to process 60-63
    # generate camera numbers from 01 to 87 as an array
    camera_numbers = [f'camera_{str(i).zfill(2)}' for i in range(1, 88)]

    frame_number = '00012'  # Frame number to look for
    # out_dir = '/Users/spooky/Developer/facebuilder/Auto-Only-Plugin/alt_source/'  # Directory to save processed frames
    out_dir = '/Users/spooky/modeling_frames/Model2/EXP_eye_neutral/'  # Directory to save processed frames
  # Directory to save processed frames

    process_frames(frames_root, camera_numbers, frame_number, out_dir)
    logger.info('Frame processing completed.')

# Radiant identified a bug in the frame numbering, and sent the table needed to repair these offsets.
# this script will use that table to correct the frame numbers in the LA-data-frames folder

import os
import sys
import logging
import pandas as pd
from datetime import datetime
from process_mp4 import convert_png_to_avif, get_all_pngs, get_all_avifs, pad_frame_number
from PIL import Image
import pillow_avif
from pathlib import Path
import cv2
import time


# Set up logging
logging.basicConfig(filename='frame_number_correction.log', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler('frame_number_correction.log'))
logger.addHandler(logging.StreamHandler(sys.stdout))

L_ROOT = '/Users/spooky/Downloads/LA-data-frames'
R_ROOT = '/mnt/data/datasets/LA-data-frames'

CAMERA_UPDATE_TABLE = {12: ((91, 194), (92, 195)),  # ((old range, new range), (old range, new range))
                       18: ((177, 194), (178, 195)),
                       19: ((23, 194), (24, 195)),
                       30: ((141,192), (144, 195)),
                       38: ((91,194), (92, 195)),
                       40: ((10, 151), (21, 162)),
                       41: ((89, 192), (92, 195)),
                       45: ((99, 148), (115-164), (149, 166), (178, 195)),
                       50: ((15, 189), (21, 195)),
                       55: ((132, 183), (144, 195)),
                       59: ((12, 186), (21, 195)),
                       64: ((91), (92), (144, 188), (151, 195)),
                       65: ((3, 19), (7, 23)),
                       70: ((28, 188), (35, 195)),
                       74: ((14, 188), (21, 195)),
                       83: ((147, 191), (151, 195)),
                       85: ((7, 138), (35, 166), (139, 156), (178, 195)),
                       89: ((28, 188), (35, 195))
                       }

def get_camera_number_from_path(avif_path):
    # Extract the camera number from the mp4_path
    tokens = avif_path.split('/')
    for t in tokens:
        if 'camera' in t:
            camera = t.split('_')[1]
            return int(camera)

def get_frame_number_from_path(avif_path):
    # Extract the frame number from the avif_path
    base = os.path.basename(avif_path)
    frame_number = base.split('-')[1].split('.')[0]
    return int(frame_number)

def get_range_entry(camera_number):
    # Get the range entry for the given camera number
    if camera_number in CAMERA_UPDATE_TABLE.keys():
        return CAMERA_UPDATE_TABLE[camera_number]
    else:
        logger.warning(f'Camera number {camera_number} not found in update table')
        return None

def frame_in_range(frame_number, range_entry):
    # Check if the frame number is in the given range entry
    try:
        for old_range, new_range in range_entry:
            if old_range[0] <= frame_number <= old_range[1]:
                return True
    except:
        pass
    return False

# def names_from_ranges(range_entry, old_filename):
#     camera_number = pad_frame_number(get_camera_number_from_path(old_filename), 2)
#     frame_number = pad_frame_number(get_frame_number_from_path(old_filename), 5)
#     base_name = os.path.basename(old_filename)
#     print(f'Base name: {base_name} Frame number: {frame_number} Camera number: {camera_number}')
#     # common case, old range is a 2 value tuple, new range is a 2 value tuple
#     if len(range_entry) == 2:
#         print(f'Range entry: {range_entry}')
#         old_range = range_entry[0]
#         new_range = range_entry[1]
#         offset = new_range - old_range
#
#         # if the frame_number is within the old range, calculate the new frame number
#         if old_range[0] >= frame_number <= old_range[1]:
#             new_frame_number = frame_number + offset
#             new_frame_padded = pad_frame_number(new_frame_number)
#             old_frame_padded = pad_frame_number(frame_number)
#             new_frame_name = old_filename.replace(old_frame_padded, new_frame_padded)
#             return new_frame_name
#     return f'Base name: {base_name} Frame number: {frame_number} Camera number: {camera_number}'


if __name__ == '__main__':
    gather = {}
    if os.path.exists(L_ROOT):
        ALL_FRAMES = get_all_avifs(L_ROOT)
    else:
        ALL_FRAMES = get_all_avifs(R_ROOT)

    if ALL_FRAMES:
        for frame in ALL_FRAMES:
            camera_number = get_camera_number_from_path(frame)
            frame_number = get_frame_number_from_path(frame)
            base_name = os.path.basename(frame)
            if camera_number in CAMERA_UPDATE_TABLE.keys():
               if camera_number not in gather.keys():
                   gather[camera_number] = []
               if frame_in_range(frame_number, CAMERA_UPDATE_TABLE[camera_number]):
                   gather[camera_number].append(base_name)

    for camera_number, frames in gather.items():
        logger.info(f'Camera number: {camera_number}')
        for frame in frames:
            logger.info(f'Frame: {frame}')

    #     logger.info(f'Found {len(ALL_FRAMES)} frames to process')
    #     for frame in ALL_FRAMES:
    #         camera_number = get_camera_number_from_path(frame)
    #         frame_number = get_frame_number_from_path(frame)
    #         print(f'Processing frame {frame_number}, camera {camera_number}')
    #         try:
    #             names = names_from_ranges(camera_number, frame)
    #             if names:
    #                 print(names)
    #                 logger.info(f'Proposed: {frame} to {names}')
    #                 # os.rename(frame, names)
    #                 if os.path.exists(names):
    #                     logger.info(f'Frame {names} exists!')
    #         except:
    #             pass
    # else:
    #     logger.warning('No frames found to process')
    #     sys.exit(1)



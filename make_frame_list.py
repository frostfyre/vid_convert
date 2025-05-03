# A script to get the total frame count of each video file in the LA-data directory.
# each row should contain the pose and frame number, from 0-the last frame, skipping every Nth frame
# output should be a CSV file with the following columns:
# - pose, frame_id

# get list of mp4 files in LA-data
import os
import pandas as pd
import logging
import sys
from datetime import datetime
from process_mp4 import get_all_mp4s, get_all_pngs, get_all_avifs
from pathlib import Path
import cv2
import time
import pillow_avif
from PIL import Image
from process_mp4 import convert_png_to_avif, get_camera_number_from_path, get_frame_number_from_path

# Set up logging
logging.basicConfig(filename='make_frame_list.log', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler('make_frame_list.log'))
logger.addHandler(logging.StreamHandler(sys.stdout))
L_ROOT = '/Users/spooky/Downloads/LA-data-frames'
R_ROOT = '/mnt/data/datasets/LA-data-frames'

def get_frame_list(mp4_path, frame_skip=1):
    """Get a list of frames from the mp4 file, skipping every Nth frame."""
    if not os.path.exists(mp4_path):
        logger.error(f'MP4 file not found: {mp4_path}')
        return []

    vidcap = cv2.VideoCapture(mp4_path)
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_list = []
    for i in range(0, total_frames, frame_skip):
        frame_list.append(i)
    return frame_list

list

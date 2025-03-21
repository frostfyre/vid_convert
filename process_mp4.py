from PIL import Image
import os
from pathlib import Path
import cv2
import time
import pillow_avif
import logging
import sys

logging.basicConfig(filename='frame_processing.log', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler('frame_processing.log'))
logger.addHandler(logging.StreamHandler(sys.stdout))


def convert_png_to_avif(image_in):
    if not os.path.exists(image_in):
        logger.error(f'Image not found: {image_in}')
        return
    # convert image to AVIF format
    if os.path.isfile(image_in):
        logger.debug(f'Converting {image_in} to AVIF')
    im = Image.open(image_in)
    # check for alpha channel and remove if found
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
        alpha = im.convert('RGBA').split()[-1]
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.paste(im, mask=alpha)
        im = bg
    im.save(image_in.replace('.png', '.avif'), 'AVIF', quality_mode='q', quality_level=100)
    # remove the PNG file
    os.remove(image_in)


def pad_frame_number(count, pad_length=5):
    #given an integer, pad it with zeros to make it pad length long
    # return as string
    count_str = str(count)
    if len(count_str) < pad_length:
        count_str = '0' * (pad_length - len(count_str)) + count_str
    return count_str


def export_mp4_to_frames(mp4_path):
    # load the mp4 file, output whole frames rotated 90 degrees clockwise
    # frames will be AVIF format
    frames_path = os.path.dirname(mp4_path.replace('/LA-data/', '/LA-data-frames/'))
    if not os.path.exists(mp4_path):
        logger.error(f'Source not found: {mp4_path}')
        return

    if not os.path.exists(frames_path) and os.path.exists(mp4_path):
        os.makedirs(frames_path)
    vidcap = cv2.VideoCapture(mp4_path)
    success, image = vidcap.read()
    count = 0
    camera = mp4_path.split('/')[-1].split('-')[0]
    pose = mp4_path.split('/')[-2]
    model = mp4_path.split('/')[-3]
    frames_path = f'{frames_path}/{camera}'
    if not os.path.exists(frames_path):
        os.makedirs(frames_path)
    logger.info(f'Extracting frames from {mp4_path}')
    while success:
        try:
            out_name = f'{frames_path}/{pose}-{pad_frame_number(count)}.png'
            avif_name = f'{frames_path}/{pose}-{pad_frame_number(count)}.avif'
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            if not os.path.exists(avif_name):
                cv2.imwrite(out_name, image)
                # logger.debug(f'Extracted {out_name}, exists: {os.path.exists(out_name)}')
                # logger.debug("generating AVIF")
                convert_png_to_avif(out_name)
                # logger.debug(f'Created {avif_name}, exists: {os.path.exists(avif_name)}')
                # print('Read a new frame: ', success)
        except BaseException as e:
            logger.error(f'Error processing frame {count} from {mp4_path}:\n\t{e}')
        success, image = vidcap.read()
        count += 1
        # logger.debug(f'\tInner Loop Count: {count}, Out_name: {avif_name}')
    logger.info(f'Wrote {count} frames from {model} {pose} {camera} to:\n{frames_path}')


def rotate_images(input_folder, output_folder, angle):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for filename in os.listdir(input_folder):
        if filename.endswith(".png"):
            img_path = os.path.join(input_folder, filename)
            img = Image.open(img_path)
            rotated_img = img.rotate(angle, expand=True)
            rotated_img.save(os.path.join(output_folder, filename))


def find_png_files(folder):
    # recursively find png files()
    png_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".png"):
                png_files.append(os.path.join(root, file))
    return png_files


def cleanup_png_files(folder='/mnt/data/datasets/LA-data-frames/'):
    # recursively find png files and convert them
    files = find_png_files(folder)
    _ = [convert_png_to_avif(file) for file in files]


def multithreaded_video_processor(vid_list):
    # multithreaded processing
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(export_mp4_to_frames, vid_list)

def gather_mp4_files(project_root = '/mnt/data/datasets/LA-data/'):
    pose_sources = []
    mp4_sources = []
    model_sources = [f for f in os.listdir(project_root) if f.startswith('Model')]
    for model in model_sources:
        pose_sources.extend([f for f in os.listdir(f'{project_root}{model}/') if os.path.isdir(f'{project_root}{model}/{f}')])
        for pose in pose_sources:
            try:
                mp4_sources.extend([f for f in os.listdir(f'{project_root}{model}/{pose}/') if f.endswith('.mp4')])
            except:
                logger.error(f'No mp4 files found in {project_root}{model}/{pose}/')

    vid_list = [f'{project_root}{model}/{pose}/{mp4}' for mp4 in mp4_sources for pose in pose_sources for model in model_sources]
    logger.info(f'{len(model_sources)} models found')
    logger.info(f'{len(set(pose_sources))} poses found')
    logger.info(f'{len(vid_list)} mp4 files found')
    vid_list = [vid for vid in vid_list if os.path.exists(vid)]
    vid_list.sort()
    return vid_list

if __name__ == '__main__':
    print('Multiprocessing Video Captures')
    start = time.time()
    # /Users/spooky/Downloads/LA-data/Model 1/EXP_cheek001  << for local testing
    vid_list = gather_mp4_files()
    try:
        multithreaded_video_processor(vid_list)
    except BaseException as e:
        logger.error(e)
    end = time.time()
    print((end - start), 'seconds')
    logger.handlers[0].close()
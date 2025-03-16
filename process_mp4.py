from PIL import Image
import os
from pathlib import Path
import cv2
import time
import pillow_avif
import logging


logging.basicConfig(filename='process_mp4.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler('process_mp4.log'))


def convert_png_to_avif(image_in):
    # convert image to AVIF format
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

    if not os.path.exists(frames_path):
        os.makedirs(frames_path)
    vidcap = cv2.VideoCapture(mp4_path)
    success, image = vidcap.read()
    count = 0
    camera = mp4_path.split('/')[-1].split('-')[0]
    pose = mp4_path.split('/')[-2]
    model = mp4_path.split('/')[-3]

    while success:
        # pad frame number with zeros
        out_name = f'{frames_path}/{camera}-{pose}-{pad_frame_number(count)}.png'
        if os.path.exists(out_name):
            logger.info(f'Frame {out_name} already exists. Skipping')
        elif not os.path.exists(out_name):
            # image rotate 90 degrees clockwise
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            cv2.imwrite(out_name, image)
            success, image = vidcap.read()
            convert_png_to_avif(out_name)
            # print('Read a new frame: ', success)
        count += 1
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
    logger.info(f'{len(pose_sources)} poses found')
    logger.info(f'{len(vid_list)} mp4 files found')
    return vid_list

if __name__ == '__main__':
    print('Multiprocessing Video Captures')
    start = time.time()
    vid_list = gather_mp4_files()
    try:
        multithreaded_video_processor(vid_list)
    except BaseException as e:
        logger.error(e)
    end = time.time()
    print((end - start), 'seconds')
    logger.handlers[0].close()
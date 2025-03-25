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

    camera = mp4_path.split('/')[-1].split('-')[0]
    pose = mp4_path.split('/')[-2]
    model = mp4_path.split('/')[-3]


def process_single_frame(input_file, frame_number):
    # Open the video file
    video = cv2.VideoCapture(input_file)

    # derive file output path from input file
    camera = input_file.split('/')[-1].split('-')[0]
    pose = input_file.split('/')[-2]
    model = input_file.split('/')[-3]
    count = pad_frame_number(frame_number)
    frames_path = os.path.dirname(input_file.replace('/LA-data/', '/LA-data-frames/'))
    output_file = f'{frames_path}/{pose}-{pad_frame_number(count)}.png'
    avif_name = f'{frames_path}/{pose}-{pad_frame_number(count)}.avif'
    # Set the frame position
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    # Read the specific frame
    success, frame = video.read()
    if not success:
        print("Failed to retrieve the frame.")
        return

    # Rotate the frame 90 degrees clockwise
    rotated_frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

    # Save the frame as a PNG image using cv2
    cv2.imwrite(output_file, rotated_frame)

    # Release video capture
    video.release()

def get_mp4_from_png_path(png_path):
    # given a path to a PNG file, derive the corresponding MP4 file
    # /mnt/data/datasets/LA-data-frames/Model1/EXP_eye_neutral/camera_07-0003.png
    # /mnt/data/datasets/LA-data/Model1/EXP_eye_neutral/camera_07-0003.mp4
    '''/mnt/data/datasets/LA-data/Model1/EXP_jaw003/camera_50-0014.mp4 << GOOD PATH'''
    '''/mnt/data/datasets/LA-data/EXP_jaw003/camera_69/EXP_jaw003.mp4 << BAD PATH'''
    base_path = str(os.path.dirname(png_path).replace('/LA-data-frames/', '/LA-data/'))
    pose = os.path.basename(png_path).split('-')[0]
    camera = os.path.dirname(png_path).split('/')[-1]
    # search for mp4 files in base_path that start with camera
    mp4_base_path = None
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.mp4') and file.startswith(camera):
                mp4_base_path = os.path.join(root, file)
    if not mp4_base_path:
        # exception for Model1 (target: /mnt/data/datasets/LA-data/Model1/EXP_jaw003)
        base_path = base_path.replace(f'/{camera}', "")
        print(camera, pose)
        print(f'exists: {os.path.exists(base_path)}')
        print(f'Searching {base_path}')
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith('.mp4') and file.startswith(camera):
                    mp4_base_path = os.path.join(root, file)
    if not mp4_base_path:
        logger.error(f'No MP4 file found for {png_path}')
    else:
        logger.info(f'Found MP4 file: {mp4_base_path}')
    return mp4_base_path


def get_all_pngs(folder):
    """Recursively get all PNG files from the given folder."""
    png_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith('.png'):
                png_files.append(os.path.join(root, file))
    return png_files


if __name__ == '__main__':
    '''
    Stragglers (TRUNCATED FILES)
    Found 7 PNG files in /mnt/data/datasets/LA-data-frames/
    /mnt/data/datasets/LA-data-frames/Model3/EXP_eyebrow/camera_46-EXP_eyebrow-00079.png
    /mnt/data/datasets/LA-data-frames/Model3/EXP_eyebrow/camera_77-EXP_eyebrow-00463.png
    /mnt/data/datasets/LA-data-frames/Model3/EXP_eyebrow/camera_53-EXP_eyebrow-00187.png
    /mnt/data/datasets/LA-data-frames/Model1/EXP_jaw003/camera_66/EXP_jaw003-00654.png
    /mnt/data/datasets/LA-data-frames/Model1/EXP_jaw003/camera_68/EXP_jaw003-00569.png
    /mnt/data/datasets/LA-data-frames/Model1/EXP_jaw003/camera_67/EXP_jaw003-00392.png        
    /mnt/data/datasets/LA-data-frames/Model1/EXP_jaw003/camera_69/EXP_jaw003-00272.png
    '''
    files = get_all_pngs('/mnt/data/datasets/LA-data-frames/')
    # files = get_all_pngs('/Users/spooky/Downloads/LA-data-frames/')

    for png in files:
        mp4_path = get_mp4_from_png_path(png)
        print(mp4_path)
    '''
        png_name = os.path.basename(png)
        frame_number = int(png_name.split('.')[0].split('-')[-1])
        if os.path.exists(png) and os.path.exists(mp4_path):
            os.remove(png)
            logger.info(f'Removed {png}')
            try:
                process_single_frame(mp4_path, frame_number)
            except BaseException as e:
                print(f'Failed to process {png}:\n{e}')
        else:
            logger.error(f'File {png} exists {os.path.exists(png)}\n{mp4_path} exists {os.path.exists(mp4_path)}')
    time.sleep(10)
    # PNGs regenerated, convert to AVIF

    for png in files:
        try:
            convert_png_to_avif(png)
        except BaseException as e:
            logger.error(f'Error converting {png} to AVIF:\n\t{e}')
            pass
    time.sleep(10)

    # should no longer be any PNGs
    pngs = get_all_pngs('/mnt/data/datasets/LA-data-frames/')
    if pngs:
        for p in pngs:
            print(p)
    '''
    # print('Multiprocessing Video Captures')
    # start = time.time()
    # # /Users/spooky/Downloads/LA-data/Model 1/EXP_cheek001  << for local testing
    # vid_list = gather_mp4_files()
    # try:
    #     multithreaded_video_processor(vid_list)
    # except BaseException as e:
    #     logger.error(e)
    # end = time.time()
    # print((end - start), 'seconds')
    # logger.handlers[0].close()


def get_all_avifs(folder):
    """Recursively get all AVIF files from the given folder."""
    avif_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith('.avif'):
                avif_files.append(os.path.join(root, file))
    return avif_files

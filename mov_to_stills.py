from PIL import Image
import pillow_avif
import os
from pathlib import Path
import cv2
import time
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


def export_mp4_to_frames(mp4_path, src='/mnt/data/datasets/LA-round2-all/selects/', dst='/mnt/data/datasets/LA-round2-frames/'):
    # load the mp4 file, output whole frames rotated 90 degrees clockwise
    # frames will be AVIF format
    # mp4_path = mp4_path.replace(src, dst)
    frames_path = os.path.dirname(mp4_path.replace(src, dst))
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
        # logger.info(f'\tRead Succeeded! Processing...')
        try:
            out_name = f'{frames_path}/{pose}-{pad_frame_number(count)}.png'
            # avif_name = f'{frames_path}/{pose}-{pad_frame_number(count)}.avif'
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            # validate the image is not empty
            if image is None or image.size == 0:
                logger.error(f'Empty image at frame {count} from {mp4_path}')
                success, image = vidcap.read()
                count += 1
                continue
            # logger.info(f'\tAttempting to write {out_name}')

            logger.debug(f'Writing {out_name}')

            cv2.imwrite(out_name, image)
            logger.debug(f'Extracted {out_name}, exists: {os.path.exists(out_name)}')
            # logger.debug("generating AVIF")
            # convert_png_to_avif(out_name)
            # logger.debug(f'Created {avif_name}, exists: {os.path.exists(avif_name)}')
            # print('Read a new frame: ', success)
        except BaseException as e:
            logger.error(f'Error processing frame {count} from {mp4_path}:\n\t{e}')

        success, image = vidcap.read()
        logger.info(f'Processing success:{success} from {mp4_path} to {frames_path}')
        count += 1
        # logger.debug(f'\tInner Loop Count: {count}, Out_name: {avif_name}')
    logger.info(f'Wrote {count} frames from {model} {pose} {camera} to:\n{frames_path}')


def export_prores_to_frames(prores_path, src='/mnt/data/datasets/LA-June', dst='/mnt/data/datasets/LA-June-frames', rotate=False):
    # using ffmpeg to extract frames from a ProRes file and write them to a folder
    frames_path = os.path.dirname(prores_path.replace(src, dst))
    base_name = os.path.basename(prores_path).split('.')[0]
    folder_name = f'{frames_path}/{base_name}'
    if not os.path.exists(prores_path):
        logger.error(f'Source not found: {prores_path}')
        return
    if not os.path.exists(frames_path) and os.path.exists(prores_path):
        os.makedirs(frames_path)
    # use ffmpeg to extract frames
    # frame output_name formatting: {frames_path}/{pose}-{pad_frame_number(count)}.png
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # ffmpeg -i input.mp4 -f image2 -frames:v 1 -c:v librav1e -speed 6 output_frames/frame_%04d.avif
    command = f'ffmpeg -i "{prores_path}" -f image2 -vf "colorspace=all=bt709" "{folder_name}/{base_name}_%04d.avif"'
    logger.info(f'Extracting frames from {prores_path} to {frames_path}')
    os.system(command)


def export_prores_to_avif(video_path):
    # Create output directory if it doesn't exist
    base_name = os.path.basename(video_path).split('.')[0]
    dir_name = os.path.dirname(video_path)
    output_folder = os.path.join(f'{dir_name}-frames/{base_name}')
    if not os.path.exists(video_path):
        logger.error(f'Source not found: {video_path}')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder, exist_ok=True)

    # Open the ProRes video file
    cap = cv2.VideoCapture(video_path)
    frame_idx = 0

    if not cap.isOpened():
        print(f"Error: Unable to open video file {video_path}")
        return
    # how many frames in the video?
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    logger.info(f'Extracting {total_frames} frames from {video_path} to {output_folder}')
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # Exit if no more frames

        # Convert frame to BT.709 color space
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # OpenCV default is BGR, converting to RGB

        # Encode as AVIF image
        success, encoded_image = cv2.imencode(".png", frame)
        if success:
            with open(os.path.join(output_folder, f"f{base_name}_{frame_idx:04d}.png"), "wb") as f:
                f.write(encoded_image)
        # wait until the file is written
        time.sleep(0.1)  # Ensure the file is written before proceeding
        if os.path.getsize(os.path.join(output_folder, f"{base_name}_{frame_idx:04d}.png")) > 0:
            # Convert PNG to AVIF using Pillow
            avif_path = os.path.join(output_folder, f"{base_name}_{frame_idx:04d}.avif")
            img = Image.open(os.path.join(output_folder, f"{base_name}_{frame_idx:04d}.png"))
            img.save(avif_path, format='AVIF', quality_mode='q', quality_level=100)
            # Remove the PNG file after conversion
            os.remove(os.path.join(output_folder, f"{base_name}_{frame_idx:04d}.png"))

        else:
            print(f"Warning: Frame {frame_idx} is empty, skipping conversion.")

        frame_idx += 1

    cap.release()
    print(f"Extraction complete! {frame_idx} frames saved to {output_folder}")



# def get_all_mp4s(folder):

# def get_all_avifs(folder):
#     """Recursively get all AVIF files from the given folder."""
#     avif_files = []
#     for root, dirs, files in os.walk(folder):
#         for file in files:
#             if file.endswith('.avif'):
#                 avif_files.append(os.path.join(root, file))
#     return avif_files



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
    # parallelize the conversion of PNG files to AVIF
    logger.info(f'Found {len(files)} PNG files to convert in {folder}')
    if not files:
        logger.warning(f'No PNG files found in {folder}')
        return
    logger.info(f'Converting {len(files)} PNG files to AVIF in {folder}')
    # convert each PNG file to AVIF
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        executor.map(convert_png_to_avif, files)


def multithreaded_video_processor(vid_list):
    # multithreaded processing
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(export_mp4_to_frames, vid_list)

# def gather_vid_files(project_root = '/mnt/data/datasets/LA-data/', extension='.mp4'):
#     pose_sources = []
#     vid_sources = []
#     for model in model_sources:
#         pose_sources.extend([f for f in os.listdir(f'{project_root}{model}/') if os.path.isdir(f'{project_root}{model}/{f}')])
#         for pose in pose_sources:
#             try:
#                 vid_sources.extend([f for f in os.listdir(f'{project_root}{model}/{pose}/') if f.endswith(extension)])
#             except:
#                 logger.error(f'No mp4 files found in {project_root}{model}/{pose}/')
#
#     vid_list = [f'{project_root}{model}/{pose}/{vid}' for vid in vid_sources for pose in pose_sources for model in model_sources]
#     logger.info(f'{len(model_sources)} models found')
#     logger.info(f'{len(set(pose_sources))} poses found')
#     logger.info(f'{len(vid_list)} mp4 files found')
#     vid_list = [vid for vid in vid_list if os.path.exists(vid)]
#     vid_list.sort()
#     return vid_list

    # camera = mp4_path.split('/')[-1].split('-')[0]
    # pose = mp4_path.split('/')[-2]
    # model = mp4_path.split('/')[-3]


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
    camera = os.path.basename(png_path).split('-')[0]
    # search for mp4 files in base_path that start with camera
    mp4_base_path = None
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.mp4') and file.startswith(camera):
                mp4_base_path = os.path.join(root, file)
    if not mp4_base_path:
        # exception for Model1 (target: /mnt/data/datasets/LA-data/Model1/EXP_jaw003)
        pose = os.path.basename(png_path).split('-')[0]
        camera = os.path.dirname(png_path).split('/')[-1]
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


def cleaning_png_files(folder='/mnt/data/datasets/LA-data-frames/'):
    # recursively find png files and convert them
    files = find_png_files(folder)
    _ = [convert_png_to_avif(file) for file in files]


def mov_extract_frame(input_file, pose_name, model_name, frame_number):
    # Open the video file
    video = cv2.VideoCapture(input_file)

    # derive file output path from input file
    camera_number = input_file.split('/')[-1].split('-')[0]
    pose = pose_name
    model = model_name
    count = pad_frame_number(frame_number)
    frames_path = os.path.dirname(input_file.replace('/LA-round2/', '/LA-round2-frames/'))
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



if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description='Process MP4 files to extract frames.')
    parser.add_argument('input_folder', type=str, help='Path to the input folder containing MP4 files.')
    parser.add_argument('--rotate', action='store_true', help='Rotate frames 90 degrees clockwise.')
    args = parser.parse_args()
    input_folder = args.input_folder
    rotate = args.rotate
    if not os.path.exists(input_folder):
        logger.error(f'Input folder does not exist: {input_folder}')
        sys.exit(1)
    # gather all MOV files in the input folder
    mov_files = [os.path.join(root, file) for root, _, files in os.walk(input_folder) for file in files if file.endswith('.mov')]
    if not mov_files:
        logger.error(f'No MOV files found in the input folder: {input_folder}')
        sys.exit(1)
    logger.info(f'Found {len(mov_files)} MOV files in {input_folder}')
    # process MOV files
    import concurrent.futures
    logger.info('Futures initialized')
    with concurrent.futures.ThreadPoolExecutor() as executor:
        logger.info(f'Processing {len(mov_files)} MOV files in {input_folder}')
        executor.map(export_prores_to_avif, mov_files)
    logger.info('All MOV files exported successfully.')



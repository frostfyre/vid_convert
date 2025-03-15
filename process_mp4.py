from PIL import Image
import os
from pathlib import Path
import cv2
import time
import pillow_avif

# TODO: improve output file names
# TODO: add support for "continue" processing, such that it does not re-render frames that already exist

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


def export_mp4_to_frames(mp4_path, frames_path):
    # load the mp4 file, output whole frames rotated 90 degrees clockwise
    # frames will be AVIF format
    if not os.path.exists(frames_path):
        os.makedirs(frames_path)
    vidcap = cv2.VideoCapture(mp4_path)
    success, image = vidcap.read()
    count = 0
    try:
        pose_name = [t for t in os.path.basename(mp4_path).split('/') if t.startswith('EXP_')]
        pose_name = pose_name[0]
    except:
        pose_name = "unknown_pose"
    cam_name = os.path.basename(mp4_path).split('-')[0]
    # construct filename
    basename = os.path.basename(mp4_path).split('.')[0]
    while success:
        # pad frame number with zeros
        if len(str(count)) == 1:
            out_name = f'{basename}_0000{count}.png'
        elif len(str(count)) == 2:
            out_name = f'{basename}_000{count}.png'
        elif len(str(count)) == 3:
            out_name = f'{basename}_00{count}.png'
        elif len(str(count)) == 4:
            out_name = f'{basename}_0{count}.png'
        else:
            out_name = f'{basename}_{count}.png'

        output_path = os.path.join(frames_path, out_name)
        # print(f'Exporting {out_name} to {frames_path}')
        # image rotate 90 degrees clockwise
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        cv2.imwrite(output_path, image)
        success, image = vidcap.read()
        convert_png_to_avif(output_path)
        # print('Read a new frame: ', success)
        count += 1
    print(f'\t Wrote {count-1} frames from {cam_name} to {frames_path}')


def rotate_images(input_folder, output_folder, angle):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for filename in os.listdir(input_folder):
        if filename.endswith(".png"):
            img_path = os.path.join(input_folder, filename)
            img = Image.open(img_path)
            rotated_img = img.rotate(angle, expand=True)
            rotated_img.save(os.path.join(output_folder, filename))


def process_video_file(video_file_path):
    frame_out = os.path.dirname(video_file_path) + '/frames/'
    export_mp4_to_frames(video_file_path, frame_out)


def multithreaded_video_processor(vid_list):
    # multithreaded processing
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_video_file, vid_list)


# enable recusrive mutlthreaded processing
# TODO: clean up the gather process

project_root = '/Users/spooky/Downloads/'

# export_mp4_to_frames(f'{project_root}camera_06-0002.mp4', project_root + '/cam_6_frames/')

mp4_sources = [f for f in os.listdir(project_root) if f.startswith('EXP_') and not f.endswith('_processed')]
video_files = {}
vid_list = []
# accumulate files to process
for project in mp4_sources:
    mp4_source = f'{project_root}{project}/'
    frames_dest = f'{project_root}{project}/frames/'
    videos = [f for f in os.listdir(mp4_source) if f.endswith('.mp4')]
    videos.sort()
    video_files[project] = [mp4_source, frames_dest, videos]

for project, files in video_files.items():
    print(f'Project: {project}')
    for video in files[2]:
        vid_list.append(f'{files[0]}{video}')

print("gather complete")

print('Multiprocessing Video Captures')
start = time.time()
try:
    multithreaded_video_processor(vid_list)
except BaseException as e:
    print(e)
end = time.time()
print((end - start), 'seconds')
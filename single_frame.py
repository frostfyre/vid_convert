import os
import cv2


def process_frame(input_file, frame_number, output_file):
    # Open the video file
    video = cv2.VideoCapture(input_file)

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
    # Example usage:
    input_mp4 = "/Users/spooky/Downloads/LA-data/Model1/EXP_eye_neutral/camera_07-0003.mp4"  # Replace with your input MP4 file path
    frame_to_extract = 256 #replace with the frame number you want to extract
    output_avif = f"./EXP_eye_neutral_camera07-frame_{frame_to_extract}.png" #replace with your desired output path
    if not os.path.exists(os.path.dirname(output_avif)):
        os.makedirs(os.path.dirname(output_avif), exist_ok=True)

    process_frame(input_mp4, frame_to_extract, output_avif)
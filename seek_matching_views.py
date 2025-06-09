import os
# given the following names:
cal_data_name = '001-RX0_9990253_C0008.04030868'
max_data_name = 'camera_01_M4_EXP_eye_neutral-00003'

# 001 corresponsds to camera_01
# for a pair of lists of names, find the matching views
def find_matching_views(cal_data_name, max_data_name):
    cal_camera_number = int(cal_data_name.split('-')[0])
    max_camera_number = int(max_data_name.split('_')[1])

    if cal_camera_number == max_camera_number:
        return True
    return False


# display the image data in each pair of names
def display_matching_views(matching_views, cal_data_src, max_data_src):
    for entry in matching_views:
        print(cal_data_src)
        print(max_data_src)
        print(entry[0])
        print(entry[1])
        cal_image_path = os.path.join(str(cal_data_src), str(entry[0]))
        max_image_path = os.path.join(str(max_data_src), str(entry[1]))

        if os.path.exists(cal_image_path) and os.path.exists(max_image_path):
            print(f'Matching Views:\nCalibration: {cal_image_path}\nMax: {max_image_path}\n')
            # display the image data (for example, using PIL or OpenCV)
            # Uncomment the following lines to display images using OpenCV
            import cv2
            cal_image = cv2.imread(cal_image_path)
            max_image = cv2.imread(max_image_path)
            # rotate cal_image if needed:
            cal_image = cv2.rotate(cal_image, cv2.ROTATE_90_CLOCKWISE)
            cv2.imshow('Calibration Image', cal_image)
            cv2.imshow('Max Image', max_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print(f'One of the images does not exist:\nCalibration: {cal_image_path}\nMax: {max_image_path}\n')

if __name__ == '__main__':
    # get list of cal_data_names and max_data_names
    cal_data_src = '/Users/spooky/Downloads/UNISON_Target_Stills'
    max_data_src = '/Users/spooky/modeling_frames/Model4/M4_MODELING_FRAMES_EXP_eye_neutral'
    cal_data_names = [f for f in os.listdir(cal_data_src) if f.endswith('.png')]
    max_data_names = [f for f in os.listdir(max_data_src) if f.endswith('.png')]

    # generate pairs of names
    matching_views = []
    removals = []
    for cal_name in cal_data_names:
        for max_name in max_data_names:
            if find_matching_views(cal_name, max_name):
                matching_views.append((cal_name, max_name))

    for cal_data_name in cal_data_names:
        if cal_data_name not in [pair[0] for pair in matching_views]:
            removals.append(cal_data_name)

    cam_list = [cams[1].split('_M4_')[0] for cams in matching_views]
    cam_list.sort()
    # display_matching_views(matching_views, cal_data_src, max_data_src)

    img_list = [cams[0] for cams in matching_views]
    img_list.sort()


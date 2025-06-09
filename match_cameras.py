import cv2
import numpy as np
import os
import csv

def load_images_from_folder(folder):
    images = {}
    for filename in os.listdir(folder):
        img = cv2.imread(os.path.join(folder, filename), cv2.IMREAD_GRAYSCALE)
        if img is not None:
            images[filename] = img
    return images

def match_images(img1, img2):
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = matcher.match(des1, des2)

    return len(matches)  # Return number of matches as a similarity measure

def process_folders(folder1, folder2, output_csv="matches.csv", match_threshold=50):
    images1 = load_images_from_folder(folder1)
    images2 = load_images_from_folder(folder2)

    match_dict = {}

    for filename1, img1 in images1.items():
        best_match = None
        best_match_count = 0

        for filename2, img2 in images2.items():
            rotated_img2 = cv2.rotate(img2, cv2.ROTATE_90_CLOCKWISE)

            match_count = match_images(img1, rotated_img2)

            if match_count > best_match_count and match_count > match_threshold:
                best_match = filename2
                best_match_count = match_count

        if best_match:
            match_dict[filename1] = best_match

    # Save matches to a CSV file
    with open(output_csv, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Folder1 Image", "Matching Folder2 Image"])
        for key, value in match_dict.items():
            writer.writerow([key, value])

    print(f"Matches saved to {output_csv}")
    return match_dict

# Example usage
folder1 = "/Users/spooky/modeling_frames/Model4/EXP_eye_neutral"
folder2 = "/Users/spooky/Downloads/UNISON_Target_Stills"
matches = process_folders(folder1, folder2)

print("Matching images:", matches)

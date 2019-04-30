import os
import cv2
import random

path = "images/"

# Get list of all image filenames
filenames = os.listdir(path + "usda_nass")

# Shuffle the names
random.shuffle(filenames)

# 80% for training, 20% for testing
cutoff = int(0.8 * len(filenames))

for fname in filenames[:cutoff]:

    # Load both images
    cop_img = cv2.imread(path + "copernicus/" + fname)
    usd_img = cv2.imread(path + "usda_nass/" + fname)

    # Save to training folder
    cv2.imwrite(path + "train/copernicus/" + fname, cop_img)
    cv2.imwrite(path + "train/usda_nass/" + fname, usd_img)

for fname in filenames[cutoff:]:

    # Load both images
    cop_img = cv2.imread(path + "copernicus/" + fname)
    usd_img = cv2.imread(path + "usda_nass/" + fname)

    # Save to training folder
    cv2.imwrite(path + "test/copernicus/" + fname, cop_img)
    cv2.imwrite(path + "test/usda_nass/" + fname, usd_img)



import os
import cv2
import random
import numpy as np

path = "images/train/"

# Get list of all image filenames
filenames = os.listdir(path + "usda_nass")

tot_white = 0.0
tot = 224.0 * 224.0 * len(filenames)

for fname in filenames:


    img = cv2.imread(path + "usda_nass/" + fname, 0) / 255.0

    img[img > 0.5] = 1.0
    img[img <= 0.5] = 0.0

    tot_white = tot_white + np.sum(img)


print "Pct. white pixels:\t" + str(tot_white / tot)
print "Pct. black pixels:\t" + str(1.0 - (tot_white / tot))



import ee
import cv2
import numpy as np
import time

from image_collection_tools import *

# Initialize Earth Engine client
ee.Initialize()

# Parameters
num_images = 30000
start_index = 13022
min_longitude = -121.0
max_longitude = -89.0
min_latitude = 36.0
max_latitude = 45.0
square_size_km = 3.75
crop_to = 224
path = "dataset/" #""/media/ekaj/JAKE/dl_project_images/"
start = time.time()

for i in range(num_images):

    # Print progress updates
    if i % 100 == 0 and i > 0:
        print "Total images collected\t" + str(i) + "\tTime for last 100:\t" + str(time.time() - start)
        start = time.time()

    # Generate random coordinate within boundaries
    new_lat = min_latitude + np.random.random() * (max_latitude - min_latitude)
    new_lon = min_longitude + np.random.random() * (max_longitude - min_longitude)

    # Compute corners of rectangle
    square = get_square([new_lon, new_lat], square_size_km)

    # Get regular image from Copernicus data
    cop_img = get_copernicus_image(square, 20, crop_to)

    # Get cultivation image from USDA_NASS data
    usda_img = get_usda_nass_image(square, 20, crop_to)

    # Save to corresponding folders with same numerical filename
    num = start_index + i
    cv2.imwrite(path + "copernicus/" + str(num).zfill(6) + ".jpg", cop_img)
    cv2.imwrite(path + "usda_nass/" + str(num).zfill(6) + ".jpg", usda_img)


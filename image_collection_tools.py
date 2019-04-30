
# Google Earth Engine modules
import ee
import ee.mapclient

# For downloading image
import urllib

# For file cleanup
import zipfile
import os

# Image formatting
import numpy as np
from PIL import Image

# Math
from math import cos, radians


# Start and end dates for COPERNICUS image searches
COPERNICUS_START = '2018-01-01'
COPERNICUS_STOP = '2018-06-30'

# Start and end dates for USDA_NASS imagery searches
USDA_NASS_START = '2017-01-01'
USDA_NASS_STOP = '2017-12-31'


# Get corner GPS coordinates for square around specified center coord
def get_square(center, length_in_km):

    # Coordinates of center of square
    center_lon = center[0]
    center_lat = center[1]

    # Compute required lat / lon change
    lat_change = length_in_km * (360.0 / 40075.0)
    lon_change = length_in_km * (360.0 / (40075.0 * cos(radians(center_lat))))

    # Compute other corner's latitude
    c1_lat = center_lat + (lat_change / 2.0)
    c2_lat = center_lat - (lat_change / 2.0)

    # Compute other corner's longitude
    c1_lon = center_lon + (lon_change / 2.0)
    c2_lon = center_lon - (lon_change / 2.0)

    return [c1_lon, c1_lat, c2_lon, c2_lat]


# Function for filtering clouds
def maskS2clouds(image):

    qa = image.select('QA60')
    cloudBitMask = 1 << 10
    cirrusBitMask = 1 << 11

    cloud_mask = qa.bitwiseAnd(cloudBitMask).eq(0)
    cirrus_mask = qa.bitwiseAnd(cirrusBitMask).eq(0)
    mask = cloud_mask.And(cirrus_mask)
    return image.updateMask(mask).divide(10000)


# Downloads and formats an image from the Copernicus Satellite
# dataset, accessible through Google Earth Engine
def get_copernicus_image(rectangle, scale, cropto=None):

    # Create an ee Rectangle object for specified region
    region = ee.Geometry.Rectangle(rectangle)

    # Filter the Copernicus collection for the correct region
    copernicus_image = ee.ImageCollection('COPERNICUS/S2')
    copernicus_image = copernicus_image.filterDate(COPERNICUS_START, COPERNICUS_STOP)
    copernicus_image = copernicus_image.filterBounds(region)
    copernicus_image = copernicus_image.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    copernicus_image = copernicus_image.map(maskS2clouds)
    copernicus_image = copernicus_image.median().clip(region)
    copernicus_image = copernicus_image.select(['B4', 'B3', 'B2'])

    # Get a download URL for the image
    path = copernicus_image.getDownloadUrl({
        "name": "image",
        'scale': scale,
        'crs': 'EPSG:3857'
    })

    # Download zipfile from download url
    urllib.urlretrieve(path, "image_zipfile")

    # Extract contents from zipfile
    zipped = zipfile.ZipFile("image_zipfile")
    zipped.extractall()

    # Convert from tif to jpg
    img_r = Image.open("image.B4.tif")
    img_g = Image.open("image.B3.tif")
    img_b = Image.open("image.B2.tif")

    # Scale brightness
    img_r_arr = np.array(img_r)
    img_g_arr = np.array(img_g)
    img_b_arr = np.array(img_b)

    img_r_arr[img_r_arr > 0.3] = 0.3
    img_g_arr[img_g_arr > 0.3] = 0.3
    img_b_arr[img_b_arr > 0.3] = 0.3

    img_r_arr = (img_r_arr * (255.0 / 0.3)).astype(np.uint8)
    img_g_arr = (img_g_arr * (255.0 / 0.3)).astype(np.uint8)
    img_b_arr = (img_b_arr * (255.0 / 0.3)).astype(np.uint8)

    # Combine r,g,b channels
    img = np.dstack([img_b_arr, img_g_arr, img_r_arr])

    # Crop to specified size
    if cropto is not None:
        if img.shape[0] >= cropto and img.shape[1] >= cropto:
            img = img[0:cropto, 0:cropto]
        else:
            print "WARNING: Retrieved image that was smaller than cropping dimensions"

    # Clean up extra files
    os.remove("image_zipfile")
    os.remove("image.B2.tif")
    os.remove("image.B3.tif")
    os.remove("image.B4.tif")
    os.remove("image.B2.tfw")
    os.remove("image.B3.tfw")
    os.remove("image.B4.tfw")

    # Return image
    return img



# Downloads and formats an image from the Copernicus Satellite
# dataset, accessible through Google Earth Engine
def get_usda_nass_image(rectangle, scale, cropto=None):

    # Create an ee Rectangle object for specified region
    region = ee.Geometry.Rectangle(rectangle)

    # Filter the Copernicus collection for the correct region
    usda_nass_image = ee.ImageCollection("USDA/NASS/CDL")
    usda_nass_image = usda_nass_image.filterDate(USDA_NASS_START, USDA_NASS_STOP)
    usda_nass_image = usda_nass_image.filterBounds(region)
    usda_nass_image = usda_nass_image.median().clip(region)
    usda_nass_image = usda_nass_image.select(['cultivated'])

    # Get a download URL for the image
    path = usda_nass_image.getDownloadUrl({
        "name": "image",
        'scale': scale,
        'crs': 'EPSG:3857'
    })

    # Download zipfile from download url
    urllib.urlretrieve(path, "image_zipfile")

    # Extract contents from zipfile
    zipped = zipfile.ZipFile("image_zipfile")
    zipped.extractall()

    # Convert from tif to jpg
    img = Image.open("image.cultivated.tif")

    # Scale brightness
    img = np.array(img)

    img = ((img - 1.0) * (255.0)).astype(np.uint8)

    # Crop to specified size
    if cropto is not None:
        if img.shape[0] >= cropto and img.shape[1] >= cropto:
            img = img[0:cropto, 0:cropto]
        else:
            print "WARNING: Retrieved image that was smaller than cropping dimensions"

    # Clean up extra files
    os.remove("image_zipfile")
    os.remove("image.cultivated.tif")
    os.remove("image.cultivated.tfw")

    # Return image
    return img

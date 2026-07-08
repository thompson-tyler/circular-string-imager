from os import path


PIXEL_VALUE_SUBTRACT = 10
BOOST_FOR_MORE_POINTS = False
INPUT_DIR = "input/"
OUTPUT_DIR = "output/"
ARCHIVE_DIR = "archive/"
POINTS_ON_CIRCLE = 250
RADIUS_SCALE = 1.0
NUM_CORDS = 10000
LOG_EVERY_N = 100
EXPORT_IMAGE_EVERY = 100
LINE_OPACITY = 0.15  # PIXEL_VALUE_SUBTRACT / 255.0
TARGET_BLACK_PIXELS = True
EDGE_PREPROCESS = False
BUMP_CONTRAST = True
FORCE_SQUARE = True  # If true, will crop the image to a square before processing
# Minimum distance between points on the circle to consider a cord
MIN_CORD_DISTANCE = 40
DEFAULT_MAX_SIZE = 1000


def output_path(img_name=None):
    return (
        path.join(OUTPUT_DIR, img_name)
        if img_name
        else OUTPUT_DIR
    )

def output_progress_path(img_name=None):
    return (
        path.join(OUTPUT_DIR, img_name, "progress") 
        if img_name
        else path.join(OUTPUT_DIR, "progress")
    )

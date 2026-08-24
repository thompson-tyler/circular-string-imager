from os import path


PIXEL_VALUE_SUBTRACT = 10
INPUT_DIR = "input/"
OUTPUT_DIR = "output/"
ARCHIVE_DIR = "archive/"
POINTS_ON_CIRCLE = 250
RADIUS_SCALE = 1.0
NUM_CORDS = 10000
LOG_EVERY_N = NUM_CORDS // 10
EXPORT_IMAGE_EVERY = None
LINE_OPACITY = 0.15  # PIXEL_VALUE_SUBTRACT / 255.0
TARGET_BLACK_PIXELS = True
BUMP_CONTRAST = True
FORCE_SQUARE = True  # If true, will crop the image to a square before processing
# Minimum distance between points on the circle to consider a cord
MIN_CORD_DISTANCE = POINTS_ON_CIRCLE // 8
DEFAULT_MAX_SIZE = 1000


# This should really be a validation rule on the CLI args
assert PIXEL_VALUE_SUBTRACT > 0, "PIXEL_VALUE_SUBTRACT must be positive"


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

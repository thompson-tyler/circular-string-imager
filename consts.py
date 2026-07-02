from os import path


PIXEL_VALUE_SUBTRACT = 25
BOOST_FOR_MORE_POINTS = True
INPUT_DIR = "input/"
OUTPUT_DIR = "output/"


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

from os import path


PIXEL_VALUE_SUBTRACT = 25
BOOST_FOR_MORE_POINTS = True
IMAGE_DIR = "images/"


def image_path(img_path=None):
    return path.join(IMAGE_DIR, img_path) if img_path else IMAGE_DIR


def output_path(img_path=None):
    return (
        path.join(IMAGE_DIR, "output", img_path)
        if img_path
        else path.join(IMAGE_DIR, "output")
    )

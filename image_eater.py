from PIL import Image
import numpy as np


def open_image(image_path):
    with Image.open(image_path) as img:
        img = img.convert("RGB")

    # Convert to NumPy array (shape: height x width x 3)
    arr = np.array(img)

    # Convert to array of RGB tuples (shape: height x width)
    rgb_tuples = np.apply_along_axis(lambda x: tuple(x), 2, arr)

    return rgb_tuples

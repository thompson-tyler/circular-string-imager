import numpy as np
from PIL import Image


def open_image(image_path):
    with Image.open(image_path) as img:
        img = img.convert("L")  # Convert to grayscale

    # Convert to NumPy array (shape: height x width)
    return np.array(img)

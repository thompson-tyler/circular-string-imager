import cv2
from consts import image_path


def append_suffix_to_filename(filename, suffix):
    [path, extension] = filename.rsplit(".", 1)
    return f"{path}_{suffix}.{extension}"


def preprocess_image_edge(image_name):
    img = cv2.imread(image_path(image_name), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Image at path {image_name} could not be loaded.")
    edges = cv2.Canny(img, 100, 200)
    new_path = append_suffix_to_filename(image_name, "edges")
    cv2.imwrite(image_path(new_path), edges)
    return new_path


def invert_image(image_name):
    img = cv2.imread(image_path(image_name), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Image at path {image_name} could not be loaded.")
    inverted_img = cv2.bitwise_not(img)
    new_path = append_suffix_to_filename(image_name, "inverted")
    cv2.imwrite(image_path(new_path), inverted_img)
    return new_path


def bump_contrast(image_name, clip_limit=2.0, tile_grid_size=(8, 8)):
    img = cv2.imread(image_path(image_name), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Image at path {image_name} could not be loaded.")
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    contrast_img = clahe.apply(img)
    new_path = append_suffix_to_filename(image_name, "bumped_contrast")
    cv2.imwrite(image_path(new_path), contrast_img)
    return new_path

# Takes an image of arbitrary dimensions and saves a square version of it, cropping the longer dimension to match the shorter one. Returns the path to the new image.
def squareizer(image_name):
    img = cv2.imread(image_path(image_name))
    if img is None:
        raise ValueError(f"Image at path {image_name} could not be loaded.")
    height, width = img.shape[:2]
    if height == width:
        return image_name  # Already square
    min_dim = min(height, width)
    start_x = (width - min_dim) // 2
    start_y = (height - min_dim) // 2
    square_img = img[start_y:start_y + min_dim, start_x:start_x + min_dim]
    new_path = append_suffix_to_filename(image_name, "squared")
    cv2.imwrite(image_path(new_path), square_img)
    return new_path

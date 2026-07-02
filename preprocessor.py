import cv2
import os


def append_suffix_to_filename(image_path, suffix):
    filename = os.path.basename(image_path)
    [name, extension] = os.path.splitext(filename)
    return f"{name}_{suffix}{extension}"


def preprocess_image_edge(image_path, output_dir):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Image at path \"{image_path}\" could not be loaded.")
    edges = cv2.Canny(img, 100, 200)
    new_filename = append_suffix_to_filename(image_path, "edges")
    new_path = os.path.join(output_dir, new_filename)
    cv2.imwrite(new_path, edges)
    return new_path


def invert_image(image_path, output_dir):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Image at path \"{image_path}\" could not be loaded.")
    inverted_img = cv2.bitwise_not(img)
    new_filename = append_suffix_to_filename(image_path, "inverted")
    new_path = os.path.join(output_dir, new_filename)
    cv2.imwrite(new_path, inverted_img)
    return new_path


def bump_contrast(image_path, output_dir, clip_limit=2.0, tile_grid_size=(8, 8)):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Image at path \"{image_path}\" could not be loaded.")
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    contrast_img = clahe.apply(img)
    new_filename = append_suffix_to_filename(image_path, "bumped_contrast")
    new_path = os.path.join(output_dir, new_filename)
    cv2.imwrite(new_path, contrast_img)
    return new_path

# Takes an image of arbitrary dimensions and saves a square version of it, cropping the longer dimension to match the shorter one. Returns the path to the new image.
def squareizer(image_path, output_dir):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Image at path \"{image_path}\" could not be loaded.")
    height, width = img.shape[:2]
    if height == width:
        print(f"Image at path \"{image_path}\" is already square. No changes made.")
        return image_path  # Already square
    min_dim = min(height, width)
    start_x = (width - min_dim) // 2
    start_y = (height - min_dim) // 2
    square_img = img[start_y:start_y + min_dim, start_x:start_x + min_dim]
    new_filename = append_suffix_to_filename(image_path, "squared")
    new_path = os.path.join(output_dir, new_filename)
    cv2.imwrite(new_path, square_img)
    return new_path

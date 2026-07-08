import cv2
import os


def load_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Image at path \"{image_path}\" could not be loaded.")
    return img


def preprocess_image_edge(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    return cv2.Canny(gray, 100, 200)


def invert_image(img):
    return cv2.bitwise_not(img)


def bump_contrast(img, clip_limit=2.0, tile_grid_size=(8, 8)):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    return clahe.apply(gray)


def squareizer(img):
    height, width = img.shape[:2]
    if height == width:
        return img
    min_dim = min(height, width)
    start_x = (width - min_dim) // 2
    start_y = (height - min_dim) // 2
    return img[start_y:start_y + min_dim, start_x:start_x + min_dim]


def resize_to_max(img, max_size):
    max_width, max_height = max_size
    height, width = img.shape[:2]

    scale = min(max_width / width, max_height / height)
    if scale >= 1:
        return img

    print(f"Scaling image down by {scale:.2f} to fit within {max_width}x{max_height}")
    new_width = int(width * scale)
    new_height = int(height * scale)
    return cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)


def export_adjusted_image(img, source_image_path, output_dir):
    source_name = os.path.basename(source_image_path)
    name, ext = os.path.splitext(source_name)
    extension = ext if ext else ".png"
    adjusted_path = os.path.join(output_dir, f"{name}_adjusted{extension}")
    cv2.imwrite(adjusted_path, img)
    return adjusted_path

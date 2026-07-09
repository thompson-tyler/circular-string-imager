import os
from typing import TypeAlias
import numpy as np
from numpy.typing import NDArray
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


ImageArray: TypeAlias = NDArray[np.uint8]


def load_image(image_path: str) -> ImageArray:
    try:
        with Image.open(image_path) as img:
            # Keep color input as 3-channel for downstream processing.
            return np.array(img.convert("RGB"))
    except OSError as exc:
        raise ValueError(f"Image at path \"{image_path}\" could not be loaded.") from exc


def invert_image(img: ImageArray) -> ImageArray:
    pil_img = Image.fromarray(img)

    if pil_img.mode not in ("L", "RGB"):
        pil_img = pil_img.convert("RGB")

    return np.array(ImageOps.invert(pil_img), dtype=np.uint8)


def bump_contrast(img: ImageArray) -> ImageArray:
    pil_img = Image.fromarray(img)

    gray = ImageOps.grayscale(pil_img)

    # A small blur can reduce noise amplification during equalization.
    blur_radius = 0.0
    if blur_radius > 0:
        gray = gray.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    gray = ImageOps.autocontrast(gray, cutoff=1)
    gray = ImageOps.equalize(gray)
    gray = ImageEnhance.Contrast(gray).enhance(1.15)

    return np.array(gray, dtype=np.uint8)


def squareizer(img: ImageArray) -> ImageArray:
    height, width = img.shape[:2]
    if height == width:
        return img
    min_dim = min(height, width)
    start_x = (width - min_dim) // 2
    start_y = (height - min_dim) // 2
    return img[start_y:start_y + min_dim, start_x:start_x + min_dim]


def resize_to_max(img: ImageArray, max_size: tuple[int, int]) -> ImageArray:
    max_width, max_height = max_size
    height, width = img.shape[:2]
    pil_img = Image.fromarray(img)

    if width <= max_width and height <= max_height:
        return img

    print(f"Scaling image down to fit within {max_width}x{max_height}")
    try:
        resized = pil_img.resize((max_width, max_height), Image.Resampling.LANCZOS)
    except AttributeError:
        resized = pil_img.resize((max_width, max_height), Image.LANCZOS)

    return np.array(resized, dtype=np.uint8)


def export_adjusted_image(img: ImageArray, source_image_path: str, output_dir: str) -> str:
    source_name = os.path.basename(source_image_path)
    name, ext = os.path.splitext(source_name)
    extension = ext if ext else ".png"
    adjusted_path = os.path.join(output_dir, f"{name}_adjusted{extension}")

    out_img = Image.fromarray(img)

    # JPEG does not support alpha; ensure compatible mode before save.
    if extension.lower() in (".jpg", ".jpeg") and out_img.mode == "RGBA":
        out_img = out_img.convert("RGB")

    out_img.save(adjusted_path)
    return adjusted_path

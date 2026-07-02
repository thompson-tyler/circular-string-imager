from PIL import Image, ImageDraw


def render_path(
    path_points: list[tuple[float, float]],
    image_size: tuple[int, int],
    background_color="white",
    line_opacity=1.0,
    line_width=1,
    supersample=1,
):
    """
    Draws a path as a sequence of lines using Pillow, with optional supersampling for anti-aliasing.
    - path_points: list of (x, y) tuples
    - image_size: (width, height)
    - background_color: color string or (R,G,B) or (R,G,B,A)
    - line_opacity: float 0-1
    - line_width: width of the line in pixels
    - supersample: int, >1 for anti-aliasing
    """
    print(f"with line opacity {line_opacity} and width {line_width}")
    W, H = image_size
    SW, SH = W * supersample, H * supersample
    # Convert background color to RGBA
    if isinstance(background_color, str):
        bg = background_color
    elif hasattr(background_color, "__iter__"):
        if len(background_color) == 3:
            bg = tuple(list(background_color) + [255])
        else:
            bg = tuple(background_color)
    else:
        bg = (255, 255, 255, 255)
    img = Image.new("RGBA", (SW, SH), bg)
    draw = ImageDraw.Draw(img, "RGBA")

    # Prepare line color (black with opacity)
    if line_opacity < 1.0:
        color = (0, 0, 0, int(255 * line_opacity))
    else:
        color = (0, 0, 0, 255)

    # Draw lines between consecutive points
    for p0, p1 in zip(path_points, path_points[1:]):
        draw.line(
            [
                (p0[0] * supersample, p0[1] * supersample),
                (p1[0] * supersample, p1[1] * supersample),
            ],
            fill=color,
            width=max(1, int(line_width * supersample)),
            joint="curve",
        )

    # Downsample for anti-aliasing
    if supersample > 1:
        # Pillow >=9.1.0 uses Image.Resampling.LANCZOS
        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = 3  # BICUBIC integer fallback for older Pillow
        img = img.resize((W, H), resample)

    return img

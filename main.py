import random
from image_eater import open_image
from line_optimizer import find_best_cord
from point_generator import generate_circle_points, points_on_line
from points_printer import plot_path_ascii, plot_points_ascii
from line_renderer import render_path
from preprocessor import invert_image, preprocess_image_edge, bump_contrast, squareizer
from consts import PIXEL_VALUE_SUBTRACT, image_path, output_path
import os
import shutil


IMAGE_NAME = "geo_fire.jpeg"

POINTS_ON_CIRCLE = 240
RADIUS_SCALE = 1.0
NUM_CORDS = 5000
LOG_EVERY_N = 50
LINE_OPACITY = 0.25  # PIXEL_VALUE_SUBTRACT / 255.0
TARGET_BLACK_PIXELS = False
EDGE_PREPROCESS = False
BUMP_CONTRAST = True
FORCE_SQUARE = True  # If true, will crop the image to a square before processing
EXPORT_IMAGE_EVERY = 100
# Minimum distance between points on the circle to consider a cord
MIN_CORD_DISTANCE = 40


assert 0.0 < LINE_OPACITY <= 1.0, "LINE_OPACITY must be in (0.0, 1.0]"


def rand_index(num_points):
    if num_points <= 0:
        raise ValueError("num_points must be greater than 0")
    return random.randint(0, num_points - 1)


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


def export_image(path_points, width, height):
    # Render the path to an image and save it
    img = render_path(
        path_points,
        image_size=(width, height),
        line_opacity=LINE_OPACITY,
    )
    img.save(output_path(f"output_{len(path_points) - 1}.png"))


def make_dirs():
    os.makedirs(image_path(), exist_ok=True)
    shutil.rmtree(output_path(), ignore_errors=True)
    os.makedirs(output_path(), exist_ok=True)


def main():
    make_dirs()

    img_name = IMAGE_NAME
    if TARGET_BLACK_PIXELS:
        img_name = invert_image(img_name)
    if EDGE_PREPROCESS:
        img_name = preprocess_image_edge(img_name)
    if BUMP_CONTRAST:
        img_name = bump_contrast(img_name)
    if FORCE_SQUARE:
        img_name = squareizer(img_name)
    image = open_image(img_name)

    assert image.shape[2] == 3, "Image must be RGB"
    (height, width, _) = image.shape
    
    assert width == height, "Image must be square"

    # generate circle of points about center
    center = (width / 2, height / 2)
    radius = width / 2 * RADIUS_SCALE
    num_points = POINTS_ON_CIRCLE
    circ_points = generate_circle_points(center, radius, num_points)

    curr_circ_point = rand_index(num_points)
    path = [curr_circ_point]
    print(f"Starting computation of {NUM_CORDS} cords")
    for nth_cord in range(NUM_CORDS):
        # Check that all pixels are not zero
        if not image.any():
            print("All pixels are zero, stopping early")
            break

        best_point, best_value = find_best_cord(
            image, circ_points, curr_circ_point, min_cord_distance=MIN_CORD_DISTANCE
        )
        path.append(best_point)

        # Subtract a small value from the points along the cord to encourage exploration
        point_generator = points_on_line(
            circ_points[curr_circ_point], circ_points[best_point]
        )
        for point in point_generator:
            ix, iy = int(round(point[0])), int(round(point[1]))
            if 0 <= ix < image.shape[1] and 0 <= iy < image.shape[0]:
                r, g, b = image[iy, ix]
                r = clamp(int(r) - PIXEL_VALUE_SUBTRACT, 0, 255)
                g = clamp(int(g) - PIXEL_VALUE_SUBTRACT, 0, 255)
                b = clamp(int(b) - PIXEL_VALUE_SUBTRACT, 0, 255)
                image[iy, ix] = (r, g, b)

        curr_circ_point = best_point
        if (nth_cord + 1) % LOG_EVERY_N == 0:
            print(
                f"Completed {100 * (nth_cord + 1) / NUM_CORDS}% ({nth_cord + 1} / {NUM_CORDS}) of total cords"
            )

        if (nth_cord + 1) % EXPORT_IMAGE_EVERY == 0:
            path_points = [circ_points[i] for i in path]
            export_image(path_points, width, height)
            print(
                f"Exported intermediate image at {100 * (nth_cord + 1) / NUM_CORDS}% ({nth_cord + 1} / {NUM_CORDS}) of total cords"
            )
            print(f"Last cord was from {path[-2]} to {path[-1]}")
            print(f"Current num paths is {len(path)}")

    path_points = [circ_points[i] for i in path]
    export_image(path_points, width, height)
    print("Exported final image")


if __name__ == "__main__":
    main()

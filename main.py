import random
import shutil
from time import time
from image_eater import open_image
from line_optimizer import find_best_cord
from point_generator import generate_circle_points, points_on_line
from points_printer import plot_path_ascii, plot_points_ascii
from line_renderer import render_path
from preprocessor import invert_image, preprocess_image_edge, bump_contrast, squareizer
from consts import PIXEL_VALUE_SUBTRACT, output_path, output_progress_path
import os
import argparse


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
SOLVE_COMMAND = "solve"
RECONSTRUCT_COMMAND = "reconstruct"


assert 0.0 < LINE_OPACITY <= 1.0, "LINE_OPACITY must be in (0.0, 1.0]"


def parse_args():
    parser = argparse.ArgumentParser(
        description="String art generator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # Arguments for both subcommands
    parser.add_argument(
        "--line_opacity",
        type=float,
        default=LINE_OPACITY,
        help="Opacity of the lines drawn (0.0 to 1.0)",
    )
    parser.add_argument(
        "--num_cords",
        type=int,
        default=NUM_CORDS,
        help="Number of cords to draw. If reconstructing from a path, the number of cords in the path will be truncated to this value, or used entirely if this value is greater than the number of cords in the path",
    )

    # Define subparsers for the two subcommands
    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommand to run")

    parser_solve = subparsers.add_parser(
        SOLVE_COMMAND,
        help="Generate a path and render the image",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser_reconstruct = subparsers.add_parser(
        RECONSTRUCT_COMMAND,
        help="Take a path and render the image",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Arguments for solve subcommand
    parser_solve.add_argument(
        "--points_on_circle",
        type=int,
        default=POINTS_ON_CIRCLE,
        help="Number of points on the circle",
    )
    parser_solve.add_argument(
        "--radius_scale",
        type=float,
        default=RADIUS_SCALE,
        help="Scale of the radius of the circle relative to the image size",
    )
    parser_solve.add_argument(
        "--log_every_n",
        type=int,
        default=LOG_EVERY_N,
        help="Log progress every n cords",
    )
    parser_solve.add_argument(
        "--target_black_pixels",
        action="store_true",
        default=TARGET_BLACK_PIXELS,
        help="If set, will target black pixels instead of white",
    )
    parser_solve.add_argument(
        "--edge_preprocess",
        action="store_true",
        default=EDGE_PREPROCESS,
        help="If set, will preprocess the image to detect edges",
    )
    parser_solve.add_argument(
        "--bump_contrast",
        action="store_true",
        default=BUMP_CONTRAST,
        help="If set, will bump the contrast of the image",
    )
    parser_solve.add_argument(
        "--force_square",
        action="store_true",
        default=FORCE_SQUARE,
        help="If set, will crop the image to a square before processing",
    )
    parser_solve.add_argument(
        "--export_image_every",
        type=int,
        default=EXPORT_IMAGE_EVERY,
        help="Export an intermediate image every n cords",
    )
    parser_solve.add_argument(
        "--min_cord_distance",
        type=int,
        default=MIN_CORD_DISTANCE,
        help="Minimum distance between points on the circle to consider a cord",
    )
    parser_solve.add_argument(
        "image_path",
        type=str,
        help="Path to the input image",
    )

    # Arguments for reconstruct subcommand
    parser_reconstruct.add_argument(
        "path_file",
        type=str,
        help="Path to the file containing the path to reconstruct",
    )

    return parser.parse_args()


def rand_index(num_points):
    if num_points <= 0:
        raise ValueError("num_points must be greater than 0")
    return random.randint(0, num_points - 1)


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


def export_image(path_points, width, height, output_dir, line_opacity):
    # Render the path to an image and save it
    img = render_path(
        path_points,
        image_size=(width, height),
        line_opacity=line_opacity,
    )
    output_path = os.path.join(output_dir, f"output_{len(path_points) - 1}.png")
    img.save(output_path)


def export_path(path_points, output_dir):
    # Export the path to a text file
    with open(os.path.join(output_dir, "path.txt"), "w") as f:
        for point in path_points:
            f.write(f"{point[0]},{point[1]}\n")


def make_dirs(output_dir, progress_dir):
    os.makedirs(output_path(), exist_ok=True)
    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(progress_dir, exist_ok=True)


def reconstruct_image(path_file, output_dir, num_cords, line_opacity):
    # Read the path from the file
    path_points = []
    with open(path_file, "r") as f:
        for line in f:
            x, y = map(float, line.strip().split(","))
            path_points.append((x, y))
            if len(path_points) > num_cords:
                break

    # Render the path to an image and save it
    if not path_points:
        raise ValueError("Path file is empty")
    width = int(max(x for x, y in path_points)) + 1
    height = int(max(y for x, y in path_points)) + 1
    export_image(path_points, width, height, output_dir, line_opacity)


def main():
    args = parse_args()

    if args.command == SOLVE_COMMAND:
        img_path = args.image_path
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        output_dir = output_path(base_name)
        progress_dir = output_progress_path(base_name)
        make_dirs(output_dir, progress_dir)

        if args.target_black_pixels:
            img_path = invert_image(img_path, output_dir)
        if args.edge_preprocess:
            img_path = preprocess_image_edge(img_path, output_dir)
        if args.bump_contrast:
            img_path = bump_contrast(img_path, output_dir)
        if args.force_square:
            img_path = squareizer(img_path, output_dir)
    elif args.command == RECONSTRUCT_COMMAND:
        # dir that the path file is in will be used as the output dir
        output_dir = os.path.dirname(args.path_file)
        reconstruct_image(args.path_file, output_dir, args.num_cords, args.line_opacity)
        return
    else:
        raise ValueError(f"Unknown command: {args.command}")

    image = open_image(img_path)

    assert image.shape[2] == 3, "Image must be RGB"
    (height, width, _) = image.shape
    
    assert width == height, "Image must be square"

    # generate circle of points about center
    center = (width / 2, height / 2)
    radius = width / 2 * args.radius_scale
    num_points = args.points_on_circle
    circ_points = generate_circle_points(center, radius, num_points)

    curr_circ_point = rand_index(num_points)
    path = [curr_circ_point]
    
    start_time = time()
    last_log_time = start_time
    print(f"Starting computation of {args.num_cords} cords")
    for nth_cord in range(args.num_cords):
        # Check that all pixels are not zero
        if not image.any():
            print("All pixels are zero, stopping early")
            break

        best_point, best_value = find_best_cord(
            image, circ_points, curr_circ_point, min_cord_distance=args.min_cord_distance
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
        if (nth_cord + 1) % args.log_every_n == 0:
            print(
                f"Completed {100 * (nth_cord + 1) / args.num_cords}% ({nth_cord + 1} / {args.num_cords}) of total cords in {time() - last_log_time:.2f} seconds"
            )
            last_log_time = time()

        if (nth_cord + 1) % args.export_image_every == 0:
            path_points = [circ_points[i] for i in path]
            export_image(path_points, width, height, progress_dir, args.line_opacity)
            print(
                f"Exported intermediate image at {100 * (nth_cord + 1) / args.num_cords}% ({nth_cord + 1} / {args.num_cords}) of total cords"
            )

    path_points = [circ_points[i] for i in path]
    export_image(path_points, width, height, output_dir, args.line_opacity)
    print("Exported final image")
    export_path(path_points, output_dir)


if __name__ == "__main__":
    main()

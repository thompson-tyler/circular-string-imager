import random
import shutil
import sys
from time import time
from father_timer import FatherTimer
from image_eater import open_image
from line_optimizer import find_best_cord
from point_generator import generate_circle_points, points_on_line
from line_renderer import render_path
from preprocessor import load_image, invert_image, bump_contrast, squareizer, resize_to_max, export_adjusted_image
from consts import ARCHIVE_DIR, PIXEL_VALUE_SUBTRACT, LINE_OPACITY, NUM_CORDS, POINTS_ON_CIRCLE, RADIUS_SCALE, LOG_EVERY_N, TARGET_BLACK_PIXELS, BUMP_CONTRAST, FORCE_SQUARE, EXPORT_IMAGE_EVERY, MIN_CORD_DISTANCE, DEFAULT_MAX_SIZE, output_path, output_progress_path
import os
import argparse
import matplotlib.pyplot as plt


RECONSTRUCT_COMMAND = "reconstruct"
SOLVE_COMMAND = "solve"


assert 0.0 < LINE_OPACITY <= 1.0, "LINE_OPACITY must be in (0.0, 1.0]"


def parse_args():
    parser = argparse.ArgumentParser(
        description="String art generator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # Arguments for both subcommands
    parser.add_argument(
        "--line-opacity",
        type=float,
        default=LINE_OPACITY,
        help="Opacity of the lines drawn (0.0 to 1.0)",
    )
    parser.add_argument(
        "--num-cords",
        type=int,
        default=NUM_CORDS,
        help="Number of cords to draw. If reconstructing from a path, the number of cords in the path will be truncated to this value, or used entirely if this value is greater than the number of cords in the path",
    )
    parser.add_argument(
        "--max-size",
        type=int,
        default=DEFAULT_MAX_SIZE,
        metavar="PIXELS",
        help="Maximum input image edge size; image is downscaled to fit within a square",
    )
    parser.add_argument(
        "--pixel-value-subtract",
        type=int,
        default=PIXEL_VALUE_SUBTRACT,
        help="Amount subtracted from each RGB channel along a selected cord",
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
        "--points-on-circle",
        type=int,
        default=POINTS_ON_CIRCLE,
        help="Number of points on the circle",
    )
    parser_solve.add_argument(
        "--radius-scale",
        type=float,
        default=RADIUS_SCALE,
        help="Scale of the radius of the circle relative to the image size",
    )
    parser_solve.add_argument(
        "--log-every-n",
        type=int,
        default=LOG_EVERY_N,
        help="Log progress every n cords",
    )
    parser_solve.add_argument(
        "--target-black-pixels",
        action="store_true",
        default=TARGET_BLACK_PIXELS,
        help="If set, will target black pixels instead of white",
    )
    parser_solve.add_argument(
        "--bump-contrast",
        action="store_true",
        default=BUMP_CONTRAST,
        help="If set, will bump the contrast of the image",
    )
    parser_solve.add_argument(
        "--force-square",
        action="store_true",
        default=FORCE_SQUARE,
        help="If set, will crop the image to a square before processing",
    )
    parser_solve.add_argument(
        "--export-image-every",
        type=int,
        default=EXPORT_IMAGE_EVERY,
        help="Export an intermediate image every n cords",
    )
    parser_solve.add_argument(
        "--min-cord-distance",
        type=int,
        default=MIN_CORD_DISTANCE,
        help="Minimum distance between points on the circle to consider a cord",
    )
    parser_solve.add_argument(
        "--multi-threaded",
        action="store_true",
        help="If set, will use multi-threading to evaluate points on the circle",
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


def make_dirs(output_dir, progress_dir):
    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(progress_dir, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)


def export_image(path_points, width, height, output_dir, line_opacity):
    # Render the path to an image and save it
    img = render_path(
        path_points,
        image_size=(width, height),
        line_opacity=line_opacity,
    )
    output_path = os.path.join(output_dir, f"output_{len(path_points) - 1}.png")
    img.save(output_path)
    return output_path


def export_path(path_points, output_dir):
    # Export the path to a text file
    with open(os.path.join(output_dir, "path.txt"), "w") as f:
        for point in path_points:
            f.write(f"{point[0]},{point[1]}\n")


def export_best_values_graph(best_values, output_dir):
    plt.figure(figsize=(10, 5))
    plt.plot(best_values, marker="o", markersize=2)
    plt.title("Best Values Over Time")
    plt.xlabel("Cord Number")
    plt.ylabel("Best Value")
    plt.grid()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "best_values.png"))
    plt.close()


# Saves an image to the archive directory with a log of the parameters used to generate it
def archive_image(image_path, image_name, args):
    # copy image into archive dir with timestamp
    timestamp = int(time())
    filename = f"{timestamp}_{image_name}"
    shutil.copy(image_path, os.path.join(ARCHIVE_DIR, filename))
    # append parameters to a text file in the archive dir
    with open(os.path.join(ARCHIVE_DIR, "archive_log.txt"), "a") as f:
        f.write(f"Image: {filename}\n")
        f.write(f"Parameters:\n")
        for arg in vars(args):
            f.write(f"  {arg}: {getattr(args, arg)}\n")
        f.write("\n")


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


def time_remaining(elapsed_time, total_cords, cords_completed):
    if cords_completed == 0:
        return float("inf")
    estimated_total_time = (elapsed_time / cords_completed) * total_cords
    return estimated_total_time - elapsed_time


def format_time(seconds):
    if seconds < 60:
        return f"{seconds:.2f} s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        seconds = seconds % 60
        return f"{minutes} m, {seconds:.2f} s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours} h, {minutes} m, {seconds:.2f} s"


def main():
    args = parse_args()

    if args.command == SOLVE_COMMAND:
        original_file_name = os.path.basename(args.image_path)
        base_name = os.path.splitext(os.path.basename(args.image_path))[0]
        output_dir = output_path(base_name)
        progress_dir = output_progress_path(base_name)
        make_dirs(output_dir, progress_dir)

        preprocessed_img = load_image(args.image_path)
        if args.target_black_pixels:
            preprocessed_img = invert_image(preprocessed_img)
        if args.bump_contrast:
            preprocessed_img = bump_contrast(preprocessed_img)
        if args.force_square:
            preprocessed_img = squareizer(preprocessed_img)
        preprocessed_img = resize_to_max(preprocessed_img, (args.max_size, args.max_size))

        adjusted_image_path = export_adjusted_image(preprocessed_img, args.image_path, output_dir)
    elif args.command == RECONSTRUCT_COMMAND:
        # dir that the path file is in will be used as the output dir
        output_dir = os.path.dirname(args.path_file)
        reconstruct_image(args.path_file, output_dir, args.num_cords, args.line_opacity)
        return
    else:
        raise ValueError(f"Unknown command: {args.command}")

    image = open_image(adjusted_image_path)

    assert len(image.shape) == 2, "Image must be grayscale"
    (height, width) = image.shape
    
    assert width == height, "Image must be square"

    # generate circle of points about center
    center = (width / 2, height / 2)
    radius = width / 2 * args.radius_scale
    num_points = args.points_on_circle
    circ_points = generate_circle_points(center, radius, num_points)

    curr_circ_point = rand_index(num_points)
    path = [curr_circ_point]
    
    print(f"Threading: {'enabled' if args.multi_threaded else 'disabled'}; GIL: {'enabled' if sys._is_gil_enabled() else 'disabled'}")
    print(f"Starting computation of {args.num_cords} cords")

    ft = FatherTimer()
    best_values = []
    for nth_cord in range(args.num_cords):
        # Check that all pixels are not zero
        if not image.any():
            print("All pixels are zero, stopping early")
            break

        with ft.timer("Computing best cord"):
            best_point, best_value = find_best_cord(
                image, circ_points, curr_circ_point, min_cord_distance=args.min_cord_distance, threaded=args.multi_threaded
            )
        path.append(best_point)
        best_values.append(best_value)

        with ft.timer("Adjusting pixel values along cord"):
            # Subtract a small value from the points along the cord to encourage exploration
            point_generator = points_on_line(
                circ_points[curr_circ_point], circ_points[best_point]
            )
            for point in point_generator:
                ix, iy = int(round(point[0])), int(round(point[1]))
                if 0 <= ix < image.shape[1] and 0 <= iy < image.shape[0]:
                    val = image[iy, ix]
                    val = clamp(int(val) - args.pixel_value_subtract, 0, 255)
                    image[iy, ix] = val

        curr_circ_point = best_point
        if (nth_cord + 1) % args.log_every_n == 0:
            lap_time = ft.lap()
            time_remaining_estimate = time_remaining(ft.elapsed_time(), args.num_cords, nth_cord + 1)
            print(
                f"Completed {100 * (nth_cord + 1) / args.num_cords}% ({nth_cord + 1} / {args.num_cords}) of " +
                f"total cords in {FatherTimer.format_time(lap_time)} (estimated time remaining: " +
                f"{FatherTimer.format_time(time_remaining_estimate)})"
            )

        if args.export_image_every is not None and (nth_cord + 1) % args.export_image_every == 0:
            with ft.timer("Exporting intermediate image"):
                path_points = [circ_points[i] for i in path]
                export_image(path_points, width, height, progress_dir, args.line_opacity)

    ft.report()

    path_points = [circ_points[i] for i in path]
    final_image_path = export_image(path_points, width, height, output_dir, args.line_opacity)
    export_path(path_points, output_dir)
    export_best_values_graph(best_values, output_dir)
    archive_image(final_image_path, original_file_name, args)


if __name__ == "__main__":
    main()

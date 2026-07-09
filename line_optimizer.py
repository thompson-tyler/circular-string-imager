import sys

from consts import PIXEL_VALUE_SUBTRACT
from point_generator import points_on_line
from concurrent.futures import ThreadPoolExecutor


# For each point in points, takes the RGB value from the image and sums its components.
# Returns the average sum.
def value_of_points(image, points) -> float:
    avg = 0.0
    num_points = 0
    [y_max, x_max] = image.shape
    for x, y in points:
        if 0 <= x < x_max and 0 <= y < y_max:
            val = int(image[y, x])
            # Compute potental effect of adjusting pixel values
            val_adj = (
                PIXEL_VALUE_SUBTRACT
                if val >= PIXEL_VALUE_SUBTRACT
                else val - PIXEL_VALUE_SUBTRACT
            )
            num_points += 1
            avg += (val_adj - avg) / num_points

    return avg


# Find the cord from the current point to another point on the circle with the highest value
def find_best_cord(image, circ_points, curr_circ_point, min_cord_distance=None, threaded=False):
    if threaded and sys._is_gil_enabled():
        print("Warning: Multi-threading is enabled, but the GIL is active.")

    num_points = len(circ_points)

    def evaluate_point(i: int):
        if i == curr_circ_point:
            return (i, float("-inf"))
        if min_cord_distance:
            direct_distance = abs(i - curr_circ_point)
            circular_distance = min(direct_distance, num_points - direct_distance)
            if circular_distance < min_cord_distance:
                return (i, float("-inf"))
        point_generator = points_on_line(
            circ_points[curr_circ_point], circ_points[i]
        )
        value = value_of_points(image, point_generator)
        return (i, value)

    best_value = float("-inf")
    best_point = None

    if threaded:
        with ThreadPoolExecutor() as executor:
            results = executor.map(evaluate_point, range(num_points), chunksize=10)
    else:
        results = map(evaluate_point, range(num_points))

    (best_point, best_value) = max(results, key=lambda t: t[1])
    
    return best_point, best_value

# Find the cord from the current point to another point on the circle with the highest value
from consts import BOOST_FOR_MORE_POINTS, PIXEL_VALUE_SUBTRACT
from point_generator import points_on_line


assert PIXEL_VALUE_SUBTRACT > 0, "PIXEL_VALUE_SUBTRACT must be positive"

def bonus_for_more_points(num_points: int) -> float:
    return num_points / 2000.0

# For each point in points, takes the RGB value from the image and sums its components.
# Returns the average sum.
def value_of_points(image, points) -> float:
    avg = 0.0
    num_points = 0
    for x, y in points:
        ix, iy = int(round(x)), int(round(y))
        if 0 <= ix < image.shape[1] and 0 <= iy < image.shape[0]:
            r, g, b = map(int, image[iy, ix])
            # Compute potental effect of adjusting pixel values
            r_adj = (
                PIXEL_VALUE_SUBTRACT
                if r >= PIXEL_VALUE_SUBTRACT
                else r - PIXEL_VALUE_SUBTRACT
            )
            g_adj = (
                PIXEL_VALUE_SUBTRACT
                if g >= PIXEL_VALUE_SUBTRACT
                else g - PIXEL_VALUE_SUBTRACT
            )
            b_adj = (
                PIXEL_VALUE_SUBTRACT
                if b >= PIXEL_VALUE_SUBTRACT
                else b - PIXEL_VALUE_SUBTRACT
            )
            num_points += 1
            value = r_adj + g_adj + b_adj
            avg += (value - avg) / num_points

    # Give a small bonus for more points
    if BOOST_FOR_MORE_POINTS and num_points > 0:
        avg += bonus_for_more_points(num_points)
    return avg


def find_best_cord(image, circ_points, curr_circ_point, min_cord_distance=None):
    best_value = float("-inf")
    best_point = None
    num_points = len(circ_points)
    for i in range(num_points):
        if i == curr_circ_point:
            continue
        if min_cord_distance and abs(i - curr_circ_point) < min_cord_distance:
            continue
        point_generator = points_on_line(
            circ_points[curr_circ_point], circ_points[i]
        )
        value = value_of_points(image, point_generator)
        if value > best_value:
            best_value = value
            best_point = i
    assert best_point is not None
    return best_point, best_value

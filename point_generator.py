import math

type Point = tuple[float, float]


def generate_circle_points(
    center: Point, radius: float, num_points: int
) -> list[Point]:
    points: list[Point] = []
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        points.append((x, y))
    return points


def points_on_line(p0: tuple[float, float], p1: tuple[float, float]):
    def steep():  # -> Generator[tuple[Any, int], Any, None]:
        for y in range(min(y0, y1), max(y0, y1) + 1):
            x = x0 + (y - y0) / slope
            yield (round(x), y)

    def shallow():
        for x in range(min(x0, x1), max(x0, x1) + 1):
            y = y0 + slope * (x - x0)
            yield (x, round(y))

    def vertical():
        for y in range(min(y0, y1), max(y0, y1) + 1):
            yield (x0, y)

    x0, y0 = map(round, p0)
    x1, y1 = map(round, p1)

    slope = (y1 - y0) / (x1 - x0) if x1 != x0 else float("inf")

    # line is vertical
    if slope == float("inf"):
        yield from vertical()
    # line is steep
    elif abs(slope) > 1:
        yield from steep()
    # line is shallow
    else:
        yield from shallow()

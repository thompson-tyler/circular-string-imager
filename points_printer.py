from point_generator import points_on_line


class Grid:
    def __init__(self, points):
        self.points = list(points)
        xs, ys = zip(*self.points)
        self.min_x, self.max_x = round(min(xs)), round(max(xs))
        self.min_y, self.max_y = round(min(ys)), round(max(ys))
        self.grid = [
            [" " for _ in range(self.min_x, self.max_x + 1)]
            for _ in range(self.min_y, self.max_y + 1)
        ]
        for x, y in self.points:
            x, y = round(x), round(y)
            self.grid[y - self.min_y][x - self.min_x] = "*"

    def add_point(self, point, char="*"):
        x, y = map(round, point)
        if self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y:
            self.grid[y - self.min_y][x - self.min_x] = char

    def add_points(self, points):
        for point in points:
            self.add_point(point)

    def display(self):
        print(self.min_x, " " * (self.max_x - self.min_x - 1), self.max_x)
        print("-" * (self.max_x - self.min_x + 3), end=" ")
        print(self.max_y)
        for row in self.grid:
            print("|", end="")
            print("".join(row), end="")
            print("|")
        print("-" * (self.max_x - self.min_x + 3), end=" ")
        print(self.min_y)


def plot_points_ascii(points, p0=None, p1=None):
    if not points:
        print("No points to plot")
        return
    points = list(points)
    grid = Grid(points)

    if p0 is not None:
        p0 = tuple(map(round, p0))
        grid.add_point(p0, char="S")  # Start point
    if p1 is not None:
        p1 = tuple(map(round, p1))
        grid.add_point(p1, char="E")  # End point

    grid.display()


def plot_path_ascii(path_points, base_points=None):
    if not path_points:
        print("No path points to plot")
        return
    path_points = list(path_points)
    grid = Grid(base_points) if base_points else Grid(path_points)

    for p0, p1 in zip(path_points, path_points[1:]):
        line_points = points_on_line(p0, p1)
        grid.add_points(line_points)

    grid.display()

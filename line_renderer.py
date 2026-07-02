from matplotlib import pyplot as plt
from io import BytesIO
from PIL import Image


# Draw an image with the given paths using matplotlib
def render_path(
    path_points: list[tuple[float, float]],
    image_size: tuple[int, int],
    background_color="white",
    line_opacity=1.0,
):
    fig, ax = plt.subplots(figsize=(image_size[0] / 25, image_size[1] / 25), dpi=100)
    ax.set_xlim(0, image_size[0])
    ax.set_ylim(0, image_size[1])
    ax.invert_yaxis()  # Invert y-axis to match image coordinates
    ax.axis("off")  # Hide axes

    # Set background color
    fig.patch.set_facecolor(background_color)
    ax.set_facecolor(background_color)

    # Draw each segment individually so overlaps accumulate
    for p0, p1 in zip(path_points, path_points[1:]):
        ax.plot(
            [p0[0], p1[0]],
            [p0[1], p1[1]],
            color="black",
            linewidth=1,
            alpha=line_opacity,
            solid_capstyle="round",
        )

    # Save the figure to a PIL Image in memory
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
    buf.seek(0)
    img = Image.open(buf).convert("RGBA")
    buf.close()
    plt.close(fig)

    return img

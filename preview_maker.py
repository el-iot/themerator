import sys
import cv2
import numpy

from PIL import Image
from tqdm import tqdm

colours = [
    (26, 26, 26),
    (216, 133, 104),
    (131, 164, 113),
    (185, 147, 83),
    (142, 204, 221),
    (185, 142, 178),
    (124, 156, 174),
    (204, 204, 204),
    (118, 118, 118),
    (248, 248, 248),
    (216, 104, 104),
    (139, 108, 55),
    (34, 34, 34),
    (29, 65, 77),
    (184, 184, 184),
    (232, 232, 232),
    (204, 204, 204),
    (26, 26, 26),
]


def get_nearest(point):
    return sorted(
        colours,
        key=lambda x: abs(x[0] - point[0])
        + abs(x[1] - point[1])
        + abs(x[2] - point[2]),
    )[0]


def make_preview(scale, name):

    image = cv2.imread(name)
    height, width, _ = image.shape

    height //= scale
    width //= scale

    image = cv2.resize(image, (width, height))

    for py in tqdm(range(height)):
        for px in range(width):
            input_color = (image[py][px][0], image[py][px][1], image[py][px][2])
            nearest_color = get_nearest(input_color)

            image[py][px][0] = nearest_color[0]
            image[py][px][1] = nearest_color[1]
            image[py][px][2] = nearest_color[2]

    n_distinct = len(set([tuple(i) for j in image.tolist() for i in j]))

    print(f'Rendered to {n_distinct} distinct colours')

    Image.fromarray(image).save(name.replace(".png", "") + "_preview.png")


if __name__ == "__main__":

    scale = int(sys.argv[1])
    name = sys.argv[2]
    make_preview(scale, name)

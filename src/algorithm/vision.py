import cv2
from vision2 import find_color
from vision2 import camera_convert

CAMERA_STATE = camera_convert.CameraState((309, 0, -218), (52.8, 2.1, 0.4), (62.2, 62), (640, 480))


def process(image) -> ...:

    if image is None:
        return None

    reds_in_image = find_color.find_red(image)
    yellows_in_image = find_color.find_yellow(image)
    walls_in_image = find_color.find_wall_bottom_p(image)

    reds = []
    yellows = []
    walls = []

    for red in reds_in_image:
        s, x, y = camera_convert.img2space(CAMERA_STATE, red[0], red[1], -12.5)
        if s:
            reds.append((x, y))

    for yellow in yellows_in_image:
        s, x, y = camera_convert.img2space(CAMERA_STATE, yellow[0], yellow[1], -15)
        if s:
            yellows.append((x, y))

    if walls_in_image is not None:
        walls = [(camera_convert.img2space(CAMERA_STATE, wall[0][0], wall[0][1])[1:],
                  camera_convert.img2space(CAMERA_STATE, wall[0][2], wall[0][3])[1:]
                  ) for wall in walls_in_image]

    return reds, yellows, walls

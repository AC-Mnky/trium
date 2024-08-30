import cv2

try:
    import camera_convert
    import find_color
except ModuleNotFoundError:
    import os
    import sys

    work_path = os.getcwd()
    sys.path.append(f"{work_path}/algorithm")
    try:
        import camera_convert
        import find_color
    except ModuleNotFoundError:

        work_path = os.getcwd()
        sys.path.append(f"{work_path}/../algorithm")
        import camera_convert
        import find_color

else:
    ...


CAMERA_STATE = camera_convert.CameraState(
    # (309, 0, -218), (52.8, 2.1, 0.4), (62.2, 62), (640, 480)
    # (295, 12, -221), (57.7, 1.1, 0.3), (51.45, 51.09), (640, 480)
    # (295, 12, -221), (57.7, 1.1, 0.3), (51.45, 51.09), (640, 480)
    # (84, 4, -243), (59.4, 1.1, -0.1), (51.45, 51.09), (640, 480)
    # (78, 13, -164), (69.4, 1., 0.5), (47.66, 33.90), (640, 480)
    (78, 13, -164),
    (69.4, 1.0, 0.5),
    (47.66, 33.90),
    (320, 240),
)


def process(
    time: float, image: cv2.UMat | None
) -> (
    tuple[
        float,
        list[tuple[float, float]],
        list[tuple[float, float]],
        list[tuple[tuple[float, float], tuple[float, float]]],
    ]
    | None
):
    """
    Process the given image to extract relevant information.

    Args:
        time (float): The time associated with the image.
        image (cv2.UMat): The image to be processed.

    Returns:
        tuple: A tuple containing the following information or None:
            - time (float): The time associated with the image.
            - reds (list): A list of red points found in the image.
            - yellows (list): A list of yellow points found in the image.
            - walls (list): A list of wall segments found in the image.
            - If the image is None, None is returned.
    """
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
        walls = [
            (
                camera_convert.img2space(CAMERA_STATE, wall[0][0], wall[0][1])[1:],
                camera_convert.img2space(CAMERA_STATE, wall[0][2], wall[0][3])[1:],
            )
            for wall in walls_in_image
        ]

    return time, reds, yellows, walls

import cv2
import numpy as np

RED1 = np.array(((0, 75, 50), (10, 255, 255)))
RED2 = np.array(((165, 75, 50), (180, 255, 255)))

YELLOW = np.array(((10, 100, 50), (35, 255, 255)))

BLUE = np.array(((100, 100, 25), (125, 255, 255)))

WHITE = np.array(((0, 0, 25), (180, 100, 255)))

SHIFT1_ONLY_UP_SHIFT = True
WALL_SHIFT1 = 5  # 10
ENABLE_WALL_SHIFT2 = True
WALL_SHIFT2 = 1
HOUGH_THRESHOLD = 180

HOUGH_P_THRESHOLD = 50
HOUGH_P_MIN_LENGTH = 20
HOUGH_P_MAX_GAP = 100

SHOW_BLUE = True
SHOW_WHITE = True
SHOW_LINE = True


def get_color_mask(
    image: np.ndarray, color_range_list: list[np.ndarray], show: bool = False, color_name: str = "color"
) -> np.ndarray:
    """
    Generate a color mask for the given image based on the specified color range list.

    Args:
        image (np.ndarray): The input image.
        color_range_list (list[np.ndarray]): A list of color ranges in the HSV color space.
        show (bool, optional): Whether to display the color mask. Defaults to False.
        color_name (str, optional): The name of the color. Defaults to "color".

    Returns:
        output (np.ndarray): The color mask.
    """
    x = image
    # x = cv2.GaussianBlur(image, (3, 3), 0)
    x = cv2.cvtColor(x, cv2.COLOR_BGR2HSV)

    if len(color_range_list) == 1:
        x = cv2.inRange(x, color_range_list[0][0], color_range_list[0][1])
    elif len(color_range_list) == 2:
        x = np.maximum(
            cv2.inRange(x, color_range_list[0][0], color_range_list[0][1]),
            cv2.inRange(x, color_range_list[1][0], color_range_list[1][1]),
        )
    else:
        x = np.max(
            np.stack([cv2.inRange(x, color_range[0], color_range[1]) for color_range in color_range_list]), 0
        )

    # x = cv2.erode(x, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)), iterations=1)
    # x = cv2.dilate(x, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)), iterations=1)
    output = x

    if show:
        cv2.imshow(color_name, cv2.cvtColor(output, cv2.COLOR_GRAY2BGR))

    return output


def find_color(
    image: np.ndarray, color_range_list: list[np.ndarray], show: bool = False, color_name: str = "color"
) -> tuple[np.ndarray, list[tuple[float, float]]]:
    """
    Find the coordinates of colored objects in an image.

    Args:
        image (np.ndarray): The input image.
        color_range_list (list[np.ndarray]): A list of color ranges to search for in the image.
        show (bool, optional): Whether to display intermediate images. Defaults to False.
        color_name (str, optional): The name of the color being searched for. Defaults to "color".

    Returns:
        points (list[(int, int)]): A list of coordinates (x, y) of the colored objects found in the image.
    """
    output = get_color_mask(image, color_range_list, show, color_name)

    contours = cv2.findContours(output, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    points = []
    for c in contours:
        m = cv2.moments(c)
        if m["m00"] > 25:  # 100:
            cx = int(m["m10"] / m["m00"])
            cy = int(m["m01"] / m["m00"])
            points.append((cx, cy))

    return output, points


def find_red(image: np.ndarray, show: bool = False) -> tuple[np.ndarray, list[tuple[float, float]]]:
    """
    Find the coordinates of red pixels in the given image.

    Args:
        image (np.ndarray): The image to search for red pixels.
        show (bool, optional): Whether to display the image with red pixels highlighted. Default is False.

    Returns:
        points (list[(int, int)]): A list of coordinates (row, column) of red pixels in the image.
    """
    return find_color(image, [RED1, RED2], show, "red")


def find_yellow(image: np.ndarray, show: bool = False) -> tuple[np.ndarray, list[tuple[float, float]]]:
    """
    Find the coordinates of yellow pixels in the given image.

    Args:
        image (np.ndarray): The image to search for yellow pixels.
        show (bool, optional): Whether to display the image with yellow pixels highlighted. Default is False.

    Returns:
        points (list[(int, int)]): A list of coordinates (row, column) of yellow pixels in the image.
    """
    return find_color(image, [YELLOW], show, "yellow")


def show_blue(image: np.ndarray) -> None:
    """
    Show the blue color in the given image.

    Args:
        image (np.ndarray): the image to display.

    Returns:
        None
    """
    get_color_mask(image, [BLUE], True, "blue")


def show_white(image: np.ndarray) -> None:
    """
    Show the white color in the given image.

    Args:
        image (np.ndarray): The image to process.

    Returns:
        None
    """
    get_color_mask(image, [WHITE], True, "white")


def find_wall_bottom(image: np.ndarray, show: bool = False) -> tuple[np.ndarray, np.ndarray, list]:
    """
    Find the bottom of the given walls in an image, cv2.HoughLines() version.

    Args:
        image (np.ndarray): The input image.
        show (bool, optional): Whether to display intermediate images. Defaults to False.

    Returns:
        blue: Mask of blue.
        white: Mask of white.
        lines: The detected lines using Hough transform.
    """
    blue = get_color_mask(image, [BLUE])
    white = get_color_mask(image, [WHITE])

    if SHOW_BLUE and show:
        cv2.imshow("blue", blue)
    if SHOW_WHITE and show:
        cv2.imshow("white", white)

    x = np.zeros(image.shape[:2]).astype(np.uint8)

    x[WALL_SHIFT1:-WALL_SHIFT1, :] = np.minimum(blue[: -2 * WALL_SHIFT1, :], white[2 * WALL_SHIFT1 :, :])
    if ENABLE_WALL_SHIFT2:
        x[WALL_SHIFT2:-WALL_SHIFT2, :] = np.minimum(x[: -2 * WALL_SHIFT2, :], (255 - x)[2 * WALL_SHIFT2 :, :])

    draw = cv2.cvtColor(x, cv2.COLOR_GRAY2BGR)

    lines = cv2.HoughLines(x, 1, np.pi / 180, HOUGH_THRESHOLD)

    if lines is None:
        lines = []

    # print(lines)
    if SHOW_LINE and lines is not None:
        for line in lines:
            rho, theta = line[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * a)
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * a)
            cv2.line(draw, (x1, y1), (x2, y2), (255, 0, 0), 1)

    if show:
        cv2.imshow("wall bottom", draw)

    return blue, white, lines


def find_wall_bottom_p(image: np.ndarray, show: bool = False) -> tuple[np.ndarray, np.ndarray, list]:
    """
    Find the bottom of wall lines in an image, cv2.HoughLinesP() version.

    Args:
        image (np.ndarray): The input image.
        show (bool, optional): Whether to display intermediate images. Defaults to False.

    Returns:
        blue: Mask of blue.
        white: Mask of white.
        lines: A list of line coordinates (x1, y1, x2, y2) if lines are found, None otherwise.
    """
    blue = get_color_mask(image, [BLUE])
    white = get_color_mask(image, [WHITE])

    if SHOW_BLUE and show:
        cv2.imshow("blue", blue)
    if SHOW_WHITE and show:
        cv2.imshow("white", white)

    x = np.zeros(image.shape[:2]).astype(np.uint8)

    if SHIFT1_ONLY_UP_SHIFT:
        x[0:-WALL_SHIFT1, :] = np.minimum(blue[:-WALL_SHIFT1, :], white[WALL_SHIFT1:, :])
    else:
        x[WALL_SHIFT1:-WALL_SHIFT1, :] = np.minimum(blue[: -2 * WALL_SHIFT1, :], white[2 * WALL_SHIFT1 :, :])

    if ENABLE_WALL_SHIFT2:
        x[WALL_SHIFT2:-WALL_SHIFT2, :] = np.minimum(x[: -2 * WALL_SHIFT2, :], (255 - x)[2 * WALL_SHIFT2 :, :])

    draw = cv2.cvtColor(x, cv2.COLOR_GRAY2BGR)

    lines = cv2.HoughLinesP(
        x, 1, np.pi / 180, HOUGH_P_THRESHOLD, minLineLength=HOUGH_P_MIN_LENGTH, maxLineGap=HOUGH_P_MAX_GAP
    )

    if lines is None:
        lines = []

    # print(lines)
    if SHOW_LINE and lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(draw, (x1, y1), (x2, y2), (255, 0, 0), 1)

    if show:
        cv2.imshow("wall bottom", draw)

    return blue, white, lines


def find_bounding_rect_in_mask(mask: np.ndarray, show: bool = False) -> list[tuple[int, int, int, int]]:
    """
    Finds the bounding rectangles in a given mask.

    Args:
        mask (np.ndarray): The input mask image.
        show (bool, optional): Whether to show the result. Defaults to False.

    Returns:
        rects (list[tuple[int, int, int, int]]): A list of tuples representing the bounding rectangles.
    """
    contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    rects = []
    for c in contours:
        if cv2.contourArea(c) < 10:
            continue
        x, y, w, h = cv2.boundingRect(c)
        rects.append((x, y, w, h))

    return rects

    # m = cv2.moments(c)
    # if m["m00"] > 25:  # 100:
    #     cx = int(m["m10"] / m["m00"])
    #     cy = int(m["m01"] / m["m00"])
    #     points.append((cx, cy))

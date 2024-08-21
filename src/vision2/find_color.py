import cv2
import numpy as np


RED = [np.array(((0, 130, 100), (10, 255, 255))),
       np.array(((165, 130, 100), (180, 255, 255)))]

YELLOW = [np.array(((15, 130, 50), (35, 255, 255)))]

BLUE = [np.array(((100, 50, 50), (115, 255, 255)))]

WHITE = [np.array(((0, 0, 100), (180, 50, 255)))]

WALL_SHIFT1 = 2
WALL_SHIFT2 = 1
HOUGH_THRESHOLD = 140


def get_color_mask(image: np.ndarray, color_range_list: list[np.ndarray], show: bool = False, color_name: str = 'color'):

    x = cv2.GaussianBlur(image, (3, 3), 0)
    x = cv2.cvtColor(x, cv2.COLOR_BGR2HSV)

    y = np.zeros(image.shape[:2]).astype(np.uint8)
    for color_range in color_range_list:
        y = np.maximum(y, cv2.inRange(x, color_range[0], color_range[1]))
    x = y

    x = cv2.erode(x, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)), iterations=1)
    x = cv2.dilate(x, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=1)
    output = x

    if show:
        cv2.imshow(color_name, cv2.cvtColor(output, cv2.COLOR_GRAY2BGR))

    return output


def find_color(image: np.ndarray, color_range_list: list[np.ndarray], show: bool = False, color_name: str = 'color')\
        -> list[(int, int)]:

    output = get_color_mask(image, color_range_list, show, color_name)

    contours = cv2.findContours(output, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    points = []
    for c in contours:
        m = cv2.moments(c)
        if m['m00'] > 100:
            cx = int(m['m10'] / m['m00'])
            cy = int(m['m01'] / m['m00'])
            points.append((cx, cy))

    return points


def find_red(image: np.ndarray, show: bool = False) -> list[(int, int)]:
    return find_color(image, RED, show, 'red')


def find_yellow(image: np.ndarray, show: bool = False) -> list[(int, int)]:
    return find_color(image, YELLOW, show, 'yellow')


def show_blue(image: np.ndarray) -> None:
    get_color_mask(image, BLUE, True, 'blue')


def show_white(image: np.ndarray) -> None:
    get_color_mask(image, WHITE, True, 'white')


def find_wall_bottom(image: np.ndarray):
    blue = get_color_mask(image, BLUE)
    white = get_color_mask(image, WHITE)

    x = np.zeros(image.shape[:2]).astype(np.uint8)
    y = np.zeros(image.shape[:2]).astype(np.uint8)

    x[WALL_SHIFT1:-WALL_SHIFT1, :] = np.minimum(blue[:-2 * WALL_SHIFT1, :], white[2 * WALL_SHIFT1:, :])
    y[WALL_SHIFT2:-WALL_SHIFT2, :] = np.minimum(x[:-2 * WALL_SHIFT2, :], (255 - x)[2 * WALL_SHIFT2:, :])

    draw = cv2.cvtColor(y, cv2.COLOR_GRAY2BGR)

    lines = cv2.HoughLines(y, 1, np.pi / 180, HOUGH_THRESHOLD)

    # print(lines)
    if lines is not None:
        for l in lines:
            rho, theta = l[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * a)
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * a)
            cv2.line(draw, (x1, y1), (x2, y2), (255, 0, 0), 1)

    cv2.imshow('wall bottom', draw)

    return lines








import cv2
import numpy as np


def find_color(image: np.ndarray, color_range_list: list[np.ndarray], show: bool = False, color_name: str = 'color')\
        -> list[(int, int)]:

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
    return find_color(image, [np.array(((0, 130, 100), (10, 255, 255))),
                              np.array(((165, 130, 100), (180, 255, 255)))], show, 'red')


def find_yellow(image: np.ndarray, show: bool = False) -> list[(int, int)]:
    return find_color(image, [np.array(((15, 130, 50), (35, 255, 255)))], show, 'yellow')

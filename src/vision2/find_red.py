import cv2
import numpy as np


def find_red(image: np.ndarray) -> list[(int, int)]:
    # print(image.shape)

    # average_color = np.average(image, (0, 1))
    # print(average_color)
    #
    # img_blur = cv2.blur(image, (50, 50))
    # image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # img_blur_hsv = cv2.cvtColor(img_blur, cv2.COLOR_BGR2HSV)
    # x = np.maximum(np.subtract(image, img_blur, dtype=int), 0).astype(np.uint8)
    # y = np.maximum(np.subtract(image_hsv, img_blur_hsv, dtype=int), 0).astype(np.uint8)
    # z = image_hsv - img_blur_hsv
    #
    # double_saturation = np.array((((1, 2, 1), ), ))
    #
    # cv2.imshow('im', np.array(cv2.cvtColor(np.minimum(image_hsv * double_saturation, 255).astype(np.uint8),
    # cv2.COLOR_HSV2BGR)))

    target_color_1 = np.array(((0, 130, 100), (10, 255, 255)))
    target_color_2 = np.array(((165, 130, 100), (180, 255, 255)))
    gs = cv2.GaussianBlur(image, (3, 3), 0)
    hsv = cv2.cvtColor(gs, cv2.COLOR_BGR2HSV)
    erode_hsv = cv2.erode(hsv, None, iterations=1)
    in_range_hsv_1 = cv2.inRange(erode_hsv, target_color_1[0], target_color_1[1])
    in_range_hsv_2 = cv2.inRange(erode_hsv, target_color_2[0], target_color_2[1])
    in_range_hsv = np.maximum(in_range_hsv_1, in_range_hsv_2)
    cv2.imshow('im', cv2.cvtColor(in_range_hsv, cv2.COLOR_GRAY2BGR))

    cnts = cv2.findContours(in_range_hsv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    points = []
    for c in cnts:
        if cv2.contourArea(c) > 100:
            m = cv2.moments(c)
            cx = int(m['m10'] / m['m00'])
            cy = int(m['m01'] / m['m00'])
            points.append((cx, cy))

    return points

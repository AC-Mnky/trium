import cv2
import numpy as np
import os.path

import find_color
import camera_convert

MODE = 'file'
# MODE = 'camera'
GLOBAL_SHOW = True
MASK_SHOW = False
READ_DIR = 'wall4'
WRITE_DIR = 'wall5'

CAMERA_STATE = camera_convert.CameraState((230, 0, -180), (90 - 27, 0), (62.2, 48.8), (640, 480))

SHOW_RED = SHOW_YELLOW = True
SHOW_WALL = True
DRAW_GRID = True

USE_HOUGH_P = True

if MODE == 'camera':
    from camera import Camera


def process(img, show: bool = False):
    points_red = find_color.find_red(img, show and MASK_SHOW)
    points_yellow = find_color.find_yellow(img, show and MASK_SHOW)
    walls = find_color.find_wall_bottom_p(img, show and MASK_SHOW) if USE_HOUGH_P else \
        find_color.find_wall_bottom(img, show and MASK_SHOW)

    if DRAW_GRID:
        draw_grid((255, 255, 255, 255), 0, 2000, 50, -1000, 1000, 50)

    print()

    if SHOW_RED:
        for p in points_red:
            s, x, y = camera_convert.img2space(CAMERA_STATE, p[0], p[1], -12.5)
            if s:
                cv2.rectangle(img, (p[0] - 10, p[1] - 10, 20, 20), (255, 255, 255, 255), 2)
                print((x, y), 'red')
            else:
                cv2.rectangle(img, (p[0] - 10, p[1] - 10, 20, 20), (128, 128, 128, 255), 1)

    if SHOW_YELLOW:
        for p in points_yellow:
            s, x, y = camera_convert.img2space(CAMERA_STATE, p[0], p[1], -15)
            if s:
                cv2.circle(img, p, 10, (255, 255, 255, 255), 2)
                print((x, y), 'yellow')
            else:
                cv2.circle(img, p, 10, (128, 128, 128, 255), 1)

    if SHOW_WALL and walls is not None:
        for w in walls:
            if USE_HOUGH_P:
                h1, v1, h2, v2 = w[0]
            else:
                rho, theta = w[0]
                a = np.cos(theta)
                b = np.sin(theta)
                h0 = a * rho
                v0 = b * rho
                h1 = int(h0 + 1000 * (-b))
                v1 = int(v0 + 1000 * a)
                h2 = int(h0 - 1000 * (-b))
                v2 = int(v0 - 1000 * a)
            cv2.line(img, (h1, v1), (h2, v2), (255, 255, 255, 255), 1)
            s1, x1, y1 = camera_convert.img2space(CAMERA_STATE, h1, v1, 0)
            s2, x2, y2 = camera_convert.img2space(CAMERA_STATE, h2, v2, 0)
            print(((x1, y1), (x2, y2)), 'wall')

    if show:
        cv2.imshow('image', img)


def draw_grid(color, x_start, x_stop, x_step, y_start, y_stop, y_step):
    overlay = np.zeros(image.shape, np.uint8)

    for x in range(x_start, x_stop + x_step, x_step):
        for y in range(y_start, y_stop, y_step):
            s1, i1, j1 = camera_convert.space2img(CAMERA_STATE, x, y)
            s2, i2, j2 = camera_convert.space2img(CAMERA_STATE, x, y + y_step)
            if s1 or s2:
                cv2.line(overlay, (i1, j1), (i2, j2), color, 1)
    for y in range(y_start, y_stop + y_step, y_step):
        for x in range(x_start, x_stop, x_step):
            s1, i1, j1 = camera_convert.space2img(CAMERA_STATE, x, y)
            s2, i2, j2 = camera_convert.space2img(CAMERA_STATE, x + x_step, y)
            if s1 or s2:
                cv2.line(overlay, (i1, j1), (i2, j2), color, 1)

    overlay = np.minimum(overlay,
                         np.repeat((255 - find_color.get_color_mask(image, find_color.RED))[:, :, np.newaxis], 3,
                                   axis=2))
    overlay = np.minimum(overlay,
                         np.repeat((255 - find_color.get_color_mask(image, find_color.YELLOW))[:, :, np.newaxis], 3,
                                   axis=2))
    overlay = np.minimum(overlay,
                         np.repeat((255 - find_color.get_color_mask(image, find_color.BLUE))[:, :, np.newaxis], 3,
                                   axis=2))

    cv2.add(overlay, image, image)


if __name__ == "__main__":

    repository_path = os.path.dirname(os.path.realpath(__file__)) + '/../..'
    if MODE == 'file':
        for image_index in range(100):
            filename = repository_path + '/assets/openCV_pic/' + READ_DIR + '/' + str(
                image_index) + '.jpg'
            if not os.path.isfile(filename):
                print('cannot open ' + filename)
                continue
            image = cv2.imread(filename)

            process(image, True)
            cv2.waitKey()
    if MODE == 'camera':
        os.mkdir(repository_path + '/assets/openCV_pic/' + WRITE_DIR + '/')
        c = Camera()
        for image_index in range(100):
            image = c.capture()
            filename = repository_path + '/assets/openCV_pic/' + WRITE_DIR + '/' + str(
                image_index) + '.jpg'
            cv2.imwrite(filename, image)
            process(image, GLOBAL_SHOW)
            cv2.waitKey(500)

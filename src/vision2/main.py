import cv2
import os.path
# from picamera2 import Picamera2

from find_red import find_red
import camera_convert


def process(img, show: bool = False):
    points = find_red(img, show)

    draw_grid((255, 255, 255, 255), 0, 1500, 50, -1000, 1000, 50)

    for p in points:
        s, x, y = camera_convert.img2space(camera_state, p[0], p[1], -12.5)
        if s:
            cv2.circle(img, p, 10, (255, 255, 255, 255), 2)
            print((x, y))
        else:
            cv2.circle(img, p, 10, (128, 128, 128, 255), 1)
    if show:
        cv2.imshow('image', img)
        cv2.waitKey()


def draw_grid(color, x_start, x_stop, x_step, y_start, y_stop, y_step):
    for x in range(x_start, x_stop + x_step, x_step):
        for y in range(y_start, y_stop, y_step):
            s1, i1, j1 = camera_convert.space2img(camera_state, x, y)
            s2, i2, j2 = camera_convert.space2img(camera_state, x, y + y_step)
            if s1 or s2:
                cv2.line(image, (i1, j1), (i2, j2), color, 1)
    for y in range(y_start, y_stop + y_step, y_step):
        for x in range(x_start, x_stop, x_step):
            s1, i1, j1 = camera_convert.space2img(camera_state, x, y)
            s2, i2, j2 = camera_convert.space2img(camera_state, x + x_step, y)
            if s1 or s2:
                cv2.line(image, (i1, j1), (i2, j2), color, 1)


if __name__ == "__main__":

    camera_state = camera_convert.CameraState((100, 0, -90), (70, 0), (64, 50), (640, 480))

    for image_index in range(50):
        version = '0'
        filename = os.path.dirname(
            os.path.realpath(__file__)) + '/' + '../../assets/openCV_pic/version' + version + '/' + str(
            image_index) + '.jpg'
        if not os.path.isfile(filename):
            print('no ' + filename)
            continue
        print('yes ' + filename)
        image = cv2.imread(filename)

        process(image, True)

    # cam = Picamera2()
    # while True:
    #     cam.start()
    #     image_rgb = cam.capture_array("main")
    #     cam.stop()
    #     process(image)
